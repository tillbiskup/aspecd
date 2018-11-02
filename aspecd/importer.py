"""Importer."""


class Error(Exception):
    """Base class for exceptions in this module."""

    pass


class MissingDatasetError(Error):
    """Exception raised when no dataset exists to act on.

    Attributes
    ----------
    message : `str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class Importer:
    """Base class for importer.

    Each class actually importing data into a dataset should inherit from this
    class.

    To perform the import, call the :meth:`import_from` method of the dataset
    the import should be performed for, and provide a reference to the
    actual importer object to it.

    The actual implementation of the importing is done in the private method
    :meth:`_import` that in turn gets called by :meth:`import_into`
    which is called by the :meth:`aspecd.dataset.Dataset.import_from` method
    of the dataset object.

    Attributes
    ----------
    dataset : :obj:`aspecd.dataset.Dataset`
        dataset to import data and metadata into
    source : :obj:`string`
        specifier of the source the data and metadata will be read from

    Raises
    ------
    MissingDatasetError
        Raised when no dataset exists to act upon

    """

    def __init__(self, source=None):
        self.source = source
        self.dataset = None

    def import_into(self, dataset=None):
        """Perform the actual import into the given dataset.

        If no dataset is provided at method call, but is set as property in the
        Importer object, the :meth:`aspecd.dataset.Dataset.import_from` method
        of the dataset will be called.

        If no dataset is provided at method call nor as property in the object,
        the method will raise a respective exception.

        The Dataset object always calls this method with the respective dataset
        as argument. Therefore, in this case setting the dataset property
        within the Importer object is not necessary.

        The actual import should be implemented within the private method
        :meth:`_import`.

        Parameters
        ----------
        dataset : `aspecd.dataset.Dataset`
            Dataset to import data and metadata into

        Raises
        ------
        MissingDatasetError
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

    def _import(self):
        """Perform the actual import of the data and metadata into the dataset.

        The implementation of the actual import goes in here in all
        classes inheriting from Importer. This method is automatically
        called by :meth:`import_into`.

        Importing data and metadata includes assigning both to the respective
        fields of the :obj:`aspecd.dataset.Dataset` object. For details of
        its structure, see there.

        Usually, this method will successively call other private/protected
        methods of the importer to perform the required tasks that are
        specific for each data source.

        """
        pass
