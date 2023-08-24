========
Overview
========

Here, we present a (growing) series of working examples of how to use the ASpecD framework to perform both, day-to-day routine tasks in a laboratory as well as more complex processing and analysis tasks.

.. note::

    Generally, the ASpecD framework provides the solid ground for derived packages dedicated to particular (spectroscopic) methods, such as `cw-EPR <https://docs.cwepr.de/>`_, `tr-EPR <https://docs.trepr.de/>`_, and `UV/Vis <https://docs.uvvispy.de/>`_. However, you can use ASpecD for certain tasks out of the box, at least for basic processing, analysis, and plotting, although all the advantages of tailor-made metadata for specific methods are lacking in this case.


For each of the examples, a full recipe is provided ready to be copied and pasted and run on your local computer.

.. note::

    For each of the recipes provided so far, real example data can be found in the accompanying `repository on GitHub <https://github.com/tillbiskup/example-data-aspecd>`_. Therefore, you can download the data and recipe to get first-hand experience with the cwepr package.


Prerequisites
=============

To be able to run the example recipes locally, you need to have a working installation of the ASpecD framework and its dependencies. Have a look at the :doc:`installation instructions <../installing>` for details.

Furthermore, to be able to run ("cook") the recipes and get ("serve") the results, you need to have access to a command line, as running recipes (still) is command-line based using the command :samp:`serve {recipe.yaml}`.


Further examples
================

If you are interested in more examples, the :ref:`publication describing the cwepr package <sec-how_to_cite>` contains a number of examples of different complexity. The complete recipes are provided in the supporting information (SI). What is even better: You can download the entire set of data and corresponding recipes from GitHub:

* `EPR data and analysis for Schröder and Biskup, J. Magn. Reson. 335:107140, 2022 <https://github.com/tillbiskup/2022-jmr-data>`_

  GitHub repository containing both, data and recipes for all the examples shown in the :ref:`publication describing the cwepr package <sec-how_to_cite>`.