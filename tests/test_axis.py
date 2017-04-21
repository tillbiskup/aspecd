"""Tests for axis."""

import unittest
import numpy as np

from aspecd import axis


class TestAxis(unittest.TestCase):

    def setUp(self):
        self.axis = axis.Axis()

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


class TestAxisSettings(unittest.TestCase):

    def setUp(self):
        self.axis = axis.Axis()

    def test_set_values(self):
        self.axis.values = np.zeros(0)

    def test_set_wrong_type_for_values_fails(self):
        with self.assertRaises(axis.AxisValuesTypeError):
            self.axis.values = 0

    def test_set_multidimensional_values_fails(self):
        with self.assertRaises(axis.AxisValuesDimensionError):
            self.axis.values = np.zeros([0, 0])
