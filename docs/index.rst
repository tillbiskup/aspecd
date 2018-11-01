.. ASpecD documentation master file, created by
   sphinx-quickstart on Tue Sep  4 21:53:56 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to ASpecD's documentation!
==================================

ASpecD is a framework for handling spectroscopic data focussing on reproducibility. In short: Each and every processing step applied to your data will be recorded and can be traced back, and additionally, for each representation of your data (e.g., figures, tables) you can easily follow how the data shown have been processed and where they originate from.


.. warning::
  The ASpecD framework is currently under active development and still considered in Alpha development state. Therefore, expect frequent changes in features and public APIs that may break your own code. Nevertheless, feedback as well as feature requests are highly welcome.


Users new to ASpecD should probably start :doc:`at the beginning <audience>`, those familiar with its :doc:`underlying concepts <concepts>` may jump straight to the section explaining how to :doc:`write applications based on the ASpecD framework <applications>`.

The :doc:`API documentation <api/aspecd>` is the definite source of information for developers, besides having a look at the source code.


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   audience
   introduction
   concepts
   applications
   usecases

   api/modules


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
