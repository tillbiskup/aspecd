"""Tests for analysis."""

import unittest

import numpy as np

import aspecd.analysis
import aspecd.dataset
import aspecd.exceptions
import aspecd.history
import aspecd.processing


class TestAnalysisStep(unittest.TestCase):
    def setUp(self):
        self.analysisstep = aspecd.analysis.AnalysisStep()

    def test_instantiate_class(self):
        pass

    def test_has_name_property(self):
        self.assertTrue(hasattr(self.analysisstep, 'name'))

    def test_name_property_equals_class_name(self):
        class_name = 'aspecd.analysis.AnalysisStep'
        self.assertEqual(self.analysisstep.name, class_name)

    def test_has_parameters_property(self):
        self.assertTrue(hasattr(self.analysisstep, 'parameters'))

    def test_parameters_property_is_dict(self):
        self.assertTrue(isinstance(self.analysisstep.parameters, dict))

    def test_has_result_property(self):
        self.assertTrue(hasattr(self.analysisstep, 'result'))

    def test_has_description_property(self):
        self.assertTrue(hasattr(self.analysisstep, 'description'))

    def test_description_property_is_string(self):
        self.assertTrue(isinstance(self.analysisstep.description, str))

    def test_has_comment_property(self):
        self.assertTrue(hasattr(self.analysisstep, 'comment'))

    def test_description_comment_is_string(self):
        self.assertTrue(isinstance(self.analysisstep.comment, str))

    def test_has_analyse_method(self):
        self.assertTrue(hasattr(self.analysisstep, 'analyse'))
        self.assertTrue(callable(self.analysisstep.analyse))

    def test_has_analyze_method(self):
        self.assertTrue(hasattr(self.analysisstep, 'analyze'))
        self.assertTrue(callable(self.analysisstep.analyze))

    def test_has_applicable_method(self):
        self.assertTrue(hasattr(self.analysisstep, 'applicable'))
        self.assertTrue(callable(self.analysisstep.applicable))


class TestSingleAnalysisStep(unittest.TestCase):
    def setUp(self):
        self.analysisstep = aspecd.analysis.SingleAnalysisStep()

    def test_instantiate_class(self):
        pass

    def test_has_preprocessing_property(self):
        self.assertTrue(hasattr(self.analysisstep, 'preprocessing'))

    def test_preprocessing_is_list(self):
        self.assertTrue(isinstance(self.analysisstep.preprocessing, list))

    def test_analyse_with_dataset(self):
        test_dataset = aspecd.dataset.Dataset()
        self.analysisstep.analyse(test_dataset)
        self.assertGreater(len(test_dataset.analyses), 0)

    def test_analyse_without_argument_and_with_dataset(self):
        self.analysisstep.dataset = aspecd.dataset.Dataset()
        self.analysisstep.analyse()
        self.assertGreater(len(self.analysisstep.dataset.analyses), 0)

    def test_analyse_without_analysisstep_nor_dataset_raises(self):
        with self.assertRaises(aspecd.exceptions.MissingDatasetError):
            self.analysisstep.analyse()

    def test_analyse_returns_dataset(self):
        test_dataset = self.analysisstep.analyse(aspecd.dataset.Dataset())
        self.assertTrue(isinstance(test_dataset, aspecd.dataset.Dataset))

    def test_has_create_history_record_method(self):
        self.assertTrue(hasattr(self.analysisstep, 'create_history_record'))
        self.assertTrue(callable(self.analysisstep.create_history_record))

    def test_create_history_record_returns_history_record(self):
        self.analysisstep.dataset = aspecd.dataset.Dataset()
        history_record = self.analysisstep.create_history_record()
        self.assertTrue(isinstance(history_record,
                                   aspecd.history.AnalysisHistoryRecord))


