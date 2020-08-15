from pathlib import Path

import pytest
from numpy import nan
from numpy.testing import assert_allclose, assert_array_equal

from bgen import bgen_file, bgen_metafile, example


def test_bgen_invalid_metafile():
    mfilepath = example.get("wrong.metadata")
    with pytest.raises(RuntimeError):
        bgen_metafile(mfilepath)

    mfilepath = example.get("haplotypes.bgen.metadata.corrupted")
    with pytest.raises(RuntimeError):
        bgen_metafile(mfilepath)


def test_bgen_phased_genotype(tmp_path):
    filepath = example.get("haplotypes.bgen")
    mfilepath = tmp_path / f"{filepath.name}.metafile"

    bgen = bgen_file(filepath)
    assert bgen.filepath.name == "haplotypes.bgen"
    assert bgen.nvariants == 4
    assert bgen.nsamples == 4
    assert bgen.contain_samples
    samples = bgen.read_samples()
    assert_array_equal(samples, [b"sample_0", b"sample_1", b"sample_2", b"sample_3"])

    bgen.create_metafile(mfilepath, verbose=False)

    mf = bgen_metafile(mfilepath)

    assert mf.filepath.name == mfilepath.name
    assert mf.npartitions == 1
    assert mf.nvariants == 4
    assert mf.partition_size == 4

    part = mf.read_partition(0)

    assert part.variants.id[0] == b"SNP1"
    assert part.variants.rsid[0] == b"RS1"
    assert part.variants.chrom[0] == b"1"
    assert part.variants.position[0] == 1
    assert part.variants.nalleles[0] == 2
    assert part.variants.allele_ids[0] == b"A,G"
    voff = part.variants.offset[0]
    gt = bgen.read_genotype(voff)
    assert_allclose(
        gt.probs,
        [
            [1.0, 0.0, 1.0, 0.0],
            [0.0, 1.0, 1.0, 0.0],
            [1.0, 0.0, 0.0, 1.0],
            [0.0, 1.0, 0.0, 1.0],
        ],
    )
    assert gt.phased
    assert_allclose(gt.ploidy, [2, 2, 2, 2])
    assert_allclose(gt.missing, [False, False, False, False])

    assert part.variants.id[3] == b"SNP4"
    assert part.variants.rsid[3] == b"RS4"
    assert part.variants.chrom[3] == b"1"
    assert part.variants.position[3] == 4
    assert part.variants.nalleles[3] == 2
    assert part.variants.allele_ids[3] == b"A,G"
    voff = part.variants.offset[3]
    gt = bgen.read_genotype(voff)
    assert_allclose(
        gt.probs,
        [
            [0.0, 1.0, 0.0, 1.0],
            [1.0, 0.0, 1.0, 0.0],
            [0.0, 1.0, 1.0, 0.0],
            [1.0, 0.0, 0.0, 1.0],
        ],
    )
    assert gt.phased
    assert_allclose(gt.ploidy, [2, 2, 2, 2])
    assert_allclose(gt.missing, [False, False, False, False])

    mf.close()
    bgen.close()


def test_bgen_complex_unphased(tmp_path: Path):
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
