"""Tests for history."""

import unittest

from aspecd import history, processing


class TestHistoryRecord(unittest.TestCase):

    def setUp(self):
        self.hrec = history.HistoryRecord()

    def test_instantiate_class(self):
        pass

    def test_has_processing_property(self):
        self.assertTrue(hasattr(self.hrec, 'processing'))

    def test_processing_is_processingstep(self):
        self.assertTrue(isinstance(self.hrec.processing,
                                   processing.ProcessingStep))

