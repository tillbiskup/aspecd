"""Tests for datset."""

import unittest
import os
from datetime import datetime, timedelta

import numpy as np

import aspecd.analysis
import aspecd.annotation
import aspecd.plotting
import aspecd.processing
from aspecd import annotation, analysis, dataset, io, plotting, \
    processing, system
import aspecd.metadata


class TestDataset(unittest.TestCase):
    def setUp(self):
        self.dataset = dataset.Dataset()

    def test_instantiate_class(self):
        pass

    def test_has_data_property(self):
        self.assertTrue(hasattr(self.dataset, 'data'))

    def test_data_is_data(self):
        self.assertTrue(isinstance(self.dataset.data, dataset.Data))

    def test_has_origdata_property(self):
        self.assertTrue(hasattr(self.dataset, '_origdata'))

    def test_origdata_is_data(self):
        self.assertTrue(isinstance(self.dataset._origdata, dataset.Data))

    def test_has_metadata_property(self):
        self.assertTrue(hasattr(self.dataset, 'metadata'))

    def test_has_history_property(self):
        self.assertTrue(hasattr(self.dataset, 'history'))

    def test_history_is_list(self):
        self.assertTrue(isinstance(self.dataset.history, list))

    def test_has_analyses_property(self):
        self.assertTrue(hasattr(self.dataset, 'analyses'))

    def test_analyses_is_list(self):
        self.assertTrue(isinstance(self.dataset.analyses, list))

    def test_has_protected_package_name_property(self):
        self.assertTrue(hasattr(self.dataset, '_package_name'))

    def test_has_representations_property(self):
        self.assertTrue(hasattr(self.dataset, 'representations'))

    def test_has_id_property(self):
        self.assertTrue(hasattr(self.dataset, 'id'))

    def test_has_references_property(self):
        self.assertTrue(hasattr(self.dataset, 'references'))

    def test_has_package_name_property(self):
        self.assertTrue(hasattr(self.dataset, 'package_name'))

    def test_package_name_property_is_readonly(self):
        with self.assertRaises(AttributeError):
            # noinspection PyPropertyAccess
            self.dataset.package_name = 'foo'

    def test_has_tasks_property(self):
        self.assertTrue(hasattr(self.dataset, 'tasks'))


class TestDatasetProcessing(unittest.TestCase):
    def setUp(self):
        self.dataset = dataset.Dataset()
        self.processing_step = processing.ProcessingStep()

    def test_has_process_method(self):
        self.assertTrue(hasattr(self.dataset, 'process'))
        self.assertTrue(callable(self.dataset.process))

    def test_process_without_processing_step_raises(self):
        with self.assertRaises(dataset.MissingProcessingStepError):
            self.dataset.process()

    def test_process_adds_history_record(self):
        self.dataset.process(self.processing_step)
        self.assertFalse(self.dataset.history == [])

    def test_added_history_record_is_historyrecord(self):
        self.dataset.process(self.processing_step)
        self.assertTrue(isinstance(self.dataset.history[-1],
                                   aspecd.processing.ProcessingHistoryRecord))

    def test_process_increments_history_pointer(self):
        historypointer = self.dataset._history_pointer
        self.dataset.process(self.processing_step)
        self.assertTrue(self.dataset._history_pointer == historypointer + 1)

    def test_process_writes_different_historyrecords(self):
        self.dataset.process(self.processing_step)
        self.dataset.process(self.processing_step)
        self.assertIsNot(self.dataset.history[-1].processing,
                         self.dataset.history[-2].processing)

    def test_process_history_record_process_is_processing_step_record(self):
        self.dataset.process(self.processing_step)
        self.assertTrue(isinstance(self.dataset.history[-1].processing,
                                   processing.ProcessingStepRecord))

    def test_process_copies_processingstep_object(self):
        self.dataset.process(self.processing_step)
        self.assertIsNot(self.processing_step,
                         self.dataset.history[-1].processing)

    def test_process_returns_processing_object(self):
        processing_object = processing.ProcessingStep()
        processing_step = self.dataset.process(processing_object)
        self.assertTrue(isinstance(processing_step, processing.ProcessingStep))

    def test_process_sets_package_in_sysinfo(self):
        # Fake package name
        self.dataset._package_name = "numpy"
        self.dataset.process(self.processing_step)
        history_record = self.dataset.history[0]
        self.assertTrue("numpy" in history_record.sysinfo.packages.keys())

    def test_undoable_processing_step_does_not_touch_origdata(self):
        processing_step = processing.ProcessingStep()
        processing_step.undoable = True
        old_origdata = self.dataset._origdata
        self.dataset.process(processing_step)
        self.assertIs(self.dataset._origdata, old_origdata)

    def test_not_undoable_processing_step_resets_origdata(self):
        processing_step = processing.ProcessingStep()
        processing_step.undoable = False
        old_origdata = self.dataset._origdata
        self.dataset.process(processing_step)
        self.assertIsNot(self.dataset._origdata, old_origdata)

    def test_not_undoable_processing_step_empties_representations(self):
        processing_step = processing.ProcessingStep()
        processing_step.undoable = False
        self.dataset.process(processing_step)
        self.assertEqual(self.dataset.representations, [])

    def test_process_adds_task(self):
        self.dataset.process(self.processing_step)
        self.assertNotEqual(self.dataset.tasks, [])

    def test_added_task_has_kind_processing(self):
        self.dataset.process(self.processing_step)
        self.assertEqual(self.dataset.tasks[0]['kind'], 'processing')

    def test_added_task_has_processing_history_record(self):
        self.dataset.process(self.processing_step)
        self.assertIsInstance(self.dataset.tasks[0]['task'],
                              aspecd.processing.ProcessingHistoryRecord)


