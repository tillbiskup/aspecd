r"""
Tabular representation of datasets.

.. sidebar:: Contents

    .. contents::
        :local:
        :depth: 1


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
(PrettyTable, Tablib, pandas, to name but a few), all these do much more than
only formatting tables, but are designed to work with tables as well, *i.e.*
modifying and filtering the table contents. This is, however, not needed in
the given context, hence the attempt to create a rather lightweight
implementation.

The implementation focuses on the following aspects:

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
    tab = ds.tabulate(tab)

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
    tab = ds.tabulate(tab)

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
    tab.column_format = ['8.6f']
    tab = ds.tabulate(tab)

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
    tab.column_format = ['8.6f']
    tab = ds.tabulate(tab)

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


Output formats
==============

Tables can be output using different formats, and if you need a special
format, you can of course implement one on your own, by subclassing
:class:`Format`. However, out of the box there are already a number of
formats, from plain (default, shown above) to text to reStructuredText (rst),
DokuWiki, and LaTeX. To give you a quick overview, we will create a dataset
with both, row indices and column headers, and show the different formats.


.. code-block::

    ds = dataset.Dataset()
    ds.data.data = np.random.random([5,3])
    ds.data.axes[0].index = ['a', 'b', 'c', 'd', 'e']
    ds.data.axes[1].index = ['foo', 'bar', 'baz']

    tab = table.Table()
    tab.column_format = ['8.6f']
    tab = ds.tabulate(tab)

    print(tab.table)


The result is the same as already shown above, just a plain table, though
already quite useful:

.. code-block::

      foo      bar      baz
    a 0.689140 0.775321 0.657159
    b 0.315142 0.412736 0.580745
    c 0.116352 0.807541 0.410055
    d 0.226994 0.715985 0.967606
    e 0.532774 0.620670 0.745630


Now, let's see how the text format looks like:

.. code-block::

    # Same as above
    tab.format = 'text'
    tab = ds.tabulate(tab)

    print(tab.table)


And here you go:

.. code-block::

    +---+----------+----------+----------+
    |   | foo      | bar      | baz      |
    +---+----------+----------+----------+
    | a | 0.689140 | 0.775321 | 0.657159 |
    | b | 0.315142 | 0.412736 | 0.580745 |
    | c | 0.116352 | 0.807541 | 0.410055 |
    | d | 0.226994 | 0.715985 | 0.967606 |
    | e | 0.532774 | 0.620670 | 0.745630 |
    +---+----------+----------+----------+


Next is reStructuredText:

.. code-block::

    # Same as above
    tab.format = 'rst'
    tab = ds.tabulate(tab)

    print(tab.table)


As you can see, this format outputs the "simple" rst style, that can be used
as well for an easy-to-read text-only output:

.. code-block::

    = ======== ======== ========
      foo      bar      baz
    = ======== ======== ========
    a 0.689140 0.775321 0.657159
    b 0.315142 0.412736 0.580745
    c 0.116352 0.807541 0.410055
    d 0.226994 0.715985 0.967606
    e 0.532774 0.620670 0.745630
    = ======== ======== ========


Another format that may be useful is DokuWiki, as this kind of lightweight
wiki can be used as an electronic lab notebook (ELN):

.. code-block::

    # Same as above
    tab.format = 'dokuwiki'
    tab = ds.tabulate(tab)

    print(tab.table)


This will even correctly highlight the column headers and row indices as
"headers":

.. code-block::

    |   ^ foo      ^ bar      ^ baz      ^
    ^ a | 0.689140 | 0.775321 | 0.657159 |
    ^ b | 0.315142 | 0.412736 | 0.580745 |
    ^ c | 0.116352 | 0.807541 | 0.410055 |
    ^ d | 0.226994 | 0.715985 | 0.967606 |
    ^ e | 0.532774 | 0.620670 | 0.745630 |


And finally, LaTeX, as this is of great use in the scientific world,
and honestly, manually formatting LaTeX tables can be quite tedious.

.. code-block::

    # Same as above
    tab.format = 'latex'
    tab = ds.tabulate(tab)

    print(tab.table)


As you can see, the details of the formatting are left to you, but at least,
you get valid LaTeX code and a table layout according to typesetting
standards, *i.e.* only horizontal lines. Note that the horizontal lines (
"rules") are typeset using the booktabs package that should always be used:

.. code-block:: latex

    \begin{tabular}{llll}
    \toprule
      & foo      & bar      & baz      \\
    \midrule
    a & 0.689140 & 0.775321 & 0.657159 \\
    b & 0.315142 & 0.412736 & 0.580745 \\
    c & 0.116352 & 0.807541 & 0.410055 \\
    d & 0.226994 & 0.715985 & 0.967606 \\
    e & 0.532774 & 0.620670 & 0.745630 \\
    \bottomrule
    \end{tabular}


Captions
========

Tables can and should have captions that describe the content, as rarely the
numbers (and row indices and column headers) stand on their own. Hence,
you can add a table caption to a table. As writing a caption is necessarily a
manual task, it would only be fair if the table output would include this
caption. For formats such as DokuWiki and LaTeX, it is fairly obvious how to
add the table caption, and for the other formats, the caption is added as
plain text on top of the actual table, wrapped to not have endless lines.


.. code-block::

    ds = dataset.Dataset()
    ds.data.data = np.random.random([5,5])
    ds.data.axes[0].index = ['a', 'b', 'c', 'd', 'e']
    ds.data.axes[1].index = ['foo', 'bar', 'baz', 'foobar', 'frob']

    caption = table.Caption()
    caption.title = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.'
    caption.text = 'Quisque varius tortor ac faucibus posuere. In hac ' \
                   'habitasse platea dictumst. Morbi rutrum felis vitae '\
                   'tristique accumsan. Sed est nisl, auctor a metus a, ' \
                   'elementum cursus velit. Proin et rutrum erat. ' \
                   'Praesent id urna odio. Duis quis augue ac nunc commodo' \
                   ' euismod quis id orci.'

    tab = table.Table()
    tab.caption = caption
    tab.column_format = ['8.6f']
    tab = ds.tabulate(tab)

    print(tab.table)


The result of the print statement above would output something like this:

.. code-block::

    Lorem ipsum dolor sit amet, consectetur adipiscing elit. Quisque
    varius tortor ac faucibus posuere. In hac habitasse platea dictumst.
    Morbi rutrum felis vitae tristique accumsan. Sed est nisl, auctor a
    metus a, elementum cursus velit. Proin et rutrum erat. Praesent id
    urna odio. Duis quis augue ac nunc commodo euismod quis id orci.

      foo      bar      baz      foobar   frob
    a 0.162747 0.620320 0.677983 0.719360 0.426734
    b 0.342259 0.907828 0.252471 0.987115 0.563511
    c 0.253853 0.752020 0.277696 0.479128 0.929410
    d 0.768840 0.220356 0.247271 0.379556 0.231765
    e 0.113655 0.725631 0.098438 0.753049 0.363572


Note that the caption has been wrapped for better readability, and that an
empty line is inserted between caption and table. Of course, you can combine
the caption with the other textual formats ("text", "rst") as well, and it
will be output in the same way. The formats "dokuwiki" and "latex" are
special, see the respective format class definitions (
:class:`DokuwikiFormat`, :class:`LatexFormat`) for details.


Module documentation
====================

"""
import logging
import textwrap

