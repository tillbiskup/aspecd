"""
Constituents of a recipe-driven data analysis.

One main aspect of tasks is to provide the constituents of a
:ref:`recipe-driven data analysis <recipes>`, i.e.
:class:`aspecd.tasks.Recipe` and :class:`aspecd.tasks.Chef`. In its
simplest form, a recipe gets cooked by a chef, resulting in a series of
tasks being performed on a list of datasets.

From a user's perspective, a recipe is usually stored in a `YAML
<https://yaml.org/>`_ file. This allows to easily create and modify recipes
without knowing too much about the underlying processes. For an accessible
overview of the YAML syntax, see the `introduction provided by ansible
<https://docs.ansible.com/ansible/reference_appendices/YAMLSyntax.html>`_ .


Recipe-driven data analysis by example
======================================

Recipes always consist of two major parts: A list of datasets to operate
on, and a list of tasks to be performed on the datasets. Of course, you can
specify for each task on which datasets it should be performed, and if
possible, whether it should be performed on each dataset separately or
combined. The latter is particularly interesting for representations (e.g.,
plots) consisting of multiple datasets, or analysis steps spanning multiple
datasets.

To give a first impression of how such a recipe may look like::

    datasets:
      - loi:xxx
      - loi:yyy

    tasks:
      -
        kind: processing
        type: ProcessingStep
        properties:
          parameters:
            param1: bar
            param2: foo
          prop2: blub
      -
        kind: analysis
        type: SingleAnalysisStep
        properties:
          parameters:
            param1: bar
            param2: foo
          prop2: blub
        apply_to:
          - loi:xxx
        result: new_dataset

Here, ``tasks`` is a list of dictionary-style entries. The key ``kind``
determines which kind of task should be performed. For each kind, a class
subclassing :class:`aspecd.tasks.Task` needs to exist. For details,
see below. The key ``type`` stores the name of the actual class, such as a
concrete processing step derived from
:class:`aspecd.processing.ProcessingStep`. The dictionary ``properties``
contains keys corresponding to the attributes of the respective class.
Depending on the type of task, additional keys can be used, such as
``apply_to`` to determine the datasets this task should be applied to,
or ``result`` providing a label for a dataset created newly by an analysis
task.


.. note::
    The use of ``loi:`` markers in the example above points to a situation
    in which every dataset can be accessed by a unique identifier. For
    details, see the `LabInform documentation <https://www.labinform.de/>`_.


Types of tasks
==============

Each task is internally represented by an :obj:`aspecd.tasks.Task` object,
more precisely an object instantiated from a subclass of
:class:`aspecd.tasks.Task`. This polymorphism of task classes makes it
possible to easily extend the scope of recipe-driven data analysis.
Currently, the following subclasses are implemented:

  * :class:`aspecd.tasks.ProcessingTask`
  * :class:`aspecd.tasks.AnalysisTask`

     * :class:`aspecd.tasks.SingleanalysisTask`
     * :class:`aspecd.tasks.MultianalysisTask`

  * :class:`aspecd.tasks.AnnotationTask`
  * :class:`aspecd.tasks.PlotTask`

     * :class:`aspecd.tasks.SingleplotTask`
     * :class:`aspecd.tasks.MultiplotTask`

  * :class:`aspecd.tasks.ReportTask`

For each task, you can set all attributes of the underlying class using the
``properties`` dictionary in the recipe. Therefore, to know which
parameters can be set for what type of task means simply to check the
documentation for the respective classes. I.e., for a task represented by
an :obj:`aspecd.tasks.ProcessingTask` object, check out the appropriate
class from the :mod:`aspecd.processing` module. The same is true for
packages derived from ASpecD.

Furthermore, depending on the type of task, you may be able to set
additional parameters controlling in more detail how the particular task is
performed. For details, see the documentation of the respective task subclass.

.. todo::
    There is a number of things that are not yet implemented, but required
    for a working recipe-driven data analysis that follows good practice
    for reproducible research. This includes (but may not be limited to):

      * Store history of each task (in a way the result can be used as a
        recipe again).
      * Parser for recipes performing a static analysis of their syntax.
        Useful particulary for larger datasets and/or longer lists of tasks.


Prerequisites for recipe-driven data analysis
=============================================

To be able to use recipe-driven data analysis in packages derived from the
ASpecD framework, a series of prerequisites needs to be met, *i.e.*, classes
implemented. Besides the usual suspects such as
:class:`aspecd.dataset.Dataset` and its constituents as well as the
different processing and analysis steps based on
:class:`aspecd.processing.ProcessingStep` and
:class:`aspecd.analysis.SingleAnalysisStep`, two different factory
classes need to be implemented in particular, subclassing

  * :class:`aspecd.dataset.DatasetFactory` and
  * :class:`aspecd.io.DatasetImporterFactory`,

respectively. Actually, only :class:`aspecd.dataset.DatasetFactory` is
directly used by :class:`aspecd.tasks.Recipe`, however, internally it relies
on the existence of :class:`aspecd.io.DatasetImporterFactory` to return a
dataset based solely on a (unique) ID.

Besides implementing these classes, the facilities provided by the
:mod:`aspecd.tasks` module should be fully sufficient for regular
recipe-driven data analysis. In particular, normally there should be no need
to subclass any of the classes within this module in a package derived from
the ASpecD framework. One particular design goal of recipe-driven data
analysis is to decouple the actual tasks being performed from the
general handling of recipes. The former is implemented within each
respective package built upon the ASpecD framework, the latter is taken care
of fully by the ASpecD framework itself. You might want to implement a simple
proxy within a derived package to prevent the user from having to call out to
functionality provided directly by the ASpecD framework (what might be
confusing for those unfamiliar with the underlying details, *i.e.*,
most common users).

"""

