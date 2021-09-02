"""
Plotting: Graphical representations of data extracted from datasets.

Plotting relies on `matplotlib <https://matplotlib.org/>`_, and mainly its
object-oriented interface should be used for the actual plotting. Each
plotter contains references to the respective figure and axes created usually
by a call similar to::

    fig, ax = matplotlib.pyplot.subplots()

For convenience, short hands for the :attr:`figure` and :attr:`axes`
properties of a plotter are available, named :attr:`fig` and :attr:`ax`,
respectively. For details on handling (own) figure and axes objects, see below.

Generally, two types of plotters can be distinguished:

* Plotters for handling single datasets

  Shall be derived from :class:`aspecd.plotting.SinglePlotter`.

* Plotters for handling multiple datasets

  Shall be derived from :class:`aspecd.plotting.MultiPlotter`.

In the first case, the plot is usually handled using the :meth:`plot` method
of the respective :obj:`aspecd.dataset.Dataset` object. Additionally,
those plotters always only operate on the data of a single dataset, and the
plot can easily be attached as a representation to the respective dataset.
Plotters handling single datasets should always inherit from the
:class:`aspecd.plotting.SinglePlotter` class.

In the second case, the plot is handled using the :meth:`plot` method of the
:obj:`aspecd.plotting.Plotter` object, and the datasets are stored as a list
within the plotter. As these plots span several datasets, there is no easy
connection between a single dataset and such a plot in sense of
representations stored in datasets. Plotters handling multiple datasets should
always inherit from the :class:`aspecd.plotting.MultiPlotter` class.

In a certain sense, there is a third type of plotters:

* Plotters consisting of more than one axes

  Shall be derived from :class:`aspecd.plotting.CompositePlotter`.

However, practically mostly these composite plotters will behave like
plotters handling either single or multiple datasets. Generally,
these composite plotters will use other types of plotters to perform the
actual plot tasks. This modular approach allows for great flexibility.

Regardless of the type of plotter, **saving plots** is always done using
objects of the :class:`aspecd.plotting.Saver` class. The actual task of
saving a plot is as easy as calling the :meth:`save` method of a plotter
with a saver object as its argument.


A note on array dimensions and axes
===================================

Something often quite confusing is the apparent inconsistency between the
order of array dimensions and the order of axes. While we are used to assign
axes in the order *x*, *y*, *z*, and assuming *x* to be horizontal,
*y* vertical (and *z* sticking out of the paper plane), arrays are usually
indexed row-first, column-second. That means, however, that if you simply
plot a 2D array in axes, your *first* dimension is along the *y* axis,
the *second* dimension along the *x* axis.

Therefore, as the axes of your datasets will always correspond to the array
dimensions of your data, in case of 2D plots you will need to *either* use
the information contained in the second axis object for your *x* axis label,
and the information from the first axis object for your *y* axis label,
*or* to transpose the data array.

Another aspect to have in mind is the position of the origin. Usually,
in a Cartesian coordinate system, convention is to have the origin (0,
0) in the *lower left* of the axes (for the positive quadrant). However,
for images, convention is to have the corresponding (0, 0) pixel located in
the *upper left* edge of your image. Therefore, those plotting methods
dealing with images will usually *revert* the direction of your *y* axis.
Most probably, eventually you will have to check with real data and ensure
the plotters to plot data and axes in a consistent fashion.


Types of concrete plotters
==========================

The ASpecD framework comes with a series of concrete plotters included ready
to be used. As stated above, plotters can generally be divided into two
types: plotters operating on single datasets and plotters combining the data
of multiple datasets into a single figure.

Additionally, plotters can be categorised with regard to creating figures
consisting of a single or multiple axes. The latter are plotters inheriting
from the :class:`aspecd.plotting.CompositePlotter` class. The latter can be
thought of as templates for the other plotters to operate on, *i.e.* they
provide the axes for other plotters to display their results.


Concrete plotters for single datasets
-------------------------------------

* :class:`aspecd.plotting.SinglePlotter1D`

  Basic line plots for single datasets, allowing to plot a series of
  line-type plots, including (semi)log plots

* :class:`aspecd.plotting.SinglePlotter2D`

  Basic 2D plots for single datasets, allowing to plot a series of 2D plots,
  including contour plots and image-type display

* :class:`aspecd.plotting.SinglePlotter2DStacked`

  Stacked plots of 2D data, converting a 2D display into a series of 1D line
  plots stacked on top of each other.

* :class:`aspecd.plotting.SingleCompositePlotter`

  Composite plotter for single datasets, allowing to plot different views of
  one and the same datasets by using existing plotters for single datasets.


Concrete plotters for multiple datasets
---------------------------------------

* :class:`aspecd.plotting.MultiPlotter1D`

  Basic line plots for multiple datasets, allowing to plot a series of
  line-type plots, including (semi)log plots

* :class:`aspecd.plotting.MultiPlotter1DStacked`

  Stacked line plots for multiple datasets, allowing to plot a series of
  line-type plots, including (semi)log plots


Plotting to existing axes
=========================

Figure and axes properties of a plotter object will only be populated upon
calling the method :meth:`aspecd.plotting.Plotter.plot`, therefore by using
the :meth:`plot` method of the respective plotter class.

Furthermore, figure and axes properties will only be populated if both are not
existing already. Therefore, if you like to use a plotter to plot to an
existing axis, set its figure and axes properties before calling  the
:meth:`aspecd.plotting.Plotter.plot` method.

.. important::
    If you do so, make sure to set *both*, figure and axes properties,
    as failing to set a valid figure property will cause matplotlib to throw
    exceptions.


A simple example may look like this::

    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    plotter = aspecd.plotting.SinglePlotter1D()
    plotter.figure = fig
    plotter.axes = ax
    plotter.plot()

In this case, the plotter will plot to the axis specified before calling its
:meth:`plot` method. Thus, it should be straight-forward to write plotter
classes that create complex plots consisting of several subplots by reusing
available plotter classes. This is what the
:class:`aspecd.plotting.CompositePlotter` class is for, and how it basically
works.


Module API documentation
========================

"""

import copy
import os

import matplotlib as mpl
# pylint: disable=unused-import
import matplotlib.collections
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

import aspecd.dataset
import aspecd.exceptions
import aspecd.history
import aspecd.utils


class Plotter:
    """Base class for plots.

    Each class actually plotting data should inherit from this class.
    Furthermore, all parameters, implicit and explicit, necessary to
    perform the plot, should eventually be stored in the property
    :attr:`parameters` (currently a dictionary).

    Further things that need to be changed upon inheriting from this class
    are the string stored in :attr:`description`, being basically a one-liner.

    The actual implementation of the plotting is done in the private method
    :meth:`_create_plot` that in turn gets called by :meth:`plot`.

    .. note::
        Usually, you will never implement an instance of this class for
        actual plotting tasks, but rather one of the child classes.


    Attributes
    ----------
    name : :class:`str`
        Name of the plotter.

        Defaults always to the full class name, don't change!

    parameters : :class:`dict`
        All parameters necessary for the plot, implicit and explicit

        The following keys exist:

        show_legend : :class:`bool`
            Whether to show a legend in the plot

            Default: False

        show_zero_lines : :class:`bool`
            Whether to show zero lines in the plot

            Regardless of whether you set this to true, zero lines will only be
            added to the final plot if the zero value is within the current
            axes limits.

            Zero line properties can be set via the
            :attr:`aspecd.plotting.Plotter.properties` attribute.

            Default: True

    properties : :class:`aspecd.plotting.PlotProperties`
        Properties of the plot, defining its appearance

    description : :class:`str`
        Short description, to be set in class definition

    figure : :class:`matplotlib.figure.Figure`
        Reference to figure object

    axes : :class:`matplotlib.axes.Axes`
        Reference to axes object used for actual plotting

    filename : :class:`str`
        Name of file to save the plot to

        Actual saving is done using an :obj:`aspecd.plotting.Saver` object.

    caption : :class:`aspecd.plotting.Caption`
        User-supplied information for the figure.

    legend : :class:`matplotlib.legend.Legend`
        Legend object

    style : :class:`str`
        plotting style to use

        You can use all plotting styles understood by matplotlib. See
        :mod:`matplotlib.style` for details.


    .. note::
        If you set the style via :attr:`aspecd.plotting.Plotter.style`,
        all following figures will use this style, until you set another style.

        As it seems, there is no way in matplotlib to find out the current
        style, and hence reset to it. One way to fix this problem would be
        to revert to the default style by issuing the following command::

            matplotlib.pyplot.style.use('default')


    Raises
    ------
    aspecd.exceptions.MissingSaverError
        Raised when no saver is provided when trying to save

    """

    def __init__(self):
        # Name defaults always to the full class name, don't change!
        self.name = aspecd.utils.full_class_name(self)
        self.parameters = {
            'show_legend': False,
            'show_zero_lines': True
        }
        self.properties = PlotProperties()
        self.description = 'Abstract plotting step'
        self.figure = None
        self.axes = None
        self.filename = ''
        self.caption = Caption()
        self.legend = None
        self.style = ''

    @property
    def fig(self):
        """Short hand for :attr:`figure`."""
        return self.figure

    @property
    def ax(self):  # pylint: disable=invalid-name
        """Short hand for :attr:`axes`."""
        return self.axes

    def plot(self):
        """Perform the actual plotting.

        The actual plotting should be implemented within the private
        method :meth:`_create_plot`.

        """
        self._set_style()
        self._create_figure_and_axes()
        self._create_plot()
        self.properties.apply(plotter=self)
        self._set_legend()
        self._add_zero_lines()

    # noinspection PyUnusedLocal
    @staticmethod
    def applicable(dataset):  # pylint: disable=unused-argument
        """Check whether plot is applicable to the given dataset.

        Returns `True` by default and needs to be implemented in classes
        inheriting from Plotter according to their needs.

        A typical example would be a 2D plot applied to a 1D dataset that will
        most probably not be possible/sensible.

        Returns
        -------
        applicable : :class:`bool`
            `True` if successful, `False` otherwise.

        """
        return True

    def _set_style(self):
        if self.style:
            if self.style not in plt.style.available + ['default', 'xkcd']:
                message = 'Cannot find matplotlib style "{style}".'.format(
                    style=self.style)
                raise aspecd.exceptions.StyleNotFoundError(message=message)
            if self.style == 'xkcd':
                plt.xkcd()
            else:
                plt.style.use(self.style)

    def _create_figure_and_axes(self):
        """Create figure and axes and assign to attributes.

        Figure and axes will only be created upon calling the method
        :meth:`plot`. If you need to change the way figure and axes are
        created, override this method.

        .. note::
            Figure and axes will only be created if both are not existing
            already. Therefore, if you like to use a plotter to plot to an
            existing axis, set its figure and axes properties before calling
            the :meth:`plot` method.

            If you do so, make sure to set *both*, figure and axes
            properties, as failing to set a valid figure property will cause
            matplotlib to throw exceptions.


        In any case, figure and axes need to be assigned to the
        :attr:`figure` and :attr:`axes` properties of the plotter class.
        """
        if not self.figure and not self.axes:
            mpl.interactive(False)  # Mac OS X: prevent plot window from opening
            self.figure, self.axes = plt.subplots()

    def _create_plot(self):
        """Perform the actual plotting of the data of the dataset(s).

        The implementation of the actual plotting goes in here in all
        classes inheriting from Plotter. This method is automatically
        called by :meth:`plot` after some background checks.

        The reference to the figure object is stored in :attr:`figure`. By
        default, the backend is set to non-interactive, and to actually
        display the figure, you would need to call :meth:`show` on the
        figure object stored in :attr:`figure`.

        Plotting should be done using a method of the
        :class:`matplotlib.axes.Axes` class accessible via the :attr:`axes`
        attribute of the plotter.

        """

    def save(self, saver=None):
        """Save the plot to a file.

        The actual saving is postponed to an object of class
        :class:`aspecd.plotting.Saver` that is submitted as parameter.

        Parameters
        ----------
        saver : `aspecd.plotting.Saver`
            Saver handling the actual saving of the plot

        Returns
        -------
        saver : `aspecd.plotting.Saver`
            Saver used to save the plot

        Raises
        ------
        aspecd.exceptions.MissingSaverError
            Raised if no Saver is provided as parameter.

        """
        if not saver:
            raise aspecd.exceptions.MissingSaverError
        saver.save(self)
        self.filename = saver.filename
        return saver

    @staticmethod
    def _create_axis_label_string(axis):
        """Create axis label conforming to conventions used in science

        Here, the quantity is set in italics, and the unit in upright font,
        with a slash separating both, quantity and unit. In case the
        quantity contains spaces, these will be escaped thus that they are
        contained in the final string (using the math mode of matplotlib).

        .. note::
            It might be worth discussing whether a proper axis label
            conforming to scientific conventions sets the symbol in italics,
            but not the quantity (name) as such. Therefore, a full label might
            look like this: "magnetic field, B_0 / mT" with the term
            "magnetic field" set in upright font, and only the symbol,
            here $B_0$, in italics. For this, a property for the symbol has
            been added to the axis class.


        This method is called automatically and indirectly by :meth:`plot`.

        If you ever need to change the appearance of your axes labels,
        override this method in a child class.

        Returns
        -------
        label: :class:`str`
            label for the axis

        """
        label = ''
        if axis.quantity:
            label = '$' + axis.quantity.replace(' ', '\\ ') + '$'
            if axis.unit:
                label += ' / ' + axis.unit
        return label

    def _set_legend(self):
        if self.parameters['show_legend']:
            self.legend = self.axes.legend(**self.properties.legend.to_dict())

    def _add_zero_lines(self):
        if self.parameters['show_zero_lines']:
            if isinstance(self.axes, list):
                for axes in self.axes:
                    if axes.get_ylim()[0] <= 0 <= axes.get_ylim()[1]:
                        axes.axhline(**self.properties.zero_lines.to_dict(),
                                     zorder=1)
                    if axes.get_xlim()[0] <= 0 <= axes.get_xlim()[1]:
                        axes.axvline(**self.properties.zero_lines.to_dict(),
                                     zorder=1)
            else:
                if self.axes.get_ylim()[0] <= 0 <= self.axes.get_ylim()[1]:
                    self.axes.axhline(**self.properties.zero_lines.to_dict(),
                                      zorder=1)
                if self.axes.get_xlim()[0] <= 0 <= self.axes.get_xlim()[1]:
                    self.axes.axvline(**self.properties.zero_lines.to_dict(),
                                      zorder=1)


