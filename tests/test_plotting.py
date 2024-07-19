"""Tests for plotting."""
import contextlib
import hashlib
import io
import warnings

import matplotlib.axes
import matplotlib.collections
import matplotlib.figure
import matplotlib.legend
import matplotlib.lines
import matplotlib.pyplot as plt
import numpy as np
import os
import unittest
from unittest.mock import MagicMock, patch

import aspecd.exceptions
from aspecd import plotting, utils, dataset, annotation


class TestPlotter(unittest.TestCase):
    def setUp(self):
        self.plotter = plotting.Plotter()
        self.filename = "Testfile.png"

    def tearDown(self):
        if os.path.isfile(self.filename):
            os.remove(self.filename)
        if self.plotter.fig:
            plt.close(self.plotter.fig)

    def test_instantiate_class(self):
        pass

    def test_has_plot_method(self):
        self.assertTrue(hasattr(self.plotter, "plot"))
        self.assertTrue(callable(self.plotter.plot))

    def test_name_property_equals_full_class_name(self):
        full_class_name = utils.full_class_name(self.plotter)
        self.assertEqual(self.plotter.name, full_class_name)

    def test_has_parameters_property(self):
        self.assertTrue(hasattr(self.plotter, "parameters"))

    def test_parameters_property_is_dict(self):
        self.assertTrue(isinstance(self.plotter.parameters, dict))

    def test_has_properties_property(self):
        self.assertTrue(hasattr(self.plotter, "properties"))

    def test_has_description_property(self):
        self.assertTrue(hasattr(self.plotter, "description"))

    def test_description_property_is_string(self):
        self.assertTrue(isinstance(self.plotter.description, str))

    def test_has_figure_property(self):
        self.assertTrue(hasattr(self.plotter, "figure"))

    def test_has_fig_property(self):
        self.assertTrue(hasattr(self.plotter, "fig"))

    def test_fig_property_and_figure_property_are_identical(self):
        self.assertTrue(self.plotter.figure is self.plotter.fig)

    def test_has_axes_property(self):
        self.assertTrue(hasattr(self.plotter, "axes"))

    def test_has_ax_property(self):
        self.assertTrue(hasattr(self.plotter, "axes"))

    def test_ax_property_and_axes_property_are_identical(self):
        self.assertTrue(self.plotter.axes is self.plotter.ax)

    def test_has_filename_property(self):
        self.assertTrue(hasattr(self.plotter, "filename"))

    def test_has_caption_property(self):
        self.assertTrue(hasattr(self.plotter, "caption"))

    def test_has_style_property(self):
        self.assertTrue(hasattr(self.plotter, "style"))

    def test_has_label_property(self):
        self.assertTrue(hasattr(self.plotter, "label"))

    def test_has_comment_property(self):
        self.assertTrue(hasattr(self.plotter, "comment"))

    def test_has_to_dict_method(self):
        self.assertTrue(hasattr(self.plotter, "to_dict"))
        self.assertTrue(callable(self.plotter.to_dict))

    def test_to_dict_does_not_contain_certain_keys(self):
        for key in ["name", "description", "figure", "axes", "legend"]:
            with self.subTest(key=key):
                self.assertNotIn(key, self.plotter.to_dict())

    def test_has_save_method(self):
        self.assertTrue(hasattr(self.plotter, "save"))
        self.assertTrue(callable(self.plotter.save))

    def test_plot_sets_figure_property(self):
        self.plotter.plot()
        self.assertTrue(
            isinstance(self.plotter.figure, matplotlib.figure.Figure)
        )
        plt.close(self.plotter.figure)

    def test_plot_sets_fig_property(self):
        self.plotter.plot()
        self.assertTrue(
            isinstance(self.plotter.fig, matplotlib.figure.Figure)
        )
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
        self.assertEqual(
            self.plotter.properties.figure.dpi, self.plotter.figure.dpi
        )

    def test_plot_with_unknown_style_raises(self):
        self.plotter.style = "foo"
        with self.assertRaises(aspecd.exceptions.StyleNotFoundError):
            self.plotter.plot()

    def test_plot_with_style_restores_previous_settings_after_plot(self):
        orig_rcparams = matplotlib.rcParams.copy()
        self.plotter.style = "fivethirtyeight"
        self.plotter.plot()
        self.assertEqual(
            orig_rcparams["axes.facecolor"],
            matplotlib.rcParams["axes.facecolor"],
        )
        # Cleanup in case anything goes wrong
        dict.update(matplotlib.rcParams, orig_rcparams)

    def test_plot_with_xkcd_style_restores_previous_settings_after_plot(self):
        orig_rcparams = matplotlib.rcParams.copy()
        self.plotter.style = "xkcd"
        self.plotter.plot()
        self.assertEqual(
            orig_rcparams["path.effects"], matplotlib.rcParams["path.effects"]
        )
        # Cleanup in case anything goes wrong
        dict.update(matplotlib.rcParams, orig_rcparams)

    def test_plot_adds_zero_lines(self):
        self.plotter.parameters["show_zero_lines"] = True
        self.plotter.plot()
        self.assertEqual(2, len(self.plotter.ax.get_lines()))

    def test_plot_without_zero_lines_does_not_add_zero_lines(self):
        self.plotter.parameters["show_zero_lines"] = False
        self.plotter.plot()
        self.assertEqual(0, len(self.plotter.ax.get_lines()))

    def test_plot_applies_properties_to_zero_lines(self):
        self.plotter.parameters["show_zero_lines"] = True
        self.plotter.properties.zero_lines.color = "#999"
        self.plotter.plot()
        self.assertEqual(
            self.plotter.properties.zero_lines.color,
            self.plotter.ax.get_lines()[0]._color,
        )

    def test_plot_sets_tight_layout(self):
        self.plotter.parameters["tight_layout"] = True
        mock = MagicMock()
        with patch("matplotlib.figure.Figure.set_tight_layout", mock):
            self.plotter.plot()
        mock.assert_called()

    def test_plot_has_device_data_parameter(self):
        self.assertIn("device_data", self.plotter.parameters)

    def test_has_annotate_method(self):
        self.assertTrue(hasattr(self.plotter, "annotate"))
        self.assertTrue(callable(self.plotter.annotate))

    def test_annotate_adds_annotation_record(self):
        self.plotter.annotate(aspecd.annotation.PlotAnnotation())
        self.assertTrue(self.plotter.annotations)

    def test_added_annotation_record_is_plotannotation(self):
        self.plotter.annotate(aspecd.annotation.PlotAnnotation())
        self.assertIsInstance(
            self.plotter.annotations[-1], aspecd.annotation.PlotAnnotation
        )

    def test_annotate_returns_annotation_object(self):
        annotation = self.plotter.annotate(aspecd.annotation.PlotAnnotation())
        self.assertIsInstance(annotation, aspecd.annotation.PlotAnnotation)

    def test_has_delete_annotation_method(self):
        self.assertTrue(hasattr(self.plotter, "delete_annotation"))
        self.assertTrue(callable(self.plotter.delete_annotation))

    def test_delete_annotation_deletes_annotation_record(self):
        self.plotter.annotate(aspecd.annotation.PlotAnnotation())
        orig_len_annotations = len(self.plotter.annotations)
        self.plotter.delete_annotation(0)
        new_len_annotations = len(self.plotter.annotations)
        self.assertGreater(orig_len_annotations, new_len_annotations)

    def test_delete_annotation_deletes_correct_annotation_record(self):
        self.plotter.annotate(aspecd.annotation.PlotAnnotation())
        self.plotter.annotate(aspecd.annotation.PlotAnnotation())
        annotation_step = self.plotter.annotations[-1]
        self.plotter.delete_annotation(0)
        self.assertIs(annotation_step, self.plotter.annotations[-1])


class TestSinglePlotter(unittest.TestCase):
    def setUp(self):
        self.plotter = plotting.SinglePlotter()

    def tearDown(self):
        if self.plotter.fig:
            plt.close(self.plotter.fig)

    def test_instantiate_class(self):
        pass

    def test_has_drawing_property(self):
        self.assertTrue(hasattr(self.plotter, "drawing"))

    def test_has_data_property(self):
        self.assertTrue(hasattr(self.plotter, "data"))

    def test_to_dict_does_not_contain_certain_keys(self):
        for key in ["dataset", "drawing", "data"]:
            with self.subTest(key=key):
                self.assertNotIn(key, self.plotter.to_dict())

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
        test_dataset.data.axes[0].quantity = "foo"
        test_dataset.data.axes[0].unit = "bar"
        test_dataset.data.axes[1].quantity = "foo"
        test_dataset.data.axes[1].unit = "bar"
        xlabel = (
            "$"
            + test_dataset.data.axes[0].quantity
            + "$"
            + " / "
            + test_dataset.data.axes[0].unit
        )
        ylabel = (
            "$"
            + test_dataset.data.axes[1].quantity
            + "$"
            + " / "
            + test_dataset.data.axes[1].unit
        )
        plotter = test_dataset.plot(self.plotter)
        self.assertEqual(xlabel, plotter.axes.get_xlabel())
        self.assertEqual(ylabel, plotter.axes.get_ylabel())

    def test_axes_labels_with_empty_unit_without_slash(self):
        test_dataset = dataset.Dataset()
        test_dataset.data.axes[0].quantity = "foo"
        test_dataset.data.axes[0].unit = ""
        test_dataset.data.axes[1].quantity = "foo"
        test_dataset.data.axes[1].unit = ""
        xlabel = "$" + test_dataset.data.axes[0].quantity + "$"
        ylabel = "$" + test_dataset.data.axes[1].quantity + "$"
        plotter = test_dataset.plot(self.plotter)
        self.assertEqual(xlabel, plotter.axes.get_xlabel())
        self.assertEqual(ylabel, plotter.axes.get_ylabel())

    def test_plot_with_dataset_with_label_properties_sets_axes_labels(self):
        test_dataset = dataset.Dataset()
        test_dataset.data.axes[0].quantity = "foo"
        test_dataset.data.axes[0].unit = "bar"
        test_dataset.data.axes[1].quantity = "foo"
        test_dataset.data.axes[1].unit = "bar"
        self.plotter.properties.axes.xlabel = None
        self.plotter.properties.axes.ylabel = None
        plotter = test_dataset.plot(self.plotter)
        self.assertEqual("", plotter.axes.get_xlabel())
        self.assertEqual("", plotter.axes.get_ylabel())

    def test_plot_returns_dataset(self):
        test_dataset = self.plotter.plot(dataset=dataset.Dataset())
        self.assertTrue(isinstance(test_dataset, dataset.Dataset))

    def test_plot_checks_applicability(self):
        class MyPlotter(aspecd.plotting.SinglePlotter):
            @staticmethod
            def applicable(data):
                return False

        dataset = aspecd.dataset.Dataset()
        plotter = MyPlotter()
        with self.assertRaises(aspecd.exceptions.NotApplicableToDatasetError):
            dataset.plot(plotter)

    def test_plot_check_applicability_prints_helpful_message(self):
        class MyPlotter(aspecd.plotting.SinglePlotter):
            @staticmethod
            def applicable(data):
                return False

        dataset = aspecd.dataset.Dataset()
        dataset.id = "foo"
        plotter = MyPlotter()
        message = "MyPlotter not applicable to dataset with id foo"
        with self.assertRaisesRegex(
            aspecd.exceptions.NotApplicableToDatasetError, message
        ):
            dataset.plot(plotter)

    def test_plot_from_dataset_sets_data(self):
        test_dataset = dataset.Dataset()
        test_dataset.data.data = np.random.random(5)
        plotter = test_dataset.plot(self.plotter)
        self.assertListEqual(
            list(plotter.data.data), list(test_dataset.data.data)
        )

    def test_plot_from_dataset_with_device_data_sets_data(self):
        test_dataset = dataset.Dataset()
        device_data = dataset.DeviceData()
        device_data.data = np.random.random(5)
        test_dataset.device_data["test"] = device_data
        self.plotter.parameters["device_data"] = "test"
        plotter = test_dataset.plot(self.plotter)
        self.assertListEqual(list(plotter.data.data), list(device_data.data))

    def test_plot_from_dataset_with_non_existent_device_data_raises(self):
        test_dataset = dataset.Dataset()
        device_data = dataset.DeviceData()
        device_data.data = np.random.random(5)
        test_dataset.device_data["test"] = device_data
        self.plotter.parameters["device_data"] = "nonexistent"
        with self.assertRaises(KeyError) as context:
            test_dataset.plot(self.plotter)
        the_exception = context.exception
        self.assertIn("not found in dataset", str(the_exception))


