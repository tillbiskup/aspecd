"""Tests for tasks."""

import os
import unittest

from aspecd import dataset, io, plotting, processing, report, tasks, utils


class TestRecipe(unittest.TestCase):
    def setUp(self):
        self.recipe = tasks.Recipe()
        self.filename = 'test.yaml'
        self.dataset = 'foo'
        self.datasets = ['foo', 'bar']
        self.task = {'kind': 'processing', 'type': 'ProcessingStep'}
        self.dataset_factory = dataset.DatasetFactory()
        self.dataset_factory.importer_factory = io.DatasetImporterFactory()

    def tearDown(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)

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

    def test_import_from_without_importer_raises(self):
        with self.assertRaises(tasks.MissingImporterError):
            self.recipe.import_from()

    def test_import_from_yaml_importer_with_task_sets_task(self):
        yaml_contents = {'tasks': [self.task]}
        with open(self.filename, 'w') as file:
            utils.yaml.dump(yaml_contents, file)
        importer = io.RecipeYamlImporter(source=self.filename)
        self.recipe.dataset_factory = self.dataset_factory
        self.recipe.import_from(importer=importer)
        for key in self.task:
            self.assertEqual(getattr(self.recipe.tasks[0], key),
                             self.task[key])

    def test_import_from_yaml_importer_with_datasets_sets_datasets(self):
        yaml_contents = {'datasets': self.datasets}
        with open(self.filename, 'w') as file:
            utils.yaml.dump(yaml_contents, file)
        importer = io.RecipeYamlImporter(source=self.filename)
        self.recipe.dataset_factory = self.dataset_factory
        self.recipe.import_from(importer=importer)
        self.assertEqual(len(self.recipe.datasets), len(self.datasets))
        for dataset_ in self.recipe.datasets:
            self.assertTrue(isinstance(self.recipe.datasets[dataset_],
                                       dataset.Dataset))

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
        with self.assertRaises(tasks.MissingDatasetFactoryError):
            self.recipe.from_dict(dict_)

    def test_from_dict_with_dataset_sets_dataset(self):
        dict_ = {'datasets': [self.dataset]}
        self.recipe.dataset_factory = self.dataset_factory
        self.recipe.from_dict(dict_)
        self.assertTrue(isinstance(self.recipe.datasets[self.dataset],
                                   dataset.Dataset))

    def test_from_dict_with_dataset_sets_dataset_id(self):
        dict_ = {'datasets': [self.dataset]}
        self.recipe.dataset_factory = self.dataset_factory
        self.recipe.from_dict(dict_)
        self.assertEqual(self.dataset, self.recipe.datasets[self.dataset].id)

    def test_from_dict_with_multiple_datasets_sets_datasets(self):
        dict_ = {'datasets': self.datasets}
        self.recipe.dataset_factory = self.dataset_factory
        self.recipe.from_dict(dict_)
        for dataset_ in self.recipe.datasets:
            self.assertTrue(isinstance(self.recipe.datasets[dataset_],
                                       dataset.Dataset))

    def test_from_dict_with_tasks_without_task_factory_raises(self):
        dict_ = {'tasks': [self.task]}
        self.recipe.dataset_factory = self.dataset_factory
        self.recipe.task_factory = None
        with self.assertRaises(tasks.MissingTaskFactoryError):
            self.recipe.from_dict(dict_)

    def test_from_dict_with_task_adds_task(self):
        dict_ = {'tasks': [self.task]}
        self.recipe.dataset_factory = self.dataset_factory
        self.recipe.from_dict(dict_)
        self.assertTrue(isinstance(self.recipe.tasks[0], tasks.Task))
        for key in self.task:
            self.assertEqual(getattr(self.recipe.tasks[0], key),
                             self.task[key])

    def test_from_dict_with_task_adds_task_with_correct_type(self):
        dict_ = {'tasks': [self.task]}
        self.recipe.dataset_factory = self.dataset_factory
        self.recipe.from_dict(dict_)
        self.assertTrue(isinstance(self.recipe.tasks[0],
                                   tasks.ProcessingTask))

    def test_has_to_dict_method(self):
        self.assertTrue(hasattr(self.recipe, 'to_dict'))
        self.assertTrue(callable(self.recipe.to_dict))

    def test_to_dict_with_datasets_returns_dataset_sources(self):
        for dataset_ in self.datasets:
            tmp = dataset.Dataset()
            tmp.id = dataset_
            self.recipe.datasets[dataset_] = tmp
        dict_ = self.recipe.to_dict()
        self.assertEqual(self.datasets, dict_['datasets'])

    def test_to_dict_with_task_returns_task_dict(self):
        task = tasks.Task()
        task.from_dict(self.task)
        self.recipe.tasks.append(task)
        dict_ = self.recipe.to_dict()
        self.assertEqual(task.to_dict(), dict_['tasks'][0])

    def test_has_get_dataset_method(self):
        self.assertTrue(hasattr(self.recipe, 'get_dataset'))
        self.assertTrue(callable(self.recipe.get_dataset))

    def test_get_dataset_without_identifier_raises(self):
        with self.assertRaises(tasks.MissingDatasetIdentifierError):
            self.recipe.get_dataset()

    def test_get_dataset_with_valid_identifier_returns_dataset(self):
        dict_ = {'datasets': [self.dataset]}
        self.recipe.dataset_factory = self.dataset_factory
        self.recipe.from_dict(dict_)
        dataset_ = self.recipe.get_dataset(identifier=self.dataset)
        self.assertTrue(isinstance(dataset_, dataset.Dataset))

    def test_get_dataset_with_invalid_identifier_returns_nothing(self):
        dict_ = {'datasets': [self.dataset]}
        self.recipe.dataset_factory = self.dataset_factory
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
        with self.assertRaises(tasks.MissingDatasetIdentifierError):
            self.recipe.get_datasets()

    def test_get_datasets_with_valid_identifier_returns_dataset(self):
        dict_ = {'datasets': self.datasets}
        self.recipe.dataset_factory = self.dataset_factory
        self.recipe.from_dict(dict_)
        datasets = self.recipe.get_datasets(identifiers=self.datasets)
        for dataset_ in datasets:
            self.assertTrue(isinstance(dataset_, dataset.Dataset))

    def test_get_datasets_with_invalid_identifier_returns_nothing(self):
        dict_ = {'datasets': self.datasets}
        self.recipe.dataset_factory = self.dataset_factory
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


