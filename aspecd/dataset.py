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

    def process(self):
        self.history.append(history.HistoryRecord())
        self._historypointer += 1

    def undo(self):
        if len(self.history) == 0:
            raise UndoWithEmptyHistoryError
        if self._historypointer == -1:
            raise UndoAtBeginningOfHistoryError
        if self.history[-1].processing.undoable:
            raise UndoStepUndoableError
        self._historypointer -= 1

    def redo(self):
        if self._historypointer == len(self.history)-1:
            raise RedoAlreadyAtLatestChangeError
        self._historypointer += 1
