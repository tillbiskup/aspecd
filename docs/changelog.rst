=========
Changelog
=========

This page contains a summary of changes between the official ASpecD releases. Only the biggest changes are listed here. A complete and detailed log of all changes is available through the `GitHub Repository Browser <https://github.com/tillbiskup/aspecd/commits/master>`_.


Version 0.7.0
=============

Not yet released


Version 0.6.2
=============

Not yet released


Fixes
-----

* Recipe containing a MultiplotTask does not contain datasets as dicts


Version 0.6.1
=============

Released 2021-11-10


Fixes
-----

* ReportTask works with output directory set in recipe
* LatexReporter finds templates with relative path
* Yaml handles numpy floats and ints
* ProcessingTask handles multiple datasets, SinglePlotTask automatically generated figure filenames with multiple datasets
* ProcessingTask no longer tries to deep-copy matplotlib objects
* Replacing dataset labels in recipes works with dataset ids/source


Version 0.6.0
=============

Released 2021-11-05


New features
------------

* Reports

  * Templates for reporting information contained in datasets come bundled with ASpecD.
  * Context contains ``templates_dir`` allowing to include sub-templates.
  * New class :class:`TxtReporter` for plain text reports

* Tasks/Recipe-driven data analysis

  * YAML representation of recipe and tasks via :meth:`aspecd.tasks.Recipe.to_yaml` and :meth:`aspecd.tasks.Task.to_yaml`
  * Figure labels can be set in plotters; otherwise a default label will be set and can be accessed from within reports.

* Utils

  * :func:`change_working_dir` can be used as context manager to temporarily change the working directory.

* General

  * :meth:`aspecd.utils.ToDictMixin.to_dict` can optionally remove keys with empty values.
  * ``to_dict()`` method in :class:`aspecd.processing.ProcessingStep`, :class:`aspecd.analysis.AnalysisStep`, :class:`aspecd.annotation.Annotation`, :class:`aspecd.plotting.Plotter`, :class:`aspecd.table.Table`, :class:`aspecd.report.Reporter`, :class:`aspecd.model.Model`

* Models

  * Axes quantities and units can be explicitly set on model creation.


Changes
-------

* Dataset labels do not contain source path.
* Recipe dataset_source and output directories are no longer converted to absolute paths.
* More complete recipe history for tasks, including more of their properties
* Recipe-driven data analysis: Figures get added to recipe with default label if no label is provided.
* :class:`aspecd.processing.Noise`: explicit noise amplitude can be given.
* Model can add label to created dataset.
* ModelTask adds result label as id to result.
* Plotter: Default figure size changed to (6., 4.) inch


Fixes
-----

* :meth:`aspecd.tasks.Task.to_yaml` serialises numpy arrays
* Datasets from foreign packages are correctly listed in recipe history
* :func:`aspecd.utils.copy_keys_between_dicts` properly traverses
* :class:`aspecd.utils.Yaml` handles :class:`numpy.double`
* Recipe-driven data analysis: automatically generated figure filenames get added to recipe figure record
* Models work now correctly when based on a dataset
* :class:`aspecd.model.FamilyOfCurves` sets correct values for additional axis
* :class:`aspecd.processing.Differentiation` works correctly for 2D datasets
* :class:`aspecd.processing.Noise`: normalisation works with >1D datasets
* :class:`aspecd.plotting.SinglePlotter2DStacked`: ylabel is set to third axis if offset = 0


Version 0.5.0
=============

Released 2021-10-12

New features
------------

* Tasks/Recipe-driven data analysis

  * YAML representation of tasks and recipes using :meth:`aspecd.tasks.Task.to_yaml` and :meth:`aspecd.tasks.Recipe.to_yaml` - convenience methods for later use in guided recipe generation
  * :class:`aspecd.tasks.AggregatedanalysisTask` for performing a SingleAnalysisStep on a series of datasets, aggregating the result in a CalculatedDataset
  * :class:`aspecd.tasks.TabulateTask` for tabular representation of data of a dataset

* Datasets

  * New attribute :attr:`aspecd.dataset.Axis.index` (for individual labels for each data point, similar to pandas and for tabular data)
  * :meth:`aspecd.dataset.Dataset.tabulate` to create tables from datasets