import collections

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
    """Exception raised when expecting a dict but none is provided

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


class MissingDatasetFactoryError(Error):
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


class MissingPlotterError(Error):
    """Exception raised when no Plotter instance is provided

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
    datasets. To actually carry out all tasks in a recipe, it is handed
    over to a :obj:`aspecd.tasks.Chef` object for cooking using the
    respective :meth:`aspecd.tasks.Chef.cook` method.

    From a user's perspective, recipes reside usually in YAML files from
    where they are imported into an :obj:`aspecd.tasks.Recipe` object using
    its respective :meth:`import_into` method and an object of class
    :class:`aspecd.io.RecipeYamlImporter`. Similarly, a given recipe can be
    exported back to a YAML file using the :meth:`export_to` method and an
    object of class :class:`aspecd.io.RecipeYamlExporter`.

    In contrast to the persistent form of a recipe (e.g., as file on the
    file system), the object contains actual datasets and tasks that are
    objects of the respective classes. Therefore, the attributes of a
    recipe are normally set by the respective methods from either a file or
    a dictionary (that in turn will normally be created from contents of a
    file).

    Retrieving datasets is delegated to an
    :class:`aspecd.dataset.DatasetFactory` instance stored in
    :attr:`dataset_factory`. This provides a maximum of flexibility but
    makes it necessary to specify (and first implement) such factory in
    packages derived from the ASpecD framework.

    .. todo::
        Can recipes have LOIs themselves and therefore be retrieved from
        the extended data safe? Might be a sensible option, although
        generic (and at the same time unique) LOIs for recipes are much
        harder to create than LOIs for datasets and alike.

        Generally, the concept of a LOI is nothing a recipe needs to know
        about. But it does know about an ID of any kind. Whether this ID
        is a (local) path or a LOI doesn't matter. Somewhere in the ASpecD
        framework there may exist a resolver (factory) for handling IDs of
        any kind and eventually retrieving the respective information.


    Attributes
    ----------
    datasets : :class:`collections.OrderedDict`
        Ordered dictionary of datasets the tasks should be performed for

        Each dataset is an object of class :class:`aspecd.dataset.Dataset`.

        The keys are the dataset ids.
    tasks : :class:`list`
        List of tasks to be performed on the datasets

        Each task is an object of class :class:`aspecd.tasks.Task`.
    results : :class:`collections.OrderedDict`
        Ordered dictionary of results originating from analysis tasks

        Results can be of any type, but are mostly either instances of
        :class:`aspecd.dataset.Dataset` or
        :class:`aspecd.metadata.PhysicalQuantity`.

        The keys are those defined by
        :attr:`aspecd.tasks.SingleanalysisTask.result` and
        :attr:`aspecd.tasks.MultianalysisTask.result`, respectively.
    figures : :class:`collections.OrderedDict`
        Ordered dictionary of figures originating from plotting tasks

        Each entry is an object of class :class:`aspecd.tasks.FigureRecord`.
    dataset_factory : :class:`aspecd.dataset.DatasetFactory`
        Factory for datasets used to retrieve datasets

        If no factory is set, but a recipe imported from a file or set from
        a dictionary, an exception will be raised.
    task_factory : :class:`aspecd.tasks.TaskFactory`
        Factory for tasks

        Defaults to an object of class :class:`aspecd.tasks.TaskFactory`.

        If no factory is set, but a recipe imported from a file or set from
        a dictionary, an exception will be raised.

    Raises
    ------
    aspecd.tasks.MissingDictError
        Raised if no dict is provided.
    aspecd.tasks.MissingImporterError
        Raised if no importer is provided.
    aspecd.tasks.MissingExporterError
        Raised if no exporter is provided.
    aspecd.tasks.MissingDatasetFactoryError
        Raised if :attr:`dataset_factory` is invalid.
    aspecd.tasks.MissingTaskFactoryError
        Raised if :attr:`task_factory` is invalid.

    """

    def __init__(self):
        super().__init__()
        self.datasets = collections.OrderedDict()
        self.results = collections.OrderedDict()
        self.figures = collections.OrderedDict()
        self.tasks = list()
        self.dataset_factory = None
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
        aspecd.tasks.MissingDictError
            Raised if no dict is provided.
        aspecd.tasks.MissingDatasetFactoryError
            Raised if :attr:`importer_factory` is invalid.
        aspecd.tasks.MissingTaskFactoryError
            Raised if :attr:`task_factory` is invalid.

        """
        if not dict_:
            raise MissingDictError
        if not self.dataset_factory:
            raise MissingDatasetFactoryError
        if not self.task_factory:
            raise MissingTaskFactoryError
        if 'datasets' in dict_:
            for key in dict_['datasets']:
                self._append_dataset(key)
        if 'tasks' in dict_:
            for key in dict_['tasks']:
                self._append_task(key)

    def _append_dataset(self, key):
        dataset = self.dataset_factory.get_dataset(source=key)
        self.datasets[key] = dataset

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
            dict_['datasets'].append(self.datasets[dataset].id)
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
        aspecd.tasks.MissingImporterError
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
        aspecd.tasks.MissingExporterError
            Raised if no exporter is provided

        """
        if not exporter:
            raise MissingExporterError('An exporter instance is needed to '
                                       'export a recipe.')
        exporter.export_from(self)

    def get_dataset(self, identifier=''):
        """
        Return dataset corresponding to given identifier.

        In case of having a list of identifiers, use the similar method
        :meth:`aspecd.tasks.Recipe.get_datasets`.

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
        aspecd.tasks.MissingDatasetIdentifierError
            Raised if no identifier is provided.

        """
        if not identifier:
            raise MissingDatasetIdentifierError
        matching_dataset = None
        if identifier in self.datasets:
            matching_dataset = self.datasets[identifier]
        if identifier in self.results:
            if isinstance(self.results[identifier], aspecd.dataset.Dataset):
                matching_dataset = self.results[identifier]
        return matching_dataset

    def get_datasets(self, identifiers=None):
        """
        Return datasets corresponding to given list of identifiers.

        In case of having a single identifier, use the similar method
        :meth:`aspecd.tasks.Recipe.get_dataset`.

        Parameters
        ----------
        identifiers : :class:`list`
            Identifiers matching the :attr:`aspecd.dataset.Dataset.id`
            attribute.

        Returns
        -------
        datasets : :class:`list`
            Datasets corresponding to given identifier

            Each dataset is an instance of :class:`aspecd.dataset.Dataset`.

            If no datasets corresponding to the given identifiers could be
            found, an empty list is returned.

        Raises
        ------
        aspecd.tasks.MissingDatasetIdentifierError
            Raised if no identifiers are provided.

        """
        if not identifiers:
            raise MissingDatasetIdentifierError
        matching_datasets = [self.datasets[key] for key in identifiers if
                             key in self.datasets]
        for identifier in identifiers:
            if identifier in self.results:
                if isinstance(self.results[identifier],
                              aspecd.dataset.Dataset):
                    matching_datasets.append(self.results[identifier])
                    identifiers.remove(identifier)
                    break
        return matching_datasets


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
    aspecd.tasks.MissingRecipeError
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
        aspecd.tasks.MissingRecipeError
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
    For a number of basic tasks available in the ASpecD package, this has
    already been done. See:

        * :class:`aspecd.tasks.ProcessingTask`
        * :class:`aspecd.tasks.AnalysisTask`

           * :class:`aspecd.tasks.SingleanalysisTask`
           * :class:`aspecd.tasks.MultianalysisTask`

        * :class:`aspecd.tasks.AnnotationTask`
        * :class:`aspecd.tasks.PlotTask`

           * :class:`aspecd.tasks.SingleplotTask`
           * :class:`aspecd.tasks.MultiplotTask`

        * :class:`aspecd.tasks.ReportTask`

    Note that imports of datasets are usually not handled using tasks,
    as this is taken care of automatically by defining a list of datasets
    in a :class:`aspecd.tasks.Recipe`.

    Usually, you need not care to instantiate objects of the correct type,
    as this is done automatically by the :class:`aspecd.tasks.Recipe` using
    the :class:`aspecd.tasks.TaskFactory`.


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
    properties : :class:`dict`
        Properties necessary to perform the task.

        Should have keys corresponding to the properties of the class given
        as :attr:`type` attribute.

        Generally, all keys in :attr:`aspecd.tasks.Task.properties` will be
        mapped to the underlying object created to perform the actual task.

        In contrast, all additional attributes of a given task object
        subclassing :class:`aspecd.tasks.Task` that are specific to the task
        object as such and its operation, but not for the object created by
        the task object to perform the task, are not part of the
        :attr:`aspecd.tasks.Task.properties` dict. For a recipe, this means
        that these additional attributes are at the same level as
        :attr:`aspecd.tasks.Task.properties`.
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
    aspecd.tasks.MissingDictError
        Raised if no dict is provided when calling :meth:`from_dict`.
    aspecd.tasks.MissingRecipeError
        Raised if no recipe is available upon performing the task.

    """

    def __init__(self, recipe=None):
        super().__init__()
        self.kind = ''
        self.type = ''
        self.properties = dict()
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
        aspecd.tasks.MissingDictError
            Raised if no dict is provided.

        """
        if not dict_:
            raise MissingDictError
        for key in dict_:
            if hasattr(self, key):
                if isinstance(getattr(self, key), list):
                    if isinstance(dict_[key], list):
                        for element in dict_[key]:
                            getattr(self, key).append(element)
                    else:
                        getattr(self, key).append(dict_[key])
                else:
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
        aspecd.tasks.MissingRecipeError
            Raised if no recipe is available.

        """
        if not self.recipe:
            raise MissingRecipeError
        if not self.apply_to:
            for dataset in self.recipe.datasets:
                self.apply_to.append(self.recipe.datasets[dataset].id)
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
        Set attributes in object from the keys of the :attr:`properties` dict.

        Only those keys that have a matching attribute in the object are
        actually mapped, all others silently ignored.

        Properties or values of dicts in properties that correspond to keys
        in :attr:`aspecd.recipe.results` of the recipe stored in
        :attr:`aspecd.task.recipe` will be replaced accordingly. The same is
        true for properties corresponding to keys in
        :attr:`aspecd.recipe.datasets` of the recipe stored in
        :attr:`aspecd.task.recipe`. Thus, dataset references can be used in
        properties and get replaced by the actual datasets. Similarly,
        figures stored in :attr:`aspecd.recipe.figures` can be referenced
        and will be replaced by the actual :obj:`aspecd.tasks.FigureRecord`
        objects.

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
        properties = self._parse_properties()
        for key in properties:
            if hasattr(obj, key):
                attr = getattr(obj, key)
                if isinstance(attr, dict) and attr:
                    prop = aspecd.utils.copy_keys_between_dicts(
                        source=properties[key], target=attr)
                    setattr(obj, key, prop)
                else:
                    setattr(obj, key, properties[key])

    def _parse_properties(self):
        """
        Replace labels for datasets, results, and figures in properties

        Returns
        -------
        properties : :class:`dict`
            properties with labels replaced by actual object references

        """
        if self.recipe:
            properties = aspecd.utils.replace_value_in_dict(
                self.recipe.datasets, self.properties)
            if self.recipe.results:
                properties = aspecd.utils.replace_value_in_dict(
                    self.recipe.results, self.properties)
            if self.recipe.figures:
                properties = aspecd.utils.replace_value_in_dict(
                    self.recipe.figures, self.properties)
        else:
            properties = self.properties
        return properties


