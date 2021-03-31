.. _use_cases:

=========
Use cases
=========

Usually, you will either use an existing package based on the ASpecD framework (such as `cwEPR <https://docs.cwepr.de/>`_ or `trEPR <https://docs.trepr.de/>`_) or :doc:`write your own package based on the ASpecD framework <applications>` for your data analysis. However, this section will give you an impression how *working* with such a package, and particulary with *recipe-driven data analysis* may look like – and why it is fun and will help you tremendously speed up your data analysis, while allowing for full reproducibility.


General usage
=============

The best tools will only get used if they are at least somewhat intuitively usable. One notable exception are tools such powerful and without viable alternative that a user will immediately see the advantages of getting used to a non-intuitive interface.

It is up to the users to decide whether the ASpecD framework is such a "best tool". It does, however, provide powerful functionality striving for fully reproducible data processing and analysis, while keeping the usage as simple as possible. Applications built on top of such a framework may revolutionise the way the average scientist looks at these fundamental aspects of science.

Currently, the main interface to the ASpecD framework and packages built upon it is the "**recipe-driven data analysis**":  the user writes "recipes" in form of human-readable YAML files telling the application which tasks to perform on what datasets. This allows for fully unattended, automated and scheduled processing of data, eventually including simulation and fitting. At the same time, it allows the user to analyse the data without need for actual programming. [#fn1]_

Actually, there are two steps to recipe-driven data analysis:

* Writing a recipe, specifying what tasks shall be performed to which datasets.

* Serving the recipe by typing a single command on the terminal.

To give you a first example, here is a short recipe, followed by the command you need to issue in the terminal:

.. code-block:: yaml
    :linenos:

    datasets:
      - /path/to/first/dataset
      - /path/to/second/dataset

    tasks:
      - kind: processing
        type: BaselineCorrection
        properties:
          parameters:
            kind: polynomial
            order: 0
      - kind: singleplot
        type: SinglePlotter
        properties:
          filename:
            - first-dataset.pdf
            - second-dataset.pdf

The details of what happens here with this recipe will be detailed below, but it should nevertheless be pretty self-explaining. Suppose you have saved this recipe to a YAML file named ``my-first-recipe.yaml``. Then the only thing you need to do to actually "serve" the recipe and get the figure created is issuing the following command in a terminal:

.. code-block:: bash

    serve my-first-recipe.yaml

If you wonder where the command ``serve`` comes from: This gets installed when you install the ASpecD Python package. Hence, it may only be available from within a Python virtual environment if you installed ASpecD this way (what is generally preferrable for Python packages).


Anatomy of a recipe
===================

Recipes always consist of two major parts: A list of datasets to operate on, and a list of tasks to be performed on the datasets. Of course, you can specify for each task on which datasets it should be performed, and if possible, whether it should be performed on each dataset separately or combined. The latter is particularly interesting for representations (e.g., plots) consisting of multiple datasets, or analysis steps spanning multiple datasets.

Therefore, in a recipe that is basically a YAML file, you will always find two keys on the highest level: ``datasets`` and ``tasks``. There are, however, a few additional (optional) keys that may appear on the highest level, setting such things as the :ref:`default package to use <specific_packages>` (for packages derived from ASpecD), the default source directory for datasets and the default output directory for figures and reports. A recipe written as history from cooking another recipe will additionally automatically contain information on the system and versions of the software packages used.


Importing datasets
==================

The first step in analysing data is to import them. In terms of recipe-driven data analysis, you only need to specify a unique identifier for your dataset, usually (for the time being) a (relative or absolute) path to a file accessible from your file system.

.. code-block:: yaml

    datasets:
      - /path/to/my/first/dataset
      - /path/to/my/second/dataset


At the same time, the paths are used to refer to the datasets internally within the recipe. Such references are frequently used if you want to perform a task not for all datasets, but only a subset of the datasets specified on top of a recipe. If you say now that always having to provide the full path to a dataset is error-prone and not user-friendly, stay tuned and continue reading: we got you covered.

A few comments on the syntax: ``datasets:`` is the key on the highest level, and the trailing colon ``:`` marks it as key (for a dictionary or associative array). The datasets are given as a list, using the leading minus ``-``. Whether you use tabs or spaces for indentation does not matter, as long as the indentation within one block is consistent. If you're not familiar with the YAML syntax, it is highly recommended to have a look on one of the many resources available online.


Absolute and relative paths
---------------------------

Generally, you can provide both, absolute and relative paths. In this documentation, we will always use UNIX-style paths, with the slash ``/`` as separator. A leading slash makes a path absolute.

If you specify relative paths, they will be relative to the current directory the recipe is cooked from, *i.e.* you call ``serve`` from, or relative to the datasets source directory specified at the beginning of the recipe. See below for details.


Specifying ID and label of datasets
-----------------------------------

At the time you list your datasets to operate on at the beginning of a recipe, you anyway focus on selecting the right datasets. Hence this is the time to specify additional settings for each individual dataset, such as an ID to refer to it throughout the recipe, and a label that will, *inter alia*, appear in a figure legend by default.

To specify additional settings for a dataset, you need to slightly alter the way you provide the datasets list in the recipe:

.. code-block:: yaml

    datasets:
      - source: /path/to/my/first/dataset
        id: first
        label: first overview
      - source: /path/to/my/second/dataset
        id: second
        label: correct parameters


So what happened here? We specified the source, ID, and label for each of the two datasets. The ``source`` is identical to the string shown earlier for the plain list of datasets. The ``id`` is the (unique) identifier the dataset can be referred to throughout the recipe. Of course, using IDs as shown here ("first", "second") is usually a bad idea, but as you will have a clear idea of what these datasets are, you can provide descriptive and meaningful IDs. The ``label`` provides a descriptive string usually appearing in a figure legend when multiple datasets are graphically represented. Depending on your package and the kind of metadata you tend to write upon acquiring data, datasets may come with a label. However, in the context of a recipe, you may want to change this label text according to your local needs.

Note that you need not specify all fields for all datasets. You can even mix plain lists with lists of dictionaries (*i.e.*, lists with key–value pairs, as shown in the example above). The only important thing to keep in mind: As soon as you start providing ``id`` or ``label`` keys, you *need to* provide a ``source`` key as well.


Importing datasets from other packages
--------------------------------------

Suppose you are using slightly different spectroscopic methods that each have their own Python package based on the ASpecD framework for data analysis, but you would like to compare the results of two of those datasets, *e.g.* in a single graphical representation.

So far, you did not need to care at all about the "magic" happening when cooking a recipe. You just rightly assumed that specifying a list of datasets will under the hood call out to the correct importer of the correct Python package. Don't worry, you need not care about the details now either. All you need to know is that if you would like to load datasets from different packages, you need to tell ASpecD within your recipe which package it should consult to import the dataset for you:

.. code-block:: yaml

    datasets:
      - source: /path/to/my/first/dataset
        id: cwepr
      - source: /path/to/my/second/dataset
        id: trepr
        package: trepr

In the above example, you're importing two datasets, and from the (optional) IDs, it is obvious that one is a dataset recorded using cw-EPR spectroscopy, while the other was recorded using tr-EPR spectroscopy. All you need to do to make ASpecD or your respective package (here: cwepr) to import the second dataset is to tell it the Python package name. As long as the package exists and is installed locally (and follows the basic layout of the ASpecD framework), everything should work well.


Setting the datasets source directory
-------------------------------------

Having a place for all your data is often a rather good idea. Usually, this place will be a single directory on your hard drive, with an arbitrary number and hierarchically organised subdirectories. Sometimes the data you want to analyse reside all in a single directory. In both cases, it can be quite convenient (and dramatically shortens) the paths you need to specify in the ``datasets:`` block of your recipe if you could tell ASpecD this common datasets source directory. Here you go:

.. code-block:: yaml

    datasets_source_directory: /path/to/all/my/datasets/

    datasets:
      - first-dataset
      - second-dataset

In this simple example we have specified an absolute path as datasets source directory, and all datasets are imported relative to this path.

You can, however, provide a relative path for the datasets source directory. Beware that the location of your recipe(s) may change, breaking relative paths, while providing absolute paths will work only as long as the (central) place for your datasets does not change (and is the same for all the computers you are working at).

Similarly, you can provide relative paths for the actual datasets that are relative to the source directory specified above. This is most convenient if you happen to have a hierarchical directory structure for your data and would like to set the common part as datasets source directory.


Operating on datasets
=====================

Different operations can be performed on datasets, and the ASpecD framework distinguishes between processing and analysis tasks, for starters. The first will operate directly on the data of the dataset, alter them accordingly, and result in an altered dataset. The second will operate on the data of a dataset as well, but return an independent result, be it a scalar, a vector, or even a (new) dataset.

Operations on datasets are defined within the ``tasks:`` block of a recipe, like so:

.. code-block:: yaml

    tasks:
      - kind: processing
        type: BaselineCorrection
        properties:
          parameters:
            kind: polynomial
            order: 0


Things to add:

* example for an analysis step
* description of how to set properties

  (and where to find documentation which properties can be set)
* applying a task to only a subset of the datasets loaded
* storing results in variables and accessing results afterwards


Can we see something?
=====================

One of the strengths of recipe-driven data analysis is that it can run fully unattended in the background or on some server even not having any graphical display attached. However, data analysis always yields some results we would like to look at. Here, two general options are provided by the ASpecD framework:

* representations (*e.g.*, plots)
* reports


.. code-block:: yaml

    tasks:
      - kind: singleplot
        type: SinglePlotter
        properties:
          filename:
            - first-dataset.pdf
            - second-dataset.pdf


Things to add:

* Setting properties for plots
* Different kinds of plots
* Reports
* Setting default output directory


.. _specific_packages:

Working with specific packages
==============================

While the ASpecD framework comes with an increasing list of processing and analysis steps, besides providing all the machinery necessary for fully reproducible data analysis, you will usually work with packages derived from the ASpecD framework and dedicated to your specific spectroscopic method at hand.

To make it possible to use the ``serve`` command on the terminal provided by the ASpecD framework even for your own packages, you need to specify which package to use for cooking and serving the recipe – best done at the very beginning of your recipe:

.. code-block:: yaml

    default_package: cwepr

In this case, the ``cwepr`` package will be used for importing datasets and performing all tasks, as long as you don't specify other package for a particular dataset or task. Of course, you need to make sure that the Python package specified here exists and is installed locally when serving such a recipe. Furthermore, the Python package needs to fulfil all the requirements of an ASpecD-derived package to allow for recipe-driven data analysis.


.. rubric:: Footnotes

.. [#fn1] Interactive command-line (CLI) and graphical user interfaces (GUI) are an entirely different story, requiring a whole set of different skills and knowledge about concepts of software architecture developed within the last decades. However, the ASpecD framework provides the solid ground to build such interfaces upon. In terms of an overall software architecture, the ASpecD framework and the concepts contained form the inner core of an application for scientific data processing and analysis. User interfaces, similar to persistence layers, are outer layers the core does not know nor care about.