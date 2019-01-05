"""Tests for tasks."""

import os
import unittest

from aspecd import dataset, io, processing, tasks, utils


class TestRecipe(unittest.TestCase):
    def setUp(self):
        self.recipe = tasks.Recipe()
        self.filename = 'test.yaml'
        self.dataset = 'foo'
        self.datasets = ['foo', 'bar']
        self.task = {'kind': 'processing', 'type': 'ProcessingStep'}
        self.importer_factory = io.DatasetImporterFactory()

    def tearDown(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def test_instantiate_class(self):
        pass

    def test_has_datasets_property(self):
        self.assertTrue(hasattr(self.recipe, 'datasets'))

    def test_has_tasks_property(self):
        self.assertTrue(hasattr(self.recipe, 'tasks'))

    def test_has_importer_factory_property(self):
        self.assertTrue(hasattr(self.recipe, 'importer_factory'))

    def test_import_from_without_importer_raises(self):
        with self.assertRaises(tasks.MissingImporterError):
            self.recipe.import_from()

    def test_import_from_yaml_importer_with_task_sets_task(self):
        yaml_contents = {'tasks': [self.task]}
        with open(self.filename, 'w') as file:
            utils.yaml.dump(yaml_contents, file)
        importer = io.RecipeYamlImporter(source=self.filename)
        self.recipe.importer_factory = self.importer_factory
        self.recipe.import_from(importer=importer)
        for key in self.task:
            self.assertEqual(getattr(self.recipe.tasks[0], key),
                             self.task[key])

    def test_import_from_yaml_importer_with_datasets_sets_datasets(self):
        yaml_contents = {'datasets': self.datasets}
        with open(self.filename, 'w') as file:
            utils.yaml.dump(yaml_contents, file)
        importer = io.RecipeYamlImporter(source=self.filename)
        self.recipe.importer_factory = self.importer_factory
        self.recipe.import_from(importer=importer)
        self.assertEqual(len(self.recipe.datasets), len(self.datasets))
        for dataset_ in self.recipe.datasets:
            self.assertTrue(isinstance(dataset_, dataset.Dataset))

    def test_export_to_without_exporter_raises(self):
        with self.assertRaises(tasks.MissingExporterError):
            self.recipe.export_to()

    def test_export_to_yaml_exporter_writes_yaml_file(self):
        exporter = io.RecipeYamlExporter(target=self.filename)
        self.recipe.export_to(exporter)
        to_dict_contents = self.recipe.to_dict()
        with open(self.filename, 'r') as file:
            contents = utils.yaml.load(file)
        self.assertEqual(to_dict_contents, contents)

    def test_from_dict_without_dict_raises(self):
        with self.assertRaises(tasks.MissingDictError):
            self.recipe.from_dict()

    def test_from_dict_with_dataset_without_importer_factory_raises(self):
        dict_ = {'datasets': [self.dataset]}
        with self.assertRaises(tasks.MissingImporterFactoryError):
            self.recipe.from_dict(dict_)

    def test_from_dict_with_dataset_sets_dataset(self):
        dict_ = {'datasets': [self.dataset]}
        self.recipe.importer_factory = self.importer_factory
        self.recipe.from_dict(dict_)
        self.assertTrue(isinstance(self.recipe.datasets[0], dataset.Dataset))

    def test_from_dict_with_dataset_sets_dataset_source(self):
        dict_ = {'datasets': [self.dataset]}
        self.recipe.importer_factory = self.importer_factory
        self.recipe.from_dict(dict_)
        self.assertEqual(self.dataset, self.recipe.datasets[0].source)

    def test_from_dict_with_multiple_datasets_sets_datasets(self):
        dict_ = {'datasets': self.datasets}
        self.recipe.importer_factory = self.importer_factory
        self.recipe.from_dict(dict_)
        for dataset_ in self.recipe.datasets:
            self.assertTrue(isinstance(dataset_, dataset.Dataset))

    def test_from_dict_with_task_adds_task(self):
        dict_ = {'tasks': [self.task]}
        self.recipe.importer_factory = self.importer_factory
        self.recipe.from_dict(dict_)
        self.assertTrue(isinstance(self.recipe.tasks[0], tasks.Task))
        for key in self.task:
            self.assertEqual(getattr(self.recipe.tasks[0], key),
                             self.task[key])

    def test_has_to_dict_method(self):
        self.assertTrue(hasattr(self.recipe, 'to_dict'))
        self.assertTrue(callable(self.recipe.to_dict))

    def test_to_dict_with_datasets_returns_dataset_sources(self):
        for dataset_ in self.datasets:
            tmp = dataset.Dataset()
            tmp.source = dataset_
            self.recipe.datasets.append(tmp)
        dict_ = self.recipe.to_dict()
        self.assertEqual(self.datasets, dict_['datasets'])

    def test_to_dict_with_task_returns_task_dict(self):
        task = tasks.Task()
        task.from_dict(self.task)
        self.recipe.tasks.append(task)
        dict_ = self.recipe.to_dict()
        self.assertEqual(task.to_dict(), dict_['tasks'][0])


class TestChef(unittest.TestCase):
    def setUp(self):
        self.chef = tasks.Chef()
        self.recipe = tasks.Recipe()
        self.recipe.importer_factory = io.DatasetImporterFactory()
        self.dataset = 'foo'
        self.processing_task = {'kind': 'processing',
                                'type': 'ProcessingStep'}
        self.analysis_task = {'kind': 'analysis',
                              'type': 'AnalysisStep'}
        self.annotation_task = {'kind': 'annotation',
                                'type': 'Comment'}
        self.plotting_task = {'kind': 'plotting',
                              'type': 'SinglePlotter'}

    def test_instantiate_class(self):
        pass

    def test_has_cook_method(self):
        self.assertTrue(hasattr(self.chef, 'cook'))
        self.assertTrue(callable(self.chef.cook))

    def test_has_recipe_property(self):
        self.assertTrue(hasattr(self.chef, 'recipe'))

    def test_cook_sets_recipe(self):
        recipe = self.recipe
        self.chef.cook(recipe)
        self.assertEqual(self.chef.recipe, recipe)

    def test_instantiate_with_recipe_sets_recipe(self):
        recipe = self.recipe
        chef = tasks.Chef(recipe=recipe)
        self.assertEqual(chef.recipe, recipe)

    def test_cook_without_recipe_raises(self):
        with self.assertRaises(tasks.MissingRecipeError):
            self.chef.cook()

    def test_cook_with_preset_recipe(self):
        recipe = self.recipe
        self.chef.recipe = recipe
        self.chef.cook()
        self.assertEqual(recipe, self.chef.recipe)

    def test_cook_recipe_with_processing_task_performs_task(self):
        recipe = self.recipe
        recipe_dict = {'datasets': [self.dataset],
                       'tasks': [self.processing_task]}
        recipe.from_dict(recipe_dict)
        self.chef.cook(recipe=recipe)
        self.assertTrue(self.chef.recipe.datasets[0].history)

    def test_cook_recipe_with_analysis_task_performs_task(self):
        recipe = self.recipe
        recipe_dict = {'datasets': [self.dataset],
                       'tasks': [self.analysis_task]}
        recipe.from_dict(recipe_dict)
        self.chef.cook(recipe=recipe)
        self.assertTrue(self.chef.recipe.datasets[0].analyses)

    def test_cook_recipe_with_annotation_task_performs_task(self):
        recipe = self.recipe
        recipe_dict = {'datasets': [self.dataset],
                       'tasks': [self.annotation_task]}
        recipe.from_dict(recipe_dict)
        self.chef.cook(recipe=recipe)
        self.assertTrue(self.chef.recipe.datasets[0].annotations)

    def test_cook_recipe_with_plotting_task_performs_task(self):
        recipe = self.recipe
        recipe_dict = {'datasets': [self.dataset],
                       'tasks': [self.plotting_task]}
        recipe.from_dict(recipe_dict)
        self.chef.cook(recipe=recipe)
        self.assertTrue(self.chef.recipe.datasets[0].representations)


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

    def test_get_object_with_full_class_name_returns_correct_object(self):
        kind = 'aspecd.processing'
        type_ = 'ProcessingStep'
        self.task.kind = kind
        self.task.type = type_
        obj = self.task.get_object()
        self.assertTrue(isinstance(obj, processing.ProcessingStep))

    def test_get_object_without_package_name_returns_correct_object(self):
        kind = 'processing'
        type_ = 'ProcessingStep'
        self.task.kind = kind
        self.task.type = type_
        obj = self.task.get_object()
        self.assertTrue(isinstance(obj, processing.ProcessingStep))

    def test_get_object_sets_object_attributes(self):
        kind = 'processing'
        type_ = 'ProcessingStep'
        metadata = {'parameters': {'foo': 'bar'}}
        self.task.kind = kind
        self.task.type = type_
        self.task.metadata = metadata
        obj = self.task.get_object()
        self.assertEqual(metadata['parameters'], getattr(obj, 'parameters'))

    def test_get_object_sets_only_existing_object_attributes(self):
        kind = 'processing'
        type_ = 'ProcessingStep'
        metadata = {'foo': {'foo': 'bar'}}
        self.task.kind = kind
        self.task.type = type_
        self.task.metadata = metadata
        obj = self.task.get_object()
        self.assertFalse(hasattr(obj, 'foo'))
