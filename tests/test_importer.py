"""Tests for plotting."""

import unittest

from aspecd import importer, dataset


class TestImporter(unittest.TestCase):
    def setUp(self):
        self.importer = importer.Importer()

    def test_instantiate_class(self):
        pass

    def test_instantiate_with_source_sets_source(self):
        source = 'filename'
        importer_ = importer.Importer(source)
        self.assertEqual(importer_.source, source)

    def test_has_load_method(self):
        self.assertTrue(hasattr(self.importer, 'import_into'))
        self.assertTrue(callable(self.importer.import_into))

    def test_import_into_without_dataset_raises(self):
        with self.assertRaises(importer.MissingDatasetError):
            self.importer.import_into()

    def test_import_into_with_dataset_sets_dataset(self):
        test_dataset = dataset.Dataset()
        self.importer.import_into(test_dataset)
        self.assertIs(self.importer.dataset, test_dataset)
