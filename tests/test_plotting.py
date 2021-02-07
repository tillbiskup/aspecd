"""Tests for plotting."""

import matplotlib.figure
import matplotlib.axes
import matplotlib.legend
import matplotlib.pyplot as plt
import numpy as np
import os
import unittest

import aspecd.exceptions
from aspecd import plotting, utils, dataset


class TestPlotter(unittest.TestCase):
    def setUp(self):
        self.plotter = plotting.Plotter()
        self.filename = 'Testfile.png'

    def tearDown(self):
        if os.path.isfile(self.filename):
            os.remove(self.filename)
        if self.plotter.fig:
            plt.close(self.plotter.fig)

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

    def test_has_style_property(self):
        self.assertTrue(hasattr(self.plotter, 'style'))

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

    def test_plot_sets_no_new_figure_property_if_existing(self):
        fig, ax = plt.subplots()
        self.plotter.figure = fig
        self.plotter.axes = ax
        self.plotter.plot()
        self.assertIs(fig, self.plotter.figure)

    def test_plot_sets_no_new_axes_property_if_existing(self):
        fig, ax = plt.subplots()
        self.plotter.figure = fig
        self.plotter.axes = ax
        self.plotter.plot()
        self.assertIs(ax, self.plotter.axes)

    def test_save_without_saver_raises(self):
        with self.assertRaises(aspecd.exceptions.MissingSaverError):
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

    def test_plot_with_unknown_style_raises(self):
        self.plotter.style = 'foo'
        with self.assertRaises(aspecd.exceptions.StyleNotFoundError):
            self.plotter.plot()

    def test_plot_adds_zero_lines(self):
        self.plotter.parameters['show_zero_lines'] = True
        self.plotter.plot()
        self.assertEqual(2, len(self.plotter.ax.get_lines()))

    def test_plot_without_zero_lines_does_not_add_zero_lines(self):
        self.plotter.parameters['show_zero_lines'] = False
        self.plotter.plot()
        self.assertEqual(0, len(self.plotter.ax.get_lines()))

    def test_plot_applies_properties_to_zero_lines(self):
        self.plotter.parameters['show_zero_lines'] = True
        self.plotter.properties.zero_lines.color = '#999'
        self.plotter.plot()
        self.assertEqual(self.plotter.properties.zero_lines.color,
                         self.plotter.ax.get_lines()[0]._color)


class TestSinglePlotter(unittest.TestCase):
    def setUp(self):
        self.plotter = plotting.SinglePlotter()

    def tearDown(self):
        if self.plotter.fig:
            plt.close(self.plotter.fig)

    def test_instantiate_class(self):
        pass

    def test_has_drawing_property(self):
        self.assertTrue(hasattr(self.plotter, 'drawing'))

    def test_plot_without_dataset_raises(self):
        with self.assertRaises(aspecd.exceptions.MissingDatasetError):
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

    def tearDown(self):
        if self.plotter.fig:
            plt.close(self.plotter.fig)

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
        with self.assertRaises(
                aspecd.exceptions.PlotNotApplicableToDatasetError):
            self.plotter.plot(dataset_)

    def test_set_line_colour_from_dict(self):
        line_colour = '#cccccc'
        properties = {'drawing': {'color': line_colour}}
        self.plotter.properties.from_dict(properties)
        self.assertEqual(line_colour, self.plotter.properties.drawing.color)

    def test_plot_sets_correct_line_color(self):
        color = '#cccccc'
        dict_ = {'drawing': {'color': color}}
        self.plotter.properties.from_dict(dict_)
        self.plotter.plot(dataset=dataset.Dataset())
        self.assertEqual(color, self.plotter.drawing.get_color())

    def test_plot_adds_no_x_zero_line_if_out_of_range(self):
        self.plotter.parameters['show_zero_lines'] = True
        dataset_ = aspecd.dataset.CalculatedDataset()
        dataset_.data.data = np.random.random([10])+5
        plotter = dataset_.plot(self.plotter)
        self.assertEqual([0., 0.], plotter.ax.get_lines()[1].get_xdata())

    def test_plot_adds_no_y_zero_line_if_out_of_range(self):
        self.plotter.parameters['show_zero_lines'] = True
        dataset_ = aspecd.dataset.CalculatedDataset()
        dataset_.data.data = np.random.random([10])-0.5
        dataset_.data.axes[0].values = np.linspace(4, 5, 10)
        plotter = dataset_.plot(self.plotter)
        print(plotter.ax.get_lines())
        self.assertEqual([0., 0.], plotter.ax.get_lines()[1].get_ydata())


