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

    def test_description_property_is_sensible(self):
        self.assertIn(self.processing.description, 'Abstract processing step')

    def test_has_comment_property(self):
        self.assertTrue(hasattr(self.processing, 'comment'))

    def test_description_comment_is_string(self):
        self.assertTrue(isinstance(self.processing.comment, str))

    def test_has_process_method(self):
        self.assertTrue(hasattr(self.processing, 'process'))
        self.assertTrue(callable(self.processing.process))


class TestSingleProcessingStep(unittest.TestCase):
    def setUp(self):
        self.processing = aspecd.processing.SingleProcessingStep()

    def test_instantiate_class(self):
        pass

    def test_is_processingstep(self):
        self.assertTrue(isinstance(self.processing,
                                   aspecd.processing.ProcessingStep))

    def test_description_property_is_sensible(self):
        self.assertIn(self.processing.description,
                      'Abstract singleprocessing step')

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


class TestMultiProcessingStep(unittest.TestCase):
    def setUp(self):
        self.processing = aspecd.processing.MultiProcessingStep()

    def test_instantiate_class(self):
        pass

    def test_is_processingstep(self):
        self.assertTrue(isinstance(self.processing,
                                   aspecd.processing.ProcessingStep))

    def test_description_property_is_sensible(self):
        self.assertIn(self.processing.description,
                      'Abstract multiprocessing step')

    def test_has_datasets_property(self):
        self.assertTrue(hasattr(self.processing, 'datasets'))

    def test_datasets_property_is_list(self):
        self.assertTrue(isinstance(self.processing.datasets, list))

    def test_process_without_datasets_raises(self):
        with self.assertRaises(aspecd.exceptions.MissingDatasetError):
            self.processing.process()

    def test_process_with_datasets(self):
        self.processing.datasets.append(aspecd.dataset.Dataset())
        self.processing.process()

    def test_process_checks_applicability(self):
        dataset1 = aspecd.dataset.Dataset()
        dataset1.data.data = np.random.random([5, 5])
        dataset2 = aspecd.dataset.Dataset()
        dataset2.data.data = np.random.random(5)

        class MyProcessingStep(aspecd.processing.MultiProcessingStep):
            @staticmethod
            def applicable(dataset):
                return len(dataset.data.axes) == 2

        processing_step = MyProcessingStep()
        processing_step.datasets.append(dataset1)
        processing_step.datasets.append(dataset2)
        with self.assertRaises(aspecd.exceptions.NotApplicableToDatasetError):
            processing_step.process()

    def test_process_with_datasets_appends_history_record(self):
        dataset1 = aspecd.dataset.Dataset()
        dataset2 = aspecd.dataset.Dataset()
        self.processing.datasets.append(dataset1)
        self.processing.datasets.append(dataset2)
        self.processing.process()
        self.assertTrue(dataset1.history)
        self.assertTrue(dataset2.history)


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

    def test_normalise_to_maximum_with_noisy_data(self):
        self.dataset.data.data = \
            np.concatenate((np.zeros(50), self.dataset.data.data, np.zeros(50)))
        self.dataset.data.data \
            += (np.random.random(len(self.dataset.data.data))-0.5) * 0.5
        self.processing.parameters["kind"] = 'maximum'
        self.processing.parameters["noise_range"] = 10
        self.dataset.process(self.processing)
        self.assertGreaterEqual(1.25, self.dataset.data.data.max(), 1)

    def test_normalise_to_minimum_with_noisy_data(self):
        self.dataset.data.data = \
            np.concatenate((np.zeros(50), self.dataset.data.data, np.zeros(50)))
        self.dataset.data.data \
            += (np.random.random(len(self.dataset.data.data))-0.5) * 0.5
        self.processing.parameters["kind"] = 'minimum'
        self.processing.parameters["noise_range"] = 10
        self.dataset.process(self.processing)
        self.assertLessEqual(-1.25, self.dataset.data.data.min(), 1)

    def test_normalise_to_amplitude_with_noisy_data(self):
        self.dataset.data.data = \
            np.concatenate((np.zeros(50), self.dataset.data.data, np.zeros(50)))
        self.dataset.data.data \
            += (np.random.random(len(self.dataset.data.data))-0.5) * 0.5
        self.processing.parameters["kind"] = 'amplitude'
        self.processing.parameters["noise_range"] = 10
        self.dataset.process(self.processing)
        self.assertGreaterEqual(1.25, self.dataset.data.data.max() -
                                self.dataset.data.data.min())


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
        self.dataset.data.axes[0].quantity = 'foo'
        self.dataset.data.axes[1].quantity = 'bar'
        self.dataset.data.axes[2].quantity = 'intensity'
        self.dataset.process(self.processing)
        self.assertEqual('bar', self.dataset.data.axes[0].quantity)
        self.assertEqual('intensity', self.dataset.data.axes[-1].quantity)

    def test_project_removes_correct_axis_projecting_along_second_axis(self):
        self.dataset.data.axes[0].quantity = 'foo'
        self.dataset.data.axes[1].quantity = 'bar'
        self.dataset.data.axes[2].quantity = 'intensity'
        self.processing.parameters['axis'] = 1
        self.dataset.process(self.processing)
        self.assertEqual('foo', self.dataset.data.axes[0].quantity)
        self.assertEqual('intensity', self.dataset.data.axes[-1].quantity)

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
        self.processing.parameters['position'] = 10
        with self.assertRaisesRegex(ValueError, "Index out of axis range."):
            self.dataset.process(self.processing)

    def test_extract_slice(self):
        origdata = self.dataset.data.data
        self.processing.parameters['position'] = 3
        self.dataset.process(self.processing)
        np.testing.assert_allclose(origdata[3, :], self.dataset.data.data)

    def test_extract_slice_with_index_zero(self):
        origdata = self.dataset.data.data
        self.processing.parameters['position'] = 0
        self.dataset.process(self.processing)
        np.testing.assert_allclose(origdata[0, :], self.dataset.data.data)

    def test_extract_slice_removes_axis(self):
        self.processing.parameters['position'] = 3
        self.dataset.process(self.processing)
        self.assertEqual(2, len(self.dataset.data.axes))

    def test_extract_slice_removes_correct_axis(self):
        self.processing.parameters['position'] = 3
        self.dataset.data.axes[0].quantity = 'foo'
        self.dataset.data.axes[1].quantity = 'bar'
        self.dataset.data.axes[2].quantity = 'intensity'
        self.dataset.process(self.processing)
        self.assertEqual('bar', self.dataset.data.axes[0].quantity)
        self.assertEqual('intensity', self.dataset.data.axes[-1].quantity)

    def test_extract_slice_removes_correct_axis_with_axis_one(self):
        self.processing.parameters['position'] = 3
        self.processing.parameters['axis'] = 1
        self.dataset.data.axes[0].quantity = 'foo'
        self.dataset.data.axes[1].quantity = 'bar'
        self.dataset.data.axes[2].quantity = 'intensity'
        self.dataset.process(self.processing)
        self.assertEqual('foo', self.dataset.data.axes[0].quantity)
        self.assertEqual('intensity', self.dataset.data.axes[-1].quantity)

    def test_extract_slice_operates_along_first_axis_by_default(self):
        origdata = self.dataset.data.data
        self.processing.parameters['position'] = 3
        self.dataset.process(self.processing)
        np.testing.assert_allclose(origdata[3, :], self.dataset.data.data)

    def test_extract_slice_along_second_axis(self):
        origdata = self.dataset.data.data
        self.processing.parameters['position'] = 3
        self.processing.parameters['axis'] = 1
        self.dataset.process(self.processing)
        np.testing.assert_allclose(origdata[:, 3], self.dataset.data.data)

    def test_extract_slice_along_non_existing_axis_raises(self):
        with self.assertRaisesRegex(IndexError, "Axis [0-9]+ out of bounds"):
            self.processing.parameters['position'] = 3
            self.processing.parameters['axis'] = 2
            self.dataset.process(self.processing)

    def test_extract_slice_with_wrong_unit_raises(self):
        self.processing.parameters["unit"] = "foo"
        self.processing.parameters["position"] = 3
        with self.assertRaises(ValueError):
            self.dataset.process(self.processing)

    def test_extract_slice_with_axis_units(self):
        self.processing.parameters["unit"] = "axis"
        self.dataset.data.axes[0].values = \
            np.linspace(30, 70, len(self.dataset.data.axes[0].values))
        self.processing.parameters["position"] = 40
        data = self.dataset.data.data[1, :]
        self.dataset.process(self.processing)
        np.testing.assert_allclose(data, self.dataset.data.data)

    def test_unit_is_case_insensitive(self):
        self.processing.parameters["unit"] = "aXis"
        self.dataset.data.axes[0].values = \
            np.linspace(30, 70, len(self.dataset.data.axes[0].values))
        self.processing.parameters["position"] = 40
        data = self.dataset.data.data[1, :]
        self.dataset.process(self.processing)
        np.testing.assert_allclose(data, self.dataset.data.data)

    def test_extract_slice_with_axis_units_out_of_range_raises(self):
        self.processing.parameters["unit"] = "axis"
        self.dataset.data.axes[0].values = \
            np.linspace(30, 70, len(self.dataset.data.axes[0].values))
        self.processing.parameters["position"] = 300
        with self.assertRaises(ValueError):
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

    def test_baseline_correction_without_area(self):
        self.dataset.data.data = np.ones(100) + 10
        self.dataset.data.axes[0].values = np.linspace(1, 100, num=100)
        self.dataset.process(self.processing)
        self.assertAlmostEqual(self.dataset.data.data[5], 0)

    def test_baseline_correction_with_unequal_no_of_points_per_side(self):
        self.dataset.data.data = np.r_[np.ones(5) + 5, np.ones(75), np.ones(
            20)+5]
        self.dataset.data.axes[0].values = np.linspace(1, 100, num=100)
        self.processing.parameters['fit_area'] = [5, 20]
        self.dataset.process(self.processing)
        self.assertAlmostEqual(self.dataset.data.data[-20], 0)

    def test_baseline_correction_with_percentage_float(self):
        self.dataset.data.data = np.r_[np.ones(20) + 5, np.ones(60), np.ones(
            20)+5]
        self.dataset.data.axes[0].values = np.linspace(1, 100, num=100)
        self.processing.parameters['fit_area'] = 20.
        self.dataset.process(self.processing)
        self.assertAlmostEqual(self.dataset.data.data[19], 0)

    def test_baseline_correction_with_percentage_int(self):
        self.dataset.data.data = np.r_[np.ones(20) + 5, np.ones(60), np.ones(
            20)+5]
        self.dataset.data.axes[0].values = np.linspace(1, 100, num=100)
        self.processing.parameters['fit_area'] = 20
        self.dataset.process(self.processing)
        self.assertAlmostEqual(self.dataset.data.data[19], 0)

    def test_baseline_correction_with_percentage_list_one_element(self):
        self.dataset.data.data = np.r_[np.ones(20) + 5, np.ones(60), np.ones(
            20)+5]
        self.dataset.data.axes[0].values = np.linspace(1, 100, num=100)
        self.processing.parameters['percentage'] = [20, ]
        self.dataset.process(self.processing)
        self.assertAlmostEqual(self.dataset.data.data[19], 0)

    def test_with_2D_dataset(self):
        dataset = aspecd.dataset.Dataset()
        dataset.data.data = np.ones([5, 100])
        dataset.process(self.processing)
        self.assertAlmostEqual(0, dataset.data.data.mean())

    def test_with_2D_dataset_along_second_axis(self):
        dataset = aspecd.dataset.Dataset()
        dataset.data.data = np.ones([5, 100])
        self.processing.parameters["axis"] = 1
        dataset.process(self.processing)
        self.assertAlmostEqual(0, dataset.data.data.mean())


