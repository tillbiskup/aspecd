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

"""

import copy
from datetime import datetime

import numpy as np

from aspecd import analysis, annotation, metadata, plotting, processing, \
    system, utils


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
    """Exception raised importing without :class:`aspecd.io.Importer`

    Attributes
    ----------
    message : `str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class MissingExporterError(Error):
    """Exception raised importing without :class:`aspecd.io.Exporter`

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
    representations : `list`
        representations of the dataset, e.g., plots

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
        self.representations = []
        # Package name is used to store the package version in history records
        self._package_name = utils.package_name(self)

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

        .. todo::
            If processing_step is undoable, set _origdata to data.
            The only true undoable processing steps I can currently think of
            are those that add several datasets together. Changing _origdata
            here prevents the need of exposing _origdata in any way.
            In such case, all previous plots stored in the (to be implemented)
            list of representations need to be removed, or at least the user
            should be notified on that, as these plots cannot be reproduced
            due to a change in _origdata.

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

    def _create_processing_history_record(self, processing_step):
        historyrecord = \
            ProcessingHistoryRecord(processing_step=processing_step,
                                    package=self._package_name)
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

        Same method as :meth:`analyse`, but for those preferring AE
        over BE.

        """
        self.analyse(analysis_step)

    def _create_analysis_history_record(self, analysis_step):
        history_record = AnalysisHistoryRecord(package=self._package_name)
        history_record.analysis = analysis_step
        return history_record

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
        history_record = self._create_annotation_history_record(annotation_)
        annotation_.annotate(self)
        self.annotations.append(history_record)

    def _create_annotation_history_record(self, annotation_):
        history_record = AnnotationHistoryRecord(package=self._package_name)
        history_record.annotation = annotation_
        return history_record

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
        MissingPlotterError
            Raised when trying to plot without plotter

        """
        if not plotter:
            raise MissingPlotterError
        plotter.dataset = self
        plotter.plot()
        plot_record = self._create_plot_record(plotter=plotter)
        self.representations.append(plot_record)
        return plotter

    def _create_plot_record(self, plotter=None):
        plot_record = PlotHistoryRecord(package=self._package_name)
        plot_record.plot = plotting.SinglePlotRecord(plotter=plotter)
        plot_record.plot.processing_steps = copy.deepcopy(self.history)
        return plot_record

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
        importer : :class:`aspecd.io.Importer`
            Importer containing data and metadata read from some source

        """
        if not importer:
            raise MissingImporterError("No importer provided")
        importer.import_into(self)

    def export_to(self, exporter=None):
        """Export data and metadata.

        This requires initialising an :obj:`aspecd.io.Importer` object
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
        exporter : :class:`aspecd.io.Exporter`
            Exporter writing data and metadata to specific output format

        """
        if not exporter:
            raise MissingExporterError("No exporter provided")
        exporter.export_from(self)


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
        AxesCountError
            Raised if number of axes is inconsistent with data dimensions
        AxesValuesInconsistentWithDataError
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

        Raises
        ------
        AxisValuesTypeError
            Raised of axis values are of wrong type
        AxisValuesDimensionError
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

    Parameters
    ----------
    package : `str`
        Name of package the hstory record gets recorded for

        Prerequisite for reproducibility, gets stored in the
        :attr:`sysinfo` attribute. Will usually be provided automatically by
        the dataset.

    """

    def __init__(self, package=''):
        self.date = datetime.today()
        self.sysinfo = system.SystemInfo(package=package)


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

    package : `str`
        Name of package the hstory record gets recorded for

        Prerequisite for reproducibility, gets stored in the
        :attr:`aspecd.dataset.HistoryRecord.sysinfo` attribute.
        Will usually be provided automatically by the dataset.

    """

    def __init__(self, processing_step=None, package=''):
        super().__init__(package=package)
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

    package : `str`
        Name of package the hstory record gets recorded for

        Prerequisite for reproducibility, gets stored in the
        :attr:`aspecd.dataset.HistoryRecord.sysinfo` attribute.
        Will usually be provided automatically by the dataset.

    """

    def __init__(self, package=''):
        super().__init__(package=package)
        self.analysis = analysis.AnalysisStep()


class AnnotationHistoryRecord(HistoryRecord):
    """History record for annotations of datasets.

    Attributes
    ----------
    annotation : :class:`aspecd.analysis.Annotation`
        Annotation the history is saved for

    package : `str`
        Name of package the hstory record gets recorded for

        Prerequisite for reproducibility, gets stored in the
        :attr:`aspecd.dataset.HistoryRecord.sysinfo` attribute.
        Will usually be provided automatically by the dataset.

    """

    def __init__(self, package=''):
        super().__init__(package=package)
        self.annotation = annotation.Annotation()


class PlotHistoryRecord(HistoryRecord):
    """History record for plots of datasets.

    Attributes
    ----------
    plot : :class:`aspecd.plotting.SinglePlotRecord`
        Plot the history is saved for

    package : `str`
        Name of package the hstory record gets recorded for

        Prerequisite for reproducibility, gets stored in the
        :attr:`aspecd.dataset.HistoryRecord.sysinfo` attribute.
        Will usually be provided automatically by the dataset.

    """

    def __init__(self, package=''):
        super().__init__(package=package)
        self.plot = plotting.SinglePlotRecord()
