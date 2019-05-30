"""Tests for plotting."""

import matplotlib.figure
import matplotlib.axes
import matplotlib.pyplot as plt
import numpy as np
import os
import unittest

from aspecd import plotting, utils, dataset


class TestPlotter(unittest.TestCase):
    def setUp(self):
        self.plotter = plotting.Plotter()
        self.filename = 'Testfile.png'

    def tearDown(self):
        if os.path.isfile(self.filename):
            os.remove(self.filename)

    def test_instantiate_class(self):
        pass

    def test_has_plot_method(self):
        self.assertTrue(hasattr(self.plotter, 'plot'))
        self.assertTrue(callable(self.plotter.plot))

    def test_name_property_equals_full_class_name(self):
        full_class_name = utils.full_class_name(self.plotter)
        self.assertEqual(self.plotter.name, full_class_name)

    def test_has_parameters_property(self):
        self.assertTrue(hasattr(self.plotter, 'parameters'))

    def test_parameters_property_is_dict(self):
        self.assertTrue(isinstance(self.plotter.parameters, dict))

    def test_has_properties_property(self):
        self.assertTrue(hasattr(self.plotter, 'properties'))

    def test_has_description_property(self):
        self.assertTrue(hasattr(self.plotter, 'description'))

    def test_description_property_is_string(self):
        self.assertTrue(isinstance(self.plotter.description, str))

    def test_has_figure_property(self):
        self.assertTrue(hasattr(self.plotter, 'figure'))

    def test_has_fig_property(self):
        self.assertTrue(hasattr(self.plotter, 'fig'))

    def test_fig_property_and_figure_property_are_identical(self):
        self.assertTrue(self.plotter.figure is self.plotter.fig)

    def test_has_axes_property(self):
        self.assertTrue(hasattr(self.plotter, 'axes'))

    def test_has_ax_property(self):
        self.assertTrue(hasattr(self.plotter, 'axes'))

    def test_ax_property_and_axes_property_are_identical(self):
        self.assertTrue(self.plotter.axes is self.plotter.ax)

    def test_has_filename_property(self):
        self.assertTrue(hasattr(self.plotter, 'filename'))

    def test_has_caption_property(self):
        self.assertTrue(hasattr(self.plotter, 'caption'))

    def test_has_save_method(self):
        self.assertTrue(hasattr(self.plotter, 'save'))
        self.assertTrue(callable(self.plotter.save))

    def test_plot_sets_figure_property(self):
        self.plotter.plot()
        self.assertTrue(isinstance(self.plotter.figure,
                                   matplotlib.figure.Figure))
        plt.close(self.plotter.figure)

    def test_plot_sets_fig_property(self):
        self.plotter.plot()
        self.assertTrue(isinstance(self.plotter.fig, matplotlib.figure.Figure))
        plt.close(self.plotter.fig)

    def test_plot_sets_axes_property(self):
        self.plotter.plot()
        self.assertTrue(isinstance(self.plotter.axes, matplotlib.axes.Axes))
        plt.close(self.plotter.figure)

    def test_plot_sets_ax_property(self):
        self.plotter.plot()
        self.assertTrue(isinstance(self.plotter.ax, matplotlib.axes.Axes))
        plt.close(self.plotter.figure)

    def test_save_without_saver_raises(self):
        with self.assertRaises(plotting.MissingSaverError):
            self.plotter.save()

    def test_save_returns_saver(self):
        saver = plotting.Saver()
        saver.filename = self.filename
        self.plotter.plot()
        returned_saver = self.plotter.save(saver)
        self.assertTrue(isinstance(returned_saver, plotting.Saver))

    def test_save_sets_plot_in_saver(self):
        saver = plotting.Saver()
        saver.filename = self.filename
        self.plotter.plot()
        returned_saver = self.plotter.save(saver)
        self.assertEqual(returned_saver.plotter, self.plotter)

    def test_save_sets_filename(self):
        saver = plotting.Saver()
        saver.filename = self.filename
        self.plotter.plot()
        self.plotter.save(saver)
        self.assertEqual(self.filename, self.plotter.filename)

    def test_plot_applies_properties(self):
        self.plotter.properties.figure.dpi = 300.0
        self.plotter.plot()
        self.assertEqual(self.plotter.properties.figure.dpi,
                         self.plotter.figure.dpi)


