import copy
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

    def test_has_description_property(self):
        self.assertTrue(hasattr(self.model, 'description'))

    def test_description_property_describes_abstract_model(self):
        self.assertIn('abstract model', self.model.description.lower())

    def test_has_references_property(self):
        self.assertTrue(hasattr(self.model, 'references'))

    def test_description_references_is_list(self):
        self.assertTrue(isinstance(self.model.references, list))

    def test_has_to_dict_method(self):
        self.assertTrue(hasattr(self.model, 'to_dict'))
        self.assertTrue(callable(self.model.to_dict))

    def test_to_dict_does_not_contain_certain_keys(self):
        for key in ['name', 'description', 'references']:
            with self.subTest(key=key):
                self.assertNotIn(key, self.model.to_dict())

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

    def test_create_with_missing_parameter_raises(self):
        class MyModel(aspecd.model.Model):
            def _sanitise_parameters(self):
                if "coefficient" not in self.parameters:
                    raise aspecd.exceptions.MissingParameterError(
                        message="Parameter 'coefficient' missing")

        model = MyModel()
        model.parameters["foo"] = "bar"
        model.variables = [np.linspace(0, 1)]
        with self.assertRaisesRegex(aspecd.exceptions.MissingParameterError,
                                    "coefficient"):
            model.create()

    def test_create_returns_calculated_dataset(self):
        self.model.parameters = [0]
        self.model.variables = [np.linspace(0, 1)]
        dataset = self.model.create()
        self.assertIsInstance(dataset, aspecd.dataset.CalculatedDataset)

    def test_create_sets_calculated_dataset_axis_values(self):
        self.model.parameters = [0]
        self.model.variables = [np.linspace(0, 1)]
        dataset = self.model.create()
        np.testing.assert_allclose(dataset.data.axes[0].values,
                                   self.model.variables[0])

    def test_create_sets_last_axis_quantity_and_unit_to_defaults(self):
        self.model.parameters = [0]
        self.model.variables = [np.linspace(0, 1)]
        dataset = self.model.create()
        self.assertEqual('amplitude', dataset.data.axes[-1].quantity)
        self.assertEqual('a.u.', dataset.data.axes[-1].unit)

    def test_create_with_axes_sets_axes_quantities_and_units(self):
        axes = [
            {'quantity': 'foo0', 'unit': 'bar0'},
            {'quantity': 'foo1', 'unit': 'bar1'},
        ]
        self.model.parameters = [0]
        self.model.variables = [np.linspace(0, 1)]
        self.model.axes = axes
        dataset = self.model.create()
        for idx, axis in enumerate(dataset.data.axes):
            self.assertEqual(axes[idx]["quantity"], axis.quantity)
            self.assertEqual(axes[idx]["unit"], axis.unit)

    def test_create_with_axes_and_omitted_axis(self):
        axes = [
            None,
            {'quantity': 'foo1', 'unit': 'bar1'},
        ]
        self.model.parameters = [0]
        self.model.variables = [np.linspace(0, 1)]
        self.model.axes = axes
        dataset = self.model.create()
        for idx, axis in enumerate(dataset.data.axes):
            if axes[idx]:
                self.assertEqual(axes[idx]["quantity"], axis.quantity)
                self.assertEqual(axes[idx]["unit"], axis.unit)
            else:
                self.assertEqual("", axis.quantity)
                self.assertEqual("", axis.unit)

    def test_create_with_axes_unequal_to_number_of_dataset_axes_raises(self):
        axes = [{'quantity': 'foo0', 'unit': 'bar0'}]
        self.model.parameters = [0]
        self.model.variables = [np.linspace(0, 1)]
        self.model.axes = axes
        message = "Number of axes and dataset axes need to be identical"
        with self.assertRaisesRegex(IndexError, message):
            self.model.create()

    def test_create_sets_calculated_dataset_origdata_axis_values(self):
        self.model.parameters = [0]
        self.model.variables = [np.linspace(0, 1)]
        dataset = self.model.create()
        np.testing.assert_allclose(dataset._origdata.axes[0].values,
                                   self.model.variables[0])

    def test_create_with_2d_sets_calculated_dataset_axis_values(self):
        self.model.parameters = [0]
        self.model.variables = [np.linspace(0, 1), np.linspace(2, 3)]
        dataset = self.model.create()
        for index in range(len(self.model.variables)):
            np.testing.assert_allclose(dataset.data.axes[index].values,
                                       self.model.variables[index])

    def test_create_with_2d_sets_last_axis_measure_and_unit_to_defaults(self):
        self.model.parameters = [0]
        self.model.variables = [np.linspace(0, 1), np.linspace(2, 3)]
        dataset = self.model.create()
        self.assertEqual('amplitude', dataset.data.axes[-1].quantity)
        self.assertEqual('a.u.', dataset.data.axes[-1].unit)

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

    def test_create_with_label_sets_label_of_calculated_dataset(self):
        self.model.parameters = [0]
        self.model.variables = [np.linspace(0, 1)]
        self.model.label = 'foobar'
        dataset = self.model.create()
        self.assertEqual(self.model.label,
                         dataset.label)

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
        for index in range(len(dataset.data.axes)-1):
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

    def test_has_from_dict_method(self):
        self.assertTrue(hasattr(self.model, 'from_dict'))
        self.assertTrue(callable(self.model.from_dict))

    def test_from_dict_without_dict_raises(self):
        with self.assertRaises(aspecd.exceptions.MissingDictError):
            self.model.from_dict()

    def test_from_dict_sets_parameters(self):
        dict_ = {'parameters': {'foo': 42}, 'variables': [np.linspace(0, 1)]}
        self.model.from_dict(dict_)
        self.assertDictEqual(dict_["parameters"], self.model.parameters)

    def test_from_dict_sets_variables(self):
        dict_ = {'parameters': {'foo': 42}, 'variables': [np.linspace(0, 1)]}
        self.model.from_dict(dict_)
        self.assertEqual(dict_["variables"], self.model.variables)

    def test_from_dict_sets_only_valid_properties(self):
        dict_ = {'foo': 42}
        self.model.from_dict(dict_)
        self.assertFalse(hasattr(self.model, 'foo'))

    def test_has_evaluate_method(self):
        self.assertTrue(hasattr(self.model, 'evaluate'))
        self.assertTrue(callable(self.model.evaluate))

    def test_evaluate_returns_data(self):
        self.model.parameters = {'foo': 42}
        self.model.variables = [np.linspace(0, 1)]
        data = self.model.evaluate()
        self.assertListEqual(list(self.model.variables[0]), list(data))


