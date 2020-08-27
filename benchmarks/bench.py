import tempfile

import cbgen


class ReadSuite:
    def setup(self):
        self._filepath = cbgen.example.get("merged_487400x220000.bgen")

    def time_create_metafile(self):
        with tempfile.TemporaryDirectory as tmpdir:
            with cbgen.bgen_file(self._filepath) as bgen:
                bgen.create_metafile(tmpdir / "metafile", verbose=False)