class ProcessingTask(Task):
    """
    Processing step defined as task in recipe-driven data analysis.

    Processing steps will always be performed individually for each dataset.

    For more information on the underlying general class,
    see :class:`aspecd.processing.ProcessingStep`.

    For an example of how such a processing task may be included into a
    recipe, see the YAML listing below::

        kind: processing
        type: ProcessingStep
        properties:
          parameters:
            param1: bar
            param2: foo
          comment: >
            Some free text describing in more details the processing step
        apply_to:
          - loi:xxx

    Note that you can refer to datasets and results created during cooking
    of a recipe using their respective labels. Those labels will
    automatically be replaced by the actual dataset/result prior to
    performing the task.

    """

    def _perform(self):
        for dataset_id in self.apply_to:
            dataset = self.recipe.get_dataset(dataset_id)
            task = self.get_object()
            dataset.process(processing_step=task)


class AnalysisTask(Task):
    """
    Analysis step defined as task in recipe-driven data analysis.

    Analysis steps can be performed individually for each dataset or the
    results combined, depending on the type of analysis step.

    An AnalysisTask should not be used directly but rather the two
    classes derived from this class, namely:

      * :class:`aspecd.tasks.SingleanalysisTask` and
      * :class:`aspecd.tasks.MultianalysisTask`.

    For more information on the underlying general class,
    see :class:`aspecd.analysis.AnalysisStep`.


    Attributes
    ----------
    result : :class:`str`
        Label for the dataset resulting from an analysis step.

        This label will be used to refer to the dataset later on when
        further processing the recipe.

    """

    def __init__(self, recipe=None):
        super().__init__(recipe=recipe)
        self.result = ''
        self._module = 'analysis'