class TestCompositeModel(unittest.TestCase):
    def setUp(self):
        self.model = aspecd.model.CompositeModel()

    def test_instantiate_class(self):
        pass

    def test_has_appropriate_description(self):
        self.assertIn('composite model consisting of several weighted models',
                      self.model.description.lower())

    def test_has_models_property(self):
        self.assertTrue(hasattr(self.model, 'models'))

    def test_has_weights_property(self):
        self.assertTrue(hasattr(self.model, 'weights'))

    def test_create_with_single_model_equivalent_to_single_model(self):
        variables = np.linspace(0, 5)
        models = ['Polynomial']
        parameters = {'coefficients': [1]}
        # Create single model
        single_model = aspecd.model.Polynomial()
        single_model.parameters = parameters
        single_model.variables = [variables]
        single_model_result = single_model.create()
        # Create composite model
        self.model.models = models
        self.model.parameters = [parameters]
        self.model.variables = [variables]
        composite_model_result = self.model.create()
        self.assertListEqual(list(single_model_result.data.data),
                             list(composite_model_result.data.data))

    def test_weighting_with_single_model(self):
        variables = np.linspace(0, 5)
        models = ['Polynomial']
        parameters = {'coefficients': [1]}
        weights = [2]
        # Create single model
        single_model = aspecd.model.Polynomial()
        single_model.parameters = parameters
        single_model.variables = [variables]
        single_model_result = single_model.create()
        # Create composite model
        self.model.models = models
        self.model.parameters = [parameters]
        self.model.weights = weights
        self.model.variables = [variables]
        composite_model_result = self.model.create()
        self.assertListEqual(list(single_model_result.data.data * weights[0]),
                             list(composite_model_result.data.data))

    def test_create_with_multiple_models_equivalent_to_sum_of_models(self):
        variables = [np.linspace(0, 5)]
        models = ['Sine', 'Exponential']
        parameters = [{'amplitude': 10}, {'rate': -4}]
        # Create individual models
        data = np.zeros(len(variables[0]))
        for idx, model_name in enumerate(models):
            model = aspecd.utils.object_from_class_name('aspecd.model.' +
                                                        model_name)
            for key in parameters[idx]:
                # noinspection PyUnresolvedReferences
                model.parameters[key] = parameters[idx][key]
            model.variables = variables
            # noinspection PyUnresolvedReferences
            model_result = model.create()
            data += model_result.data.data
        # Create composite model
        self.model.models = models
        self.model.parameters = parameters
        self.model.variables = variables
        composite_model_result = self.model.create()
        self.assertListEqual(list(data), list(composite_model_result.data.data))

    def test_create_with_operator(self):
        variables = [np.linspace(0, 5)]
        models = ['Sine', 'Exponential']
        parameters = [{'amplitude': 10}, {'rate': -4}]
        operators = ['*']
        # Create individual models
        data = np.zeros(len(variables[0]))
        for idx, model_name in enumerate(models):
            model = aspecd.utils.object_from_class_name('aspecd.model.' +
                                                        model_name)
            for key in parameters[idx]:
                # noinspection PyUnresolvedReferences
                model.parameters[key] = parameters[idx][key]
            model.variables = variables
            # noinspection PyUnresolvedReferences
            model_result = model.create()
            if not idx:
                data += model_result.data.data
            else:
                data *= model_result.data.data
        # Create composite model
        self.model.models = models
        self.model.parameters = parameters
        self.model.variables = variables
        self.model.operators = operators
        composite_model_result = self.model.create()
        self.assertListEqual(list(data), list(composite_model_result.data.data))

    def test_create_with_incompatible_no_of_models_and_parameters_raises(self):
        self.model.models = ['Sine', 'Exponential']
        self.model.parameters = [{'amplitude': 10}]
        self.model.variables = np.linspace(0, 5)
        with self.assertRaisesRegex(IndexError,
                                    'Models and parameters count differs'):
            self.model.create()

    def test_create_with_incompatible_no_of_weights(self):
        self.model.models = ['Sine', 'Exponential']
        self.model.parameters = [{'amplitude': 10}, {'rate': -4}]
        self.model.weights = [2]
        self.model.variables = np.linspace(0, 5)
        with self.assertRaisesRegex(IndexError,
                                    'Models and weights count differs'):
            self.model.create()

    def test_create_with_incompatible_no_of_operators(self):
        self.model.models = ['Sine', 'Exponential', 'Sine']
        self.model.parameters = \
            [{'amplitude': 10}, {'rate': -4}, {'frequency': 0.5}]
        self.model.operators = ['*']
        self.model.variables = np.linspace(0, 5)
        with self.assertRaisesRegex(IndexError,
                                    'Models and operators count differs'):
            self.model.create()


