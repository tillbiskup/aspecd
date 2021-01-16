"""Tests for processing."""

import unittest

import numpy as np

import aspecd.dataset
import aspecd.exceptions
import aspecd.history
import aspecd.processing
import aspecd.utils


class TestProcessingStep(unittest.TestCase):
    def setUp(self):
        self.processing = aspecd.processing.ProcessingStep()

    def test_instantiate_class(self):
        pass

    def test_has_undoable_property(self):
        self.assertTrue(hasattr(self.processing, 'undoable'))

    def test_has_name_property(self):
        self.assertTrue(hasattr(self.processing, 'name'))

    def test_name_property_equals_full_class_name(self):
        full_class_name = aspecd.utils.full_class_name(self.processing)
        self.assertEqual(self.processing.name, full_class_name)

    def test_has_parameters_property(self):
        self.assertTrue(hasattr(self.processing, 'parameters'))

    def test_parameters_property_is_dict(self):
        self.assertTrue(isinstance(self.processing.parameters, dict))

    def test_has_info_property(self):
        self.assertTrue(hasattr(self.processing, 'info'))

    def test_info_property_is_dict(self):
        self.assertTrue(isinstance(self.processing.info, dict))

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
        self.processing.dataset = aspecd.dataset.Dataset()
        self.processing.process()
        self.assertGreater(len(self.processing.dataset.history), 0)

    def test_process_without_processingstep_nor_dataset_raises(self):
        with self.assertRaises(aspecd.exceptions.MissingDatasetError):
            self.processing.process()

    def test_process_with_dataset_sets_dataset(self):
        test_dataset = aspecd.dataset.Dataset()
        processing_step = test_dataset.process(self.processing)
        self.assertTrue(isinstance(processing_step.dataset,
                                   aspecd.dataset.Dataset))

    def test_process_with_dataset_writes_history(self):
        test_dataset = self.processing.process(dataset=aspecd.dataset.Dataset())
        self.assertGreater(len(test_dataset.history), 0)

    def test_process_with_dataset_using_dataset_process_writes_history(self):
        test_dataset = aspecd.dataset.Dataset()
        test_dataset.process(self.processing)
        self.assertGreater(len(test_dataset.history), 0)

    def test_process_returns_dataset(self):
        test_dataset = self.processing.process(aspecd.dataset.Dataset())
        self.assertTrue(isinstance(test_dataset, aspecd.dataset.Dataset))

    def test_has_create_history_record_method(self):
        self.assertTrue(hasattr(self.processing, 'create_history_record'))
        self.assertTrue(callable(self.processing.create_history_record))

    def test_create_history_record_returns_history_record(self):
        self.processing.dataset = aspecd.dataset.Dataset()
        history_record = self.processing.create_history_record()
        self.assertTrue(isinstance(history_record,
                                   aspecd.history.ProcessingHistoryRecord))