class TestAveraging(unittest.TestCase):
    def setUp(self):
        self.processing = aspecd.processing.Averaging()
        self.dataset = aspecd.dataset.Dataset()
        # data = np.sin(np.linspace(0, 2*np.pi, num=500))
        self.dataset.data.data = np.random.random([5, 500])

    def test_instantiate_class(self):
        pass

    def test_has_appropriate_description(self):
        self.assertIn('average', self.processing.description.lower())

    def test_is_undoable(self):
        self.assertTrue(self.processing.undoable)

    def test_with_1D_dataset_raises(self):
        dataset = aspecd.dataset.Dataset()
        dataset.data.data = np.sin(np.linspace(0, 2*np.pi, num=500))
        with self.assertRaises(
                aspecd.exceptions.NotApplicableToDatasetError):
            dataset.process(self.processing)

    def test_without_range_raises(self):
        with self.assertRaises(ValueError):
            self.dataset.process(self.processing)

    def test_with_start_range_outside_axis_range_raises(self):
        self.processing.parameters["range"] = [-6, 3]
        with self.assertRaises(ValueError):
            self.dataset.process(self.processing)

    def test_with_end_range_outside_axis_range_raises(self):
        self.processing.parameters["range"] = \
            [1, self.dataset.data.data.shape[0]+1]
        with self.assertRaises(ValueError):
            self.dataset.process(self.processing)

    def test_average_reduces_data_dimensionality(self):
        self.processing.parameters["range"] = [2, 3]
        self.dataset.process(self.processing)
        self.assertEqual(1, self.dataset.data.data.ndim)

    def test_average_averages_correctly(self):
        self.processing.parameters["range"] = [2, 3]
        data = np.average(self.dataset.data.data[2:3+1, :], axis=0)
        self.dataset.process(self.processing)
        np.testing.assert_allclose(data, self.dataset.data.data)

    def test_average_with_negative_second_value_averages_correctly(self):
        self.processing.parameters["range"] = [2, -1]
        data = np.average(self.dataset.data.data[2:-1, :], axis=0)
        self.dataset.process(self.processing)
        np.testing.assert_allclose(data, self.dataset.data.data)

    def test_average_with_two_negative_values_averages_correctly(self):
        self.processing.parameters["range"] = [-2, -1]
        data = np.average(self.dataset.data.data[-2:-1, :], axis=0)
        self.dataset.process(self.processing)
        np.testing.assert_allclose(data, self.dataset.data.data)

    def test_average_removes_axis(self):
        self.processing.parameters["range"] = [2, 3]
        self.dataset.process(self.processing)
        self.assertEqual(2, len(self.dataset.data.axes))

    def test_average_removes_correct_axis(self):
        self.processing.parameters["range"] = [2, 3]
        self.dataset.data.axes[0].quantity = 'foo'
        self.dataset.data.axes[1].quantity = 'bar'
        self.dataset.data.axes[2].quantity = 'intensity'
        self.dataset.process(self.processing)
        self.assertEqual('bar', self.dataset.data.axes[0].quantity)
        self.assertEqual('intensity', self.dataset.data.axes[-1].quantity)

    def test_average_averages_along_first_axis_by_default(self):
        length = self.dataset.data.data.shape[1]
        self.processing.parameters["range"] = [2, 3]
        self.dataset.process(self.processing)
        self.assertEqual(length, self.dataset.data.data.shape[0])

    def test_average_along_second_axis(self):
        length = self.dataset.data.data.shape[0]
        self.processing.parameters["range"] = [2, 3]
        self.processing.parameters['axis'] = 1
        self.dataset.process(self.processing)
        self.assertEqual(length, self.dataset.data.data.shape[0])

    def test_average_along_second_axis_averages_correctly(self):
        length = self.dataset.data.data.shape[0]
        self.processing.parameters["range"] = [20, 30]
        self.processing.parameters['axis'] = 1
        data = np.average(self.dataset.data.data[:, 20:30+1], axis=1)
        self.dataset.process(self.processing)
        self.assertEqual(length, self.dataset.data.data.shape[0])
        np.testing.assert_allclose(data, self.dataset.data.data)

    def test_along_second_axis_with_end_range_outside_axis_range_raises(self):
        self.processing.parameters['axis'] = 1
        self.processing.parameters["range"] = \
            [1, self.dataset.data.data.shape[1]+1]
        with self.assertRaises(ValueError):
            self.dataset.process(self.processing)

    def test_average_along_non_existing_axis_raises(self):
        with self.assertRaisesRegex(IndexError, "Axis [0-9]+ out of bounds"):
            self.processing.parameters["range"] = [2, 3]
            self.processing.parameters['axis'] = 2
            self.dataset.process(self.processing)

    def test_average_with_wrong_unit_raises(self):
        self.processing.parameters["unit"] = "foo"
        self.processing.parameters["range"] = [2, 3]
        with self.assertRaises(ValueError):
            self.dataset.process(self.processing)

    def test_average_with_axis_units(self):
        self.processing.parameters["unit"] = "axis"
        self.dataset.data.axes[0].values = \
            np.linspace(30, 70, len(self.dataset.data.axes[0].values))
        self.processing.parameters["range"] = [30, 40]
        data = np.average(self.dataset.data.data[0:2, :], axis=0)
        self.dataset.process(self.processing)
        np.testing.assert_allclose(data, self.dataset.data.data)

    def test_unit_is_case_insensitive(self):
        self.processing.parameters["unit"] = "aXis"
        self.dataset.data.axes[0].values = \
            np.linspace(30, 70, len(self.dataset.data.axes[0].values))
        self.processing.parameters["range"] = [30, 40]
        data = np.average(self.dataset.data.data[0:2, :], axis=0)
        self.dataset.process(self.processing)
        np.testing.assert_allclose(data, self.dataset.data.data)

    def test_average_with_axis_units_out_of_range_raises(self):
        self.processing.parameters["unit"] = "axis"
        self.dataset.data.axes[0].values = \
            np.linspace(30, 70, len(self.dataset.data.axes[0].values))
        self.processing.parameters["range"] = [300, 400]
        with self.assertRaises(ValueError):
            self.dataset.process(self.processing)


