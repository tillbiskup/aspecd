"""Tests for utils."""

import collections
import copy
import datetime
import os
import shutil
import unittest
from unittest.mock import patch

import numpy as np
import oyaml as yaml

import aspecd.exceptions
import aspecd.utils
from aspecd import utils, dataset


class TestFullClassName(unittest.TestCase):

    def test_full_class_name(self):
        dataset_ = aspecd.dataset.Dataset()
        class_name = utils.full_class_name(dataset_)
        self.assertEqual(class_name, 'aspecd.dataset.Dataset')


class TestObjectFromClassName(unittest.TestCase):

    def test_object_from_class_name(self):
        class_name = 'aspecd.dataset.Dataset'
        object_ = utils.object_from_class_name(class_name)
        self.assertTrue(isinstance(object_, dataset.Dataset))


class TestToDictMixin(unittest.TestCase):

    def setUp(self):
        class MixedIn(utils.ToDictMixin):
            pass

        self.mixed_in = MixedIn()

    @staticmethod
    def set_properties_from_dict(obj=None, dict_=None):
        dict_ = copy.deepcopy(dict_)
        for key in dict_:
            setattr(obj, key, dict_[key])

    def test_instantiate_class(self):
        pass

    def test_string_property(self):
        orig_dict = {"foo": "bar"}
        self.set_properties_from_dict(obj=self.mixed_in, dict_=orig_dict)
        obj_dict = self.mixed_in.to_dict()
        self.assertDictEqual(orig_dict, obj_dict)

    def test_only_public_properties(self):
        orig_dict = {"foo": "bar"}
        self.set_properties_from_dict(obj=self.mixed_in, dict_=orig_dict)
        self.mixed_in._protected_property = None
        obj_dict = self.mixed_in.to_dict()
        self.assertDictEqual(orig_dict, obj_dict)

    def test_dict_property(self):
        orig_dict = {"foo": {"bar": "baz"}}
        self.set_properties_from_dict(obj=self.mixed_in, dict_=orig_dict)
        obj_dict = self.mixed_in.to_dict()
        self.assertDictEqual(orig_dict, obj_dict)

    def test_cascaded_dict_property(self):
        orig_dict = {"foo": {"bar": {"baz": "baf"}}}
        self.set_properties_from_dict(obj=self.mixed_in, dict_=orig_dict)
        obj_dict = self.mixed_in.to_dict()
        self.assertDictEqual(orig_dict, obj_dict)

    def test_ordered_dict_property(self):
        orig_dict = {"foo": collections.OrderedDict({"bar": "baz"})}
        self.set_properties_from_dict(obj=self.mixed_in, dict_=orig_dict)
        obj_dict = self.mixed_in.to_dict()
        self.assertDictEqual(orig_dict, obj_dict)

    def test_mixed_in_object_property(self):
        orig_dict = {"foo": "bar"}
        mixed_in = utils.ToDictMixin()
        self.set_properties_from_dict(obj=mixed_in, dict_=orig_dict)
        self.mixed_in.object = mixed_in
        full_dict = {"object": {"foo": "bar"}}
        obj_dict = self.mixed_in.to_dict()
        self.assertDictEqual(full_dict, obj_dict)

    def test_generic_object_property(self):
        orig_dict = {"foo": "bar"}

        class DummyClass:
            pass

        obj = DummyClass()
        self.set_properties_from_dict(obj=obj, dict_=orig_dict)
        self.mixed_in.object = obj
        full_dict = {"object": {"foo": "bar"}}
        obj_dict = self.mixed_in.to_dict()
        self.assertDictEqual(full_dict, obj_dict)

    def test_list_of_dicts_property(self):
        orig_dict = {"foo": [{"foo": "bar"}, {"bar": "baz"}]}
        self.set_properties_from_dict(obj=self.mixed_in, dict_=orig_dict)
        obj_dict = self.mixed_in.to_dict()
        self.assertDictEqual(orig_dict, obj_dict)

    def test_list_of_dicts_containing_dicts_property(self):
        orig_dict = {"foo": [{"foo": {"foobar": "bar"}}, {"bar": "baz"}]}
        self.set_properties_from_dict(obj=self.mixed_in, dict_=orig_dict)
        obj_dict = self.mixed_in.to_dict()
        self.assertDictEqual(orig_dict, obj_dict)

    def test_list_of_objects_property(self):
        toobj_dict = {"foo": "bar"}
        obj1 = utils.ToDictMixin()
        obj2 = utils.ToDictMixin()
        self.set_properties_from_dict(obj=obj1, dict_=toobj_dict)
        self.set_properties_from_dict(obj=obj2, dict_=toobj_dict)
        self.mixed_in.objects = [obj1, obj2]
        orig_dict = {"objects": [toobj_dict, toobj_dict]}
        obj_dict = self.mixed_in.to_dict()
        self.assertDictEqual(orig_dict, obj_dict)

    def test_list_of_dicts_containing_objects_property(self):
        toobj_dict = {"foo": "bar"}
        obj1 = utils.ToDictMixin()
        obj2 = utils.ToDictMixin()
        self.set_properties_from_dict(obj=obj1, dict_=toobj_dict)
        self.set_properties_from_dict(obj=obj2, dict_=toobj_dict)
        orig_dict = {"foo": [{"foo": toobj_dict}, {"bar": toobj_dict}]}
        self.set_properties_from_dict(obj=self.mixed_in, dict_=orig_dict)
        # noinspection PyUnresolvedReferences
        self.mixed_in.foo[0]["foo"] = obj1
        # noinspection PyUnresolvedReferences
        self.mixed_in.foo[1]["bar"] = obj2
        obj_dict = self.mixed_in.to_dict()
        self.assertEqual(orig_dict["foo"], obj_dict["foo"])

    def test_datetime_property(self):
        date = datetime.datetime.now()
        toobj_dict = {"date": date}
        self.set_properties_from_dict(obj=self.mixed_in, dict_=toobj_dict)
        orig_dict = {"date": str(date)}
        obj_dict = self.mixed_in.to_dict()
        self.assertDictEqual(orig_dict, obj_dict)

    def test_date_property(self):
        date = datetime.date.today()
        toobj_dict = {"date": date}
        self.set_properties_from_dict(obj=self.mixed_in, dict_=toobj_dict)
        orig_dict = {"date": str(date)}
        obj_dict = self.mixed_in.to_dict()
        self.assertDictEqual(orig_dict, obj_dict)

    def test_time_property(self):
        date = datetime.time(12, 10, 30)
        toobj_dict = {"date": date}
        self.set_properties_from_dict(obj=self.mixed_in, dict_=toobj_dict)
        orig_dict = {"date": str(date)}
        obj_dict = self.mixed_in.to_dict()
        self.assertDictEqual(orig_dict, obj_dict)

    def test_has_odict_attribute(self):
        self.assertTrue(hasattr(self.mixed_in, '__odict__'))

    def test_odict_attribute_is_ordered_dict(self):
        self.assertTrue(isinstance(self.mixed_in.__odict__,
                                   collections.OrderedDict))

    def test_odict_preserves_argument_definition_order(self):
        arguments = ["purpose", "operator", "labbook"]

        class Test(utils.ToDictMixin):
            def __init__(self):
                super().__init__()
                self.purpose = ''
                self.operator = ''
                self.labbook = ''

        obj = Test()
        self.assertEqual(arguments, list(obj.to_dict().keys()))

    def test_with_properties_to_exclude(self):
        class Test(utils.ToDictMixin):
            def __init__(self):
                super().__init__()
                self.purpose = ''
                self.operator = ''
                self._exclude_from_to_dict = ['operator']

        obj = Test()
        self.assertEqual(['purpose'], list(obj.to_dict().keys()))

    def test_with_property_to_include(self):
        class Test(utils.ToDictMixin):
            def __init__(self):
                super().__init__()
                self.purpose = ''
                self._foo = None
                self._include_in_to_dict = ['_foo']

        obj = Test()
        self.assertEqual(['purpose', '_foo'], list(obj.to_dict().keys()))

    def test_with_properties_to_include(self):
        class Test(utils.ToDictMixin):
            def __init__(self):
                super().__init__()
                self.purpose = ''
                self._foo = None
                self._bar = None
                self._include_in_to_dict = ['_foo', '_bar']

        obj = Test()
        self.assertEqual(['purpose', '_foo', '_bar'],
                         list(obj.to_dict().keys()))

    def test_remove_empty_properties_from_dict(self):
        class Test(utils.ToDictMixin):
            def __init__(self):
                super().__init__()
                self.purpose = ''
                self.comment = 'Lorem ipsum'

        obj = Test()
        self.assertEqual(['comment'],
                         list(obj.to_dict(remove_empty=True).keys()))


