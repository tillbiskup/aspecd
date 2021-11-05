"""Tests for annotation."""

import unittest

import aspecd.annotation
import aspecd.dataset
import aspecd.exceptions
import aspecd.history


class TestAnnotation(unittest.TestCase):
    def setUp(self):
        self.annotation = aspecd.annotation.Annotation()
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

    def test_has_to_dict_method(self):
        self.assertTrue(hasattr(self.annotation, 'to_dict'))
        self.assertTrue(callable(self.annotation.to_dict))

    def test_to_dict_does_not_contain_certain_keys(self):
        for key in ['dataset', 'type']:
            with self.subTest(key=key):
                self.assertNotIn(key, self.annotation.to_dict())

    def test_has_annotate_method(self):
        self.assertTrue(hasattr(self.annotation, 'annotate'))
        self.assertTrue(callable(self.annotation.annotate))

    def test_annotate_without_argument_and_with_dataset(self):
        self.annotation.dataset = aspecd.dataset.Dataset()
        self.annotation.annotate()
        self.assertGreater(len(self.annotation.dataset.annotations), 0)

    def test_annotate_via_dataset_annotate(self):
        test_dataset = aspecd.dataset.Dataset()
        test_dataset.annotate(self.annotation)
        self.assertGreater(len(test_dataset.annotations), 0)

    def test_annotate_with_dataset(self):
        test_dataset = aspecd.dataset.Dataset()
        self.annotation.annotate(test_dataset)
        self.assertGreater(len(test_dataset.annotations), 0)

    def test_annotate_without_argument_nor_dataset_raises(self):
        with self.assertRaises(aspecd.exceptions.MissingDatasetError):
            self.annotation.annotate()

    def test_annotate_with_empty_content_raises(self):
        self.annotation.dataset = aspecd.dataset.Dataset()
        self.annotation.content.clear()
        with self.assertRaises(aspecd.exceptions.NoContentError):
            self.annotation.annotate()

    def test_annotate_with_empty_scope_sets_default_scope(self):
        self.annotation.dataset = aspecd.dataset.Dataset()
        self.annotation.annotate()
        self.assertEqual(self.annotation.scope, 'dataset')

    def test_setting_unknown_scope_raises(self):
        with self.assertRaises(aspecd.exceptions.UnknownScopeError):
            self.annotation.scope = 'foo'

    def test_annotate_returns_dataset(self):
        test_dataset = self.annotation.annotate(aspecd.dataset.Dataset())
        self.assertTrue(isinstance(test_dataset, aspecd.dataset.Dataset))

    def test_has_create_history_record_method(self):
        self.assertTrue(hasattr(self.annotation, 'create_history_record'))
        self.assertTrue(callable(self.annotation.create_history_record))

    def test_create_history_record_returns_history_record(self):
        self.annotation.dataset = aspecd.dataset.Dataset()
        history_record = self.annotation.create_history_record()
        self.assertTrue(isinstance(history_record,
                                   aspecd.history.AnnotationHistoryRecord))


class TestComment(unittest.TestCase):
    def setUp(self):
        self.comment = aspecd.annotation.Comment()

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
        self.artefact = aspecd.annotation.Artefact()

    def test_instantiate_class(self):
        pass

    def test_content_has_key_comment(self):
        self.assertTrue('comment' in self.artefact.content)


class TestCharacteristic(unittest.TestCase):
    def setUp(self):
        self.characteristic = aspecd.annotation.Characteristic()

    def test_instantiate_class(self):
        pass
