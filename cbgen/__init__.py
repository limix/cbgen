from importlib import import_module as _import_module

from . import example
from ._bgen_file import bgen_file
from ._bgen_metafile import bgen_metafile
from ._env import BGEN_CACHE_HOME
from ._testit import test

try:
    from ._ffi import ffi

    del ffi
except Exception as e:
    _ffi_err = """
It is likely caused by a broken installation of this package.
Please, make sure you have a C compiler and try to uninstall
and reinstall the package again."""

    raise RuntimeError(str(e) + _ffi_err)

try:
    __version__ = getattr(_import_module("cbgen._version"), "version", "x.x.x")
except ModuleNotFoundError:
    __version__ = "x.x.x"

__all__ = [
    "BGEN_CACHE_HOME",
    "__version__",
    "bgen_file",
    "bgen_metafile",
    "example",
    "test",
    "typing",
]
