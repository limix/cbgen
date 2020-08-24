CBGEN's documentation
=====================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   bgen_file
   bgen_metafile
   typing

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

Comments and bugs
=================

You can get the source code and open issues `on Github.`_

.. _on Github.: https://github.com/limix/cbgen
