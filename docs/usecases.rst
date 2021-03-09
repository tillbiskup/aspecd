=========
Use cases
=========

Usually, you will either use an existing package based on the ASpecD framework (such as `cwEPR <https://docs.cwepr.de/>`_ or `trEPR <https://docs.trepr.de/>`_) or :doc:`write your own package based on the ASpecD framework <applications>` for your data analysis. However, this section will give you an impression how *working* with such a package, and particulary with *recipe-driven data analysis* may look like – and why it is fun and will help you tremendously speed up your data analysis, while allowing for full reproducibility.


.. important::
    The following section needs complete rewrite, as it predates the full implementation of recipe-driven data analysis. Once done, it will include a series of simple and not so simple tasks routinely occurring during scientific data analysis that can be performed with the functionality provided by the ASpecD framework.


General usage
=============

The best tools will only get used if they are at least somewhat intuitively usable. One notable exception are tools such powerful and without viable alternative that a user will immediately see the advantages of getting used to a non-intuitive interface.

The ASpecD framework may not be such a "best tool". It does, however, provide powerful functionality striving for fully reproducible data processing and analysis. Applications built on top of such a framework may revolutionise the way the average scientist looks at these fundamental aspects of science.

For the time being, the ASpecD framework focusses on fully developing these underlying concepts, not on user interfaces. Therefore, the standard way of using applications based on the ASpecD framework will be to manually create the different objects and interact with them either in a script or on the interactive command line.

With the advent of "recipe-driven data analysis" this restriction will be lifted. Here, the user will be able to write "recipes" in form of human-readable YAML files telling the application which tasks to perform on what datasets. This allows for fully unattended, automated and scheduled processing of data, eventually including simulation and fitting.

Interactive command-line (CLI) and graphical user interfaces (GUI) are an entirely different story, requiring a whole set of different skills and knowledge about concepts of software architecture developed within the last decades. However, the ASpecD framework provides the solid ground to build such interfaces upon. In terms of an overall software architecture, the ASpecD framework and the concepts contained form the inner core of an application for scientific data processing and analysis. User interfaces, similar to persistence layers, are outer layers the core does not know nor care about.


Importing datasets
==================

The first step in analysing data is to import them. In terms of recipe-driven data analysis, you only need to specify a unique identifier for your dataset, usually (for the time being) a path to a file accessible from your file system.

.. code-block:: yaml

    datasets:
      - /path/to/my/first/dataset
      - /path/to/my/second/dataset


Things to add:

* specifying id and label
* importing datasets from other packages


Operating on datasets
=====================

Different operations can be performed on datasets, and the ASpecD framework distinguishes between processing and analysis tasks, for starters. The first will operate directly on the data of the dataset, alter them accordingly, and result in an altered dataset. The second will operate on the data of a dataset as well, but return an independent result, be it a scalar, a vector, or even a (new) dataset.

Operations on datasets are defined within the ``tasks:`` block of a recipe, like so:

.. code-block:: yaml

    tasks:
      - kind: processing
        type: SubtractBaseline
        properties:
          parameters:
            kind: polynomial
            order: 0


Things to add:

* example for an analysis step
* description of how to set properties
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