class TestChef(unittest.TestCase):
    def setUp(self):
        self.chef = tasks.Chef()
        self.recipe = tasks.Recipe()
        dataset_factory = dataset.DatasetFactory()
        dataset_factory.importer_factory = io.DatasetImporterFactory()
        self.recipe.dataset_factory = dataset_factory
        self.dataset = 'foo'
        self.processing_task = {'kind': 'processing',
                                'type': 'ProcessingStep'}
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
        self.assertTrue(self.chef.recipe.datasets[self.dataset].history)

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
        self.chef.cook(recipe=recipe)
        self.assertTrue(self.chef.recipe.datasets[
                            self.dataset].representations)


class TestTask(unittest.TestCase):
    def setUp(self):
        self.task = tasks.Task()

    def test_instantiate_class(self):
        pass

    def test_has_kind_property(self):
        self.assertTrue(hasattr(self.task, 'kind'))

    def test_has_type_property(self):
        self.assertTrue(hasattr(self.task, 'type'))

    def test_has_properties_property(self):
        self.assertTrue(hasattr(self.task, 'properties'))

    def test_has_apply_to_property(self):
        self.assertTrue(hasattr(self.task, 'apply_to'))

    def test_has_recipe_property(self):
        self.assertTrue(hasattr(self.task, 'recipe'))

    def test_instantiate_with_recipe_sets_recipe(self):
        recipe = tasks.Recipe()
        task = tasks.Task(recipe=recipe)
        self.assertEqual(recipe, task.recipe)

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

    def test_from_dict_with_append_to_appends_to_list(self):
        dataset_id = 'foo'
        dict_ = {'apply_to': dataset_id}
        self.task.from_dict(dict_)
        self.assertTrue(isinstance(self.task.apply_to, list))
        self.assertEqual(dataset_id, self.task.apply_to[0])

    def test_from_dict_does_not_set_unknown_attribute(self):
        attribute = 'foo'
        dict_ = dict()
        dict_[attribute] = 'foo'
        self.task.from_dict(dict_)
        self.assertFalse(hasattr(self.task, attribute))

    def test_has_perform_method(self):
        self.assertTrue(hasattr(self.task, 'perform'))
        self.assertTrue(callable(self.task.perform))

    def test_perform_without_recipe_raises(self):
        with self.assertRaises(tasks.MissingRecipeError):
            self.task.perform()

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
        self.task.properties = metadata
        obj = self.task.get_object()
        self.assertEqual(metadata['parameters'], getattr(obj, 'parameters'))

    def test_get_object_sets_only_existing_object_attributes(self):
        kind = 'processing'
        type_ = 'ProcessingStep'
        metadata = {'foo': {'foo': 'bar'}}
        self.task.kind = kind
        self.task.type = type_
        self.task.properties = metadata
        obj = self.task.get_object()
        self.assertFalse(hasattr(obj, 'foo'))

    # ATTENTION: The following tests access protected methods - due to not
    # knowing better how to do it properly for the time being...
    def test_set_object_attributes_sets_field_in_dict(self):
        processing_step = processing.ProcessingStep()
        processing_step.parameters = {'foo': 'a', 'bar': 'b'}
        metadata = {'parameters': {'foo': 'bar'}}
        self.task.properties = metadata
        self.task._set_object_attributes(processing_step)
        self.assertEqual(metadata['parameters']['foo'],
                         processing_step.parameters['foo'])

    def test_set_object_attributes_sets_fields_in_dict(self):
        processing_step = processing.ProcessingStep()
        processing_step.parameters = {'foo': 'a', 'bar': 'b'}
        metadata = {'parameters': {'foo': 'bar', 'bar': 'foo'}}
        self.task.properties = metadata
        self.task._set_object_attributes(processing_step)
        self.assertEqual(metadata['parameters']['foo'],
                         processing_step.parameters['foo'])
        self.assertEqual(metadata['parameters']['bar'],
                         processing_step.parameters['bar'])

    def test_set_object_attributes_does_not_override_dict(self):
        processing_step = processing.ProcessingStep()
        processing_step.parameters = {'foo': 'a', 'bar': 'b'}
        metadata = {'parameters': {'foo': 'bar'}}
        self.task.properties = metadata
        self.task._set_object_attributes(processing_step)
        self.assertTrue('bar' in processing_step.parameters)

    def test_set_object_attributes_replaces_results_from_recipe(self):
        processing_step = processing.ProcessingStep()
        processing_step.parameters = {'foo': '', 'bar': ''}
        metadata = {'parameters': {'foo': 'bar'}}
        self.task.properties = metadata
        self.task.recipe = tasks.Recipe()
        self.task.recipe.results['bar'] = dataset.Dataset()
        self.task._set_object_attributes(processing_step)
        self.assertEqual(self.task.recipe.results['bar'],
                         processing_step.parameters['foo'])

    def test_set_object_attributes_replaces_datasets_from_recipe(self):
        processing_step = processing.ProcessingStep()
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


