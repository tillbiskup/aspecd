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


class TestScalarAlgebra(unittest.TestCase):
    def setUp(self):
        self.processing = aspecd.processing.ScalarAlgebra()
        self.dataset = aspecd.dataset.Dataset()
        self.dataset.data.data = np.sin(np.linspace(0, 2*np.pi, num=500))

    def test_instantiate_class(self):
        pass

    def test_has_appropriate_description(self):
        self.assertIn('algebra', self.processing.description.lower())

    def test_is_undoable(self):
        self.assertTrue(self.processing.undoable)

    def test_without_kind_raises(self):
        with self.assertRaises(ValueError):
            self.dataset.process(self.processing)

    def test_with_wrong_kind_raises(self):
        self.processing.parameters["kind"] = 'foo'
        with self.assertRaises(ValueError):
            self.dataset.process(self.processing)

    def test_add(self):
        self.processing.parameters["kind"] = 'plus'
        self.processing.parameters["value"] = 3
        self.dataset.process(self.processing)
        self.assertAlmostEqual(4, self.dataset.data.data.max(), 5)

    def test_add_with_2D_dataset(self):
        self.dataset.data.data = np.tile(self.dataset.data.data, (5, 1))
        self.processing.parameters["kind"] = 'plus'
        self.processing.parameters["value"] = 3
        self.dataset.process(self.processing)
        self.assertAlmostEqual(4, self.dataset.data.data.max(), 5)

    def test_add_using_capitalised_name(self):
        self.processing.parameters["kind"] = 'Plus'
        self.processing.parameters["value"] = 3
        self.dataset.process(self.processing)
        self.assertAlmostEqual(4, self.dataset.data.data.max(), 5)

    def test_add_using_alternative_name(self):
        self.processing.parameters["kind"] = 'add'
        self.processing.parameters["value"] = 3
        self.dataset.process(self.processing)
        self.assertAlmostEqual(4, self.dataset.data.data.max(), 5)

    def test_add_using_symbol(self):
        self.processing.parameters["kind"] = '+'
        self.processing.parameters["value"] = 3
        self.dataset.process(self.processing)
        self.assertAlmostEqual(4, self.dataset.data.data.max(), 5)

    def test_subtract(self):
        self.processing.parameters["kind"] = 'minus'
        self.processing.parameters["value"] = 3
        self.dataset.process(self.processing)
        self.assertAlmostEqual(-2, self.dataset.data.data.max(), 5)

    def test_subtract_using_alternative_name(self):
        self.processing.parameters["kind"] = 'subtract'
        self.processing.parameters["value"] = 3
        self.dataset.process(self.processing)
        self.assertAlmostEqual(-2, self.dataset.data.data.max(), 5)

    def test_subtract_with_symbol(self):
        self.processing.parameters["kind"] = '-'
        self.processing.parameters["value"] = 3
        self.dataset.process(self.processing)
        self.assertAlmostEqual(-2, self.dataset.data.data.max(), 5)

    def test_multiply(self):
        self.processing.parameters["kind"] = 'times'
        self.processing.parameters["value"] = 3
        self.dataset.process(self.processing)
        self.assertAlmostEqual(3, self.dataset.data.data.max(), 4)

    def test_multiply_with_alternative_name(self):
        self.processing.parameters["kind"] = 'multiply'
        self.processing.parameters["value"] = 3
        self.dataset.process(self.processing)
        self.assertAlmostEqual(3, self.dataset.data.data.max(), 4)

    def test_multiply_with_symbol(self):
        self.processing.parameters["kind"] = '*'
        self.processing.parameters["value"] = 3
        self.dataset.process(self.processing)
        self.assertAlmostEqual(3, self.dataset.data.data.max(), 4)

    def test_divide(self):
        self.processing.parameters["kind"] = 'by'
        self.processing.parameters["value"] = 2
        self.dataset.process(self.processing)
        self.assertAlmostEqual(0.5, self.dataset.data.data.max(), 5)

    def test_divide_with_alternative_name(self):
        self.processing.parameters["kind"] = 'divide'
        self.processing.parameters["value"] = 2
        self.dataset.process(self.processing)
        self.assertAlmostEqual(0.5, self.dataset.data.data.max(), 5)

    def test_divide_with_symbol(self):
        self.processing.parameters["kind"] = '/'
        self.processing.parameters["value"] = 2
        self.dataset.process(self.processing)
        self.assertAlmostEqual(0.5, self.dataset.data.data.max(), 5)


class TestProjection(unittest.TestCase):
    def setUp(self):
        self.processing = aspecd.processing.Projection()
        self.dataset = aspecd.dataset.Dataset()
        data = np.sin(np.linspace(0, 2*np.pi, num=500))
        self.dataset.data.data = np.tile(data, (5, 1))

    def test_instantiate_class(self):
        pass

    def test_has_appropriate_description(self):
        self.assertIn('project', self.processing.description.lower())

    def test_is_undoable(self):
        self.assertTrue(self.processing.undoable)

    def test_with_1D_dataset_raises(self):
        dataset = aspecd.dataset.Dataset()
        dataset.data.data = np.sin(np.linspace(0, 2*np.pi, num=500))
        with self.assertRaises(
                aspecd.exceptions.NotApplicableToDatasetError):
            dataset.process(self.processing)

    def test_project_reduces_data_dimensionality(self):
        self.dataset.process(self.processing)
        self.assertEqual(1, self.dataset.data.data.ndim)

    def test_project_removes_axis(self):
        self.dataset.process(self.processing)
        self.assertEqual(2, len(self.dataset.data.axes))

    def test_project_removes_correct_axis(self):
        self.dataset.data.axes[1].quantity = 'foo'
        self.dataset.data.axes[2].quantity = 'intensity'
        self.dataset.process(self.processing)
        self.assertNotEqual('foo', self.dataset.data.axes[1])
        self.assertNotEqual('intensity', self.dataset.data.axes[-1])

    def test_project_averages_along_first_axis_by_default(self):
        self.dataset.process(self.processing)
        self.assertEqual(500, self.dataset.data.data.shape[0])

    def test_project_along_second_axis(self):
        self.processing.parameters['axis'] = 1
        self.dataset.process(self.processing)
        self.assertEqual(5, self.dataset.data.data.shape[0])

    def test_project_along_non_existing_axis_raises(self):
        with self.assertRaisesRegex(IndexError, "Axis [0-9]+ out of bounds"):
            self.processing.parameters['axis'] = 2
            self.dataset.process(self.processing)