class SinglePlotter(Plotter):
    """Base class for plots of single datasets.

    Each class actually plotting data of a dataset should inherit from this
    class. Furthermore, all parameters, implicit and explicit, necessary to
    perform the plot, should eventually be stored in the property
    :attr:`parameters` (currently a dictionary).

    There are two concrete classes available for conveniently performing
    plots of single datasets:

    * :class:`aspecd.plotting.SinglePlotter1D`

      1D plots, such as line, scatter, log, semilog

    * :class:`aspecd.plotting.SinglePlotter2D`

      2D plots, such as contour, image

    To perform the plot, call the :meth:`plot` method of the dataset the plot
    should be performed for, and provide a reference to the actual plotter
    object to it.

    Further things that need to be changed upon inheriting from this class
    are the string stored in :attr:`description`, being basically a one-liner.

    The actual implementation of the plotting is done in the private method
    :meth:`_create_plot` that in turn gets called by :meth:`plot`
    which is called by the :meth:`aspecd.dataset.Dataset.plot` method of the
    dataset object.

    Attributes
    ----------
    properties : :class:`aspecd.plotting.SinglePlotProperties`
        Properties of the plot, defining its appearance

    dataset : :class:`aspecd.dataset.Dataset`
        Dataset the plotting should be done for

    drawing : :class:`matplotlib.artist.Artist`
        Actual graphical representation of the data


    Raises
    ------
    aspecd.exceptions.MissingDatasetError
        Raised when no dataset exists to act on

    aspecd.exceptions.NotApplicableToDatasetError
        Raised when processing step is not applicable to dataset

    """

    def __init__(self):
        super().__init__()
        self.properties = SinglePlotProperties()
        self.dataset = None
        self.drawing = None
        self.description = 'Abstract plotting step for single dataset'

    # pylint: disable=arguments-differ
    def plot(self, dataset=None, from_dataset=False):
        """Perform the actual plotting on the given dataset.

        If no dataset is set as property in the object, the method will
        raise a respective exception. The Dataset object :meth:`plot` method
        always assigns its dataset as the respective dataset attribute of
        the plotter class.

        The actual plotting should be implemented within the non-public
        method :meth:`_create_plot`. Besides that, the applicability of the
        plotting to the given dataset will be checked automatically. These
        checks should be implemented in the method :meth:`applicable`.

        Note that the axis labels are added automatically. If you ever need
        to change the handling or appearance of your axis labels, you may
        want to override the corresponding methods :meth:`_set_axes_labels`
        and :meth:`_create_axis_label_string`, respectively.

        Parameters
        ----------
        dataset : :class:`aspecd.dataset.Dataset`
            dataset to perform plot for

        from_dataset : `boolean`
            whether we are called from within a dataset

            Defaults to "False" and shall never be set manually.

        Returns
        -------
        dataset : :class:`aspecd.dataset.Dataset`
            dataset plot has been performed for

        Raises
        ------
        aspecd.exceptions.NotApplicableToDatasetError
            Raised when plotting is not applicable to dataset
        aspecd.exceptions.MissingDatasetError
            Raised when no dataset exists to act on

        """
        self._assign_dataset(dataset)
        self._call_from_dataset(from_dataset)
        return self.dataset

    def create_history_record(self):
        """
        Create history record to be added to the dataset.

        Usually, this method gets called from within the
        :meth:`aspecd.dataset.plot` method of the
        :class:`aspecd.dataset.Dataset` class and ensures the history of
        each plotting step to get written properly.

        Returns
        -------
        history_record : :class:`aspecd.history.PlotHistoryRecord`
            history record for plotting step

        """
        history_record = \
            aspecd.history.PlotHistoryRecord(package=self.dataset.package_name)
        history_record.plot = aspecd.history.SinglePlotRecord(plotter=self)
        history_record.plot.preprocessing = copy.deepcopy(
            self.dataset.history)
        return history_record

    def _assign_dataset(self, dataset):
        if not dataset:
            if not self.dataset:
                raise aspecd.exceptions.MissingDatasetError
        else:
            self.dataset = dataset

    def _call_from_dataset(self, from_dataset):
        if not from_dataset:
            self.dataset.plot(self)
        else:
            self._check_applicability()
            super().plot()
            self._set_axes_labels()
            self.properties.apply(plotter=self)

    def _check_applicability(self):
        if not self.applicable(self.dataset):
            message = "%s not applicable to dataset with id %s" \
                      % (self.name, self.dataset.id)
            raise aspecd.exceptions.NotApplicableToDatasetError(message=message)

    def _set_axes_labels(self):
        """Set axes labels from axes in dataset.

        This method is called automatically by :meth:`plot`.

        If you ever need to change the handling of your axes labels,
        override this method in a child class.
        """
        xlabel = self._create_axis_label_string(self.dataset.data.axes[0])
        ylabel = self._create_axis_label_string(self.dataset.data.axes[1])
        self.axes.set_xlabel(xlabel)
        self.axes.set_ylabel(ylabel)


class SinglePlotter1D(SinglePlotter):
    # noinspection PyUnresolvedReferences
    """1D plots of single datasets.

    Convenience class taking care of 1D plots of single datasets. The type
    of plot can be set in its :attr:`aspecd.plotting.SinglePlotter1D.type`
    attribute. Allowed types are stored in the
    :attr:`aspecd.plotting.SinglePlotter1D.allowed_types` attribute.

    Quite a number of properties for figure, axes, and line can be set
    using the :attr:`aspecd.plotting.SinglePlotter1D.properties` attribute.
    For details, see the documentation of its respective class,
    :class:`aspecd.plotting.SinglePlot1DProperties`.

    To perform the plot, call the :meth:`plot` method of the dataset the plot
    should be performed for, and provide a reference to the actual plotter
    object to it.

    Attributes
    ----------
    properties : :class:`aspecd.plotting.SinglePlot1DProperties`
        Properties of the plot, defining its appearance

        For the properties that can be set this way, see the documentation
        of the :class:`aspecd.plotting.SinglePlot1DProperties` class.

    parameters : :class:`dict`
        All parameters necessary for the plot, implicit and explicit

        The following keys exist, in addition to those of the superclass:

        tight: :class:`str`
            Whether to set the axes limits tight to the data

            Possible values: 'x', 'y', 'both'

            Default: ''

    Raises
    ------
    TypeError
        Raised when wrong plot type is set

    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. Of course, all parameters settable
    for the superclasses can be set as well. The examples focus each on a
    single aspect.

    In the simplest case, just invoke the plotter with default values:

    .. code-block:: yaml

       - kind: singleplot
         type: SinglePlotter1D
         properties:
           filename: output.pdf

    """

    def __init__(self):
        super().__init__()
        self.description = '1D plotting step for single dataset'
        self.properties = SinglePlot1DProperties()
        # noinspection PyTypeChecker
        self.parameters['tight'] = ''
        self._type = 'plot'
        self._allowed_types = ['plot', 'scatter', 'step', 'loglog',
                               'semilogx', 'semilogy', 'stemplot']

    @property
    def type(self):
        """
        Get or set the plot type.

        Types need to be methods of the :class:`matplotlib.axes.Axes` class.

        Allowed plot types are stored in the
        :attr:`aspecd.plotting.SinglePlotter1D.allowed_types` attribute.

        Default: 'plot'

        Raises
        ------
        TypeError
            Raised in case of wrong type

        """
        return self._type

    @property
    def allowed_types(self):
        """
        Return the allowed plot types.

        Returns
        -------
        allowed_types: :class:`list`
            List of strings

        """
        return self._allowed_types

    @type.setter
    def type(self, plot_type=None):
        if plot_type not in self.allowed_types:
            raise TypeError
        self._type = plot_type

    def _create_plot(self):
        plot_function = getattr(self.axes, self.type)
        if not self.properties.drawing.label:
            self.properties.drawing.label = self.dataset.label
        self.drawing, = plot_function(self.dataset.data.axes[0].values,
                                      self.dataset.data.data,
                                      label=self.properties.drawing.label)
        if self.parameters['tight']:
            if self.parameters['tight'] in ('x', 'both'):
                self.axes.set_xlim([self.dataset.data.axes[0].values.min(),
                                    self.dataset.data.axes[0].values.max()])
            if self.parameters['tight'] in ('y', 'both'):
                self.axes.set_ylim([self.dataset.data.data.min(),
                                    self.dataset.data.data.max()])

    @staticmethod
    def applicable(dataset):
        """Check whether plot is applicable to the given dataset.

        Checks for the dimension of the data of the dataset, i.e. the
        :attr:`aspecd.dataset.Data.data` attribute. Returns `True` if data
        are one-dimensional, and `False` otherwise.

        Returns
        -------
        applicable : :class:`bool`
            `True` if successful, `False` otherwise.

        """
        return dataset.data.data.ndim == 1


