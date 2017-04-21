"""Tests for data."""

import unittest
import numpy as np

from aspecd import data


class TestAxis(unittest.TestCase):

    def setUp(self):
        self.data = data.Data()

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

    # @TODO test_set_data_in_constructor
    # @TODO test_set_axes_in_constructor
    # @TODO test_set_calculated_in_constructor
    # @TODO test_setting_too_many_axes_fails
    # @TODO test_axes_values_dimensions_are_consistent_with_data