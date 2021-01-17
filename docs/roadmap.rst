=======
Roadmap
=======

A few ideas how to develop the project further, currently a list as a reminder for the main developers themselves, in no particular order, though with a tendency to list more important aspects first:


For version 0.1
===============

* Plotter: Implement MultiPlotter1D

* Plotter: Handle multiple axes (cwepr:GoniometerPlotter) - via SingleCompositePlotter

* Plotter: Handle (cascaded) properties for all parts of a plot

* Metadata mapper via yaml file

* Documentation: Use cases

* Documentation: YAML representation of dataset structure(s)


For later versions
==================

* Remaining basic processing and analysis steps, such as baseline correction, algebra with datasets, slice extraction for >2D datasets, averaging (over parts of axis) for N-D datasets, peak finding, SNR determination, denoising, filtering, noise

* Reporter: Method for adding dict representations of datasets to context

* Reporter task: Operating on recipes, *i.e.* report on all tasks in a recipe

* Reporter task: Adding arbitrary dict representations of properties of datasets/results to context

* Templates for creating derived packages

* Default report templates for each type of processing/analysis task

  Includes deciding where to store these templates, whether to have them stored in different directories for different languages, and alike. Ideally, templates should be copied to a user-accessible directory for modifying there.

* Logging

* Tabular representations of characteristics extracted from datasets


Todos
=====

A list of todos, extracted from the code and documentation itself, and only meant as convenience for the main developers. Ideally, this list will be empty at some point.

.. todolist::