class TestFamilyOfCurves(unittest.TestCase):
    def setUp(self):
        self.model = aspecd.model.FamilyOfCurves()
        self.variables = np.linspace(0, 6*np.pi)

    def test_instantiate_class(self):
        pass

    def test_has_appropriate_description(self):
        self.assertIn('family of curves for a model with one parameter varied',
                      self.model.description.lower())

    def test_has_model_property(self):
        self.assertTrue(hasattr(self.model, 'model'))

    def test_has_vary_property(self):
        self.assertTrue(hasattr(self.model, 'vary'))

    def test_create_without_model_raises(self):
        with self.assertRaisesRegex(ValueError, 'Missing a model'):
            self.model.create()

    def test_create_model_with_scalar_varied_parameter_value(self):
        self.model.model = "Sine"
        self.model.vary["parameter"] = "amplitude"
        self.model.vary["values"] = 4
        self.model.variables = [self.variables]
        simple_model = aspecd.model.Sine()
        simple_model.variables = [self.variables]
        simple_model.parameters["amplitude"] = self.model.vary["values"]
        simple_dataset = simple_model.create()
        family_of_curves = self.model.create()
        self.assertListEqual(list(simple_dataset.data.data),
                             list(family_of_curves.data.data))

    def test_create_model_with_actually_varied_parameter_value(self):
        self.model.model = "Sine"
        self.model.vary["parameter"] = "amplitude"
        self.model.vary["values"] = [2, 4]
        self.model.variables = [self.variables]
        simple_model1 = aspecd.model.Sine()
        simple_model1.variables = [self.variables]
        simple_model1.parameters["amplitude"] = self.model.vary["values"][0]
        simple_dataset1 = simple_model1.create()
        simple_model2 = copy.deepcopy(simple_model1)
        simple_model2.parameters["amplitude"] = self.model.vary["values"][1]
        simple_dataset2 = simple_model2.create()
        family_of_curves = self.model.create()
        self.assertListEqual(list(simple_dataset1.data.data),
                             list(family_of_curves.data.data[:, 0]))
        self.assertListEqual(list(simple_dataset2.data.data),
                             list(family_of_curves.data.data[:, 1]))

    def test_create_model_sets_quantity_of_additional_axis(self):
        self.model.model = "Sine"
        self.model.vary["parameter"] = "amplitude"
        self.model.vary["values"] = [2, 4]
        self.model.variables = [self.variables]
        family_of_curves = self.model.create()
        self.assertEqual(self.model.vary["parameter"],
                         family_of_curves.data.axes[-2].quantity)

    def test_create_model_sets_axis_values(self):
        self.model.model = "Sine"
        self.model.vary["parameter"] = "amplitude"
        self.model.vary["values"] = [2, 4]
        self.model.variables = [self.variables]
        family_of_curves = self.model.create()
        self.assertListEqual(self.model.vary["values"],
                             list(family_of_curves.data.axes[-2].values))

    def test_create_model_sets_float_axis_values(self):
        self.model.model = "Sine"
        self.model.vary["parameter"] = "amplitude"
        self.model.vary["values"] = [2., 4.]
        self.model.variables = [self.variables]
        family_of_curves = self.model.create()
        self.assertListEqual(self.model.vary["values"],
                             list(family_of_curves.data.axes[-2].values))

    def test_create_from_dataset(self):
        values = np.linspace(5, 50)
        dataset = aspecd.dataset.Dataset()
        dataset.data.data = np.linspace(0, 1)
        dataset.data.axes[0].values = values
        self.model.from_dataset(dataset=dataset)
        self.model.model = "Sine"
        self.model.vary["parameter"] = "amplitude"
        self.model.vary["values"] = [2, 4]
        family_of_curves = self.model.create()
        self.assertEqual(self.model.vary["parameter"],
                         family_of_curves.data.axes[-2].quantity)

    def test_create_with_axes_unequal_to_number_of_dataset_axes_raises(self):
        axes = [
            {'quantity': 'foo0', 'unit': 'bar0'},
            {'quantity': 'foo0', 'unit': 'bar0'}
        ]
        values = np.linspace(5, 50)
        dataset = aspecd.dataset.Dataset()
        dataset.data.data = np.linspace(0, 1)
        dataset.data.axes[0].values = values
        self.model.from_dataset(dataset=dataset)
        self.model.model = "Sine"
        self.model.vary["parameter"] = "amplitude"
        self.model.vary["values"] = [2, 4]
        self.model.axes = axes
        message = "Number of axes and dataset axes need to be identical"
        with self.assertRaisesRegex(IndexError, message):
            self.model.create()


