=======
Roadmap
=======

A few ideas how to develop the project further, currently a list as a reminder for the main developers themselves, in no particular order, though with a tendency to list more important aspects first:


For version 0.8
===============

* Plotting

  * Colorbar for 2D plotter

  * colormaps for multiple lines

* Processing

  * ExtractSlices (plural): extract several slices from a dataset and combine them in a new dataset

  * CombineDatasets: combine data from several datasets into a single dataset; parameters allowing to define the axis values/quantity/unit, possibly even from given metadata; to decide: How to handle metadata that might be invalidated?

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

* Processing of 2D (eventually ND with N>1) datasets:

  * Projecting/averaging excluding certain lines (due to artifacts from external noise sources or else)
  * Combining a list of 1D datasets to a 2D dataset (reverse operation of SliceExtraction)


For later versions
==================

* Get rid of OrderedDict instances, as Python preserves order in dictionaries since version 3.6

* Plot styles

  * Switch in recipe settings for applying a style to all plots
  * user-defined styles

* Annotations

  * graphical annotations for characteristic points (and distances, areas?)

* Remaining basic processing and analysis steps:

  * denoising (via SVD or similar)

  * SNREstimation with explicitly providing noise (using both, processing and analysis)

* Interpolation

  * for ND with N>2
  * different types of interpolation

* Templates for creating derived packages

* Plotter: Factory to create single plots of each given dataset.

* Basic maths in values of recipes (ranges, basic numpy functions)?

  May impair the platform-independence of the recipe (*i.e.*, tying it to Python/NumPy)

* Convert from :class:`collections.OrderedDict` to :class:`dict`, as starting with Python 3.7, dicts preserve the insertion-order of the keys.


Todos
=====

A list of todos, extracted from the code and documentation itself, and only meant as convenience for the main developers. Ideally, this list will be empty at some point.

.. todolist::