class TestSinglePlotter1D(unittest.TestCase):
    def setUp(self):
        self.plotter = plotting.SinglePlotter1D()
        self.dataset = aspecd.dataset.ExperimentalDataset()
        self.dataset.data.data = np.random.random(5)
        self.dataset.data.axes[0].quantity = "magnetic field"
        self.dataset.data.axes[0].unit = "mT"
        self.dataset.data.axes[1].quantity = "intensity"
        self.dataset.data.axes[1].unit = "V"

    def tearDown(self):
        if self.plotter.fig:
            plt.close(self.plotter.fig)

    def test_instantiate_class(self):
        pass

    def test_has_type_property(self):
        self.assertTrue(hasattr(self.plotter, "type"))

    def test_set_type(self):
        plot_type = "scatter"
        self.plotter.type = plot_type
        self.assertEqual(self.plotter.type, plot_type)

    def test_setting_wrong_type_raises(self):
        with self.assertRaises(TypeError):
            self.plotter.type = "foo"

    def test_plot_sets_drawing(self):
        self.plotter.plot(dataset=dataset.Dataset())
        self.assertTrue(self.plotter.drawing)

    def test_plot_with_2D_data_raises(self):
        dataset_ = dataset.Dataset()
        dataset_.data.data = np.random.rand(3, 2)
        with self.assertRaises(aspecd.exceptions.NotApplicableToDatasetError):
            self.plotter.plot(dataset_)

    def test_set_line_colour_from_dict(self):
        line_colour = "#cccccc"
        properties = {"drawing": {"color": line_colour}}
        self.plotter.properties.from_dict(properties)
        self.assertEqual(line_colour, self.plotter.properties.drawing.color)

    def test_plot_sets_correct_line_color(self):
        color = "#cccccc"
        dict_ = {"drawing": {"color": color}}
        self.plotter.properties.from_dict(dict_)
        self.plotter.plot(dataset=dataset.Dataset())
        self.assertEqual(color, self.plotter.drawing.get_color())

    def test_plot_sets_axes_xlabel(self):
        label = "foo bar"
        dict_ = {"axes": {"xlabel": label}}
        self.plotter.properties.from_dict(dict_)
        self.plotter.plot(dataset=dataset.Dataset())
        self.assertEqual(label, self.plotter.axes.get_xlabel())

    def test_plot_adds_no_x_zero_line_if_out_of_range(self):
        self.plotter.parameters["show_zero_lines"] = True
        dataset_ = aspecd.dataset.CalculatedDataset()
        dataset_.data.data = np.random.random([10]) + 5
        plotter = dataset_.plot(self.plotter)
        self.assertEqual([0.0, 0.0], plotter.ax.get_lines()[1].get_xdata())

    def test_plot_adds_no_y_zero_line_if_out_of_range(self):
        self.plotter.parameters["show_zero_lines"] = True
        dataset_ = aspecd.dataset.CalculatedDataset()
        dataset_.data.data = np.random.random([10]) - 0.5
        dataset_.data.axes[0].values = np.linspace(4, 5, 10)
        plotter = dataset_.plot(self.plotter)
        self.assertEqual([0.0, 0.0], plotter.ax.get_lines()[1].get_ydata())

    def test_plot_with_show_legend_sets_legend_label(self):
        dataset_ = aspecd.dataset.CalculatedDataset()
        dataset_.data.data = np.random.random([10]) - 0.5
        dataset_.data.axes[0].values = np.linspace(4, 5, 10)
        dataset_.label = "foo"
        self.plotter.parameters["show_legend"] = True
        plotter = dataset_.plot(self.plotter)
        self.assertEqual(
            dataset_.label, plotter.legend.get_texts()[0].get_text()
        )

    def test_axes_tight_x_sets_xlim_to_data_limits(self):
        dataset_ = aspecd.dataset.CalculatedDataset()
        dataset_.data.data = np.random.random([100])
        dataset_.data.axes[0].values = np.linspace(np.pi, 2 * np.pi, 100)
        self.plotter.parameters["tight"] = "x"
        plotter = dataset_.plot(self.plotter)
        self.assertEqual(
            dataset_.data.axes[0].values[0], plotter.axes.get_xlim()[0]
        )

    def test_axes_tight_y_sets_ylim_to_data_limits(self):
        dataset_ = aspecd.dataset.CalculatedDataset()
        dataset_.data.data = np.random.random([100])
        dataset_.data.axes[0].values = np.linspace(np.pi, 2 * np.pi, 100)
        self.plotter.parameters["tight"] = "y"
        plotter = dataset_.plot(self.plotter)
        self.assertEqual(dataset_.data.data.min(), plotter.axes.get_ylim()[0])

    def test_axes_tight_both_sets_xlim_and_ylim_to_data_limits(self):
        dataset_ = aspecd.dataset.CalculatedDataset()
        dataset_.data.data = np.random.random([100])
        dataset_.data.axes[0].values = np.linspace(np.pi, 2 * np.pi, 100)
        self.plotter.parameters["tight"] = "both"
        plotter = dataset_.plot(self.plotter)
        self.assertEqual(
            dataset_.data.axes[0].values[0], plotter.axes.get_xlim()[0]
        )
        self.assertEqual(dataset_.data.data.min(), plotter.axes.get_ylim()[0])

    def test_has_switch_axes_parameter(self):
        self.assertTrue("switch_axes" in self.plotter.parameters)

    def test_switch_axes_sets_correct_axes_labels(self):
        self.plotter.parameters["switch_axes"] = True
        self.plotter.dataset = self.dataset
        self.plotter.plot()
        self.assertIn("intensity", self.plotter.ax.get_xlabel())
        self.assertIn("magnetic", self.plotter.ax.get_ylabel())

    def test_switch_axes_actually_switches_axes(self):
        self.plotter.parameters["switch_axes"] = True
        self.plotter.dataset = self.dataset
        self.plotter.plot()
        self.assertListEqual(
            list(self.dataset.data.data),
            list(self.plotter.axes.lines[0].get_xdata()),
        )

    def test_plot_device_data_plots_device_data(self):
        device_data = dataset.DeviceData()
        device_data.data = np.random.random(5)
        self.dataset.device_data["test"] = device_data
        self.plotter.parameters["device_data"] = "test"
        self.plotter.dataset = self.dataset
        self.plotter.plot()
        self.assertListEqual(
            list(device_data.data),
            list(self.plotter.axes.lines[0].get_ydata()),
        )

    def test_plot_device_data_checks_applicability(self):
        device_data = dataset.DeviceData()
        device_data.data = np.random.random([5, 5])
        self.dataset.device_data["test"] = device_data
        self.plotter.parameters["device_data"] = "test"
        self.plotter.dataset = self.dataset
        with self.assertRaises(aspecd.exceptions.NotApplicableToDatasetError):
            self.plotter.plot()

    def test_semilogy_plot_with_negative_values_logs_warning(self):
        self.plotter.type = "semilogy"
        self.dataset.data.data = self.dataset.data.data - np.mean(
            self.dataset.data.data
        )
        self.plotter.dataset = self.dataset
        with self.assertLogs(__package__, level="WARNING") as cm:
            self.plotter.plot()
        self.assertIn("", cm.output[0])

    def test_semilogx_plot_with_negative_axis_values_logs_warning(self):
        self.plotter.type = "semilogx"
        self.dataset.data.axes[0].values = np.linspace(
            -2, 2, len(self.dataset.data.data)
        )
        self.plotter.dataset = self.dataset
        with self.assertLogs(__package__, level="WARNING") as cm:
            self.plotter.plot()
        self.assertIn("Negative values", cm.output[0])

    def test_loglog_plot_with_negative_values_logs_warning(self):
        self.plotter.type = "loglog"
        self.dataset.data.data = self.dataset.data.data - np.mean(
            self.dataset.data.data
        )
        self.plotter.dataset = self.dataset
        with self.assertLogs(__package__, level="WARNING") as cm:
            self.plotter.plot()
        self.assertIn("Negative values", cm.output[0])

    def test_loglog_plot_with_negative_axis_values_logs_warning(self):
        self.plotter.type = "loglog"
        self.dataset.data.axes[0].values = np.linspace(
            -2, 2, len(self.dataset.data.data)
        )
        self.plotter.dataset = self.dataset
        with self.assertLogs(__package__, level="WARNING") as cm:
            self.plotter.plot()
        self.assertIn("Negative values", cm.output[0])

    def test_semilogy_plot_w_neg_axis_values_and_switch_axis_logs_warning(
        self,
    ):
        self.plotter.type = "semilogy"
        self.plotter.parameters["switch_axes"] = True
        self.dataset.data.axes[0].values = np.linspace(
            -2, 2, len(self.dataset.data.data)
        )
        self.plotter.dataset = self.dataset
        with self.assertLogs(__package__, level="WARNING") as cm:
            self.plotter.plot()
        self.assertIn("", cm.output[0])

    def test_semilogx_plot_w_neg_values_and_switch_axis_logs_warning(self):
        self.plotter.type = "semilogx"
        self.plotter.parameters["switch_axes"] = True
        self.dataset.data.data = self.dataset.data.data - np.mean(
            self.dataset.data.data
        )
        self.plotter.dataset = self.dataset
        with self.assertLogs(__package__, level="WARNING") as cm:
            self.plotter.plot()
        self.assertIn("Negative values", cm.output[0])


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
        with self.assertRaises(aspecd.exceptions.NotApplicableToDatasetError):
            dataset_.plot(self.plotter)

    def test_has_type_property(self):
        self.assertTrue(hasattr(self.plotter, "type"))

    def test_set_type(self):
        plot_type = "contour"
        self.plotter.type = plot_type
        self.assertEqual(self.plotter.type, plot_type)

    def test_setting_wrong_type_raises(self):
        with self.assertRaises(TypeError):
            self.plotter.type = "foo"

    def test_plot_sets_drawing(self):
        dataset_ = dataset.Dataset()
        dataset_.data.data = np.random.rand(3, 2)
        self.plotter.plot(dataset=dataset_)
        self.assertTrue(self.plotter.drawing)

    def test_plot_with_dataset_sets_axes_labels(self):
        test_dataset = dataset.Dataset()
        test_dataset.data.data = np.random.random([5, 5])
        test_dataset.data.axes[0].quantity = "zero"
        test_dataset.data.axes[0].unit = "foo"
        test_dataset.data.axes[1].quantity = "one"
        test_dataset.data.axes[1].unit = "bar"
        xlabel = (
            "$"
            + test_dataset.data.axes[0].quantity
            + "$"
            + " / "
            + test_dataset.data.axes[0].unit
        )
        ylabel = (
            "$"
            + test_dataset.data.axes[1].quantity
            + "$"
            + " / "
            + test_dataset.data.axes[1].unit
        )
        plotter = test_dataset.plot(self.plotter)
        self.assertEqual(xlabel, plotter.axes.get_xlabel())
        self.assertEqual(ylabel, plotter.axes.get_ylabel())

    def test_plot_with_dataset_sets_axes_limits(self):
        test_dataset = dataset.Dataset()
        test_dataset.data.data = np.random.random([5, 5])
        test_dataset.data.axes[0].quantity = "zero"
        test_dataset.data.axes[0].unit = "foo"
        test_dataset.data.axes[0].values = np.linspace(5, 10, 5)
        test_dataset.data.axes[1].quantity = "one"
        test_dataset.data.axes[1].unit = "bar"
        test_dataset.data.axes[1].values = np.linspace(50, 100, 5)
        xlimits = tuple(test_dataset.data.axes[0].values[[0, -1]])
        ylimits = tuple(test_dataset.data.axes[1].values[[0, -1]])
        plotter = test_dataset.plot(self.plotter)
        self.assertEqual(xlimits, plotter.axes.get_xlim())
        self.assertEqual(ylimits, plotter.axes.get_ylim())

    def test_plot_contour(self):
        self.plotter.type = "contour"
        test_dataset = dataset.Dataset()
        test_dataset.data.data = np.random.random([5, 5])
        test_dataset.plot(self.plotter)

    def test_plot_with_switched_axes(self):
        test_dataset = dataset.Dataset()
        test_dataset.data.data = np.random.random([5, 5])
        test_dataset.data.axes[0].quantity = "zero"
        test_dataset.data.axes[0].unit = "foo"
        test_dataset.data.axes[0].values = np.linspace(5, 10, 5)
        test_dataset.data.axes[1].quantity = "one"
        test_dataset.data.axes[1].unit = "bar"
        test_dataset.data.axes[1].values = np.linspace(50, 100, 5)
        xlimits = tuple(test_dataset.data.axes[1].values[[0, -1]])
        ylimits = tuple(test_dataset.data.axes[0].values[[0, -1]])
        self.plotter.parameters["switch_axes"] = True
        plotter = test_dataset.plot(self.plotter)
        self.assertEqual(xlimits, plotter.axes.get_xlim())
        self.assertEqual(ylimits, plotter.axes.get_ylim())

    def test_plot_contour_with_levels(self):
        self.plotter.type = "contour"
        self.plotter.parameters["levels"] = 40
        test_dataset = dataset.Dataset()
        test_dataset.data.data = np.random.random([5, 5])
        plotter = test_dataset.plot(self.plotter)
        self.assertGreaterEqual(
            len(plotter.drawing.levels), self.plotter.parameters["levels"] - 5
        )

    def test_set_cmap_from_dict(self):
        cmap = "RdGy"
        properties = {"drawing": {"cmap": cmap}}
        self.plotter.properties.from_dict(properties)
        self.assertEqual(cmap, self.plotter.properties.drawing.cmap)

    def test_plot_sets_correct_cmap(self):
        cmap = "RdGy"
        dict_ = {"drawing": {"cmap": cmap}}
        self.plotter.properties.from_dict(dict_)
        test_dataset = dataset.Dataset()
        test_dataset.data.data = np.random.random([5, 5])
        self.plotter.plot(dataset=test_dataset)
        self.assertEqual(cmap, self.plotter.drawing.cmap.name)

    def test_plot_imshow_with_levels_ignores_levels(self):
        self.plotter.parameters["levels"] = 40
        test_dataset = dataset.Dataset()
        test_dataset.data.data = np.random.random([5, 5])
        test_dataset.plot(self.plotter)

    def test_plot_imshow_sets_aspect_to_auto(self):
        test_dataset = dataset.Dataset()
        test_dataset.data.data = np.random.random([5, 5])
        test_dataset.plot(self.plotter)
        self.assertEqual("auto", self.plotter.ax._aspect)

    def test_show_contour_lines_plots_contour_lines_in_contourf(self):
        self.plotter.type = "contourf"
        self.plotter.parameters["show_contour_lines"] = True
        test_dataset = dataset.Dataset()
        test_dataset.data.data = np.random.random([5, 5])
        plotter = test_dataset.plot(self.plotter)
        line_collection = [
            isinstance(
                x,
                (
                    matplotlib.collections.LineCollection,
                    matplotlib.collections.PathCollection,
                    matplotlib.contour.QuadContourSet,
                ),
            )
            for x in plotter.ax.get_children()
        ]
        self.assertTrue(any(line_collection))

    def test_contour_plot_sets_correct_linewidths(self):
        self.plotter.type = "contour"
        dict_ = {"drawing": {"linewidths": 2}}
        self.plotter.properties.from_dict(dict_)
        test_dataset = dataset.Dataset()
        test_dataset.data.data = np.random.random([5, 5])
        plotter = test_dataset.plot(self.plotter)
        line_collection = [
            x
            for x in plotter.ax.get_children()
            if isinstance(
                x,
                (
                    matplotlib.collections.LineCollection,
                    matplotlib.collections.PathCollection,
                    matplotlib.contour.QuadContourSet,
                ),
            )
        ]
        self.assertEqual(
            dict_["drawing"]["linewidths"],
            line_collection[0].get_linewidths()[0],
        )

    def test_contour_plot_sets_correct_linestyles(self):
        self.plotter.type = "contour"
        dict_ = {"drawing": {"linestyles": ":", "linewidths": 1}}
        self.plotter.properties.from_dict(dict_)
        test_dataset = dataset.Dataset()
        test_dataset.data.data = np.random.random([5, 5])
        plotter = test_dataset.plot(self.plotter)
        line_collection = [
            x
            for x in plotter.ax.get_children()
            if isinstance(
                x,
                (
                    matplotlib.collections.LineCollection,
                    matplotlib.collections.PathCollection,
                    matplotlib.contour.QuadContourSet,
                ),
            )
        ]
        # linestyle ':' => (0.0, [1.0, 1.65]) for linewidth = 1
        self.assertEqual(
            (0.0, [1.0, 1.65]), line_collection[0].get_linestyles()[0]
        )

    def test_contour_plot_sets_correct_colors(self):
        self.plotter.type = "contour"
        dict_ = {"drawing": {"colors": "k"}}
        self.plotter.properties.from_dict(dict_)
        test_dataset = dataset.Dataset()
        test_dataset.data.data = np.random.random([5, 5])
        plotter = test_dataset.plot(self.plotter)
        contour_lines = [
            x
            for x in plotter.ax.get_children()
            if isinstance(
                x,
                (
                    matplotlib.collections.LineCollection,
                    matplotlib.collections.PathCollection,
                    matplotlib.contour.QuadContourSet,
                ),
            )
        ]
        if hasattr(contour_lines[0], "get_colors"):
            contour_color = list(contour_lines[0].get_colors()[0])
        else:
            contour_color = list(contour_lines[0].get_facecolor()[0])
        self.assertListEqual([0.0, 0.0, 0.0, 1.0], contour_color)

    def test_contourf_plot_with_contour_lines_sets_correct_linewidths(self):
        self.plotter.type = "contourf"
        self.plotter.parameters["show_contour_lines"] = True
        dict_ = {"drawing": {"linewidths": 2}}
        self.plotter.properties.from_dict(dict_)
        test_dataset = dataset.Dataset()
        test_dataset.data.data = np.random.random([5, 5])
        plotter = test_dataset.plot(self.plotter)
        line_collection = [
            x
            for x in plotter.ax.get_children()
            if isinstance(
                x,
                (
                    matplotlib.collections.LineCollection,
                    matplotlib.collections.PathCollection,
                    matplotlib.contour.QuadContourSet,
                ),
            )
        ]
        self.assertEqual(
            dict_["drawing"]["linewidths"],
            line_collection[0].get_linewidths()[0],
        )

    def test_contourf_plot_with_contour_lines_sets_correct_linestyles(self):
        self.plotter.type = "contourf"
        self.plotter.parameters["show_contour_lines"] = True
        dict_ = {"drawing": {"linestyles": ":", "linewidths": 1}}
        self.plotter.properties.from_dict(dict_)
        test_dataset = dataset.Dataset()
        test_dataset.data.data = np.random.random([5, 5])
        plotter = test_dataset.plot(self.plotter)
        line_collection = [
            x
            for x in plotter.ax.get_children()
            if isinstance(
                x,
                (
                    matplotlib.collections.LineCollection,
                    matplotlib.collections.PathCollection,
                    matplotlib.contour.QuadContourSet,
                ),
            )
        ]
        # linestyle ':' => (0.0, [1.0, 1.65]) for linewidth = 1
        self.assertEqual(
            (0.0, [1.0, 1.65]), line_collection[0].get_linestyles()[0]
        )

    def test_contourf_plot_with_contour_lines_sets_correct_colors(self):
        self.plotter.type = "contourf"
        self.plotter.parameters["show_contour_lines"] = True
        dict_ = {"drawing": {"colors": "k"}}
        self.plotter.properties.from_dict(dict_)
        test_dataset = dataset.Dataset()
        test_dataset.data.data = np.random.random([5, 5])
        plotter = test_dataset.plot(self.plotter)
        contour_lines = [
            x
            for x in plotter.ax.get_children()
            if isinstance(
                x,
                (
                    matplotlib.collections.LineCollection,
                    matplotlib.collections.PathCollection,
                    matplotlib.contour.QuadContourSet,
                ),
            )
        ]
        if hasattr(contour_lines[0], "get_colors"):
            contour_color = list(contour_lines[0].get_colors()[0])
        else:
            contour_color = list(contour_lines[0].get_facecolor()[0])
        self.assertListEqual([0.0, 0.0, 0.0, 1.0], contour_color)

    def test_plot_device_data_checks_applicability_of_device_data(self):
        device_data = dataset.DeviceData()
        device_data.data = np.random.random(5)
        test_dataset = aspecd.dataset.CalculatedDataset()
        test_dataset.device_data["test"] = device_data
        self.plotter.parameters["device_data"] = "test"
        with self.assertRaises(aspecd.exceptions.NotApplicableToDatasetError):
            plotter = test_dataset.plot(self.plotter)

    def test_colorbar_sets_colorbar(self):
        self.plotter.parameters["show_colorbar"] = True
        test_dataset = dataset.Dataset()
        test_dataset.data.data = np.random.random([5, 5])
        plotter = test_dataset.plot(self.plotter)
        self.assertIsInstance(plotter.colorbar, matplotlib.colorbar.Colorbar)

    def test_colorbar_properties_affect_colorbar(self):
        self.plotter.parameters["show_colorbar"] = True
        self.plotter.properties.colorbar.location = "top"
        test_dataset = dataset.Dataset()
        test_dataset.data.data = np.random.random([5, 5])
        plotter = test_dataset.plot(self.plotter)
        # Note: the location is not set in the colorbar, only the orientation
        self.assertEqual("horizontal", plotter.colorbar.orientation)

    def test_colorbar_with_label_sets_label(self):
        self.plotter.parameters["show_colorbar"] = True
        self.plotter.properties.colorbar.label = {"text": "foo"}
        test_dataset = dataset.Dataset()
        test_dataset.data.data = np.random.random([5, 5])
        plotter = test_dataset.plot(self.plotter)
        self.assertEqual(
            self.plotter.properties.colorbar.label["text"],
            plotter.colorbar.ax.yaxis.label.get_text(),
        )

    def test_colorbar_with_label_location_sets_label_location(self):
        self.plotter.parameters["show_colorbar"] = True
        self.plotter.properties.colorbar.label = {
            "text": "foo",
            "location": "bottom",
        }
        test_dataset = dataset.Dataset()
        test_dataset.data.data = np.random.random([5, 5])
        plotter = test_dataset.plot(self.plotter)
        self.assertEqual(0, plotter.colorbar.ax.yaxis.label.get_position()[0])


