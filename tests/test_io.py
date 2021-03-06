"""Tests for input and output (IO)."""

import os
import unittest
import zipfile

import numpy as np

import aspecd.exceptions
import aspecd.processing
from aspecd import io, dataset, tasks


class TestDatasetImporter(unittest.TestCase):
    def setUp(self):
        self.importer = io.DatasetImporter()

    def test_instantiate_class(self):
        pass

    def test_instantiate_with_source_sets_source(self):
        source = 'filename'
        importer = io.DatasetImporter(source)
        self.assertEqual(importer.source, source)

    def test_has_import_into_method(self):
        self.assertTrue(hasattr(self.importer, 'import_into'))
        self.assertTrue(callable(self.importer.import_into))

    def test_import_into_without_dataset_raises(self):
        with self.assertRaises(aspecd.exceptions.MissingDatasetError):
            self.importer.import_into()

    def test_import_into_with_dataset_sets_dataset(self):
        test_dataset = dataset.Dataset()
        self.importer.import_into(test_dataset)
        self.assertIs(self.importer.dataset, test_dataset)

    def test_import_into_with_dataset_sets_id(self):
        test_dataset = dataset.Dataset()
        self.importer.source = 'filename'
        self.importer.import_into(test_dataset)
        self.assertIs(test_dataset.id, self.importer.source)

    def test_import_into_with_dataset_sets_label(self):
        test_dataset = dataset.Dataset()
        self.importer.source = 'filename'
        self.importer.import_into(test_dataset)
        self.assertIs(test_dataset.label, self.importer.source)


class TestDatasetExporter(unittest.TestCase):
    def setUp(self):
        self.exporter = io.DatasetExporter()

    def test_instantiate_class(self):
        pass

    def test_instantiate_with_target_sets_target(self):
        target = 'filename'
        exporter = io.DatasetExporter(target=target)
        self.assertEqual(exporter.target, target)

    def test_has_export_from_method(self):
        self.assertTrue(hasattr(self.exporter, 'export_from'))
        self.assertTrue(callable(self.exporter.export_from))

    def test_export_from_without_dataset_raises(self):
        with self.assertRaises(aspecd.exceptions.MissingDatasetError):
            self.exporter.export_from()

    def test_export_from_with_dataset_sets_dataset(self):
        test_dataset = dataset.Dataset()
        self.exporter.export_from(test_dataset)
        self.assertIs(self.exporter.dataset, test_dataset)


class TestDatasetImporterFactory(unittest.TestCase):
    def setUp(self):
        self.factory = io.DatasetImporterFactory()
        self.source = '/foo'

    def test_instantiate_class(self):
        pass

    def test_get_importer_returns_importer(self):
        importer = self.factory.get_importer(source=self.source)
        self.assertTrue(isinstance(importer, io.DatasetImporter))

    def test_get_importer_sets_source_in_importer(self):
        importer = self.factory.get_importer(source=self.source)
        self.assertEqual(self.source, importer.source)

    def test_get_importer_with_relative_source_sets_absolute_path(self):
        source = 'foo'
        root_path = os.path.abspath(os.curdir)
        importer = self.factory.get_importer(source=source)
        self.assertEqual(os.path.join(root_path, source), importer.source)

    def test_get_importer_without_source_raises(self):
        with self.assertRaises(aspecd.exceptions.MissingSourceError):
            self.factory.get_importer()


class TestRecipeImporter(unittest.TestCase):
    def setUp(self):
        self.importer = io.RecipeImporter()
        self.source = 'filename'

    def test_instantiate_class(self):
        pass

    def test_instantiate_with_source_sets_source(self):
        importer = io.RecipeImporter(source=self.source)
        self.assertEqual(importer.source, self.source)

    def test_has_import_into_method(self):
        self.assertTrue(hasattr(self.importer, 'import_into'))
        self.assertTrue(callable(self.importer.import_into))

    def test_import_into_without_recipe_raises(self):
        with self.assertRaises(aspecd.exceptions.MissingRecipeError):
            self.importer.import_into()

    def test_import_into_without_parameter_but_recipe_preset(self):
        recipe = tasks.Recipe()
        self.importer.recipe = recipe
        self.importer.import_into()
        self.assertIs(self.importer.recipe, recipe)

    def test_import_into_with_recipe_sets_recipe(self):
        recipe = tasks.Recipe()
        self.importer.import_into(recipe=recipe)
        self.assertIs(self.importer.recipe, recipe)

    def test_import_into_with_source_sets_filename_in_recipe(self):
        recipe = tasks.Recipe()
        importer = io.RecipeImporter(source=self.source)
        importer.recipe = recipe
        importer.import_into()
        self.assertEqual(importer.recipe.filename, self.source)


