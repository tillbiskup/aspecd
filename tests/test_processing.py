"""Tests for processing."""
import copy
import unittest

import numpy as np
import scipy.ndimage
import scipy.signal

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
        self.assertTrue(hasattr(self.processing, "undoable"))

    def test_has_name_property(self):
        self.assertTrue(hasattr(self.processing, "name"))

    def test_name_property_equals_full_class_name(self):
        full_class_name = aspecd.utils.full_class_name(self.processing)
        self.assertEqual(self.processing.name, full_class_name)

    def test_has_parameters_property(self):
        self.assertTrue(hasattr(self.processing, "parameters"))

    def test_parameters_property_is_dict(self):
        self.assertTrue(isinstance(self.processing.parameters, dict))

    def test_has_info_property(self):
        self.assertTrue(hasattr(self.processing, "info"))

    def test_info_property_is_dict(self):
        self.assertTrue(isinstance(self.processing.info, dict))

    def test_has_description_property(self):
        self.assertTrue(hasattr(self.processing, "description"))

    def test_description_property_is_sensible(self):
        self.assertIn(self.processing.description, "Abstract processing step")

    def test_has_comment_property(self):
        self.assertTrue(hasattr(self.processing, "comment"))

    def test_description_comment_is_string(self):
        self.assertTrue(isinstance(self.processing.comment, str))

    def test_has_references_property(self):
        self.assertTrue(hasattr(self.processing, "references"))

    def test_description_references_is_list(self):
        self.assertTrue(isinstance(self.processing.references, list))

    def test_has_process_method(self):
        self.assertTrue(hasattr(self.processing, "process"))
        self.assertTrue(callable(self.processing.process))

    def test_has_to_dict_method(self):
        self.assertTrue(hasattr(self.processing, "to_dict"))
        self.assertTrue(callable(self.processing.to_dict))

    def test_to_dict_does_not_contain_certain_keys(self):
        for key in ["undoable", "name", "description", "references"]:
            with self.subTest(key=key):
                self.assertNotIn(key, self.processing.to_dict())


class TestSingleProcessingStep(unittest.TestCase):
    def setUp(self):
        self.processing = aspecd.processing.SingleProcessingStep()

    def test_instantiate_class(self):
        pass

    def test_is_processingstep(self):
        self.assertTrue(
            isinstance(self.processing, aspecd.processing.ProcessingStep)
        )

    def test_description_property_is_sensible(self):
        self.assertIn(
            self.processing.description, "Abstract singleprocessing step"
        )

    def test_to_dict_does_not_contain_certain_keys(self):
        for key in ["dataset"]:
            with self.subTest(key=key):
                self.assertNotIn(key, self.processing.to_dict())

    def test_to_dict_keeps_dataset_key_in_subdict(self):
        self.processing.parameters["dataset"] = "foo"
        self.assertIn("dataset", self.processing.to_dict()["parameters"])

    def test_process_checks_applicability(self):
        class MyProcessingStep(aspecd.processing.SingleProcessingStep):
            @staticmethod
            def applicable(dataset):
                return False

        dataset = aspecd.dataset.Dataset()
        processing = MyProcessingStep()
        with self.assertRaises(aspecd.exceptions.NotApplicableToDatasetError):
            dataset.process(processing)

    def test_process_checks_applicability_prints_helpful_message(self):
        class MyProcessingStep(aspecd.processing.SingleProcessingStep):
            @staticmethod
            def applicable(dataset):
                return False

        dataset = aspecd.dataset.Dataset()
        dataset.id = "foo"
        processing = MyProcessingStep()
        message = "MyProcessingStep not applicable to dataset with id foo"
        with self.assertRaisesRegex(
            aspecd.exceptions.NotApplicableToDatasetError, message
        ):
            dataset.process(processing)

    def test_process_sets_default_parameters(self):
        class MyProcessingStep(aspecd.processing.SingleProcessingStep):
            def __init__(self):
                super().__init__()
                self.parameters["test"] = None

            def _set_defaults(self):
                if not self.parameters["test"]:
                    self.parameters["test"] = "It works!"

        dataset = aspecd.dataset.Dataset()
        processing = MyProcessingStep()
        processing = dataset.process(processing)
        self.assertEqual("It works!", processing.parameters["test"])

    def test_process_sets_default_parameters_before_sanitising(self):
        class MyProcessingStep(aspecd.processing.SingleProcessingStep):
            def __init__(self):
                super().__init__()
                self.parameters["test"] = None

            def _set_defaults(self):
                if not self.parameters["test"]:
                    self.parameters["test"] = "It works!"

            def _sanitise_parameters(self):
                if not self.parameters["test"]:
                    raise ValueError("No parameter test")

        dataset = aspecd.dataset.Dataset()
        processing = MyProcessingStep()
        processing = dataset.process(processing)
        self.assertEqual("It works!", processing.parameters["test"])

    def test_process_sanitises_parameters(self):
        class MyProcessingStep(aspecd.processing.SingleProcessingStep):
            def __init__(self):
                super().__init__()
                self.parameters["test"] = None

            def _sanitise_parameters(self):
                if not self.parameters["test"]:
                    raise ValueError("No parameter test")

        dataset = aspecd.dataset.Dataset()
        processing = MyProcessingStep()
        with self.assertRaisesRegex(ValueError, "No parameter test"):
            dataset.process(processing)

    def test_process_performs_task(self):
        class MyProcessingStep(aspecd.processing.SingleProcessingStep):
            def __init__(self):
                super().__init__()
                self.parameters["test"] = None

            def _perform_task(self):
                self.parameters["test"] = "It works!"

        dataset = aspecd.dataset.Dataset()
        processing = MyProcessingStep()
        processing = dataset.process(processing)
        self.assertEqual("It works!", processing.parameters["test"])

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
        self.assertTrue(
            isinstance(processing_step.dataset, aspecd.dataset.Dataset)
        )

    def test_process_with_dataset_writes_history(self):
        test_dataset = self.processing.process(
            dataset=aspecd.dataset.Dataset()
        )
        self.assertGreater(len(test_dataset.history), 0)

    def test_process_with_dataset_using_dataset_process_writes_history(self):
        test_dataset = aspecd.dataset.Dataset()
        test_dataset.process(self.processing)
        self.assertGreater(len(test_dataset.history), 0)

    def test_process_returns_dataset(self):
        test_dataset = self.processing.process(aspecd.dataset.Dataset())
        self.assertTrue(isinstance(test_dataset, aspecd.dataset.Dataset))

    def test_has_create_history_record_method(self):
        self.assertTrue(hasattr(self.processing, "create_history_record"))
        self.assertTrue(callable(self.processing.create_history_record))

    def test_create_history_record_returns_history_record(self):
        self.processing.dataset = aspecd.dataset.Dataset()
        history_record = self.processing.create_history_record()
        self.assertTrue(
            isinstance(history_record, aspecd.history.ProcessingHistoryRecord)
        )


class TestMultiProcessingStep(unittest.TestCase):
    def setUp(self):
        self.processing = aspecd.processing.MultiProcessingStep()

    def test_instantiate_class(self):
        pass

    def test_is_processingstep(self):
        self.assertTrue(
            isinstance(self.processing, aspecd.processing.ProcessingStep)
        )

    def test_description_property_is_sensible(self):
        self.assertIn(
            self.processing.description, "Abstract multiprocessing step"
        )

    def test_to_dict_does_not_contain_certain_keys(self):
        for key in ["datasets"]:
            with self.subTest(key=key):
                self.assertNotIn(key, self.processing.to_dict())

    def test_has_datasets_property(self):
        self.assertTrue(hasattr(self.processing, "datasets"))

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

    def test_process_checks_applicability_prints_helpful_message(self):
        dataset1 = aspecd.dataset.Dataset()
        dataset1.data.data = np.random.random([5, 5])
        dataset1.id = "foo"
        dataset2 = aspecd.dataset.Dataset()
        dataset2.data.data = np.random.random(5)
        dataset2.id = "bar"

        class MyProcessingStep(aspecd.processing.MultiProcessingStep):
            @staticmethod
            def applicable(dataset):
                return len(dataset.data.axes) == 2

        processing_step = MyProcessingStep()
        processing_step.datasets.append(dataset1)
        processing_step.datasets.append(dataset2)
        message = "MyProcessingStep not applicable to dataset with id foo"
        with self.assertRaisesRegex(
            aspecd.exceptions.NotApplicableToDatasetError, message
        ):
            processing_step.process()

    def test_process_with_datasets_appends_history_record(self):
        dataset1 = aspecd.dataset.Dataset()
        dataset2 = aspecd.dataset.Dataset()
        self.processing.datasets.append(dataset1)
        self.processing.datasets.append(dataset2)
        self.processing.process()
        self.assertTrue(dataset1.history)
        self.assertTrue(dataset2.history)

    def test_process_with_datasets_increments_history_pointer(self):
        dataset1 = aspecd.dataset.Dataset()
        dataset2 = aspecd.dataset.Dataset()
        self.processing.datasets.append(dataset1)
        self.processing.datasets.append(dataset2)
        self.processing.process()
        self.assertEqual(len(dataset1.history) - 1, dataset1._history_pointer)
        self.assertEqual(len(dataset2.history) - 1, dataset2._history_pointer)


