from __future__ import annotations

from math import floor, sqrt
from pathlib import Path
from typing import Union

from numpy import empty, float32, float64, uint8, zeros

from cbgen.typing import CData, DtypeLike, Genotype

from ._ffi import ffi, lib

__all__ = ["bgen_file"]


class bgen_file:
    """
    BGEN file handler.

    >>> import cbgen
    >>>
    >>> bgen = cbgen.bgen_file(cbgen.example.get("haplotypes.bgen"))
    >>> print(bgen.nvariants)
    4
    >>> print(bgen.nsamples)
    4
    >>> print(bgen.contain_samples)
    True
    >>> print(bgen.read_samples())
    [b'sample_0' b'sample_1' b'sample_2' b'sample_3']
    >>> mf = cbgen.bgen_metafile(cbgen.example.get("haplotypes.bgen.metafile"))
    >>> part = mf.read_partition(0)
    >>> gt = bgen.read_genotype(part.variants.offset[0])
    >>> print(gt.probability)
    [[1. 0. 1. 0.]
     [0. 1. 1. 0.]
     [1. 0. 0. 1.]
     [0. 1. 0. 1.]]
    >>> mf.close()
    >>> bgen.close()

    Use `with`-statement context to guarantee file closing at the end.

    >>> with cbgen.bgen_file(cbgen.example.get("haplotypes.bgen")) as bgen:
    ...     print(bgen.nvariants)
    4

    Parameters
    ----------
    filepath
        BGEN file path.
    """

    def __init__(self, filepath: Union[str, Path]):
        self._filepath = Path(filepath)
        self._bgen_file: CData = ffi.NULL
        self._bgen_file = lib.bgen_file_open(bytes(self._filepath))
        if self._bgen_file == ffi.NULL:
            raise RuntimeError(f"Failed to open {filepath}.")

    @property
    def filepath(self) -> Path:
        """
        File path.

        Returns
        -------
        File path.
        """
        return self._filepath

    @property
    def nvariants(self) -> int:
        """
        Number of variants.

        Returns
        -------
        Number of variants.
        """
        return lib.bgen_file_nvariants(self._bgen_file)

    @property
    def nsamples(self) -> int:
        """
        Number of samples.

        Returns
        -------
        Number of samples.
        """
        return lib.bgen_file_nsamples(self._bgen_file)

    @property
    def contain_samples(self) -> bool:
        """
        Check if it contains samples.

        Returns
        -------
        ``True`` if it does contain samples; ``False`` otherwise.
        """
        return lib.bgen_file_contain_samples(self._bgen_file)

    def read_samples(self) -> DtypeLike:
        """
        Read samples.

        Returns
        -------
        Samples.

        Raises
        ------
        RuntimeError
            If samples are not stored or a file stream reading error occurs.
        """
        nsamples = self.nsamples
        bgen_samples: CData = lib.bgen_file_read_samples(self._bgen_file)
        if bgen_samples == ffi.NULL:
            raise RuntimeError("Could not fetch samples from the bgen file.")

        try:
            samples_max_len = ffi.new("uint32_t[]", 1)
            lib.read_samples_part1(bgen_samples, nsamples, samples_max_len)
            samples = zeros(nsamples, dtype=f"S{samples_max_len[0]}")
            lib.read_samples_part2(
                bgen_samples,
                nsamples,
                ffi.from_buffer("char[]", samples),
                samples_max_len[0],
            )
        finally:
            lib.bgen_samples_destroy(bgen_samples)

        return samples

    def create_metafile(self, filepath: Union[str, Path], verbose=False):
        """
        Create metafile file.

        Parameters
        ----------
        filepath
            File path.
        verbose
            ``True`` to show progress; ``False`` otherwise (default).
        """
        n = estimate_best_npartitions(self.nvariants)
        filepath = Path(filepath)

        mf = lib.bgen_metafile_create(self._bgen_file, bytes(filepath), n, verbose)
        if mf == ffi.NULL:
            raise RuntimeError(f"Error while creating metafile {filepath}.")

        lib.bgen_metafile_close(mf)

    def read_genotype(self, offset: int, precision: int = 64) -> Genotype:
        """
        Read genotype.

        Parameters
        ----------
        offset
            Variant offset.
        precision
            Probability precision in bits: 64 (default) or 32.

        Returns
        -------
        Genotype.

        Raises
        ------
        RuntimeError
            If invalid offset of or a file stream reading error occurs.
        """
        gt: CData = lib.bgen_file_open_genotype(self._bgen_file, offset)
        if gt == ffi.NULL:
            raise RuntimeError(f"Could not open genotype (offset {offset}).")

        if precision not in [64, 32]:
            raise ValueError("Precision should be either 64 or 32.")

        nsamples = self.nsamples
        ncombs = lib.bgen_genotype_ncombs(gt)
        err: int = 0
        if precision == 64:
            probs = empty((nsamples, ncombs), dtype=float64)
            err = lib.bgen_genotype_read64(gt, ffi.cast("double *", probs.ctypes.data))
        else:
            probs = empty((nsamples, ncombs), dtype=float32)
            err = lib.bgen_genotype_read32(gt, ffi.cast("float *", probs.ctypes.data))

        if err != 0:
            msg = f"Could not read genotype probabilities (offset {offset})."
            raise RuntimeError(msg)

        phased = lib.bgen_genotype_phased(gt)

        ploidy = empty(nsamples, dtype=uint8)
        lib.read_ploidy(gt, ffi.cast("uint8_t *", ploidy.ctypes.data), nsamples)

        missing = empty(nsamples, dtype=bool)
        lib.read_missing(gt, ffi.cast("bool *", missing.ctypes.data), nsamples)

        lib.bgen_genotype_close(gt)

        return Genotype(probs, phased, ploidy, missing)

    def read_probability(self, offset: int, precision: int = 64) -> DtypeLike:
        """
        Read genotype probability.

        Parameters
        ----------
        offset
            Variant offset.
        precision
            Probability precision in bits: 64 (default) or 32.

        Returns
        -------
        Probabilities.

        Raises
        ------
        RuntimeError
            If invalid offset of or a file stream reading error occurs.
        """
        gt: CData = lib.bgen_file_open_genotype(self._bgen_file, offset)
        if gt == ffi.NULL:
            raise RuntimeError(f"Could not open genotype (offset {offset}).")

        if precision not in [64, 32]:
            raise ValueError("Precision should be either 64 or 32.")

        nsamples = self.nsamples
        ncombs = lib.bgen_genotype_ncombs(gt)
        err: int = 0
        if precision == 64:
            probs = empty((nsamples, ncombs), dtype=float64)
            err = lib.bgen_genotype_read64(gt, ffi.cast("double *", probs.ctypes.data))
        else:
            probs = empty((nsamples, ncombs), dtype=float32)
            err = lib.bgen_genotype_read32(gt, ffi.cast("float *", probs.ctypes.data))

        if err != 0:
            msg = f"Could not read genotype probabilities (offset {offset})."
            raise RuntimeError(msg)

        lib.bgen_genotype_close(gt)

        return probs

    def close(self):
        """
        Close file stream.
        """
        if self._bgen_file != ffi.NULL:
            lib.bgen_file_close(self._bgen_file)
            self._bgen_file = ffi.NULL

    def __del__(self):
        self.close()

    def __enter__(self) -> bgen_file:
        return self

    def __exit__(self, *_):
        self.close()


def estimate_best_npartitions(nvariants: int) -> int:
    min_variants = 128
    m = max(min(min_variants, nvariants), floor(sqrt(nvariants)))
    return nvariants // m