class TestDatasetUndo(unittest.TestCase):
    def setUp(self):
        self.dataset = dataset.Dataset()
        self.processingStep = processing.ProcessingStep()

    def test_has_undo_method(self):
        self.assertTrue(hasattr(self.dataset, 'undo'))
        self.assertTrue(callable(self.dataset.undo))

    def test_undo_with_empty_history_raises(self):
        self.dataset.history.clear()
        with self.assertRaises(dataset.UndoWithEmptyHistoryError):
            self.dataset.undo()

    def test_undo_decrements_historypointer(self):
        self.dataset.process(self.processingStep)
        historypointer = self.dataset._history_pointer
        self.dataset.undo()
        self.assertEqual(self.dataset._history_pointer, historypointer - 1)

    def test_undo_with_historypointer_zero_raises(self):
        self.dataset.process(self.processingStep)
        self.dataset.undo()
        with self.assertRaises(dataset.UndoAtBeginningOfHistoryError):
            self.dataset.undo()

    def test_undo_with_undoable_processing_step_raises(self):
        processingstep = self.processingStep
        processingstep.undoable = True
        self.dataset.process(processingstep)
        with self.assertRaises(dataset.UndoStepUndoableError):
            self.dataset.undo()

    def test_multiple_undo_with_undoable_processing_step_raises(self):
        processingstep = self.processingStep
        processingstep.undoable = True
        self.dataset.process(processingstep)
        processingstep.undoable = False
        self.dataset.process(processingstep)
        self.dataset.undo()
        with self.assertRaises(dataset.UndoStepUndoableError):
            self.dataset.undo()


class TestDatasetRedo(unittest.TestCase):
    def setUp(self):
        self.dataset = dataset.Dataset()
        self.processingStep = processing.ProcessingStep()

    def test_has_redo_method(self):
        self.assertTrue(hasattr(self.dataset, 'redo'))
        self.assertTrue(callable(self.dataset.redo))

    def test_redo_with_empty_history_raises(self):
        self.dataset.history.clear()
        with self.assertRaises(dataset.RedoAlreadyAtLatestChangeError):
            self.dataset.redo()

    def test_redo_at_latest_change_raises(self):
        self.dataset.process(self.processingStep)
        with self.assertRaises(dataset.RedoAlreadyAtLatestChangeError):
            self.dataset.redo()

    def test_redo_increments_historypointer(self):
        self.dataset.process(self.processingStep)
        self.dataset.undo()
        historypointer = self.dataset._history_pointer
        self.dataset.redo()
        self.assertEqual(self.dataset._history_pointer, historypointer + 1)


class TestDatasetIO(unittest.TestCase):
    def setUp(self):
        self.dataset = dataset.Dataset()

    def test_has_load_method(self):
        self.assertTrue(hasattr(self.dataset, 'load'))
        self.assertTrue(callable(self.dataset.load))

    def test_has_save_method(self):
        self.assertTrue(hasattr(self.dataset, 'save'))
        self.assertTrue(callable(self.dataset.save))

    def test_has_importfrom_method(self):
        self.assertTrue(hasattr(self.dataset, 'import_from'))
        self.assertTrue(callable(self.dataset.import_from))

    def test_has_exportto_method(self):
        self.assertTrue(hasattr(self.dataset, 'export_to'))
        self.assertTrue(callable(self.dataset.export_to))

    def test_importfrom_sets_origdata(self):
        importer = io.DatasetImporter()
        old_origdata = self.dataset._origdata
        self.dataset.import_from(importer)
        self.assertIsNot(self.dataset._origdata, old_origdata)


class TestDatasetProcessingWithHistory(unittest.TestCase):
    def setUp(self):
        self.dataset = dataset.Dataset()
        self.processingStep = processing.ProcessingStep()
        self.dataset.process(self.processingStep)
        self.dataset.undo()

    def test_stripping_leading_history_deletes_history_entries(self):
        orig_len_history = len(self.dataset.history)
        self.dataset.strip_history()
        new_len_history = len(self.dataset.history)
        self.assertGreater(orig_len_history, new_len_history)

    def test_process_with_leading_history_raises(self):
        with self.assertRaises(dataset.ProcessingWithLeadingHistoryError):
            self.dataset.process(self.processingStep)

    def test_stripping_leading_history_allows_processing(self):
        self.dataset.strip_history()
        self.dataset.process(self.processingStep)


