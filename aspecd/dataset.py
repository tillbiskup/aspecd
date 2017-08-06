"""Dataset."""

from aspecd import data, history
import copy


class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class UndoWithEmptyHistoryError(Error):
    """Exception raised trying to undo with empty history

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message=''):
        self.message = message


class UndoAtBeginningOfHistoryError(Error):
    """Exception raised trying to undo with history pointer at zero

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message=''):
        self.message = message


class UndoStepUndoableError(Error):
    """Exception raised trying to undo an undoable step of history

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message=''):
        self.message = message


class RedoAlreadyAtLatestChangeError(Error):
    """Exception raised trying to redo with empty history

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message=''):
        self.message = message


class ProcessingWithLeadingHistoryError(Error):
    """Exception raised trying to process with leading history

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message=''):
        self.message = message


class Dataset:
    def __init__(self):
        self.data = data.Data()
        self._origdata = data.Data()
        self.metadata = dict()
        self.history = []
        self._historypointer = -1
        self.analyses = []

    def process(self, processingstep):
        if self._has_leading_history():
            raise ProcessingWithLeadingHistoryError
        # Important: Need a copy, not the reference to the original object
        processingstep = copy.deepcopy(processingstep)
        historyrecord = self._create_processinghistoryrecord(processingstep)
        processingstep.process(self)
        self._append_processinghistoryrecord(historyrecord)

    def undo(self):
        if len(self.history) == 0:
            raise UndoWithEmptyHistoryError
        if self._historypointer == -1:
            raise UndoAtBeginningOfHistoryError
        if self.history[self._historypointer].undoable:
            raise UndoStepUndoableError
        self._decrement_historypointer()
        self._replay_history()

    def redo(self):
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
    def _create_processinghistoryrecord(processingstep):
        historyrecord = history.ProcessingHistoryRecord()
        historyrecord.processing = processingstep
        return historyrecord

    def _append_processinghistoryrecord(self, historyrecord):
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
        if not self._has_leading_history():
            return
        del self.history[self._historypointer + 1:]

    def analyse(self, analysisstep):
        # Important: Need a copy, not the reference to the original object
        analysisstep = copy.deepcopy(analysisstep)
        # TODO: Add all processing steps in history of dataset to AnalysisStep.
        # At least if preprocessing list in AnalysisStep is empty.
        # Otherwise, perhaps copy dataset object, perform processing steps from
        # preprocessing list in AnalysisStep and analyse this one...
        historyrecord = self._create_analysishistoryrecord(analysisstep)
        analysisstep.analyse(self)
        self.analyses.append(historyrecord)

    def analyze(self, analysisstep):
        self.analyse(analysisstep)

    @staticmethod
    def _create_analysishistoryrecord(analysisstep):
        historyrecord = history.AnalysisHistoryRecord()
        historyrecord.analysis = analysisstep
        return historyrecord

    def delete_analysis(self, index):
        del self.analyses[index]

    def load(self):
        pass

    def save(self):
        pass

    def importfrom(self):
        pass

    def exportto(self):
        pass