class TestZeros(unittest.TestCase):
    def setUp(self):
        self.model = aspecd.model.Zeros()
        self.dataset = aspecd.dataset.CalculatedDataset()
        self.dataset.data.data = np.random.randn(10)
        self.dataset3d = aspecd.dataset.CalculatedDataset()
        self.dataset3d.data.data = np.random.randn(10, 10, 10)

    def test_instantiate_class(self):
        pass

    def test_has_appropriate_description(self):
        self.assertIn('containing only zeros', self.model.description.lower())

    def test_create_without_coefficients_raises(self):
        with self.assertRaisesRegex(aspecd.exceptions.MissingParameterError,
                                    "shape"):
            self.model.create()

    def test_create_returns_zeros_of_given_shape(self):
        self.model.parameters["shape"] = 5
        dataset = self.model.create()
        self.assertListEqual(list(np.zeros(5)), list(dataset.data.data))

    def test_create_returns_zeros_of_given_3d_shape(self):
        self.model.parameters["shape"] = [5, 5, 5]
        dataset = self.model.create()
        self.assertFalse(all(dataset.data.data.flatten()))
        self.assertEqual((5, 5, 5), dataset.data.data.shape)

    def test_create_from_1d_dataset_returns_zeros_with_correct_shape(self):
        self.model.from_dataset(self.dataset)
        dataset = self.model.create()
        self.assertEqual(len(self.dataset.data.data), len(dataset.data.data))

    def test_create_from_3d_dataset_returns_zeros_with_correct_shape(self):
        self.model.from_dataset(self.dataset3d)
        dataset = self.model.create()
        self.assertEqual(len(self.dataset3d.data.data), len(dataset.data.data))

    def test_create_1d_with_range_sets_axis_range(self):
        self.model.parameters["shape"] = 5
        self.model.parameters["range"] = [35, 42]
        dataset = self.model.create()
        self.assertEqual(self.model.parameters["range"][0][0],
                         dataset.data.axes[0].values[0])
        self.assertEqual(self.model.parameters["range"][0][-1],
                         dataset.data.axes[0].values[-1])

    def test_create_2d_with_range_sets_axis_range(self):
        self.model.parameters["shape"] = [5, 5]
        self.model.parameters["range"] = [[35, 42], [17.5, 21]]
        dataset = self.model.create()
        self.assertEqual(self.model.parameters["range"][0][0],
                         dataset.data.axes[0].values[0])
        self.assertEqual(self.model.parameters["range"][0][-1],
                         dataset.data.axes[0].values[-1])
        self.assertEqual(self.model.parameters["range"][1][0],
                         dataset.data.axes[1].values[0])
        self.assertEqual(self.model.parameters["range"][1][-1],
                         dataset.data.axes[1].values[-1])

    def test_range_incompatible_to_shape_raises(self):
        self.model.parameters["shape"] = 5
        self.model.parameters["range"] = [[35, 42], [17.5, 21]]
        with self.assertRaisesRegex(IndexError,
                                    'Shape and range must be compatible'):
            self.model.create()


