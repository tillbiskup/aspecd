"""Tests for metadata."""

import collections
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

    def test_to_dict(self):
        self.physical_quantity.from_string('5 m')
        test_dict = {"value": 5.0, "unit": "m", "dimension": "", "name": ""}
        to_dict = self.physical_quantity.to_dict()
        self.assertDictEqual(test_dict, to_dict)


class TestMetadata(unittest.TestCase):
    def setUp(self):
        self.metadata = metadata.Metadata()

    def test_instantiate_class(self):
        pass

    def test_set_properties_from_dict(self):
        dict_ = {"purpose": "Kill time", "operator": "John Doe",
                 "labbook": "loi:42.1001/foo/bar"}
        for key in dict_:
            setattr(self.metadata, key, '')
        self.metadata.from_dict(dict_)
        for key in dict_:
            self.assertEqual(getattr(self.metadata, key), dict_[key])

    def test_set_properties_from_dict_case_insensitive(self):
        dict_ = {"Purpose": "Kill time", "Operator": "John Doe",
                 "Labbook": "loi:42.1001/foo/bar"}
        for key in dict_:
            setattr(self.metadata, key.lower(), '')
        self.metadata.from_dict(dict_)
        for key in dict_:
            self.assertEqual(getattr(self.metadata, key.lower()), dict_[key])

    def test_set_properties_from_dict_with_spaces_in_keys(self):
        dict_ = {"Purpose": "Kill time", "Operator": "John Doe",
                 "Lab book": "loi:42.1001/foo/bar"}
        for key in dict_:
            setattr(self.metadata, key.replace(' ', '_').lower(), '')
        self.metadata.from_dict(dict_)
        for key in dict_:
            self.assertEqual(dict_[key],
                             getattr(self.metadata,
                                     key.replace(' ', '_').lower()))

    def test_instantiate_properties_from_dict_with_physical_quantities(self):
        dict_ = {"purpose": "Kill time", "operator": "John Doe",
                 "labbook": "loi:42.1001/foo/bar", "length": "1.0 mm"}
        metadata_class = metadata.Metadata
        for key in dict_:
            setattr(metadata_class, key, '')
        metadata_class.length = metadata.PhysicalQuantity()
        metadata_ = metadata_class(dict_)
        for key in dict_:
            if isinstance(getattr(metadata_, key),
                          metadata.PhysicalQuantity):
                self.assertEqual(str(getattr(metadata_, key)), dict_[key])
            else:
                self.assertEqual(getattr(metadata_, key), dict_[key])

    def test_set_properties_from_dict_with_physical_quantities(self):
        dict_ = {"purpose": "Kill time", "operator": "John Doe",
                 "labbook": "loi:42.1001/foo/bar", "length": "1.0 mm"}
        for key in dict_:
            setattr(self.metadata, key, '')
        self.metadata.length = metadata.PhysicalQuantity()
        self.metadata.from_dict(dict_)
        for key in dict_:
            if isinstance(getattr(self.metadata, key),
                          metadata.PhysicalQuantity):
                self.assertEqual(str(getattr(self.metadata, key)), dict_[key])
            else:
                self.assertEqual(getattr(self.metadata, key), dict_[key])

    def test_to_dict(self):
        dict_ = {"purpose": "Kill time", "operator": "John Doe",
                 "labbook": "loi:42.1001/foo/bar"}
        for key in dict_:
            setattr(self.metadata, key, '')
        self.metadata.from_dict(dict_)
        to_dict = self.metadata.to_dict()
        self.assertDictEqual(dict_, to_dict)

    def test_to_dict_with_physical_quantities(self):
        dict_ = {"purpose": "Kill time", "operator": "John Doe",
                 "labbook": "loi:42.1001/foo/bar", "length": "1.0 mm"}
        for key in dict_:
            setattr(self.metadata, key, '')
        self.metadata.length = metadata.PhysicalQuantity()
        self.metadata.from_dict(dict_)
        test_dict = {"purpose": "Kill time", "operator": "John Doe",
                     "labbook": "loi:42.1001/foo/bar",
                     "length": {"value": 1.0, "unit": "mm", "dimension": "",
                                "name": ""}}
        to_dict = self.metadata.to_dict()
        self.assertDictEqual(test_dict, to_dict)

    def test_to_dict_preserves_order(self):
        arguments = ["purpose", "operator", "labbook"]
        for argument in arguments:
            setattr(self.metadata, argument, '')
        to_dict = self.metadata.to_dict()
        self.assertEqual(arguments, list(to_dict.keys()))


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


