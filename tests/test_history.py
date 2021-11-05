"""Tests for history."""

import unittest
from datetime import datetime, timedelta

import aspecd.annotation
import aspecd.exceptions
import aspecd.history
import aspecd.system
import aspecd.utils
from aspecd import processing, dataset, analysis, plotting, table


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
        self.processing_step = processing.SingleProcessingStep()
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
        self.assertTrue(isinstance(test_object, processing.SingleProcessingStep))

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

    def test_has_references_property(self):
        self.assertTrue(hasattr(self.processing_record, 'references'))

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

    def test_processing_object_gets_correct_references_value(self):
        self.processing_step.references = ['foo']
        self.processing_record = \
            aspecd.history.ProcessingStepRecord(self.processing_step)
        test_object = self.processing_record.create_processing_step()
        self.assertEqual(test_object.references, ['foo'])

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
        self.processing_step = processing.SingleProcessingStep()
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


class TestAnalysisStepRecord(unittest.TestCase):
    def setUp(self):
        self.analysis_step = analysis.AnalysisStep()
        self.analysis_record = \
            aspecd.history.AnalysisStepRecord(self.analysis_step)

    def test_instantiate_class(self):
        aspecd.history.AnalysisStepRecord()

    def test_instantiate_class_with_analysis_step(self):
        aspecd.history.AnalysisStepRecord(self.analysis_step)

    def test_instantiate_description_from_analysis_step(self):
        self.analysis_step.description = 'Test'
        analysis_record = \
            aspecd.history.AnalysisStepRecord(self.analysis_step)
        self.assertEqual(analysis_record.description, 'Test')

    def test_has_create_analysis_step_method(self):
        self.assertTrue(hasattr(self.analysis_record,
                                'create_analysis_step'))
        self.assertTrue(
            callable(self.analysis_record.create_analysis_step))

    def test_has_from_processing_step_method(self):
        self.assertTrue(hasattr(self.analysis_record, 'from_analysis_step'))
        self.assertTrue(callable(self.analysis_record.from_analysis_step))

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

    def test_has_references_property(self):
        self.assertTrue(hasattr(self.analysis_record, 'references'))

    def test_analysis_object_gets_correct_parameters_value(self):
        test_dictionary = dict(bla='blub', foo='bar')
        self.analysis_step.parameters = test_dictionary
        self.analysis_record = \
            aspecd.history.AnalysisStepRecord(self.analysis_step)
        test_object = self.analysis_record.create_analysis_step()
        self.assertEqual(test_object.parameters, test_dictionary)

    def test_analysis_object_gets_correct_comment_value(self):
        test_comment = 'Frobnicate the bizbaz'
        self.analysis_step.comment = test_comment
        self.analysis_record = \
            aspecd.history.AnalysisStepRecord(self.analysis_step)
        test_object = self.analysis_record.create_analysis_step()
        self.assertEqual(test_object.comment, test_comment)

    def test_analysissteprecord_gets_correct_references_value(self):
        self.analysis_step.references = ['foo']
        self.analysis_record = \
            aspecd.history.AnalysisStepRecord(self.analysis_step)
        test_object = self.analysis_record.create_analysis_step()
        self.assertEqual(['foo'], test_object.references)

    def test_analysissteprecord_gets_result_from_analysisstep(self):
        test_result = ['foo']
        self.analysis_step.result = test_result
        self.analysis_record = \
            aspecd.history.AnalysisStepRecord(self.analysis_step)
        self.assertEqual(self.analysis_record.result, test_result)

    def test_analysisstep_from_record_has_no_result_value(self):
        test_result = ['foo']
        self.analysis_step.result = test_result
        self.analysis_record = \
            aspecd.history.AnalysisStepRecord(self.analysis_step)
        test_object = self.analysis_record.create_analysis_step()
        self.assertEqual(test_object.result, None)

    def test_has_to_dict_method(self):
        self.assertTrue(hasattr(self.analysis_record, 'to_dict'))
        self.assertTrue(callable(self.analysis_record.to_dict))

    def test_from_dict(self):
        orig_dict = self.analysis_record.to_dict()
        orig_dict["comment"] = 'foo'
        new_processing_record = \
            aspecd.history.AnalysisStepRecord(self.analysis_step)
        new_processing_record.from_dict(orig_dict)
        self.assertDictEqual(orig_dict, new_processing_record.to_dict())


