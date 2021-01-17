import unittest

import numpy as np

import aspecd.dataset
import aspecd.exceptions
import aspecd.model
import aspecd.utils


class TestModel(unittest.TestCase):
    def setUp(self):
        self.model = aspecd.model.Model()

    def test_instantiate_class(self):
        pass

    def test_has_name_property(self):
        self.assertTrue(hasattr(self.model, 'name'))

    def test_name_property_equals_full_class_name(self):
        full_class_name = aspecd.utils.full_class_name(self.model)
        self.assertEqual(self.model.name, full_class_name)

    def test_has_parameters_property(self):
        self.assertTrue(hasattr(self.model, 'parameters'))

    def test_has_variables_property(self):
        self.assertTrue(hasattr(self.model, 'variables'))

    def test_has_create_method(self):
        self.assertTrue(hasattr(self.model, 'create'))
        self.assertTrue(callable(self.model.create))

    def test_create_without_parameters_raises(self):
        with self.assertRaises(aspecd.exceptions.MissingParameterError):
            self.model.create()

    def test_create_without_variables_raises(self):
        self.model.parameters = [0]
        with self.assertRaises(aspecd.exceptions.MissingParameterError):
            self.model.create()

    def test_create_returns_calculated_dataset(self):
        self.model.parameters = [0]
        self.model.variables = [np.linspace(0, 1)]
        dataset = self.model.create()
        self.assertEqual(aspecd.dataset.CalculatedDataset, type(dataset))

    def test_create_sets_calculated_dataset_axis_values(self):
        self.model.parameters = [0]
        self.model.variables = [np.linspace(0, 1)]
        dataset = self.model.create()
        np.testing.assert_allclose(dataset.data.axes[0].values,
                                   self.model.variables[0])

    def test_create_with_2d_sets_calculated_dataset_axis_values(self):
        self.model.parameters = [0]
        self.model.variables = [np.linspace(0, 1), np.linspace(2, 3)]
        dataset = self.model.create()
        for index in range(len(self.model.variables)):
            np.testing.assert_allclose(dataset.data.axes[index].values,
                                       self.model.variables[index])

    def test_create_sets_calculated_dataset_calculation_type(self):
        self.model.parameters = [0]
        self.model.variables = [np.linspace(0, 1)]
        dataset = self.model.create()
        self.assertEqual(self.model.name, dataset.metadata.calculation.type)

    def test_create_sets_calculated_dataset_calculation_parameters(self):
        self.model.parameters = [0]
        self.model.variables = [np.linspace(0, 1)]
        dataset = self.model.create()
        self.assertEqual(self.model.parameters,
                         dataset.metadata.calculation.parameters)

    def test_has_from_dataset_method(self):
        self.assertTrue(hasattr(self.model, 'from_dataset'))
        self.assertTrue(callable(self.model.from_dataset))

    def test_from_dataset_without_dataset_raises(self):
        with self.assertRaises(aspecd.exceptions.MissingDatasetError):
            self.model.from_dataset()

    def test_from_dataset_sets_values(self):
        values = np.linspace(5, 50)
        dataset = aspecd.dataset.Dataset()
        dataset.data.data = np.linspace(0, 1)
        dataset.data.axes[0].values = values
        self.model.from_dataset(dataset=dataset)
        np.testing.assert_allclose(values, self.model.variables[0])

    def test_from_2d_dataset_sets_values(self):
        dataset = aspecd.dataset.Dataset()
        dataset.data.data = np.random.random([10, 5])
        self.model.from_dataset(dataset=dataset)
        for index in range(len(dataset.data.axes)):
            np.testing.assert_allclose(dataset.data.axes[index].values,
                                       self.model.variables[index])

    def test_from_dataset_applies_dataset_axes_to_calculated_dataset(self):
        dataset = aspecd.dataset.Dataset()
        dataset.data.data = np.linspace(0, 1)
        dataset.data.axes[0].quantity = 'foo'
        dataset.data.axes[1].quantity = 'bar'
        self.model.from_dataset(dataset=dataset)
        self.model.parameters = [0]
        calculated_dataset = self.model.create()
        for index in range(len(dataset.data.axes)):
            self.assertEqual(dataset.data.axes[index].quantity,
                             calculated_dataset.data.axes[index].quantity)