class TestMeasurement(unittest.TestCase):
    def setUp(self):
        self.measurement = metadata.Measurement()

    def test_instantiate_class(self):
        pass

    def test_instantiate_properties_from_dict(self):
        dict_ = {"purpose": "Kill time", "operator": "John Doe",
                 "labbook_entry": "loi:42.1001/foo/bar"}
        measurement = metadata.Measurement(dict_)
        for key in dict_:
            self.assertEqual(getattr(measurement, key), dict_[key])

    def test_set_properties_from_dict(self):
        dict_ = {"purpose": "Kill time", "operator": "John Doe",
                 "labbook_entry": "loi:42.1001/foo/bar"}
        self.measurement.from_dict(dict_)
        for key in dict_:
            self.assertEqual(getattr(self.measurement, key), dict_[key])

    def test_instantiate_start_end_from_dict(self):
        dict_ = {"start": {"date": "2017-01-02", "time": "11:00:00"},
                 "end": {"date": "2017-01-02", "time": "11:01:00"}}
        measurement = metadata.Measurement(dict_)
        fmt = "%Y%m%dT%H%M%S"
        self.assertEqual(measurement.start.strftime(fmt), "20170102T110000")
        self.assertEqual(measurement.end.strftime(fmt), "20170102T110100")

    def test_set_start_end_from_dict_with_strings(self):
        dict_ = {"start": "2017-01-02 11:00:00",
                 "end": "2017-01-02 11:01:00"}
        measurement = metadata.Measurement(dict_)
        fmt = "%Y%m%dT%H%M%S"
        self.assertEqual(measurement.start.strftime(fmt), "20170102T110000")
        self.assertEqual(measurement.end.strftime(fmt), "20170102T110100")

    def test_to_dict_preserves_order(self):
        arguments = ["start", "end", "purpose", "operator", "labbook_entry"]
        to_dict = self.measurement.to_dict()
        self.assertEqual(arguments, list(to_dict.keys()))


class TestSample(unittest.TestCase):
    def setUp(self):
        self.sample = metadata.Sample()

    def test_instantiate_class(self):
        pass

    def test_instantiate_properties_from_dict(self):
        dict_ = {"name": "Sample1", "id": 42, "loi": "loi:42.1001/foo/bar"}
        sample = metadata.Sample(dict_)
        for key in dict_:
            self.assertEqual(getattr(sample, key), dict_[key])

    def test_set_properties_from_dict(self):
        dict_ = {"name": "Sample1", "id": 42, "loi": "loi:42.1001/foo/bar"}
        self.sample.from_dict(dict_)
        for key in dict_:
            self.assertEqual(getattr(self.sample, key), dict_[key])


class TestCalculation(unittest.TestCase):
    def setUp(self):
        self.calculation = metadata.Calculation()

    def test_instantiate_class(self):
        pass

    def test_instantiate_properties_from_dict(self):
        dict_ = {"type": "foo", "parameters": {"foo": "bar"}}
        calculation = metadata.Calculation(dict_)
        for key in dict_:
            self.assertEqual(getattr(calculation, key), dict_[key])

    def test_set_properties_from_dict(self):
        dict_ = {"type": "foo", "parameters": {"foo": "bar"}}
        self.calculation.from_dict(dict_)
        for key in dict_:
            self.assertEqual(getattr(self.calculation, key), dict_[key])