class TestSinglePlotter2D(unittest.TestCase):
    def setUp(self):
        self.plotter = plotting.SinglePlotter2D()

    def tearDown(self):
        if self.plotter.fig:
            plt.close(self.plotter.fig)

    def test_instantiate_class(self):
        pass

    def test_plot_with_1D_dataset_raises(self):
        dataset_ = aspecd.dataset.CalculatedDataset()
        dataset_.data.data = np.random.random([5])
        with self.assertRaises(
                aspecd.exceptions.PlotNotApplicableToDatasetError):
            dataset_.plot(self.plotter)

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

    def test_plot_with_dataset_sets_axes_labels(self):
        test_dataset = dataset.Dataset()
        test_dataset.data.data = np.random.random([5, 5])
        test_dataset.data.axes[0].quantity = 'zero'
        test_dataset.data.axes[0].unit = 'foo'
        test_dataset.data.axes[1].quantity = 'one'
        test_dataset.data.axes[1].unit = 'bar'
        xlabel = '$' + test_dataset.data.axes[1].quantity + '$' + ' / ' + \
                 test_dataset.data.axes[1].unit
        ylabel = '$' + test_dataset.data.axes[0].quantity + '$' + ' / ' + \
                 test_dataset.data.axes[0].unit
        plotter = test_dataset.plot(self.plotter)
        self.assertEqual(xlabel, plotter.axes.get_xlabel())
        self.assertEqual(ylabel, plotter.axes.get_ylabel())


class TestSinglePlotter2DStacked(unittest.TestCase):
    def setUp(self):
        self.plotter = plotting.SinglePlotter2DStacked()

    def tearDown(self):
        if self.plotter.fig:
            plt.close(self.plotter.fig)

    def test_instantiate_class(self):
        pass

    def test_plot_with_1D_dataset_raises(self):
        dataset_ = aspecd.dataset.CalculatedDataset()
        dataset_.data.data = np.random.random([5])
        with self.assertRaises(
                aspecd.exceptions.PlotNotApplicableToDatasetError):
            plotter = dataset_.plot(self.plotter)

    def test_parameters_have_stacking_dimension_key(self):
        self.assertIn('stacking_dimension', self.plotter.parameters)

    def test_plot_consists_of_correct_number_of_lines(self):
        dataset_ = aspecd.dataset.CalculatedDataset()
        dataset_.data.data = np.random.random([5, 10]) - 0.5
        plotter = dataset_.plot(self.plotter)
        self.assertEqual(12, len(plotter.axes.get_lines()))

    def test_plot_along_zero_dim_consists_of_correct_number_of_lines(self):
        self.plotter.parameters['stacking_dimension'] = 0
        dataset_ = aspecd.dataset.CalculatedDataset()
        dataset_.data.data = np.random.random([5, 10]) - 0.5
        plotter = dataset_.plot(self.plotter)
        self.assertEqual(7, len(plotter.axes.get_lines()))

    def test_plot_stacks_plots(self):
        dataset_ = aspecd.dataset.CalculatedDataset()
        dataset_.data.data = np.random.random([5, 10]) - 0.5
        plotter = dataset_.plot(self.plotter)
        self.assertGreater(max(plotter.axes.get_lines()[5].get_ydata()),
                           max(plotter.axes.get_lines()[0].get_ydata())*3)

    def test_plot_along_zero_dim_stacks_plots(self):
        self.plotter.parameters['stacking_dimension'] = 0
        dataset_ = aspecd.dataset.CalculatedDataset()
        dataset_.data.data = np.random.random([5, 10]) - 0.5
        plotter = dataset_.plot(self.plotter)
        self.assertGreater(max(plotter.axes.get_lines()[4].get_ydata()),
                           max(plotter.axes.get_lines()[0].get_ydata())*3)

    def test_plot_with_offset_stacks_plots_accordingly(self):
        self.plotter.parameters['offset'] = 2
        dataset_ = aspecd.dataset.CalculatedDataset()
        dataset_.data.data = np.random.random([5, 10]) - 0.5
        plotter = dataset_.plot(self.plotter)
        self.assertGreater(max(plotter.axes.get_lines()[5].get_ydata()),
                           max(plotter.axes.get_lines()[0].get_ydata())*10)


