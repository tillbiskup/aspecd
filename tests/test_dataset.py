"""Tests for datset."""

import unittest

import numpy as np

from aspecd import dataset, history, processing, analysis, plotting, \
    importer


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


class TestDatasetProcessing(unittest.TestCase):
    def setUp(self):
        self.dataset = dataset.Dataset()
        self.processingStep = processing.ProcessingStep()

    def test_has_process_method(self):
        self.assertTrue(hasattr(self.dataset, 'process'))
        self.assertTrue(callable(self.dataset.process))

    def test_process_without_processing_step_raises(self):
        with self.assertRaises(dataset.MissingProcessingStepError):
            self.dataset.process()

    def test_process_adds_history_record(self):
        self.dataset.process(self.processingStep)
        self.assertFalse(self.dataset.history == [])

    def test_added_history_record_is_historyrecord(self):
        self.dataset.process(self.processingStep)
        self.assertTrue(isinstance(self.dataset.history[-1],
                                   history.ProcessingHistoryRecord))

    def test_process_increments_history_pointer(self):
        historypointer = self.dataset._history_pointer
        self.dataset.process(self.processingStep)
        self.assertTrue(self.dataset._history_pointer == historypointer + 1)

    def test_process_writes_different_historyrecords(self):
        self.dataset.process(self.processingStep)
        self.dataset.process(self.processingStep)
        self.assertIsNot(self.dataset.history[-1].processing,
                         self.dataset.history[-2].processing)

    def test_process_history_record_process_is_processing_step_record(self):
        self.dataset.process(self.processingStep)
        self.assertTrue(isinstance(self.dataset.history[-1].processing,
                                   processing.ProcessingStepRecord))

    def test_process_copies_processingstep_object(self):
        self.dataset.process(self.processingStep)
        self.assertIsNot(self.processingStep,
                         self.dataset.history[-1].processing)

    def test_dataset_process_returns_processing_object(self):
        processing_object = processing.ProcessingStep()
        processing_step = self.dataset.process(processing_object)
        self.assertTrue(isinstance(processing_step, processing.ProcessingStep))


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
        self.analysisstep = analysis.AnalysisStep()

    def test_has_analyse_method(self):
        self.assertTrue(hasattr(self.dataset, 'analyse'))
        self.assertTrue(callable(self.dataset.analyse))

    def test_has_analyze_method(self):
        self.assertTrue(hasattr(self.dataset, 'analyze'))
        self.assertTrue(callable(self.dataset.analyze))

    def test_analyse_adds_analysis_record(self):
        self.dataset.analyse(self.analysisstep)
        self.assertFalse(self.dataset.analyses == [])

    def test_added_analysis_record_is_analysishistoryrecord(self):
        self.dataset.analyse(self.analysisstep)
        self.assertTrue(isinstance(self.dataset.analyses[-1],
                                   history.AnalysisHistoryRecord))

    def test_has_delete_analysis_method(self):
        self.assertTrue(hasattr(self.dataset, 'delete_analysis'))
        self.assertTrue(callable(self.dataset.delete_analysis))

    def test_delete_analysis_deletes_analysis_record(self):
        self.dataset.analyse(self.analysisstep)
        orig_len_analyses = len(self.dataset.analyses)
        self.dataset.delete_analysis(0)
        new_len_analyses = len(self.dataset.analyses)
        self.assertGreater(orig_len_analyses, new_len_analyses)

    def test_delete_analysis_deletes_correct_analysis_record(self):
        self.dataset.analyse(self.analysisstep)
        self.dataset.analyse(self.analysisstep)
        analysisstep = self.dataset.analyses[-1]
        self.dataset.delete_analysis(0)
        self.assertIs(analysisstep, self.dataset.analyses[-1])


class TestDatasetPlotting(unittest.TestCase):
    def setUp(self):
        self.dataset = dataset.Dataset()
        self.plotter = plotting.Plotter()

    def test_has_plot_method(self):
        self.assertTrue(hasattr(self.dataset, 'plot'))
        self.assertTrue(callable(self.dataset.plot))

    def test_dataset_plot_returns_plotter_object(self):
        plotter_object = plotting.Plotter()
        plot = self.dataset.plot(plotter_object)
        self.assertTrue(isinstance(plot, plotting.Plotter))

    def test_plot_without_plotter_raises(self):
        with self.assertRaises(dataset.MissingPlotterError):
            self.dataset.plot()


class TestDatasetImporting(unittest.TestCase):
    def setUp(self):
        self.dataset = dataset.Dataset()
        self.importer = importer.Importer()

    def test_has_import_from_method(self):
        self.assertTrue(hasattr(self.dataset, 'import_from'))
        self.assertTrue(callable(self.dataset.import_from))

    def test_import_without_importer_raises(self):
        with self.assertRaises(dataset.MissingImporterError):
            self.dataset.import_from()


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
        self.axis.values = np.arange(0,5,1)
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