class TestDatasetAnalysis(unittest.TestCase):
    def setUp(self):
        self.dataset = dataset.Dataset()
        self.analysis_step = analysis.SingleAnalysisStep()

    def test_has_analyse_method(self):
        self.assertTrue(hasattr(self.dataset, 'analyse'))
        self.assertTrue(callable(self.dataset.analyse))

    def test_has_analyze_method(self):
        self.assertTrue(hasattr(self.dataset, 'analyze'))
        self.assertTrue(callable(self.dataset.analyze))

    def test_analyse_adds_analysis_record(self):
        self.dataset.analyse(self.analysis_step)
        self.assertFalse(self.dataset.analyses == [])

    def test_added_analysis_record_is_analysishistoryrecord(self):
        self.dataset.analyse(self.analysis_step)
        self.assertTrue(isinstance(self.dataset.analyses[-1],
                                   aspecd.analysis.AnalysisHistoryRecord))

    def test_added_analysis_record_contains_history(self):
        processing_step = processing.ProcessingStep()
        self.dataset.process(processing_step)
        self.dataset.analyse(self.analysis_step)
        analysis_ = self.dataset.analyses[-1]
        self.assertEqual(len(self.dataset.history),
                         len(analysis_.analysis.preprocessing))

    def test_added_analysis_record_history_is_deepcopy(self):
        processing_step = processing.ProcessingStep()
        self.dataset.process(processing_step)
        self.dataset.analyse(self.analysis_step)
        analysis_ = self.dataset.analyses[-1]
        self.assertNotEqual(self.dataset.history,
                            analysis_.analysis.preprocessing)

    def test_analyse_returns_analysis_object(self):
        analysis_step = self.dataset.analyse(self.analysis_step)
        self.assertTrue(isinstance(analysis_step, analysis.SingleAnalysisStep))

    def test_analyze_returns_analysis_object(self):
        analysis_step = self.dataset.analyze(self.analysis_step)
        self.assertTrue(isinstance(analysis_step, analysis.SingleAnalysisStep))

    def test_has_delete_analysis_method(self):
        self.assertTrue(hasattr(self.dataset, 'delete_analysis'))
        self.assertTrue(callable(self.dataset.delete_analysis))

    def test_delete_analysis_deletes_analysis_record(self):
        self.dataset.analyse(self.analysis_step)
        orig_len_analyses = len(self.dataset.analyses)
        self.dataset.delete_analysis(0)
        new_len_analyses = len(self.dataset.analyses)
        self.assertGreater(orig_len_analyses, new_len_analyses)

    def test_delete_analysis_deletes_correct_analysis_record(self):
        self.dataset.analyse(self.analysis_step)
        self.dataset.analyse(self.analysis_step)
        analysisstep = self.dataset.analyses[-1]
        self.dataset.delete_analysis(0)
        self.assertIs(analysisstep, self.dataset.analyses[-1])

    def test_dataset_analyse_sets_package_in_sysinfo(self):
        # Fake package name
        self.dataset._package_name = "numpy"
        self.dataset.analyse(self.analysis_step)
        analysis_record = self.dataset.analyses[0]
        self.assertTrue("numpy" in analysis_record.sysinfo.packages.keys())

    def test_analyse_adds_task(self):
        self.dataset.analyse(self.analysis_step)
        self.assertNotEqual(self.dataset.tasks, [])

    def test_added_task_has_kind_analysis(self):
        self.dataset.analyse(self.analysis_step)
        self.assertEqual(self.dataset.tasks[0]['kind'], 'analysis')

    def test_added_task_has_analysis_history_record(self):
        self.dataset.analyse(self.analysis_step)
        self.assertIsInstance(self.dataset.tasks[0]['task'],
                              aspecd.analysis.AnalysisHistoryRecord)


