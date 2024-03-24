.. _use_cases:

=========
Use cases
=========

.. sidebar:: Contents

    .. contents::
        :local:
        :depth: 1

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

    format:
      type: ASpecD recipe
      version: '0.2'

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
        type: SinglePlotter1D
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

Therefore, in a recipe that is basically a YAML file, you will always find two keys on the highest level: ``datasets`` and ``tasks``.


.. code-block:: yaml

    datasets:
      - ...

    tasks:
      - ...


But what about the first block shown in the first example, the top-level ``format`` key? Let's have a look at it again:


.. code-block:: yaml

    format:
      type: ASpecD recipe
      version: '0.2'


This first block of every ASpecD recipe simply describes the file format, *e.g.* an ASpecD recipe, and the version of the format. Note that regardless of the package based on the ASpecD framework, the format type will always be "ASpecD recipe" (at least for the time being), and the version number is *independent* of the version number of the ASpecD framework or any derived package, but is an independent version number of the recipe file format as such.

Besides the two essential blocks (datasets and tasks) mentioned above, a few additional (optional) keys may appear on the highest level, setting such things as the :ref:`default package to use <specific_packages>` (for packages derived from ASpecD), the default source directory for datasets and the default output directory for figures and reports.


.. code-block:: yaml

    settings:
      default_package:
      autosave_plots: true
      write_history: true

    directories:
      output:
      datasets_source:

    datasets:
      - ...

    tasks:
      - ...


A recipe written as history from cooking another recipe will additionally automatically contain information on the system and versions of the software packages used. Note that this additional information is automatically obtained. Below is a slightly modified output from a real recipe history:


.. code-block:: yaml

    info:
      start: 'YYYY-MM-DDThh:mm:ss'
      end: 'YYYY-MM-DDThh:mm:ss'

    system_info:
      python:
        version: "3.7.3 (default, Jan 22 2021, 20:04:44) \n[GCC 8.3.0]"
      packages:
        aspecd: 0.4.0
        jinja2: 2.11.2
        matplotlib: 3.3.3
        numpy: 1.19.5
        scipy: 1.5.4
        oyaml: '1.0'
        asdf: 2.7.1
        bibrecord: 0.1.0
      platform: Linux-4.19.0-17-amd64-x86_64-with-debian-10.10
      user:
        login: <username>

    format:
      type: ASpecD recipe
      version: '0.2'

    settings:
      default_package:
      autosave_plots: true
      write_history: true

    directories:
      output:
      datasets_source:

    datasets:
      - ...

    tasks:
      - ...

Such a recipe history can directly be used as a new recipe, hence you get full reproducibility and always know what exactly you have done with your data.


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

    directories:
      datasets_source: /path/to/all/my/datasets/

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


You can see already the general structure of how to define a task as well as a number of important aspects. Tasks are items in a list, hence the prepending ``-``. Furthermore, for each task, you need to provide both, kind and type. Usually, the "kind" is identical to the (ASpecD) module the respective class used to perform the task is located in, such as "processing". There are, however, special cases where you need to be more specific, as in cases of plots (more later). The "type" always refers to the class name of the object eventually used to perform the task.

Another aspect shown already in the example above is how to set properties for the individual tasks using the "properties" keyword. Which properties you can set depends on the particular type of task and can be found in the API documentation. In the example given above, you set the "parameters" property of the :obj:`aspecd.processing.BaselineCorrection` object.


Applying a task to only a subset of the datasets loaded
-------------------------------------------------------

One particular strength of recipe-driven data analysis is its simple approach to operating on and comparing multiple datasets. Simply provide a list of datasets at the beginning of a recipe and work on them afterwards.

Often, however, you would like to restrict a certain task to a subset of the datasets loaded within the recipe. This is fairly easy as well, as every task as the ``apply_to`` keyword for exactly this purpose:

.. code-block:: yaml

    datasets:
      - dataset
      - another_dataset

    tasks:
      - kind: processing
        type: BaselineCorrection
        properties:
          parameters:
            kind: polynomial
            order: 0
        apply_to:
          - dataset


