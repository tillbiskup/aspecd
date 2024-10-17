"""Tests for annotation."""

import unittest

import matplotlib
import numpy as np

import aspecd.annotation as annotation
import aspecd.dataset
import aspecd.exceptions
import aspecd.history
import aspecd.plotting


class TestDatasetAnnotation(unittest.TestCase):
    def setUp(self):
        self.annotation = annotation.DatasetAnnotation()
        self.annotation.content["foo"] = "bar"

    def test_instantiate_class(self):
        pass

    def test_has_scope_property(self):
        self.assertTrue(hasattr(self.annotation, "scope"))

    def test_scope_property_is_string(self):
        self.assertTrue(isinstance(self.annotation.scope, str))

    def test_has_content_property(self):
        self.assertTrue(hasattr(self.annotation, "content"))

    def test_content_property_is_dict(self):
        self.assertTrue(isinstance(self.annotation.content, dict))

    def test_has_dataset_property(self):
        self.assertTrue(hasattr(self.annotation, "dataset"))

    def test_dataset_property_is_initially_none(self):
        self.assertEqual(self.annotation.dataset, None)

    def test_has_type_property(self):
        self.assertTrue(hasattr(self.annotation, "type"))

    def test_type_property_equals_lower_classname(self):
        self.assertEqual(
            self.annotation.type, self.annotation.__class__.__name__.lower()
        )

    def test_has_to_dict_method(self):
        self.assertTrue(hasattr(self.annotation, "to_dict"))
        self.assertTrue(callable(self.annotation.to_dict))

    def test_to_dict_does_not_contain_certain_keys(self):
        for key in ["dataset", "type"]:
            with self.subTest(key=key):
                self.assertNotIn(key, self.annotation.to_dict())

    def test_has_annotate_method(self):
        self.assertTrue(hasattr(self.annotation, "annotate"))
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
        self.assertEqual(self.annotation.scope, "dataset")

    def test_setting_unknown_scope_raises(self):
        with self.assertRaises(aspecd.exceptions.UnknownScopeError):
            self.annotation.scope = "foo"

    def test_annotate_returns_dataset(self):
        test_dataset = self.annotation.annotate(aspecd.dataset.Dataset())
        self.assertTrue(isinstance(test_dataset, aspecd.dataset.Dataset))

    def test_has_create_history_record_method(self):
        self.assertTrue(hasattr(self.annotation, "create_history_record"))
        self.assertTrue(callable(self.annotation.create_history_record))

    def test_create_history_record_returns_history_record(self):
        self.annotation.dataset = aspecd.dataset.Dataset()
        history_record = self.annotation.create_history_record()
        self.assertIsInstance(
            history_record, aspecd.history.AnnotationHistoryRecord
        )


class TestComment(unittest.TestCase):
    def setUp(self):
        self.comment = annotation.Comment()

    def test_instantiate_class(self):
        pass

    def test_type_property_equals_lower_classname_in_derived_class(self):
        self.assertEqual(
            self.comment.type, self.comment.__class__.__name__.lower()
        )

    def test_content_has_key_comment(self):
        self.assertTrue("comment" in self.comment.content)

    def test_has_comment_property(self):
        self.assertTrue(hasattr(self.comment, "comment"))

    def test_comment_property_sets_content_comment(self):
        commenttext = "Lorem ipsum"
        self.comment.comment = commenttext
        self.assertEqual(self.comment.content["comment"], commenttext)

    def test_comment_property_gets_content_comment(self):
        commenttext = "Lorem ipsum"
        self.comment.content["comment"] = commenttext
        self.assertEqual(self.comment.comment, commenttext)


class TestArtefact(unittest.TestCase):
    def setUp(self):
        self.artefact = annotation.Artefact()

    def test_instantiate_class(self):
        pass

    def test_content_has_key_comment(self):
        self.assertTrue("comment" in self.artefact.content)


class TestCharacteristic(unittest.TestCase):
    def setUp(self):
        self.characteristic = annotation.Characteristic()

    def test_instantiate_class(self):
        pass


