"""Input and output (IO) of information from and to the persistence layer.

Currently, input and output of both, datasets and recipes can be handled.


Datasets
========

Both, data and metadata contained in datasets as well as the information
stored in recipes for recipe-driven data analysis can be read and written.

For datasets, two generic classes are provided:

* :class:`aspecd.io.DatasetImporter`

* :class:`aspecd.io.DatasetExporter`

As the name says, these classes should be used to implement import and
export functionality for your own purposes in applications derived from the
ASpecD framework.

Generally, both import and export should be handled via the respective
methods of the :class:`aspecd.dataset.Dataset` class, thus first
instantiating an object of that class and an appropriate importer or
exporter, and afterwards only operating on the dataset using its methods.

In its most generic form, this may look something like::

    dataset = aspecd.dataset.Dataset()
    importer = aspecd.io.DatasetImporter(source="/path/to/your/data")
    dataset.import_from(importer)

Similarly, you would handle the export of your data (and metadata)
contained in a dataset object using an exporter object, respectively.


Importers for specific file formats
-----------------------------------

There exists a series of importers for specific file formats:

* :class:`aspecd.io.AdfImporter`

  Importer for data in ASpecD Dataset Format (ADF)

* :class:`aspecd.io.AsdfImporter`

  Importer for data in asdf format

* :class:`aspecd.io.TxtImporter`

  Importer for data in plain text format

For details, see the respective class documentation.


Exporters for specific file formats
-----------------------------------

Datasets need to be persisted sometimes, and currently, there exist two
exporters for specific file formats that can be imported again using the
respective importers. Furthermore, the full information contained in a
dataset will be retained.

* :class:`aspecd.io.AdfExporter`

  Exporter for datasets to ASpecD Dataset Format (ADF)

* :class:`aspecd.io.AsdfExporter`

  Exporter for datasets to asdf format

For details, see the respective class documentation.


Writing importers for data
--------------------------

When writing importer classes for your own data, there is a number of
pitfalls, some of which shall be described here together with solutions and
"best practices".

Dimensions of data
~~~~~~~~~~~~~~~~~~

Usually, we assign axes in the order *x*, *y*, *z*, and assume the *x* axis
to be the horizontal axis in a plot. However, numpy (as well as other
software), follows a different convention, with the first index referring to
the *row* of your matrix, the second index to the *column*. That boils down
to having the first index correspond to the *y* axis, and the second index
referring to the *x* axis.

As long as your data are one-dimensional, resulting in two axes objects in
your dataset, everything is fine, and the second axis will have no values.

However, if your data to be imported are two-dimensional, your first
dimension will be the index of rows (along a column), hence the *y* axis,
and the second dimension the index of your columns (along a row), *i.e.* the
*x* axis. This is perfectly fine, and it is equally fine to revert this
order, as long as you ensure your axis objects to be consistent with the
dimensions of your data.

If you assign numeric data to the :attr:`aspecd.dataset.Data.data` property,
the corresponding axes values will initially be set to the indices of the
data points along the corresponding dimension, with the first axis (index 0)
corresponding to the first dimension (row indices along a column) and
similar for each of the following dimensions of your data. Note that there
will always be one axis more than dimensions of your data. This last axis
will not have values, and usually its quantity is something like "intensity".


Backup of the data
~~~~~~~~~~~~~~~~~~

One essential concept of the ASpecD dataset is to store the original data
together with their axes in a separate, non-public property. This is done
automatically by the importer after calling out to its non-public method
:meth:`aspecd.io.DatasetImporter._import`. Hence, usually you need not take
care of this at all.


Handling of metadata
~~~~~~~~~~~~~~~~~~~~

Data without information about these data are usually pretty useless. Hence,
an ASpecD dataset is always a unit of numerical data and corresponding
metadata. While you will need to come up with your own structure for
metadata of your datasets and create a hierarchy of classes derived from
:class:`aspecd.metadata.DatasetMetadata`, your importers need to ensure that
these metadata are populated respectively. Of course, which metadata can be
populated depends strongly on the file format you are about to import.


Handling different file formats for importing data
--------------------------------------------------

Often, data are available in different formats, and deciding which importer
is appropriate for a given format can be quite involved. To free other
classes from having to contain the relevant code, a factory can be used:

* :class:`aspecd.io.DatasetImporterFactory`

Currently, the sole information provided to decide about the appropriate
importer is the source (a string). A concrete importer object is returned
by the method :meth:`get_importer`. Thus, using the factory in another
class may look like the following::

  importer_factory = aspecd.io.DatasetImporterFactory()
  importer = importer_factory.get_importer(source="/path/to/your/data")
  dataset = aspecd.dataset.Dataset()
  dataset.import_from(importer)

Here, as in the example above, "source" refers to a (unique) identifier of
your dataset, be it a filename, path, URL/URI, LOI, or alike.

.. important::
    For recipe-driven data analysis to work with an ASpecD-derived package,
    you need to implement a :class:`aspecd.io.DatasetImporterFactory` class
    there as well that can be obtained by instantiating
    ``<your_package>.io.DatasetImporterFactory()``.


Recipes
=======

For recipes, a similar set of classes is provided:

* :class:`aspecd.io.RecipeImporter`

* :class:`aspecd.io.RecipeExporter`

For additional concrete classes handling import and export from and to YAML
files see below.

The same general principles laid out above for the datasets applies to
these classes as well. In particular, both import and export should be
handled via the respective methods of the :class:`aspecd.tasks.Recipe`
class, thus first instantiating an object of that class and an appropriate
importer or exporter, and afterwards only operating on the recipe using
its methods.

In its most generic form, this may look something like::

    recipe = aspecd.tasks.Recipe()
    importer = aspecd.io.RecipeImporter(source="/path/to/your/recipe")
    recipe.import_from(importer)

Similarly, you would handle the export of the information contained in a
recipe object using an exporter object, respectively.

To simplify the input and output of recipes, and due recipe-driven data
analysis being an intrinsic property of the ASpecD framework, two classes
handling the import and export from and to YAML files are provided as well:

* :class:`aspecd.io.RecipeYamlImporter`

* :class:`aspecd.io.RecipeYamlExporter`

These classes can directly be used to work with YAML files containing
information for recipe-driven data analysis. For details of the YAML file
structure, see the :class:`aspecd.tasks.Recipe` class and its attributes.


Module documentation
====================

"""
import copy
import os
import tempfile
import zipfile