class SinglePlotter2D(SinglePlotter):
    # noinspection PyUnresolvedReferences
    """2D plots of single datasets.

    Convenience class taking care of 2D plots of single datasets. The type
    of plot can be set in its :attr:`aspecd.plotting.SinglePlotter2D.type`
    attribute. Allowed types are stored in the
    :attr:`aspecd.plotting.SinglePlotter2D.allowed_types` attribute.

    Quite a number of properties for figure, axes, and surface can be set
    using the :attr:`aspecd.plotting.SinglePlotter2D.properties` attribute.
    For details, see the documentation of its respective class,
    :class:`aspecd.plotting.SinglePlot2DProperties`.

    To perform the plot, call the :meth:`plot` method of the dataset the
    plot should be performed for, and provide a reference to the actual
    plotter object to it.

    .. important::
        Due to the difference between axes conventions in plots,
        with axes being labelled *x*, *y*, *z* accordingly, and the
        convention of indexing arrays (first index refers to the row,
        converting to the *y* axis, the second index to the column,
        *i.e*. the *x* axis), the *x* axis in the plot will be the second
        axis, the *y* axis the first axis of your dataset. If you need to
        change this, you can set the ``switch_axes`` parameter to True.

        While usually, it is only a matter of convention how to display
        your 2D data, it is often confusing, as we intuitively think in *x*,
        *y*, *z* axes, not in row-column indices.


    Attributes
    ----------
    parameters : :class:`dict`
        All parameters necessary for the plot, implicit and explicit

        The following keys exist, in addition to those of the superclasses:

        switch_axes : :class:`bool`
            Whether to switch *x* and *y* axes

            Normally, the first axis is used as *x* axis, and the second
            as *y* axis. Sometimes, switching this assignment is
            necessary or convenient.

            Default: False

        levels : :class:`int`
            Number of levels of a contour plot

            If None, the number of levels will be determined automatically.

            Default: None

        show_contour_lines : :class:`bool`
            Whether to show contour lines in case of contourf plot

    properties : :class:`aspecd.plotting.SinglePlot2DProperties`
        Properties of the plot, defining its appearance

        For the properties that can be set this way, see the documentation
        of the :class:`aspecd.plotting.SinglePlot2DProperties` class.

    Raises
    ------
    TypeError
        Raised when wrong plot type is set

    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. Of course, all parameters settable
    for the superclasses can be set as well. The examples focus each on a
    single aspect.

    In the simplest case, just invoke the plotter with default values:

    .. code-block:: yaml

       - kind: singleplot
         type: SinglePlotter2D
         properties:
           filename: output.pdf

    To change the axes (flip *x* and *y* axis):

    .. code-block:: yaml

       - kind: singleplot
         type: SinglePlotter2D
         properties:
           filename: output.pdf
           parameters:
             switch_axes: True

    To use another type (here: contour):

    .. code-block:: yaml

       - kind: singleplot
         type: SinglePlotter2D
         properties:
           filename: output.pdf
           type: contour

    To set the number of levels of a contour plot to 10:

    .. code-block:: yaml

       - kind: singleplot
         type: SinglePlotter2D
         properties:
           filename: output.pdf
           type: contour
           parameters:
             levels: 10

    To change the colormap (cmap) used:

    .. code-block:: yaml

       - kind: singleplot
         type: SinglePlotter2D
         properties:
           filename: output.pdf
           properties:
             drawing:
               cmap: RdGy

    To plot both, filled contours and contour lines, setting the appearance
    of the contour lines as well:

    .. code-block:: yaml

       - kind: singleplot
         type: SinglePlotter2D
         properties:
           type: contourf
           filename: output.pdf
           parameters:
             show_contour_lines: True
           properties:
             drawing:
               cmap: RdGy
               linewidths: 0.5
               linestyles: '-'
               colors: k

    In this particular case, the contour lines are thin black solid lines.

    Make sure to check the documentation for further parameters that can be
    set.

    """

    def __init__(self):
        super().__init__()
        self.description = '2D plotting step for single dataset'
        self.parameters['switch_axes'] = False
        # noinspection PyTypeChecker
        self.parameters['levels'] = None
        self.parameters['show_contour_lines'] = False
        self.properties = SinglePlot2DProperties()
        self._type = 'imshow'
        self._allowed_types = ['contour', 'contourf', 'imshow']

    @property
    def type(self):
        """
        Get or set the plot type.

        Types need to be methods of the :class:`matplotlib.axes.Axes` class.

        Allowed plot types are stored in the
        :attr:`aspecd.plotting.SinglePlotter2D.allowed_types` attribute.

        Default: 'imshow'

        Raises
        ------
        TypeError
            Raised in case of wrong type

        """
        return self._type

    @property
    def allowed_types(self):
        """
        Return the allowed plot types.

        Returns
        -------
        allowed_types: :class:`list`
            List of strings

        """
        return self._allowed_types

    @type.setter
    def type(self, plot_type=None):
        if plot_type not in self.allowed_types:
            raise TypeError
        self._type = plot_type

    @staticmethod
    def applicable(dataset):
        """Check whether plot is applicable to the given dataset.

        Checks for the dimension of the data of the dataset, i.e. the
        :attr:`aspecd.dataset.Data.data` attribute. Returns `True` if data
        are two-dimensional, and `False` otherwise.

        Returns
        -------
        applicable : :class:`bool`
            `True` if successful, `False` otherwise.

        """
        return dataset.data.data.ndim == 2

    def _create_plot(self):
        """Create actual plot.

        Due to ``imshow`` and ``contour`` needing slightly different
        handling, the plotting is a bit more complex. Many parameters such
        as extent and levels can *only* be set during  invoking the actual
        plotting class.

        """
        plot_function = getattr(self.axes, self.type)
        data = self._shape_data()
        # matplotlib imshow and contour have incompatible properties
        if self.type == 'imshow':
            self.drawing = plot_function(data, extent=self._get_extent(),
                                         aspect='auto')
            return
        if self.parameters['levels']:
            self.drawing = plot_function(data, extent=self._get_extent(),
                                         levels=self.parameters['levels'])
        else:
            self.drawing = plot_function(data, extent=self._get_extent())
        if self.type == 'contourf' and self.parameters['show_contour_lines']:
            self.axes.contour(self.drawing, colors='k', linewidths=0.5,
                              linestyles='-')

    def _shape_data(self):
        if self.parameters['switch_axes']:
            data = self.dataset.data.data
        else:
            data = self.dataset.data.data.T
        if self.type == 'imshow':
            data = np.flipud(data)
        return data

    def _get_extent(self):
        if self.parameters['switch_axes']:
            extent = [self.dataset.data.axes[1].values[0],
                      self.dataset.data.axes[1].values[-1],
                      self.dataset.data.axes[0].values[0],
                      self.dataset.data.axes[0].values[-1]]
        else:
            extent = [self.dataset.data.axes[0].values[0],
                      self.dataset.data.axes[0].values[-1],
                      self.dataset.data.axes[1].values[0],
                      self.dataset.data.axes[1].values[-1]]
        return extent

    def _set_axes_labels(self):
        """Set axes labels from axes in dataset.

        This method is called automatically by :meth:`plot`.

        .. note::
            Due to the difference between axes conventions in plots,
            with axes being labelled *x*, *y*, *z* accordingly, and the
            convention of indexing arrays (first index refers to the row,
            converting to the *y* axis, the second index to the column,
            *i.e*. the *x* axis), labels have to be reverted for *x* and *y*
            axis with respect to the situation with 1D data.

        If you ever need to change the handling of your axes labels,
        override this method in a child class.
        """
        if self.parameters['switch_axes']:
            xlabel = self._create_axis_label_string(self.dataset.data.axes[1])
            ylabel = self._create_axis_label_string(self.dataset.data.axes[0])
        else:
            xlabel = self._create_axis_label_string(self.dataset.data.axes[0])
            ylabel = self._create_axis_label_string(self.dataset.data.axes[1])
        self.axes.set_xlabel(xlabel)
        self.axes.set_ylabel(ylabel)


