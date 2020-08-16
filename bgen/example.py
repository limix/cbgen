import logging
from pathlib import Path

import pooch

from ._env import BGEN_CACHE_HOME

__all__ = ["get"]

pooch.get_logger().setLevel(logging.ERROR)

goodboy = pooch.create(
    path=BGEN_CACHE_HOME / "test_data",
    base_url="https://bgen-examples.s3.amazonaws.com/",
    registry={
        "complex.23bits.no.samples.bgen": "25d30a4e489da1aeb05f9893af98e8bf3b09d74db2982bf1828f8c8565886fc6",
        "haplotypes.bgen": "84e0b59efcc83c7c305cf5446e5dc26b49b15aeb4157a9eb36451376ce3efe4c",
        "haplotypes.bgen.metadata.corrupted": "8f55628770c1ae8155c1ced2463f15df80d32bc272a470bb1d6b68225e1604b1",
        "wrong.metadata": "f746345605150076f3234fbeea7c52e86bf95c9329b2f08e1e3e92a7918b98fb",
        "merged_487400x220000.bgen": "8dccd89a53e048ea24305cb04c3653b0eb2af265b04d05a60cfa2cca5fb7ae94",
        "merged_487400x2420000.bgen": "81aecfab787bee1cb7f1d0d21f2465c581a4db78011d8b0f0f73c868e17ec888",
    },
)


def get(filename: str) -> Path:
    return Path(goodboy.fetch(filename))
