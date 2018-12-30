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


class Recipe(aspecd.utils.ToDictMixin):
    """
    Recipes get cooked by chefs in recipe-driven data analysis.

    A recipe contains a list of tasks to be performed on a list of
    datasets. From a user's perspective, recipes "live" usually in YAML
    files from where they are read into a :obj:`aspecd.tasks.Recipe` object
    using its respective :meth:`read_from` method. Similarly, a given
    recipe can be written back into a YAML file using the :meth:`write_to`
    method.

    Attributes
    ----------
    datasets : `list`
        List of datasets the tasks should be performed for
    tasks : `list`
        List of tasks to be performed on the datasets

    Raises
    ------
    MissingFilenameError
        Raised if no filename is given to read from/write to.

    """

    def __init__(self):
        super().__init__()
        self.datasets = []
        self.tasks = []

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
        if 'datasets' in yaml.dict:
            self.datasets = yaml.dict['datasets']
        if 'tasks' in yaml.dict:
            self.tasks = yaml.dict['tasks']

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

    Parameters
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

        Parameters
        ----------
        recipe : :class:`aspecd.tasks.Recipe`
            Recipe to cook, i.e. to carry out

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
            problematic and if so, how to cope with it.

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
