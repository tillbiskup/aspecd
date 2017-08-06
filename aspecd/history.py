"""History."""


from aspecd import processing, system
from datetime import datetime


class HistoryRecord:

    def __init__(self):
        self.processing = processing.ProcessingStep()
        self.date = datetime.today()
        self.sysinfo = system.SystemInfo()

    @property
    def undoable(self):
        return self.processing.undoable