class TestDatasetAnnotation(unittest.TestCase):
    def setUp(self):
        self.dataset = dataset.Dataset()
        self.annotation = annotation.Annotation()
        self.annotation.content = 'boo'

    def test_has_annotate_method(self):
        self.assertTrue(hasattr(self.dataset, 'annotate'))
        self.assertTrue(callable(self.dataset.annotate))

    def test_annotate_adds_annotation_record(self):
        self.dataset.annotate(self.annotation)
        self.assertFalse(self.dataset.annotations == [])

    def test_added_annotation_record_is_annotationhistoryrecord(self):
        self.dataset.annotate(self.annotation)
        self.assertTrue(isinstance(self.dataset.annotations[-1],
                                   aspecd.annotation.AnnotationHistoryRecord))

    def test_has_delete_annotation_method(self):
        self.assertTrue(hasattr(self.dataset, 'delete_annotation'))
        self.assertTrue(callable(self.dataset.delete_annotation))

    def test_delete_annotation_deletes_analysis_record(self):
        self.dataset.annotate(self.annotation)
        orig_len_annotations = len(self.dataset.annotations)
        self.dataset.delete_annotation(0)
        new_len_annotations = len(self.dataset.annotations)
        self.assertGreater(orig_len_annotations, new_len_annotations)

    def test_delete_annotation_deletes_correct_annotation_record(self):
        self.dataset.annotate(self.annotation)
        self.dataset.annotate(self.annotation)
        annotation_step = self.dataset.annotations[-1]
        self.dataset.delete_annotation(0)
        self.assertIs(annotation_step, self.dataset.annotations[-1])

    def test_dataset_annotate_sets_package_in_sysinfo(self):
        # Fake package name
        self.dataset._package_name = "numpy"
        self.dataset.annotate(self.annotation)
        annotation_record = self.dataset.annotations[0]
        self.assertTrue("numpy" in annotation_record.sysinfo.packages.keys())

    def test_annotate_adds_task(self):
        self.dataset.annotate(self.annotation)
        self.assertNotEqual(self.dataset.tasks, [])

    def test_added_task_has_kind_annotation(self):
        self.dataset.annotate(self.annotation)
        self.assertEqual(self.dataset.tasks[0]['kind'], 'annotation')

    def test_added_task_has_annotation_history_record(self):
        self.dataset.annotate(self.annotation)
        self.assertIsInstance(self.dataset.tasks[0]['task'],
                              aspecd.annotation.AnnotationHistoryRecord)


class TestDatasetPlotting(unittest.TestCase):
    def setUp(self):
        self.dataset = dataset.Dataset()
        self.plotter = plotting.SinglePlotter()

    def test_has_plot_method(self):
        self.assertTrue(hasattr(self.dataset, 'plot'))
        self.assertTrue(callable(self.dataset.plot))

    def test_dataset_plot_returns_plotter_object(self):
        plotter_object = plotting.SinglePlotter()
        plot = self.dataset.plot(plotter_object)
        self.assertTrue(isinstance(plot, plotting.Plotter))

    def test_plot_without_plotter_raises(self):
        with self.assertRaises(dataset.MissingPlotterError):
            self.dataset.plot()

    def test_plot_adds_task(self):
        self.dataset.plot(self.plotter)
        self.assertNotEqual(self.dataset.tasks, [])

    def test_added_task_has_kind_representation(self):
        self.dataset.plot(self.plotter)
        self.assertEqual(self.dataset.tasks[0]['kind'], 'representation')

    def test_added_task_has_plot_history_record(self):
        self.dataset.plot(self.plotter)
        self.assertIsInstance(self.dataset.tasks[0]['task'],
                              aspecd.plotting.PlotHistoryRecord)


class TestDatasetRepresentations(unittest.TestCase):
    def setUp(self):
        self.dataset = dataset.Dataset()
        self.plotter = plotting.SinglePlotter()

    def test_plot_adds_plot_record_to_representations(self):
        self.dataset.plot(self.plotter)
        self.assertFalse(self.dataset.representations == [])

    def test_added_plot_record_is_plotrecord(self):
        self.dataset.plot(self.plotter)
        self.assertTrue(isinstance(self.dataset.representations[-1],
                                   aspecd.plotting.PlotHistoryRecord))

    def test_added_plot_record_contains_history(self):
        processing_step = processing.ProcessingStep()
        self.dataset.process(processing_step)
        self.dataset.plot(self.plotter)
        representation = self.dataset.representations[-1]
        self.assertEqual(len(self.dataset.history),
                         len(representation.plot.preprocessing))

    def test_added_plot_record_history_is_deepcopy(self):
        processing_step = processing.ProcessingStep()
        self.dataset.process(processing_step)
        self.dataset.plot(self.plotter)
        representation = self.dataset.representations[-1]
        self.assertNotEqual(self.dataset.history,
                            representation.plot.preprocessing)

    def test_has_delete_representation_method(self):
        self.assertTrue(hasattr(self.dataset, 'delete_representation'))
        self.assertTrue(callable(self.dataset.delete_representation))

    def test_delete_representation_deletes_representation_record(self):
        self.dataset.plot(self.plotter)
        orig_len_representations = len(self.dataset.representations)
        self.dataset.delete_representation(0)
        new_len_representations = len(self.dataset.representations)
        self.assertGreater(orig_len_representations, new_len_representations)

    def test_delete_representation_deletes_correct_representation_record(self):
        self.dataset.plot(self.plotter)
        self.dataset.plot(self.plotter)
        representation = self.dataset.representations[-1]
        self.dataset.delete_representation(0)
        self.assertIs(representation, self.dataset.representations[-1])


