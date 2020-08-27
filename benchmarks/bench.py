import cbgen


class ReadSuite:
    def setup(self):
        self._filepath = cbgen.example.get("merged_487400x220000.bgen")

    def time_bgen_file(self):
        cbgen.bgen_file(self._filepath)
