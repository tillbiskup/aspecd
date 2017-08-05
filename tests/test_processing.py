"""Tests for processing."""

import unittest

from aspecd import processing


class TestProcessingStep(unittest.TestCase):

    def setUp(self):
        self.processing = processing.ProcessingStep()

    def test_instantiate_class(self):
        pass

    def test_has_undoable_property(self):
        self.assertTrue(hasattr(self.processing, 'undoable'))

    def test_has_name_property(self):
        self.assertTrue(hasattr(self.processing, 'name'))

    def test_name_property_equals_class_name(self):
        self.assertEqual(self.processing.name, 'ProcessingStep')

    def test_has_parameters_property(self):
        self.assertTrue(hasattr(self.processing, 'parameters'))

    def test_parameters_property_is_dict(self):
        self.assertTrue(isinstance(self.processing.parameters, dict))