class TestDatasetImporting(unittest.TestCase):
    def setUp(self):
        self.dataset = dataset.Dataset()
        self.importer = io.DatasetImporter()

    def test_has_import_from_method(self):
        self.assertTrue(hasattr(self.dataset, 'import_from'))
        self.assertTrue(callable(self.dataset.import_from))

    def test_import_without_importer_raises(self):
        with self.assertRaises(dataset.MissingImporterError):
            self.dataset.import_from()


class TestDatasetExporting(unittest.TestCase):
    def setUp(self):
        self.dataset = dataset.Dataset()
        self.exporter = io.DatasetExporter()

    def test_has_export_to_method(self):
        self.assertTrue(hasattr(self.dataset, 'export_to'))
        self.assertTrue(callable(self.dataset.export_to))

    def test_export_without_exporter_raises(self):
        with self.assertRaises(dataset.MissingExporterError):
            self.dataset.export_to()


class TestDatasetToDict(unittest.TestCase):
    def setUp(self):
        self.dataset = dataset.Dataset()
        self.figure_filename = 'foo.pdf'

    def tearDown(self):
        if os.path.exists(self.figure_filename):
            os.remove(self.figure_filename)

    def test_has_to_dict_method(self):
        self.assertTrue(hasattr(self.dataset, 'to_dict'))
        self.assertTrue(callable(self.dataset.to_dict))

    def test_to_dict_with_empty_dataset(self):
        self.dataset.to_dict()

    def test_to_dict_with_processing_step(self):
        processing_step = aspecd.processing.ProcessingStep()
        self.dataset.process(processing_step)
        self.dataset.to_dict()

    def test_to_dict_with_analysis_step(self):
        analysis_step = aspecd.analysis.SingleAnalysisStep()
        self.dataset.analyse(analysis_step)
        self.dataset.to_dict()

    def test_to_dict_with_annotation(self):
        annotation_step = aspecd.annotation.Annotation()
        annotation_step.content = 'foo'
        self.dataset.annotate(annotation_step)
        self.dataset.to_dict()

    def test_to_dict_with_representation(self):
        plotter = aspecd.plotting.SinglePlotter()
        self.dataset.plot(plotter)
        self.dataset.to_dict()

    def test_to_dict_with_representation_from_plotter(self):
        plotter = aspecd.plotting.SinglePlotter()
        plotter.plot(self.dataset)
        self.dataset.to_dict()

    def test_to_dict_with_saved_representation(self):
        plotter = aspecd.plotting.SinglePlotter()
        saver = aspecd.plotting.Saver(filename=self.figure_filename)
        plot = self.dataset.plot(plotter)
        plot.save(saver)
        self.dataset.to_dict()


class TestDatasetReferences(unittest.TestCase):
    def setUp(self):
        self.dataset = dataset.Dataset()

    def test_has_add_reference_method(self):
        self.assertTrue(hasattr(self.dataset, 'add_reference'))
        self.assertTrue(callable(self.dataset.add_reference))

    def test_add_reference_without_dataset_raises(self):
        with self.assertRaises(aspecd.dataset.MissingDatasetError):
            self.dataset.add_reference()

    def test_add_reference_adds_dataset_to_references(self):
        new_dataset = aspecd.dataset.CalculatedDataset()
        self.dataset.add_reference(new_dataset)
        self.assertTrue(self.dataset.references)

    def test_add_reference_adds_dataset_references_to_references(self):
        new_dataset = aspecd.dataset.CalculatedDataset()
        self.dataset.add_reference(new_dataset)
        self.assertTrue(isinstance(self.dataset.references[0],
                                   aspecd.dataset.DatasetReference))

    def test_has_remove_reference_method(self):
        self.assertTrue(hasattr(self.dataset, 'remove_reference'))
        self.assertTrue(callable(self.dataset.remove_reference))

    def test_remove_reference_without_id_raises(self):
        with self.assertRaises(aspecd.dataset.MissingDatasetError):
            self.dataset.remove_reference()

    def test_remove_reference_removes_dataset_from_references(self):
        new_dataset = aspecd.dataset.CalculatedDataset()
        new_dataset.id = 'foo'
        self.dataset.add_reference(new_dataset)
        self.dataset.remove_reference(dataset_id=new_dataset.id)
        self.assertFalse(self.dataset.references)

    def test_remove_reference_with_wrong_id_doesnt_remove_dataset(self):
        new_dataset = aspecd.dataset.CalculatedDataset()
        new_dataset.id = 'foo'
        self.dataset.add_reference(new_dataset)
        self.dataset.remove_reference(dataset_id='bar')
        self.assertTrue(self.dataset.references)


class TestExperimentalDataset(unittest.TestCase):
    def setUp(self):
        self.dataset = dataset.ExperimentalDataset()

    def test_instantiate_class(self):
        pass

    def test_metadata_is_ExperimentalDatasetMetadata(self):
        self.assertTrue(isinstance(self.dataset.metadata,
                                   aspecd.metadata.ExperimentalDatasetMetadata))