class TestNormalisation(unittest.TestCase):
    def setUp(self):
        self.processing = aspecd.processing.Normalisation()
        self.dataset = aspecd.dataset.Dataset()
        self.dataset.data.data = (
            np.sin(np.linspace(0, 3 * np.pi, num=500)) * 2
        )

    def test_instantiate_class(self):
        pass

    def test_has_appropriate_description(self):
        self.assertIn("normalise", self.processing.description.lower())

    def test_is_undoable(self):
        self.assertTrue(self.processing.undoable)

    def test_with_unknown_kind_raises(self):
        self.processing.parameters["kind"] = "foo"
        with self.assertRaisesRegex(ValueError, "not recognised"):
            self.dataset.process(self.processing)

    def test_normalise_to_maximum(self):
        self.processing.parameters["kind"] = "maximum"
        self.dataset.process(self.processing)
        self.assertEqual(1, self.dataset.data.data.max())

    def test_normalise_to_minimum(self):
        # Asymmetric data with maximum < minimum
        self.dataset.data.data = (
            np.sin(np.linspace(0.6 * np.pi, 2.4 * np.pi, num=500)) * 2
        )
        self.processing.parameters["kind"] = "minimum"
        self.dataset.process(self.processing)
        self.assertAlmostEqual(-1, self.dataset.data.data.min(), 4)

    def test_normalise_to_amplitude(self):
        self.processing.parameters["kind"] = "amplitude"
        self.dataset.process(self.processing)
        self.assertAlmostEqual(
            1, self.dataset.data.data.max() - self.dataset.data.data.min(), 4
        )

    def test_normalise_to_area(self):
        self.processing.parameters["kind"] = "area"
        self.dataset.process(self.processing)
        dataset2 = aspecd.dataset.Dataset()
        dataset2.data.data = np.sin(np.linspace(0, 3 * np.pi, num=200)) * 2
        dataset2.process(self.processing)
        # noinspection PyTypeChecker
        self.assertAlmostEqual(1, np.sum(np.abs(self.dataset.data.data)), 4)
        self.assertAlmostEqual(1, np.sum(np.abs(dataset2.data.data)), 4)

        self.assertAlmostEqual(
            abs(self.dataset.data.data).max(),
            abs(dataset2.data.data.max()),
            2,
        )

    def test_normalise_to_with_different_number_of_points(self):
        self.processing.parameters["kind"] = "area"
        self.dataset.process(self.processing)
        # noinspection PyTypeChecker
        self.assertAlmostEqual(1, np.sum(np.abs(self.dataset.data.data)), 4)

    def test_normalise_to_maximum_2d(self):
        self.processing.parameters["kind"] = "maximum"
        self.dataset.data.data = np.random.random([10, 10])
        self.dataset.process(self.processing)
        self.assertEqual(1, self.dataset.data.data.max())

    def test_normalise_to_minimum_2d(self):
        self.processing.parameters["kind"] = "minimum"
        self.dataset.data.data = np.random.random([10, 10])
        self.dataset.process(self.processing)
        self.assertEqual(1, self.dataset.data.data.min())

    def test_normalise_to_amplitude_2d(self):
        self.processing.parameters["kind"] = "amplitude"
        self.dataset.data.data = np.random.random([10, 10])
        self.dataset.process(self.processing)
        self.assertAlmostEqual(
            1, self.dataset.data.data.max() - self.dataset.data.data.min(), 4
        )

    def test_normalise_to_area_2d(self):
        self.processing.parameters["kind"] = "area"
        self.dataset.data.data = np.random.random([10, 10])
        self.dataset.process(self.processing)
        # noinspection PyTypeChecker
        self.assertAlmostEqual(1, np.sum(np.abs(self.dataset.data.data)), 4)

    def test_normalise_to_maximum_with_noisy_data(self):
        self.dataset.data.data = np.concatenate(
            (np.zeros(50), self.dataset.data.data, np.zeros(50))
        )
        self.dataset.data.data += (
            np.random.random(len(self.dataset.data.data)) - 0.5
        ) * 0.5
        self.processing.parameters["kind"] = "maximum"
        self.processing.parameters["noise_range"] = [0, 10]
        self.dataset.process(self.processing)
        self.assertGreaterEqual(1.25, self.dataset.data.data.max(), 1)

    def test_normalise_to_minimum_with_noisy_data(self):
        self.dataset.data.data = np.concatenate(
            (np.zeros(50), self.dataset.data.data, np.zeros(50))
        )
        self.dataset.data.data += (
            np.random.random(len(self.dataset.data.data)) - 0.5
        ) * 0.5
        self.processing.parameters["kind"] = "minimum"
        self.processing.parameters["noise_range"] = [0, 10]
        self.dataset.process(self.processing)
        self.assertLessEqual(-1.25, self.dataset.data.data.min(), 1)

    def test_normalise_to_amplitude_with_noisy_data(self):
        self.dataset.data.data = np.concatenate(
            (np.zeros(50), self.dataset.data.data, np.zeros(50))
        )
        self.dataset.data.data += (
            np.random.random(len(self.dataset.data.data)) - 0.5
        ) * 0.5
        self.processing.parameters["kind"] = "amplitude"
        self.processing.parameters["noise_range"] = [0, 10]
        self.dataset.process(self.processing)
        self.assertGreaterEqual(
            1.25, self.dataset.data.data.max() - self.dataset.data.data.min()
        )

    def test_normalise_to_maximum_with_noisy_2d_data(self):
        # sometimes fails but not always
        data = np.concatenate(
            (np.zeros(50), self.dataset.data.data, np.zeros(50))
        )
        self.dataset.data.data = np.reshape(np.tile(data, 100), (100, 600))
        self.dataset.data.data += (
            np.random.random(self.dataset.data.data.shape) - 0.5
        ) * 0.5
        self.processing.parameters["kind"] = "maximum"
        self.processing.parameters["noise_range"] = [[0, 10], [0, 10]]
        self.dataset.process(self.processing)
        self.assertGreaterEqual(1.26, self.dataset.data.data.max(), 1)

    def test_normalise_to_maximum_with_noisy_2d_data_and_axis_units(self):
        data = np.concatenate(
            (np.zeros(50), self.dataset.data.data, np.zeros(50))
        )
        self.dataset.data.data = np.reshape(np.tile(data, 100), (100, 600))
        self.dataset.data.data += (
            np.random.random(self.dataset.data.data.shape) - 0.5
        ) * 0.5
        self.dataset.data.axes[0].values = np.linspace(21, 42, 100)
        self.dataset.data.axes[1].values = np.linspace(340, 350, 600)
        self.processing.parameters["kind"] = "maximum"
        self.processing.parameters["noise_range"] = [[21, 25], [340, 341]]
        self.processing.parameters["noise_range_unit"] = "axis"
        self.dataset.process(self.processing)
        self.assertGreaterEqual(1.25, self.dataset.data.data.max(), 1)

    def test_normalise_to_maximum_over_range(self):
        self.dataset.data.data = np.append(
            self.dataset.data.data, self.dataset.data.data * 0.5
        )
        self.processing.parameters["kind"] = "maximum"
        self.processing.parameters["range"] = [501, 1000]
        self.dataset.process(self.processing)
        self.assertEqual(2.0, self.dataset.data.data.max())

    def test_normalise_to_maximum_over_range_with_axis_units(self):
        self.dataset.data.data = np.append(
            self.dataset.data.data, self.dataset.data.data * 0.5
        )
        self.dataset.data.axes[0].values = np.linspace(0, 6 * np.pi, 1000)
        self.processing.parameters["kind"] = "maximum"
        self.processing.parameters["range"] = [3 * np.pi, 6 * np.pi]
        self.processing.parameters["range_unit"] = "axis"
        self.dataset.process(self.processing)
        self.assertEqual(2.0, self.dataset.data.data.max())

    def test_normalise_to_maximum_2d_with_range(self):
        self.processing.parameters["kind"] = "maximum"
        self.processing.parameters["range"] = [[50, 150], [50, 150]]
        self.dataset.data.data = np.random.random([200, 200])
        self.dataset.data.data[50:150, 50:150] *= 0.5
        self.dataset.process(self.processing)
        self.assertAlmostEqual(2, self.dataset.data.data.max(), 2)

    def test_normalise_removes_unit_of_last_axis(self):
        self.dataset.data.axes[-1].unit = "mV"
        for kind in ["min", "max", "amp", "area"]:
            with self.subTest(kind=kind):
                self.processing.parameters["kind"] = kind
                self.dataset.process(self.processing)
                self.assertEqual("", self.dataset.data.axes[-1].unit)


class TestIntegration(unittest.TestCase):
    def setUp(self):
        self.processing = aspecd.processing.Integration()
        self.dataset = aspecd.dataset.Dataset()
        self.dataset.data.data = np.sin(np.linspace(0, 2 * np.pi, num=500))

    def test_instantiate_class(self):
        pass

    def test_has_appropriate_description(self):
        self.assertIn("integrate", self.processing.description.lower())

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
        xdata = np.linspace(0, 2 * np.pi, num=500)
        self.dataset.data.data = np.sin(xdata) * np.sin(xdata)

    def test_instantiate_class(self):
        pass

    def test_has_appropriate_description(self):
        self.assertIn("differentiate", self.processing.description.lower())

    def test_is_undoable(self):
        self.assertTrue(self.processing.undoable)

    def test_differentiate_returns_symmetric_spectrum(self):
        self.dataset.process(self.processing)
        self.assertAlmostEqual(
            -np.min(self.dataset.data.data), np.max(self.dataset.data.data)
        )

    def test_differentiate_returns_spectrum_of_same_length_as_original(self):
        original_data = self.dataset.data.data
        self.dataset.process(self.processing)
        self.assertEqual(len(original_data), len(self.dataset.data.data))

    def test_integrate_2D_dataset(self):
        self.dataset.data.data = np.tile(self.dataset.data.data, (5, 1))
        self.dataset.process(self.processing)
        self.assertAlmostEqual(
            -np.min(self.dataset.data.data), np.max(self.dataset.data.data)
        )

    def test_differentiate_2D_dataset_retains_shape(self):
        self.dataset.data.data = np.tile(self.dataset.data.data, (5, 1))
        original_data = self.dataset.data.data
        self.dataset.process(self.processing)
        self.assertEqual(
            np.shape(original_data), np.shape(self.dataset.data.data)
        )


class TestScalarAlgebra(unittest.TestCase):
    def setUp(self):
        self.processing = aspecd.processing.ScalarAlgebra()
        self.dataset = aspecd.dataset.Dataset()
        self.dataset.data.data = np.sin(np.linspace(0, 2 * np.pi, num=500))

    def test_instantiate_class(self):
        pass

    def test_has_appropriate_description(self):
        self.assertIn("algebra", self.processing.description.lower())

    def test_is_undoable(self):
        self.assertTrue(self.processing.undoable)

    def test_without_kind_raises(self):
        with self.assertRaises(ValueError):
            self.dataset.process(self.processing)

    def test_with_wrong_kind_raises(self):
        self.processing.parameters["kind"] = "foo"
        with self.assertRaises(ValueError):
            self.dataset.process(self.processing)

    def test_add(self):
        self.processing.parameters["kind"] = "plus"
        self.processing.parameters["value"] = 3
        self.dataset.process(self.processing)
        self.assertAlmostEqual(4, self.dataset.data.data.max(), 5)

    def test_add_with_2D_dataset(self):
        self.dataset.data.data = np.tile(self.dataset.data.data, (5, 1))
        self.processing.parameters["kind"] = "plus"
        self.processing.parameters["value"] = 3
        self.dataset.process(self.processing)
        self.assertAlmostEqual(4, self.dataset.data.data.max(), 5)

    def test_add_using_capitalised_name(self):
        self.processing.parameters["kind"] = "Plus"
        self.processing.parameters["value"] = 3
        self.dataset.process(self.processing)
        self.assertAlmostEqual(4, self.dataset.data.data.max(), 5)

    def test_add_using_alternative_name(self):
        self.processing.parameters["kind"] = "add"
        self.processing.parameters["value"] = 3
        self.dataset.process(self.processing)
        self.assertAlmostEqual(4, self.dataset.data.data.max(), 5)

    def test_add_using_symbol(self):
        self.processing.parameters["kind"] = "+"
        self.processing.parameters["value"] = 3
        self.dataset.process(self.processing)
        self.assertAlmostEqual(4, self.dataset.data.data.max(), 5)

    def test_subtract(self):
        self.processing.parameters["kind"] = "minus"
        self.processing.parameters["value"] = 3
        self.dataset.process(self.processing)
        self.assertAlmostEqual(-2, self.dataset.data.data.max(), 5)

    def test_subtract_using_alternative_name(self):
        self.processing.parameters["kind"] = "subtract"
        self.processing.parameters["value"] = 3
        self.dataset.process(self.processing)
        self.assertAlmostEqual(-2, self.dataset.data.data.max(), 5)

    def test_subtract_with_symbol(self):
        self.processing.parameters["kind"] = "-"
        self.processing.parameters["value"] = 3
        self.dataset.process(self.processing)
        self.assertAlmostEqual(-2, self.dataset.data.data.max(), 5)

    def test_multiply(self):
        self.processing.parameters["kind"] = "times"
        self.processing.parameters["value"] = 3
        self.dataset.process(self.processing)
        self.assertAlmostEqual(3, self.dataset.data.data.max(), 4)

    def test_multiply_with_alternative_name(self):
        self.processing.parameters["kind"] = "multiply"
        self.processing.parameters["value"] = 3
        self.dataset.process(self.processing)
        self.assertAlmostEqual(3, self.dataset.data.data.max(), 4)

    def test_multiply_with_symbol(self):
        self.processing.parameters["kind"] = "*"
        self.processing.parameters["value"] = 3
        self.dataset.process(self.processing)
        self.assertAlmostEqual(3, self.dataset.data.data.max(), 4)

    def test_divide(self):
        self.processing.parameters["kind"] = "by"
        self.processing.parameters["value"] = 2
        self.dataset.process(self.processing)
        self.assertAlmostEqual(0.5, self.dataset.data.data.max(), 5)

    def test_divide_with_alternative_name(self):
        self.processing.parameters["kind"] = "divide"
        self.processing.parameters["value"] = 2
        self.dataset.process(self.processing)
        self.assertAlmostEqual(0.5, self.dataset.data.data.max(), 5)

    def test_divide_with_symbol(self):
        self.processing.parameters["kind"] = "/"
        self.processing.parameters["value"] = 2
        self.dataset.process(self.processing)
        self.assertAlmostEqual(0.5, self.dataset.data.data.max(), 5)


class TestProjection(unittest.TestCase):
    def setUp(self):
        self.processing = aspecd.processing.Projection()
        self.dataset = aspecd.dataset.Dataset()
        data = np.sin(np.linspace(0, 2 * np.pi, num=500))
        self.dataset.data.data = np.tile(data, (5, 1))

    def test_instantiate_class(self):
        pass

    def test_has_appropriate_description(self):
        self.assertIn("project", self.processing.description.lower())

    def test_is_undoable(self):
        self.assertTrue(self.processing.undoable)

    def test_with_1D_dataset_raises(self):
        dataset = aspecd.dataset.Dataset()
        dataset.data.data = np.sin(np.linspace(0, 2 * np.pi, num=500))
        with self.assertRaises(aspecd.exceptions.NotApplicableToDatasetError):
            dataset.process(self.processing)

    def test_project_reduces_data_dimensionality(self):
        self.dataset.process(self.processing)
        self.assertEqual(1, self.dataset.data.data.ndim)

    def test_project_removes_axis(self):
        self.dataset.process(self.processing)
        self.assertEqual(2, len(self.dataset.data.axes))

    def test_project_removes_correct_axis(self):
        self.dataset.data.axes[0].quantity = "foo"
        self.dataset.data.axes[1].quantity = "bar"
        self.dataset.data.axes[2].quantity = "intensity"
        self.dataset.process(self.processing)
        self.assertEqual("bar", self.dataset.data.axes[0].quantity)
        self.assertEqual("intensity", self.dataset.data.axes[-1].quantity)

    def test_project_removes_correct_axis_projecting_along_second_axis(self):
        self.dataset.data.axes[0].quantity = "foo"
        self.dataset.data.axes[1].quantity = "bar"
        self.dataset.data.axes[2].quantity = "intensity"
        self.processing.parameters["axis"] = 1
        self.dataset.process(self.processing)
        self.assertEqual("foo", self.dataset.data.axes[0].quantity)
        self.assertEqual("intensity", self.dataset.data.axes[-1].quantity)

    def test_project_averages_along_first_axis_by_default(self):
        self.dataset.process(self.processing)
        self.assertEqual(500, self.dataset.data.data.shape[0])

    def test_project_along_second_axis(self):
        self.processing.parameters["axis"] = 1
        self.dataset.process(self.processing)
        self.assertEqual(5, self.dataset.data.data.shape[0])

    def test_project_along_non_existing_axis_raises(self):
        with self.assertRaisesRegex(IndexError, "Axis [0-9]+ out of bounds"):
            self.processing.parameters["axis"] = 2
            self.dataset.process(self.processing)


