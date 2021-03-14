====================
Writing applications
====================

As the name says, the ASpecD framework in itself only provides the scaffold for applications aiming at reproducible processing and analysis of spectroscopic data. However, that does not mean that you need to start from scratch when implementing a Python package for your preferred spectroscopic method. ASpecD comes with (some) "batteries included", namely an increasing list of generally applicable processing and analysis steps.

Writing applications based on the ASpecD framework should be fairly straight-forward once familiar with its :doc:`concepts <concepts>`.


.. note::

    Most users of a package based on the ASpecD framework will not bother about how to further develop these packages. They will usually only work with the package by means of ":ref:`recipe-driven data analysis <recipes>`". However, if you are interested in writing or further developing packages for the analysis of spectroscopic data based on the ASpecD framework, continue reading.


Before you start
================

ASpecD is all about reproducible data analysis, hence more `reproducible and reliable science <https://www.reproducible-research.de/>`_. Therefore, before you start writing your own applications based on the ASpecD framework, make sure to have a minimal infrastructure available and use it for your developments. Without a version control system (VCS) and a scheme for version numbers that you follow thoroughly, fundamental aspects of the ASpecD framework simply won't work. Additionally, do choose an appropriate license for your program. After all, the time frame of reproducibility is not the typical length of a PhD thesis, but rather decades.

If you have experience already with version control systems and version numbering schemes, go ahead with what you are familiar with. However, if you fancy some hints what to use, here are our suggestions:

  * Version control system: `git <https://git-scm.com/>`_
  * Version numbering scheme: `SemVer <https://semver.org/>`_

This is what ASpecD is developed with and what it uses -- for good reasons.


How to start
============

Applications based on the ASpecD framework should be Python packages following the standards laid out by the `Python Packaging Authority (PyPA) <https://www.pypa.io/>`_ in their `Python Packaging User Guide <https://python-packaging-user-guide.readthedocs.io/>`_.

Generally, you will probably start off with deciding about a name for your application. Names, particularly for programs and packages, need care in choosing. It is a good idea to check the `Python Package Index <https://pypi.org/>`_ for similar packages and possible name clashes, in case you plan to eventually publish your package there (always a good idea to keep in mind).


.. hint::

    For the sake of argument, we will choose the name "**spectro**" for the hypothetic new package here. Of course, you will never choose this name for an actual package, as it is pretty meaningless. Hence, a good choice here...