class SinglePlotter2DStacked(SinglePlotter):
    # noinspection PyUnresolvedReferences
    """Stacked plots of 2D data

    A stackplot creates a series of lines stacked on top of each other from
    a 2D dataset.

    Attributes
    ----------
    dataset : :class:`aspecd.dataset.Dataset`
        Dataset the plotting should be done for

    drawing : :class:`list`
        list of :obj:`matplotlib.artist.Artist` objects, one for each of the
        actual lines of the plot

    parameters : :class:`dict`
        All parameters necessary for the plot, implicit and explicit

        The following keys exist, in addition to the keys inherited from the
        superclass:

        show_legend : :class:`bool`
            Whether to show a legend in the plot

            Default: False

        show_zero_lines : :class:`bool`
            Whether to show zero lines in the plot

            Regardless of whether you set this to true, zero lines will only be
            added to the final plot if the zero value is within the current
            axes limits.

            Zero line properties can be set via the
            :attr:`aspecd.plotting.Plotter.properties` attribute.

            Default: False

        stacking_dimension : :class:`int`
            dimension of data along which to stack the plot

            Default: 1

        offset : :class:`float`
            offset between lines

            If not explicitly set, the plotter will try its best to determine a
            sensible value, by using ``self.dataset.data.data.max() * 1.05``.

            Default: 0

        yticklabelformat : :class:`string`
            format for tick labels on the y axis

            Useful in case of too many decimals displayed on the y axis.
            Uses (currently) the "old-style" formatting syntax familiar from
            the C programming language, *e.g.* "%.2f" would format your
            labels with two decimals (including rounding).

            If "None", no explicit formatting will be performed and the
            defaults of Matplotlib applied.

            Default: None

    properties : :class:`aspecd.plotting.SinglePlot1DProperties`
        Properties of the plot, defining its appearance

        For the properties that can be set this way, see the documentation
        of the :class:`aspecd.plotting.SinglePlot1DProperties` class.


    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. Of course, all parameters settable
    for the superclasses can be set as well. The examples focus each on a
    single aspect.

    In the simplest case, just invoke the plotter with default values:

    .. code-block:: yaml

       - kind: singleplot
         type: SinglePlotter2DStacked
         properties:
           filename: output.pdf

    If you need to more precisely control the formatting of the y tick
    labels, particularly the number of decimals shown, you can set the
    formatting accordingly:

    .. code-block:: yaml

       - kind: singleplot
         type: SinglePlotter2DStacked
         properties:
           filename: output.pdf
           parameters:
             yticklabelformat: '%.2f'

    In this particular case, the y tick labels will appear with only two
    decimals. Note that currently, the "old style" formatting specifications
    are used due to their widespread use in other programming languages and
    hence the familiarity of many users with this particular notation.

    Sometimes you want to have horizontal "zero lines" appear for each
    individual trace of the stacked plot. This can be achieved explicitly
    setting the "show_zero_lines" parameter to "True" that is set to "False"
    by default:

    .. code-block:: yaml

       - kind: singleplot
         type: SinglePlotter2DStacked
         properties:
           filename: output.pdf
           parameters:
             show_zero_lines: True

    """

    # noinspection PyTypeChecker
    def __init__(self):
        super().__init__()
        self.description = '2D stackplot for a single dataset'
        self.dataset = None
        self.parameters = {
            'show_legend': False,
            'show_zero_lines': False,
            'stacking_dimension': 1,
            'offset': 0,
            'yticklabelformat': None,
        }
        self.drawing = []
        self.properties = SinglePlot1DProperties()

    @staticmethod
    def applicable(dataset):
        """Check whether plot is applicable to the given dataset.

        Checks for the dimension of the data of the dataset, i.e. the
        :attr:`aspecd.dataset.Data.data` attribute. Returns `True` if data
        are two-dimensional, and `False` otherwise.

        Returns
        -------
        applicable : :class:`bool`
            `True` if successful, `False` otherwise.

        """
        return dataset.data.data.ndim == 2

    def _create_plot(self):
        if not self.parameters['offset']:
            self.parameters['offset'] = self.dataset.data.data.max() * 1.05
        yticks = []
        if self.parameters['stacking_dimension'] == 0:
            for idx in range(self.dataset.data.data.shape[0]):
                handle = self.axes.plot(self.dataset.data.axes[1].values,
                                        self.dataset.data.data[idx, :]
                                        + idx * self.parameters['offset'])
                self.drawing.append(handle[0])
                yticks.append(idx * self.parameters['offset'])
            yticklabels = self.dataset.data.axes[0].values.astype(float)
        else:
            for idx in range(self.dataset.data.data.shape[1]):
                handle = self.axes.plot(self.dataset.data.axes[0].values,
                                        self.dataset.data.data[:, idx]
                                        + idx * self.parameters['offset'])
                self.drawing.append(handle[0])
                yticks.append(idx * self.parameters['offset'])
            yticklabels = self.dataset.data.axes[1].values.astype(float)
        self.properties.axes.yticks = yticks
        self.properties.axes.yticklabels = self._format_yticklabels(yticklabels)

    def _format_yticklabels(self, yticklabels):
        if self.parameters['yticklabelformat']:
            formatting = self.parameters['yticklabelformat']
            yticklabels = [formatting % label for label in yticklabels]
        return yticklabels

    def _set_axes_labels(self):
        """Set axes labels from axes in dataset.

        This method is called automatically by :meth:`plot`.

        .. note::
            Due to the difference between axes conventions in plots,
            with axes being labelled *x*, *y*, *z* accordingly, and the
            convention of indexing arrays (first index refers to the row,
            converting to the *y* axis, the second index to the column,
            *i.e*. the *x* axis), labels have to be reverted for *x* and *y*
            axis with respect to the situation with 1D data.

        If you ever need to change the handling of your axes labels,
        override this method in a child class.
        """
        if self.parameters['stacking_dimension'] == 0:
            xlabel = self._create_axis_label_string(self.dataset.data.axes[1])
            ylabel = self._create_axis_label_string(self.dataset.data.axes[0])
        else:
            xlabel = self._create_axis_label_string(self.dataset.data.axes[0])
            ylabel = self._create_axis_label_string(self.dataset.data.axes[1])
        self.axes.set_xlabel(xlabel)
        self.axes.set_ylabel(ylabel)

    def _add_zero_lines(self):
        if self.parameters['show_zero_lines']:
            dimension = self.parameters['stacking_dimension']
            for idx in range(self.dataset.data.data.shape[dimension]):
                offset = idx * self.parameters['offset']
                self.axes.axhline(
                    y=offset,
                    **self.properties.zero_lines.to_dict(),
                    zorder=1)


class MultiPlotter(Plotter):
    """Base class for plots of multiple datasets.

    Each class actually plotting data of multiple datasets should inherit from
    this class. Furthermore, all parameters, implicit and explicit,
    necessary to perform the plot, should eventually be stored in the property
    :attr:`parameters` (currently a dictionary).

    To perform the plot, call the :meth:`plot` method of the plotter directly.

    Further things that need to be changed upon inheriting from this class
    are the string stored in :attr:`description`, being basically a one-liner.

    The actual implementation of the plotting is done in the private method
    :meth:`_create_plot` that in turn gets called by :meth:`plot` that
    needs to be called directly (not from a dataset).

    Attributes
    ----------
    properties : :class:`aspecd.plotting.MultiPlotProperties`
        Properties of the plot, defining its appearance
    datasets : :class:`list`
        List of dataset the plotting should be done for

    Raises
    ------
    aspecd.exceptions.MissingDatasetError
        Raised when no dataset exists to act on
    aspecd.exceptions.NotApplicableToDatasetError
        Raised when processing step is not applicable to dataset

    """

    def __init__(self):
        super().__init__()
        self.properties = MultiPlotProperties()
        self.datasets = []
        self.description = 'Abstract plotting step for multiple dataset'
        # noinspection PyTypeChecker
        self.parameters['axes'] = [aspecd.dataset.Axis(),
                                   aspecd.dataset.Axis()]

    def plot(self):
        """Perform the actual plotting on the given list of datasets.

        If no dataset is added to the list of datasets of the
        object, the method will raise a respective exception.

        The actual plotting should be implemented within the non-public
        method :meth:`_create_plot`. Besides that, the applicability of the
        plotting to the given list of datasets will be checked automatically.
        These checks should be implemented in the method :meth:`applicable`.

        .. note::
            There is two ways of setting axes labels: The user may provide the
            information required in the "axes" key of the
            :attr:`aspecd.plotting.Plotter.parameters` property containing a
            list of :obj:`aspecd.dataset.Axis` objects. Alternatively,
            if no such information is provided, the axes of each dataset are
            checked for consistency, and if they are found to be identical,
            this information is used.

        Raises
        ------
        aspecd.exceptions.NotApplicableToDatasetError
            Raised when plotting is not applicable to at least one of the
            datasets listed in :attr:`datasets`
        aspecd.exceptions.MissingDatasetError
            Raised when no datasets exist to act on

        """
        self._check_for_applicability()
        self._set_drawing_properties()
        super().plot()
        self._set_axes_labels()
        self.properties.apply(plotter=self)

    def _check_for_applicability(self):
        if not self.datasets:
            raise aspecd.exceptions.MissingDatasetError
        if not all([self.applicable(dataset) for dataset in self.datasets]):
            raise aspecd.exceptions.NotApplicableToDatasetError(
                '%s not applicable to one or more datasets' % self.name)

    def _set_drawing_properties(self):
        if len(self.properties.drawings) < len(self.datasets):
            for _ in range(len(self.properties.drawings),
                           len(self.datasets)):
                self.properties.add_drawing()

    # noinspection PyUnresolvedReferences
    def _set_axes_labels(self):
        """Set axes labels from axes.

        This method is called automatically by :meth:`plot`.

        There is two ways of setting axes labels: The user may provide the
        information required in the "axes" key of the
        :attr:`aspecd.plotting.Plotter.parameters` property containing a
        list of :obj:`aspecd.dataset.Axis` objects. Alternatively,
        if no such information is provided, the axes of each dataset are
        checked for consistency, and if they are found to be identical,
        this information is used.

        If you ever need to change the handling of your axes labels,
        override this method in a child class.
        """
        xquantities = [ds.data.axes[0].quantity for ds in self.datasets]
        xunits = [ds.data.axes[0].unit for ds in self.datasets]
        yquantities = [ds.data.axes[1].quantity for ds in self.datasets]
        yunits = [ds.data.axes[1].unit for ds in self.datasets]
        if self.parameters['axes'][0].quantity:
            xlabel = \
                self._create_axis_label_string(self.parameters['axes'][0])
        elif all(xquantities) and all(xunits) and \
                aspecd.utils.all_equal(xquantities) and \
                aspecd.utils.all_equal(xunits):
            xlabel = \
                self._create_axis_label_string(self.datasets[0].data.axes[0])
        elif self.properties.axes.xlabel:
            xlabel = self.properties.axes.xlabel
        else:
            xlabel = ''
        if self.parameters['axes'][1].quantity:
            ylabel = \
                self._create_axis_label_string(self.parameters['axes'][1])
        elif all(yquantities) and all(yunits) and \
                aspecd.utils.all_equal(yquantities) and \
                aspecd.utils.all_equal(yunits):
            ylabel = \
                self._create_axis_label_string(self.datasets[0].data.axes[1])
        elif self.properties.axes.ylabel:
            ylabel = self.properties.axes.ylabel
        else:
            ylabel = ''
        self.axes.set_xlabel(xlabel)
        self.axes.set_ylabel(ylabel)