class TestDatasetAlgebra(unittest.TestCase):
    def setUp(self):
        self.processing = aspecd.processing.DatasetAlgebra()
        self.dataset1 = aspecd.dataset.Dataset()
        self.dataset2 = aspecd.dataset.Dataset()

    def test_instantiate_class(self):
        pass

    def test_has_appropriate_description(self):
        self.assertIn('algebra', self.processing.description.lower())
        self.assertIn('datasets', self.processing.description.lower())

    def test_is_singleprocessing_step(self):
        self.assertTrue(isinstance(self.processing,
                                   aspecd.processing.SingleProcessingStep))

    def test_process_without_parameter_dataset_raises(self):
        with self.assertRaises(aspecd.exceptions.MissingDatasetError):
            self.dataset1.process(self.processing)

    @unittest.skip
    def test_is_not_undoable(self):
        self.assertFalse(self.processing.undoable)

    def test_process_without_kind_raises(self):
        self.processing.parameters["dataset"] = self.dataset2
        with self.assertRaises(ValueError):
            self.dataset1.process(self.processing)

    def test_process_with_wrong_kind_raises(self):
        self.processing.parameters["dataset"] = self.dataset2
        self.processing.parameters["kind"] = 'foo'
        with self.assertRaises(ValueError):
            self.dataset1.process(self.processing)

    def test_process_with_differing_shapes_raises(self):
        self.dataset1.data.data = np.random.random(5)
        self.dataset2.data.data = np.random.random(6)
        self.processing.parameters["dataset"] = self.dataset2
        self.processing.parameters["kind"] = "add"
        with self.assertRaisesRegex(ValueError, "different shapes"):
            self.dataset1.process(self.processing)

    def test_add_with_1d_datasets(self):
        self.dataset1.data.data = np.ones(5)
        self.dataset2.data.data = np.ones(5)
        self.processing.parameters["dataset"] = self.dataset2
        self.processing.parameters["kind"] = "add"
        self.dataset1.process(self.processing)
        self.assertTrue(np.all(self.dataset1.data.data == 2))

    def test_subtract_with_1d_datasets(self):
        self.dataset1.data.data = np.ones(5) * 2
        self.dataset2.data.data = np.ones(5)
        self.processing.parameters["dataset"] = self.dataset2
        self.processing.parameters["kind"] = "subtract"
        self.dataset1.process(self.processing)
        self.assertTrue(np.all(self.dataset1.data.data == 1))

    def test_add_with_2d_datasets(self):
        self.dataset1.data.data = np.ones([5, 5])
        self.dataset2.data.data = np.ones([5, 5])
        self.processing.parameters["dataset"] = self.dataset2
        self.processing.parameters["kind"] = "add"
        self.dataset1.process(self.processing)
        self.assertTrue(np.all(self.dataset1.data.data == 2))

    def test_subtract_with_2d_datasets(self):
        self.dataset1.data.data = np.ones([5, 5]) * 2
        self.dataset2.data.data = np.ones([5, 5])
        self.processing.parameters["dataset"] = self.dataset2
        self.processing.parameters["kind"] = "subtract"
        self.dataset1.process(self.processing)
        self.assertTrue(np.all(self.dataset1.data.data == 1))

    def test_process_replaces_dataset_parameter_with_dataset_id(self):
        self.dataset1.data.data = np.ones(5)
        self.dataset2.data.data = np.ones(5)
        self.dataset2.id = '12345'
        self.processing.parameters["dataset"] = self.dataset2
        self.processing.parameters["kind"] = "add"
        processing = self.dataset1.process(self.processing)
        self.assertEqual(self.dataset2.id,
                         processing.parameters["dataset"])

    def test_process_writes_dataset_id_in_history(self):
        self.dataset1.data.data = np.ones(5)
        self.dataset2.data.data = np.ones(5)
        self.dataset2.id = '12345'
        self.processing.parameters["dataset"] = self.dataset2
        self.processing.parameters["kind"] = "add"
        self.dataset1.process(self.processing)
        self.assertEqual(self.dataset2.id,
                         self.dataset1.history[-1].processing.parameters[
                             "dataset"])


