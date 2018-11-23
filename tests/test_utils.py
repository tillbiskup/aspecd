"""Tests for utils."""

import collections
import datetime
import unittest

from aspecd import utils, dataset


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


class TestGetVersion(unittest.TestCase):

    def test_version_not_empty(self):
        version = utils.get_version()
        self.assertTrue(version)


class TestPackageName(unittest.TestCase):

    def test_package_name_returns_correct_package(self):
        package_name = utils.package_name()
        self.assertEqual(package_name, 'aspecd')

    def test_package_name_with_object_returns_correct_package(self):
        package_name = utils.package_name(unittest.TestCase())
        self.assertEqual(package_name, 'unittest')


class TestConfigDir(unittest.TestCase):

    def test_config_dir_not_empty(self):
        version = utils.config_dir()
        self.assertTrue(version)