class MultiPlotter1D(MultiPlotter):
    """
    1D plots of multiple datasets.

    Convenience class taking care of 1D plots of multiple datasets. The type
    of plot can be set in its :attr:`aspecd.plotting.MultiPlotter1D.type`
    attribute. Allowed types are stored in the
    :attr:`aspecd.plotting.MultiPlotter1D.allowed_types` attribute.

    Quite a number of properties for figure, axes, and line can be set
    using the :attr:`aspecd.plotting.MultiPlotter1D.properties` attribute.
    For details, see the documentation of its respective class,
    :class:`aspecd.plotting.MultiPlot1DProperties`.

    To perform the plot, call the :meth:`plot` method of the plotter directly.

    Attributes
    ----------
    drawings : :class:`list`
        Actual graphical representations of the data of the datasets

    properties : :class:`aspecd.plotting.MultiPlot1DProperties`
        Properties of the plot, defining its appearance

        For the properties that can be set this way, see the documentation
        of the :class:`aspecd.plotting.MultiPlotProperties` class.

    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. Of course, all parameters settable
    for the superclasses can be set as well. The examples focus each on a
    single aspect.

    In the simplest case, just invoke the plotter with default values:

    .. code-block:: yaml

       - kind: multiplot
         type: MultiPlotter1D
         properties:
           filename: output.pdf

    To change the settings of each individual line (here the colour and label),
    supposing you have three lines, you need to specify the properties in a
    list for each of the drawings:

    .. code-block:: yaml

       - kind: multiplot
         type: MultiPlotter1D
         properties:
           filename: output.pdf
           properties:
             drawings:
               - color: '#FF0000'
                 label: foo
               - color: '#00FF00'
                 label: bar
               - color: '#0000FF'
                 label: foobar

    .. important::
        If you set colours using the hexadecimal RGB triple prefixed by
        ``#``, you need to explicitly tell YAML that these are strings,
        surrounding the values by quotation marks.

    """

    def __init__(self):
        super().__init__()
        self.description = '1D plotting step for multiple datasets'
        self.drawings = []
        self.properties = MultiPlot1DProperties()
        self._type = 'plot'
        self._allowed_types = ['plot', 'step', 'loglog', 'semilogx',
                               'semilogy', ]

    @property
    def type(self):
        """
        Get or set the plot type.

        Types need to be methods of the :class:`matplotlib.axes.Axes` class.

        Allowed plot types are stored in the
        :attr:`aspecd.plotting.SinglePlotter1D.allowed_types` attribute.

        Default: 'plot'

        Raises
        ------
        TypeError
            Raised in case of wrong type

        """
        return self._type

    @property
    def allowed_types(self):
        """
        Return the allowed plot types.

        Returns
        -------
        allowed_types: :class:`list`
            List of strings

        """
        return self._allowed_types

    @type.setter
    def type(self, plot_type=None):
        if plot_type not in self.allowed_types:
            raise TypeError
        self._type = plot_type

    @staticmethod
    def applicable(dataset):
        """Check whether plot is applicable to the given dataset.

        Checks for the dimension of the data of the dataset, i.e. the
        :attr:`aspecd.dataset.Data.data` attribute. Returns `True` if data
        are one-dimensional, and `False` otherwise.

        Returns
        -------
        applicable : :class:`bool`
            `True` if successful, `False` otherwise.

        """
        return dataset.data.data.ndim == 1

    def _create_plot(self):
        """Actual drawing of datasets"""
        plot_function = getattr(self.axes, self.type)
        self.drawings = []
        for idx, dataset in enumerate(self.datasets):
            if not self.properties.drawings[idx].label:
                self.properties.drawings[idx].label = dataset.label
            drawing, = plot_function(dataset.data.axes[0].values,
                                     dataset.data.data,
                                     label=self.properties.drawings[idx].label)
            self.drawings.append(drawing)


class MultiPlotter1DStacked(MultiPlotter1D):
    # noinspection PyUnresolvedReferences
    """
    Stacked 1D plots of multiple datasets.

    Convenience class taking care of 1D plots of multiple datasets. The type
    of plot can be set in its :attr:`aspecd.plotting.MultiPlotter1D.type`
    attribute. Allowed types are stored in the
    :attr:`aspecd.plotting.MultiPlotter1D.allowed_types` attribute.

    Quite a number of properties for figure, axes, and line can be set
    using the :attr:`aspecd.plotting.MultiPlotter1D.properties` attribute.
    For details, see the documentation of its respective class,
    :class:`aspecd.plotting.MultiPlot1DProperties`.

    To perform the plot, call the :meth:`plot` method of the plotter directly.

    Attributes
    ----------
    parameters : :class:`dict`
        All parameters necessary for this step.

        offset : :class:`float`
            The offset used for stacking the individual lines of the plot.

            If not provided, automatically a best fit will be calculated.

            Default: None

    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. Of course, all parameters settable
    for the superclasses can be set as well. The examples focus each on a
    single aspect.

    In the simplest case, just invoke the plotter with default values:

    .. code-block:: yaml

       - kind: multiplot
         type: MultiPlotter1DStacked
         properties:
           filename: output.pdf

    To change the settings of each individual line (here the colour and label),
    supposing you have three lines, you need to specify the properties in a
    list for each of the drawings:

    .. code-block:: yaml

       - kind: multiplot
         type: MultiPlotter1DStacked
         properties:
           filename: output.pdf
           properties:
             drawings:
               - color: '#FF0000'
                 label: foo
               - color: '#00FF00'
                 label: bar
               - color: '#0000FF'
                 label: foobar

    .. important::
        If you set colours using the hexadecimal RGB triple prefixed by
        ``#``, you need to explicitly tell YAML that these are strings,
        surrounding the values by quotation marks.

    Sometimes you want to have horizontal "zero lines" appear for each
    individual trace of the stacked plot. This can be achieved explicitly
    setting the "show_zero_lines" parameter to "True" that is set to "False"
    by default. The offset is automatically set that spectra don't overlap
    but can also be chosen freely (in units of the intensity):

    .. code-block:: yaml

       - kind: multiplot
         type: MultiPlotter1DStacked
         properties:
           filename: output.pdf
           parameters:
             show_zero_lines: True
             offset: 0.3

    """

    def __init__(self):
        super().__init__()
        self.description = '1D plotter for stacked display of multiple datasets'
        self.parameters["show_zero_lines"] = False
        # noinspection PyTypeChecker
        self.parameters["offset"] = None

    def _create_plot(self):
        """Actual drawing of datasets"""
        if not self.parameters['offset']:
            offset = abs(self.datasets[0].data.data.min()) * 1.05
            self.parameters["offset"] = offset
        else:
            offset = self.parameters["offset"]
        plot_function = getattr(self.axes, self.type)
        self.drawings = []
        for idx, dataset in enumerate(self.datasets):
            if not self.properties.drawings[idx].label:
                self.properties.drawings[idx].label = dataset.label
            drawing, = plot_function(dataset.data.axes[0].values,
                                     dataset.data.data - idx * offset,
                                     label=self.properties.drawings[idx].label)
            self.drawings.append(drawing)
        self.axes.tick_params(axis='y', which='both', left=False,
                              right=False, labelleft=False, labelright=False)

    def _add_zero_lines(self):
        if self.parameters['show_zero_lines']:
            for idx in range(len(self.datasets)):
                offset = -idx * self.parameters['offset']
                self.axes.axhline(
                    y=offset,
                    **self.properties.zero_lines.to_dict(),
                    zorder=1)


class CompositePlotter(Plotter):
    """Base class for plots consisting of multiple axes.

    The underlying idea of composite plotters is to use a dedicated
    existing plotter for each axis and assign this plotter to the list of
    plotters of the CompositePlotter object. Thus the actual plotting task
    is left to the individual plotter and the CompositePlotter only takes
    care of the specifics of plots consisting of more than one axis.

    In the framework of the CompositePlotter you can define the grid within
    which the axes are arranged. First, you define the grid dimension as a
    two-element vector, and second you define the subplot locations as list
    of four-element vectors. For details, see the documentation of the
    attributes :attr:`grid_dimensions` and :attr:`subplot_locations` below.

    For each of the subplots, define a plotter and add the object to the
    list of plotters, the attribute :attr:`plotter`. Make sure to equip each
    of these plotters with the necessary information. To actually plot,
    use the :meth:`plot` method of the CompositePlotter object.

    If you would like to display a single dataset in several ways within one
    and the same figure window, have a look at the
    :class:`SingleCompositePlotter` class. This class pretty much behaves
    like an ordinary SinglePlotter, where you can (and should) use the
    :meth:`aspecd.dataset.Dataset.plot` method to plot.

    .. note::
        When writing classes based on this class, do *not* override the
        :meth:`_create_plot` method. Generally, providing a list of plotters
        for each of the axes should be sufficient, and the CompositePlotter
        will call the :meth:`plot` property of each of these plotters
        automatically for you.

    Attributes
    ----------
    axes : :class:`list`
        List of axes

        Will eventually be objects of subtypes of
        :class:`matplotlib.axes.Axes` and populated upon calling
        :meth:`aspecd.plotting.Plotter.plot`.

    grid_dimensions : :class:`list`
        Dimensions of the grid used to layout the figure

        two elements: number of rows, number of columns

        Default: [1, 1]

    subplot_locations : :class:`list`
        List of subplot locations

        Each subplot location is a list with four numeric elements:
        [start_row, start_column, row_span, column_span]

        Default: [[0, 0, 1, 1]]

    axes_positions: :class:`list`
        List of axes positions for fine-adjustment

        Each axes position is a list with four numeric elements:
        [left_scale, bottom_scale, width_scale, height_scale] that are
        applied in the following way to the position of the individual axes::

            [left, bottom, width, height] = ax[idx].get_position().bounds
            new_position = [
                left + left_scale * width, bottom + bottom_scale * height,
                width * width_scale, height * height_scale
            ]
            ax[idx].set_position(new_position)

        Values can be both, positive and negative floats. Note, however,
        that negative values for the width and height parameter will mirror
        the axes accordingly.

        Default: []

    plotter : :class:`list`
        List of plotters

        Plotters are objects of type :class:`aspecd.plotting.Plotter`.

        Upon calling :meth:`aspecd.plotting.Plotter.plot`, for each axes in
        the list of axes, the corresponding plotter will be accessed and its
        :meth:`aspecd.plotting.Plotter.plot` method called.

    properties : :class:`aspecd.plotting.CompositePlotProperties`
        Properties of the plot, defining its appearance

        These properties are used for the CompositePlot as such, and if set
        will override those properties of the individual plotters used to
        fill the axes of the CompositePlot. For details, see the
        documentation of the :class:`aspecd.plotting.CompositePlotProperties`
        class.

    Raises
    ------
    aspecd.exceptions.MissingPlotterError
        Raised if the number of plotters does not match the number of axes

        Note that for each axes you need a corresponding plotter.

    """

    def __init__(self):
        super().__init__()
        self.description = 'Composite plotter displaying several axes'
        self.axes = []
        self.grid_dimensions = [1, 1]
        self.subplot_locations = [[0, 0, 1, 1]]
        self.axes_positions = []
        self.plotter = []
        self.properties = CompositePlotProperties()

    def _create_figure_and_axes(self):
        self.figure = plt.figure()
        grid_spec = self.figure.add_gridspec(self.grid_dimensions[0],
                                             self.grid_dimensions[1])
        for subplot in self.subplot_locations:
            self.axes.append(self.figure.add_subplot(
                grid_spec[subplot[0]:subplot[0] + subplot[2],
                          subplot[1]:subplot[1] + subplot[3]]))

    def _create_plot(self):
        if not self.plotter or len(self.plotter) < len(self.axes):
            raise aspecd.exceptions.MissingPlotterError
        for idx, axes in enumerate(self.axes):
            self.plotter[idx].figure = self.figure
            self.plotter[idx].axes = axes
            self.plotter[idx].plot()
        for idx, position in enumerate(self.axes_positions):
            left, bottom, width, height = self.axes[idx].get_position().bounds
            new_position = [
                left + position[0] * width, bottom + position[1] * height,
                position[2] * width, position[3] * height
            ]
            self.axes[idx].set_position(new_position)


