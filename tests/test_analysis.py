"""Tests for analysis."""

import unittest

from aspecd import analysis, processing, dataset


class TestAnalysis(unittest.TestCase):
    def setUp(self):
        self.analysisstep = analysis.AnalysisStep()

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

    def test_has_results_property(self):
        self.assertTrue(hasattr(self.analysisstep, 'results'))

    def test_parameters_results_is_dict(self):
        self.assertTrue(isinstance(self.analysisstep.results, dict))

    def test_has_preprocessing_property(self):
        self.assertTrue(hasattr(self.analysisstep, 'preprocessing'))

    def test_parameters_preprocessing_is_list(self):
        self.assertTrue(isinstance(self.analysisstep.preprocessing, list))

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

    def test_analyse_with_dataset(self):
        test_dataset = dataset.Dataset()
        self.analysisstep.analyse(test_dataset)
        self.assertGreater(len(test_dataset.analyses), 0)

    def test_analyse_without_argument_and_with_dataset(self):
        self.analysisstep.dataset = dataset.Dataset()
        self.analysisstep.analyse()
        self.assertGreater(len(self.analysisstep.dataset.analyses), 0)

    def test_analyse_without_analysisstep_nor_dataset_raises(self):
        with self.assertRaises(analysis.MissingDatasetError):
            self.analysisstep.analyse()

    def test_analyse_returns_dataset(self):
        test_dataset = self.analysisstep.analyse(dataset.Dataset())
        self.assertTrue(isinstance(test_dataset, dataset.Dataset))

    def test_has_resulting_dataset_property(self):
        self.assertTrue(hasattr(self.analysisstep, 'resulting_dataset'))

    def test_resulting_dataset_is_calculated_dataset(self):
        self.assertTrue(isinstance(self.analysisstep.resulting_dataset,
                                   dataset.CalculatedDataset))

    def test_has_create_history_record_method(self):
        self.assertTrue(hasattr(self.analysisstep, 'create_history_record'))
        self.assertTrue(callable(self.analysisstep.create_history_record))

    def test_create_history_record_returns_history_record(self):
        self.analysisstep.dataset = dataset.Dataset()
        history_record = self.analysisstep.create_history_record()
        self.assertTrue(isinstance(history_record,
                                   analysis.AnalysisHistoryRecord))


class TestPreprocessing(unittest.TestCase):
    def setUp(self):
        self.analysisstep = analysis.AnalysisStep()
        self.processingstep = processing.ProcessingStep()

    def test_has_add_preprocessing_step_method(self):
        self.assertTrue(hasattr(self.analysisstep, 'add_preprocessing_step'))
        self.assertTrue(callable(self.analysisstep.add_preprocessing_step))

    def test_add_processing_step_copies_processingstep_object(self):
        self.analysisstep.add_preprocessing_step(self.processingstep)
        self.assertIsNot(self.processingstep,
                         self.analysisstep.preprocessing[-1])


class TestAnalysisHistoryRecord(unittest.TestCase):
    def setUp(self):
        self.historyrecord = analysis.AnalysisHistoryRecord()

    def test_instantiate_class(self):
        pass

    def test_instantiate_class_with_package_name(self):
        analysis.AnalysisHistoryRecord(package="numpy")

    def test_instantiate_class_with_package_name_sets_sysinfo(self):
        analysis_step = analysis.AnalysisHistoryRecord(package="numpy")
        self.assertTrue("numpy" in analysis_step.sysinfo.packages.keys())

    def test_has_analysis_property(self):
        self.assertTrue(hasattr(self.historyrecord, 'analysis'))

    def test_analysis_is_analysisstep(self):
        self.assertTrue(isinstance(self.historyrecord.analysis,
                                   analysis.AnalysisStep))