class SingleanalysisTask(AnalysisTask):
    """
    Analysis step defined as task in recipe-driven data analysis.

    Singleanalysis steps can only be performed individually for each dataset.
    For analyses combining multiple datasets,
    see :class:`aspecd.tasks.MultianalyisTask`.

    For more information on the underlying general class,
    see :class:`aspecd.analysis.SingleAnalysisStep`.

    For an example of how such an analysis task may be included into a
    recipe, see the YAML listing below::

        kind: singleanalysis
        type: SingleAnalysisStep
        properties:
          parameters:
            param1: bar
            param2: foo
          comment: >
            Some free text describing in more details the analysis step
        apply_to:
          - loi:xxx
        result: label

    Note that you can refer to datasets and results created during cooking
    of a recipe using their respective labels. Those labels will
    automatically be replaced by the actual dataset/result prior to
    performing the task.

    """

    # noinspection PyUnresolvedReferences
    def _perform(self):
        for dataset_id in self.apply_to:
            dataset = self.recipe.get_dataset(dataset_id)
            task = self.get_object()
            task = dataset.analyse(analysis_step=task)
            if self.result:
                if isinstance(task.result, aspecd.dataset.Dataset):
                    task.result.id = self.result
                self.recipe.results[self.result] = task.result


class MultianalysisTask(AnalysisTask):
    """
    Analysis step defined as task in recipe-driven data analysis.

    Multianalysis steps are performed on a list of datasets and combine
    them in one single analysis. For analyses performed on individual
    datasets, see :class:`aspecd.tasks.SingleanalysisTask`.

    For more information on the underlying general class,
    see :class:`aspecd.analysis.MultiAnalysisStep`.

    For an example of how such an analysis task may be included into a
    recipe, see the YAML listing below::

        kind: multianalysis
        type: MultiAnalysisStep
        properties:
          parameters:
            param1: bar
            param2: foo
          comment: >
            Some free text describing in more details the analysis step
        apply_to:
          - loi:xxx
        result:
          - label1
          - label2

    Note that you can refer to datasets and results created during cooking
    of a recipe using their respective labels. Those labels will
    automatically be replaced by the actual dataset/result prior to
    performing the task.

    In case such a multianalysis step results in a list of resulting
    datasets, result should be a list of labels, not a single label.

    Raises
    ------
    IndexError
        Raised if list of result labels and results are not of same length

    """

    # noinspection PyUnresolvedReferences
    def _perform(self):
        task = self.get_object()
        task.datasets = self.recipe.get_datasets(self.apply_to)
        task.analyse()
        if self.result:
            # NOTE: This code is currently widely untested due to lack of
            # ideas of how to test it properly.
            if isinstance(self.result, list):
                if len(self.result) != len(task.result):
                    raise IndexError('List of result labels and results '
                                     ' must be of same length')
                for index, label in enumerate(self.result):
                    self._assign_result(label=label, result=task.result[index])
            else:
                self._assign_result(label=self.result, result=task.result)

    def _assign_result(self, label='', result=None):
        if isinstance(result, aspecd.dataset.Dataset):
            result.id = label
        self.recipe.results[label] = result


