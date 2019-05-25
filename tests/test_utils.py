"""Tests for utils."""

import collections
import copy
import datetime
import os
import unittest

import oyaml as yaml

import aspecd.utils
from aspecd import utils, dataset, plotting


class TestFullClassName(unittest.TestCase):

    def test_full_class_name(self):
        dataset_ = dataset.Dataset()
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
        self.mixed_in.foo[0]["foo"] = obj1
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
        self.assertEqual(arguments, list(obj.__odict__.keys()))


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
        with self.assertRaises(utils.MissingFilenameError):
            self.yaml.read_from()

    def test_has_write_to_method(self):
        self.assertTrue(hasattr(self.yaml, 'write_to'))
        self.assertTrue(callable(self.yaml.write_to))

    def test_write_to_without_filename_raises(self):
        with self.assertRaises(utils.MissingFilenameError):
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
            contents = yaml.load(file)
        self.assertEqual(contents, self.yaml.dict)


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
        with self.assertRaises(aspecd.utils.MissingDictError):
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
