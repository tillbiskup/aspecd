"""Tests for input and output (IO)."""

import unittest

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
        with self.assertRaises(io.MissingDatasetError):
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
        with self.assertRaises(io.MissingDatasetError):
            self.exporter.export_from()

    def test_export_from_with_dataset_sets_dataset(self):
        test_dataset = dataset.Dataset()
        self.exporter.export_from(test_dataset)
        self.assertIs(self.exporter.dataset, test_dataset)


class TestDatasetImporterFactory(unittest.TestCase):
    def setUp(self):
        self.factory = io.DatasetImporterFactory()
        self.source = 'foo'

    def test_instantiate_class(self):
        pass

    def test_get_importer_returns_importer(self):
        importer = self.factory.get_importer(source=self.source)
        self.assertTrue(isinstance(importer, io.DatasetImporter))

    def test_get_importer_sets_source_in_importer(self):
        importer = self.factory.get_importer(source=self.source)
        self.assertEqual(self.source, importer.source)

    def test_get_importer_without_source_raises(self):
        with self.assertRaises(io.MissingSourceError):
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
        with self.assertRaises(io.MissingRecipeError):
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
        with self.assertRaises(io.MissingRecipeError):
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