class TestSinglePlotter2DStacked(unittest.TestCase):
    def setUp(self):
        self.plotter = plotting.SinglePlotter2DStacked()
        self.filename = "foo.pdf"

    def tearDown(self):
        if self.plotter.fig:
            plt.close(self.plotter.fig)
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def test_instantiate_class(self):
        pass

    def test_class_has_sensible_description(self):
        self.assertIn("stack", self.plotter.description)

    def test_plot_with_1D_dataset_raises(self):
        dataset_ = aspecd.dataset.CalculatedDataset()
        dataset_.data.data = np.random.random([5])
        with self.assertRaises(aspecd.exceptions.NotApplicableToDatasetError):
            dataset_.plot(self.plotter)

    def test_parameters_have_stacking_dimension_key(self):
        self.assertIn("stacking_dimension", self.plotter.parameters)

    def test_plot_consists_of_correct_number_of_lines(self):
        dataset_ = aspecd.dataset.CalculatedDataset()
        dataset_.data.data = np.random.random([5, 10]) - 0.5
        plotter = dataset_.plot(self.plotter)
        self.assertGreaterEqual(10, len(plotter.axes.get_lines()))

    def test_plot_along_zero_dim_consists_of_correct_number_of_lines(self):
        self.plotter.parameters["stacking_dimension"] = 0
        dataset_ = aspecd.dataset.CalculatedDataset()
        dataset_.data.data = np.random.random([5, 10]) - 0.5
        plotter = dataset_.plot(self.plotter)
        self.assertGreaterEqual(5, len(plotter.axes.get_lines()))

    def test_plot_stacks_plots(self):
        dataset_ = aspecd.dataset.CalculatedDataset()
        dataset_.data.data = np.random.random([5, 10]) - 0.5
        plotter = dataset_.plot(self.plotter)
        self.assertGreater(
            max(plotter.axes.get_lines()[5].get_ydata()),
            max(plotter.axes.get_lines()[0].get_ydata()) * 3,
        )

    def test_plot_with_zero_offset_preserves_offset(self):
        self.plotter.parameters["offset"] = 0
        dataset_ = aspecd.dataset.CalculatedDataset()
        dataset_.data.data = np.random.random([5, 10]) - 0.5
        plotter = dataset_.plot(self.plotter)
        self.assertEqual(0, plotter.parameters["offset"])

    def test_plot_along_zero_dim_stacks_plots(self):
        self.plotter.parameters["stacking_dimension"] = 0
        dataset_ = aspecd.dataset.CalculatedDataset()
        dataset_.data.data = np.random.random([5, 10]) - 0.5
        plotter = dataset_.plot(self.plotter)
        self.assertGreater(
            max(plotter.axes.get_lines()[4].get_ydata()),
            max(plotter.axes.get_lines()[0].get_ydata()) * 3,
        )

    def test_plot_along_zero_dim_sets_correct_axes_labels(self):
        self.plotter.parameters["stacking_dimension"] = 0
        test_dataset = aspecd.dataset.CalculatedDataset()
        test_dataset.data.data = np.random.random([5, 10]) - 0.5
        test_dataset.data.axes[0].quantity = "zero"
        test_dataset.data.axes[0].unit = "foo"
        test_dataset.data.axes[1].quantity = "one"
        test_dataset.data.axes[1].unit = "bar"
        plotter = test_dataset.plot(self.plotter)
        self.assertIn(
            test_dataset.data.axes[1].unit, plotter.axes.get_xlabel()
        )

    def test_plot_sets_correct_axes_limits(self):
        test_dataset = aspecd.dataset.CalculatedDataset()
        test_dataset.data.data = np.random.random([5, 10]) - 0.5
        test_dataset.data.axes[0].quantity = "zero"
        test_dataset.data.axes[0].unit = "foo"
        test_dataset.data.axes[0].values = np.linspace(5, 10, 5)
        test_dataset.data.axes[1].quantity = "one"
        test_dataset.data.axes[1].unit = "bar"
        test_dataset.data.axes[1].values = np.linspace(50, 100, 10)
        plotter = test_dataset.plot(self.plotter)
        xlimits = tuple(test_dataset.data.axes[0].values[[0, -1]])
        self.assertLessEqual(plotter.axes.get_xlim()[0], xlimits[0])
        self.assertGreaterEqual(plotter.axes.get_xlim()[1], xlimits[1])

    def test_plot_along_zero_dim_sets_correct_axes_limits(self):
        self.plotter.parameters["stacking_dimension"] = 0
        test_dataset = aspecd.dataset.CalculatedDataset()
        test_dataset.data.data = np.random.random([5, 10]) - 0.5
        test_dataset.data.axes[0].quantity = "zero"
        test_dataset.data.axes[0].unit = "foo"
        test_dataset.data.axes[0].values = np.linspace(5, 10, 5)
        test_dataset.data.axes[1].quantity = "one"
        test_dataset.data.axes[1].unit = "bar"
        test_dataset.data.axes[1].values = np.linspace(50, 100, 10)
        plotter = test_dataset.plot(self.plotter)
        xlimits = tuple(test_dataset.data.axes[1].values[[0, -1]])
        self.assertLessEqual(plotter.axes.get_xlim()[0], xlimits[0])
        self.assertGreaterEqual(plotter.axes.get_xlim()[1], xlimits[1])

    def test_plot_with_offset_stacks_plots_accordingly(self):
        self.plotter.parameters["offset"] = 2
        dataset_ = aspecd.dataset.CalculatedDataset()
        dataset_.data.data = np.random.random([5, 10]) - 0.5
        plotter = dataset_.plot(self.plotter)
        self.assertGreater(
            max(plotter.axes.get_lines()[5].get_ydata()),
            max(plotter.axes.get_lines()[0].get_ydata()) * 10,
        )

    def test_plot_calculates_offset_accordingly(self):
        dataset_ = aspecd.dataset.CalculatedDataset()
        dataset_.data.data = np.random.random([5, 10]) - 10
        plotter = dataset_.plot(self.plotter)
        self.assertAlmostEqual(
            10 * 1.05, self.plotter.parameters["offset"], 1
        )

    def test_plot_sets_drawings(self):
        dataset_ = aspecd.dataset.CalculatedDataset()
        dataset_.data.data = np.random.random([5, 10]) - 0.5
        dataset_.plot(self.plotter)
        self.assertEqual(10, len(self.plotter.drawing))

    def test_plot_applies_drawing_properties_to_all_drawings(self):
        self.plotter.properties.drawing.color = "#aaccee"
        dataset_ = aspecd.dataset.CalculatedDataset()
        dataset_.data.data = np.random.random([5, 10]) - 0.5
        plotter = dataset_.plot(self.plotter)
        self.assertEqual(
            self.plotter.properties.drawing.color,
            plotter.axes.get_lines()[0]._color,
        )
        self.assertEqual(
            self.plotter.properties.drawing.color,
            plotter.axes.get_lines()[4]._color,
        )

    def test_set_color_from_dict(self):
        color = "#aaccee"
        properties = {"drawing": {"color": color}}
        self.plotter.properties.from_dict(properties)
        self.assertEqual(color, self.plotter.properties.drawing.color)

    def test_save_plot_with_set_color_does_not_raise(self):
        self.plotter.properties.drawing.color = "#aaccee"
        dataset_ = aspecd.dataset.CalculatedDataset()
        dataset_.data.data = np.random.random([5, 10]) - 0.5
        plotter = dataset_.plot(self.plotter)
        saver_ = aspecd.plotting.Saver()
        saver_.filename = self.filename
        plotter.save(saver_)
        self.assertTrue(os.path.exists(self.filename))

    def test_plot_sets_correct_yticks(self):
        test_dataset = aspecd.dataset.CalculatedDataset()
        test_dataset.data.data = np.random.random([5, 10]) - 0.5
        test_dataset.data.axes[1].quantity = "one"
        test_dataset.data.axes[1].unit = "bar"
        test_dataset.data.axes[1].values = np.linspace(50, 100, 10)
        plotter = test_dataset.plot(self.plotter)
        self.assertEqual(10, len(plotter.axes.get_yticks()))

    def test_plot_along_zero_dim_sets_correct_yticks(self):
        self.plotter.parameters["stacking_dimension"] = 0
        test_dataset = aspecd.dataset.CalculatedDataset()
        test_dataset.data.data = np.random.random([5, 10]) - 0.5
        test_dataset.data.axes[0].quantity = "zero"
        test_dataset.data.axes[0].unit = "foo"
        test_dataset.data.axes[0].values = np.linspace(5, 10, 5)
        plotter = test_dataset.plot(self.plotter)
        self.assertEqual(5, len(plotter.axes.get_yticks()))

    def test_plot_sets_correct_yticklabels(self):
        test_dataset = aspecd.dataset.CalculatedDataset()
        test_dataset.data.data = np.random.random([5, 10]) - 0.5
        test_dataset.data.axes[1].quantity = "one"
        test_dataset.data.axes[1].unit = "bar"
        test_dataset.data.axes[1].values = np.linspace(50, 100, 10)
        plotter = test_dataset.plot(self.plotter)
        self.assertEqual(
            test_dataset.data.axes[1].values[0].astype(str),
            plotter.axes.get_yticklabels()[0].get_text(),
        )

    def test_plot_along_zero_dim_sets_correct_yticklabels(self):
        self.plotter.parameters["stacking_dimension"] = 0
        test_dataset = aspecd.dataset.CalculatedDataset()
        test_dataset.data.data = np.random.random([5, 10]) - 0.5
        test_dataset.data.axes[0].quantity = "zero"
        test_dataset.data.axes[0].unit = "foo"
        test_dataset.data.axes[0].values = np.linspace(5, 10, 5)
        plotter = test_dataset.plot(self.plotter)
        self.assertEqual(
            test_dataset.data.axes[0].values[0].astype(str),
            plotter.axes.get_yticklabels()[0].get_text(),
        )

    def test_plot_with_ytick_format_sets_correct_yticklabels(self):
        test_dataset = aspecd.dataset.CalculatedDataset()
        test_dataset.data.data = np.random.random([5, 10]) - 0.5
        test_dataset.data.axes[1].quantity = "one"
        test_dataset.data.axes[1].unit = "bar"
        test_dataset.data.axes[1].values = np.linspace(50, 100, 10)
        self.plotter.parameters["yticklabelformat"] = "%.2f"
        plotter = test_dataset.plot(self.plotter)
        self.assertEqual(
            "%.2f" % test_dataset.data.axes[1].values[2],
            plotter.axes.get_yticklabels()[2].get_text(),
        )

    def test_plot_zero_lines_for_each_trace(self):
        dataset_ = aspecd.dataset.CalculatedDataset()
        dataset_.data.data = np.random.random([5, 10]) - 0.5
        self.plotter.parameters["show_zero_lines"] = True
        plotter = dataset_.plot(self.plotter)
        self.assertGreaterEqual(20, len(plotter.axes.get_lines()))

    def test_plot_with_offset_zero_sets_correct_ylabel(self):
        test_dataset = aspecd.dataset.CalculatedDataset()
        test_dataset.data.data = np.random.random([5, 10]) - 0.5
        test_dataset.data.axes[2].quantity = "intensity"
        test_dataset.data.axes[2].unit = "a.u."
        self.plotter.parameters["offset"] = 0
        plotter = test_dataset.plot(self.plotter)
        self.assertEqual("$intensity$ / a.u.", plotter.axes.get_ylabel())

    def test_axes_tight_x_sets_xlim_to_data_limits(self):
        dataset_ = aspecd.dataset.CalculatedDataset()
        dataset_.data.data = np.random.random([100, 5])
        dataset_.data.axes[0].values = np.linspace(np.pi, 2 * np.pi, 100)
        self.plotter.parameters["tight"] = "x"
        plotter = dataset_.plot(self.plotter)
        self.assertEqual(
            dataset_.data.axes[0].values[0], plotter.axes.get_xlim()[0]
        )

    def test_axes_tight_y_and_offset_zero_sets_ylim_to_data_limits(self):
        dataset_ = aspecd.dataset.CalculatedDataset()
        dataset_.data.data = np.random.random([100, 5])
        self.plotter.parameters["offset"] = 0
        self.plotter.parameters["tight"] = "y"
        plotter = dataset_.plot(self.plotter)
        self.assertEqual(dataset_.data.data.min(), plotter.axes.get_ylim()[0])

    def test_axes_tight_both_and_offset_zero_sets_limits(self):
        dataset_ = aspecd.dataset.CalculatedDataset()
        dataset_.data.data = np.random.random([100, 5])
        dataset_.data.axes[0].values = np.linspace(np.pi, 2 * np.pi, 100)
        self.plotter.parameters["offset"] = 0
        self.plotter.parameters["tight"] = "both"
        plotter = dataset_.plot(self.plotter)
        self.assertEqual(
            dataset_.data.axes[0].values[0], plotter.axes.get_xlim()[0]
        )
        self.assertEqual(dataset_.data.data.min(), plotter.axes.get_ylim()[0])

    def test_set_maximum_of_yticks(self):
        self.plotter.parameters["stacking_dimension"] = 0
        test_dataset = aspecd.dataset.CalculatedDataset()
        test_dataset.data.data = np.random.random([50, 10]) - 0.5
        test_dataset.data.axes[0].quantity = "zero"
        test_dataset.data.axes[0].unit = "foo"
        test_dataset.data.axes[0].values = np.linspace(5, 10, 50)
        self.plotter.parameters["ytickcount"] = 19
        plotter = test_dataset.plot(self.plotter)
        self.assertEqual(
            self.plotter.parameters["ytickcount"],
            len(plotter.axes.get_yticks()),
        )

    def test_set_maximum_of_yticks_does_not_exceed_lines(self):
        self.plotter.parameters["stacking_dimension"] = 0
        test_dataset = aspecd.dataset.CalculatedDataset()
        test_dataset.data.data = np.random.random([5, 10]) - 0.5
        test_dataset.data.axes[0].quantity = "zero"
        test_dataset.data.axes[0].unit = "foo"
        test_dataset.data.axes[0].values = np.linspace(5, 10, 5)
        self.plotter.parameters["ytickcount"] = 19
        plotter = test_dataset.plot(self.plotter)
        self.assertEqual(5, len(plotter.axes.get_yticks()))

    def test_plot_device_data_plots_device_data(self):
        device_data = dataset.DeviceData()
        device_data.data = np.random.random([5, 5])
        test_dataset = aspecd.dataset.CalculatedDataset()
        test_dataset.device_data["test"] = device_data
        self.plotter.parameters["device_data"] = "test"
        plotter = test_dataset.plot(self.plotter)
        self.assertListEqual(
            list(device_data.data[:, 0]),
            list(plotter.axes.lines[0].get_ydata()),
        )

    def test_plot_device_data_checks_applicability_of_device_data(self):
        device_data = dataset.DeviceData()
        device_data.data = np.random.random(5)
        test_dataset = aspecd.dataset.CalculatedDataset()
        test_dataset.device_data["test"] = device_data
        self.plotter.parameters["device_data"] = "test"
        with self.assertRaises(aspecd.exceptions.NotApplicableToDatasetError):
            test_dataset.plot(self.plotter)


