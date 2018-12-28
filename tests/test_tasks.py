"""Tests for tasks."""

import os
import unittest

from aspecd import io, tasks


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