class TestPlotAnnotation(unittest.TestCase):
    def setUp(self):
        self.annotation = annotation.PlotAnnotation()

    def test_instantiate_class(self):
        pass

    def test_has_plotter_property(self):
        self.assertTrue(hasattr(self.annotation, "plotter"))

    def test_plotter_property_is_initially_none(self):
        self.assertEqual(self.annotation.plotter, None)

    def test_has_type_property(self):
        self.assertTrue(hasattr(self.annotation, "type"))

    def test_type_property_equals_lower_classname(self):
        self.assertEqual(
            self.annotation.type, self.annotation.__class__.__name__.lower()
        )

    def test_has_parameters_property(self):
        self.assertTrue(hasattr(self.annotation, "parameters"))
        self.assertIsInstance(self.annotation.parameters, dict)

    def test_has_properties_property(self):
        self.assertTrue(hasattr(self.annotation, "properties"))

    def test_has_drawings_property(self):
        self.assertTrue(hasattr(self.annotation, "drawings"))
        self.assertIsInstance(self.annotation.drawings, list)

    def test_has_to_dict_method(self):
        self.assertTrue(hasattr(self.annotation, "to_dict"))
        self.assertTrue(callable(self.annotation.to_dict))

    def test_to_dict_does_not_contain_certain_keys(self):
        for key in ["plotter", "type", "drawings"]:
            with self.subTest(key=key):
                self.assertNotIn(key, self.annotation.to_dict())

    def test_has_annotate_method(self):
        self.assertTrue(hasattr(self.annotation, "annotate"))
        self.assertTrue(callable(self.annotation.annotate))

    def test_annotate_without_argument_and_with_plotter(self):
        self.annotation.plotter = aspecd.plotting.Plotter()
        self.annotation.annotate()
        self.assertGreater(len(self.annotation.plotter.annotations), 0)

    def test_annotate_via_plotter_annotate(self):
        test_plotter = aspecd.plotting.Plotter()
        test_plotter.annotate(self.annotation)
        self.assertGreater(len(test_plotter.annotations), 0)

    def test_annotate_with_plotter(self):
        test_plotter = aspecd.plotting.Plotter()
        self.annotation.annotate(test_plotter)
        self.assertGreater(len(test_plotter.annotations), 0)

    def test_annotate_without_argument_nor_plotter_raises(self):
        with self.assertRaises(aspecd.exceptions.MissingPlotterError):
            self.annotation.annotate()

    @unittest.skip
    def test_annotate_with_empty_parameters_raises(self):
        self.annotation.plotter = aspecd.plotting.Plotter()
        self.annotation.parameters.clear()
        with self.assertRaises(aspecd.exceptions.NoContentError):
            self.annotation.annotate()

    def test_annotate_returns_plotter(self):
        test_plotter = self.annotation.annotate(aspecd.plotting.Plotter())
        self.assertTrue(isinstance(test_plotter, aspecd.plotting.Plotter))


class TestVerticalLine(unittest.TestCase):
    def setUp(self):
        self.annotation = annotation.VerticalLine()
        self.plotter = aspecd.plotting.Plotter()

    def test_instantiate_class(self):
        pass

    def test_annotate_adds_line_to_plotter(self):
        self.annotation.parameters["positions"] = [0.5]
        self.plotter.plot()
        annotation_ = self.plotter.annotate(self.annotation)
        self.assertIn(annotation_.drawings[0], self.plotter.ax.get_children())

    def test_annotate_adds_line_at_correct_position(self):
        self.annotation.parameters["positions"] = [0.5]
        self.plotter.plot()
        annotation_ = self.plotter.annotate(self.annotation)
        self.assertEqual(
            annotation_.parameters["positions"][0],
            annotation_.drawings[0].get_xdata()[0],
        )

    def test_annotate_adds_lines_to_plotter(self):
        self.annotation.parameters["positions"] = [0.25, 0.5, 0.75]
        self.plotter.plot()
        annotation_ = self.plotter.annotate(self.annotation)
        self.assertEqual(
            len(annotation_.parameters["positions"]),
            len(annotation_.drawings),
        )
        for drawing in annotation_.drawings:
            self.assertIn(drawing, self.plotter.ax.get_children())

    def test_annotate_adds_line_to_plotter_after_plotting(self):
        self.annotation.parameters["positions"] = [0.5]
        annotation_ = self.plotter.annotate(self.annotation)
        self.plotter.plot()
        self.assertIn(annotation_.drawings[0], self.plotter.ax.get_children())

    def test_annotate_before_plotting_does_not_add_annotation_twice(self):
        self.annotation.parameters["positions"] = [0.5]
        self.plotter.annotate(self.annotation)
        self.plotter.plot()
        self.assertEqual(1, len(self.plotter.annotations))

    def test_set_line_colour_from_dict(self):
        line_colour = "#cccccc"
        properties = {"color": line_colour}
        self.annotation.properties.from_dict(properties)
        self.assertEqual(line_colour, self.annotation.properties.color)

    def test_annotate_sets_correct_line_color(self):
        color = "#cccccc"
        properties = {"color": color}
        self.annotation.properties.from_dict(properties)
        self.plotter.plot()
        self.annotation.parameters["positions"] = [0.5]
        annotation_ = self.plotter.annotate(self.annotation)
        self.assertEqual(color, annotation_.drawings[0].get_color())

    def test_annotate_sets_correct_line_color_for_each_line(self):
        color = "#cccccc"
        properties = {"color": color}
        self.annotation.properties.from_dict(properties)
        self.plotter.plot()
        self.annotation.parameters["positions"] = [0.25, 0.5, 0.75]
        annotation_ = self.plotter.annotate(self.annotation)
        for drawing in annotation_.drawings:
            self.assertEqual(color, drawing.get_color())

    def test_annotate_with_limits_sets_limits(self):
        self.annotation.parameters["positions"] = [0.5]
        self.annotation.parameters["limits"] = [0.25, 0.75]
        self.plotter.plot()
        annotation_ = self.plotter.annotate(self.annotation)
        self.assertListEqual(
            annotation_.parameters["limits"],
            annotation_.drawings[0].get_ydata(),
        )