class TestSinglePlotter(unittest.TestCase):
    def setUp(self):
        self.plotter = plotting.SinglePlotter()

    def test_instantiate_class(self):
        pass

    def test_has_drawing_property(self):
        self.assertTrue(hasattr(self.plotter, 'drawing'))

    def test_plot_without_dataset_raises(self):
        with self.assertRaises(plotting.MissingDatasetError):
            self.plotter.plot()

    def test_plot_with_preset_dataset(self):
        self.plotter.dataset = dataset.Dataset()
        self.plotter.plot()

    def test_plot_from_dataset_sets_dataset(self):
        test_dataset = dataset.Dataset()
        plotter = test_dataset.plot(self.plotter)
        self.assertTrue(isinstance(plotter.dataset, dataset.Dataset))

    def test_plot_with_dataset(self):
        test_dataset = dataset.Dataset()
        self.plotter.plot(dataset=test_dataset)
        self.assertGreater(len(test_dataset.representations), 0)

    def test_plot_with_dataset_sets_axes_labels(self):
        test_dataset = dataset.Dataset()
        test_dataset.data.axes[0].quantity = 'foo'
        test_dataset.data.axes[0].unit = 'bar'
        test_dataset.data.axes[1].quantity = 'foo'
        test_dataset.data.axes[1].unit = 'bar'
        xlabel = '$' + test_dataset.data.axes[0].quantity + '$' + ' / ' + \
                 test_dataset.data.axes[0].unit
        ylabel = '$' + test_dataset.data.axes[1].quantity + '$' + ' / ' + \
                 test_dataset.data.axes[1].unit
        plotter = test_dataset.plot(self.plotter)
        self.assertEqual(xlabel, plotter.axes.get_xlabel())
        self.assertEqual(ylabel, plotter.axes.get_ylabel())

    def test_plot_returns_dataset(self):
        test_dataset = self.plotter.plot(dataset=dataset.Dataset())
        self.assertTrue(isinstance(test_dataset, dataset.Dataset))


class TestSinglePlotter1D(unittest.TestCase):
    def setUp(self):
        self.plotter = plotting.SinglePlotter1D()

    def test_instantiate_class(self):
        pass

    def test_has_type_property(self):
        self.assertTrue(hasattr(self.plotter, 'type'))

    def test_set_type(self):
        plot_type = 'scatter'
        self.plotter.type = plot_type
        self.assertEqual(self.plotter.type, plot_type)

    def test_setting_wrong_type_raises(self):
        with self.assertRaises(TypeError):
            self.plotter.type = 'foo'

    def test_plot_sets_drawing(self):
        self.plotter.plot(dataset=dataset.Dataset())
        self.assertTrue(self.plotter.drawing)

    def test_plot_with_2D_data_raises(self):
        dataset_ = dataset.Dataset()
        dataset_.data.data = np.random.rand(3, 2)
        with self.assertRaises(plotting.PlotNotApplicableToDatasetError):
            self.plotter.plot(dataset_)


class TestSinglePlotter2D(unittest.TestCase):
    def setUp(self):
        self.plotter = plotting.SinglePlotter2D()

    def test_instantiate_class(self):
        pass

    def test_has_type_property(self):
        self.assertTrue(hasattr(self.plotter, 'type'))

    def test_set_type(self):
        plot_type = 'contour'
        self.plotter.type = plot_type
        self.assertEqual(self.plotter.type, plot_type)

    def test_setting_wrong_type_raises(self):
        with self.assertRaises(TypeError):
            self.plotter.type = 'foo'

    def test_plot_sets_drawing(self):
        dataset_ = dataset.Dataset()
        dataset_.data.data = np.random.rand(3, 2)
        self.plotter.plot(dataset=dataset_)
        self.assertTrue(self.plotter.drawing)