class AnnotationTask(Task):
    """
    Annotation step defined as task in recipe-driven data analysis.

    Annotation steps will always be performed individually for each dataset.

    For more information on the underlying general class,
    see :class:`aspecd.processing.Annotation`.

    """

    def _perform(self):
        for dataset_id in self.apply_to:
            dataset = self.recipe.get_dataset(dataset_id)
            task = self.get_object()
            dataset.annotate(annotation_=task)


class PlotTask(Task):
    """
    Plot step defined as task in recipe-driven data analysis.

    A PlotTask should not be used directly but rather the two classes
    derived from this class, namely:

      * :class:`aspecd.tasks.SingleplotTask` and
      * :class:`aspecd.tasks.MultiplotTask`.

    For more information on the underlying general class,
    see :class:`aspecd.plotting.Plotter`.


    Attributes
    ----------
    label : :class:`str`
        Label for the fighure resulting from a plotting step.

        This label will be used to refer to the plot later on when
        further processing the recipe. Actually, in the recipe's
        :attr:`aspecd.tasks.Recipe.figures` dict, this label is used as a
        key and a :obj:`aspecd.tasks.FigureRecord` object stored containing
        all information necessary for further handling the results of the plot.

    """

    def __init__(self):
        super().__init__()
        self.label = ''
        self._module = 'plotting'

    def perform(self):
        """
        Call the appropriate method of the underlying object.

        For details, see the method :meth:`aspecd.tasks.Task.perform` of the
        base class.

        Additionally to what is done in the base class, a PlotTask adds a
        :obj:`aspecd.tasks.FigureRecord` object to the
        :attr:`aspecd.tasks.Recipe.figures` property of the underlying
        recipe in case an :attr:`aspecd.tasks.PlotTask.label` has been set.

        """
        super().perform()
        if self.label:
            self._add_figure_to_recipe()

    def _add_figure_to_recipe(self):
        figure_record = FigureRecord()
        # noinspection PyTypeChecker
        figure_record.from_plotter(self.get_object())
        self.recipe.figures[self.label] = figure_record

    def save_plot(self, plot=None):
        """
        Save the figure of the plot created by the task.

        Parameters
        ----------
        plot : :class:`aspecd.plotting.Plotter`
            Plot whose figure should be saved

        """
        if 'filename' in self.properties and self.properties['filename']:
            saver = aspecd.plotting.Saver(filename=self.properties['filename'])
            plot.save(saver)


