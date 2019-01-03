"""Tests for input and output (IO)."""

import unittest

from aspecd import io, dataset


class TestImporter(unittest.TestCase):
    def setUp(self):
        self.importer = io.DatasetImporter()

    def test_instantiate_class(self):
        pass

    def test_instantiate_with_source_sets_source(self):
        source = 'filename'
        importer_ = io.DatasetImporter(source)
        self.assertEqual(importer_.source, source)

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

    def test_import_into_with_dataset_sets_source(self):
        test_dataset = dataset.Dataset()
        self.importer.source = 'filename'
        self.importer.import_into(test_dataset)
        self.assertIs(test_dataset.source, self.importer.source)


class TestExporter(unittest.TestCase):
    def setUp(self):
        self.exporter = io.DatasetExporter()

    def test_instantiate_class(self):
        pass

    def test_instantiate_with_target_sets_target(self):
        target = 'filename'
        exporter_ = io.DatasetExporter(target=target)
        self.assertEqual(exporter_.target, target)

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


class TestImporterFactory(unittest.TestCase):
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
