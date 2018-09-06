"""History."""

from aspecd import processing, system, analysis, annotation
from datetime import datetime


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
    :class:`aspecd.history.HistoryRecord` gets used, and it is this second type
    that is stored inside the Dataset object.
    """

    def __init__(self):
        self.date = datetime.today()
        self.sysinfo = system.SystemInfo()


class ProcessingHistoryRecord(HistoryRecord):
    """History record for processing steps on datasets.

    Parameters
    ----------
    processing_step : :class:`aspecd.processing.ProcessingStep`
        record of the processing step the history is saved for
    """

    def __init__(self, processing_step=None):
        super().__init__()
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
    """History record for analysis steps on datasets."""

    def __init__(self):
        super().__init__()
        self.analysis = analysis.AnalysisStep()


class AnnotationHistoryRecord(HistoryRecord):
    """History record for annotations of datasets."""

    def __init__(self):
        super().__init__()
        self.annotation = annotation.Annotation()
