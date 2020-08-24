from dataclasses import dataclass
from typing import Any

__all__ = ["CData", "DtypeLike", "Variants", "Genotype", "Partition"]

# Waiting for official type hint: https://foss.heptapod.net/pypy/cffi/issues/456
CData = Any

# Waiting for numpy release: https://github.com/numpy/numpy/labels/static%20typing
DtypeLike = Any


@dataclass
class Genotype:
    """
    Genotype.

    >>> import cbgen
    >>>
    >>> bgen = cbgen.bgen_file(cbgen.example.get("haplotypes.bgen"))
    >>> mf = cbgen.bgen_metafile(cbgen.example.get("haplotypes.bgen.metafile"))
    >>> part = mf.read_partition(0)
    >>> gt = bgen.read_genotype(part.variants.offset[0])
    >>> print(type(gt))
    <class 'cbgen.typing.Genotype'>
    >>> print(gt.probability)
    [[1. 0. 1. 0.]
     [0. 1. 1. 0.]
     [1. 0. 0. 1.]
     [0. 1. 0. 1.]]
    >>> print(gt.phased)
    True
    >>> print(gt.ploidy)
    [2 2 2 2]
    >>> print(gt.missing)
    [False False False False]
    >>> mf.close()
    >>> bgen.close()

    Attributes
    ----------
    Probability
        Probability.
    phased
         Phasedness.
    ploidy
        Ploidy.
    missing
        Missingness.
    """

    probability: DtypeLike
    phased: DtypeLike
    ploidy: DtypeLike
    missing: DtypeLike


@dataclass
class Variants:
    """
    Variants.

    >>> import cbgen
    >>>
    >>> bgen = cbgen.bgen_file(cbgen.example.get("haplotypes.bgen"))
    >>> mf = cbgen.bgen_metafile(cbgen.example.get("haplotypes.bgen.metafile"))
    >>> part = mf.read_partition(0)
    >>> variants = part.variants
    >>> print(type(variants))
    <class 'cbgen.typing.Variants'>
    >>> print(variants.size)
    4
    >>> print(variants.id[3])
    b'SNP4'
    >>> print(variants.rsid[3])
    b'RS4'
    >>> print(variants.chromosome[3])
    b'1'
    >>> print(variants.position[3])
    4
    >>> print(variants.nalleles[3])
    2
    >>> print(variants.allele_ids[3])
    b'A,G'
    >>> print(variants.offset[3])
    273
    >>> mf.close()
    >>> bgen.close()

    Attributes
    ----------
    id
        Identification.
    rsid
         Reference SNP cluster ID.
    chromosome
        Chromosome.
    position
        Position.
    nalleles
        Number of alleles per variant.
    allele_ids
        Allele identifications.
    offset
        Variant offset.
    """

    id: DtypeLike
    rsid: DtypeLike
    chromosome: DtypeLike
    position: DtypeLike
    nalleles: DtypeLike
    allele_ids: DtypeLike
    offset: DtypeLike

    @property
    def size(self) -> int:
        """
        Number of variants.

        Returns
        -------
        Number of variants.
        """
        return self.id.shape[0]


@dataclass
class Partition:
    """
    Partition of variants.

    >>> import cbgen
    >>>
    >>> bgen = cbgen.bgen_file(cbgen.example.get("haplotypes.bgen"))
    >>> mf = cbgen.bgen_metafile(cbgen.example.get("haplotypes.bgen.metafile"))
    >>> part = mf.read_partition(0)
    >>> print(type(part))
    <class 'cbgen.typing.Partition'>
    >>> print(part.offset)
    0
    >>> print(type(part.variants))
    <class 'cbgen.typing.Variants'>
    >>> mf.close()
    >>> bgen.close()

    Attributes
    ----------
    offset
        Partition offset.
    variants
        Variants.
    """

    offset: int
    variants: Variants