class TestMultiPlotter(unittest.TestCase):
    def setUp(self):
        self.plotter = plotting.MultiPlotter()

    def tearDown(self):
        if self.plotter.fig:
            plt.close(self.plotter.fig)

    def test_instantiate_class(self):
        pass

    def test_has_datasets_property(self):
        self.assertTrue(hasattr(self.plotter, 'datasets'))

    def test_datasets_property_is_list(self):
        self.assertTrue(isinstance(self.plotter.datasets, list))

    def test_plot_without_datasets_raises(self):
        with self.assertRaises(aspecd.exceptions.MissingDatasetError):
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
        self.plotter.parameters['axes'][1].quantity = 'foo2'
        self.plotter.parameters['axes'][1].unit = 'bar2'
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

    def test_plot_with_datasets_adds_drawing_properties(self):
        self.plotter.datasets.append(dataset.Dataset())
        self.plotter.plot()
        self.assertEqual(len(self.plotter.datasets),
                         len(self.plotter.properties.drawings))

    def test_plot_with_show_legend_set_to_true_adds_legend(self):
        self.plotter.datasets.append(dataset.Dataset())
        self.plotter.parameters['show_legend'] = True
        self.plotter.plot()
        self.assertIs(type(self.plotter.legend), matplotlib.legend.Legend)


class TestMultiPlotter1D(unittest.TestCase):
    def setUp(self):
        self.plotter = plotting.MultiPlotter1D()

    def tearDown(self):
        if self.plotter.fig:
            plt.close(self.plotter.fig)

    def test_instantiate_class(self):
        pass

    def test_description_is_sensible(self):
        self.assertNotIn('Abstract', self.plotter.description)

    def test_properties_are_of_correct_type(self):
        self.assertIs(type(self.plotter.properties),
                      aspecd.plotting.MultiPlot1DProperties)

    def test_has_type_property(self):
        self.assertTrue(hasattr(self.plotter, 'type'))

    def test_set_type(self):
        plot_type = 'loglog'
        self.plotter.type = plot_type
        self.assertEqual(self.plotter.type, plot_type)

    def test_setting_wrong_type_raises(self):
        with self.assertRaises(TypeError):
            self.plotter.type = 'foo'

    def test_plot_with_2D_data_raises(self):
        dataset_ = dataset.Dataset()
        dataset_.data.data = np.random.rand(3, 2)
        self.plotter.datasets.append(dataset_)
        with self.assertRaises(
                aspecd.exceptions.PlotNotApplicableToDatasetError):
            self.plotter.plot()

    def test_plot_with_datasets(self):
        self.plotter.datasets.append(dataset.Dataset())
        self.plotter.plot()

    def test_plot_with_datasets_adds_drawing_to_properties(self):
        self.plotter.datasets.append(dataset.Dataset())
        self.plotter.plot()
        self.assertEqual(1, len(self.plotter.properties.drawings))

    def test_added_drawing_is_correct_type(self):
        self.plotter.datasets.append(dataset.Dataset())
        self.plotter.plot()
        self.assertIs(type(self.plotter.properties.drawings[0]),
                      aspecd.plotting.LineProperties)

    def test_plot_sets_correct_line_color(self):
        color = '#000000'
        dict_ = {'drawings': [{'color': color}]}
        self.plotter.properties.from_dict(dict_)
        self.plotter.datasets.append(dataset.Dataset())
        self.plotter.plot()
        self.assertEqual(color, self.plotter.drawings[0].get_color())

    def test_plot_with_show_legend_sets_legend_label(self):
        dataset_ = dataset.Dataset()
        dataset_.label = 'foo'
        self.plotter.datasets.append(dataset_)
        self.plotter.parameters['show_legend'] = True
        self.plotter.plot()
        self.assertEqual(dataset_.label,
                         self.plotter.legend.get_texts()[0].get_text())