In this case, the task is only applied to the first dataset loaded. If you work with several datasets, it is most convenient to work with expressive labels that you can specify for each dataset individually (see above for details).


Storing results in variables and accessing results
--------------------------------------------------

Some tasks return results, and you usually want to refer to these results later in your recipe. Analysis steps will always yield results, but sometimes you would like to work on a copy of a dataset upon processing rather than modifying the original dataset, as would be normal for processing steps. In any case, simply provide a label with the key ``result``.

.. code-block:: yaml

    tasks:
      - kind: processing
        type: BaselineCorrection
        properties:
          parameters:
            kind: polynomial
            order: 0
        result: baseline_corrected_dataset


You can refer to these results in the same way as you can refer to datasets, even using the labels in the ``apply_to`` field of a following task.

Storing the result becomes particularly important if the task is not a processing step, but an analysis step, as the latter does not result in an altered dataset. A simple example would be determining the signal-to-noise ratio of the data:

.. code-block:: yaml

    tasks:
      - kind: singleanalysis
        type: BlindSNREstimation
        result: SNR


Note that in case of analysis steps, you need to explicitly tell whether you use an analysis step operating on individual datasets (as in this example, kind: ``singleanalysis``) or an analysis step operating on a list of datasets at once (kind: ``multianalysis``). In case of processing steps, as long as you want to operate on individual datasets, giving ``processing`` as kind will always work.

The type of the result returned by an analysis step depends on the particular analysis step performed and possibly the parameters given. Some analysis steps can return either a (calculated) dataset or some other type. One example would be peak finding:

.. code-block:: yaml

    tasks:
      - kind: singleanalysis
        type: PeakFinding
        result: peaks

In this case, the result is a list of peaks. If, however, you would like to get a calculated dataset, provide the appropriate parameter:

.. code-block:: yaml

    tasks:
      - kind: singleanalysis
        type: PeakFinding
        properties:
          parameters:
            return_dataset: True
        result: peaks

Now, the result will be a calculated dataset, and in this particular case, this can be quite helpful for plotting both, the original data and the detected peaks highlighted on top. As peak finding is often rather tricky, visual inspection of the results is usually necessary.


Can we see something?
=====================

One of the strengths of recipe-driven data analysis is that it can run fully unattended in the background or on some server even not having any graphical display attached. However, data analysis always yields some results we would like to look at. Here, two general options are provided by the ASpecD framework:

* representations (*e.g.*, plots)
* reports

While graphical representations, *i.e.* plots, are fully covered by the ASpecD framework, reports usually need a bit more work and contribution from the user due to their underlying complexity. Here, we will focus mostly on plots.


Graphical representation: a simple plot
---------------------------------------

The importance of graphical representations for data processing and analysis cannot be overestimated. Hence, a typical use case is to generate plots of a dataset following individual processing steps such as baseline correction. As recipes work in a non-interactive mode, saving these plots to files is a prerequisite. The most simple and straight-forward graphical representation would be defined in a recipe as follows:

.. code-block:: yaml

    tasks:
      - kind: singleplot
        type: SinglePlotter1D
        properties:
          filename:
            - dataset.pdf

This will create a simple plot of a single one-dimensional dataset using default settings and store the result to the file ``dataset.pdf``. Of course, you can apply the same plotting step to a series of datasets. As long as the list of datasets the plotter is employed for matches the number of filenames provided, everything should work smoothly:

.. code-block:: yaml

    datasets:
      - dataset
      - another_dataset

    tasks:
      - kind: singleplot
        type: SinglePlotter1D
        properties:
          filename:
            - first_dataset.pdf
            - second_dataset.pdf


Remember that you can use the key ``apply_to`` for any task to restict the list of datasets it is applied to, that you can set these labels for the datasets, and that you can refer to results labels as well.


Setting properties for plots
----------------------------

Plots are, compared to processing and analysis steps, highly complex tasks, probably only beaten by reports. There are literally zillions of properties you can explicitly set for a plot (or implicitly assume), such as line colours, widths, and styles, axes labels, and much more.

