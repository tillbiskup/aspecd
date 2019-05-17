"""Datasets: units containing data and metadata.

The dataset is one key concept of the ASpecD framework, consisting of the
data as well as the corresponding metadata. Storing metadata in a
structured way is a prerequisite for a semantic understanding within the
routines. Furthermore, a history of every processing, analysis and
annotation step is recorded as well, aiming at a maximum of
reproducibility. This is part of how the ASpecD framework tries to support
good scientific practice.

Therefore, each processing and analysis step of data should always be
performed using the respective methods of a dataset, at least as long as it
can be performed on a single dataset.

Generally, there are two types of datasets: Those containing experimental
data and those containing calculated data. Therefore, two corresponding
subclasses exist, and packages building upon the ASpecD framework should
inherit from either of them:

  * :class:`aspecd.dataset.ExperimentalDataset`
  * :class:`aspecd.dataset.CalculatedDataset`

Additional classes used within the dataset that are normally not necessary
to implement directly on your own in packages building upon the ASpecD
framework, are:

  * :class:`aspecd.dataset.Data`

    Unit containing both, numeric data and corresponding axes.

    The data class ensures consistency in terms of dimensions between
    numerical data and axes.

  * :class:`aspecd.dataset.Axis`

    Axis for data in a dataset.

    An axis contains always both, numerical values as well as the metadata
    necessary to create axis labels and to make sense of the numerical
    information.

  * :class:`aspecd.dataset.DatasetReference`

    Reference to a dataset.

    Often, one dataset needs to reference other datasets. A typical example
    would be a simulation stored in a dataset of class
    :class:`aspecd.dataset.CalculatedDataset` that needs to reference the
    corresponding experimental data, stored in a dataset of class
    :class:`aspecd.dataset.ExperimentalDataset`. Vice versa,
    the experimental dataset might want to store a reference to one (or
    more) simulations.


In addition, to handle the history contained within a dataset, there is a
series of classes for storing history records:

  * :class:`aspecd.dataset.HistoryRecord`

    Generic base class for all kinds of history records.

    For all classes operating on datasets, such as
    :class:`aspecd.processing.ProcessingStep`,
    :class:`aspecd.analysis.SingleAnalysisStep` and others, there exist at least two
    "representations": (i) the generic one not (necessarily) tied to any
    concrete dataset, thus portable, and (ii) a concrete one having operated on
    a dataset and thus being accompanied with information about who has done
    what when how to what dataset.

    For this second type, a history class derived from
    :class:`aspecd.dataset.HistoryRecord` gets used, and it is this second type
    that is stored inside the Dataset object.

  * :class:`aspecd.dataset.ProcessingHistoryRecord`

    History record for processing steps on datasets.

  * :class:`aspecd.dataset.AnalysisHistoryRecord`

    History record for analysis steps on datasets.

  * :class:`aspecd.dataset.AnnotationHistoryRecord`

    History record for annotations of datasets.

  * :class:`aspecd.dataset.PlotHistoryRecord`

    History record for plots of datasets.

"""

import copy
from datetime import datetime

import numpy as np

import aspecd.metadata
import aspecd.system
import aspecd.utils


class Error(Exception):
    """Base class for exceptions in this module."""

    pass