class TestCompositePlotter(unittest.TestCase):
    def setUp(self):
        self.plotter = plotting.CompositePlotter()
        self.dataset = aspecd.dataset.CalculatedDataset()
        self.dataset.data.data = np.sin(np.linspace(0, 2*np.pi, 101))

    def tearDown(self):
        if self.plotter.fig:
            plt.close(self.plotter.fig)

    def test_instantiate_class(self):
        pass

    def test_description_is_sensible(self):
        self.assertIn('Composite', self.plotter.description)

    def test_has_grid_dimensions_property(self):
        self.assertTrue(hasattr(self.plotter, 'grid_dimensions'))

    def test_has_subplot_locations_property(self):
        self.assertTrue(hasattr(self.plotter, 'subplot_locations'))

    def test_has_plotter_property(self):
        self.assertTrue(hasattr(self.plotter, 'plotter'))

    def test_plot_with_single_subplot_adds_axis_to_axes(self):
        self.plotter.grid_dimensions = [1, 1]
        self.plotter.subplot_locations = [[0, 0, 1, 1]]
        single_plotter = plotting.SinglePlotter1D()
        single_plotter.dataset = self.dataset
        self.plotter.plotter.append(single_plotter)
        self.plotter.plot()
        self.assertEqual(1, len(self.plotter.axes))

    def test_plot_with_multiple_subplots_adds_axes_to_axes(self):
        self.plotter.grid_dimensions = [2, 2]
        self.plotter.subplot_locations = [[0, 0, 1, 1],
                                          [1, 0, 1, 1],
                                          [0, 1, 2, 1]]
        single_plotter = plotting.SinglePlotter1D()
        single_plotter.dataset = self.dataset
        self.plotter.plotter.append(single_plotter)
        self.plotter.plotter.append(single_plotter)
        self.plotter.plotter.append(single_plotter)
        self.plotter.plot()
        self.assertEqual(len(self.plotter.subplot_locations),
                         len(self.plotter.axes))

    def test_plot_with_single_subplot_and_plotter_plots_line(self):
        self.plotter.grid_dimensions = [1, 1]
        self.plotter.subplot_locations = [[0, 0, 1, 1]]
        single_plotter = plotting.SinglePlotter1D()
        single_plotter.dataset = self.dataset
        self.plotter.plotter.append(single_plotter)
        self.plotter.plot()
        self.assertTrue(self.plotter.axes[0].has_data())

    def test_plot_without_plotter_raises(self):
        self.plotter.grid_dimensions = [1, 1]
        self.plotter.subplot_locations = [[0, 0, 1, 1]]
        with self.assertRaises(aspecd.exceptions.MissingPlotterError):
            self.plotter.plot()

    def test_plot_with_not_enough_plotters_raises(self):
        self.plotter.grid_dimensions = [2, 2]
        self.plotter.subplot_locations = [[0, 0, 1, 1],
                                          [1, 0, 1, 1],
                                          [0, 1, 2, 1]]
        single_plotter = plotting.SinglePlotter1D()
        single_plotter.dataset = self.dataset
        self.plotter.plotter.append(single_plotter)
        self.plotter.plotter.append(single_plotter)
        with self.assertRaises(aspecd.exceptions.MissingPlotterError):
            self.plotter.plot()

    def test_plot_with_datasets_adds_axes_to_properties(self):
        self.plotter.grid_dimensions = [1, 1]
        self.plotter.subplot_locations = [[0, 0, 1, 1]]
        single_plotter = plotting.SinglePlotter1D()
        single_plotter.dataset = self.dataset
        self.plotter.plotter.append(single_plotter)
        self.plotter.plot()
        self.assertEqual(1, len(self.plotter.properties.axes))

    def test_added_axes_is_correct_type(self):
        self.plotter.grid_dimensions = [1, 1]
        self.plotter.subplot_locations = [[0, 0, 1, 1]]
        single_plotter = plotting.SinglePlotter1D()
        single_plotter.dataset = self.dataset
        self.plotter.plotter.append(single_plotter)
        self.plotter.plot()
        self.assertIs(type(self.plotter.properties.axes[0]),
                      aspecd.plotting.AxesProperties)