class TestExperimentalDatasetMetadata(unittest.TestCase):
    def setUp(self):
        self.dataset_metadata = metadata.ExperimentalDatasetMetadata()

    def test_instantiate_class(self):
        pass

    def test_set_measurement_metadata_from_dict(self):
        dict_ = {"measurement": {"purpose": "Kill time",
                                 "operator": "John Doe",
                                 "labbook_entry": "loi:42.1001/foo/bar"}}
        self.dataset_metadata.from_dict(dict_)
        for key in dict_["measurement"]:
            self.assertEqual(dict_["measurement"][key],
                             getattr(self.dataset_metadata.measurement, key))

    def test_set_measurement_metadata_from_dict_case_insensitive(self):
        dict_ = {"Measurement": {"purpose": "Kill time",
                                 "operator": "John Doe",
                                 "labbook_entry": "loi:42.1001/foo/bar"}}
        self.dataset_metadata.from_dict(dict_)
        for key in dict_["Measurement"]:
            self.assertEqual(dict_["Measurement"][key],
                             getattr(self.dataset_metadata.measurement, key))

    def test_set_properties_from_dict_with_spaces_in_keys(self):
        dict_ = {"Temperature Control": {"controller": "Oxford ITC503S"}}
        self.dataset_metadata.from_dict(dict_)
        for key in dict_["Temperature Control"]:
            self.assertEqual(dict_["Temperature Control"][key],
                             getattr(
                                 self.dataset_metadata.temperature_control,
                                 key))

    def test_set_temperature_metadata_from_dict(self):
        dict_ = {"temperature_control": {"controlled": True,
                                         "temperature": "270 K",
                                         "controller": "Oxford ITC 503S"}}
        self.dataset_metadata.from_dict(dict_)
        self.assertTrue(self.dataset_metadata.temperature_control.controlled)
        self.assertEqual(
            self.dataset_metadata.temperature_control.temperature.value, 270.)
        self.assertEqual(
            self.dataset_metadata.temperature_control.temperature.unit, 'K')
        self.assertEqual(dict_["temperature_control"]["controller"],
                         self.dataset_metadata.temperature_control.controller)

    def test_set_sample_metadata_from_dict(self):
        dict_ = {"sample": {"name": "Sample1",
                            "id": 42,
                            "loi": "loi:42.1001/foo/bar"}}
        self.dataset_metadata.from_dict(dict_)
        for key in dict_["sample"]:
            self.assertEqual(dict_["sample"][key],
                             getattr(self.dataset_metadata.sample, key))

    def test_to_dict(self):
        dict_ = {"sample": {"name": "Sample1",
                            "id": 42,
                            "loi": "loi:42.1001/foo/bar"}}
        self.dataset_metadata.from_dict(dict_)
        to_dict = self.dataset_metadata.to_dict()
        self.assertDictEqual(dict_["sample"], to_dict["sample"])


class TestCalculatedDatasetMetadata(unittest.TestCase):
    def setUp(self):
        self.dataset_metadata = metadata.CalculatedDatasetMetadata()

    def test_instantiate_class(self):
        pass

    def test_has_calculation_property(self):
        self.assertTrue(hasattr(self.dataset_metadata, 'calculation'))

    def test_calculation_property_is_calculation(self):
        self.assertTrue(isinstance(self.dataset_metadata.calculation,
                                   metadata.Calculation))