class TestSliceExtraction(unittest.TestCase):
    def setUp(self):
        self.processing = aspecd.processing.SliceExtraction()
        self.dataset = aspecd.dataset.Dataset()
        data = np.sin(np.linspace(0, 2*np.pi, num=500))
        self.dataset.data.data = np.tile(data, (5, 1)) \
            * np.tile(np.linspace(1, 2, num=5), (500, 1)).T

    def test_instantiate_class(self):
        pass

    def test_has_appropriate_description(self):
        self.assertIn('extract slice', self.processing.description.lower())

    def test_is_undoable(self):
        self.assertTrue(self.processing.undoable)

    def test_with_1D_dataset_raises(self):
        dataset = aspecd.dataset.Dataset()
        dataset.data.data = np.sin(np.linspace(0, 2*np.pi, num=500))
        with self.assertRaises(
                aspecd.exceptions.NotApplicableToDatasetError):
            dataset.process(self.processing)

    def test_without_index_raises(self):
        with self.assertRaisesRegex(IndexError, "for slice extraction"):
            self.dataset.process(self.processing)

    def test_with_index_exceeding_dimension_raises(self):
        self.processing.parameters['index'] = 10
        with self.assertRaisesRegex(IndexError, "Index [0-9]+ out of bounds"):
            self.dataset.process(self.processing)

    def test_extract_slice(self):
        origdata = self.dataset.data.data
        self.processing.parameters['index'] = 3
        self.dataset.process(self.processing)
        np.testing.assert_allclose(origdata[3, :], self.dataset.data.data)

    def test_extract_slice_removes_axis(self):
        self.processing.parameters['index'] = 3
        self.dataset.process(self.processing)
        self.assertEqual(2, len(self.dataset.data.axes))

    def test_extract_slice_removes_correct_axis(self):
        self.processing.parameters['index'] = 3
        self.dataset.data.axes[1].quantity = 'foo'
        self.dataset.data.axes[2].quantity = 'intensity'
        self.dataset.process(self.processing)
        self.assertNotEqual('foo', self.dataset.data.axes[1])
        self.assertNotEqual('intensity', self.dataset.data.axes[-1])

    def test_extract_slice_operates_along_first_axis_by_default(self):
        origdata = self.dataset.data.data
        self.processing.parameters['index'] = 3
        self.dataset.process(self.processing)
        np.testing.assert_allclose(origdata[3, :], self.dataset.data.data)

    def test_extract_slice_along_second_axis(self):
        origdata = self.dataset.data.data
        self.processing.parameters['index'] = 3
        self.processing.parameters['axis'] = 1
        self.dataset.process(self.processing)
        np.testing.assert_allclose(origdata[:, 3], self.dataset.data.data)

    def test_extract_slice_along_non_existing_axis_raises(self):
        with self.assertRaisesRegex(IndexError, "Axis [0-9]+ out of bounds"):
            self.processing.parameters['index'] = 3
            self.processing.parameters['axis'] = 2
            self.dataset.process(self.processing)


class TestBaselineCorrection(unittest.TestCase):
    def setUp(self):
        self.processing = aspecd.processing.BaselineCorrection()
        self.dataset = aspecd.dataset.Dataset()
        self.dataset.data.data = np.linspace(0, 2, num=500)

    def test_instantiate_class(self):
        pass

    def test_has_appropriate_description(self):
        self.assertIn('correct baseline',
                      self.processing.description.lower())

    def test_has_parameter_kind(self):
        self.assertIn('kind', self.processing.parameters)

    def test_has_parameter_order(self):
        self.assertIn('order', self.processing.parameters)

    def test_has_parameter_coefficients(self):
        self.assertIn('coefficients', self.processing.parameters)

    def test_has_parameter_fit_area(self):
        self.assertIn('fit_area', self.processing.parameters)

    def test_subtract_polynomial_baseline_of_zeroth_order(self):
        self.processing.parameters['order'] = 0
        self.dataset.process(self.processing)
        self.assertAlmostEqual(0, self.dataset.data.data.mean())

    def test_subtract_polynomial_baseline_of_first_order(self):
        self.processing.parameters['order'] = 1
        self.dataset.process(self.processing)
        self.assertAlmostEqual(0, self.dataset.data.data[0])
        self.assertAlmostEqual(0, self.dataset.data.data[-1])

    def test_subtract_polynomial_sets_coefficients(self):
        self.processing.parameters['order'] = 0
        processing_step = self.dataset.process(self.processing)
        self.assertTrue(processing_step.parameters['coefficients'])

    def test_with_2D_dataset_raises(self):
        dataset = aspecd.dataset.Dataset()
        dataset.data.data = np.random.random([5, 5])
        with self.assertRaises(
                aspecd.exceptions.NotApplicableToDatasetError):
            dataset.process(self.processing)