class TestOnes(unittest.TestCase):
    def setUp(self):
        self.model = aspecd.model.Ones()
        self.dataset = aspecd.dataset.CalculatedDataset()
        self.dataset.data.data = np.random.randn(10)
        self.dataset3d = aspecd.dataset.CalculatedDataset()
        self.dataset3d.data.data = np.random.randn(10, 10, 10)

    def test_instantiate_class(self):
        pass

    def test_has_appropriate_description(self):
        self.assertIn('containing only ones', self.model.description.lower())

    def test_create_without_coefficients_raises(self):
        with self.assertRaisesRegex(aspecd.exceptions.MissingParameterError,
                                    "shape"):
            self.model.create()

    def test_create_returns_ones_of_given_shape(self):
        self.model.parameters["shape"] = 5
        dataset = self.model.create()
        self.assertListEqual(list(np.ones(5)), list(dataset.data.data))

    def test_create_returns_ones_of_given_3d_shape(self):
        self.model.parameters["shape"] = [5, 5, 5]
        dataset = self.model.create()
        self.assertFalse(all(dataset.data.data.flatten()-1))
        self.assertEqual((5, 5, 5), dataset.data.data.shape)

    def test_create_from_1d_dataset_returns_zeros_with_correct_shape(self):
        self.model.from_dataset(self.dataset)
        dataset = self.model.create()
        self.assertEqual(len(self.dataset.data.data), len(dataset.data.data))

    def test_create_from_3d_dataset_returns_zeros_with_correct_shape(self):
        self.model.from_dataset(self.dataset3d)
        dataset = self.model.create()
        self.assertEqual(len(self.dataset3d.data.data), len(dataset.data.data))

    def test_create_1d_with_range_sets_axis_range(self):
        self.model.parameters["shape"] = 5
        self.model.parameters["range"] = [35, 42]
        dataset = self.model.create()
        self.assertEqual(self.model.parameters["range"][0][0],
                         dataset.data.axes[0].values[0])
        self.assertEqual(self.model.parameters["range"][0][-1],
                         dataset.data.axes[0].values[-1])

    def test_create_2d_with_range_sets_axis_range(self):
        self.model.parameters["shape"] = [5, 5]
        self.model.parameters["range"] = [[35, 42], [17.5, 21]]
        dataset = self.model.create()
        self.assertEqual(self.model.parameters["range"][0][0],
                         dataset.data.axes[0].values[0])
        self.assertEqual(self.model.parameters["range"][0][-1],
                         dataset.data.axes[0].values[-1])
        self.assertEqual(self.model.parameters["range"][1][0],
                         dataset.data.axes[1].values[0])
        self.assertEqual(self.model.parameters["range"][1][-1],
                         dataset.data.axes[1].values[-1])

    def test_range_incompatible_to_shape_raises(self):
        self.model.parameters["shape"] = 5
        self.model.parameters["range"] = [[35, 42], [17.5, 21]]
        with self.assertRaisesRegex(IndexError,
                                    'Shape and range must be compatible'):
            self.model.create()


