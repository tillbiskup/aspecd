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

    def test_has_description_property(self):
        self.assertTrue(hasattr(self.processing, 'description'))

    def test_description_property_is_string(self):
        self.assertTrue(isinstance(self.processing.description, str))

    def test_has_comment_property(self):
        self.assertTrue(hasattr(self.processing, 'comment'))

    def test_description_comment_is_string(self):
        self.assertTrue(isinstance(self.processing.comment, str))

    def test_has_process_method(self):
        self.assertTrue(hasattr(self.processing, 'process'))
        self.assertTrue(callable(self.processing.process))