import asdf
import numpy as np

import aspecd.exceptions
import aspecd.utils


class DatasetImporter:
    """Base class for dataset importer.

    Each class actually importing data and metadata into a dataset should
    inherit from this class.

    To perform the import, call the
    :meth:`~aspecd.dataset.Dataset.import_from` method of the dataset
    the import should be performed for, and provide a reference to the
    actual importer object to it.

    The actual implementation of the importing is done in the private method
    :meth:`_import` that in turn gets called by :meth:`import_into`
    which is called by the :meth:`aspecd.dataset.Dataset.import_from` method
    of the dataset object.

    One question arising when actually implementing an importer for a
    specific file format: How do the data get into the dataset? The simple
    answer: The :meth:`_import` method of the importer knows about the
    dataset and its structure (see :class:`aspecd.dataset.Dataset` for
    details) and assigns data (and metadata) read from an external source
    to the respective fields of the dataset. In terms of a broader software
    architecture point of view: The dataset knows nothing about the
    importer besides its bare existence and interface, whereas the importer
    knows about the dataset and how to map data and metadata.

    Attributes
    ----------
    dataset : :obj:`aspecd.dataset.Dataset`
        dataset to import data and metadata into
    source : string
        specifier of the source the data and metadata will be read from

    Raises
    ------
    aspecd.io.MissingDatasetError
        Raised when no dataset exists to act upon

    """

    def __init__(self, source=None):
        self.source = source
        self.dataset = None

    def import_into(self, dataset=None):
        """Perform the actual import into the given dataset.

        If no dataset is provided at method call, but is set as property in
        the importer object, the :meth:`aspecd.dataset.Dataset.import_from`
        method of the dataset will be called.

        If no dataset is provided at method call nor as property in the
        object, the method will raise a respective exception.

        The dataset object always calls this method with the respective
        dataset as argument. Therefore, in this case setting the dataset
        property within the importer object is not necessary.

        The actual import should be implemented within the non-public method
        :meth:`_import`.

        .. note::
            A number of parameters of the dataset are automatically assigned
            *after* calling out to the non-public method
            :meth:`aspecd.io.DatasetImporter._import`, namely the
            non-public property ``_origdata`` of the dataset is populated
            with a copy of :attr:`aspecd.dataset.Dataset.data`, and id and
            label are set to :attr:`aspecd.io.DatasetImporter.source`.

        Parameters
        ----------
        dataset : :class:`aspecd.dataset.Dataset`
            Dataset to import data and metadata into

        Raises
        ------
        aspecd.io.MissingDatasetError
            Raised if no dataset is provided.

        """
        if not dataset:
            if self.dataset:
                self.dataset.import_from(self)
            else:
                raise aspecd.exceptions.MissingDatasetError(
                    "No dataset provided")
        else:
            self.dataset = dataset
        self._import()
        # Untested due to lack of ideas how to test
        # pylint: disable=protected-access
        self.dataset._origdata = copy.deepcopy(self.dataset.data)
        self.dataset.id = self.source
        self.dataset.label = self.source

    def _import(self):
        """Perform the actual import of data and metadata into the dataset.

        The implementation of the actual import goes in here in all
        classes inheriting from DatasetImporter. This method is automatically
        called by :meth:`import_into`.

        Importing data and metadata includes assigning both to the respective
        fields of the :obj:`aspecd.dataset.Dataset` object. For details of
        its structure, see there.

        Usually, this method will successively call other private/protected
        methods of the importer to perform the required tasks that are
        specific for each data source.

        """


