"""
Tabular representation of datasets.

While spectroscopic data are usually presented graphically (see
the :mod:`aspecd.plotting` module for details), there are cases where a
tabular representation is useful or even necessary.

One prime example of a situation where you would want to have a tabular
representation of a (calculated) dataset is the result of an
:class:`aspecd.analysis.AggregatedAnalysisStep`. Here, you perform a
:class:`aspecd.analysis.SingleAnalysisStep` on a series of datasets and
collect the results in a :class:`aspecd.dataset.CalculatedDataset`. Of
course, there are situations where you can simply plot this dataset,
but while graphical representations are often helpful for obtaining trends,
if the exact numbers are relevant, a table is often much more useful.


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


There is a list of formatters for different purposes:

* :class:`TextFormat`

  Grid layout for text output

* :class:`RstFormat`

  Simple layout for reStructuredText (rst)

* :class:`DokuwikiFormat`

  DokuWiki table syntax

* :class:`LatexFormat`

  LaTeX table syntax

For simple output, you can use the basic formatter, :class:`Format`,
as well. As this is the default in the :class:`Table` class, nothing needs
to be done in this case.


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

Let's look at a dataset with information on the different columns set in the
second axis. A full example could look like this:

.. code-block::

    ds = dataset.Dataset()
    ds.data.data = np.random.random([5,3])
    ds.data.axes[1].index = ['foo', 'bar', 'baz']

    tab = table.Table()
    tab.dataset = ds
    tab.column_format = ['8.6f']
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
    tab.column_format = ['8.6f']
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
from aspecd import utils


class Table:
    """
    Tabular representation of datasets.

    Formatting of a table can be controlled by the formatter class contained
    in :attr:`format`. See the documentation of the :class:`Format` class
    and its subclasses for details. Furthermore, the individual columns
    containing numerical data can be formatted as well, specifying formats
    for the individual columns in :attr:`column_format`.

    In case the axes of a dataset contain values in their
    :attr:`aspecd.dataset.Axis.index` attribute, these values will be used
    as first column and column headers, respectively.

    In case of indices present in either the first or second axis or both,
    they will be used as row indices and column headers, respectively. One
    particular use case is in combination with the results of an
    :class:`aspecd.analysis.AggregatedAnalysisStep` operating on a series of
    datasets and combining the result in a
    :class:`aspecd.dataset.CalculatedDataset` with the row indices being the
    labels of the corresponding datasets.

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

    format : :class:`str`
        Identifier for output format.

        Valid identifiers are either the empty string or any first part of a
        subclass of :class:`Format`, *i.e.* the part before "Format".

        Examples for currently valid identifiers: ``text``, ``rst``,
        ``dokuwiki``, ``latex``

        See :class:`Format` and the respective subclasses for details on the
        formats available and what kind of output they create.

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
        self.format = ''
        self.column_format = []
        self._format = Format()
        self._columns = []
        self._rows = []
        self._column_widths = []

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
        self._set_format()
        self._format_columns()
        self._format_rows()
        self._add_rules()
        self._add_opening_and_closing()
        self.table = '\n'.join(self._rows)

    def _set_format(self):
        format_class = self.format.lower().capitalize() + 'Format'
        format_class = '.'.join(['aspecd.table', format_class])
        self._format = utils.object_from_class_name(format_class)

    def _format_columns(self):
        self._columns = []
        if any(self.dataset.data.axes[0].index):
            row_indices = []
            if any(self.dataset.data.axes[1].index):
                row_indices.append('')
            row_indices.extend(self.dataset.data.axes[0].index)
            self._columns.append(self._adjust_column_width(row_indices))
        if self.dataset.data.data.ndim == 2:
            for column in range(self.dataset.data.data.shape[1]):
                current_column = []
                if any(self.dataset.data.axes[1].index):
                    current_column.append(
                        self.dataset.data.axes[1].index[column])
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
        self._column_widths = [len(x[0]) for x in self._columns]

    @staticmethod
    def _adjust_column_width(current_column):
        width = max([len(x) for x in current_column])
        return [x.ljust(width) for x in current_column]

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

    def _format_rows(self):
        self._rows = []
        for row in range(len(self._columns[0])):
            current_row = []
            padding = self._format.padding * ' '
            for column in self._columns:
                current_row.append(column[row])
            if any(self.dataset.data.axes[1].index) and row == 0:
                separator = '{padding}{separator}{padding}'.format(
                    padding=padding, separator=self._format.header_separator
                )
                if any(self.dataset.data.axes[0].index):
                    prefix = self._format.column_prefix
                else:
                    prefix = self._format.header_prefix
                formatted_row = \
                    '{prefix}{padding}{row}{padding}{postfix}'.format(
                        prefix=prefix,
                        padding=padding,
                        row=separator.join(current_row),
                        postfix=self._format.header_postfix
                    )
            else:
                separator = '{padding}{separator}{padding}'.format(
                    padding=padding, separator=self._format.column_separator
                )
                if any(self.dataset.data.axes[0].index):
                    prefix = self._format.header_prefix
                else:
                    prefix = self._format.column_prefix
                formatted_row = \
                    '{prefix}{padding}{row}{padding}{postfix}'.format(
                        prefix=prefix,
                        padding=padding,
                        row=separator.join(current_row),
                        postfix=self._format.column_postfix
                    )
            self._rows.append(formatted_row)

    def _add_rules(self):
        top_rule = self._format.top_rule(column_widths=self._column_widths)
        if top_rule:
            self._rows.insert(0, top_rule)
        if any(self.dataset.data.axes[1].index):
            middle_rule = \
                self._format.middle_rule(column_widths=self._column_widths)
            if middle_rule:
                self._rows.insert(2, middle_rule)
        bottom_rule = \
            self._format.bottom_rule(column_widths=self._column_widths)
        if bottom_rule:
            self._rows.append(bottom_rule)

    def _add_opening_and_closing(self):
        opening = self._format.opening(columns=len(self._columns))
        if opening:
            self._rows.insert(0, opening)
        closing = self._format.closing()
        if closing:
            self._rows.append(closing)