Some aspects eternalised in the `"Zen of Python" <https://www.python.org/dev/peps/pep-0020/>`_ can be applied to graphical representations in general and to defining them in context of a framework for data analysis in particular:

  | Explicit is better than implicit.
  | Simple is better than complex.
  | Complex is better than complicated.

Therefore, ASpecD allows you to set pretty many parameters of a plot explicitly, resulting in quite lengthly recipes if used excessively. This gives you fine-grained control over the look and feel of your plots and aims at a maximum of reproducibility. Both are quite important when it comes to preparing graphics for publications. On the other hand, it tries to provide sensible defaults that work "out of the box" for most of the standard cases.

Setting properties is identical to what has been discussed for other types of tasks above. Simply provide the keys corresponding to the properties below the ``properties`` key, as shown for the ``filename`` above. Which properties can be set depends on the type of plotter used. Generally, they are grouped hierarchically, and each plotter will have the following keys: ``figure``, ``legend``, ``zero_lines``. The properties of each of them can be looked up in the respective API documentation for the classes: :class:`aspecd.plotting.FigureProperties`, :class:`aspecd.plotting.LegendProperties`, :class:`aspecd.plotting.LineProperties`.

To give you a first impression of how a more detailed and explicit setting of plot properties may look like, see the following example:


.. code-block:: yaml

    tasks:
      - kind: singleplot
        type: SinglePlotter1D
        properties:
          properties:
            figure:
              size: 6, 4.5
              dpi: 300
              title: My first figure
            axes:
              facecolor: '#cccccc'
            drawing:
              color: tab:red
              linewidth: 2
            legend:
              location: upper right
              frameon: False
          filename:
            - dataset.pdf


Of course, this is only a (small) subset of all the properties you can set for a plot. See the API documentation of the respective plotter classes for more details.


Different kinds of plots
------------------------

"Batteries included" is one of the concepts of the Python programming language that helped its wide-spread adoption. While scientific plotting is intrinsically complex, there are not so many different types of plots, and the ASpecD framework tries to provide the user with at least the most common of them "out of the box". This allows users of one package derived from ASpecD to use the same plotting capabilities in any other package using ASpecD. Together with a user-friendly and intuitive interface, this greatly facilitates plotting with ASpecD.

Generally, we can distinguish between plotters working with single and those operating on multiple datasets. Another distinction is one- and two-dimensional datasets. For more details, see the :mod:`aspecd.plotting` module documentation.


Setting the default output directory
------------------------------------

Plots as well as reports usually result in files being written to the hard drive (or, more generally, to some storage device). For playing around, having the plots and reports written to the current directory may be sensible and straight-forward. In a productive context, however, you will usually have clear ideas where to store your generated representations and reports, and this will often be a dedicated (sub)directory.

Of course, you can provide a full path to each output file for plots and reports. But similar to the datasets source directory (see above), you can provide a default output directory in the recipe:

.. code-block:: yaml

    directories:
      output: /absolute/path/for/the/output

    datasets:
      - dataset

    tasks:
      - kind: singleplot
        type: SinglePlotter
        properties:
          filename:
            - dataset-representation.pdf


In the above example, an absolute path has been provided for the output, and of course you can provide relative paths for the filenames of the plot. Similar to the absolute path set using ``output_directory``, you can set relative paths that are interpreted relative to the path the recipe is cooked from.


Automatically saving plots
--------------------------

Sometimes, particularly when trying to get an overview of a large series of datasets, it is tedious to provide filenames for each single dataset to save the resulting plot to. Therefore, in case you do not provide filename(s) for a plotting task, and as long as the top-level directive ``autosave_plots`` is set to True, your plots will automatically be saved. The name consists of the basename of the dataset source (excluding path and file extension) and the class name of the plotter used.

.. note::

    Not providing filenames for plotters may be convenient when you use every plotter only once per dataset, as otherwise, later plots will overwrite the results of previous plots. On the other hand, the autosave feature may lead to your output directory being populated with a lot of files. Therefore, usually it is best to be more explicit and provide filenames to save your plots to.


Just to show an example of how to switch off the autosaving of plots:

