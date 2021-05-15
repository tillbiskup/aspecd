=========
Changelog
=========

This page contains a summary of changes between the official ASpecD releases. Only the biggest changes are listed here. A complete and detailed log of all changes is available through the `GitHub Repository Browser <https://github.com/tillbiskup/aspecd/commits/master>`_.


Version 0.2.0
=============

Not yet released


New features
------------

* Method ``create_dataset()`` in AnalysisStep

* PeakFinding (for 1D data)

* BlindSNREstimation (currently only with simplest method)

* BasicStatistics

* BasicCharacteristics

* ProcessingStep provides non-public method ``_set_defaults()`` for setting default parameters before sanitising parameters.

* Filtering (with uniform, Gaussian, and Savitzky-Golay filter)

* Interpolation (at least for 1D and 2D datasets)

* Normalisation:

  * Act on parts of the data of a dataset

  * Handle noise for ND data with N>1

* RangeExtraction: extract range of data from dataset (using slice notation)

* MultiprocessingTask (and SingleprocessingTask aliasing ProcessingTask)

* ScalarAxisAlgebra: perform scalar algebra on axis values

* DatasetAlgebra: add and subtract data of second dataset to/from dataset

* CommonRangeExtraction for 1D and 2D datasets

* SinglePlotter2D:

  * Filled contour plot with additional contour lines that can be styled

  * Lines of contour plot can be styled

* SliceExtraction now handles both, axis indices and axis values


Changes
-------

* Dataset: method :meth:`aspecd.dataset.append_history_record` made public

* SystemInfo: Packages contain now full list of dependencies with version numbers of currently installed packages

* SliceExtraction:

  * parameter "index" renamed to "position"

  * works for ND datasets with N>1

* ProcessingStep split into SingleProcessingStep and MultiProcessingStep

  All processing steps previously inheriting from aspecd.ProcessingStep need to inherit now from aspecd.SingleProcessingStep to continue working as expected.


New dependencies
----------------

* scipy (for interpolation in ExtractCommonRange and various analysis steps)


Version 0.1.1
=============

Released 2021-05-03

The following bugs have been fixed:

* MetadataMapper: Fix sequence of mapping operations performed

* MetadataMapper: Mappings are automatically loaded from file if filename is given

* CompositePlotter: Legends for subplots work

* SliceExtraction: Remove correct axis from dataset

* MultiPlotter1D*: Fix problem in conjunction with CompositePlotter and assigning drawings

* SliceExtraction: fix problem extracting slice with index zero

* CompositePlotter: more intuitive axes_positions

* Fix bug with aspect ratio of 2D plots using imshow

* Update intersphinx mapping for matplotlib


Version 0.1.0
=============

Released 2021-04-24

* First public release

* List of generally applicable concrete processing steps

* List of generally applicable concrete plotters

* Recipe-driven data analysis fully working with history

* Introduced ASpecD dataset format (ADF)


Version 0.1.0.dev280
====================

Released 2019-06-14

* First public pre-release on PyPI