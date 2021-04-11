=======
Roadmap
=======

A few ideas how to develop the project further, currently a list as a reminder for the main developers themselves, in no particular order, though with a tendency to list more important aspects first:


For version 0.1
===============

* Plotter: CompositePlotter - better handling of properties

* Report task: Add figure captions to context if available

* Documentation: Use cases

* Documentation: YAML representation of dataset structure(s) (automatically generated together with the documentation and using the ``literalinclude`` directive)


For later versions
==================

* Remaining basic processing and analysis steps, such as algebra with datasets, slice extraction for >2D datasets, peak finding, SNR determination, denoising, filtering, noise, cut dataset and axis (to common range)

* Normalising over parts of a dataset

* :meth:`aspecd.processing.ProcessingStep._set_defaults()` method called before :meth:`aspecd.processing.ProcessingStep._sanitise_parameters`

* Reporter: Method for adding dict representations of datasets to context

* Report task: Operating on recipes, *i.e.* report on all tasks in a recipe

* Report task: Adding arbitrary dict representations of properties of datasets/results to context

* Default report templates for each type of processing/analysis task

  Includes deciding where to store these templates, whether to have them stored in different directories for different languages, and alike. Ideally, templates should be copied to a user-accessible directory for modifying there.

* Importer with parameters in recipe (*e.g.*, for CSV importer)

* Templates for creating derived packages

* Logging

* Tabular representations of characteristics extracted from datasets

* Plotter: Factory to create single plots of each given dataset. Probably needs a way to create default filenames (e.g. label + date?).


Todos
=====

A list of todos, extracted from the code and documentation itself, and only meant as convenience for the main developers. Ideally, this list will be empty at some point.

.. todolist::

