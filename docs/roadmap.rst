=======
Roadmap
=======

A few ideas how to develop the project further, currently a list as a reminder for the main developers themselves, in no particular order, though with a tendency to list more important aspects first:


For version 0.1
===============

* Metadata mapper via yaml file

* Documentation: Use cases

* Plotter: Handle multiple axes (cwepr:GoniometerPlotter)

* Plotter: Handle (cascaded) properties for all parts of a plot

* Models as classes returning calculated datasets for given coefficients and variables

  Come in quite handy if one wants to obtain, say, the values of a polynomial for given coefficients, to plot it together with other data. Can (and will) be generalised to many more models, eventually probably becoming a base for simulations of all kinds. Will be quite useful for testing purposes as well.


For later versions
==================

* Remaining basic processing and analysis steps, such as baseline correction, algebra with datasets, slice extraction for >2D datasets, averaging (over parts of axis) for N-D datasets, peak finding, SNR determination, denoising, filtering, noise

* Templates for creating derived packages

* Default report templates for each type of processing/analysis task

* Logging

* Tabular representations of characteristics extracted from datasets


Todos
=====

A list of todos, extracted from the code and documentation itself, and only meant as convenience for the main developers. Ideally, this list will be empty at some point.

.. todolist::

