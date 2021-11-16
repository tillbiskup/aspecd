=======
Roadmap
=======

A few ideas how to develop the project further, currently a list as a reminder for the main developers themselves, in no particular order, though with a tendency to list more important aspects first:


For version 0.7
===============

* Report task:

  * Operating on recipes, *i.e.* report on all tasks in a recipe
  * Adding arbitrary dict representations of properties of datasets/results to context

* Recipes: Subrecipes that can be included in recipes

* Reports:

  * LaTeXFigureReporter for generating LaTeX code to include figures in documents
  * Looking for templates in derived packages
  * Looking for templates in user directory

* Processing of 2D (eventually ND with N>1) datasets:

  * Projecting/averaging excluding certain lines (due to artifacts from external noise sources or else)
  * Combining a list of 1D datasets to a 2D dataset (reverse operation of SliceExtraction)


For later versions
==================

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