class TestMultiDeviceDataPlotter1D(unittest.TestCase):
    def setUp(self):
        self.plotter = plotting.MultiDeviceDataPlotter1D()
        self.filename = "foo.pdf"
        self.dataset = None

    def tearDown(self):
        if self.plotter.fig:
            plt.close(self.plotter.fig)
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def create_dataset(self, devices=("device1", "device2")):
        self.dataset = aspecd.dataset.CalculatedDataset()
        xdata = np.linspace(0, 2 * np.pi, 501)
        for device in devices:
            device_data = dataset.DeviceData()
            device_data.data = np.sin(xdata + np.random.random())
            device_data.axes[0].quantity = "time"
            device_data.axes[0].unit = "ms"
            device_data.axes[1].quantity = "intensity"
            device_data.axes[1].unit = "a.u."
            self.dataset.device_data[device] = device_data
        self.plotter.parameters["device_data"] = list(devices)

    def test_instantiate_class(self):
        pass

    def test_class_has_sensible_description(self):
        self.assertIn("multiple device data", self.plotter.description)

    def test_plot_with_2D_device_data_raises(self):
        test_dataset = aspecd.dataset.CalculatedDataset()
        device_data = dataset.DeviceData()
        device_data.data = np.random.random([5, 5])
        test_dataset.device_data["test"] = device_data
        self.plotter.parameters["device_data"] = "test"
        with self.assertRaises(aspecd.exceptions.NotApplicableToDatasetError):
            test_dataset.plot(self.plotter)

    def test_plot_with_one_2D_device_data_raises(self):
        test_dataset = aspecd.dataset.CalculatedDataset()
        device_data1 = dataset.DeviceData()
        device_data1.data = np.random.random(5)
        test_dataset.device_data["test1"] = device_data1
        device_data2 = dataset.DeviceData()
        device_data2.data = np.random.random([5, 5])
        test_dataset.device_data["test2"] = device_data2
        self.plotter.parameters["device_data"] = ["test1", "test2"]
        with self.assertRaises(aspecd.exceptions.NotApplicableToDatasetError):
            test_dataset.plot(self.plotter)

    def test_plot_without_datasets_raises(self):
        with self.assertRaises(aspecd.exceptions.MissingDatasetError):
            self.plotter.plot()

    def test_plot_without_device_data_raises(self):
        test_dataset = aspecd.dataset.CalculatedDataset()
        with self.assertRaises(KeyError) as context:
            test_dataset.plot(self.plotter)
        the_exception = context.exception
        self.assertIn("No device data provided", str(the_exception))

    def test_plot_with_device_data_sets_data(self):
        self.create_dataset()
        self.dataset.plot(self.plotter)
        self.assertEqual(
            len(self.plotter.parameters["device_data"]),
            len(self.plotter.data),
        )

    def test_parameters_have_axes_key(self):
        self.assertIn("axes", self.plotter.parameters)

    def test_parameters_axes_is_list_of_axes_objects(self):
        self.assertTrue(isinstance(self.plotter.parameters["axes"], list))
        self.assertTrue(self.plotter.parameters["axes"])
        for axis in self.plotter.parameters["axes"]:
            self.assertTrue(isinstance(axis, dataset.Axis))

    def test_plot_with_axes_in_parameters_sets_axes_labels(self):
        self.plotter.parameters["axes"][0].quantity = "foo"
        self.plotter.parameters["axes"][0].unit = "bar"
        self.plotter.parameters["axes"][1].quantity = "foo2"
        self.plotter.parameters["axes"][1].unit = "bar2"
        xlabel = (
            "$"
            + self.plotter.parameters["axes"][0].quantity
            + "$"
            + " / "
            + self.plotter.parameters["axes"][0].unit
        )
        ylabel = (
            "$"
            + self.plotter.parameters["axes"][1].quantity
            + "$"
            + " / "
            + self.plotter.parameters["axes"][1].unit
        )
        self.create_dataset()
        plotter = self.dataset.plot(self.plotter)
        self.assertEqual(xlabel, plotter.axes.get_xlabel())
        self.assertEqual(ylabel, plotter.axes.get_ylabel())

    def test_plot_with_datasets_with_identical_axes_sets_axes_labels(self):
        self.create_dataset()
        device = self.plotter.parameters["device_data"][0]
        device_data = self.dataset.device_data[device]
        xlabel = (
            "$"
            + device_data.axes[0].quantity
            + "$"
            + " / "
            + device_data.axes[0].unit
        )
        ylabel = (
            "$"
            + device_data.axes[1].quantity
            + "$"
            + " / "
            + device_data.axes[1].unit
        )
        plotter = self.dataset.plot(self.plotter)
        self.assertEqual(xlabel, plotter.axes.get_xlabel())
        self.assertEqual(ylabel, plotter.axes.get_ylabel())

    def test_axes_properties_set_axes_labels(self):
        self.create_dataset()
        self.plotter.properties.axes.xlabel = "foo"
        self.plotter.properties.axes.ylabel = "bar"
        plotter = self.dataset.plot(self.plotter)
        self.assertEqual(
            plotter.properties.axes.xlabel, plotter.axes.get_xlabel()
        )
        self.assertEqual(
            plotter.properties.axes.ylabel, plotter.axes.get_ylabel()
        )

    def test_plot_consists_of_correct_number_of_lines(self):
        self.create_dataset()
        plotter = self.dataset.plot(self.plotter)
        self.assertGreaterEqual(
            len(plotter.axes.get_lines()),
            len(self.plotter.parameters["device_data"]),
        )

    def test_plot_sets_drawings(self):
        self.create_dataset()
        self.dataset.plot(self.plotter)
        self.assertEqual(
            len(self.plotter.parameters["device_data"]),
            len(self.plotter.drawing),
        )

    def test_plot_adds_drawing_properties(self):
        self.create_dataset()
        self.dataset.plot(self.plotter)
        self.assertEqual(
            len(self.plotter.data), len(self.plotter.properties.drawings)
        )

    def test_plot_sets_label_from_device_metadata(self):
        self.create_dataset()
        devices = list(self.dataset.device_data.keys())
        self.dataset.device_data[devices[0]].metadata.label = "device foo"
        self.dataset.device_data[devices[1]].metadata.label = "device bar"
        plotter = self.dataset.plot(self.plotter)
        for idx, device in enumerate(devices):
            self.assertEqual(
                self.dataset.device_data[device].metadata.label,
                plotter.drawing[idx].get_label(),
            )

    def test_plot_sets_label_from_device_key_if_no_metadata_label(self):
        self.create_dataset()
        devices = list(self.dataset.device_data.keys())
        plotter = self.dataset.plot(self.plotter)
        for idx, device in enumerate(devices):
            self.assertEqual(device, plotter.drawing[idx].get_label())

    def test_axes_tight_x_sets_xlim_to_data_limits(self):
        self.create_dataset()
        self.plotter.parameters["tight"] = "x"
        plotter = self.dataset.plot(self.plotter)
        self.assertAlmostEqual(
            plotter.data[0].axes[0].values[0], plotter.axes.get_xlim()[0], 4
        )

    def test_axes_tight_y_sets_ylim_to_data_limits(self):
        self.create_dataset()
        self.plotter.parameters["tight"] = "y"
        plotter = self.dataset.plot(self.plotter)
        self.assertAlmostEqual(
            plotter.data[0].data.min(), plotter.axes.get_ylim()[0], 4
        )

    def test_axes_tight_both_sets_xlim_and_ylim_to_data_limits(self):
        self.create_dataset()
        self.plotter.parameters["tight"] = "both"
        plotter = self.dataset.plot(self.plotter)
        self.assertAlmostEqual(
            plotter.data[0].axes[0].values[0], plotter.axes.get_xlim()[0], 4
        )
        self.assertAlmostEqual(
            plotter.data[0].data.min(), plotter.axes.get_ylim()[0], 4
        )

    def test_has_switch_axes_parameter(self):
        self.assertTrue("switch_axes" in self.plotter.parameters)

    def test_switch_axes_sets_correct_axes_labels(self):
        self.create_dataset()
        self.plotter.parameters["switch_axes"] = True
        plotter = self.dataset.plot(self.plotter)
        device_data = self.dataset.device_data[
            self.plotter.parameters["device_data"][0]
        ]
        self.assertIn(device_data.axes[1].quantity, plotter.ax.get_xlabel())
        self.assertIn(device_data.axes[0].quantity, plotter.ax.get_ylabel())

    def test_switch_axes_actually_switches_axes(self):
        self.create_dataset()
        self.plotter.parameters["switch_axes"] = True
        plotter = self.dataset.plot(self.plotter)
        device_data = self.dataset.device_data[
            self.plotter.parameters["device_data"][0]
        ]
        self.assertListEqual(
            list(device_data.data), list(plotter.axes.lines[0].get_xdata())
        )

    def test_plot_sets_correct_line_color(self):
        self.create_dataset()
        color1 = "#abcdef"
        color2 = "#012345"
        dict_ = {"drawings": [{"color": color1}, {"color": color2}]}
        self.plotter.properties.from_dict(dict_)
        plotter = self.dataset.plot(self.plotter)
        self.assertEqual(color1, plotter.drawing[0].get_color())


class TestMultiPlotter(unittest.TestCase):
    def setUp(self):
        self.plotter = plotting.MultiPlotter()

    def tearDown(self):
        if self.plotter.fig:
            plt.close(self.plotter.fig)

    def test_instantiate_class(self):
        pass

    def test_has_datasets_property(self):
        self.assertTrue(hasattr(self.plotter, "datasets"))

    def test_datasets_property_is_list(self):
        self.assertTrue(isinstance(self.plotter.datasets, list))

    def test_has_data_property(self):
        self.assertTrue(hasattr(self.plotter, "data"))

    def test_data_property_is_list(self):
        self.assertTrue(isinstance(self.plotter.data, list))

    def test_to_dict_does_not_contain_certain_keys(self):
        for key in ["datasets", "drawings", "data"]:
            with self.subTest(key=key):
                self.assertNotIn(key, self.plotter.to_dict())

    def test_plot_without_datasets_raises(self):
        with self.assertRaises(aspecd.exceptions.MissingDatasetError):
            self.plotter.plot()

    def test_plot_with_datasets(self):
        self.plotter.datasets.append(dataset.Dataset())
        self.plotter.plot()

    def test_parameters_have_axes_key(self):
        self.assertIn("axes", self.plotter.parameters)

    def test_parameters_axes_is_list_of_axes_objects(self):
        self.assertTrue(isinstance(self.plotter.parameters["axes"], list))
        self.assertTrue(self.plotter.parameters["axes"])
        for axis in self.plotter.parameters["axes"]:
            self.assertTrue(isinstance(axis, dataset.Axis))

    def test_plot_with_axes_in_parameters_sets_axes_labels(self):
        self.plotter.parameters["axes"][0].quantity = "foo"
        self.plotter.parameters["axes"][0].unit = "bar"
        self.plotter.parameters["axes"][1].quantity = "foo2"
        self.plotter.parameters["axes"][1].unit = "bar2"
        xlabel = (
            "$"
            + self.plotter.parameters["axes"][0].quantity
            + "$"
            + " / "
            + self.plotter.parameters["axes"][0].unit
        )
        ylabel = (
            "$"
            + self.plotter.parameters["axes"][1].quantity
            + "$"
            + " / "
            + self.plotter.parameters["axes"][1].unit
        )
        self.plotter.datasets.append(dataset.Dataset())
        self.plotter.plot()
        self.assertEqual(xlabel, self.plotter.axes.get_xlabel())
        self.assertEqual(ylabel, self.plotter.axes.get_ylabel())

    def test_plot_with_datasets_with_identical_axes_sets_axes_labels(self):
        test_dataset0 = dataset.Dataset()
        test_dataset0.data.axes[0].quantity = "foo"
        test_dataset0.data.axes[0].unit = "bar"
        test_dataset0.data.axes[1].quantity = "foo"
        test_dataset0.data.axes[1].unit = "bar"
        test_dataset1 = dataset.Dataset()
        test_dataset1.data.axes[0].quantity = "foo"
        test_dataset1.data.axes[0].unit = "bar"
        test_dataset1.data.axes[1].quantity = "foo"
        test_dataset1.data.axes[1].unit = "bar"
        xlabel = (
            "$"
            + test_dataset0.data.axes[0].quantity
            + "$"
            + " / "
            + test_dataset0.data.axes[0].unit
        )
        ylabel = (
            "$"
            + test_dataset0.data.axes[1].quantity
            + "$"
            + " / "
            + test_dataset0.data.axes[1].unit
        )
        self.plotter.datasets.append(test_dataset0)
        self.plotter.datasets.append(test_dataset1)
        self.plotter.plot()
        self.assertEqual(xlabel, self.plotter.axes.get_xlabel())
        self.assertEqual(ylabel, self.plotter.axes.get_ylabel())

    def test_plot_with_datasets_w_identical_quantity_sets_axes_labels(self):
        test_dataset0 = dataset.Dataset()
        test_dataset0.data.axes[0].quantity = "foo"
        test_dataset0.data.axes[0].unit = ""
        test_dataset0.data.axes[1].quantity = "foo"
        test_dataset0.data.axes[1].unit = ""
        test_dataset1 = dataset.Dataset()
        test_dataset1.data.axes[0].quantity = "foo"
        test_dataset1.data.axes[0].unit = ""
        test_dataset1.data.axes[1].quantity = "foo"
        test_dataset1.data.axes[1].unit = ""
        xlabel = "$" + test_dataset0.data.axes[0].quantity + "$"
        ylabel = "$" + test_dataset0.data.axes[1].quantity + "$"
        self.plotter.datasets.append(test_dataset0)
        self.plotter.datasets.append(test_dataset1)
        self.plotter.plot()
        self.assertEqual(xlabel, self.plotter.axes.get_xlabel())
        self.assertEqual(ylabel, self.plotter.axes.get_ylabel())

    def test_plot_with_datasets_adds_drawing_properties(self):
        self.plotter.datasets.append(dataset.Dataset())
        self.plotter.plot()
        self.assertEqual(
            len(self.plotter.datasets), len(self.plotter.properties.drawings)
        )

    def test_plot_with_show_legend_set_to_true_adds_legend(self):
        self.plotter.datasets.append(dataset.Dataset())
        self.plotter.parameters["show_legend"] = True
        with contextlib.redirect_stderr(io.StringIO()):
            self.plotter.plot()
        self.assertIs(type(self.plotter.legend), matplotlib.legend.Legend)

    def test_axes_properties_set_axes_labels(self):
        self.plotter.properties.axes.xlabel = "foo"
        self.plotter.properties.axes.ylabel = "bar"
        test_dataset = dataset.Dataset()
        test_dataset.data.axes[0].quantity = "foo"
        test_dataset.data.axes[0].unit = "bar"
        test_dataset.data.axes[1].quantity = "foo"
        test_dataset.data.axes[1].unit = "bar"
        self.plotter.datasets.append(test_dataset)
        self.plotter.plot()
        self.assertEqual(
            self.plotter.properties.axes.xlabel,
            self.plotter.axes.get_xlabel(),
        )
        self.assertEqual(
            self.plotter.properties.axes.ylabel,
            self.plotter.axes.get_ylabel(),
        )

    def test_plot_checks_applicability(self):
        class MyPlotter(aspecd.plotting.MultiPlotter):
            @staticmethod
            def applicable(dataset):
                return False

        dataset1 = aspecd.dataset.Dataset()
        dataset2 = aspecd.dataset.Dataset()
        plotter = MyPlotter()
        plotter.datasets.append(dataset1)
        plotter.datasets.append(dataset2)
        with self.assertRaises(aspecd.exceptions.NotApplicableToDatasetError):
            plotter.plot()

    def test_plot_checks_applicability_and_prints_helpful_message(self):
        class MyPlotter(aspecd.plotting.MultiPlotter):
            @staticmethod
            def applicable(dataset):
                return False

        dataset1 = aspecd.dataset.Dataset()
        dataset2 = aspecd.dataset.Dataset()
        plotter = MyPlotter()
        plotter.datasets.append(dataset1)
        plotter.datasets.append(dataset2)
        message = "MyPlotter not applicable to one or more datasets"
        with self.assertRaisesRegex(
            aspecd.exceptions.NotApplicableToDatasetError, message
        ):
            plotter.plot()

    def test_plot_sets_data(self):
        test_dataset = dataset.Dataset()
        test_dataset.data.data = np.random.random(5)
        self.plotter.datasets.append(test_dataset)
        self.plotter.plot()
        self.assertListEqual(
            list(self.plotter.data[0].data), list(test_dataset.data.data)
        )

    def test_plot_with_device_data_sets_data(self):
        device_data = dataset.DeviceData()
        device_data.data = np.random.random(5)
        test_dataset = dataset.Dataset()
        test_dataset.device_data["test"] = device_data
        self.plotter.datasets.append(test_dataset)
        self.plotter.parameters["device_data"] = "test"
        self.plotter.plot()
        self.assertListEqual(
            list(self.plotter.data[0].data), list(device_data.data)
        )


