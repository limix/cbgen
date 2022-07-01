import os
import platform
import shutil
import subprocess
import tarfile
import urllib.request
from pathlib import Path
from typing import List

from cffi import FFI
from cmake import CMAKE_BIN_DIR

ffibuilder = FFI()

libs = ["bgen", "athr", "elapsed"]

if platform.system() == "Windows":
    libs += ["zstd_static", "zlibstatic"]
else:
    libs += ["zstd", "z"]

pwd = Path(os.path.dirname(os.path.abspath(__file__)))


def rm(folder: Path, pattern: str):
    for filename in folder.glob(pattern):
        filename.unlink()


def build_deps(pwd: Path, user: str, project: str, version: str):
    ext_dir = pwd / ".ext_deps"
    shutil.rmtree(ext_dir, ignore_errors=True)

    prj_dir = ext_dir / f"{project}-{version}"
    build_dir = prj_dir / "build"
    os.makedirs(build_dir, exist_ok=True)

    url = f"https://github.com/{user}/{project}/archive/refs/tags/v{version}.tar.gz"

    with urllib.request.urlopen(url) as rf:
        data = rf.read()

    tar_filename = f"{project}-{version}.tar.gz"

    with open(ext_dir / tar_filename, "wb") as lf:
        lf.write(data)

    with tarfile.open(ext_dir / tar_filename) as tf:
        tf.extractall(ext_dir)

    cmake_bin = str(next(Path(CMAKE_BIN_DIR).glob("cmake*")))
    subprocess.check_call(
        [
            cmake_bin,
            "-S",
            str(prj_dir),
            "-B",
            str(build_dir),
            "-DCMAKE_BUILD_TYPE=Release",
            "-DENABLE_ALL_WARNINGS=ON",
            "-DCMAKE_POSITION_INDEPENDENT_CODE=ON",
        ],
    )
    subprocess.check_call([cmake_bin, "--build", str(build_dir), "--config", "Release"])
    subprocess.check_call(
        [cmake_bin, "--install", str(build_dir), "--prefix", str(ext_dir)]
    )
    rm(ext_dir / "lib", "*.dylib")
    rm(ext_dir / "lib", "*.so*")
    rm(ext_dir / "lib64", "*.dylib")
    rm(ext_dir / "lib64", "*.so*")

    extra_libs = set()
    for line in open(build_dir / "CMakeCache.txt", "r"):
        line = line.strip()
        if line.startswith("CURSES_CURSES_LIBRARY:"):
            if not line.endswith("NOTFOUND"):
                extra_libs.add("curses")
        elif line.startswith("CURSES_NCURSES_LIBRARY:"):
            if not line.endswith("NOTFOUND"):
                extra_libs.add("ncurses")

    if len(extra_libs) > 1:
        extra_libs.remove("curses")

    return list(extra_libs)


if not os.getenv("BGEN_SKIP_BUILD_DEPS", False):
    libs += build_deps(pwd, "limix", "bgen", "4.1.9")

with open(pwd / "cbgen" / "interface.h", "r") as f:
    ffibuilder.cdef(f.read())

with open(pwd / "cbgen" / "genotype.h", "r") as f:
    ffibuilder.cdef(f.read())

with open(pwd / "cbgen" / "genotype.c", "r") as f:
    genotype_c = f.read()

with open(pwd / "cbgen" / "partition.h", "r") as f:
    ffibuilder.cdef(f.read())

with open(pwd / "cbgen" / "partition.c", "r") as f:
    partition_c = f.read()

with open(pwd / "cbgen" / "samples.h", "r") as f:
    ffibuilder.cdef(f.read())

with open(pwd / "cbgen" / "samples.c", "r") as f:
    samples_c = f.read()

extra_link_args: List[str] = []
if "BGEN_EXTRA_LINK_ARGS" in os.environ:
    extra_link_args += os.environ["BGEN_EXTRA_LINK_ARGS"].split(os.pathsep)

ffibuilder.set_source(
    "cbgen._ffi",
    rf"""
    #include "bgen/bgen.h"
    {genotype_c}
    {partition_c}
    {samples_c}
    """,
    libraries=libs,
    extra_link_args=extra_link_args,
    language="c",
    library_dirs=[str(pwd / ".ext_deps" / "lib"), str(pwd / ".ext_deps" / "lib64")],
    include_dirs=[str(pwd / ".ext_deps" / "include")],
)

if __name__ == "__main__":
    ffibuilder.compile(verbose=True)
