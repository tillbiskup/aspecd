"""Tests for plotting."""

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

    def test_plot_without_dataset_raises(self):
        with self.assertRaises(plotting.MissingDatasetError):
            self.plotter.plot()

    def test_plot_with_dataset(self):
        self.plotter.dataset = dataset.Dataset()
        self.plotter.plot()

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

    def test_has_save_method(self):
        self.assertTrue(hasattr(self.plotter, 'save'))
        self.assertTrue(callable(self.plotter.save))