class TestHorizontalLine(unittest.TestCase):
    def setUp(self):
        self.annotation = annotation.HorizontalLine()
        self.plotter = aspecd.plotting.Plotter()

    def test_instantiate_class(self):
        pass

    def test_annotate_adds_line_to_plotter(self):
        self.annotation.parameters["positions"] = [0.5]
        self.plotter.plot()
        annotation_ = self.plotter.annotate(self.annotation)
        self.assertIn(annotation_.drawings[0], self.plotter.ax.get_children())

    def test_annotate_adds_line_at_correct_position(self):
        self.annotation.parameters["positions"] = [0.5]
        self.plotter.plot()
        annotation_ = self.plotter.annotate(self.annotation)
        self.assertEqual(
            annotation_.parameters["positions"][0],
            annotation_.drawings[0].get_ydata()[0],
        )

    def test_annotate_adds_lines_to_plotter(self):
        self.annotation.parameters["positions"] = [0.25, 0.5, 0.75]
        self.plotter.plot()
        annotation_ = self.plotter.annotate(self.annotation)
        self.assertEqual(
            len(annotation_.parameters["positions"]),
            len(annotation_.drawings),
        )
        for drawing in annotation_.drawings:
            self.assertIn(drawing, self.plotter.ax.get_children())

    def test_annotate_adds_line_to_plotter_after_plotting(self):
        self.annotation.parameters["positions"] = [0.5]
        annotation_ = self.plotter.annotate(self.annotation)
        self.plotter.plot()
        self.assertIn(annotation_.drawings[0], self.plotter.ax.get_children())

    def test_set_line_colour_from_dict(self):
        line_colour = "#cccccc"
        properties = {"color": line_colour}
        self.annotation.properties.from_dict(properties)
        self.assertEqual(line_colour, self.annotation.properties.color)

    def test_annotate_sets_correct_line_color(self):
        color = "#cccccc"
        properties = {"color": color}
        self.annotation.properties.from_dict(properties)
        self.plotter.plot()
        self.annotation.parameters["positions"] = [0.5]
        annotation_ = self.plotter.annotate(self.annotation)
        self.assertEqual(color, annotation_.drawings[0].get_color())

    def test_annotate_sets_correct_line_color_for_each_line(self):
        color = "#cccccc"
        properties = {"color": color}
        self.annotation.properties.from_dict(properties)
        self.plotter.plot()
        self.annotation.parameters["positions"] = [0.25, 0.5, 0.75]
        annotation_ = self.plotter.annotate(self.annotation)
        for drawing in annotation_.drawings:
            self.assertEqual(color, drawing.get_color())

    def test_annotate_with_limits_sets_limits(self):
        self.annotation.parameters["positions"] = [0.5]
        self.annotation.parameters["limits"] = [0.25, 0.75]
        self.plotter.plot()
        annotation_ = self.plotter.annotate(self.annotation)
        self.assertListEqual(
            annotation_.parameters["limits"],
            annotation_.drawings[0].get_xdata(),
        )


class TestText(unittest.TestCase):
    def setUp(self):
        self.annotation = annotation.Text()
        self.plotter = aspecd.plotting.Plotter()

    def test_instantiate_class(self):
        pass

    def test_annotate_adds_text_to_plotter(self):
        self.annotation.parameters["positions"] = [[0.5, 0.5]]
        self.annotation.parameters["texts"] = ["foo"]
        self.plotter.plot()
        annotation_ = self.plotter.annotate(self.annotation)
        self.assertIn(annotation_.drawings[0], self.plotter.ax.get_children())

    def test_annotate_adds_text_at_correct_position(self):
        self.annotation.parameters["positions"] = [[0.5, 0.5]]
        self.annotation.parameters["texts"] = ["foo"]
        self.plotter.plot()
        annotation_ = self.plotter.annotate(self.annotation)
        self.assertListEqual(
            annotation_.parameters["positions"][0],
            list(annotation_.drawings[0].get_position()),
        )

    def test_annotate_adds_correct_text(self):
        self.annotation.parameters["positions"] = [[0.5, 0.5]]
        self.annotation.parameters["texts"] = ["foo"]
        self.plotter.plot()
        annotation_ = self.plotter.annotate(self.annotation)
        result = [
            item
            for item in self.plotter.ax.get_children()
            if item is annotation_.drawings[0]
        ][0]
        self.assertEqual(
            annotation_.parameters["texts"][0], result.get_text()
        )

    def test_annotate_adds_texts_to_plotter(self):
        self.annotation.parameters["positions"] = [[0.5, 0.5], [0.7, 0.7]]
        self.annotation.parameters["texts"] = ["foo", "bar"]
        self.plotter.plot()
        annotation_ = self.plotter.annotate(self.annotation)
        self.assertEqual(
            len(annotation_.parameters["positions"]),
            len(annotation_.drawings),
        )
        for drawing in annotation_.drawings:
            self.assertIn(drawing, self.plotter.ax.get_children())

    def test_annotate_with_xpositions_and_ypositions(self):
        self.annotation.parameters["xpositions"] = [0.3]
        self.annotation.parameters["ypositions"] = [0.7]
        self.annotation.parameters["texts"] = ["foo"]
        self.plotter.plot()
        annotation_ = self.plotter.annotate(self.annotation)
        self.assertIn(annotation_.drawings[0], self.plotter.ax.get_children())

    def test_annotate_with_xpositions_as_ndarray_and_ypositions(self):
        self.annotation.parameters["xpositions"] = np.asarray([0.3, 0.4])
        self.annotation.parameters["ypositions"] = [0.7, 0.7]
        self.annotation.parameters["texts"] = ["foo", "bar"]
        self.plotter.plot()
        annotation_ = self.plotter.annotate(self.annotation)
        self.assertIn(annotation_.drawings[0], self.plotter.ax.get_children())

    def test_annotate_with_xpositions_and_ypositions_zero(self):
        self.annotation.parameters["xpositions"] = [0]
        self.annotation.parameters["ypositions"] = [0]
        self.annotation.parameters["texts"] = ["foo"]
        self.plotter.plot()
        annotation_ = self.plotter.annotate(self.annotation)
        self.assertIn(annotation_.drawings[0], self.plotter.ax.get_children())

    def test_annotate_with_xpositions_and_scalar_ypositions(self):
        self.annotation.parameters["xpositions"] = [0.3]
        self.annotation.parameters["ypositions"] = 0.7
        self.annotation.parameters["texts"] = ["foo"]
        self.plotter.plot()
        annotation_ = self.plotter.annotate(self.annotation)
        self.assertIn(annotation_.drawings[0], self.plotter.ax.get_children())

    def test_annotate_with_xpositions_and_scalar_ypositions_zero(self):
        self.annotation.parameters["xpositions"] = [0.3]
        self.annotation.parameters["ypositions"] = 0
        self.annotation.parameters["texts"] = ["foo"]
        self.plotter.plot()
        annotation_ = self.plotter.annotate(self.annotation)
        self.assertIn(annotation_.drawings[0], self.plotter.ax.get_children())

    def test_annotate_with_many_xpositions_and_one_ypositions(self):
        self.annotation.parameters["xpositions"] = [0.3, 0.5, 0.7]
        self.annotation.parameters["ypositions"] = [0.7]
        self.annotation.parameters["texts"] = ["foo", "bar", "baz"]
        self.plotter.plot()
        annotation_ = self.plotter.annotate(self.annotation)
        self.assertIn(annotation_.drawings[0], self.plotter.ax.get_children())

    def test_to_dict_contains_properties(self):
        dict_ = self.annotation.to_dict()
        self.assertIn("properties", dict_)


