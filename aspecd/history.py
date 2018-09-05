"""History."""

from aspecd import processing, system, analysis, annotation
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

    def __init__(self, processing_step=None):
        super().__init__()
        self.processing = processing.ProcessingStepRecord(processing_step)

    @property
    def undoable(self):
        return self.processing.undoable

    def replay(self, dataset):
        processing_step = self.processing.create_processing_step()
        processing_step.process(dataset=dataset)


class AnalysisHistoryRecord(HistoryRecord):
    """
    History record for analysis steps on datasets.
    """

    def __init__(self):
        super().__init__()
        self.analysis = analysis.AnalysisStep()


class AnnotationHistoryRecord(HistoryRecord):
    """
    History record for annotations of datasets.
    """

    def __init__(self):
        super().__init__()
        self.annotation = annotation.Annotation()