class TestGetAspecdVersion(unittest.TestCase):

    def test_version_not_empty(self):
        version = utils.get_aspecd_version()
        self.assertTrue(version)


class TestGetVersion(unittest.TestCase):

    def test_version_not_empty(self):
        version = utils.package_version("aspecd")
        self.assertTrue(version)

    def test_version_correct_for_aspecd_package(self):
        version = utils.package_version("aspecd")
        self.assertEqual(utils.get_aspecd_version(), version)


class TestPackageName(unittest.TestCase):

    def test_package_name_returns_correct_package(self):
        package_name = utils.package_name()
        self.assertEqual(package_name, 'aspecd')

    def test_package_name_with_object_returns_correct_package(self):
        package_name = utils.package_name(unittest.TestCase())
        self.assertEqual(package_name, 'unittest')


class TestConfigDir(unittest.TestCase):

    def test_config_dir_not_empty(self):
        config_dir = utils.config_dir()
        self.assertTrue(config_dir)


class TestYaml(unittest.TestCase):
    def setUp(self):
        self.yaml = utils.Yaml()
        self.filename = 'test.yaml'
        self.dict = {'foo': 'bar'}

    def tearDown(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def test_instantiate_class(self):
        pass

    def test_has_dict_property(self):
        self.assertTrue(hasattr(self.yaml, 'dict'))

    def test_dict_property_is_ordered_dict(self):
        self.assertTrue(isinstance(self.yaml.dict, collections.OrderedDict))

    def test_has_read_from_method(self):
        self.assertTrue(hasattr(self.yaml, 'read_from'))
        self.assertTrue(callable(self.yaml.read_from))

    def test_read_from_without_filename_raises(self):
        with self.assertRaises(aspecd.exceptions.MissingFilenameError):
            self.yaml.read_from()

    def test_has_write_to_method(self):
        self.assertTrue(hasattr(self.yaml, 'write_to'))
        self.assertTrue(callable(self.yaml.write_to))

    def test_write_to_without_filename_raises(self):
        with self.assertRaises(aspecd.exceptions.MissingFilenameError):
            self.yaml.write_to()

    def test_read_from_reads_file(self):
        with open(self.filename, 'w') as file:
            yaml.dump(self.dict, file)
        self.yaml.read_from(self.filename)
        self.assertEqual(self.dict, self.yaml.dict)

    def test_writes_to_writes_file(self):
        self.yaml.dict = self.dict
        self.yaml.write_to(self.filename)
        with open(self.filename, 'r') as file:
            contents = yaml.load(file, Loader=yaml.SafeLoader)
        self.assertEqual(contents, self.yaml.dict)

    def test_has_serialise_numpy_array_method(self):
        self.assertTrue(hasattr(self.yaml, 'serialise_numpy_arrays'))
        self.assertTrue(callable(self.yaml.serialise_numpy_arrays))

    def test_has_serialize_numpy_array_method(self):
        self.assertTrue(hasattr(self.yaml, 'serialize_numpy_arrays'))
        self.assertTrue(callable(self.yaml.serialize_numpy_arrays))

    def test_serialise_numpy_array_creates_dict(self):
        array = np.asarray([[0., 1., 2.], [1., 2., 3.]])
        resulting_dict = {'foo': {'type': 'numpy.ndarray',
                                  'dtype': str(array.dtype),
                                  'array': array.tolist()}}
        self.yaml.dict = {'foo': array}
        self.yaml.serialise_numpy_arrays()
        self.assertDictEqual(resulting_dict, self.yaml.dict)

    def test_serialise_numpy_array_creates_list(self):
        array = np.asarray([[0., 1., 2.], [1., 2., 3.]])
        resulting_dict = {'foo': array.tolist()}
        self.yaml.dict = {'foo': array}
        self.yaml.numpy_array_to_list = True
        self.yaml.serialise_numpy_arrays()
        self.assertDictEqual(resulting_dict, self.yaml.dict)

    def test_serialise_large_numpy_array_creates_dict_and_file(self):
        array = np.random.rand(self.yaml.numpy_array_size_threshold + 1)
        resulting_dict = {'foo': {'type': 'numpy.ndarray',
                                  'dtype': str(array.dtype),
                                  'file': 'foo'}}
        self.yaml.dict = {'foo': array}
        self.yaml.serialise_numpy_arrays()
        # Necessary as the true filename will be generated
        filename = self.yaml.dict["foo"]["file"]
        resulting_dict["foo"]["file"] = filename
        self.assertDictEqual(resulting_dict, self.yaml.dict)
        self.assertTrue(os.path.exists(filename))
        os.remove(filename)

    def test_serialise_large_numpy_array_sets_filenames(self):
        array = np.random.rand(self.yaml.numpy_array_size_threshold + 1)
        self.yaml.dict = {'foo': array}
        self.yaml.serialise_numpy_arrays()
        # Necessary as the true filename will be generated
        filename = self.yaml.dict["foo"]["file"]
        self.assertTrue(self.yaml.binary_files)
        os.remove(filename)

    def test_serialise_large_non_c_contiguous_numpy_array(self):
        array = np.random.random([6, 8])
        self.yaml.numpy_array_size_threshold = 5
        self.yaml.dict = {'foo': array.T}
        self.yaml.serialise_numpy_arrays()
        # Necessary as the true filename will be generated
        filename = self.yaml.dict["foo"]["file"]
        self.assertTrue(self.yaml.binary_files)
        os.remove(filename)

    def test_serialise_large_numpy_array_with_binary_directory(self):
        array = np.random.rand(self.yaml.numpy_array_size_threshold + 1)
        resulting_dict = {'foo': {'type': 'numpy.ndarray',
                                  'dtype': str(array.dtype),
                                  'file': 'foo'}}
        self.yaml.dict = {'foo': array}
        self.yaml.binary_directory = 'bar'
        self.yaml.serialise_numpy_arrays()
        # Necessary as the true filename will be generated
        filename = self.yaml.dict["foo"]["file"]
        resulting_dict["foo"]["file"] = filename
        self.assertDictEqual(resulting_dict, self.yaml.dict)
        self.assertTrue(os.path.exists(os.path.join('bar', filename)))
        os.remove(os.path.join('bar', filename))
        os.rmdir('bar')

    def test_serialise_numpy_array_in_hierarchical_dict_creates_dict(self):
        array = np.asarray([[0., 1., 2.], [1., 2., 3.]])
        array_dict = {'foo': {'type': 'numpy.ndarray',
                              'dtype': str(array.dtype),
                              'array': array.tolist()}}
        resulting_dict = {'bar': array_dict}
        self.yaml.dict = {'bar': {'foo': array}}
        self.yaml.serialise_numpy_arrays()
        self.assertDictEqual(resulting_dict, self.yaml.dict)

    def test_serialise_numpy_array_in_list_in_dict_creates_dict(self):
        array = np.asarray([[0., 1., 2.], [1., 2., 3.]])
        array_dict = {'foo': {'type': 'numpy.ndarray',
                              'dtype': str(array.dtype),
                              'array': array.tolist()}}
        resulting_dict = {'bar': [array_dict]}
        self.yaml.dict = {'bar': [{'foo': array}]}
        self.yaml.serialise_numpy_arrays()
        self.assertDictEqual(resulting_dict, self.yaml.dict)

    def test_serialise_numpy_array_in_ordered_dict_creates_dict(self):
        array = np.asarray([[0., 1., 2.], [1., 2., 3.]])
        array_dict = {'foo': {'type': 'numpy.ndarray',
                              'dtype': str(array.dtype),
                              'array': array.tolist()}}
        resulting_dict = {'foobar':
                          collections.OrderedDict({'bar': array_dict})}
        self.yaml.dict = {'foobar':
                          collections.OrderedDict({'bar': {'foo': array}})}
        self.yaml.serialise_numpy_arrays()
        self.assertDictEqual(resulting_dict, self.yaml.dict)

    def test_has_deserialise_numpy_array_method(self):
        self.assertTrue(hasattr(self.yaml, 'deserialise_numpy_arrays'))
        self.assertTrue(callable(self.yaml.deserialise_numpy_arrays))

    def test_has_deserialize_numpy_array_method(self):
        self.assertTrue(hasattr(self.yaml, 'deserialize_numpy_arrays'))
        self.assertTrue(callable(self.yaml.deserialize_numpy_arrays))

    def test_deserialise_numpy_array_creates_numpy_array(self):
        array = np.asarray([[0., 1., 2.], [1., 2., 3.]])
        resulting_dict = {'foo': array}
        self.yaml.dict = {'foo': {'type': 'numpy.ndarray',
                                  'dtype': str(array.dtype),
                                  'array': array.tolist()}}
        self.yaml.deserialise_numpy_arrays()
        np.testing.assert_allclose(resulting_dict["foo"], self.yaml.dict["foo"])

    def test_deserialise_large_numpy_array_creates_numpy_array(self):
        array = np.random.rand(self.yaml.numpy_array_size_threshold + 1)
        resulting_dict = {'foo': array}
        self.yaml.dict = {'foo': {'type': 'numpy.ndarray',
                                  'dtype': str(array.dtype),
                                  'file': 'foo.npy'}}
        np.save('foo', array, allow_pickle=False)
        self.yaml.deserialise_numpy_arrays()
        np.testing.assert_allclose(resulting_dict["foo"], self.yaml.dict["foo"])
        os.remove('foo.npy')

    def test_deserialise_large_numpy_array_with_binary_directory(self):
        array = np.random.rand(self.yaml.numpy_array_size_threshold + 1)
        resulting_dict = {'foo': array}
        self.yaml.dict = {'foo': {'type': 'numpy.ndarray',
                                  'dtype': str(array.dtype),
                                  'file': 'foo.npy'}}
        self.yaml.binary_directory = 'bar'
        os.mkdir('bar')
        np.save('bar/foo.npy', array, allow_pickle=False)
        self.yaml.deserialise_numpy_arrays()
        np.testing.assert_allclose(resulting_dict["foo"], self.yaml.dict["foo"])
        os.remove('bar/foo.npy')
        os.rmdir('bar')

    def test_deserialise_numpy_array_in_hierarchical_dict_creates_numpy_array(
            self):
        array = np.asarray([[0., 1., 2.], [1., 2., 3.]])
        resulting_dict = {'bar': {'foo': array}}
        self.yaml.dict = {'bar': {'foo': {'type': 'numpy.ndarray',
                                          'dtype': str(array.dtype),
                                          'array': array.tolist()}}}
        self.yaml.deserialise_numpy_arrays()
        np.testing.assert_allclose(resulting_dict["bar"]["foo"],
                                   self.yaml.dict["bar"]["foo"])

    def test_deserialise_numpy_array_in_list_in_dict_creates_numpy_array(
            self):
        array = np.asarray([[0., 1., 2.], [1., 2., 3.]])
        resulting_dict = {'bar': [{'foo': array}]}
        self.yaml.dict = {'bar': [{'foo': {'type': 'numpy.ndarray',
                                           'dtype': str(array.dtype),
                                           'array': array.tolist()}}]}
        self.yaml.deserialise_numpy_arrays()
        np.testing.assert_allclose(resulting_dict["bar"][0]["foo"],
                                   self.yaml.dict["bar"][0]["foo"])

    def test_deserialise_numpy_array_in_ordered_dict_creates_numpy_array(
            self):
        array = np.asarray([[0., 1., 2.], [1., 2., 3.]])
        resulting_dict = {'foobar':
                          collections.OrderedDict({'bar': {'foo': array}})}
        self.yaml.dict = {'foobar':
                          collections.OrderedDict({'bar':
                                                  {'foo': {
                                                   'type': 'numpy.ndarray',
                                                   'dtype': str(array.dtype),
                                                   'array': array.tolist()}}})}
        self.yaml.deserialise_numpy_arrays()
        np.testing.assert_allclose(resulting_dict["foobar"]["bar"]["foo"],
                                   self.yaml.dict["foobar"]["bar"]["foo"])

    def test_write_stream(self):
        self.yaml.dict = self.dict
        dump = yaml.dump(self.dict)
        self.assertEqual(dump, self.yaml.write_stream())

    def test_write_stream_with_numpy_float(self):
        self.yaml.dict = {'foo': np.float64(5)}
        self.assertEqual('foo: 5.0', self.yaml.write_stream().strip())

    def test_write_stream_with_numpy_int(self):
        self.yaml.dict = {'foo': np.int64(5)}
        self.assertEqual('foo: 5', self.yaml.write_stream().strip())

    def test_read_stream(self):
        self.yaml.dict = self.dict
        dump = yaml.dump(self.dict)
        yaml_object = aspecd.utils.Yaml()
        yaml_object.read_stream(dump)
        self.assertEqual(self.dict, yaml_object.dict)

    def test_read_from_converts_floats_with_exponent_to_float(self):
        yaml_dict = {'foo': '1e3'}
        with open(self.filename, 'w') as file:
            yaml.dump(yaml_dict, file)
        self.yaml.read_from(self.filename)
        self.assertEqual(1e3, self.yaml.dict['foo'])

    def test_read_stream_converts_floats_with_exponent_to_float(self):
        yaml_dict = {'foo': '1e3'}
        dump = yaml.dump(yaml_dict)
        yaml_object = aspecd.utils.Yaml()
        yaml_object.read_stream(dump)
        self.assertEqual(1e3, yaml_object.dict['foo'])

    def test_write_stream_converts_tuple_to_list(self):
        yaml_dict = {'foo': (1, 2)}
        self.yaml.dict = yaml_dict
        dump = self.yaml.write_stream()
        self.assertNotIn('!!python/tuple', dump)


class TestReplaceValueInDict(unittest.TestCase):

    def test_replace_value_returns_dict(self):
        target_dict = {'kfoo': 'vfoo', 'kbar': 'vbar'}
        replacement = {'kfoo': 'vbar'}
        target_dict = utils.replace_value_in_dict(replacement, target_dict)
        self.assertTrue(isinstance(target_dict, dict))

    def test_replace_value_replaces_existing_value(self):
        target_dict = {'kfoo': 'vfoo', 'kbar': 'vbar'}
        replacement = {'vfoo': 'vbar'}
        target_dict = utils.replace_value_in_dict(replacement, target_dict)
        self.assertEqual(replacement['vfoo'], target_dict['kfoo'])

    def test_replace_value_replaces_existing_value_in_cascaded_dict(self):
        target_dict = {'kfoo': {'kbar': 'vfoo'}}
        replacement = {'vfoo': 'vbar'}
        target_dict = utils.replace_value_in_dict(replacement, target_dict)
        self.assertEqual(replacement['vfoo'], target_dict['kfoo']['kbar'])

    def test_replace_value_replaces_existing_value_in_doubly_cascaded_dict(
            self):
        target_dict = {'kfoo': {'kfoobar': {'kbar': 'vfoo'}}}
        replacement = {'vfoo': 'vbar'}
        target_dict = utils.replace_value_in_dict(replacement, target_dict)
        self.assertEqual(replacement['vfoo'],
                         target_dict['kfoo']['kfoobar']['kbar'])

    def test_replace_value_ignores_nonexisting_value(self):
        target_dict = {'kfoo': 'vfoo', 'kbar': 'vbar'}
        replacement = {'kfoo': 'vbar'}
        modified_dict = utils.replace_value_in_dict(replacement, target_dict)
        self.assertEqual(modified_dict, target_dict)

    def test_replace_value_ignores_nonexisting_value_in_cascaded_dict(self):
        target_dict = {'kfoo': {'kbar': 'vfoo'}}
        replacement = {'kfoo': 'vbar'}
        modified_dict = utils.replace_value_in_dict(replacement, target_dict)
        self.assertEqual(modified_dict, target_dict)

    def test_replace_value_replaces_existing_value_in_list(self):
        target_dict = {'kfoo': ['vfoo', 'vbar']}
        replacement = {'vfoo': 'vbar'}
        target_dict = utils.replace_value_in_dict(replacement, target_dict)
        self.assertEqual(replacement['vfoo'], target_dict['kfoo'][0])

    def test_replace_value_handles_lists_of_dicts(self):
        target_dict = {'kfoo': [{'kfoo': 'vfoo'}, {'kbar': 'vbar'}]}
        replacement = {'vfoo': 'vbar'}
        target_dict = utils.replace_value_in_dict(replacement, target_dict)
        self.assertEqual(replacement['vfoo'], target_dict['kfoo'][0]['kfoo'])

    def test_replace_value_replaces_empty_list_in_target(self):
        target_dict = {'kfoo': []}
        replacement = {'kfoo': ['foo', 'bar']}
        target_dict = utils.replace_value_in_dict(replacement, target_dict)
        self.assertEqual(replacement['kfoo'], target_dict['kfoo'])


class TestCopyValuesBetweenDicts(unittest.TestCase):

    def test_copy_values_returns_dict(self):
        target_dict = utils.copy_values_between_dicts(dict(), dict())
        self.assertTrue(isinstance(target_dict, dict))

    def test_copy_values_copies_existing_value(self):
        source = {'kfoo': 'vbar'}
        target = {'kfoo': 'vfoo', 'kbar': 'vbar'}
        target = utils.copy_values_between_dicts(source, target)
        self.assertEqual(source['kfoo'], target['kfoo'])

    def test_copy_values_ignores_nonexisting_value(self):
        source = {'kfoobar': 'vbar'}
        target = {'kfoo': 'vfoo', 'kbar': 'vbar'}
        modified_target = utils.copy_values_between_dicts(source, target)
        self.assertEqual(modified_target, target)

    def test_copy_values_copies_existing_value_in_cascaded_target_dict(self):
        source = {'kbar': 'vfoo'}
        target = {'kfoo': {'kbar': 'vbar'}}
        target = utils.copy_values_between_dicts(source, target)
        self.assertEqual(source['kbar'], target['kfoo']['kbar'])

    def test_copy_values_copies_existing_value_in_cascaded_dicts(self):
        source = {'kfoo': {'kbar': 'vfoo'}}
        target = {'kfoo': {'kbar': 'vbar'}}
        target = utils.copy_values_between_dicts(source, target)
        self.assertEqual(source['kfoo']['kbar'], target['kfoo']['kbar'])


class TestCopyKeysBetweenDicts(unittest.TestCase):

    def test_copy_keys_returns_dict(self):
        target_dict = utils.copy_keys_between_dicts(dict(), dict())
        self.assertTrue(isinstance(target_dict, dict))

    def test_copy_keys_copies_existing_key(self):
        source = {'kfoo': 'vbar'}
        target = {'kfoo': 'vfoo', 'kbar': 'vbar'}
        target = utils.copy_keys_between_dicts(source, target)
        self.assertEqual(source['kfoo'], target['kfoo'])

    def test_copy_keys_copies_existing_key_in_cascaded_dicts(self):
        source = {'kfoo': {'kbar': 'vfoo'}}
        target = {'kfoo': {'kbar': 'vbar'}}
        target = utils.copy_keys_between_dicts(source, target)
        self.assertEqual(source['kfoo']['kbar'], target['kfoo']['kbar'])

    def test_copy_keys_preserves_existing_keys_in_target_dicts(self):
        source = {'kfoo': {'kbar': 'vfoo'}}
        target = {'kfoo': {'kbar': 'vbar', 'kfoobar': 'vfoobar'}}
        target = utils.copy_keys_between_dicts(source, target)
        self.assertIn('kfoobar', target['kfoo'])

    def test_copy_keys_of_cascaded_dict_with_nonexisting_target_key(self):
        source = {'kfoo': {'kbar': 'vfoo'}}
        target = {'kbar': {'kbar': 'vbar', 'kfoobar': 'vfoobar'}}
        target = utils.copy_keys_between_dicts(source, target)
        self.assertIn('kfoo', target)

    def test_copy_keys_if_dict_in_list(self):
        source = {'kfoo': [{'kbar': 'vfoo'}]}
        target = {'kfoo': [{'kbar': 'vbar', 'kfoobar': 'vfoobar'}]}
        target = utils.copy_keys_between_dicts(source, target)
        self.assertEqual('vfoo', target["kfoo"][0]["kbar"])

    def test_copy_key_if_target_key_is_dict_but_source_key_is_not(self):
        source = {'kfoo': 'kbar'}
        target = {'kfoo': {'kbar': 'vfoo'}}
        target = utils.copy_keys_between_dicts(source, target)
        self.assertEqual(source['kfoo'], target['kfoo'])


class TestRemoveEmptyValuesFromDicts(unittest.TestCase):

    def test_remove_empty_values_returns_dict(self):
        target_dict = utils.remove_empty_values_from_dict(dict())
        self.assertTrue(isinstance(target_dict, dict))

    def test_remove_empty_values_removes_keys_with_empty_values(self):
        dict_ = {'foo': ''}
        target_dict = utils.remove_empty_values_from_dict(dict_)
        self.assertEqual(target_dict, dict())

    def test_remove_empty_values_only_removes_keys_with_empty_values(self):
        dict_ = {'foo': '', 'bar': 'bla'}
        target_dict = utils.remove_empty_values_from_dict(dict_)
        self.assertEqual(target_dict, {'bar': 'bla'})

    def test_remove_empty_values_recursively_removes_keys(self):
        dict_ = {'foo': {'bar': ''}}
        target_dict = utils.remove_empty_values_from_dict(dict_)
        self.assertEqual(target_dict, dict())

    def test_remove_empty_values_removes_deep_keys(self):
        dict_ = {'foo': {'bar': '', 'bla': 'blub'}}
        target_dict = utils.remove_empty_values_from_dict(dict_)
        self.assertEqual(target_dict, {'foo': {'bla': 'blub'}})


class TestConvertKeysToVariableNames(unittest.TestCase):

    def test_convert_keys_returns_dict(self):
        target_dict = utils.convert_keys_to_variable_names(dict())
        self.assertTrue(isinstance(target_dict, dict))

    def test_convert_keys_converts_to_lower_case(self):
        dict_ = {'Foo': 'bar'}
        target_dict = utils.convert_keys_to_variable_names(dict_)
        self.assertDictEqual({'foo': 'bar'}, target_dict)

    def test_convert_keys_converts_space_to_underscore(self):
        dict_ = {'foo bar': 'bar'}
        target_dict = utils.convert_keys_to_variable_names(dict_)
        self.assertDictEqual({'foo_bar': 'bar'}, target_dict)

    def test_convert_keys_recursively_converts_to_lower_case(self):
        dict_ = {'Foo': {'Bar': 'bla'}}
        target_dict = utils.convert_keys_to_variable_names(dict_)
        self.assertDictEqual({'foo': {'bar': 'bla'}}, target_dict)

    def test_convert_keys_recursively_converts_space_to_underscore(self):
        dict_ = {'foo bar': {'bar bla': 'blub'}}
        target_dict = utils.convert_keys_to_variable_names(dict_)
        self.assertDictEqual({'foo_bar': {'bar_bla': 'blub'}}, target_dict)


class TestAllEqual(unittest.TestCase):

    def test_equal_elements_of_list_return_true(self):
        self.assertTrue(utils.all_equal(['foo', 'foo']))

    def test_different_elements_of_list_return_false(self):
        self.assertFalse(utils.all_equal(['foo', 'bar']))


class TestProperties(unittest.TestCase):
    def setUp(self):
        self.properties = aspecd.utils.Properties()

    def test_instantiate_class(self):
        pass

    def test_has_to_dict_method(self):
        self.assertTrue(hasattr(self.properties, 'to_dict'))
        self.assertTrue(callable(self.properties.to_dict))

    def test_has_from_dict_method(self):
        self.assertTrue(hasattr(self.properties, 'from_dict'))
        self.assertTrue(callable(self.properties.from_dict))

    def test_from_dict_without_dict_raises(self):
        with self.assertRaises(aspecd.exceptions.MissingDictError):
            self.properties.from_dict()

    def test_from_dict_sets_attribute(self):
        attribute = 'foo'
        dict_ = dict()
        dict_[attribute] = 'foo'
        setattr(self.properties, attribute, None)
        self.properties.from_dict(dict_)
        self.assertEqual(dict_[attribute],
                         getattr(self.properties, attribute))

    def test_from_dict_with_list_attribute_appends_to_list(self):
        attribute = 'foo'
        dict_ = dict()
        dict_[attribute] = 'foo'
        setattr(self.properties, attribute, ['bar'])
        self.properties.from_dict(dict_)
        self.assertEqual(['bar', dict_[attribute]],
                         getattr(self.properties, attribute))

    def test_from_dict_with_list_attribute_appends_each_element(self):
        attribute = 'foo'
        dict_ = dict()
        dict_[attribute] = ['foo', 'bar']
        setattr(self.properties, attribute, ['bar'])
        self.properties.from_dict(dict_)
        self.assertEqual(['bar', 'foo', 'bar'],
                         getattr(self.properties, attribute))

    def test_from_dict_does_not_set_unknown_attribute(self):
        attribute = 'foo'
        dict_ = dict()
        dict_[attribute] = 'foo'
        self.properties.from_dict(dict_)
        self.assertFalse(hasattr(self.properties, attribute))

    def test_from_dict_with_property_object_as_property(self):
        dict_ = {'prop1': {'prop2': 'foo'}}
        prop1 = aspecd.utils.Properties()
        setattr(prop1, 'prop2', '')
        setattr(self.properties, 'prop1', prop1)
        self.properties.from_dict(dict_)
        # noinspection PyUnresolvedReferences
        self.assertEqual('foo', self.properties.prop1.prop2)

    def test_has_get_properties_method(self):
        self.assertTrue(hasattr(self.properties, 'get_properties'))
        self.assertTrue(callable(self.properties.get_properties))

    def test_get_properties_without_properties_returns_empty_list(self):
        self.assertEqual([], self.properties.get_properties())

    def test_get_properties_returns_list_of_properties(self):
        props = ['foo', 'bar']
        for prop in props:
            setattr(self.properties, prop, None)
        self.assertEqual(props, self.properties.get_properties())

    def test_get_properties_does_not_return_nonpublic_properties(self):
        props = ['_foo', 'bar']
        for prop in props:
            setattr(self.properties, prop, None)
        self.assertEqual(['bar'], self.properties.get_properties())

    def test_get_properties_does_not_return_excluded_properties(self):
        props = ['foo', 'bar']
        for prop in props:
            setattr(self.properties, prop, None)
        self.properties._exclude = ['foo']
        self.assertEqual(['bar'], self.properties.get_properties())


class TestBasename(unittest.TestCase):

    def test_basename_returns_last_part_of_path_without_extension(self):
        self.assertEqual('bar', utils.basename('/foo/bar.bla'))

    def test_basename_returns_last_part_if_starting_with_dot(self):
        self.assertEqual('.bashrc', utils.basename('/home/doe/.bashrc'))

    def test_basename_removes_only_last_extension(self):
        self.assertEqual('foo.tar', utils.basename('/home/doe/foo.tar.gz'))

    def test_basename_works_without_path(self):
        self.assertEqual('foo', utils.basename('foo.bar'))

    def test_basename_works_without_extension(self):
        self.assertEqual('foo', utils.basename('/path/to/foo'))

    def test_basename_works_with_relative_path(self):
        self.assertEqual('foo', utils.basename('./path/to/foo'))


class TestPath(unittest.TestCase):

    def test_path_returns_path_without_filename(self):
        self.assertEqual('/foo/', utils.path('/foo/bar.bla'))

    def test_path_works_with_relative_path(self):
        self.assertEqual('./foo/', utils.path('./foo/bar.bla'))


class TestNotZero(unittest.TestCase):

    def test_not_zero_of_zero_returns_nonzero_value(self):
        self.assertGreater(utils.not_zero(0), 0)

    def test_not_zero_of_zero_returns_np_float_resolution(self):
        self.assertEqual(np.finfo(np.float64).resolution,
                         utils.not_zero(0))

    def test_not_zero_of_positive_value_preserves_sign(self):
        self.assertGreater(utils.not_zero(1e-20), 0)

    def test_not_zero_of_negative_value_preserves_sign(self):
        self.assertLess(utils.not_zero(-1e-20), 0)

    def test_not_zero_of_negative_value_closer_than_limit_returns_limit(self):
        self.assertEqual(-np.finfo(np.float64).resolution,
                         utils.not_zero(-1e-20))


class TestIterable(unittest.TestCase):

    def test_iterable_returns_true_for_list(self):
        self.assertTrue(utils.isiterable([]))

    def test_iterable_returns_true_for_tuple(self):
        self.assertTrue(utils.isiterable(tuple()))

    def test_iterable_returns_true_for_nd_array(self):
        self.assertTrue(utils.isiterable(np.asarray([])))

    def test_iterable_returns_true_for_string(self):
        self.assertTrue(utils.isiterable('foo'))

    def test_iterable_returns_false_for_scalar(self):
        self.assertFalse(utils.isiterable(1))


class TestGetPackageData(unittest.TestCase):
    def setUp(self):
        self.filename = 'bar'
        self.data_dir = 'foo'

    def tearDown(self):
        if os.path.exists(self.data_dir):
            shutil.rmtree(self.data_dir)

    def create_data_dir_and_contents(self):
        data_dir = os.path.join(self.data_dir, 'aspecd')
        os.makedirs(data_dir)
        with open(os.path.join(data_dir, self.filename),
                  'w+', encoding='utf8') as file:
            file.write('foo')

    def test_get_package_data_without_name_raises(self):
        with self.assertRaises(ValueError):
            utils.get_package_data()

    def test_get_package_data_returns_content(self):
        with patch('pkgutil.get_data', return_value="foo".encode()):
            content = utils.get_package_data(self.filename)
        self.assertTrue(content)

    def test_get_package_data_with_prefixed_package_returns_content(self):
        content = utils.get_package_data('aspecd@utils.py')
        self.assertTrue(content)

    def test_get_package_data_with_foreign_package_returns_content(self):
        content = utils.get_package_data('pip@__main__.py', directory='')
        self.assertTrue(content)


class TestChangeWorkingDir(unittest.TestCase):

    def test_change_working_dir_changes_working_dir(self):
        with utils.change_working_dir('..'):
            working_dir = os.path.abspath(os.getcwd())
        self.assertEqual(os.path.split(os.getcwd())[0], working_dir)

    def test_change_working_dir_returns_to_original_dir(self):
        oldpwd = os.getcwd()
        with utils.change_working_dir('..'):
            pass
        self.assertEqual(oldpwd, os.getcwd())