class SingleplotTask(PlotTask):
    """
    Singleplot step defined as task in recipe-driven data analysis.

    Singleplot steps can only be performed individually for each dataset.
    For plots combining multiple datasets,
    see :class:`aspecd.tasks.MultiplotTask`.

    For more information on the underlying general class,
    see :class:`aspecd.plotting.SinglePlotter`.

    For an example of how such a analysis task may be included into a
    recipe, see the YAML listing below::

        kind: singleplot
        type: SinglePlotter
        properties:
          parameters:
            param1: bar
            param2: foo
          caption:
            title: >
              Ideally a single sentence summarising the intend of the figure
            text: >
              More text for the figure caption
            parameters:
              - a list of parameters
              - that shall (additionally) be listed
              - in the figure caption
          filename: fancyfigure.pdf
        apply_to:
          - loi:xxx
        label: label

    Note that you can refer to datasets and results created during cooking
    of a recipe using their respective labels. Those labels will
    automatically be replaced by the actual dataset/result prior to
    performing the task.

    .. note::
        As soon as you provide a filename in the properties of your recipe,
        the resulting plot will automatically be saved to that filename,
        inferring the file format from the extension of the filename. For
        details of how the format is inferred see the documentation for the
        :meth:`matplotlib.figure.Figure.savefig` method.

    """

    def _perform(self):
        for dataset_id in self.apply_to:
            dataset = self.recipe.get_dataset(dataset_id)
            task = self.get_object()
            dataset.plot(plotter=task)
            # noinspection PyTypeChecker
            self.save_plot(plot=task)


