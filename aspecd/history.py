"""History."""


from aspecd import processing, system
from datetime import datetime


class HistoryRecord:

    def __init__(self):
        self.date = datetime.today()
        self.sysinfo = system.SystemInfo()


class ProcessingHistoryRecord(HistoryRecord):

    def __init__(self):
        super().__init__()
        self.processing = processing.ProcessingStep()

    @property
    def undoable(self):
        return self.processing.undoable

    def replay(self, dataset):
        self.processing.process(dataset=dataset)
