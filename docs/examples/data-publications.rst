=================
Data publications
=================

There is a (growing) number of publications whose data are analysed with packages based on the ASpecD framework and where the data together with the recipes are published as digital appendix online. This is an attempt to get closer to *true reproducible research* -- and the ASpecD framework provides the gap-less protocol from the raw data to the final data representation in your publication.


List of publications
====================

* `Schröder and Biskup, J. Magn. Reson. 335:107140, 2022 <https://github.com/tillbiskup/2022-jmr-data>`_

  GitHub repository containing both, data and recipes for all the examples shown in the publication describing the cwepr package:

  Mirjam Schröder, Till Biskup. cwepr -- a Python package for analysing cw-EPR data focussing on reproducibility and simple usage. *Journal of Magnetic Resonance* **335**:107140, 2022. doi:`10.1016/j.jmr.2021.107140 <https://doi.org/10.1016/j.jmr.2021.107140>`_ | `PDF <https://www.till-biskup.de/_media/de/person/schr-jmr-335-107140-accepted.pdf>`_ | `SI <https://www.till-biskup.de/_media/de/person/schr-jmr-335-107140-si.pdf>`_

* `Järsvall et al., Chem. Mater. 34:5673, 2022 <https://github.com/tillbiskup/2022-cm-data>`_

  GitHub repository containing both, raw data and analysis "recipes" used to analyse the EPR data for the following publication:

  Emmy Järsvall, Till Biskup, Yadong Zhang, Renee Kroon, Stephen Barlow, Seth Marder, Christian Müller: Double doping of a low-ionization energy polythiophene with a molybdenum dithiolene complex. *Chemistry of Materials*, **34**:5673-5679, 2022, doi:`10.1021/acs.chemmater.2c01040 <https://doi.org/10.1021/acs.chemmater.2c01040>`_


How to contribute to the list?
==============================

If you use ASpecD or a derived package to analyse your data, and you afterwards publish both, the manuscript and the data and analysis recipes, the latter as digital appendix, feel free to get in touch with the authors of the ASpecD framework to have your publication added to the above list.

For the nerds out there: If you like, you could even clone the ASpecD repository from GitHub, add your publication this page, and provide us with a pull request.


How to create a data publication
================================

Data publications are still comparably rare, particularly in the spectroscopy field. Therefore, a few ideas how to publish your data and analysis recipes along with your manuscript. Please note that these are only first ideas.

* Get your data and analysis recipes organised

  If there is a series of distinct analyses, it might be a good idea to work with subdirectories. Figures may go to a separate output directory for convenience. In all cases, make sure the recipes work if you copy the entire root directory containing data and recipes.

* Prepare your data for publication

  As a bare minimum, decide upon and add information on a (permissive) license, such as a Creative Commons license. The actual license usually goes into a file called ``LICENSE``. Add a ``README`` file (preferably in Markdown format) describing the data and referring to the (text) publication. Add a ``Citation.cff`` file.

* Publish the entire data package online and get a DOI

  It does not matter whether you use a combination of GitHub and Zenodo, just Zenodo, FigShare or any other repository out there. Important is to get your data out (regardless of an embargo or else) and a DOI attached to the publication.

* Refer to the data publication in your manuscript (using the DOI)

  As you got a DOI for your data publication in the last step, make sure to refer to the data in your manuscript using this DOI. For Zenodo users: you may want to use the DOI covering *all* versions, not necessarily the DOI pointing only to your first upload. This makes it easier to afterwards add data and explanations.

As you can see from the first two entries of the list at the top of the page, the authors of the ASpecD framework and derived packages currently use a combination of GitHub and Zenodo for their data publications.