class SingleCompositePlotter(CompositePlotter):
    """Composite plotter for single datasets

    This composite plotter is used for different representations of one and the
    same dataset in multiple axes contained in one figure. In this respect,
    it works like all the other ordinary single plotters derived from
    :class:`SinglePlotter`, *i.e.* it usually gets called by using the dataset's
    :meth:`aspecd.dataset.Dataset.plot` method.

    As with the generic :class:`CompositePlotter`, specify both the axes
    grid and locations as well as the plotters to use for each individual
    plot. Calling :meth:`plot` by means of
    :meth:`aspecd.dataset.Dataset.plot` will assign the dataset to each of
    the individual plotters and make them plot the data contained in the
    dataset.

    Attributes
    ----------
    dataset : :class:`aspecd.dataset.Dataset`
        Dataset the plotting should be done for

    Raises
    ------
    aspecd.exceptions.MissingDatasetError
        Raised when no dataset exists to act on

    aspecd.exceptions.NotApplicableToDatasetError
        Raised when processing step is not applicable to dataset

    """

    def __init__(self):
        super().__init__()
        self.dataset = None
        self.description = 'Composite plotter for single dataset'

    # pylint: disable=arguments-differ
    def plot(self, dataset=None, from_dataset=False):
        """Perform the actual plotting on the given dataset.

        If no dataset is set as property in the object, the method will
        raise a respective exception. The dataset object :meth:`plot` method
        always assigns its dataset as the respective dataset attribute of
        the plotter class.

        The actual plotting should be implemented within the non-public
        method :meth:`_create_plot`. Besides that, the applicability of the
        plotting to the given dataset will be checked automatically. These
        checks should be implemented in the method :meth:`applicable`.

        Parameters
        ----------
        dataset : :class:`aspecd.dataset.Dataset`
            dataset to perform plot for

        from_dataset : `boolean`
            whether we are called from within a dataset

            Defaults to "False" and shall never be set manually.

        Returns
        -------
        dataset : :class:`aspecd.dataset.Dataset`
            dataset plot has been performed for

        Raises
        ------
        aspecd.exceptions.NotApplicableToDatasetError
            Raised when plotting is not applicable to dataset
        aspecd.exceptions.MissingDatasetError
            Raised when no dataset exists to act on

        """
        self._assign_dataset(dataset)
        self._call_from_dataset(from_dataset)
        return self.dataset

    def create_history_record(self):
        """
        Create history record to be added to the dataset.

        Usually, this method gets called from within the
        :meth:`aspecd.dataset.plot` method of the
        :class:`aspecd.dataset.Dataset` class and ensures the history of
        each plotting step to get written properly.

        Returns
        -------
        history_record : :class:`aspecd.history.PlotHistoryRecord`
            history record for plotting step

        """
        history_record = \
            aspecd.history.PlotHistoryRecord(package=self.dataset.package_name)
        history_record.plot = aspecd.history.SinglePlotRecord(plotter=self)
        history_record.plot.preprocessing = copy.deepcopy(
            self.dataset.history)
        return history_record

    def _assign_dataset(self, dataset):
        if not dataset:
            if not self.dataset:
                raise aspecd.exceptions.MissingDatasetError
        else:
            self.dataset = dataset
        for plotter in self.plotter:
            plotter.dataset = self.dataset

    def _call_from_dataset(self, from_dataset):
        if not from_dataset:
            self.dataset.plot(self)
        else:
            self._check_applicability()
            super().plot()

    def _check_applicability(self):
        if not self.applicable(self.dataset):
            message = "%s not applicable to dataset with id %s" \
                      % (self.name, self.dataset.id)
            raise aspecd.exceptions.NotApplicableToDatasetError(message=message)


class Saver:
    """Base class for saving plots.

    For basic saving of plots, no subclassing is necessary, as the
    :meth:`save` method uses :meth:`matplotlib.figure.Figure.savefig` and
    can cope with all possible parameters via the :attr:`parameters` property.

    Attributes
    ----------
    filename : :class:`str`
        Name of the file the plot should get saved to
    parameters : :class:`dict`
        Key-value store of parameters for saving.

        See :meth:`matplotlib.figure.Figure.savefig` for details and
        available options.
    plotter : :class:`aspecd.plotting.Plotter`
        Plotter whose plot should be saved.

    Raises
    ------
    aspecd.exceptions.MissingFilenameError
        Raised if no filename is provided for saver.
    aspecd.exceptions.MissingPlotError
        Raised if no plot is provided to act upon.

    """

    def __init__(self, filename=None):
        self.filename = filename
        self.parameters = dict()
        self.plotter = None

    def save(self, plotter=None):
        """Save the plot to a file.

        If no plotter is provided at method call, but is set as property in the
        Saver object, the :meth:`aspecd.plotting.Plotter.save` method of the
        plotter will be called.

        If no plotter is provided at method call nor as property of the object,
        the method will raise a respective exception.

        The actual saving is implemented within the private method
        :meth:`_save_plot`.

        Parameters
        ----------
        plotter : `aspecd.plotting.Plotter`
            plot to be saved

        Raises
        ------
        aspecd.exceptions.MissingFilenameError
            Raised if no filename is provided for saver.
        aspecd.exceptions.MissingPlotError
            Raised if no plot is provided to act upon.

        """
        if not self.filename:
            raise aspecd.exceptions.MissingFilenameError
        if not plotter:
            if self.plotter:
                self.plotter.save(self)
            else:
                raise aspecd.exceptions.MissingPlotError
        else:
            self.plotter = plotter
        self._save_plot()

    def _save_plot(self):
        """Perform the actual saving of the plot.

        The implementation of the actual saving goes in here in all
        classes inheriting from Saver. This method is automatically
        called by :meth:`save`.

        In the simplest case, saving is a call to :meth:`savefig` of the
        figure to save. To access this figure, use the property
        :attr:`plotter.figure`.

        """
        self._add_file_extension()
        self.plotter.figure.savefig(self.filename, **self.parameters)

    def _add_file_extension(self):
        """Add file extension to filename if available.

        Check whether an export file format has been explicitly given,
        and if so, add proper extension to filename.

        Two cases are possible, and are dealt with as follows:

        (1) No file extension, but format specified.

        The appropriate file extension (same as format) will be added.

        (2) File extension does not match format specifier.

        The file extension will be replaced by the one specified in format.

        """
        file_basename, file_extension = os.path.splitext(self.filename)
        if "format" in self.parameters:
            if file_extension != self.parameters["format"]:
                self.filename = '.'.join([file_basename,
                                          self.parameters["format"]])
            elif not file_extension:
                self.filename = '.'.join([self.filename,
                                          self.parameters["format"]])


class Caption(aspecd.utils.Properties):
    """
    Caption for figures.

    Attributes
    ----------
    title: :class:`str`
        usually one sentence describing the intent of the figure

        Often plotted bold-face in a figure caption.

    text: :class:`str`
        additional text directly following the title

        Contains more information about the plot. Ideally, a figure caption
        is self-contained such that it explains the figure sufficiently to
        understand its intent and content without needing to read all the
        surrounding text.

    parameters: :class:`list`
        names of parameters that should be included in the figure caption

        Usually, these parameters get included at the very end of a figure
        caption.

    """

    def __init__(self):
        super().__init__()
        self.title = ''
        self.text = ''
        self.parameters = []


class PlotProperties(aspecd.utils.Properties):
    """
    Properties of a plot, defining its appearance.

    Attributes
    ----------
    figure : :class:`aspecd.plotting.FigureProperties`
        Properties of the figure as such

        For the properties that can be set this way, see the documentation
        of the :class:`aspecd.plotting.FigureProperties` class.

    legend : :class:`aspecd.plotting.LegendProperties`
        Properties of the legend.

        For the properties that can be set this way, see the documentation
        of the :class:`aspecd.plotting.LegendProperties` class.

    zero_lines : :class:`aspecd.plotting.LineProperties`
        Properties of the zero lines.

        For the properties that can be set this way, see the documentation
        of the :class:`aspecd.plotting.LineProperties` class.

        Default values for the zero lines are:

        * color: #cccccc


    Raises
    ------
    aspecd.exceptions.MissingPlotterError
        Raised if no plotter is provided.

    """

    def __init__(self):
        super().__init__()
        self.figure = FigureProperties()
        self.legend = LegendProperties()
        self.zero_lines = LineProperties()
        # Set default properties
        self.zero_lines.color = '#cccccc'

    def apply(self, plotter=None):
        """
        Apply properties to plot.

        In this generic class having only figure properties, only these
        properties are set. Classes derived from
        :class:`aspecd.plotting.PlotProperties` need to take care of
        setting all available properties.

        Parameters
        ----------
        plotter: :class:`aspecd.plotting.Plotter`
            Plotter the properties should be applied to.

        Raises
        ------
        aspecd.exceptions.MissingPlotterError
            Raised if no plotter is provided.

        """
        if not plotter:
            raise aspecd.exceptions.MissingPlotterError
        self.figure.apply(figure=plotter.figure)