class TestSliceExtraction(unittest.TestCase):
    def setUp(self):
        self.processing = aspecd.processing.SliceExtraction()
        self.dataset = aspecd.dataset.Dataset()
        data = np.sin(np.linspace(0, 2 * np.pi, num=500))
        self.dataset.data.data = (
            np.tile(data, (5, 1))
            * np.tile(np.linspace(1, 2, num=5), (500, 1)).T
        )

    def test_instantiate_class(self):
        pass

    def test_has_appropriate_description(self):
        self.assertIn("extract slice", self.processing.description.lower())

    def test_is_undoable(self):
        self.assertTrue(self.processing.undoable)

    def test_with_1D_dataset_raises(self):
        dataset = aspecd.dataset.Dataset()
        dataset.data.data = np.sin(np.linspace(0, 2 * np.pi, num=500))
        with self.assertRaises(aspecd.exceptions.NotApplicableToDatasetError):
            dataset.process(self.processing)

    def test_without_index_raises(self):
        with self.assertRaisesRegex(IndexError, "for slice extraction"):
            self.dataset.process(self.processing)

    def test_with_index_exceeding_dimension_raises(self):
        self.processing.parameters["position"] = 10
        with self.assertRaisesRegex(
            ValueError, "Position out of axis range."
        ):
            self.dataset.process(self.processing)

    def test_extract_slice(self):
        origdata = self.dataset.data.data
        self.processing.parameters["position"] = 3
        self.dataset.process(self.processing)
        np.testing.assert_allclose(origdata[3, :], self.dataset.data.data)

    def test_extract_slice_with_index_zero(self):
        origdata = self.dataset.data.data
        self.processing.parameters["position"] = 0
        self.dataset.process(self.processing)
        np.testing.assert_allclose(origdata[0, :], self.dataset.data.data)

    def test_extract_slice_removes_axis(self):
        self.processing.parameters["position"] = 3
        self.dataset.process(self.processing)
        self.assertEqual(2, len(self.dataset.data.axes))

    def test_extract_slice_removes_correct_axis(self):
        self.processing.parameters["position"] = 3
        self.dataset.data.axes[0].quantity = "foo"
        self.dataset.data.axes[1].quantity = "bar"
        self.dataset.data.axes[2].quantity = "intensity"
        self.dataset.process(self.processing)
        self.assertEqual("bar", self.dataset.data.axes[0].quantity)
        self.assertEqual("intensity", self.dataset.data.axes[-1].quantity)

    def test_extract_slice_removes_correct_axis_with_axis_one(self):
        self.processing.parameters["position"] = 3
        self.processing.parameters["axis"] = 1
        self.dataset.data.axes[0].quantity = "foo"
        self.dataset.data.axes[1].quantity = "bar"
        self.dataset.data.axes[2].quantity = "intensity"
        self.dataset.process(self.processing)
        self.assertEqual("foo", self.dataset.data.axes[0].quantity)
        self.assertEqual("intensity", self.dataset.data.axes[-1].quantity)

    def test_extract_slice_operates_along_first_axis_by_default(self):
        origdata = self.dataset.data.data
        self.processing.parameters["position"] = 3
        self.dataset.process(self.processing)
        np.testing.assert_allclose(origdata[3, :], self.dataset.data.data)

    def test_extract_slice_along_second_axis(self):
        origdata = self.dataset.data.data
        self.processing.parameters["position"] = 3
        self.processing.parameters["axis"] = 1
        self.dataset.process(self.processing)
        np.testing.assert_allclose(origdata[:, 3], self.dataset.data.data)

    def test_extract_slice_along_non_existing_axis_raises(self):
        with self.assertRaisesRegex(IndexError, "Axis [0-9]+ out of bounds"):
            self.processing.parameters["position"] = 3
            self.processing.parameters["axis"] = 2
            self.dataset.process(self.processing)

    def test_extract_slice_with_wrong_unit_raises(self):
        self.processing.parameters["unit"] = "foo"
        self.processing.parameters["position"] = 3
        with self.assertRaises(ValueError):
            self.dataset.process(self.processing)

    def test_extract_slice_with_axis_units(self):
        self.processing.parameters["unit"] = "axis"
        self.dataset.data.axes[0].values = np.linspace(
            30, 70, len(self.dataset.data.axes[0].values)
        )
        self.processing.parameters["position"] = 40
        data = self.dataset.data.data[1, :]
        self.dataset.process(self.processing)
        np.testing.assert_allclose(data, self.dataset.data.data)

    def test_unit_is_case_insensitive(self):
        self.processing.parameters["unit"] = "aXis"
        self.dataset.data.axes[0].values = np.linspace(
            30, 70, len(self.dataset.data.axes[0].values)
        )
        self.processing.parameters["position"] = 40
        data = self.dataset.data.data[1, :]
        self.dataset.process(self.processing)
        np.testing.assert_allclose(data, self.dataset.data.data)

    def test_extract_slice_with_axis_units_out_of_range_raises(self):
        self.processing.parameters["unit"] = "axis"
        self.dataset.data.axes[0].values = np.linspace(
            30, 70, len(self.dataset.data.axes[0].values)
        )
        self.processing.parameters["position"] = 300
        with self.assertRaises(ValueError):
            self.dataset.process(self.processing)

    def test_extract_slice_sets_label(self):
        self.dataset.data.axes[0].unit = "s"
        self.dataset.data.axes[0].values = np.linspace(
            5, 9, self.dataset.data.data.shape[0]
        )
        self.dataset.data.axes[1].unit = "mV"
        self.processing.parameters["position"] = 3
        self.dataset.process(self.processing)
        self.assertEqual("8.0 s", self.dataset.label)

    def test_extract_slice_with_axis_units_sets_label(self):
        self.dataset.data.axes[0].unit = "s"
        self.dataset.data.axes[0].values = np.linspace(
            5, 9, self.dataset.data.data.shape[0]
        )
        self.dataset.data.axes[1].unit = "mV"
        self.processing.parameters["unit"] = "axis"
        self.processing.parameters["position"] = 7.0
        self.dataset.process(self.processing)
        self.assertEqual("7.0 s", self.dataset.label)

    def test_extract_2d_slice_from_3d_dataset(self):
        self.dataset.data.data = np.random.random([5, 5, 5])
        origdata = self.dataset.data.data
        self.processing.parameters["position"] = 3
        self.processing.parameters["axis"] = 0
        self.dataset.process(self.processing)
        np.testing.assert_allclose(origdata[3, :, :], self.dataset.data.data)

    def test_extract_2d_slice_from_3d_dataset_along_third_dimension(self):
        self.dataset.data.data = np.random.random([5, 5, 5])
        origdata = self.dataset.data.data
        self.processing.parameters["position"] = 3
        self.processing.parameters["axis"] = 2
        self.dataset.process(self.processing)
        np.testing.assert_allclose(origdata[:, :, 3], self.dataset.data.data)

    def test_extract_2d_slice_from_3d_dataset_sets_label(self):
        self.dataset.data.data = np.random.random([5, 5, 5])
        self.dataset.data.axes[2].unit = "s"
        self.dataset.data.axes[2].values = np.linspace(
            5, 9, self.dataset.data.data.shape[2]
        )
        self.dataset.data.axes[1].unit = "mV"
        self.processing.parameters["position"] = 3
        self.processing.parameters["axis"] = 2
        self.dataset.process(self.processing)
        self.assertEqual("8.0 s", self.dataset.label)

    def test_extract_2d_slice_from_3d_dataset_with_axis_units_sets_label(
        self,
    ):
        self.dataset.data.data = np.random.random([5, 5, 5])
        self.dataset.data.axes[2].unit = "s"
        self.dataset.data.axes[2].values = np.linspace(
            5, 9, self.dataset.data.data.shape[2]
        )
        self.dataset.data.axes[1].unit = "mV"
        self.processing.parameters["unit"] = "axis"
        self.processing.parameters["position"] = 7.0
        self.processing.parameters["axis"] = 2
        self.dataset.process(self.processing)
        self.assertEqual("7.0 s", self.dataset.label)

    def test_extract_1d_slice_from_3d_dataset(self):
        self.dataset.data.data = np.random.random([5, 5, 5])
        origdata = self.dataset.data.data
        self.processing.parameters["position"] = [3, 3]
        self.processing.parameters["axis"] = [0, 1]
        self.dataset.process(self.processing)
        np.testing.assert_allclose(origdata[3, 3, :], self.dataset.data.data)

    def test_extract_1d_slice_from_3d_dataset_sets_label(self):
        self.dataset.data.data = np.random.random([5, 5, 5])
        self.dataset.data.axes[0].unit = "s"
        self.dataset.data.axes[1].unit = "mV"
        self.dataset.data.axes[0].values = np.linspace(
            5, 9, self.dataset.data.data.shape[0]
        )
        self.dataset.data.axes[1].values = np.linspace(
            3, 7, self.dataset.data.data.shape[1]
        )
        self.processing.parameters["position"] = [3, 3]
        self.processing.parameters["axis"] = [0, 1]
        self.dataset.process(self.processing)
        self.assertEqual("8.0 s, 6.0 mV", self.dataset.label)

    def test_extract_1d_slice_from_3d_dataset_with_axis_units_sets_label(
        self,
    ):
        self.dataset.data.data = np.random.random([5, 5, 5])
        self.dataset.data.axes[0].unit = "s"
        self.dataset.data.axes[1].unit = "mV"
        self.dataset.data.axes[0].values = np.linspace(
            5, 9, self.dataset.data.data.shape[0]
        )
        self.dataset.data.axes[1].values = np.linspace(
            3, 7, self.dataset.data.data.shape[1]
        )
        self.processing.parameters["unit"] = "axis"
        self.processing.parameters["position"] = [7.0, 5.0]
        self.processing.parameters["axis"] = [0, 1]
        self.dataset.process(self.processing)
        self.assertEqual("7.0 s, 5.0 mV", self.dataset.label)

    def test_extract_slice_from_3d_dataset_with_3_axes_raises(self):
        self.dataset.data.data = np.random.random([5, 5, 5])
        self.processing.parameters["position"] = [3, 3, 3]
        self.processing.parameters["axis"] = [0, 1, 2]
        with self.assertRaisesRegex(ValueError, "Too many axes"):
            self.dataset.process(self.processing)

    def test_extract_slice_with_uneven_axes_and_positions_count_raises(self):
        self.dataset.data.data = np.random.random([5, 5, 5])
        self.processing.parameters["position"] = [3]
        self.processing.parameters["axis"] = [0, 1]
        message = "Need same number of values for position and axis"
        with self.assertRaisesRegex(ValueError, message):
            self.dataset.process(self.processing)


class TestSliceRemoval(unittest.TestCase):
    def setUp(self):
        self.processing = aspecd.processing.SliceRemoval()
        self.dataset = aspecd.dataset.Dataset()
        data = np.sin(np.linspace(0, 2 * np.pi, num=500))
        self.dataset.data.data = (
            np.tile(data, (5, 1))
            * np.tile(np.linspace(1, 2, num=5), (500, 1)).T
        )

    def test_instantiate_class(self):
        pass

    def test_has_appropriate_description(self):
        self.assertIn("remove slice", self.processing.description.lower())

    def test_is_undoable(self):
        self.assertTrue(self.processing.undoable)

    def test_with_1D_dataset_raises(self):
        dataset = aspecd.dataset.Dataset()
        dataset.data.data = np.sin(np.linspace(0, 2 * np.pi, num=500))
        with self.assertRaises(aspecd.exceptions.NotApplicableToDatasetError):
            dataset.process(self.processing)

    def test_without_position_raises(self):
        with self.assertRaisesRegex(IndexError, "for slice extraction"):
            self.dataset.process(self.processing)

    def test_with_index_exceeding_dimension_raises(self):
        self.processing.parameters["position"] = 10
        with self.assertRaisesRegex(
            ValueError, "Position out of axis range."
        ):
            self.dataset.process(self.processing)

    def test_remove_slice(self):
        origdata = self.dataset.data.data
        self.processing.parameters["position"] = 3
        self.dataset.process(self.processing)
        # This assertion is currently wrong ([:2, :])
        np.testing.assert_allclose(
            np.delete(origdata, 3, 0), self.dataset.data.data
        )

    def test_remove_slice_with_index_zero(self):
        origdata = self.dataset.data.data
        self.processing.parameters["position"] = 0
        self.dataset.process(self.processing)
        np.testing.assert_allclose(origdata[1:, :], self.dataset.data.data)

    def test_remove_slice_operates_along_first_axis_by_default(self):
        origdata = self.dataset.data.data
        self.processing.parameters["position"] = 3
        self.dataset.process(self.processing)
        np.testing.assert_allclose(
            np.delete(origdata, 3, 0), self.dataset.data.data
        )

    def test_remove_slice_along_second_axis(self):
        origdata = self.dataset.data.data
        self.processing.parameters["position"] = 3
        self.processing.parameters["axis"] = 1
        self.dataset.process(self.processing)
        np.testing.assert_allclose(
            np.delete(origdata, 3, 1), self.dataset.data.data
        )

    def test_remove_slice_along_non_existing_axis_raises(self):
        with self.assertRaisesRegex(IndexError, "Axis [0-9]+ out of bounds"):
            self.processing.parameters["position"] = 3
            self.processing.parameters["axis"] = 2
            self.dataset.process(self.processing)

    def test_remove_slice_with_wrong_unit_raises(self):
        self.processing.parameters["unit"] = "foo"
        self.processing.parameters["position"] = 3
        with self.assertRaises(ValueError):
            self.dataset.process(self.processing)

    def test_remove_slice_with_axis_units(self):
        self.processing.parameters["unit"] = "axis"
        self.dataset.data.axes[0].values = np.linspace(
            30, 70, len(self.dataset.data.axes[0].values)
        )
        self.processing.parameters["position"] = 40
        data = np.delete(self.dataset.data.data, 1, 0)
        self.dataset.process(self.processing)
        np.testing.assert_allclose(data, self.dataset.data.data)

    def test_unit_is_case_insensitive(self):
        self.processing.parameters["unit"] = "aXis"
        self.dataset.data.axes[0].values = np.linspace(
            30, 70, len(self.dataset.data.axes[0].values)
        )
        self.processing.parameters["position"] = 40
        data = np.delete(self.dataset.data.data, 1, 0)
        self.dataset.process(self.processing)
        np.testing.assert_allclose(data, self.dataset.data.data)

    def test_remove_slice_with_axis_units_out_of_range_raises(self):
        self.processing.parameters["unit"] = "axis"
        self.dataset.data.axes[0].values = np.linspace(
            30, 70, len(self.dataset.data.axes[0].values)
        )
        self.processing.parameters["position"] = 300
        with self.assertRaises(ValueError):
            self.dataset.process(self.processing)