class TestRecipeExporter(unittest.TestCase):
    def setUp(self):
        self.exporter = io.RecipeExporter()
        self.target = 'filename'

    def test_instantiate_class(self):
        pass

    def test_instantiate_with_target_sets_target(self):
        exporter = io.RecipeExporter(target=self.target)
        self.assertEqual(exporter.target, self.target)

    def test_has_export_from_method(self):
        self.assertTrue(hasattr(self.exporter, 'export_from'))
        self.assertTrue(callable(self.exporter.export_from))

    def test_export_from_without_recipe_raises(self):
        with self.assertRaises(aspecd.exceptions.MissingRecipeError):
            self.exporter.export_from()

    def test_export_from_with_recipe_sets_recipe(self):
        recipe = tasks.Recipe()
        self.exporter.export_from(recipe)
        self.assertIs(self.exporter.recipe, recipe)


class TestRecipeYamlImporter(unittest.TestCase):
    def setUp(self):
        self.importer = io.RecipeYamlImporter()
        self.source = 'filename'

    def test_instantiate_class(self):
        pass

    def test_is_recipe_importer(self):
        self.assertTrue(isinstance(self.importer, io.RecipeImporter))


class TestRecipeYamlExporter(unittest.TestCase):
    def setUp(self):
        self.exporter = io.RecipeYamlExporter()
        self.source = 'filename'

    def test_instantiate_class(self):
        pass

    def test_is_recipe_exporter(self):
        self.assertTrue(isinstance(self.exporter, io.RecipeExporter))


class TestAdfExporter(unittest.TestCase):
    def setUp(self):
        self.exporter = io.AdfExporter()
        self.dataset = dataset.Dataset()
        self.target = 'target'
        self.extension = '.adf'

    def tearDown(self):
        if os.path.exists(self.target + self.extension):
            os.remove(self.target + self.extension)

    def test_instantiate_class(self):
        pass

    def test_export_from_without_target_raises(self):
        with self.assertRaises(aspecd.exceptions.MissingTargetError):
            self.exporter.export_from(dataset=self.dataset)

    def test_export_with_target_creates_file(self):
        self.exporter.target = self.target
        self.exporter.export_from(self.dataset)
        self.assertTrue(os.path.exists(self.target + self.extension))

    def test_export_creates_zip_file(self):
        self.exporter.target = self.target
        self.exporter.export_from(self.dataset)
        self.assertTrue(zipfile.is_zipfile(self.target + self.extension))

    def test_created_zipfile_contains_correct_files(self):
        self.exporter.target = self.target
        self.exporter.export_from(self.dataset)
        expected_list_of_files = ['dataset.yaml', 'VERSION', 'README',
                                  'binaryData/']
        expected_list_of_files.sort()
        with zipfile.ZipFile(self.target + self.extension, 'r') as zipped_file:
            actual_list_of_files = zipped_file.namelist()
        actual_list_of_files.sort()
        self.assertListEqual(expected_list_of_files, actual_list_of_files)

    def test_export_with_large_array_adds_binary_files(self):
        self.exporter.target = self.target
        self.dataset.data.data = np.random.random(1001)
        self.exporter.export_from(self.dataset)
        with zipfile.ZipFile(self.target + self.extension, 'r') as zipped_file:
            list_of_files = zipped_file.namelist()
        binary_files = [x for x in list_of_files if x.startswith('binaryData')]
        self.assertEqual(3, len(binary_files))

    def test_export_sets_version(self):
        self.exporter.target = self.target
        self.exporter.export_from(self.dataset)
        with zipfile.ZipFile(self.target + self.extension, 'r') as zipped_file:
            version = zipped_file.read('VERSION')
        self.assertEqual(self.exporter._version, version.decode('ascii'))

    def test_export_writes_readme(self):
        self.exporter.target = self.target
        self.exporter.export_from(self.dataset)
        with zipfile.ZipFile(self.target + self.extension, 'r') as zipped_file:
            readme = zipped_file.read('README')
        self.assertTrue(readme)


