"""Tests for tasks."""

import os
import unittest

from aspecd import io, processing, tasks


class TestRecipe(unittest.TestCase):
    def setUp(self):
        self.recipe = tasks.Recipe()
        self.filename = 'test.yaml'

    def tearDown(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def test_instantiate_class(self):
        pass

    def test_has_datasets_property(self):
        self.assertTrue(hasattr(self.recipe, 'datasets'))

    def test_has_tasks_property(self):
        self.assertTrue(hasattr(self.recipe, 'tasks'))

    def test_has_read_from_method(self):
        self.assertTrue(hasattr(self.recipe, 'read_from'))
        self.assertTrue(callable(self.recipe.read_from))

    def test_read_from_without_filename_raises(self):
        with self.assertRaises(tasks.MissingFilenameError):
            self.recipe.read_from()

    def test_has_write_to_method(self):
        self.assertTrue(hasattr(self.recipe, 'write_to'))
        self.assertTrue(callable(self.recipe.write_to))

    def test_write_to_without_filename_raises(self):
        with self.assertRaises(tasks.MissingFilenameError):
            self.recipe.write_to()

    def test_has_to_dict_method(self):
        self.assertTrue(hasattr(self.recipe, 'to_dict'))
        self.assertTrue(callable(self.recipe.to_dict))

    def test_write_to_writes_yaml_file(self):
        self.recipe.write_to(self.filename)
        to_dict_contents = self.recipe.to_dict()
        with open(self.filename, 'r') as file:
            contents = io.yaml.load(file)
        self.assertEqual(to_dict_contents, contents)

    def test_read_from_yaml_file_with_datasets_sets_datasets(self):
        datasets = ['foo', 'bar']
        yaml_contents = {'datasets': datasets}
        with open(self.filename, 'w') as file:
            io.yaml.dump(yaml_contents, file)
        self.recipe.read_from(self.filename)
        self.assertEqual(self.recipe.datasets, datasets)

    def test_read_from_yaml_file_with_task_sets_task(self):
        task = {'kind': 'processing', 'type': 'ProcessingStep'}
        yaml_contents = {'tasks': [task]}
        with open(self.filename, 'w') as file:
            io.yaml.dump(yaml_contents, file)
        self.recipe.read_from(self.filename)
        for key in task:
            self.assertEqual(getattr(self.recipe.tasks[0], key), task[key])

    def test_from_dict_without_dict_raises(self):
        with self.assertRaises(tasks.MissingDictError):
            self.recipe.from_dict()

    def test_from_dict_with_datasets_sets_datasets(self):
        datasets = ['foo', 'bar']
        dict_ = {'datasets': datasets}
        self.recipe.from_dict(dict_)
        self.assertEqual(datasets, self.recipe.datasets)

    def test_from_dict_with_task_adds_task(self):
        task = {'kind': 'processing', 'type': 'ProcessingStep'}
        dict_ = {'tasks': [task]}
        self.recipe.from_dict(dict_)
        self.assertTrue(isinstance(self.recipe.tasks[0], tasks.Task))
        for key in task:
            self.assertEqual(getattr(self.recipe.tasks[0], key), task[key])


class TestChef(unittest.TestCase):
    def setUp(self):
        self.chef = tasks.Chef()

    def test_instantiate_class(self):
        pass

    def test_has_cook_method(self):
        self.assertTrue(hasattr(self.chef, 'cook'))
        self.assertTrue(callable(self.chef.cook))

    def test_has_recipe_property(self):
        self.assertTrue(hasattr(self.chef, 'recipe'))

    def test_cook_sets_recipe(self):
        recipe = tasks.Recipe()
        self.chef.cook(recipe)
        self.assertEqual(self.chef.recipe, recipe)

    def test_instantiate_with_recipe_sets_recipe(self):
        recipe = tasks.Recipe()
        chef = tasks.Chef(recipe=recipe)
        self.assertEqual(chef.recipe, recipe)

    def test_cook_without_recipe_raises(self):
        with self.assertRaises(tasks.MissingRecipeError):
            self.chef.cook()


class TestTask(unittest.TestCase):
    def setUp(self):
        self.task = tasks.Task()

    def test_instantiate_class(self):
        pass

    def test_has_kind_property(self):
        self.assertTrue(hasattr(self.task, 'kind'))

    def test_has_type_property(self):
        self.assertTrue(hasattr(self.task, 'type'))

    def test_has_metadata_property(self):
        self.assertTrue(hasattr(self.task, 'metadata'))

    def test_has_apply_to_property(self):
        self.assertTrue(hasattr(self.task, 'apply_to'))

    def test_apply_to_is_empty(self):
        self.assertEqual(0, len(self.task.apply_to))

    def test_has_to_dict_method(self):
        self.assertTrue(hasattr(self.task, 'to_dict'))
        self.assertTrue(callable(self.task.to_dict))

    def test_has_from_dict_method(self):
        self.assertTrue(hasattr(self.task, 'from_dict'))
        self.assertTrue(callable(self.task.from_dict))

    def test_from_dict_without_dict_raises(self):
        with self.assertRaises(tasks.MissingDictError):
            self.task.from_dict()

    def test_from_dict_sets_kind(self):
        kind = 'foo'
        dict_ = {'kind': kind}
        self.task.from_dict(dict_)
        self.assertEqual(kind, self.task.kind)

    def test_from_dict_sets_type(self):
        type_ = 'foo'
        dict_ = {'type': type_}
        self.task.from_dict(dict_)
        self.assertEqual(type_, self.task.type)

    def test_from_dict_does_not_set_unknown_attribute(self):
        attribute = 'foo'
        dict_ = dict()
        dict_[attribute] = 'foo'
        self.task.from_dict(dict_)
        self.assertFalse(hasattr(self.task, attribute))

    def test_get_task_returns_correct_object(self):
        kind = 'processing'
        type_ = 'ProcessingStep'
        self.task.kind = kind
        self.task.type = type_
        obj = self.task.get_object()
        self.assertTrue(isinstance(obj, processing.ProcessingStep))

    def test_get_task_sets_object_attributes(self):
        kind = 'processing'
        type_ = 'ProcessingStep'
        metadata = {'parameters': {'foo': 'bar'}}
        self.task.kind = kind
        self.task.type = type_
        self.task.metadata = metadata
        obj = self.task.get_object()
        self.assertEqual(metadata['parameters'], getattr(obj, 'parameters'))

    def test_get_task_sets_only_existing_object_attributes(self):
        kind = 'processing'
        type_ = 'ProcessingStep'
        metadata = {'foo': {'foo': 'bar'}}
        self.task.kind = kind
        self.task.type = type_
        self.task.metadata = metadata
        obj = self.task.get_object()
        self.assertFalse(hasattr(obj, 'foo'))
