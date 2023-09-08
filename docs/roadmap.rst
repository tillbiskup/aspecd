=======
Roadmap
=======

A few ideas how to develop the project further, currently a list as a reminder for the main developers themselves, in no particular order, though with a tendency to list more important aspects first:


For version 0.9
===============

* Usability

  * Importer/ImporterFactory should issue a warning if no dataset could be loaded, rather than silently continuing, as this often leads to downstream problems and exceptions thrown.

* Plotting

  * Colorbar for 2D plotter
  * (Arbitrary) lines in plot, *e.g.* to compare peak positions

    Need to decide whether this goes into plotter properties or gets handled as proper annotations; probably the former, but a good starting point to think about the latter.
  * If figure is plotted twice using automatically generated filenames, use different filenames (e.g. increment number).
  * Axis direction can be switched (*e.g.*, for FTIR data, hence not needing to set axis limits in reverse order)
  * Bugfix: Title of figure and axis label overlap when adding an axis on the top side of the figure

* Processing

  * CombineDatasets: combine data from several datasets into a single dataset; parameters allowing to define the axis values/quantity/unit, possibly even from given metadata; to decide: How to handle metadata that might be invalidated?

  * MetadataUpdate/MetadataChange: Change metadata of a given dataset from within a recipe. Useful in case datasets contain (known) spurious or otherwise inappropriate metadata. (Metadata are provided manually and are therefore prone to human errors).

  * :class:`aspecd.processing.BaselineCorrection` with ``fit_area`` definable as axis range, and arbitrary parts of the axis (*e.g.*, in the middle of a dataset or with separate fit areas)

* Logging

  * Add loggers from other modules (than task) and derived packages

    Probably this means to switch to package-wide logging and documenting that derived packages need to log to the ASpecD logger as well.

* Add export tasks to dataset tasks

* Recipe-driven data analysis:

  * Better handling of automatically generated filenames for saving plots and reports: unique filenames; using the label rather than the source (id) of the dataset

  * Handling of results: automatically add datasets to dataset list? How to deal with result labels identical to existing datasets?

  * Sub-recipes that can be included in recipes

    Allows for creating a library of recipes for rather complex tasks that can simply be called as single step from another recipe

* Report task:

  * Operating on recipes, *i.e.* report on all tasks in a recipe
  * Adding arbitrary dict representations of properties of datasets/results to context

* Reports:

  * Looking for templates in user directory

* Documentation:

  * How to debug a recipe?

  * Better document command-line options of the "serve" command


For later versions
==================

* Convert from :class:`collections.OrderedDict` to :class:`dict`, as starting with Python 3.7, dicts preserve the insertion-order of the keys.

* Plot styles

  * user-defined styles

* Annotations

  * graphical annotations for characteristic points (and distances, areas?)

* Remaining basic processing and analysis steps:

  * denoising (via SVD or similar)

  * SNREstimation with explicitly providing noise (using both, processing and analysis)

* Interpolation

  * different types of interpolation

* Templates for creating derived packages

* Plotter: Factory to create single plots of each given dataset.

* Basic maths in values of recipes (ranges, basic numpy functions)?

  May impair the platform-independence of the recipe (*i.e.*, tying it to Python/NumPy)


Todos
=====

A list of todos, extracted from the code and documentation itself, and only meant as convenience for the main developers. Ideally, this list will be empty at some point.

.. todolist::

