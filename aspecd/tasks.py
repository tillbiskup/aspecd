"""
Tasks.

One main aspect of tasks is the constituents of a recipe-driven data
analysis, i.e. :class:`aspecd.tasks.Recipe` and :class:`aspecd.tasks.Chef`.
In its simplest form, a recipe gets cooked by a chef, resulting in a series
of tasks being performed on a list of datasets.

From a user's perspective, a recipe is usually stored in a YAML file. This
allows to easily create and modify recipes without knowing too much about
the underlying processes.
"""

import aspecd.io
import aspecd.utils


class Error(Exception):
    """Base class for exceptions in this module."""

    pass


class MissingRecipeError(Error):
    """Exception raised trying to cook without recipe

    Attributes
    ----------
    message : `str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class MissingFilenameError(Error):
    """Exception raised when expecting a filename but none is provided

    Attributes
    ----------
    message : `str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class MissingDictError(Error):
    """Exception raised when expecting a filename but none is provided

    Attributes
    ----------
    message : `str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class MissingImporterFactoryError(Error):
    """Exception raised when expecting a filename but none is provided

    Attributes
    ----------
    message : `str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class Recipe():
    """
    Recipes get cooked by chefs in recipe-driven data analysis.

    A recipe contains a list of tasks to be performed on a list of
    datasets. From a user's perspective, recipes "live" usually in YAML
    files from where they are read into a :obj:`aspecd.tasks.Recipe` object
    using its respective :meth:`read_from` method. Similarly, a given
    recipe can be written back into a YAML file using the :meth:`write_to`
    method.

    .. todo::
        Rename :meth:`read_from` and :meth:`write_to` in
        :meth:`import_from` and :meth:`export_to` and create
        importer/exporter base classes in :mod:`aspecd.io` module.

    .. todo::
        Can recipes have LOIs themselves and therefore be retrieved from
        the extended data safe? Might be a sensible option, although
        generic LOIs are much harder to create than LOIs for datasets and
        alike.

    Attributes
    ----------
    datasets : `list`
        List of datasets the tasks should be performed for

        Each dataset is an object of class :class:`aspecd.dataset.Dataset`.
    tasks : `list`
        List of tasks to be performed on the datasets

        Each task is an object of class :class:`aspecd.tasks.Task`.
    importer_factory : :class:`aspecd.io.ImporterFactory`
        Factory for importers used to import datasets

    Raises
    ------
    MissingDictError
        Raised if no dict is provided.
    MissingFilenameError
        Raised if no filename is given to read from/write to.
    MissingImporterFactoryError
        Raised if :attr:`importer_factory` is invalid.

    """

    def __init__(self):
        super().__init__()
        self.datasets = []
        self.tasks = list()
        self.importer_factory = None

    def from_dict(self, dict_=None):
        """
        Set attributes from dictionary.

        Loads datasets and creates :obj:`aspecd.tasks.Task` objects that
        are stored as lists respectively.

        Parameters
        ----------
        dict_ : `dict`
            Dictionary containing information of a recipe.

        Raises
        ------
        MissingDictError
            Raised if no dict is provided.
        MissingImporterFactoryError
            Raised if :attr:`importer_factory` is invalid.

        """
        if not dict_:
            raise MissingDictError
        if not self.importer_factory:
            raise MissingImporterFactoryError
        if 'datasets' in dict_:
            for key in dict_['datasets']:
                self._append_dataset(key)
        if 'tasks' in dict_:
            for key in dict_['tasks']:
                self._append_task(key)

    def _append_dataset(self, key):
        dataset = aspecd.dataset.Dataset()
        importer = self.importer_factory.get_importer(source=key)
        dataset.import_from(importer)
        self.datasets.append(dataset)

    def _append_task(self, key):
        task = Task()
        task.from_dict(key)
        self.tasks.append(task)

    def to_dict(self):
        """
        Return dict from attributes.

        Returns
        -------
        dict_ : `dict`
            Dictionary with fields "datasets" and "tasks"

        """
        dict_ = {'datasets': [], 'tasks': []}
        for dataset in self.datasets:
            dict_['datasets'].append(dataset.source)
        for task in self.tasks:
            dict_['tasks'].append(task.to_dict())
        return dict_

    def read_from(self, filename=''):
        """
        Read recipe from YAML file.

        Parameters
        ----------
        filename : `str`
            Name of the YAML file to read from.

        Raises
        ------
        MissingFilenameError
            Raised if no filename is given to read from.

        """
        if not filename:
            raise MissingFilenameError
        yaml = aspecd.io.Yaml()
        yaml.read_from(filename=filename)
        self.from_dict(yaml.dict)

    def write_to(self, filename=''):
        """
        Write recipe to YAML file.

        Parameters
        ----------
        filename : `str`
            Name of the YAML file to write to.

        Raises
        ------
        MissingFilenameError
            Raised if no filename is given to write to.

        """
        if not filename:
            raise MissingFilenameError
        yaml = aspecd.io.Yaml()
        yaml.dict = self.to_dict()
        yaml.write_to(filename=filename)


class Chef:
    """
    Chefs cook recipes in recipe-driven data analysis.

    As a result, they create some kind of history of the tasks performed.
    In this respect, they make the history independent of a singe dataset
    and allow to trace processing and analysis of multiple datasets. One
    necessary prerequisite is therefore the LOI as a persistent and
    unique identifier for each dataset.

    .. todo::
        Decide about the way this kind of history gets stored and
        persisted. One reasonable idea might be to persist it in a form
        that can be used as a recipe again. The file format for persistence
        will most probably be YAML for the time being.

    Parameters
    ----------
    recipe : :class:`aspecd.tasks.Recipe`
        Recipe to cook, i.e. to carry out

    Attributes
    ----------
    recipe : :class:`aspecd.tasks.Recipe`
        Recipe to cook, i.e. to carry out

    Raises
    ------
    MissingRecipeError
        Raised if no recipe is available to be cooked

    """

    def __init__(self, recipe=None):
        self.recipe = recipe

    def cook(self, recipe=None):
        """
        Cook recipe, i.e. carry out tasks contained therein.

        A recipe is an object of class :class:`aspecd.tasks.Recipe` and
        contains both, a list of datasets and a list of tasks to be
        performed on these datasets.

        Parameters
        ----------
        recipe : :class:`aspecd.tasks.Recipe`
            Recipe to cook, i.e. tasks to carry out on particular datasets

        Raises
        ------
        MissingRecipeError
            Raised if no recipe is available to be cooked

        """
        self.recipe = recipe
        if not self.recipe:
            raise MissingRecipeError


class Task(aspecd.utils.ToDictMixin):
    """
    Property class storing information for a single task.

    Attributes
    ----------
    kind : `str`
        Kind of task.

        Corresponds to module name the type (class) is defined in.
    type : `str`
        Type of task.

        Corresponds to the class name eventually responsible for performing
        the task.
    metadata : `dict`
        Metadata necessary to perform the task.

        Should have keys corresponding to the properties of the class given
        as type attribute.
    apply_to : `list`
        List of datasets the task should be applied to.

        Defaults to an empty list, meaning that the task will be performed
        for all datasets contained in a :class:`aspecd.tasks.Recipe`.

        .. todo::
            What kind of information should be stored in this list? Numbers
            corresponding to the indices in the datasets list in a recipe?
            Or better LOIs that can be compared to the list of datasets?
            The latter seems more robust, as changes in the order of
            datasets do not affect the information.

    Raises
    ------
    MissingDictError
        Raised if no dict is provided when calling :meth:`from_dict`.

    """

    def __init__(self):
        super().__init__()
        self.kind = ''
        self.type = ''
        self.metadata = dict()
        self.apply_to = []

    def from_dict(self, dict_=None):
        """
        Set attributes from dictionary.

        Parameters
        ----------
        dict_ : `dict`
            Dictionary containing information of a task.

        Raises
        ------
        MissingDictError
            Raised if no dict is provided.

        """
        if not dict_:
            raise MissingDictError
        for key in dict_:
            if hasattr(self, key):
                setattr(self, key, dict_[key])

    def get_object(self):
        """
        Return object for a particular task including all attributes.

        Returns
        -------
        obj : `object`
            Object of a class defined in the :attr:`type` attribute of a task

        """
        obj = self._create_object()
        self._set_object_attributes(obj)
        return obj

    def _create_object(self):
        """
        Create object for a particular task.

        To create the object, the current package is prepended to kind and
        type stored in :attr:`kind' and :attr:`type`, respectively.

        .. todo::
            Think about whether preprending the current package gets
            problematic and if so, how to cope with it. If another package
            than the current one is necessary, this information needs to be
            stored in the persisted recipe (i.e., usually a YAML file),
            either in an additional field or as a prefix to the kind
            attribute. In any case, using a try...except clause might be an
            option.

        Returns
        -------
        obj : `object`
            Object of a class defined in the :attr:`type` attribute of a task

        """
        class_name = '.'.join([aspecd.utils.package_name(self),
                               self.kind,
                               self.type])
        obj = aspecd.utils.object_from_class_name(class_name)
        return obj

    def _set_object_attributes(self, obj):
        """
        Set attributes in object from the keys of the :attr:`metadata` dict.

        Only those keys that have a matching attribute in the object are
        actually mapped, all others silently ignored.

        .. todo::
            Eventually, with the advent of logging in the ASpecD framework,
            it might be sensible to at least add a log message if a key
            gets ignored, such that it is no longer silently ignored. This
            might be helpful for debugging purposes.

        Parameters
        ----------
        obj : `object`
            Object of a class defined in the :attr:`type` attribute of a task

        """
        for key in self.metadata:
            if hasattr(obj, key):
                setattr(obj, key, self.metadata[key])