class TestVerticalSpan(unittest.TestCase):
    def setUp(self):
        self.annotation = annotation.VerticalSpan()
        self.plotter = aspecd.plotting.Plotter()

    def test_instantiate_class(self):
        pass

    def test_annotate_adds_span_to_plotter(self):
        self.annotation.parameters["positions"] = [[0.5, 0.6]]
        self.plotter.plot()
        annotation_ = self.plotter.annotate(self.annotation)
        self.assertIn(annotation_.drawings[0], self.plotter.ax.get_children())

    def test_annotate_adds_span_at_correct_position(self):
        self.annotation.parameters["positions"] = [[0.5, 0.6]]
        self.plotter.plot()
        annotation_ = self.plotter.annotate(self.annotation)
        self.assertEqual(
            annotation_.parameters["positions"][0][0],
            annotation_.drawings[0].get_corners()[0][0],
        )
        self.assertEqual(
            annotation_.parameters["positions"][0][1],
            annotation_.drawings[0].get_corners()[1][0],
        )

    def test_annotate_adds_spans_to_plotter(self):
        self.annotation.parameters["positions"] = [[0.1, 0.3], [0.5, 0.6]]
        self.plotter.plot()
        annotation_ = self.plotter.annotate(self.annotation)
        self.assertEqual(
            len(annotation_.parameters["positions"]),
            len(annotation_.drawings),
        )
        for drawing in annotation_.drawings:
            self.assertIn(drawing, self.plotter.ax.get_children())

    def test_annotate_adds_span_to_plotter_after_plotting(self):
        self.annotation.parameters["positions"] = [[0.5, 0.6]]
        annotation_ = self.plotter.annotate(self.annotation)
        self.plotter.plot()
        self.assertIn(annotation_.drawings[0], self.plotter.ax.get_children())

    def test_annotate_before_plotting_does_not_add_annotation_twice(self):
        self.annotation.parameters["positions"] = [[0.5, 0.6]]
        self.plotter.annotate(self.annotation)
        self.plotter.plot()
        self.assertEqual(1, len(self.plotter.annotations))

    def test_set_span_facecolour_from_dict(self):
        color = "#cccccc"
        properties = {"facecolor": color}
        self.annotation.properties.from_dict(properties)
        self.assertEqual(color, self.annotation.properties.facecolor)

    def test_annotate_sets_correct_facecolor(self):
        color = "#cccccc"
        properties = {"facecolor": color}
        self.annotation.properties.from_dict(properties)
        self.plotter.plot()
        self.annotation.parameters["positions"] = [[0.5, 0.6]]
        annotation_ = self.plotter.annotate(self.annotation)
        self.assertEqual(
            color,
            matplotlib.colors.to_hex(annotation_.drawings[0].get_facecolor()),
        )

    def test_annotate_sets_correct_facecolor_for_each_span(self):
        color = "#cccccc"
        properties = {"facecolor": color}
        self.annotation.properties.from_dict(properties)
        self.plotter.plot()
        self.annotation.parameters["positions"] = [[0.1, 0.3], [0.5, 0.6]]
        annotation_ = self.plotter.annotate(self.annotation)
        for drawing in annotation_.drawings:
            self.assertEqual(
                color, matplotlib.colors.to_hex(drawing.get_facecolor())
            )

    def test_annotate_with_limits_sets_limits(self):
        self.annotation.parameters["positions"] = [[0.5, 0.6]]
        self.annotation.parameters["limits"] = [0.25, 0.75]
        self.plotter.plot()
        annotation_ = self.plotter.annotate(self.annotation)
        self.assertListEqual(
            annotation_.parameters["limits"],
            list(annotation_.drawings[0].get_corners()[:, 1][1:3]),
        )


