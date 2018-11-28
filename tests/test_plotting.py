"""Tests for plotting."""

import matplotlib.figure
import matplotlib.axes
import matplotlib.pyplot as plt
import unittest

from aspecd import plotting, utils, dataset


class TestPlotter(unittest.TestCase):
    def setUp(self):
        self.plotter = plotting.Plotter()

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
        filename = 'Testfile'
        saver = plotting.Saver()
        saver.filename = filename
        returned_saver = self.plotter.save(saver)
        self.assertTrue(isinstance(returned_saver, plotting.Saver))

    def test_save_sets_plot_in_saver(self):
        filename = 'Testfile'
        saver = plotting.Saver()
        saver.filename = filename
        returned_saver = self.plotter.save(saver)
        self.assertEqual(returned_saver.plotter, self.plotter)


class TestSinglePlotter(unittest.TestCase):
    def setUp(self):
        self.plotter = plotting.SinglePlotter()

    def test_instantiate_class(self):
        pass

    def test_plot_without_dataset_raises(self):
        with self.assertRaises(plotting.MissingDatasetError):
            self.plotter.plot()

    def test_plot_with_dataset(self):
        self.plotter.dataset = dataset.Dataset()
        self.plotter.plot()

    def test_plot_with_dataset_sets_dataset(self):
        test_dataset = dataset.Dataset()
        plotter = test_dataset.plot(self.plotter)
        self.assertTrue(isinstance(plotter.dataset, dataset.Dataset))


class TestMultiPlotter(unittest.TestCase):
    def setUp(self):
        self.plotter = plotting.MultiPlotter()

    def test_instantiate_class(self):
        pass

    def test_has_datasets_property(self):
        self.assertTrue(hasattr(self.plotter, 'datasets'))

    def test_datasets_property_is_dict(self):
        self.assertTrue(isinstance(self.plotter.datasets, list))

    def test_plot_without_datasets_raises(self):
        with self.assertRaises(plotting.MissingDatasetError):
            self.plotter.plot()

    def test_plot_with_datasets(self):
        self.plotter.datasets.append(dataset.Dataset())
        self.plotter.plot()


class TestSaver(unittest.TestCase):
    def setUp(self):
        self.saver = plotting.Saver()

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
        self.saver.filename = 'Testfile'
        self.saver.save()

    def test_instantiate_with_filename_sets_filename(self):
        filename = 'Testfile'
        self.saver = plotting.Saver(filename)
        self.assertEqual(self.saver.filename, filename)

    def test_save_without_plotter_raises(self):
        self.saver.filename = 'Testfile'
        with self.assertRaises(plotting.MissingPlotError):
            self.saver.save()

    def test_save_with_plotter_sets_plotter(self):
        plotter = plotting.Plotter()
        self.saver.filename = 'Testfile'
        self.saver.save(plotter)
        self.assertEqual(self.saver.plotter, plotter)

    def test_has_parameters_property(self):
        self.assertTrue(hasattr(self.saver, 'parameters'))

    def test_parameters_property_is_dict(self):
        self.assertTrue(isinstance(self.saver.parameters, dict))