class TestPolynomial(unittest.TestCase):
    def setUp(self):
        self.model = aspecd.model.Polynomial()

    def test_instantiate_class(self):
        pass

    def test_has_appropriate_description(self):
        self.assertIn('polynomial', self.model.description.lower())

    def test_create_returns_polynomial(self):
        self.model.parameters["coefficients"] = [0, 1]
        self.model.variables = [np.linspace(0, 5, 6)]
        dataset = self.model.create()
        self.assertEqual(0, dataset.data.data[0])
        self.assertEqual(5, dataset.data.data[-1])

    def test_create_without_coefficients_raises(self):
        self.model.variables = np.linspace(0, 5, 6)
        with self.assertRaisesRegex(aspecd.exceptions.MissingParameterError,
                                    "coefficient"):
            self.model.create()


def get_fwhm(dataset):
    xdata = dataset.data.axes[0].values
    ydata = dataset.data.data
    max_value = np.max(ydata)
    max_pos = np.argmax(ydata)
    halfmax_pos_left = np.argmin(abs(ydata[:max_pos] - (max_value/2)))
    halfmax_pos_right = \
        np.argmin(abs(ydata[max_pos:] - (max_value/2))) + max_pos
    fwhm = xdata[halfmax_pos_right] - xdata[halfmax_pos_left]
    return fwhm


