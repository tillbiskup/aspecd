=======
Roadmap
=======

A few ideas how to develop the project further, currently a list as a reminder for the main developers themselves, in no particular order, though with a tendency to list more important aspects first:


For version 0.11
================

* Plotting

  * Plot annotations

    * Text annotations with additional lines/arrows
    * additional types of annotations, *e.g.* ``axvspan``, ``axhspan``, symbols

* Example recipes

  * A series of example recipes, starting with models for generating artificial data.
  * Show-off of different plotters and the possibilities there.


For next releases
=================

* Plotting

  * Support for device data (via `self.data`) in :class:`aspecd.plotting.CompositePlotter` and derived classes

  * :class:`aspecd.plotting.MultiDeviceDataPlotter1DStacked`

    Similar to :class:`aspecd.plotting.MultiDeviceDataPlotter1D`, but stacked display of the individual lines as in :class:`aspecd.plotting.SinglePlotter2DStacked`

  * :class:`aspecd.plotting.MultiDeviceDataPlotter1DSeparated`

    Similar to :class:`aspecd.plotting.MultiDeviceDataPlotter1D`, but with the different device data plotted in separate axes stacked vertically

  * Quiver plots

    https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.quiver.html

* Processing

  * DatasetCombination: combine data from several datasets into a single dataset; parameters allowing to define the axis values/quantity/unit, possibly even from given metadata; to decide: How to handle metadata that might be invalidated?

  * MetadataUpdate/MetadataChange: Change metadata of a given dataset from within a recipe. Useful in case datasets contain (known) spurious or otherwise inappropriate metadata. (Metadata are provided manually and are therefore prone to human errors).

  * :class:`aspecd.processing.BaselineCorrection` with ``fit_area`` definable as axis range, and arbitrary parts of the axis (*e.g.*, in the middle of a dataset or with separate fit areas)

* Recipe-driven data analysis:

  * Tasks can be "recycled" with only few properties changed.

    * Most useful, probably, for plots where you want to change, *e.g.*, the title of a more complex plot for individual datasets, but don't want to copy&paste the plotting task in the recipe for each dataset independently. (`#4 <https://github.com/tillbiskup/aspecd/issues/4>`_)

  * Better handling of automatically generated filenames for saving plots and reports: unique filenames; using the label rather than the source (id) of the dataset

  * If figure is plotted twice using automatically generated filenames, use different filenames (e.g. increment number).

   Points towards reworking the :class:`aspecd.plotting.Saver` class, allowing for an additional optional parameter ``suffix`` or else. Would make handling too long filenames easier as well.

  * Handling of results: automatically add datasets to dataset list? How to deal with result labels identical to existing datasets?

  * Sub-recipes that can be included in recipes

    Allows for creating a library of recipes for rather complex tasks that can simply be called as single step from another recipe

  * Static (syntax) checker for recipes prior to their execution

* Report task:

  * Operating on recipes, *i.e.* report on all tasks in a recipe
  * Adding arbitrary dict representations of properties of datasets/results to context

* Reports:

  * Looking for templates in user directory

* Documentation:

  * More developer documentation providing hints and "best practices" for how to develop classes either in ASpecD or in derived packages.

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

