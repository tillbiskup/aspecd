"""Tests for utils."""

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
