from typing import Any as _Any
from typing import NamedTuple as _NamedTuple

__all__ = ["CData", "DtypeLike", "Genotype"]

# Waiting for official type hint: https://foss.heptapod.net/pypy/cffi/issues/456
CData = _Any

# Waiting for numpy release: https://github.com/numpy/numpy/labels/static%20typing
DtypeLike = _Any

Genotype = _NamedTuple(
    "Genotype",
    [
        ("probs", DtypeLike),
        ("phased", DtypeLike),
        ("ploidy", DtypeLike),
        ("missing", DtypeLike),
    ],
)