class TestMultiPlotter1D(unittest.TestCase):
    def setUp(self):
        self.plotter = plotting.MultiPlotter1D()
        self.dataset = aspecd.dataset.ExperimentalDataset()
        self.dataset.data.data = np.random.random(5)
        self.dataset.data.axes[0].quantity = "magnetic field"
        self.dataset.data.axes[0].unit = "mT"
        self.dataset.data.axes[1].quantity = "intensity"
        self.dataset.data.axes[1].unit = "V"

    def tearDown(self):
        if self.plotter.fig:
            plt.close(self.plotter.fig)

    def test_instantiate_class(self):
        pass

    def test_description_is_sensible(self):
        self.assertNotIn("Abstract", self.plotter.description)

    def test_properties_are_of_correct_type(self):
        self.assertIs(
            type(self.plotter.properties),
            aspecd.plotting.MultiPlot1DProperties,
        )

    def test_has_type_property(self):
        self.assertTrue(hasattr(self.plotter, "type"))

    def test_set_type(self):
        plot_type = "loglog"
        self.plotter.type = plot_type
        self.assertEqual(self.plotter.type, plot_type)

    def test_setting_wrong_type_raises(self):
        with self.assertRaises(TypeError):
            self.plotter.type = "foo"

    def test_plot_with_2D_data_raises(self):
        dataset_ = dataset.Dataset()
        dataset_.data.data = np.random.rand(3, 2)
        self.plotter.datasets.append(dataset_)
        with self.assertRaises(aspecd.exceptions.NotApplicableToDatasetError):
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
        self.assertIs(
            type(self.plotter.properties.drawings[0]),
            aspecd.plotting.LineProperties,
        )

    def test_plot_sets_correct_line_color(self):
        color = "#abcdef"
        dict_ = {"drawings": [{"color": color}]}
        self.plotter.properties.from_dict(dict_)
        self.plotter.datasets.append(dataset.Dataset())
        self.plotter.plot()
        self.assertEqual(color, self.plotter.drawings[0].get_color())

    def test_plot_with_show_legend_sets_legend_label(self):
        dataset_ = dataset.Dataset()
        dataset_.label = "foo"
        self.plotter.datasets.append(dataset_)
        self.plotter.parameters["show_legend"] = True
        self.plotter.plot()
        self.assertEqual(
            dataset_.label, self.plotter.legend.get_texts()[0].get_text()
        )

    def test_has_switch_axes_parameter(self):
        self.assertTrue("switch_axes" in self.plotter.parameters)

    def test_switch_axes_sets_correct_axes_labels(self):
        self.plotter.parameters["switch_axes"] = True
        self.plotter.datasets.append(self.dataset)
        self.plotter.plot()
        self.assertIn("intensity", self.plotter.ax.get_xlabel())
        self.assertIn("magnetic", self.plotter.ax.get_ylabel())

    def test_switch_axes_actually_switches_axes(self):
        self.plotter.parameters["switch_axes"] = True
        self.plotter.datasets.append(self.dataset)
        self.plotter.plot()
        self.assertListEqual(
            list(self.dataset.data.data),
            list(self.plotter.axes.lines[0].get_xdata()),
        )

    def test_has_tight_parameter(self):
        self.assertTrue("tight" in self.plotter.parameters)

    def test_tight_sets_correct_x_axes_limits(self):
        self.plotter.parameters["tight"] = "x"
        self.plotter.datasets.append(self.dataset)
        self.plotter.plot()
        self.assertListEqual([0, 4], list(self.plotter.ax.get_xlim()))

    def test_tight_sets_correct_y_axes_limits(self):
        self.plotter.parameters["tight"] = "y"
        self.plotter.datasets.append(self.dataset)
        self.plotter.plot()
        self.assertListEqual(
            [min(self.dataset.data.data), max(self.dataset.data.data)],
            list(self.plotter.ax.get_ylim()),
        )

    def test_tight_sets_correct_axes_limits_with(self):
        self.plotter.parameters["tight"] = "both"
        self.plotter.datasets.append(self.dataset)
        self.plotter.plot()
        self.assertListEqual([0, 4], list(self.plotter.ax.get_xlim()))
        self.assertListEqual(
            [min(self.dataset.data.data), max(self.dataset.data.data)],
            list(self.plotter.ax.get_ylim()),
        )

    def test_tight_sets_correct_x_axes_limits_with_switched_axes(self):
        self.plotter.parameters["switch_axes"] = True
        self.plotter.parameters["tight"] = "x"
        self.plotter.datasets.append(self.dataset)
        self.plotter.plot()
        self.assertListEqual(
            [min(self.dataset.data.data), max(self.dataset.data.data)],
            list(self.plotter.ax.get_xlim()),
        )

    def test_tight_sets_correct_y_axes_limits_with_switched_axes(self):
        self.plotter.parameters["switch_axes"] = True
        self.plotter.parameters["tight"] = "y"
        self.plotter.datasets.append(self.dataset)
        self.plotter.plot()
        self.assertListEqual([0, 4], list(self.plotter.ax.get_ylim()))

    def test_tight_sets_correct_axes_limits_with_switched_axes(self):
        self.plotter.parameters["switch_axes"] = True
        self.plotter.parameters["tight"] = "both"
        self.plotter.datasets.append(self.dataset)
        self.plotter.plot()
        self.assertListEqual(
            [min(self.dataset.data.data), max(self.dataset.data.data)],
            list(self.plotter.ax.get_xlim()),
        )
        self.assertListEqual([0, 4], list(self.plotter.ax.get_ylim()))

    def test_plot_device_data_checks_applicability(self):
        device_data = dataset.DeviceData()
        device_data.data = np.random.random([5, 5])
        self.dataset.device_data["test"] = device_data
        self.plotter.parameters["device_data"] = "test"
        self.plotter.datasets.append(self.dataset)
        with self.assertRaises(aspecd.exceptions.NotApplicableToDatasetError):
            self.plotter.plot()

    def test_plot_device_data_plots_device_data(self):
        device_data = dataset.DeviceData()
        device_data.data = np.random.random(5)
        self.dataset.device_data["test"] = device_data
        self.plotter.parameters["device_data"] = "test"
        self.plotter.datasets.append(self.dataset)
        self.plotter.plot()
        self.assertListEqual(
            list(device_data.data),
            list(self.plotter.axes.lines[0].get_ydata()),
        )

    def test_semilogy_plot_with_negative_values_logs_warning(self):
        self.plotter.type = "semilogy"
        self.dataset.data.data = self.dataset.data.data - np.mean(
            self.dataset.data.data
        )
        self.plotter.datasets.append(self.dataset)
        with self.assertLogs(__package__, level="WARNING") as cm:
            self.plotter.plot()
        self.assertIn("", cm.output[0])

    def test_semilogx_plot_with_negative_axis_values_logs_warning(self):
        self.plotter.type = "semilogx"
        self.dataset.data.axes[0].values = np.linspace(
            -2, 2, len(self.dataset.data.data)
        )
        self.plotter.datasets.append(self.dataset)
        with self.assertLogs(__package__, level="WARNING") as cm:
            self.plotter.plot()
        self.assertIn("Negative values", cm.output[0])

    def test_loglog_plot_with_negative_values_logs_warning(self):
        self.plotter.type = "loglog"
        self.dataset.data.data = self.dataset.data.data - np.mean(
            self.dataset.data.data
        )
        self.plotter.datasets.append(self.dataset)
        with self.assertLogs(__package__, level="WARNING") as cm:
            self.plotter.plot()
        self.assertIn("Negative values", cm.output[0])

    def test_loglog_plot_with_negative_axis_values_logs_warning(self):
        self.plotter.type = "loglog"
        self.dataset.data.axes[0].values = np.linspace(
            -2, 2, len(self.dataset.data.data)
        )
        self.plotter.datasets.append(self.dataset)
        with self.assertLogs(__package__, level="WARNING") as cm:
            self.plotter.plot()
        self.assertIn("Negative values", cm.output[0])

    def test_semilogy_plot_w_neg_axis_values_and_switch_axis_logs_warning(
        self,
    ):
        self.plotter.type = "semilogy"
        self.plotter.parameters["switch_axes"] = True
        self.dataset.data.axes[0].values = np.linspace(
            -2, 2, len(self.dataset.data.data)
        )
        self.plotter.datasets.append(self.dataset)
        with self.assertLogs(__package__, level="WARNING") as cm:
            self.plotter.plot()
        self.assertIn("", cm.output[0])

    def test_semilogx_plot_w_neg_values_and_switch_axis_logs_warning(self):
        self.plotter.type = "semilogx"
        self.plotter.parameters["switch_axes"] = True
        self.dataset.data.data = self.dataset.data.data - np.mean(
            self.dataset.data.data
        )
        self.plotter.datasets.append(self.dataset)
        with self.assertLogs(__package__, level="WARNING") as cm:
            self.plotter.plot()
        self.assertIn("Negative values", cm.output[0])


class TestMultiPlotter1DStacked(unittest.TestCase):
    def setUp(self):
        self.plotter = plotting.MultiPlotter1DStacked()
        dataset_ = aspecd.dataset.CalculatedDataset()
        dataset_.data.data = np.sin(np.linspace(0, 2 * np.pi))
        dataset_.data.axes[0].quantity = "magnetic field"
        dataset_.data.axes[0].unit = "mT"
        self.plotter.datasets.append(dataset_)
        self.plotter.datasets.append(dataset_)
        self.plotter.datasets.append(dataset_)

    def tearDown(self):
        if self.plotter.fig:
            plt.close(self.plotter.fig)

    def test_instantiate_class(self):
        pass

    def test_description_is_sensible(self):
        self.assertNotIn("Abstract", self.plotter.description)

    def test_plot_stacks_plots(self):
        self.plotter.plot()
        self.assertLess(
            min(self.plotter.axes.get_lines()[2].get_ydata()),
            min(self.plotter.axes.get_lines()[0].get_ydata()) * 2,
        )

    def test_plot_removes_yticks(self):
        self.plotter.plot()
        self.assertEqual(0, len(self.plotter.axes.get_yticklabels()))

    def test_plot_has_zero_lines_turned_off_by_default(self):
        self.plotter.plot()
        self.assertFalse(self.plotter.parameters["show_zero_lines"])

    def test_parameters_have_offset_key(self):
        self.assertIn("offset", self.plotter.parameters)

    def test_plot_stacks_plots_with_given_offset(self):
        self.plotter.parameters["offset"] = 10
        self.plotter.plot()
        self.assertLess(
            min(self.plotter.axes.get_lines()[2].get_ydata()),
            min(self.plotter.axes.get_lines()[0].get_ydata()) * 20,
        )

    def test_plot_zero_lines_for_each_trace(self):
        self.plotter.parameters["show_zero_lines"] = True
        self.plotter.plot()
        self.assertEqual(
            2 * len(self.plotter.datasets), len(self.plotter.axes.get_lines())
        )

    def test_plot_zero_lines_for_each_trace_at_correct_position(self):
        self.plotter.parameters["show_zero_lines"] = True
        self.plotter.plot()
        self.assertGreater(
            0, self.plotter.axes.get_lines()[-1].get_ydata()[0]
        )

    def test_has_tight_parameter(self):
        self.assertTrue("tight" in self.plotter.parameters)

    def test_tight_sets_correct_x_axes_limits(self):
        self.plotter.parameters["tight"] = "x"
        self.plotter.plot()
        self.assertListEqual(
            [0, len(self.plotter.datasets[0].data.data) - 1],
            list(self.plotter.ax.get_xlim()),
        )

    def test_tight_sets_correct_y_axes_limits(self):
        self.plotter.parameters["tight"] = "y"
        self.plotter.plot()
        data_limits = [
            min(
                [
                    dataset_.data.data.min()
                    for dataset_ in self.plotter.datasets
                ]
            ),
            max(
                [
                    dataset_.data.data.max()
                    for dataset_ in self.plotter.datasets
                ]
            ),
        ]
        data_limits[0] -= self.plotter.parameters["offset"] * (
            len(self.plotter.datasets) - 1
        )
        self.assertListEqual(data_limits, list(self.plotter.ax.get_ylim()))

    def test_tight_sets_correct_axes_limits(self):
        self.plotter.parameters["tight"] = "both"
        self.plotter.plot()
        self.assertListEqual(
            [0, len(self.plotter.datasets[0].data.data) - 1],
            list(self.plotter.ax.get_xlim()),
        )
        data_limits = [
            min(
                [
                    dataset_.data.data.min()
                    for dataset_ in self.plotter.datasets
                ]
            ),
            max(
                [
                    dataset_.data.data.max()
                    for dataset_ in self.plotter.datasets
                ]
            ),
        ]
        data_limits[0] -= self.plotter.parameters["offset"] * (
            len(self.plotter.datasets) - 1
        )
        self.assertListEqual(data_limits, list(self.plotter.ax.get_ylim()))

    def test_has_switch_axes_parameter(self):
        self.assertTrue("switch_axes" in self.plotter.parameters)

    def test_switch_axes_sets_correct_axes_labels(self):
        self.plotter.parameters["switch_axes"] = True
        self.plotter.plot()
        self.assertIn("magnetic", self.plotter.ax.get_ylabel())

    def test_switch_axes_actually_switches_axes(self):
        self.plotter.parameters["switch_axes"] = True
        self.plotter.plot()
        self.assertListEqual(
            list(self.plotter.datasets[0].data.data),
            list(self.plotter.axes.lines[0].get_xdata()),
        )

    def test_tight_sets_correct_x_axes_limits_with_switched_axes(self):
        self.plotter.parameters["tight"] = "x"
        self.plotter.parameters["switch_axes"] = True
        self.plotter.plot()
        data_limits = [
            min(
                [
                    dataset_.data.data.min()
                    for dataset_ in self.plotter.datasets
                ]
            ),
            max(
                [
                    dataset_.data.data.max()
                    for dataset_ in self.plotter.datasets
                ]
            ),
        ]
        data_limits[0] -= self.plotter.parameters["offset"] * (
            len(self.plotter.datasets) - 1
        )
        self.assertListEqual(data_limits, list(self.plotter.ax.get_xlim()))

    def test_tight_sets_correct_y_axes_limits_with_switched_axes(self):
        self.plotter.parameters["tight"] = "y"
        self.plotter.parameters["switch_axes"] = True
        self.plotter.plot()
        self.assertListEqual(
            [0, len(self.plotter.datasets[0].data.data) - 1],
            list(self.plotter.ax.get_ylim()),
        )

    def test_tight_sets_correct_axes_limits_with_switched_axes(self):
        self.plotter.parameters["tight"] = "both"
        self.plotter.parameters["switch_axes"] = True
        self.plotter.plot()
        self.assertListEqual(
            [0, len(self.plotter.datasets[0].data.data) - 1],
            list(self.plotter.ax.get_ylim()),
        )
        data_limits = [
            min(
                [
                    dataset_.data.data.min()
                    for dataset_ in self.plotter.datasets
                ]
            ),
            max(
                [
                    dataset_.data.data.max()
                    for dataset_ in self.plotter.datasets
                ]
            ),
        ]
        data_limits[0] -= self.plotter.parameters["offset"] * (
            len(self.plotter.datasets) - 1
        )
        self.assertListEqual(data_limits, list(self.plotter.ax.get_xlim()))