class TestSingleCompositePlotter(unittest.TestCase):
    def setUp(self):
        self.plotter = plotting.SingleCompositePlotter()

    def tearDown(self):
        if self.plotter.fig:
            plt.close(self.plotter.fig)

    def test_instantiate_class(self):
        pass

    def test_description_is_sensible(self):
        self.assertIn('single dataset', self.plotter.description)

    def test_plot_without_dataset_raises(self):
        with self.assertRaises(aspecd.exceptions.MissingDatasetError):
            self.plotter.plot()

    def test_plot_with_preset_dataset(self):
        self.plotter.dataset = dataset.Dataset()
        self.plotter.grid_dimensions = [1, 1]
        self.plotter.subplot_locations = [[0, 0, 1, 1]]
        single_plotter = plotting.SinglePlotter1D()
        self.plotter.plotter.append(single_plotter)
        self.plotter.plot()

    def test_plot_from_dataset_sets_dataset(self):
        self.plotter.grid_dimensions = [1, 1]
        self.plotter.subplot_locations = [[0, 0, 1, 1]]
        single_plotter = plotting.SinglePlotter1D()
        self.plotter.plotter.append(single_plotter)
        test_dataset = dataset.Dataset()
        plotter = test_dataset.plot(self.plotter)
        self.assertTrue(isinstance(plotter.dataset, dataset.Dataset))

    def test_plot_with_dataset(self):
        self.plotter.grid_dimensions = [1, 1]
        self.plotter.subplot_locations = [[0, 0, 1, 1]]
        single_plotter = plotting.SinglePlotter1D()
        self.plotter.plotter.append(single_plotter)
        test_dataset = dataset.Dataset()
        self.plotter.plot(dataset=test_dataset)
        self.assertGreater(len(test_dataset.representations), 0)


class TestSaver(unittest.TestCase):
    def setUp(self):
        self.saver = plotting.Saver()
        self.filename = 'test.pdf'

    def tearDown(self):
        if os.path.isfile(self.filename):
            os.remove(self.filename)
        if self.saver.plotter and self.saver.plotter.fig:
            plt.close(self.saver.plotter.fig)

    def test_instantiate_class(self):
        pass

    def test_has_save_method(self):
        self.assertTrue(hasattr(self.saver, 'save'))
        self.assertTrue(callable(self.saver.save))

    def test_save_without_filename_raises(self):
        with self.assertRaises(aspecd.exceptions.MissingFilenameError):
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
        with self.assertRaises(aspecd.exceptions.MissingPlotError):
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

    def test_save_with_singleplotter1d(self):
        test_dataset = dataset.Dataset()
        plotter = plotting.SinglePlotter1D()
        plotter = test_dataset.plot(plotter)
        plotter.plot()
        self.saver.filename = self.filename
        self.saver.save(plotter)

    def test_save_with_singleplotter2d(self):
        test_dataset = dataset.Dataset()
        test_dataset.data.data = np.random.rand(3, 2)
        plotter = plotting.SinglePlotter2D()
        plotter = test_dataset.plot(plotter)
        plotter.plot()
        self.saver.filename = self.filename
        self.saver.save(plotter)

    def test_save_with_multiplotter(self):
        plotter = plotting.MultiPlotter()
        plotter.datasets.append(dataset.Dataset())
        plotter.plot()
        self.saver.filename = self.filename
        self.saver.save(plotter)


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
        with self.assertRaises(aspecd.exceptions.MissingDrawingError):
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
        with self.assertRaises(aspecd.exceptions.MissingDrawingError):
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
        with self.assertRaises(aspecd.exceptions.MissingPlotterError):
            self.plot_properties.apply()

    def test_apply_sets_properties(self):
        self.plot_properties.figure.dpi = 300.0
        plot = plotting.Plotter()
        plot.plot()
        self.plot_properties.apply(plotter=plot)
        self.assertEqual(self.plot_properties.figure.dpi,
                         plot.figure.get_dpi())
        plt.close(plot.figure)


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
        for prop in ['size', 'dpi', 'title']:
            self.assertTrue(hasattr(self.figure_properties, prop))

    def test_has_apply_method(self):
        self.assertTrue(hasattr(self.figure_properties, 'apply'))
        self.assertTrue(callable(self.figure_properties.apply))

    def test_apply_without_argument_raises(self):
        with self.assertRaises(aspecd.exceptions.MissingFigureError):
            self.figure_properties.apply()

    def test_apply_sets_figure_dpi(self):
        self.figure_properties.dpi = 300.0
        plot = plotting.Plotter()
        plot.plot()
        self.figure_properties.apply(figure=plot.figure)
        self.assertEqual(self.figure_properties.dpi, plot.figure.get_dpi())
        plt.close(plot.figure)

    def test_apply_sets_figure_size(self):
        self.figure_properties.size = (10, 5)
        plot = plotting.Plotter()
        plot.plot()
        self.figure_properties.apply(figure=plot.figure)
        self.assertListEqual(list(self.figure_properties.size),
                             list(plot.figure.get_size_inches()))
        plt.close(plot.figure)

    def test_apply_sets_figure_title(self):
        self.figure_properties.title = 'foo'
        plot = plotting.Plotter()
        plot.plot()
        self.figure_properties.apply(figure=plot.figure)
        self.assertEqual(self.figure_properties.title,
                         plot.figure._suptitle.get_text())
        plt.close(plot.figure)


