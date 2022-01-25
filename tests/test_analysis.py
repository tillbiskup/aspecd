"""Tests for analysis."""

import unittest

import numpy as np
import scipy.signal

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

    def test_has_references_property(self):
        self.assertTrue(hasattr(self.analysisstep, 'references'))

    def test_description_references_is_list(self):
        self.assertTrue(isinstance(self.analysisstep.references, list))

    def test_has_index_property(self):
        self.assertTrue(hasattr(self.analysisstep, 'index'))

    def test_index_is_list(self):
        self.assertTrue(isinstance(self.analysisstep.index, list))

    def test_has_analyse_method(self):
        self.assertTrue(hasattr(self.analysisstep, 'analyse'))
        self.assertTrue(callable(self.analysisstep.analyse))

    def test_has_analyze_method(self):
        self.assertTrue(hasattr(self.analysisstep, 'analyze'))
        self.assertTrue(callable(self.analysisstep.analyze))

    def test_has_applicable_method(self):
        self.assertTrue(hasattr(self.analysisstep, 'applicable'))
        self.assertTrue(callable(self.analysisstep.applicable))

    def test_create_dataset_creates_calculated_dataset(self):
        self.assertIsInstance(self.analysisstep.create_dataset(),
                              aspecd.dataset.CalculatedDataset)

    def test_created_dataset_has_correct_type_in_metadata(self):
        dataset = self.analysisstep.create_dataset()
        self.assertEqual(self.analysisstep.name,
                         dataset.metadata.calculation.type)

    def test_created_dataset_contains_parameters_in_metadata(self):
        self.analysisstep.parameters["foo"] = "bar"
        dataset = self.analysisstep.create_dataset()
        self.assertDictEqual(self.analysisstep.parameters,
                             dataset.metadata.calculation.parameters)

    def test_create_dataset_with_dataset_type_returns_correct_type(self):
        self.analysisstep.dataset_type = 'aspecd.dataset.CalculatedDataset'
        self.assertIsInstance(self.analysisstep.create_dataset(),
                              aspecd.dataset.CalculatedDataset)

    def test_has_to_dict_method(self):
        self.assertTrue(hasattr(self.analysisstep, 'to_dict'))
        self.assertTrue(callable(self.analysisstep.to_dict))

    def test_to_dict_does_not_contain_certain_keys(self):
        for key in ['name', 'description', 'references', 'result']:
            with self.subTest(key=key):
                self.assertNotIn(key, self.analysisstep.to_dict())


class TestSingleAnalysisStep(unittest.TestCase):
    def setUp(self):
        self.analysisstep = aspecd.analysis.SingleAnalysisStep()

    def test_instantiate_class(self):
        pass

    def test_has_preprocessing_property(self):
        self.assertTrue(hasattr(self.analysisstep, 'preprocessing'))

    def test_preprocessing_is_list(self):
        self.assertTrue(isinstance(self.analysisstep.preprocessing, list))

    def test_to_dict_does_not_contain_certain_keys(self):
        for key in ['dataset']:
            with self.subTest(key=key):
                self.assertNotIn(key, self.analysisstep.to_dict())

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

    def test_analyse_checks_applicability(self):
        class MyAnalysisStep(aspecd.analysis.SingleAnalysisStep):

            @staticmethod
            def applicable(dataset):
                return False

        dataset_ = aspecd.dataset.Dataset()
        analysis = MyAnalysisStep()
        with self.assertRaises(aspecd.exceptions.NotApplicableToDatasetError):
            dataset_.analyse(analysis)

    def test_analyse_checks_applicability_prints_helpful_message(self):
        class MyAnalysisStep(aspecd.analysis.SingleAnalysisStep):

            @staticmethod
            def applicable(dataset):
                return False

        dataset_ = aspecd.dataset.Dataset()
        dataset_.id = "foo"
        analysis = MyAnalysisStep()
        message = "MyAnalysisStep not applicable to dataset with id foo"
        with self.assertRaisesRegex(
                aspecd.exceptions.NotApplicableToDatasetError, message):
            dataset_.analyse(analysis)

    def test_dataset_contains_parameters_obtained_during_analysis(self):

        class MyAnalysisStep(aspecd.analysis.SingleAnalysisStep):
            def _perform_task(self):
                self.result = self.create_dataset()
                self.parameters['foo'] = 'bar'

        dataset_ = aspecd.dataset.Dataset()
        analysis = MyAnalysisStep()
        new_analysis = dataset_.analyse(analysis)
        self.assertIn('foo',
                      new_analysis.result.metadata.calculation.parameters)

    def test_returned_dataset_contains_correct_origdata(self):

        class MyAnalysisStep(aspecd.analysis.SingleAnalysisStep):
            def _perform_task(self):
                self.result = self.create_dataset()
                self.result.data.data = np.random.random(5)

        dataset_ = aspecd.dataset.Dataset()
        analysis = MyAnalysisStep()
        new_analysis = dataset_.analyse(analysis)
        new_dataset = new_analysis.result
        self.assertListEqual(list(new_dataset.data.data),
                             list(new_dataset._origdata.data))