class TestCompositePlotter(unittest.TestCase):
    def setUp(self):
        self.plotter = plotting.CompositePlotter()
        self.dataset = aspecd.dataset.CalculatedDataset()
        self.dataset.data.data = np.sin(np.linspace(0, 2 * np.pi, 101))

    def tearDown(self):
        if self.plotter.fig:
            plt.close(self.plotter.fig)

    def test_instantiate_class(self):
        pass

    def test_description_is_sensible(self):
        self.assertIn("Composite", self.plotter.description)

    def test_has_grid_dimensions_property(self):
        self.assertTrue(hasattr(self.plotter, "grid_dimensions"))

    def test_has_subplot_locations_property(self):
        self.assertTrue(hasattr(self.plotter, "subplot_locations"))

    def test_has_axes_positions_property(self):
        self.assertTrue(hasattr(self.plotter, "axes_positions"))

    def test_has_plotter_property(self):
        self.assertTrue(hasattr(self.plotter, "plotter"))

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
        self.plotter.subplot_locations = [
            [0, 0, 1, 1],
            [1, 0, 1, 1],
            [0, 1, 2, 1],
        ]
        single_plotter = plotting.SinglePlotter1D()
        single_plotter.dataset = self.dataset
        self.plotter.plotter.append(single_plotter)
        self.plotter.plotter.append(single_plotter)
        self.plotter.plotter.append(single_plotter)
        self.plotter.plot()
        self.assertEqual(
            len(self.plotter.subplot_locations), len(self.plotter.axes)
        )

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
        self.plotter.subplot_locations = [
            [0, 0, 1, 1],
            [1, 0, 1, 1],
            [0, 1, 2, 1],
        ]
        single_plotter = plotting.SinglePlotter1D()
        single_plotter.dataset = self.dataset
        self.plotter.plotter.append(single_plotter)
        self.plotter.plotter.append(single_plotter)
        with self.assertRaises(aspecd.exceptions.MissingPlotterError):
            self.plotter.plot()

    def test_plot_sets_axes_position(self):
        self.plotter.grid_dimensions = [1, 1]
        self.plotter.subplot_locations = [[0, 0, 1, 1]]
        self.plotter.axes_positions = [[0.2, 0.2, -0.2, -0.2]]
        single_plotter = plotting.SinglePlotter1D()
        single_plotter.dataset = self.dataset
        self.plotter.plotter.append(single_plotter)
        self.plotter.plot()
        offsets = self.plotter.axes_positions[0]
        axis_position = [
            0.125 + offsets[0] * 0.775,
            0.110 + offsets[1] * 0.77,
            offsets[2] * 0.775,
            offsets[3] * 0.77,
        ]
        self.assertListEqual(
            axis_position, list(self.plotter.axes[0].get_position().bounds)
        )

    def test_plot_shows_legend(self):
        self.plotter.grid_dimensions = [1, 1]
        self.plotter.subplot_locations = [[0, 0, 1, 1]]
        single_plotter = plotting.SinglePlotter1D()
        single_plotter.dataset = self.dataset
        single_plotter.parameters["show_legend"] = True
        self.plotter.plotter.append(single_plotter)
        with contextlib.redirect_stderr(io.StringIO()):
            self.plotter.plot()
        self.assertTrue(
            isinstance(
                self.plotter.axes[0].get_legend(), matplotlib.legend.Legend
            )
        )

    def test_plot_sets_style_property_to_plotters(self):
        self.plotter.grid_dimensions = [1, 1]
        self.plotter.subplot_locations = [[0, 0, 1, 1]]
        single_plotter = plotting.SinglePlotter1D()
        single_plotter.dataset = self.dataset
        self.plotter.style = "xkcd"
        self.plotter.plotter.append(single_plotter)
        with contextlib.redirect_stderr(io.StringIO()):
            self.plotter.plot()
        self.assertEqual(self.plotter.style, self.plotter.plotter[0].style)


class TestSingleCompositePlotter(unittest.TestCase):
    def setUp(self):
        self.plotter = plotting.SingleCompositePlotter()

    def tearDown(self):
        if self.plotter.fig:
            plt.close(self.plotter.fig)

    def test_instantiate_class(self):
        pass

    def test_description_is_sensible(self):
        self.assertIn("single dataset", self.plotter.description)

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

    def test_plot_with_dataset_sets_only_one_representation(self):
        self.plotter.grid_dimensions = [1, 1]
        self.plotter.subplot_locations = [[0, 0, 1, 1]]
        single_plotter = plotting.SinglePlotter1D()
        self.plotter.plotter.append(single_plotter)
        test_dataset = dataset.Dataset()
        self.plotter.plot(dataset=test_dataset)
        self.assertEqual(1, len(test_dataset.representations))

    def test_plot_with_dataset_sets_only_one_task(self):
        self.plotter.grid_dimensions = [1, 1]
        self.plotter.subplot_locations = [[0, 0, 1, 1]]
        single_plotter = plotting.SinglePlotter1D()
        self.plotter.plotter.append(single_plotter)
        test_dataset = dataset.Dataset()
        self.plotter.plot(dataset=test_dataset)
        self.assertEqual(1, len(test_dataset.tasks))

    def test_plot_checks_applicability(self):
        class MyPlotter(aspecd.plotting.SingleCompositePlotter):
            @staticmethod
            def applicable(dataset):
                return False

        dataset = aspecd.dataset.Dataset()
        plotter = MyPlotter()
        with self.assertRaises(aspecd.exceptions.NotApplicableToDatasetError):
            dataset.plot(plotter)

    def test_plot_check_applicability_prints_helpful_message(self):
        class MyPlotter(aspecd.plotting.SingleCompositePlotter):
            @staticmethod
            def applicable(dataset):
                return False

        dataset = aspecd.dataset.Dataset()
        dataset.id = "foo"
        plotter = MyPlotter()
        message = "MyPlotter not applicable to dataset with id foo"
        with self.assertRaisesRegex(
            aspecd.exceptions.NotApplicableToDatasetError, message
        ):
            dataset.plot(plotter)


class TestSaver(unittest.TestCase):
    def setUp(self):
        self.saver = plotting.Saver()
        self.filename = "test.pdf"

    def tearDown(self):
        if os.path.isfile(self.filename):
            os.remove(self.filename)
        if self.saver.plotter and self.saver.plotter.fig:
            plt.close(self.saver.plotter.fig)

    def test_instantiate_class(self):
        pass

    def test_has_save_method(self):
        self.assertTrue(hasattr(self.saver, "save"))
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
        self.assertTrue(hasattr(self.saver, "parameters"))

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
        self.filename = "test.pdf"
        self.saver.filename, _ = os.path.splitext(self.filename)
        self.saver.parameters["format"] = "pdf"
        self.saver.save(plotter)
        self.assertTrue(os.path.isfile(self.filename))

    def test_set_format_parameter_corrects_extension(self):
        plotter = plotting.Plotter()
        plotter.plot()
        self.filename = "test.pdf"
        basename, _ = os.path.splitext(self.filename)
        self.saver.parameters["format"] = "pdf"
        self.saver.filename = ".".join([basename, "png"])
        self.saver.save(plotter)
        self.assertTrue(os.path.isfile(self.filename))

    def test_set_format_parameter_writes_appropriate_file(self):
        plotter = plotting.Plotter()
        plotter.plot()
        self.filename = "test.pdf"
        self.saver.filename, _ = os.path.splitext(self.filename)
        self.saver.parameters["format"] = "pdf"
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

    def test_save_with_too_long_filename_replaces_filename_with_hash(self):
        self.saver.plotter = plotting.Plotter()
        self.saver.plotter.plot()
        self.filename = "a_very_long_filename_making_python_crash" * 25
        md5hash = hashlib.md5(self.filename.encode()).hexdigest()
        self.filename = self.filename + ".pdf"
        self.saver.filename = self.filename
        self.saver.save()
        self.assertEqual(md5hash + ".pdf", self.saver.filename)
        self.filename = self.saver.filename  # to automatically remove file


class TestCaption(unittest.TestCase):
    def setUp(self):
        self.caption = plotting.Caption()

    def test_instantiate_class(self):
        pass

    def test_has_to_dict_method(self):
        self.assertTrue(hasattr(self.caption, "to_dict"))
        self.assertTrue(callable(self.caption.to_dict))

    def test_has_from_dict_method(self):
        self.assertTrue(hasattr(self.caption, "from_dict"))
        self.assertTrue(callable(self.caption.from_dict))

    def test_has_title_property(self):
        self.assertTrue(hasattr(self.caption, "title"))

    def test_has_text_property(self):
        self.assertTrue(hasattr(self.caption, "text"))

    def test_has_parameters_property(self):
        self.assertTrue(hasattr(self.caption, "parameters"))


class TestDrawingProperties(unittest.TestCase):
    def setUp(self):
        self.drawing_properties = plotting.DrawingProperties()

    def test_instantiate_class(self):
        pass

    def test_has_to_dict_method(self):
        self.assertTrue(hasattr(self.drawing_properties, "to_dict"))
        self.assertTrue(callable(self.drawing_properties.to_dict))

    def test_has_from_dict_method(self):
        self.assertTrue(hasattr(self.drawing_properties, "from_dict"))
        self.assertTrue(callable(self.drawing_properties.from_dict))

    def test_has_properties(self):
        for prop in ["label"]:
            self.assertTrue(hasattr(self.drawing_properties, prop))

    def test_has_apply_method(self):
        self.assertTrue(hasattr(self.drawing_properties, "apply"))
        self.assertTrue(callable(self.drawing_properties.apply))

    def test_apply_without_argument_raises(self):
        with self.assertRaises(aspecd.exceptions.MissingDrawingError):
            self.drawing_properties.apply()

    def test_apply_sets_properties(self):
        self.drawing_properties.label = "foo"
        line = matplotlib.lines.Line2D([0, 1], [0, 0])
        self.drawing_properties.apply(drawing=line)
        self.assertEqual(self.drawing_properties.label, line.get_label())

    def test_apply_with_nonexisting_property_issues_log_message(self):
        self.drawing_properties.foobar = "foo"
        line = matplotlib.lines.Line2D([0, 1], [0, 0])
        with self.assertLogs(__package__, level="DEBUG") as cm:
            self.drawing_properties.apply(drawing=line)
        self.assertIn(
            '"{}" has no setter for attribute "{}", hence not '
            "set".format(line.__class__, "foobar"),
            cm.output[0],
        )


class TestLineProperties(unittest.TestCase):
    def setUp(self):
        self.line_properties = plotting.LineProperties()

    def test_instantiate_class(self):
        pass

    def test_has_to_dict_method(self):
        self.assertTrue(hasattr(self.line_properties, "to_dict"))
        self.assertTrue(callable(self.line_properties.to_dict))

    def test_has_from_dict_method(self):
        self.assertTrue(hasattr(self.line_properties, "from_dict"))
        self.assertTrue(callable(self.line_properties.from_dict))

    def test_has_properties(self):
        for prop in [
            "color",
            "drawstyle",
            "label",
            "linestyle",
            "linewidth",
            "marker",
        ]:
            self.assertTrue(hasattr(self.line_properties, prop))

    def test_has_apply_method(self):
        self.assertTrue(hasattr(self.line_properties, "apply"))
        self.assertTrue(callable(self.line_properties.apply))

    def test_apply_without_argument_raises(self):
        with self.assertRaises(aspecd.exceptions.MissingDrawingError):
            self.line_properties.apply()

    def test_apply_sets_properties(self):
        self.line_properties.label = "foo"
        # noinspection PyUnresolvedReferences
        line = matplotlib.lines.Line2D([0, 1], [0, 0])
        self.line_properties.apply(drawing=line)
        self.assertEqual(self.line_properties.label, line.get_label())


class TestSurfaceProperties(unittest.TestCase):
    def setUp(self):
        self.properties = plotting.SurfaceProperties()

    def test_instantiate_class(self):
        pass

    def test_has_to_dict_method(self):
        self.assertTrue(hasattr(self.properties, "to_dict"))
        self.assertTrue(callable(self.properties.to_dict))

    def test_has_from_dict_method(self):
        self.assertTrue(hasattr(self.properties, "from_dict"))
        self.assertTrue(callable(self.properties.from_dict))

    def test_has_properties(self):
        for prop in ["cmap"]:
            self.assertTrue(hasattr(self.properties, prop))

    def test_has_apply_method(self):
        self.assertTrue(hasattr(self.properties, "apply"))
        self.assertTrue(callable(self.properties.apply))

    def test_apply_without_argument_raises(self):
        with self.assertRaises(aspecd.exceptions.MissingDrawingError):
            self.properties.apply()

    @unittest.skip
    def test_apply_sets_properties(self):
        self.properties.cmap = "RdGy"
        # noinspection PyUnresolvedReferences
        contour = matplotlib.lines.Line2D([0, 1], [0, 0])
        self.properties.apply(drawing=contour)
        self.assertEqual(self.properties.cmap, contour.cmap.name)


class TestPlotProperties(unittest.TestCase):
    def setUp(self):
        self.plot_properties = plotting.PlotProperties()

    def test_instantiate_class(self):
        pass

    def test_has_to_dict_method(self):
        self.assertTrue(hasattr(self.plot_properties, "to_dict"))
        self.assertTrue(callable(self.plot_properties.to_dict))

    def test_has_from_dict_method(self):
        self.assertTrue(hasattr(self.plot_properties, "from_dict"))
        self.assertTrue(callable(self.plot_properties.from_dict))

    def test_has_figure_property(self):
        self.assertTrue(hasattr(self.plot_properties, "figure"))

    def test_has_apply_method(self):
        self.assertTrue(hasattr(self.plot_properties, "apply"))
        self.assertTrue(callable(self.plot_properties.apply))

    def test_apply_without_argument_raises(self):
        with self.assertRaises(aspecd.exceptions.MissingPlotterError):
            self.plot_properties.apply()

    def test_apply_sets_properties(self):
        self.plot_properties.figure.dpi = 300.0
        plot = plotting.Plotter()
        plot.plot()
        self.plot_properties.apply(plotter=plot)
        self.assertEqual(
            self.plot_properties.figure.dpi, plot.figure.get_dpi()
        )
        plt.close(plot.figure)


