"""Tests for history."""

import unittest
from datetime import datetime, timedelta

import aspecd.history
import aspecd.system
from aspecd import processing, dataset


class TestHistoryRecord(unittest.TestCase):
    def setUp(self):
        self.history_record = aspecd.history.HistoryRecord()

    def test_instantiate_class(self):
        pass

    def test_instantiate_class_with_package_name(self):
        aspecd.history.HistoryRecord(package="aspecd")

    def test_instantiate_class_with_package_name_sets_sysinfo(self):
        history = aspecd.history.HistoryRecord(package="numpy")
        self.assertTrue("numpy" in history.sysinfo.packages.keys())

    def test_has_date_property(self):
        self.assertTrue(hasattr(self.history_record, 'date'))

    def test_date_is_datetime(self):
        self.assertTrue(isinstance(self.history_record.date, datetime))

    def test_date_is_current_date(self):
        now = datetime.today()
        # noinspection PyTypeChecker
        self.assertAlmostEqual(now, self.history_record.date,
                               delta=timedelta(seconds=1))

    def test_has_sysinfo_property(self):
        self.assertTrue(hasattr(self.history_record, 'sysinfo'))

    def test_sysinfo_is_systeminfo(self):
        self.assertTrue(
            isinstance(self.history_record.sysinfo, aspecd.system.SystemInfo))

    def test_has_to_dict_method(self):
        self.assertTrue(hasattr(self.history_record, 'to_dict'))
        self.assertTrue(callable(self.history_record.to_dict))

    def test_has_from_dict_method(self):
        self.assertTrue(hasattr(self.history_record, 'from_dict'))
        self.assertTrue(callable(self.history_record.from_dict))

    def test_from_dict_sets_date(self):
        orig_dict = self.history_record.to_dict()
        new_history_record = aspecd.history.HistoryRecord()
        new_history_record.from_dict(orig_dict)
        self.assertEqual(self.history_record.date, new_history_record.date)

    def test_from_dict_sets_sysinfo(self):
        orig_dict = self.history_record.to_dict()
        orig_dict["sysinfo"]["user"]["login"] = 'foo'
        new_history_record = aspecd.history.HistoryRecord()
        new_history_record.from_dict(orig_dict)
        self.assertEqual(orig_dict["sysinfo"]["user"]["login"],
                         new_history_record.sysinfo.user["login"])

    def test_from_dict_sets_arbitrary_existing_attribute(self):
        orig_dict = self.history_record.to_dict()
        orig_dict["foo"] = "bar"
        new_history_record = aspecd.history.HistoryRecord()
        new_history_record.foo = ''
        new_history_record.from_dict(orig_dict)
        self.assertEqual(orig_dict["foo"], new_history_record.foo)

    def test_from_dict_ignores_arbitrary_non_existing_attribute(self):
        orig_dict = self.history_record.to_dict()
        orig_dict["foo"] = "bar"
        new_history_record = aspecd.history.HistoryRecord()
        new_history_record.from_dict(orig_dict)
        self.assertFalse(hasattr(new_history_record, 'foo'))


class TestProcessingStepRecord(unittest.TestCase):
    def setUp(self):
        self.processing_step = processing.ProcessingStep()
        self.processing_record = \
            aspecd.history.ProcessingStepRecord(self.processing_step)

    def test_instantiate_class(self):
        aspecd.history.ProcessingStepRecord()

    def test_instantiate_class_with_processing_step(self):
        aspecd.history.ProcessingStepRecord(self.processing_step)

    def test_instantiate_description_from_processing_step(self):
        self.processing_step.description = 'Test'
        processing_record = \
            aspecd.history.ProcessingStepRecord(self.processing_step)
        self.assertEqual(processing_record.description, 'Test')

    def test_has_from_processing_step_method(self):
        self.assertTrue(hasattr(self.processing_record, 'from_processing_step'))
        self.assertTrue(callable(self.processing_record.from_processing_step))

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
            aspecd.history.ProcessingStepRecord(self.processing_step)
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
            aspecd.history.ProcessingStepRecord(self.processing_step)
        test_object = self.processing_record.create_processing_step()
        self.assertEqual(test_object.comment, test_comment)

    def test_has_to_dict_method(self):
        self.assertTrue(hasattr(self.processing_record, 'to_dict'))
        self.assertTrue(callable(self.processing_record.to_dict))

    def test_from_dict(self):
        orig_dict = self.processing_record.to_dict()
        orig_dict["comment"] = 'foo'
        new_processing_record = \
            aspecd.history.ProcessingStepRecord(self.processing_step)
        new_processing_record.from_dict(orig_dict)
        self.assertDictEqual(orig_dict, new_processing_record.to_dict())


class TestProcessingHistoryRecord(unittest.TestCase):
    def setUp(self):
        self.processing_step = processing.ProcessingStep()
        self.historyrecord = \
            aspecd.history.ProcessingHistoryRecord(self.processing_step)

    def test_instantiate_class(self):
        pass

    def test_instantiate_class_with_processing_step(self):
        aspecd.history.ProcessingHistoryRecord(self.processing_step)

    def test_instantiate_class_with_package_name(self):
        aspecd.history.ProcessingHistoryRecord(
            processing_step=self.processing_step, package="numpy")

    def test_instantiate_class_with_package_name_sets_sysinfo(self):
        processing_step = aspecd.history.ProcessingHistoryRecord(
            processing_step=self.processing_step,
            package="numpy")
        self.assertTrue("numpy" in processing_step.sysinfo.packages.keys())

    def test_has_processing_property(self):
        self.assertTrue(hasattr(self.historyrecord, 'processing'))

    def test_processing_is_processingsteprecord(self):
        self.assertTrue(isinstance(self.historyrecord.processing,
                                   aspecd.history.ProcessingStepRecord))

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