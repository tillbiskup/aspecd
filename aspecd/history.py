"""History."""


from aspecd import processing, system
from datetime import datetime


class HistoryRecord:
    """
    Generic base class for all classes that can eventually operate on datasets.

    For all classes operating on datasets, such as ProcessingStep, AnalysisStep
    and others, there exist at least two "representations": (i) the generic one
    not (necessarily) tied to any concrete dataset, thus portable, and (ii) a
    concrete one having operated on a dataset and thus being accompanied with
    information about who has done what when how to what dataset.

    For this second type, a history class derived from HistoryRecord gets used,
    and it is this second type that is stored inside the Dataset object.
    """

    def __init__(self):
        self.date = datetime.today()
        self.sysinfo = system.SystemInfo()


class ProcessingHistoryRecord(HistoryRecord):
    """
    History record for processing steps on datasets.
    """

    def __init__(self):
        super().__init__()
        self.processing = processing.ProcessingStep()

    @property
    def undoable(self):
        return self.processing.undoable

    def replay(self, dataset):
        self.processing.process(dataset=dataset)
