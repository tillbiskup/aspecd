"""
Tabular representation of datasets.

While spectroscopic data are usually presented graphically (see
the :mod:`aspecd.plotting` module for details), there are cases where a
tabular representation is useful or even necessary.

.. versionadded:: 0.5


Why this module?
================

While there are several Python packages available capable of formatting tables
(PrettyTable, Tablib, pandas), all these do much more than only formatting
tables, but are designed to work with tables as well, *i.e.* modifying and
filtering the table contents. This is, however, not needed in the given
context, hence the attempt to create a rather lightweight implementation.

The implementation focusses on the following aspects:

  * Tabulation of 1D and 2D datasets
  * Primarily textual output
  * Control over formatting (necessary for different output formats)
  * Control over formatting of numbers
  * Automatic column headers and row indices if present in the dataset axes.


Currently, the module consists of two types of classes:

* :class:`Table`

  The actual class for tabulating data of a dataset

* :class:`Format`

  A general class controlling the format of the tables created by :class:`Table`


Basic usage
===========

To give you an idea how working with this module may look like, have a look
at the following examples:

.. code-block::

    import numpy as np
    from aspecd import dataset, table

    ds = dataset.Dataset()
    ds.data.data = np.random.random([5,3])

    tab = table.Table()
    tab.dataset = ds
    tab.tabulate()

    print(tab.table)


The last line will produce an output similar to the following -- of course
the numbers will be different in your case, as we are using random numbers:

.. code-block::

    0.6457921026722823  0.5634217835847304 0.16339715303360636
    0.1946206354990324  0.7901047968358327 0.16098166185006968
    0.9898725675813765  0.8892801098024301 0.9657653854952412
    0.38858973357936466 0.5818405189808569 0.03264142581790075
    0.9391951330574149  0.5412481787012977 0.9171357572017617


Note that even though the number of digits of the individual cells are not
always identical, the columns are nicely aligned.

If we would want to reduce the number of digits shown, we could use the
:attr:`Table.column_format` attribute, like so:

.. code-block::

    tab.column_format = ['8.6f']
    tab.tabulate()

    print(tab.table)


.. note::

    Two things are relevant here: :attr:`Table.column_format` is a *list*,
    and you can provide fewer format strings than columns in your table. In
    this case, the last format will be used for all remaining columns.


The last line will in this case produce an output similar to the following
-- again with different numbers in your case:

.. code-block::

    0.645792 0.563422 0.163397
    0.194621 0.790105 0.160982
    0.989873 0.889280 0.965765
    0.388590 0.581841 0.032641
    0.939195 0.541248 0.917136


So far, you could get pretty much the same using an ASCII exporter for your
dataset. So what is special with :class:`Table`? A few things: You have much
more control on the output, and you can have column headers and row indices
included automatically if these are present in your dataset.

Let's look at a dataset with information on the different column set in the
second axis. A full example could look like this:

.. code-block::

    ds = dataset.Dataset()
    ds.data.data = np.random.random([5,3])
    ds.data.axes[1].index = ['foo', 'bar', 'baz']

    tab = table.Table()
    tab.dataset = ds
    tab.tabulate()

    print(tab.table)


And the result of the print statement would show you the column headers added:


.. code-block::

    foo      bar      baz
    0.645792 0.563422 0.163397
    0.194621 0.790105 0.160982
    0.989873 0.889280 0.965765
    0.388590 0.581841 0.032641
    0.939195 0.541248 0.917136


Of course, the same would work if you would have row indices provided,
and it even works if for both axes, indices are provided. To demonstrate the
latter (admittedly again in an artificial example):

.. code-block::

    ds = dataset.Dataset()
    ds.data.data = np.random.random([5,3])
    ds.data.axes[0].index = ['a', 'b', 'c', 'd', 'e']
    ds.data.axes[1].index = ['foo', 'bar', 'baz']

    tab = table.Table()
    tab.dataset = ds
    tab.tabulate()

    print(tab.table)


And the result of the print statement would show you both, the column headers
and the row indices added:


.. code-block::

      foo      bar      baz
    a 0.645792 0.563422 0.163397
    b 0.194621 0.790105 0.160982
    c 0.989873 0.889280 0.965765
    d 0.388590 0.581841 0.032641
    e 0.939195 0.541248 0.917136




Module documentation
====================

"""
import aspecd.exceptions