class DatasetImporterFactory:
    """
    Factory for creating importer objects based on the source provided.

    Often, data are available in different formats, and deciding which
    importer is appropriate for a given format can be quite involved. To
    free other classes from having to contain the relevant code, a factory
    can be used.

    Currently, the sole information provided to decide about the
    appropriate importer is the source (a string). A concrete importer
    object is returned by the method :meth:`get_importer`. If no source is
    provided, an exception will be raised.

    The actual code for deciding which type of importer to return in what
    case should be implemented in the non-public method :meth:`_get_importer`
    in any package based on the ASpecD framework.

    In its basic implementation, as done here, the non-public method
    :meth:`_get_importer` returns the importers for ADF, ASDF, and TXT
    depending on the file extension, and in all other cases the standard
    importer.

    This might be a viable way for an own :class:`DatasetImporterFactory`
    implementation in the rare case of having only one single type of data,
    but provides a sensible starting point for own developments.

    Raises
    ------
    aspecd.io.MissingSourceError
        Raised if no source is provided

    """

    def get_importer(self, source=''):
        """
        Return importer object for dataset specified by its source.

        The actual code for deciding which type of importer to return in what
        case should be implemented in the non-public method
        :meth:`_get_importer` in any package based on the ASpecD framework.

        .. note::
            Currently, only filenames/paths are supported, and if ``source``
            does not start with the file separator, the absolute path to the
            current directory is prepended.


        Parameters
        ----------
        source : :class:`str`
            string describing the source of the dataset

            May be a filename or path, a URL/URI, a LOI, or similar

        Returns
        -------
        importer : :class:`aspecd.io.DatasetImporter`
            importer object of appropriate class

        Raises
        ------
        aspecd.io.MissingSourceError
            Raised if no source is provided

        """
        if not source:
            raise aspecd.exceptions.MissingSourceError(
                'A source is required to return an appropriate importer')
        return self._get_importer(source)

    # noinspection PyMethodMayBeStatic
    # pylint: disable=no-self-use
    def _get_importer(self, source):
        if not source.startswith(os.pathsep):
            source = os.path.join(os.path.abspath(os.curdir), source)
        _, file_extension = os.path.splitext(source)
        if file_extension == '.adf':
            return AdfImporter(source=source)
        if file_extension == '.asdf':
            return AsdfImporter(source=source)
        if file_extension == '.txt':
            return TxtImporter(source=source)
        return DatasetImporter(source=source)