class TestCalculatedDataset(unittest.TestCase):
    def setUp(self):
        self.dataset = dataset.CalculatedDataset()

    def test_instantiate_class(self):
        pass

    def test_metadata_is_CalculatedDatasetMetadata(self):
        self.assertTrue(isinstance(self.dataset.metadata,
                                   aspecd.metadata.CalculatedDatasetMetadata))

    def test_data_is_calculated(self):
        self.assertTrue(self.dataset.data.calculated)

    def test_origdata_is_calculated(self):
        self.assertTrue(self.dataset._origdata.calculated)


class TestDatasetReference(unittest.TestCase):
    def setUp(self):
        self.reference = dataset.DatasetReference()
        self.dataset = dataset.Dataset()

    def test_instantiate_class(self):
        pass

    def test_has_type_property(self):
        self.assertTrue(hasattr(self.reference, 'type'))

    def test_has_id_property(self):
        self.assertTrue(hasattr(self.reference, 'id'))

    def test_has_history_property(self):
        self.assertTrue(hasattr(self.reference, 'history'))

    def test_has_from_dataset_method(self):
        self.assertTrue(hasattr(self.reference, 'from_dataset'))
        self.assertTrue(callable(self.reference.from_dataset))

    def test_from_dataset_without_dataset_raises(self):
        with self.assertRaises(aspecd.dataset.MissingDatasetError):
            self.reference.from_dataset()

    def test_from_dataset_sets_type(self):
        self.reference.from_dataset(self.dataset)
        self.assertEqual(aspecd.utils.full_class_name(self.dataset),
                         self.reference.type)

    def test_from_dataset_sets_id(self):
        self.dataset.source = 'foo'
        self.reference.from_dataset(self.dataset)
        self.assertEqual(self.dataset.id, self.reference.id)

    def test_from_dataset_sets_history(self):
        processing_step = aspecd.processing.ProcessingStep()
        self.dataset.process(processing_step)
        self.reference.from_dataset(self.dataset)
        self.assertTrue(self.reference.history)

    def test_from_dataset_copies_history(self):
        processing_step = aspecd.processing.ProcessingStep()
        self.dataset.process(processing_step)
        self.reference.from_dataset(self.dataset)
        self.assertIsNot(self.dataset.history, self.reference.history)

    def test_has_to_dataset_method(self):
        self.assertTrue(hasattr(self.reference, 'to_dataset'))
        self.assertTrue(callable(self.reference.to_dataset))

    def test_to_dataset_without_type_raises(self):
        with self.assertRaises(aspecd.dataset.MissingDatasetError):
            self.reference.to_dataset()

    def test_to_dataset_returns_dataset(self):
        self.reference.type = aspecd.utils.full_class_name(self.dataset)
        dataset_ = self.reference.to_dataset()
        self.assertTrue(isinstance(dataset_, aspecd.dataset.Dataset))

    def test_to_dataset_returns_dataset_of_correct_type(self):
        original_dataset = aspecd.dataset.CalculatedDataset()
        self.reference.from_dataset(original_dataset)
        new_dataset = self.reference.to_dataset()
        self.assertTrue(isinstance(new_dataset,
                                   aspecd.dataset.CalculatedDataset))

    def test_to_dataset_sets_dataset_id(self):
        self.reference.type = aspecd.utils.full_class_name(self.dataset)
        self.reference.id = 'foo'
        dataset_ = self.reference.to_dataset()
        self.assertEqual(self.reference.id, dataset_.id)

    def test_to_dataset_applies_history(self):
        processing_step = aspecd.processing.ProcessingStep()
        self.dataset.process(processing_step)
        self.reference.from_dataset(self.dataset)
        dataset_ = self.reference.to_dataset()
        self.assertTrue(dataset_.history)


class TestDatasetFactory(unittest.TestCase):
    def setUp(self):
        self.factory = dataset.DatasetFactory()
        self.source = 'foo'

    def test_instantiate_class(self):
        pass

    def test_has_importer_factory_property(self):
        self.assertTrue(hasattr(self.factory, 'importer_factory'))

    def test_get_dataset_returns_dataset(self):
        self.factory.importer_factory = io.DatasetImporterFactory()
        dataset_ = self.factory.get_dataset(source=self.source)
        self.assertTrue(isinstance(dataset_, dataset.Dataset))

    def test_get_dataset_without_source_raises(self):
        with self.assertRaises(dataset.MissingSourceError):
            self.factory.get_dataset()

    def test_get_dataset_without_importer_factory_raises(self):
        with self.assertRaises(dataset.MissingImporterFactoryError):
            self.factory.get_dataset(source=self.source)

    def test_get_dataset_sets_id_from_source_in_dataset(self):
        self.factory.importer_factory = io.DatasetImporterFactory()
        dataset_ = self.factory.get_dataset(source=self.source)
        self.assertEqual(self.source, dataset_.id)


