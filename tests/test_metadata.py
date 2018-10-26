"""Tests for metadata."""

import unittest

from aspecd import metadata


class TestPhysicalQuantity(unittest.TestCase):
    def setUp(self):
        self.physical_quantity = metadata.PhysicalQuantity()

    def test_instantiate_class(self):
        pass

    def test_has_value_property(self):
        self.assertTrue(hasattr(self.physical_quantity, 'value'))

    def test_value_is_float(self):
        self.assertTrue(isinstance(self.physical_quantity.value, type(0.)))

    def test_set_wrong_type_for_value_fails(self):
        with self.assertRaises(TypeError):
            self.physical_quantity.value = 0

    def test_set_value(self):
        value = 5.
        self.physical_quantity.value = value
        self.assertEqual(self.physical_quantity.value, value)

    def test_has_unit_property(self):
        self.assertTrue(hasattr(self.physical_quantity, 'unit'))

    def test_has_dimension_property(self):
        self.assertTrue(hasattr(self.physical_quantity, 'dimension'))

    def test_has_name_property(self):
        self.assertTrue(hasattr(self.physical_quantity, 'name'))

    def test_instantiate_with_string(self):
        physical_quantity = metadata.PhysicalQuantity('5 m')
        self.assertEqual(physical_quantity.value, 5.)
        self.assertEqual(physical_quantity.unit, 'm')

    def test_instantiate_with_string_without_unit(self):
        physical_quantity = metadata.PhysicalQuantity('5')
        self.assertEqual(physical_quantity.value, 5.)
        self.assertFalse(physical_quantity.unit)

    def test_instantiate_with_value_unit(self):
        physical_quantity = metadata.PhysicalQuantity(value=5., unit='m')
        self.assertEqual(physical_quantity.value, 5.)
        self.assertEqual(physical_quantity.unit, 'm')

    def test_string_representation(self):
        string = '5.0 m'
        physical_quantity = metadata.PhysicalQuantity(string)
        self.assertEqual(str(physical_quantity), string)

    def test_string_representation_with_empty_value_unit(self):
        self.assertEqual(str(self.physical_quantity), '')

    def test_string_representation_when_value_is_zero(self):
        string = '0.0 m'
        physical_quantity = metadata.PhysicalQuantity(string)
        self.assertEqual(str(physical_quantity), string)

    def test_commensurable_with_same_unit(self):
        string = '5.0 m'
        physical_quantity1 = metadata.PhysicalQuantity(string)
        physical_quantity2 = metadata.PhysicalQuantity(string)
        self.assertTrue(physical_quantity1.commensurable(physical_quantity2))

    def test_commensurable_with_same_dimension(self):
        dimension = 'T'
        physical_quantity1 = metadata.PhysicalQuantity()
        physical_quantity1.dimension = dimension
        physical_quantity2 = metadata.PhysicalQuantity()
        physical_quantity2.dimension = dimension
        self.assertTrue(physical_quantity1.commensurable(physical_quantity2))

    def test_incommensurable_with_different_units(self):
        physical_quantity1 = metadata.PhysicalQuantity('5.0 m')
        physical_quantity2 = metadata.PhysicalQuantity('3 s')
        self.assertFalse(physical_quantity1.commensurable(physical_quantity2))

    def test_incommensurable_with_different_dimensions(self):
        physical_quantity1 = metadata.PhysicalQuantity()
        physical_quantity1.dimension = 'T'
        physical_quantity2 = metadata.PhysicalQuantity()
        physical_quantity2.dimension = 'L'
        self.assertFalse(physical_quantity1.commensurable(physical_quantity2))

    def test_incommensurable_if_has_no_unit(self):
        physical_quantity = metadata.PhysicalQuantity('5.0 m')
        self.assertFalse(physical_quantity.commensurable([]))

    def test_incommensurable_if_has_no_dimension(self):
        physical_quantity = metadata.PhysicalQuantity()
        physical_quantity.dimension = 'T'
        self.assertFalse(physical_quantity.commensurable([]))

    def test_set_value_and_unit_from_string(self):
        self.physical_quantity.from_string('5 m')
        self.assertEqual(self.physical_quantity.value, 5.0)
        self.assertEqual(self.physical_quantity.unit, 'm')

    def test_set_value_and_unit_from_empty_string(self):
        self.physical_quantity.from_string('')
        self.assertFalse(self.physical_quantity.value)
        self.assertFalse(self.physical_quantity.unit)

    def test_empty_string_clears_value_and_unit(self):
        self.physical_quantity.from_string('5 m')
        self.physical_quantity.from_string('')
        self.assertFalse(self.physical_quantity.value)
        self.assertFalse(self.physical_quantity.unit)


