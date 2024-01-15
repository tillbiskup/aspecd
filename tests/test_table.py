import os
import textwrap
import unittest

import numpy as np

from aspecd import table, dataset, exceptions


class TestTable(unittest.TestCase):
    def setUp(self):
        self.table = table.Table()
        self.dataset = dataset.CalculatedDataset()
        self.dataset.data.data = np.random.random(5)
        self.filename = "foo"

    def tearDown(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def test_instantiate_class(self):
        pass

    def test_has_to_dict_method(self):
        self.assertTrue(hasattr(self.table, "to_dict"))
        self.assertTrue(callable(self.table.to_dict))

    def test_to_dict_does_not_contain_certain_keys(self):
        for key in ["name", "dataset", "table"]:
            with self.subTest(key=key):
                self.assertNotIn(key, self.table.to_dict())

    def test_has_tabulate_method(self):
        self.assertTrue(hasattr(self.table, "tabulate"))
        self.assertTrue(callable(self.table.tabulate))

    def test_tabulate_without_dataset_raises(self):
        self.table.dataset = None
        with self.assertRaises(exceptions.MissingDatasetError):
            self.table.tabulate()

    def test_tabulate_with_dataset_with_empty_data_warns(self):
        self.table.dataset = dataset.Dataset()
        with self.assertLogs(__package__, level="WARNING") as cm:
            self.table.tabulate()
        self.assertIn(
            "Dataset contains no data, hence nothing to tabulate.",
            cm.output[0],
        )

    def test_tabulate_with_dataset_parameter_sets_dataset(self):
        self.table.dataset = None
        self.table.tabulate(self.dataset)
        self.assertEqual(self.dataset, self.table.dataset)

    def test_tabulate_with_dataset_adds_representation_to_dataset(self):
        self.table.dataset = None
        self.table.tabulate(self.dataset)
        self.assertTrue(self.dataset.representations)

    def test_tabulate_with_3D_dataset_raises(self):
        self.dataset.data.data = np.random.random([5, 5, 5])
        self.table.dataset = self.dataset
        with self.assertRaisesRegex(
            exceptions.NotApplicableToDatasetError,
            "Tables work only with 1D and 2D data",
        ):
            self.table.tabulate()

    def test_tabulate_sets_table(self):
        self.table.dataset = self.dataset
        self.table.tabulate()
        self.assertTrue(self.table.table)

    def test_table_and_dataset_rows_are_consistent(self):
        self.table.dataset = self.dataset
        self.table.tabulate()
        self.assertEqual(
            self.dataset.data.data.shape[0], len(self.table.table.split("\n"))
        )

    def test_multiple_tabulate_calls_reset_table(self):
        self.table.dataset = self.dataset
        self.table.tabulate()
        self.table.tabulate()
        self.assertEqual(
            self.dataset.data.data.shape[0], len(self.table.table.split("\n"))
        )

    def test_rows_have_equal_width(self):
        self.dataset.data.data = np.asarray([1.0, 3.14, 4.1234])
        self.table.dataset = self.dataset
        self.table.tabulate()
        rows = self.table.table.split("\n")
        width = max([len(x) for x in rows])
        for row in rows:
            self.assertEqual(width, len(row))

    def test_tabulate_with_multiple_rows(self):
        self.dataset.data.data = np.ones(3) * np.pi
        self.table.dataset = self.dataset
        self.table.tabulate()
        column = "{}\n{}\n{}".format(*self.dataset.data.data)
        self.assertEqual(column, self.table.table)

    def test_tabulate_with_multiple_columns(self):
        self.dataset.data.data = np.random.random([1, 3])
        self.table.dataset = self.dataset
        self.table.tabulate()
        row = "{} {} {}".format(*self.dataset.data.data[0, :])
        self.assertEqual(row, self.table.table)

    def test_tabulate_with_column_format(self):
        self.dataset.data.data = np.random.random(3)
        self.table.dataset = self.dataset
        format_ = "5.3f"
        self.table.column_format = [format_]
        self.table.tabulate()
        column = "{:{format}}\n{:{format}}\n{:{format}}".format(
            *self.dataset.data.data, format=format_
        )
        self.assertEqual(column, self.table.table)

    def test_tabulate_with_column_format_and_multiple_columns(self):
        self.dataset.data.data = np.random.random([1, 3])
        self.table.dataset = self.dataset
        format_ = ["5.3f", "6.4f", "7.5f"]
        self.table.column_format = format_
        self.table.tabulate()
        column = "{:{format0}} {:{format1}} {:{format2}}".format(
            *self.dataset.data.data[0, :],
            format0=format_[0],
            format1=format_[1],
            format2=format_[2],
        )
        self.assertEqual(column, self.table.table)

    def test_tabulate_with_one_column_format_and_multiple_columns(self):
        self.dataset.data.data = np.random.random([1, 3])
        self.table.dataset = self.dataset
        format_ = "5.3f"
        self.table.column_format = [format_]
        self.table.tabulate()
        column = "{:{format}} {:{format}} {:{format}}".format(
            *self.dataset.data.data[0, :], format=format_
        )
        self.assertEqual(column, self.table.table)

    def test_index_in_first_axis_adds_index_to_rows(self):
        self.dataset.data.data = np.random.random(3)
        index = ["foo", "bar", "foobar"]
        self.dataset.data.axes[0].index = index
        self.table.dataset = self.dataset
        self.table.tabulate()
        rows = self.table.table.split("\n")
        for idx, row in enumerate(rows):
            self.assertTrue(row.startswith(index[idx]))

    def test_index_in_second_axis_adds_column_headers(self):
        self.dataset.data.data = np.random.random([1, 3])
        index = ["foo", "bar", "foobar"]
        self.dataset.data.axes[1].index = index
        self.table.dataset = self.dataset
        self.table.tabulate()
        column_headers = self.table.table.split("\n")[0].split()
        for idx, header in enumerate(column_headers):
            self.assertEqual(index[idx], header)

    def test_long_column_headers_expand_data_column_width(self):
        self.dataset.data.data = np.random.random([1, 3])
        index = ["foo foo foo foo foo", "bar", "foobar"]
        self.table.column_format = ["5.3f"]
        self.dataset.data.axes[1].index = index
        self.table.dataset = self.dataset
        self.table.tabulate()
        data_rows = self.table.table.split("\n")
        self.assertEqual(len(data_rows[0]), len(data_rows[1]))

    def test_column_headers_with_row_index(self):
        self.dataset.data.data = np.ones([3, 3])
        index = ["foo", "bar", "foobar"]
        self.dataset.data.axes[0].index = index
        self.dataset.data.axes[1].index = index
        self.table.dataset = self.dataset
        self.table.tabulate()
        column_headers = self.table.table.split("\n")[0]
        self.assertTrue(column_headers.startswith("   "))

    @unittest.skip
    def test_column_separator_from_format(self):
        self.dataset.data.data = np.random.random([1, 3])
        self.table.dataset = self.dataset
        format_ = table.Format()
        format_.column_separator = " & "
        self.table.format = format_
        self.table.tabulate()
        row = "{}{sep}{}{sep}{}".format(
            *self.dataset.data.data[0, :], sep=format_.column_separator
        )
        self.assertEqual(row, self.table.table)

    @unittest.skip
    def test_column_prefix_from_format(self):
        self.dataset.data.data = np.random.random([1, 3])
        self.table.dataset = self.dataset
        format_ = table.Format()
        format_.column_prefix = "| "
        format_.column_separator = " | "
        self.table.format = format_
        self.table.tabulate()
        row = "{prefix}{}{sep}{}{sep}{}".format(
            *self.dataset.data.data[0, :],
            sep=format_.column_separator,
            prefix=format_.column_prefix,
        )
        self.assertEqual(row, self.table.table)

    @unittest.skip
    def test_column_postfix_from_format(self):
        self.dataset.data.data = np.random.random([1, 3])
        self.table.dataset = self.dataset
        format_ = table.Format()
        format_.column_postfix = "| "
        format_.column_separator = " | "
        self.table.format = format_
        self.table.tabulate()
        row = "{}{sep}{}{sep}{}{postfix}".format(
            *self.dataset.data.data[0, :],
            sep=format_.column_separator,
            postfix=format_.column_postfix,
        )
        self.assertEqual(row, self.table.table)

    @unittest.skip
    def test_header_separator_from_format(self):
        self.dataset.data.data = np.ones([1, 3])
        index = ["foo", "bar", "foobar"]
        self.dataset.data.axes[1].index = index
        self.table.dataset = self.dataset
        format_ = table.Format()
        format_.header_separator = " ^ "
        self.table._format = format_
        self.table.tabulate()
        row = "{}{sep}{}{sep}{}".format(*index, sep=format_.header_separator)
        self.assertEqual(row, self.table.table.split("\n")[0])

    @unittest.skip
    def test_header_prefix_from_format(self):
        self.dataset.data.data = np.ones([1, 3])
        index = ["foo", "bar", "foobar"]
        self.dataset.data.axes[1].index = index
        self.table.dataset = self.dataset
        format_ = table.Format()
        format_.header_prefix = "^ "
        format_.header_separator = " ^ "
        self.table.format = format_
        self.table.tabulate()
        row = "{prefix}{}{sep}{}{sep}{}".format(
            *index, sep=format_.header_separator, prefix=format_.header_prefix
        )
        self.assertEqual(row, self.table.table.split("\n")[0])

    @unittest.skip
    def test_header_postfix_from_format(self):
        self.dataset.data.data = np.ones([1, 3])
        index = ["foo", "bar", "foobar"]
        self.dataset.data.axes[1].index = index
        self.table.dataset = self.dataset
        format_ = table.Format()
        format_.header_postfix = "^ "
        format_.header_separator = " ^ "
        self.table.format = format_
        self.table.tabulate()
        row = "{}{sep}{}{sep}{}{postfix}".format(
            *index,
            sep=format_.header_separator,
            postfix=format_.header_postfix,
        )
        self.assertEqual(row, self.table.table.split("\n")[0])

    def test_top_rule(self):
        self.dataset.data.data = np.ones([1, 3])
        self.table.dataset = self.dataset
        format_ = table.TextFormat()
        self.table.format = "text"
        self.table.tabulate()
        row = format_.top_rule(column_widths=[3, 3, 3])
        self.assertEqual(row, self.table.table.split("\n")[0])

    def test_middle_rule(self):
        self.dataset.data.data = np.ones([3, 3])
        index = ["foo", "bar", "baz"]
        self.dataset.data.axes[1].index = index
        self.table.dataset = self.dataset
        format_ = table.TextFormat()
        self.table.format = "text"
        self.table.tabulate()
        row = format_.middle_rule(column_widths=[3, 3, 3])
        self.assertEqual(row, self.table.table.split("\n")[2])

    def test_bottom_rule(self):
        self.dataset.data.data = np.ones([1, 3])
        self.table.dataset = self.dataset
        format_ = table.TextFormat()
        self.table.format = "text"
        self.table.tabulate()
        row = format_.bottom_rule(column_widths=[3, 3, 3])
        self.assertEqual(row, self.table.table.split("\n")[-1])

    def test_padding(self):
        self.dataset.data.data = np.ones([1, 3])
        self.table.dataset = self.dataset
        format_ = table.TextFormat()
        format_.padding = 1
        self.table.format = "text"
        self.table.tabulate()
        row = "{prefix} {} {sep} {} {sep} {} {postfix}".format(
            *self.dataset.data.data[0, :],
            prefix=format_.column_prefix,
            sep=format_.column_separator,
            postfix=format_.column_postfix,
        )
        self.assertEqual(row, self.table.table.split("\n")[1])

    def test_padding_with_header(self):
        self.dataset.data.data = np.ones([1, 3])
        index = ["foo", "bar", "baz"]
        self.dataset.data.axes[1].index = index
        self.table.dataset = self.dataset
        format_ = table.TextFormat()
        format_.padding = 1
        self.table.format = "text"
        self.table.tabulate()
        row = "{prefix} {} {sep} {} {sep} {} {postfix}".format(
            *index,
            prefix=format_.header_prefix,
            sep=format_.header_separator,
            postfix=format_.header_postfix,
        )
        self.assertEqual(row, self.table.table.split("\n")[1])

    def test_dokuwiki_format(self):
        self.dataset.data.data = np.ones([1, 3])
        self.table.dataset = self.dataset
        format_ = table.DokuwikiFormat()
        self.table.format = "dokuwiki"
        self.table.tabulate()
        row = "{prefix} {} {sep} {} {sep} {} {postfix}".format(
            *self.dataset.data.data[0, :],
            prefix=format_.column_prefix,
            sep=format_.column_separator,
            postfix=format_.column_postfix,
        )
        self.assertEqual(row, self.table.table.split("\n")[0])

    def test_dokuwiki_format_header(self):
        self.dataset.data.data = np.ones([1, 3])
        index = ["foo", "bar", "baz"]
        self.dataset.data.axes[1].index = index
        self.table.dataset = self.dataset
        format_ = table.DokuwikiFormat()
        self.table.format = "dokuwiki"
        self.table.tabulate()
        row = "{prefix} {} {sep} {} {sep} {} {postfix}".format(
            *index,
            prefix=format_.header_prefix,
            sep=format_.header_separator,
            postfix=format_.header_postfix,
        )
        self.assertEqual(row, self.table.table.split("\n")[0])

    def test_dokuwiki_format_row_index(self):
        self.dataset.data.data = np.ones(3)
        index = ["foo", "bar", "baz"]
        self.dataset.data.axes[0].index = index
        self.table.dataset = self.dataset
        format_ = table.DokuwikiFormat()
        self.table.format = "dokuwiki"
        self.table.tabulate()
        row = "{prefix} {} {sep} {} {postfix}".format(
            *[index[0], self.dataset.data.data[0]],
            prefix=format_.header_prefix,
            sep=format_.column_separator,
            postfix=format_.column_postfix,
        )
        self.assertEqual(row, self.table.table.split("\n")[0])

    def test_dokuwiki_format_header_and_row_index(self):
        self.dataset.data.data = np.ones([3, 3])
        index = ["foo", "bar", "baz"]
        self.dataset.data.axes[0].index = index
        self.dataset.data.axes[1].index = index
        self.table.dataset = self.dataset
        format_ = table.DokuwikiFormat()
        self.table.format = "dokuwiki"
        self.table.tabulate()
        row = "{prefix} {} {sep} {} {sep} {} {sep} {} {postfix}".format(
            *["   ", *index],
            prefix=format_.column_prefix,
            sep=format_.header_separator,
            postfix=format_.header_postfix,
        )
        self.assertEqual(row, self.table.table.split("\n")[0])

    def test_latex_format_opening(self):
        self.dataset.data.data = np.ones([1, 3])
        self.table.dataset = self.dataset
        format_ = table.LatexFormat()
        self.table.format = "latex"
        self.table.tabulate()
        row = r"\begin{tabular}{lll}"
        self.assertEqual(row, self.table.table.split("\n")[0])

    def test_latex_format_closing(self):
        self.dataset.data.data = np.ones([1, 3])
        self.table.dataset = self.dataset
        format_ = table.LatexFormat()
        self.table.format = "latex"
        self.table.tabulate()
        row = r"\end{tabular}"
        self.assertEqual(row, self.table.table.split("\n")[-1])

    def test_latex_format_of_numerical_data(self):
        self.dataset.data.data = np.ones([1, 3])
        self.table.dataset = self.dataset
        format_ = table.LatexFormat()
        self.table.format = "latex"
        self.table.tabulate()
        row = r"{}{sep}{}{sep}{} \\".format(
            *self.dataset.data.data[0, :],
            sep=format_.column_separator,
        )
        self.assertEqual(row, self.table.table.split("\n")[2])

    def test_latex_format_with_header(self):
        self.dataset.data.data = np.ones([1, 3])
        index = ["foo", "bar", "baz"]
        self.dataset.data.axes[1].index = index
        self.table.dataset = self.dataset
        format_ = table.LatexFormat()
        self.table.format = "latex"
        self.table.tabulate()
        self.assertEqual(r"\midrule", self.table.table.split("\n")[3])

    def test_with_caption(self):
        caption = table.Caption()
        caption.title = "Lorem ipsum dolor sit amet"
        self.dataset.data.data = np.ones([3, 3])
        index = ["foo", "bar", "baz"]
        self.dataset.data.axes[0].index = index
        self.dataset.data.axes[1].index = index
        self.table.dataset = self.dataset
        self.table.caption = caption
        self.table.tabulate()
        self.assertEqual(caption.title, self.table.table.split("\n")[0])
        self.assertEqual("", self.table.table.split("\n")[1])

    def test_save(self):
        self.table.dataset = self.dataset
        self.table.tabulate()
        self.table.filename = self.filename
        self.table.save()
        self.assertTrue(os.path.exists(self.filename))

    def test_save_writes_content(self):
        self.table.dataset = self.dataset
        self.table.tabulate()
        self.table.filename = self.filename
        self.table.save()
        with open(self.filename, "r") as file:
            file_content = file.read()
        self.assertEqual(self.table.table, file_content)


class TestFormat(unittest.TestCase):
    def setUp(self):
        self.format = table.Format()

    def test_instantiate_class(self):
        pass

    def test_has_properties(self):
        properties = [
            "column_separator",
            "column_prefix",
            "column_postfix",
            "header_separator",
            "header_prefix",
            "header_postfix",
        ]
        for prop in properties:
            with self.subTest(property=prop):
                self.assertTrue(hasattr(self.format, prop))

    def test_has_top_rule_method(self):
        self.assertTrue(hasattr(self.format, "top_rule"))
        self.assertTrue(callable(self.format.top_rule))

    def test_top_rule_returns_string(self):
        self.assertIsInstance(self.format.top_rule(), str)

    def test_top_rule_with_column_widths(self):
        self.format.top_rule(column_widths=[3, 3, 3])

    def test_has_middle_rule_method(self):
        self.assertTrue(hasattr(self.format, "middle_rule"))
        self.assertTrue(callable(self.format.middle_rule))

    def test_midrule_returns_string(self):
        self.assertIsInstance(self.format.middle_rule(), str)

    def test_middle_rule_with_column_widths(self):
        self.format.middle_rule(column_widths=[3, 3, 3])

    def test_has_bottom_rule_method(self):
        self.assertTrue(hasattr(self.format, "bottom_rule"))
        self.assertTrue(callable(self.format.bottom_rule))

    def test_bottom_rule_returns_string(self):
        self.assertIsInstance(self.format.bottom_rule(), str)

    def test_bottom_rule_with_column_widths(self):
        self.format.bottom_rule(column_widths=[3, 3, 3])

    def test_has_opening_method(self):
        self.assertTrue(hasattr(self.format, "opening"))
        self.assertTrue(callable(self.format.opening))

    def test_opening_returns_string(self):
        self.assertIsInstance(self.format.opening(), str)

    def test_opening_with_columns(self):
        self.format.opening(columns=5)

    def test_opening_with_columns_and_caption(self):
        self.format.opening(columns=5, caption=table.Caption())

    def test_opening_with_caption_returns_caption(self):
        caption = table.Caption()
        caption.title = "Lorem ipsum"
        expected_opening = "\n".join(textwrap.wrap(caption.title)) + "\n"
        opening = self.format.opening(caption=caption)
        self.assertEqual(expected_opening, opening)

    def test_opening_with_caption_with_title_and_text(self):
        caption = table.Caption()
        caption.title = "Lorem ipsum"
        caption.text = (
            "dolor sit amet, consectetur adipiscing elit. "
            "Curabitur commodo tempor vulputate. Sed placerat "
            "ultricies ex. Donec iaculis ipsum non felis mattis, "
            "quis mollis urna pharetra"
        )
        expected_opening = (
            "\n".join(textwrap.wrap(" ".join([caption.title, caption.text])))
            + "\n"
        )
        opening = self.format.opening(caption=caption)
        self.assertEqual(expected_opening, opening)

    def test_has_closing_method(self):
        self.assertTrue(hasattr(self.format, "closing"))
        self.assertTrue(callable(self.format.closing))

    def test_closing_with_caption(self):
        self.format.closing(caption=table.Caption())

    def test_begin_environment_returns_string(self):
        self.assertIsInstance(self.format.closing(), str)


class TestTextFormat(unittest.TestCase):
    def setUp(self):
        self.format = table.TextFormat()

    def test_instantiate_class(self):
        pass

    def test_top_rule_returns_rule(self):
        self.format.padding = 0
        rule = "+---+---+---+"
        self.assertEqual(rule, self.format.top_rule([3, 3, 3]))

    def test_middle_rule_returns_rule(self):
        self.format.padding = 0
        rule = "+---+---+---+"
        self.assertEqual(rule, self.format.middle_rule([3, 3, 3]))

    def test_bottom_rule_returns_rule(self):
        self.format.padding = 0
        rule = "+---+---+---+"
        self.assertEqual(rule, self.format.bottom_rule([3, 3, 3]))

    def test_top_rule_with_padding(self):
        self.format.padding = 2
        rule = "+-------+-------+-------+"
        self.assertEqual(rule, self.format.top_rule([3, 3, 3]))

    def test_default_padding_is_one(self):
        rule = "+-----+-----+-----+"
        self.assertEqual(rule, self.format.top_rule([3, 3, 3]))


class TestRstFormat(unittest.TestCase):
    def setUp(self):
        self.format = table.RstFormat()

    def test_instantiate_class(self):
        pass

    def test_top_rule_returns_rule(self):
        rule = "=== === ==="
        self.assertEqual(rule, self.format.top_rule([3, 3, 3]))

    def test_middle_rule_returns_rule(self):
        rule = "=== === ==="
        self.assertEqual(rule, self.format.middle_rule([3, 3, 3]))

    def test_bottom_rule_returns_rule(self):
        rule = "=== === ==="
        self.assertEqual(rule, self.format.bottom_rule([3, 3, 3]))


class TestDokuwikiFormat(unittest.TestCase):
    def setUp(self):
        self.format = table.DokuwikiFormat()

    def test_instantiate_class(self):
        pass

    def test_top_rule_is_empty(self):
        self.assertEqual("", self.format.top_rule())

    def test_middle_rule_is_empty(self):
        self.assertEqual("", self.format.middle_rule())

    def test_bottom_rule_is_empty(self):
        self.assertEqual("", self.format.bottom_rule())

    def test_opening_without_caption_is_empty(self):
        self.assertEqual("", self.format.opening())

    def test_opening_with_caption(self):
        caption = table.Caption()
        caption.title = "Lorem ipsum"
        expected_opening = "\n".join(
            ["<table>", "<caption>*{}*</caption>".format(caption.title)]
        )
        opening = self.format.opening(caption=caption)
        self.assertEqual(expected_opening, opening)

    def test_opening_with_caption_with_title_and_text(self):
        caption = table.Caption()
        caption.title = "Lorem ipsum"
        caption.text = "dolor sit amet"
        expected_opening = "\n".join(
            [
                "<table>",
                "<caption>*{}* {}</caption>".format(
                    caption.title, caption.text
                ),
            ]
        )
        opening = self.format.opening(caption=caption)
        self.assertEqual(expected_opening, opening)

    def test_closing_without_caption_is_empty(self):
        self.assertEqual("", self.format.closing())

    def test_closing_with_caption(self):
        caption = table.Caption()
        caption.title = "Lorem ipsum"
        closing = self.format.closing(caption=caption)
        self.assertEqual("</table>", closing)


class TestLatexFormat(unittest.TestCase):
    def setUp(self):
        self.format = table.LatexFormat()

    def test_instantiate_class(self):
        pass

    def test_top_rule(self):
        self.assertEqual(r"\toprule", self.format.top_rule())

    def test_middle_rule(self):
        self.assertEqual(r"\midrule", self.format.middle_rule())

    def test_bottom_rule(self):
        self.assertEqual(r"\bottomrule", self.format.bottom_rule())

    def test_opening_with_caption_adds_table_environment_and_caption(self):
        caption = table.Caption()
        caption.title = "Lorem ipsum"
        expected_opening = "\n".join(
            [
                r"\begin{table}",
                r"\caption{\textbf{" + caption.title + r"}}",
                r"\begin{tabular}{l}",
            ]
        )
        opening = self.format.opening(columns=1, caption=caption)
        self.assertEqual(expected_opening, opening)

    def test_opening_with_caption_title_and_text(self):
        caption = table.Caption()
        caption.title = "Lorem ipsum"
        caption.text = "dolor sit amet"
        caption_text = (
            r"\caption{\textbf{" + caption.title + r"} " + caption.text + r"}"
        )
        opening = self.format.opening(columns=1, caption=caption)
        self.assertEqual(caption_text, opening.splitlines()[1])

    def test_closing_with_caption_adds_table_environment(self):
        caption = table.Caption()
        caption.title = "Lorem ipsum"
        expected_closing = "\n".join([r"\end{tabular}", r"\end{table}"])
        closing = self.format.closing(caption=caption)
        self.assertEqual(expected_closing, closing)


class TestCaption(unittest.TestCase):
    def setUp(self):
        self.caption = table.Caption()

    def test_instantiate_class(self):
        pass

    def test_has_to_dict_method(self):
        self.assertTrue(hasattr(self.caption, "to_dict"))
        self.assertTrue(callable(self.caption.to_dict))

    def test_has_from_dict_method(self):
        self.assertTrue(hasattr(self.caption, "from_dict"))
        self.assertTrue(callable(self.caption.from_dict))

    def test_has_title_property(self):
        self.assertTrue(hasattr(self.caption, "title"))

    def test_has_text_property(self):
        self.assertTrue(hasattr(self.caption, "text"))
