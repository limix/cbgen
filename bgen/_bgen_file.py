from math import floor, sqrt
from pathlib import Path
from typing import Union

from numpy import float64, full, nan, uint8, zeros
from pandas import Series

from ._ffi import ffi, lib
from ._typing import CData, Genotype

__all__ = ["bgen_file"]


class bgen_file:
    def __init__(self, filepath: Union[str, Path]):
        self._filepath = Path(filepath)
        self._bgen_file: CData = ffi.NULL
        self._bgen_file = lib.bgen_file_open(bytes(self._filepath))
        if self._bgen_file == ffi.NULL:
            raise RuntimeError(f"Failed to open {filepath}.")

    @property
    def filepath(self) -> Path:
        return self._filepath

    @property
    def nvariants(self) -> int:
        return lib.bgen_file_nvariants(self._bgen_file)

    @property
    def nsamples(self) -> int:
        return lib.bgen_file_nsamples(self._bgen_file)

    @property
    def contain_samples(self) -> bool:
        return lib.bgen_file_contain_samples(self._bgen_file)

    def read_samples(self) -> Series:
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

        return Series(samples, dtype=str, name="id")

    def create_metafile(self, filepath: Union[str, Path], verbose=True):
        n = _estimate_best_npartitions(self.nvariants)
        filepath = Path(filepath)

        mf = lib.bgen_metafile_create(self._bgen_file, bytes(filepath), n, verbose)
        if mf == ffi.NULL:
            raise RuntimeError(f"Error while creating metafile {filepath}.")

        lib.bgen_metafile_close(mf)

    def read_genotype(self, offset: int) -> Genotype:
        gt: CData = lib.bgen_file_open_genotype(self._bgen_file, offset)
        if gt == ffi.NULL:
            raise RuntimeError(f"Could not open genotype (offset {offset}).")

        nsamples = self.nsamples
        ncombs = lib.bgen_genotype_ncombs(gt)
        probs = full((nsamples, ncombs), nan, dtype=float64)
        err: int = lib.bgen_genotype_read(gt, ffi.cast("double *", probs.ctypes.data))
        if err != 0:
            msg = f"Could not read genotype probabilities (offset {offset})."
            raise RuntimeError(msg)

        phased = lib.bgen_genotype_phased(gt)

        ploidy = full(nsamples, 0, dtype=uint8)
        lib.read_ploidy(gt, ffi.cast("uint8_t *", ploidy.ctypes.data), nsamples)

        missing = full(nsamples, 0, dtype=bool)
        lib.read_missing(gt, ffi.cast("bool *", missing.ctypes.data), nsamples)

        lib.bgen_genotype_close(gt)

        return Genotype(probs, phased, ploidy, missing)

    def close(self):
        if self._bgen_file != ffi.NULL:
            lib.bgen_file_close(self._bgen_file)

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()


def _estimate_best_npartitions(nvariants: int) -> int:
    min_variants = 128
    m = max(min(min_variants, nvariants), floor(sqrt(nvariants)))
    return nvariants // m