class MultiplotTask(PlotTask):
    """
    Multiplot step defined as task in recipe-driven data analysis.

    Multiplot steps are performed on a list of datasets and combine them in
    one single plot. For plots performed on individual datasets,
    see :class:`aspecd.tasks.SingleplotTask`.

    For more information on the underlying general class,
    see :class:`aspecd.plotting.MultiPlotter`.

    For an example of how such a analysis task may be included into a
    recipe, see the YAML listing below::

        kind: multiplot
        type: MultiPlotter
        properties:
          parameters:
            param1: bar
            param2: foo
          caption:
            title: >
              Ideally a single sentence summarising the intend of the figure
            text: >
              More text for the figure caption
            parameters:
              - a list of parameters
              - that shall (additionally) be listed
              - in the figure caption
          filename: fancyfigure.pdf
        apply_to:
          - loi:xxx
          - loi:yyy
        label: label

    Note that you can refer to datasets and results created during cooking
    of a recipe using their respective labels. Those labels will
    automatically be replaced by the actual dataset/result prior to
    performing the task.

    .. note::
        As soon as you provide a filename in the properties of your recipe,
        the resulting plot will automatically be saved to that filename,
        inferring the file format from the extension of the filename. For
        details of how the format is inferred see the documentation for the
        :meth:`matplotlib.figure.Figure.savefig` method.

    """

    def _perform(self):
        task = self.get_object()
        task.datasets = self.recipe.get_datasets(self.apply_to)
        # noinspection PyUnresolvedReferences
        task.plot()
        # noinspection PyTypeChecker
        self.save_plot(plot=task)