class DatasetExporter:
    """Base class for dataset exporter.

    Each class actually exporting data from a dataset to some other should
    inherit from this class.

    To perform the export, call the
    :meth:`~aspecd.dataset.Dataset.export_to` method of the dataset
    the export should be performed for, and provide a reference to the
    actual exporter object to it.

    The actual implementation of the exporting is done in the non-public
    method :meth:`_export` that in turn gets called by :meth:`export_from`
    which is called by the :meth:`aspecd.dataset.Dataset.export_to` method
    of the dataset object.

    Attributes
    ----------
    dataset : :obj:`aspecd.dataset.Dataset`
        dataset to export data and metadata from
    target : string
        specifier of the target the data and metadata will be written to

    Raises
    ------
    aspecd.io.MissingDatasetError
        Raised when no dataset exists to act upon

    """

    def __init__(self, target=None):
        self.target = target
        self.dataset = None

    def export_from(self, dataset=None):
        """Perform the actual export from the given dataset.

        If no dataset is provided at method call, but is set as property in
        the exporter object, the :meth:`aspecd.dataset.Dataset.export_to`
        method of the dataset will be called.

        If no dataset is provided at method call nor as property in the
        object, the method will raise a respective exception.

        The dataset object always calls this method with the respective
        dataset as argument. Therefore, in this case setting the dataset
        property within the exporter object is not necessary.

        The actual export should be implemented within the non-public method
        :meth:`_export`.

        Parameters
        ----------
        dataset : :class:`aspecd.dataset.Dataset`
            Dataset to export data and metadata from

        Raises
        ------
        aspecd.io.MissingDatasetError
            Raised if no dataset is provided.

        """
        if not dataset:
            if self.dataset:
                self.dataset.export_to(self)
            else:
                raise aspecd.exceptions.MissingDatasetError(
                    "No dataset provided")
        else:
            self.dataset = dataset
        self._export()

    def _export(self):
        """Perform the actual export of data and metadata from the dataset.

        The implementation of the actual export goes in here in all
        classes inheriting from DatasetExporter. This method is automatically
        called by :meth:`export_from`.

        Usually, this method will successively call other private/protected
        methods of the exporter to perform the required tasks that are
        specific for each target format.

        """


class RecipeImporter:
    """Base class for recipe importer.

    Each class actually importing recipes into a :obj:`aspecd.tasks.Recipe`
    object should inherit from this class.

    To perform the import, call the
    :meth:`~aspecd.tasks.Recipe.import_from` method of the recipe the
    import should be performed for, and provide a reference to the
    actual importer object to it.

    The actual implementation of the importing is done in the non-public
    method :meth:`_import` that in turn gets called by :meth:`import_into`
    which is called by the :meth:`aspecd.tasks.Recipe.import_from` method
    of the recipe object.

    One question arising when actually implementing an importer for a
    specific file format: How does the information get into the recipe? The
    simple answer: The :meth:`_import` method of the importer knows about the
    recipe and its structure (see :class:`aspecd.tasks.Recipe` for
    details) and creates a dictionary with keys corresponding to the
    respective attributes of the recipe. In turn, it can then call the
    :meth:`aspecd.tasks.Recipe.from_dict` method. In terms of a broader
    software architecture point of view: The recipe knows nothing about the
    importer besides its bare existence and interface, whereas the importer
    knows about the recipe and how to map the information obtained to it.

    Attributes
    ----------
    recipe : :obj:`aspecd.tasks.Recipe`
        recipe to import into
    source : :class:`str`
        specifier of the source the information will be read from

    Raises
    ------
    aspecd.io.MissingRecipeError
        Raised when no dataset exists to act upon

    """

    def __init__(self, source=''):
        self.source = source
        self.recipe = None

    def import_into(self, recipe=None):
        """Perform the actual import into the given recipe.

        If no recipe is provided at method call, but is set as property in
        the importer object, the :meth:`aspecd.tasks.Recipe.import_from`
        method of the recipe will be called.

        If no recipe is provided at method call nor as property in the
        object, the method will raise a respective exception.

        The recipe object always calls this method with the respective
        recipe as argument. Therefore, in this case setting the recipe
        property within the importer object is not necessary.

        The actual import should be implemented within the non-public method
        :meth:`_import`.

        Parameters
        ----------
        recipe : :obj:`aspecd.tasks.Recipe`
            recipe to import into

        Raises
        ------
        aspecd.io.MissingRecipeError
            Raised if no recipe is provided.

        """
        if not recipe:
            if self.recipe:
                self.recipe.import_from(self)
            else:
                raise aspecd.exceptions.MissingRecipeError("No recipe provided")
        else:
            self.recipe = recipe
        self.recipe.filename = self.source
        self._import()

    def _import(self):
        """Perform the actual import into the recipe.

        The implementation of the actual import goes in here in all
        classes inheriting from RecipeImporter. This method is automatically
        called by :meth:`import_into`.

        Importing metadata includes assigning it to the respective fields
        of the :obj:`aspecd.tasks.Recipe` object. For details of
        its structure, see there. To do this, the method should create a
        dictionary that can afterwards be supplied as an argument to a call
        to :meth:`aspecd.tasks.Recipe.from_dict`.

        """