class TestMultiPlotter(unittest.TestCase):
    def setUp(self):
        self.plotter = plotting.MultiPlotter()

    def test_instantiate_class(self):
        pass

    def test_has_datasets_property(self):
        self.assertTrue(hasattr(self.plotter, 'datasets'))

    def test_datasets_property_is_list(self):
        self.assertTrue(isinstance(self.plotter.datasets, list))

    def test_plot_without_datasets_raises(self):
        with self.assertRaises(plotting.MissingDatasetError):
            self.plotter.plot()

    def test_plot_with_datasets(self):
        self.plotter.datasets.append(dataset.Dataset())
        self.plotter.plot()

    def test_parameters_have_axes_key(self):
        self.assertIn('axes', self.plotter.parameters)

    def test_parameters_axes_is_list_of_axes_objects(self):
        self.assertTrue(isinstance(self.plotter.parameters['axes'], list))
        self.assertTrue(self.plotter.parameters['axes'])
        for axis in self.plotter.parameters['axes']:
            self.assertTrue(isinstance(axis, dataset.Axis))

    def test_plot_with_axes_in_parameters_sets_axes_labels(self):
        self.plotter.parameters['axes'][0].quantity = 'foo'
        self.plotter.parameters['axes'][0].unit = 'bar'
        self.plotter.parameters['axes'][1].quantity = 'foo'
        self.plotter.parameters['axes'][1].unit = 'bar'
        xlabel = '$' + self.plotter.parameters['axes'][0].quantity + \
                 '$' + ' / ' + self.plotter.parameters['axes'][0].unit
        ylabel = '$' + self.plotter.parameters['axes'][1].quantity + \
                 '$' + ' / ' + self.plotter.parameters['axes'][1].unit
        self.plotter.datasets.append(dataset.Dataset())
        self.plotter.plot()
        self.assertEqual(xlabel, self.plotter.axes.get_xlabel())
        self.assertEqual(ylabel, self.plotter.axes.get_ylabel())

    def test_plot_with_datasets_with_identical_axes_sets_axes_labels(self):
        test_dataset0 = dataset.Dataset()
        test_dataset0.data.axes[0].quantity = 'foo'
        test_dataset0.data.axes[0].unit = 'bar'
        test_dataset0.data.axes[1].quantity = 'foo'
        test_dataset0.data.axes[1].unit = 'bar'
        test_dataset1 = dataset.Dataset()
        test_dataset1.data.axes[0].quantity = 'foo'
        test_dataset1.data.axes[0].unit = 'bar'
        test_dataset1.data.axes[1].quantity = 'foo'
        test_dataset1.data.axes[1].unit = 'bar'
        xlabel = '$' + test_dataset0.data.axes[0].quantity + '$' + ' / ' + \
                 test_dataset0.data.axes[0].unit
        ylabel = '$' + test_dataset0.data.axes[1].quantity + '$' + ' / ' + \
                 test_dataset0.data.axes[1].unit
        self.plotter.datasets.append(test_dataset0)
        self.plotter.datasets.append(test_dataset1)
        self.plotter.plot()
        self.assertEqual(xlabel, self.plotter.axes.get_xlabel())
        self.assertEqual(ylabel, self.plotter.axes.get_ylabel())


