"""Tests for input and output (IO)."""

import collections
import os
import unittest

import oyaml as yaml

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

    def test_import_into_with_dataset_sets_source(self):
        test_dataset = dataset.Dataset()
        self.importer.source = 'filename'
        self.importer.import_into(test_dataset)
        self.assertIs(test_dataset.source, self.importer.source)


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


class TestYaml(unittest.TestCase):
    def setUp(self):
        self.yaml = io.Yaml()
        self.filename = 'test.yaml'
        self.dict = {'foo': 'bar'}

    def tearDown(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def test_instantiate_class(self):
        pass

    def test_has_dict_property(self):
        self.assertTrue(hasattr(self.yaml, 'dict'))

    def test_dict_property_is_ordered_dict(self):
        self.assertTrue(isinstance(self.yaml.dict, collections.OrderedDict))

    def test_has_read_from_method(self):
        self.assertTrue(hasattr(self.yaml, 'read_from'))
        self.assertTrue(callable(self.yaml.read_from))

    def test_read_from_without_filename_raises(self):
        with self.assertRaises(io.MissingFilenameError):
            self.yaml.read_from()

    def test_has_write_to_method(self):
        self.assertTrue(hasattr(self.yaml, 'write_to'))
        self.assertTrue(callable(self.yaml.write_to))

    def test_write_to_without_filename_raises(self):
        with self.assertRaises(io.MissingFilenameError):
            self.yaml.write_to()

    def test_read_from_reads_file(self):
        with open(self.filename, 'w') as file:
            yaml.dump(self.dict, file)
        self.yaml.read_from(self.filename)
        self.assertEqual(self.dict, self.yaml.dict)

    def test_writes_to_writes_file(self):
        self.yaml.dict = self.dict
        self.yaml.write_to(self.filename)
        with open(self.filename, 'r') as file:
            contents = yaml.load(file)
        self.assertEqual(contents, self.yaml.dict)


class TestImporterFactory(unittest.TestCase):
    def setUp(self):
        self.factory = io.ImporterFactory()
        self.source = 'foo'

    def test_instantiate_class(self):
        pass

    def test_get_importer_returns_importer(self):
        importer = self.factory.get_importer(source=self.source)
        self.assertTrue(isinstance(importer, io.Importer))

    def test_get_importer_sets_source_in_importer(self):
        importer = self.factory.get_importer(source=self.source)
        self.assertEqual(self.source, importer.source)

    def test_get_importer_without_source_raises(self):
        with self.assertRaises(io.MissingSourceError):
            self.factory.get_importer()