class TestSingleAnalysisStepRecord(unittest.TestCase):
    def setUp(self):
        self.analysis_step = analysis.SingleAnalysisStep()
        self.analysis_record = \
            aspecd.history.SingleAnalysisStepRecord(self.analysis_step)

    def test_instantiate_class(self):
        pass


class TestAnalysisHistoryRecord(unittest.TestCase):
    def setUp(self):
        self.analysis_step = analysis.SingleAnalysisStep()
        self.historyrecord = \
            aspecd.history.AnalysisHistoryRecord(self.analysis_step)

    def test_instantiate_class(self):
        pass

    def test_instantiate_class_with_package_name(self):
        aspecd.history.AnalysisHistoryRecord(analysis_step=self.analysis_step,
                                             package="numpy")

    def test_instantiate_class_with_package_name_sets_sysinfo(self):
        analysis_step = aspecd.history.AnalysisHistoryRecord(
            analysis_step=self.analysis_step, package="numpy")
        self.assertTrue("numpy" in analysis_step.sysinfo.packages.keys())

    def test_has_analysis_property(self):
        self.assertTrue(hasattr(self.historyrecord, 'analysis'))

    def test_analysis_is_analysissteprecord(self):
        self.assertTrue(isinstance(self.historyrecord.analysis,
                                   aspecd.history.SingleAnalysisStepRecord))

    def test_has_replay_method(self):
        self.assertTrue(hasattr(self.historyrecord, 'replay'))
        self.assertTrue(callable(self.historyrecord.replay))

    def test_replay(self):
        self.historyrecord.replay(dataset.Dataset())


class TestAnnotationRecord(unittest.TestCase):
    def setUp(self):
        self.annotation = aspecd.annotation.Annotation()
        self.annotation_record = \
            aspecd.history.AnnotationRecord(self.annotation)

    def test_instantiate_class(self):
        aspecd.annotation.Annotation()

    def test_instantiate_class_with_annotation(self):
        aspecd.history.AnnotationRecord(self.annotation)

    def test_instantiate_content_from_annotation(self):
        self.annotation.content = {'foo': 'bar'}
        annotation_record = \
            aspecd.history.AnnotationRecord(self.annotation)
        self.assertEqual(annotation_record.content, self.annotation.content)

    def test_instantiate_class_name_from_annotation(self):
        annotation_record = \
            aspecd.history.AnnotationRecord(self.annotation)
        self.assertEqual(annotation_record.class_name,
                         aspecd.utils.full_class_name(self.annotation))

    def test_has_from_annotation_method(self):
        self.assertTrue(hasattr(self.annotation_record, 'from_annotation'))
        self.assertTrue(callable(self.annotation_record.from_annotation))

    def test_has_create_annotation_method(self):
        self.assertTrue(hasattr(self.annotation_record,
                                'create_annotation'))
        self.assertTrue(
            callable(self.annotation_record.create_annotation))

    def test_create_annotation_returns_annotation_object(self):
        test_object = self.annotation_record.create_annotation()
        self.assertTrue(isinstance(test_object, aspecd.annotation.Annotation))

    def test_annotation_object_has_correct_contents_value(self):
        self.annotation_record.content = {'foo': 'bar'}
        test_object = self.annotation_record.create_annotation()
        self.assertEqual(self.annotation_record.content, test_object.content)

    def test_has_to_dict_method(self):
        self.assertTrue(hasattr(self.annotation_record, 'to_dict'))
        self.assertTrue(callable(self.annotation_record.to_dict))

    def test_from_dict(self):
        orig_dict = self.annotation_record.to_dict()
        orig_dict["content"]["comment"] = 'foo'
        new_annotation_record = aspecd.history.AnnotationRecord()
        new_annotation_record.from_dict(orig_dict)
        self.assertDictEqual(orig_dict["content"],
                             new_annotation_record.to_dict()["content"])


