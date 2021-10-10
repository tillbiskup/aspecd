import unittest

import numpy as np

from aspecd import table, dataset, exceptions


class TestTable(unittest.TestCase):
    def setUp(self):
        self.table = table.Table()
        self.dataset = dataset.CalculatedDataset()
        self.dataset.data.data = np.random.random(5)

    def test_instantiate_class(self):
        pass

    def test_has_tabulate_method(self):
        self.assertTrue(hasattr(self.table, 'tabulate'))
        self.assertTrue(callable(self.table.tabulate))

    def test_tabulate_without_dataset_raises(self):
        self.table.dataset = None
        with self.assertRaises(exceptions.MissingDatasetError):
            self.table.tabulate()

    def test_tabulate_with_3D_dataset_raises(self):
        self.dataset.data.data = np.random.random([5, 5, 5])
        self.table.dataset = self.dataset
        with self.assertRaisesRegex(exceptions.NotApplicableToDatasetError,
                                    'Tables work only with 1D and 2D data'):
            self.table.tabulate()

    def test_tabulate_sets_table(self):
        self.table.dataset = self.dataset
        self.table.tabulate()
        self.assertTrue(self.table.table)

    def test_table_and_dataset_rows_are_consistent(self):
        self.table.dataset = self.dataset
        self.table.tabulate()
        self.assertEqual(self.dataset.data.data.shape[0],
                         len(self.table.table.split('\n')))

    def test_multiple_tabulate_calls_reset_table(self):
        self.table.dataset = self.dataset
        self.table.tabulate()
        self.table.tabulate()
        self.assertEqual(self.dataset.data.data.shape[0],
                         len(self.table.table.split('\n')))

    def test_rows_have_equal_width(self):
        self.dataset.data.data = np.asarray([1., 3.14, 4.1234])
        self.table.dataset = self.dataset
        self.table.tabulate()
        rows = self.table.table.split('\n')
        width = max([len(x) for x in rows])
        for row in rows:
            self.assertEqual(width, len(row))

    def test_tabulate_with_multiple_rows(self):
        self.dataset.data.data = np.ones(3)*np.pi
        self.table.dataset = self.dataset
        self.table.tabulate()
        column = '{}\n{}\n{}'.format(*self.dataset.data.data)
        self.assertEqual(column, self.table.table)

    def test_tabulate_with_multiple_columns(self):
        self.dataset.data.data = np.random.random([1, 3])
        self.table.dataset = self.dataset
        self.table.tabulate()
        row = '{} {} {}'.format(*self.dataset.data.data[0, :])
        self.assertEqual(row, self.table.table)

    def test_tabulate_with_column_format(self):
        self.dataset.data.data = np.random.random(3)
        self.table.dataset = self.dataset
        format_ = '5.3f'
        self.table.column_format = [format_]
        self.table.tabulate()
        column = '{:{format}}\n{:{format}}\n{:{format}}'.format(
            *self.dataset.data.data, format=format_)
        self.assertEqual(column, self.table.table)

    def test_tabulate_with_column_format_and_multiple_columns(self):
        self.dataset.data.data = np.random.random([1, 3])
        self.table.dataset = self.dataset
        format_ = ['5.3f', '6.4f', '7.5f']
        self.table.column_format = format_
        self.table.tabulate()
        column = '{:{format0}} {:{format1}} {:{format2}}'.format(
            *self.dataset.data.data[0, :], format0=format_[0],
            format1=format_[1], format2=format_[2])
        self.assertEqual(column, self.table.table)

    def test_tabulate_with_one_column_format_and_multiple_columns(self):
        self.dataset.data.data = np.random.random([1, 3])
        self.table.dataset = self.dataset
        format_ = '5.3f'
        self.table.column_format = [format_]
        self.table.tabulate()
        column = '{:{format}} {:{format}} {:{format}}'.format(
            *self.dataset.data.data[0, :], format=format_)
        self.assertEqual(column, self.table.table)

    def test_index_in_first_axis_adds_index_to_rows(self):
        self.dataset.data.data = np.random.random(3)
        index = ['foo', 'bar', 'foobar']
        self.dataset.data.axes[0].index = index
        self.table.dataset = self.dataset
        self.table.tabulate()
        rows = self.table.table.split('\n')
        for idx, row in enumerate(rows):
            self.assertTrue(row.startswith(index[idx]))

    def test_index_in_second_axis_adds_column_headers(self):
        self.dataset.data.data = np.random.random([1, 3])
        index = ['foo', 'bar', 'foobar']
        self.dataset.data.axes[1].index = index
        self.table.dataset = self.dataset
        self.table.tabulate()
        column_headers = self.table.table.split('\n')[0].split()
        for idx, header in enumerate(column_headers):
            self.assertEqual(index[idx], header)

    def test_long_column_headers_expand_data_column_width(self):
        self.dataset.data.data = np.random.random([1, 3])
        index = ['foo foo foo foo foo', 'bar', 'foobar']
        self.table.column_format = ['5.3f']
        self.dataset.data.axes[1].index = index
        self.table.dataset = self.dataset
        self.table.tabulate()
        data_rows = self.table.table.split('\n')
        self.assertEqual(len(data_rows[0]), len(data_rows[1]))

    def test_column_headers_with_row_index(self):
        self.dataset.data.data = np.ones([3, 3])
        index = ['foo', 'bar', 'foobar']
        self.dataset.data.axes[0].index = index
        self.dataset.data.axes[1].index = index
        self.table.dataset = self.dataset
        self.table.tabulate()
        column_headers = self.table.table.split('\n')[0]
        self.assertTrue(column_headers.startswith('   '))

    def test_column_separator_from_format(self):
        self.dataset.data.data = np.random.random([1, 3])
        self.table.dataset = self.dataset
        format_ = table.Format()
        format_.column_separator = ' & '
        self.table.format = format_
        self.table.tabulate()
        row = '{}{sep}{}{sep}{}'.format(*self.dataset.data.data[0, :],
                                        sep=format_.column_separator)
        self.assertEqual(row, self.table.table)

    def test_column_prefix_from_format(self):
        self.dataset.data.data = np.random.random([1, 3])
        self.table.dataset = self.dataset
        format_ = table.Format()
        format_.column_prefix = '| '
        format_.column_separator = ' | '
        self.table.format = format_
        self.table.tabulate()
        row = '{prefix}{}{sep}{}{sep}{}'.format(*self.dataset.data.data[0, :],
                                                sep=format_.column_separator,
                                                prefix=format_.column_prefix)
        self.assertEqual(row, self.table.table)

    def test_column_postfix_from_format(self):
        self.dataset.data.data = np.random.random([1, 3])
        self.table.dataset = self.dataset
        format_ = table.Format()
        format_.column_postfix = '| '
        format_.column_separator = ' | '
        self.table.format = format_
        self.table.tabulate()
        row = '{}{sep}{}{sep}{}{postfix}'.format(*self.dataset.data.data[0, :],
                                                 sep=format_.column_separator,
                                                 postfix=format_.column_postfix)
        self.assertEqual(row, self.table.table)

    def test_header_separator_from_format(self):
        self.dataset.data.data = np.ones([1, 3])
        index = ['foo', 'bar', 'foobar']
        self.dataset.data.axes[1].index = index
        self.table.dataset = self.dataset
        format_ = table.Format()
        format_.header_separator = ' ^ '
        self.table.format = format_
        self.table.tabulate()
        row = '{}{sep}{}{sep}{}'.format(*index, sep=format_.header_separator)
        self.assertEqual(row, self.table.table.split('\n')[0])

    def test_header_prefix_from_format(self):
        self.dataset.data.data = np.ones([1, 3])
        index = ['foo', 'bar', 'foobar']
        self.dataset.data.axes[1].index = index
        self.table.dataset = self.dataset
        format_ = table.Format()
        format_.header_prefix = '^ '
        format_.header_separator = ' ^ '
        self.table.format = format_
        self.table.tabulate()
        row = '{prefix}{}{sep}{}{sep}{}'.format(*index,
                                                sep=format_.header_separator,
                                                prefix=format_.header_prefix)
        self.assertEqual(row, self.table.table.split('\n')[0])

    def test_header_postfix_from_format(self):
        self.dataset.data.data = np.ones([1, 3])
        index = ['foo', 'bar', 'foobar']
        self.dataset.data.axes[1].index = index
        self.table.dataset = self.dataset
        format_ = table.Format()
        format_.header_postfix = '^ '
        format_.header_separator = ' ^ '
        self.table.format = format_
        self.table.tabulate()
        row = '{}{sep}{}{sep}{}{postfix}'.format(*index,
                                                 sep=format_.header_separator,
                                                 postfix=format_.header_postfix)
        self.assertEqual(row, self.table.table.split('\n')[0])


class TestFormat(unittest.TestCase):
    def setUp(self):
        self.format = table.Format()

    def test_instantiate_class(self):
        pass

    def test_has_properties(self):
        properties = [
            'column_separator', 'column_prefix', 'column_postfix',
            'header_separator', 'header_prefix', 'header_postfix',
        ]
        for prop in properties:
            with self.subTest(property=prop):
                self.assertTrue(hasattr(self.format, prop))
