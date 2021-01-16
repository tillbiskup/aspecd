import unittest

import numpy as np

import aspecd.dataset
import aspecd.exceptions
import aspecd.model


class TestModel(unittest.TestCase):
    def setUp(self):
        self.model = aspecd.model.Model()

    def test_instantiate_class(self):
        pass

    def test_has_parameters_property(self):
        self.assertTrue(hasattr(self.model, 'parameters'))

    def test_has_values_property(self):
        self.assertTrue(hasattr(self.model, 'values'))

    def test_has_create_method(self):
        self.assertTrue(hasattr(self.model, 'create'))
        self.assertTrue(callable(self.model.create))

    def test_create_without_parameters_raises(self):
        with self.assertRaises(aspecd.exceptions.MissingParameterError):
            self.model.create()

    def test_create_without_values_raises(self):
        self.model.parameters = [0]
        with self.assertRaises(aspecd.exceptions.MissingParameterError):
            self.model.create()

    def test_create_returns_calculated_dataset(self):
        self.model.parameters = [0]
        self.model.values = np.linspace(0, 1)
        dataset = self.model.create()
        self.assertEqual(aspecd.dataset.CalculatedDataset, type(dataset))

    def test_create_sets_calculated_dataset_axis_values(self):
        self.model.parameters = [0]
        self.model.values = np.linspace(0, 1)
        dataset = self.model.create()
        np.testing.assert_allclose(dataset.data.axes[0].values,
                                   self.model.values)

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
        np.testing.assert_allclose(values, self.model.values)
