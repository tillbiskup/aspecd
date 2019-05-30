"""
Plotting: Graphical representations of data extracted from datasets.

Plotting relies on `matplotlib <https://matplotlib.org/>`_, and mainly its
object-oriented interface should be used for the actual plotting. Each
plotter contains references to the respective figure and axes created usually
by a call similar to::

    fig, ax = matplotlib.pyplot.subplots()

For convenience, short hands for the :attr:`figure` and :attr:`axes`
properties of a plotter are available, named :attr:`fig` and :attr:`ax`,
respectively.

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

Regardless of the type of plotter, saving plots is always done using
objects of the :class:`aspecd.plotting.Saver` class. The actual task of
saving a plot is as easy as calling the :meth:`save` method of a plotter
with a saver object as its argument.

"""

import copy
import os

import matplotlib as mpl
import matplotlib.pyplot as plt

import aspecd.utils
import aspecd.dataset


class Error(Exception):
    """Base class for exceptions in this module."""

    pass


class MissingDatasetError(Error):
    """Exception raised when no dataset exists to act on

    Attributes
    ----------
    message : :class:`str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class PlotNotApplicableToDatasetError(Error):
    """Exception raised when processing step is not applicable to dataset

    Attributes
    ----------
    message : :class:`str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class MissingSaverError(Error):
    """Exception raised when no saver is provided.

    Attributes
    ----------
    message : :class:`str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class MissingFilenameError(Error):
    """Exception raised when no filename was provided

    Attributes
    ----------
    message : :class:`str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class MissingPlotError(Error):
    """Exception raised when no plot exists to save.

    Attributes
    ----------
    message : :class:`str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class MissingPlotterError(Error):
    """Exception raised when no plotter is provided.

    Attributes
    ----------
    message : :class:`str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class MissingFigureError(Error):
    """Exception raised when no figure is provided.

    Attributes
    ----------
    message : :class:`str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class MissingAxisError(Error):
    """Exception raised when no axis is provided.

    Attributes
    ----------
    message : :class:`str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class MissingLegendError(Error):
    """Exception raised when no legend is provided.

    Attributes
    ----------
    message : :class:`str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class MissingDrawingError(Error):
    """Exception raised when no drawing (line, ...) is provided.

    Attributes
    ----------
    message : :class:`str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


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

    Attributes
    ----------
    name : :class:`str`
        Name of the plotter.

        Defaults always to the full class name, don't change!
    parameters : :class:`dict`
        All parameters necessary for the plot, implicit and explicit
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
        User-supplied information for the figure line_properties.

    Raises
    ------
    aspecd.plotting.MissingSaverError
        Raised when no saver is provided when trying to save

    """

    def __init__(self):
        # Name defaults always to the full class name, don't change!
        self.name = aspecd.utils.full_class_name(self)
        self.parameters = dict()
        self.properties = PlotProperties()
        self.description = 'Abstract plotting step'
        self.figure = None
        self.axes = None
        self.filename = ''
        self.caption = Caption()

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
        self._create_figure_and_axes()
        self._create_plot()
        self.properties.apply(plotter=self)

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

    def _create_figure_and_axes(self):
        """Create figure and axes and assign to attributes.

        Figure and axes will only be created upon calling the method
        :meth:`plot`. If you need to change the way figure and axes are
        created, override this method.

        In any case, figure and axes need to be assigned to the
        :attr:`figure` and :attr:`axes` properties of the plotter class.
        """
        mpl.interactive(False)  # Mac OS X: prevent a plot window from opening
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
        pass

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
        aspecd.plotting.MissingSaverError
            Raised if no Saver is provided as parameter.

        """
        if not saver:
            raise MissingSaverError
        saver.save(self)
        self.filename = saver.filename
        return saver

    @staticmethod
    def _create_axis_label_string(axis):
        """Create axis label conforming to conventions used in science

        This method is called automatically and indirectly by :meth:`plot`.

        If you ever need to change the appearance of your axes labels,
        override this method in a child class.
        """
        label = ''
        if axis.quantity:
            label = '$' + axis.quantity + '$' + ' / ' + axis.unit
        return label


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
    aspecd.plotting.MissingDatasetError
        Raised when no dataset exists to act on

    aspecd.plotting.PlotNotApplicableToDatasetError
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
        aspecd.plotting.PlotNotApplicableToDatasetError
            Raised when plotting is not applicable to dataset
        aspecd.plotting.MissingDatasetError
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
        history_record : :class:`aspecd.plotting.PlotHistoryRecord`
            history record for plotting step

        """
        history_record = PlotHistoryRecord(package=self.dataset.package_name)
        history_record.plot = SinglePlotRecord(plotter=self)
        history_record.plot.preprocessing = copy.deepcopy(
            self.dataset.history)
        return history_record

    def _assign_dataset(self, dataset):
        if not dataset:
            if not self.dataset:
                raise MissingDatasetError
        else:
            self.dataset = dataset

    def _call_from_dataset(self, from_dataset):
        if not from_dataset:
            self.dataset.plot(self)
        else:
            self._check_applicability()
            super().plot()
            self._set_axes_labels()

    def _check_applicability(self):
        if not self.applicable(self.dataset):
            raise PlotNotApplicableToDatasetError

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

    Raises
    ------
    TypeError
        Raised when wrong plot type is set

    """

    def __init__(self):
        super().__init__()
        self.description = '1D plotting step for single dataset'
        self.properties = SinglePlot1DProperties()
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
        aspecd.plotting.TypeError
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
        self.drawing, = plot_function(self.dataset.data.axes[0].values,
                                      self.dataset.data.data)

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
    """2D plots of single datasets.

    Convenience class taking care of 2D plots of single datasets. The type
    of plot can be set in its :attr:`aspecd.plotting.SinglePlotter2D.type`
    attribute. Allowed types are stored in the
    :attr:`aspecd.plotting.SinglePlotter2D.allowed_types` attribute.

    Quite a number of properties for figure, axes, and line can be set
    using the :attr:`aspecd.plotting.SinglePlotter.properties` attribute.
    For details, see the documentation of its respective class,
    :class:`aspecd.plotting.SinglePlotProperties`.

    To perform the plot, call the :meth:`plot` method of the dataset the plot
    should be performed for, and provide a reference to the actual plotter
    object to it.

    Raises
    ------
    TypeError
        Raised when wrong plot type is set

    """

    def __init__(self):
        super().__init__()
        self.description = '2D plotting step for single dataset'
        self._type = 'imshow'
        self._allowed_types = ['contour', 'contourf', 'imshow', 'pcolor',
                               'pcolormesh']

    @property
    def type(self):
        """
        Get or set the plot type.

        Types need to be methods of the :class:`matplotlib.axes.Axes` class.

        Allowed plot types are stored in the
        :attr:`aspecd.plotting.SinglePlotter2D.allowed_types` attribute.

        Default: 'plot'

        Raises
        ------
        aspecd.plotting.TypeError
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
        """
        Create actual plot

        .. todo::
            Handle axes appropriately, depending on plot type.

        """
        plot_function = getattr(self.axes, self.type)
        self.drawing = plot_function(self.dataset.data.data)


