"""Tests for input and output (IO)."""

import unittest

from aspecd import io, dataset


class TestImporter(unittest.TestCase):
    def setUp(self):
        self.importer = io.Importer()

    def test_instantiate_class(self):
        pass

    def test_instantiate_with_source_sets_source(self):
        source = 'filename'
        importer_ = io.Importer(source)
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


class TestExporter(unittest.TestCase):
    def setUp(self):
        self.exporter = io.Exporter()

    def test_instantiate_class(self):
        pass

    def test_instantiate_with_target_sets_target(self):
        target = 'filename'
        exporter_ = io.Exporter(target=target)
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