class TestTemperatureControl(unittest.TestCase):
    def setUp(self):
        self.temperature_control = metadata.TemperatureControl()

    def test_instantiate_class(self):
        pass

    def test_has_controlled_property(self):
        self.assertTrue(hasattr(self.temperature_control, 'controlled'))

    def test_has_temperature_property(self):
        self.assertTrue(hasattr(self.temperature_control, 'temperature'))

    def test_has_controller_property(self):
        self.assertTrue(hasattr(self.temperature_control, 'controller'))

    def test_instantiate_with_temperature_from_string(self):
        temperature_control = metadata.TemperatureControl(temperature='270 K')
        self.assertEqual(temperature_control.temperature.value, 270.)
        self.assertEqual(temperature_control.temperature.unit, 'K')

    def test_instantiate_with_temperature_sets_controlled(self):
        temperature_control = metadata.TemperatureControl(temperature='270 K')
        self.assertTrue(temperature_control.controlled)

    def test_setting_temperature_sets_controlled(self):
        self.temperature_control.temperature.from_string('270 K')
        self.assertTrue(self.temperature_control.controlled)

    def test_instantiate_properties_from_dict(self):
        dict_ = {"controlled": True, "temperature": "270 K",
                 "controller": "Oxford ITC 503S"}
        temperature_control = metadata.TemperatureControl(dict_)
        self.assertTrue(temperature_control.controlled)
        self.assertEqual(temperature_control.temperature.value, 270.)
        self.assertEqual(temperature_control.temperature.unit, 'K')
        self.assertEqual(temperature_control.controller, dict_["controller"])

    def test_instantiate_properties_from_dict_overwrites_controlled(self):
        dict_ = {"controlled": False, "temperature": "270 K",
                 "controller": "Oxford ITC 503S"}
        temperature_control = metadata.TemperatureControl(dict_)
        self.assertFalse(temperature_control.controlled)

    def test_set_properties_from_dict(self):
        dict_ = {"controlled": True, "temperature": "270 K",
                 "controller": "Oxford ITC 503S"}
        self.temperature_control.from_dict(dict_)
        self.assertTrue(self.temperature_control.controlled)
        self.assertEqual(self.temperature_control.temperature.value, 270.)
        self.assertEqual(self.temperature_control.temperature.unit, 'K')
        self.assertEqual(self.temperature_control.controller,
                         dict_["controller"])

    def test_set_properties_from_dict_with_missing_controlled_field(self):
        dict_ = {"temperature": "270 K", "controller": "Oxford ITC 503S"}
        self.temperature_control.from_dict(dict_)
        self.assertTrue(self.temperature_control.controlled)
        self.assertEqual(self.temperature_control.temperature.value, 270.)
        self.assertEqual(self.temperature_control.temperature.unit, 'K')
        self.assertEqual(self.temperature_control.controller,
                         dict_["controller"])

    def test_set_properties_from_dict_with_missing_temperature_field(self):
        dict_ = {"controller": "Oxford ITC 503S"}
        self.temperature_control.from_dict(dict_)
        self.assertEqual(self.temperature_control.controller,
                         dict_["controller"])
