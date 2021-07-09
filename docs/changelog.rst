=========
Changelog
=========

This page contains a summary of changes between the official ASpecD releases. Only the biggest changes are listed here. A complete and detailed log of all changes is available through the `GitHub Repository Browser <https://github.com/tillbiskup/aspecd/commits/master>`_.


Version 0.3.0
=============

Not yet released

New features
------------

* Processing steps

  * Adding (coloured) noise to datasets (:class:`aspecd.processing.Noise`)
  * Provide a new range of axis values for a dataset for correction (:class:`aspecd.processing.ChangeAxesValues`)

* Analysis steps

  * Power spectral density of 1D dataset (:class:`aspecd.analysis.PowerDensitySpectrum`), *e.g.*, for analysing noise
  * Polynomial fit of 1D data (:class:`aspecd.analysis.PolynomialFit`)
  * Linear regression of 1D data without fitting the intercept (:class:`aspecd.analysis.LinearRegressionWithFixedIntercept`)

* Class :class:`aspecd.model.Model`

  * New attribute :attr:`aspecd.model.Model.description`
  * New non-public method ``_sanitise_parameters``

* New models

  * :class:`aspecd.model.Polynomial` for evaluating polynomials (*e.g.*, as obtained using :class:`aspecd.analysis.PolynomialFit`)
  * :class:`aspecd.model.Zeros`
  * :class:`aspecd.model.Ones`
  * :class:`aspecd.model.Gaussian`
  * :class:`aspecd.model.NormalisedGaussian`
  * :class:`aspecd.model.Lorentzian`
  * :class:`aspecd.model.NormalisedLorentzian`
  * :class:`aspecd.model.Sine`

* Utils

  * :func:`aspecd.utils.not_zero` ensuring a float not to cause DivisionByZero errors


Changes
-------

* :class:`aspecd.processing.Differentiation` uses :func:`numpy.gradient` instead of :func:`numpy.diff`
* :class:`aspecd.processing.BaselineCorrection` returns polynomial coefficients in unscaled data domain


Fixes
-----


Version 0.2.2
=============

Released 2021-06-19

The following bugs have been fixed:

* Normalisation to minimum now divides by absolute value of minimum

* Normalisation raises ValueError in case of unknown kind

* Import with explicit importer when importer resides in (sub)package

* Recipe history shortens dataset source if dataset_source_directory has trailing slash


Version 0.2.1
=============

Released 2021-06-03

The following bugs have been fixed:

* Report: template can have ".." in its path
* :func:`aspecd.utils.copy_values_between_dicts` cascades through source dict
* Add missing template files for sphinx multiversion

Additionally, the following new helper functions appeared:

* :func:`aspecd.utils.remove_empty_values_from_dict`
* :func:`aspecd.utils.convert_keys_to_variable_names`


Version 0.2.0
=============

Released 2021-05-19

New features
------------

* Singleplot and multiplot tasks automatically save results to generic file(s) when no filename is provided

* Importer and importer parameters can be set in recipe

* DatasetImporterFactory: importer can be set explicitly, parameters can be passed to importers

* DatasetImporter with parameters property

* Meaningful error messages for exceptions in ProcessingSteps, AnalysisSteps, Plotters

* Method ``create_dataset()`` in AnalysisStep

* PeakFinding (for 1D data)

* BlindSNREstimation (currently only with simplest method)

* BasicStatistics (mean, median, std, var)

* BasicCharacteristics (min, max, amplitude, area)

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

* Removed parameter ``source`` from method ``_get_importer`` in DatasetImporterFactory, importer factories of derived packages now handle ASpecD-implemented importers by default.

* Dataset: method :meth:`aspecd.dataset.append_history_record` made public

* SystemInfo: Packages contain now full list of dependencies with version numbers of currently installed packages

* SliceExtraction:

  * parameter "index" renamed to "position"

  * works for ND datasets with N>1

* ProcessingStep split into SingleProcessingStep and MultiProcessingStep

  All processing steps previously inheriting from aspecd.ProcessingStep need to inherit now from aspecd.SingleProcessingStep to continue working as expected.

* Plots throw "NotApplicableToDataset" exceptions rather than "PlotNotApplicableToDataset"


Fixes
-----

* SingleanalysisTask assigns results of multiple (individual) datasets

* Exceptions print messages


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