class TestHorizontalSpan(unittest.TestCase):
    def setUp(self):
        self.annotation = annotation.HorizontalSpan()
        self.plotter = aspecd.plotting.Plotter()

    def test_instantiate_class(self):
        pass

    def test_annotate_adds_span_to_plotter(self):
        self.annotation.parameters["positions"] = [[0.5, 0.6]]
        self.plotter.plot()
        annotation_ = self.plotter.annotate(self.annotation)
        self.assertIn(annotation_.drawings[0], self.plotter.ax.get_children())

    def test_annotate_adds_span_at_correct_position(self):
        self.annotation.parameters["positions"] = [[0.5, 0.6]]
        self.plotter.plot()
        annotation_ = self.plotter.annotate(self.annotation)
        self.assertEqual(
            annotation_.parameters["positions"][0][0],
            annotation_.drawings[0].get_corners()[1][1],
        )
        self.assertEqual(
            annotation_.parameters["positions"][0][1],
            annotation_.drawings[0].get_corners()[2][1],
        )

    def test_annotate_adds_spans_to_plotter(self):
        self.annotation.parameters["positions"] = [[0.1, 0.3], [0.5, 0.6]]
        self.plotter.plot()
        annotation_ = self.plotter.annotate(self.annotation)
        self.assertEqual(
            len(annotation_.parameters["positions"]),
            len(annotation_.drawings),
        )
        for drawing in annotation_.drawings:
            self.assertIn(drawing, self.plotter.ax.get_children())

    def test_annotate_adds_span_to_plotter_after_plotting(self):
        self.annotation.parameters["positions"] = [[0.5, 0.6]]
        annotation_ = self.plotter.annotate(self.annotation)
        self.plotter.plot()
        self.assertIn(annotation_.drawings[0], self.plotter.ax.get_children())

    def test_annotate_before_plotting_does_not_add_annotation_twice(self):
        self.annotation.parameters["positions"] = [[0.5, 0.6]]
        self.plotter.annotate(self.annotation)
        self.plotter.plot()
        self.assertEqual(1, len(self.plotter.annotations))

    def test_set_span_facecolour_from_dict(self):
        color = "#cccccc"
        properties = {"facecolor": color}
        self.annotation.properties.from_dict(properties)
        self.assertEqual(color, self.annotation.properties.facecolor)

    def test_annotate_sets_correct_facecolor(self):
        color = "#cccccc"
        properties = {"facecolor": color}
        self.annotation.properties.from_dict(properties)
        self.plotter.plot()
        self.annotation.parameters["positions"] = [[0.5, 0.6]]
        annotation_ = self.plotter.annotate(self.annotation)
        self.assertEqual(
            color,
            matplotlib.colors.to_hex(annotation_.drawings[0].get_facecolor()),
        )

    def test_annotate_sets_correct_facecolor_for_each_span(self):
        color = "#cccccc"
        properties = {"facecolor": color}
        self.annotation.properties.from_dict(properties)
        self.plotter.plot()
        self.annotation.parameters["positions"] = [[0.1, 0.3], [0.5, 0.6]]
        annotation_ = self.plotter.annotate(self.annotation)
        for drawing in annotation_.drawings:
            self.assertEqual(
                color, matplotlib.colors.to_hex(drawing.get_facecolor())
            )

    def test_annotate_with_limits_sets_limits(self):
        self.annotation.parameters["positions"] = [[0.5, 0.6]]
        self.annotation.parameters["limits"] = [0.25, 0.75]
        self.plotter.plot()
        annotation_ = self.plotter.annotate(self.annotation)
        self.assertListEqual(
            annotation_.parameters["limits"],
            list(annotation_.drawings[0].get_corners()[:, 0][0:2]),
        )