class TestMultiAnalysisStep(unittest.TestCase):
    def setUp(self):
        self.analysisstep = aspecd.analysis.MultiAnalysisStep()

    def test_instantiate_class(self):
        pass

    def test_has_datasets_property(self):
        self.assertTrue(hasattr(self.analysisstep, 'datasets'))

    def test_datasets_property_is_list(self):
        self.assertTrue(isinstance(self.analysisstep.datasets, list))

    def test_analyse_without_datasets_raises(self):
        with self.assertRaises(aspecd.exceptions.MissingDatasetError):
            self.analysisstep.analyse()

    def test_analyse_with_datasets(self):
        self.analysisstep.datasets.append(aspecd.dataset.Dataset())
        self.analysisstep.analyse()


class TestPreprocessing(unittest.TestCase):
    def setUp(self):
        self.analysisstep = aspecd.analysis.SingleAnalysisStep()
        self.processingstep = aspecd.processing.SingleProcessingStep()

    def test_has_add_preprocessing_step_method(self):
        self.assertTrue(hasattr(self.analysisstep, 'add_preprocessing_step'))
        self.assertTrue(callable(self.analysisstep.add_preprocessing_step))

    def test_add_processing_step_copies_processingstep_object(self):
        self.analysisstep.add_preprocessing_step(self.processingstep)
        self.assertIsNot(self.processingstep,
                         self.analysisstep.preprocessing[-1])