class Table:
    """
    Tabular representation of datasets.

    Formatting of a table can be controlled by the formatter class contained
    in :attr:`format`. See the documentation of the :class:`Format` class for
    details. Furthermore, the individual columns containing numerical data
    can be formatted as well, specifying formats for the individual columns in
    :attr:`column_format`.

    In case the axes of a dataset contain values in their
    :attr:`aspecd.dataset.Axis.index` attribute, these values will be used
    as first column and column headers, respectively.

    .. note::

        For obvious reasons, only 1D and 2D datasets can be tabulated.
        Therefore, if you try to tabulate a ND dataset with N>2, this will
        raise an exception.


    Attributes
    ----------
    dataset : :class:`aspecd.dataset.Dataset`
        Dataset containing numerical data to tabulate

    table : :class:`str`
        Final table ready to be output

    format : :class:`Format`
        Settings for output format.

        See :class:`Format` for details

    column_format: :class:`list`
        (Optional) formats for the data

        The format strings are used by :meth:`str.format`, see there for
        details.

        If the list is shorter than the number of columns, the last element
        will be used for the remaining columns.


    .. versionadded:: 0.5

    """

    def __init__(self):
        self.dataset = None
        self.table = None
        self.format = Format()
        self.column_format = []
        self._columns = []
        self._rows = []

    def tabulate(self):
        """
        Create tabular representation of the numerical data of a dataset.

        The result is stored in :attr:`table`.
        """
        if not self.dataset:
            raise aspecd.exceptions.MissingDatasetError
        if self.dataset.data.data.ndim > 2:
            raise aspecd.exceptions.NotApplicableToDatasetError(
                message='Tables work only with 1D and 2D data')
        self._columns = []
        self._rows = []
        self._format_columns()
        self._format_rows()
        self.table = '\n'.join(self._rows)

    def _format_columns(self):
        if any(self.dataset.data.axes[0].index):
            self._columns.append(self._adjust_column_width(
                self.dataset.data.axes[0].index))
        if self.dataset.data.data.ndim == 2:
            for column in range(self.dataset.data.data.shape[1]):
                current_column = []
                for row in self.dataset.data.data[:, column]:
                    current_column.append(self._format_number(row,
                                                              column=column))
                current_column = self._adjust_column_width(current_column)
                self._columns.append(current_column)
        else:
            current_column = []
            for row in self.dataset.data.data:
                current_column.append(self._format_number(row))
            current_column = self._adjust_column_width(current_column)
            self._columns.append(current_column)

    @staticmethod
    def _adjust_column_width(current_column):
        width = max([len(x) for x in current_column])
        return [x.ljust(width) for x in current_column]

    def _format_rows(self):
        self._add_column_headers()
        for row in range(self.dataset.data.data.shape[0]):
            current_row = []
            for column in self._columns:
                current_row.append(column[row])
            formatted_row = '{prefix}{row}{postfix}'.format(
                prefix=self.format.column_prefix,
                row=self.format.column_separator.join(current_row),
                postfix=self.format.column_postfix
            )
            self._rows.append(formatted_row)

    def _add_column_headers(self):
        if any(self.dataset.data.axes[1].index):
            current_row = []
            if any(self.dataset.data.axes[0].index):
                current_row.append(''.ljust(len(self._columns[0][0])))
                for num, column in enumerate(self._columns[1:]):
                    header = self.dataset.data.axes[1].index[num]
                    width = max([len(column[0]), len(header)])
                    current_row.append(header.ljust(width))
                    self._columns[num + 1] = [x.ljust(width) for x in column]
            else:
                for num, column in enumerate(self._columns):
                    header = self.dataset.data.axes[1].index[num]
                    width = max([len(column[0]), len(header)])
                    current_row.append(header.ljust(width))
                    self._columns[num] = [x.ljust(width) for x in column]
            formatted_row = '{prefix}{row}{postfix}'.format(
                prefix=self.format.header_prefix,
                row=self.format.header_separator.join(current_row),
                postfix=self.format.header_postfix
            )
            self._rows.append(formatted_row)

    def _format_number(self, number, column=0):
        if self.column_format:
            try:
                string_format = self.column_format[column]
            except IndexError:
                string_format = self.column_format[-1]
            formatted_number = \
                '{:{format}}'.format(number, format=string_format)
        else:
            formatted_number = '{}'.format(number)
        return formatted_number


class Format:
    """
    Base class for settings for formatting tables.

    The formatter is used by :class:`Table` to control the output.

    Different formats can be implemented by subclassing this class.

    Attributes
    ----------
    column_separator : :class:`str`
        String used to separate columns in a row

    column_prefix : :class:`str`
        String used to prefix the first column in a row

    column_postfix : :class:`str`
        String used to postfix the last column in a row

    header_separator : :class:`str`
        String used to separate columns in the header (if present)

    header_prefix : :class:`str`
        String used to prefix the first column in the header (if present)

    header_postfix : :class:`str`
        String used to postfix the last column in the header (if present)


    .. versionadded:: 0.5

    """

    def __init__(self):
        self.column_separator = ' '
        self.column_prefix = ''
        self.column_postfix = ''
        self.header_separator = ' '
        self.header_prefix = ''
        self.header_postfix = ''