class TestNormalisation(unittest.TestCase):
    def setUp(self):
        self.processing = aspecd.processing.Normalisation()
        self.dataset = aspecd.dataset.Dataset()
        self.dataset.data.data = np.sin(np.linspace(0, 3*np.pi, num=500))*2

    def test_instantiate_class(self):
        pass

    def test_has_appropriate_description(self):
        self.assertIn('normalise', self.processing.description.lower())

    def test_is_undoable(self):
        self.assertTrue(self.processing.undoable)

    def test_normalise_to_maximum(self):
        self.processing.parameters["kind"] = 'maximum'
        self.dataset.process(self.processing)
        self.assertEqual(1, self.dataset.data.data.max())

    def test_normalise_to_minimum(self):
        self.processing.parameters["kind"] = 'minimum'
        self.dataset.process(self.processing)
        self.assertAlmostEqual(-1, self.dataset.data.data.min(), 4)

    def test_normalise_to_amplitude(self):
        self.processing.parameters["kind"] = 'amplitude'
        self.dataset.process(self.processing)
        self.assertAlmostEqual(1, self.dataset.data.data.max() -
                               self.dataset.data.data.min(), 4)

    def test_normalise_to_area(self):
        self.processing.parameters["kind"] = 'area'
        self.dataset.process(self.processing)
        # noinspection PyTypeChecker
        self.assertAlmostEqual(1, np.sum(np.abs(self.dataset.data.data)), 4)

    def test_normalise_to_maximum_2d(self):
        self.processing.parameters["kind"] = 'maximum'
        self.dataset.data.data = np.random.random([10, 10])
        self.dataset.process(self.processing)
        self.assertEqual(1, self.dataset.data.data.max())

    def test_normalise_to_minimum_2d(self):
        self.processing.parameters["kind"] = 'minimum'
        self.dataset.data.data = np.random.random([10, 10])
        self.dataset.process(self.processing)
        self.assertEqual(1, self.dataset.data.data.min())

    def test_normalise_to_amplitude_2d(self):
        self.processing.parameters["kind"] = 'amplitude'
        self.dataset.data.data = np.random.random([10, 10])
        self.dataset.process(self.processing)
        self.assertAlmostEqual(1, self.dataset.data.data.max() -
                               self.dataset.data.data.min(), 4)

    def test_normalise_to_area_2d(self):
        self.processing.parameters["kind"] = 'area'
        self.dataset.data.data = np.random.random([10, 10])
        self.dataset.process(self.processing)
        # noinspection PyTypeChecker
        self.assertAlmostEqual(1, np.sum(np.abs(self.dataset.data.data)), 4)


class TestIntegration(unittest.TestCase):
    def setUp(self):
        self.processing = aspecd.processing.Integration()
        self.dataset = aspecd.dataset.Dataset()
        self.dataset.data.data = np.sin(np.linspace(0, 2*np.pi, num=500))

    def test_instantiate_class(self):
        pass

    def test_has_appropriate_description(self):
        self.assertIn('integrate', self.processing.description.lower())

    def test_is_undoable(self):
        self.assertTrue(self.processing.undoable)

    def test_integrate_returns_only_positive_values(self):
        self.dataset.process(self.processing)
        self.assertAlmostEqual(0, np.min(self.dataset.data.data))

    def test_integrate_2D_dataset(self):
        self.dataset.data.data = np.tile(self.dataset.data.data, (5, 1))
        self.dataset.process(self.processing)
        self.assertAlmostEqual(0, np.min(self.dataset.data.data))


class TestDifferentiation(unittest.TestCase):
    def setUp(self):
        self.processing = aspecd.processing.Differentiation()
        self.dataset = aspecd.dataset.Dataset()
        xdata = np.linspace(0, 2*np.pi, num=500)
        self.dataset.data.data = np.sin(xdata)*np.sin(xdata)

    def test_instantiate_class(self):
        pass

    def test_has_appropriate_description(self):
        self.assertIn('differentiate', self.processing.description.lower())

    def test_is_undoable(self):
        self.assertTrue(self.processing.undoable)

    def test_differentiate_returns_symmetric_spectrum(self):
        self.dataset.process(self.processing)
        self.assertAlmostEqual(-np.min(self.dataset.data.data),
                               np.max(self.dataset.data.data))

    def test_differentiate_returns_spectrum_of_same_length_as_original(self):
        original_data = self.dataset.data.data
        self.dataset.process(self.processing)
        self.assertEqual(len(original_data), len(self.dataset.data.data))

    def test_integrate_2D_dataset(self):
        self.dataset.data.data = np.tile(self.dataset.data.data, (5, 1))
        self.dataset.process(self.processing)
        self.assertAlmostEqual(-np.min(self.dataset.data.data),
                               np.max(self.dataset.data.data))

    def test_differentiate_2D_dataset_retains_shape(self):
        self.dataset.data.data = np.tile(self.dataset.data.data, (5, 1))
        original_data = self.dataset.data.data
        self.dataset.process(self.processing)
        self.assertEqual(np.shape(original_data),
                         np.shape(self.dataset.data.data))