class MultiPlotter(Plotter):
    """Base class for plots of multiple datasets.

    Each class actually plotting data of multiple dataset should inherit from
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
    aspecd.plotting.MissingDatasetError
        Raised when no dataset exists to act on
    aspecd.plotting.PlotNotApplicableToDatasetError
        Raised when processing step is not applicable to dataset

    """

    def __init__(self):
        super().__init__()
        self.properties = MultiPlotProperties()
        self.datasets = []
        self.description = 'Abstract plotting step for multiple dataset'
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
        aspecd.plotting.PlotNotApplicableToDatasetError
            Raised when plotting is not applicable to at least one of the
            datasets listed in :attr:`datasets`
        aspecd.plotting.MissingDatasetError
            Raised when no datasets exist to act on

        """
        if not self.datasets:
            raise MissingDatasetError
        if not all([self.applicable(dataset) for dataset in self.datasets]):
            raise PlotNotApplicableToDatasetError('Plot not applicable to one '
                                                  'or more datasets')
        super().plot()
        self._set_axes_labels()

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
        else:
            ylabel = ''
        self.axes.set_xlabel(xlabel)
        self.axes.set_ylabel(ylabel)


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
    aspecd.plotting.MissingFilenameError
        Raised if no filename is provided for saver.
    aspecd.plotting.MissingPlotError
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
        aspecd.plotting.MissingFilenameError
            Raised if no filename is provided for saver.
        aspecd.plotting.MissingPlotError
            Raised if no plot is provided to act upon.

        """
        if not self.filename:
            raise MissingFilenameError
        if not plotter:
            if self.plotter:
                self.plotter.save(self)
            else:
                raise MissingPlotError
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