class TestAxisProperties(unittest.TestCase):
    def setUp(self):
        self.axis_properties = plotting.AxesProperties()

    def test_instantiate_class(self):
        pass

    def test_has_to_dict_method(self):
        self.assertTrue(hasattr(self.axis_properties, 'to_dict'))
        self.assertTrue(callable(self.axis_properties.to_dict))

    def test_has_from_dict_method(self):
        self.assertTrue(hasattr(self.axis_properties, 'from_dict'))
        self.assertTrue(callable(self.axis_properties.from_dict))

    def test_has_properties(self):
        for prop in ['aspect', 'facecolor', 'title', 'xlabel', 'xlim',
                     'xscale', 'xticklabels', 'xticks', 'ylabel', 'ylim',
                     'yscale', 'yticklabels', 'yticks']:
            self.assertTrue(hasattr(self.axis_properties, prop))

    def test_has_apply_properties_method(self):
        self.assertTrue(hasattr(self.axis_properties, 'apply'))
        self.assertTrue(callable(self.axis_properties.apply))

    def test_apply_properties_without_argument_raises(self):
        with self.assertRaises(aspecd.exceptions.MissingAxisError):
            self.axis_properties.apply()

    def test_apply_properties_sets_axis_properties(self):
        self.axis_properties.xlabel = 'foo'
        plot = plotting.Plotter()
        plot.plot()
        self.axis_properties.apply(axes=plot.axes)
        self.assertEqual(self.axis_properties.xlabel, plot.axes.get_xlabel())
        plt.close(plot.figure)

    def test_apply_properties_from_dict_sets_axis_properties(self):
        label = 'foo'
        properties = {'axes': {'xlabel': label}}
        plot = plotting.MultiPlotter1D()
        plot.datasets.append(aspecd.dataset.Dataset())
        plot.properties.from_dict(properties)
        plot.plot()
        self.assertEqual(label, plot.axes.get_xlabel())
        plt.close(plot.figure)


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
        for prop in ['loc', 'frameon']:
            self.assertTrue(hasattr(self.legend_properties, prop))

    def test_has_apply_method(self):
        self.assertTrue(hasattr(self.legend_properties, 'apply'))
        self.assertTrue(callable(self.legend_properties.apply))

    def test_apply_without_argument_raises(self):
        with self.assertRaises(aspecd.exceptions.MissingLegendError):
            self.legend_properties.apply()

    def test_apply_properties_sets_legend_properties(self):
        self.legend_properties.loc = 'center'
        plot = plotting.Plotter()
        plot.plot()
        legend = plot.axes.legend()
        self.legend_properties.apply(legend=legend)
        self.assertEqual(self.legend_properties.loc, legend.loc)
        plt.close(plot.figure)

    def test_location_sets_legend_loc(self):
        location = 5
        self.legend_properties.location = location
        plot = plotting.Plotter()
        plot.properties.legend = self.legend_properties
        plot.parameters['show_legend'] = True
        plot.plot()
        legend = plot.legend
        self.assertEqual(location, legend._loc)
        plt.close(plot.figure)

    def test_location_from_dict_sets_legend_loc(self):
        location = 5
        properties = {'legend': {'location': location}}
        plot = plotting.Plotter()
        plot.properties.from_dict(properties)
        plot.parameters['show_legend'] = True
        plot.plot()
        legend = plot.legend
        self.assertEqual(location, legend._loc)
        plt.close(plot.figure)

    def test_frameon_sets_legend_frameon(self):
        frameon = False
        self.legend_properties.frameon = frameon
        plot = plotting.Plotter()
        plot.properties.legend = self.legend_properties
        plot.parameters['show_legend'] = True
        plot.plot()
        legend = plot.legend
        self.assertEqual(frameon, legend.get_frame_on())
        plt.close(plot.figure)

    def test_location_not_included_in_to_dict(self):
        self.assertNotIn('location', self.legend_properties.to_dict())


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
        plt.close(plot.figure)

    def test_apply_sets_drawing_properties(self):
        self.plot_properties.drawing.label = 'foo'
        plot = plotting.SinglePlotter1D()
        plot.plot(dataset=dataset.Dataset())
        self.plot_properties.apply(plotter=plot)
        self.assertEqual(self.plot_properties.drawing.label,
                         plot.drawing.get_label())
        plt.close(plot.figure)


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
        plt.close(plot.figure)


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
        plt.close(plot.figure)

    def test_apply_sets_legend_properties(self):
        self.plot_properties.legend.loc = 'center'
        plot = plotting.MultiPlotter()
        plot.datasets = [dataset.Dataset()]
        plot.plot()
        plot.legend = plot.axes.legend()
        self.plot_properties.apply(plotter=plot)
        self.assertEqual(self.plot_properties.legend.loc,
                         plot.legend.loc)
        plt.close(plot.figure)

    def test_from_dict_sets_drawings(self):
        dict_ = {'drawings': [{'label': 'foo'}]}
        self.plot_properties.from_dict(dict_)
        self.assertEqual('foo', self.plot_properties.drawings[0].label)

    def test_from_dict_sets_multiple_drawings(self):
        dict_ = {'drawings': [{'label': 'foo'}, {'label': 'bar'}]}
        self.plot_properties.from_dict(dict_)
        self.assertEqual('foo', self.plot_properties.drawings[0].label)
        self.assertEqual('bar', self.plot_properties.drawings[1].label)

    def test_from_dict_does_not_add_drawing_if_it_exists(self):
        self.plot_properties.drawings.append(
            aspecd.plotting.DrawingProperties())
        dict_ = {'drawings': [{'label': 'foo'}]}
        self.plot_properties.from_dict(dict_)
        self.assertEqual(1, len(self.plot_properties.drawings))

    def test_from_dict_adds_missing_drawing(self):
        dict_ = {'drawings': [{'label': 'foo'}]}
        self.plot_properties.from_dict(dict_)
        self.assertEqual(1, len(self.plot_properties.drawings))

    def test_from_dict_adds_missing_drawings(self):
        dict_ = {'drawings': [{'label': 'foo'}, {'label': 'bar'}]}
        self.plot_properties.from_dict(dict_)
        self.assertEqual(2, len(self.plot_properties.drawings))

    def test_from_dict_sets_legend(self):
        dict_ = {'legend': {'loc': 'center'}, 'drawings': [{'label': 'foo'}]}
        self.plot_properties.from_dict(dict_)
        self.assertEqual('center', self.plot_properties.legend.loc)


