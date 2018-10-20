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