class TestBasicCharacteristics(unittest.TestCase):
    def setUp(self):
        self.analysis = aspecd.analysis.BasicCharacteristics()
        self.dataset = aspecd.dataset.Dataset()
        self.dataset.data.data = np.random.random(10)
        self.dataset3d = aspecd.dataset.Dataset()
        self.dataset3d.data.data = np.random.random([10, 10, 10])

    def test_instantiate_class(self):
        pass

    def test_has_appropriate_description(self):
        self.assertIn('basic characteristics',
                      self.analysis.description.lower())

    def test_analyse_without_kind_raises(self):
        with self.assertRaisesRegex(ValueError,
                                    "No kind of characteristics given"):
            self.dataset.analyse(self.analysis)

    def test_analyse_with_unknown_kind_raises(self):
        self.analysis.parameters["kind"] = "foo"
        with self.assertRaisesRegex(ValueError,
                                    "Unknown kind foo"):
            self.dataset.analyse(self.analysis)

    def test_analyse_with_unknown_output_raises(self):
        self.analysis.parameters["kind"] = "min"
        self.analysis.parameters["output"] = "foo"
        with self.assertRaisesRegex(ValueError,
                                    "Unknown output type foo"):
            self.dataset.analyse(self.analysis)

    def test_min(self):
        self.analysis.parameters["kind"] = "min"
        analysis = self.dataset.analyse(self.analysis)
        self.assertEqual(self.dataset.data.data.min(), analysis.result)

    def test_max(self):
        self.analysis.parameters["kind"] = "max"
        analysis = self.dataset.analyse(self.analysis)
        self.assertEqual(self.dataset.data.data.max(), analysis.result)

    def test_amplitude(self):
        self.analysis.parameters["kind"] = "amplitude"
        analysis = self.dataset.analyse(self.analysis)
        self.assertEqual(
            self.dataset.data.data.max()-self.dataset.data.data.min(),
            analysis.result)

    def test_area(self):
        self.analysis.parameters["kind"] = "area"
        analysis = self.dataset.analyse(self.analysis)
        self.assertEqual(self.dataset.data.data.sum(), analysis.result)

    def test_all(self):
        self.analysis.parameters["kind"] = "all"
        result_dict = {
            'min': self.dataset.data.data.min(),
            'max': self.dataset.data.data.max(),
            'amplitude':
                self.dataset.data.data.max() - self.dataset.data.data.min(),
            'area': self.dataset.data.data.sum(),
        }
        analysis = self.dataset.analyse(self.analysis)
        self.assertEqual(result_dict, analysis.result)

    def test_min_with_axes_output(self):
        self.analysis.parameters["kind"] = "min"
        self.analysis.parameters["output"] = "axes"
        analysis = self.dataset.analyse(self.analysis)
        result = \
            [self.dataset.data.axes[0].values[self.dataset.data.data.argmin()]]
        self.assertEqual(result, analysis.result)

    def test_max_with_axes_output(self):
        self.analysis.parameters["kind"] = "max"
        self.analysis.parameters["output"] = "axes"
        analysis = self.dataset.analyse(self.analysis)
        result = \
            [self.dataset.data.axes[0].values[self.dataset.data.data.argmax()]]
        self.assertEqual(result, analysis.result)

    def test_min_with_indices_output(self):
        self.analysis.parameters["kind"] = "min"
        self.analysis.parameters["output"] = "indices"
        analysis = self.dataset.analyse(self.analysis)
        self.assertEqual([self.dataset.data.data.argmin()], analysis.result)

    def test_max_with_indices_output(self):
        self.analysis.parameters["kind"] = "max"
        self.analysis.parameters["output"] = "indices"
        analysis = self.dataset.analyse(self.analysis)
        self.assertEqual([self.dataset.data.data.argmax()], analysis.result)

    def test_area_or_amplitude_with_axes_output_raises(self):
        characteristics = ["area", "amplitude"]
        self.analysis.parameters["output"] = "axes"
        for characteristic in characteristics:
            with self.subTest(characteristic=characteristic):
                self.analysis.parameters["kind"] = characteristic
                with self.assertRaisesRegex(ValueError,
                                            "Output %s not available for "\
                                            "characteristic %s."
                                            % ("axes", characteristic)):
                    self.dataset.analyse(self.analysis)

    def test_area_or_amplitude_with_indices_output_raises(self):
        characteristics = ["area", "amplitude"]
        self.analysis.parameters["output"] = "indices"
        for characteristic in characteristics:
            with self.subTest(characteristic=characteristic):
                self.analysis.parameters["kind"] = characteristic
                with self.assertRaisesRegex(ValueError,
                                            "Output %s not available for "\
                                            "characteristic %s."
                                            % ("indices", characteristic)):
                    self.dataset.analyse(self.analysis)

    def test_min_with_3d_data(self):
        self.analysis.parameters["kind"] = "min"
        analysis = self.dataset3d.analyse(self.analysis)
        self.assertEqual(self.dataset3d.data.data.min(), analysis.result)

    def test_max_with_3d_data(self):
        self.analysis.parameters["kind"] = "max"
        analysis = self.dataset3d.analyse(self.analysis)
        self.assertEqual(self.dataset3d.data.data.max(), analysis.result)

    def test_amplitude_with_3d_data(self):
        self.analysis.parameters["kind"] = "amplitude"
        analysis = self.dataset3d.analyse(self.analysis)
        self.assertEqual(
            self.dataset3d.data.data.max()-self.dataset3d.data.data.min(),
            analysis.result)

    def test_area_with_3d_data(self):
        self.analysis.parameters["kind"] = "area"
        analysis = self.dataset3d.analyse(self.analysis)
        self.assertEqual(self.dataset3d.data.data.sum(), analysis.result)

    def test_all_with_3d_data(self):
        self.analysis.parameters["kind"] = "all"
        result_dict = {
            'min': self.dataset3d.data.data.min(),
            'max': self.dataset3d.data.data.max(),
            'amplitude':
                self.dataset3d.data.data.max() - self.dataset3d.data.data.min(),
            'area': self.dataset3d.data.data.sum(),
        }
        analysis = self.dataset3d.analyse(self.analysis)
        self.assertEqual(result_dict, analysis.result)

    def test_min_with_axes_output_with_3d_data(self):
        self.analysis.parameters["kind"] = "min"
        self.analysis.parameters["output"] = "axes"
        analysis = self.dataset3d.analyse(self.analysis)
        result = []
        idx = np.unravel_index(self.dataset3d.data.data.argmin(),
                               self.dataset3d.data.data.shape)
        for dim in range(self.dataset3d.data.data.ndim):
            result.append(self.dataset3d.data.axes[dim].values[idx[dim]])
        self.assertEqual(result, analysis.result)

    def test_max_with_axes_output_with_3d_data(self):
        self.analysis.parameters["kind"] = "max"
        self.analysis.parameters["output"] = "axes"
        analysis = self.dataset3d.analyse(self.analysis)
        result = []
        idx = np.unravel_index(self.dataset3d.data.data.argmax(),
                               self.dataset3d.data.data.shape)
        for dim in range(self.dataset3d.data.data.ndim):
            result.append(self.dataset3d.data.axes[dim].values[idx[dim]])
        self.assertEqual(result, analysis.result)

    def test_min_with_indices_output_with_3d_data(self):
        self.analysis.parameters["kind"] = "min"
        self.analysis.parameters["output"] = "indices"
        analysis = self.dataset3d.analyse(self.analysis)
        result = list(np.unravel_index(self.dataset3d.data.data.argmin(),
                                       self.dataset3d.data.data.shape))
        self.assertListEqual(result, analysis.result)

    def test_max_with_indices_output_with_3d_data(self):
        self.analysis.parameters["kind"] = "max"
        self.analysis.parameters["output"] = "indices"
        analysis = self.dataset3d.analyse(self.analysis)
        result = list(np.unravel_index(self.dataset3d.data.data.argmax(),
                                       self.dataset3d.data.data.shape))
        self.assertListEqual(result, analysis.result)