class TestMetadataMapper(unittest.TestCase):
    def setUp(self):
        self.metadata_mapper = metadata.MetadataMapper()

    def test_instantiate_class(self):
        pass

    def test_has_method_rename_key(self):
        self.assertTrue(callable(self.metadata_mapper.rename_key))

    def test_rename_key(self):
        new_key = 'foo'
        old_key = 'bar'
        self.metadata_mapper.metadata[old_key] = 'bar'
        self.metadata_mapper.rename_key(old_key, new_key)
        self.assertTrue(new_key in self.metadata_mapper.metadata.keys())
        self.assertFalse(old_key in self.metadata_mapper.metadata.keys())

    def test_has_method_combine_items(self):
        self.assertTrue(callable(self.metadata_mapper.combine_items))

    def test_combine_items(self):
        old_keys = collections.OrderedDict()  # ordered dict for reproducibility
        old_keys['key1'] = 'bla'
        old_keys['key2'] = 'blub'
        new_key = 'new_key'
        for key in old_keys.keys():
            self.metadata_mapper.metadata[key] = old_keys[key]
        self.metadata_mapper.combine_items(old_keys, new_key)

        self.assertTrue(new_key in self.metadata_mapper.metadata.keys())
        for key in old_keys.keys():
            self.assertFalse(key in self.metadata_mapper.metadata.keys())
        self.assertEqual(self.metadata_mapper.metadata[new_key], 'blablub')

    def test_combine_items_joint_by_pattern(self):
        old_keys = collections.OrderedDict()  # ordered dict for reproducibility
        old_keys['key1'] = 'bla'
        old_keys['key2'] = 'blub'
        new_key = 'new_key'
        for key in old_keys.keys():
            self.metadata_mapper.metadata[key] = old_keys[key]
        self.metadata_mapper.combine_items(old_keys, new_key, pattern=' ')

        self.assertTrue(new_key in self.metadata_mapper.metadata.keys())
        for key in old_keys.keys():
            self.assertFalse(key in self.metadata_mapper.metadata.keys())
        self.assertEqual(self.metadata_mapper.metadata[new_key], 'bla blub')

    def test_has_method_keys_to_variable_names(self):
        self.assertTrue(callable(self.metadata_mapper.keys_to_variable_names))

    def test_keys_to_variable_names(self):
        dict_ = {'Temperature Control': {'Temperature': '278 K',
                                         'Transfer Line': 'Oxford'}}
        converted = {'temperature_control': {'temperature': '278 K',
                                             'transfer_line': 'Oxford'}}
        self.metadata_mapper.metadata = dict_
        self.metadata_mapper.keys_to_variable_names()
        self.assertDictEqual(self.metadata_mapper.metadata, converted)

    def test_has_attribute_mapping(self):
        self.assertTrue(hasattr(self.metadata_mapper, 'mappings'))

    def test_rename_key_via_mapping(self):
        self.metadata_mapper.metadata['old'] = 'foo'
        mapping = [['', 'rename_key', ['old', 'new']]]
        self.metadata_mapper.mappings = mapping
        self.metadata_mapper.map()
        self.assertTrue('new' in self.metadata_mapper.metadata.keys())
        self.assertFalse('old' in self.metadata_mapper.metadata.keys())

    def test_rename_key_on_second_level_via_mapping(self):
        self.metadata_mapper.metadata['test'] = {'old': 'foo'}
        mapping = [['test', 'rename_key', ['old', 'new']]]
        self.metadata_mapper.mappings = mapping
        self.metadata_mapper.map()
        self.assertTrue('new' in self.metadata_mapper.metadata['test'].keys())
        self.assertFalse('old' in self.metadata_mapper.metadata['test'].keys())

    def test_combine_items_via_mapping(self):
        old_keys = {'key1': 'bla', 'key2': 'blub'}
        new_key = 'new_key'
        mapping = [['', 'combine_items', [["key1", "key2"], "new_key"]]]
        self.metadata_mapper.mappings = mapping
        for key in old_keys.keys():
            self.metadata_mapper.metadata[key] = old_keys[key]
        self.metadata_mapper.map()

        self.assertTrue(new_key in self.metadata_mapper.metadata.keys())
        for key in old_keys.keys():
            self.assertFalse(key in self.metadata_mapper.metadata.keys())
        self.assertEqual(self.metadata_mapper.metadata[new_key], 'blablub')

    def test_combine_items_joint_by_pattern_via_mapping(self):
        old_keys = {'key1': 'bla', 'key2': 'blub'}
        new_key = 'new_key'
        mapping = [['', 'combine_items', [["key1", "key2"], "new_key", " "]]]
        self.metadata_mapper.mappings = mapping
        for key in old_keys.keys():
            self.metadata_mapper.metadata[key] = old_keys[key]
        self.metadata_mapper.map()

        self.assertTrue(new_key in self.metadata_mapper.metadata.keys())
        for key in old_keys.keys():
            self.assertFalse(key in self.metadata_mapper.metadata.keys())
        self.assertEqual(self.metadata_mapper.metadata[new_key], 'bla blub')

    def test_combine_items_on_second_level_via_mapping(self):
        old_keys = {'key1': 'bla', 'key2': 'blub'}
        new_key = 'new_key'
        mapping = [['test', 'combine_items', [["key1", "key2"], "new_key"]]]
        self.metadata_mapper.mappings = mapping
        self.metadata_mapper.metadata['test'] = dict()
        for key in old_keys.keys():
            self.metadata_mapper.metadata['test'][key] = old_keys[key]
        self.metadata_mapper.map()

        self.assertTrue(new_key in
                        self.metadata_mapper.metadata['test'].keys())
        for key in old_keys.keys():
            self.assertFalse(key in
                             self.metadata_mapper.metadata['test'].keys())
        self.assertEqual(self.metadata_mapper.metadata['test'][new_key],
                         'blablub')

    def test_has_method_copy_key(self):
        self.assertTrue(callable(self.metadata_mapper.copy_key))

    def test_copy_key(self):
        new_key = 'foo'
        old_key = 'bar'
        self.metadata_mapper.metadata[old_key] = 'bar'
        self.metadata_mapper.copy_key(old_key, new_key)
        self.assertTrue(new_key in self.metadata_mapper.metadata.keys())
        self.assertTrue(old_key in self.metadata_mapper.metadata.keys())

    def test_copy_key_via_mapping(self):
        self.metadata_mapper.metadata['old'] = 'foo'
        mapping = [['', 'copy_key', ['old', 'new']]]
        self.metadata_mapper.mappings = mapping
        self.metadata_mapper.map()
        self.assertTrue('new' in self.metadata_mapper.metadata.keys())
        self.assertTrue('old' in self.metadata_mapper.metadata.keys())

    def test_copy_key_on_second_level_via_mapping(self):
        self.metadata_mapper.metadata['test'] = {'old': 'foo'}
        mapping = [['test', 'copy_key', ['old', 'new']]]
        self.metadata_mapper.mappings = mapping
        self.metadata_mapper.map()
        self.assertTrue('new' in self.metadata_mapper.metadata['test'].keys())
        self.assertTrue('old' in self.metadata_mapper.metadata['test'].keys())

    def test_has_method_move_item(self):
        self.assertTrue(callable(self.metadata_mapper.move_item))

    def test_move_item(self):
        key = 'foobar'
        source = 'foo'
        target = 'bar'
        self.metadata_mapper.metadata = {'foo': {'foobar': 'baz'}, 'bar': {}}
        self.metadata_mapper.move_item(key, source, target)
        self.assertTrue(key in self.metadata_mapper.metadata[target].keys())
        self.assertFalse(key in self.metadata_mapper.metadata[source].keys())

    def test_move_item_via_mapping(self):
        key = 'foobar'
        source = 'foo'
        target = 'bar'
        self.metadata_mapper.metadata = {'foo': {'foobar': 'baz'}, 'bar': {}}
        mapping = [['', 'move_item', [key, source, target]]]
        self.metadata_mapper.mappings = mapping
        self.metadata_mapper.map()
        self.assertTrue(key in self.metadata_mapper.metadata[target].keys())
        self.assertFalse(key in self.metadata_mapper.metadata[source].keys())

    def test_move_item_on_second_level_via_mapping(self):
        key = 'foobar'
        source = 'foo'
        target = 'bar'
        self.metadata_mapper.metadata['test'] = {'foo': {'foobar': 'baz'},
                                                 'bar': {}}
        mapping = [['test', 'move_item', [key, source, target]]]
        self.metadata_mapper.mappings = mapping
        self.metadata_mapper.map()
        self.assertTrue(key in self.metadata_mapper.metadata['test'][
            target].keys())
        self.assertFalse(key in self.metadata_mapper.metadata['test'][
            source].keys())

    def test_move_item_via_mapping_creating_target_dict(self):
        key = 'foobar'
        source = 'foo'
        target = 'bar'
        self.metadata_mapper.metadata = {'foo': {'foobar': 'baz'}}
        mapping = [['', 'move_item', [key, source, target, True]]]
        self.metadata_mapper.mappings = mapping
        self.metadata_mapper.map()
        self.assertTrue(key in self.metadata_mapper.metadata[target].keys())
        self.assertFalse(key in self.metadata_mapper.metadata[source].keys())

    def test_move_item_via_mapping_to_nonexistent_dict_raises(self):
        key = 'foobar'
        source = 'foo'
        target = 'bar'
        self.metadata_mapper.metadata = {'foo': {'foobar': 'baz'}}
        mapping = [['', 'move_item', [key, source, target, False]]]
        self.metadata_mapper.mappings = mapping
        with self.assertRaises(KeyError):
            self.metadata_mapper.map()
