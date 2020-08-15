from pathlib import Path

import pytest
from numpy import nan
from numpy.testing import assert_allclose

from bgen import bgen_file, bgen_metafile, example


def test_bgen_samples_not_present(tmp_path: Path):
    filepath = example.get("complex.23bits.no.samples.bgen")
    mfilepath = tmp_path / f"{filepath.name}.metafile"
    with bgen_file(filepath) as bgen:
        assert bgen.filepath.name == "complex.23bits.no.samples.bgen"
        assert bgen.nvariants == 10
        assert bgen.nsamples == 4
        assert not bgen.contain_samples
        with pytest.raises(RuntimeError):
            bgen.read_samples()
        bgen.create_metafile(mfilepath, verbose=False)

    with bgen_metafile(mfilepath) as mf:
        assert mf.filepath.name == mfilepath.name
        assert mf.npartitions == 1
        assert mf.nvariants == 10
        assert mf.partition_size == 10

        part = mf.read_partition(0)

        assert part.variants.id[0] == b""
        assert part.variants.rsid[0] == b"V1"
        assert part.variants.chrom[0] == b"01"
        assert part.variants.position[0] == 1
        assert part.variants.nalleles[0] == 2
        assert part.variants.allele_ids[0] == b"A,G"

        with bgen_file(filepath) as bgen:
            voff = part.variants.offset[0]
            gt = bgen.read_genotype(voff)
            assert_allclose(
                gt.probs,
                [[1.0, 0.0, nan], [1.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]],
            )
            assert not gt.phased
            assert_allclose(gt.ploidy, [1, 2, 2, 2])
            assert_allclose(gt.missing, [False, False, False, False])

            voff = part.variants.offset[-1]
            gt = bgen.read_genotype(voff)
            assert_allclose(
                gt.probs,
                [
                    [1.0, 0.0, 0.0, 0.0, 0.0],
                    [0.0, 1.0, 0.0, 0.0, 0.0],
                    [0.0, 0.0, 1.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0, 1.0, 0.0],
                ],
            )
            assert not gt.phased
            assert_allclose(gt.ploidy, [4, 4, 4, 4])
            assert_allclose(gt.missing, [False, False, False, False])

            valid_offsets = set(list(part.variants.offset))
            all_offsets = set(list(range(0, int(max(valid_offsets)) + 1)))
            invalid_offsets = all_offsets - valid_offsets

            for offset in list(invalid_offsets):
                with pytest.raises(RuntimeError):
                    bgen.read_genotype(offset)

        with pytest.raises(RuntimeError):
            part = mf.read_partition(1)