class TestTextWithLine(unittest.TestCase):
    def setUp(self):
        self.annotation = annotation.TextWithLine()
        self.plotter = aspecd.plotting.Plotter()

    def test_instantiate_class(self):
        pass

    def test_annotate_adds_text_to_plotter(self):
        self.annotation.parameters["positions"] = [[0.5, 0.5]]
        self.annotation.parameters["texts"] = ["foo"]
        self.plotter.plot()
        annotation_ = self.plotter.annotate(self.annotation)
        self.assertIn(annotation_.drawings[0], self.plotter.ax.get_children())

    def test_annotate_adds_text_at_correct_position(self):
        self.annotation.parameters["positions"] = [[0.5, 0.5]]
        self.annotation.parameters["texts"] = ["foo"]
        self.plotter.plot()
        annotation_ = self.plotter.annotate(self.annotation)
        self.assertListEqual(
            annotation_.parameters["positions"][0],
            list(annotation_.drawings[0].get_position()),
        )

    def test_annotate_adds_text_at_correct_offset(self):
        self.annotation.parameters["positions"] = [[0.5, 0.5]]
        self.annotation.parameters["offsets"] = [[1, 1]]
        self.annotation.parameters["texts"] = ["foo"]
        self.plotter.plot()
        annotation_ = self.plotter.annotate(self.annotation)
        self.assertListEqual(
            [1.5, 1.5],
            list(annotation_.drawings[0].get_position()),
        )

    def test_annotate_adds_correct_text(self):
        self.annotation.parameters["positions"] = [[0.5, 0.5]]
        self.annotation.parameters["texts"] = ["foo"]
        self.plotter.plot()
        annotation_ = self.plotter.annotate(self.annotation)
        result = [
            item
            for item in self.plotter.ax.get_children()
            if item is annotation_.drawings[0]
        ][0]
        self.assertEqual(
            annotation_.parameters["texts"][0], result.get_text()
        )

    def test_annotate_sets_correct_horizontal_alignment(self):
        self.annotation.parameters["positions"] = [
            [0.5, 0.5],
            [0.5, 0.5],
            [0.5, 0.5],
        ]
        self.annotation.parameters["offsets"] = [[0, 1], [1, 1], [-1, 1]]
        self.annotation.parameters["texts"] = ["foo", "bar", "baz"]
        self.plotter.plot()
        annotation_ = self.plotter.annotate(self.annotation)
        self.assertEqual(
            "center", annotation_.drawings[0].get_horizontalalignment()
        )
        self.assertEqual(
            "left", annotation_.drawings[1].get_horizontalalignment()
        )
        self.assertEqual(
            "right", annotation_.drawings[2].get_horizontalalignment()
        )

    def test_annotate_sets_correct_rel_position(self):
        self.annotation.parameters["positions"] = [
            [0.5, 0.5],
            [0.5, 0.5],
            [0.5, 0.5],
            [0.5, 0.5],
            [0.5, 0.5],
            [0.5, 0.5],
        ]
        self.annotation.parameters["offsets"] = [
            [0, 1],
            [1, 1],
            [-1, 1],
            [0, -1],
            [1, -1],
            [-1, -1],
        ]
        self.annotation.parameters["texts"] = [
            "foo",
            "bar",
            "baz",
            "-foo",
            "-bar",
            "-baz",
        ]
        self.plotter.plot()
        annotation_ = self.plotter.annotate(self.annotation)
        relpos = [
            [0.5, 0.5],
            [0, 0],
            [1, 0],
            [0.5, 0.5],
            [0, 1],
            [1, 1],
        ]
        for idx, annotation in enumerate(annotation_.drawings):
            self.assertListEqual(relpos[idx], annotation.arrowprops["relpos"])

    def test_annotate_sets_correct_connection_style(self):
        self.annotation.parameters["positions"] = [
            [0.5, 0.5],
            [0.5, 0.5],
            [0.5, 0.5],
        ]
        self.annotation.parameters["offsets"] = [[0, 1], [1, 1], [-1, 1]]
        self.annotation.parameters["texts"] = ["foo", "bar", "baz"]
        self.plotter.plot()
        annotation_ = self.plotter.annotate(self.annotation)
        self.assertIsNone(
            annotation_.drawings[0].arrowprops["connectionstyle"]
        )
        self.assertIn(
            "angleA=-135",
            annotation_.drawings[1].arrowprops["connectionstyle"],
        )
        self.assertIn(
            "angleA=-45",
            annotation_.drawings[2].arrowprops["connectionstyle"],
        )

    def test_annotate_adds_texts_to_plotter(self):
        self.annotation.parameters["positions"] = [[0.5, 0.5], [0.7, 0.7]]
        self.annotation.parameters["texts"] = ["foo", "bar"]
        self.plotter.plot()
        annotation_ = self.plotter.annotate(self.annotation)
        self.assertEqual(
            len(annotation_.parameters["positions"]),
            len(annotation_.drawings),
        )
        for drawing in annotation_.drawings:
            self.assertIn(drawing, self.plotter.ax.get_children())

    def test_annotate_with_xpositions_and_ypositions(self):
        self.annotation.parameters["xpositions"] = [0.3]
        self.annotation.parameters["ypositions"] = [0.7]
        self.annotation.parameters["texts"] = ["foo"]
        self.plotter.plot()
        annotation_ = self.plotter.annotate(self.annotation)
        self.assertIn(annotation_.drawings[0], self.plotter.ax.get_children())

    def test_annotate_with_xpositions_as_ndarray_and_ypositions(self):
        self.annotation.parameters["xpositions"] = np.asarray([0.3, 0.5])
        self.annotation.parameters["ypositions"] = [0.7, 0.7]
        self.annotation.parameters["texts"] = ["foo", "bar"]
        self.plotter.plot()
        annotation_ = self.plotter.annotate(self.annotation)
        self.assertIn(annotation_.drawings[0], self.plotter.ax.get_children())

    def test_annotate_with_xpositions_and_scalar_ypositions(self):
        self.annotation.parameters["xpositions"] = [0.3]
        self.annotation.parameters["ypositions"] = 0.7
        self.annotation.parameters["texts"] = ["foo"]
        self.plotter.plot()
        annotation_ = self.plotter.annotate(self.annotation)
        self.assertIn(annotation_.drawings[0], self.plotter.ax.get_children())

    def test_annotate_with_many_xpositions_and_one_ypositions(self):
        self.annotation.parameters["xpositions"] = [0.3, 0.5, 0.7]
        self.annotation.parameters["ypositions"] = [0.7]
        self.annotation.parameters["texts"] = ["foo", "bar", "baz"]
        self.plotter.plot()
        annotation_ = self.plotter.annotate(self.annotation)
        self.assertIn(annotation_.drawings[0], self.plotter.ax.get_children())

    def test_to_dict_contains_properties(self):
        dict_ = self.annotation.to_dict()
        self.assertIn("properties", dict_)


