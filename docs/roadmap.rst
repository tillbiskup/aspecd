=======
Roadmap
=======

A few ideas how to develop the project further, currently a list as a reminder for the main developers themselves, in no particular order, though with a tendency to list more important aspects first:


For version 0.2
===============

* Add Zenodo badge to start page of documentation in release

* Full list of required packages (including their installed versions) in SystemInfo, to be included in history (and recipe history)

* Remaining basic processing and analysis steps:

  * interpolation (useful as well for reducing knots of a grid for 3D plots)
  * peak finding
  * SNR determination
  * denoising
  * filtering
  * adding noise
  * ? AxisAlgebra: provide a function that gets evaluated on the values of an axis

* :meth:`aspecd.processing.ProcessingStep._set_defaults()` method called before :meth:`aspecd.processing.ProcessingStep._sanitise_parameters`

* Importer with parameters in recipe (*e.g.*, for CSV importer)

* Expand use cases

* Plot task: default filename for saved figure


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

