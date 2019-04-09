"""Tests for processing."""

import unittest

import aspecd.processing
from aspecd import processing, dataset, utils


class TestProcessingStep(unittest.TestCase):
    def setUp(self):
        self.processing = processing.ProcessingStep()

    def test_instantiate_class(self):
        pass

    def test_has_undoable_property(self):
        self.assertTrue(hasattr(self.processing, 'undoable'))

    def test_has_name_property(self):
        self.assertTrue(hasattr(self.processing, 'name'))

    def test_name_property_equals_full_class_name(self):
        full_class_name = utils.full_class_name(self.processing)
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

    def test_process_with_dataset_writes_history(self):
        test_dataset = self.processing.process(dataset=dataset.Dataset())
        self.assertGreater(len(test_dataset.history), 0)

    def test_process_with_dataset_using_dataset_process_writes_history(self):
        test_dataset = dataset.Dataset()
        test_dataset.process(self.processing)
        self.assertGreater(len(test_dataset.history), 0)

    def test_process_returns_dataset(self):
        test_dataset = self.processing.process(dataset.Dataset())
        self.assertTrue(isinstance(test_dataset, dataset.Dataset))

    def test_has_create_history_record_method(self):
        self.assertTrue(hasattr(self.processing, 'create_history_record'))
        self.assertTrue(callable(self.processing.create_history_record))

    def test_create_history_record_returns_history_record(self):
        self.processing.dataset = dataset.Dataset()
        history_record = self.processing.create_history_record()
        self.assertTrue(isinstance(history_record,
                                   processing.ProcessingHistoryRecord))


class TestProcessingStepRecord(unittest.TestCase):
    def setUp(self):
        self.processing_step = processing.ProcessingStep()
        self.processing_record = \
            processing.ProcessingStepRecord(self.processing_step)

    def test_instantiate_class(self):
        pass

    def test_instantiate_without_processing_step_raises(self):
        with self.assertRaises(processing.MissingProcessingStepError):
            processing.ProcessingStepRecord()

    def test_instantiate_class_with_processing_step(self):
        processing.ProcessingStepRecord(self.processing_step)

    def test_instantiate_description_from_processing_step(self):
        self.processing_step.description = 'Test'
        processing_record = \
            processing.ProcessingStepRecord(self.processing_step)
        self.assertEqual(processing_record.description, 'Test')

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

    def test_has_comment_property(self):
        self.assertTrue(hasattr(self.processing_record, 'comment'))

    def test_processing_object_gets_correct_parameters_value(self):
        test_dictionary = dict(bla='blub', foo='bar')
        self.processing_step.parameters = test_dictionary
        self.processing_record = \
            processing.ProcessingStepRecord(self.processing_step)
        test_object = self.processing_record.create_processing_step()
        self.assertEqual(test_object.parameters, test_dictionary)

    def test_processing_object_gets_correct_undoable_value(self):
        self.processing_record.undoable = True
        test_object = self.processing_record.create_processing_step()
        self.assertEqual(test_object.undoable, True)

    def test_processing_object_gets_correct_comment_value(self):
        test_comment = 'Frobnicate the bizbaz'
        self.processing_step.comment = test_comment
        self.processing_record = \
            processing.ProcessingStepRecord(self.processing_step)
        test_object = self.processing_record.create_processing_step()
        self.assertEqual(test_object.comment, test_comment)


class TestProcessingHistoryRecord(unittest.TestCase):
    def setUp(self):
        self.processing_step = processing.ProcessingStep()
        self.historyrecord = \
            aspecd.processing.ProcessingHistoryRecord(self.processing_step)

    def test_instantiate_class(self):
        pass

    def test_instantiate_class_with_processing_step(self):
        aspecd.processing.ProcessingHistoryRecord(self.processing_step)

    def test_instantiate_class_with_package_name(self):
        aspecd.processing.ProcessingHistoryRecord(
            processing_step=self.processing_step, package="numpy")

    def test_instantiate_class_with_package_name_sets_sysinfo(self):
        processing_step = aspecd.processing.ProcessingHistoryRecord(
            processing_step=self.processing_step,
            package="numpy")
        self.assertTrue("numpy" in processing_step.sysinfo.packages.keys())

    def test_has_processing_property(self):
        self.assertTrue(hasattr(self.historyrecord, 'processing'))

    def test_processing_is_processingsteprecord(self):
        self.assertTrue(isinstance(self.historyrecord.processing,
                                   processing.ProcessingStepRecord))

    def test_has_date_property(self):
        self.assertTrue(hasattr(self.historyrecord, 'date'))

    def test_has_sysinfo_property(self):
        self.assertTrue(hasattr(self.historyrecord, 'sysinfo'))

    def test_has_undoable_property(self):
        self.assertTrue(hasattr(self.historyrecord, 'undoable'))

    def test_undoable_is_boolean(self):
        self.assertTrue(isinstance(self.historyrecord.undoable, bool))

    def test_has_replay_method(self):
        self.assertTrue(hasattr(self.historyrecord, 'replay'))
        self.assertTrue(callable(self.historyrecord.replay))

    def test_replay(self):
        self.historyrecord.replay(dataset.Dataset())