class PlotRecord:
    """Base class for records storing information about a plot.

    For reproducibility of plots performed on either a single dataset or
    multiple datasets, information for each plot needs to be collected that
    suffices to reproduce the plot. This is what a PlotRecord is good for.

    All information will usually be obtained from a plotter object, either
    by instantiating a PlotRecord object providing a plotter object,
    or by calling :meth:`from_plotter` on a PlotRecord object.

    Subclasses for :obj:`aspecd.plotting.SinglePlotter` and
    :obj:`aspecd.plotting.MultiPlotter` objects are available, namely
    :class:`aspecd.plotting.SinglePlotRecord` and
    :class:`aspecd.plotting.MultiPlotRecord`.

    Attributes
    ----------
    name : :class:`str`
        Name of the plotter.

        Defaults to the plotter class name and shall never be set manually.
    description : :class:`str`
        Short description of the plot
    parameters : :class:`dict`
        All parameters necessary for the plot, implicit and explicit
    filename : :class:`str`
        Name of the file the plot has been/should be saved to


    Parameters
    ----------
    plotter : :obj:`aspecd.plotting.Plotter`
        Plotter object to obtain information from

    Raises
    ------
    aspecd.plotting.MissingPlotterError
        Raised if no plotter is provided.

    """

    def __init__(self, plotter=None):
        self.name = ''
        self.description = ''
        self.parameters = dict()
        self.filename = ''
        if plotter:
            self.from_plotter(plotter=plotter)

    def from_plotter(self, plotter=None):
        """Obtain information from plotter.

        Parameters
        ----------
        plotter : :obj:`aspecd.plotting.Plotter`
        Plotter object to obtain information from

        Raises
        ------
        aspecd.plotting.MissingPlotterError
            Raised if no plotter is provided.

        """
        if not plotter:
            raise MissingPlotterError
        self.name = plotter.name
        self.description = plotter.description
        self.parameters = plotter.parameters
        self.filename = plotter.filename


class SinglePlotRecord(PlotRecord):
    """Record for SinglePlotter objects.

    When plotting data of a single dataset, classes derived from
    :class:`aspecd.plotting.SinglePlotter` will be used. The information
    obtained from these plotters will be stored in a SinglePlotRecord object.

    Attributes
    ----------
    preprocessing : :class:`list`
        List of processing steps

        The actual processing steps are objects of the class
        :class:`aspecd.processing.ProcessingStepRecord`.

    Parameters
    ----------
    plotter : :obj:`aspecd.plotting.Plotter`
        Plotter object to obtain information from

    """

    def __init__(self, plotter=None):
        self.preprocessing = list()
        super().__init__(plotter=plotter)


class MultiPlotRecord(PlotRecord):
    """Record for MultiPlotter objects.

    When plotting data of multiple datasets, classes derived from
    :class:`aspecd.plotting.MultiPlotter` will be used. The information
    obtained from these plotters will be stored in a MultiPlotRecord object.

    Attributes
    ----------
    datasets : :class:`list`
        List of datasets whose data appear in the plot.

    Parameters
    ----------
    plotter : :obj:`aspecd.plotting.Plotter`
        Plotter object to obtain information from

    """

    def __init__(self, plotter=None):
        self.datasets = list()
        super().__init__(plotter=plotter)