class TestProcessingTask(unittest.TestCase):
    def setUp(self):
        self.task = tasks.ProcessingTask()
        self.recipe = tasks.Recipe()
        self.dataset = ['foo']

    def prepare_recipe(self):
        self.processing_task = {'kind': 'processing',
                                'type': 'ProcessingStep',
                                'apply_to': self.dataset}
        dataset_factory = dataset.DatasetFactory()
        dataset_factory.importer_factory = io.DatasetImporterFactory()
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

    def test_perform_task_on_multiple_datasets(self):
        self.dataset = ['foo', 'bar']
        self.prepare_recipe()
        self.task.from_dict(self.processing_task)
        self.task.recipe = self.recipe
        self.task.perform()
        for dataset_ in self.recipe.datasets:
            self.assertTrue(self.recipe.datasets[dataset_].history)


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
        dataset_factory.importer_factory = io.DatasetImporterFactory()
        self.recipe.dataset_factory = dataset_factory
        recipe_dict = {'datasets': self.dataset,
                       'tasks': [self.analysis_task]}
        self.recipe.from_dict(recipe_dict)

    def test_instantiate_class(self):
        pass

    def test_has_result_property(self):
        self.assertTrue(hasattr(self.task, 'result'))


class TestSingleAnalysisTask(unittest.TestCase):
    def setUp(self):
        self.task = tasks.SingleanalysisTask()
        self.recipe = tasks.Recipe()
        self.dataset = ['foo']

    def prepare_recipe(self):
        self.analysis_task = {'kind': 'singleanalysis',
                              'type': 'SingleAnalysisStep',
                              'apply_to': self.dataset}
        dataset_factory = dataset.DatasetFactory()
        dataset_factory.importer_factory = io.DatasetImporterFactory()
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
        self.assertTrue(self.recipe.datasets[self.dataset[0]].analyses)

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

    @unittest.skip
    def test_perform_task_with_result_sets_resulting_dataset_id(self):
        self.prepare_recipe()
        result = 'foo'
        self.analysis_task['result'] = result
        self.task.from_dict(self.analysis_task)
        self.task.recipe = self.recipe
        self.task.perform()
        self.assertEqual(self.recipe.results[result].id, result)


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
        dataset_factory.importer_factory = io.DatasetImporterFactory()
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
        dataset_factory.importer_factory = io.DatasetImporterFactory()
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