class TestData(unittest.TestCase):

    def setUp(self):
        self.data = dataset.Data()

    def test_instantiate_class(self):
        pass

    def test_has_data_property(self):
        self.assertTrue(hasattr(self.data, 'data'))

    def test_data_is_ndarray(self):
        self.assertTrue(isinstance(self.data.data, np.ndarray))

    def test_has_axes_property(self):
        self.assertTrue(hasattr(self.data, 'axes'))

    def test_axes_is_list(self):
        self.assertTrue(isinstance(self.data.axes, list))

    def test_axes_have_right_count_for_1d_data(self):
        self.data.data = np.zeros(0)
        self.assertEqual(len(self.data.axes), 2)

    def test_axes_have_right_count_for_2d_data(self):
        self.data.data = np.zeros([0, 0])
        self.assertEqual(len(self.data.axes), 3)

    def test_has_calculated_property(self):
        self.assertTrue(hasattr(self.data, 'calculated'))

    def test_calculated_is_boolean(self):
        self.assertTrue(isinstance(self.data.calculated, bool))

    def test_modify_data_with_same_dimension_does_not_change_axes(self):
        data = np.zeros(5)
        axis_values = np.arange(len(data))
        self.data.data = data
        self.data.axes[0].values = axis_values
        self.data.data = data
        self.assertTrue(np.allclose(self.data.axes[0].values, axis_values))

    def test_modify_data_with_different_dimensions_keeps_axes_metadata(self):
        old_data = np.zeros([5, 1])
        new_data = np.zeros([5, 2])
        axis_quantity = 'foobar'
        self.data.data = old_data
        self.data.axes[0].values = np.arange(len(old_data))
        self.data.axes[0].quantity = axis_quantity
        self.data.data = new_data
        self.assertTrue(self.data.axes[0].quantity, axis_quantity)

    def test_modify_data_with_different_dimensions_adjusts_axes_values(self):
        old_data = np.zeros([5, 1])
        new_data = np.zeros([7, 1])
        self.data.data = old_data
        self.data.axes[0].values = np.arange(len(old_data))
        self.data.data = new_data
        self.assertEqual(new_data.size, self.data.axes[0].values.size)


class TestAxisSetupInConstructor(unittest.TestCase):

    def setUp(self):
        self.data = np.zeros(0)
        self.axes = [dataset.Axis(), dataset.Axis()]
        self.calculated = True

    def test_set_data_in_constructor(self):
        data_obj = dataset.Data(data=self.data)
        self.assertEqual(data_obj.data.tolist(), self.data.tolist())

    def test_set_axes_in_constructor(self):
        data_obj = dataset.Data(axes=self.axes)
        self.assertEqual(data_obj.axes, self.axes)

    def test_set_calculated_in_constructor(self):
        data_obj = dataset.Data(calculated=self.calculated)
        self.assertEqual(data_obj.calculated, self.calculated)

    def test_setting_too_many_axes_raises(self):
        axes = self.axes
        axes.append(dataset.Axis())
        with self.assertRaises(dataset.AxesCountError):
            dataset.Data(self.data, axes)

    def test_axes_values_dimensions_are_consistent_with_empty_1D_data(self):
        data_obj = dataset.Data(self.data, self.axes)
        self.assertEqual(len(data_obj.axes[0].values), 0)

    def test_axes_values_dimensions_are_consistent_with_empty_2D_data(self):
        tmp_data = np.zeros([0, 0])
        data_obj = dataset.Data(tmp_data)
        print(data_obj.axes[0].values)
        self.assertEqual(len(data_obj.axes[0].values), 0)
        self.assertEqual(len(data_obj.axes[1].values), 0)

    def test_axes_values_dimensions_are_consistent_with_nonempty_1D_data(self):
        len_data = 5
        tmp_data = np.zeros(len_data)
        tmp_axes = [dataset.Axis(), dataset.Axis()]
        tmp_axes[0].values = np.zeros(len_data)
        data_obj = dataset.Data(tmp_data, tmp_axes)
        self.assertEqual(len(data_obj.axes[0].values), len_data)

    def test_axes_values_dimensions_are_consistent_with_nonempty_2D_data(self):
        len_data = [5, 3]
        tmp_data = np.zeros(len_data)
        tmp_axes = [dataset.Axis(), dataset.Axis(), dataset.Axis()]
        tmp_axes[0].values = np.zeros(len_data[0])
        tmp_axes[1].values = np.zeros(len_data[1])
        data_obj = dataset.Data(tmp_data, tmp_axes)
        self.assertEqual(len(data_obj.axes[0].values), len_data[0])
        self.assertEqual(len(data_obj.axes[1].values), len_data[1])

    def test_wrong_axes_values_dimensions_with_nonempty_1D_data_raises(self):
        len_data = 5
        tmp_data = np.zeros(len_data)
        with self.assertRaises(dataset.AxesValuesInconsistentWithDataError):
            dataset.Data(tmp_data, self.axes)

    def test_wrong_axes_values_dimensions_with_nonempty_2D_data_raises(self):
        len_data = [5, 3]
        tmp_data = np.zeros(len_data)
        with self.assertRaises(dataset.AxesValuesInconsistentWithDataError):
            dataset.Data(tmp_data, self.axes)

    def test_set_wrong_axes_dimensions_with_nonempty_1D_data_raises(self):
        len_data = 5
        tmp_data = np.zeros(len_data)
        tmp_axis = dataset.Axis()
        tmp_axis.values = np.zeros(2*len_data)
        tmp_axes = [tmp_axis, dataset.Axis()]
        with self.assertRaises(dataset.AxesValuesInconsistentWithDataError):
            dataset.Data(tmp_data, tmp_axes)

    def test_set_wrong_axes_dimensions_with_nonempty_2D_data_raises(self):
        len_data = [5, 3]
        tmp_data = np.zeros(len_data)
        tmp_axis1 = dataset.Axis()
        tmp_axis1.values = np.zeros(2*len_data[0])
        tmp_axis2 = dataset.Axis()
        tmp_axis2.values = np.zeros(2*len_data[1])
        tmp_axes = [tmp_axis1, tmp_axis2, dataset.Axis()]
        with self.assertRaises(dataset.AxesValuesInconsistentWithDataError):
            dataset.Data(tmp_data, tmp_axes)


