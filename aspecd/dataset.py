"""Dataset."""


from aspecd import data, history


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


class Dataset:

    def __init__(self):
        self.data = data.Data()
        self._origdata = data.Data()
        self.metadata = dict()
        self.history = []
        self._historypointer = -1

    def process(self, processingstep):
        historyrecord = self._create_historyrecord(processingstep)
        processingstep.process(self)
        self._append_historyrecord(historyrecord)

    def undo(self):
        if len(self.history) == 0:
            raise UndoWithEmptyHistoryError
        if self._historypointer == -1:
            raise UndoAtBeginningOfHistoryError
        if self.history[-1].processing.undoable:
            raise UndoStepUndoableError
        self._decrement_historypointer()
        self._replay_history()

    def redo(self):
        if self._historypointer == len(self.history)-1:
            raise RedoAlreadyAtLatestChangeError
        processingstep = self.history[self._historypointer+1].processing
        processingstep.process(self)
        self._increment_historypointer()

    @staticmethod
    def _create_historyrecord(processingstep):
        historyrecord = history.HistoryRecord()
        historyrecord.processing = processingstep
        return historyrecord

    def _append_historyrecord(self, historyrecord):
        self.history.append(historyrecord)
        self._increment_historypointer()

    def _increment_historypointer(self):
        self._historypointer += 1

    def _decrement_historypointer(self):
        self._historypointer -= 1

    def _replay_history(self):
        self.data = self._origdata
        for historyentry in self.history[:self._historypointer]:
            historyentry.processing.process(self)