class TestScalarAxisAlgebra(unittest.TestCase):
    def setUp(self):
        self.processing = aspecd.processing.ScalarAxisAlgebra()
        self.dataset = aspecd.dataset.Dataset()

    def test_instantiate_class(self):
        pass

    def test_has_appropriate_description(self):
        self.assertIn('scalar algebra on the axis',
                      self.processing.description.lower())

    def test_is_singleprocessing_step(self):
        self.assertTrue(isinstance(self.processing,
                                   aspecd.processing.SingleProcessingStep))

    def test_is_undoable(self):
        self.assertTrue(self.processing.undoable)

    def test_process_without_kind_raises(self):
        with self.assertRaises(ValueError):
            self.dataset.process(self.processing)

    def test_process_with_wrong_kind_raises(self):
        self.processing.parameters["kind"] = 'foo'
        with self.assertRaises(ValueError):
            self.dataset.process(self.processing)

    def test_add(self):
        self.processing.parameters["kind"] = 'add'
        self.processing.parameters["value"] = 3
        self.dataset.data.data = np.random.random(5)
        self.dataset.data.axes[0].values = np.linspace(0, 5, 5)
        self.dataset.process(self.processing)
        self.assertTrue(np.all(np.linspace(0, 5, 5)+3
                               == self.dataset.data.axes[0].values))

    def test_plus(self):
        self.processing.parameters["kind"] = 'plus'
        self.processing.parameters["value"] = 3
        self.dataset.data.data = np.random.random(5)
        self.dataset.data.axes[0].values = np.linspace(0, 5, 5)
        self.dataset.process(self.processing)
        self.assertTrue(np.all(np.linspace(0, 5, 5)+3
                               == self.dataset.data.axes[0].values))

    def test_add_specified_by_sign(self):
        self.processing.parameters["kind"] = '+'
        self.processing.parameters["value"] = 3
        self.dataset.data.data = np.random.random(5)
        self.dataset.data.axes[0].values = np.linspace(0, 5, 5)
        self.dataset.process(self.processing)
        self.assertTrue(np.all(np.linspace(0, 5, 5)+3
                               == self.dataset.data.axes[0].values))

    def test_add_with_2D_dataset_and_second_axis(self):
        self.processing.parameters["kind"] = 'plus'
        self.processing.parameters["axis"] = 1
        self.processing.parameters["value"] = 3
        self.dataset.data.data = np.random.random([5, 5])
        self.dataset.data.axes[0].values = np.linspace(0, 5, 5)
        self.dataset.data.axes[1].values = np.linspace(0, 5, 5)
        self.dataset.process(self.processing)
        self.assertTrue(np.all(np.linspace(0, 5, 5)
                               == self.dataset.data.axes[0].values))
        self.assertTrue(np.all(np.linspace(0, 5, 5)+3
                               == self.dataset.data.axes[1].values))

    def test_subtract(self):
        self.processing.parameters["kind"] = 'subtract'
        self.processing.parameters["value"] = 3
        self.dataset.data.data = np.random.random(5)
        self.dataset.data.axes[0].values = np.linspace(0, 5, 5)
        self.dataset.process(self.processing)
        self.assertTrue(np.all(np.linspace(0, 5, 5)-3
                               == self.dataset.data.axes[0].values))

    def test_minus(self):
        self.processing.parameters["kind"] = 'minus'
        self.processing.parameters["value"] = 3
        self.dataset.data.data = np.random.random(5)
        self.dataset.data.axes[0].values = np.linspace(0, 5, 5)
        self.dataset.process(self.processing)
        self.assertTrue(np.all(np.linspace(0, 5, 5)-3
                               == self.dataset.data.axes[0].values))

    def test_subtract_specified_by_sign(self):
        self.processing.parameters["kind"] = '-'
        self.processing.parameters["value"] = 3
        self.dataset.data.data = np.random.random(5)
        self.dataset.data.axes[0].values = np.linspace(0, 5, 5)
        self.dataset.process(self.processing)
        self.assertTrue(np.all(np.linspace(0, 5, 5)-3
                               == self.dataset.data.axes[0].values))

    def test_multiply(self):
        self.processing.parameters["kind"] = 'multiply'
        self.processing.parameters["value"] = 3
        self.dataset.data.data = np.random.random(5)
        self.dataset.data.axes[0].values = np.linspace(0, 5, 5)
        self.dataset.process(self.processing)
        self.assertTrue(np.all(np.linspace(0, 5, 5)*3
                               == self.dataset.data.axes[0].values))

    def test_times(self):
        self.processing.parameters["kind"] = 'times'
        self.processing.parameters["value"] = 3
        self.dataset.data.data = np.random.random(5)
        self.dataset.data.axes[0].values = np.linspace(0, 5, 5)
        self.dataset.process(self.processing)
        self.assertTrue(np.all(np.linspace(0, 5, 5)*3
                               == self.dataset.data.axes[0].values))

    def test_multiply_specified_by_sign(self):
        self.processing.parameters["kind"] = '*'
        self.processing.parameters["value"] = 3
        self.dataset.data.data = np.random.random(5)
        self.dataset.data.axes[0].values = np.linspace(0, 5, 5)
        self.dataset.process(self.processing)
        self.assertTrue(np.all(np.linspace(0, 5, 5)*3
                               == self.dataset.data.axes[0].values))

    def test_divide(self):
        self.processing.parameters["kind"] = 'divide'
        self.processing.parameters["value"] = 3
        self.dataset.data.data = np.random.random(5)
        self.dataset.data.axes[0].values = np.linspace(0, 5, 5)
        self.dataset.process(self.processing)
        self.assertTrue(np.all(np.linspace(0, 5, 5)/3
                               == self.dataset.data.axes[0].values))

    def test_by(self):
        self.processing.parameters["kind"] = 'by'
        self.processing.parameters["value"] = 3
        self.dataset.data.data = np.random.random(5)
        self.dataset.data.axes[0].values = np.linspace(0, 5, 5)
        self.dataset.process(self.processing)
        self.assertTrue(np.all(np.linspace(0, 5, 5)/3
                               == self.dataset.data.axes[0].values))

    def test_divide_specified_by_sign(self):
        self.processing.parameters["kind"] = '/'
        self.processing.parameters["value"] = 3
        self.dataset.data.data = np.random.random(5)
        self.dataset.data.axes[0].values = np.linspace(0, 5, 5)
        self.dataset.process(self.processing)
        self.assertTrue(np.all(np.linspace(0, 5, 5)/3
                               == self.dataset.data.axes[0].values))

    def test_power(self):
        self.processing.parameters["kind"] = 'power'
        self.processing.parameters["value"] = 3
        self.dataset.data.data = np.random.random(5)
        self.dataset.data.axes[0].values = np.linspace(0, 5, 5)
        self.dataset.process(self.processing)
        self.assertTrue(np.all(np.linspace(0, 5, 5)**3
                               == self.dataset.data.axes[0].values))

    def test_pow(self):
        self.processing.parameters["kind"] = 'pow'
        self.processing.parameters["value"] = 3
        self.dataset.data.data = np.random.random(5)
        self.dataset.data.axes[0].values = np.linspace(0, 5, 5)
        self.dataset.process(self.processing)
        self.assertTrue(np.all(np.linspace(0, 5, 5)**3
                               == self.dataset.data.axes[0].values))

    def test_power_specified_by_sign(self):
        self.processing.parameters["kind"] = '**'
        self.processing.parameters["value"] = 3
        self.dataset.data.data = np.random.random(5)
        self.dataset.data.axes[0].values = np.linspace(0, 5, 5)
        self.dataset.process(self.processing)
        self.assertTrue(np.all(np.linspace(0, 5, 5)**3
                               == self.dataset.data.axes[0].values))