class TestAxis(unittest.TestCase):

    def setUp(self):
        self.axis = dataset.Axis()

    def test_instantiate_class(self):
        pass

    def test_has_values_property(self):
        self.assertTrue(hasattr(self.axis, 'values'))

    def test_values_is_ndarray(self):
        self.assertTrue(isinstance(self.axis.values, np.ndarray))

    def test_values_is_1d(self):
        self.assertTrue(self.axis.values.ndim, 1)

    def test_has_quantity_property(self):
        self.assertTrue(hasattr(self.axis, 'quantity'))

    def test_quantity_is_string(self):
        self.assertTrue(isinstance(self.axis.quantity, str))

    def test_has_unit_property(self):
        self.assertTrue(hasattr(self.axis, 'unit'))

    def test_unit_is_string(self):
        self.assertTrue(isinstance(self.axis.unit, str))

    def test_has_label_property(self):
        self.assertTrue(hasattr(self.axis, 'label'))

    def test_label_is_string(self):
        self.assertTrue(isinstance(self.axis.label, str))

    def test_has_equidistant_property(self):
        self.assertTrue(hasattr(self.axis, 'equidistant'))

    def test_equidistant_is_none_by_default(self):
        self.assertEqual(self.axis.equidistant, None)

    def test_equidistant_is_true_for_equidistant_axes(self):
        self.axis.values = np.arange(0, 5, 1)
        self.assertTrue(self.axis.equidistant)

    def test_equidistant_is_false_for_nonequidistant_axes(self):
        self.axis.values = np.asarray([0, 1, 2, 4, 8])
        self.assertFalse(self.axis.equidistant)


class TestAxisSettings(unittest.TestCase):

    def setUp(self):
        self.axis = dataset.Axis()

    def test_set_values(self):
        self.axis.values = np.zeros(0)

    def test_set_wrong_type_for_values_fails(self):
        with self.assertRaises(dataset.AxisValuesTypeError):
            self.axis.values = 0

    def test_set_multidimensional_values_fails(self):
        with self.assertRaises(dataset.AxisValuesDimensionError):
            self.axis.values = np.zeros([0, 0])


class TestHistoryRecord(unittest.TestCase):
    def setUp(self):
        self.historyrecord = dataset.HistoryRecord()

    def test_instantiate_class(self):
        pass

    def test_instantiate_class_with_package_name(self):
        dataset.HistoryRecord(package="aspecd")

    def test_instantiate_class_with_package_name_sets_sysinfo(self):
        history = dataset.HistoryRecord(package="numpy")
        self.assertTrue("numpy" in history.sysinfo.packages.keys())

    def test_has_date_property(self):
        self.assertTrue(hasattr(self.historyrecord, 'date'))

    def test_date_is_datetime(self):
        self.assertTrue(isinstance(self.historyrecord.date, datetime))

    def test_date_is_current_date(self):
        now = datetime.today()
        # noinspection PyTypeChecker
        self.assertAlmostEqual(now, self.historyrecord.date,
                               delta=timedelta(seconds=1))

    def test_has_sysinfo_property(self):
        self.assertTrue(hasattr(self.historyrecord, 'sysinfo'))

    def test_sysinfo_is_systeminfo(self):
        self.assertTrue(
            isinstance(self.historyrecord.sysinfo, system.SystemInfo))

    def test_has_to_dict_method(self):
        self.assertTrue(hasattr(self.historyrecord, 'to_dict'))
        self.assertTrue(callable(self.historyrecord.to_dict))
