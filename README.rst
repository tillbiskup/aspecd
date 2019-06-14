ASpecD
======

``aspecd`` is a framework for handling spectroscopic data focussing on reproducibility. In short: Each and every processing step applied to your data will be recorded and can be traced back, and additionally, for each representation of your data (e.g., figures, tables) you can easily follow how the data shown have been processed and where they originate from.


Features
--------

A list of features, not all implemented yet but aimed at for the first public release (ASpecD 0.1):

* Framework for writing applications handling spectroscopic data

* Consistent handling of numeric data and corresponding metadata

* History of each processing step, automatically generated, aiming at full reproducibility

* Undo and redo of processing steps

* Import and export of data

* Generic plotting capabilities, easily extendable

* Report generation using pre-defined templates

* Recipe-driven data analysis, allowing tasks to be performed fully unattended in the background


And to make it even more convenient for users and future-proof:

* Open source project written in Python (>= 3.5)

* Developed fully test-driven

* Extensive user and API documentation


.. warning::
  The ASpecD framework is currently under active development and still considered in Alpha development state. Therefore, expect frequent changes in features and public APIs that may break your own code. Nevertheless, feedback as well as feature requests are highly welcome.