class SinglePlotProperties(PlotProperties):
    """
    Properties of a single plot, defining its appearance.

    Attributes
    ----------
    axes : :class:`aspecd.plotting.AxesProperties`
        Properties of the axes.

        For the properties that can be set this way, see the documentation
        of the :class:`aspecd.plotting.AxesProperties` class.

    grid : :class:`aspecd.plotting.GridProperties`
        Properties of the grid.

        For the properties that can be set this way, see the documentation
        of the :class:`aspecd.plotting.GridProperties` class.

    drawing : :class:`aspecd.plotting.DrawingProperties`
        Properties of the line within a plot

        For the properties that can be set this way, see the documentation
        of the :class:`aspecd.plotting.DrawingProperties` class.

    Raises
    ------
    aspecd.exceptions.MissingPlotterError
        Raised if no plotter is provided.

    """

    def __init__(self):
        super().__init__()
        self.axes = AxesProperties()
        self.grid = GridProperties()
        self.drawing = DrawingProperties()

    def apply(self, plotter=None):
        """
        Apply properties to plot.

        Parameters
        ----------
        plotter: :class:`aspecd.plotting.SinglePlotter`
            Plotter the properties should be applied to.

        Raises
        ------
        aspecd.exceptions.MissingPlotterError
            Raised if no plotter is provided.

        """
        super().apply(plotter=plotter)
        self.axes.apply(axes=plotter.axes)
        self.grid.apply(axes=plotter.axes)
        if plotter.drawing:
            self.drawing.apply(drawing=plotter.drawing)


class SinglePlot1DProperties(SinglePlotProperties):
    """
    Properties of a 1D single plot, defining its appearance.

    Attributes
    ----------
    drawing : :class:`aspecd.plotting.LineProperties`
        Properties of the line within a plot

        For the properties that can be set this way, see the documentation
        of the :class:`aspecd.plotting.LineProperties` class.

    Raises
    ------
    aspecd.exceptions.MissingPlotterError
        Raised if no plotter is provided.

    """

    def __init__(self):
        super().__init__()
        self.drawing = LineProperties()


class SinglePlot2DProperties(SinglePlotProperties):
    """
    Properties of a 2D single plot, defining its appearance.

    Attributes
    ----------
    drawing : :class:`aspecd.plotting.SurfaceProperties`
        Properties of the surface within a plot

        For the properties that can be set this way, see the documentation
        of the :class:`aspecd.plotting.SurfaceProperties` class.

    Raises
    ------
    aspecd.exceptions.MissingPlotterError
        Raised if no plotter is provided.

    """

    def __init__(self):
        super().__init__()
        self.drawing = SurfaceProperties()


class MultiPlotProperties(PlotProperties):
    """
    Properties of a multiplot, defining its appearance.

    Attributes
    ----------
    axes : :class:`aspecd.plotting.AxesProperties`
        Properties of the axes.

        For the properties that can be set this way, see the documentation
        of the :class:`aspecd.plotting.AxesProperties` class.

    grid : :class:`aspecd.plotting.GridProperties`
        Properties of the grid.

        For the properties that can be set this way, see the documentation
        of the :class:`aspecd.plotting.GridProperties` class.

    drawings : :class:`list`
        Properties of the lines within a plot.

        Each element is a :obj:`aspecd.plotting.DrawingProperties` object

        For the properties that can be set this way, see the documentation
        of the :class:`aspecd.plotting.DrawingProperties` class.

    Raises
    ------
    aspecd.plotting.MissingPlotterError
        Raised if no plotter is provided.

    """

    def __init__(self):
        super().__init__()
        self.axes = AxesProperties()
        self.grid = GridProperties()
        self.drawings = []

    def from_dict(self, dict_=None):
        """
        Set attributes from dictionary.

        The key ``drawing`` is handled in a special way: First of all,
        :attr:`aspecd.plotting.MultiPlotProperties.drawing` is a list,
        hence we need to iterate over the entries of the list. Furthermore,
        a new element of the list is appended only if it does not exist
        already.

        As different MultiPlotter objects will use different properties
        classes for their drawing, adding a new drawing is handled by a
        separate method,
        :meth:`aspecd.plotting.MultiPlotProperties.add_drawing`.
        Additionally, each MultiPlotter class can use this method as well,
        to add drawing properties for each plotted item.

        Parameters
        ----------
        dict_ : :class:`dict`
            Dictionary containing information of a task.

        Raises
        ------
        aspecd.exceptions.MissingDictError
            Raised if no dict is provided.

        """
        if 'drawings' in dict_:
            for idx in range(len(self.drawings), len(dict_['drawings'])):
                self.add_drawing()
            for idx, drawing in enumerate(dict_['drawings']):
                self.drawings[idx].from_dict(drawing)
            dict_.pop('drawings')
        if dict_:
            super().from_dict(dict_)

    def add_drawing(self):
        """
        Add a :obj:`aspecd.plotting.DrawingProperties` object to the list.

        As different MultiPlotter objects will use different properties
        classes for their drawing, adding a new drawing is handled by this
        method. Additionally, each MultiPlotter class can use this method as
        well, to add drawing properties for each plotted item.

        .. note::
            A note for developers: Concrete MultiPlotter classes will use
            classes derived from :class:`aspecd.plotting.MultiPlotProperties`
            for their ``properties`` property. These properties classes
            should override this method to ensure the correct type of
            :class:`aspecd.plotting.DrawingProperties` is instantiated.
            Furthermore, make sure to set default values according to the
            current cycler.

        """
        drawing_properties = DrawingProperties()
        self.drawings.append(drawing_properties)

    def apply(self, plotter=None):
        """
        Apply properties to plot.

        Parameters
        ----------
        plotter: :class:`aspecd.plotting.MultiPlotter`
            Plotter the properties should be applied to.

        Raises
        ------
        aspecd.exceptions.MissingPlotterError
            Raised if no plotter is provided.

        """
        super().apply(plotter=plotter)
        self.axes.apply(axes=plotter.axes)
        self.grid.apply(axes=plotter.axes)
        if hasattr(plotter, 'legend') and plotter.legend:
            self.legend.apply(legend=plotter.legend)
        if hasattr(plotter, 'drawings'):
            for idx, drawing in enumerate(plotter.drawings):
                self.drawings[idx].apply(drawing=drawing)


class MultiPlot1DProperties(MultiPlotProperties):
    """
    Properties of a 1D multiplot, defining its appearance.

    drawings : :class:`list`
        Properties of the lines within a plot.

        Each element is a :obj:`aspecd.plotting.LineProperties` object

        For the properties that can be set this way, see the documentation
        of the :class:`aspecd.plotting.LineProperties` class.

    Raises
    ------
    aspecd.exceptions.MissingPlotterError
        Raised if no plotter is provided.

    """

    def add_drawing(self):
        """
        Add a :obj:`aspecd.plotting.LineProperties` object to the list.

        The default properties are set as well, as obtained from
        :obj:`matplotlib.pyplot.rcParams`. These contain at least colour,
        width, marker, and style of a line.
        """
        drawing_properties = LineProperties()
        self._set_default_properties(drawing_properties)
        self.drawings.append(drawing_properties)

    def _set_default_properties(self, drawing_properties):
        property_cycle = plt.rcParams['axes.prop_cycle'].by_key()
        length_properties = len(property_cycle["color"])
        idx = len(self.drawings)
        for key, value in property_cycle.items():
            setattr(drawing_properties, key, value[idx % length_properties])
        for key in ['linewidth', 'linestyle', 'marker']:
            rc_property = 'lines.' + key
            if rc_property in plt.rcParams.keys():
                setattr(drawing_properties, key, plt.rcParams[rc_property])


class CompositePlotProperties(PlotProperties):
    """
    Properties of a composite plot, defining its appearance.

    Attributes
    ----------
    axes : :class:`aspecd.plotting.AxesProperties`
        Properties for all axes of the CompositePlotter.

        This property is used to set properties for all axes of a
        CompositePlotter at once. This will override the settings of the
        individual plotters.

        For the properties that can be set this way, see the documentation
        of the :class:`aspecd.plotting.AxesProperties` class.

    Raises
    ------
    aspecd.exceptions.MissingPlotterError
        Raised if no plotter is provided.

    """

    def __init__(self):
        super().__init__()
        self.axes = AxesProperties()

    def apply(self, plotter=None):
        """
        Apply properties to plot.

        Parameters
        ----------
        plotter: :class:`aspecd.plotting.CompositePlotter`
            Plotter the properties should be applied to.

        Raises
        ------
        aspecd.exceptions.MissingPlotterError
            Raised if no plotter is provided.

        """
        super().apply(plotter=plotter)
        if hasattr(plotter, 'axes'):
            for axes in plotter.axes:
                self.axes.apply(axes=axes)


class FigureProperties(aspecd.utils.Properties):
    """
    Properties of a figure of a plot, i.e., the most general aspects.

    Basically, the attributes are a subset of what :mod:`matplotlib` defines
    for :obj:`matplotlib.figure.Figure` objects.

    Attributes
    ----------
    size: :class:`tuple`
        Figure dimension (width, height) in inches.

        2-tuple of floats

        Default: 6.4, 4.8

    dpi: :class:`float`
        Figure resolution in dots per inch.

        Default: 100

    title: :class:`str`
        Title for the figure as a whole

    Raises
    ------
    aspecd.exceptions.MissingFigureError
        Raised if no figure is provided.

    """

    def __init__(self):
        super().__init__()
        self.size = (6.4, 4.8)
        self.dpi = 100.0
        self.title = ''

    def apply(self, figure=None):
        """
        Apply properties to figure.

        Parameters
        ----------
        figure: :class:`matplotlib.figure.Figure`
            Plotter the properties should be applied to.

        Raises
        ------
        aspecd.exceptions.MissingFigureError
            Raised if no figure is provided.

        """
        if not figure:
            raise aspecd.exceptions.MissingFigureError
        for prop in self.get_properties():
            setattr(figure, prop, getattr(self, prop))
        # Need to set size and title manually
        figure.set_size_inches(self.size)
        figure.suptitle(self.title)


