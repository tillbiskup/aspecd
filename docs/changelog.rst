=========
Changelog
=========

This page contains a summary of changes between the official ASpecD releases. Only the biggest changes are listed here. A complete and detailed log of all changes is available through the `GitHub Repository Browser <https://github.com/tillbiskup/aspecd/commits/master>`_.


Version 0.10.0
==============

Released 2024-08-10


New features
------------

* Plotting

  * Set individual properties for each of the lines of a :class:`aspecd.plotting.SinglePlotter2DStacked`
  * Conveniently set identical properties for all lines of :class:`aspecd.plotting.SinglePlotter2DStacked` and :class:`aspecd.plotting.MultiPlotter1D`
  * :class:`aspecd.plotting.TextProerties`
  * :class:`aspecd.plotting.DrawingProperties` has attribute ``zorder``.
  * :class:`aspecd.plotting.SubplotGridSpecs` for properties of the subplot grid of a CompositePlotter.
  * :class:`aspecd.plotting.CompositePlotter` allows to share *x* and *y* axes.

* Plot annotations

  * :class:`aspecd.annotations.Text` for text annotations to plot(ter)s

* Tasks

  * :class:`aspecd.tasks.SingleplotTask` allows to set as many results as datasets, to allow for adding an individual plotter (for one of the datasets) to a :class:`aspecd.tasks.CompositeplotTask`. (`#3 <https://github.com/tillbiskup/aspecd/issues/3>`_)

* Models

    * :class:`aspecd.model.Voigtian` for creating Voigt profiles frequently used in spectroscopy to describe line shapes.


Fixes
-----

* Tasks

  * :class:`aspecd.tasks.MultiplotTask` preserves order of datasets the task is applied to, regardless whether the datasets are originally imported or result from prior tasks (via ``result`` property). (`#2 <https://github.com/tillbiskup/aspecd/issues/2>`_)
  * :meth:`aspecd.tasks.Recipe.get_datasets` preserves order of datasets, regardless whether the datasets are originally imported or result from prior tasks (via ``result`` property).
  * :meth:`aspecd.tasks.Chef.cook` closes open figures.

* Plotting

  * :class:`CompositePlotter` does not add additional drawings any more to the plotters used. (`#5 <https://github.com/tillbiskup/aspecd/issues/5>`_)


Version 0.9.3
=============

Released 2024-07-22


Fixes
-----

* Correct method for area normalization: take number of points into account.
* Adjust stacking in ``SinglePlotter2DStacked`` for data with larger minima than maxima.
* Templates for LaTeX dataset report: escape ``_`` and ``#`` in dataset label.
* Axis labels can be removed by setting one or both of ``xlabel`` and ``ylabel`` to ``None`` (or ``null`` in YAML/recipe).


Version 0.9.2
=============

Released 2024-03-24


Fixes
-----

* Revert changes in :class:`aspecd.utils.ToDictMixin` from version 0.9.1, as it caused problems with Matplotlib.
* Updates on contour plots to work with Matplotlib 3.8
* Updates to prevent deprecation warning for NumPy 1.25
* :class:`aspecd.processing.RangeExtraction` extracts correct range for axis values.


Version 0.9.1
=============

Released 2024-01-15


Fixes
-----

* :class:`aspecd.utils.ToDictMixin` does no longer modify the ``__dict__`` or ``__odict__`` property of a class directly, what may have resulted in unexpected behaviour, but operates on a (deep)copy.


Changes
-------

* Use Black for automatic code formatting


Version 0.9.0
=============

Released 2024-01-13


New features
------------

* Processing steps

  * :class:`aspecd.processing.CommonRangeExtraction` works for *N*\ D datasets with arbitrary dimension *N*

* Plotting

  * Legend title can be set from recipes

  * New attribute :attr:`aspecd.plotting.AxesProperties.invert` for inverting axes. Helpful, *e.g.*, for plotting FTIR data without having to resort to explicitly provide descending axis limits.

  * Setting font size of axes labels via ``label_fontsize`` property.

  * Colorbar for 2D plotter

  * Annotations for plots

    For details, see :ref:`the documentation of plot annotations <:sec:annotation:plot>` and the :mod:`aspecd.annotation` module.

* Device data

  * New property :attr:`aspecd.dataset.Dataset.device_data` for storing additional/secondary (monitoring) data.

  * New class :class:`aspecd.dataset.DeviceData` for device data.
  * New class :class:`aspecd.analysis.DeviceDataExtraction` for extracting device data from a dataset as a separate dataset. This allows to proceed with the extracted datasets as with any other dataset.
  * New class :class:`aspecd.plotting.MultiDeviceDataPlotter1D` for plotting multiple device data of a single dataset.

  * New parameter ``device_data`` in :class:`aspecd.plotting.Plotter` for plotting device data rather than primary data of a dataset/datasets

