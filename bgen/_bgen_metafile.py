from __future__ import annotations

from pathlib import Path
from typing import Union

from numpy import empty, uint16, uint32, uint64, zeros

from ._ffi import ffi, lib
from ._typing import CData, Partition, Variants

__all__ = ["bgen_metafile"]


class bgen_metafile:
    def __init__(self, filepath: Union[str, Path]):
        self._filepath = Path(filepath)
        self._bgen_metafile: CData = ffi.NULL
        self._bgen_metafile = lib.bgen_metafile_open(bytes(self._filepath))
        if self._bgen_metafile == ffi.NULL:
            raise RuntimeError(f"Failed to open {filepath}.")

    @property
    def filepath(self) -> Path:
        return self._filepath

    @property
    def npartitions(self) -> int:
        return lib.bgen_metafile_npartitions(self._bgen_metafile)

    @property
    def nvariants(self) -> int:
        return lib.bgen_metafile_nvariants(self._bgen_metafile)

    @property
    def partition_size(self) -> int:
        return ceildiv(self.nvariants, self.npartitions)

    def read_partition(self, index: int) -> Partition:
        partition = lib.bgen_metafile_read_partition(self._bgen_metafile, index)
        if partition == ffi.NULL:
            raise RuntimeError(f"Could not read partition {partition}.")

        nvariants = lib.bgen_partition_nvariants(partition)

        position = empty(nvariants, dtype=uint32)
        nalleles = empty(nvariants, dtype=uint16)
        var_offset = empty(nvariants, dtype=uint64)
        vid_max_len = ffi.new("uint32_t[]", 1)
        rsid_max_len = ffi.new("uint32_t[]", 1)
        chrom_max_len = ffi.new("uint32_t[]", 1)
        allele_ids_max_len = ffi.new("uint32_t[]", 1)

        position_ptr = ffi.cast("uint32_t *", ffi.from_buffer(position))
        nalleles_ptr = ffi.cast("uint16_t *", ffi.from_buffer(nalleles))
        offset_ptr = ffi.cast("uint64_t *", ffi.from_buffer(var_offset))
        lib.read_partition_part1(
            partition,
            position_ptr,
            nalleles_ptr,
            offset_ptr,
            vid_max_len,
            rsid_max_len,
            chrom_max_len,
            allele_ids_max_len,
        )

        vid = zeros(nvariants, dtype=f"S{vid_max_len[0]}")
        rsid = zeros(nvariants, dtype=f"S{rsid_max_len[0]}")
        chrom = zeros(nvariants, dtype=f"S{chrom_max_len[0]}")
        allele_ids = zeros(nvariants, dtype=f"S{allele_ids_max_len[0]}")

        lib.read_partition_part2(
            partition,
            ffi.from_buffer("char[]", vid),
            vid_max_len[0],
            ffi.from_buffer("char[]", rsid),
            rsid_max_len[0],
            ffi.from_buffer("char[]", chrom),
            chrom_max_len[0],
            ffi.from_buffer("char[]", allele_ids),
            allele_ids_max_len[0],
        )
        lib.bgen_partition_destroy(partition)

        part_offset = self.partition_size * index
        v = Variants(vid, rsid, chrom, position, nalleles, allele_ids, var_offset)
        return Partition(part_offset, v)

    def close(self):
        if self._bgen_metafile != ffi.NULL:
            lib.bgen_metafile_close(self._bgen_metafile)

    def __enter__(self) -> bgen_metafile:
        return self

    def __exit__(self, *_):
        self.close()


def ceildiv(a, b) -> int:
    return -(-a // b)