class ReportTask(Task):
    """
    Reporting step defined as task in recipe-driven data analysis.

    For more information on the underlying general class,
    see :class:`aspecd.report.Reporter`.

    For an example of how such an analysis task may be included into a
    recipe, see the YAML listing below::

        kind: report
        type: LaTeXReporter
        properties:
          template: my-fancy-latex-template.tex
          filename: some-filename-for-final-report.tex
          context:
            general:
              title: Some fancy title
              author: John Doe
            free_text:
              intro: >
                Short introduction of the experiment performed
              metadata: >
                Tabular and customisable overview of the dataset's metadata
              history: >
                Presentation of all processing, analysis and representation
                steps
            figures:
              title: my_fancy_figure
        compile: True
        apply_to:
          - loi:xxx

    Note that you can refer to datasets, results, and figures created during
    cooking of a recipe using their respective labels. Those labels will
    automatically be replaced by the actual dataset/result prior to
    performing the task.

    Whatever fields you set as property ``context`` can be accessed
    directly from within the template using the usual Python syntax for
    accessing keys of dictionaries. The fields shown here assume
    a certain structure of your template containing user-supplied free text
    for the introduction to several sections.

    Additionally, the task will provide the key ``dataset`` containing the
    result of the :meth:`aspecd.dataset.Dataset.to_dict` method, thus the full
    information contained in the dataset.


    Attributes
    ----------
    compile : :class:`bool`
        Option for compiling a template.

        Some types of templates need an additional "compile" step to create
        output, most prominently LaTeX templates. If the Reporter class does
        not support compiling, but :attr:`compile` is set to True, it gets
        silently ignored.

    """

    def __init__(self):
        super().__init__()
        self.compile = False

    # noinspection PyUnresolvedReferences
    def _perform(self):
        self._add_figure_filenames_to_includes()
        for dataset_id in self.apply_to:
            dataset = self.recipe.get_dataset(dataset_id)
            task = self.get_object()
            task.context['dataset'] = dataset.to_dict()
            task.create()
            if self.compile and hasattr(task, 'compile'):
                task.compile()

    def _add_figure_filenames_to_includes(self):
        if 'includes' in self.properties:
            self.properties['includes'].append(
                self._get_filenames_of_figures())
        else:
            self.properties['includes'] = self._get_filenames_of_figures()

    def _get_filenames_of_figures(self):
        filenames = []
        for figure in self.recipe.figures:
            filenames.append(self.recipe.figures[figure].filename)
        return filenames


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
    aspecd.tasks.MissingTaskDescriptionError
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
        aspecd.tasks.MissingTaskDescriptionError
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
        aspecd.tasks.MissingTaskDescriptionError
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


class FigureRecord(aspecd.utils.ToDictMixin):
    """
    Information about a figure created by a PlotTask.

    Figures created during recipe-driven data analysis may need to be added,
    e.g., to a report. Therefore, the information contained in the PlotTask
    needs to be accessible by the recipe and other tasks in turn.

    Attributes
    ----------
    caption : :class:`dict`
        User-supplied information for the figure caption.

        Has three fields: "title", "text", and "parameters".

        "title" is usually one sentence describing the intent of the figure
        and often plotted bold-face in a figure caption.

        "text" is additional text directly following the title,
        containing more information about the plot.

        "parameters" is a list of parameter names that should be included in
        the figure caption, usually at the very end.
    parameters : :class:`dict`
        All parameters necessary for the plot, implicit and explicit
    label : :class:`str`
        Label the figure should be referred to from within the recipe

        Similar to the :attr:`aspecd.tasks.SingleanalysisTask.result`
        attribute of the :class:`aspecd.tasks.SingleanalysisTask` class.
    filename : :class:`str`
        Name of file to save the plot to

    Raises
    ------
    aspecd.tasks.MissingPlotterError
        Raised if no plotter is provided

    """

    def __init__(self):
        super().__init__()
        self.caption = {
            'title': '',
            'text': '',
            'parameters': []
        }
        self.parameters = dict()
        self.label = ''
        self.filename = ''

    def from_plotter(self, plotter=None):
        """
        Set attributes from plotter

        Usually, a plotter contains all information necessary for an
        :obj:`aspecd.tasks.FigureRecord` object.

        Parameters
        ----------
        plotter : :class:`aspecd.plotting.Plotter`
            Plotter the figure record should be created for.

        Raises
        ------
        aspecd.tasks.MissingPlotterError
            Raised if no plotter is provided

        """
        if not plotter:
            raise MissingPlotterError
        for attribute in ['caption', 'parameters', 'filename']:
            setattr(self, attribute, getattr(plotter, attribute))