class TestRangeExtraction(unittest.TestCase):
    def setUp(self):
        self.processing = aspecd.processing.RangeExtraction()
        self.dataset = aspecd.dataset.Dataset()
        self.dataset.data.data = np.random.random(10)
        self.dataset2d = aspecd.dataset.Dataset()
        self.dataset2d.data.data = np.random.random([10, 8])

    def test_instantiate_class(self):
        pass

    def test_has_appropriate_description(self):
        self.assertIn("extract range", self.processing.description.lower())

    def test_is_undoable(self):
        self.assertTrue(self.processing.undoable)

    def test_without_range_raises(self):
        with self.assertRaisesRegex(IndexError, "for range extraction"):
            self.dataset.process(self.processing)

    def test_range_exceeding_dimension_raises(self):
        self.processing.parameters["range"] = [3, 20]
        with self.assertRaisesRegex(ValueError, "Range out of axis range"):
            self.dataset.process(self.processing)

    def test_range_exceeding_dimension_of_2nd_axis_raises(self):
        self.processing.parameters["range"] = [[3, 5], [3, 10]]
        with self.assertRaisesRegex(ValueError, "Range out of axis range"):
            self.dataset2d.process(self.processing)

    def test_range_exceeding_dimension_with_axis_units_raises(self):
        self.dataset.data.axes[0].values = np.linspace(0, 5, 10)
        self.processing.parameters["range"] = [3, 8]
        self.processing.parameters["unit"] = "axis"
        with self.assertRaisesRegex(ValueError, "Range out of axis range"):
            self.dataset.process(self.processing)

    def test_range_exceeding_dimension_of_2nd_axis_with_axis_units_raises(
        self,
    ):
        self.dataset2d.data.axes[0].values = np.linspace(0, 5, 10)
        self.dataset2d.data.axes[1].values = np.linspace(0, 5, 10)
        self.processing.parameters["range"] = [[2, 4], [3, 20]]
        self.processing.parameters["unit"] = "axis"
        with self.assertRaisesRegex(ValueError, "Range out of axis range"):
            self.dataset2d.process(self.processing)

    def test_range_exceeding_dimension_with_percentage_unit_raises(self):
        self.dataset.data.data = np.random.random(200)
        self.dataset.data.axes[0].values = np.linspace(0, 200, 200)
        self.processing.parameters["range"] = [3, 101]
        self.processing.parameters["unit"] = "percentage"
        with self.assertRaisesRegex(ValueError, "Range out of axis range"):
            self.dataset.process(self.processing)

    def test_extract_range(self):
        origdata = self.dataset.data.data
        self.processing.parameters["range"] = [3, 6]
        self.dataset.process(self.processing)
        np.testing.assert_allclose(origdata[3:6], self.dataset.data.data)

    def test_extract_range_adjusts_axis(self):
        self.dataset.data.axes[0].values = np.linspace(10, 20, 10)
        origaxis = self.dataset.data.axes[0].values
        self.processing.parameters["range"] = [3, 6]
        self.dataset.process(self.processing)
        np.testing.assert_allclose(
            origaxis[3:6], self.dataset.data.axes[0].values
        )

    def test_extract_range_with_step(self):
        origdata = self.dataset.data.data
        self.processing.parameters["range"] = [3, 6, 2]
        self.dataset.process(self.processing)
        np.testing.assert_allclose(origdata[3:6:2], self.dataset.data.data)

    def test_extract_range_with_step_adjusts_axis(self):
        self.dataset.data.axes[0].values = np.linspace(10, 20, 10)
        origaxis = self.dataset.data.axes[0].values
        self.processing.parameters["range"] = [3, 6, 2]
        self.dataset.process(self.processing)
        np.testing.assert_allclose(
            origaxis[3:6:2], self.dataset.data.axes[0].values
        )

    def test_extract_range_with_2d_data_with_only_one_range_raises(self):
        self.processing.parameters["range"] = [3, 6]
        with self.assertRaisesRegex(
            IndexError, "Got only 1 range for 2D data"
        ):
            self.dataset2d.process(self.processing)

    def test_extract_range_with_2d_data(self):
        origdata = self.dataset2d.data.data
        self.processing.parameters["range"] = [[3, 6], [2, 5]]
        self.dataset2d.process(self.processing)
        np.testing.assert_allclose(
            origdata[3:6, 2:5], self.dataset2d.data.data
        )

    def test_extract_range_with_2d_data_adjusts_axis(self):
        self.dataset2d.data.axes[0].values = np.linspace(10, 20, 10)
        self.dataset2d.data.axes[1].values = np.linspace(20, 30, 8)
        origaxis0 = self.dataset2d.data.axes[0].values
        origaxis1 = self.dataset2d.data.axes[1].values
        self.processing.parameters["range"] = [[3, 6], [2, 5]]
        self.dataset2d.process(self.processing)
        np.testing.assert_allclose(
            origaxis0[3:6], self.dataset2d.data.axes[0].values
        )
        np.testing.assert_allclose(
            origaxis1[2:5], self.dataset2d.data.axes[1].values
        )

    def test_extract_range_with_wrong_unit_raises(self):
        self.processing.parameters["range"] = [3, 6]
        self.processing.parameters["unit"] = "foo"
        with self.assertRaisesRegex(ValueError, "Wrong unit"):
            self.dataset.process(self.processing)

    def test_extract_range_with_axis_units(self):
        origdata = self.dataset.data.data
        self.dataset.data.axes[0].values = np.linspace(0, 18, 10)
        origaxis = self.dataset.data.axes[0].values
        self.processing.parameters["range"] = [6, 12]
        self.processing.parameters["unit"] = "axis"
        self.dataset.process(self.processing)
        np.testing.assert_allclose(origdata[3:7], self.dataset.data.data)
        np.testing.assert_allclose(
            origaxis[3:7], self.dataset.data.axes[0].values
        )

    def test_extract_range_with_percentage_units(self):
        origdata = self.dataset.data.data
        self.processing.parameters["range"] = [10, 80]
        self.processing.parameters["unit"] = "percentage"
        self.dataset.process(self.processing)
        np.testing.assert_allclose(origdata[1:10], self.dataset.data.data)


