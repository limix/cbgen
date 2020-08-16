from dataclasses import dataclass
from typing import Any

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
    offset: int
    variants: Variants
