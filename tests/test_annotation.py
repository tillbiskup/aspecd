"""Tests for annotation."""

import unittest

from aspecd import annotation, dataset


class TestAnnotation(unittest.TestCase):
    def setUp(self):
        self.annotation = annotation.Annotation()
        self.annotation.content['foo'] = 'bar'

    def test_instantiate_class(self):
        pass

    def test_has_scope_property(self):
        self.assertTrue(hasattr(self.annotation, 'scope'))

    def test_scope_property_is_string(self):
        self.assertTrue(isinstance(self.annotation.scope, str))

    def test_has_content_property(self):
        self.assertTrue(hasattr(self.annotation, 'content'))

    def test_content_property_is_dict(self):
        self.assertTrue(isinstance(self.annotation.content, dict))

    def test_has_dataset_property(self):
        self.assertTrue(hasattr(self.annotation, 'dataset'))

    def test_dataset_property_is_initially_none(self):
        self.assertEqual(self.annotation.dataset, None)

    def test_has_type_property(self):
        self.assertTrue(hasattr(self.annotation, 'type'))

    def test_type_property_equals_lower_classname(self):
        self.assertEqual(self.annotation.type,
                         self.annotation.__class__.__name__.lower())

    def test_has_annotate_method(self):
        self.assertTrue(hasattr(self.annotation, 'annotate'))
        self.assertTrue(callable(self.annotation.annotate))

    def test_annotate_without_argument_and_with_dataset(self):
        self.annotation.dataset = dataset.Dataset()
        self.annotation.annotate()
        self.assertGreater(len(self.annotation.dataset.annotations), 0)

    def test_annotate_without_argument_nor_dataset_raises(self):
        with self.assertRaises(annotation.MissingDatasetError):
            self.annotation.annotate()

    def test_annotate_with_empty_content_raises(self):
        self.annotation.dataset = dataset.Dataset()
        self.annotation.content.clear()
        with self.assertRaises(annotation.NoContentError):
            self.annotation.annotate()


class TestComment(unittest.TestCase):
    def setUp(self):
        self.comment = annotation.Comment()

    def test_instantiate_class(self):
        pass

    def test_type_property_equals_lower_classname_in_derived_class(self):
        self.assertEqual(self.comment.type,
                         self.comment.__class__.__name__.lower())

    def test_content_has_key_comment(self):
        self.assertTrue('comment' in self.comment.content)

    def test_has_comment_property(self):
        self.assertTrue(hasattr(self.comment, 'comment'))

    def test_comment_property_sets_content_comment(self):
        commenttext = 'Lorem ipsum'
        self.comment.comment = commenttext
        self.assertEqual(self.comment.content['comment'], commenttext)

    def test_comment_property_gets_content_comment(self):
        commenttext = 'Lorem ipsum'
        self.comment.content['comment'] = commenttext
        self.assertEqual(self.comment.comment, commenttext)


class TestArtefact(unittest.TestCase):
    def setUp(self):
        self.artefact = annotation.Artefact()

    def test_instantiate_class(self):
        pass

    def test_content_has_key_comment(self):
        self.assertTrue('comment' in self.artefact.content)


class TestCharacteristic(unittest.TestCase):
    def setUp(self):
        self.characteristic = annotation.Characteristic()

    def test_instantiate_class(self):
        pass