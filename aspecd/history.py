"""History."""


from aspecd import processing
from datetime import datetime


class HistoryRecord:

    def __init__(self):
        self.processing = processing.ProcessingStep()
        self.date = datetime.today()