class TestSaver(unittest.TestCase):
    def setUp(self):
        self.saver = plotting.Saver()
        self.filename = 'test.pdf'

    def tearDown(self):
        if os.path.isfile(self.filename):
            os.remove(self.filename)

    def test_instantiate_class(self):
        pass

    def test_has_save_method(self):
        self.assertTrue(hasattr(self.saver, 'save'))
        self.assertTrue(callable(self.saver.save))

    def test_save_without_filename_raises(self):
        with self.assertRaises(plotting.MissingFilenameError):
            self.saver.save(plotting.Plotter())

    def test_with_filename_set_previously(self):
        self.saver.plotter = plotting.Plotter()
        self.saver.plotter.plot()
        self.saver.filename = self.filename
        self.saver.save()

    def test_instantiate_with_filename_sets_filename(self):
        self.saver = plotting.Saver(self.filename)
        self.assertEqual(self.saver.filename, self.filename)

    def test_save_without_plotter_raises(self):
        self.saver.filename = self.filename
        with self.assertRaises(plotting.MissingPlotError):
            self.saver.save()

    def test_save_with_plotter_sets_plotter(self):
        plotter = plotting.Plotter()
        plotter.plot()
        self.saver.filename = self.filename
        self.saver.save(plotter)
        self.assertEqual(self.saver.plotter, plotter)

    def test_has_parameters_property(self):
        self.assertTrue(hasattr(self.saver, 'parameters'))

    def test_parameters_property_is_dict(self):
        self.assertTrue(isinstance(self.saver.parameters, dict))

    def test_save_creates_file(self):
        plotter = plotting.Plotter()
        plotter.plot()
        self.saver.filename = self.filename
        self.saver.save(plotter)
        self.assertTrue(os.path.isfile(self.filename))

    def test_set_format_parameter_adds_extension(self):
        plotter = plotting.Plotter()
        plotter.plot()
        self.filename = 'test.pdf'
        self.saver.filename, _ = os.path.splitext(self.filename)
        self.saver.parameters["format"] = 'pdf'
        self.saver.save(plotter)
        self.assertTrue(os.path.isfile(self.filename))

    def test_set_format_parameter_corrects_extension(self):
        plotter = plotting.Plotter()
        plotter.plot()
        self.filename = 'test.pdf'
        basename, _ = os.path.splitext(self.filename)
        self.saver.parameters["format"] = 'pdf'
        self.saver.filename = '.'.join([basename, "png"])
        self.saver.save(plotter)
        self.assertTrue(os.path.isfile(self.filename))

    def test_set_format_parameter_writes_appropriate_file(self):
        plotter = plotting.Plotter()
        plotter.plot()
        self.filename = 'test.pdf'
        self.saver.filename, _ = os.path.splitext(self.filename)
        self.saver.parameters["format"] = 'pdf'
        self.saver.save(plotter)
        self.assertTrue(os.path.isfile(self.filename))


class TestPlotRecord(unittest.TestCase):
    def setUp(self):
        self.plot_record = plotting.PlotRecord()

    def test_instantiate_class(self):
        pass

    def test_has_name_property(self):
        self.assertTrue(hasattr(self.plot_record, 'name'))

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
        plotting.PlotRecord(plotter=plotter)

    def test_from_plotter_without_plotter_raises(self):
        with self.assertRaises(plotting.MissingPlotterError):
            self.plot_record.from_plotter()

    def test_from_plotter_sets_attributes(self):
        plotter = plotting.Plotter()
        plotter.filename = 'test'
        self.plot_record.from_plotter(plotter)
        self.assertEqual(plotter.name, self.plot_record.name)
        self.assertEqual(plotter.filename, self.plot_record.filename)
        self.assertEqual(plotter.parameters, self.plot_record.parameters)
        self.assertEqual(plotter.description, self.plot_record.description)

    def test_instantiate_with_plotter_sets_attributes_from_plotter(self):
        plotter = plotting.Plotter()
        plotter.filename = 'test'
        plot_record = plotting.PlotRecord(plotter=plotter)
        self.assertEqual(plotter.name, plot_record.name)
        self.assertEqual(plotter.filename, plot_record.filename)
        self.assertEqual(plotter.parameters, plot_record.parameters)
        self.assertEqual(plotter.description, plot_record.description)


class TestSinglePlotRecord(unittest.TestCase):
    def setUp(self):
        self.plot_record = plotting.SinglePlotRecord()

    def test_instantiate_class(self):
        pass

    def test_has_preprocessing_property(self):
        self.assertTrue(hasattr(self.plot_record, 'preprocessing'))


class TestMultiPlotRecord(unittest.TestCase):
    def setUp(self):
        self.plot_record = plotting.MultiPlotRecord()

    def test_instantiate_class(self):
        pass

    def test_has_datasets_property(self):
        self.assertTrue(hasattr(self.plot_record, 'datasets'))