class TestFigureProperties(unittest.TestCase):
    def setUp(self):
        self.figure_properties = plotting.FigureProperties()

    def test_instantiate_class(self):
        pass

    def test_has_to_dict_method(self):
        self.assertTrue(hasattr(self.figure_properties, "to_dict"))
        self.assertTrue(callable(self.figure_properties.to_dict))

    def test_has_from_dict_method(self):
        self.assertTrue(hasattr(self.figure_properties, "from_dict"))
        self.assertTrue(callable(self.figure_properties.from_dict))

    def test_has_properties(self):
        for prop in ["size", "dpi", "title"]:
            self.assertTrue(hasattr(self.figure_properties, prop))

    def test_has_apply_method(self):
        self.assertTrue(hasattr(self.figure_properties, "apply"))
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
        self.assertListEqual(
            list(self.figure_properties.size),
            list(plot.figure.get_size_inches()),
        )
        plt.close(plot.figure)

    def test_apply_sets_figure_title(self):
        self.figure_properties.title = "foo"
        plot = plotting.Plotter()
        plot.plot()
        self.figure_properties.apply(figure=plot.figure)
        self.assertEqual(
            self.figure_properties.title, plot.figure._suptitle.get_text()
        )
        plt.close(plot.figure)


class TestAxesProperties(unittest.TestCase):
    def setUp(self):
        self.axis_properties = plotting.AxesProperties()

    def test_instantiate_class(self):
        pass

    def test_has_to_dict_method(self):
        self.assertTrue(hasattr(self.axis_properties, "to_dict"))
        self.assertTrue(callable(self.axis_properties.to_dict))

    def test_has_from_dict_method(self):
        self.assertTrue(hasattr(self.axis_properties, "from_dict"))
        self.assertTrue(callable(self.axis_properties.from_dict))

    def test_has_properties(self):
        for prop in [
            "aspect",
            "facecolor",
            "position",
            "title",
            "xlabel",
            "xlim",
            "xscale",
            "xticklabels",
            "xticks",
            "ylabel",
            "ylim",
            "yscale",
            "yticklabels",
            "yticks",
            "xticklabelangle",
            "yticklabelangle",
            "invert",
        ]:
            self.assertTrue(hasattr(self.axis_properties, prop))

    def test_has_apply_properties_method(self):
        self.assertTrue(hasattr(self.axis_properties, "apply"))
        self.assertTrue(callable(self.axis_properties.apply))

    def test_apply_properties_without_argument_raises(self):
        with self.assertRaises(aspecd.exceptions.MissingAxisError):
            self.axis_properties.apply()

    def test_apply_properties_sets_axis_properties(self):
        self.axis_properties.xlabel = "foo"
        plot = plotting.Plotter()
        plot.plot()
        self.axis_properties.apply(axes=plot.axes)
        self.assertEqual(self.axis_properties.xlabel, plot.axes.get_xlabel())
        plt.close(plot.figure)

    def test_set_empty_axis_ylabel(self):
        self.axis_properties.ylabel = ""
        plot = plotting.Plotter()
        plot.plot()
        self.axis_properties.apply(axes=plot.axes)
        self.assertEqual(self.axis_properties.ylabel, plot.axes.get_ylabel())
        plt.close(plot.figure)

    def test_apply_properties_from_dict_sets_axis_properties(self):
        label = "foo"
        properties = {"axes": {"xlabel": label}}
        plot = plotting.MultiPlotter1D()
        plot.datasets.append(aspecd.dataset.Dataset())
        plot.properties.from_dict(properties)
        plot.plot()
        self.assertEqual(label, plot.axes.get_xlabel())
        plt.close(plot.figure)

    def test_set_xticks(self):
        self.axis_properties.xticks = np.linspace(0, 1, 11)
        plot = plotting.Plotter()
        plot.plot()
        self.axis_properties.apply(axes=plot.axes)
        self.assertListEqual(
            list(self.axis_properties.xticks), list(plot.axes.get_xticks())
        )
        plt.close(plot.figure)

    def test_set_xtick_labels(self):
        self.axis_properties.xticks = np.linspace(0, 1, 11)
        self.axis_properties.xticklabels = np.linspace(2, 3, 11).astype(str)
        plot = plotting.Plotter()
        plot.plot()
        self.axis_properties.apply(axes=plot.axes)
        self.assertEqual(
            self.axis_properties.xticklabels[5],
            plot.axes.get_xticklabels()[5].get_text(),
        )
        plt.close(plot.figure)

    def test_set_yticks(self):
        self.axis_properties.yticks = np.linspace(0, 1, 11)
        plot = plotting.Plotter()
        plot.plot()
        self.axis_properties.apply(axes=plot.axes)
        self.assertListEqual(
            list(self.axis_properties.yticks), list(plot.axes.get_yticks())
        )
        plt.close(plot.figure)

    def test_set_ytick_labels(self):
        self.axis_properties.yticks = np.linspace(0, 1, 11)
        self.axis_properties.yticklabels = np.linspace(2, 3, 11).astype(str)
        plot = plotting.Plotter()
        plot.plot()
        self.axis_properties.apply(axes=plot.axes)
        self.assertEqual(
            self.axis_properties.yticklabels[5],
            plot.axes.get_yticklabels()[5].get_text(),
        )
        plt.close(plot.figure)

    def test_set_ticks_and_labels_does_not_issue_warning(self):
        self.axis_properties.xticks = np.linspace(0, 1, 11)
        self.axis_properties.xticklabels = np.linspace(2, 3, 11).astype(str)
        plot = plotting.Plotter()
        plot.plot()
        with warnings.catch_warnings(record=True) as warning:
            self.axis_properties.apply(axes=plot.axes)
            self.assertFalse(len(warning))
        plt.close(plot.figure)

    def test_set_xtick_label_angle(self):
        self.axis_properties.xticklabelangle = 45.0
        plot = plotting.Plotter()
        plot.plot()
        self.axis_properties.apply(axes=plot.axes)
        self.assertEqual(
            self.axis_properties.xticklabelangle,
            plot.axes.get_xticklabels()[0].get_rotation(),
        )
        plt.close(plot.figure)

    def test_set_ytick_label_angle(self):
        self.axis_properties.yticklabelangle = 45.0
        plot = plotting.Plotter()
        plot.plot()
        self.axis_properties.apply(axes=plot.axes)
        self.assertEqual(
            self.axis_properties.yticklabelangle,
            plot.axes.get_yticklabels()[0].get_rotation(),
        )
        plt.close(plot.figure)

    def test_invert_x_axis_with_scalar_value(self):
        self.axis_properties.invert = "x"
        plot = plotting.Plotter()
        plot.plot()
        self.axis_properties.apply(axes=plot.axes)
        self.assertTrue(plot.axes.xaxis_inverted())
        plt.close(plot.figure)

    def test_invert_y_axis_with_scalar_value(self):
        self.axis_properties.invert = "y"
        plot = plotting.Plotter()
        plot.plot()
        self.axis_properties.apply(axes=plot.axes)
        self.assertTrue(plot.axes.yaxis_inverted())
        plt.close(plot.figure)

    def test_invert_x_axis_with_scalar_capital_value(self):
        self.axis_properties.invert = "X"
        plot = plotting.Plotter()
        plot.plot()
        self.axis_properties.apply(axes=plot.axes)
        self.assertTrue(plot.axes.xaxis_inverted())
        plt.close(plot.figure)

    def test_invert_x_axis_with_string_starting_with_x(self):
        self.axis_properties.invert = "xaxis"
        plot = plotting.Plotter()
        plot.plot()
        self.axis_properties.apply(axes=plot.axes)
        self.assertTrue(plot.axes.xaxis_inverted())
        plt.close(plot.figure)

    def test_invert_x_axis_with_list_value(self):
        self.axis_properties.invert = ["x"]
        plot = plotting.Plotter()
        plot.plot()
        self.axis_properties.apply(axes=plot.axes)
        self.assertTrue(plot.axes.xaxis_inverted())
        plt.close(plot.figure)

    def test_invert_both_axes(self):
        self.axis_properties.invert = ["x", "y"]
        plot = plotting.Plotter()
        plot.plot()
        self.axis_properties.apply(axes=plot.axes)
        self.assertTrue(plot.axes.xaxis_inverted())
        self.assertTrue(plot.axes.yaxis_inverted())
        plt.close(plot.figure)

    def test_invert_does_not_invert_already_inverted_x_axis(self):
        self.axis_properties.invert = ["x"]
        plot = plotting.Plotter()
        plot.plot()
        plot.axes.invert_xaxis()
        self.axis_properties.apply(axes=plot.axes)
        self.assertTrue(plot.axes.xaxis_inverted())
        plt.close(plot.figure)

    def test_invert_does_not_invert_already_inverted_y_axis(self):
        self.axis_properties.invert = ["y"]
        plot = plotting.Plotter()
        plot.plot()
        plot.axes.invert_yaxis()
        self.axis_properties.apply(axes=plot.axes)
        self.assertTrue(plot.axes.yaxis_inverted())
        plt.close(plot.figure)

    def test_label_fontsize_sets_label_fontsize(self):
        fontsize = "large"
        self.axis_properties.label_fontsize = fontsize
        plot = plotting.Plotter()
        plot.plot()
        self.axis_properties.apply(axes=plot.axes)
        self.assertEqual(
            plt.rcParams["font.size"] * 1.2,
            plot.axes.get_xaxis().get_label().get_fontsize(),
        )
        self.assertEqual(
            plt.rcParams["font.size"] * 1.2,
            plot.axes.get_yaxis().get_label().get_fontsize(),
        )
        plt.close(plot.figure)


class TestLegendProperties(unittest.TestCase):
    def setUp(self):
        self.legend_properties = plotting.LegendProperties()

    def test_instantiate_class(self):
        pass

    def test_has_to_dict_method(self):
        self.assertTrue(hasattr(self.legend_properties, "to_dict"))
        self.assertTrue(callable(self.legend_properties.to_dict))

    def test_has_from_dict_method(self):
        self.assertTrue(hasattr(self.legend_properties, "from_dict"))
        self.assertTrue(callable(self.legend_properties.from_dict))

    def test_has_properties(self):
        for prop in ["loc", "frameon"]:
            self.assertTrue(hasattr(self.legend_properties, prop))

    def test_has_apply_method(self):
        self.assertTrue(hasattr(self.legend_properties, "apply"))
        self.assertTrue(callable(self.legend_properties.apply))

    def test_apply_without_argument_raises(self):
        with self.assertRaises(aspecd.exceptions.MissingLegendError):
            self.legend_properties.apply()

    def test_apply_properties_sets_legend_properties(self):
        self.legend_properties.loc = "center"
        plot = plotting.Plotter()
        plot.plot()
        with contextlib.redirect_stderr(io.StringIO()):
            legend = plot.axes.legend()
        self.legend_properties.apply(legend=legend)
        self.assertEqual(self.legend_properties.loc, legend.loc)
        plt.close(plot.figure)

    def test_location_sets_legend_loc(self):
        location = 5
        self.legend_properties.location = location
        plot = plotting.Plotter()
        plot.properties.legend = self.legend_properties
        plot.parameters["show_legend"] = True
        with contextlib.redirect_stderr(io.StringIO()):
            plot.plot()
        legend = plot.legend
        self.assertEqual(location, legend._loc)
        plt.close(plot.figure)

    def test_location_from_dict_sets_legend_loc(self):
        location = 5
        properties = {"legend": {"location": location}}
        plot = plotting.Plotter()
        plot.properties.from_dict(properties)
        plot.parameters["show_legend"] = True
        with contextlib.redirect_stderr(io.StringIO()):
            plot.plot()
        legend = plot.legend
        self.assertEqual(location, legend._loc)
        plt.close(plot.figure)

    def test_frameon_sets_legend_frameon(self):
        frameon = False
        self.legend_properties.frameon = frameon
        plot = plotting.Plotter()
        plot.properties.legend = self.legend_properties
        plot.parameters["show_legend"] = True
        with contextlib.redirect_stderr(io.StringIO()):
            plot.plot()
        legend = plot.legend
        self.assertEqual(frameon, legend.get_frame_on())
        plt.close(plot.figure)

    def test_location_not_included_in_to_dict(self):
        self.assertNotIn("location", self.legend_properties.to_dict())

    def test_labelspacing_sets_legend_labelspacing(self):
        labelspacing = 0.1
        self.legend_properties.labelspacing = labelspacing
        plot = plotting.Plotter()
        plot.properties.legend = self.legend_properties
        plot.parameters["show_legend"] = True
        with contextlib.redirect_stderr(io.StringIO()):
            plot.plot()
        legend = plot.legend
        self.assertEqual(labelspacing, legend.labelspacing)
        plt.close(plot.figure)

    def test_fontsize_sets_legend_fontsize(self):
        fontsize = "large"
        self.legend_properties.fontsize = fontsize
        plot = plotting.Plotter()
        plot.properties.legend = self.legend_properties
        plot.parameters["show_legend"] = True
        with contextlib.redirect_stderr(io.StringIO()):
            plot.plot()
        legend = plot.legend
        self.assertEqual(
            plt.rcParams["font.size"] * 1.2, legend.prop.get_size()
        )
        plt.close(plot.figure)

    def test_ncol_sets_legend_columns(self):
        ncol = 2
        self.legend_properties.ncol = ncol
        plot = plotting.MultiPlotter1D()
        for idx in range(5):
            dataset_ = dataset.Dataset()
            dataset_.data.data = np.random.random(5)
            dataset_.label = str(idx)
            plot.datasets.append(dataset_)
        plot.properties.legend = self.legend_properties
        plot.parameters["show_legend"] = True
        with contextlib.redirect_stderr(io.StringIO()):
            plot.plot()
        legend = plot.legend
        # plt.show()
        if hasattr(legend, "_ncol"):
            self.assertEqual(ncol, legend._ncol)
        else:
            self.assertEqual(ncol, legend._ncols)
        plt.close(plot.figure)

    def test_title_sets_legend_title(self):
        title = "My fancy title"
        self.legend_properties.title = title
        plot = plotting.Plotter()
        plot.properties.legend = self.legend_properties
        plot.parameters["show_legend"] = True
        with contextlib.redirect_stderr(io.StringIO()):
            plot.plot()
        legend = plot.legend
        self.assertEqual(title, legend.get_title().get_text())
        plt.close(plot.figure)


class TestGridProperties(unittest.TestCase):
    def setUp(self):
        self.grid_properties = plotting.GridProperties()

    def test_instantiate_class(self):
        pass

    def test_has_to_dict_method(self):
        self.assertTrue(hasattr(self.grid_properties, "to_dict"))
        self.assertTrue(callable(self.grid_properties.to_dict))

    def test_has_from_dict_method(self):
        self.assertTrue(hasattr(self.grid_properties, "from_dict"))
        self.assertTrue(callable(self.grid_properties.from_dict))

    def test_has_properties(self):
        for prop in ["show", "ticks", "axis", "lines"]:
            self.assertTrue(hasattr(self.grid_properties, prop))

    def test_has_apply_method(self):
        self.assertTrue(hasattr(self.grid_properties, "apply"))
        self.assertTrue(callable(self.grid_properties.apply))

    def test_apply_without_argument_raises(self):
        with self.assertRaises(TypeError):
            self.grid_properties.apply()

    def test_lines_color_is_sensible_for_grid(self):
        self.assertEqual("#cccccc", self.grid_properties.lines.color)

    def test_apply_properties_sets_properties(self):
        self.grid_properties.show = True
        self.grid_properties.lines.color = "#cccccc"
        plot = plotting.Plotter()
        plot.plot()
        self.grid_properties.apply(axes=plot.axes)
        self.assertEqual(
            self.grid_properties.lines.color,
            plot.axes.xaxis.get_gridlines()[0].get_color(),
        )
        plt.close(plot.figure)