class RecipeExporter:
    """Base class for recipe exporter.

    Each class actually exporting recipes from :obj:`aspecd.tasks.Recipe`
    objects should inherit from this class.

    To perform the export, call the
    :meth:`aspecd.tasks.Recipe.export_to` method of the recipe the export
    should be performed for, and provide a reference to the actual exporter
    object to it.

    The actual implementation of the exporting is done in the non-public
    method :meth:`_export` that in turn gets called by :meth:`export_from`
    which is called by the :meth:`aspecd.tasks.Recipe.export_to` method
    of the recipe object.

    Attributes
    ----------
    recipe : :obj:`aspecd.tasks.Recipe`
        recipe to export information from
    target : string
        specifier of the target the information will be written to

    Raises
    ------
    aspecd.io.MissingRecipeError
        Raised when no dataset exists to act upon

    """

    def __init__(self, target=''):
        self.target = target
        self.recipe = None

    def export_from(self, recipe=None):
        """Perform the actual export from the given recipe.

        If no recipe is provided at method call, but is set as property in
        the exporter object, the :meth:`aspecd.tasks.Recipe.export_to`
        method of the recipe will be called.

        If no recipe is provided at method call nor as property in the
        object, the method will raise a respective exception.

        The recipe object always calls this method with the respective
        recipe as argument. Therefore, in this case setting the recipe
        property within the exporter object is not necessary.

        The actual export should be implemented within the non-public method
        :meth:`_export`.

        Parameters
        ----------
        recipe : :class:`aspecd.tasks.Recipe`
            Recipe to export from

        Raises
        ------
        aspecd.io.MissingRecipeError
            Raised if no recipe is provided.

        """
        if not recipe:
            if self.recipe:
                self.recipe.export_to(self)
            else:
                raise aspecd.exceptions.MissingRecipeError("No recipe provided")
        else:
            self.recipe = recipe
        self._export()

    def _export(self):
        """Perform the actual export from the recipe.

        The implementation of the actual export goes in here in all
        classes inheriting from RecipeExporter. This method is automatically
        called by :meth:`export_from`.

        Usually, this method will first create a dictionary from the recipe
        using the :meth:`aspecd.tasks.Recipe.to_dict` method. This
        dictionary can afterwards be further processed and written to some
        file.

        """


class RecipeYamlImporter(RecipeImporter):
    """
    Recipe importer for importing from YAML files.

    The YAML file needs to have a structure compatible to the actual
    recipe, such that the dict created from reading the YAML file can be
    directly fed into the :meth:`aspecd.tasks.Recipe.from_dict` method.

    The order of entries of the YAML file is preserved due to using ordered
    dictionaries (:class:`collections.OrderedDict`) internally.

    Parameters
    ----------
    source : :class:`str`
        filename of a YAML file to read from

    """

    def __init__(self, source=''):
        super().__init__(source=source)

    def _import(self):
        yaml = aspecd.utils.Yaml()
        yaml.read_from(filename=self.source)
        self.recipe.from_dict(yaml.dict)