class TestGaussian(unittest.TestCase):
    def setUp(self):
        self.model = aspecd.model.Gaussian()

    def test_instantiate_class(self):
        pass

    def test_has_appropriate_description(self):
        self.assertIn('generalised gaussian', self.model.description.lower())

    def test_amplitude_sets_maximum(self):
        amplitude = 0.5
        self.model.variables = [np.linspace(-5, 5, 2**10)]
        self.model.parameters["amplitude"] = amplitude
        dataset = self.model.create()
        self.assertAlmostEqual(amplitude, max(dataset.data.data), 4)

    def test_position_set_position(self):
        position = 0.5
        self.model.variables = [np.linspace(-5, 5, 1001)]
        self.model.parameters["position"] = position
        dataset = self.model.create()
        self.assertAlmostEqual(position, self.model.variables[0][np.argmax(
            dataset.data.data)], 4)

    def test_width_sets_width(self):
        width = 2
        self.model.variables = [np.linspace(-5, 5, 10001)]
        self.model.parameters["width"] = width
        dataset = self.model.create()
        fwhm_expected = 2*np.sqrt(2*np.log(2))*width
        self.assertAlmostEqual(fwhm_expected, get_fwhm(dataset), 3)

    def test_zero_width_returns_finite_output(self):
        width = 0
        self.model.variables = [np.linspace(-5, 5)]
        self.model.parameters["width"] = width
        with np.errstate(divide='raise'):
            dataset = self.model.create()
        self.assertTrue(np.all(np.isfinite(dataset.data.data)))


class TestNormalisedGaussian(unittest.TestCase):
    def setUp(self):
        self.model = aspecd.model.NormalisedGaussian()

    def test_instantiate_class(self):
        pass

    def test_has_appropriate_description(self):
        self.assertIn('normalised gaussian', self.model.description.lower())

    def test_amplitude_is_normalised(self):
        self.model.variables = [np.linspace(-5, 5, 2**10)]
        amplitude = 1 / (self.model.parameters["width"] * np.sqrt(2 * np.pi))
        dataset = self.model.create()
        self.assertAlmostEqual(amplitude, max(dataset.data.data), 4)

    def test_position_set_position(self):
        position = 0.5
        self.model.variables = [np.linspace(-5, 5, 1001)]
        self.model.parameters["position"] = position
        dataset = self.model.create()
        self.assertAlmostEqual(position, self.model.variables[0][np.argmax(
            dataset.data.data)], 4)

    def test_width_sets_width(self):
        width = 2
        self.model.variables = [np.linspace(-5, 5, 10001)]
        self.model.parameters["width"] = width
        dataset = self.model.create()
        fwhm_expected = 2*np.sqrt(2*np.log(2))*width
        self.assertAlmostEqual(fwhm_expected, get_fwhm(dataset), 3)

    def test_zero_width_returns_finite_output(self):
        width = 0
        self.model.variables = [np.linspace(-5, 5)]
        self.model.parameters["width"] = width
        with np.errstate(divide='raise'):
            dataset = self.model.create()
        self.assertTrue(np.all(np.isfinite(dataset.data.data)))


class TestLorentzian(unittest.TestCase):
    def setUp(self):
        self.model = aspecd.model.Lorentzian()

    def test_instantiate_class(self):
        pass

    def test_has_appropriate_description(self):
        self.assertIn('generalised lorentzian', self.model.description.lower())

    def test_amplitude_sets_maximum(self):
        amplitude = 0.5
        self.model.variables = [np.linspace(-5, 5, 2**10)]
        self.model.parameters["amplitude"] = amplitude
        dataset = self.model.create()
        self.assertAlmostEqual(amplitude, max(dataset.data.data), 4)

    def test_position_set_position(self):
        position = 0.5
        self.model.variables = [np.linspace(-5, 5, 1001)]
        self.model.parameters["position"] = position
        dataset = self.model.create()
        self.assertAlmostEqual(position, self.model.variables[0][np.argmax(
            dataset.data.data)], 4)

    def test_width_sets_width(self):
        width = 2
        self.model.variables = [np.linspace(-5, 5, 10001)]
        self.model.parameters["width"] = width
        dataset = self.model.create()
        fwhm_expected = 2*width
        self.assertAlmostEqual(fwhm_expected, get_fwhm(dataset), 3)

    def test_zero_width_returns_finite_output(self):
        width = 0
        self.model.variables = [np.linspace(-5, 5)]
        self.model.parameters["width"] = width
        with np.errstate(divide='raise'):
            dataset = self.model.create()
        self.assertTrue(np.all(np.isfinite(dataset.data.data)))


