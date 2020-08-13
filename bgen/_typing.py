from collections import OrderedDict
from dataclasses import dataclass
from typing import Any, NamedTuple

from pandas import DataFrame

__all__ = ["CData", "DtypeLike", "Genotype", "Partition"]

# Waiting for official type hint: https://foss.heptapod.net/pypy/cffi/issues/456
CData = Any

# Waiting for numpy release: https://github.com/numpy/numpy/labels/static%20typing
DtypeLike = Any

Genotype = NamedTuple(
    "Genotype",
    [
        ("probs", DtypeLike),
        ("phased", DtypeLike),
        ("ploidy", DtypeLike),
        ("missing", DtypeLike),
    ],
)


@dataclass
class Partition:
    index_offset: int
    nvariants: int
    vid: DtypeLike
    rsid: DtypeLike
    chrom: DtypeLike
    position: DtypeLike
    nalleles: DtypeLike
    allele_ids: DtypeLike
    offset: DtypeLike

    def as_dataframe(self) -> DataFrame:
        data = OrderedDict(
            [
                ("id", self.vid.astype(str)),
                ("rsid", self.rsid.astype(str)),
                ("chrom", self.chrom.astype(str)),
                ("pos", self.position),
                ("nalleles", self.nalleles),
                ("allele_ids", self.allele_ids.astype(str)),
                ("vaddr", self.offset),
            ]
        )

        df = DataFrame(data)
        df.index = range(self.index_offset, self.index_offset + self.nvariants)
        return df
