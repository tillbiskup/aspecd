===========================
ASpecD dataset format (adf)
===========================

Datasets need to be persisted from time to time. While there are plenty of different file formats, storing both, metadata and binary data can get quite complicated pretty fast.


General ideas
=============

The ASpecD dataset format is vaguely reminiscent of the Open Document Format, *i.e.* a zipped directory containing structured data (in this case in form of a YAML file) and binary data in a corresponding subdirectory.

As PyYAML is not capable of dealing with NumPy arrays out of the box, those are dealt with separately. Small arrays are stored inline as lists, larger arrays in separate files. For details, see the :class:`aspecd.utils.Yaml` class.

The data format tries to be as self-contained as possible, using standard file formats and a brief description of its layout contained within the archive. Collecting the contents in a single ZIP archive allows the user to deal with a single file for a dataset, while more advanced users can easily dig into the details and write importers for other platforms and programming languages, making the format rather platform-independent and future-safe. Due to using binary representation for larger numerical arrays, the format should be more memory-efficient than other formats.



Files and their meaning
=======================

What follows is a short description of the different files contained in the ZIP archive.

* ``dataset.yaml`` - text/YAML

  hierarchical metadata store

* ``binaryData/<filename>.npy`` - NumPy binary

  numerical data of the dataset stored in NumPy format

  Only arrays exceeding a certain threshold are stored
  in binary format, mainly to save space and preserve
  numerical accuracy.

* ``VERSION`` - text

  version number of the dataset format

  The version number follows the semantic versioning scheme.

* ``README`` - text

  General information on the dataset format


README in the ZIP archive
=========================

As mentioned above, the ASpecD dataset format is essentially a ZIP archive that consists of a number of files. One of these is a text file called ``README`` with some basic information of the contents of the archive -- an attempt to be as self-consistent as possible. Below the contents of this file are shown.

.. code-block:: text

    Readme
    ======

    This directory contains an ASpecD dataset stored in the
    ASpecD dataset format (adf).

    What follows is a bit of information on the meaning of
    each of the files in the directory.
    Sources of further information on the file format
    are provided at the end of the file.

    Copyright (c) 2021, Till Biskup
    2021-01-04

    Files and their meaning
    -----------------------

    * dataset.yaml - text/YAML
      hierarchical metadata store

    * binaryData/<filename>.npy - NumPy binary
      numerical data of the dataset stored in NumPy format

      Only arrays exceeding a certain threshold are stored
      in binary format, mainly to save space and preserve
      numerical accuracy.

    * VERSION - text
      version number of the dataset format

      The version number follows the semantic versioning scheme.

    * README - text
      This file

    Further information
    -------------------

    More information can be found on the web in the
    ASpecD package documentation:

    https://docs.aspecd.de/adf.html