class TestAnnotationHistoryRecord(unittest.TestCase):
    def setUp(self):
        self.annotation = aspecd.annotation.Annotation()
        self.annotation_record = aspecd.history.AnnotationHistoryRecord(
            annotation=self.annotation)

    def test_instantiate_class(self):
        pass

    def test_instantiate_class_with_package_name(self):
        aspecd.history.AnnotationHistoryRecord(
            annotation=self.annotation, package="numpy")

    def test_instantiate_class_with_package_name_sets_sysinfo(self):
        annotation_step = aspecd.history.AnnotationHistoryRecord(
            annotation=self.annotation, package="numpy")
        self.assertTrue("numpy" in annotation_step.sysinfo.packages.keys())

    def test_has_annotation_property(self):
        self.assertTrue(hasattr(self.annotation_record, 'annotation'))

    def test_annotation_is_annotation_record(self):
        self.assertTrue(isinstance(self.annotation_record.annotation,
                                   aspecd.history.AnnotationRecord))


class TestPlotRecord(unittest.TestCase):
    def setUp(self):
        self.plot_record = aspecd.history.PlotRecord()

    def test_instantiate_class(self):
        pass

    def test_has_name_property(self):
        self.assertTrue(hasattr(self.plot_record, 'class_name'))

    def test_has_parameters_property(self):
        self.assertTrue(hasattr(self.plot_record, 'parameters'))

    def test_has_description_property(self):
        self.assertTrue(hasattr(self.plot_record, 'description'))

    def test_has_filename_property(self):
        self.assertTrue(hasattr(self.plot_record, 'filename'))

    def test_has_from_plotter_method(self):
        self.assertTrue(hasattr(self.plot_record, 'from_plotter'))
        self.assertTrue(callable(self.plot_record.from_plotter))

    def test_instantiate_with_plotter(self):
        plotter = plotting.Plotter()
        aspecd.history.PlotRecord(plotter=plotter)

    def test_from_plotter_without_plotter_raises(self):
        with self.assertRaises(aspecd.exceptions.MissingPlotterError):
            self.plot_record.from_plotter()

    def test_from_plotter_sets_attributes(self):
        plotter = plotting.Plotter()
        plotter.filename = 'test'
        caption = plotting.Caption()
        caption.title = 'My fancy figure'
        caption.text = 'Some more description'
        plotter.caption = caption
        plotter.label = 'label'
        self.plot_record.from_plotter(plotter)
        self.assertEqual(plotter.name, self.plot_record.class_name)
        self.assertEqual(plotter.filename, self.plot_record.filename)
        self.assertEqual(plotter.parameters, self.plot_record.parameters)
        self.assertEqual(plotter.properties, self.plot_record.properties)
        self.assertEqual(plotter.description, self.plot_record.description)
        self.assertEqual(plotter.caption.title, self.plot_record.caption.title)
        self.assertEqual(plotter.label, self.plot_record.label)

    def test_instantiate_with_plotter_sets_attributes_from_plotter(self):
        plotter = plotting.Plotter()
        plotter.filename = 'test'
        caption = plotting.Caption()
        caption.title = 'My fancy figure'
        caption.text = 'Some more description'
        plotter.caption = caption
        plot_record = aspecd.history.PlotRecord(plotter=plotter)
        self.assertEqual(plotter.name, plot_record.class_name)
        self.assertEqual(plotter.filename, plot_record.filename)
        self.assertEqual(plotter.parameters, plot_record.parameters)
        self.assertEqual(plotter.description, plot_record.description)
        self.assertEqual(plotter.caption.title, plot_record.caption.title)

    def test_has_to_dict_method(self):
        self.assertTrue(hasattr(self.plot_record, 'to_dict'))
        self.assertTrue(callable(self.plot_record.to_dict))

    def test_from_dict(self):
        orig_dict = self.plot_record.to_dict()
        orig_dict["description"] = 'foo'
        new_plot_record = aspecd.history.PlotRecord()
        new_plot_record.from_dict(orig_dict)
        self.assertDictEqual(orig_dict, new_plot_record.to_dict())


