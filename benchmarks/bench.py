import tempfile
from pathlib import Path

import cbgen


class BGENSuite:
    timeout = 10 * 60.0

    def __init__(self):
        self._filepath = cbgen.example.get("merged_487400x220000.bgen")
        self._mfilepath = Path("metafile")
        with cbgen.bgen_file(self._filepath) as bgen:
            bgen.create_metafile(self._mfilepath, verbose=False)

    def setup(self):
        pass

    def time_bgen_file(self):
        with cbgen.bgen_file(self._filepath):
            pass

    def time_create_metafile(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with cbgen.bgen_file(self._filepath) as bgen:
                bgen.create_metafile(Path(tmpdir) / "metafile", verbose=False)

    def time_bgen_metafile(self):
        with cbgen.bgen_metafile(self._mfilepath):
            pass

    def time_read_partitions(self):
        with cbgen.bgen_metafile(self._mfilepath) as mf:
            for i in range(mf.npartitions):
                mf.read_partition(i)