class TestMarker(unittest.TestCase):
    def setUp(self):
        self.annotation = annotation.Marker()
        self.plotter = aspecd.plotting.Plotter()

    def test_instantiate_class(self):
        pass

    def test_annotate_adds_marker_to_plotter(self):
        self.annotation.parameters["positions"] = [[0.5, 0.5]]
        self.annotation.parameters["marker"] = "o"
        self.plotter.plot()
        annotation_ = self.plotter.annotate(self.annotation)
        self.assertIn(annotation_.drawings[0], self.plotter.ax.get_children())

    def test_annotate_adds_marker_at_correct_position(self):
        self.annotation.parameters["positions"] = [[0.5, 0.5]]
        self.annotation.parameters["marker"] = "o"
        self.plotter.plot()
        annotation_ = self.plotter.annotate(self.annotation)
        self.assertListEqual(
            annotation_.parameters["positions"][0],
            list(annotation_.drawings[0].get_data()),
        )

    def test_annotate_adds_correct_marker(self):
        self.annotation.parameters["positions"] = [[0.5, 0.5]]
        self.annotation.parameters["marker"] = "o"
        self.plotter.plot()
        annotation_ = self.plotter.annotate(self.annotation)
        result = [
            item
            for item in self.plotter.ax.get_children()
            if item is annotation_.drawings[0]
        ][0]
        self.assertEqual(
            annotation_.parameters["marker"][0], result.get_marker()
        )

    def test_annotate_with_marker_keywords(self):
        self.annotation.parameters["positions"] = [[0.5, 0.5]]
        self.annotation.parameters["marker"] = "octagon"
        self.plotter.plot()
        annotation_ = self.plotter.annotate(self.annotation)
        result = [
            item
            for item in self.plotter.ax.get_children()
            if item is annotation_.drawings[0]
        ][0]
        self.assertEqual("8", result.get_marker())

    def test_annotate_with_mathtext(self):
        self.annotation.parameters["positions"] = [[0.5, 0.5]]
        self.annotation.parameters["marker"] = "$\mathcal{A}$"
        self.plotter.plot()
        annotation_ = self.plotter.annotate(self.annotation)
        result = [
            item
            for item in self.plotter.ax.get_children()
            if item is annotation_.drawings[0]
        ][0]
        self.assertEqual(
            annotation_.parameters["marker"], result.get_marker()
        )

    def test_annotate_adds_markers_to_plotter(self):
        self.annotation.parameters["positions"] = [[0.5, 0.5], [0.7, 0.7]]
        self.annotation.parameters["marker"] = "o"
        self.plotter.plot()
        annotation_ = self.plotter.annotate(self.annotation)
        self.assertEqual(
            len(annotation_.parameters["positions"]),
            len(annotation_.drawings),
        )
        for drawing in annotation_.drawings:
            self.assertIn(drawing, self.plotter.ax.get_children())

    def test_annotate_with_multiple_markers_does_not_add_connecting_line(
        self,
    ):
        self.annotation.parameters["positions"] = [[0.5, 0.5], [0.7, 0.7]]
        self.annotation.parameters["marker"] = "o"
        self.plotter.plot()
        annotation_ = self.plotter.annotate(self.annotation)
        for drawing in annotation_.drawings:
            self.assertEqual("None", drawing.get_linestyle())

    def test_annotate_with_xpositions_and_ypositions(self):
        self.annotation.parameters["xpositions"] = [0.3]
        self.annotation.parameters["ypositions"] = [0.7]
        self.annotation.parameters["marker"] = "o"
        self.plotter.plot()
        annotation_ = self.plotter.annotate(self.annotation)
        self.assertIn(annotation_.drawings[0], self.plotter.ax.get_children())

    def test_annotate_with_xpositions_as_ndarray_and_ypositions(self):
        self.annotation.parameters["xpositions"] = np.asarray([0.3, 0.4])
        self.annotation.parameters["ypositions"] = [0.7, 0.7]
        self.annotation.parameters["marker"] = "o"
        self.plotter.plot()
        annotation_ = self.plotter.annotate(self.annotation)
        self.assertIn(annotation_.drawings[0], self.plotter.ax.get_children())

    def test_annotate_with_xpositions_and_ypositions_zero(self):
        self.annotation.parameters["xpositions"] = [0]
        self.annotation.parameters["ypositions"] = [0]
        self.annotation.parameters["marker"] = "o"
        self.plotter.plot()
        annotation_ = self.plotter.annotate(self.annotation)
        self.assertIn(annotation_.drawings[0], self.plotter.ax.get_children())

    def test_annotate_with_xpositions_and_scalar_ypositions(self):
        self.annotation.parameters["xpositions"] = [0.3]
        self.annotation.parameters["ypositions"] = 0.7
        self.annotation.parameters["marker"] = "o"
        self.plotter.plot()
        annotation_ = self.plotter.annotate(self.annotation)
        self.assertIn(annotation_.drawings[0], self.plotter.ax.get_children())

    def test_annotate_with_xpositions_and_scalar_ypositions_zero(self):
        self.annotation.parameters["xpositions"] = [0.3]
        self.annotation.parameters["ypositions"] = 0
        self.annotation.parameters["marker"] = "o"
        self.plotter.plot()
        annotation_ = self.plotter.annotate(self.annotation)
        self.assertIn(annotation_.drawings[0], self.plotter.ax.get_children())

    def test_annotate_with_many_xpositions_and_one_ypositions(self):
        self.annotation.parameters["xpositions"] = [0.3, 0.5, 0.7]
        self.annotation.parameters["ypositions"] = [0.7]
        self.annotation.parameters["marker"] = "o"
        self.plotter.plot()
        annotation_ = self.plotter.annotate(self.annotation)
        self.assertIn(annotation_.drawings[0], self.plotter.ax.get_children())

    def test_to_dict_contains_properties(self):
        dict_ = self.annotation.to_dict()
        self.assertIn("properties", dict_)

    def test_annotate_sets_correct_facecolor_for_each_mark(self):
        color = "#cccccc"
        properties = {"facecolor": color}
        self.annotation.properties.from_dict(properties)
        self.plotter.plot()
        self.annotation.parameters["positions"] = [[0.1, 0.3], [0.5, 0.6]]
        annotation_ = self.plotter.annotate(self.annotation)
        for drawing in annotation_.drawings:
            self.assertEqual(
                color, matplotlib.colors.to_hex(drawing.get_markerfacecolor())
            )

    def test_annotate_with_scalar_yoffset(self):
        self.annotation.parameters["positions"] = [[0.5, 0.5]]
        self.annotation.parameters["yoffset"] = 0.1
        self.annotation.parameters["marker"] = "o"
        self.plotter.plot()
        annotation_ = self.plotter.annotate(self.annotation)
        self.assertEqual(
            annotation_.parameters["positions"][0][1]
            + self.annotation.parameters["yoffset"],
            annotation_.drawings[0].get_data()[1],
        )


