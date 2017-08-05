"""Tests for data."""

import unittest
import numpy as np

from aspecd import data
from aspecd import axis


class TestData(unittest.TestCase):

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


class TestAxisSetupInConstructor(unittest.TestCase):

    def setUp(self):
        self.data = np.zeros(0)
        self.axes = [axis.Axis(), axis.Axis()]
        self.calculated = True

    def test_set_data_in_constructor(self):
        data_obj = data.Data(data=self.data)
        self.assertEqual(data_obj.data.tolist(), self.data.tolist())

    def test_set_axes_in_constructor(self):
        data_obj = data.Data(axes=self.axes)
        self.assertEqual(data_obj.axes, self.axes)

    def test_set_calculated_in_constructor(self):
        data_obj = data.Data(calculated=self.calculated)
        self.assertEqual(data_obj.calculated, self.calculated)

    def test_setting_too_many_axes_raises(self):
        axes = self.axes
        axes.append(axis.Axis())
        with self.assertRaises(data.AxesCountError):
            data.Data(self.data, axes)

    def test_axes_values_dimensions_are_consistent_with_empty_1D_data(self):
        data_obj = data.Data(self.data, self.axes)
        self.assertEqual(len(data_obj.axes[0].values), 0)

    def test_axes_values_dimensions_are_consistent_with_empty_2D_data(self):
        tmp_data = np.zeros([0, 0])
        data_obj = data.Data(tmp_data)
        print(data_obj.axes[0].values)
        self.assertEqual(len(data_obj.axes[0].values), 0)
        self.assertEqual(len(data_obj.axes[1].values), 0)

    def test_axes_values_dimensions_are_consistent_with_nonempty_1D_data(self):
        len_data = 5
        tmp_data = np.zeros(len_data)
        tmp_axes = [axis.Axis(), axis.Axis()]
        tmp_axes[0].values = np.zeros(len_data)
        data_obj = data.Data(tmp_data, tmp_axes)
        self.assertEqual(len(data_obj.axes[0].values), len_data)

    def test_axes_values_dimensions_are_consistent_with_nonempty_2D_data(self):
        len_data = [5, 3]
        tmp_data = np.zeros(len_data)
        tmp_axes = [axis.Axis(), axis.Axis(), axis.Axis()]
        tmp_axes[0].values = np.zeros(len_data[0])
        tmp_axes[1].values = np.zeros(len_data[1])
        data_obj = data.Data(tmp_data, tmp_axes)
        self.assertEqual(len(data_obj.axes[0].values), len_data[0])
        self.assertEqual(len(data_obj.axes[1].values), len_data[1])

    def test_wrong_axes_values_dimensions_with_nonempty_1D_data_raises(self):
        len_data = 5
        tmp_data = np.zeros(len_data)
        with self.assertRaises(data.AxesValuesInconsistentWithDataError):
            data.Data(tmp_data, self.axes)

    def test_wrong_axes_values_dimensions_with_nonempty_2D_data_raises(self):
        len_data = [5, 3]
        tmp_data = np.zeros(len_data)
        with self.assertRaises(data.AxesValuesInconsistentWithDataError):
            data.Data(tmp_data, self.axes)

    def test_set_wrong_axes_dimensions_with_nonempty_1D_data_raises(self):
        len_data = 5
        tmp_data = np.zeros(len_data)
        tmp_axis = axis.Axis()
        tmp_axis.values = np.zeros(2*len_data)
        tmp_axes = [tmp_axis, axis.Axis()]
        with self.assertRaises(data.AxesValuesInconsistentWithDataError):
            data.Data(tmp_data, tmp_axes)

    def test_set_wrong_axes_dimensions_with_nonempty_2D_data_raises(self):
        len_data = [5, 3]
        tmp_data = np.zeros(len_data)
        tmp_axis1 = axis.Axis()
        tmp_axis1.values = np.zeros(2*len_data[0])
        tmp_axis2 = axis.Axis()
        tmp_axis2.values = np.zeros(2*len_data[1])
        tmp_axes = [tmp_axis1, tmp_axis2, axis.Axis()]
        with self.assertRaises(data.AxesValuesInconsistentWithDataError):
            data.Data(tmp_data, tmp_axes)


if __name__ == '__main__':
    unittest.main()