class Format:
    """
    Base class for settings for formatting tables.

    The formatter is used by :class:`Table` to control the output.

    Different formats can be implemented by subclassing this class.
    Currently, the following subclasses are available:

    * :class:`TextFormat`

      Grid layout for text output

    * :class:`RstFormat`

      Simple layout for reStructuredText (rst)

    * :class:`DokuwikiFormat`

      DokuWiki table syntax

    * :class:`LatexFormat`

      LaTeX table syntax

    For simple output, you can use the basic formatter, :class:`Format`,
    as well. As this is the default in the :class:`Table` class, nothing needs
    to be done in this case.

    Attributes
    ----------
    padding : :class:`int`
        Number of spaces left and right of a field

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
        self.padding = 0
        self.column_separator = ' '
        self.column_prefix = ''
        self.column_postfix = ''
        self.header_separator = ' '
        self.header_prefix = ''
        self.header_postfix = ''

    # noinspection PyUnusedLocal,PyMethodMayBeStatic
    # pylint: disable=no-self-use,unused-argument
    def top_rule(self, column_widths=None):
        """
        Create top rule for table.

        Tables usually have three types of rules: top rule, middle rule,
        and bottom rule. The middle rule gets used to separate column
        headers from the actual tabular data.

        If your format in a class inheriting from :class:`Format` does not need
        this rule, don't override this method, as it will by default return
        the empty string, and hence no rule gets added to the table.

        Parameters
        ----------
        column_widths : :class:`list`
            (optional) list of column widths

        Returns
        -------
        rule : class:`str`
            Actual rule that gets added to the table output

            Default: ''

        """
        return ''

    # noinspection PyUnusedLocal,PyMethodMayBeStatic
    def middle_rule(self, column_widths=None):
        """
        Create middle rule for table.

        Tables usually have three types of rules: top rule, middle rule,
        and bottom rule. The middle rule gets used to separate column
        headers from the actual tabular data.

        If your format in a class inheriting from :class:`Format` does not need
        this rule, don't override this method, as it will by default return
        the empty string, and hence no rule gets added to the table.

        Parameters
        ----------
        column_widths : :class:`list`
            (optional) list of column widths

        Returns
        -------
        rule : class:`str`
            Actual rule that gets added to the table output

            Default: ''

        """
        return ''

    # noinspection PyUnusedLocal,PyMethodMayBeStatic
    def bottom_rule(self, column_widths=None):
        """
        Create bottom rule for table.

        Tables usually have three types of rules: top rule, middle rule,
        and bottom rule. The middle rule gets used to separate column
        headers from the actual tabular data.

        If your format in a class inheriting from :class:`Format` does not need
        this rule, don't override this method, as it will by default return
        the empty string, and hence no rule gets added to the table.

        Parameters
        ----------
        column_widths : :class:`list`
            (optional) list of column widths

        Returns
        -------
        rule : class:`str`
            Actual rule that gets added to the table output

            Default: ''

        """
        return ''

    # noinspection PyUnusedLocal,PyMethodMayBeStatic
    def opening(self, columns=None):
        """
        Create opening code.

        Some formats have opening (and closing, see :meth:`closing`) parts,
        *e.g.* opening and closing tags in XML and related languages, but in
        LaTeX as well.

        If your format in a class inheriting from :class:`Format` does not need
        this code, don't override this method, as it will by default return
        the empty string, and hence no code gets added to the table.

        Parameters
        ----------
        columns : :class:`int`
            (optional) number of columns of the table

        Returns
        -------
        opening : :class:`str`
            Code for opening the environment

            Default: ''

        """
        return ''

    # noinspection PyMethodMayBeStatic
    def closing(self):
        """
        Create closing code.

        Some formats have opening (see :meth:`opening`) and closing parts,
        *e.g.* opening and closing tags in XML and related languages, but in
        LaTeX as well.

        If your format in a class inheriting from :class:`Format` does not need
        this code, don't override this method, as it will by default return
        the empty string, and hence no code gets added to the table.

        Returns
        -------
        closing : :class:`str`
            Code for closing the environment

            Default: ''

        """
        return ''


class TextFormat(Format):
    """
    Table formatter for textual output.

    With its default settings, the table would be surrounded by a grid, such as:

    .. code-block::

        +-----+-----+-----+
        | foo | bar | baz |
        +-----+-----+-----+
        | 1.0 | 1.1 | 1.2 |
        | 2.0 | 2.1 | 2.2 |
        +-----+-----+-----+


    Attributes
    ----------
    rule_character : :class:`str`
        Character used for drawing horizontal lines (rules)

    rule_edge_character : :class:`str`
        Character used for the edges of horizontal lines (rules)

    rule_separator_character : :class:`str`
        Character used for the column separators of horizontal lines (rules)


    .. versionadded:: 0.5

    """

    def __init__(self):
        super().__init__()
        self.padding = 1
        self.rule_character = '-'
        self.rule_edge_character = '+'
        self.rule_separator_character = '+'
        self.column_separator = '|'
        self.column_prefix = '|'
        self.column_postfix = '|'
        self.header_separator = '|'
        self.header_prefix = '|'
        self.header_postfix = '|'

    def top_rule(self, column_widths=None):
        """
        Create top rule for table.

        Tables usually have three types of rules: top rule, middle rule,
        and bottom rule. The middle rule gets used to separate column
        headers from the actual tabular data.

        The rule gets constructed according to this overall scheme:

        * Use the :attr:`rule_character` for the rule
        * Use the :attr:`rule_separator_character` for the gaps between columns
        * Use the :attr:`rule_edge_character` for beginning and end of the rule
        * Use the :attr:`padding` information to add horizontal space in a cell

        Parameters
        ----------
        column_widths : :class:`list`
            List of column widths

        Returns
        -------
        rule : class:`str`
            Actual rule that gets added to the table output

        """
        segments = []
        for width in column_widths:
            segments.append((width + 2 * self.padding) * self.rule_character)
        rule = self.rule_separator_character.join(segments)
        return '{edge}{rule}{edge}'.format(edge=self.rule_edge_character,
                                           rule=rule)

    def middle_rule(self, column_widths=None):
        """
        Create middle rule for table.

        Here, the middle rule is identical to the :meth:`top_rule`. See
        there for details how the rule is constructed.

        Parameters
        ----------
        column_widths : :class:`list`
            List of column widths

        Returns
        -------
        rule : class:`str`
            Actual rule that gets added to the table output

        """
        return self.top_rule(column_widths=column_widths)

    def bottom_rule(self, column_widths=None):
        """
        Create bottom rule for table.

        Here, the middle rule is identical to the :meth:`top_rule`. See
        there for details how the rule is constructed.

        Parameters
        ----------
        column_widths : :class:`list`
            List of column widths

        Returns
        -------
        rule : class:`str`
            Actual rule that gets added to the table output

        """
        return self.top_rule(column_widths=column_widths)


class RstFormat(TextFormat):
    """
    Table formatter for reStructuredText (rst) output.

    This formatter actually uses the simple format for rst tables, such as:

    .. code-block:: rst

        === === ===
        foo bar baz
        === === ===
        1.0 1.1 1.2
        2.0 2.1 2.2
        === === ===


    The above code would result in:

    === === ===
    foo bar baz
    === === ===
    1.0 1.1 1.2
    2.0 2.1 2.2
    === === ===


    .. versionadded:: 0.5

    """

    def __init__(self):
        super().__init__()
        self.padding = 0
        self.rule_character = '='
        self.rule_edge_character = ''
        self.rule_separator_character = ' '
        self.column_separator = ' '
        self.column_prefix = ''
        self.column_postfix = ''
        self.header_separator = ' '
        self.header_prefix = ''
        self.header_postfix = ''


class DokuwikiFormat(Format):
    """
    Table formatter for DokuWiki output.

    For details about the syntax, see
    the `DokuWiki syntax <https://www.dokuwiki.org/wiki:syntax #tables>`_
    documentation.

    An example of a table in DokuWiki syntax could look like this:

    .. code-block::

        ^ foo ^ bar ^ baz ^
        | 1.0 | 1.1 | 1.2 |
        | 2.0 | 2.1 | 2.2 |

    And in case of both, column headers and row indices, this would even
    convert to:

    .. code-block::

        |     ^ foo ^ bar ^ baz ^
        ^ foo | 1.0 | 1.0 | 1.0 |
        ^ bar | 1.0 | 1.0 | 1.0 |
        ^ baz | 1.0 | 1.0 | 1.0 |


    .. versionadded:: 0.5

    """

    def __init__(self):
        super().__init__()
        self.padding = 1
        self.column_separator = '|'
        self.column_prefix = '|'
        self.column_postfix = '|'
        self.header_separator = '^'
        self.header_prefix = '^'
        self.header_postfix = '^'


class LatexFormat(Format):
    r"""
    Table formatter for LaTeX output.

    Results in a rather generic LaTeX table, and the goal of this formatter
    is to provide valid LaTeX code without trying to go into too many
    details of all the possibilities of LaTeX table formatting.

    .. note::

        The format requires the package "booktabs" to be loaded,
        as the horizontal rules defined by this package are automatically
        added to the LaTeX output.

    An example of the LaTeX code of a table may look as follows:

    .. code-block::

        \begin{tabular}{lll}
        \toprule
        foo & bar & baz \\
        \midrule
        1.0 & 1.1 & 1.2 \\
        2.0 & 2.1 & 2.2 \\
        \bottomrule
        \end{tabular}


    .. versionadded:: 0.5

    """

    def __init__(self):
        super().__init__()
        self.padding = 0
        self.column_separator = ' & '
        self.column_prefix = ''
        self.column_postfix = r' \\'
        self.header_separator = ' & '
        self.header_prefix = ''
        self.header_postfix = r' \\'

    def top_rule(self, column_widths=None):
        """
        Create top rule for table.

        Tables usually have three types of rules: top rule, middle rule,
        and bottom rule. The middle rule gets used to separate column
        headers from the actual tabular data.

        Parameters
        ----------
        column_widths : :class:`list`
            Ignored in this particular case

        Returns
        -------
        rule : class:`str`
            Actual rule that gets added to the table output

        """
        return r'\toprule'

    def middle_rule(self, column_widths=None):
        """
        Create middle rule for table.

        Tables usually have three types of rules: top rule, middle rule,
        and bottom rule. The middle rule gets used to separate column
        headers from the actual tabular data.

        Parameters
        ----------
        column_widths : :class:`list`
            Ignored in this particular case

        Returns
        -------
        rule : class:`str`
            Actual rule that gets added to the table output

        """
        return r'\midrule'

    def bottom_rule(self, column_widths=None):
        """
        Create bottom rule for table.

        Tables usually have three types of rules: top rule, middle rule,
        and bottom rule. The middle rule gets used to separate column
        headers from the actual tabular data.

        Parameters
        ----------
        column_widths : :class:`list`
            Ignored in this particular case

        Returns
        -------
        rule : class:`str`
            Actual rule that gets added to the table output

        """
        return r'\bottomrule'

    def opening(self, columns=None):
        r"""
        Create opening code.

        In case of LaTeX, this is usually:

        .. code-block::

            \begin{tabular}{<column-specification>}

        As this class strives for a rather generic, though valid LaTeX code,
        the column specification is simply 'l' times the number of columns (for
        exclusively left-aligned columns).


        Parameters
        ----------
        columns : :class:`int`
            Number of columns of the table

        Returns
        -------
        opening : :class:`str`
            Code for opening the environment

        """
        return r'\begin{tabular}{' + columns * 'l' + r'}'

    def closing(self):
        r"""
        Create closing code.

        In case of LaTeX, this is usually:

        .. code-block::

            \end{tabular}


        Returns
        -------
        closing : :class:`str`
            Code for closing the environment

        """
        return r'\end{tabular}'