class TestBaselineCorrection(unittest.TestCase):
    def setUp(self):
        self.processing = aspecd.processing.BaselineCorrection()
        self.dataset = aspecd.dataset.Dataset()
        self.dataset.data.data = np.linspace(0, 2, num=500)

    def test_instantiate_class(self):
        pass

    def test_has_appropriate_description(self):
        self.assertIn("correct baseline", self.processing.description.lower())

    def test_has_parameter_kind(self):
        self.assertIn("kind", self.processing.parameters)

    def test_has_parameter_order(self):
        self.assertIn("order", self.processing.parameters)

    def test_has_parameter_coefficients(self):
        self.assertIn("coefficients", self.processing.parameters)

    def test_has_parameter_fit_area(self):
        self.assertIn("fit_area", self.processing.parameters)

    def test_subtract_polynomial_baseline_of_zeroth_order(self):
        self.processing.parameters["order"] = 0
        self.dataset.process(self.processing)
        self.assertAlmostEqual(0, self.dataset.data.data.mean())

    def test_subtract_polynomial_baseline_of_first_order(self):
        self.processing.parameters["order"] = 1
        self.dataset.process(self.processing)
        self.assertAlmostEqual(0, self.dataset.data.data[0])
        self.assertAlmostEqual(0, self.dataset.data.data[-1])

    def test_subtract_polynomial_sets_coefficients(self):
        self.processing.parameters["order"] = 0
        processing_step = self.dataset.process(self.processing)
        self.assertTrue(processing_step.parameters["coefficients"])

    def test_coefficients_are_in_data_domain(self):
        self.processing.parameters["order"] = 1
        slope = max(self.dataset.data.data) / (
            len(self.dataset.data.data) - 1
        )
        processing_step = self.dataset.process(self.processing)
        self.assertAlmostEqual(
            0, processing_step.parameters["coefficients"][0]
        )
        self.assertAlmostEqual(
            slope, processing_step.parameters["coefficients"][1]
        )

    def test_baseline_correction_without_area(self):
        self.dataset.data.data = np.ones(100) + 10
        self.dataset.data.axes[0].values = np.linspace(1, 100, num=100)
        self.dataset.process(self.processing)
        self.assertAlmostEqual(self.dataset.data.data[5], 0)

    def test_baseline_correction_with_unequal_no_of_points_per_side(self):
        self.dataset.data.data = np.r_[
            np.ones(5) + 5, np.ones(75), np.ones(20) + 5
        ]
        self.dataset.data.axes[0].values = np.linspace(1, 100, num=100)
        self.processing.parameters["fit_area"] = [5, 20]
        self.dataset.process(self.processing)
        self.assertAlmostEqual(self.dataset.data.data[-20], 0)

    def test_baseline_correction_with_only_left_side(self):
        self.dataset.data.data = np.r_[
            np.ones(5) + 2, np.ones(75), np.ones(20) + 5
        ]
        self.dataset.data.axes[0].values = np.linspace(1, 100, num=100)
        self.processing.parameters["fit_area"] = [5, 0]
        processing = self.dataset.process(self.processing)
        self.assertAlmostEqual(self.dataset.data.data[-20], 3)

    def test_baseline_correction_with_only_right_side(self):
        self.dataset.data.data = np.r_[
            np.ones(5) + 2, np.ones(75), np.ones(20) + 5
        ]
        self.dataset.data.axes[0].values = np.linspace(1, 100, num=100)
        self.processing.parameters["fit_area"] = [0, 5]
        processing = self.dataset.process(self.processing)
        self.assertAlmostEqual(self.dataset.data.data[0], -3)

    def test_baseline_correction_with_percentage_float(self):
        self.dataset.data.data = np.r_[
            np.ones(20) + 5, np.ones(60), np.ones(20) + 5
        ]
        self.dataset.data.axes[0].values = np.linspace(1, 100, num=100)
        self.processing.parameters["fit_area"] = 20.0
        self.dataset.process(self.processing)
        self.assertAlmostEqual(self.dataset.data.data[19], 0)

    def test_baseline_correction_with_percentage_int(self):
        self.dataset.data.data = np.r_[
            np.ones(20) + 5, np.ones(60), np.ones(20) + 5
        ]
        self.dataset.data.axes[0].values = np.linspace(1, 100, num=100)
        self.processing.parameters["fit_area"] = 20
        self.dataset.process(self.processing)
        self.assertAlmostEqual(self.dataset.data.data[19], 0)

    def test_baseline_correction_with_percentage_list_one_element(self):
        self.dataset.data.data = np.r_[
            np.ones(20) + 5, np.ones(60), np.ones(20) + 5
        ]
        self.dataset.data.axes[0].values = np.linspace(1, 100, num=100)
        self.processing.parameters["fit_area"] = [
            20,
        ]
        self.dataset.process(self.processing)
        self.assertAlmostEqual(self.dataset.data.data[19], 0)

    def test_baseline_correction_with_more_than_hundred_percent(self):
        self.dataset.data.data = np.r_[
            np.ones(20) + 5, np.ones(60), np.ones(20) + 5
        ]
        self.dataset.data.axes[0].values = np.linspace(1, 100, num=100)
        self.processing.parameters["fit_area"] = [120, 120]
        with self.assertLogs() as captured:
            self.dataset.process(self.processing)
        self.assertEqual(len(captured.records), 1)

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
        self.assertIn("average", self.processing.description.lower())

    def test_is_undoable(self):
        self.assertTrue(self.processing.undoable)

    def test_with_1D_dataset_raises(self):
        dataset = aspecd.dataset.Dataset()
        dataset.data.data = np.sin(np.linspace(0, 2 * np.pi, num=500))
        with self.assertRaises(aspecd.exceptions.NotApplicableToDatasetError):
            dataset.process(self.processing)

    def test_without_range_raises(self):
        with self.assertRaises(ValueError):
            self.dataset.process(self.processing)

    def test_with_start_range_outside_axis_range_raises(self):
        self.processing.parameters["range"] = [-6, 3]
        with self.assertRaises(ValueError):
            self.dataset.process(self.processing)

    def test_with_end_range_outside_axis_range_raises(self):
        self.processing.parameters["range"] = [
            1,
            self.dataset.data.data.shape[0] + 1,
        ]
        with self.assertRaises(ValueError):
            self.dataset.process(self.processing)

    def test_average_reduces_data_dimensionality(self):
        self.processing.parameters["range"] = [2, 3]
        self.dataset.process(self.processing)
        self.assertEqual(1, self.dataset.data.data.ndim)

    def test_average_averages_correctly(self):
        self.processing.parameters["range"] = [2, 3]
        data = np.average(self.dataset.data.data[2 : 3 + 1, :], axis=0)
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
        self.dataset.data.axes[0].quantity = "foo"
        self.dataset.data.axes[1].quantity = "bar"
        self.dataset.data.axes[2].quantity = "intensity"
        self.dataset.process(self.processing)
        self.assertEqual("bar", self.dataset.data.axes[0].quantity)
        self.assertEqual("intensity", self.dataset.data.axes[-1].quantity)

    def test_average_averages_along_first_axis_by_default(self):
        length = self.dataset.data.data.shape[1]
        self.processing.parameters["range"] = [2, 3]
        self.dataset.process(self.processing)
        self.assertEqual(length, self.dataset.data.data.shape[0])

    def test_average_along_second_axis(self):
        length = self.dataset.data.data.shape[0]
        self.processing.parameters["range"] = [2, 3]
        self.processing.parameters["axis"] = 1
        self.dataset.process(self.processing)
        self.assertEqual(length, self.dataset.data.data.shape[0])

    def test_average_along_second_axis_averages_correctly(self):
        length = self.dataset.data.data.shape[0]
        self.processing.parameters["range"] = [20, 30]
        self.processing.parameters["axis"] = 1
        data = np.average(self.dataset.data.data[:, 20 : 30 + 1], axis=1)
        self.dataset.process(self.processing)
        self.assertEqual(length, self.dataset.data.data.shape[0])
        np.testing.assert_allclose(data, self.dataset.data.data)

    def test_along_second_axis_with_end_range_outside_axis_range_raises(self):
        self.processing.parameters["axis"] = 1
        self.processing.parameters["range"] = [
            1,
            self.dataset.data.data.shape[1] + 1,
        ]
        with self.assertRaises(ValueError):
            self.dataset.process(self.processing)

    def test_average_along_non_existing_axis_raises(self):
        with self.assertRaisesRegex(IndexError, "Axis [0-9]+ out of bounds"):
            self.processing.parameters["range"] = [2, 3]
            self.processing.parameters["axis"] = 2
            self.dataset.process(self.processing)

    def test_average_with_wrong_unit_raises(self):
        self.processing.parameters["unit"] = "foo"
        self.processing.parameters["range"] = [2, 3]
        with self.assertRaises(ValueError):
            self.dataset.process(self.processing)

    def test_average_with_axis_units(self):
        self.processing.parameters["unit"] = "axis"
        self.dataset.data.axes[0].values = np.linspace(
            30, 70, len(self.dataset.data.axes[0].values)
        )
        self.processing.parameters["range"] = [30, 40]
        data = np.average(self.dataset.data.data[0:2, :], axis=0)
        self.dataset.process(self.processing)
        np.testing.assert_allclose(data, self.dataset.data.data)

    def test_unit_is_case_insensitive(self):
        self.processing.parameters["unit"] = "aXis"
        self.dataset.data.axes[0].values = np.linspace(
            30, 70, len(self.dataset.data.axes[0].values)
        )
        self.processing.parameters["range"] = [30, 40]
        data = np.average(self.dataset.data.data[0:2, :], axis=0)
        self.dataset.process(self.processing)
        np.testing.assert_allclose(data, self.dataset.data.data)

    def test_average_with_axis_units_out_of_range_raises(self):
        self.processing.parameters["unit"] = "axis"
        self.dataset.data.axes[0].values = np.linspace(
            30, 70, len(self.dataset.data.axes[0].values)
        )
        self.processing.parameters["range"] = [300, 400]
        with self.assertRaises(ValueError):
            self.dataset.process(self.processing)

    def test_average_sets_label(self):
        self.dataset.data.axes[0].unit = "s"
        self.dataset.data.axes[0].values = np.linspace(
            5, 9, self.dataset.data.data.shape[0]
        )
        self.dataset.data.axes[1].unit = "mV"
        self.processing.parameters["range"] = [2, 3]
        self.dataset.process(self.processing)
        self.assertEqual("7.0-8.0 s", self.dataset.label)

    def test_average_with_axis_units_sets_label(self):
        self.dataset.data.axes[0].unit = "s"
        self.dataset.data.axes[0].values = np.linspace(
            5, 9, self.dataset.data.data.shape[0]
        )
        self.dataset.data.axes[1].unit = "mV"
        self.processing.parameters["unit"] = "axis"
        self.processing.parameters["range"] = [7.0, 8.0]
        self.dataset.process(self.processing)
        self.assertEqual("7.0-8.0 s", self.dataset.label)

    def test_average_along_second_axis_sets_label(self):
        self.dataset.data.axes[0].unit = "s"
        self.dataset.data.axes[1].values = np.linspace(
            5, 9, self.dataset.data.data.shape[0]
        )
        self.dataset.data.axes[1].unit = "mV"
        self.processing.parameters["axis"] = 1
        self.processing.parameters["range"] = [2, 3]
        self.dataset.process(self.processing)
        self.assertEqual("7.0-8.0 mV", self.dataset.label)

    def test_average_along_second_axis_with_axis_units_sets_label(self):
        self.dataset.data.axes[0].unit = "s"
        self.dataset.data.axes[1].values = np.linspace(
            5, 9, self.dataset.data.data.shape[0]
        )
        self.dataset.data.axes[1].unit = "mV"
        self.processing.parameters["unit"] = "axis"
        self.processing.parameters["axis"] = 1
        self.processing.parameters["range"] = [7.0, 8.0]
        self.dataset.process(self.processing)
        self.assertEqual("7.0-8.0 mV", self.dataset.label)


class TestDatasetAlgebra(unittest.TestCase):
    def setUp(self):
        self.processing = aspecd.processing.DatasetAlgebra()
        self.dataset1 = aspecd.dataset.Dataset()
        self.dataset2 = aspecd.dataset.Dataset()

    def test_instantiate_class(self):
        pass

    def test_has_appropriate_description(self):
        self.assertIn("algebra", self.processing.description.lower())
        self.assertIn("datasets", self.processing.description.lower())

    def test_is_singleprocessing_step(self):
        self.assertTrue(
            isinstance(
                self.processing, aspecd.processing.SingleProcessingStep
            )
        )

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
        self.processing.parameters["kind"] = "foo"
        with self.assertRaises(ValueError):
            self.dataset1.process(self.processing)

    def test_process_with_differing_shapes_raises(self):
        self.dataset1.data.data = np.random.random(5)
        self.dataset2.data.data = np.random.random(6)
        self.processing.parameters["dataset"] = self.dataset2
        self.processing.parameters["kind"] = "add"
        with self.assertRaisesRegex(ValueError, "different shapes"):
            self.dataset1.process(self.processing)

    def test_process_with_differing_shapes_shows_shape_in_message(self):
        self.dataset1.data.data = np.random.random(5)
        self.dataset2.data.data = np.random.random(6)
        self.processing.parameters["dataset"] = self.dataset2
        self.processing.parameters["kind"] = "add"
        with self.assertRaisesRegex(
            ValueError, str(self.dataset1.data.data.shape)
        ):
            self.dataset1.process(self.processing)

    def test_add_with_1d_datasets(self):
        self.dataset1.data.data = np.ones(5)
        self.dataset2.data.data = np.ones(5)
        self.processing.parameters["dataset"] = self.dataset2
        self.processing.parameters["kind"] = "add"
        self.dataset1.process(self.processing)
        self.assertTrue(np.all(self.dataset1.data.data == 2))

    def test_add_with_1d_datasets_with_history(self):
        self.dataset1.data.data = np.ones(5)
        self.dataset2.data.data = np.ones(5)
        preprocessing = aspecd.processing.Normalisation()
        preprocessing.parameters["kind"] = "max"
        self.dataset1.process(preprocessing)
        self.dataset2.process(preprocessing)
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
        self.dataset2.id = "12345"
        self.processing.parameters["dataset"] = self.dataset2
        self.processing.parameters["kind"] = "add"
        processing = self.dataset1.process(self.processing)
        self.assertEqual(self.dataset2.id, processing.parameters["dataset"])

    def test_process_writes_dataset_id_in_history(self):
        self.dataset1.data.data = np.ones(5)
        self.dataset2.data.data = np.ones(5)
        self.dataset2.id = "12345"
        self.processing.parameters["dataset"] = self.dataset2
        self.processing.parameters["kind"] = "add"
        self.dataset1.process(self.processing)
        self.assertEqual(
            self.dataset2.id,
            self.dataset1.history[-1].processing.parameters["dataset"],
        )