class TestFillBetween(unittest.TestCase):
    def setUp(self):
        self.annotation = annotation.FillBetween()
        self.plotter = aspecd.plotting.Plotter()
        self.dataset = aspecd.dataset.CalculatedDataset()
        self.dataset.data.data = np.ones(101)

    def test_instantiate_class(self):
        pass

    def test_annotate_adds_annotation_to_plotter(self):
        self.annotation.parameters["data"] = self.dataset
        self.plotter.plot()
        annotation_ = self.plotter.annotate(self.annotation)
        self.assertIn(annotation_.drawings[0], self.plotter.ax.get_children())
        self.assertIsInstance(
            annotation_.drawings[0], matplotlib.collections.PolyCollection
        )

    def test_annotate_adds_annotations_to_plotter(self):
        self.annotation.parameters["data"] = [self.dataset, self.dataset]
        self.plotter.plot()
        annotation_ = self.plotter.annotate(self.annotation)
        self.assertEqual(
            len(annotation_.parameters["data"]),
            len(annotation_.drawings),
        )
        for drawing in annotation_.drawings:
            self.assertIn(drawing, self.plotter.ax.get_children())

    def test_to_dict_contains_properties(self):
        dict_ = self.annotation.to_dict()
        self.assertIn("properties", dict_)

    def test_annotate_sets_correct_facecolor_for_each_annotation(self):
        color = "#cccccc"
        properties = {"facecolor": color}
        self.annotation.properties.from_dict(properties)
        self.plotter.plot()
        self.annotation.parameters["data"] = [self.dataset, self.dataset]
        annotation_ = self.plotter.annotate(self.annotation)
        for drawing in annotation_.drawings:
            self.assertEqual(
                color, matplotlib.colors.to_hex(drawing.get_facecolor())
            )

    def test_annotate_with_second_as_scalar(self):
        self.annotation.parameters["data"] = self.dataset
        self.annotation.parameters["second"] = 0.1
        self.plotter.plot()
        annotation_ = self.plotter.annotate(self.annotation)
        self.assertAlmostEqual(
            0.1,
            annotation_.drawings[0].get_paths()[0].get_extents().bounds[1],
        )

    def test_annotate_with_second_as_dataset(self):
        self.annotation.parameters["data"] = self.dataset
        second = aspecd.dataset.CalculatedDataset()
        second.data.data = np.ones(101) * 0.1
        self.annotation.parameters["second"] = second
        self.plotter.plot()
        annotation_ = self.plotter.annotate(self.annotation)
        self.assertAlmostEqual(
            0.1,
            annotation_.drawings[0].get_paths()[0].get_extents().bounds[1],
        )

    def test_annotate_with_seconds_as_list_of_datasets(self):
        self.annotation.parameters["data"] = self.dataset
        second = aspecd.dataset.CalculatedDataset()
        second.data.data = np.ones(101) * 0.1
        self.annotation.parameters["second"] = [second, second]
        self.plotter.plot()
        annotation_ = self.plotter.annotate(self.annotation)
        self.assertAlmostEqual(
            0.1,
            annotation_.drawings[0].get_paths()[0].get_extents().bounds[1],
        )

    def test_annotate_with_seconds_as_list_of_scalars(self):
        self.annotation.parameters["data"] = self.dataset
        self.annotation.parameters["second"] = [0.2, 0.5]
        self.plotter.plot()
        annotation_ = self.plotter.annotate(self.annotation)
        self.assertAlmostEqual(
            0.2,
            annotation_.drawings[0].get_paths()[0].get_extents().bounds[1],
        )

    def test_annotate_with_seconds_as_mixed_list(self):
        self.annotation.parameters["data"] = [self.dataset, self.dataset]
        second = aspecd.dataset.CalculatedDataset()
        second.data.data = np.ones(101) * 0.1
        self.annotation.parameters["second"] = [0.2, second]
        self.plotter.plot()
        annotation_ = self.plotter.annotate(self.annotation)
        self.assertAlmostEqual(
            0.2,
            annotation_.drawings[0].get_paths()[0].get_extents().bounds[1],
        )
        self.assertAlmostEqual(
            0.1,
            annotation_.drawings[1].get_paths()[0].get_extents().bounds[1],
        )
