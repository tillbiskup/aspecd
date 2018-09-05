"""Tests for processing."""

import unittest

from aspecd import processing, dataset


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

    def test_process_without_processingstep_and_with_dataset(self):
        self.processing.dataset = dataset.Dataset()
        self.processing.process()
        self.assertGreater(len(self.processing.dataset.history), 0)

    def test_process_without_processingstep_nor_dataset_raises(self):
        with self.assertRaises(processing.MissingDatasetError):
            self.processing.process()

    def test_process_with_dataset_sets_dataset(self):
        test_dataset = dataset.Dataset()
        processing_step = test_dataset.process(self.processing)
        self.assertTrue(isinstance(processing_step.dataset, dataset.Dataset))

    def test_process_with_dataset(self):
        test_dataset = dataset.Dataset()
        test_dataset.process(self.processing)
        self.assertGreater(len(test_dataset.history), 0)

    def test_calling_process_returns_dataset(self):
        test_dataset = self.processing.process(dataset.Dataset())
        self.assertTrue(isinstance(test_dataset, dataset.Dataset))


class TestProcessingStepRecord(unittest.TestCase):
    def setUp(self):
        self.processing_record = processing.ProcessingStepRecord()

    def test_instantiate_class(self):
        pass

    def test_has_create_processing_step_method(self):
        self.assertTrue(hasattr(self.processing_record,
                                'create_processing_step'))
        self.assertTrue(
            callable(self.processing_record.create_processing_step))

    def test_create_processing_step_returns_processing_object(self):
        test_object = self.processing_record.create_processing_step()
        self.assertTrue(isinstance(test_object, processing.ProcessingStep))

    def test_processing_object_has_correct_undoable_value(self):
        self.processing_record.undoable = True
        test_object = self.processing_record.create_processing_step()
        self.assertTrue(test_object.undoable, self.processing_record.undoable)

    def test_has_parameters_property(self):
        self.assertTrue(hasattr(self.processing_record, 'parameters'))

    def test_processing_object_has_correct_parameters_value(self):
        self.processing_record.parameters['test'] = True
        test_object = self.processing_record.create_processing_step()
        self.assertEqual(test_object.parameters['test'], True)

    def test_has_description_property(self):
        self.assertTrue(hasattr(self.processing_record, 'description'))

    def test_processing_object_has_correct_description_value(self):
        self.processing_record.description = 'Test'
        test_object = self.processing_record.create_processing_step()
        self.assertEqual(test_object.description, 'Test')

    def test_has_class_name_property(self):
        self.assertTrue(hasattr(self.processing_record, 'class_name'))
