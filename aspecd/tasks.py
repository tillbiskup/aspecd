"""
Constituents of a recipe-driven data analysis.

One main aspect of tasks is to provide the constituents of a recipe-driven
data analysis, i.e. :class:`aspecd.tasks.Recipe` and
:class:`aspecd.tasks.Chef`. In its simplest form, a recipe gets cooked by a
chef, resulting in a series of tasks being performed on a list of datasets.

From a user's perspective, a recipe is usually stored in a YAML file. This
allows to easily create and modify recipes without knowing too much about
the underlying processes.

Recipes always consist of two major parts: A list of datasets to operate
on, and a list of tasks to be performed on the datasets. Of course, you can
specify for each task on which datasets it should be performed, and if
possible, whether it should be performed on each dataset separately or
combined. The latter is particularly interesting for representations (e.g.,
plots) consisting of multiple datasets, or analysis steps spanning multiple
datasets.

Each task is internally represented by an :obj:`aspecd.tasks.Task` object,
more precisely an object instantiated from a subclass of
:class:`aspecd.tasks.Task`. This polymorphism of task classes makes it
possible to easily extend the scope.

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
    message : :class:`str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class MissingDictError(Error):
    """Exception raised when expecting a filename but none is provided

    Attributes
    ----------
    message : :class:`str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class MissingImporterError(Error):
    """Exception raised when no Importer instance is provided

    Attributes
    ----------
    message : :class:`str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class MissingExporterError(Error):
    """Exception raised when no Importer instance is provided

    Attributes
    ----------
    message : :class:`str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class MissingImporterFactoryError(Error):
    """Exception raised when no ImporterFactory instance is provided

    Attributes
    ----------
    message : :class:`str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class MissingTaskFactoryError(Error):
    """Exception raised when no TaskFactory instance is provided

    Attributes
    ----------
    message : :class:`str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class MissingTaskDescriptionError(Error):
    """Exception raised when no description for creating a task is provided

    Attributes
    ----------
    message : :class:`str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class MissingDatasetIdentifierError(Error):
    """Exception raised when no dataset id is provided

    Attributes
    ----------
    message : :class:`str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class Recipe:
    """
    Recipes get cooked by chefs in recipe-driven data analysis.

    A recipe contains a list of tasks to be performed on a list of
    datasets. From a user's perspective, recipes reside usually in YAML
    files from where they are imported into an :obj:`aspecd.tasks.Recipe`
    object using its respective :meth:`import_into` method and an object of
    class :class:`aspecd.io.RecipeYamlImporter`. Similarly, a given
    recipe can be exported back to a YAML file using the :meth:`export_to`
    method and an object of class :class:`aspecd.io.RecipeYamlExporter`.

    In contrast to the persistent form of a recipe (e.g., as file on the
    file system), the object contains actual datasets and tasks that are
    objects of the respective classes. Therefore, the attributes of a
    recipe are normally set by the respective methods from either a file or
    a dictionary (that in turn will normally be created from contents of a
    file).

    Importing datasets is delegated to an
    :class:`aspecd.io.DatasetImporterFactory` instance stored in
    :attr:`importer_factory`. This provides a maximum of flexibility but
    makes it necessary to specify (and first implement) such factory in
    packages derived from the ASpecD framework.

    .. todo::
        Can recipes have LOIs themselves and therefore be retrieved from
        the extended data safe? Might be a sensible option, although
        generic LOIs are much harder to create than LOIs for datasets and
        alike.

    Attributes
    ----------
    datasets : :class:`list`
        List of datasets the tasks should be performed for

        Each dataset is an object of class :class:`aspecd.dataset.Dataset`.
    tasks : :class:`list`
        List of tasks to be performed on the datasets

        Each task is an object of class :class:`aspecd.tasks.Task`.
    importer_factory : :class:`aspecd.io.DatasetImporterFactory`
        Factory for importers used to import datasets

        If no factory is set, but a recipe imported from a file or set from
        a dictionary, an exception will be raised.
    task_factory : :class:`aspecd.tasks.TaskFactory`
        Factory for tasks

        Defaults to an object of class :class:`aspecd.tasks.TaskFactory`.

        If no factory is set, but a recipe imported from a file or set from
        a dictionary, an exception will be raised.

    Raises
    ------
    MissingDictError
        Raised if no dict is provided.
    MissingImporterError
        Raised if no importer is provided.
    MissingExporterError
        Raised if no exporter is provided.
    MissingImporterFactoryError
        Raised if :attr:`importer_factory` is invalid.
    MissingTaskFactoryError
        Raised if :attr:`task_factory` is invalid.

    """

    def __init__(self):
        super().__init__()
        self.datasets = []
        self.tasks = list()
        self.importer_factory = None
        self.task_factory = TaskFactory()

    def from_dict(self, dict_=None):
        """
        Set attributes from dictionary.

        Loads datasets and creates :obj:`aspecd.tasks.Task` objects that
        are stored as lists respectively.

        Parameters
        ----------
        dict_ : :class:`dict`
            Dictionary containing information of a recipe.

        Raises
        ------
        MissingDictError
            Raised if no dict is provided.
        MissingImporterFactoryError
            Raised if :attr:`importer_factory` is invalid.
        MissingTaskFactoryError
            Raised if :attr:`task_factory` is invalid.

        """
        if not dict_:
            raise MissingDictError
        if not self.importer_factory:
            raise MissingImporterFactoryError
        if not self.task_factory:
            raise MissingTaskFactoryError
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
        task = self.task_factory.get_task_from_dict(key)
        task.from_dict(key)
        task.recipe = self
        self.tasks.append(task)

    def to_dict(self):
        """
        Return dict from attributes.

        Returns
        -------
        dict_ : :class:`dict`
            Dictionary with fields "datasets" and "tasks"

        """
        dict_ = {'datasets': [], 'tasks': []}
        for dataset in self.datasets:
            dict_['datasets'].append(dataset.source)
        for task in self.tasks:
            dict_['tasks'].append(task.to_dict())
        return dict_

    def import_from(self, importer=None):
        """
        Import recipe using importer.

        Importers can be created to read recipes from different sources.
        Thus the recipe as such is entirely independent of the persistence
        layer.

        Parameters
        ----------
        importer : :class:`aspecd.io.RecipeImporter`
            importer used to actually import recipe

        Raises
        ------
        MissingImporterError
            Raised if no importer is provided

        """
        if not importer:
            raise MissingImporterError('An importer instance is needed to '
                                       'import a recipe.')
        importer.import_into(self)

    def export_to(self, exporter=None):
        """
        Export recipe using exporter.

        Exporters can be created to write recipes to different targets.
        Thus the recipe as such is entirely independent of the persistence
        layer.

        Parameters
        ----------
        exporter : :class:`aspecd.io.RecipeExporter`
            exporter used to actually export recipe

        Raises
        ------
        MissingExporterError
            Raised if no exporter is provided

        """
        if not exporter:
            raise MissingExporterError('An exporter instance is needed to '
                                       'export a recipe.')
        exporter.export_from(self)

    def get_dataset(self, identifier=''):
        """
        Return dataset corresponding to given identifier.

        Parameters
        ----------
        identifier : :class:`str`
            Identifier matching the :attr:`aspecd.dataset.Dataset.id`
            attribute.

        Returns
        -------
        dataset : :class:`aspecd.dataset.Dataset`
            Dataset corresponding to given identifier

            If no dataset corresponding to the given identifier could be
            found, :obj:`None` is returned.

        Raises
        ------
        MissingDatasetIdentifierError
            Raised if no identifier is provided.

        """
        if not identifier:
            raise MissingDatasetIdentifierError
        return_value = None
        for dataset in self.datasets:
            if dataset.id == identifier:
                return_value = dataset
        return return_value


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
        self._assign_recipe(recipe)
        for task in self.recipe.tasks:
            task.perform()

    def _assign_recipe(self, recipe):
        if not recipe:
            if not self.recipe:
                raise MissingRecipeError
        else:
            self.recipe = recipe


class Task(aspecd.utils.ToDictMixin):
    """
    Base class storing information for a single task.

    Different underlying objects used to actually perform the respective
    task have different requirements and different signatures. In order to
    generically perform a task, for each kind of task -- such as
    processing, analysis, plotting -- this class needs to be subclassed.

    Attributes
    ----------
    kind : :class:`str`
        Kind of task.

        Usually corresponds to the module name the type (class) is defined in.
        See the note below for special cases.
    type : :class:`str`
        Type of task.

        Corresponds to the class name eventually responsible for performing
        the task.
    metadata : :class:`dict`
        Metadata necessary to perform the task.

        Should have keys corresponding to the properties of the class given
        as type attribute.
    apply_to : :class:`list`
        List of datasets the task should be applied to.

        Defaults to an empty list, meaning that the task will be performed
        for all datasets contained in a :class:`aspecd.tasks.Recipe`.

        Each dataset is referred to by the value of its
        :attr:`aspecd.dataset.Dataset.source` attribute. This should be
        unique and can consist of a filename, path, URL/URI, LOI, or alike.
    recipe : :class:`aspecd.tasks.Recipe`
        Recipe containing the task and the list of datasets the task refers to


    .. note::
        A note to developers: Usually, the :attr:`aspecd.tasks.Task.kind`
        attribute is identical to the module name the respective class
        resides in. However, sometimes this is not the case, as with the
        plotters. In this case, an additional, non-public attribute
        :attr:`aspecd.tasks.Task._module` can be set in classes derived from
        :class:`aspecd.tasks.Task`.


    Raises
    ------
    MissingDictError
        Raised if no dict is provided when calling :meth:`from_dict`.
    MissingRecipeError
        Raised if no recipe is available upon performing the task.

    """

    def __init__(self, recipe=None):
        super().__init__()
        self.kind = ''
        self.type = ''
        self.metadata = dict()
        self.apply_to = []
        self.recipe = recipe
        self._module = ''

    def from_dict(self, dict_=None):
        """
        Set attributes from dictionary.

        Parameters
        ----------
        dict_ : :class:`dict`
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

    def perform(self):
        """
        Call the appropriate method of the underlying object.

        The actual implementation is contained in the non-public method
        :meth:`aspecd.tasks.Task._perform`.

        Different underlying objects have different methods used to
        actually perform the respective task. In order to generically
        perform a task, classes derived from the :class:`aspecd.tasks.Task`
        base class need to override :meth:`aspecd.tasks.Task._perform`
        accordingly.

        Use :meth:`aspecd.tasks.Task.get_object` to get an instance of the
        actual object necessary to perform the task, and afterwards call
        its appropriate method.

        Similarly, to get the actual dataset using the dataset id stored in
        :attr:`aspecd.tasks.Task.apply_to`, use the method
        :meth:`aspecd.tasks.Recipe.get_dataset` of the recipe stored in
        :attr:`aspecd.tasks.Task.recipe`.

        Raises
        ------
        MissingRecipeError
            Raised if no recipe is available.

        """
        if not self.recipe:
            raise MissingRecipeError
        if not self.apply_to:
            for dataset in self.recipe.datasets:
                self.apply_to.append(dataset.id)
        self._perform()

    def _perform(self):
        """
        Call the appropriate method of the underlying object.

        Classes derived from :class:`aspecd.tasks.Task` need to override
        this method and provide the actual implementation.

        """
        pass

    def get_object(self):
        """
        Return object for a particular task including all attributes.

        Returns
        -------
        obj : :class:`object`
            Object of a class defined in the :attr:`type` attribute of a task

        """
        obj = self._create_object()
        self._set_object_attributes(obj)
        return obj

    def _create_object(self):
        """
        Create object for a particular task.

        In case no object can be retrieved from the class name provided,
        the current package is prepended to kind and type stored in
        :attr:`kind' and :attr:`type`, respectively. This allows for
        specifying explicit class names including packages, but at the same
        time to omit the package name for classes from the current package.

        Returns
        -------
        obj : `object`
            Object of a class defined in the :attr:`type` attribute of a task

        """
        if self._module:
            class_name = '.'.join([self._module, self.type])
        else:
            class_name = '.'.join([self.kind, self.type])
        try:
            obj = aspecd.utils.object_from_class_name(class_name)
        except ImportError:
            package_name = aspecd.utils.package_name(self)
            class_name = '.'.join([package_name, class_name])
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


class ProcessingTask(Task):
    """
    Processing step defined as task in recipe-driven data analysis.

    Processing steps will always be performed individually for each dataset.

    """

    def _perform(self):
        for dataset_id in self.apply_to:
            dataset = self.recipe.get_dataset(dataset_id)
            task = self.get_object()
            # noinspection PyUnresolvedReferences
            task.process(dataset=dataset)


class AnalysisTask(Task):
    """
    Analysis step defined as task in recipe-driven data analysis.

    Analysis steps can be performed individually for each dataset or the
    results combined, depending on the type of analysis step.

    """

    def _perform(self):
        for dataset_id in self.apply_to:
            dataset = self.recipe.get_dataset(dataset_id)
            task = self.get_object()
            # noinspection PyUnresolvedReferences
            task.analyse(dataset=dataset)


class AnnotationTask(Task):
    """
    Annotation step defined as task in recipe-driven data analysis.

    Annotation steps will always be performed individually for each dataset.

    """

    def _perform(self):
        for dataset_id in self.apply_to:
            dataset = self.recipe.get_dataset(dataset_id)
            task = self.get_object()
            # noinspection PyUnresolvedReferences
            task.annotate(dataset=dataset)


class SingleplotTask(Task):
    """
    Singleplot step defined as task in recipe-driven data analysis.

    Singleplot steps can only be performed individually for each dataset.
    For plots combining multiple datasets,
    see :class:`aspecd.tasks.MultiplotTask`.

    """

    def __init__(self):
        super().__init__()
        self._module = 'plotting'

    def _perform(self):
        for dataset_id in self.apply_to:
            dataset = self.recipe.get_dataset(dataset_id)
            task = self.get_object()
            # noinspection PyUnresolvedReferences
            task.plot(dataset=dataset)


class ReportTask(Task):
    """
    Reporting step defined as task in recipe-driven data analysis.

    Reporting steps can be performed individually for each dataset or the
    results combined, depending on the type of analysis step.

    """

    pass


class TaskFactory:
    """
    Factory for creating task objects based on the kind provided.

    The kind reflects the name of the module the actual object required for
    performing the task resides in. Furthermore, two ways are available for
    specifying the kind, either directly as argument provided to
    :meth:`aspecd.tasks.TaskFactory.get_task` or as key in a dict used as
    an argument for :meth:`aspecd.tasks.TaskFactory.get_task_from_dict`.

    The classes for the different tasks follow a simple convention:
    "<Module>Task" with "<Module>" being the capitalised module name the
    actual class necessary for performing the task resides in. Therefore,
    for each new module tasks should be available for, you will need to
    create an appropriate task class deriving from :class:`aspecd.tasks.Task`.

    Raises
    ------
    MissingTaskDescriptionError
        Raised if no description is given necessary to create task.
    KeyError
        Raised if dict with task description does not contain "kind" key.

    """

    def get_task(self, kind=None):
        """
        Return task object specified by its kind.

        Parameters
        ----------
        kind : :class:`str`
            Kind of task to create

            Reflects the name of the module the actual object required for
            performing the task resides in.

        Returns
        -------
        task : :class:`aspecd.tasks.Task`
            Task object

            The actual subclass depends on the kind.

        Raises
        ------
        MissingTaskDescriptionError
            Raised if no description is given necessary to create task.

        """
        if not kind:
            raise MissingTaskDescriptionError
        task = self._create_task_object(kind=kind)
        return task

    def get_task_from_dict(self, dict_=None):
        """
        Return task object specified by the "kind" key in the dict.

        Parameters
        ----------
        dict_ : :class:`dict`
            Dictionary containing "kind" key

            The "kind" key reflects the name of the module the actual object
            required for performing the task resides in.

        Returns
        -------
        task : :class:`aspecd.tasks.Task`
            Task object

            The actual subclass depends on the kind.

        Raises
        ------
        MissingTaskDescriptionError
            Raised if no description is given necessary to create task.
        KeyError
            Raised if dict does not contain "kind" key.

        """
        if not dict_:
            raise MissingTaskDescriptionError
        if 'kind' not in dict_:
            raise KeyError
        task = self._create_task_object(kind=dict_['kind'])
        return task

    def _create_task_object(self, kind=None):
        """
        Create and return actual task object based on the kind provided.

        The classes for the different tasks follow a simple convention:
        "<Module>Task" with "<Module>" being the capitalised module name
        the actual class necessary for performing the task resides in.

        Parameters
        ----------
        kind : :class:`str`
            Kind of task to create

            Reflects the name of the module the actual object required for
            performing the task resides in.

        Returns
        -------
        task : :class:`aspecd.tasks.Task`
            Task object

            The actual subclass depends on the kind.

        .. todo::
            Check whether there are some ways to circumvent "package_name"
            to automatically be prefixed, as this would allow to use
            classes from different packages (if that is sensible to do).

        """
        class_name = ''.join([kind.capitalize(), 'Task'])
        package_name = aspecd.utils.package_name(self)
        full_class_name = '.'.join([package_name, 'tasks', class_name])
        task = aspecd.utils.object_from_class_name(full_class_name)
        return task
