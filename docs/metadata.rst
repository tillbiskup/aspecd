================================
Metadata during data acquisition
================================

(Numerical) data without accompanying metadata are pretty useless, as data can only be analysed (and the results somewhat reproduced) knowing the context of their recording, *i.e.* what (instrumental) parameters have been used for data acquisition and what sample has been measured. While the ASpecD framework and derived packages take care of recording all metadata acquired *during* data processing and analysis, we are here concerned with **metadata during data acquisition**, *i.e.* the step before ASpecD and derived packages enter the stage.

.. important::

    While most spectrometers automatically record *some* instrumental parameters and include them in the vendor file format, usually these parameters are *not sufficiently complete*, and essential information such as what sample has been measured (by whom) is regularly not included. Hence, **you need to manually record essential metadata during data acquisition**, and to allow ASpecD/derived packages to access these crucial metadata, you better use a file format that can automatically be imported together with the data.


The Infofile format
===================

Recording metadata during data acquisition is both, an essential aspect of and as old as science itself. The Infofile format is a simple textual file format developed to **document research data**. It allows researchers in the lab to record all relevant metadata **during data acquisition** in a user-friendly and obvious way while minimising any external dependencies. The resulting machine-actionable metadata in turn allow processing and analysis software to access relevant information, besides **making the research data more reproducible** and FAIRer.


.. tip::

    The ASpecD framework and derived packages will automatically look for a file with the same base name and the extension ``.info`` when importing files. Hence, the clear advice is to make it a habit to record all relevant metadata in an Infofile *during data acquisition* and store it next to the actual data files.


Further information on the format including the full specification and a discussion of the advantages (and disadvantages) compared to other formats can be found in the following publication:

  * Bernd Paulus, Till Biskup: Towards more reproducible and FAIRer research data: documenting provenance during data acquisition using the Infofile format. *Digital Discovery* **2**:234–244, 2023, doi:`10.1039/D2DD00131D <https://doi.org/10.1039/D2DD00131D>`_

For actual Infofile example files, see the git repository available at GitHub:

  * https://github.com/tillbiskup/infofile

An example of a (rather artificial) general Infofile is provided below for convenience as well.


Features
--------

* Simple text format
* Storing structured, machine-actionable metadata
* Minimum formatting overhead
* Focussing on human-writability
* No external (software) dependencies
* Easily extendable


Benefits
--------

* No thinking required: never miss any relevant parameter
* All information for the materials&methods part always available (even for collaboration partners)
* Automatic import using ASpecD and derived packages: information available during data processing and analysis (and in reports)
* Big step forward towards *truly* reproducible research


Example
-------

Below is an example of a generic Infofile. For actual methods, you need to extend the file with specific blocks and key--value pairs. The format should be pretty self-explaining. For templates and information regarding further development, see the corresponding `GitHub repository <https://github.com/tillbiskup/infofile>`_. A full format description is given in the `accompanying publication <https://doi.org/10.1039/D2DD00131D>`_.


.. literalinclude:: common.info