class TestCaption(unittest.TestCase):
    def setUp(self):
        self.caption = plotting.Caption()

    def test_instantiate_class(self):
        pass

    def test_has_to_dict_method(self):
        self.assertTrue(hasattr(self.caption, 'to_dict'))
        self.assertTrue(callable(self.caption.to_dict))

    def test_has_from_dict_method(self):
        self.assertTrue(hasattr(self.caption, 'from_dict'))
        self.assertTrue(callable(self.caption.from_dict))

    def test_has_title_property(self):
        self.assertTrue(hasattr(self.caption, 'title'))

    def test_has_text_property(self):
        self.assertTrue(hasattr(self.caption, 'text'))

    def test_has_parameters_property(self):
        self.assertTrue(hasattr(self.caption, 'parameters'))


class TestDrawingProperties(unittest.TestCase):
    def setUp(self):
        self.drawing_properties = plotting.DrawingProperties()

    def test_instantiate_class(self):
        pass

    def test_has_to_dict_method(self):
        self.assertTrue(hasattr(self.drawing_properties, 'to_dict'))
        self.assertTrue(callable(self.drawing_properties.to_dict))

    def test_has_from_dict_method(self):
        self.assertTrue(hasattr(self.drawing_properties, 'from_dict'))
        self.assertTrue(callable(self.drawing_properties.from_dict))

    def test_has_properties(self):
        for prop in ['label']:
            self.assertTrue(hasattr(self.drawing_properties, prop))

    def test_has_apply_method(self):
        self.assertTrue(hasattr(self.drawing_properties, 'apply'))
        self.assertTrue(callable(self.drawing_properties.apply))

    def test_apply_without_argument_raises(self):
        with self.assertRaises(plotting.MissingDrawingError):
            self.drawing_properties.apply()

    def test_apply_sets_properties(self):
        self.drawing_properties.label = 'foo'
        # noinspection PyUnresolvedReferences
        line = matplotlib.lines.Line2D([0, 1], [0, 0])
        self.drawing_properties.apply(drawing=line)
        self.assertEqual(self.drawing_properties.label, line.get_label())


class TestLineProperties(unittest.TestCase):
    def setUp(self):
        self.line_properties = plotting.LineProperties()

    def test_instantiate_class(self):
        pass

    def test_has_to_dict_method(self):
        self.assertTrue(hasattr(self.line_properties, 'to_dict'))
        self.assertTrue(callable(self.line_properties.to_dict))

    def test_has_from_dict_method(self):
        self.assertTrue(hasattr(self.line_properties, 'from_dict'))
        self.assertTrue(callable(self.line_properties.from_dict))

    def test_has_properties(self):
        for prop in ['color', 'drawstyle', 'label', 'linestyle', 'linewidth',
                     'marker']:
            self.assertTrue(hasattr(self.line_properties, prop))

    def test_has_apply_method(self):
        self.assertTrue(hasattr(self.line_properties, 'apply'))
        self.assertTrue(callable(self.line_properties.apply))

    def test_apply_without_argument_raises(self):
        with self.assertRaises(plotting.MissingDrawingError):
            self.line_properties.apply()

    def test_apply_sets_properties(self):
        self.line_properties.label = 'foo'
        # noinspection PyUnresolvedReferences
        line = matplotlib.lines.Line2D([0, 1], [0, 0])
        self.line_properties.apply(drawing=line)
        self.assertEqual(self.line_properties.label, line.get_label())


class TestPlotProperties(unittest.TestCase):
    def setUp(self):
        self.plot_properties = plotting.PlotProperties()

    def test_instantiate_class(self):
        pass

    def test_has_to_dict_method(self):
        self.assertTrue(hasattr(self.plot_properties, 'to_dict'))
        self.assertTrue(callable(self.plot_properties.to_dict))

    def test_has_from_dict_method(self):
        self.assertTrue(hasattr(self.plot_properties, 'from_dict'))
        self.assertTrue(callable(self.plot_properties.from_dict))

    def test_has_figure_property(self):
        self.assertTrue(hasattr(self.plot_properties, 'figure'))

    def test_has_apply_method(self):
        self.assertTrue(hasattr(self.plot_properties, 'apply'))
        self.assertTrue(callable(self.plot_properties.apply))

    def test_apply_without_argument_raises(self):
        with self.assertRaises(plotting.MissingPlotterError):
            self.plot_properties.apply()

    def test_apply_sets_properties(self):
        self.plot_properties.figure.dpi = 300.0
        plot = plotting.Plotter()
        plot.plot()
        self.plot_properties.apply(plotter=plot)
        self.assertEqual(self.plot_properties.figure.dpi,
                         plot.figure.get_dpi())


