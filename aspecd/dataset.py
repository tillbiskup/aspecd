"""Datasets.

The dataset is one key concept of the ASpecD framework, containing the data as
well as the corresponding metadata. Furthermore, a history of every processing,
analysis and annotation step is recorded as well, aiming at a maximum of
reproducibility. This is part of how the ASpecD framework tries to support good
scientific practice.

"""

import copy
from datetime import datetime

import numpy as np

from aspecd import metadata, processing, system, analysis, annotation


class Error(Exception):
    """Base class for exceptions in this module."""

    pass


class MissingProcessingStepError(Error):
    """Exception raised trying to process without processing_step

    Attributes
    ----------
    message : `str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class UndoWithEmptyHistoryError(Error):
    """Exception raised trying to undo with empty history

    Attributes
    ----------
    message : `str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class UndoAtBeginningOfHistoryError(Error):
    """Exception raised trying to undo with history pointer at zero

    Attributes
    ----------
    message : `str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class UndoStepUndoableError(Error):
    """Exception raised trying to undo an undoable step of history

    Attributes
    ----------
    message : `str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class RedoAlreadyAtLatestChangeError(Error):
    """Exception raised trying to redo with empty history

    Attributes
    ----------
    message : `str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class ProcessingWithLeadingHistoryError(Error):
    """Exception raised trying to process with leading history

    Attributes
    ----------
    message : `str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class MissingPlotterError(Error):
    """Exception raised trying to plot without :class:`aspecd.plotting.Plotter`

    Attributes
    ----------
    message : `str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class MissingImporterError(Error):
    """Exception raised importing without :class:`aspecd.importer.Importer`

    Attributes
    ----------
    message : `str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class Dataset:
    """Base class for all kinds of datasets.

    The dataset is one of the core elements of the ASpecD framework, basically
    containing both, (numeric) data and corresponding metadata, aka information
    available about the data.

    Attributes
    ----------
    data : :obj:`aspecd.dataset.Data`
        numeric data and axes
    metadata : :obj:`aspecd.metadata.DatasetMetadata`
        hierarchical key-value store of metadata
    history : `list`
        processing steps performed on the numeric data
    analyses : `list`
        analysis steps performed on the dataset
    annotations : `list`
        annotations of the dataset

    Raises
    ------
    UndoWithEmptyHistoryError
        Raised when trying to undo with empty history
    UndoAtBeginningOfHistoryError
        Raised when trying to undo with history pointer at zero
    UndoStepUndoableError
        Raised when trying to undo an undoable step of history
    RedoAlreadyAtLatestChangeError
        Raised  when trying to redo with empty history
    ProcessingWithLeadingHistoryError
        Raised  when trying to process with leading history

    """

    def __init__(self):
        self.data = Data()
        self._origdata = Data()
        self.metadata = metadata.DatasetMetadata()
        self.history = []
        self._history_pointer = -1
        self.analyses = []
        self.annotations = []

    def process(self, processing_step=None):
        """Apply processing step to dataset.

        Every processing step is an object of type
        :class:`aspecd.processing.ProcessingStep` and is passed as argument
        to :func:`process`.

        Calling this function ensures that the history record is added to the
        dataset as well as a few basic checks are performed such as for leading
        history, meaning that the ``_history_pointer`` is not set to the
        current tip of the history of the dataset. In this case, an error is
        raised.

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
        ProcessingWithLeadingHistoryError
            Raised when trying to process with leading history

        """
        if self._has_leading_history():
            raise ProcessingWithLeadingHistoryError
        if not processing_step:
            raise MissingProcessingStepError
        # Important: Need a copy, not the reference to the original object
        processing_step = copy.deepcopy(processing_step)
        processing_step.process(self)
        history_record = \
            self._create_processing_history_record(processing_step)
        self._append_processing_history_record(history_record)
        return processing_step

    def undo(self):
        """Revert last processing step.

        Actually, the history pointer is decremented and starting from the
        ``_origdata``, all processing steps are reapplied to the data up to
        this point in history.

        Raises
        ------
        UndoWithEmptyHistoryError
            Raised when trying to undo with empty history
        UndoAtBeginningOfHistoryError
            Raised when trying to undo with history pointer at zero
        UndoStepUndoableError
            Raised when trying to undo an undoable step of history

        """
        if not self.history:
            raise UndoWithEmptyHistoryError
        if self._history_pointer == -1:
            raise UndoAtBeginningOfHistoryError
        if self.history[self._history_pointer].undoable:
            raise UndoStepUndoableError
        self._decrement_history_pointer()
        self._replay_history()

    def redo(self):
        """Reapply previously undone processing step.

        Raises
        ------
        RedoAlreadyAtLatestChangeError
            Raised when trying to redo with empty history

        """
        if self._history_pointer == len(self.history) - 1:
            raise RedoAlreadyAtLatestChangeError
        processing_step_record = \
            self.history[self._history_pointer + 1].processing
        processing_step = processing_step_record.create_processing_step()
        processing_step.process(self)
        self._increment_history_pointer()

    def _has_leading_history(self):
        return len(self.history) - 1 > self._history_pointer

    @staticmethod
    def _create_processing_history_record(processing_step):
        historyrecord = ProcessingHistoryRecord(processing_step)
        return historyrecord

    def _append_processing_history_record(self, history_record):
        self.history.append(history_record)
        self._increment_history_pointer()

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

        Parameters
        ----------
        analysis_step : :obj:`aspecd.analysis.AnalysisStep`
            analysis step to apply to the dataset

        """
        # Important: Need a copy, not the reference to the original object
        analysis_step = copy.deepcopy(analysis_step)
        # TODO: Add all processing steps in history of dataset to AnalysisStep.
        # At least if preprocessing list in AnalysisStep is empty.
        # Otherwise, perhaps copy dataset object, perform processing steps from
        # preprocessing list in AnalysisStep and analyse this one...
        history_record = self._create_analysis_history_record(analysis_step)
        analysis_step.analyse(self)
        self.analyses.append(history_record)

    def analyze(self, analysis_step=None):
        """Apply analysis to dataset.

        Same method as :func:`analyse`, but for those preferring AE
        over BE.

        """
        self.analyse(analysis_step)

    @staticmethod
    def _create_analysis_history_record(analysis_step):
        history_record = AnalysisHistoryRecord()
        history_record.analysis = analysis_step
        return history_record

    def delete_analysis(self, index):
        """Remove analysis step record from dataset."""
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
        history_record = self._create_annotation_history_record(annotation_)
        annotation_.annotate(self)
        self.annotations.append(history_record)

    @staticmethod
    def _create_annotation_history_record(annotation_):
        history_record = AnnotationHistoryRecord()
        history_record.annotation = annotation_
        return history_record

    def plot(self, plotter=None):
        """Perform plot with data of current dataset.

        Every plotter is an object of type :class:`aspecd.plotting.Plotter`
        and is passed as an argument to :func:`plot`.

        .. todo::
            Does :func:`plot` save some "PlotRecord" in a field like
            "representations", similar to :func:`process` saves a
            :class:`aspecd.processing.ProcessingStepRecord` to the history?
            Idea there would be to have a list of representations performed
            on the given dataset.

            How to deal with the history? How to tie a representation (plot)
            to a given state of the history? How to figure out when trying to
            undo a step in history whether a representation is affected?

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
        MissingPlotterError
            Raised when trying to plot without plotter

        """
        if not plotter:
            raise MissingPlotterError
        plotter.plot(self)
        return plotter

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

        This requires initialising an :obj:`aspecd.importer.Importer` object
        first that is provided as an argument for this method.

        .. note::
            The same operation can be performed by calling the
            :func:`import_into` method of an :obj:`aspecd.importer.Importer`
            object taking an :obj:`aspecd.dataset.Dataset` object as argument.

            However, as usually one wants to continue working with a dataset,
            first creating an instance of a dataset and a respective importer
            and then calling :func:`import_from` of the dataset is the
            preferred way.

        Parameters
        ----------
        importer : :class:`aspecd.importer.Importer`
            Importer containing data and metadata read from some source

        """
        if not importer:
            raise MissingImporterError("No importer provided")
        importer.import_into(self)

    def export_to(self):
        """Export data and metadata.

        .. todo::
            This needs to be implemented, probably using a generic exporter.

        """
        pass


class AxesCountError(Error):
    """Exception raised for wrong number of axes

    Attributes
    ----------
    message : `str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class AxesValuesInconsistentWithDataError(Error):
    """Exception raised for axes values inconsistent with data

    Attributes
    ----------
    message : `str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class Data:
    """
    Unit containing both, numeric data and corresponding axes.

    The data class ensures consistency in terms of dimensions between
    numerical data and axes.

    Parameters
    ----------
    data : `numpy.array`
        Numerical data
    axes : `list`
        List of objects of type :class:`aspecd.dataset.Axis`

        The number of axes needs to be consistent with the dimensions of data.

        Axes will be set automatically when setting data. Hence,
        the easiest is to first set data and only afterwards set axis values.
    calculated : `bool`
        Indicator for the origin of the numerical data (calculation or
        experiment).

    Attributes
    ----------
    calculated : `bool`
        Indicate whether numeric data are calculated rather than
        experimentally recorded

    Raises
    ------
    AxesCountError
        Raised if number of axes is inconsistent with data dimensions
    AxesValuesInconsistentWithDataError
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
        """Get (numeric) data.

        Returns
        -------
        data : `numpy.array`
            Numerical data

        """
        return self._data

    @data.setter
    def data(self, data):
        self._data = data
        self._create_axes()

    @property
    def axes(self):
        """Get axes.

        Returns
        -------
        axes : `list`
            List of objects of type :class:`aspecd.dataset.Axis`

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

    def _check_axes(self):
        if len(self._axes) > self.data.ndim + 1:
            raise AxesCountError
        data_shape = self.data.shape
        for index in range(self.data.ndim):
            if len(self.axes[index].values) != data_shape[index]:
                raise AxesValuesInconsistentWithDataError


class AxisValuesDimensionError(Error):
    """Exception raised for wrong dimension of values

    Attributes
    ----------
    message : `str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class AxisValuesTypeError(Error):
    """Exception raised for wrong type of values

    Attributes
    ----------
    message : `str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


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
    AxisValuesTypeError
        Raised when trying to set axis values to another type than numpy array
    AxisValuesDimensionError
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