* Analysis steps

  * New class :class:`aspecd.analysis.AggregatedAnalysisStep` for aggregating the results of a SingleAnalysisStep on multiple datasets in a CalculatedDataset

* Tabular representation of datasets

  * New module :mod:`aspecd.table`
  * Series of output formats for tables (including DokuWiki and LaTeX)
  * Tables can have captions that are output as well

* Utils

  * :func:`aspecd.utils.get_package_data` for obtaining package data (*i.e.*, non-code files contained in distribution)


Changes
-------

* :class:`aspecd.analysis.BasicCharacteristics` always returns scalars or lists in its results and writes index (for compatibility with :class:`aspecd.analysis.AggregatedAnalysisStep` and tabular output).


Version 0.4.0
=============

Released 2021-10-08

**Note**: Starting with this release ASpecD requires **Python >= 3.7**.

New features
------------

* Tasks/Recipe-driven data analysis

  * New attribute :attr:`aspecd.tasks.PlotTask.target` allows adding a plot to an already existing plot.
  * :meth:`aspecd.tasks.Task.to_dict` adds (implicit) parameters of underlying task object
  * Classes from the ASpecD framework can be used without prefixing them with "aspecd" in recipes with "default_package" set to a package based on the ASpecD framework.
  * ``serve`` command outputs log messages for each task
  * Command-line options for ``serve`` setting the log level/verbosity
  * Catching of errors, excluding the stack trace and only showing the error message (but full stack trace in verbose mode)
  * Switch in recipe to suppress writing history (for development/debugging, issuing warning on the command line via logging)
  * New structure of recipes: Move ``default_package`` and ``autosave_plots`` to new dict ``settings``; ``output_directory`` and ``datasets_source_directory`` to new dict ``directories``
  * Add ``format`` dict to recipe with fields ``type`` and ``version``
  * Automatically convert old recipe formats within :class:`aspecd.io.RecipeYamlImporter`
  * Processing steps writing parameters during execution and applied to multiple datasetes are unpacked in the recipe history if these parameters change for each dataset


* References in processing and analysis steps and models (using bibrecord package)


Version 0.3.1
=============

Released 2021-09-21

The following bugs have been fixed:

* Handling of lists as properties in recipes
* Improved handling of axes labels with xkcd style
* Offset in SinglePlotter2DStacked can be set to zero


Version 0.3.0
=============

Released 2021-09-02

**Note**: This is the last ASpecD release with explicit support for Python 3.5.

New features
------------

* Processing steps

  * Adding (coloured) noise to datasets (:class:`aspecd.processing.Noise`)
  * Provide a new range of axis values for a dataset for correction (:class:`aspecd.processing.ChangeAxesValues`)

* Analysis steps

  * Power spectral density of 1D dataset (:class:`aspecd.analysis.PowerDensitySpectrum`), *e.g.*, for analysing noise
  * Polynomial fit of 1D data (:class:`aspecd.analysis.PolynomialFit`)
  * Linear regression of 1D data without fitting the intercept (:class:`aspecd.analysis.LinearRegressionWithFixedIntercept`)
  * Additional methods in :class:`aspecd.analysis.BlindSNREstimation`

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
  * :class:`aspecd.model.Exponential`

  * :class:`aspecd.model.CompositeModel` for models consisting of a (weighted) sum of individual models
  * :class:`aspecd.model.FamilyOfCurves` for inspecting systematic variations of one parameter of a given model

* Tasks

  * Comments can be added easily to processing and analysis steps using the top-level key ``comment`` of the respective task.


* Utils

  * :func:`aspecd.utils.not_zero` ensuring a float not to cause DivisionByZero errors


Changes
-------

* :class:`aspecd.processing.Differentiation` uses :func:`numpy.gradient` instead of :func:`numpy.diff`
* :class:`aspecd.processing.BaselineCorrection` returns polynomial coefficients in unscaled data domain


Fixes
-----

* Axis labels without "/" if no unit is present
* :class:`aspecd.metadata.Measurement` handles dates imported from YAML (implicitly converted into datetime.date object)


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