class TestScalarAxisAlgebra(unittest.TestCase):
    def setUp(self):
        self.processing = aspecd.processing.ScalarAxisAlgebra()
        self.dataset = aspecd.dataset.Dataset()

    def test_instantiate_class(self):
        pass

    def test_has_appropriate_description(self):
        self.assertIn(
            "scalar algebra on the axis", self.processing.description.lower()
        )

    def test_is_singleprocessing_step(self):
        self.assertTrue(
            isinstance(
                self.processing, aspecd.processing.SingleProcessingStep
            )
        )

    def test_is_undoable(self):
        self.assertTrue(self.processing.undoable)

    def test_process_without_kind_raises(self):
        with self.assertRaises(ValueError):
            self.dataset.process(self.processing)

    def test_process_with_wrong_kind_raises(self):
        self.processing.parameters["kind"] = "foo"
        with self.assertRaises(ValueError):
            self.dataset.process(self.processing)

    def test_add(self):
        self.processing.parameters["kind"] = "add"
        self.processing.parameters["value"] = 3
        self.dataset.data.data = np.random.random(5)
        self.dataset.data.axes[0].values = np.linspace(0, 5, 5)
        self.dataset.process(self.processing)
        self.assertTrue(
            np.all(
                np.linspace(0, 5, 5) + 3 == self.dataset.data.axes[0].values
            )
        )

    def test_plus(self):
        self.processing.parameters["kind"] = "plus"
        self.processing.parameters["value"] = 3
        self.dataset.data.data = np.random.random(5)
        self.dataset.data.axes[0].values = np.linspace(0, 5, 5)
        self.dataset.process(self.processing)
        self.assertTrue(
            np.all(
                np.linspace(0, 5, 5) + 3 == self.dataset.data.axes[0].values
            )
        )

    def test_add_specified_by_sign(self):
        self.processing.parameters["kind"] = "+"
        self.processing.parameters["value"] = 3
        self.dataset.data.data = np.random.random(5)
        self.dataset.data.axes[0].values = np.linspace(0, 5, 5)
        self.dataset.process(self.processing)
        self.assertTrue(
            np.all(
                np.linspace(0, 5, 5) + 3 == self.dataset.data.axes[0].values
            )
        )

    def test_add_with_2D_dataset_and_second_axis(self):
        self.processing.parameters["kind"] = "plus"
        self.processing.parameters["axis"] = 1
        self.processing.parameters["value"] = 3
        self.dataset.data.data = np.random.random([5, 5])
        self.dataset.data.axes[0].values = np.linspace(0, 5, 5)
        self.dataset.data.axes[1].values = np.linspace(0, 5, 5)
        self.dataset.process(self.processing)
        self.assertTrue(
            np.all(np.linspace(0, 5, 5) == self.dataset.data.axes[0].values)
        )
        self.assertTrue(
            np.all(
                np.linspace(0, 5, 5) + 3 == self.dataset.data.axes[1].values
            )
        )

    def test_subtract(self):
        self.processing.parameters["kind"] = "subtract"
        self.processing.parameters["value"] = 3
        self.dataset.data.data = np.random.random(5)
        self.dataset.data.axes[0].values = np.linspace(0, 5, 5)
        self.dataset.process(self.processing)
        self.assertTrue(
            np.all(
                np.linspace(0, 5, 5) - 3 == self.dataset.data.axes[0].values
            )
        )

    def test_minus(self):
        self.processing.parameters["kind"] = "minus"
        self.processing.parameters["value"] = 3
        self.dataset.data.data = np.random.random(5)
        self.dataset.data.axes[0].values = np.linspace(0, 5, 5)
        self.dataset.process(self.processing)
        self.assertTrue(
            np.all(
                np.linspace(0, 5, 5) - 3 == self.dataset.data.axes[0].values
            )
        )

    def test_subtract_specified_by_sign(self):
        self.processing.parameters["kind"] = "-"
        self.processing.parameters["value"] = 3
        self.dataset.data.data = np.random.random(5)
        self.dataset.data.axes[0].values = np.linspace(0, 5, 5)
        self.dataset.process(self.processing)
        self.assertTrue(
            np.all(
                np.linspace(0, 5, 5) - 3 == self.dataset.data.axes[0].values
            )
        )

    def test_multiply(self):
        self.processing.parameters["kind"] = "multiply"
        self.processing.parameters["value"] = 3
        self.dataset.data.data = np.random.random(5)
        self.dataset.data.axes[0].values = np.linspace(0, 5, 5)
        self.dataset.process(self.processing)
        self.assertTrue(
            np.all(
                np.linspace(0, 5, 5) * 3 == self.dataset.data.axes[0].values
            )
        )

    def test_times(self):
        self.processing.parameters["kind"] = "times"
        self.processing.parameters["value"] = 3
        self.dataset.data.data = np.random.random(5)
        self.dataset.data.axes[0].values = np.linspace(0, 5, 5)
        self.dataset.process(self.processing)
        self.assertTrue(
            np.all(
                np.linspace(0, 5, 5) * 3 == self.dataset.data.axes[0].values
            )
        )

    def test_multiply_specified_by_sign(self):
        self.processing.parameters["kind"] = "*"
        self.processing.parameters["value"] = 3
        self.dataset.data.data = np.random.random(5)
        self.dataset.data.axes[0].values = np.linspace(0, 5, 5)
        self.dataset.process(self.processing)
        self.assertTrue(
            np.all(
                np.linspace(0, 5, 5) * 3 == self.dataset.data.axes[0].values
            )
        )

    def test_divide(self):
        self.processing.parameters["kind"] = "divide"
        self.processing.parameters["value"] = 3
        self.dataset.data.data = np.random.random(5)
        self.dataset.data.axes[0].values = np.linspace(0, 5, 5)
        self.dataset.process(self.processing)
        self.assertTrue(
            np.all(
                np.linspace(0, 5, 5) / 3 == self.dataset.data.axes[0].values
            )
        )

    def test_by(self):
        self.processing.parameters["kind"] = "by"
        self.processing.parameters["value"] = 3
        self.dataset.data.data = np.random.random(5)
        self.dataset.data.axes[0].values = np.linspace(0, 5, 5)
        self.dataset.process(self.processing)
        self.assertTrue(
            np.all(
                np.linspace(0, 5, 5) / 3 == self.dataset.data.axes[0].values
            )
        )

    def test_divide_specified_by_sign(self):
        self.processing.parameters["kind"] = "/"
        self.processing.parameters["value"] = 3
        self.dataset.data.data = np.random.random(5)
        self.dataset.data.axes[0].values = np.linspace(0, 5, 5)
        self.dataset.process(self.processing)
        self.assertTrue(
            np.all(
                np.linspace(0, 5, 5) / 3 == self.dataset.data.axes[0].values
            )
        )

    def test_power(self):
        self.processing.parameters["kind"] = "power"
        self.processing.parameters["value"] = 3
        self.dataset.data.data = np.random.random(5)
        self.dataset.data.axes[0].values = np.linspace(0, 5, 5)
        self.dataset.process(self.processing)
        self.assertTrue(
            np.all(
                np.linspace(0, 5, 5) ** 3 == self.dataset.data.axes[0].values
            )
        )

    def test_pow(self):
        self.processing.parameters["kind"] = "pow"
        self.processing.parameters["value"] = 3
        self.dataset.data.data = np.random.random(5)
        self.dataset.data.axes[0].values = np.linspace(0, 5, 5)
        self.dataset.process(self.processing)
        self.assertTrue(
            np.all(
                np.linspace(0, 5, 5) ** 3 == self.dataset.data.axes[0].values
            )
        )

    def test_power_specified_by_sign(self):
        self.processing.parameters["kind"] = "**"
        self.processing.parameters["value"] = 3
        self.dataset.data.data = np.random.random(5)
        self.dataset.data.axes[0].values = np.linspace(0, 5, 5)
        self.dataset.process(self.processing)
        self.assertTrue(
            np.all(
                np.linspace(0, 5, 5) ** 3 == self.dataset.data.axes[0].values
            )
        )


class TestInterpolation(unittest.TestCase):
    def setUp(self):
        self.processing = aspecd.processing.Interpolation()
        self.dataset = aspecd.dataset.Dataset()
        self.dataset.data.data = np.linspace(10, 20, 11)
        self.dataset.data.axes[0].values = np.linspace(5, 15, 11)
        self.dataset2d = aspecd.dataset.Dataset()
        self.dataset2d.data.data = np.reshape(
            np.tile(np.linspace(0, 5, 11), 21), (21, 11)
        )
        self.dataset2d.data.axes[0].values = np.linspace(30, 40, 21)
        self.dataset2d.data.axes[1].values = np.linspace(5, 15, 11)
        self.dataset3d = aspecd.dataset.Dataset()
        self.dataset3d.data.data = np.reshape(
            np.tile(np.linspace(0, 5, 11), [21, 16]).ravel(), (21, 11, 16)
        )
        self.dataset3d.data.axes[0].values = np.linspace(30, 40, 21)
        self.dataset3d.data.axes[1].values = np.linspace(5, 15, 11)
        self.dataset3d.data.axes[2].values = np.linspace(2.5, 10, 16)

    def test_instantiate_class(self):
        pass

    def test_has_appropriate_description(self):
        self.assertIn("interpolate", self.processing.description.lower())

    def test_is_undoable(self):
        self.assertTrue(self.processing.undoable)

    def test_interpolate_without_range_raises(self):
        self.processing.parameters["npoints"] = 21
        with self.assertRaisesRegex(ValueError, "No range provided"):
            self.dataset.process(self.processing)

    def test_interpolate_without_npoints_raises(self):
        self.processing.parameters["range"] = [0, 10]
        with self.assertRaisesRegex(
            ValueError, "No number of points provided"
        ):
            self.dataset.process(self.processing)

    def test_interpolate_1d_data_with_range_outside_data_raises(self):
        self.processing.parameters["range"] = [15, 15]
        self.processing.parameters["npoints"] = 21
        with self.assertRaisesRegex(IndexError, "out of range"):
            self.dataset.process(self.processing)

    def test_interpolate_1d_data_interpolates_data(self):
        self.processing.parameters["range"] = [0, 10]
        self.processing.parameters["npoints"] = 21
        self.dataset.process(self.processing)
        self.assertListEqual(
            list(np.linspace(10, 20, 21)), list(self.dataset.data.data)
        )

    def test_interpolate_1d_data_interpolates_axis(self):
        self.processing.parameters["range"] = [0, 10]
        self.processing.parameters["npoints"] = 21
        self.dataset.process(self.processing)
        self.assertListEqual(
            list(np.linspace(5, 15, 21)),
            list(self.dataset.data.axes[0].values),
        )

    def test_interpolate_with_wrong_unit_raises(self):
        self.processing.parameters["range"] = [5, 15]
        self.processing.parameters["npoints"] = 21
        self.processing.parameters["unit"] = "foo"
        with self.assertRaisesRegex(ValueError, "Unknown unit foo"):
            self.dataset.process(self.processing)

    def test_interpolate_1d_data_with_axis_unit_outside_range_raises(self):
        self.processing.parameters["range"] = [0, 10]
        self.processing.parameters["npoints"] = 21
        self.processing.parameters["unit"] = "axis"
        with self.assertRaisesRegex(IndexError, "out of range"):
            self.dataset.process(self.processing)

    def test_interpolate_1d_data_with_axis_unit_interpolates_data(self):
        self.processing.parameters["range"] = [5, 15]
        self.processing.parameters["npoints"] = 21
        self.processing.parameters["unit"] = "axis"
        self.dataset.process(self.processing)
        self.assertListEqual(
            list(np.linspace(10, 20, 21)), list(self.dataset.data.data)
        )

    def test_interpolate_1d_data_with_axis_unit_interpolates_axis(self):
        self.processing.parameters["range"] = [5, 15]
        self.processing.parameters["npoints"] = 21
        self.processing.parameters["unit"] = "axis"
        self.dataset.process(self.processing)
        self.assertListEqual(
            list(np.linspace(5, 15, 21)),
            list(self.dataset.data.axes[0].values),
        )

    def test_interpolate_1d_data_w_axis_unit_interpolates_axis_odd_values(
        self,
    ):
        self.processing.parameters["range"] = [5.85, 14.83]
        self.processing.parameters["npoints"] = 21
        self.processing.parameters["unit"] = "axis"
        self.dataset.process(self.processing)
        self.assertListEqual(
            list(np.linspace(5.85, 14.83, 21)),
            list(self.dataset.data.axes[0].values),
        )

    def test_interpolate_2d_data_with_missing_range_raises(self):
        self.processing.parameters["range"] = [0, 10]
        self.processing.parameters["npoints"] = [41, 21]
        with self.assertRaisesRegex(
            IndexError, "List of ranges does not fit " "data dimensions"
        ):
            self.dataset2d.process(self.processing)

    def test_interpolate_2d_data_with_missing_npoints_raises(self):
        self.processing.parameters["range"] = [[0, 20], [0, 10]]
        self.processing.parameters["npoints"] = 41
        with self.assertRaisesRegex(
            IndexError, "List of npoints does not fit " "data dimensions"
        ):
            self.dataset2d.process(self.processing)

    def test_interpolate_2d_data_outside_range_raises(self):
        self.processing.parameters["range"] = [[30, 320], [0, 10]]
        self.processing.parameters["npoints"] = [41, 21]
        with self.assertRaisesRegex(IndexError, "out of range"):
            self.dataset2d.process(self.processing)

    def test_interpolate_2d_data_outside_range_with_axis_values_raises(self):
        self.processing.parameters["range"] = [[30, 320], [0, 10]]
        self.processing.parameters["npoints"] = [41, 21]
        self.processing.parameters["unit"] = "axis"
        with self.assertRaisesRegex(IndexError, "out of range"):
            self.dataset2d.process(self.processing)

    def test_interpolate_2d_data_interpolates_data(self):
        self.processing.parameters["range"] = [[0, 20], [0, 10]]
        self.processing.parameters["npoints"] = [41, 21]
        self.dataset2d.process(self.processing)
        self.assertListEqual(
            list(np.linspace(0, 5, 21)), list(self.dataset2d.data.data[0, :])
        )

    def test_interpolate_2d_data_interpolates_axis(self):
        self.processing.parameters["range"] = [[0, 20], [0, 10]]
        self.processing.parameters["npoints"] = [41, 21]
        self.dataset2d.process(self.processing)
        self.assertListEqual(
            list(np.linspace(30, 40, 41)),
            list(self.dataset2d.data.axes[0].values),
        )

    def test_interpolate_3d_data_with_missing_range_raises(self):
        self.processing.parameters["range"] = [[0, 20], [0, 10]]
        self.processing.parameters["npoints"] = [41, 21, 21]
        with self.assertRaisesRegex(
            IndexError, "List of ranges does not fit " "data dimensions"
        ):
            self.dataset3d.process(self.processing)

    def test_interpolate_3d_data_with_missing_npoints_raises(self):
        self.processing.parameters["range"] = [[0, 20], [0, 10], [5, 15]]
        self.processing.parameters["npoints"] = [41, 21]
        with self.assertRaisesRegex(
            IndexError, "List of npoints does not fit " "data dimensions"
        ):
            self.dataset3d.process(self.processing)

    def test_interpolate_3d_data_interpolates_data(self):
        self.processing.parameters["range"] = [[0, 20], [0, 10], [0, 15]]
        self.processing.parameters["npoints"] = [41, 21, 16]
        old_data = self.dataset3d.data.data[0, :, 0]
        self.dataset3d.process(self.processing)
        self.assertListEqual(
            list(old_data), list(self.dataset3d.data.data[0, ::2, 0])
        )