class HistoryRecord:
    """Generic base class for all kinds of history records.

    For all classes operating on datasets, such as
    :class:`aspecd.processing.ProcessingStep`,
    :class:`aspecd.analysis.AnalysisStep` and others, there exist at least two
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

    """

    def __init__(self):
        self.date = datetime.today()
        self.sysinfo = system.SystemInfo()


class ProcessingHistoryRecord(HistoryRecord):
    """History record for processing steps on datasets.

    Attributes
    ----------
    processing : `aspecd.processing.ProcessingStepRecord`
        record of the processing step

    Parameters
    ----------
    processing_step : :class:`aspecd.processing.ProcessingStep`
        processing step the history is saved for

    """

    def __init__(self, processing_step=None):
        super().__init__()
        self.processing = processing.ProcessingStepRecord(processing_step)

    @property
    def undoable(self):
        """Can this processing step be reverted?"""
        return self.processing.undoable

    def replay(self, dataset):
        """Replay the processing step saved in the history record.

        Parameters
        ----------
        dataset : :class:`aspecd.dataset.Dataset`
            dataset the processing step should be replayed to

        """
        processing_step = self.processing.create_processing_step()
        processing_step.process(dataset=dataset)


class AnalysisHistoryRecord(HistoryRecord):
    """History record for analysis steps on datasets.

    Attributes
    ----------
    analysis : :class:`aspecd.analysis.AnalysisStep`
        Analysis step the history is saved for

    """

    def __init__(self):
        super().__init__()
        self.analysis = analysis.AnalysisStep()


class AnnotationHistoryRecord(HistoryRecord):
    """History record for annotations of datasets.

    Attributes
    ----------
    annotation : :class:`aspecd.analysis.Annotation`
        Annotation the history is saved for

    """

    def __init__(self):
        super().__init__()
        self.annotation = annotation.Annotation()