class PlotHistoryRecord(aspecd.dataset.HistoryRecord):
    """History record for plots of datasets.

    Attributes
    ----------
    plot : :class:`aspecd.plotting.SinglePlotRecord`
        Plot the history is saved for

    package : :class:`str`
        Name of package the hstory record gets recorded for

        Prerequisite for reproducibility, gets stored in the
        :attr:`aspecd.dataset.HistoryRecord.sysinfo` attribute.
        Will usually be provided automatically by the dataset.

    """

    def __init__(self, package=''):
        super().__init__(package=package)
        self.plot = aspecd.plotting.SinglePlotRecord()


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
        line_properties.

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

    Raises
    ------
    aspecd.plotting.MissingPlotterError
        Raised if no plotter is provided.

    """

    def __init__(self):
        super().__init__()
        self.figure = FigureProperties()

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
        aspecd.plotting.MissingPlotterError
            Raised if no plotter is provided.

        """
        if not plotter:
            raise MissingPlotterError
        self.figure.apply(figure=plotter.figure)


class SinglePlotProperties(PlotProperties):
    """
    Properties of a single plot, defining its appearance.

    Attributes
    ----------
    axes : :class:`aspecd.plotting.AxisProperties`
        Properties of the axes.

    drawing : :class:`aspecd.plotting.DrawingProperties`
        Properties of the line within a plot

    Raises
    ------
    aspecd.plotting.MissingPlotterError
        Raised if no plotter is provided.

    """

    def __init__(self):
        super().__init__()
        self.axes = AxisProperties()
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
        aspecd.plotting.MissingPlotterError
            Raised if no plotter is provided.

        """
        super().apply(plotter=plotter)
        self.axes.apply(axis=plotter.axes)
        if plotter.drawing:
            self.drawing.apply(drawing=plotter.drawing)


class SinglePlot1DProperties(SinglePlotProperties):
    """
    Properties of a 1D single plot, defining its appearance.

    Attributes
    ----------
    drawing : :class:`aspecd.plotting.LineProperties`
        Properties of the line within a plot

    Raises
    ------
    aspecd.plotting.MissingPlotterError
        Raised if no plotter is provided.

    """

    def __init__(self):
        super().__init__()
        self.drawing = LineProperties()


class MultiPlotProperties(PlotProperties):
    """
    Properties of a multiplot, defining its appearance.

    Attributes
    ----------
    axes : :class:`aspecd.plotting.AxisProperties`
        Properties of the axes.

    legend : :class:`aspecd.plotting.LegendProperties`
        Properties of the legend.

    drawings : :class:`list`
        Properties of the lines within a plot.

        Each element is a :obj:`aspecd.plotting.LineProperties` object

    Raises
    ------
    aspecd.plotting.MissingPlotterError
        Raised if no plotter is provided.

    """

    def __init__(self):
        super().__init__()
        self.axes = AxisProperties()
        self.legend = LegendProperties()
        self.drawings = []

    def apply(self, plotter=None):
        """
        Apply properties to plot.

        Parameters
        ----------
        plotter: :class:`aspecd.plotting.MultiPlotter`
            Plotter the properties should be applied to.

        Raises
        ------
        aspecd.plotting.MissingPlotterError
            Raised if no plotter is provided.

        """
        super().apply(plotter=plotter)
        self.axes.apply(axis=plotter.axes)
        if hasattr(plotter, 'legend'):
            self.legend.apply(legend=plotter.legend)


class FigureProperties(aspecd.utils.Properties):
    """
    Properties of a figure of a plot, i.e., the most general aspects.

    Basically, the attributes are a subset of what :mod:`matplotlib` defines
    for :obj:`matplotlib.figure.Figure` objects.

    Attributes
    ----------
    figsize: :class:`tuple`
        Figure dimension (width, height) in inches.

        2-tuple of floats

    dpi: :class:`float`
        Dots per inch.

    Raises
    ------
    aspecd.plotting.MissingFigureError
        Raised if no figure is provided.

    """

    def __init__(self):
        super().__init__()
        self.figsize = (6.4, 4.8)
        self.dpi = 100.0

    def apply(self, figure=None):
        """
        Apply properties to figure.

        Parameters
        ----------
        figure: :class:`matplotlib.figure.Figure`
            Plotter the properties should be applied to.

        Raises
        ------
        aspecd.plotting.MissingFigureError
            Raised if no figure is provided.

        """
        if not figure:
            raise MissingFigureError
        for prop in self.get_properties():
            setattr(figure, prop, getattr(self, prop))


class AxisProperties(aspecd.utils.Properties):
    """
    Properties of an axis of a plot.

    Basically, the attributes are a subset of what :mod:`matplotlib` defines
    for :obj:`matplotlib.axes.Axes` objects.

    .. todo::
        How to deal with at least two axes per figure, i.e. x and y axis,
        whereas matplotlib handles the overall axes as one object?

        How about multiple separate axes within a figure window?

    Attributes
    ----------
    aspect: {'auto', 'equal'} or num
        aspect of the axis scaling, i.e. the ratio of y-unit to x-unit

    facecolor: color
        facecolor of the Axes

    xlabel: :class:`str`
        label for the x-axis

    xlim: :class:`list`
        x-axis view limits, two floats

    xscale: :class:`str`
        x-axis scale

        possible values: "linear", "log", "symlog", "logit"

    xticklabels: :class:`list`
        x-tick labels: list of string labels

    xticks:
        y ticks with list of ticks

    ylabel: :class:`str`
        label for the y-axis

    ylim: :class:`list`
        y-axis view limits, two floats

    yscale: :class:`str`
        y-axis scale

        possible values: "linear", "log", "symlog", "logit"

    yticklabels: :class:`list`
        y-tick labels: list of string labels

    yticks:
        y ticks with list of ticks

    Raises
    ------
    aspecd.plotting.MissingAxisError
        Raised if no axis is provided.

    """

    def __init__(self):
        super().__init__()
        self.aspect = 'auto'
        self.facecolor = None
        self.xlabel = ''
        self.xlim = []
        self.xscale = 'linear'
        self.xticklabels = None
        self.xticks = None
        self.ylabel = ''
        self.ylim = []
        self.yscale = 'linear'
        self.yticklabels = None
        self.yticks = None

    def apply(self, axis=None):
        """
        Apply settable properties to axis.

        Only properties that are not None or empty will be set, in order to
        prevent problems. The underlying method used to set the axis
        properties is :meth:`matplotlib.axes.Axes.update`.

        Parameters
        ----------
        axis: :class:`matplotlib.axes.Axes`
            axis to set properties for

        Raises
        ------
        aspecd.plotting.MissingAxisError
            Raised if no axis is provided.

        """
        if not axis:
            raise MissingAxisError
        axis.update(self._get_settable_properties())

    def _get_settable_properties(self):
        """
        Return properties that can be applied to an axis.

        Properties that are either None or empty often cause problems.
        Therefore, the properties of
        :class:`aspecd.plotting.AxisProperties` are reduced accordingly to
        those properties that are neither None nor empty.

        Returns
        -------
        properties: :class:`dict`
            Properties that are neither None nor empty

        """
        all_properties = self.to_dict()
        properties = dict()
        for prop in all_properties:
            if all_properties[prop]:
                properties[prop] = all_properties[prop]
        return properties


class LegendProperties(aspecd.utils.Properties):
    """
    Properties of a legend of a plot, i.e., the most general aspects.

    Basically, the attributes are a subset of what :mod:`matplotlib` defines
    for :obj:`matplotlib.legend.Legend` objects.

    Attributes
    ----------
    loc: :class:`str`
        Location of the legend

        For possible values, see :class:`matplotlib.legend.Legend`

    Raises
    ------
    aspecd.plotting.MissingLegendError
        Raised if no legend is provided.

    """

    def __init__(self):
        super().__init__()
        self.loc = 'best'

    def apply(self, legend=None):
        """
        Apply properties to legend.

        Parameters
        ----------
        legend: :class:`matplotlib.legend.Legend`
            Plotter the properties should be applied to.

        Raises
        ------
        aspecd.plotting.MissingFigureError
            Raised if no figure is provided.

        """
        if not legend:
            raise MissingLegendError
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
    aspecd.plotting.MissingDrawingError
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
        aspecd.plotting.MissingDrawingError
            Raised if no line is provided.

        """
        if not drawing:
            raise MissingDrawingError
        for prop in self.get_properties():
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
    aspecd.plotting.MissingDrawingError
        Raised if no line is provided.

    """

    def __init__(self):
        super().__init__()
        self.color = None
        self.drawstyle = 'default'
        self.linestyle = 'solid'
        self.linewidth = 1.5
        self.marker = ''