class TestFiltering(unittest.TestCase):
    def setUp(self):
        self.processing = aspecd.processing.Filtering()
        self.dataset = aspecd.dataset.Dataset()
        self.dataset.data.data = np.linspace(10, 20, 11)
        self.dataset2d = aspecd.dataset.Dataset()
        self.dataset2d.data.data = np.reshape(
            np.tile(np.linspace(0, 5, 21), 11), (11, 21)
        )

    def test_instantiate_class(self):
        pass

    def test_has_appropriate_description(self):
        self.assertIn("filter", self.processing.description.lower())

    def test_is_undoable(self):
        self.assertTrue(self.processing.undoable)

    def test_process_without_type_raises(self):
        with self.assertRaisesRegex(ValueError, "Missing filter type"):
            self.dataset.process(self.processing)

    def test_process_with_wrong_type_raises(self):
        self.processing.parameters["type"] = "foo"
        with self.assertRaisesRegex(ValueError, "Wrong filter type foo"):
            self.dataset.process(self.processing)

    def test_process_without_window_length_raises(self):
        self.processing.parameters["type"] = "uniform"
        with self.assertRaisesRegex(
            ValueError, "Missing filter window length"
        ):
            self.dataset.process(self.processing)

    def test_process_with_window_outside_data_range_raises(self):
        self.processing.parameters["type"] = "uniform"
        self.processing.parameters["window_length"] = (
            min(self.dataset2d.data.data.shape) + 1
        )
        with self.assertRaisesRegex(
            ValueError, "Filter window outside data " "range"
        ):
            self.dataset2d.process(self.processing)

    def test_process_with_window_outside_data_range_with_2d_data_raises(self):
        self.processing.parameters["type"] = "uniform"
        self.processing.parameters["window_length"] = (
            self.dataset.data.data.size + 1
        )
        with self.assertRaisesRegex(
            ValueError, "Filter window outside data " "range"
        ):
            self.dataset.process(self.processing)

    def test_uniform_filter_with_1d_data(self):
        self.processing.parameters["type"] = "uniform"
        self.processing.parameters["window_length"] = 3
        filtered_data = scipy.ndimage.uniform_filter(
            self.dataset.data.data, 3
        )
        self.dataset.process(self.processing)
        self.assertTrue(all(filtered_data == self.dataset.data.data))

    def test_uniform_filter_with_1d_data_preserves_shape(self):
        self.processing.parameters["type"] = "uniform"
        self.processing.parameters["window_length"] = 3
        orig_shape = self.dataset.data.data.shape
        self.dataset.process(self.processing)
        self.assertEqual(orig_shape, self.dataset.data.data.shape)

    def test_gaussian_filter_with_1d_data(self):
        self.processing.parameters["type"] = "gaussian"
        self.processing.parameters["window_length"] = 3
        filtered_data = scipy.ndimage.gaussian_filter(
            self.dataset.data.data,
            self.processing.parameters["window_length"],
        )
        self.dataset.process(self.processing)
        self.assertTrue(all(filtered_data == self.dataset.data.data))

    def test_gaussian_filter_with_1d_data_preserves_shape(self):
        self.processing.parameters["type"] = "gaussian"
        self.processing.parameters["window_length"] = 3
        orig_shape = self.dataset.data.data.shape
        self.dataset.process(self.processing)
        self.assertEqual(orig_shape, self.dataset.data.data.shape)

    def test_savitzky_golay_filter_without_order_raises(self):
        self.processing.parameters["type"] = "savitzky-golay"
        self.processing.parameters["window_length"] = 3
        with self.assertRaisesRegex(
            ValueError, "Missing order for this " "filter"
        ):
            self.dataset.process(self.processing)

    def test_savitzky_golay_filter_with_1d_data(self):
        self.processing.parameters["type"] = "savitzky-golay"
        self.processing.parameters["window_length"] = 3
        self.processing.parameters["order"] = 2
        filtered_data = scipy.signal.savgol_filter(
            self.dataset.data.data,
            self.processing.parameters["window_length"],
            self.processing.parameters["order"],
        )
        self.dataset.process(self.processing)
        self.assertTrue(all(filtered_data == self.dataset.data.data))

    def test_savitzky_golay__filter_with_1d_data_preserves_shape(self):
        self.processing.parameters["type"] = "savitzky-golay"
        self.processing.parameters["window_length"] = 3
        self.processing.parameters["order"] = 2
        orig_shape = self.dataset.data.data.shape
        self.dataset.process(self.processing)
        self.assertEqual(orig_shape, self.dataset.data.data.shape)

    def test_uniform_filter_with_1d_data_with_alternative_names(self):
        alternative_names = ["box", "boxcar", "moving-average", "car"]
        self.processing.parameters["window_length"] = 3
        for filter_name in alternative_names:
            with self.subTest(filter_name=filter_name):
                filtered_data = scipy.ndimage.uniform_filter(
                    self.dataset.data.data,
                    self.processing.parameters["window_length"],
                )
                self.processing.parameters["type"] = filter_name
                self.dataset.process(self.processing)
                self.assertTrue(all(filtered_data == self.dataset.data.data))

    def test_gaussian_filter_with_1d_data_with_alternative_names(self):
        alternative_names = ["binom", "binomial"]
        self.processing.parameters["window_length"] = 3
        for filter_name in alternative_names:
            with self.subTest(filter_name=filter_name):
                filtered_data = scipy.ndimage.gaussian_filter(
                    self.dataset.data.data,
                    self.processing.parameters["window_length"],
                )
                self.processing.parameters["type"] = filter_name
                self.dataset.process(self.processing)
                self.assertTrue(all(filtered_data == self.dataset.data.data))

    def test_savitzky_golay_filter_with_1d_data_with_alternative_names(self):
        alternative_names = [
            "savitzky_golay",
            "savitzky golay",
            "savgol",
            "savitzky",
        ]
        self.processing.parameters["window_length"] = 3
        self.processing.parameters["order"] = 2
        for filter_name in alternative_names:
            with self.subTest(filter_name=filter_name):
                filtered_data = scipy.signal.savgol_filter(
                    self.dataset.data.data,
                    self.processing.parameters["window_length"],
                    self.processing.parameters["order"],
                )
                self.processing.parameters["type"] = filter_name
                self.dataset.process(self.processing)
                self.assertTrue(all(filtered_data == self.dataset.data.data))

    def test_savitzky_golay_filter_with_1d_data_with_even_window_length(self):
        self.processing.parameters["type"] = "savitzky-golay"
        self.processing.parameters["window_length"] = 10
        self.processing.parameters["order"] = 3
        filtered_data = scipy.signal.savgol_filter(
            self.dataset.data.data,
            self.processing.parameters["window_length"] + 1,
            self.processing.parameters["order"],
        )
        self.dataset.process(self.processing)
        self.assertTrue(all(filtered_data == self.dataset.data.data))

    def test_filter_with_alternative_names_sets_generic_filter_type(self):
        alternative_names = ["box", "boxcar", "moving-average", "car"]
        self.processing.parameters["window_length"] = 3
        for filter_name in alternative_names:
            with self.subTest(filter_name=filter_name):
                self.processing.parameters["type"] = filter_name
                processing = self.dataset.process(self.processing)
                self.assertEqual("uniform", processing.parameters["type"])

    def test_uniform_filter_with_2d_data(self):
        self.processing.parameters["type"] = "uniform"
        self.processing.parameters["window_length"] = 3
        filtered_data = scipy.ndimage.uniform_filter(
            self.dataset2d.data.data,
            self.processing.parameters["window_length"],
        )
        self.dataset2d.process(self.processing)
        self.assertTrue((filtered_data == self.dataset2d.data.data).all())


class TestCommonRangeExtraction(unittest.TestCase):
    def setUp(self):
        self.processing = aspecd.processing.CommonRangeExtraction()
        self.dataset1 = aspecd.dataset.Dataset()
        self.dataset2 = aspecd.dataset.Dataset()

    def test_instantiate_class(self):
        pass

    def test_has_appropriate_description(self):
        self.assertIn(
            "common data range", self.processing.description.lower()
        )

    def test_is_multiprocessing_step(self):
        self.assertTrue(
            isinstance(self.processing, aspecd.processing.MultiProcessingStep)
        )

    def test_is_undoable(self):
        self.assertTrue(self.processing.undoable)

    def test_with_only_one_dataset_raises(self):
        self.processing.datasets.append(self.dataset1)
        with self.assertRaisesRegex(IndexError, "Need more than one dataset"):
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
        self.dataset1.data.axes[0].unit = "foo"
        self.dataset1.data.axes[1].unit = "bar"
        self.dataset2.data.data = np.random.random([10, 10])
        self.dataset2.data.axes[0].values = np.linspace(0, 5, 10)
        self.dataset2.data.axes[1].values = np.linspace(0, 5, 10)
        self.dataset2.data.axes[0].unit = "foobar"
        self.dataset2.data.axes[1].unit = "bar"
        self.processing.datasets.append(self.dataset1)
        self.processing.datasets.append(self.dataset2)
        with self.assertRaisesRegex(ValueError, "different units"):
            self.processing.process()

    def test_process_datasets_ignores_last_axis(self):
        self.dataset1.data.data = np.random.random(10)
        self.dataset1.data.axes[0].values = np.linspace(0, 5, 10)
        self.dataset1.data.axes[0].unit = "foo"
        self.dataset1.data.axes[1].unit = "bar"
        self.dataset2.data.data = np.random.random(10)
        self.dataset2.data.axes[0].values = np.linspace(0, 5, 10)
        self.dataset2.data.axes[0].unit = "foo"
        self.dataset2.data.axes[1].unit = "baz"
        self.processing.datasets.append(self.dataset1)
        self.processing.datasets.append(self.dataset2)
        self.processing.process()

    def test_process_ignores_different_axes_units_if_told_so(self):
        self.dataset1.data.data = np.random.random([10, 10])
        self.dataset1.data.axes[0].values = np.linspace(0, 5, 10)
        self.dataset1.data.axes[1].values = np.linspace(0, 5, 10)
        self.dataset1.data.axes[0].unit = "foo"
        self.dataset1.data.axes[1].unit = "bar"
        self.dataset2.data.data = np.random.random([10, 10])
        self.dataset2.data.axes[0].values = np.linspace(0, 5, 10)
        self.dataset2.data.axes[1].values = np.linspace(0, 5, 10)
        self.dataset2.data.axes[0].unit = "foobar"
        self.dataset2.data.axes[1].unit = "bar"
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
        self.assertListEqual(
            self.processing.parameters["common_range"], [[1.0, 4.0]]
        )

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
        self.assertListEqual(
            self.processing.parameters["common_range"],
            [[1.0, 4.0], [11.0, 14.0]],
        )

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
        self.dataset1.data.data = np.linspace(10, 15, 420)
        self.dataset1.data.axes[0].values = np.linspace(-10, 53, 420)
        self.dataset2.data.data = np.linspace(11, 14, 230)
        self.dataset2.data.axes[0].values = np.linspace(1, 44, 230)
        self.processing.datasets.append(self.dataset1)
        self.processing.datasets.append(self.dataset2)
        self.processing.process()
        self.assertListEqual(
            list(np.linspace(1, 44, 230)),
            list(self.dataset1.data.axes[0].values),
        )
        self.assertListEqual(
            list(np.linspace(1, 44, 230)),
            list(self.dataset2.data.axes[0].values),
        )
        self.assertTrue(
            np.array_equal(
                self.dataset1.data.axes[0].values,
                self.dataset2.data.axes[0].values,
            )
        )

    def test_process_interpolates_data_for_1d_datasets(self):
        self.dataset1.data.data = np.linspace(10, 15, 11)
        self.dataset1.data.axes[0].values = np.linspace(0, 5, 11)
        self.dataset2.data.data = np.linspace(11, 14, 11)
        self.dataset2.data.axes[0].values = np.linspace(1, 4, 11)
        self.processing.datasets.append(self.dataset1)
        self.processing.datasets.append(self.dataset2)
        self.processing.process()
        self.assertListEqual(
            list(np.linspace(11, 14, 7)), list(self.dataset1.data.data)
        )
        self.assertListEqual(
            list(np.linspace(11, 14, 7)), list(self.dataset2.data.data)
        )

    def test_process_interpolates_data_for_2d_datasets(self):
        axis0 = np.linspace(0, 5, 11)
        axis1 = np.linspace(0, 5, 11)
        rows, cols = np.meshgrid(axis0, axis1, indexing="ij")
        self.dataset1.data.data = np.sin(rows**2 + cols**2)
        self.dataset1.data.axes[0].values = axis0
        self.dataset1.data.axes[1].values = axis1
        axis0 = np.linspace(2, 4, 5)
        axis1 = np.linspace(2, 4, 5)
        rows, cols = np.meshgrid(axis0, axis1, indexing="ij")
        self.dataset2.data.data = np.sin(rows**2 + cols**2)
        self.dataset2.data.axes[0].values = axis0
        self.dataset2.data.axes[1].values = axis1
        self.processing.datasets.append(self.dataset1)
        self.processing.datasets.append(self.dataset2)
        self.processing.process()
        self.assertTrue(
            np.all(self.dataset2.data.data == self.dataset1.data.data)
        )

    def test_process_sets_npoints_for_3d_datasets(self):
        self.dataset1.data.data = np.random.random([11, 11, 11])
        self.dataset1.data.axes[0].values = np.linspace(0, 5, 11)
        self.dataset1.data.axes[1].values = np.linspace(10, 15, 11)
        self.dataset1.data.axes[2].values = np.linspace(20, 25, 11)
        self.dataset2.data.data = np.random.random([11, 11, 11])
        self.dataset2.data.axes[0].values = np.linspace(1, 4, 11)
        self.dataset2.data.axes[1].values = np.linspace(11, 14, 11)
        self.dataset2.data.axes[2].values = np.linspace(21, 24, 11)
        self.processing.datasets.append(self.dataset1)
        self.processing.datasets.append(self.dataset2)
        self.processing.process()
        self.assertEqual([7, 7, 7], self.processing.parameters["npoints"])

    def test_process_interpolates_data_for_3d_datasets(self):
        axis0 = np.linspace(0, 5, 11)
        axis1 = np.linspace(0, 5, 11)
        axis2 = np.linspace(0, 5, 11)
        xx, yy, zz = np.meshgrid(axis0, axis1, axis2, indexing="ij")
        self.dataset1.data.data = np.sin(xx**2 + yy**2 + zz**2)
        self.dataset1.data.axes[0].values = axis0
        self.dataset1.data.axes[1].values = axis1
        self.dataset1.data.axes[2].values = axis2
        axis0 = np.linspace(2, 4, 5)
        axis1 = np.linspace(2, 4, 5)
        axis2 = np.linspace(2, 4, 5)
        xx, yy, zz = np.meshgrid(axis0, axis1, axis2, indexing="ij")
        self.dataset2.data.data = np.sin(xx**2 + yy**2 + zz**2)
        self.dataset2.data.axes[0].values = axis0
        self.dataset2.data.axes[1].values = axis1
        self.dataset2.data.axes[2].values = axis2
        self.processing.datasets.append(self.dataset1)
        self.processing.datasets.append(self.dataset2)
        self.processing.process()
        self.assertTrue(
            np.all(self.dataset2.data.data == self.dataset1.data.data)
        )


