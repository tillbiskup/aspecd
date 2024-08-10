.. ASpecD documentation master file, created by
   sphinx-quickstart on Tue Sep  4 21:53:56 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. image:: https://zenodo.org/badge/DOI/10.5281/zenodo.4717937.svg
   :target: https://doi.org/10.5281/zenodo.4717937
   :align: right

ASpecD documentation
====================

Welcome! This is the documentation for ASpecD -- a **framework** for handling **spectroscopic data** focussing on **reproducibility**.

In short: Each and every processing step applied to your data will be recorded and can be traced back. Additionally, for each representation of your data (*e.g.*, figures, tables) you can easily follow how the data shown have been processed and where they originate from.

What is even better: Actual data processing and analysis **no longer requires programming skills**, but is as simple as writing a text file summarising all the steps you want to have been performed on your dataset(s) in an organised way. Curious? Have a look at :doc:`recipe-driven data analysis <recipes>` – or at the following example:


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


For more general information on the ASpecD framework see its `Homepage <https://www.aspecd.de/>`_, and for how to use it, carry on reading. Interested in more real-live examples? Check out the :ref:`use cases section <use_cases>`.


Features
--------

A list of features:

* Framework for writing applications handling spectroscopic data

* Consistent handling of numeric data and corresponding metadata

* History of each processing step, automatically generated, aiming at full reproducibility

* Undo and redo of processing steps

* Import and export of data

* Generic plotting capabilities, easily extendable

* Report generation using pre-defined templates

* Recipe-driven data analysis, allowing tasks to be performed fully unattended in the background and without programming skills


And to make it even more convenient for users and future-proof:

* Open source project written in Python (>= 3.7)

* Developed fully test-driven

* Extensive user and API documentation


Requirements
------------

The ASpecD framework comes with a rather minimal set of requirements:

* Python >= 3.7 with numpy, scipy and matplotlib packages
* command-line access for :doc:`recipe-driven data analysis <usecases>`
* :doc:`metadata <metadata>` (in addition to the usual parameter files)


.. _sec-how_to_cite:

How to cite
-----------

ASpecD is free software. However, if you use ASpecD for your own research, please cite both, the article describing it and the software itself:

  * Jara Popp, Till Biskup. ASpecD: A Modular Framework for the Analysis of Spectroscopic Data Focussing on Reproducibility and Good Scientific Practice. *Chemistry--Methods* **2**:e202100097, 2022. `doi:10.1002/cmtd.202100097 <https://doi.org/10.1002/cmtd.202100097>`_

  * Till Biskup. ASpecD (2022). `doi:10.5281/zenodo.4717937 <https://doi.org/10.5281/zenodo.4717937>`_

To make things easier, ASpecD has a `DOI <https://doi.org/10.5281/zenodo.4717937>`_ provided by `Zenodo <https://zenodo.org/>`_, and you may click on the badge below to directly access the record associated with it. Note that this DOI refers to the package as such and always forwards to the most current version.

.. image:: https://zenodo.org/badge/DOI/10.5281/zenodo.4717937.svg
   :target: https://doi.org/10.5281/zenodo.4717937


Where to start
--------------

Users new to ASpecD should probably start :doc:`at the beginning <audience>`, those familiar with its :doc:`underlying concepts <concepts>` may jump straight to the section explaining how to :doc:`write applications based on the ASpecD framework <applications>`.

If you are interested in how working with the ASpecD framework looks like, particularly recipe-driven data analysis, have a look at the :doc:`use cases section <usecases>`.

The :doc:`API documentation <api/index>` is the definite source of information for developers, besides having a look at the source code.


Installation
------------

To install the ASpecD framework on your computer (sensibly within a Python virtual environment), open a terminal (activate your virtual environment), and type in the following:

.. code-block:: bash

    pip install aspecd

Have a look at the more detailed :doc:`installation instructions <installing>` as well.


Actual use cases
----------------

Python packages based on the ASpecD framework have been used already for analysing published data, and for some, the data and recipes have been published as "data publications". See the list of :doc:`data publications <examples/data-publications>` for further details.


Related projects
----------------

There is a number of related packages that are based on the ASpecD framework and each focus on one particular type of spectroscopy. The most mature packages available to date are:

* `trepr <https://docs.trepr.de/>`_

  Package for processing and analysing time-resolved electron paramagnetic resonance (TREPR) data, developed by J. Popp, currently developed and maintained by M. Schröder and T. Biskup.

* `cwepr <https://docs.cwepr.de/>`_

  Package for processing and analysing continuous-wave electron paramagnetic resonance (cw-EPR) data, originally implemented by P. Kirchner, developed and maintained by M. Schröder and T. Biskup.

* `nmraspecds <https://docs.nmraspecds.de/>`_

  Package for processing and analysing nuclear magnetic resonance (NMR) data, developed and maintained by M. Schröder.

* `FitPy <https://docs.fitpy.de/>`_

  Framework for the advanced fitting of models to spectroscopic data focussing on reproducibility, developed by T. Biskup.

You may as well be interested in the `LabInform project <https://www.labinform.de/>`_ focussing on the necessary more global infrastructure in a laboratory/scientific workgroup interested in more `reproducible research <https://www.reproducible-research.de/>`_. In short, LabInform is "The Open-Source Laboratory Information System".

Finally, don't forget to check out the website on `reproducible research <https://www.reproducible-research.de/>`_ covering in more general terms aspects of reproducible research and good scientific practice.


.. toctree::
   :maxdepth: 2
   :caption: User Manual:
   :hidden:

   audience
   introduction
   concepts
   metadata
   recipes
   usecases
   applications
   installing

.. toctree::
   :maxdepth: 2
   :caption: Examples:
   :hidden:

   examples/index
   examples/list
   examples/data-publications

.. toctree::
   :maxdepth: 2
   :caption: Developers:
   :hidden:

   people
   developers
   changelog
   roadmap
   adf
   dataset-structure
   api/index


License
-------

This program is free software: you can redistribute it and/or modify it under the terms of the **BSD License**. However, if you use ASpecD for your own research, please cite it appropriately. See :ref:`How to cite <sec-how_to_cite>` for details.


A note on the logo
------------------

The snake (obviously a python, look at how it's holding the magnifying glass) is well familiar with the scientific method and illustrates the basic idea of the ASpecD framework: reproducible data analysis. The copyright of the logo belongs to J. Popp.

