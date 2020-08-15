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
        "complex.sample": "19a9149e0551f2862c26be48e006b8ac8cd0bd9ca2793ca82ca4b63a1c16083f",
        "haplotypes.bgen": "84e0b59efcc83c7c305cf5446e5dc26b49b15aeb4157a9eb36451376ce3efe4c",
        "haplotypes.bgen.metadata.corrupted": "8f55628770c1ae8155c1ced2463f15df80d32bc272a470bb1d6b68225e1604b1",
        "wrong.metadata": "f746345605150076f3234fbeea7c52e86bf95c9329b2f08e1e3e92a7918b98fb",
    },
)


def get(filename: str) -> Path:
    return Path(goodboy.fetch(filename))
