"""Tests for history."""

import unittest

from aspecd import history, processing, analysis, system, dataset
from datetime import datetime, timedelta


class TestHistoryRecord(unittest.TestCase):
    def setUp(self):
        self.historyrecord = history.HistoryRecord()

    def test_instantiate_class(self):
        pass

    def test_has_date_property(self):
        self.assertTrue(hasattr(self.historyrecord, 'date'))

    def test_date_is_datetime(self):
        self.assertTrue(isinstance(self.historyrecord.date, datetime))

    def test_date_is_current_date(self):
        now = datetime.today()
        self.assertAlmostEqual(now, self.historyrecord.date,
                               delta=timedelta(seconds=1))

    def test_has_sysinfo_property(self):
        self.assertTrue(hasattr(self.historyrecord, 'sysinfo'))

    def test_sysinfo_is_systeminfo(self):
        self.assertTrue(
            isinstance(self.historyrecord.sysinfo, system.SystemInfo))


class TestProcessingHistoryRecord(unittest.TestCase):
    def setUp(self):
        self.historyrecord = history.ProcessingHistoryRecord()
        self.processing_step = processing.ProcessingStep()

    def test_instantiate_class(self):
        pass

    def test_instantiate_class_with_processing_step(self):
        history.ProcessingHistoryRecord(self.processing_step)

    def test_has_processing_property(self):
        self.assertTrue(hasattr(self.historyrecord, 'processing'))

    def test_processing_is_processingsteprecord(self):
        self.assertTrue(isinstance(self.historyrecord.processing,
                                   processing.ProcessingStepRecord))

    def test_has_date_property(self):
        self.assertTrue(hasattr(self.historyrecord, 'date'))

    def test_has_sysinfo_property(self):
        self.assertTrue(hasattr(self.historyrecord, 'sysinfo'))

    def test_has_undoable_property(self):
        self.assertTrue(hasattr(self.historyrecord, 'undoable'))

    def test_undoable_is_boolean(self):
        self.assertTrue(isinstance(self.historyrecord.undoable, bool))

    def test_has_replay_method(self):
        self.assertTrue(hasattr(self.historyrecord, 'replay'))
        self.assertTrue(callable(self.historyrecord.replay))

    def test_replay(self):
        self.historyrecord.replay(dataset.Dataset())


class TestAnalysisHistoryRecord(unittest.TestCase):
    def setUp(self):
        self.historyrecord = history.AnalysisHistoryRecord()

    def test_instantiate_class(self):
        pass

    def test_has_processing_property(self):
        self.assertTrue(hasattr(self.historyrecord, 'analysis'))

    def test_processing_is_processingstep(self):
        self.assertTrue(isinstance(self.historyrecord.analysis,
                                   analysis.AnalysisStep))
