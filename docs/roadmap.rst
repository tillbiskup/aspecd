=======
Roadmap
=======

A few ideas how to develop the project further, currently a list as a reminder for the main developers themselves, in no particular order, though with a tendency to list more important aspects first:


For version 0.3
===============

* Remaining basic processing and analysis steps:

  * denoising

  * SNREstimation with explicitly providing noise (using both, processing and analysis)

* References in processing and analysis steps?

  * May be useful to automatically create a list of references to cite (report) depending on the methods actually used.
  * May need an implementation of some kind of bibliographic record


For version 0.4
===============

* Reporter: Method for adding dict representations of datasets to context

* Report task:

  * Add figure captions to context if available
  * Operating on recipes, *i.e.* report on all tasks in a recipe
  * Adding arbitrary dict representations of properties of datasets/results to context

* Default report templates for each type of processing/analysis task

  Includes deciding where to store these templates, whether to have them stored in different directories for different languages, and alike. Ideally, templates should be copied to a user-accessible directory for modifying there.

* Expand use cases: reports

* Recipes: Subrecipes that can be included in recipes

* Interfacing towards fitting/simulation frameworks

* Basic maths in values of recipes (ranges, basic numpy functions)?

  May impair the platform-independence of the recipe (*i.e.*, tying it to Python/NumPy)


For later versions
==================

* Interpolation

  * for ND with N>2
  * different types of interpolation

* Templates for creating derived packages

* Logging

* Tabular representations of characteristics extracted from datasets

* Plotter: Factory to create single plots of each given dataset.


Todos
=====

A list of todos, extracted from the code and documentation itself, and only meant as convenience for the main developers. Ideally, this list will be empty at some point.

.. todolist::