class TestAdfImporter(unittest.TestCase):
    def setUp(self):
        self.importer = io.AdfImporter()
        self.dataset = dataset.ExperimentalDataset()
        self.source = 'target'
        self.extension = '.adf'
        self.exporter = io.AdfExporter()
        self.exporter.target = self.source

    def tearDown(self):
        if os.path.exists(self.source + self.extension):
            os.remove(self.source + self.extension)

    def test_instantiate_class(self):
        pass

    def test_import_sets_data_and_origdata(self):
        dataset_ = dataset.Dataset()
        dataset_.data.data = np.asarray([1.])
        dataset_._origdata.data = np.asarray([1.])
        dataset_.export_to(self.exporter)

        self.importer.source = self.source
        self.dataset.import_from(self.importer)
        self.assertEqual(dataset_.data.data, self.dataset.data.data)
        self.assertEqual(dataset_._origdata.data, self.dataset._origdata.data)

    def test_import_sets_metadata(self):
        dataset_ = dataset.ExperimentalDataset()
        dataset_.metadata.sample.name = 'foo'
        dataset_.export_to(self.exporter)
        self.importer.source = self.source
        self.dataset.import_from(self.importer)
        self.assertEqual(dataset_.metadata.sample.name,
                         self.dataset.metadata.sample.name)

    def test_import_sets_history(self):
        dataset_ = dataset.ExperimentalDataset()
        processing_step = aspecd.processing.ProcessingStep()
        processing_step.comment = 'foo'
        dataset_.process(processing_step)
        dataset_.export_to(self.exporter)
        self.importer.source = self.source
        self.dataset.import_from(self.importer)
        self.assertDictEqual(dataset_.history[0].to_dict(),
                             self.dataset.history[0].to_dict())

    def test_import_with_large_array(self):
        dataset_ = dataset.Dataset()
        dataset_.data.data = np.random.random(1001)
        dataset_.export_to(self.exporter)

        self.importer.source = self.source
        self.dataset.import_from(self.importer)
        np.testing.assert_allclose(dataset_.data.data, self.dataset.data.data)


class TestAsdfExporter(unittest.TestCase):
    def setUp(self):
        self.exporter = io.AsdfExporter()
        self.dataset = dataset.Dataset()
        self.target = 'target'
        self.extension = '.asdf'

    def tearDown(self):
        if os.path.exists(self.target + self.extension):
            os.remove(self.target + self.extension)

    def test_instantiate_class(self):
        pass

    def test_export_from_without_target_raises(self):
        with self.assertRaises(aspecd.exceptions.MissingTargetError):
            self.exporter.export_from(dataset=self.dataset)

    def test_export_with_target_creates_file(self):
        self.exporter.target = self.target
        self.exporter.export_from(self.dataset)
        self.assertTrue(os.path.exists(self.target + self.extension))


class TestAsdfImporter(unittest.TestCase):
    def setUp(self):
        self.importer = io.AsdfImporter()
        self.dataset = dataset.ExperimentalDataset()
        self.source = 'target'
        self.extension = '.asdf'
        self.exporter = io.AsdfExporter()
        self.exporter.target = self.source

    def tearDown(self):
        if os.path.exists(self.source + self.extension):
            os.remove(self.source + self.extension)

    def test_instantiate_class(self):
        pass

    def test_import_sets_data_and_origdata(self):
        dataset_ = dataset.Dataset()
        dataset_.data.data = np.asarray([1.])
        dataset_._origdata.data = np.asarray([1.])
        dataset_.export_to(self.exporter)

        self.importer.source = self.source
        self.dataset.import_from(self.importer)
        self.assertEqual(dataset_.data.data, self.dataset.data.data)
        self.assertEqual(dataset_._origdata.data, self.dataset._origdata.data)

    def test_import_sets_metadata(self):
        dataset_ = dataset.ExperimentalDataset()
        dataset_.metadata.sample.name = 'foo'
        dataset_.export_to(self.exporter)
        self.importer.source = self.source
        self.dataset.import_from(self.importer)
        self.assertEqual(dataset_.metadata.sample.name,
                         self.dataset.metadata.sample.name)

    def test_import_sets_history(self):
        dataset_ = dataset.ExperimentalDataset()
        processing_step = aspecd.processing.ProcessingStep()
        processing_step.comment = 'foo'
        dataset_.process(processing_step)
        dataset_.export_to(self.exporter)
        self.importer.source = self.source
        self.dataset.import_from(self.importer)
        self.assertDictEqual(dataset_.history[0].to_dict(),
                             self.dataset.history[0].to_dict())