class TestFigureProperties(unittest.TestCase):
    def setUp(self):
        self.figure_properties = plotting.FigureProperties()

    def test_instantiate_class(self):
        pass

    def test_has_to_dict_method(self):
        self.assertTrue(hasattr(self.figure_properties, 'to_dict'))
        self.assertTrue(callable(self.figure_properties.to_dict))

    def test_has_from_dict_method(self):
        self.assertTrue(hasattr(self.figure_properties, 'from_dict'))
        self.assertTrue(callable(self.figure_properties.from_dict))

    def test_has_properties(self):
        for prop in ['figsize', 'dpi']:
            self.assertTrue(hasattr(self.figure_properties, prop))

    def test_has_apply_method(self):
        self.assertTrue(hasattr(self.figure_properties, 'apply'))
        self.assertTrue(callable(self.figure_properties.apply))

    def test_apply_without_argument_raises(self):
        with self.assertRaises(plotting.MissingFigureError):
            self.figure_properties.apply()

    def test_apply_sets_figure_properties(self):
        self.figure_properties.dpi = 300.0
        plot = plotting.Plotter()
        plot.plot()
        self.figure_properties.apply(figure=plot.figure)
        self.assertEqual(self.figure_properties.dpi, plot.figure.get_dpi())


class TestAxisProperties(unittest.TestCase):
    def setUp(self):
        self.axis_properties = plotting.AxisProperties()

    def test_instantiate_class(self):
        pass

    def test_has_to_dict_method(self):
        self.assertTrue(hasattr(self.axis_properties, 'to_dict'))
        self.assertTrue(callable(self.axis_properties.to_dict))

    def test_has_from_dict_method(self):
        self.assertTrue(hasattr(self.axis_properties, 'from_dict'))
        self.assertTrue(callable(self.axis_properties.from_dict))

    def test_has_properties(self):
        for prop in ['aspect', 'facecolor', 'xlabel', 'xlim', 'xscale',
                     'xticklabels', 'xticks', 'ylabel', 'ylim', 'yscale',
                     'yticklabels', 'yticks']:
            self.assertTrue(hasattr(self.axis_properties, prop))

    def test_has_apply_properties_method(self):
        self.assertTrue(hasattr(self.axis_properties, 'apply'))
        self.assertTrue(callable(self.axis_properties.apply))

    def test_apply_properties_without_argument_raises(self):
        with self.assertRaises(plotting.MissingAxisError):
            self.axis_properties.apply()

    def test_apply_properties_sets_axis_properties(self):
        self.axis_properties.xlabel = 'foo'
        plot = plotting.Plotter()
        plot.plot()
        self.axis_properties.apply(axis=plot.axes)
        self.assertEqual(self.axis_properties.xlabel, plot.axes.get_xlabel())


class TestLegendProperties(unittest.TestCase):
    def setUp(self):
        self.legend_properties = plotting.LegendProperties()

    def test_instantiate_class(self):
        pass

    def test_has_to_dict_method(self):
        self.assertTrue(hasattr(self.legend_properties, 'to_dict'))
        self.assertTrue(callable(self.legend_properties.to_dict))

    def test_has_from_dict_method(self):
        self.assertTrue(hasattr(self.legend_properties, 'from_dict'))
        self.assertTrue(callable(self.legend_properties.from_dict))

    def test_has_properties(self):
        for prop in ['loc']:
            self.assertTrue(hasattr(self.legend_properties, prop))

    def test_has_apply_method(self):
        self.assertTrue(hasattr(self.legend_properties, 'apply'))
        self.assertTrue(callable(self.legend_properties.apply))

    def test_apply_without_argument_raises(self):
        with self.assertRaises(plotting.MissingLegendError):
            self.legend_properties.apply()

    def test_apply_properties_sets_legend_properties(self):
        self.legend_properties.loc = 'center'
        plot = plotting.Plotter()
        plot.plot()
        legend = plot.axes.legend()
        self.legend_properties.apply(legend=legend)
        self.assertEqual(self.legend_properties.loc, legend.loc)


