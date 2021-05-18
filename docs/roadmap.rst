=======
Roadmap
=======

A few ideas how to develop the project further, currently a list as a reminder for the main developers themselves, in no particular order, though with a tendency to list more important aspects first:


For version 0.2
===============

* Add Zenodo badge to start page of documentation in release

* Plot task: default filename for saved figure


For version 0.3
===============

* Remaining basic processing and analysis steps:

  * denoising
  * adding noise
  * ? AxisAlgebra: provide a function that gets evaluated on the values of an axis
  * Interpolation

    * for ND with N>2
    * different types of interpolation

  * BlindSNREstimation with alternative methods
  * SNREstimation with explicitly providing noise (using both, processing and analysis)

* Expand use cases: reports



For later versions
==================

* Recipes: Subrecipes that can be included in recipes

* Report task: Add figure captions to context if available

* Reporter: Method for adding dict representations of datasets to context

* Report task: Operating on recipes, *i.e.* report on all tasks in a recipe

* Report task: Adding arbitrary dict representations of properties of datasets/results to context

* Default report templates for each type of processing/analysis task

  Includes deciding where to store these templates, whether to have them stored in different directories for different languages, and alike. Ideally, templates should be copied to a user-accessible directory for modifying there.

* Templates for creating derived packages

* Logging

* Tabular representations of characteristics extracted from datasets

* Plotter: Factory to create single plots of each given dataset. Probably needs a way to create default filenames (e.g. label + date?).


Todos
=====

A list of todos, extracted from the code and documentation itself, and only meant as convenience for the main developers. Ideally, this list will be empty at some point.

.. todolist::