class TestSinglePlotRecord(unittest.TestCase):
    def setUp(self):
        self.plot_record = aspecd.history.SinglePlotRecord()

    def test_instantiate_class(self):
        pass

    def test_has_preprocessing_property(self):
        self.assertTrue(hasattr(self.plot_record, 'preprocessing'))


class TestMultiPlotRecord(unittest.TestCase):
    def setUp(self):
        self.plot_record = aspecd.history.MultiPlotRecord()

    def test_instantiate_class(self):
        pass

    def test_has_datasets_property(self):
        self.assertTrue(hasattr(self.plot_record, 'datasets'))


class TestTableRecord(unittest.TestCase):
    def setUp(self):
        self.table = aspecd.table.Table()
        self.table_record = \
            aspecd.history.TableRecord(self.table)

    def test_instantiate_class(self):
        pass

    def test_instantiate_format_from_table(self):
        self.table.format = 'dokuwiki'
        table_record = aspecd.history.TableRecord(self.table)
        self.assertEqual(table_record.format, self.table.format)

    def test_instantiate_class_name_from_table(self):
        table_record = aspecd.history.TableRecord(self.table)
        self.assertEqual(table_record.class_name,
                         aspecd.utils.full_class_name(self.table))

    def test_has_from_table_method(self):
        self.assertTrue(hasattr(self.table_record, 'from_table'))
        self.assertTrue(callable(self.table_record.from_table))

    def test_has_create_table_method(self):
        self.assertTrue(hasattr(self.table_record, 'create_table'))
        self.assertTrue(callable(self.table_record.create_table))

    def test_create_table_returns_table_object(self):
        test_object = self.table_record.create_table()
        self.assertTrue(isinstance(test_object, aspecd.table.Table))

    def test_table_object_has_correct_format_value(self):
        self.table.format = 'dokuwiki'
        test_object = self.table_record.create_table()
        self.assertEqual(self.table_record.format, test_object.format)

    def test_has_to_dict_method(self):
        self.assertTrue(hasattr(self.table_record, 'to_dict'))
        self.assertTrue(callable(self.table_record.to_dict))

    def test_from_dict(self):
        orig_dict = self.table_record.to_dict()
        orig_dict["format"] = 'dokuwiki'
        new_table_record = aspecd.history.TableRecord()
        new_table_record.from_dict(orig_dict)
        self.assertDictEqual(orig_dict,
                             new_table_record.to_dict())


class TestTableHistoryRecord(unittest.TestCase):
    def setUp(self):
        self.table = aspecd.table.Table()
        self.table_record = aspecd.history.TableHistoryRecord(table=self.table)

    def test_instantiate_class(self):
        pass

    def test_instantiate_class_with_package_name(self):
        aspecd.history.TableHistoryRecord(table=self.table, package="numpy")

    def test_instantiate_class_with_package_name_sets_sysinfo(self):
        table_ = aspecd.history.TableHistoryRecord(table=self.table,
                                                   package="numpy")
        self.assertTrue("numpy" in table_.sysinfo.packages.keys())

    def test_has_annotation_property(self):
        self.assertTrue(hasattr(self.table_record, 'table'))

    def test_annotation_is_annotation_record(self):
        self.assertTrue(isinstance(self.table_record.table,
                                   aspecd.history.TableRecord))
