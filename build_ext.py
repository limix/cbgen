import os
import platform
from os.path import join
from typing import List

from cffi import FFI

ffibuilder = FFI()
libs = ["bgen", "athr"]

if platform.system() == "Windows":
    libs += ["zlib", "libzstd"]
else:
    libs += ["z", "zstd"]

folder = os.path.dirname(os.path.abspath(__file__))

with open(join(folder, "bgen", "interface.h"), "r") as f:
    ffibuilder.cdef(f.read())

with open(join(folder, "bgen", "genotype.h"), "r") as f:
    ffibuilder.cdef(f.read())

with open(join(folder, "bgen", "genotype.c"), "r") as f:
    genotype_c = f.read()

with open(join(folder, "bgen", "partition.h"), "r") as f:
    ffibuilder.cdef(f.read())

with open(join(folder, "bgen", "partition.c"), "r") as f:
    partition_c = f.read()

with open(join(folder, "bgen", "samples.h"), "r") as f:
    ffibuilder.cdef(f.read())

with open(join(folder, "bgen", "samples.c"), "r") as f:
    samples_c = f.read()

extra_link_args: List[str] = []
if "BGEN_EXTRA_LINK_ARGS" in os.environ:
    extra_link_args += os.environ["BGEN_EXTRA_LINK_ARGS"].split(os.pathsep)

ffibuilder.set_source(
    "bgen._ffi",
    fr"""
    #include "bgen/bgen.h"
    {genotype_c}
    {partition_c}
    {samples_c}
    """,
    libraries=libs,
    extra_link_args=extra_link_args,
    language="c",
)

if __name__ == "__main__":
    ffibuilder.compile(verbose=True)
