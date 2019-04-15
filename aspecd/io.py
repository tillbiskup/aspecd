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

"""

import aspecd.utils


class Error(Exception):
    """Base class for exceptions in this module."""

    pass


class MissingDatasetError(Error):
    """Exception raised when no dataset exists to act on.

    Attributes
    ----------
    message : :class:`str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class MissingSourceError(Error):
    """Exception raised when expecting a filename but none is provided

    Attributes
    ----------
    message : :class:`str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class MissingRecipeError(Error):
    """Exception raised when no recipe exists to act on.

    Attributes
    ----------
    message : :class:`str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


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
                raise MissingDatasetError("No dataset provided")
        else:
            self.dataset = dataset
        self._import()
        self.dataset.id = self.source

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
        pass


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

    In its most basic implementation, as done here, the non-public method
    :meth:`_get_importer` simply returns the standard importer::

        def _get_importer(self, source):
            return DatasetImporter(source=source)

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
            raise MissingSourceError('A source is required to return an '
                                     'appropriate importer')
        return self._get_importer(source)

    # noinspection PyMethodMayBeStatic
    # pylint: disable=no-self-use
    def _get_importer(self, source):
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
                raise MissingDatasetError("No dataset provided")
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
        pass


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
                raise MissingRecipeError("No recipe provided")
        else:
            self.recipe = recipe
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
        pass


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
                raise MissingRecipeError("No recipe provided")
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
        pass


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