class TestMultiAnalysisStep(unittest.TestCase):
    def setUp(self):
        self.analysisstep = aspecd.analysis.MultiAnalysisStep()

    def test_instantiate_class(self):
        pass

    def test_to_dict_does_not_contain_certain_keys(self):
        for key in ['datasets']:
            with self.subTest(key=key):
                self.assertNotIn(key, self.analysisstep.to_dict())

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

    def test_analyse_checks_applicability(self):
        dataset1 = aspecd.dataset.Dataset()
        dataset1.data.data = np.random.random([5, 5])
        dataset2 = aspecd.dataset.Dataset()
        dataset2.data.data = np.random.random(5)

        class MyAnalysisStep(aspecd.analysis.MultiAnalysisStep):
            @staticmethod
            def applicable(dataset):
                return len(dataset.data.axes) == 2

        analysis_step = MyAnalysisStep()
        analysis_step.datasets.append(dataset1)
        analysis_step.datasets.append(dataset2)
        with self.assertRaises(aspecd.exceptions.NotApplicableToDatasetError):
            analysis_step.analyse()

    def test_analyse_checks_applicability_prints_helpful_message(self):
        dataset1 = aspecd.dataset.Dataset()
        dataset1.data.data = np.random.random([5, 5])
        dataset1.id = "foo"
        dataset2 = aspecd.dataset.Dataset()
        dataset2.data.data = np.random.random(5)
        dataset2.id = "bar"

        class MyAnalysisStep(aspecd.analysis.MultiAnalysisStep):
            @staticmethod
            def applicable(dataset):
                return len(dataset.data.axes) == 2

        analysis_step = MyAnalysisStep()
        analysis_step.datasets.append(dataset1)
        analysis_step.datasets.append(dataset2)
        message = "MyAnalysisStep not applicable to dataset with id foo"
        with self.assertRaisesRegex(
                aspecd.exceptions.NotApplicableToDatasetError, message):
            analysis_step.analyse()

    def test_returned_dataset_contains_correct_origdata(self):

        class MyAnalysisStep(aspecd.analysis.MultiAnalysisStep):
            def _perform_task(self):
                self.result = self.create_dataset()
                self.result.data.data = np.random.random(5)

        analysis_step = MyAnalysisStep()
        analysis_step.datasets.append(aspecd.dataset.Dataset())
        analysis_step.analyse()
        new_dataset = analysis_step.result
        self.assertListEqual(list(new_dataset.data.data),
                             list(new_dataset._origdata.data))


