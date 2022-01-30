"""Tests for tasks."""
import collections
import contextlib
import copy
import datetime
import glob
import io
import os
import shutil
import subprocess
import unittest
from unittest.mock import patch
import warnings

import numpy as np
from matplotlib import pyplot as plt

import aspecd.exceptions
import aspecd.io
from aspecd import dataset, plotting, processing, report, tasks, utils


class TestRecipe(unittest.TestCase):
    def setUp(self):
        self.recipe = tasks.Recipe()
        self.filename = 'test.yaml'
        self.dataset = '/foo'
        self.datasets = ['/foo', '/bar']
        self.dataset_filename = 'foo'
        self.task = {'kind': 'processing', 'type': 'SingleProcessingStep'}
        self.dataset_factory = dataset.DatasetFactory()
        self.dataset_factory.importer_factory = \
            aspecd.io.DatasetImporterFactory()

    def tearDown(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)
        if os.path.exists(self.dataset_filename):
            os.remove(self.dataset_filename)

    def test_instantiate_class(self):
        pass

    def test_has_datasets_property(self):
        self.assertTrue(hasattr(self.recipe, 'datasets'))

    def test_has_tasks_property(self):
        self.assertTrue(hasattr(self.recipe, 'tasks'))

    def test_has_dataset_factory_property(self):
        self.assertTrue(hasattr(self.recipe, 'dataset_factory'))

    def test_has_task_factory_property(self):
        self.assertTrue(hasattr(self.recipe, 'task_factory'))

    def test_has_results_property(self):
        self.assertTrue(hasattr(self.recipe, 'results'))

    def test_has_figures_property(self):
        self.assertTrue(hasattr(self.recipe, 'figures'))

    def test_has_plotters_property(self):
        self.assertTrue(hasattr(self.recipe, 'plotters'))

    def test_has_default_package_property(self):
        self.assertTrue(hasattr(self.recipe, 'default_package'))

    def test_has_format_and_settings_and_directories_properties(self):
        self.assertTrue(hasattr(self.recipe, 'format'))
        self.assertTrue(hasattr(self.recipe, 'settings'))
        self.assertTrue(hasattr(self.recipe, 'directories'))

    def test_format_property_is_dict_with_fields(self):
        self.assertEqual(['type', 'version'], list(self.recipe.format.keys()))

    def test_settings_property_is_dict_with_fields(self):
        self.assertEqual(['default_package', 'autosave_plots', 'write_history'],
                         list(self.recipe.settings.keys()))

    def test_directories_property_is_dict_with_fields(self):
        self.assertEqual(['output', 'datasets_source'],
                         list(self.recipe.directories.keys()))

    def test_import_from_without_importer_raises(self):
        with self.assertRaises(aspecd.exceptions.MissingImporterError):
            self.recipe.import_from()

    def test_import_from_yaml_importer_with_task_sets_task(self):
        yaml_contents = {'tasks': [self.task]}
        with open(self.filename, 'w') as file:
            utils.yaml.dump(yaml_contents, file)
        importer = aspecd.io.RecipeYamlImporter(source=self.filename)
        self.recipe.dataset_factory = self.dataset_factory
        self.recipe.import_from(importer=importer)
        for key in self.task:
            self.assertEqual(getattr(self.recipe.tasks[0], key),
                             self.task[key])

    def test_import_from_yaml_importer_sets_filename(self):
        yaml_contents = {'tasks': [self.task]}
        with open(self.filename, 'w') as file:
            utils.yaml.dump(yaml_contents, file)
        importer = aspecd.io.RecipeYamlImporter(source=self.filename)
        self.recipe.dataset_factory = self.dataset_factory
        self.recipe.import_from(importer=importer)
        self.assertEqual(self.filename, self.recipe.filename)

    def test_import_from_yaml_importer_with_datasets_sets_datasets(self):
        yaml_contents = {'datasets': self.datasets}
        with open(self.filename, 'w') as file:
            utils.yaml.dump(yaml_contents, file)
        importer = aspecd.io.RecipeYamlImporter(source=self.filename)
        self.recipe.dataset_factory = self.dataset_factory
        self.recipe.import_from(importer=importer)
        self.assertEqual(len(self.recipe.datasets), len(self.datasets))
        for dataset_ in self.recipe.datasets:
            self.assertTrue(isinstance(self.recipe.datasets[dataset_],
                                       dataset.Dataset))

    def test_export_to_without_exporter_raises(self):
        with self.assertRaises(aspecd.exceptions.MissingExporterError):
            self.recipe.export_to()

    def test_export_to_yaml_exporter_writes_yaml_file(self):
        exporter = aspecd.io.RecipeYamlExporter(target=self.filename)
        self.recipe.export_to(exporter)
        to_dict_contents = self.recipe.to_dict()
        with open(self.filename, 'r') as file:
            contents = utils.yaml.safe_load(file)
        self.assertEqual(to_dict_contents, contents)

    def test_from_dict_without_dict_raises(self):
        with self.assertRaises(aspecd.exceptions.MissingDictError):
            self.recipe.from_dict()

    def test_from_dict_with_dataset_without_dataset_factory_sets_factory(self):
        dict_ = {'datasets': [self.dataset]}
        self.recipe.from_dict(dict_)
        self.assertTrue(self.recipe.dataset_factory)

    def test_from_dict_with_default_package_wo_dataset_factory_raises(self):
        dict_ = {'settings': {'default_package': 'foo'}}
        with self.assertRaisesRegex(ModuleNotFoundError, 'No module named'):
            self.recipe.from_dict(dict_)

    def test_from_dict_with_dataset_sets_dataset(self):
        dict_ = {'datasets': [self.dataset]}
        self.recipe.from_dict(dict_)
        self.assertTrue(isinstance(self.recipe.datasets[self.dataset],
                                   dataset.Dataset))

    def test_from_dict_with_dataset_issues_log_message(self):
        id_ = 'foobar'
        dict_ = {'datasets': [{'source': self.dataset, 'id': id_}]}
        with self.assertLogs(__package__, level='INFO') as cm:
            self.recipe.from_dict(dict_)
        self.assertIn('Import dataset "{}" as "{}"'.format(self.dataset, id_),
                      cm.output[0])

    def test_from_dict_with_dataset_sets_dataset_id(self):
        dict_ = {'datasets': [self.dataset]}
        self.recipe.from_dict(dict_)
        self.assertEqual(self.dataset, self.recipe.datasets[self.dataset].id)

    def test_from_dict_with_dataset_and_source_dir_sets_dataset_id(self):
        dict_ = {'datasets': ['foo'],
                 'directories': {'datasets_source': '/bla'}}
        self.recipe.from_dict(dict_)
        self.assertEqual('/bla/foo', self.recipe.datasets['foo'].id)

    def test_from_dict_with_dataset_and_rel_source_dir_sets_dataset_id(self):
        dict_ = {'datasets': ['foo'],
                 'directories': {'datasets_source': 'bla'}}
        self.recipe.from_dict(dict_)
        abspath = os.path.join(os.path.abspath(os.path.curdir), 'bla', 'foo')
        self.assertEqual(abspath, self.recipe.datasets['foo'].id)

    def test_from_dict_with_multiple_datasets_sets_datasets(self):
        dict_ = {'datasets': self.datasets}
        self.recipe.from_dict(dict_)
        for dataset_ in self.recipe.datasets:
            self.assertTrue(isinstance(self.recipe.datasets[dataset_],
                                       dataset.Dataset))

    def test_from_dict_with_dataset_as_dict_sets_dataset(self):
        dict_ = {'datasets': [{'source': self.dataset}]}
        self.recipe.from_dict(dict_)
        self.assertTrue(isinstance(self.recipe.datasets[self.dataset],
                                   dataset.Dataset))

    def test_from_dict_with_dataset_as_dict_sets_dataset_label(self):
        id_ = 'foobar'
        dict_ = {'datasets': [{'source': self.dataset, 'id': id_}]}
        self.recipe.from_dict(dict_)
        self.assertTrue(isinstance(self.recipe.datasets[id_],
                                   dataset.Dataset))

    def test_from_dict_with_dataset_as_dict_sets_dataset_property(self):
        label = 'foobar'
        dict_ = {'datasets': [{'source': self.dataset, 'label': label}]}
        self.recipe.from_dict(dict_)
        self.assertEqual(label, self.recipe.datasets[self.dataset].label)

    def test_from_dict_with_dataset_as_dict_and_importer(self):
        data = np.random.random(1)
        np.savetxt(self.dataset_filename, data)
        dict_ = {'datasets': [{'source': self.dataset_filename,
                               'importer': 'TxtImporter'}]}
        self.recipe.from_dict(dict_)
        self.assertEqual(data,
                         self.recipe.datasets[self.dataset_filename].data.data)

    def test_from_dict_with_dataset_as_dict_and_importer_parameters(self):
        data = np.random.random(2)
        parameters = {'skiprows': 1}
        np.savetxt(self.dataset_filename, data)
        dict_ = {'datasets': [{'source': self.dataset_filename,
                               'importer': 'TxtImporter',
                               'importer_parameters': parameters}]}
        self.recipe.from_dict(dict_)
        self.assertEqual(data[1],
                         self.recipe.datasets[self.dataset_filename].data.data)

    def test_from_dict_with_dataset_as_dict_and_package_sets_dataset(self):
        dict_ = {'datasets': [{'source': self.dataset, 'package': 'aspecd'}]}
        self.recipe.dataset_factory = 'foo'
        self.recipe.from_dict(dict_)
        self.assertTrue(isinstance(self.recipe.datasets[self.dataset],
                                   dataset.Dataset))

    def test_from_dict_with_dataset_as_dict_and_package_and_importer(self):
        data = np.random.random(1)
        np.savetxt(self.dataset_filename, data)
        dict_ = {'datasets': [{'source': self.dataset_filename,
                               'importer': 'TxtImporter',
                               'package': 'aspecd'}]}
        self.recipe.from_dict(dict_)
        self.assertEqual(data,
                         self.recipe.datasets[self.dataset_filename].data.data)

    def test_from_dict_with_dataset_dict_package_and_importer_parameters(self):
        data = np.random.random(2)
        parameters = {'skiprows': 1}
        np.savetxt(self.dataset_filename, data)
        dict_ = {'datasets': [{'source': self.dataset_filename,
                               'importer': 'TxtImporter',
                               'importer_parameters': parameters,
                               'package': 'aspecd'}]}
        self.recipe.from_dict(dict_)
        self.assertEqual(data[1],
                         self.recipe.datasets[self.dataset_filename].data.data)

    def test_from_dict_with_task_adds_task(self):
        dict_ = {'tasks': [self.task]}
        self.recipe.from_dict(dict_)
        self.assertTrue(isinstance(self.recipe.tasks[0], tasks.Task))
        for key in self.task:
            self.assertEqual(getattr(self.recipe.tasks[0], key),
                             self.task[key])

    def test_from_dict_with_task_adds_task_with_correct_type(self):
        dict_ = {'tasks': [self.task]}
        self.recipe.from_dict(dict_)
        self.assertTrue(isinstance(self.recipe.tasks[0],
                                   tasks.ProcessingTask))

    def test_from_dict_with_default_package_sets_package(self):
        dict_ = {'settings': {'default_package': 'foo'}}
        self.recipe.dataset_factory = self.dataset_factory
        self.recipe.from_dict(dict_)
        self.assertEqual('foo', self.recipe.settings['default_package'])

    def test_from_dict_with_default_package_adds_package_to_task(self):
        dict_ = {'settings': {'default_package': 'foo'}, 'tasks': [self.task]}
        self.recipe.dataset_factory = self.dataset_factory
        self.recipe.from_dict(dict_)
        self.assertEqual('foo', self.recipe.tasks[0].package)

    def test_from_dict_with_default_pkg_and_task_pkg_sets_correct_pkg(self):
        dict_ = {'settings': {'default_package': 'foo'}, 'tasks': [self.task]}
        dict_["tasks"][0]["kind"] = 'bar' + '.' + dict_["tasks"][0]["kind"]
        self.recipe.dataset_factory = self.dataset_factory
        self.recipe.from_dict(dict_)
        self.assertEqual('bar', self.recipe.tasks[0].package)

    def test_has_to_dict_method(self):
        self.assertTrue(hasattr(self.recipe, 'to_dict'))
        self.assertTrue(callable(self.recipe.to_dict))

    def test_to_dict_contains_format_dict(self):
        recipe_dict = self.recipe.to_dict()
        self.assertDictEqual(self.recipe.format, recipe_dict['format'])

    def test_to_dict_contains_settings_dict(self):
        recipe_dict = self.recipe.to_dict()
        self.assertDictEqual(self.recipe.settings, recipe_dict['settings'])

    def test_to_dict_contains_directories_dict(self):
        recipe_dict = self.recipe.to_dict()
        self.assertDictEqual(self.recipe.directories,
                             recipe_dict['directories'])

    def test_to_dict_with_datasets_returns_dataset_sources(self):
        for dataset_ in self.datasets:
            tmp = dataset.Dataset()
            tmp.id = dataset_
            tmp.label = dataset_
            self.recipe.datasets[dataset_] = tmp
        dict_ = self.recipe.to_dict()
        self.assertEqual(self.datasets, dict_['datasets'])

    def test_to_dict_with_dataset_with_id_returns_dataset_as_dict(self):
        id_ = 'foobar'
        tmp = dataset.Dataset()
        tmp.id = self.dataset
        tmp.label = self.dataset
        self.recipe.datasets[id_] = tmp
        dict_ = self.recipe.to_dict()
        self.assertDictEqual({'source': self.dataset, 'id': id_},
                             dict_['datasets'][0])

    def test_to_dict_with_dataset_with_label_returns_dataset_as_dict(self):
        label = 'foobar'
        tmp = dataset.Dataset()
        tmp.id = self.dataset
        tmp.label = label
        self.recipe.datasets[self.dataset] = tmp
        dict_ = self.recipe.to_dict()
        self.assertDictEqual({'source': self.dataset, 'label': label},
                             dict_['datasets'][0])

    def test_to_dict_with_dataset_w_label_and_id_returns_dataset_as_dict(self):
        id_ = 'foobar'
        label = 'foobar'
        tmp = dataset.Dataset()
        tmp.id = self.dataset
        tmp.label = label
        self.recipe.datasets[id_] = tmp
        dict_ = self.recipe.to_dict()
        self.assertDictEqual({'source': self.dataset,
                              'label': label,
                              'id': id_},
                             dict_['datasets'][0])

    def test_to_dict_with_foreign_dataset_includes_package_in_dict(self):
        class ForeignDataset:
            id = self.dataset
            label = self.dataset
        foreign_dataset = ForeignDataset()
        self.recipe.datasets[self.dataset] = foreign_dataset
        dict_ = self.recipe.to_dict()
        self.assertDictEqual(
            {'source': self.dataset, 'package': 'test_tasks'},
            dict_['datasets'][0])

    def test_to_dict_with_foreign_dataset_and_default_package(self):
        class ForeignDataset:
            id = self.dataset
            label = self.dataset
        foreign_dataset = ForeignDataset()
        self.recipe.settings['default_package'] = __name__
        self.recipe.datasets[self.dataset] = foreign_dataset
        dict_ = self.recipe.to_dict()
        self.assertEqual(self.dataset, dict_['datasets'][0])

    def test_to_dict_with_datasets_source_directory(self):
        self.recipe.directories['datasets_source'] = 'foo'
        id_ = 'foobar'
        tmp = dataset.Dataset()
        tmp.id = os.path.join(self.recipe.directories['datasets_source'],
                               id_)
        tmp.label = id_
        self.recipe.datasets[id_] = tmp
        dict_ = self.recipe.to_dict()
        self.assertEqual(id_, dict_['datasets'][0])

    def test_to_dict_with_datasets_source_directory_and_id_with_subpath(self):
        self.recipe.directories['datasets_source'] = 'foo'
        id_ = 'foo/foobar'
        tmp = dataset.Dataset()
        tmp.id = os.path.join(self.recipe.directories['datasets_source'],
                               id_)
        tmp.label = id_
        self.recipe.datasets[id_] = tmp
        dict_ = self.recipe.to_dict()
        self.assertEqual(id_, dict_['datasets'][0])

    def test_to_dict_without_datasets_source_directory(self):
        dataset_id = 'foo'
        recipe_dict = {'datasets': [dataset_id]}
        self.recipe.from_dict(recipe_dict)
        dict_ = self.recipe.to_dict()
        self.assertEqual(dataset_id, dict_['datasets'][0])

    def test_to_dict_with_task_returns_task_dict(self):
        task = tasks.Task()
        task.from_dict(self.task)
        self.recipe.tasks.append(task)
        dict_ = self.recipe.to_dict()
        self.assertEqual(task.to_dict(), dict_['tasks'][0])

    def test_to_dict_w_remove_empty_removes_empty_fields_in_task(self):
        task = tasks.Task()
        task.from_dict(self.task)
        self.recipe.tasks.append(task)
        dict_ = self.recipe.to_dict(remove_empty=True)
        self.assertEqual(task.to_dict(remove_empty=True), dict_['tasks'][0])

    def test_has_get_dataset_method(self):
        self.assertTrue(hasattr(self.recipe, 'get_dataset'))
        self.assertTrue(callable(self.recipe.get_dataset))

    def test_get_dataset_without_identifier_raises(self):
        with self.assertRaises(aspecd.exceptions.MissingDatasetIdentifierError):
            self.recipe.get_dataset()

    def test_get_dataset_with_valid_identifier_returns_dataset(self):
        dict_ = {'datasets': [self.dataset]}
        self.recipe.from_dict(dict_)
        dataset_ = self.recipe.get_dataset(identifier=self.dataset)
        self.assertTrue(isinstance(dataset_, dataset.Dataset))

    def test_get_dataset_with_invalid_identifier_returns_nothing(self):
        dict_ = {'datasets': [self.dataset]}
        self.recipe.from_dict(dict_)
        dataset_ = self.recipe.get_dataset(identifier='invalid')
        self.assertFalse(dataset_)

    def test_get_dataset_from_results_returns_dataset(self):
        dataset_ = dataset.CalculatedDataset()
        dataset_.id = self.dataset
        self.recipe.results = {self.dataset: dataset_}
        dataset_ = self.recipe.get_dataset(identifier=self.dataset)
        self.assertTrue(isinstance(dataset_, dataset.Dataset))

    def test_has_get_datasets_method(self):
        self.assertTrue(hasattr(self.recipe, 'get_datasets'))
        self.assertTrue(callable(self.recipe.get_datasets))

    def test_get_datasets_without_identifier_raises(self):
        with self.assertRaises(aspecd.exceptions.MissingDatasetIdentifierError):
            self.recipe.get_datasets()

    def test_get_datasets_with_valid_identifier_returns_dataset(self):
        dict_ = {'datasets': self.datasets}
        self.recipe.from_dict(dict_)
        datasets = self.recipe.get_datasets(identifiers=self.datasets)
        for dataset_ in datasets:
            self.assertTrue(isinstance(dataset_, dataset.Dataset))

    def test_get_datasets_with_invalid_identifier_returns_nothing(self):
        dict_ = {'datasets': self.datasets}
        self.recipe.from_dict(dict_)
        datasets = self.recipe.get_datasets(
            identifiers=['invalid', 'invalid2'])
        self.assertFalse(datasets)

    def test_get_datasets_from_results_returns_dataset(self):
        dataset0 = dataset.CalculatedDataset()
        dataset0.id = self.datasets[0]
        dataset1 = dataset.CalculatedDataset()
        dataset1.id = self.datasets[1]
        self.recipe.results = {self.datasets[0]: dataset0}
        self.recipe.datasets = [dataset1]
        datasets = self.recipe.get_datasets(identifiers=self.datasets)
        self.assertTrue(datasets)
        for dataset_ in datasets:
            self.assertTrue(isinstance(dataset_, dataset.Dataset))

    def test_from_dict_with_output_directory_sets_output_directory(self):
        dict_ = {'directories': {'output': '/foo'}}
        self.recipe.from_dict(dict_)
        self.assertEqual('/foo', self.recipe.directories['output'])

    def test_from_dict_sets_autosave_plots(self):
        dict_ = {'settings': {'autosave_plots': False}}
        self.recipe.from_dict(dict_)
        self.assertFalse(self.recipe.settings['autosave_plots'])

    def test_to_yaml_returns_string(self):
        self.assertIsInstance(self.recipe.to_yaml(), str)

    def test_to_yaml_contains_format(self):
        self.assertIn('format:', self.recipe.to_yaml())

    def test_to_yaml_w_remove_empty_removes_empty_fields_in_task(self):
        task = tasks.Task()
        task.from_dict(self.task)
        self.recipe.tasks.append(task)
        self.assertNotIn('apply_to', self.recipe.to_yaml(remove_empty=True))