.. code-block:: yaml

    settings:
      autosave_plots: False

    datasets:
      - dataset

    tasks:
      - kind: singleplot
        type: SinglePlotter


In this particular case, the result of the singleplot task will not be saved to a file, and unless you add a label and use the resulting plotter in a compositeplotter task, you will not see the results, as recipe-driven data analysis works fully unattended and non-interactive.


Reports
-------

While plotting can become quite complex and involved already, reports push things to another level entirely. On the other hand, reports are indispensable to get access to all the information contained in datasets and recipes, hence information you as scientist have provided during data analysis.

Using a template engine (`Jinja2 <http://jinja.pocoo.org/>`_), reports separate the data source (dataset, recipe, ...) from layout and final report and allow for creating reports in a number of different output formats. Generally, formatting and contents of your reports are only limited by your imagination, and using the template inheritance mechanisms of Jinja2 allows even for very elegant and economic generation of complex reports reusing standard building blocks.

However, things can become complex quite quickly. Therefore, we will refrain from digging too much into details here and continue with a simple yet powerful "out-of-the-box" example:

.. code-block:: yaml

    datasets:
      - dataset

    tasks:
      - kind: report
        type: LaTeXReporter
        properties:
          template: dataset.tex
          filename: report.tex
        compile: true

So what happens here? We have loaded a single dataset and used the :class:`aspecd.report.LaTeXReporter` on it. Here, we used ``dataset.tex`` as template and output the report to ``report.tex``. The template is one of the bundled templates that come with the ASpecD package (starting with version 0.6) and work out of the box. As we've set ``compile`` to true, we will even get our LaTeX report compiled into a PDF document. Therefore, we will end up with a file ``report.tex`` with the final LaTeX-formatted report and a file ``report.pdf`` containing the typeset result.

And what does this report contain? Basically an overview of all the information contained within the dataset, *i.e.* a list of processing and analysis steps, all representations (including the generated figures), annotations, and a summary of the metadata of the dataset. Of course, as this is a generic template, the formatting tries to be as generic as possible as well. Nevertheless, never underestimate the power of generic reports with uniform formatting, as this greatly facilitates comparing reports for different datasets.

But what if you don't like the way the bundled templates look like? Don't
worry, we've got you covered: Simply provide a relative or absolute path to
your own template, even with the same name. Hence, in the above example,
if you place a file ``dataset.tex`` in the directory you serve the recipe
from, it will be used instead of the bundled one.

Of course, LaTeX is not the only format available and supported. Generally, many formats are supported thanks to Jinja2. Currently (as of version 0.6), only LaTeX and plain text are supported, but more may be added in the future. For details, see the documentation of the :mod:`aspecd.report` module.


.. _specific_packages:

Working with specific packages
==============================

While the ASpecD framework comes with an increasing list of processing and analysis steps, besides providing all the machinery necessary for fully reproducible data analysis, you will usually work with packages derived from the ASpecD framework and dedicated to your specific spectroscopic method at hand.

To make it possible to use the ``serve`` command on the terminal provided by the ASpecD framework even for your own packages, you need to specify which package to use for cooking and serving the recipe – best done at the very beginning of your recipe:

.. code-block:: yaml

    settings:
      default_package: cwepr

In this case, the ``cwepr`` package will be used for importing datasets and performing all tasks, as long as you don't specify other package for a particular dataset or task. Of course, you need to make sure that the Python package specified here exists and is installed locally when serving such a recipe. Furthermore, the Python package needs to fulfil all the requirements of an ASpecD-derived package to allow for recipe-driven data analysis.


.. rubric:: Footnotes

.. [#fn1] Interactive command-line (CLI) and graphical user interfaces (GUI) are an entirely different story, requiring a whole set of different skills and knowledge about concepts of software architecture developed within the last decades. However, the ASpecD framework provides the solid ground to build such interfaces upon. In terms of an overall software architecture, the ASpecD framework and the concepts contained form the inner core of an application for scientific data processing and analysis. User interfaces, similar to persistence layers, are outer layers the core does not know nor care about.