CBGEN documentation
===================

`BGEN`_ is a file format for storing large genetic datasets.
It supports both unphased genotypes and phased haplotype data with variable
ploidy and number of alleles. It was designed to provide a compact data
representation without sacrificing variant access performance.
This Python package is a wrapper around the `bgen library`_,
a low-memory footprint reader that efficiently reads bgen files.
It fully supports the bgen format specifications: 1.2 and 1.3;
as well as their optional compressed formats.

Installation
------------

::

  pip install cbgen

Usage example
-------------

.. code-block:: python

    >>> import cbgen
    >>>
    >>> bgen = cbgen.bgen_file(cbgen.example.get("haplotypes.bgen"))
    >>> bgen.create_metafile("haplotypes.bgen.metafile")
    >>> mf = cbgen.bgen_metafile("haplotypes.bgen.metafile")
    >>> print(mf.npartitions)
    1
    >>> print(mf.nvariants)
    4
    >>> print(mf.partition_size)
    4
    >>> part = mf.read_partition(0)
    >>> gt = bgen.read_genotype(part.variants.offset[0])
    >>> print(gt.probability)
    [[1. 0. 1. 0.]
     [0. 1. 1. 0.]
     [1. 0. 0. 1.]
     [0. 1. 0. 1.]]
    >>> mf.close()
    >>> bgen.close()

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   bgen_file
   bgen_metafile
   cache_home
   example
   typing

Comments and bugs
=================

You can get the source code and open issues `on Github.`_

.. _BGEN: https://www.well.ox.ac.uk/~gav/bgen_format/
.. _bgen library: https://github.com/limix/bgen
.. _on Github.: https://github.com/limix/cbgen