class TestNormalisedLorentzian(unittest.TestCase):
    def setUp(self):
        self.model = aspecd.model.NormalisedLorentzian()

    def test_instantiate_class(self):
        pass

    def test_has_appropriate_description(self):
        self.assertIn('normalised lorentzian', self.model.description.lower())

    def test_amplitude_is_normalised(self):
        self.model.variables = [np.linspace(-5, 5, 2**10)]
        amplitude = 1 / (self.model.parameters["width"] * np.pi)
        dataset = self.model.create()
        self.assertAlmostEqual(amplitude, max(dataset.data.data), 4)

    def test_position_set_position(self):
        position = 0.5
        self.model.variables = [np.linspace(-5, 5, 1001)]
        self.model.parameters["position"] = position
        dataset = self.model.create()
        self.assertAlmostEqual(position, self.model.variables[0][np.argmax(
            dataset.data.data)], 4)

    def test_width_sets_width(self):
        width = 2
        self.model.variables = [np.linspace(-5, 5, 10001)]
        self.model.parameters["width"] = width
        dataset = self.model.create()
        fwhm_expected = 2*width
        self.assertAlmostEqual(fwhm_expected, get_fwhm(dataset), 3)

    def test_zero_width_returns_finite_output(self):
        width = 0
        self.model.variables = [np.linspace(-5, 5)]
        self.model.parameters["width"] = width
        with np.errstate(divide='raise'):
            dataset = self.model.create()
        self.assertTrue(np.all(np.isfinite(dataset.data.data)))


class TestSine(unittest.TestCase):
    def setUp(self):
        self.model = aspecd.model.Sine()

    def test_instantiate_class(self):
        pass

    def test_has_appropriate_description(self):
        self.assertIn('sine', self.model.description.lower())

    def test_roots_at_correct_place(self):
        self.model.variables = [np.linspace(0, 2*np.pi, 1001)]
        dataset = self.model.create()
        for index in [0, 500, 1000]:
            self.assertAlmostEqual(0, dataset.data.data[index])
        self.assertTrue(np.all(dataset.data.data[1:499]))
        self.assertTrue(np.all(dataset.data.data[501:1000]))

    def test_amplitude_sets_amplitude(self):
        amplitude = 42.
        self.model.variables = [np.linspace(0, 2*np.pi, 1001)]
        self.model.parameters["amplitude"] = amplitude
        dataset = self.model.create()
        self.assertAlmostEqual(amplitude, max(dataset.data.data))

    def test_frequency_sets_frequency(self):
        self.model.variables = [np.linspace(0, 2*np.pi, 1001)]
        self.model.parameters["frequency"] = 2
        dataset = self.model.create()
        for index in [0, 250, 500, 750, 1000]:
            self.assertAlmostEqual(0, dataset.data.data[index])

    def test_phase_shifts_roots(self):
        self.model.variables = [np.linspace(0, 2*np.pi, 1001)]
        self.model.parameters["phase"] = 0.5 * np.pi
        dataset = self.model.create()
        for index in [250, 750]:
            self.assertAlmostEqual(0, dataset.data.data[index])


class TestExponential(unittest.TestCase):
    def setUp(self):
        self.model = aspecd.model.Exponential()

    def test_instantiate_class(self):
        pass

    def test_has_appropriate_description(self):
        self.assertIn('exponential', self.model.description.lower())

    def test_only_positive_values(self):
        self.model.variables = [np.linspace(-1, 2, 101)]
        dataset = self.model.create()
        self.assertTrue(np.all(dataset.data.data > 0))

    def test_prefactor_sets_intercept(self):
        prefactor = 42.
        self.model.variables = [np.linspace(0, 2, 101)]
        self.model.parameters["prefactor"] = prefactor
        dataset = self.model.create()
        self.assertAlmostEqual(prefactor, dataset.data.data[0])

    def test_rate_sets_rate(self):
        rate = 4.2
        self.model.variables = [np.linspace(0, 2, 101)]
        self.model.parameters["rate"] = rate
        dataset = self.model.create()
        self.assertAlmostEqual(np.exp(rate * self.model.variables[0][-1]),
                               dataset.data.data[-1])