class AxesProperties(aspecd.utils.Properties):
    """
    Properties of an axis of a plot.

    Basically, the attributes are a subset of what :mod:`matplotlib` defines
    for :obj:`matplotlib.axes.Axes` objects.

    Attributes
    ----------
    aspect: {'auto', 'equal'} or num
        aspect of the axis scaling, i.e. the ratio of y-unit to x-unit

        Default: ''

    facecolor: color
        facecolor of the axes

        Default: None

    position: :class:`list`
        position of the axes: left, bottom, width, height

        four numbers in the interval [0..1]

        Default: []

    title: :class:`str`
        title for the axis

        Note that this is a per-axis title, unlike the figure title set for
        the whole figure.

        Default: ''

    xlabel: :class:`str`
        label for the x-axis

        Default: ''

    xlim: :class:`list`
        x-axis view limits, two floats

        Default: []

    xscale: :class:`str`
        x-axis scale

        possible values: "linear", "log", "symlog", "logit"

        Default: ''

    xticks:
        y ticks with list of ticks

        Default: None

    xticklabels: :class:`list`
        x-tick labels: list of string labels

        Default: None

    ylabel: :class:`str`
        label for the y-axis

        Default: ''

    ylim: :class:`list`
        y-axis view limits, two floats

        Default: []

    yscale: :class:`str`
        y-axis scale

        possible values: "linear", "log", "symlog", "logit"

        Default: ''

    yticks:
        y ticks with list of ticks

        Default: None

    yticklabels: :class:`list`
        y-tick labels: list of string labels

        Default: None

    Raises
    ------
    aspecd.exceptions.MissingAxisError
        Raised if no axis is provided.

    """

    def __init__(self):
        super().__init__()
        self.aspect = ''
        self.facecolor = None
        self.position = []
        self.title = ''
        self.xlabel = ''
        self.xlim = []
        self.xscale = ''
        self.xticklabels = None
        self.xticks = None
        self.ylabel = ''
        self.ylim = []
        self.yscale = ''
        self.yticklabels = None
        self.yticks = None

    def apply(self, axes=None):
        """
        Apply settable properties to axis.

        Only properties that are not None or empty will be set, in order to
        prevent problems. The underlying method used to set the axis
        properties is :meth:`matplotlib.axes.Axes.update`.

        Parameters
        ----------
        axes: :class:`matplotlib.axes.Axes`
            axis to set properties for

        Raises
        ------
        aspecd.exceptions.MissingAxisError
            Raised if no axis is provided.

        """
        if not axes:
            raise aspecd.exceptions.MissingAxisError
        axes.update(self._get_settable_properties())
        for property_, value in self._get_settable_properties().items():
            if hasattr(axes, 'set_' + property_):
                getattr(axes, 'set_' + property_)(value)
        if self.xticks is not None:
            axes.xaxis.set_major_locator(ticker.FixedLocator(self.xticks))
        if self.yticks is not None:
            axes.yaxis.set_major_locator(ticker.FixedLocator(self.yticks))
        if self.xticklabels is not None:
            axes.set_xticklabels(self.xticklabels)
        if self.yticklabels is not None:
            axes.set_yticklabels(self.yticklabels)

    def _get_settable_properties(self):
        """
        Return properties that can be applied to an axis.

        Properties that are either None or empty often cause problems.
        Therefore, the properties of
        :class:`aspecd.plotting.AxesProperties` are reduced accordingly to
        those properties that are neither None nor empty.

        Returns
        -------
        properties: :class:`dict`
            Properties that are neither None nor empty

        """
        all_properties = self.to_dict()
        properties = dict()
        for prop in all_properties:
            if prop.startswith(('xtick', 'ytick')):
                pass
            elif isinstance(all_properties[prop], np.ndarray):
                if any(all_properties[prop]):
                    properties[prop] = all_properties[prop]
            elif all_properties[prop]:
                properties[prop] = all_properties[prop]
        return properties


class LegendProperties(aspecd.utils.Properties):
    """
    Properties of a legend of a plot, i.e., the most general aspects.

    Basically, the attributes are a subset of what :mod:`matplotlib` defines
    for :obj:`matplotlib.legend.Legend` objects.

    Attributes
    ----------
    loc : :class:`str`
        Location of the legend

        For possible values, see :class:`matplotlib.legend.Legend`
    frameon : :class:`bool`
        Whether to plot a box around the legend

        Default: True

    Raises
    ------
    aspecd.exceptions.MissingLegendError
        Raised if no legend is provided.

    """

    def __init__(self):
        super().__init__()
        self.loc = 'best'
        self.frameon = True
        self._exclude = ['location']
        self._exclude_from_to_dict = ['location']

    @property
    def location(self):
        """Alias for :attr:`aspecd.plotting.LegendProperties.loc`"""
        return self.loc

    @location.setter
    def location(self, value=''):
        self.loc = value

    def apply(self, legend=None):
        """
        Apply properties to legend.

        Parameters
        ----------
        legend: :class:`matplotlib.legend.Legend`
            Plotter the properties should be applied to.

        Raises
        ------
        aspecd.exceptions.MissingFigureError
            Raised if no figure is provided.

        """
        if not legend:
            raise aspecd.exceptions.MissingLegendError
        for prop in self.get_properties():
            setattr(legend, prop, getattr(self, prop))


class DrawingProperties(aspecd.utils.Properties):
    """
    Properties of a drawing within a plot.

    A drawing is the most abstract object representing data within axes,
    such as a line, contour, etcetera.

    Attributes
    ----------
    label: :class:`str`
        label of a line that gets used within a legend, default: ''

    Raises
    ------
    aspecd.exceptions.MissingDrawingError
        Raised if no drawing is provided.

    """

    def __init__(self):
        super().__init__()
        self.label = ''

    def apply(self, drawing=None):
        """
        Apply properties to drawing.

        For each property, the corresponding "set_<property>" method of the
        line will be called.

        Parameters
        ----------
        drawing: :class:`matplotlib.axes.Axes`
            axis to set properties for

        Raises
        ------
        aspecd.exceptions.MissingDrawingError
            Raised if no line is provided.

        """
        if not drawing:
            raise aspecd.exceptions.MissingDrawingError
        for prop in self.get_properties():
            if isinstance(drawing, list):
                for element in drawing:
                    self._save_set_drawing_property(element, prop)
            else:
                self._save_set_drawing_property(drawing, prop)

    def _save_set_drawing_property(self, drawing=None, prop=None):
        """Save setting of drawing properties.

        The method first checks whether the corresponding setter for the
        property exists and only in this case sets the property.

        .. todo::
            Currently, the situation of no setter existing will be silently
            ignored. This should change in the future with the advent of
            logging.

        Parameters
        ----------
        drawing : :class:`matplotlib.axes.Axes`
            axis to set properties for

        prop : :class:`str`
            name of the property to set

        """
        if hasattr(drawing, ''.join(['set_', prop])):
            getattr(drawing, ''.join(['set_', prop]))(getattr(self, prop))


class LineProperties(DrawingProperties):
    """
    Properties of a line within a plot.

    Basically, the attributes are a subset of what :mod:`matplotlib` defines
    for :obj:`matplotlib.lines.Line2D` objects.

    Attributes
    ----------
    color: color
        color of the line

        For details see :mod:`matplotlib.colors`

    drawstyle: :class:`str`
        drawing style of the line, default: 'default'

        For details see :meth:`matplotlib.lines.Line2D.set_drawstyle`

    linestyle: :class:`str`
        style of the line, default: 'solid'

        For details see :meth:`matplotlib.lines.Line2D.set_linestyle`

    linewidth: :class:`float`
        width of the line, float value in points, default: 1.5

    marker: :class:`str`
        marker used for the line, default: ''

        For details see :mod:`matplotlib.markers`

    Raises
    ------
    aspecd.exceptions.MissingDrawingError
        Raised if no line is provided.

    """

    def __init__(self):
        super().__init__()
        self.color = '#000000'
        self.drawstyle = 'default'
        self.linestyle = 'solid'
        self.linewidth = 1.0
        self.marker = ''

    def settable_properties(self):
        """
        Return properties that are not empty or None.

        Returns
        -------
        properties : :class:`dict`
            Dictionary containing all settable properties, *i.e.* properties
            that are neither empty nor None.

        """
        properties = dict()
        for prop in self.get_properties():
            if getattr(self, prop):
                properties[prop] = getattr(self, prop)
        return properties


class SurfaceProperties(DrawingProperties):
    """
    Properties of a surface within a plot.

    Basically, the attributes are a subset of what :mod:`matplotlib` defines
    for :obj:`matplotlib.contour.ContourSet` and
    :obj:`matplotlib.image.AxesImage` objects.

    Attributes
    ----------
    cmap : :class:`str`
        name of the colormap to use

        For details see :class:`matplotlib.colors.Colormap`

    linewidths : :class:`float`
        Width of the contour lines (if present)

    linestyles : :class:`str`
        Style of the contour lines (if present)

    colors : :class:`str`
        Colour of the contour lines (if present)

    """

    def __init__(self):
        super().__init__()
        self.cmap = 'viridis'
        self.linewidths = None
        self.linestyles = None
        self.colors = None

    def apply(self, drawing=None):
        """
        Apply properties to drawing.

        Parameters
        ----------
        drawing:
            matplotlib object to set properties for

        """
        super().apply(drawing=drawing)
        # Note: Since Python 3.6 and compatible matplotlib versions,
        #       all drawings have an attribute "axes", hence when dropping
        #       Python 3.5 support, testing can be removed
        if hasattr(drawing, 'axes'):
            children = drawing.axes.get_children()
        else:
            children = drawing.ax.get_children()
        for child in children:
            if isinstance(child, mpl.collections.LineCollection):
                if self.linewidths:
                    child.set_linewidths(self.linewidths)
                if self.linestyles:
                    child.set_linestyles(self.linestyles)
                if self.colors:
                    child.set_color(self.colors)


class GridProperties(aspecd.utils.Properties):
    """
    Properties of a line within a plot.

    Basically, the attributes are a subset of what :mod:`matplotlib` defines
    for :obj:`matplotlib.lines.Line2D` objects.

    Attributes
    ----------
    show: :class:`bool`
        whether to show grids

    ticks: :class:`str`
        ticks to set grid lines for: {'major', 'minor', 'both'}

        For details see the ``which`` parameter of
        :meth:`matplotlib.axes.Axes.grid`

    axis: :class:`str`
        axis to set grid lines for: {'both', 'x', 'y'}

        For details see :meth:`matplotlib.axes.Axes.grid`

    lines: :class:`aspecd.plotting.LineProperties`
        line properties of the grid

    Raises
    ------
    TypeError
        Raised if no axes is provided.

    """

    def __init__(self):
        super().__init__()
        self.show = False
        self.ticks = ''
        self.axis = ''
        self.lines = LineProperties()
        # Set default properties
        self.lines.color = '#cccccc'

    def apply(self, axes=None):
        """
        Apply properties to axes.

        If :attr:`show` is false, no grid will be displayed. Otherwise,
        the properties will be set, including the line properties.

        Parameters
        ----------
        axes: :class:`matplotlib.axes.Axes`
            axis to set properties for

        Raises
        ------
        TypeError
            Raised if called without axes object

        """
        if not axes:
            raise TypeError('Missing 1 positional argument: axes')
        # Partly untested code: no plan how to test that a grid is present
        if not self.show:
            axes.grid(False)
        else:
            if self.ticks and self.axis:
                axes.grid(True, which=self.ticks, axis=self.axis,
                          **self.lines.settable_properties())
            elif self.ticks:
                axes.grid(True, which=self.ticks,
                          **self.lines.settable_properties())
            elif self.axis:
                axes.grid(True, axis=self.axis,
                          **self.lines.settable_properties())
            else:
                axes.grid(True, **self.lines.settable_properties())