class RecipeYamlExporter(RecipeExporter):
    """
    Recipe exporter for exporting to YAML files.

    The YAML file will have a structure corresponding to the output of the
    :meth:`aspecd.tasks.Recipe.to_dict` method of the recipe object.

    Parameters
    ----------
    target : :class:`str`
        filename of a YAML file to write to

    """

    def __init__(self, target=''):
        super().__init__(target=target)

    def _export(self):
        yaml = aspecd.utils.Yaml()
        yaml.dict = self.recipe.to_dict()
        yaml.write_to(filename=self.target)


class AdfExporter(DatasetExporter):
    """
    Dataset exporter for exporting to ASpecD dataset format.

    The ASpecD dataset format is vaguely reminiscent of the Open Document
    Format, *i.e.* a zipped directory containing structured data (in this
    case in form of a YAML file) and binary data in a corresponding
    subdirectory.

    As PyYAML is not capable of dealing with NumPy arrays out of the box,
    those are dealt with separately. Small arrays are stored inline as
    lists, larger arrays in separate files. For details, see the
    :class:`aspecd.utils.Yaml` class.

    The data format tries to be as self-contained as possible,
    using standard file formats and a brief description of its layout
    contained within the archive. Collecting the contents in a single ZIP
    archive allows the user to deal with a single file for a dataset,
    while more advanced users can easily dig into the details and write
    importers for other platforms and programming languages, making the
    format rather platform-independent and future-safe. Due to using binary
    representation for larger numerical arrays, the format should be more
    memory-efficient than other formats.

    """

    def __init__(self, target=None):
        super().__init__(target=target)
        self.extension = '.adf'
        self._filenames = {
            'dataset': 'dataset.yaml',
            'version': 'VERSION',
            'readme': 'README',
        }
        self._bin_dir = 'binaryData'
        self._tempdir_name = ''
        self._version = '1.0.0'

    def _export(self):
        if not self.target:
            raise aspecd.exceptions.MissingTargetError
        with tempfile.TemporaryDirectory() as tempdir:
            self._tempdir_name = tempdir
            self._create_files()
            self._create_zip_archive()

    def _create_zip_archive(self):
        with zipfile.ZipFile(self.target + self.extension, 'w') as zipped_file:
            for filename in self._filenames.values():
                zipped_file.write(
                    filename=os.path.join(self._tempdir_name, filename),
                    arcname=filename)
            bin_dir_path = os.path.join(self._tempdir_name, self._bin_dir)
            zipped_file.write(
                filename=os.path.join(bin_dir_path),
                arcname=self._bin_dir)
            for filename in os.listdir(bin_dir_path):
                zipped_file.write(
                    filename=os.path.join(bin_dir_path, filename),
                    arcname=os.path.join(self._bin_dir, filename))

    def _create_files(self):
        self._create_dataset_yaml()
        self._create_version_file()
        self._create_readme_file()

    def _create_dataset_yaml(self):
        bin_dir_path = os.path.join(self._tempdir_name, self._bin_dir)
        os.mkdir(bin_dir_path)
        yaml = aspecd.utils.Yaml()
        yaml.binary_directory = bin_dir_path
        yaml.dict = self.dataset.to_dict()
        yaml.serialise_numpy_arrays()
        yaml.write_to(filename=os.path.join(self._tempdir_name,
                                            self._filenames["dataset"]))

    def _create_version_file(self):
        with open(os.path.join(self._tempdir_name,
                               self._filenames["version"]), 'w+') as file:
            file.write(self._version)

    def _create_readme_file(self):
        readme_contents = (
            "Readme\n"
            "======\n\n"
            "This directory contains an ASpecD dataset stored in the\n"
            "ASpecD dataset format (adf).\n\n"
            "What follows is a bit of information on the meaning of\n"
            "each of the files in the directory.\n"
            "Sources of further information on the file format\n"
            "are provided at the end of the file.\n\n"
            "Copyright (c) 2021, Till Biskup\n"
            "2021-01-04\n\n"
            "Files and their meaning\n"
            "-----------------------\n\n"
            "* dataset.yaml - text/YAML\n"
            "  hierarchical metadata store\n\n"
            "* binaryData/<filename>.npy - NumPy binary\n"
            "  numerical data of the dataset stored in NumPy format\n\n"
            "  Only arrays exceeding a certain threshold are stored\n"
            "  in binary format, mainly to save space and preserve\n"
            "  numerical accuracy.\n\n"
            "* VERSION - text\n"
            "  version number of the dataset format\n\n"
            "  The version number follows the semantic versioning scheme.\n\n"
            "* README - text\n"
            "  This file\n\n"
            "Further information\n"
            "-------------------\n\n"
            "More information can be found on the web in the\n"
            "ASpecD package documentation:\n\n"
            "https://docs.aspecd.de/adf.html\n"
        )
        with open(os.path.join(self._tempdir_name,
                               self._filenames["readme"]), 'w+') as file:
            file.write(readme_contents)