class TestMultiPlot1DProperties(unittest.TestCase):
    def setUp(self):
        self.plot_properties = plotting.MultiPlot1DProperties()

    def test_instantiate_class(self):
        pass

    def test_added_drawing_is_line_properties_object(self):
        self.plot_properties.add_drawing()
        self.assertIs(type(self.plot_properties.drawings[0]),
                      aspecd.plotting.LineProperties)

    def test_added_drawing_has_correct_default_colour(self):
        property_cycle = plt.rcParams['axes.prop_cycle'].by_key()
        colour = property_cycle["color"][0]
        self.plot_properties.add_drawing()
        self.assertEqual(colour, self.plot_properties.drawings[0].color)

    def test_drawing_has_correct_color_if_more_drawings_than_colors(self):
        property_cycle = plt.rcParams['axes.prop_cycle'].by_key()
        colour = property_cycle["color"][0]
        for idx in range(0, len(property_cycle["color"])+1):
            self.plot_properties.add_drawing()
        self.assertEqual(colour, self.plot_properties.drawings[0].color)

    def test_added_drawing_has_correct_default_linewidth(self):
        linewidth = plt.rcParams['lines.linewidth']
        self.plot_properties.add_drawing()
        self.assertEqual(linewidth, self.plot_properties.drawings[0].linewidth)

    def test_added_drawing_has_correct_default_linestyle(self):
        linewidth = plt.rcParams['lines.linestyle']
        self.plot_properties.add_drawing()
        self.assertEqual(linewidth, self.plot_properties.drawings[0].linestyle)

    def test_added_drawing_has_correct_default_marker(self):
        linewidth = plt.rcParams['lines.marker']
        self.plot_properties.add_drawing()
        self.assertEqual(linewidth, self.plot_properties.drawings[0].marker)