class TestAggregatedAnalysisStep(unittest.TestCase):
    def setUp(self):
        self.analysis = aspecd.analysis.AggregatedAnalysisStep()
        self.analysis.datasets.append(aspecd.dataset.Dataset())
        self.analysis.analysis_step = 'BasicCharacteristics'
        self.analysis.parameters["kind"] = "min"
        self.analysis.datasets[0].data.data = np.zeros(5)
        self.analysis.datasets[0].label = 'foo'

    def test_instantiate_class(self):
        pass

    def test_has_datasets_property(self):
        self.assertTrue(hasattr(self.analysis, 'datasets'))

    def test_datasets_property_is_list(self):
        self.assertTrue(isinstance(self.analysis.datasets, list))

    def test_has_analysis_step_property(self):
        self.assertTrue(hasattr(self.analysis, 'analysis_step'))

    def test_has_appropriate_description(self):
        self.assertIn('Aggregated analysis step for multiple datasets',
                      self.analysis.description)

    def test_to_dict_does_not_contain_certain_keys(self):
        for key in ['datasets', 'result']:
            with self.subTest(key=key):
                self.assertNotIn(key, self.analysis.to_dict())

    def test_analyse_without_datasets_raises(self):
        self.analysis.datasets = []
        with self.assertRaises(aspecd.exceptions.MissingDatasetError):
            self.analysis.analyse()

    def test_analyse_without_analysis_step_raises(self):
        self.analysis.analysis_step = ''
        with self.assertRaises(aspecd.exceptions.MissingAnalysisStepError):
            self.analysis.analyse()

    def test_analyse_with_analysis_step_returning_dataset_raises(self):
        self.analysis.analysis_step = 'PowerDensitySpectrum'
        with self.assertRaisesRegex(ValueError,
                                    'Analysis step .* returns dataset'):
            self.analysis.analyse()

    def test_analyse_returns_calculated_dataset_in_result(self):
        self.analysis.analyse()
        self.assertIsInstance(self.analysis.result,
                              aspecd.dataset.CalculatedDataset)

    def test_result_has_calculation_type_set_correctly(self):
        self.analysis.analyse()
        self.assertEqual('aspecd.analysis.AggregatedAnalysisStep',
                         self.analysis.result.metadata.calculation.type)

    def test_analyse_sets_correct_value_in_result(self):
        self.analysis.analyse()
        self.assertEqual(min(self.analysis.datasets[0].data.data),
                         self.analysis.result.data.data[0])

    def test_analyse_with_full_class_name(self):
        self.analysis.analysis_step = 'aspecd.analysis.BasicCharacteristics'
        self.analysis.analyse()
        self.assertEqual(min(self.analysis.datasets[0].data.data),
                         self.analysis.result.data.data[0])

    def test_analyse_sets_index_in_result(self):
        self.analysis.analyse()
        self.assertEqual(self.analysis.datasets[0].label,
                         self.analysis.result.data.axes[0].index[0])

    def test_analyse_with_multiple_datasets_sets_correct_values_in_result(self):
        self.analysis.datasets.append(aspecd.dataset.Dataset())
        self.analysis.datasets[1].data.data = np.ones(5)
        self.analysis.datasets[1].label = 'bar'
        self.analysis.analyse()
        self.assertEqual(min(self.analysis.datasets[0].data.data),
                         self.analysis.result.data.data[0])
        self.assertEqual(min(self.analysis.datasets[1].data.data),
                         self.analysis.result.data.data[1])

    def test_analyse_with_multiple_datasets_sets_index_in_result(self):
        self.analysis.datasets.append(aspecd.dataset.Dataset())
        self.analysis.datasets[1].data.data = np.ones(5)
        self.analysis.datasets[1].label = 'bar'
        self.analysis.analyse()
        self.assertEqual(self.analysis.datasets[1].label,
                         self.analysis.result.data.axes[0].index[1])

    def test_analyse_with_list_return_sets_correct_value_in_result(self):
        self.analysis.parameters["output"] = "indices"
        self.analysis.datasets[0].data.data = np.zeros([5, 5])
        self.analysis.analyse()
        self.assertEqual(self.analysis.datasets[0].data.data.ndim,
                         len(self.analysis.result.data.data[0, :]))

    def test_analyse_with_list_return_and_multiple_datasets(self):
        self.analysis.parameters["output"] = "indices"
        self.analysis.datasets[0].data.data = np.zeros([5, 5])
        self.analysis.datasets.append(aspecd.dataset.Dataset())
        self.analysis.datasets[1].data.data = np.ones([3, 3])
        self.analysis.datasets.append(aspecd.dataset.Dataset())
        self.analysis.datasets[2].data.data = np.random.random([4, 4])
        self.analysis.analyse()
        self.assertEqual((3, 2), self.analysis.result.data.data.shape)

    def test_returned_dataset_contains_correct_origdata(self):
        self.analysis.analyse()
        self.assertListEqual(list(self.analysis.result.data.data),
                             list(self.analysis.result._origdata.data))


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

    def test_min_sets_kind_in_index(self):
        self.analysis.parameters["kind"] = "min"
        analysis = self.dataset.analyse(self.analysis)
        self.assertEqual([self.analysis.parameters["kind"]], analysis.index)

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
        self.assertEqual(list(result_dict.values()), analysis.result)
        self.assertEqual(list(result_dict.keys()), analysis.index)

    def test_min_with_axes_output(self):
        self.analysis.parameters["kind"] = "min"
        self.analysis.parameters["output"] = "axes"
        analysis = self.dataset.analyse(self.analysis)
        result = \
            [self.dataset.data.axes[0].values[self.dataset.data.data.argmin()]]
        self.assertEqual(result, analysis.result)

    def test_min_with_axes_output_sets_index(self):
        self.analysis.parameters["kind"] = "min"
        self.analysis.parameters["output"] = "axes"
        self.dataset.data.axes[0].quantity = 'foo'
        analysis = self.dataset.analyse(self.analysis)
        index = ['min(foo)']
        self.assertEqual(index, analysis.index)

    def test_max_with_axes_output(self):
        self.analysis.parameters["kind"] = "max"
        self.analysis.parameters["output"] = "axes"
        analysis = self.dataset.analyse(self.analysis)
        result = \
            [self.dataset.data.axes[0].values[self.dataset.data.data.argmax()]]
        self.assertEqual(result, analysis.result)

    def test_max_with_axes_output_sets_index(self):
        self.analysis.parameters["kind"] = "max"
        self.analysis.parameters["output"] = "axes"
        self.dataset.data.axes[0].quantity = 'foo'
        analysis = self.dataset.analyse(self.analysis)
        index = ['max(foo)']
        self.assertEqual(index, analysis.index)

    def test_min_with_indices_output(self):
        self.analysis.parameters["kind"] = "min"
        self.analysis.parameters["output"] = "indices"
        analysis = self.dataset.analyse(self.analysis)
        self.assertEqual([self.dataset.data.data.argmin()], analysis.result)

    def test_min_with_indices_output_sets_index(self):
        self.analysis.parameters["kind"] = "min"
        self.analysis.parameters["output"] = "indices"
        analysis = self.dataset.analyse(self.analysis)
        index = ['min(index0)']
        self.assertEqual(index, analysis.index)

    def test_max_with_indices_output(self):
        self.analysis.parameters["kind"] = "max"
        self.analysis.parameters["output"] = "indices"
        analysis = self.dataset.analyse(self.analysis)
        self.assertEqual([self.dataset.data.data.argmax()], analysis.result)

    def test_max_with_indices_output_sets_index(self):
        self.analysis.parameters["kind"] = "max"
        self.analysis.parameters["output"] = "indices"
        analysis = self.dataset.analyse(self.analysis)
        index = ['max(index0)']
        self.assertEqual(index, analysis.index)

    def test_area_or_amplitude_with_axes_output_raises(self):
        characteristics = ["area", "amplitude"]
        self.analysis.parameters["output"] = "axes"
        for characteristic in characteristics:
            with self.subTest(characteristic=characteristic):
                self.analysis.parameters["kind"] = characteristic
                with self.assertRaisesRegex(ValueError,
                                            "Output %s not available for "
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
                                            "Output %s not available for "
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
        self.assertEqual(list(result_dict.values()), analysis.result)

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


class TestBlindSNREstimation(unittest.TestCase):
    def setUp(self):
        self.analysis = aspecd.analysis.BlindSNREstimation()
        self.dataset = aspecd.dataset.Dataset()
        self.dataset.data.data = np.random.random(10)

    def test_instantiate_class(self):
        pass

    def test_has_appropriate_description(self):
        self.assertIn('blind signal-to-noise ratio estimation',
                      self.analysis.description.lower())

    def test_analyse_without_method_sets_method_to_simple(self):
        analysis = self.dataset.analyse(self.analysis)
        self.assertEqual(analysis.parameters["method"], "simple")

    def test_simple_method(self):
        analysis = self.dataset.analyse(self.analysis)
        result = self.dataset.data.data.mean()/self.dataset.data.data.std()
        self.assertEqual(result, analysis.result)

    def test_simple_squared_method(self):
        self.analysis.parameters["method"] = "simple_squared"
        analysis = self.dataset.analyse(self.analysis)
        result = \
            self.dataset.data.data.mean()**2/self.dataset.data.data.std()**2
        self.assertEqual(result, analysis.result)

    def test_der_snr_method_with_too_small_sample_raises(self):
        self.dataset.data.data = np.random.random(3)
        self.analysis.parameters["method"] = "der_snr"
        with self.assertRaisesRegex(ValueError, "Too few samples"):
            self.dataset.analyse(self.analysis)

    def test_der_snr_method(self):
        self.analysis.parameters["method"] = "der_snr"
        analysis = self.dataset.analyse(self.analysis)
        self.assertGreater(analysis.result, 0)


class TestPeakFinding(unittest.TestCase):
    def setUp(self):
        self.analysis = aspecd.analysis.PeakFinding()
        self.dataset = aspecd.dataset.Dataset()
        self.dataset.data.data = np.sin(np.linspace(0, 8*np.pi, num=1000))
        self.noisy_dataset = aspecd.dataset.Dataset()
        self.noisy_dataset.data.data = np.sin(np.linspace(0, 8*np.pi, num=1000))
        self.noisy_dataset.data.data \
            += (np.random.random(len(self.noisy_dataset.data.data))-0.5)*0.2

    def test_instantiate_class(self):
        pass

    def test_has_appropriate_description(self):
        self.assertIn('peak finding', self.analysis.description.lower())

    def test_with_nd_dataset_raises(self):
        self.dataset.data.data = np.random.random([5, 5])
        with self.assertRaises(aspecd.exceptions.NotApplicableToDatasetError):
            self.dataset.analyse(self.analysis)

    def test_analyse_returns_peak_positions(self):
        analysis = self.dataset.analyse(self.analysis)
        result, _ = scipy.signal.find_peaks(self.dataset.data.data)
        self.assertListEqual(list(result), list(analysis.result))

    def test_analyse_returns_peak_positions_in_axis_values(self):
        self.dataset.data.axes[0].values = \
            np.linspace(340, 350, len(self.dataset.data.data))
        analysis = self.dataset.analyse(self.analysis)
        result, _ = scipy.signal.find_peaks(self.dataset.data.data)
        result = self.dataset.data.axes[0].values[result]
        self.assertListEqual(list(result), list(analysis.result))

    def test_analyse_returns_properties(self):
        self.analysis.parameters["return_properties"] = True
        analysis = self.dataset.analyse(self.analysis)
        result, _ = scipy.signal.find_peaks(self.dataset.data.data)
        self.assertListEqual(list(result), list(analysis.result[0]))
        self.assertEqual(dict, type(analysis.result[1]))

    def test_analyse_returns_dataset(self):
        self.analysis.parameters["return_dataset"] = True
        analysis = self.dataset.analyse(self.analysis)
        result, _ = scipy.signal.find_peaks(self.dataset.data.data)
        self.assertListEqual(list(result),
                             list(analysis.result.data.axes[0].values))
        self.assertEqual(aspecd.dataset.CalculatedDataset,
                         type(analysis.result))
        self.assertEqual(self.analysis.name,
                         analysis.result.metadata.calculation.type)
        self.assertDictEqual(self.analysis.parameters,
                             analysis.result.metadata.calculation.parameters)

    def test_analyse_returns_negative_peak_positions(self):
        self.analysis.parameters["negative_peaks"] = True
        analysis = self.dataset.analyse(self.analysis)
        positive, _ = scipy.signal.find_peaks(self.dataset.data.data)
        negative, _ = scipy.signal.find_peaks(-self.dataset.data.data)
        result = np.sort(np.concatenate((positive, negative)))
        self.assertListEqual(list(result), list(analysis.result))

    def test_analyse_with_negative_peaks_does_not_return_properties(self):
        self.analysis.parameters["negative_peaks"] = True
        self.analysis.parameters["return_properties"] = True
        analysis = self.dataset.analyse(self.analysis)
        positive, _ = scipy.signal.find_peaks(self.dataset.data.data)
        negative, _ = scipy.signal.find_peaks(-self.dataset.data.data)
        result = np.sort(np.concatenate((positive, negative)))
        self.assertListEqual(list(result), list(analysis.result))

    def test_analyse_with_height(self):
        self.analysis.parameters["height"] = 1
        analysis = self.noisy_dataset.analyse(self.analysis)
        result, _ = scipy.signal.find_peaks(
            self.noisy_dataset.data.data,
            height=self.analysis.parameters["height"])
        self.assertListEqual(list(result), list(analysis.result))

    def test_analyse_with_height_with_negative_peak_positions(self):
        self.analysis.parameters["negative_peaks"] = True
        self.analysis.parameters["height"] = 1
        analysis = self.noisy_dataset.analyse(self.analysis)
        positive, _ = scipy.signal.find_peaks(
            self.noisy_dataset.data.data,
            height=self.analysis.parameters["height"])
        negative, _ = scipy.signal.find_peaks(
            -self.noisy_dataset.data.data,
            height=self.analysis.parameters["height"])
        result = np.sort(np.concatenate((positive, negative)))
        self.assertListEqual(list(result), list(analysis.result))

    def test_analyse_with_threshold(self):
        self.analysis.parameters["threshold"] = 0.145
        analysis = self.noisy_dataset.analyse(self.analysis)
        result, _ = scipy.signal.find_peaks(
            self.noisy_dataset.data.data,
            threshold=self.analysis.parameters["threshold"])
        self.assertListEqual(list(result), list(analysis.result))

    def test_analyse_with_threshold_with_negative_peak_positions(self):
        self.analysis.parameters["negative_peaks"] = True
        self.analysis.parameters["threshold"] = 0.145
        analysis = self.noisy_dataset.analyse(self.analysis)
        positive, _ = scipy.signal.find_peaks(
            self.noisy_dataset.data.data,
            threshold=self.analysis.parameters["threshold"])
        negative, _ = scipy.signal.find_peaks(
            -self.noisy_dataset.data.data,
            threshold=self.analysis.parameters["threshold"])
        result = np.sort(np.concatenate((positive, negative)))
        self.assertListEqual(list(result), list(analysis.result))

    def test_analyse_with_distance(self):
        self.analysis.parameters["distance"] = 100
        analysis = self.noisy_dataset.analyse(self.analysis)
        result, _ = scipy.signal.find_peaks(
            self.noisy_dataset.data.data,
            distance=self.analysis.parameters["distance"])
        self.assertListEqual(list(result), list(analysis.result))

    def test_analyse_with_distance_with_negative_peak_positions(self):
        self.analysis.parameters["negative_peaks"] = True
        self.analysis.parameters["distance"] = 100
        analysis = self.noisy_dataset.analyse(self.analysis)
        positive, _ = scipy.signal.find_peaks(
            self.noisy_dataset.data.data,
            distance=self.analysis.parameters["distance"])
        negative, _ = scipy.signal.find_peaks(
            -self.noisy_dataset.data.data,
            distance=self.analysis.parameters["distance"])
        result = np.sort(np.concatenate((positive, negative)))
        self.assertListEqual(list(result), list(analysis.result))

    def test_analyse_with_prominence(self):
        self.analysis.parameters["prominence"] = 0.2
        analysis = self.noisy_dataset.analyse(self.analysis)
        result, _ = scipy.signal.find_peaks(
            self.noisy_dataset.data.data,
            prominence=self.analysis.parameters["prominence"])
        self.assertListEqual(list(result), list(analysis.result))

    def test_analyse_with_prominence_with_negative_peak_positions(self):
        self.analysis.parameters["negative_peaks"] = True
        self.analysis.parameters["prominence"] = 0.2
        analysis = self.noisy_dataset.analyse(self.analysis)
        positive, _ = scipy.signal.find_peaks(
            self.noisy_dataset.data.data,
            prominence=self.analysis.parameters["prominence"])
        negative, _ = scipy.signal.find_peaks(
            -self.noisy_dataset.data.data,
            prominence=self.analysis.parameters["prominence"])
        result = np.sort(np.concatenate((positive, negative)))
        self.assertListEqual(list(result), list(analysis.result))

    def test_analyse_with_width(self):
        self.analysis.parameters["width"] = 5
        analysis = self.noisy_dataset.analyse(self.analysis)
        result, _ = scipy.signal.find_peaks(
            self.noisy_dataset.data.data,
            width=self.analysis.parameters["width"])
        self.assertListEqual(list(result), list(analysis.result))

    def test_analyse_with_width_with_negative_peak_positions(self):
        self.analysis.parameters["negative_peaks"] = True
        self.analysis.parameters["width"] = 5
        analysis = self.noisy_dataset.analyse(self.analysis)
        positive, _ = scipy.signal.find_peaks(
            self.noisy_dataset.data.data,
            width=self.analysis.parameters["width"])
        negative, _ = scipy.signal.find_peaks(
            -self.noisy_dataset.data.data,
            width=self.analysis.parameters["width"])
        result = np.sort(np.concatenate((positive, negative)))
        self.assertListEqual(list(result), list(analysis.result))


class TestPowerDensitySpectrum(unittest.TestCase):
    def setUp(self):
        self.analysis = aspecd.analysis.PowerDensitySpectrum()
        self.dataset = aspecd.dataset.Dataset()
        self.dataset.data.data = np.zeros(2**12)
        noise = aspecd.processing.Noise()
        self.dataset.process(noise)

    def test_instantiate_class(self):
        pass

    def test_has_appropriate_description(self):
        self.assertIn('power density spectrum',
                      self.analysis.description.lower())

    def test_with_nd_dataset_raises(self):
        self.dataset.data.data = np.random.random([5, 5])
        with self.assertRaises(aspecd.exceptions.NotApplicableToDatasetError):
            self.dataset.analyse(self.analysis)

    def test_returns_calculated_dataset(self):
        analysis = self.dataset.analyse(self.analysis)
        self.assertIsInstance(analysis.result, aspecd.dataset.CalculatedDataset)

    def test_returned_data_are_log_of_psd(self):
        frequencies, psd = scipy.signal.periodogram(self.dataset.data.data)
        log_psd = np.log10(psd[1:])
        analysis = self.dataset.analyse(self.analysis)
        self.assertListEqual(list(log_psd), list(analysis.result.data.data))

    def test_returned_axes_values_are_log_of_frequency(self):
        frequencies, psd = scipy.signal.periodogram(self.dataset.data.data)
        log_frequencies = np.log10(frequencies[1:])
        analysis = self.dataset.analyse(self.analysis)
        self.assertListEqual(list(log_frequencies),
                             list(analysis.result.data.axes[0].values))

    def test_axes_quantities_are_sensible(self):
        analysis = self.dataset.analyse(self.analysis)
        self.assertEqual('log frequency', analysis.result.data.axes[0].quantity)
        self.assertEqual('log power', analysis.result.data.axes[1].quantity)

    def test_method_settable_via_parameter(self):
        self.analysis.parameters["method"] = "welch"
        frequencies, psd = scipy.signal.welch(self.dataset.data.data)
        log_psd = np.log10(psd[1:])
        analysis = self.dataset.analyse(self.analysis)
        self.assertListEqual(list(log_psd), list(analysis.result.data.data))

    def test_method_defaults_to_periodogram(self):
        self.assertEqual("periodogram", self.analysis.parameters["method"])


class TestPolynomialFit(unittest.TestCase):
    def setUp(self):
        self.analysis = aspecd.analysis.PolynomialFit()
        self.dataset = aspecd.dataset.Dataset()
        self.dataset.data.data = np.linspace(0, 49)

    def test_instantiate_class(self):
        pass

    def test_has_appropriate_description(self):
        self.assertIn('polynomial fit', self.analysis.description.lower())

    def test_with_nd_dataset_raises(self):
        self.dataset.data.data = np.random.random([5, 5])
        with self.assertRaises(aspecd.exceptions.NotApplicableToDatasetError):
            self.dataset.analyse(self.analysis)

    def test_default_is_first_order(self):
        self.assertEqual(1, self.analysis.parameters["order"])

    def test_first_order_returns_two_coefficients_as_result(self):
        analysis = self.dataset.analyse(self.analysis)
        self.assertEqual(2, len(analysis.result))

    def test_first_order_returns_correct_coefficients(self):
        analysis = self.dataset.analyse(self.analysis)
        self.assertAlmostEqual(0, analysis.result[0])
        self.assertAlmostEqual(1, analysis.result[1])

    def test_zeroth_order_returns_correct_coefficients(self):
        self.analysis.parameters["order"] = 0
        analysis = self.dataset.analyse(self.analysis)
        self.assertAlmostEqual(24.5, analysis.result[0])


class TestLinearRegressionWithFixedIntercept(unittest.TestCase):
    def setUp(self):
        self.analysis = aspecd.analysis.LinearRegressionWithFixedIntercept()
        self.dataset = aspecd.dataset.Dataset()
        self.dataset.data.data = np.linspace(1, 50)
        self.dataset.data.axes[0].values = np.linspace(0.5, 25)

    def test_instantiate_class(self):
        pass

    def test_has_appropriate_description(self):
        self.assertIn('linear regression without intercept',
                      self.analysis.description.lower())

    def test_with_nd_dataset_raises(self):
        self.dataset.data.data = np.random.random([5, 5])
        with self.assertRaises(aspecd.exceptions.NotApplicableToDatasetError):
            self.dataset.analyse(self.analysis)

    def test_analysis_returns_correct_coefficient_as_result(self):
        analysis = self.dataset.analyse(self.analysis)
        self.assertAlmostEqual(2., analysis.result)

    def test_regression_with_constant_offset(self):
        self.dataset.data.data += np.pi
        self.analysis.parameters["offset"] = np.pi
        analysis = self.dataset.analyse(self.analysis)
        self.assertAlmostEqual(2., analysis.result)

    def test_polynomial_compatible_coefficients(self):
        self.dataset.data.data += np.pi
        self.analysis.parameters["offset"] = np.pi
        self.analysis.parameters["polynomial_coefficients"] = True
        analysis = self.dataset.analyse(self.analysis)
        self.assertAlmostEqual(np.pi, analysis.result[0])
        self.assertAlmostEqual(2., analysis.result[1])