import aspecd.exceptions
from aspecd import history, utils


logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class Table(utils.ToDictMixin):
    """
    Tabular representation of datasets.

    Formatting of a table can be controlled by the formatter class defined by
    :attr:`format`. See the documentation of the :class:`Format` class
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

    filename : :class:`str`
        Name of the file to save the table to.

        If calling :meth:`save`, the table contained in :attr:`table`
        will be saved to this file


    .. versionadded:: 0.5

    """

    def __init__(self):
        super().__init__()
        self.name = aspecd.utils.full_class_name(self)
        self.dataset = None
        self.caption = Caption()
        self.table = None
        self.format = ''
        self.column_format = []
        self.filename = ''
        self._format = Format()
        self._columns = []
        self._rows = []
        self._column_widths = []
        self.__kind__ = 'tabulate'
        self._exclude_from_to_dict = ['name', 'dataset', 'table']

    def tabulate(self, dataset=None, from_dataset=False):
        """
        Create tabular representation of the numerical data of a dataset.

        The result is stored in :attr:`table`.

        In case of an empty dataset, a warning is logged and no further
        action taken.

        Parameters
        ----------
        dataset : class:`aspecd.dataset.Dataset`
            Dataset to create the tabular representation for

        from_dataset : `boolean`
            whether we are called from within a dataset

            Defaults to "False" and shall never be set manually.

        """
        if dataset:
            self.dataset = dataset
        if not self.dataset:
            raise aspecd.exceptions.MissingDatasetError
        if self.dataset.data.data.ndim > 2:
            raise aspecd.exceptions.NotApplicableToDatasetError(
                message='Tables work only with 1D and 2D data')
        if self.dataset.data.data.size == 0:
            logger.warning('Dataset contains no data, hence nothing to '
                           'tabulate.')
            return
        if from_dataset:
            self._set_format()
            self._format_columns()
            self._format_rows()
            self._add_rules()
            self._add_opening_and_closing()
            self.table = '\n'.join(self._rows)
        else:
            self.dataset.tabulate(table=self)

    def save(self):
        """
        Save table to file.

        The filename is set in :attr:`filename`.

        If no table exists, *i.e.* :meth:`tabulate` has not yet been called,
        the method will silently return.
        """
        if not self.table:
            return
        with open(self.filename, 'w') as file:
            file.write(self.table)

    def create_history_record(self):
        """
        Create history record to be added to the dataset.

        Usually, this method gets called from within the
        :meth:`aspecd.dataset.Dataset.tabulate` method of the
        :class:`aspecd.dataset.Dataset` class and ensures the history of
        each tabulating step to get written properly.

        Returns
        -------
        history_record : :class:`aspecd.history.TableHistoryRecord`
            history record for tabulating step

        """
        history_record = \
            history.TableHistoryRecord(package=self.dataset.package_name)
        history_record.table = history.TableRecord(table=self)
        return history_record

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
        opening = self._format.opening(columns=len(self._columns),
                                       caption=self.caption)
        if opening:
            self._rows.insert(0, opening)
        closing = self._format.closing(caption=self.caption)
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
    def opening(self, columns=None, caption=None):
        """
        Create opening code.

        Some formats have opening (and closing, see :meth:`closing`) parts,
        *e.g.* opening and closing tags in XML and related languages, but in
        LaTeX as well.

        Furthermore, table captions are usually set above the table, and if
        your table has a caption with content, this caption will be output
        as well. In its simplest form, as implemented here, caption title
        and caption text will be concatenated and wrapped using
        :func:`textwrap.wrap`, and an empty line added after the caption to
        separate it from the actual table. Thus, your table captions are
        output together with your table in simple text format.

        Override this method according to your needs for your particular
        format.

        Parameters
        ----------
        columns : :class:`int`
            (optional) number of columns of the table

        caption : :class:`Caption`
            (optional) table caption

            For details, see the :class:`Caption` class documentation.

            Only if one of the properties of :class:`Caption` contains
            content, the caption will be considered.

        Returns
        -------
        opening : :class:`str`
            Code for opening the environment

            Default: ''

        """
        opening = ''
        if caption and (caption.title or caption.text):
            opening = self._caption_content(caption)
        return opening

    @staticmethod
    def _caption_content(caption=None):
        caption_text = ' '.join([caption.title, caption.text]).rstrip()
        return '\n'.join(textwrap.wrap(caption_text)) + '\n'

    # noinspection PyMethodMayBeStatic
    def closing(self, caption=None):
        """
        Create closing code.

        Some formats have opening (see :meth:`opening`) and closing parts,
        *e.g.* opening and closing tags in XML and related languages, but in
        LaTeX as well.

        If your format in a class inheriting from :class:`Format` does not need
        this code, don't override this method, as it will by default return
        the empty string, and hence no code gets added to the table.

        Parameters
        ----------
        caption : :class:`Caption`
            (optional) table caption

            For details, see the :class:`Caption` class documentation.

            Only if one of the properties of :class:`Caption` contains
            content, the caption will be considered.

            Having a caption requires some formats to create an additional
            container surrounding the actual table.

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

    def opening(self, columns=None, caption=None):
        """
        Create opening code.

        In case of DokuWiki, this is usually empty, except in cases where
        you have added a caption. In the latter case, code consistent with
        the DokuWiki caption plugin will be output, like so:

        .. code-block:: xml

            <table>
            <caption>*Caption title* Caption text</caption>


        To make this work in your DokuWiki, make sure to have the caption
        plugin installed.


        Parameters
        ----------
        columns : :class:`int`
            Number of columns of the table

        caption : :class:`Caption`
            (optional) table caption

            For details, see the :class:`Caption` class documentation.

            Only if one of the properties of :class:`Caption` contains
            content, the caption will be considered.

            Having a caption requires DokuWiki to create an additional
            table environment surrounding the actual table. As this needs to
            be closed, the closing needs to have the information regarding
            the caption.

        Returns
        -------
        opening : :class:`str`
            Code for opening the environment

        """
        opening = ''
        if caption and (caption.title or caption.text):
            opening = '\n'.join([
                '<table>',
                '<caption>{}</caption>'.format(self._caption_string(caption))
            ])
        return opening

    @staticmethod
    def _caption_string(caption=None):
        caption_string = []
        if caption.title:
            caption_string.append('*{}*'.format(caption.title))
        caption_string.append(caption.text)
        return ' '.join(caption_string).rstrip()

    def closing(self, caption=None):
        """
        Create closing code.

        In case of DokuWiki, this is usually empty, except in cases where
        you have added a caption. In the latter case, code consistent with
        the DokuWiki caption plugin will be output, like so:

        .. code-block:: xml

            </table>


        To make this work in your DokuWiki, make sure to have the caption
        plugin installed.


        Parameters
        ----------
        caption : :class:`Caption`
            (optional) table caption

            For details, see the :class:`Caption` class documentation.

            Only if one of the properties of :class:`Caption` contains
            content, the caption will be considered.

            Having a caption requires DokuWiki to create an additional
            table environment surrounding the actual table. As this needs to
            be closed, the closing needs to have the information regarding
            the caption.

        Returns
        -------
        closing : :class:`str`
            Code for closing the environment

        """
        closing = ''
        if caption and (caption.title or caption.text):
            closing = '</table>'
        return closing


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

    def opening(self, columns=None, caption=None):
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

        caption : :class:`Caption`
            (optional) table caption

            For details, see the :class:`Caption` class documentation.

            Only if one of the properties of :class:`Caption` contains
            content, the caption will be considered.

            Having a caption requires LaTeX to create an additional
            table environment surrounding the actual table. As this needs to
            be closed, the closing needs to have the information regarding
            the caption.

        Returns
        -------
        opening : :class:`str`
            Code for opening the environment

        """
        opening = r'\begin{tabular}{' + columns * 'l' + r'}'
        if caption and (caption.title or caption.text):
            opening = '\n'.join([
                r'\begin{table}',
                r'\caption{' + self._caption_string(caption=caption) + r'}',
                opening])
        return opening

    @staticmethod
    def _caption_string(caption):
        caption_string = []
        if caption.title:
            caption_string.append(r'\textbf{' + caption.title + r'}')
        caption_string.append(caption.text)
        return ' '.join(caption_string).rstrip()

    def closing(self, caption=None):
        r"""
        Create closing code.

        In case of LaTeX, this is usually:

        .. code-block::

            \end{tabular}


        Parameters
        ----------
        caption : :class:`Caption`
            (optional) table caption

            For details, see the :class:`Caption` class documentation.

            Only if one of the properties of :class:`Caption` contains
            content, the caption will be considered.

            Having a caption requires LaTeX to create an additional
            table environment surrounding the actual table. As this needs to
            be closed, the closing needs to have the information regarding
            the caption.

        Returns
        -------
        closing : :class:`str`
            Code for closing the environment

        """
        closing = r'\end{tabular}'
        if caption and (caption.title or caption.text):
            closing = '\n'.join([closing, r'\end{table}'])
        return closing


class Caption(utils.Properties):
    """
    Caption for tables.

    Attributes
    ----------
    title: :class:`str`
        usually one sentence describing the intent of the table

        Often plotted bold-face in a table caption.

    text: :class:`str`
        additional text directly following the title

        Contains more information about the table. Ideally, a table caption
        is self-contained such that it explains the table sufficiently to
        understand its intent and content without needing to read all the
        surrounding text.


    .. versionadded:: 0.5

    """

    def __init__(self):
        super().__init__()
        self.title = ''
        self.text = ''