class MissingProcessingStepError(Error):
    """Exception raised trying to process without processing_step

    Attributes
    ----------
    message : :class:`str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class UndoWithEmptyHistoryError(Error):
    """Exception raised trying to undo with empty history

    Attributes
    ----------
    message : :class:`str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class UndoAtBeginningOfHistoryError(Error):
    """Exception raised trying to undo with history pointer at zero

    Attributes
    ----------
    message : :class:`str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class UndoStepUndoableError(Error):
    """Exception raised trying to undo an undoable step of history

    Attributes
    ----------
    message : :class:`str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class RedoAlreadyAtLatestChangeError(Error):
    """Exception raised trying to redo with empty history

    Attributes
    ----------
    message : :class:`str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class ProcessingWithLeadingHistoryError(Error):
    """Exception raised trying to process with leading history

    Attributes
    ----------
    message : :class:`str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class MissingPlotterError(Error):
    """Exception raised trying to plot without :class:`aspecd.plotting.Plotter`

    Attributes
    ----------
    message : :class:`str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class MissingImporterError(Error):
    """Exception raised importing without :class:`aspecd.io.DatasetImporter`

    Attributes
    ----------
    message : :class:`str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class MissingExporterError(Error):
    """Exception raised importing without :class:`aspecd.io.DatasetExporter`

    Attributes
    ----------
    message : :class:`str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class MissingDatasetError(Error):
    """Exception raised when trying to create a reference without a dataset.

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


class AxesCountError(Error):
    """Exception raised for wrong number of axes

    Attributes
    ----------
    message : :class:`str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class AxesValuesInconsistentWithDataError(Error):
    """Exception raised for axes values inconsistent with data

    Attributes
    ----------
    message : :class:`str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class AxisValuesDimensionError(Error):
    """Exception raised for wrong dimension of values

    Attributes
    ----------
    message : :class:`str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class AxisValuesTypeError(Error):
    """Exception raised for wrong type of values

    Attributes
    ----------
    message : :class:`str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class Dataset(aspecd.utils.ToDictMixin):
    """Base class for all kinds of datasets.

    The dataset is one of the core elements of the ASpecD framework, basically
    containing both, (numeric) data and corresponding metadata, aka information
    available about the data.

    Generally, there are two types of datasets: Those containing
    experimental data and those containing calculated data. Therefore,
    two corresponding subclasses exist, and packages building upon the
    ASpecD framework should inherit from either of them:

      * :class:`aspecd.dataset.ExperimentalDataset`
      * :class:`aspecd.dataset.CalculatedDataset`

    The public attributes of a dataset can be converted to a dict via
    :meth:`aspecd.utils.ToDictMixin.to_dict()`.

    Attributes
    ----------
    id : :class:`str`
        (unique) identifier of the dataset (i.e., path, LOI, or else)
    data : :obj:`aspecd.dataset.Data`
        numeric data and axes
    metadata : :obj:`aspecd.metadata.DatasetMetadata`
        hierarchical key-value store of metadata
    history : :class:`list`
        processing steps performed on the numeric data

        For a full list of tasks performed on a dataset in *chronological*
        order see the :attr:`aspecd.dataset.Dataset.tasks` attribute.
    analyses : :class:`list`
        analysis steps performed on the dataset

        For a full list of tasks performed on a dataset in *chronological*
        order see the :attr:`aspecd.dataset.Dataset.tasks` attribute.
    annotations : :class:`list`
        annotations of the dataset

        For a full list of tasks performed on a dataset in *chronological*
        order see the :attr:`aspecd.dataset.Dataset.tasks` attribute.
    representations : :class:`list`
        representations of the dataset, e.g., plots

        For a full list of tasks performed on a dataset in *chronological*
        order see the :attr:`aspecd.dataset.Dataset.tasks` attribute.
    references : :class:`list`
        references to other datasets

        Each reference is an object of type
        :class:`aspecd.dataset.DatasetReference`.
    tasks : :class:`list`
        tasks performed on the dataset in *chronological* order

        Each entry in the list is a dict containing information about the
        type of task (*i.e.*, processing, analysis, annotation,
        representation) and a reference to the object containing more
        information about the respective task.

        Tasks come in quite handy in cases where the exact chronological order
        of steps performed on a dataset are of relevance, regardless of
        their particular type, *e.g.*, in context of reports.

    Raises
    ------
    aspecd.dataset.UndoWithEmptyHistoryError
        Raised when trying to undo with empty history
    aspecd.dataset.UndoAtBeginningOfHistoryError
        Raised when trying to undo with history pointer at zero
    aspecd.dataset.UndoStepUndoableError
        Raised when trying to undo an undoable step of history
    aspecd.dataset.RedoAlreadyAtLatestChangeError
        Raised  when trying to redo with empty history
    aspecd.dataset.ProcessingWithLeadingHistoryError
        Raised  when trying to process with leading history

    """

    def __init__(self):
        self.data = Data()
        self._origdata = Data()
        self.metadata = aspecd.metadata.DatasetMetadata()
        self.history = []
        self._history_pointer = -1
        self.analyses = []
        self.annotations = []
        self.representations = []
        self.id = ''  # pylint: disable=invalid-name
        self.references = []
        self.tasks = []
        # Package name is used to store the package version in history records
        self._package_name = aspecd.utils.package_name(self)
        super().__init__()

    @property
    def package_name(self):
        """Return package name.

        The name of the package the dataset is implemented in is a crucial
        detail for writing the history. The value is set automatically and
        is read-only.

        """
        return self._package_name

    def process(self, processing_step=None):
        """Apply processing step to dataset.

        Every processing step is an object of type
        :class:`aspecd.processing.ProcessingStep` and is passed as argument
        to :meth:`process`.

        Calling this function ensures that the history record is added to the
        dataset as well as a few basic checks are performed such as for leading
        history, meaning that the ``_history_pointer`` is not set to the
        current tip of the history of the dataset. In this case, an error is
        raised.

        .. note::
            If processing_step is undoable, all previous plots stored in
            the list of representations will be removed, as these plots
            cannot be reproduced due to a change in :attr:`_origdata`.

        Parameters
        ----------
        processing_step : :obj:`aspecd.processing.ProcessingStep`
            processing step to apply to the dataset

        Returns
        -------
        processing_step : :obj:`aspecd.processing.ProcessingStep`
            processing step applied to the dataset

        Raises
        ------
        aspecd.dataset.ProcessingWithLeadingHistoryError
            Raised when trying to process with leading history

        """
        self._check_processing_prerequisites(processing_step=processing_step)
        # Important: Need a copy, not the reference to the original object
        processing_step = copy.deepcopy(processing_step)
        processing_step.process(self, from_dataset=True)
        history_record = processing_step.create_history_record()
        self._append_processing_history_record(history_record)
        self._append_task(kind='processing', task=history_record)
        self._handle_not_undoable(processing_step=processing_step)
        return processing_step

    def _check_processing_prerequisites(self, processing_step=None):
        if self._has_leading_history():
            raise ProcessingWithLeadingHistoryError
        if not processing_step:
            raise MissingProcessingStepError

    def _handle_not_undoable(self, processing_step=None):
        if not processing_step.undoable:
            self._origdata = copy.deepcopy(self.data)
            self.representations = []

    def undo(self):
        """Revert last processing step.

        Actually, the history pointer is decremented and starting from the
        ``_origdata``, all processing steps are reapplied to the data up to
        this point in history.

        Raises
        ------
        aspecd.dataset.UndoWithEmptyHistoryError
            Raised when trying to undo with empty history
        aspecd.dataset.UndoAtBeginningOfHistoryError
            Raised when trying to undo with history pointer at zero
        aspecd.dataset.UndoStepUndoableError
            Raised when trying to undo an undoable step of history

        """
        self._check_undo_prerequisites()
        self._decrement_history_pointer()
        self._replay_history()

    def _check_undo_prerequisites(self):
        if not self.history:
            raise UndoWithEmptyHistoryError
        if self._history_pointer == -1:
            raise UndoAtBeginningOfHistoryError
        if self.history[self._history_pointer].undoable:
            raise UndoStepUndoableError

    def redo(self):
        """Reapply previously undone processing step.

        Raises
        ------
        aspecd.dataset.RedoAlreadyAtLatestChangeError
            Raised when trying to redo with empty history

        """
        if self._at_tip_of_history():
            raise RedoAlreadyAtLatestChangeError
        processing_step_record = \
            self.history[self._history_pointer + 1].processing
        processing_step = processing_step_record.create_processing_step()
        processing_step.process(self, from_dataset=True)
        self._increment_history_pointer()

    def _at_tip_of_history(self):
        return self._history_pointer == len(self.history) - 1

    def _has_leading_history(self):
        return len(self.history) - 1 > self._history_pointer

    def _append_processing_history_record(self, history_record):
        self.history.append(history_record)
        self._increment_history_pointer()

    def _append_task(self, kind='', task=None):
        task = {
            'kind': kind,
            'task': task,
        }
        self.tasks.append(task)

    def _increment_history_pointer(self):
        self._history_pointer += 1

    def _decrement_history_pointer(self):
        self._history_pointer -= 1

    def _replay_history(self):
        self.data = self._origdata
        for historyentry in self.history[:self._history_pointer]:
            historyentry.replay(self)

    def strip_history(self):
        """Remove leading history, if any.

        If a dataset has a leading history, i.e., its history pointer does not
        point to the last entry of the history, and you want to perform a
        processing step on this very dataset, you need first to strip its
        history, as otherwise, a :class:`ProcessingWithLeadingHistoryError`
        will be raised.

        """
        if not self._has_leading_history():
            return
        del self.history[self._history_pointer + 1:]

    def analyse(self, analysis_step=None):
        """Apply analysis to dataset.

        Every analysis step is an object of type
        :class:`aspecd.analysis.SingleAnalysisStep` and is passed as an argument
        to :meth:`analyse`.

        The information necessary to reproduce an analysis is stored in the
        :attr:`analyses` attribute as object of class
        :class:`aspecd.dataset.AnalysisHistoryRecord`. This record contains as
        well a (deep) copy of the complete history of the dataset stored in
        :attr:`history`.

        Parameters
        ----------
        analysis_step : :obj:`aspecd.analysis.SingleAnalysisStep`
            analysis step to apply to the dataset

        Returns
        -------
        analysis_step : :obj:`aspecd.analysis.SingleAnalysisStep`
            analysis step applied to the dataset

        """
        # Important: Need a copy, not the reference to the original object
        analysis_step = copy.deepcopy(analysis_step)
        analysis_step.analyse(self, from_dataset=True)
        history_record = analysis_step.create_history_record()
        self.analyses.append(history_record)
        self._append_task(kind='analysis', task=history_record)
        return analysis_step

    def analyze(self, analysis_step=None):
        """Apply analysis to dataset.

        Same method as :meth:`analyse`, but for those preferring AE
        over BE.

        """
        analysis_step = self.analyse(analysis_step)
        return analysis_step

    def delete_analysis(self, index=None):
        """Remove analysis step record from dataset.

        Parameters
        ----------
        index : `int`
            Number of analysis in analyses to delete

        """
        del self.analyses[index]

    def annotate(self, annotation_=None):
        """Add annotation to dataset.

        Parameters
        ----------
        annotation_ : :obj:`aspecd.annotation.Annotation`
            annotation to add to the dataset

        """
        # Important: Need a copy, not the reference to the original object
        annotation_ = copy.deepcopy(annotation_)
        annotation_.annotate(self, from_dataset=True)
        history_record = annotation_.create_history_record()
        self.annotations.append(history_record)
        self._append_task(kind='annotation', task=history_record)

    def delete_annotation(self, index=None):
        """Remove annotation record from dataset.

        Parameters
        ----------
        index : `int`
            Number of analysis in analyses to delete

        """
        del self.annotations[index]

    def plot(self, plotter=None):
        """Perform plot with data of current dataset.

        Every plotter is an object of type :class:`aspecd.plotting.Plotter`
        and is passed as an argument to :meth:`plot`.

        The information necessary to reproduce a plot is stored in the
        :attr:`representations` attribute as object of class
        :class:`aspecd.dataset.PlotHistoryRecord`. This record contains as
        well a (deep) copy of the complete history of the dataset stored in
        :attr:`history`. Besides being a necessary prerequisite to
        reproduce a plot, this allows to automatically recreate plots
        requiring different incompatible preprocessing steps in arbitrary
        order.

        Parameters
        ----------
        plotter : :obj:`aspecd.plotting.Plotter`
            plot to perform with data of current dataset

        Returns
        -------
        plotter : :obj:`aspecd.plotting.Plotter`
            plot performed on the current dataset

        Raises
        ------
        aspecd.dataset.MissingPlotterError
            Raised when trying to plot without plotter

        """
        if not plotter:
            raise MissingPlotterError
        plotter.plot(dataset=self, from_dataset=True)
        plot_record = plotter.create_history_record()
        self.representations.append(plot_record)
        self._append_task(kind='representation', task=plot_record)
        return plotter

    def delete_representation(self, index=None):
        """Remove representation record from dataset.

        Parameters
        ----------
        index : `int`
            Number of analysis in analyses to delete

        """
        del self.representations[index]

    def load(self):
        """Load dataset object from persistence layer.

        .. todo::
            The way how and in what format datasets are stored needs still to
            be discussed and implemented.

        """
        pass

    def save(self):
        """Save dataset to persistence layer.

        .. todo::
            The way how and in what format datasets are stored needs still to
            be discussed and implemented.

        """
        pass

    def import_from(self, importer=None):
        """Import data and metadata contained in importer object.

        This requires initialising an :obj:`aspecd.io.Importer` object
        first that is provided as an argument for this method.

        .. note::
            The same operation can be performed by calling the
            :meth:`import_into` method of an :obj:`aspecd.io.Importer`
            object taking an :obj:`aspecd.dataset.Dataset` object as argument.

            However, as usually one wants to continue working with a dataset,
            first creating an instance of a dataset and a respective importer
            and then calling :meth:`import_from` of the dataset is the
            preferred way.

        Parameters
        ----------
        importer : :class:`aspecd.io.DatasetImporter`
            Importer containing data and metadata read from some source

        """
        if not importer:
            raise MissingImporterError("No importer provided")
        importer.import_into(self)
        self._origdata = copy.deepcopy(self.data)

    def export_to(self, exporter=None):
        """Export data and metadata.

        This requires initialising an :obj:`aspecd.io.DatasetImporter` object
        first that is provided as an argument for this method.

        .. note::
            The same operation can be performed by calling the
            :meth:`export_from` method of an :obj:`aspecd.io.Exporter`
            object taking an :obj:`aspecd.dataset.Dataset` object as argument.

            However, as usually the dataset is already at hand,
            first creating an instance of a respective exporter
            and then calling :meth:`export_to` of the dataset is the
            preferred way.

        Parameters
        ----------
        exporter : :class:`aspecd.io.DatasetExporter`
            Exporter writing data and metadata to specific output format

        """
        if not exporter:
            raise MissingExporterError("No exporter provided")
        exporter.export_from(self)

    def add_reference(self, dataset=None):
        """
        Add a reference to another dataset to the list of references.

        A reference is always an object of type
        :class:`aspecd.dataset.DatasetReference` that will be automatically
        created from the dataset provided.

        Parameters
        ----------
        dataset : :class:`aspecd.dataset.Dataset`
            dataset a reference for should be added to the list of references

        Raises
        ------
        aspecd.dataset.MissingDatasetError
            Raised if no dataset was provided

        """
        if not dataset:
            raise aspecd.dataset.MissingDatasetError
        dataset_reference = aspecd.dataset.DatasetReference()
        dataset_reference.from_dataset(dataset=dataset)
        self.references.append(dataset_reference)

    def remove_reference(self, dataset_id=None):
        """
        Remove a reference to another dataset from the list of references.

        A reference is always an object of type
        :class:`aspecd.dataset.DatasetReference` that was automatically
        created from the respective dataset when adding the reference.

        Parameters
        ----------
        dataset_id : :class:`string`
            ID of the dataset the reference should be removed for

        Raises
        ------
        aspecd.dataset.MissingDatasetError
            Raised if no dataset ID was provided

        """
        if not dataset_id:
            raise aspecd.dataset.MissingDatasetError
        for index, reference in enumerate(self.references):
            if dataset_id == reference.id:
                del self.references[index]
                break


class ExperimentalDataset(Dataset):
    """Base class for experimental datasets.

    The dataset is one of the core elements of the ASpecD framework, basically
    containing both, (numeric) data and corresponding metadata, aka information
    available about the data.

    The public attributes of a dataset can be converted to a dict via
    :meth:`aspecd.utils.ToDictMixin.to_dict()`.

    Attributes
    ----------
    metadata : :obj:`aspecd.metadata.ExperimentalDatasetMetadata`
        hierarchical key-value store of metadata

    """

    def __init__(self):
        super().__init__()
        self.metadata = aspecd.metadata.ExperimentalDatasetMetadata()


class CalculatedDataset(Dataset):
    """Base class for datasets containing calculated data.

    The dataset is one of the core elements of the ASpecD framework, basically
    containing both, (numeric) data and corresponding metadata, aka information
    available about the data.

    The public attributes of a dataset can be converted to a dict via
    :meth:`aspecd.utils.ToDictMixin.to_dict()`.

    Attributes
    ----------
    metadata : :obj:`aspecd.metadata.CalculatedDatasetMetadata`
        hierarchical key-value store of metadata

    """

    def __init__(self):
        super().__init__()
        self.data.calculated = True
        self._origdata.calculated = True
        self.metadata = aspecd.metadata.CalculatedDatasetMetadata()


class DatasetReference:
    """
    Reference to a given dataset.

    Often, one dataset needs to reference other datasets. A typical example
    would be a simulation stored in a dataset of class
    :class:`aspecd.dataset.CalculatedDataset` that needs to reference the
    corresponding experimental data, stored in a dataset of class
    :class:`aspecd.dataset.ExperimentalDataset`. Vice versa,
    the experimental dataset might want to store a reference to one (or
    more) simulations.

    As the dataset ID is not sufficient, both, the ID as well as the
    history of the dataset at the time the reference has been created gets
    stored in the reference and restored upon creating a (new) dataset.
    Hence, at least the data of the dataset returned should be identical to
    the data of the original dataset the reference has been created for.

    Attributes
    ----------
    type : :class:`str`
        type of dataset

        Will be inferred directly from dataset when creating a reference
        from a given dataset and is used to return a dataset of same type.
    id : :class:`str`
        (unique) id of the dataset, i.e. path, LOI, or else
    history : :class:`list`
        history of processing steps performed on the dataset to be referenced

    Raises
    ------
    aspecd.dataset.MissingDatasetError
        Raised if no dataset was provided when calling :meth:`from_dataset`

    """

    def __init__(self):
        self.type = ''
        self.id = ''  # pylint: disable=invalid-name
        self.history = list()

    def from_dataset(self, dataset=None):
        """
        Create dataset reference from dataset.

        Parameters
        ----------
        dataset : :class:`aspecd.dataset.Dataset`
            Dataset the reference should be created for

        Raises
        ------
        aspecd.dataset.MissingDatasetError
            Raised if no dataset was provided

        """
        if not dataset:
            raise MissingDatasetError
        self.type = aspecd.utils.full_class_name(dataset)
        self.id = dataset.id
        self.history = copy.deepcopy(dataset.history)

    def to_dataset(self):
        """
        Create (new) dataset from reference

        The history stored will be applied to the newly created dataset,
        hence the dataset should be in the same state with respect to
        processing steps as the original dataset was upon creating the
        reference.

        Returns
        -------
        dataset : :class:`aspecd.dataset.Dataset`
            Dataset with identical data to the one the reference has been
            created for

        """
        if not self.type:
            raise aspecd.dataset.MissingDatasetError
        dataset = aspecd.utils.object_from_class_name(self.type)
        dataset.id = self.id
        for history_record in self.history:
            history_record.replay(dataset)
        return dataset


class DatasetFactory:
    """
    Factory for creating dataset objects based on the source provided.

    Particularly in case of recipe-driven data analysis (c.f. :mod:`tasks`),
    there is a need to automatically retrieve datasets using nothing more
    than a source string that can be, e.g., a path or LOI.

    Packages derived from ASpecD should implement a :class:`DatasetFactory`
    inheriting from :class:`aspecd.dataset.DatasetFactory` and overriding
    the protected method :meth:`_create_dataset`. The only task of this
    protected method is to provide the correct dataset object, in most
    cases an instance of a class inheriting from
    :class:`aspecd.dataset.ExperimentalDataset`.

    Attributes
    ----------
    importer_factory : :class:`aspecd.io.DatasetImporterFactory`
        ImporterFactory instance used for importing datasets

    Raises
    ------
    aspecd.dataset.MissingSourceError
        Raised if no source is provided
    aspecd.dataset.MissingImporterFactoryError
        Raised if no ImporterFactory is available

    """

    def __init__(self):
        self.importer_factory = None

    def get_dataset(self, source=''):
        """
        Return dataset object for dataset specified by its source.

        The import of data into the dataset is handled using an instance of
        :class:`aspecd.io.DatasetImporterFactory`.

        The actual code for deciding which type of dataset to return in what
        case should be implemented in the non-public method
        :meth:`_create_dataset` in any package based on the ASpecD framework.

        Parameters
        ----------
        source : :class:`str`
            string describing the source of the dataset

            May be a filename or path, a URL/URI, a LOI, or similar

        Returns
        -------
        dataset : :class:`aspecd.dataset.Dataset`
            Dataset object of appropriate class

        Raises
        ------
        aspecd.dataset.MissingSourceError
            Raised if no source is provided
        aspecd.dataset.MissingImporterFactoryError
            Raised if no ImporterFactory is available

        """
        if not source:
            raise MissingSourceError(
                'A source is required to return a dataset')
        if not self.importer_factory:
            raise MissingImporterFactoryError(
                'An ImporterFactory is required to return a dataset')
        dataset_ = self._create_dataset(source=source)
        importer = self.importer_factory.get_importer(source=source)
        dataset_.import_from(importer)
        return dataset_

    # noinspection PyUnusedLocal
    # pylint: disable=unused-argument
    @staticmethod
    def _create_dataset(source=''):
        """
        Non-public method creating the actual (empty) dataset object.

        Classes inheriting from :class:`aspecd.dataset.DatasetFactory`
        should return an instance of the appropriate class that should in
        all cases inherit from :class:`aspecd.dataset.Dataset` or one of
        its subclasses.

        The parameter :param:`source` may be used to distinguish which type of
        dataset should be returned.

        Parameters
        ----------
        source : :class:`str`
            string describing the source of the dataset

            May be a filename or path, a URL/URI, a LOI, or similar

        Returns
        -------
        dataset : :class:`aspecd.dataset.Dataset`
            Dataset object of appropriate type

        """
        return ExperimentalDataset()


class Data:
    """
    Unit containing both, numeric data and corresponding axes.

    The data class ensures consistency in terms of dimensions between
    numerical data and axes.

    Parameters
    ----------
    data : `numpy.array`
        Numerical data
    axes : :class:`list`
        List of objects of type :class:`aspecd.dataset.Axis`

        The number of axes needs to be consistent with the dimensions of data.

        Axes will be set automatically when setting data. Hence,
        the easiest is to first set data and only afterwards set axis values.
    calculated : :class:`bool`
        Indicator for the origin of the numerical data (calculation or
        experiment).

    Attributes
    ----------
    calculated : :class:`bool`
        Indicate whether numeric data are calculated rather than
        experimentally recorded

    Raises
    ------
    aspecd.dataset.AxesCountError
        Raised if number of axes is inconsistent with data dimensions
    aspecd.dataset.AxesValuesInconsistentWithDataError
        Raised if axes values are inconsistent with data

    """

    def __init__(self, data=np.zeros(0), axes=None, calculated=False):
        self._data = data
        self._axes = []
        if axes is None:
            self._create_axes()
        else:
            self.axes = axes
        self.calculated = calculated

    @property
    def data(self):
        """Get or set (numeric) data.

        .. note::
            If you set data that have different dimensions to the data
            previously stored in the dataset, the axes values will be
            set to an array with indices corresponding to the size of the
            respective data dimension. You will most probably assign proper
            axis values afterwards. On the other hand, all other
            information stored in the axis object will be retained, namely
            quantity, unit, and label.

        """
        return self._data

    @data.setter
    def data(self, data):
        old_shape = self._data.shape
        self._data = data
        if old_shape != data.shape:
            if self.axes[0].values.size == 0:
                self._create_axes()
            else:
                self._update_axes()

    @property
    def axes(self):
        """Get or set axes.

        If you set axes, they will be checked for consistency with the data.
        Therefore, first set the data and only afterwards the axes,
        with values corresponding to the dimensions of the data.

        Raises
        ------
        aspecd.dataset.AxesCountError
            Raised if number of axes is inconsistent with data dimensions
        aspecd.dataset.AxesValuesInconsistentWithDataError
            Raised if axes values are inconsistent with data dimensions

        """
        return self._axes

    @axes.setter
    def axes(self, axes):
        self._axes = axes
        self._check_axes()

    def _create_axes(self):
        self._axes = []
        missing_axes = self.data.ndim + 1
        # pylint: disable=unused-variable
        # pylint: disable=invalid-name
        for ax in range(missing_axes):
            self._axes.append(Axis())

    def _update_axes(self):
        data_shape = self.data.shape
        for index in range(self.data.ndim - 1):
            if len(self.axes[index].values) != data_shape[index]:
                self.axes[index].values = np.arange(data_shape[index])

    def _check_axes(self):
        if len(self._axes) > self.data.ndim + 1:
            raise AxesCountError
        data_shape = self.data.shape
        for index in range(self.data.ndim):
            if len(self.axes[index].values) != data_shape[index]:
                raise AxesValuesInconsistentWithDataError


class Axis:
    """Axis for data in a dataset.

    An axis contains always both, numerical values as well as the metadata
    necessary to create axis labels and to make sense of the numerical
    information.

    Attributes
    ----------
    quantity : `string`
        quantity of the numerical data, usually used as first part of an
        automatically generated axis label
    unit : `string`
        unit of the numerical data, usually used as second part of an
        automatically generated axis label
    label : `string`
        manual label for the axis, particularly useful in cases where no
        quantity and unit are provided or should be overwritten.

    Raises
    ------
    aspecd.dataset.AxisValuesTypeError
        Raised when trying to set axis values to another type than numpy array
    aspecd.dataset.AxisValuesDimensionError
        Raised when trying to set axis values to an array with more than one
        dimension.

    """

    def __init__(self):
        self._values = np.zeros(0)
        self._equidistant = None
        self.quantity = ''
        self.unit = ''
        self.label = ''

    @property
    def values(self):
        """
        Get or set the numerical axis values.

        Values require to be a one-dimensional numpy array. Trying to set
        values to either a different type or a numpy array with more than one
        dimension will raise a corresponding error.

        Raises
        ------
        aspecd.dataset.AxisValuesTypeError
            Raised of axis values are of wrong type
        aspecd.dataset.AxisValuesDimensionError
            Raised if axis values are of wrong dimension, i.e. not a vector

        """
        return self._values

    @values.setter
    def values(self, values):
        if not isinstance(values, type(self._values)):
            raise AxisValuesTypeError
        if values.ndim > 1:
            raise AxisValuesDimensionError
        self._values = values
        self._set_equidistant_property()

    @property
    def equidistant(self):
        """Return whether the axes values are equidistant.

        True if the axis values are equidistant, False otherwise. None in
        case of no axis values.

        The property is set automatically if axis values are set and
        therefore read-only.

        While simple plotting of data values against non-uniform axes with
        non-equidistant values is usually straightforward, many processing
        steps rely on equidistant axis values in their simplest possible
        implementation.

        """
        return self._equidistant

    def _set_equidistant_property(self):
        if not self.values.size:
            return
        differences = self.values[1:] - self.values[0:-1]
        self._equidistant = (differences == differences[0]).all()


class HistoryRecord(aspecd.utils.ToDictMixin):
    """Generic base class for all kinds of history records.

    For all classes operating on datasets, such as
    :class:`aspecd.processing.ProcessingStep`,
    :class:`aspecd.analysis.SingleAnalysisStep` and others, there exist at least two
    "representations": (i) the generic one not (necessarily) tied to any
    concrete dataset, thus portable, and (ii) a concrete one having operated on
    a dataset and thus being accompanied with information about who has done
    what when how to what dataset.

    For this second type, a history class derived from
    :class:`aspecd.dataset.HistoryRecord` gets used, and it is this second type
    that is stored inside the Dataset object.

    Attributes
    ----------
    date : :obj:`datetime.datetime`
        datetime object with date current at HistoryRecord instantiation
    sysinfo : :obj:`aspecd.system.SystemInfo`
        key--value store with crucial system parameters, including user
        login name

    Parameters
    ----------
    package : :class:`str`
        Name of package the hstory record gets recorded for

        Prerequisite for reproducibility, gets stored in the
        :attr:`sysinfo` attribute. Will usually be provided automatically by
        the dataset.

    """

    def __init__(self, package=''):
        self.date = datetime.today()
        self.sysinfo = aspecd.system.SystemInfo(package=package)
        super().__init__()
