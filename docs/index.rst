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

* Open source project written in Python (>= 3.5)

* Developed fully test-driven

* Extensive user and API documentation


.. warning::
  The ASpecD framework is currently under active development and still considered in Beta development state. Therefore, expect changes in features and public APIs that may break your own code. Nevertheless, feedback as well as feature requests are highly welcome.


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


Related projects
----------------

There is a number of related packages that are based on the ASpecD framework and each focus on one particular type of spectroscopy. The most mature packages available to date are:

* `trepr <https://docs.trepr.de/>`_

  Package for processing and analysing time-resolved electron paramagnetic resonance (TREPR) data, developed by J. Popp and maintained by T. Biskup.

* `cwepr <https://docs.cwepr.de/>`_

  Package for processing and analysing continuous-wave electron paramagnetic resonance (cw-EPR) data, originally developed by P. Kirchner, currently developed and maintained by M. Schröder and T. Biskup.

You may as well be interested in the `LabInform project <https://www.labinform.de/>`_ focussing on the necessary more global infrastructure in a laboratory/scientific workgroup interested in more `reproducible research <https://www.reproducible-research.de/>`_. In short, LabInform is "The Open-Source Laboratory Information System".

Finally, don't forget to check out the website on `reproducible research <https://www.reproducible-research.de/>`_ covering in more general terms aspects of reproducible research and good scientific practice.


.. toctree::
   :maxdepth: 2
   :caption: User Manual:
   :hidden:

   audience
   introduction
   concepts
   recipes
   usecases
   applications
   installing

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

This program is free software: you can redistribute it and/or modify it under the terms of the **BSD License**.


A note on the logo
------------------

The snake (obviously a python, look at how it's holding the magnifying glass) is well familiar with the scientific method and illustrates the basic idea of the ASpecD framework: reproducible data analysis. The copyright of the logo belongs to J. Popp.

