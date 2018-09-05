"""Datasets."""

from aspecd import data, history
import copy


class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class UndoWithEmptyHistoryError(Error):
    """Exception raised trying to undo with empty history

    Attributes
    ----------
    message : `str`
        explanation of the error
    """

    def __init__(self, message=''):
        self.message = message


class UndoAtBeginningOfHistoryError(Error):
    """Exception raised trying to undo with history pointer at zero

    Attributes
    ----------
    message : `str`
        explanation of the error
    """

    def __init__(self, message=''):
        self.message = message


class UndoStepUndoableError(Error):
    """Exception raised trying to undo an undoable step of history

    Attributes
    ----------
    message : `str`
        explanation of the error
    """

    def __init__(self, message=''):
        self.message = message


class RedoAlreadyAtLatestChangeError(Error):
    """Exception raised trying to redo with empty history

    Attributes
    ----------
    message : `str`
        explanation of the error
    """

    def __init__(self, message=''):
        self.message = message


class ProcessingWithLeadingHistoryError(Error):
    """Exception raised trying to process with leading history

    Attributes
    ----------
    message : `str`
        explanation of the error
    """

    def __init__(self, message=''):
        self.message = message


class Dataset:
    """Base class for all kinds of datasets.

    The dataset is one of the core elements of the ASpecD framework, basically
    containing both, (numeric) data and corresponding metadata, aka information
    available about the data.

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
        self.data = data.Data()
        self._origdata = data.Data()
        self.metadata = dict()
        self.history = []
        self._historypointer = -1
        self.analyses = []
        self.annotations = []

    def process(self, processing_step):
        """Apply processing step to dataset.

        Every processing step is an object of type processing.ProcessingStep
        and is passed as argument to dataset.process.

        .. todo:: This should probably be changed.

        Calling this function ensures that the history record is added to the
        dataset as well as a few basic checks are performed such as for leading
        history, meaning that the _historypointer is not set to the current tip
        of the history of the dataset. In this case, an error is raised.

        Parameters
        ----------
        processing_step : `aspecd.processing.ProcessingStep`
            processing step to apply to the dataset

        Returns
        -------
        processing_step : `aspecd.processing.ProcessingStep`
            processing step applied to the dataset

        Raises
        ------
        ProcessingWithLeadingHistoryError
            Raised  when trying to process with leading history
        """
        if self._has_leading_history():
            raise ProcessingWithLeadingHistoryError
        # Important: Need a copy, not the reference to the original object
        processing_step = copy.deepcopy(processing_step)
        historyrecord = self._create_processing_historyrecord(processing_step)
        processing_step.process(self)
        self._append_processing_historyrecord(historyrecord)
        return processing_step

    def undo(self):
        """Revert last processing step.

        Actually, the history pointer is decremented and starting from the
        ``origdata``, all processing steps are reapplied to the data up to
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
        if len(self.history) == 0:
            raise UndoWithEmptyHistoryError
        if self._historypointer == -1:
            raise UndoAtBeginningOfHistoryError
        if self.history[self._historypointer].undoable:
            raise UndoStepUndoableError
        self._decrement_historypointer()
        self._replay_history()

    def redo(self):
        """Reapply previously undone processing step.

        Raises
        ------
        RedoAlreadyAtLatestChangeError
            Raised  when trying to redo with empty history
        """
        if self._historypointer == len(self.history) - 1:
            raise RedoAlreadyAtLatestChangeError
        processingstep = self.history[self._historypointer + 1].processing
        processingstep.process(self)
        self._increment_historypointer()

    def _has_leading_history(self):
        if len(self.history) - 1 > self._historypointer:
            return True
        else:
            return False

    @staticmethod
    def _create_processing_historyrecord(processing_step):
        historyrecord = history.ProcessingHistoryRecord(processing_step)
        historyrecord.processing = processing_step
        return historyrecord

    def _append_processing_historyrecord(self, historyrecord):
        self.history.append(historyrecord)
        self._increment_historypointer()

    def _increment_historypointer(self):
        self._historypointer += 1

    def _decrement_historypointer(self):
        self._historypointer -= 1

    def _replay_history(self):
        self.data = self._origdata
        for historyentry in self.history[:self._historypointer]:
            historyentry.replay(self)

    def strip_history(self):
        """Remove leading history, if any.
        """
        if not self._has_leading_history():
            return
        del self.history[self._historypointer + 1:]

    def analyse(self, analysisstep):
        """Apply analysis to dataset.

        Parameters
        ----------
        analysisstep : `aspecd.analysis.AnalysisStep`
            analysis step to apply to the dataset
        """
        # Important: Need a copy, not the reference to the original object
        analysisstep = copy.deepcopy(analysisstep)
        # TODO: Add all processing steps in history of dataset to AnalysisStep.
        # At least if preprocessing list in AnalysisStep is empty.
        # Otherwise, perhaps copy dataset object, perform processing steps from
        # preprocessing list in AnalysisStep and analyse this one...
        historyrecord = self._create_analysis_historyrecord(analysisstep)
        analysisstep.analyse(self)
        self.analyses.append(historyrecord)

    def analyze(self, analysisstep):
        """Same method as ``self.analyse``, but for those preferring AE over BE.
        """
        self.analyse(analysisstep)

    @staticmethod
    def _create_analysis_historyrecord(analysisstep):
        historyrecord = history.AnalysisHistoryRecord()
        historyrecord.analysis = analysisstep
        return historyrecord

    def delete_analysis(self, index):
        """Remove analysis step record from dataset."""
        del self.analyses[index]

    def annotate(self, annotation):
        """Add annotation to dataset.

        Parameters
        ----------
        annotation : `aspecd.annotation.Annotation`
            annotation to add to the dataset
        """
        # Important: Need a copy, not the reference to the original object
        annotation = copy.deepcopy(annotation)
        historyrecord = self._create_annotation_historyrecord(annotation)
        annotation.annotate(self)
        self.annotations.append(historyrecord)
        pass

    @staticmethod
    def _create_annotation_historyrecord(annotation):
        historyrecord = history.AnnotationHistoryRecord()
        historyrecord.annotation = annotation
        return historyrecord

    def load(self):
        pass

    def save(self):
        pass

    def importfrom(self):
        pass

    def exportto(self):
        pass
