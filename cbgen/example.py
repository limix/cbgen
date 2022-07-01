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
        "haplotypes.bgen.metafile": "7e8b13aed04e2166649dde2c1c44aa4239f158aef7cf06d69c51113b9a2ae175",
        "wrong.metadata": "f746345605150076f3234fbeea7c52e86bf95c9329b2f08e1e3e92a7918b98fb",
        "merged_487400x220000.bgen": "blake2b:2bf8043907eff9c00021dd044d80d63873f465898b8732c8bcbb533ca5fcd63875aa54e8103768631610f76c4c82577bc7c15f7bea90bb1ab1906b12ceddf56e",
        "merged_487400x2420000.bgen": "81aecfab787bee1cb7f1d0d21f2465c581a4db78011d8b0f0f73c868e17ec888",
        "merged_487400x4840000.bgen": "5ef82f92a001615c93bbb317a9fd2329272370c6d481405d4f8f0a2b7fddf68b",
    },
)


def get(filename: str) -> Path:
    """
    Get file path to an example.

    Recognized file names:

    - ``complex.23bits.no.samples.bgen``
    - ``haplotypes.bgen``
    - ``haplotypes.bgen.metadata.corrupted``
    - ``haplotypes.bgen.metafile``
    - ``wrong.metadata``
    - ``merged_487400x220000.bgen``
    - ``merged_487400x2420000.bgen``
    - ``merged_487400x4840000.bgen``

    Parameters
    ----------
    filename
        File name to fetch.

    Returns
    -------
    File path.
    """
    return Path(goodboy.fetch(filename))
