"""Tests for history."""

import unittest

from aspecd import history, processing, system
from datetime import datetime, timedelta


class TestHistoryRecord(unittest.TestCase):
    def setUp(self):
        self.historyrecord = history.HistoryRecord()

    def test_instantiate_class(self):
        pass

    def test_has_processing_property(self):
        self.assertTrue(hasattr(self.historyrecord, 'processing'))

    def test_processing_is_processingstep(self):
        self.assertTrue(isinstance(self.historyrecord.processing,
                                   processing.ProcessingStep))

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