class TestCompositePlotProperties(unittest.TestCase):
    def setUp(self):
        self.plot_properties = plotting.CompositePlotProperties()

    def test_instantiate_class(self):
        pass

    def test_has_figure_property(self):
        self.assertTrue(hasattr(self.plot_properties, 'figure'))

    def test_has_axes_property(self):
        self.assertTrue(hasattr(self.plot_properties, 'axes'))

    def test_has_to_dict_method(self):
        self.assertTrue(hasattr(self.plot_properties, 'to_dict'))
        self.assertTrue(callable(self.plot_properties.to_dict))

    def test_has_from_dict_method(self):
        self.assertTrue(hasattr(self.plot_properties, 'from_dict'))
        self.assertTrue(callable(self.plot_properties.from_dict))

    def test_added_axes_is_axes_properties_object(self):
        self.plot_properties.add_axes()
        self.assertIs(type(self.plot_properties.axes[0]),
                      aspecd.plotting.AxesProperties)

    def test_from_dict_sets_axes(self):
        dict_ = {'axes': [{'xlabel': 'foo'}]}
        self.plot_properties.from_dict(dict_)
        self.assertEqual('foo', self.plot_properties.axes[0].xlabel)

    def test_from_dict_sets_multiple_axes(self):
        dict_ = {'axes': [{'xlabel': 'foo'}, {'xlabel': 'bar'}]}
        self.plot_properties.from_dict(dict_)
        self.assertEqual('foo', self.plot_properties.axes[0].xlabel)
        self.assertEqual('bar', self.plot_properties.axes[1].xlabel)

    def test_from_dict_does_not_add_axes_if_it_exists(self):
        self.plot_properties.axes.append(
            aspecd.plotting.DrawingProperties())
        dict_ = {'axes': [{'xlabel': 'foo'}]}
        self.plot_properties.from_dict(dict_)
        self.assertEqual(1, len(self.plot_properties.axes))

    def test_from_dict_adds_missing_axes(self):
        dict_ = {'axes': [{'xlabel': 'foo'}]}
        self.plot_properties.from_dict(dict_)
        self.assertEqual(1, len(self.plot_properties.axes))

    def test_from_dict_adds_multiple_missing_axes(self):
        dict_ = {'axes': [{'xlabel': 'foo'}, {'xlabel': 'bar'}]}
        self.plot_properties.from_dict(dict_)
        self.assertEqual(2, len(self.plot_properties.axes))

    def test_apply_sets_axis_properties(self):
        self.plot_properties.add_axes()
        self.plot_properties.axes[0].xlabel = 'foo'
        plot = plotting.CompositePlotter()
        plot.grid_dimensions = [1, 1]
        plot.subplot_locations = [[0, 0, 1, 1]]
        single_plotter = plotting.SinglePlotter1D()
        dataset_ = aspecd.dataset.CalculatedDataset()
        dataset_.data.data = np.sin(np.linspace(0, 2*np.pi, 101))
        single_plotter.dataset = dataset_
        plot.plotter.append(single_plotter)
        plot.plot()
        self.plot_properties.apply(plotter=plot)
        self.assertEqual(self.plot_properties.axes[0].xlabel,
                         plot.axes[0].get_xlabel())
        plt.close(plot.figure)