class TestChef(unittest.TestCase):
    def setUp(self):
        self.chef = tasks.Chef()
        self.recipe = tasks.Recipe()
        dataset_factory = dataset.DatasetFactory()
        dataset_factory.importer_factory = aspecd.io.DatasetImporterFactory()
        self.recipe.dataset_factory = dataset_factory
        self.dataset = '/foo'
        self.processing_task = {'kind': 'processing',
                                'type': 'SingleProcessingStep'}
        self.analysis_task = {'kind': 'singleanalysis',
                              'type': 'SingleAnalysisStep'}
        self.annotation_task = {'kind': 'annotation',
                                'type': 'Comment'}
        self.plotting_task = {'kind': 'singleplot',
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
        with self.assertRaises(aspecd.exceptions.MissingRecipeError):
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
        self.assertTrue(self.chef.recipe.datasets[self.dataset].history)

    def test_cook_recipe_with_multiple_datasets_performs_task(self):
        recipe = self.recipe
        recipe_dict = {'datasets': [self.dataset, 'bar'],
                       'tasks': [self.processing_task]}
        recipe.from_dict(recipe_dict)
        self.chef.cook(recipe=recipe)
        self.assertTrue(self.chef.recipe.datasets[self.dataset].history)
        self.assertTrue(self.chef.recipe.datasets['bar'].history)

    def test_cook_recipe_with_multiple_datasets_and_empty_apply_to(self):
        recipe = self.recipe
        self.processing_task['apply_to'] = []
        recipe_dict = {'datasets': [self.dataset, 'bar'],
                       'tasks': [self.processing_task]}
        recipe.from_dict(recipe_dict)
        self.chef.cook(recipe=recipe)
        self.assertTrue(self.chef.recipe.datasets[self.dataset].history)
        self.assertTrue(self.chef.recipe.datasets['bar'].history)

    def test_cook_recipe_with_processing_task_with_apply_to_performs_task(self):
        recipe = self.recipe
        self.processing_task['apply_to'] = self.dataset
        recipe_dict = {'datasets': [self.dataset],
                       'tasks': [self.processing_task]}
        recipe.from_dict(recipe_dict)
        self.chef.cook(recipe=recipe)
        self.assertTrue(self.chef.recipe.datasets[self.dataset].history)

    def test_cook_recipe_with_processing_params_with_multiple_datasets(self):
        recipe = self.recipe
        self.dataset = ['foo', 'bar']
        self.processing_task["type"] = 'BaselineCorrection'
        self.processing_task['apply_to'] = self.dataset
        recipe_dict = {'datasets': self.dataset,
                       'tasks': [self.processing_task]}
        recipe.from_dict(recipe_dict)
        recipe.datasets['foo'].data.data = np.random.random(10)+5
        recipe.datasets['bar'].data.data = np.random.random(10)+3
        self.chef.cook(recipe=recipe)
        self.assertIsInstance(self.chef.history['tasks'][0], dict)
        self.assertEqual(2, len(self.chef.history['tasks']))

    def test_cook_recipe_with_analysis_task_performs_task(self):
        recipe = self.recipe
        recipe_dict = {'datasets': [self.dataset],
                       'tasks': [self.analysis_task]}
        recipe.from_dict(recipe_dict)
        self.chef.cook(recipe=recipe)
        self.assertTrue(self.chef.recipe.datasets[self.dataset].analyses)

    def test_cook_recipe_with_annotation_task_performs_task(self):
        recipe = self.recipe
        recipe_dict = {'datasets': [self.dataset],
                       'tasks': [self.annotation_task]}
        recipe.from_dict(recipe_dict)
        self.chef.cook(recipe=recipe)
        self.assertTrue(self.chef.recipe.datasets[self.dataset].annotations)

    def test_cook_recipe_with_plotting_task_performs_task(self):
        recipe = self.recipe
        recipe_dict = {'datasets': [self.dataset],
                       'tasks': [self.plotting_task]}
        recipe.from_dict(recipe_dict)
        recipe.settings["autosave_plots"] = False
        self.chef.cook(recipe=recipe)
        self.assertTrue(self.chef.recipe.datasets[
                            self.dataset].representations)

    def test_has_history_property(self):
        self.assertTrue(hasattr(self.chef, 'history'))

    def test_history_property_is_ordered_dict(self):
        self.assertEqual(collections.OrderedDict, type(self.chef.history))

    def test_cook_adds_system_info_key_to_history(self):
        recipe = self.recipe
        self.chef.cook(recipe)
        self.assertIn('system_info', self.chef.history)

    def test_cook_adds_default_package_key_to_history(self):
        recipe = self.recipe
        recipe_dict = {'datasets': [self.dataset],
                       'tasks': [self.analysis_task],
                       'settings': {'default_package': 'aspecd'}}
        recipe.from_dict(recipe_dict)
        self.chef.cook(recipe=recipe)
        self.assertIn('default_package', self.chef.history["settings"])

    def test_cook_adds_datasets_source_directory_to_history(self):
        recipe = self.recipe
        recipe_dict = {'datasets': [self.dataset],
                       'tasks': [self.analysis_task],
                       'directories': {'datasets_source': 'foo'}}
        recipe.from_dict(recipe_dict)
        self.chef.cook(recipe=recipe)
        self.assertIn('datasets_source', self.chef.history["directories"])

    def test_cook_with_datasets_source_directory_shortens_dataset_paths(self):
        recipe = self.recipe
        recipe_dict = {'datasets': ['bar'],
                       'tasks': [self.analysis_task],
                       'directories': {'datasets_source': '/foo'}}
        recipe.from_dict(recipe_dict)
        self.chef.cook(recipe=recipe)
        self.assertEqual('bar', self.chef.history["datasets"][0])

    def test_cook_w_datasets_source_dir_w_slash_shortens_dataset_paths(self):
        recipe = self.recipe
        recipe_dict = {'datasets': ['bar'],
                       'tasks': [self.analysis_task],
                       'directories': {'datasets_source': '/foo/'}}
        recipe.from_dict(recipe_dict)
        self.chef.cook(recipe=recipe)
        self.assertEqual('bar', self.chef.history["datasets"][0])

    def test_cook_adds_output_directory_to_history(self):
        recipe = self.recipe
        recipe_dict = {'datasets': [self.dataset],
                       'tasks': [self.analysis_task],
                       'directories': {'output': 'foo'}}
        recipe.from_dict(recipe_dict)
        self.chef.cook(recipe=recipe)
        self.assertIn('output', self.chef.history["directories"])

    def test_system_info_value_in_history_is_ordered_dict(self):
        recipe = self.recipe
        self.chef.cook(recipe)
        self.assertIs(collections.OrderedDict,
                      type(self.chef.history["system_info"]))

    def test_cook_adds_datasets_key_to_history(self):
        recipe = self.recipe
        recipe_dict = {'datasets': [self.dataset],
                       'tasks': [self.processing_task]}
        recipe.from_dict(recipe_dict)
        self.chef.cook(recipe)
        self.assertIn('datasets', self.chef.history)

    def test_datasets_value_in_history_is_list(self):
        recipe = self.recipe
        recipe_dict = {'datasets': [self.dataset],
                       'tasks': [self.processing_task]}
        recipe.from_dict(recipe_dict)
        self.chef.cook(recipe)
        self.assertIs(list, type(self.chef.history["datasets"]))

    def test_datasets_value_in_history_preserves_dicts(self):
        recipe = self.recipe
        dataset_dict = {'source': self.dataset, 'label': 'foo'}
        recipe_dict = {'datasets': [dataset_dict],
                       'tasks': [self.processing_task]}
        recipe.from_dict(recipe_dict)
        self.chef.cook(recipe)
        self.assertDictEqual(dataset_dict, self.chef.history["datasets"][0])

    def test_cook_adds_tasks_key_to_history(self):
        recipe = self.recipe
        self.chef.cook(recipe)
        self.assertIn('tasks', self.chef.history)

    def test_cook_adds_task_history_to_history(self):
        recipe = self.recipe
        recipe_dict = {'datasets': [self.dataset],
                       'tasks': [self.processing_task]}
        recipe.from_dict(recipe_dict)
        self.chef.cook(recipe)
        for key in self.processing_task.keys():
            self.assertIn(key, self.chef.history["tasks"][0])

    def test_cook_adds_info_key_to_history(self):
        recipe = self.recipe
        self.chef.cook(recipe)
        self.assertIn('info', self.chef.history)

    def test_info_key_in_history_contains_correct_fields(self):
        recipe = self.recipe
        self.chef.cook(recipe)
        for key in ['start', 'end']:
            self.assertIn(key, self.chef.history["info"])

    def test_info_key_in_history_contains_correct_start_timestamp(self):
        recipe = self.recipe
        self.chef.cook(recipe)
        try:
            timestamp = datetime.datetime.now().isoformat(timespec='minutes')
        except TypeError:
            timestamp = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M')
        self.assertTrue(self.chef.history["info"]["start"].startswith(
            timestamp))

    def test_info_key_in_history_contains_correct_end_timestamp(self):
        recipe = self.recipe
        self.chef.cook(recipe)
        try:
            timestamp = datetime.datetime.now().isoformat(timespec='minutes')
        except TypeError:
            timestamp = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M')
        self.assertTrue(self.chef.history["info"]["end"].startswith(
            timestamp))

    def test_cook_adds_autosave_plots_to_history(self):
        recipe = self.recipe
        recipe_dict = {'datasets': [self.dataset],
                       'tasks': [self.analysis_task]}
        recipe.from_dict(recipe_dict)
        self.chef.cook(recipe=recipe)
        self.assertIn('autosave_plots', self.chef.history["settings"])
        self.assertTrue(self.chef.history["settings"]["autosave_plots"])


class TestTask(unittest.TestCase):
    def setUp(self):
        self.task = tasks.Task()

    def test_instantiate_class(self):
        pass

    def test_has_kind_property(self):
        self.assertTrue(hasattr(self.task, 'kind'))

    def test_has_type_property(self):
        self.assertTrue(hasattr(self.task, 'type'))

    def test_has_package_property(self):
        self.assertTrue(hasattr(self.task, 'package'))

    def test_has_properties_property(self):
        self.assertTrue(hasattr(self.task, 'properties'))

    def test_has_apply_to_property(self):
        self.assertTrue(hasattr(self.task, 'apply_to'))

    def test_has_recipe_property(self):
        self.assertTrue(hasattr(self.task, 'recipe'))

    def test_has_recipe_property(self):
        self.assertTrue(hasattr(self.task, 'comment'))

    def test_instantiate_with_recipe_sets_recipe(self):
        recipe = tasks.Recipe()
        task = tasks.Task(recipe=recipe)
        self.assertEqual(recipe, task.recipe)

    def test_apply_to_is_empty(self):
        self.assertEqual(0, len(self.task.apply_to))

    def test_has_to_dict_method(self):
        self.assertTrue(hasattr(self.task, 'to_dict'))
        self.assertTrue(callable(self.task.to_dict))

    def test_to_dict_does_not_contain_package_key(self):
        dict_ = self.task.to_dict()
        self.assertNotIn('package', dict_)

    def test_has_from_dict_method(self):
        self.assertTrue(hasattr(self.task, 'from_dict'))
        self.assertTrue(callable(self.task.from_dict))

    def test_from_dict_without_dict_raises(self):
        with self.assertRaises(aspecd.exceptions.MissingDictError):
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

    def test_from_dict_with_apply_to_appends_to_list(self):
        dataset_id = 'foo'
        dict_ = {'apply_to': dataset_id}
        self.task.from_dict(dict_)
        self.assertTrue(isinstance(self.task.apply_to, list))
        self.assertEqual(dataset_id, self.task.apply_to[0])

    def test_from_dict_with_apply_to_is_none_does_not_append(self):
        dict_ = {'apply_to': None}
        self.task.from_dict(dict_)
        self.assertTrue(isinstance(self.task.apply_to, list))
        self.assertEqual([], self.task.apply_to)

    def test_from_dict_does_not_set_unknown_attribute(self):
        attribute = 'foo'
        dict_ = dict()
        dict_[attribute] = 'foo'
        with warnings.catch_warnings(record=True) as warning:
            self.task.from_dict(dict_)
        self.assertFalse(hasattr(self.task, attribute))

    def test_from_dict_with_unknown_attribute_warns(self):
        attribute = 'foo'
        dict_ = dict()
        dict_[attribute] = 'foo'
        with self.assertLogs(__package__, level='WARNING') as cm:
            self.task.from_dict(dict_)
        self.assertIn('Unknown key', cm.output[0])
        self.assertFalse(hasattr(self.task, attribute))

    def test_has_perform_method(self):
        self.assertTrue(hasattr(self.task, 'perform'))
        self.assertTrue(callable(self.task.perform))

    def test_perform_without_recipe_raises(self):
        with self.assertRaises(aspecd.exceptions.MissingRecipeError):
            self.task.perform()

    def test_get_object_with_full_class_name_returns_correct_object(self):
        kind = 'aspecd.processing'
        type_ = 'SingleProcessingStep'
        self.task.kind = kind
        self.task.type = type_
        obj = self.task.get_object()
        self.assertTrue(isinstance(obj, processing.SingleProcessingStep))

    def test_get_object_without_package_name_returns_correct_object(self):
        kind = 'processing'
        type_ = 'SingleProcessingStep'
        self.task.kind = kind
        self.task.type = type_
        obj = self.task.get_object()
        self.assertTrue(isinstance(obj, processing.SingleProcessingStep))

    def test_get_object_existing_in_aspecd_but_not_in_current_package(self):
        kind = 'processing'
        type_ = 'SingleProcessingStep'
        self.task.kind = kind
        self.task.type = type_
        self.task.package = 'foobar'
        obj = self.task.get_object()
        self.assertTrue(isinstance(obj, processing.SingleProcessingStep))

    def test_get_object_sets_object_attributes(self):
        kind = 'processing'
        type_ = 'SingleProcessingStep'
        metadata = {'parameters': {'foo': 'bar'}}
        self.task.kind = kind
        self.task.type = type_
        self.task.properties = metadata
        obj = self.task.get_object()
        self.assertEqual(metadata['parameters'], getattr(obj, 'parameters'))

    def test_get_object_sets_only_existing_object_attributes(self):
        kind = 'processing'
        type_ = 'SingleProcessingStep'
        metadata = {'foo': {'foo': 'bar'}}
        self.task.kind = kind
        self.task.type = type_
        self.task.properties = metadata
        obj = self.task.get_object()
        self.assertFalse(hasattr(obj, 'foo'))

    def test_get_object_with_not_existing_object_attributes_logs_message(self):
        kind = 'processing'
        type_ = 'SingleProcessingStep'
        metadata = {'foo': {'foo': 'bar'}}
        self.task.kind = kind
        self.task.type = type_
        self.task.properties = metadata
        with self.assertLogs(__package__, level='DEBUG') as cm:
            self.task.get_object()
        self.assertIn('"{}" has no property "{}".'.format(type_, "foo"),
                      cm.output[0])

    # ATTENTION: The following tests access protected methods - due to not
    # knowing better how to do it properly for the time being...
    def test_set_object_attributes_sets_field_in_dict(self):
        processing_step = processing.SingleProcessingStep()
        processing_step.parameters = {'foo': 'a', 'bar': 'b'}
        metadata = {'parameters': {'foo': 'bar'}}
        self.task.properties = metadata
        self.task._set_object_attributes(processing_step)
        self.assertEqual(metadata['parameters']['foo'],
                         processing_step.parameters['foo'])

    def test_set_object_attributes_sets_fields_in_dict(self):
        processing_step = processing.SingleProcessingStep()
        processing_step.parameters = {'foo': 'a', 'bar': 'b'}
        metadata = {'parameters': {'foo': 'bar', 'bar': 'foo'}}
        self.task.properties = metadata
        self.task._set_object_attributes(processing_step)
        self.assertEqual(metadata['parameters']['foo'],
                         processing_step.parameters['foo'])
        self.assertEqual(metadata['parameters']['bar'],
                         processing_step.parameters['bar'])

    def test_set_object_attributes_sets_fields_in_object_in_list(self):
        processing_step = processing.SingleProcessingStep()
        processing_step.parameters = {'foo': [aspecd.dataset.Axis()]}
        metadata = {'parameters': {'foo': [{'unit': 'foo'}]}}
        self.task.properties = metadata
        self.task._set_object_attributes(processing_step)
        self.assertEqual(metadata['parameters']['foo'][0]['unit'],
                         processing_step.parameters['foo'][0].unit)

    def test_set_object_attributes_sets_fields_in_objects_in_list(self):
        processing_step = processing.SingleProcessingStep()
        processing_step.parameters = {'foo': [aspecd.dataset.Axis(),
                                              aspecd.dataset.Axis()]}
        metadata = {'parameters': {'foo': [{'unit': 'foo'}, {'unit': 'bar'}]}}
        self.task.properties = metadata
        self.task._set_object_attributes(processing_step)
        self.assertEqual(metadata['parameters']['foo'][0]['unit'],
                         processing_step.parameters['foo'][0].unit)
        self.assertEqual(metadata['parameters']['foo'][1]['unit'],
                         processing_step.parameters['foo'][1].unit)

    def test_set_object_attributes_sets_fields_in_empty_list(self):
        processing_step = processing.SingleProcessingStep()
        processing_step.parameters = {'foo': []}
        metadata = {'parameters': {'foo': [35, 42]}}
        self.task.properties = metadata
        self.task._set_object_attributes(processing_step)
        self.assertEqual(metadata['parameters']['foo'][0],
                         processing_step.parameters['foo'][0])

    def test_set_object_attributes_does_not_override_dict(self):
        processing_step = processing.SingleProcessingStep()
        processing_step.parameters = {'foo': 'a', 'bar': 'b'}
        metadata = {'parameters': {'foo': 'bar'}}
        self.task.properties = metadata
        self.task._set_object_attributes(processing_step)
        self.assertTrue('bar' in processing_step.parameters)

    def test_set_object_attributes_replaces_results_dataset_from_recipe(self):
        processing_step = processing.SingleProcessingStep()
        processing_step.parameters = {'foo': '', 'bar': ''}
        metadata = {'parameters': {'foo': 'bar'}}
        self.task.properties = metadata
        self.task.recipe = tasks.Recipe()
        self.task.recipe.results['bar'] = dataset.Dataset()
        self.task._set_object_attributes(processing_step)
        self.assertEqual(self.task.recipe.results['bar'],
                         processing_step.parameters['foo'])

    def test_set_object_attributes_replaces_results_from_recipe(self):
        processing_step = processing.SingleProcessingStep()
        processing_step.parameters = {'foo': '', 'bar': ''}
        metadata = {'parameters': {'foo': 'bar'}}
        self.task.properties = metadata
        self.task.recipe = tasks.Recipe()
        self.task.recipe.results['bar'] = [0., 1.72, 3.14]
        self.task._set_object_attributes(processing_step)
        self.assertEqual(self.task.recipe.results['bar'],
                         processing_step.parameters['foo'])

    def test_set_object_attributes_replaces_datasets_from_recipe(self):
        processing_step = processing.SingleProcessingStep()
        processing_step.parameters = {'foo': '', 'bar': ''}
        metadata = {'parameters': {'foo': 'bar'}}
        self.task.properties = metadata
        self.task.recipe = tasks.Recipe()
        self.task.recipe.datasets['bar'] = dataset.Dataset()
        self.task._set_object_attributes(processing_step)
        self.assertEqual(self.task.recipe.datasets['bar'],
                         processing_step.parameters['foo'])

    def test_set_object_attributes_replaces_figure_from_recipe(self):
        report_step = report.Reporter()
        report_step.context = {'foo': '', 'bar': ''}
        metadata = {'context': {'foo': 'bar'}}
        self.task.properties = metadata
        self.task.recipe = tasks.Recipe()
        self.task.recipe.figures['bar'] = tasks.FigureRecord()
        self.task._set_object_attributes(report_step)
        self.assertEqual(self.task.recipe.figures['bar'],
                         report_step.context['foo'])

    def test_set_object_attributes_replaces_label(self):
        processing_step = processing.SingleProcessingStep()
        processing_step.parameters = {'foo': '', 'bar': ''}
        metadata = {'parameters': {'foo': '{{ id(bar) }}.pdf'}}
        self.task.properties = metadata
        self.task.recipe = tasks.Recipe()
        self.task.recipe.datasets['bar'] = dataset.Dataset()
        self.task._set_object_attributes(processing_step)
        self.assertEqual('bar.pdf', processing_step.parameters['foo'])

    def test_set_object_attributes_replaces_label_without_spaces(self):
        processing_step = processing.SingleProcessingStep()
        processing_step.parameters = {'foo': '', 'bar': ''}
        metadata = {'parameters': {'foo': '{{id(bar)}}.pdf'}}
        self.task.properties = metadata
        self.task.recipe = tasks.Recipe()
        self.task.recipe.datasets['bar'] = dataset.Dataset()
        self.task._set_object_attributes(processing_step)
        self.assertEqual('bar.pdf', processing_step.parameters['foo'])

    def test_set_object_attributes_replaces_basename(self):
        processing_step = processing.SingleProcessingStep()
        processing_step.parameters = {'foo': '', 'bar': ''}
        metadata = {'parameters': {'foo': '{{ basename(bar) }}.pdf'}}
        self.task.properties = metadata
        self.task.recipe = tasks.Recipe()
        dataset_ = dataset.Dataset()
        dataset_.id = '/foo/bar/bla.blub'
        self.task.recipe.datasets['bar'] = dataset_
        self.task._set_object_attributes(processing_step)
        self.assertEqual('bla.pdf', processing_step.parameters['foo'])

    def test_set_object_attributes_replaces_path(self):
        processing_step = processing.SingleProcessingStep()
        processing_step.parameters = {'foo': '', 'bar': ''}
        metadata = {'parameters': {'foo': '{{ path(bar) }}test.pdf'}}
        self.task.properties = metadata
        self.task.recipe = tasks.Recipe()
        dataset_ = dataset.Dataset()
        dataset_.id = '/foo/bar/bla.blub'
        self.task.recipe.datasets['bar'] = dataset_
        self.task._set_object_attributes(processing_step)
        self.assertEqual('/foo/bar/test.pdf', processing_step.parameters['foo'])

    def test_set_object_attributes_replaces_path_and_basename(self):
        processing_step = processing.SingleProcessingStep()
        processing_step.parameters = {'foo': '', 'bar': ''}
        metadata = {'parameters': {'foo': '{{ path(bar) }}{{ basename('
                                          'bar)}}.pdf'}}
        self.task.properties = metadata
        self.task.recipe = tasks.Recipe()
        dataset_ = dataset.Dataset()
        dataset_.id = '/foo/bar/bla.blub'
        self.task.recipe.datasets['bar'] = dataset_
        self.task._set_object_attributes(processing_step)
        self.assertEqual('/foo/bar/bla.pdf', processing_step.parameters['foo'])

    def test_set_object_attributes_replaces_plotter_from_recipe(self):
        processing_step = processing.SingleProcessingStep()
        processing_step.parameters = {'foo': '', 'bar': ''}
        metadata = {'parameters': {'foo': 'bar'}}
        self.task.properties = metadata
        self.task.recipe = tasks.Recipe()
        self.task.recipe.plotters['bar'] = plotting.Plotter()
        self.task._set_object_attributes(processing_step)
        self.assertEqual(self.task.recipe.plotters['bar'],
                         processing_step.parameters['foo'])

    # The following tests do *not* access non-public methods
    def test_to_dict_with_processing_step(self):
        kind = 'processing'
        type_ = 'SingleProcessingStep'
        self.task.kind = kind
        self.task.type = type_
        self.task.recipe = tasks.Recipe()
        self.task.perform()
        self.task.to_dict()

    def test_to_dict_adds_implicit_parameters_of_task_object(self):
        kind = 'processing'
        type_ = 'Normalisation'
        self.task.kind = kind
        self.task.type = type_
        self.task.recipe = tasks.Recipe()
        self.task.perform()
        dict_ = self.task.to_dict()
        self.assertTrue(dict_["properties"]["parameters"]["kind"])

    def test_to_dict_with_dataset_in_properties_replaces_it_with_label(self):
        kind = 'processing'
        type_ = 'SingleProcessingStep'
        self.task.kind = kind
        self.task.type = type_
        dataset = aspecd.dataset.Dataset()
        recipe = tasks.Recipe()
        recipe.datasets["foo"] = dataset
        self.task.recipe = recipe
        self.task.properties["foo"] = dataset
        self.task.perform()
        dict_ = self.task.to_dict()
        self.assertEqual(dict_["properties"]["foo"], "foo")

    def test_to_dict_with_dataset_from_results_replaces_it_with_label(self):
        kind = 'processing'
        type_ = 'SingleProcessingStep'
        self.task.kind = kind
        self.task.type = type_
        dataset = aspecd.dataset.Dataset()
        recipe = tasks.Recipe()
        recipe.results["foo"] = dataset
        self.task.recipe = recipe
        self.task.properties["foo"] = dataset
        self.task.perform()
        dict_ = self.task.to_dict()
        self.assertEqual(dict_["properties"]["foo"], "foo")

    def test_to_dict_with_value_from_results_replaces_it_with_label(self):
        kind = 'processing'
        type_ = 'SingleProcessingStep'
        self.task.kind = kind
        self.task.type = type_
        value = 3.1415
        recipe = tasks.Recipe()
        recipe.results["foo"] = value
        self.task.recipe = recipe
        self.task.properties["foo"] = value
        self.task.perform()
        dict_ = self.task.to_dict()
        self.assertEqual(dict_["properties"]["foo"], "foo")

    def test_to_dict_with_figure_in_properties_replaces_it_with_label(self):
        kind = 'processing'
        type_ = 'SingleProcessingStep'
        self.task.kind = kind
        self.task.type = type_
        figure_record = tasks.FigureRecord()
        recipe = tasks.Recipe()
        recipe.figures["foo"] = figure_record
        self.task.recipe = recipe
        self.task.properties["foo"] = figure_record
        self.task.perform()
        dict_ = self.task.to_dict()
        self.assertEqual(dict_["properties"]["foo"], "foo")

    def test_to_dict_with_plotter_in_properties_replaces_it_with_label(self):
        kind = 'processing'
        type_ = 'SingleProcessingStep'
        self.task.kind = kind
        self.task.type = type_
        plotter = aspecd.plotting.Plotter()
        recipe = tasks.Recipe()
        recipe.plotters["foo"] = plotter
        self.task.recipe = recipe
        self.task.properties["foo"] = plotter
        self.task.perform()
        dict_ = self.task.to_dict()
        self.assertEqual(dict_["properties"]["foo"], "foo")

    def test_to_dict_with_dataset_in_parameters_replaces_it_with_label(self):
        dataset = aspecd.dataset.Dataset()
        recipe = tasks.Recipe()
        recipe.datasets["foo"] = dataset
        task_dict = {
            'kind': 'processing',
            'type': 'SingleProcessingStep',
            'properties': {'parameters': {'foo': dataset}}
        }
        self.task.from_dict(task_dict)
        self.task.recipe = recipe
        self.task.perform()
        dict_ = self.task.to_dict()
        self.assertEqual(dict_["properties"]["parameters"]["foo"], "foo")

    def test_to_dict_with_result_in_parameters_replaces_it_with_label(self):
        kind = 'processing'
        type_ = 'SingleProcessingStep'
        self.task.kind = kind
        self.task.type = type_
        dataset = aspecd.dataset.Dataset()
        recipe = tasks.Recipe()
        recipe.results["foo"] = dataset
        self.task.recipe = recipe
        self.task.properties["parameters"] = {"foo": dataset}
        self.task.perform()
        dict_ = self.task.to_dict()
        self.assertEqual(dict_["properties"]["parameters"]["foo"], "foo")

    def test_to_dict_with_figure_in_parameters_replaces_it_with_label(self):
        kind = 'processing'
        type_ = 'SingleProcessingStep'
        self.task.kind = kind
        self.task.type = type_
        figure_record = tasks.FigureRecord()
        recipe = tasks.Recipe()
        recipe.figures["foo"] = figure_record
        self.task.recipe = recipe
        self.task.properties["parameters"] = {"foo": figure_record}
        self.task.perform()
        dict_ = self.task.to_dict()
        self.assertEqual(dict_["properties"]["parameters"]["foo"], "foo")

    def test_to_dict_with_plotter_in_parameters_replaces_it_with_label(self):
        self.task.kind = 'processing'
        self.task.type = 'SingleProcessingStep'
        plotter = aspecd.plotting.Plotter()
        recipe = tasks.Recipe()
        recipe.plotters["foo"] = plotter
        self.task.recipe = recipe
        self.task.properties["parameters"] = {"foo": plotter}
        self.task.perform()
        dict_ = self.task.to_dict()
        self.assertEqual(dict_["properties"]["parameters"]["foo"], "foo")

    def test_to_dict_replaces_dataset_in_parameters_subdict_with_label(self):
        dataset = aspecd.dataset.Dataset()
        recipe = tasks.Recipe()
        recipe.datasets["foo"] = dataset
        task_dict = {
            'kind': 'processing',
            'type': 'SingleProcessingStep',
            'properties': {'parameters': {'foo': {'bar': dataset}}}
        }
        self.task.from_dict(task_dict)
        self.task.recipe = recipe
        self.task.perform()
        dict_ = self.task.to_dict()
        self.assertEqual(dict_["properties"]["parameters"]["foo"]["bar"], "foo")

    def test_to_dict_replaces_dataset_in_parameters_subsubdict_with_label(self):
        dataset = aspecd.dataset.Dataset()
        recipe = tasks.Recipe()
        recipe.datasets["foo"] = dataset
        task_dict = {
            'kind': 'processing',
            'type': 'SingleProcessingStep',
            'properties': {'parameters': {'foo': {'bar': {'baz': dataset}}}}
        }
        self.task.from_dict(task_dict)
        self.task.recipe = recipe
        self.task.perform()
        dict_ = self.task.to_dict()
        self.assertEqual(
            dict_["properties"]["parameters"]["foo"]["bar"]["baz"], "foo")

    def test_to_dict_with_remove_empty(self):
        self.task.kind = 'processing'
        self.task.type = 'SingleProcessingStep'
        self.task.properties["parameters"] = {}
        dict_ = self.task.to_dict(remove_empty=True)
        self.assertNotIn("properties", dict_)

    def test_to_yaml_returns_string(self):
        self.assertIsInstance(self.task.to_yaml(), str)

    def test_to_yaml_contains_kind(self):
        self.assertIn('kind: ', self.task.to_yaml())

    def test_to_yaml_with_concrete_type_contains_parameters(self):
        self.task.kind = 'processing'
        self.task.type = 'ProcessingStep'
        self.assertIn('parameters: ', self.task.to_yaml())

    def test_to_yaml_with_numpy_arrays(self):
        self.task.kind = 'plotting'
        self.task.type = 'MultiPlotter1D'
        self.task.to_yaml()

    def test_to_yaml_with_remove_empty(self):
        self.task.kind = 'processing'
        self.task.type = 'SingleProcessingStep'
        self.task.properties["parameters"] = {}
        self.assertNotIn("properties", self.task.to_yaml(remove_empty=True))


class TestProcessingTask(unittest.TestCase):
    def setUp(self):
        self.task = tasks.ProcessingTask()
        self.recipe = tasks.Recipe()
        self.dataset = ['baz']
        self.processing_task = {'kind': 'processing',
                                'type': 'SingleProcessingStep',
                                'apply_to': self.dataset}

    def prepare_recipe(self):
        self.processing_task['apply_to'] = self.dataset
        dataset_factory = dataset.DatasetFactory()
        dataset_factory.importer_factory = aspecd.io.DatasetImporterFactory()
        self.recipe.dataset_factory = dataset_factory
        recipe_dict = {'datasets': self.dataset,
                       'tasks': [self.processing_task]}
        self.recipe.from_dict(recipe_dict)

    def test_instantiate_class(self):
        pass

    def test_perform_task(self):
        self.prepare_recipe()
        self.task.from_dict(self.processing_task)
        self.task.recipe = self.recipe
        self.task.perform()
        self.assertTrue(self.recipe.datasets[self.dataset[0]].history)

    def test_perform_task_issues_log_message(self):
        self.prepare_recipe()
        self.task.from_dict(self.processing_task)
        self.task.recipe = self.recipe
        with self.assertLogs(__package__, level='INFO') as cm:
            self.task.perform()
        self.assertIn('Perform "{}" on dataset "{}"'.format(
            self.processing_task['type'], self.dataset[0]), cm.output[0])

    def test_perform_task_on_multiple_datasets(self):
        self.dataset = ['foo', 'bar']
        self.prepare_recipe()
        self.task.from_dict(self.processing_task)
        self.task.recipe = self.recipe
        self.task.perform()
        for dataset_ in self.recipe.datasets:
            self.assertTrue(self.recipe.datasets[dataset_].history)

    def test_has_result_property(self):
        self.assertTrue(hasattr(self.task, 'result'))

    def test_result_attribute_gets_set_from_dict(self):
        self.prepare_recipe()
        result = 'foo'
        self.processing_task['result'] = result
        self.task.from_dict(self.processing_task)
        self.assertEqual(result, self.task.result)

    def test_perform_task_with_result_adds_result(self):
        self.prepare_recipe()
        result = 'foo'
        self.processing_task['result'] = result
        self.task.from_dict(self.processing_task)
        self.task.recipe = self.recipe
        self.task.perform()
        self.assertTrue(len(self.recipe.results))

    def test_perform_task_with_result_name_identical_to_dataset_warns(self):
        self.prepare_recipe()
        self.processing_task['result'] = self.dataset[0]
        self.task.from_dict(self.processing_task)
        self.task.recipe = self.recipe
        with self.assertLogs(__package__, level='WARNING') as cm:
            self.task.perform()
        self.assertIn('identical to dataset', cm.output[0])

    def test_perform_task_with_result_issues_log_message(self):
        self.prepare_recipe()
        result = 'foo'
        self.processing_task['result'] = result
        self.task.from_dict(self.processing_task)
        self.task.recipe = self.recipe
        with self.assertLogs(__package__, level='INFO') as cm:
            self.task.perform()
        self.assertIn('Perform "{}" on dataset "{}" resulting in "{}"'.format(
            self.processing_task['type'], self.dataset[0], result),
            cm.output[0])

    def test_perform_task_with_result_and_multiple_datasets_adds_results(self):
        self.prepare_recipe()
        result = ['foo', 'bar']
        recipe_dict = {'datasets': result,
                       'tasks': [self.processing_task]}
        self.recipe.from_dict(recipe_dict)
        self.processing_task['result'] = ['fooz', 'barz']
        self.processing_task['apply_to'] = result
        self.task.from_dict(self.processing_task)
        self.task.recipe = self.recipe
        self.task.perform()
        self.assertEqual(len(result), len(self.recipe.results))

    def test_perform_task_with_comment_adds_comment(self):
        self.processing_task["comment"] = "Lorem ipsum dolor sit amet"
        self.prepare_recipe()
        self.task.from_dict(self.processing_task)
        self.task.recipe = self.recipe
        self.task.perform()
        self.assertEqual(self.processing_task["comment"],
                         self.recipe.datasets[self.dataset[0]].history[
                             0].processing.comment)

    def test_to_dict_adds_params_from_processing_of_task_object(self):
        self.processing_task["type"] = 'BaselineCorrection'
        self.prepare_recipe()
        self.recipe.datasets[self.dataset[0]].data.data = \
            np.random.random(10)+5
        self.task.from_dict(self.processing_task)
        self.task.recipe = self.recipe
        self.task.perform()
        dict_ = self.task.to_dict()
        self.assertTrue(dict_["properties"]["parameters"]["coefficients"])

    def test_to_dict_with_multiple_datasets_and_params_returns_list(self):
        self.dataset = ['foo', 'bar']
        self.processing_task["type"] = 'BaselineCorrection'
        self.prepare_recipe()
        self.recipe.datasets['foo'].data.data = np.random.random(10)+5
        self.recipe.datasets['bar'].data.data = np.random.random(10)+3
        self.task.from_dict(self.processing_task)
        self.task.recipe = self.recipe
        self.task.perform()
        dict_ = self.task.to_dict()
        self.assertIsInstance(dict_, list)

    def test_to_dict_with_multiple_datasets_and_same_params_returns_dict(self):
        self.dataset = ['foo', 'bar']
        self.processing_task["type"] = 'Noise'
        self.prepare_recipe()
        self.recipe.datasets['foo'].data.data = np.random.random(10)+5
        self.recipe.datasets['bar'].data.data = np.random.random(10)+3
        self.task.from_dict(self.processing_task)
        self.task.recipe = self.recipe
        self.task.perform()
        dict_ = self.task.to_dict()
        self.assertIsInstance(dict_, dict)

    def test_to_dict_with_multiple_datasets_and_params_adjusts_apply_to(self):
        self.dataset = ['foo', 'bar']
        self.processing_task["type"] = 'BaselineCorrection'
        self.prepare_recipe()
        self.recipe.datasets['foo'].data.data = np.random.random(10)+5
        self.recipe.datasets['bar'].data.data = np.random.random(10)+3
        self.task.from_dict(self.processing_task)
        self.task.recipe = self.recipe
        self.task.perform()
        dict_ = self.task.to_dict()
        self.assertEqual(dict_[0]['apply_to'], [self.dataset[0]])

    def test_to_dict_with_multiple_datasets_and_params_adjusts_result(self):
        self.dataset = ['foo', 'bar']
        self.processing_task["type"] = 'BaselineCorrection'
        self.processing_task["result"] = ['result1', 'result2']
        self.prepare_recipe()
        self.recipe.datasets['foo'].data.data = np.random.random(10)+5
        self.recipe.datasets['bar'].data.data = np.random.random(10)+3
        self.task.from_dict(self.processing_task)
        self.task.recipe = self.recipe
        self.task.perform()
        dict_ = self.task.to_dict()
        self.assertEqual(dict_[0]['result'], 'result1')

    def test_to_dict_with_numpy_params_does_not_warn(self):
        self.dataset = ['foo', 'bar']
        self.processing_task["type"] = 'BaselineCorrection'
        self.processing_task["result"] = ['result1', 'result2']
        self.prepare_recipe()
        self.recipe.datasets['foo'].data.data = np.random.random(10)+5
        self.recipe.datasets['bar'].data.data = np.random.random(10)+3
        self.task.from_dict(self.processing_task)
        self.task.recipe = self.recipe
        with warnings.catch_warnings(record=True) as warning:
            self.task.perform()
            self.assertFalse(warning)

    def test_to_dict_sets_kind(self):
        dict_ = self.task.to_dict()
        self.assertEqual('processing', dict_['kind'])

    def test_to_dict_with_multiprocessingstep_sets_kind(self):
        self.task.kind = 'processing'
        self.task.type = 'MultiProcessingStep'
        self.task._task = self.task.get_object()
        dict_ = self.task.to_dict()
        self.assertEqual('multiprocessing', dict_['kind'])

    def test_to_dict_with_singleplotter_sets_kind(self):
        self.task.kind = 'plotting'
        self.task.type = 'SinglePlotter1D'
        self.task._task = self.task.get_object()
        dict_ = self.task.to_dict()
        self.assertEqual('singleplot', dict_['kind'])

    def test_to_dict_with_multiplotter_sets_kind(self):
        self.task.kind = 'plotting'
        self.task.type = 'MultiPlotter1D'
        self.task._task = self.task.get_object()
        dict_ = self.task.to_dict()
        self.assertEqual('multiplot', dict_['kind'])

    def test_to_dict_with_compositeplotter_sets_kind(self):
        self.task.kind = 'plotting'
        self.task.type = 'CompositePlotter'
        self.task._task = self.task.get_object()
        dict_ = self.task.to_dict()
        self.assertEqual('compositeplot', dict_['kind'])

    def test_to_dict_with_singleanalysis_sets_kind(self):
        self.task.kind = 'analysis'
        self.task.type = 'SingleAnalysisStep'
        self.task._task = self.task.get_object()
        dict_ = self.task.to_dict()
        self.assertEqual('singleanalysis', dict_['kind'])

    def test_to_dict_with_multianalysis_sets_kind(self):
        self.task.kind = 'analysis'
        self.task.type = 'MultiAnalysisStep'
        self.task._task = self.task.get_object()
        dict_ = self.task.to_dict()
        self.assertEqual('multianalysis', dict_['kind'])

    def test_to_dict_with_aggregatedanalysis_sets_kind(self):
        self.task.kind = 'analysis'
        self.task.type = 'AggregatedAnalysisStep'
        self.task._task = self.task.get_object()
        dict_ = self.task.to_dict()
        self.assertEqual('aggregatedanalysis', dict_['kind'])

    def test_to_yaml_sets_kind(self):
        self.task.to_yaml()
        self.assertEqual('processing', self.task.kind)

    def test_to_yaml_with_actual_type(self):
        self.task.type = 'Normalisation'
        self.task.to_yaml()

    def test_processing_after_plot_task_with_multiple_datasets(self):
        self.dataset = ['foo', 'bar']
        self.processing_task["type"] = 'Noise'
        self.prepare_recipe()
        self.recipe.datasets['foo'].data.data = np.random.random(10)+5
        self.recipe.datasets['bar'].data.data = np.random.random(10)+3
        self.recipe.settings['autosave_plots'] = False
        plot_task = tasks.SingleplotTask()
        plot_task.from_dict({'kind': 'singleplot',
                             'type': 'SinglePlotter1D'})
        plot_task.recipe = self.recipe
        plot_task.perform()
        self.task.from_dict(self.processing_task)
        self.task.recipe = self.recipe
        self.task.perform()
        self.assertEqual(2, len(self.recipe.datasets['foo'].tasks))

    def test_to_dict_with_multiple_datasets_and_dataset_ids(self):
        self.dataset = ['foo', 'bar']
        self.processing_task["type"] = 'DatasetAlgebra'
        self.processing_task["properties"] = {'parameters': {'kind': 'minus',
                                                             'dataset': 'foo'}}
        self.prepare_recipe()
        self.recipe.datasets['foo'].data.data = np.random.random(10)+5
        self.recipe.datasets['bar'].data.data = np.random.random(10)+3
        self.task.recipe = self.recipe
        self.task.from_dict(self.processing_task)
        self.task.perform()
        self.assertEqual('foo', self.task.properties['parameters']['dataset'])


class TestSingleProcessingTask(unittest.TestCase):
    def setUp(self):
        self.task = tasks.SingleprocessingTask()
        self.recipe = tasks.Recipe()
        self.dataset = ['foo']

    def prepare_recipe(self):
        self.processing_task = {'kind': 'singleprocessing',
                                'type': 'SingleProcessingStep',
                                'apply_to': self.dataset}
        dataset_factory = dataset.DatasetFactory()
        dataset_factory.importer_factory = aspecd.io.DatasetImporterFactory()
        self.recipe.dataset_factory = dataset_factory
        recipe_dict = {'datasets': self.dataset,
                       'tasks': [self.processing_task]}
        self.recipe.from_dict(recipe_dict)

    def test_instantiate_class(self):
        pass

    def test_perform_task(self):
        self.prepare_recipe()
        self.task.from_dict(self.processing_task)
        self.task.recipe = self.recipe
        self.task.perform()
        self.assertTrue(self.recipe.datasets[self.dataset[0]].history)


class TestMultiProcessingTask(unittest.TestCase):
    def setUp(self):
        self.task = tasks.MultiprocessingTask()
        self.recipe = tasks.Recipe()
        self.dataset = ['foo']

    def prepare_recipe(self):
        self.processing_task = {'kind': 'multiprocessing',
                                'type': 'MultiProcessingStep',
                                'apply_to': self.dataset}
        dataset_factory = dataset.DatasetFactory()
        dataset_factory.importer_factory = aspecd.io.DatasetImporterFactory()
        self.recipe.dataset_factory = dataset_factory
        recipe_dict = {'datasets': self.dataset,
                       'tasks': [self.processing_task]}
        self.recipe.from_dict(recipe_dict)

    def test_instantiate_class(self):
        pass

    def test_perform_task(self):
        self.prepare_recipe()
        self.task.from_dict(self.processing_task)
        self.task.recipe = self.recipe
        self.task.perform()
        self.assertTrue(self.recipe.datasets[self.dataset[0]].history)

    def test_perform_task_issues_log_message(self):
        self.prepare_recipe()
        self.task.from_dict(self.processing_task)
        self.task.recipe = self.recipe
        with self.assertLogs(__package__, level='INFO') as cm:
            self.task.perform()
        self.assertIn('Perform "{}" on datasets "{}"'.format(
            self.processing_task['type'], self.dataset[0]), cm.output[0])

    def test_perform_task_on_multiple_datasets(self):
        self.dataset = ['foo', 'bar']
        self.prepare_recipe()
        self.task.from_dict(self.processing_task)
        self.task.recipe = self.recipe
        self.task.perform()
        for dataset_ in self.recipe.datasets:
            self.assertTrue(self.recipe.datasets[dataset_].history)

    def test_perform_task_on_multiple_datasets_issues_log_message(self):
        self.dataset = ['foo', 'bar']
        self.prepare_recipe()
        self.task.from_dict(self.processing_task)
        self.task.recipe = self.recipe
        with self.assertLogs(__package__, level='INFO') as cm:
            self.task.perform()
        self.assertIn('Perform "{}" on datasets "{}"'.format(
            self.processing_task['type'], ', '.join(self.dataset)),
            cm.output[0])

    def test_has_result_property(self):
        self.assertTrue(hasattr(self.task, 'result'))

    def test_result_attribute_gets_set_from_dict(self):
        self.prepare_recipe()
        result = 'foo'
        self.processing_task['result'] = result
        self.task.from_dict(self.processing_task)
        self.assertEqual(result, self.task.result)

    def test_perform_task_with_result_adds_result(self):
        self.prepare_recipe()
        result = 'foo'
        self.processing_task['result'] = result
        self.task.from_dict(self.processing_task)
        self.task.recipe = self.recipe
        self.task.perform()
        self.assertTrue(len(self.recipe.results))

    def test_perform_task_with_result_does_not_change_original_dataset(self):
        self.prepare_recipe()
        result = ['foo']
        self.processing_task['result'] = result
        self.task.from_dict(self.processing_task)
        self.task.recipe = self.recipe
        self.task.perform()
        self.assertNotEqual(self.recipe.results[result[0]],
                            self.recipe.datasets[self.dataset[0]])

    def test_perform_task_with_result_sets_id_of_resulting_dataset(self):
        self.prepare_recipe()
        result = ['foofoo']
        self.processing_task['result'] = result
        self.task.from_dict(self.processing_task)
        self.task.recipe = self.recipe
        self.task.perform()
        self.assertEqual(result[0], self.recipe.results[result[0]].id)

    def test_perform_task_with_result_issues_log_message(self):
        self.prepare_recipe()
        result = ['foo']
        self.processing_task['result'] = result
        self.task.from_dict(self.processing_task)
        self.task.recipe = self.recipe
        with self.assertLogs(__package__, level='INFO') as cm:
            self.task.perform()
        self.assertIn('Perform "{}" on datasets "{}" resulting in "{}"'.format(
            self.processing_task['type'], self.dataset[0], result[0]),
            cm.output[0])

    def test_perform_task_with_result_and_multiple_datasets_adds_results(self):
        self.prepare_recipe()
        result = ['foo', 'bar']
        recipe_dict = {'datasets': result,
                       'tasks': [self.processing_task]}
        self.recipe.from_dict(recipe_dict)
        self.processing_task['result'] = result
        self.processing_task['apply_to'] = result
        self.task.from_dict(self.processing_task)
        self.task.recipe = self.recipe
        self.task.perform()
        self.assertEqual(len(result), len(self.recipe.results))

    def test_perform_task_with_result_name_identical_to_dataset_warns(self):
        self.prepare_recipe()
        self.processing_task['result'] = self.dataset
        self.task.from_dict(self.processing_task)
        self.task.recipe = self.recipe
        with self.assertLogs(__package__, level='WARNING') as cm:
            self.task.perform()
        self.assertIn('identical to dataset', cm.output[0])


class TestAnalysisTask(unittest.TestCase):
    def setUp(self):
        self.task = tasks.AnalysisTask()
        self.recipe = tasks.Recipe()
        self.dataset = ['foo']

    def prepare_recipe(self):
        self.analysis_task = {'kind': 'analysis',
                              'type': 'AnalysisStep',
                              'apply_to': self.dataset}
        dataset_factory = dataset.DatasetFactory()
        dataset_factory.importer_factory = aspecd.io.DatasetImporterFactory()
        self.recipe.dataset_factory = dataset_factory
        recipe_dict = {'datasets': self.dataset,
                       'tasks': [self.analysis_task]}
        self.recipe.from_dict(recipe_dict)

    def test_instantiate_class(self):
        pass

    def test_has_result_property(self):
        self.assertTrue(hasattr(self.task, 'result'))

    def test_perform_issues_warning(self):
        self.prepare_recipe()
        self.task.from_dict(self.analysis_task)
        self.task.recipe = self.recipe
        message = "Don't use AnalysisTask directly, but rather"
        with self.assertWarnsRegex(UserWarning, message):
            self.task.perform()


class TestSingleAnalysisTask(unittest.TestCase):
    def setUp(self):
        self.task = tasks.SingleanalysisTask()
        self.recipe = tasks.Recipe()
        self.dataset = ['baz']

    def prepare_recipe(self):
        self.analysis_task = {'kind': 'singleanalysis',
                              'type': 'SingleAnalysisStep',
                              'apply_to': self.dataset}
        recipe_dict = {'datasets': self.dataset,
                       'tasks': [self.analysis_task]}
        self.recipe.from_dict(recipe_dict)

    def test_instantiate_class(self):
        pass

    def test_perform_task(self):
        self.prepare_recipe()
        self.task.from_dict(self.analysis_task)
        self.task.recipe = self.recipe
        self.task.perform()
        self.assertTrue(self.recipe.datasets[self.dataset[0]].analyses)

    def test_perform_task_issues_log_message(self):
        self.prepare_recipe()
        self.task.from_dict(self.analysis_task)
        self.task.recipe = self.recipe
        with self.assertLogs(__package__, level='INFO') as cm:
            self.task.perform()
        self.assertIn('Perform "{}" on dataset "{}"'.format(
            self.analysis_task['type'], self.dataset[0]), cm.output[0])

    def test_result_attribute_gets_set_from_dict(self):
        self.prepare_recipe()
        result = 'foo'
        self.analysis_task['result'] = result
        self.task.from_dict(self.analysis_task)
        self.assertEqual(result, self.task.result)

    def test_perform_task_with_result_adds_result(self):
        self.prepare_recipe()
        result = 'foo'
        self.analysis_task['result'] = result
        self.task.from_dict(self.analysis_task)
        self.task.recipe = self.recipe
        self.task.perform()
        self.assertTrue(len(self.recipe.results))

    def test_perform_task_with_result_sets_resulting_dataset_id(self):
        self.prepare_recipe()
        result = 'foo'
        self.analysis_task['result'] = result
        self.task.from_dict(self.analysis_task)
        self.task.recipe = self.recipe
        with patch('aspecd.analysis.SingleAnalysisStep',
                   result=aspecd.dataset.Dataset()) as mock_obj:
            with patch('aspecd.tasks.Task._create_object',
                       return_value=mock_obj):
                self.task.perform()
        self.assertEqual(result, self.recipe.results[result].id)

    def test_perform_task_with_result_name_identical_to_dataset_warns(self):
        self.prepare_recipe()
        self.analysis_task['result'] = self.dataset[0]
        self.task.from_dict(self.analysis_task)
        self.task.recipe = self.recipe
        with patch('aspecd.analysis.SingleAnalysisStep',
                   result=aspecd.dataset.Dataset()) as mock_obj:
            with patch('aspecd.tasks.Task._create_object',
                       return_value=mock_obj):
                with self.assertLogs(__package__, level='WARNING') as cm:
                    self.task.perform()
                self.assertIn('identical to dataset', cm.output[0])

    def test_perform_task_with_result_and_multiple_datasets_adds_results(self):
        self.prepare_recipe()
        result = ['foo', 'bar']
        recipe_dict = {'datasets': result,
                       'tasks': [self.analysis_task]}
        self.recipe.from_dict(recipe_dict)
        self.analysis_task['result'] = result
        self.analysis_task['apply_to'] = result
        self.task.from_dict(self.analysis_task)
        self.task.recipe = self.recipe
        self.task.perform()
        self.assertEqual(len(result), len(self.recipe.results))

    def test_perform_task_with_comment_adds_comment(self):
        self.prepare_recipe()
        self.analysis_task["comment"] = "Lorem ipsum dolor sit amet"
        self.task.from_dict(self.analysis_task)
        self.task.recipe = self.recipe
        self.task.perform()
        self.assertEqual(self.analysis_task["comment"],
                         self.recipe.datasets[self.dataset[0]].analyses[
                             0].analysis.comment)


class TestMultiAnalysisTask(unittest.TestCase):
    def setUp(self):
        self.task = tasks.MultianalysisTask()
        self.recipe = tasks.Recipe()
        self.dataset = ['foo']

    def prepare_recipe(self):
        self.analysis_task = {'kind': 'multianalysis',
                              'type': 'MultiAnalysisStep',
                              'apply_to': self.dataset}
        dataset_factory = dataset.DatasetFactory()
        dataset_factory.importer_factory = aspecd.io.DatasetImporterFactory()
        self.recipe.dataset_factory = dataset_factory
        recipe_dict = {'datasets': self.dataset,
                       'tasks': [self.analysis_task]}
        self.recipe.from_dict(recipe_dict)

    def test_instantiate_class(self):
        pass

    def test_perform_task(self):
        self.prepare_recipe()
        self.task.from_dict(self.analysis_task)
        self.task.recipe = self.recipe
        self.task.perform()

    def test_perform_task_issues_log_message(self):
        self.prepare_recipe()
        self.task.from_dict(self.analysis_task)
        self.task.recipe = self.recipe
        with self.assertLogs(__package__, level='INFO') as cm:
            self.task.perform()
        self.assertIn('Perform "{}" on datasets "{}"'.format(
            self.analysis_task['type'], ', '.join(self.dataset)), cm.output[0])

    def test_result_attribute_gets_set_from_dict(self):
        self.prepare_recipe()
        result = 'foo'
        self.analysis_task['result'] = result
        self.task.from_dict(self.analysis_task)
        self.assertEqual(result, self.task.result)

    def test_result_attribute_as_list_gets_set_from_dict(self):
        self.prepare_recipe()
        result = ['foo', 'bar']
        self.analysis_task['result'] = result
        self.task.from_dict(self.analysis_task)
        self.assertEqual(result, self.task.result)

    def test_perform_task_with_result_adds_result(self):
        self.prepare_recipe()
        result = 'foo'
        self.analysis_task['result'] = result
        self.task.from_dict(self.analysis_task)
        self.task.recipe = self.recipe
        self.task.perform()
        self.assertTrue(len(self.recipe.results))

    def test_perform_task_with_result_name_identical_to_dataset_warns(self):
        self.prepare_recipe()
        self.analysis_task['result'] = self.dataset[0]
        self.task.from_dict(self.analysis_task)
        self.task.recipe = self.recipe
        with patch('aspecd.analysis.MultiAnalysisStep',
                   result=aspecd.dataset.Dataset()) as mock_obj:
            with patch('aspecd.tasks.Task._create_object',
                       return_value=mock_obj):
                with self.assertLogs(__package__, level='WARNING') as cm:
                    self.task.perform()
                self.assertIn('identical to dataset', cm.output[0])

    @unittest.skip
    def test_perform_task_with_result_list_adds_result(self):
        self.dataset = ['foo', 'bar']
        self.prepare_recipe()
        results = ['foo', 'bar']
        self.analysis_task['result'] = results
        self.task.from_dict(self.analysis_task)
        self.task.recipe = self.recipe
        self.task.perform()
        self.assertEqual(len(self.recipe.results), len(results))
        for result in results:
            self.assertEqual(self.recipe.results[result].id, result)


class TestAggregatedAnalysisTask(unittest.TestCase):
    def setUp(self):
        self.task = tasks.AggregatedanalysisTask()
        self.recipe = tasks.Recipe()
        self.dataset = ['foo', 'bar']
        self.result = 'aggregated_result'
        self.analysis_task = {'kind': 'aggregatedanalysis',
                              'type': 'BasicCharacteristics',
                              'properties': {'parameters': {'kind': 'min'}},
                              'apply_to': self.dataset,
                              'result': self.result}

    def prepare_recipe(self):
        recipe_dict = {'datasets': self.dataset,
                       'tasks': [self.analysis_task]}
        self.recipe.from_dict(recipe_dict)
        self.recipe.datasets[self.dataset[0]].data.data = np.zeros(5)
        self.recipe.datasets[self.dataset[1]].data.data = np.ones(5)
        self.recipe.datasets[self.dataset[0]].label = self.dataset[0]
        self.recipe.datasets[self.dataset[1]].label = self.dataset[1]

    def test_instantiate_class(self):
        pass

    def test_perform_task_returns_calculated_dataset_in_result(self):
        self.prepare_recipe()
        self.task.from_dict(self.analysis_task)
        self.task.recipe = self.recipe
        self.task.perform()
        self.assertIsInstance(self.recipe.results[self.result],
                              aspecd.dataset.CalculatedDataset)

    def test_perform_task_with_result_name_identical_to_dataset_warns(self):
        self.prepare_recipe()
        self.analysis_task['result'] = self.dataset[0]
        self.task.from_dict(self.analysis_task)
        self.task.recipe = self.recipe
        with self.assertLogs(__package__, level='WARNING') as cm:
            self.task.perform()
        self.assertIn('identical to dataset', cm.output[0])

    def test_perform_task_sets_values_in_result(self):
        self.prepare_recipe()
        self.task.from_dict(self.analysis_task)
        self.task.recipe = self.recipe
        self.task.perform()
        self.assertEqual(len(self.dataset),
                         len(self.recipe.results[self.result].data.data))

    def test_perform_task_sets_correct_values_in_result(self):
        self.prepare_recipe()
        self.task.from_dict(self.analysis_task)
        self.task.recipe = self.recipe
        self.task.perform()
        self.assertEqual(0., self.recipe.results[self.result].data.data[0])
        self.assertEqual(1., self.recipe.results[self.result].data.data[1])

    def test_perform_task_sets_index_in_result(self):
        self.prepare_recipe()
        self.task.from_dict(self.analysis_task)
        self.task.recipe = self.recipe
        self.task.perform()
        self.assertEqual(self.dataset,
                         self.recipe.results[self.result].data.axes[0].index)

    def test_perform_task_issues_log_message(self):
        self.prepare_recipe()
        self.task.from_dict(self.analysis_task)
        self.task.recipe = self.recipe
        with self.assertLogs(__package__, level='INFO') as cm:
            self.task.perform()
        self.assertIn('Perform "{}" on datasets "{}" resulting in "{}"'.format(
            self.analysis_task['type'], ', '.join(self.dataset), self.result),
            cm.output[0])

    def test_to_dict_contains_original_type(self):
        self.prepare_recipe()
        self.task.from_dict(self.analysis_task)
        self.task.recipe = self.recipe
        self.task.perform()
        dict_ = self.task.to_dict()
        self.assertEqual(self.analysis_task['type'], dict_['type'])


class TestAnnotationTask(unittest.TestCase):
    def setUp(self):
        self.task = tasks.AnnotationTask()
        self.recipe = tasks.Recipe()
        self.dataset = ['foo']

    def prepare_recipe(self):
        self.annotation_task = {'kind': 'annotation',
                                'type': 'Comment',
                                'apply_to': self.dataset}
        dataset_factory = dataset.DatasetFactory()
        dataset_factory.importer_factory = aspecd.io.DatasetImporterFactory()
        self.recipe.dataset_factory = dataset_factory
        recipe_dict = {'datasets': self.dataset,
                       'tasks': [self.annotation_task]}
        self.recipe.from_dict(recipe_dict)

    def test_instantiate_class(self):
        pass

    def test_perform_task(self):
        self.prepare_recipe()
        self.task.from_dict(self.annotation_task)
        self.task.recipe = self.recipe
        self.task.perform()
        self.assertTrue(self.recipe.datasets[self.dataset[0]].annotations)

    def test_perform_task_issues_log_message(self):
        self.prepare_recipe()
        self.task.from_dict(self.annotation_task)
        self.task.recipe = self.recipe
        with self.assertLogs(__package__, level='INFO') as cm:
            self.task.perform()
        self.assertIn('Perform "{}" on dataset "{}"'.format(
            self.annotation_task['type'], self.dataset[0]), cm.output[0])

    def test_to_dict_sets_kind(self):
        dict_ = self.task.to_dict()
        self.assertEqual('annotation', dict_['kind'])


class TestPlotTask(unittest.TestCase):
    def setUp(self):
        self.task = tasks.PlotTask()
        self.recipe = tasks.Recipe()
        self.dataset = ['foo']
        self.plotting_task = {'kind': 'plot',
                              'type': 'Plotter',
                              'apply_to': self.dataset}

    def prepare_recipe(self):
        dataset_factory = dataset.DatasetFactory()
        dataset_factory.importer_factory = aspecd.io.DatasetImporterFactory()
        self.recipe.dataset_factory = dataset_factory
        recipe_dict = {'datasets': self.dataset,
                       'tasks': [self.plotting_task]}
        self.recipe.from_dict(recipe_dict)

    def test_instantiate_class(self):
        pass

    def test_perform_task(self):
        self.prepare_recipe()
        self.task.from_dict(self.plotting_task)
        self.task.recipe = self.recipe
        self.task.perform()

    def test_has_label_property(self):
        self.assertTrue(hasattr(self.task, 'label'))

    def test_label_attribute_gets_set_from_dict(self):
        self.prepare_recipe()
        label = 'foo'
        self.plotting_task['label'] = label
        self.task.from_dict(self.plotting_task)
        self.assertEqual(label, self.task.label)

    def test_perform_task_without_label_adds_figure_to_recipe(self):
        self.prepare_recipe()
        self.task.from_dict(self.plotting_task)
        self.task.recipe = self.recipe
        self.task.perform()
        self.assertTrue(len(self.recipe.figures))

    def test_perform_task_without_label_sets_default_label(self):
        self.prepare_recipe()
        self.task.from_dict(self.plotting_task)
        self.task.recipe = self.recipe
        self.task.perform()
        self.assertIn('fig1', self.recipe.figures)

    def test_perform_task_with_label_adds_figure_to_recipe(self):
        self.prepare_recipe()
        label = 'foo'
        self.plotting_task['label'] = label
        self.task.from_dict(self.plotting_task)
        self.task.recipe = self.recipe
        self.task.perform()
        self.assertTrue(len(self.recipe.figures))

    def test_perform_task_with_label_adds_label_to_figure_record(self):
        self.prepare_recipe()
        label = 'foo'
        self.plotting_task['label'] = label
        self.task.from_dict(self.plotting_task)
        self.task.recipe = self.recipe
        self.task.perform()
        self.assertEqual(label, self.recipe.figures[label].label)

    def test_figure_added_to_recipe_is_figure_record(self):
        self.prepare_recipe()
        label = 'foo'
        self.plotting_task['label'] = label
        self.task.from_dict(self.plotting_task)
        self.task.recipe = self.recipe
        self.task.perform()
        self.assertTrue(isinstance(self.recipe.figures[label],
                                   tasks.FigureRecord))

    def test_figure_added_to_recipe_contains_content_from_task(self):
        self.prepare_recipe()
        label = 'foo'
        self.plotting_task['label'] = label
        # noinspection PyTypeChecker
        self.plotting_task['properties'] = {
            'caption': {
                'title': 'My fancy figure title',
            }
        }
        self.task.from_dict(self.plotting_task)
        self.task.recipe = self.recipe
        self.task.perform()
        # noinspection PyTypeChecker
        self.assertEqual(self.plotting_task['properties']['caption']['title'],
                         self.recipe.figures[label].caption.title)

    def test_has_result_property(self):
        self.assertTrue(hasattr(self.task, 'result'))

    def test_result_attribute_gets_set_from_dict(self):
        self.prepare_recipe()
        result = 'foo'
        self.plotting_task['result'] = result
        self.task.from_dict(self.plotting_task)
        self.assertEqual(result, self.task.result)

    def test_perform_task_with_result_adds_plotter(self):
        self.prepare_recipe()
        result = 'foo'
        self.plotting_task['result'] = result
        self.task.from_dict(self.plotting_task)
        self.task.recipe = self.recipe
        self.task.perform()
        self.assertTrue(len(self.recipe.plotters))

    def test_has_target_property(self):
        self.assertTrue(hasattr(self.task, 'target'))

    def test_to_dict_adds_properties_to_properties(self):
        self.task.from_dict(self.plotting_task)
        self.task._task = self.task.get_object()
        dict_ = self.task.to_dict()
        self.assertIn('properties', dict_['properties'])


class TestSinglePlotTask(unittest.TestCase):
    def setUp(self):
        self.task = tasks.SingleplotTask()
        self.recipe = tasks.Recipe()
        self.dataset = ['foo']
        self.figure_filename = 'foo.pdf'
        self.datasets = ['foo', 'bar']
        self.figure_filenames = ['foo.pdf', 'bar.pdf']
        self.plotting_task = {'kind': 'singleplot',
                              'type': 'SinglePlotter',
                              'apply_to': self.dataset}
        self.recipe_dict = {'datasets': self.dataset,
                            'tasks': [self.plotting_task]}
        root_path = os.path.split(os.path.abspath(__file__))[0]
        self.output_directory = os.path.join(root_path, 'output_directory')
        os.mkdir(self.output_directory)

    def tearDown(self):
        if os.path.exists(self.figure_filename):
            os.remove(self.figure_filename)
        for file in self.figure_filenames:
            if os.path.exists(file):
                os.remove(file)
        if os.path.exists(self.output_directory):
            shutil.rmtree(self.output_directory)
        # Remove autogenerated files
        if self.task._task and self.task._task.filename:
            if isinstance(self.task._task.filename, list):
                for filename in self.task._task.filename:
                    if os.path.exists(filename):
                        os.remove(filename)
            elif os.path.exists(self.task._task.filename):
                os.remove(self.task._task.filename)

    def prepare_recipe(self):
        dataset_factory = dataset.DatasetFactory()
        dataset_factory.importer_factory = aspecd.io.DatasetImporterFactory()
        self.recipe.dataset_factory = dataset_factory
        self.recipe.from_dict(self.recipe_dict)

    def test_instantiate_class(self):
        pass

    def test_perform_task(self):
        self.prepare_recipe()
        self.task.from_dict(self.plotting_task)
        self.task.recipe = self.recipe
        self.task.perform()
        self.assertTrue(self.recipe.datasets[self.dataset[0]].representations)

    def test_perform_task_issues_log_message(self):
        self.prepare_recipe()
        self.task.from_dict(self.plotting_task)
        self.task.recipe = self.recipe
        with self.assertLogs(__package__, level='INFO') as cm:
            self.task.perform()
        self.assertIn('Perform "{}" on dataset "{}"'.format(
            self.plotting_task['type'], self.dataset[0]), cm.output[0])

    def test_perform_task_with_filename_saves_plot(self):
        self.prepare_recipe()
        # noinspection PyTypeChecker
        self.plotting_task['properties'] = {'filename': self.figure_filename}
        self.task.from_dict(self.plotting_task)
        self.task.recipe = self.recipe
        self.task.perform()
        self.assertTrue(os.path.exists(self.figure_filename))

    def test_figure_added_to_recipe_contains_filename_with_output_dir(self):
        self.prepare_recipe()
        output_directory = 'outputdir'
        self.recipe.directories['output'] = output_directory
        # noinspection PyTypeChecker
        label = 'foo'
        self.plotting_task['label'] = label
        self.plotting_task['properties'] = {'filename': self.figure_filename}
        self.task.from_dict(self.plotting_task)
        self.task.recipe = self.recipe
        if not os.path.exists(output_directory):
            os.mkdir(output_directory)
        self.task.perform()
        self.assertEqual(os.path.join('outputdir', 'foo.pdf'),
                         self.recipe.figures[label].filename)
        shutil.rmtree(output_directory)

    def test_perform_task_with_filename_issues_log_message(self):
        self.prepare_recipe()
        # noinspection PyTypeChecker
        self.plotting_task['properties'] = {'filename': self.figure_filename}
        self.task.from_dict(self.plotting_task)
        self.task.recipe = self.recipe
        with self.assertLogs(__package__, level='INFO') as cm:
            self.task.perform()
        self.assertIn('Save figure from "{}" to file "{}"'.format(
            self.plotting_task['type'], self.figure_filename), cm.output[1])

    def test_perform_task_with_list_of_filenames_saves_plots(self):
        self.plotting_task = {'kind': 'singleplot',
                              'type': 'SinglePlotter',
                              'apply_to': self.datasets}
        dataset_factory = dataset.DatasetFactory()
        dataset_factory.importer_factory = aspecd.io.DatasetImporterFactory()
        self.recipe.dataset_factory = dataset_factory
        recipe_dict = {'datasets': self.datasets,
                       'tasks': [self.plotting_task]}
        self.recipe.from_dict(recipe_dict)
        # noinspection PyTypeChecker
        self.plotting_task['properties'] = {'filename': self.figure_filenames}
        self.task.from_dict(self.plotting_task)
        self.task.recipe = self.recipe
        self.task.perform()
        for file in self.figure_filenames:
            self.assertTrue(os.path.exists(file))

    def test_perform_task_without_filename_saves_plot_to_default_name(self):
        self.figure_filename = \
            "".join([self.dataset[0], "_", self.plotting_task["type"], ".pdf"])
        self.prepare_recipe()
        self.task.from_dict(self.plotting_task)
        self.task.recipe = self.recipe
        self.task.perform()
        self.assertTrue(os.path.exists(self.figure_filename))

    def test_perform_task_without_filename_saves_plots_to_default_names(self):
        self.plotting_task = {'kind': 'singleplot',
                              'type': 'SinglePlotter',
                              'apply_to': self.datasets}
        self.figure_filenames = []
        for name in self.datasets:
            self.figure_filenames.append(
                "".join([name, "_", self.plotting_task["type"], ".pdf"])
            )
        dataset_factory = dataset.DatasetFactory()
        dataset_factory.importer_factory = aspecd.io.DatasetImporterFactory()
        self.recipe.dataset_factory = dataset_factory
        recipe_dict = {'datasets': self.datasets,
                       'tasks': [self.plotting_task]}
        self.recipe.from_dict(recipe_dict)
        # noinspection PyTypeChecker
        self.task.from_dict(self.plotting_task)
        self.task.recipe = self.recipe
        self.task.perform()
        for name in self.figure_filenames:
            self.assertTrue(os.path.exists(name))

    def test_perform_task_autosaving_adds_filename_to_task(self):
        self.figure_filename = \
            "".join([self.dataset[0], "_", self.plotting_task["type"], ".pdf"])
        self.prepare_recipe()
        self.task.from_dict(self.plotting_task)
        self.task.recipe = self.recipe
        self.task.perform()
        self.assertTrue(self.task.properties['filename'])

    def test_perform_task_autosaving_adds_filenames_to_figure_record(self):
        self.plotting_task = {'kind': 'singleplot',
                              'type': 'SinglePlotter',
                              'apply_to': self.datasets}
        self.figure_filenames = []
        for name in self.datasets:
            self.figure_filenames.append(
                "".join([name, "_", self.plotting_task["type"], ".pdf"])
            )
        dataset_factory = dataset.DatasetFactory()
        dataset_factory.importer_factory = aspecd.io.DatasetImporterFactory()
        self.recipe.dataset_factory = dataset_factory
        recipe_dict = {'datasets': self.datasets,
                       'tasks': [self.plotting_task]}
        self.recipe.from_dict(recipe_dict)
        # noinspection PyTypeChecker
        self.task.from_dict(self.plotting_task)
        self.task.recipe = self.recipe
        self.task.perform()
        self.assertListEqual(self.figure_filenames,
                             self.recipe.figures['fig1'].filename)

    def test_perform_task_wo_filename_wo_autosave_does_not_save_plot(self):
        self.figure_filename = \
            "".join([self.dataset[0], "_", self.plotting_task["type"], ".pdf"])
        self.prepare_recipe()
        self.recipe.settings['autosave_plots'] = False
        self.task.from_dict(self.plotting_task)
        self.task.recipe = self.recipe
        self.task.perform()
        self.assertFalse(os.path.exists(self.figure_filename))

    def test_set_line_colour_from_properties(self):
        self.plotting_task["properties"] = \
            {'properties': {'drawing': {'color': '#cccccc'}}}
        self.prepare_recipe()
        self.task.from_dict(self.plotting_task)
        self.task.recipe = self.recipe
        self.task.perform()

    def test_perform_task_with_filename_and_output_directory_saves_plot(self):
        self.prepare_recipe()
        self.recipe.directories['output'] = self.output_directory
        # noinspection PyTypeChecker
        self.plotting_task['properties'] = {'filename': self.figure_filename}
        self.task.from_dict(self.plotting_task)
        self.task.recipe = self.recipe
        self.task.perform()
        self.assertTrue(os.path.exists(os.path.join(self.output_directory,
                                                    self.figure_filename)))

    def test_perform_task_closes_figure(self):
        self.prepare_recipe()
        self.task.from_dict(self.plotting_task)
        self.task.recipe = self.recipe
        self.task.perform()
        self.assertFalse(plt.fignum_exists(self.task._task.figure.number))

    def test_perform_task_with_result_does_not_close_figure(self):
        self.prepare_recipe()
        self.plotting_task["result"] = 'foo'
        self.task.from_dict(self.plotting_task)
        self.task.recipe = self.recipe
        self.task.perform()
        self.assertTrue(plt.fignum_exists(self.task._task.figure.number))

    def test_perform_task_with_target_sets_figure_and_axes(self):
        self.prepare_recipe()
        plotting_task2 = copy.copy(self.plotting_task)
        plotting_task2["result"] = 'bar'
        plotting_task2["target"] = 'foo'
        self.recipe.tasks.append(plotting_task2)
        task2 = copy.copy(self.task)
        self.plotting_task["result"] = plotting_task2["target"]
        self.task.from_dict(self.plotting_task)
        self.task.recipe = self.recipe
        self.task.perform()
        task2.from_dict(plotting_task2)
        task2.recipe = self.recipe
        task2.perform()
        self.assertEqual(self.task._task.figure.number,
                         task2._task.figure.number)

    def test_perform_task_with_label_adds_label_to_dataset_figure_record(self):
        self.prepare_recipe()
        label = 'foo'
        self.plotting_task['label'] = label
        self.task.from_dict(self.plotting_task)
        self.task.recipe = self.recipe
        self.task.perform()
        self.assertEqual(label, self.recipe.datasets[
            self.dataset[0]].representations[0].plot.label)

    def test_perform_task_wo_label_adds_default_label_to_dataset_fig_rec(self):
        self.prepare_recipe()
        self.task.from_dict(self.plotting_task)
        self.task.recipe = self.recipe
        self.task.perform()
        self.assertEqual('fig1', self.recipe.datasets[
            self.dataset[0]].representations[0].plot.label)

    def test_label_converted_to_dataset_gets_replaced_by_dataset_label(self):
        self.plotting_task['properties'] = \
            {'properties': {'drawing': {'label': self.dataset[0]}}}
        self.prepare_recipe()
        self.task.recipe = self.recipe
        self.task.from_dict(self.plotting_task)
        self.task.perform()
        dict_ = self.task.to_dict()
        self.assertEqual(self.dataset[0],
                         dict_['properties']['properties']['drawing']['label'])


class TestMultiPlotTask(unittest.TestCase):
    def setUp(self):
        self.task = tasks.MultiplotTask()
        self.recipe = tasks.Recipe()
        self.dataset = ['foo']
        self.figure_filename = 'foo.pdf'
        self.plotting_task = {'kind': 'multiplot',
                              'type': 'MultiPlotter',
                              'apply_to': self.dataset}

    def tearDown(self):
        if os.path.exists(self.figure_filename):
            os.remove(self.figure_filename)
        if "filename" in self.task.properties \
                and os.path.exists(self.task.properties["filename"]):
            os.remove(self.task.properties["filename"])

    def prepare_recipe(self):
        dataset_factory = dataset.DatasetFactory()
        dataset_factory.importer_factory = aspecd.io.DatasetImporterFactory()
        self.recipe.dataset_factory = dataset_factory
        recipe_dict = {'datasets': self.dataset,
                       'tasks': [self.plotting_task]}
        self.recipe.from_dict(recipe_dict)

    def test_instantiate_class(self):
        pass

    def test_perform_task(self):
        self.prepare_recipe()
        self.task.from_dict(self.plotting_task)
        self.task.recipe = self.recipe
        self.task.perform()

    def test_perform_task_issues_log_message(self):
        self.prepare_recipe()
        self.task.from_dict(self.plotting_task)
        self.task.recipe = self.recipe
        with self.assertLogs(__package__, level='INFO') as cm:
            self.task.perform()
        self.assertIn('Perform "{}" on datasets "{}"'.format(
            self.plotting_task['type'], ', '.join(self.dataset)), cm.output[0])

    def test_perform_task_with_filename_saves_plot(self):
        self.prepare_recipe()
        # noinspection PyTypeChecker
        self.plotting_task['properties'] = {'filename': self.figure_filename}
        self.task.from_dict(self.plotting_task)
        self.task.recipe = self.recipe
        self.task.perform()
        self.assertTrue(os.path.exists(self.figure_filename))

    def test_perform_task_without_filename_saves_plot_to_default_filename(self):
        self.dataset = ['foo', 'bar']
        self.plotting_task["apply_to"] = self.dataset
        self.figure_filename = \
            "".join(["_".join(self.plotting_task["apply_to"]), "_",
                     self.plotting_task["type"], ".pdf"])
        self.prepare_recipe()
        # noinspection PyTypeChecker
        self.task.from_dict(self.plotting_task)
        self.task.recipe = self.recipe
        self.task.perform()
        self.assertTrue(os.path.exists(self.figure_filename))

    def test_perform_task_wo_filename_adds_default_filename_to_properties(self):
        self.dataset = ['foo', 'bar']
        self.plotting_task["apply_to"] = self.dataset
        self.figure_filename = \
            "".join(["_".join(self.plotting_task["apply_to"]), "_",
                     self.plotting_task["type"], ".pdf"])
        self.prepare_recipe()
        # noinspection PyTypeChecker
        self.task.from_dict(self.plotting_task)
        self.task.recipe = self.recipe
        self.task.perform()
        self.assertEqual(self.figure_filename, self.task.properties["filename"])

    def test_perform_task_wo_filename_wo_autosave_does_not_save_plot(self):
        self.dataset = ['foo', 'bar']
        self.plotting_task["apply_to"] = self.dataset
        self.figure_filename = \
            "".join(["_".join(self.plotting_task["apply_to"]), "_",
                     self.plotting_task["type"], ".pdf"])
        self.prepare_recipe()
        self.recipe.settings['autosave_plots'] = False
        self.task.from_dict(self.plotting_task)
        self.task.recipe = self.recipe
        self.task.perform()
        self.assertFalse(os.path.exists(self.figure_filename))

    def test_perform_task_closes_figure(self):
        self.prepare_recipe()
        self.task.from_dict(self.plotting_task)
        self.task.recipe = self.recipe
        self.task.perform()
        self.assertFalse(plt.fignum_exists(self.task._task.figure.number))

    def test_perform_task_with_result_does_not_close_figure(self):
        self.prepare_recipe()
        self.plotting_task["result"] = 'foo'
        self.task.from_dict(self.plotting_task)
        self.task.recipe = self.recipe
        self.task.perform()
        self.assertTrue(plt.fignum_exists(self.task._task.figure.number))

    def test_perform_task_with_target_sets_figure_and_axes(self):
        self.prepare_recipe()
        plotting_task2 = copy.copy(self.plotting_task)
        plotting_task2["result"] = 'bar'
        plotting_task2["target"] = 'foo'
        self.recipe.tasks.append(plotting_task2)
        task2 = copy.copy(self.task)
        self.plotting_task["result"] = plotting_task2["target"]
        self.task.from_dict(self.plotting_task)
        self.task.recipe = self.recipe
        self.task.perform()
        task2.from_dict(plotting_task2)
        task2.recipe = self.recipe
        task2.perform()
        self.assertEqual(self.task._task.figure.number,
                         task2._task.figure.number)

    def test_label_converted_to_dataset_gets_replaced_by_dataset_label(self):
        self.plotting_task['properties'] = \
            {'properties': {'drawings': [{'label': self.dataset[0]}]}}
        self.prepare_recipe()
        self.task.recipe = self.recipe
        self.task.from_dict(self.plotting_task)
        self.task.perform()
        dict_ = self.task.to_dict()
        self.assertEqual(self.dataset[0],
                         dict_['properties']['properties']['drawings'][0][
                             'label'])


class TestCompositePlotTask(unittest.TestCase):
    def setUp(self):
        self.task = tasks.CompositeplotTask()
        self.pretask = tasks.SingleplotTask()
        self.recipe = tasks.Recipe()
        self.dataset = ['foo']
        self.figure_filename = 'foo.pdf'
        self.singleplotting_task = {'kind': 'singleplot',
                                    'type': 'SinglePlotter1D',
                                    'apply_to': self.dataset,
                                    'result': 'singleplotter'}
        self.multiplotting_task = {'kind': 'multiplot',
                                   'type': 'MultiPlotter1D',
                                   'apply_to': self.dataset,
                                   'result': 'multiplotter'}
        self.plotting_task = {'kind': 'compositeplot',
                              'type': 'CompositePlotter',
                              'properties': {'plotter': ['singleplotter']}}

    def tearDown(self):
        if os.path.exists(self.figure_filename):
            os.remove(self.figure_filename)
        # Remove autogenerated files
        if self.task._task and self.task._task.filename \
                and os.path.exists(self.task._task.filename):
            os.remove(self.task._task.filename)
        if self.pretask._task and self.pretask._task.filename:
            if isinstance(self.pretask._task.filename, list):
                for filename in self.pretask._task.filename:
                    if os.path.exists(filename):
                        os.remove(filename)
            elif os.path.exists(self.pretask._task.filename):
                os.remove(self.pretask._task.filename)

    def prepare_recipe(self):
        dataset_factory = dataset.DatasetFactory()
        dataset_factory.importer_factory = aspecd.io.DatasetImporterFactory()
        self.recipe.dataset_factory = dataset_factory
        recipe_dict = {'datasets': self.dataset,
                       'tasks': [self.singleplotting_task, self.plotting_task]}
        self.recipe.from_dict(recipe_dict)

    def test_instantiate_class(self):
        pass

    def  test_task_has_correct_module(self):
        self.assertEqual('plotting', self.task._module)

    def test_perform_task(self):
        self.prepare_recipe()
        self.pretask.from_dict(self.singleplotting_task)
        self.pretask.recipe = self.recipe
        self.pretask.perform()
        self.task.from_dict(self.plotting_task)
        self.task.recipe = self.recipe
        self.task.perform()
        self.assertTrue(isinstance(self.task._task.plotter[0],
                                   aspecd.plotting.Plotter))

    def test_perform_task_issues_log_message(self):
        self.prepare_recipe()
        self.pretask.from_dict(self.singleplotting_task)
        self.pretask.recipe = self.recipe
        self.pretask.perform()
        self.task.from_dict(self.plotting_task)
        self.task.recipe = self.recipe
        with self.assertLogs(__package__, level='INFO') as cm:
            self.task.perform()
        self.assertIn('Perform "{}"'.format(self.plotting_task['type']),
            cm.output[0])

    def test_perform_task_with_multiplotter(self):
        self.pretask = tasks.MultiplotTask()
        self.plotting_task['properties']['plotter'] = ['multiplotter']
        self.prepare_recipe()
        self.pretask.from_dict(self.multiplotting_task)
        self.pretask.recipe = self.recipe
        self.pretask.perform()
        self.task.from_dict(self.plotting_task)
        self.task.recipe = self.recipe
        self.task.perform()
        self.assertTrue(isinstance(self.task._task.plotter[0],
                                   aspecd.plotting.Plotter))

    def test_perform_task_with_filename_saves_plot(self):
        self.prepare_recipe()
        self.pretask.from_dict(self.singleplotting_task)
        self.pretask.recipe = self.recipe
        self.pretask.perform()
        # noinspection PyTypeChecker
        self.plotting_task['properties']['filename'] = self.figure_filename
        self.task.from_dict(self.plotting_task)
        self.task.recipe = self.recipe
        self.task.perform()
        self.assertTrue(os.path.exists(self.figure_filename))

    def test_task_to_dict(self):
        self.prepare_recipe()
        self.pretask.from_dict(self.singleplotting_task)
        self.pretask.recipe = self.recipe
        self.pretask.perform()
        # noinspection PyTypeChecker
        self.plotting_task['properties']['filename'] = self.figure_filename
        self.task.from_dict(self.plotting_task)
        self.task.recipe = self.recipe
        self.task.perform()
        self.task.to_dict()

    def test_task_to_dict_replaces_plotter_with_label(self):
        self.prepare_recipe()
        self.pretask.from_dict(self.singleplotting_task)
        self.pretask.recipe = self.recipe
        self.pretask.perform()
        # noinspection PyTypeChecker
        self.plotting_task['properties']['filename'] = self.figure_filename
        self.task.from_dict(self.plotting_task)
        self.task.recipe = self.recipe
        self.task.perform()
        dict_ = self.task.to_dict()
        self.assertEqual(self.singleplotting_task['result'],
                         dict_['properties']['plotter'][0])


class TestReportTask(unittest.TestCase):
    def setUp(self):
        self.task = tasks.ReportTask()
        self.recipe = tasks.Recipe()
        self.dataset = '/foo'
        self.template = 'test_template.tex'
        self.filename = 'test_report.tex'
        self.result = 'test_report.pdf'
        self.report_task = {'kind': 'report',
                            'type': 'LaTeXReporter',
                            'properties': {'template': self.template,
                                           'filename': self.filename,
                                           },
                            'apply_to': self.dataset}
        root_path = os.path.split(os.path.abspath(__file__))[0]
        self.output_directory = os.path.join(root_path, 'output_directory')
        os.mkdir(self.output_directory)

    def tearDown(self):
        if os.path.exists(self.template):
            os.remove(self.template)
        if os.path.exists(self.filename):
            os.remove(self.filename)
        if os.path.exists(self.result):
            os.remove(self.result)
        if os.path.exists(self.output_directory):
            shutil.rmtree(self.output_directory)

    def prepare_recipe(self):
        dataset_factory = dataset.DatasetFactory()
        dataset_factory.importer_factory = aspecd.io.DatasetImporterFactory()
        self.recipe.dataset_factory = dataset_factory
        recipe_dict = {'datasets': [self.dataset],
                       'tasks': [self.report_task]}
        self.recipe.from_dict(recipe_dict)

    def prepare_template(self, content=''):
        template_content = content
        with open(self.template, 'w+') as f:
            f.write(template_content)

    def test_instantiate_class(self):
        pass

    def test_perform_task(self):
        self.prepare_recipe()
        template_content = "{@dataset['id']}"
        self.prepare_template(template_content)
        self.task.from_dict(self.report_task)
        self.task.recipe = self.recipe
        self.task.perform()
        self.assertTrue(os.path.exists(self.filename))

    def test_perform_task_issues_log_message(self):
        self.prepare_recipe()
        template_content = "{@dataset['id']}"
        self.prepare_template(template_content)
        self.task.from_dict(self.report_task)
        self.task.recipe = self.recipe
        with self.assertLogs(__package__, level='INFO') as cm:
            self.task.perform()
        self.assertIn('Perform "{}" on dataset "{}"'.format(
            self.report_task['type'], self.dataset), cm.output[0])

    def test_perform_task_adds_dataset_to_context(self):
        self.prepare_recipe()
        template_content = "{@dataset['id']}"
        self.prepare_template(template_content)
        self.task.from_dict(self.report_task)
        self.task.recipe = self.recipe
        self.task.perform()
        with open(self.filename) as f:
            read_content = f.read()
        self.assertEqual(read_content, '/foo')

    def test_perform_task_compiles_template(self):
        self.prepare_recipe()
        template_content = '\\documentclass{article}' \
                           '\\begin{document}' \
                           "{@dataset['id']}" \
                           '\\end{document}'
        self.prepare_template(template_content)
        # noinspection PyTypeChecker
        self.report_task['compile'] = True
        self.task.from_dict(self.report_task)
        self.task.recipe = self.recipe
        with contextlib.redirect_stdout(io.StringIO()):
            self.task.perform()
        self.assertTrue(os.path.exists(self.result))

    def test_perform_task_does_not_compile_if_not_possible(self):
        self.prepare_recipe()
        template_content = "{@dataset['id']}"
        self.prepare_template(template_content)
        # noinspection PyTypeChecker
        self.report_task['compile'] = True
        self.report_task['type'] = 'Reporter'
        self.task.from_dict(self.report_task)
        self.task.recipe = self.recipe
        self.task.perform()

    def test_perform_task_adds_figure_filenames_to_includes(self):
        self.prepare_recipe()
        figure_record = tasks.FigureRecord()
        figure_record.filename = 'bar'
        self.recipe.figures['foo'] = figure_record
        template_content = ""
        self.prepare_template(template_content)
        self.task.from_dict(self.report_task)
        self.task.recipe = self.recipe
        self.task.perform()
        self.assertIn(figure_record.filename, self.task.properties['includes'])

    def test_perform_task_does_not_add_empty_figure_filename_to_includes(self):
        self.prepare_recipe()
        figure_record = tasks.FigureRecord()
        figure_record.filename = ''
        self.recipe.figures['foo'] = figure_record
        template_content = ""
        self.prepare_template(template_content)
        self.task.from_dict(self.report_task)
        self.task.recipe = self.recipe
        self.task.perform()
        self.assertNotIn(figure_record.filename,
                         self.task.properties['includes'])

    def test_perform_task_compiles_template_with_additional_properties(self):
        self.prepare_recipe()
        self.recipe.tasks[0].properties['context'] = \
            {'general': {'title': 'bar'}}
        template_content = "{@general['title']}"
        self.prepare_template(template_content)
        self.task.from_dict(self.report_task)
        self.task.recipe = self.recipe
        self.task.perform()
        with open(self.filename) as f:
            read_content = f.read()
        self.assertEqual(read_content, 'bar')

    def test_perform_task_applies_to_dict_to_datasets_in_context(self):
        self.prepare_recipe()
        self.recipe.datasets[self.dataset].id = 'bar'
        self.recipe.tasks[0].properties['context'] = \
            {'dataset2': self.dataset}
        template_content = "{@dataset2['id']}"
        self.prepare_template(template_content)
        self.task.from_dict(self.report_task)
        self.task.recipe = self.recipe
        self.task.perform()
        with open(self.filename) as f:
            read_content = f.read()
        self.assertEqual(read_content, 'bar')

    def test_perform_task_applies_to_dict_to_datasets_in_deep_context(self):
        self.prepare_recipe()
        self.recipe.datasets[self.dataset].id = 'blub'
        self.recipe.tasks[0].properties['context'] = \
            {'foo': {'bar': {'dataset2': self.dataset}}}
        template_content = "{@foo['bar']['dataset2']['id']}"
        self.prepare_template(template_content)
        self.task.from_dict(self.report_task)
        self.task.recipe = self.recipe
        self.task.perform()
        with open(self.filename) as f:
            read_content = f.read()
        self.assertEqual(read_content, 'blub')

    def test_perform_task_with_multiple_datasets_and_filenames(self):
        # noinspection PyTypedDict
        self.report_task["properties"]["filename"] = \
            ['test-report1.tex', 'test-report2.tex']
        self.report_task.pop("apply_to")
        self.prepare_recipe()
        self.recipe.datasets["bar"] = aspecd.dataset.Dataset()
        template_content = " "
        self.prepare_template(template_content)
        self.task.from_dict(self.report_task)
        self.task.recipe = self.recipe
        self.task.perform()
        for filename in self.report_task["properties"]["filename"]:
            self.assertTrue(os.path.exists(filename))
        # Manual teardown in this case
        for filename in self.report_task["properties"]["filename"]:
            if os.path.exists(filename):
                os.remove(filename)

    def test_report_gets_saved_to_output_directory_if_provided(self):
        self.prepare_recipe()
        template_content = "{@dataset['id']}"
        self.prepare_template(template_content)
        self.task.from_dict(self.report_task)
        self.recipe.directories['output'] = self.output_directory
        self.task.recipe = self.recipe
        self.task.perform()
        self.assertTrue(os.path.exists(os.path.join(self.output_directory,
                                                    self.filename)))

    def test_perform_task_without_filename_saves_report_to_default_name(self):
        self.filename = "_".join([self.dataset[1:], "report", self.template])
        self.prepare_recipe()
        template_content = "{@dataset['id']}"
        self.prepare_template(template_content)
        self.report_task['properties'].pop('filename')
        self.task.from_dict(self.report_task)
        self.task.recipe = self.recipe
        self.task.perform()
        self.assertTrue(os.path.exists(self.filename))

    def test_perform_task_with_language_and_template_from_package(self):
        self.prepare_recipe()
        self.report_task['properties']['template'] = 'abbildung.tex'
        self.report_task['properties']['language'] = 'de'
        self.task.from_dict(self.report_task)
        self.task.recipe = self.recipe
        self.report_task['properties']['context'] = \
            {'figure': {'caption': {'title': '', 'text': ''}}}
        self.task.perform()
        self.assertTrue(os.path.exists(self.filename))


class TestFigureReportTask(unittest.TestCase):
    def setUp(self):
        self.task = tasks.FigurereportTask()
        self.recipe = tasks.Recipe()
        self.template = 'figure.tex'
        self.filename = 'figure-caption.tex'
        self.figure = 'fig'
        self.report_task = {'kind': 'figurereport',
                            'type': 'LaTeXReporter',
                            'properties': {'template': self.template,
                                           'filename': self.filename,
                                           },
                            'apply_to': self.figure}
        self.figure_record = aspecd.tasks.FigureRecord()
        root_path = os.path.split(os.path.abspath(__file__))[0]
        self.output_directory = os.path.join(root_path, 'output_directory')
        os.mkdir(self.output_directory)

    def tearDown(self):
        if os.path.exists(self.template):
            os.remove(self.template)
        if os.path.exists(self.filename):
            os.remove(self.filename)
        if os.path.exists(self.output_directory):
            shutil.rmtree(self.output_directory)

    def prepare_recipe(self):
        dataset_factory = dataset.DatasetFactory()
        dataset_factory.importer_factory = aspecd.io.DatasetImporterFactory()
        self.recipe.dataset_factory = dataset_factory
        recipe_dict = {'tasks': [self.report_task]}
        self.recipe.from_dict(recipe_dict)

    def prepare_template(self, content=''):
        template_content = content
        with open(self.template, 'w+') as f:
            f.write(template_content)

    def test_instantiate_class(self):
        pass

    def test_perform_task(self):
        self.prepare_recipe()
        template_content = ""
        self.prepare_template(template_content)
        self.task.from_dict(self.report_task)
        self.recipe.figures[self.figure] = self.figure_record
        self.task.recipe = self.recipe
        self.task.perform()
        self.assertTrue(os.path.exists(self.filename))

    def test_perform_task_adds_figure_to_context(self):
        self.prepare_recipe()
        template_content = "{@figure['label']}"
        self.prepare_template(template_content)
        self.task.from_dict(self.report_task)
        self.figure_record.label = 'foo'
        self.recipe.figures[self.figure] = self.figure_record
        self.task.recipe = self.recipe
        self.task.perform()
        with open(self.filename) as f:
            read_content = f.read()
        self.assertEqual(self.figure_record.label, read_content)

    def test_perform_task_issues_log_message(self):
        self.prepare_recipe()
        self.task.from_dict(self.report_task)
        self.recipe.figures[self.figure] = self.figure_record
        self.task.recipe = self.recipe
        with self.assertLogs(__package__, level='INFO') as cm:
            self.task.perform()
        self.assertIn('Perform "{}" on figure "{}"'.format(
            self.report_task['type'], self.figure), cm.output[0])

    def test_perform_task_with_multiple_figures_and_filenames(self):
        # noinspection PyTypedDict
        self.report_task["properties"]["filename"] = \
            ['test-report1.tex', 'test-report2.tex']
        # noinspection PyTypedDict
        self.report_task["apply_to"] = [self.figure, "fig2"]
        self.prepare_recipe()
        self.recipe.figures[self.figure] = self.figure_record
        self.recipe.figures["fig2"] = aspecd.tasks.FigureRecord()
        template_content = ""
        self.prepare_template(template_content)
        self.task.from_dict(self.report_task)
        self.task.recipe = self.recipe
        self.task.perform()
        for filename in self.report_task["properties"]["filename"]:
            self.assertTrue(os.path.exists(filename))
        # Manual teardown in this case
        for filename in self.report_task["properties"]["filename"]:
            if os.path.exists(filename):
                os.remove(filename)

    def test_report_gets_saved_to_output_directory_if_provided(self):
        self.prepare_recipe()
        template_content = ""
        self.prepare_template(template_content)
        self.task.from_dict(self.report_task)
        self.recipe.figures[self.figure] = self.figure_record
        self.recipe.directories['output'] = self.output_directory
        self.task.recipe = self.recipe
        self.task.perform()
        self.assertTrue(os.path.exists(os.path.join(self.output_directory,
                                                    self.filename)))

    def test_perform_task_without_filename_saves_report_to_default_name(self):
        self.filename = "_".join([self.figure, "report", self.template])
        self.prepare_recipe()
        template_content = ""
        self.prepare_template(template_content)
        self.report_task['properties'].pop('filename')
        self.task.from_dict(self.report_task)
        self.recipe.figures[self.figure] = self.figure_record
        self.task.recipe = self.recipe
        self.task.perform()
        self.assertTrue(os.path.exists(self.filename))

    def test_perform_task_with_language_and_template_from_package(self):
        self.prepare_recipe()
        self.report_task['properties']['template'] = 'abbildung.tex'
        self.report_task['properties']['language'] = 'de'
        self.task.from_dict(self.report_task)
        self.recipe.figures[self.figure] = self.figure_record
        self.task.recipe = self.recipe
        self.task.perform()
        self.assertTrue(os.path.exists(self.filename))


class TestModelTask(unittest.TestCase):
    def setUp(self):
        self.task = tasks.ModelTask()
        self.recipe = tasks.Recipe()
        self.dataset = 'foo'
        self.model_task = {'kind': 'model',
                           'type': 'Model',
                           'properties': {'parameters': [42], 'variables': [
                               np.linspace(0, 1)]},
                           }

    def prepare_recipe(self):
        dataset_factory = dataset.DatasetFactory()
        dataset_factory.importer_factory = aspecd.io.DatasetImporterFactory()
        self.recipe.dataset_factory = dataset_factory
        recipe_dict = {'datasets': [self.dataset],
                       'tasks': [self.model_task]}
        self.recipe.from_dict(recipe_dict)

    def test_instantiate_class(self):
        pass

    def test_has_result_property(self):
        self.assertTrue(hasattr(self.task, 'result'))

    def test_perform_task(self):
        self.prepare_recipe()
        self.task.from_dict(self.model_task)
        self.task.recipe = self.recipe
        self.task.perform()

    def test_perform_task_issues_log_message(self):
        self.prepare_recipe()
        self.task.from_dict(self.model_task)
        self.task.recipe = self.recipe
        with self.assertLogs(__package__, level='INFO') as cm:
            self.task.perform()
        self.assertIn('Create model "{}"'.format(self.model_task['type']),
                      cm.output[0])

    def test_result_attribute_gets_set_from_dict(self):
        self.prepare_recipe()
        result = 'foo'
        self.model_task['result'] = result
        self.task.from_dict(self.model_task)
        self.assertEqual(result, self.task.result)

    def test_perform_task_with_result_adds_result(self):
        self.prepare_recipe()
        result = 'foo'
        self.model_task['result'] = result
        self.task.from_dict(self.model_task)
        self.task.recipe = self.recipe
        self.task.perform()
        self.assertTrue(len(self.recipe.results))

    def test_perform_task_with_result_adds_result_as_id_to_dataset(self):
        self.prepare_recipe()
        result = 'foo'
        self.model_task['result'] = result
        self.task.from_dict(self.model_task)
        self.task.recipe = self.recipe
        self.task.perform()
        self.assertEqual(result, self.recipe.results[result].id)

    def test_added_result_is_calculated_dataset(self):
        self.prepare_recipe()
        result = 'foo'
        self.model_task['result'] = result
        self.task.from_dict(self.model_task)
        self.task.recipe = self.recipe
        self.task.perform()
        self.assertEqual(aspecd.dataset.CalculatedDataset,
                         type(self.recipe.results[result]))

    def test_from_dataset_obtains_variables_from_dataset(self):
        self.prepare_recipe()
        self.recipe.datasets[self.dataset].data.data = np.linspace(0, 1)
        del self.model_task["properties"]["variables"]
        self.model_task["from_dataset"] = self.dataset
        result = 'foo'
        self.model_task['result'] = result
        self.task.from_dict(self.model_task)
        self.task.recipe = self.recipe
        self.task.perform()
        np.testing.assert_allclose(
            self.recipe.datasets[self.dataset].data.axes[0].values,
            self.recipe.results[result].data.axes[0].values)

    def test_output_model_returns_model(self):
        self.prepare_recipe()
        result = 'foo'
        self.model_task['result'] = result
        self.model_task["output"] = 'model'
        self.task.from_dict(self.model_task)
        self.task.recipe = self.recipe
        self.task.perform()
        self.assertEqual(aspecd.model.Model,
                         type(self.recipe.results[result]))


class TestExportTask(unittest.TestCase):
    def setUp(self):
        self.task = tasks.ExportTask()
        self.recipe = tasks.Recipe()
        self.dataset = 'foo'
        self.filename = 'foo.txt'
        self.filename2 = 'bla.txt'
        self.export_task = {'kind': 'export',
                            'type': 'TxtExporter',
                            'properties': {'target': self.filename},
                            }
        root_path = os.path.split(os.path.abspath(__file__))[0]
        self.output_directory = os.path.join(root_path, 'output_directory')
        os.mkdir(self.output_directory)

    def tearDown(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)
        if os.path.exists(self.filename2):
            os.remove(self.filename2)
        if os.path.exists(self.output_directory):
            shutil.rmtree(self.output_directory)

    def prepare_recipe(self):
        dataset_factory = dataset.DatasetFactory()
        dataset_factory.importer_factory = aspecd.io.DatasetImporterFactory()
        self.recipe.dataset_factory = dataset_factory
        recipe_dict = {'datasets': [self.dataset],
                       'tasks': [self.export_task]}
        self.recipe.from_dict(recipe_dict)

    def test_instantiate_class(self):
        pass

    def test_perform_task(self):
        self.prepare_recipe()
        self.task.from_dict(self.export_task)
        self.task.recipe = self.recipe
        self.task.perform()

    def test_perform_task_issues_log_message(self):
        self.prepare_recipe()
        self.task.from_dict(self.export_task)
        self.task.recipe = self.recipe
        with self.assertLogs(__package__, level='INFO') as cm:
            self.task.perform()
        self.assertIn('Export "{}" to file "{}"'.format(self.dataset,
                                                        self.filename),
                      cm.output[0])

    def test_perform_task_writes_file(self):
        self.prepare_recipe()
        self.task.from_dict(self.export_task)
        self.task.recipe = self.recipe
        self.task.perform()
        self.assertTrue(os.path.exists(self.filename))

    def test_perform_task_with_multiple_datasets_writes_files(self):
        # noinspection PyTypedDict
        self.export_task['properties']['target'] = [self.filename,
                                                    self.filename2]
        recipe_dict = {'datasets': ['foo', 'bar'],
                       'tasks': [self.export_task]}
        self.prepare_recipe()
        self.recipe.from_dict(recipe_dict)
        self.task.from_dict(self.export_task)
        self.task.recipe = self.recipe
        self.task.perform()
        self.assertTrue(os.path.exists(self.filename))
        self.assertTrue(os.path.exists(self.filename2))

    def test_perform_task_with_output_directory_writes_file(self):
        self.prepare_recipe()
        self.recipe.directories['output'] = self.output_directory
        self.task.from_dict(self.export_task)
        self.task.recipe = self.recipe
        self.task.perform()
        self.assertTrue(os.path.exists(os.path.join(self.output_directory,
                                                    self.filename)))


class TestTabulateTask(unittest.TestCase):
    def setUp(self):
        self.task = tasks.TabulateTask()
        self.recipe = tasks.Recipe()
        self.dataset = ['foo']
        self.table_filename = 'foo.pdf'
        self.datasets = ['foo', 'bar']
        self.table_filenames = ['foo.pdf', 'bar.pdf']
        self.tabulate_task = {'kind': 'tabulate',
                              'type': 'Table',
                              'apply_to': self.dataset}

    def tearDown(self):
        if os.path.exists(self.table_filename):
            os.remove(self.table_filename)
        for file in self.table_filenames:
            if os.path.exists(file):
                os.remove(file)

    def prepare_recipe(self):
        dataset_factory = dataset.DatasetFactory()
        dataset_factory.importer_factory = aspecd.io.DatasetImporterFactory()
        self.recipe.dataset_factory = dataset_factory
        recipe_dict = {'datasets': self.dataset,
                       'tasks': [self.tabulate_task]}
        self.recipe.from_dict(recipe_dict)

    def test_instantiate_class(self):
        pass

    def test_perform_task(self):
        self.prepare_recipe()
        self.recipe.datasets[self.dataset[0]].data.data = np.random.random(5)
        self.task.from_dict(self.tabulate_task)
        self.task.recipe = self.recipe
        self.task.perform()
        self.assertTrue(self.recipe.datasets[self.dataset[0]].tasks)

    def test_perform_task_issues_log_message(self):
        self.prepare_recipe()
        self.task.from_dict(self.tabulate_task)
        self.task.recipe = self.recipe
        with self.assertLogs(__package__, level='INFO') as cm:
            self.task.perform()
        self.assertIn('Perform "{}" on dataset "{}"'.format(
            self.tabulate_task['type'], self.dataset[0]), cm.output[0])

    def test_perform_task_with_filename_saves_table(self):
        self.prepare_recipe()
        self.recipe.datasets[self.dataset[0]].data.data = np.random.random(5)
        # noinspection PyTypeChecker
        self.tabulate_task['properties'] = {'filename': self.table_filename}
        self.task.from_dict(self.tabulate_task)
        self.task.recipe = self.recipe
        self.task.perform()
        self.assertTrue(os.path.exists(self.table_filename))

    def test_perform_task_with_filename_issues_log_message(self):
        self.prepare_recipe()
        self.recipe.datasets[self.dataset[0]].data.data = np.random.random(5)
        # noinspection PyTypeChecker
        self.tabulate_task['properties'] = {'filename': self.table_filename}
        self.task.from_dict(self.tabulate_task)
        self.task.recipe = self.recipe
        with self.assertLogs(__package__, level='INFO') as cm:
            self.task.perform()
        self.assertIn('Save table from "{}" to file "{}"'.format(
            self.tabulate_task['type'], self.table_filename), cm.output[1])

    def test_perform_task_with_list_of_filenames_saves_plots(self):
        self.tabulate_task = {'kind': 'tabulate',
                              'type': 'Table',
                              'apply_to': self.datasets}
        dataset_factory = dataset.DatasetFactory()
        dataset_factory.importer_factory = aspecd.io.DatasetImporterFactory()
        self.recipe.dataset_factory = dataset_factory
        recipe_dict = {'datasets': self.datasets,
                       'tasks': [self.tabulate_task]}
        self.recipe.from_dict(recipe_dict)
        self.recipe.datasets[self.datasets[0]].data.data = np.random.random(5)
        self.recipe.datasets[self.datasets[1]].data.data = np.random.random(5)
        # noinspection PyTypeChecker
        self.tabulate_task['properties'] = {'filename': self.table_filenames}
        self.task.from_dict(self.tabulate_task)
        self.task.recipe = self.recipe
        self.task.perform()
        for file in self.table_filenames:
            self.assertTrue(os.path.exists(file))


class TestTaskFactory(unittest.TestCase):
    def setUp(self):
        self.task_factory = tasks.TaskFactory()

    def test_instantiate_class(self):
        pass

    def test_has_get_task_method(self):
        self.assertTrue(hasattr(self.task_factory, 'get_task'))
        self.assertTrue(callable(self.task_factory.get_task))

    def test_get_task_without_kind_raises(self):
        with self.assertRaises(aspecd.exceptions.MissingTaskDescriptionError):
            self.task_factory.get_task()

    def test_get_task_returns_task(self):
        task = self.task_factory.get_task(kind='processing')
        self.assertTrue(isinstance(task, tasks.Task))

    def test_get_task_with_package_prefix_returns_task(self):
        task = self.task_factory.get_task(kind='aspecd.processing')
        self.assertTrue(isinstance(task, tasks.Task))

    def test_get_task_with_package_prefix_sets_task_package(self):
        kind = 'mypackage.processing'
        task = self.task_factory.get_task(kind=kind)
        self.assertEqual(task.package, 'mypackage')

    def test_has_get_task_from_dict_method(self):
        self.assertTrue(hasattr(self.task_factory, 'get_task_from_dict'))
        self.assertTrue(callable(self.task_factory.get_task_from_dict))

    def test_get_task_from_dict_without_dict_raises(self):
        with self.assertRaises(aspecd.exceptions.MissingTaskDescriptionError):
            self.task_factory.get_task_from_dict()

    def test_get_task_from_dict_without_kind_key_raises(self):
        dict_ = {'foo': 'bar'}
        with self.assertRaises(KeyError):
            self.task_factory.get_task_from_dict(dict_=dict_)

    def test_get_task_from_dict_returns_task(self):
        dict_ = {'kind': 'processing'}
        task = self.task_factory.get_task_from_dict(dict_=dict_)
        self.assertTrue(isinstance(task, tasks.Task))

    def test_get_processing_task_from_kind(self):
        kind = 'processing'
        task = self.task_factory.get_task(kind=kind)
        self.assertTrue(isinstance(task, tasks.ProcessingTask))

    def test_get_processing_task_from_dict(self):
        kind = 'processing'
        dict_ = {'kind': kind}
        task = self.task_factory.get_task_from_dict(dict_=dict_)
        self.assertTrue(isinstance(task, tasks.ProcessingTask))


class TestFigureRecord(unittest.TestCase):
    def setUp(self):
        self.figure_record = tasks.FigureRecord()
        self.plotter = plotting.Plotter()

    def test_instantiate_class(self):
        pass

    def test_has_caption_property(self):
        self.assertTrue(hasattr(self.figure_record, 'caption'))

    def test_caption_dict_has_fields_title_text_parameters(self):
        fieldnames = ['title', 'text', 'parameters']
        for fieldname in fieldnames:
            self.assertTrue(fieldname in self.figure_record.caption.keys())

    def test_has_parameters_property(self):
        self.assertTrue(hasattr(self.figure_record, 'parameters'))

    def test_has_label_property(self):
        self.assertTrue(hasattr(self.figure_record, 'label'))

    def test_has_filename_property(self):
        self.assertTrue(hasattr(self.figure_record, 'filename'))

    def test_has_to_dict_method(self):
        self.assertTrue(hasattr(self.figure_record, 'to_dict'))
        self.assertTrue(callable(self.figure_record.to_dict))

    def test_has_from_plotter_method(self):
        self.assertTrue(hasattr(self.figure_record, 'from_plotter'))
        self.assertTrue(callable(self.figure_record.from_plotter))

    def test_from_plotter_without_plotter_raises(self):
        with self.assertRaises(aspecd.exceptions.MissingPlotterError):
            self.figure_record.from_plotter()

    def test_from_plotter_sets_caption(self):
        caption = {
            'title': 'Title',
            'text': 'Text',
            'parameters': ['foo', 'bar']
        }
        self.plotter.caption = caption
        self.figure_record.from_plotter(self.plotter)
        self.assertEqual(caption, self.figure_record.caption)

    def test_from_plotter_sets_parameters(self):
        parameters = ['foo', 'bar']
        self.plotter.parameters = parameters
        self.figure_record.from_plotter(self.plotter)
        self.assertEqual(parameters, self.figure_record.parameters)

    def test_from_plotter_sets_filename(self):
        filename = 'foo.pdf'
        self.plotter.filename = filename
        self.figure_record.from_plotter(self.plotter)
        self.assertEqual(filename, self.figure_record.filename)


class TestChefDeService(unittest.TestCase):

    def setUp(self):
        self.chef_de_service = tasks.ChefDeService()
        self.recipe_filename = 'foo.yaml'
        self.figure_filename = 'foo.pdf'
        self.history_filename = ''

    def tearDown(self):
        if os.path.exists(self.recipe_filename):
            os.remove(self.recipe_filename)
        if os.path.exists(self.figure_filename):
            os.remove(self.figure_filename)
        if self.history_filename and os.path.exists(self.history_filename):
            os.remove(self.history_filename)

    def create_recipe(self):
        recipe_dict = {
            'datasets': ['foo'],
            'tasks': [{'kind': 'singleplot', 'type': 'SinglePlotter',
                       'properties': {'filename': self.figure_filename}}],
        }
        yaml = utils.Yaml()
        yaml.dict = recipe_dict
        yaml.write_to(self.recipe_filename)

    def create_recipe_with_numpy_array(self):
        recipe_dict = {
            'datasets': ['foo'],
            'tasks': [{'kind': 'singleplot', 'type': 'SinglePlotter',
                       'properties': {'filename': self.figure_filename,
                                      'foo': np.random.random(1)}}],
        }
        yaml = utils.Yaml()
        yaml.dict = recipe_dict
        yaml.serialise_numpy_arrays()
        yaml.write_to(self.recipe_filename)

    def create_recipe_with_no_history(self):
        recipe_dict = {
            'settings': {'write_history': False},
            'datasets': ['foo'],
            'tasks': [{'kind': 'singleplot', 'type': 'SinglePlotter',
                       'properties': {'filename': self.figure_filename}}],
        }
        yaml = utils.Yaml()
        yaml.dict = recipe_dict
        yaml.write_to(self.recipe_filename)

    def test_instantiate_class(self):
        pass

    def test_has_serve_method(self):
        self.assertTrue(hasattr(self.chef_de_service, 'serve'))
        self.assertTrue(callable(self.chef_de_service.serve))

    def test_serve_without_recipe_raises(self):
        with self.assertRaises(aspecd.exceptions.MissingRecipeError):
            self.chef_de_service.serve()

    def test_serve_with_preset_recipe(self):
        self.create_recipe()
        self.chef_de_service.recipe_filename = self.recipe_filename
        self.history_filename = self.chef_de_service.serve()

    def test_serve_with_recipe_cooks_recipe(self):
        self.create_recipe()
        self.history_filename = \
            self.chef_de_service.serve(recipe_filename=self.recipe_filename)
        self.assertTrue(os.path.exists(self.figure_filename))

    def test_serve_returns_history_filename(self):
        self.create_recipe()
        self.history_filename = \
            self.chef_de_service.serve(recipe_filename=self.recipe_filename)
        self.assertTrue(self.history_filename)

    def test_serve_returns_history_filename_starting_with_recipe_name(self):
        self.create_recipe()
        self.history_filename = \
            self.chef_de_service.serve(recipe_filename=self.recipe_filename)
        recipe_filename, _ = os.path.splitext(self.recipe_filename)
        self.assertTrue(self.history_filename.startswith(recipe_filename))

    def test_serve_writes_history_to_file(self):
        self.create_recipe()
        self.history_filename = \
            self.chef_de_service.serve(recipe_filename=self.recipe_filename)
        self.assertTrue(os.path.exists(self.history_filename))

    def test_serve_does_not_write_history_to_file_if_told_so(self):
        self.create_recipe_with_no_history()
        self.history_filename = \
            self.chef_de_service.serve(recipe_filename=self.recipe_filename)
        self.assertFalse(os.path.exists(self.history_filename))

    def test_serve_issues_warning_if_told_to_not_write_history(self):
        self.create_recipe_with_no_history()
        with self.assertLogs(__package__, level='WARNING') as cm:
            self.chef_de_service.serve(recipe_filename=self.recipe_filename)
        self.assertIn('No history has been written. This is considered bad '
                      'practice in terms of reproducible research',
                      cm.output[0])

    def test_written_history_can_be_used_as_recipe(self):
        self.create_recipe()
        self.history_filename = \
            self.chef_de_service.serve(recipe_filename=self.recipe_filename)
        history_filename = \
            self.chef_de_service.serve(recipe_filename=self.history_filename)
        os.remove(history_filename)

    def test_written_history_with_numpy_array_can_be_used_as_recipe(self):
        self.create_recipe_with_numpy_array()
        self.history_filename = \
            self.chef_de_service.serve(recipe_filename=self.recipe_filename)
        history_filename = \
            self.chef_de_service.serve(recipe_filename=self.history_filename)
        os.remove(history_filename)


@unittest.skip
class TestServe(unittest.TestCase):

    def setUp(self):
        self.chef_de_service = tasks.ChefDeService()
        self.recipe_filename = 'foo.yaml'
        self.figure_filename = 'foo.pdf'
        self.recipe_dict = {
            'datasets': ['foo'],
            'tasks': [{'kind': 'singleplot', 'type': 'SinglePlotter',
                       'properties': {'filename': self.figure_filename}}],
        }

    def tearDown(self):
        if os.path.exists(self.recipe_filename):
            os.remove(self.recipe_filename)
        if os.path.exists(self.figure_filename):
            os.remove(self.figure_filename)
        for file in glob.glob(f'{self.recipe_filename.split(".")[0]}-*.yaml'):
            os.remove(file)

    def create_recipe(self):
        yaml = utils.Yaml()
        yaml.dict = self.recipe_dict
        yaml.write_to(self.recipe_filename)

    def test_call_without_recipe_prints_help(self):
        result = subprocess.run(["serve"], capture_output=True, text=True)
        self.assertIn('error: the following arguments are required',
                      result.stderr)

    def test_help_contains_program_name(self):
        result = subprocess.run(["serve", "-h"], capture_output=True, text=True)
        self.assertIn('usage: serve [', result.stdout)

    def test_help_contains_program_description(self):
        result = subprocess.run(["serve", "-h"], capture_output=True, text=True)
        self.assertIn('Process a recipe in context of recipe-driven data '
                      'analysis', result.stdout)

    def test_help_contains_description_of_recipe_argument(self):
        result = subprocess.run(["serve", "-h"], capture_output=True, text=True)
        self.assertIn('YAML file containing recipe', result.stdout)

    def test_has_quiet_argument(self):
        result = subprocess.run(["serve", "-h"], capture_output=True, text=True)
        self.assertIn('-q, --quiet', result.stdout)

    def test_quiet_argument_has_description(self):
        result = subprocess.run(["serve", "-h"], capture_output=True, text=True)
        self.assertIn("-q, --quiet    don't show any output", result.stdout)

    def test_has_verbose_argument(self):
        result = subprocess.run(["serve", "-h"], capture_output=True, text=True)
        self.assertIn('-v, --verbose', result.stdout)

    def test_verbose_argument_has_description(self):
        result = subprocess.run(["serve", "-h"], capture_output=True, text=True)
        self.assertIn("-v, --verbose  show debug output", result.stdout)

    def test_verbose_and_quite_arguments_are_mutually_exclusive(self):
        result = subprocess.run(["serve", "-h"], capture_output=True, text=True)
        self.assertIn("[-v | -q]", result.stdout)

    def test_serve_console_entry_point_cooks_recipe(self):
        self.create_recipe()
        subprocess.run(["serve", self.recipe_filename])
        self.assertTrue(os.path.exists(self.figure_filename))

    def test_serve_console_entry_point_without_recipe_raises(self):
        self.create_recipe()
        with self.assertRaises(subprocess.CalledProcessError):
            subprocess.run(["serve"], check=True)

    def test_serve_console_entry_point_prints_log_info(self):
        self.create_recipe()
        result = subprocess.run(["serve", self.recipe_filename],
                                capture_output=True, text=True)
        self.assertIn('INFO - Import dataset', result.stdout)

    def test_call_with_quiet_option_does_not_print_log_info(self):
        self.create_recipe()
        result = subprocess.run(["serve", "-q", self.recipe_filename],
                                capture_output=True, text=True)
        self.assertNotIn('Import dataset', result.stdout)

    def test_serve_catches_exceptions(self):
        self.recipe_dict["tasks"][0]["kind"] = "foo"
        self.create_recipe()
        result = subprocess.run(["serve", self.recipe_filename],
                                capture_output=True, text=True)
        self.assertNotIn("Traceback (most recent call last):",
                         [result.stderr, result.stdout])

    def test_serve_shows_stack_trace_of_exception_in_verbose_mode(self):
        self.recipe_dict["tasks"][0]["kind"] = "foo"
        self.create_recipe()
        result = subprocess.run(["serve", "-v", self.recipe_filename],
                                capture_output=True, text=True)
        self.assertIn("Traceback (most recent call last):", result.stdout)