class TestPlotTask(unittest.TestCase):
    def setUp(self):
        self.task = tasks.PlotTask()
        self.recipe = tasks.Recipe()
        self.dataset = ['foo']

    def prepare_recipe(self):
        self.plotting_task = {'kind': 'plot',
                              'type': 'Plotter',
                              'apply_to': self.dataset}
        dataset_factory = dataset.DatasetFactory()
        dataset_factory.importer_factory = io.DatasetImporterFactory()
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

    def test_perform_task_without_label_doesnt_add_figure_to_recipe(self):
        self.prepare_recipe()
        self.task.from_dict(self.plotting_task)
        self.task.recipe = self.recipe
        self.task.perform()
        self.assertFalse(self.recipe.figures)

    def test_perform_task_with_label_adds_figure_to_recipe(self):
        self.prepare_recipe()
        label = 'foo'
        self.plotting_task['label'] = label
        self.task.from_dict(self.plotting_task)
        self.task.recipe = self.recipe
        self.task.perform()
        self.assertTrue(len(self.recipe.figures))

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
                         self.recipe.figures[label].caption['title'])


class TestSinglePlotTask(unittest.TestCase):
    def setUp(self):
        self.task = tasks.SingleplotTask()
        self.recipe = tasks.Recipe()
        self.dataset = ['foo']
        self.figure_filename = 'foo.pdf'

    def tearDown(self):
        if os.path.exists(self.figure_filename):
            os.remove(self.figure_filename)

    def prepare_recipe(self):
        self.plotting_task = {'kind': 'singleplot',
                              'type': 'SinglePlotter',
                              'apply_to': self.dataset}
        dataset_factory = dataset.DatasetFactory()
        dataset_factory.importer_factory = io.DatasetImporterFactory()
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
        self.assertTrue(self.recipe.datasets[self.dataset[0]].representations)

    def test_perform_task_with_filename_saves_plot(self):
        self.prepare_recipe()
        # noinspection PyTypeChecker
        self.plotting_task['properties'] = {'filename': self.figure_filename}
        self.task.from_dict(self.plotting_task)
        self.task.recipe = self.recipe
        self.task.perform()
        self.assertTrue(os.path.exists(self.figure_filename))