* Logging

  * New function :func:`aspecd.utils.get_logger` to get a logger object for a given module with the logger within the hierarchy of the ASpecD root logger. Important for packages derived from the ASpecD framework in order to get their log messages being captured, *e.g.* during recipe-driven data analysis.


Changes
-------

* Plotters can now handle device data instead of the primary data of a dataset (see above). This means, however, that instead of accessing ``self.dataset.data`` (or ``self.datasets[#].data``), plotters need to access ``self.data.data`` (or ``self.data[#].data``) instead.

  **Authors of derived packages should update their plotters accordingly.** See the :ref:`hints for developers on device data in the plotting module <sec:plotting:developers_data>`.

* Serving recipes logs messages from all ASpecD modules, not only from the :mod:`aspecd.tasks` module.

* :class:`aspecd.io.DatasetImporterFactory` logs warning if no concrete importer could be found for a given dataset, as this will usually result in (sometimes hard to detect) downstream problems.

* :class:`aspecd.io.DatasetExporter` adds a history record to :attr:`aspecd.dataset.Dataset.tasks`.

* :class:`aspecd.plotting.SinglePlotter1D` and :class:`aspecd.plotting.MultiPlotter1D` issue warning with log plotters and negative values.

* :class:`aspecd.annotation.DatasetAnnotation` has been renamed from ``Annotation`` to reflect the fact that there are now plot annotations as well.


Documentation
-------------

* New example: :doc:`Plotting FTIR spectra normalised to spectral feature <examples/ftir>`
* Section with :ref:`general tips and tricks for styling plotters <sec:plotting:tips_tricks>`.


Fixes
-----

* :meth:`aspecd.utils.ToDictMixin.to_dict` does not traverse settings for properties to exclude and include.
* Workaround for :meth:`matplotlib.figure.Figure.savefig` not correctly handling figure DPI settings.


Version 0.8.3
=============

Released 2023-09-08

Fixes
-----

* Exporter tasks (:class:`aspecd.tasks.ExportTask`) automatically save datasets with default name if no target is provided.
* Correct setting of contour plot properties with newer versions of Matplotlib


Changes
-------

* :class:`aspecd.processing.Interpolation` changed interpolation method for 2D data from deprecated :class:`scipy.interpolate.interp2d` to :class:`scipy.interpolate.RegularGridInterpolator`


New features
------------

* :class:`aspecd.processing.Interpolation` works for *N*\ D datasets with arbitrary dimension *N*
* :class:`aspecd.tasks.Recipe` with new setting ``autosave_datasets`` (default: ``True``)


Version 0.8.2
=============

Released 2023-08-24

Fixes
-----

* Handling of too long filenames when saving plots: the filename is replaced by its MD5 hash.


New features
------------

* New setting ``default_colormap`` in recipes.
* Property ``colormap`` in :class:`aspecd.plotting.SinglePlot2DProperties`, allowing for consistently setting (default) colormaps for 2D surface plots within a recipe.


Version 0.8.1
=============

Released 2023-08-11

Documentation
-------------

* New section on :doc:`metadata during data acquisition <metadata>`
* New section with :doc:`examples <examples/index>`
* New section with :doc:`data publications <examples/data-publications>`


Fixes
-----

* Baseline correction in :class:`aspecd.processing.BaselineCorrection` issues warning if more than 100% of the data are used and resets to 50% on each side.
* Recipe history contains importer parameters


Version 0.8.0
=============

Released 2023-03-26

New features
------------

* Plotting

  * MultiPlotter1D can use colormaps for coloring multiple lines
  * Number of columns can be set for legends of plots

* Processing steps

  * New class :class:`aspecd.processing.SliceRemoval` for removing slices from a ND dataset with N>1.
  * New class :class:`aspecd.processing.RelativeAxis` for converting an axis into a relative axis, centred about a (given) origin.


Fixes
-----

* Interpolation in :class:`aspecd.processing.Interpolation` works correctly if axis range is given and no corresponding axis point exists in the original dataset.


Version 0.7.1
=============

Released 2022-06-12

New features
------------

* Reference to publication in documentation and colophon of reports.


Version 0.7.0
=============

Released 2022-01-30


New features
------------

* :class:`aspecd.tasks.FigurereportTask` for creating figure captions that can, *e.g.*, be included in other documents
* Attributes ``labelspacing`` and ``fontsize`` in :class:`aspecd.plotting.LegendProperties`
* Attribute ``output`` in :class:`aspecd.tasks.ModelTask` controlling the type of output returned (dataset or model)
* Method :meth:`aspecd.model.Model.evaluate` for fast evaluation of models without any checks (useful in context of fitting)
* Attribute ``dataset_type`` in :class:`aspecd.analysis.AnalysisStep` to define type of calculated dataset that gets returned
* :class:`aspecd.plotting.MultiPlotter1D` and :class:`aspecd.plotting.MultiPlotter1DStacked` with parameter "tight" for tight axes and "switch_axes" for switching axes
* :class:`aspecd.plotting.SinglePlotter1D` with parameter "switch_axes" for switching axes
* :class:`aspecd.plotting.AxesProperties`: angles of the axes tick labels can be set using the ``xticklabelangle`` and ``yticklabelangle`` properties


Changes
-------

* :class:`aspecd.processing.SliceExtraction` sets dataset label to slice position
* :class:`aspecd.processing.Averaging` sets dataset label to averaging range


Fixes
-----

* Dataset importer does not override dataset label.
* AnalysisSteps assign data to _origdata attribute if result is dataset
* MultiprocessingTask correctly sets label of resulting datasets


Version 0.6.4
=============

Released 2021-11-25


Changes
-------

* New attribute ``comment`` in :class:`aspecd.tasks.Task`, :class:`aspecd.report.Reporter`, :class:`aspecd.plotting.Plotter`, :class:`aspecd.io.DatasetExporter` allowing for storing user-supplied comments


Fixes
-----

* Warnings issued during cooking of a recipe are now log messages.


Version 0.6.3
=============

Released 2021-11-24


Changes
-------

* :class:`aspecd.report.Reporter` adds template loader for package if :attr:`aspecd.report.Reporter.package` is provided, allowing to override templates from the ASpecD framework within derived packages.
* :class:`aspecd.tasks.ReportTask` passes through the default package from the recipe to the reporter for overriding templates.
* :class:`aspecd.infofile.Infofile`: Comment gets converted into a single string
* Dependency change: Jinja >= 3.0
* :class:`aspecd.io.TxtImporter` handles decimal separator different than dot


Fixes
-----

* :class:`aspecd.tasks.Task` warns if key in dict (recipe) is no property of the task.
* :class:`aspecd.processing.DatasetAlgebra` returns shape in error message if shapes differ.
* Processing and analysis tasks issue warning if result name is identical to dataset label
* Ensure window length for Savitzky-Golay filter in :class:`aspecd.processing.Filtering` to always be odd
* :class:`aspecd.processing.CommonRangeExtraction` ignores unit of last axis (*i.e.*, intensity) when checking for identical units
* :class:`aspecd.utils.ToDictMixin`: Added superclass call to preserve mro in dependent subclasses
* Tasks properly handle non-dataset results from recipe
* :class:`aspecd.plotting.MultiPlotter` sets axis labels when units are empty
* :class:`aspecd.processing.Normalisation` removes unit from last axis
* :class:`aspecd.processing.BaselineCorrection` handles zero values in range properly
* :class:`aspecd.analysis.AggregateAnalysisStep` no longer adds ``datasets`` and ``result`` to output of ``to_dict()``
* :class:`aspecd.tasks.AggregatedAnalysisTask` sets correct type in output of ``to_dict()``
* :class:`aspecd.tasks.ReportTask` does not add empty figure filenames to includes
* :class:`aspecd.Tasks.PlotTask` preserves labels of drawings
* Recipe history does not contain path to current directory in dataset source


Version 0.6.2
=============

Released 2021-11-16


Changes
-------

* New parameter ``ytickcount`` for :class:`aspecd.plotting.SinglePlotter2DStacked` to control maximum number of yticks
* New parameter ``tight_layout`` for :class:`aspecd.plotting.Plotter` to prevent labels from getting clipped


Fixes
-----

* Recipe containing a MultiplotTask does not contain datasets as dicts
* PlotTask with automatically generated filenames and >1 datasets writes correct filenames to figure record in recipe
* CompositePlotter sets plot style of plotters
* Grammar in ``dataset.tex`` template
* Colophon of report via ReportTask contains default package set in recipe
* CompositePlotter does not add plotters of subfigures to list of dataset representations and list of dataset tasks
* Escaping of "_" in LaTeX templates


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