Having decided upon a name for your new package, continue by creating a basic directory structure and a Python virtual environment for your package, and installing the ASpecD framework [#aspecd_availability]_ (and your package) within this virtual environment. The basic directory structure of your new package may look like follows:

.. code-block::

    spectro
    ├── docs
    ├── spectro
    │   ├── __init__.py
    │   ├── analysis.py
    │   ├── dataset.py
    │   ├── io.py
    │   ├── metadata.py
    │   ├── plotting.py
    │   └── processing.py
    ├── tests
    │   ├── test_analysis.py
    │   ├── test_dataset.py
    │   ├── test_io.py
    │   ├── test_metadata.py
    │   ├── test_plotting.py
    │   └── test_processing.py
    ├── LICENSE
    ├── README.rst
    ├── Requirements.txt
    ├── setup.py
    └── VERSION


Directories and files should be pretty self-explaining. If in doubt, consult the `Python Packaging Authority (PyPA) <https://www.pypa.io/>`_ and their `Python Packaging User Guide <https://python-packaging-user-guide.readthedocs.io/>`_ or have a look at the `ASpecD source code <https://github.com/tillbiskup/aspecd/>`_.

To create the virtual environment and install ASpecD and your package, open a terminal and type something like the following commands:

.. code-block:: bash

    python3 -m venv spectro_venv
    source spectro_venv/bin/activate
    pip install aspecd


Make sure to install your package in an editable fashion, using the ``-e`` switch of the ``pip`` command:

.. code-block:: bash

    pip install -e spectro


With this, you should be ready to start developing your application.


.. note::
    Before starting to write your own classes, make sure that you have obtained a decent understanding of the role and interactions of each of the different classes in the ASpecD framework. Many aspects rely on "convention over configuration", and therefore, it is crucial to understand and follow these conventions, as detailed in the :doc:`API documentation <api/index>`. The ultimate goal of a good object-oriented design is a set of coherent and loosely-coupled classes and units that allow to easily extend and modify a program in response to new requirements. Whereas far from perfect, the ASpecD framework tries to follow these guidelines as set out in the respective literature.


Datasets
========

Probably the most fundamental unit of the ASpecD framework is the dataset. Hence, you should first create a dataset class of your own that inherits from the dataset class of the ASpecD framework. Here, we assume that you start with experimental datasets, as opposed to datasets containing calculated data. Therefore, create a module named ``dataset`` and include the following code::

    import aspecd

    class ExperimentalDataset(aspecd.dataset.ExperimentalDataset):

        def __init__(self):
            super().__init__()

This was easy, and in most cases, this is all you need to do to have a full-fledged dataset. Of course, you should document your newly created dataset class appropriately. Make sure to obey the rules laid out in `PEP 257 <https://www.python.org/dev/peps/pep-0257/>`_.

However, life is a bit more complicated to get things working properly and to be able to actually work on data. Next steps include creating importers for raw data and metadata, and creating appropriate metadata classes for storing these metadata within the dataset. Eventually, this means that you will need to modify your newly created dataset class very slightly to reflect the changes you made to your metadata. For details, see the `metadata`_ section below.


Importer
========

To actually be able to work on (numeric) data and to store them together with their accompanying metadata in a dataset, you need to write importer classes specific for each type of raw data. To do so, create a module named ``io`` and include the following code::

    import aspecd

    class DatasetImporter(aspecd.io.DatasetImporter):

        def __init__(self, source=''):
            super().__init__(source=source)

        def _import(self):
            # And here goes your code actually importing the data and metadata

Of course, you need to add appropriate code to the non-public function ``_import`` of the importer class you just created. And if you have more than one type of raw data, make sure to give your classes better names than just "DatasetImporter". Even if you start with one type of raw data, naming the importer class closer to the actual file format is always helpful. This prevents you from having to change your depending code later on.

The importer should make sure not only to import the numeric data appropriately into the dataset object (they go into its ``data.data`` attribute), but to also create appropriate axes and to read the metadata accompanying the (raw) data. For the necessary structures within the dataset's ``metadata`` attribute and how to eventually fill the metadata into this hierachy of objects, see the `metadata`_ section.

In the (usual) case where you have more than one raw format data are stored in, you would like to create a single class that takes care of returning the correct importer, given a string specifying the source of the data. This is what factories are good for: Returning different subtypes of a common basetype depending on the particular needs. To achieve this for the importers of your application, create a class ``DatasetImporterFactory`` that inherits from :class:`aspecd.io.DatasetImporterFactory`::

    import aspecd

    class DatasetImporterFactory(aspecd.io.DatasetImporterFactory):

        def _get_importer(self, source):
            # And here goes your code actually choosing the correct importer


Metadata
========

The ``metadata`` attribute of the (experimental) dataset is actually an instance of :class:`aspecd.metadata.ExperimentalDatasetMetadata` that in itself contains a list of attributes found in any case, namely general information about the measurement (``measurement``), the sample (``sample``) and the temperature control (``temperature_control``). Each of these attributes are instances of their respective classes defined as well within the ASpecD framework.

In order to store all the metadata usually contained in files written at the time of data acquisition, you will need to create additional metadata classes and extend :class:`aspecd.metadata.ExperimentalDatasetMetadata` by writing your own "ExperimentalDatasetMetadata" class subclassing the one from the ASpecD framework::

    import aspecd

    class ExperimentalDatasetMetadata(aspecd.metadata.ExperimentalDatasetMetadata):

        def __init__(self, path=''):
            super().__init__()
            # Add here attributes that are instances of your metadata classes

Your metadata classes should be based on the generic :class:`aspecd.metadata.Metadata` class. Additionally, all physical quantities appearing somewhere in your metadata should be stored in objects of the class :class:`aspecd.metadata.PhysicalQuantity`. Note that it might be useful to define the attributes in each of the metadata classes in the order they would be contained in a metadata file and should be included in a report. The :class:`aspecd.metadata.Metadata` class provides means to include the information contained in its attributes that preserves the order in which they were originally defined within the respective class.

Eventually, you will need to extend your ``Dataset`` class that you have defined as described in the `corresponding section <#datasets>`_ accordingly::

    import aspecd

    class ExperimentalDataset(aspecd.dataset.ExperimentalDataset):

        def __init__(self):
            super().__init__()
            self.metadata = ExperimentalDatasetMetadata()

Once you have created all the necessary classes for the different groups of metadata, the actual import of the metadata can become quite simple. The only prerequisite here is to have them initially stored in a Python dictionary whose structure resembles that of the hierarchy of objects contained in your :class:`ExperimentalDatasetMetadata` class. Therefore, make sure that at least the top-level keys of this dictionary have names corresponding to the (public) attributes of your :class:`ExperimentalDatasetMetadata` class. [#metadata_names]_

.. note::
  The organisation of metadata in a metadata file that gets created during measurement and the representation of the very same metadata within the ``Dataset`` class need not be the same, and they will most probably diverge at least over time. To nevertheless be able to map the metadata read from a file and contained in a dictionary (ideally in a :class:`collections.OrderedDict`), there exists the :class:`aspecd.metadata.MetadataMapper` class allowing to map the dictionary to the structure of the class hierarchy in your :class:`ExperimentalDatasetMetadata` class.

Once you have a dictionary, e.g. ``metadata_dict``, with all your metadata and with (top-level) keys corresponding to the the attributes of your :class:`ExperimentalDatasetMetadata` class, you can import the metadata into your dataset with just one line::

    dataset.metadata.from_dict(metadata_dict)

All your metadata classes share this very same method, as long as they are based on :class:`aspecd.metadata.Metadata`. This allows to traverse the dictionary containing your metadata.

.. note::
  The ``from_dict()`` method is rather forgiving, only copying those values of the dict to the corresponding metadata object that are attributes of the object, and neither caring about additional keys in the dictionary nor additional attributes in the object. Therefore, it is your sole responsibility to check that the metadata contained in the dictionary and your metadata classes have corresponding keys/attributes.


Comments
--------

Comments are often found (for good reason) in metadata files that accompany raw data and get written during data acquisition. While usually part of the metadata files, they should *not* be put in the metadata property of the ``Dataset`` class. Technically, comments are annotations, and for this very purpose, a whole set of classes is available within the ASpecD framework, namely in the :mod:`aspecd.annotation` module. Usually, you will not need to subclass any of the classes provided in that module.

To add a comment to a dataset, you will need to instantiate an object of class :class:`aspecd.annotation.Comment`, assign the comment to it, and finally annotate your dataset::

    import aspecd

    comment = aspecd.annotation.Comment()
    comment.comment = metadata_dict["comment"]
    dataset.annotate(comment)

Here, we assumed for simplicity that your metadata are contained in the dictionary ``metadata_dict``, and that your dataset resides in ``dataset``. If you implement this very functionality within your ``Importer`` class in its ``_import()`` method (`see above <#importer>`_), as you should do, [#import_method]_ you will have to adjust some of the variable names accordingly.


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
            self.undoable = True

        def _perform_task(self):
            # And here goes your code performing the actual processing step

A few comments on this code stub:

* Always set the ``description`` attribute appropriately, as it gets stored in the history and is intended to give the user a first impression of what the processing step was good for. Be concise. More than about 60 characters are definitely too exhaustive.

* Usually, the processing steps are undoable, hence, set the attribute ``undoable`` appropriately. For safety reasons, it is set to ``False`` in the base class.

* Store all parameters, implicit and explicit, in the public attribute ``parameters`` of the :class:`ProcessingStep` class. This application of the "convention over configuration" strategy greatly facilitates automatic processing of your data and proper handling of the history.

* Put all the actual processing into the :meth:`_perform_task()` method. Usually, this will contain a series of calls to other non-public methods performing each their respective part of the processing step.

* Your classes inheriting from :class:`aspecd.processing.ProcessingStep` should have no more public attributes than their parent class.

* Put *all* your processing steps into the :mod:`processing` module, as this is a prerequisite for reproducing your data processing afterwards. This is another application of the "convention over configuration" strategy greatly facilitating the automatic handling of your data.

If you need to sanitise the parameters before applying the actual processing step to your data, override the non-public method ``_sanitise_parameters()`` that will be called straight before ``_perform_task()`` when calling the ``process()`` method on either the ``ProcessingStep`` object or the ``Dataset`` object.


What's next?
============

Of course, there is much more to a full-fledged application for processing and analysis of spectroscopic data, but the steps described so far should get you somehow started.

Additional aspects you may want to consider and that will be detailed here a bit more in the future include:

* Analysis steps

* Plotting

* Reports based on pre-defined templates

* Recipe-driven data processing and analysis

Make sure to understand the :doc:`underlying concepts of the ASpecD framework <concepts>` and have a look at its :doc:`API documentation <api/index>` as well as the source code.


.. rubric:: Footnotes

.. [#aspecd_availability] The ASpecD framework is `available <https://pypi.org/project/aspecd/>`_ via the `Python Package Index (PyPI) <https://pypi.org/>`_: `<https://pypi.org/project/aspecd/>`_. For the latest version, check it out from its `GitHub repository <https://github.com/tillbiskup/aspecd/>`_.

.. [#metadata_names] Note that at least for older metadata files in the author's lab, the block named "General" needs to be renamed into "measurement" in the dictionary containing the metadata to correspond to the :class:`aspecd.metadata.Measurement` class.

.. [#import_method] Usually, your :meth:`_import()` method will consist of calls to other (non-public) methods of your :class:`Dataset` class. Typical use cases would be methods for importing numeric data and metadata, respectively. This is, however, just the usual general advice for small functions/methods with statements that all share the same level of abstraction. See the appropriate literature for more details on this topic.