class TestMultiPlotTask(unittest.TestCase):
    def setUp(self):
        self.task = tasks.MultiplotTask()
        self.recipe = tasks.Recipe()
        self.dataset = ['foo']
        self.figure_filename = 'foo.pdf'

    def tearDown(self):
        if os.path.exists(self.figure_filename):
            os.remove(self.figure_filename)

    def prepare_recipe(self):
        self.plotting_task = {'kind': 'multiplot',
                              'type': 'MultiPlotter',
                              'apply_to': self.dataset}
        dataset_factory = dataset.DatasetFactory()
        dataset_factory.importer_factory = io.DatasetImporterFactory()
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

    def test_perform_task_with_filename_saves_plot(self):
        self.prepare_recipe()
        # noinspection PyTypeChecker
        self.plotting_task['properties'] = {'filename': self.figure_filename}
        self.task.from_dict(self.plotting_task)
        self.task.recipe = self.recipe
        self.task.perform()
        self.assertTrue(os.path.exists(self.figure_filename))


class TestReportTask(unittest.TestCase):
    def setUp(self):
        self.task = tasks.ReportTask()
        self.recipe = tasks.Recipe()
        self.dataset = ['foo']
        self.template = 'test_template.tex'
        self.filename = 'test_report.tex'
        self.result = 'test_report.pdf'

    def tearDown(self):
        if os.path.exists(self.template):
            os.remove(self.template)
        if os.path.exists(self.filename):
            os.remove(self.filename)
        if os.path.exists(self.result):
            os.remove(self.result)

    def prepare_recipe(self):
        self.report_task = {'kind': 'report',
                            'type': 'LaTeXReporter',
                            'properties': {'template': self.template,
                                           'filename': self.filename,
                                           },
                            'apply_to': self.dataset}
        dataset_factory = dataset.DatasetFactory()
        dataset_factory.importer_factory = io.DatasetImporterFactory()
        self.recipe.dataset_factory = dataset_factory
        recipe_dict = {'datasets': self.dataset,
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

    def test_perform_task_adds_dataset_to_context(self):
        self.prepare_recipe()
        template_content = "{@dataset['id']}"
        self.prepare_template(template_content)
        self.task.from_dict(self.report_task)
        self.task.recipe = self.recipe
        self.task.perform()
        with open(self.filename) as f:
            read_content = f.read()
        self.assertEqual(read_content, 'foo')

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


class TestTaskFactory(unittest.TestCase):
    def setUp(self):
        self.task_factory = tasks.TaskFactory()

    def test_instantiate_class(self):
        pass

    def test_has_get_task_method(self):
        self.assertTrue(hasattr(self.task_factory, 'get_task'))
        self.assertTrue(callable(self.task_factory.get_task))

    def test_get_task_without_kind_raises(self):
        with self.assertRaises(tasks.MissingTaskDescriptionError):
            self.task_factory.get_task()

    def test_get_task_returns_task(self):
        task = self.task_factory.get_task(kind='processing')
        self.assertTrue(isinstance(task, tasks.Task))

    def test_has_get_task_from_dict_method(self):
        self.assertTrue(hasattr(self.task_factory, 'get_task_from_dict'))
        self.assertTrue(callable(self.task_factory.get_task_from_dict))

    def test_get_task_from_dict_without_dict_raises(self):
        with self.assertRaises(tasks.MissingTaskDescriptionError):
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
        with self.assertRaises(tasks.MissingPlotterError):
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
