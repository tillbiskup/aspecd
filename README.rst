ASpecD
======

.. image:: https://zenodo.org/badge/DOI/10.5281/zenodo.4717937.svg
   :target: https://doi.org/10.5281/zenodo.4717937
   :align: right

ASpecD is a **framework for handling spectroscopic data** focussing on **reproducibility**. In short: Each and every processing step applied to your data will be recorded and can be traced back, and additionally, for each representation of your data (e.g., figures, tables) you can easily follow how the data shown have been processed and where they originate from.

What is even better: Actual data processing and analysis **no longer requires programming skills**, but is as simple as writing a text file summarising all the steps you want to have been performed on your dataset(s) in an organised way. Curious? Here is an example::

    format:
      type: ASpecD recipe
      version: '0.3'

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


Save this recipe to a file, *e.g.*, ``my-first-recipe.yaml``. Cooking the recipe and serving the result is the matter of issuing a single command in a terminal::

    serve my-first-recipe.yaml

This will do two things: process your data (and create the plots in our case) and write a **full and gap-less history** as an executable recipe.

For more general information on the ASpecD framework see its `homepage <https://www.aspecd.de/>`_, and for how to use it, its `documentation <https://doc.aspecd.de/>`_.


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

* `Extensive user and API documentation <https://docs.aspecd.de/>`_


Target audience
---------------

The ASpecD framework addresses every scientist working with data (both, measured and calculated) on a daily base and concerned with `reproducibility <https://www.reproducible-research.de/>`_. The ASpecD framework ensures reproducibility and---as much as possible---replicability of data processing, starting from recording data and ending with their final (graphical) representation, e.g., in a peer-reviewed publication. This is achieved by automatically creating a gap-less record of each operation performed on your data. If you do care about reproducibility and are looking for a system that helps you to achieve this goal, ASpecD may well be interesting for you.


How to cite
-----------

ASpecD is free software. However, if you use ASpecD for your own research, please cite both, the article describing it and the software itself:

* Jara Popp, Till Biskup. ASpecD: A Modular Framework for the Analysis of Spectroscopic Data Focussing on Reproducibility and Good Scientific Practice. *Chemistry--Methods* **2**:e202100097, 2022. `doi:10.1002/cmtd.202100097 <https://doi.org/10.1002/cmtd.202100097>`_

* Till Biskup. ASpecD (2022). `doi:10.5281/zenodo.4717937 <https://doi.org/10.5281/zenodo.4717937>`_

To make things easier, ASpecD has a `DOI <https://doi.org/10.5281/zenodo.4717937>`_ provided by `Zenodo <https://zenodo.org/>`_, and you may click on the badge below to directly access the record associated with it. Note that this DOI refers to the package as such and always forwards to the most current version.

.. image:: https://zenodo.org/badge/DOI/10.5281/zenodo.4717937.svg
   :target: https://doi.org/10.5281/zenodo.4717937


Related projects
----------------

There is a number of related packages that are based on the ASpecD framework and each focus on one particular type of spectroscopy. The most mature packages available to date are:

* `trepr <https://docs.trepr.de/>`_

  Package for processing and analysing time-resolved electron paramagnetic resonance (TREPR) data, developed by J. Popp, currently developed and maintained by M. Schröder and T. Biskup.

* `cwepr <https://docs.cwepr.de/>`_

  Package for processing and analysing continuous-wave electron paramagnetic resonance (cw-EPR) data, originally developed by P. Kirchner, currently developed and maintained by M. Schröder and T. Biskup.

* `NMRAspecds <https://docs.nmraspecds.de/>`_

  Package for processing and analysing nuclear magnetic resonance (NMR) data, developed and maintained by M. Schröder.

* `FitPy <https://docs.fitpy.de/>`_

  Framework for the advanced fitting of models to spectroscopic data focussing on reproducibility, developed by T. Biskup.

You may as well be interested in the `LabInform project <https://www.labinform.de/>`_ focussing on the necessary more global infrastructure in a laboratory/scientific workgroup interested in more `reproducible research <https://www.reproducible-research.de/>`_. In short, LabInform is "The Open-Source Laboratory Information System".

Finally, don't forget to check out the website on `reproducible research <https://www.reproducible-research.de/>`_ covering in more general terms aspects of reproducible research and good scientific practice.


License
-------

This program is free software: you can redistribute it and/or modify it under the terms of the **BSD License**.
