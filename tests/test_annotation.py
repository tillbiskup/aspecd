"""Tests for annotation."""

import unittest

import aspecd.annotation
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

    def test_annotate_via_dataset_annotate(self):
        test_dataset = dataset.Dataset()
        test_dataset.annotate(self.annotation)
        self.assertGreater(len(test_dataset.annotations), 0)

    def test_annotate_with_dataset(self):
        test_dataset = dataset.Dataset()
        self.annotation.annotate(test_dataset)
        self.assertGreater(len(test_dataset.annotations), 0)

    def test_annotate_without_argument_nor_dataset_raises(self):
        with self.assertRaises(annotation.MissingDatasetError):
            self.annotation.annotate()

    def test_annotate_with_empty_content_raises(self):
        self.annotation.dataset = dataset.Dataset()
        self.annotation.content.clear()
        with self.assertRaises(annotation.NoContentError):
            self.annotation.annotate()

    def test_annotate_with_empty_scope_sets_default_scope(self):
        self.annotation.dataset = dataset.Dataset()
        self.annotation.annotate()
        self.assertEqual(self.annotation.scope, 'dataset')

    def test_setting_unknown_scope_raises(self):
        with self.assertRaises(annotation.UnknownScopeError):
            self.annotation.scope = 'foo'

    def test_annotate_returns_dataset(self):
        test_dataset = self.annotation.annotate(dataset.Dataset())
        self.assertTrue(isinstance(test_dataset, dataset.Dataset))

    def test_has_create_history_record_method(self):
        self.assertTrue(hasattr(self.annotation, 'create_history_record'))
        self.assertTrue(callable(self.annotation.create_history_record))

    def test_create_history_record_returns_history_record(self):
        self.annotation.dataset = dataset.Dataset()
        history_record = self.annotation.create_history_record()
        self.assertTrue(isinstance(history_record,
                                   annotation.AnnotationHistoryRecord))


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


class TestAnnotationRecord(unittest.TestCase):
    def setUp(self):
        self.annotation = aspecd.annotation.Annotation()
        self.annotation_record = \
            aspecd.annotation.AnnotationRecord(self.annotation)

    def test_instantiate_class(self):
        pass

    def test_instantiate_without_annotation_raises(self):
        with self.assertRaises(aspecd.annotation.MissingAnnotationError):
            aspecd.annotation.AnnotationRecord()

    def test_instantiate_class_with_annotation(self):
        aspecd.annotation.AnnotationRecord(self.annotation)

    def test_instantiate_content_from_annotation(self):
        self.annotation.content = {'foo': 'bar'}
        annotation_record = \
            aspecd.annotation.AnnotationRecord(self.annotation)
        self.assertEqual(annotation_record.content, self.annotation.content)

    def test_instantiate_class_name_from_annotation(self):
        annotation_record = \
            aspecd.annotation.AnnotationRecord(self.annotation)
        self.assertEqual(annotation_record.class_name,
                         aspecd.utils.full_class_name(self.annotation))

    def test_has_create_annotation_method(self):
        self.assertTrue(hasattr(self.annotation_record,
                                'create_annotation'))
        self.assertTrue(
            callable(self.annotation_record.create_annotation))

    def test_create_annotation_returns_annotation_object(self):
        test_object = self.annotation_record.create_annotation()
        self.assertTrue(isinstance(test_object, aspecd.annotation.Annotation))

    def test_annotation_object_has_correct_contents_value(self):
        self.annotation_record.content = {'foo': 'bar'}
        test_object = self.annotation_record.create_annotation()
        self.assertEqual(self.annotation_record.content, test_object.content)


class TestAnnotationHistoryRecord(unittest.TestCase):
    def setUp(self):
        self.annotation = aspecd.annotation.Annotation()
        self.annotationrecord = aspecd.annotation.AnnotationHistoryRecord(
            annotation=self.annotation)

    def test_instantiate_class(self):
        pass

    def test_instantiate_class_with_package_name(self):
        aspecd.annotation.AnnotationHistoryRecord(
            annotation=self.annotation, package="numpy")

    def test_instantiate_class_with_package_name_sets_sysinfo(self):
        annotation_step = aspecd.annotation.AnnotationHistoryRecord(
            annotation=self.annotation, package="numpy")
        self.assertTrue("numpy" in annotation_step.sysinfo.packages.keys())

    def test_has_annotation_property(self):
        self.assertTrue(hasattr(self.annotationrecord, 'annotation'))

    def test_annotation_is_annotation_record(self):
        self.assertTrue(isinstance(self.annotationrecord.annotation,
                                   annotation.AnnotationRecord))