class TestBasicStatistics(unittest.TestCase):
    def setUp(self):
        self.analysis = aspecd.analysis.BasicStatistics()
        self.dataset = aspecd.dataset.Dataset()
        self.dataset.data.data = np.random.random(10)
        self.dataset3d = aspecd.dataset.Dataset()
        self.dataset3d.data.data = np.random.random([10, 10, 10])

    def test_instantiate_class(self):
        pass

    def test_has_appropriate_description(self):
        self.assertIn('basic statistics',
                      self.analysis.description.lower())

    def test_analyse_without_kind_raises(self):
        with self.assertRaisesRegex(ValueError,
                                    "No kind of statistics given"):
            self.dataset.analyse(self.analysis)

    def test_analyse_with_unknown_kind_raises(self):
        self.analysis.parameters["kind"] = "foo"
        with self.assertRaisesRegex(ValueError,
                                    "Unknown kind foo"):
            self.dataset.analyse(self.analysis)

    def test_mean_with_1d_data(self):
        self.analysis.parameters["kind"] = "mean"
        analysis = self.dataset.analyse(self.analysis)
        self.assertEqual(np.mean(self.dataset.data.data), analysis.result)

    def test_median_with_1d_data(self):
        self.analysis.parameters["kind"] = "median"
        analysis = self.dataset.analyse(self.analysis)
        self.assertEqual(np.median(self.dataset.data.data), analysis.result)

    def test_std_with_1d_data(self):
        self.analysis.parameters["kind"] = "std"
        analysis = self.dataset.analyse(self.analysis)
        self.assertEqual(np.std(self.dataset.data.data), analysis.result)

    def test_var_with_1d_data(self):
        self.analysis.parameters["kind"] = "var"
        analysis = self.dataset.analyse(self.analysis)
        self.assertEqual(np.var(self.dataset.data.data), analysis.result)

    def test_mean_with_3d_data(self):
        self.analysis.parameters["kind"] = "mean"
        analysis = self.dataset3d.analyse(self.analysis)
        self.assertEqual(np.mean(self.dataset3d.data.data), analysis.result)

    def test_median_with_3d_data(self):
        self.analysis.parameters["kind"] = "median"
        analysis = self.dataset3d.analyse(self.analysis)
        self.assertEqual(np.median(self.dataset3d.data.data), analysis.result)

    def test_std_with_3d_data(self):
        self.analysis.parameters["kind"] = "std"
        analysis = self.dataset3d.analyse(self.analysis)
        self.assertEqual(np.std(self.dataset3d.data.data), analysis.result)

    def test_var_with_3d_data(self):
        self.analysis.parameters["kind"] = "var"
        analysis = self.dataset3d.analyse(self.analysis)
        self.assertEqual(np.var(self.dataset3d.data.data), analysis.result)


class TestSignalToNoiseRatio(unittest.TestCase):
    def setUp(self):
        self.analysis = aspecd.analysis.SignalToNoiseRatio()

    def test_instantiate_class(self):
        pass

    def test_has_appropriate_description(self):
        self.assertIn('signal-to-noise ratio',
                      self.analysis.description.lower())
