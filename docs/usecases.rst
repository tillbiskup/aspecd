=========
Use cases
=========

Whereas the section on :doc:`writing applications based on the ASpecD framework <applications>` gave a first impression of how to use the ASpecD framework for own analysis software, this section provides a few ideas of how basic operation of applications based on the ASpecD framework may look like.


General usage
=============

The best tools will only get used if they are at least somewhat intuitively usable. One notable exception are tools such powerful and without viable alternative that a user will immediately see the advantages of getting used to a non-intuitive interface.

The ASpecD framework may not be such a "best tool". It does, however, provide powerful functionality striving for fully reproducible data processing and analysis. Applications built on top of such a framework may revolutionise the way the average scientist looks at these fundamental aspects of science.

For the time being, the ASpecD framework focusses on fully developing these underlying concepts, not on user interfaces. Therefore, the standard way of using applications based on the ASpecD framework will be to manually create the different objects and interact with them either in a script or on the interactive command line.

With the advent of "recipe-driven data analysis" this restriction will be lifted. Here, the user will be able to write "recipes" in form of human-readable YAML files telling the application which tasks to perform on what datasets. This allows for fully unattended, automated and scheduled processing of data, eventually including simulation and fitting.

Interactive command-line (CLI) and graphical user interfaces (GUI) are an entirely different story, requiring a whole set of different skills and knowledge about concepts of software architecture developed within the last decades. However, the ASpecD framework provides the solid ground to build such interfaces upon. In terms of an overall software architecture, the ASpecD framework and the concepts contained form the inner core of an application for scientific data processing and analysis. User interfaces, similar to persistence layers, are outer layers the core does not know nor care about.

Having said that, the following examples will---for the time being---show how to use applications based on the ASpecD framework in the most basic way, i.e., creating the respective objects by hand and let them interact.


Conventions used
================

To give somewhat sensible examples without restricting the imagination of the user, we assume throughout this section that the user has created or available an application for processing and analysing spectroscopic data that is called ``spectro``. The corresponding Python package shares this name as well and is assumed to be installed within a virtual environment the user works with.


Create a dataset and import data
================================

Most probably, the first step when processing and analysing data will be to actually import data into a dataset by using an importer.::

    import spectro

    dataset_ = dataset.Dataset()
    importer = io.Importer(source="path/to/some/file/containing/data")

    dataset_.import_from(importer)

This will import the data (and metadata) contained in the path provided to the argument ``source`` when instantiating the ``Importer`` object.

A few comments on these few lines of code:

* Naming the dataset object ``dataset_`` prevents shadowing the module name. Feel free to give it another equally fitting name. Appending an underscore to a variable name in such case is a common solution complying to `PEP 8 <https://www.python.org/dev/peps/pep-0008/>`_.

* Always define first an instance of the dataset class, and afterwards use the public methods of this object, such as ``import_from()`` or ``process()``.