class TestNoise(unittest.TestCase):
    def setUp(self):
        self.processing = aspecd.processing.Noise()
        self.dataset = aspecd.dataset.Dataset()
        self.dataset.data.data = np.zeros(2**12)
        self.dataset2d = aspecd.dataset.Dataset()
        self.dataset2d.data.data = np.zeros([2**10, 2**10])
        self.dataset3d = aspecd.dataset.Dataset()
        self.dataset3d.data.data = np.zeros([2**10, 2**5, 2**5])

    @staticmethod
    def slope_of_power_spectral_density(noise):
        frequencies, psd = scipy.signal.welch(noise)
        log_frequencies = np.log10(frequencies[2:-1])
        log_psd = np.log10(psd[2:-1])
        coefficients = np.polyfit(log_frequencies, log_psd, 1)
        return float(coefficients[0])

    def test_instantiate_class(self):
        pass

    def test_has_appropriate_description(self):
        self.assertIn("noise", self.processing.description.lower())

    def test_has_appropriate_reference(self):
        self.assertTrue(self.processing.references)
        self.assertIn("power law noise", self.processing.references[0].title)

    def test_is_undoable(self):
        self.assertTrue(self.processing.undoable)

    def test_process_adds_noise(self):
        self.dataset.process(self.processing)
        self.assertTrue(all(self.dataset.data.data))

    def test_white_noise_has_psd_slope_zero(self):
        self.processing.parameters["exponent"] = 0
        self.dataset.process(self.processing)
        self.assertAlmostEqual(
            0.0,
            self.slope_of_power_spectral_density(self.dataset.data.data),
            delta=0.1,
        )

    def test_white_nose_has_mean_of_zero(self):
        self.processing.parameters["exponent"] = 0
        self.dataset.process(self.processing)
        self.assertAlmostEqual(
            0.0, float(np.mean(self.dataset.data.data)), delta=0.1
        )

    def test_pink_noise_has_psd_slope_minus_one(self):
        self.processing.parameters["exponent"] = -1
        self.dataset.process(self.processing)
        self.assertAlmostEqual(
            -1.0,
            self.slope_of_power_spectral_density(self.dataset.data.data),
            delta=0.1,
        )

    def test_brownian_noise_has_psd_slope_minus_two(self):
        self.processing.parameters["exponent"] = -2
        self.dataset.process(self.processing)
        self.assertAlmostEqual(
            -2.0,
            self.slope_of_power_spectral_density(self.dataset.data.data),
            delta=0.1,
        )

    def test_normalised_noise_has_amplitude_of_one(self):
        self.processing.parameters["normalise"] = True
        self.dataset.process(self.processing)
        self.assertAlmostEqual(
            1, max(self.dataset.data.data) - min(self.dataset.data.data)
        )

    def test_normalised_noise_with_2d_has_amplitude_of_one(self):
        self.processing.parameters["normalise"] = True
        self.dataset2d.process(self.processing)
        self.assertAlmostEqual(
            1, self.dataset2d.data.data.max() - self.dataset2d.data.data.min()
        )

    def test_noise_with_given_amplitude(self):
        self.processing.parameters["amplitude"] = 0.01
        self.dataset.process(self.processing)
        self.assertAlmostEqual(
            0.01, max(self.dataset.data.data) - min(self.dataset.data.data)
        )

    def test_noise_with_given_amplitude_with_2d(self):
        self.processing.parameters["amplitude"] = 0.01
        self.dataset2d.process(self.processing)
        self.assertAlmostEqual(
            0.01,
            self.dataset2d.data.data.max() - self.dataset2d.data.data.min(),
        )

    def test_standard_is_pink_noise(self):
        self.dataset.process(self.processing)
        self.assertAlmostEqual(
            -1.0,
            self.slope_of_power_spectral_density(self.dataset.data.data),
            delta=0.1,
        )

    def test_2d_dataset(self):
        self.dataset2d.process(self.processing)
        self.assertTrue(self.dataset2d.data.data.all())

    def test_2d_dataset_with_pink_noise_is_pink_in_first_dimension_only(self):
        self.processing.parameters["exponent"] = -1
        self.dataset2d.process(self.processing)
        self.assertAlmostEqual(
            -1.0,
            self.slope_of_power_spectral_density(
                self.dataset2d.data.data[:, 0]
            ),
            delta=0.16,
        )
        self.assertAlmostEqual(
            0.0,
            self.slope_of_power_spectral_density(
                self.dataset2d.data.data[0, :]
            ),
            delta=0.16,
        )

    def test_3d_dataset(self):
        self.dataset3d.process(self.processing)
        self.assertTrue(self.dataset3d.data.data.all())


class TestChangeAxesValues(unittest.TestCase):
    def setUp(self):
        self.processing = aspecd.processing.ChangeAxesValues()
        self.dataset = aspecd.dataset.Dataset()
        self.dataset.data.data = np.zeros(2**5)
        self.dataset2d = aspecd.dataset.Dataset()
        self.dataset2d.data.data = np.zeros([2**5, 2**5])
        self.dataset3d = aspecd.dataset.Dataset()
        self.dataset3d.data.data = np.zeros([2**5, 2**5, 2**5])

    def test_instantiate_class(self):
        pass

    def test_has_appropriate_description(self):
        self.assertIn(
            "change axis values", self.processing.description.lower()
        )

    def test_is_undoable(self):
        self.assertTrue(self.processing.undoable)

    def test_change_axis_of_1d_dataset_to_given_range(self):
        new_range = [35, 42]
        self.processing.parameters["range"] = new_range
        self.dataset.process(self.processing)
        self.assertEqual(new_range[0], self.dataset.data.axes[0].values[0])
        self.assertEqual(new_range[1], self.dataset.data.axes[0].values[-1])
        self.assertEqual(
            len(self.dataset.data.data), len(self.dataset.data.axes[0].values)
        )

    def test_change_2nd_axis_of_1d_dataset_to_given_range(self):
        new_range = [35, 42]
        self.processing.parameters["range"] = new_range
        self.processing.parameters["axes"] = 1
        self.dataset2d.process(self.processing)
        self.assertEqual(new_range[0], self.dataset2d.data.axes[1].values[0])
        self.assertEqual(new_range[1], self.dataset2d.data.axes[1].values[-1])
        self.assertEqual(
            len(self.dataset2d.data.data),
            len(self.dataset2d.data.axes[1].values),
        )

    def test_change_2nd_axis_of_1d_dataset_leaves_1st_axis_alone(self):
        new_range = [35, 42]
        self.processing.parameters["range"] = new_range
        self.processing.parameters["axes"] = 1
        old_axes_values = self.dataset2d.data.axes[0].values
        self.dataset2d.process(self.processing)
        self.assertListEqual(
            list(old_axes_values), list(self.dataset2d.data.axes[0].values)
        )

    def test_change_2nd_axis_of_1d_dataset_raises(self):
        new_range = [35, 42]
        self.processing.parameters["range"] = new_range
        self.processing.parameters["axes"] = 1
        with self.assertRaisesRegex(
            IndexError, "Index out of range for axes"
        ):
            self.dataset.process(self.processing)

    def test_change_both_axes_of_2d_dataset(self):
        new_range = [[35, 42], [17.5, 21]]
        self.processing.parameters["range"] = new_range
        self.dataset2d.process(self.processing)
        self.assertEqual(
            new_range[0][0], self.dataset2d.data.axes[0].values[0]
        )
        self.assertEqual(
            new_range[0][1], self.dataset2d.data.axes[0].values[-1]
        )
        self.assertEqual(
            new_range[1][0], self.dataset2d.data.axes[1].values[0]
        )
        self.assertEqual(
            new_range[1][1], self.dataset2d.data.axes[1].values[-1]
        )

    def test_incompatible_number_of_ranges_and_axes_raises(self):
        new_range = [[35, 42], [17.5, 21]]
        self.processing.parameters["range"] = new_range
        self.processing.parameters["axes"] = 1
        with self.assertRaisesRegex(
            IndexError, "Axes and ranges must be compatible"
        ):
            self.dataset2d.process(self.processing)


class TestRelativeAxis(unittest.TestCase):
    def setUp(self):
        self.processing = aspecd.processing.RelativeAxis()
        axis_length = 2**5
        self.dataset = aspecd.dataset.Dataset()
        self.dataset.data.data = np.zeros(axis_length)
        self.dataset.data.axes[0].values = np.linspace(340, 350, axis_length)
        self.dataset2d = aspecd.dataset.Dataset()
        self.dataset2d.data.data = np.zeros([axis_length, axis_length])
        self.dataset2d.data.axes[0].values = np.linspace(
            340, 350, axis_length
        )
        self.dataset2d.data.axes[0].values = np.linspace(0, 10, axis_length)

    def test_instantiate_class(self):
        pass

    def test_has_appropriate_description(self):
        self.assertIn(
            "change axis to relative axis",
            self.processing.description.lower(),
        )

    def test_is_undoable(self):
        self.assertTrue(self.processing.undoable)

    def test_origin_is_set_to_floored_centre_if_not_given(self):
        # Here is a mistake, as we subtract the index from the axis values!
        origin_index = int(len(self.dataset.data.axes[0].values) / 2)
        origin = self.dataset.data.axes[0].values[origin_index]
        processing_step = self.dataset.process(self.processing)
        self.assertEqual(processing_step.parameters["origin"], origin)

    def test_axis_values_are_correct_with_no_origin_given(self):
        origin_index = int(len(self.dataset.data.axes[0].values) / 2)
        origin = self.dataset.data.axes[0].values[origin_index]
        original_axis = copy.copy(self.dataset.data.axes[0].values)
        self.dataset.process(self.processing)
        self.assertEqual(
            original_axis[0] - origin, self.dataset.data.axes[0].values[0]
        )
        self.assertEqual(
            original_axis[-1] - origin, self.dataset.data.axes[0].values[-1]
        )

    def test_axis_values_are_correct_with_origin_given(self):
        origin = 343
        original_axis = copy.copy(self.dataset.data.axes[0].values)
        self.processing.parameters["origin"] = origin
        self.dataset.process(self.processing)
        self.assertEqual(
            original_axis[0] - origin, self.dataset.data.axes[0].values[0]
        )
        self.assertEqual(
            original_axis[-1] - origin, self.dataset.data.axes[0].values[-1]
        )

    def test_origin_outside_axis_range_warns(self):
        origin = -343
        self.processing.parameters["origin"] = origin
        with self.assertLogs(__package__, level="WARNING") as cm:
            self.dataset.process(self.processing)
        self.assertIn("outside axis range", cm.output[0])

    def test_with_2d_dataset_and_no_axis_given_sets_first_axis(self):
        origin = 343
        original_axis_0 = copy.copy(self.dataset2d.data.axes[0].values)
        original_axis_1 = copy.copy(self.dataset2d.data.axes[1].values)
        self.processing.parameters["origin"] = origin
        self.dataset2d.process(self.processing)
        self.assertEqual(
            original_axis_0[0] - origin, self.dataset2d.data.axes[0].values[0]
        )
        self.assertEqual(
            original_axis_0[-1] - origin,
            self.dataset2d.data.axes[0].values[-1],
        )
        self.assertListEqual(
            list(original_axis_1), list(self.dataset2d.data.axes[1].values)
        )

    def test_with_2d_dataset_and_axis_sets_correct_axis(self):
        origin = 3
        axis = 1
        original_axis_0 = copy.copy(self.dataset2d.data.axes[0].values)
        original_axis_1 = copy.copy(self.dataset2d.data.axes[1].values)
        self.processing.parameters["origin"] = origin
        self.processing.parameters["axis"] = axis
        self.dataset2d.process(self.processing)
        self.assertEqual(
            original_axis_1[0] - origin, self.dataset2d.data.axes[1].values[0]
        )
        self.assertEqual(
            original_axis_1[-1] - origin,
            self.dataset2d.data.axes[1].values[-1],
        )
        self.assertListEqual(
            list(original_axis_0), list(self.dataset2d.data.axes[0].values)
        )

    # Add "Delta" to axis quantity
    def test_delta_added_to_axis_quantity(self):
        self.dataset.process(self.processing)
        self.assertTrue(self.dataset.data.axes[0].quantity.startswith("Δ"))