class AdfImporter(DatasetImporter):
    """
    Dataset importer for importing from ASpecD dataset format.

    For more details of the ASpecD dataset format, see the
    :class:`aspecd.io.AdfExporter` class.

    """

    def __init__(self, source=None):
        super().__init__(source=source)
        self.extension = '.adf'
        self._dataset_yaml_filename = 'dataset.yaml'
        self._bin_dir = 'binaryData'

    def _import(self):
        with tempfile.TemporaryDirectory() as tempdir:
            with zipfile.ZipFile(self.source + self.extension, 'r') as \
                    zipped_file:
                zipped_file.extractall(path=tempdir)
                yaml = aspecd.utils.Yaml()
                yaml.binary_directory = os.path.join(tempdir, self._bin_dir)
                yaml.read_from(os.path.join(tempdir,
                                            self._dataset_yaml_filename))
                yaml.deserialise_numpy_arrays()
        self.dataset.from_dict(yaml.dict)


class AsdfExporter(DatasetExporter):
    """
    Dataset exporter for exporting to Advanced Scientific Data Format (ASDF).

    For more information on ASDF, see the
    `homepage of the asdf package <https://asdf.readthedocs.io/en/stable/>`_,
    and its `format specification <https://asdf-standard.readthedocs.io/>`_.

    """

    def __init__(self, target=None):
        super().__init__(target=target)
        self.extension = '.asdf'

    def _export(self):
        if not self.target:
            raise aspecd.exceptions.MissingTargetError

        dataset_dict = self.dataset.to_dict()
        dataset_dict["dataset_history"] = dataset_dict.pop("history")
        asdf_file = asdf.AsdfFile(dataset_dict)
        asdf_file.write_to(self.target + self.extension)


class AsdfImporter(DatasetImporter):
    """
    Dataset importer for importing from Advanced Scientific Data Format (ASDF).

    For more information on ASDF, see the
    `homepage of the asdf package <https://asdf.readthedocs.io/en/stable/>`_,
    and its `format specification <https://asdf-standard.readthedocs.io/>`_.

    """

    def __init__(self, source=None):
        super().__init__(source=source)
        self.extension = '.asdf'

    def _import(self):
        with asdf.open(self.source + self.extension, lazy_load=False,
                       copy_arrays=True) as asdf_file:
            dataset_dict = asdf_file.tree
            dataset_dict["history"] = dataset_dict.pop("dataset_history")
            self.dataset.from_dict(dataset_dict)


class TxtImporter(DatasetImporter):
    """
    Dataset importer for importing from plain text files (TXT).

    Plain text files have often the disadvantage of no accompanying metadata,
    therefore the use of plain text files for data storage is highly
    discouraged, besides other problems like inherent low resolution/accuracy
    or otherwise large file sizes.

    The main reason for this class to exist is that it provides a simple way
    to showcase ASpecD functionality reading from primitive data sources.
    Besides that, sometimes you will encounter plain text files.

    .. note::
        The importer relies on :func:`numpy.loadtxt` for reading text files.
        Hence, the same limitations apply, *e.g.* the dot as decimal separator.

    If your data consist of two columns, the first will automatically be
    interpreted as the *x* axis. In all other cases, data will be read as is
    and no axes values explicitly written.

    """

    def __init__(self, source=None):
        super().__init__(source=source)
        self.extension = '.txt'

    def _import(self):
        data = np.loadtxt(self.source)
        if len(np.shape(data)) > 1 and np.shape(data)[1] == 2:
            self.dataset.data.axes[0].values = data[:, 0]
            data = data[:, 1]
        self.dataset.data.data = data
