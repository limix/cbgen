from collections import OrderedDict
from dataclasses import dataclass
from typing import Any

from pandas import DataFrame

__all__ = ["CData", "DtypeLike", "Genotype", "Partition"]

# Waiting for official type hint: https://foss.heptapod.net/pypy/cffi/issues/456
CData = Any

# Waiting for numpy release: https://github.com/numpy/numpy/labels/static%20typing
DtypeLike = Any


@dataclass
class Genotype:
    probs: DtypeLike
    phased: DtypeLike
    ploidy: DtypeLike
    missing: DtypeLike


@dataclass
class Variants:
    id: DtypeLike
    rsid: DtypeLike
    chrom: DtypeLike
    position: DtypeLike
    nalleles: DtypeLike
    allele_ids: DtypeLike
    offset: DtypeLike

    def __len__(self) -> int:
        return self.id.shape[0]


@dataclass
class Partition:
    partition_offset: int
    variants: Variants

    def as_dataframe(self) -> DataFrame:
        v = self.variants
        data = OrderedDict(
            [
                ("id", v.id.astype(str)),
                ("rsid", v.rsid.astype(str)),
                ("chrom", v.chrom.astype(str)),
                ("pos", v.position),
                ("nalleles", v.nalleles),
                ("allele_ids", v.allele_ids.astype(str)),
                ("vaddr", v.offset),
            ]
        )

        df = DataFrame(data)
        df.index = range(self.partition_offset, self.partition_offset + len(v))
        return df