class TestExtractCommonRange(unittest.TestCase):
    def setUp(self):
        self.processing = aspecd.processing.ExtractCommonRange()
        self.dataset1 = aspecd.dataset.Dataset()
        self.dataset2 = aspecd.dataset.Dataset()

    def test_instantiate_class(self):
        pass

    def test_has_appropriate_description(self):
        self.assertIn('common data range', self.processing.description.lower())

    def test_is_multiprocessing_step(self):
        self.assertTrue(isinstance(self.processing,
                                   aspecd.processing.MultiProcessingStep))

    def test_is_undoable(self):
        self.assertTrue(self.processing.undoable)

    def test_with_only_one_dataset_raises(self):
        self.processing.datasets.append(self.dataset1)
        with self.assertRaisesRegex(IndexError, "Need more than one dataset"):
            self.processing.process()

    def test_with_datasets_with_more_than_2d_raises(self):
        self.dataset1.data.data = np.random.random([10, 10, 10])
        self.dataset2.data.data = np.random.random([10, 10, 10])
        self.processing.datasets.append(self.dataset1)
        self.processing.datasets.append(self.dataset2)
        with self.assertRaises(aspecd.exceptions.NotApplicableToDatasetError):
            self.processing.process()

    def test_process_with_datasets_with_different_dimensions_raises(self):
        self.dataset1.data.data = np.random.random(10)
        self.dataset2.data.data = np.random.random([10, 10])
        self.processing.datasets.append(self.dataset1)
        self.processing.datasets.append(self.dataset2)
        with self.assertRaisesRegex(ValueError, "different dimensions"):
            self.processing.process()

    def test_process_1D_datasets_with_disjoint_axes_values_raises(self):
        self.dataset1.data.data = np.random.random(10)
        self.dataset1.data.axes[0].values = np.linspace(0, 5, 10)
        self.dataset2.data.data = np.random.random(15)
        self.dataset2.data.axes[0].values = np.linspace(10, 15, 15)
        self.processing.datasets.append(self.dataset1)
        self.processing.datasets.append(self.dataset2)
        with self.assertRaisesRegex(ValueError, "disjoint axes values"):
            self.processing.process()

    def test_process_2D_datasets_with_disjoint_axes_values_raises(self):
        self.dataset1.data.data = np.random.random([10, 10])
        self.dataset1.data.axes[0].values = np.linspace(0, 5, 10)
        self.dataset1.data.axes[1].values = np.linspace(0, 5, 10)
        self.dataset2.data.data = np.random.random([15, 15])
        self.dataset2.data.axes[0].values = np.linspace(0, 5, 15)
        self.dataset2.data.axes[1].values = np.linspace(10, 15, 15)
        self.processing.datasets.append(self.dataset1)
        self.processing.datasets.append(self.dataset2)
        with self.assertRaisesRegex(ValueError, "disjoint axes values"):
            self.processing.process()

    def test_process_datasets_with_different_axes_units_raises(self):
        self.dataset1.data.data = np.random.random([10, 10])
        self.dataset1.data.axes[0].values = np.linspace(0, 5, 10)
        self.dataset1.data.axes[1].values = np.linspace(0, 5, 10)
        self.dataset1.data.axes[0].unit = 'foo'
        self.dataset1.data.axes[1].unit = 'bar'
        self.dataset2.data.data = np.random.random([10, 10])
        self.dataset2.data.axes[0].values = np.linspace(0, 5, 10)
        self.dataset2.data.axes[1].values = np.linspace(0, 5, 10)
        self.dataset2.data.axes[0].unit = 'foobar'
        self.dataset2.data.axes[1].unit = 'bar'
        self.processing.datasets.append(self.dataset1)
        self.processing.datasets.append(self.dataset2)
        with self.assertRaisesRegex(ValueError, "different units"):
            self.processing.process()

    def test_process_ignores_different_axes_units_if_told_so(self):
        self.dataset1.data.data = np.random.random([10, 10])
        self.dataset1.data.axes[0].values = np.linspace(0, 5, 10)
        self.dataset1.data.axes[1].values = np.linspace(0, 5, 10)
        self.dataset1.data.axes[0].unit = 'foo'
        self.dataset1.data.axes[1].unit = 'bar'
        self.dataset2.data.data = np.random.random([10, 10])
        self.dataset2.data.axes[0].values = np.linspace(0, 5, 10)
        self.dataset2.data.axes[1].values = np.linspace(0, 5, 10)
        self.dataset2.data.axes[0].unit = 'foobar'
        self.dataset2.data.axes[1].unit = 'bar'
        self.processing.datasets.append(self.dataset1)
        self.processing.datasets.append(self.dataset2)
        self.processing.parameters["ignore_units"] = True
        self.processing.process()

    def test_process_sets_common_range_for_1d_datasets(self):
        self.dataset1.data.data = np.random.random([10])
        self.dataset1.data.axes[0].values = np.linspace(0, 5, 10)
        self.dataset2.data.data = np.random.random([10])
        self.dataset2.data.axes[0].values = np.linspace(1, 4, 10)
        self.processing.datasets.append(self.dataset1)
        self.processing.datasets.append(self.dataset2)
        self.processing.process()
        self.assertListEqual(self.processing.parameters["common_range"],
                             [[1., 4.]])

    def test_process_sets_common_range_for_2d_datasets(self):
        self.dataset1.data.data = np.random.random([10, 10])
        self.dataset1.data.axes[0].values = np.linspace(0, 5, 10)
        self.dataset1.data.axes[1].values = np.linspace(10, 15, 10)
        self.dataset2.data.data = np.random.random([10, 10])
        self.dataset2.data.axes[0].values = np.linspace(1, 4, 10)
        self.dataset2.data.axes[1].values = np.linspace(11, 14, 10)
        self.processing.datasets.append(self.dataset1)
        self.processing.datasets.append(self.dataset2)
        self.processing.process()
        self.assertListEqual(self.processing.parameters["common_range"],
                             [[1., 4.], [11., 14.]])

    def test_process_sets_npoints_for_1d_datasets(self):
        self.dataset1.data.data = np.random.random([11])
        self.dataset1.data.axes[0].values = np.linspace(0, 5, 11)
        self.dataset2.data.data = np.random.random([11])
        self.dataset2.data.axes[0].values = np.linspace(1, 4, 11)
        self.processing.datasets.append(self.dataset1)
        self.processing.datasets.append(self.dataset2)
        self.processing.process()
        self.assertEqual([7], self.processing.parameters["npoints"])

    def test_process_sets_npoints_for_2d_datasets(self):
        self.dataset1.data.data = np.random.random([11, 11])
        self.dataset1.data.axes[0].values = np.linspace(0, 5, 11)
        self.dataset1.data.axes[1].values = np.linspace(10, 15, 11)
        self.dataset2.data.data = np.random.random([11, 11])
        self.dataset2.data.axes[0].values = np.linspace(1, 4, 11)
        self.dataset2.data.axes[1].values = np.linspace(11, 14, 11)
        self.processing.datasets.append(self.dataset1)
        self.processing.datasets.append(self.dataset2)
        self.processing.process()
        self.assertEqual([7, 7], self.processing.parameters["npoints"])

    def test_process_interpolates_axes_for_1d_datasets(self):
        self.dataset1.data.data = np.linspace(10, 15, 11)
        self.dataset1.data.axes[0].values = np.linspace(0, 5, 11)
        self.dataset2.data.data = np.linspace(11, 14, 11)
        self.dataset2.data.axes[0].values = np.linspace(1, 4, 11)
        self.processing.datasets.append(self.dataset1)
        self.processing.datasets.append(self.dataset2)
        self.processing.process()
        self.assertListEqual(list(np.linspace(1, 4, 7)),
                             list(self.dataset1.data.axes[0].values))
        self.assertListEqual(list(np.linspace(1, 4, 7)),
                             list(self.dataset2.data.axes[0].values))

    def test_process_interpolates_data_for_1d_datasets(self):
        self.dataset1.data.data = np.linspace(10, 15, 11)
        self.dataset1.data.axes[0].values = np.linspace(0, 5, 11)
        self.dataset2.data.data = np.linspace(11, 14, 11)
        self.dataset2.data.axes[0].values = np.linspace(1, 4, 11)
        self.processing.datasets.append(self.dataset1)
        self.processing.datasets.append(self.dataset2)
        self.processing.process()
        self.assertListEqual(list(np.linspace(11, 14, 7)),
                             list(self.dataset1.data.data))
        self.assertListEqual(list(np.linspace(11, 14, 7)),
                             list(self.dataset2.data.data))

    def test_process_interpolates_data_for_2d_datasets(self):
        axis0 = np.linspace(0,5,11)
        axis1 = np.linspace(0,5,11)
        rows, cols = np.meshgrid(axis0, axis1, indexing='ij')
        self.dataset1.data.data = np.sin(rows**2+cols**2)
        self.dataset1.data.axes[0].values = axis0
        self.dataset1.data.axes[1].values = axis1
        axis0 = np.linspace(2,4,5)
        axis1 = np.linspace(2,4,5)
        rows, cols = np.meshgrid(axis0, axis1, indexing='ij')
        self.dataset2.data.data = np.sin(rows**2+cols**2)
        self.dataset2.data.axes[0].values = axis0
        self.dataset2.data.axes[1].values = axis1
        self.processing.datasets.append(self.dataset1)
        self.processing.datasets.append(self.dataset2)
        self.processing.process()
        self.assertTrue(np.all(self.dataset2.data.data
                               == self.dataset1.data.data))
