"""Tests for analysis."""

import unittest

from aspecd import analysis, processing, dataset


class TestAnalysisStep(unittest.TestCase):
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


class TestSingleAnalysisStep(unittest.TestCase):
    def setUp(self):
        self.analysisstep = analysis.SingleAnalysisStep()

    def test_instantiate_class(self):
        pass

    def test_has_preprocessing_property(self):
        self.assertTrue(hasattr(self.analysisstep, 'preprocessing'))

    def test_preprocessing_is_list(self):
        self.assertTrue(isinstance(self.analysisstep.preprocessing, list))

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

    def test_has_create_history_record_method(self):
        self.assertTrue(hasattr(self.analysisstep, 'create_history_record'))
        self.assertTrue(callable(self.analysisstep.create_history_record))

    def test_create_history_record_returns_history_record(self):
        self.analysisstep.dataset = dataset.Dataset()
        history_record = self.analysisstep.create_history_record()
        self.assertTrue(isinstance(history_record,
                                   analysis.AnalysisHistoryRecord))


class TestMultiAnalysisStep(unittest.TestCase):
    def setUp(self):
        self.analysisstep = analysis.MultiAnalysisStep()

    def test_instantiate_class(self):
        pass

    def test_has_datasets_property(self):
        self.assertTrue(hasattr(self.analysisstep, 'datasets'))

    def test_datasets_property_is_list(self):
        self.assertTrue(isinstance(self.analysisstep.datasets, list))

    def test_analyse_without_datasets_raises(self):
        with self.assertRaises(analysis.MissingDatasetError):
            self.analysisstep.analyse()

    def test_analyse_with_datasets(self):
        self.analysisstep.datasets.append(dataset.Dataset())
        self.analysisstep.analyse()


class TestPreprocessing(unittest.TestCase):
    def setUp(self):
        self.analysisstep = analysis.SingleAnalysisStep()
        self.processingstep = processing.ProcessingStep()

    def test_has_add_preprocessing_step_method(self):
        self.assertTrue(hasattr(self.analysisstep, 'add_preprocessing_step'))
        self.assertTrue(callable(self.analysisstep.add_preprocessing_step))

    def test_add_processing_step_copies_processingstep_object(self):
        self.analysisstep.add_preprocessing_step(self.processingstep)
        self.assertIsNot(self.processingstep,
                         self.analysisstep.preprocessing[-1])


class TestAnalysisStepRecord(unittest.TestCase):
    def setUp(self):
        self.analysis_step = analysis.AnalysisStep()
        self.analysis_record = \
            analysis.AnalysisStepRecord(self.analysis_step)

    def test_instantiate_class(self):
        pass

    def test_instantiate_without_analysis_step_raises(self):
        with self.assertRaises(analysis.MissingAnalysisStepError):
            analysis.AnalysisStepRecord()

    def test_instantiate_class_with_analysis_step(self):
        analysis.AnalysisStepRecord(self.analysis_step)

    def test_instantiate_description_from_analysis_step(self):
        self.analysis_step.description = 'Test'
        analysis_record = \
            analysis.AnalysisStepRecord(self.analysis_step)
        self.assertEqual(analysis_record.description, 'Test')

    def test_has_create_analysis_step_method(self):
        self.assertTrue(hasattr(self.analysis_record,
                                'create_analysis_step'))
        self.assertTrue(
            callable(self.analysis_record.create_analysis_step))

    def test_create_analysis_step_returns_analysis_object(self):
        test_object = self.analysis_record.create_analysis_step()
        self.assertTrue(isinstance(test_object, analysis.AnalysisStep))

    def test_has_parameters_property(self):
        self.assertTrue(hasattr(self.analysis_record, 'parameters'))

    def test_analysis_object_has_correct_parameters_value(self):
        self.analysis_record.parameters['test'] = True
        test_object = self.analysis_record.create_analysis_step()
        self.assertEqual(test_object.parameters['test'], True)

    def test_has_description_property(self):
        self.assertTrue(hasattr(self.analysis_record, 'description'))

    def test_analysis_object_has_correct_description_value(self):
        self.analysis_record.description = 'Test'
        test_object = self.analysis_record.create_analysis_step()
        self.assertEqual(test_object.description, 'Test')

    def test_has_class_name_property(self):
        self.assertTrue(hasattr(self.analysis_record, 'class_name'))

    def test_has_comment_property(self):
        self.assertTrue(hasattr(self.analysis_record, 'comment'))

    def test_analysis_object_gets_correct_parameters_value(self):
        test_dictionary = dict(bla='blub', foo='bar')
        self.analysis_step.parameters = test_dictionary
        self.analysis_record = \
            analysis.AnalysisStepRecord(self.analysis_step)
        test_object = self.analysis_record.create_analysis_step()
        self.assertEqual(test_object.parameters, test_dictionary)

    def test_analysis_object_gets_correct_comment_value(self):
        test_comment = 'Frobnicate the bizbaz'
        self.analysis_step.comment = test_comment
        self.analysis_record= \
            analysis.AnalysisStepRecord(self.analysis_step)
        test_object = self.analysis_record.create_analysis_step()
        self.assertEqual(test_object.comment, test_comment)


class TestSingleAnalysisStepRecord(unittest.TestCase):
    def setUp(self):
        self.analysis_step = analysis.SingleAnalysisStep()
        self.analysis_record = \
            analysis.SingleAnalysisStepRecord(self.analysis_step)

    def test_instantiate_class(self):
        pass


class TestAnalysisHistoryRecord(unittest.TestCase):
    def setUp(self):
        self.analysis_step = analysis.SingleAnalysisStep()
        self.historyrecord = \
            analysis.AnalysisHistoryRecord(self.analysis_step)

    def test_instantiate_class(self):
        pass

    def test_instantiate_class_with_package_name(self):
        analysis.AnalysisHistoryRecord(analysis_step=self.analysis_step,
                                       package="numpy")

    def test_instantiate_class_with_package_name_sets_sysinfo(self):
        analysis_step = analysis.AnalysisHistoryRecord(
            analysis_step=self.analysis_step, package="numpy")
        self.assertTrue("numpy" in analysis_step.sysinfo.packages.keys())

    def test_has_analysis_property(self):
        self.assertTrue(hasattr(self.historyrecord, 'analysis'))

    def test_analysis_is_analysissteprecord(self):
        self.assertTrue(isinstance(self.historyrecord.analysis,
                                   analysis.SingleAnalysisStepRecord))

    def test_has_replay_method(self):
        self.assertTrue(hasattr(self.historyrecord, 'replay'))
        self.assertTrue(callable(self.historyrecord.replay))

    def test_replay(self):
        self.historyrecord.replay(dataset.Dataset())