class TestColorbarProperties(unittest.TestCase):
    def setUp(self):
        self.properties = plotting.ColorbarProperties()
        fig, ax = plt.subplots()
        self.colorbar = fig.colorbar(
            matplotlib.cm.ScalarMappable(cmap="viridis"), ax=ax
        )

    def test_instantiate_class(self):
        pass

    def test_has_to_dict_method(self):
        self.assertTrue(hasattr(self.properties, "to_dict"))
        self.assertTrue(callable(self.properties.to_dict))

    def test_has_from_dict_method(self):
        self.assertTrue(hasattr(self.properties, "from_dict"))
        self.assertTrue(callable(self.properties.from_dict))

    def test_has_properties(self):
        for prop in [
            "location",
            "fraction",
            "aspect",
            "pad",
            "label",
            "format",
        ]:
            self.assertTrue(hasattr(self.properties, prop))

    def test_location_sets_legend_location(self):
        location = "top"
        self.properties.location = location
        plot = plotting.SinglePlotter2D()
        plot.properties.colorbar = self.properties
        plot.parameters["show_colorbar"] = True
        dataset_ = dataset.Dataset()
        dataset_.data.data = np.random.random([5, 5])
        plot.plot(dataset=dataset_)
        # Note: the location is not set in the colorbar, only the orientation
        self.assertEqual("horizontal", plot.colorbar.orientation)
        plt.close(plot.figure)

    def test_kwargs_does_not_include_extra_parameters(self):
        self.assertNotIn("label", self.properties.kwargs)


class TestSinglePlotProperties(unittest.TestCase):
    def setUp(self):
        self.plot_properties = plotting.SinglePlotProperties()

    def test_instantiate_class(self):
        pass

    def test_has_figure_property(self):
        self.assertTrue(hasattr(self.plot_properties, "figure"))

    def test_has_axes_property(self):
        self.assertTrue(hasattr(self.plot_properties, "axes"))

    def test_has_grid_property(self):
        self.assertTrue(hasattr(self.plot_properties, "grid"))

    def test_has_drawing_property(self):
        self.assertTrue(hasattr(self.plot_properties, "drawing"))

    def test_has_to_dict_method(self):
        self.assertTrue(hasattr(self.plot_properties, "to_dict"))
        self.assertTrue(callable(self.plot_properties.to_dict))

    def test_has_from_dict_method(self):
        self.assertTrue(hasattr(self.plot_properties, "from_dict"))
        self.assertTrue(callable(self.plot_properties.from_dict))

    def test_apply_sets_axis_properties(self):
        self.plot_properties.axes.xlabel = "foo"
        plot = plotting.SinglePlotter()
        plot.plot(dataset=dataset.Dataset())
        self.plot_properties.apply(plotter=plot)
        self.assertEqual(
            self.plot_properties.axes.xlabel, plot.axes.get_xlabel()
        )
        plt.close(plot.figure)

    def test_apply_sets_grid_properties(self):
        self.plot_properties.grid.show = True
        self.plot_properties.grid.lines.color = "#000000"
        plot = plotting.SinglePlotter()
        plot.plot(dataset=dataset.Dataset())
        self.plot_properties.apply(plotter=plot)
        self.assertEqual(
            self.plot_properties.grid.lines.color,
            plot.axes.xaxis.get_gridlines()[0].get_color(),
        )
        plt.close(plot.figure)

    def test_apply_sets_drawing_properties(self):
        self.plot_properties.drawing.label = "foo"
        plot = plotting.SinglePlotter1D()
        plot.plot(dataset=dataset.Dataset())
        self.plot_properties.apply(plotter=plot)
        self.assertEqual(
            self.plot_properties.drawing.label, plot.drawing.get_label()
        )
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
        self.assertEqual(
            self.plot_properties.drawing.linewidth,
            plot.drawing.get_linewidth(),
        )
        plt.close(plot.figure)


class TestSinglePlot2DProperties(unittest.TestCase):
    def setUp(self):
        self.plot_properties = plotting.SinglePlot2DProperties()

    def test_instantiate_class(self):
        pass

    def test_apply_without_argument_raises(self):
        with self.assertRaises(aspecd.exceptions.MissingPlotterError):
            self.plot_properties.apply()

    def test_apply_sets_drawing_properties(self):
        self.plot_properties.drawing.cmap = "RdGy"
        plot = plotting.SinglePlotter2D()
        dataset_ = dataset.Dataset()
        dataset_.data.data = np.random.random([5, 5])
        plot.plot(dataset=dataset_)
        self.plot_properties.apply(plotter=plot)
        self.assertEqual(
            self.plot_properties.drawing.cmap, plot.drawing.cmap.name
        )
        plt.close(plot.figure)

    def test_colormap_is_empty_by_default(self):
        self.assertEqual("", self.plot_properties.colormap)

    def test_setting_colormap_property_sets_drawing_cmap_property(self):
        colormap = "RdGy"
        self.plot_properties.colormap = colormap
        self.assertEqual(colormap, self.plot_properties.drawing.cmap)

    def test_colormap_is_included_in_to_dict(self):
        self.assertIn("colormap", self.plot_properties.to_dict())

    def test_has_colorbar_property(self):
        self.assertTrue(hasattr(self.plot_properties, "colorbar"))


class TestMultiPlotProperties(unittest.TestCase):
    def setUp(self):
        self.plot_properties = plotting.MultiPlotProperties()

    def test_instantiate_class(self):
        pass

    def test_has_figure_property(self):
        self.assertTrue(hasattr(self.plot_properties, "figure"))

    def test_has_axes_property(self):
        self.assertTrue(hasattr(self.plot_properties, "axes"))

    def test_has_grid_property(self):
        self.assertTrue(hasattr(self.plot_properties, "grid"))

    def test_has_drawings_property(self):
        self.assertTrue(hasattr(self.plot_properties, "drawings"))

    def test_has_legend_property(self):
        self.assertTrue(hasattr(self.plot_properties, "legend"))

    def test_has_to_dict_method(self):
        self.assertTrue(hasattr(self.plot_properties, "to_dict"))
        self.assertTrue(callable(self.plot_properties.to_dict))

    def test_has_from_dict_method(self):
        self.assertTrue(hasattr(self.plot_properties, "from_dict"))
        self.assertTrue(callable(self.plot_properties.from_dict))

    def test_apply_sets_axis_properties(self):
        self.plot_properties.axes.xlabel = "foo"
        plot = plotting.MultiPlotter()
        plot.datasets = [dataset.Dataset()]
        plot.plot()
        self.plot_properties.apply(plotter=plot)
        self.assertEqual(
            self.plot_properties.axes.xlabel, plot.axes.get_xlabel()
        )
        plt.close(plot.figure)

    def test_apply_sets_grid_properties(self):
        self.plot_properties.grid.show = True
        self.plot_properties.grid.lines.color = "#000000"
        plot = plotting.SinglePlotter()
        plot.plot(dataset=dataset.Dataset())
        self.plot_properties.apply(plotter=plot)
        self.assertEqual(
            self.plot_properties.grid.lines.color,
            plot.axes.xaxis.get_gridlines()[0].get_color(),
        )
        plt.close(plot.figure)

    def test_apply_sets_legend_properties(self):
        self.plot_properties.legend.loc = "center"
        plotter = plotting.MultiPlotter()
        dataset_ = dataset.Dataset()
        dataset_.label = "foo"
        plotter.datasets = [dataset_]
        plotter.plot()
        with contextlib.redirect_stderr(io.StringIO()):
            plotter.legend = plotter.axes.legend()
        self.plot_properties.apply(plotter=plotter)
        self.assertEqual(self.plot_properties.legend.loc, plotter.legend.loc)
        plt.close(plotter.figure)

    def test_from_dict_sets_drawings(self):
        dict_ = {"drawings": [{"label": "foo"}]}
        self.plot_properties.from_dict(dict_)
        self.assertEqual("foo", self.plot_properties.drawings[0].label)

    def test_from_dict_sets_multiple_drawings(self):
        dict_ = {"drawings": [{"label": "foo"}, {"label": "bar"}]}
        self.plot_properties.from_dict(dict_)
        self.assertEqual("foo", self.plot_properties.drawings[0].label)
        self.assertEqual("bar", self.plot_properties.drawings[1].label)

    def test_from_dict_does_not_add_drawing_if_it_exists(self):
        self.plot_properties.drawings.append(
            aspecd.plotting.DrawingProperties()
        )
        dict_ = {"drawings": [{"label": "foo"}]}
        self.plot_properties.from_dict(dict_)
        self.assertEqual(1, len(self.plot_properties.drawings))

    def test_from_dict_adds_missing_drawing(self):
        dict_ = {"drawings": [{"label": "foo"}]}
        self.plot_properties.from_dict(dict_)
        self.assertEqual(1, len(self.plot_properties.drawings))

    def test_from_dict_adds_missing_drawings(self):
        dict_ = {"drawings": [{"label": "foo"}, {"label": "bar"}]}
        self.plot_properties.from_dict(dict_)
        self.assertEqual(2, len(self.plot_properties.drawings))

    def test_from_dict_sets_legend(self):
        dict_ = {"legend": {"loc": "center"}, "drawings": [{"label": "foo"}]}
        self.plot_properties.from_dict(dict_)
        self.assertEqual("center", self.plot_properties.legend.loc)


class TestMultiPlot1DProperties(unittest.TestCase):
    def setUp(self):
        self.plot_properties = plotting.MultiPlot1DProperties()

    def test_instantiate_class(self):
        pass

    def test_added_drawing_is_line_properties_object(self):
        self.plot_properties.add_drawing()
        self.assertIs(
            type(self.plot_properties.drawings[0]),
            aspecd.plotting.LineProperties,
        )

    def test_added_drawing_has_correct_default_colour(self):
        property_cycle = plt.rcParams["axes.prop_cycle"].by_key()
        colour = property_cycle["color"][0]
        self.plot_properties.add_drawing()
        self.assertEqual(colour, self.plot_properties.drawings[0].color)

    def test_drawing_has_correct_color_if_more_drawings_than_colors(self):
        property_cycle = plt.rcParams["axes.prop_cycle"].by_key()
        colour = property_cycle["color"][0]
        for idx in range(0, len(property_cycle["color"]) + 1):
            self.plot_properties.add_drawing()
        self.assertEqual(colour, self.plot_properties.drawings[0].color)

    def test_added_drawing_has_correct_default_linewidth(self):
        linewidth = plt.rcParams["lines.linewidth"]
        self.plot_properties.add_drawing()
        self.assertEqual(
            linewidth, self.plot_properties.drawings[0].linewidth
        )

    def test_added_drawing_has_correct_default_linestyle(self):
        linewidth = plt.rcParams["lines.linestyle"]
        self.plot_properties.add_drawing()
        self.assertEqual(
            linewidth, self.plot_properties.drawings[0].linestyle
        )

    def test_added_drawing_has_correct_default_marker(self):
        linewidth = plt.rcParams["lines.marker"]
        self.plot_properties.add_drawing()
        self.assertEqual(linewidth, self.plot_properties.drawings[0].marker)

    def test_added_drawing_with_colormap_has_correct_colour(self):
        colormap_name = "viridis"
        n_drawings = 20
        colours = plt.get_cmap(colormap_name, n_drawings)
        self.plot_properties.colormap = colormap_name

        plotter = plotting.MultiPlotter1D()
        plotter.properties = self.plot_properties
        x = np.linspace(0, 2 * np.pi, 64)
        y = np.cos(x)
        for idx in range(n_drawings):
            dataset_ = dataset.Dataset()
            dataset_.data.data = idx * y
            plotter.datasets.append(dataset_)
        plotter.plot()
        self.assertEqual(colours(1), plotter.properties.drawings[1].color)
        # plt.show()
        plt.close(plotter.figure)

    def test_legend_with_colormap_has_correct_colour(self):
        colormap_name = "viridis"
        n_drawings = 20
        colours = plt.get_cmap(colormap_name, n_drawings)
        self.plot_properties.colormap = colormap_name

        plotter = plotting.MultiPlotter1D()
        plotter.properties = self.plot_properties
        plotter.parameters["show_legend"] = True
        x = np.linspace(0, 2 * np.pi, 64)
        y = np.cos(x)
        for idx in range(n_drawings):
            dataset_ = dataset.Dataset()
            dataset_.data.data = idx * y
            dataset_.label = str(idx)
            plotter.datasets.append(dataset_)
        plotter.plot()
        self.assertEqual(
            colours(1), plotter.legend.get_lines()[1].get_color()
        )
        # plt.show()
        plt.close(plotter.figure)


class TestCompositePlotProperties(unittest.TestCase):
    def setUp(self):
        self.plot_properties = plotting.CompositePlotProperties()

    def test_instantiate_class(self):
        pass

    def test_has_figure_property(self):
        self.assertTrue(hasattr(self.plot_properties, "figure"))

    def test_has_axes_property(self):
        self.assertTrue(hasattr(self.plot_properties, "axes"))

    def test_has_to_dict_method(self):
        self.assertTrue(hasattr(self.plot_properties, "to_dict"))
        self.assertTrue(callable(self.plot_properties.to_dict))

    def test_has_from_dict_method(self):
        self.assertTrue(hasattr(self.plot_properties, "from_dict"))
        self.assertTrue(callable(self.plot_properties.from_dict))

    def test_apply_sets_axis_properties(self):
        self.plot_properties.axes.xlabel = "foo"
        plot = plotting.CompositePlotter()
        plot.grid_dimensions = [1, 1]
        plot.subplot_locations = [[0, 0, 1, 1]]
        single_plotter = plotting.SinglePlotter1D()
        dataset_ = aspecd.dataset.CalculatedDataset()
        dataset_.data.data = np.sin(np.linspace(0, 2 * np.pi, 101))
        single_plotter.dataset = dataset_
        plot.plotter.append(single_plotter)
        plot.plot()
        self.plot_properties.apply(plotter=plot)
        self.assertEqual(
            self.plot_properties.axes.xlabel, plot.axes[0].get_xlabel()
        )
        plt.close(plot.figure)

    def test_apply_sets_axis_properties_for_multiple_plots(self):
        self.plot_properties.axes.xlabel = "foo"
        plot = plotting.CompositePlotter()
        plot.grid_dimensions = [2, 1]
        plot.subplot_locations = [[0, 0, 1, 1], [1, 0, 1, 1]]
        single_plotter = plotting.SinglePlotter1D()
        dataset_ = aspecd.dataset.CalculatedDataset()
        dataset_.data.data = np.sin(np.linspace(0, 2 * np.pi, 101))
        single_plotter.dataset = dataset_
        plot.plotter.append(single_plotter)
        plot.plotter.append(single_plotter)
        plot.plot()
        self.plot_properties.apply(plotter=plot)
        self.assertEqual(
            self.plot_properties.axes.xlabel, plot.axes[0].get_xlabel()
        )
        self.assertEqual(
            self.plot_properties.axes.xlabel, plot.axes[1].get_xlabel()
        )
        plt.close(plot.figure)

    def test_apply_overrides_axis_properties(self):
        self.plot_properties.axes.xlabel = "foo"
        plot = plotting.CompositePlotter()
        plot.grid_dimensions = [1, 1]
        plot.subplot_locations = [[0, 0, 1, 1]]
        single_plotter = plotting.SinglePlotter1D()
        single_plotter.properties.axes.xlabel = "bar"
        dataset_ = aspecd.dataset.CalculatedDataset()
        dataset_.data.data = np.sin(np.linspace(0, 2 * np.pi, 101))
        single_plotter.dataset = dataset_
        plot.plotter.append(single_plotter)
        plot.plot()
        self.plot_properties.apply(plotter=plot)
        self.assertEqual(
            self.plot_properties.axes.xlabel, plot.axes[0].get_xlabel()
        )
        plt.close(plot.figure)
