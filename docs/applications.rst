====================
Writing applications
====================

As the name says, the ASpecD framework in itself only provides the scaffold for applications aiming at processing and analysing spectroscopic data.

Writing applications based on the ASpecD framework should be fairly straight-forward once familiar with its :doc:`concepts <concepts>`.


How to start
============

Applications based on the ASpecD framework should be Python packages following the standards layed out by the `Python Packaging Authority (PyPA) <https://www.pypa.io/>`_ in their `Python Packaging User Guide <https://python-packaging-user-guide.readthedocs.io/>`_.

Generally, you will probably start off with deciding about a name for your application, creating a basic directory structure and a Python virtual environment for your package, and installing the ASpecD framework [#aspecd_availability]_ (and your package) within this virtual environment.

Make sure to install your package in an editable fashion, using the ``-e`` switch of the ``pip`` command::

  pip install -e my_package

With this, you should be ready to start developing your application.


Datasets
========

Probably the most fundamental unit of the ASpecD framework is the dataset. Hence, you should first create a dataset class of your own that inherits from the dataset class of the ASpecD framework. To do so, create a module named ``dataset`` and include the following code::

    import aspecd

    class Dataset(aspecd.dataset.Dataset):

        def __init__(self):
            super().__init__()

This was easy, and in most cases, this is all you need to do to have a full-fledged dataset. Of course, you should document your newly created dataset class appropriately. Make sure to obey the rules layed out in `PEP 257 <https://www.python.org/dev/peps/pep-0257/>`_.

However, life is a bit more complicated to get things working properly and to be able to actually work on data. Next steps include creating importers for raw data and metadata, and creating appropriate metadata classes for storing these metadata within the dataset.


Importer
========

To actually be able to work on (numeric) data and to store them together with their accompanying metadata in a dataset, you need to write importer classes specific for each type of raw data. To do so, create a module named ``importer`` and include the following code::

    import aspecd

    class Importer(aspecd.importer.Importer):

        def __init__(self, path=''):
            super().__init__()

        def _import(self):
            # And here goes your code actually importing the data and metadata

Of course, you have to add appropriate code to the non-public function ``_import`` of the just created importer class. And if you have more than one type of raw data, make sure to give your classes better names than just "Importer".

The importer should make sure not only to import the numeric data appropriately into the dataset object (they go into its ``data.data`` property), but to also create appropriate axes and to read the metadata accompanying the (raw) data. For the necessary structures within the dataset's ``metadata`` property, see the `metadata`_ section.


Metadata
========

The ``metadata`` property of the dataset is actually an instance of :class:`aspecd.metadata.DatasetMetadata` that in itself contains a list of properties found in any case, namely general information about the measurement (``measurement``), the sample (``sample``) and the temperature control (``temperature_control``). Each of these properties are instances of their respective classes defined as well within the ASpecD framework.

In order to store all the metadata usually contained in files written at the time of data acquisition, you will need to write additional metadata classes and extend :class:`aspecd.metadata.DatasetMetadata` by writing your own "DatasetMetadata" class subclassing the one from the ASpecD framework::

    import aspecd

    class DatasetMetadata(aspecd.metadata.DatasetMetadata):

        def __init__(self, path=''):
            super().__init__()
            # Add here properties that are instances of your metadata classes

Your metadata classes should be based on the generic :class:`aspecd.metadata.Metadata` class. Additionally, all physical quantities appearing somewhere in your metadata should be stored in objects of the :class:`aspecd.metadata.PhysicalQuantity`.

Eventually, you will need to extend your ``Dataset`` class that you have defined as described in the `corresponding section <#datasets>`_ accordingly::

    import aspecd

    class Dataset(aspecd.dataset.Dataset):

        def __init__(self):
            super().__init__()
            self.metadata = DatasetMetadata()

.. todo::
  Should the metadata classes go into the dataset module (in the ASpecD framework as well), or should this be a separate module? At least in applications based on the ASpecD framework, having it in the dataset module seems more sensible, as there is otherwise not much content.


Processing steps
================

After having created classes for the dataset and storing the accompanying metadata, it is time to think of processing your data. As set out in the :doc:`introduction <introduction>` already in quite some detail, reproducibility is both, at the heart of good scientific practice as well as the ASpecD framework.

Therefore, both, as a developer writing analysis software based on the ASpecD framework as well as its user, you need not bother about such aspects as having processing steps writing a history containing all their parameters. All you need to do is to subclass :class:`aspecd.processing.ProcessingStep` and adhere to a few basic rules when implementing your own data processing classes.

Let's assume for simplicity that you want to write a processing step called "MyProcessing". Generally, you would start out creating a module ``processing`` within your Python project, if it does not exist already, and add some basic code to it::

    import aspecd

    class MyProcessing(aspecd.processing.ProcessingStep):

        def __init__(self):
            super().__init__()
            self.description = 'My processing step'

        def _perform_task(self):
            # And here goes your code performing the actual processing step

A few comments to this code stub:

* Always set the ``description`` property appropriately, as it gets stored in the history and is intended to give the user a first impression of what the processing step was good for. Be concise. Mote than about 60 characters are definitely too exhaustive.

* Store all parameters, implicit and explicit, in the public property ``parameters`` of the ProcessingStep class. This application of the "convention over configuration" strategy greatly facilitates automatic processing of your data and proper handling of the history.

* Your classes inheriting from :class:`aspecd.processing.ProcessingStep` should have no more public properties than their parent class.

If you need to sanitise the parameters before applying the actual processing step to your data, override the non-public method ``_sanitise_parameters()`` that will be called straight before ``_perform_task()`` when calling the ``process()`` method on either the ``ProcessingStep`` object or the ``Dataset`` object.


What's next?
============

Of course, there is much more to a full-fledged application for processing and analysis of spectroscopic data, but the steps described so far should get you somehow started.

Make sure to understand the :doc:`underlying concepts of the ASpecD framework <concepts>` and have a look at its :doc:`API documentation <api/aspecd>` as well as the source code.


.. rubric:: Footnotes

.. [#aspecd_availability] Currently, the ASpecD framework is not available via the `Python Package Index (PyPI) <https://pypi.org/>`_, but only via checkout from a local gitlab instance. Ask its author for details.