class TestSinglePlotProperties(unittest.TestCase):
    def setUp(self):
        self.plot_properties = plotting.SinglePlotProperties()

    def test_instantiate_class(self):
        pass

    def test_has_figure_property(self):
        self.assertTrue(hasattr(self.plot_properties, 'figure'))

    def test_has_axes_property(self):
        self.assertTrue(hasattr(self.plot_properties, 'axes'))

    def test_has_drawing_property(self):
        self.assertTrue(hasattr(self.plot_properties, 'drawing'))

    def test_has_to_dict_method(self):
        self.assertTrue(hasattr(self.plot_properties, 'to_dict'))
        self.assertTrue(callable(self.plot_properties.to_dict))

    def test_has_from_dict_method(self):
        self.assertTrue(hasattr(self.plot_properties, 'from_dict'))
        self.assertTrue(callable(self.plot_properties.from_dict))

    def test_apply_sets_axis_properties(self):
        self.plot_properties.axes.xlabel = 'foo'
        plot = plotting.SinglePlotter()
        plot.plot(dataset=dataset.Dataset())
        self.plot_properties.apply(plotter=plot)
        self.assertEqual(self.plot_properties.axes.xlabel,
                         plot.axes.get_xlabel())

    def test_apply_sets_drawing_properties(self):
        self.plot_properties.drawing.label = 'foo'
        plot = plotting.SinglePlotter1D()
        plot.plot(dataset=dataset.Dataset())
        self.plot_properties.apply(plotter=plot)
        self.assertEqual(self.plot_properties.drawing.label,
                         plot.drawing.get_label())


class TestSinglePlot1DProperties(unittest.TestCase):
    def setUp(self):
        self.plot_properties = plotting.SinglePlot1DProperties()

    def test_instantiate_class(self):
        pass

    def test_apply_sets_drawing_properties(self):
        self.plot_properties.drawing.linewidth = 2.0
        plot = plotting.SinglePlotter1D()
        plot.plot(dataset=dataset.Dataset())
        self.plot_properties.apply(plotter=plot)
        self.assertEqual(self.plot_properties.drawing.linewidth,
                         plot.drawing.get_linewidth())


class TestMultiPlotProperties(unittest.TestCase):
    def setUp(self):
        self.plot_properties = plotting.MultiPlotProperties()

    def test_instantiate_class(self):
        pass

    def test_has_figure_property(self):
        self.assertTrue(hasattr(self.plot_properties, 'figure'))

    def test_has_axes_property(self):
        self.assertTrue(hasattr(self.plot_properties, 'axes'))

    def test_has_drawings_property(self):
        self.assertTrue(hasattr(self.plot_properties, 'drawings'))

    def test_has_legend_property(self):
        self.assertTrue(hasattr(self.plot_properties, 'legend'))

    def test_has_to_dict_method(self):
        self.assertTrue(hasattr(self.plot_properties, 'to_dict'))
        self.assertTrue(callable(self.plot_properties.to_dict))

    def test_has_from_dict_method(self):
        self.assertTrue(hasattr(self.plot_properties, 'from_dict'))
        self.assertTrue(callable(self.plot_properties.from_dict))

    def test_apply_sets_axis_properties(self):
        self.plot_properties.axes.xlabel = 'foo'
        plot = plotting.MultiPlotter()
        plot.datasets = [dataset.Dataset()]
        plot.plot()
        self.plot_properties.apply(plotter=plot)
        self.assertEqual(self.plot_properties.axes.xlabel,
                         plot.axes.get_xlabel())

    def test_apply_sets_legend_properties(self):
        self.plot_properties.legend.loc = 'center'
        plot = plotting.MultiPlotter()
        plot.datasets = [dataset.Dataset()]
        plot.plot()
        plot.legend = plot.axes.legend()
        self.plot_properties.apply(plotter=plot)
        self.assertEqual(self.plot_properties.legend.loc,
                         plot.legend.loc)
