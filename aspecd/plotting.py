"""Plotting: Graphical representations of data extracted from datasets."""

import matplotlib as mpl
import matplotlib.pyplot as plt

from aspecd import utils


class Error(Exception):
    """Base class for exceptions in this module."""

    pass


class MissingDatasetError(Error):
    """Exception raised when no dataset exists to act on

    Attributes
    ----------
    message : `str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class PlotNotApplicableToDatasetError(Error):
    """Exception raised when processing step is not applicable to dataset

    Attributes
    ----------
    message : `str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class MissingSaverError(Error):
    """Exception raised when no saver is provided.

    Attributes
    ----------
    message : `str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class MissingFilenameError(Error):
    """Exception raised when no filename was provided

    Attributes
    ----------
    message : `str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class MissingPlotError(Error):
    """Exception raised when no plot exists to save.

    Attributes
    ----------
    message : `str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class Plotter:
    """Base class for plots.

    Each class actually plotting data of a dataset should inherit from this
    class. Furthermore, all parameters, implicit and explicit, necessary to
    perform the plot, should eventually be stored in the property
    :attr:`parameters` (currently a dictionary).

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
    name : `str`
        Name of the plotter.

        Defaults always to the full class name, don't change!
    parameters : `dict`
        All parameters necessary for the plot, implicit and explicit
    description : `str`
        Short description, to be set in class definition
    dataset : :class:`aspecd.dataset.Dataset`
        Dataset the analysis step should be performed on
    figure : :class:`matplotlib.figure.Figure`
        Reference to figure object
    axes : :class:`matplotlib.axes.Axes`
        Reference to axes object used for actual plotting

    Raises
    ------
    MissingDatasetError
        Raised when no dataset exists to act on
    PlotNotApplicableToDatasetError
        Raised when processing step is not applicable to dataset
    MissingSaverError
        Raised when no saver is provided when trying to save

    """

    def __init__(self):
        # Name defaults always to the full class name, don't change!
        self.name = utils.full_class_name(self)
        self.parameters = dict()
        self.description = 'Abstract plotting step'
        self.dataset = None
        self.figure = None
        self.axes = None

    @property
    def fig(self):
        """Short hand for figure."""
        return self.figure

    @property
    def ax(self):
        """Short hand for axes."""
        return self.axes

    def plot(self, dataset=None):
        """Perform the actual plotting on the given dataset.

        If no dataset is provided at method call, but is set as property in the
        Plotter object, the :meth:`aspecd.dataset.Dataset.plot` method of the
        dataset will be called and thus the history written.

        If no dataset is provided at method call nor as property in the object,
        the method will raise a respective exception.

        The Dataset object always calls this method with the respective dataset
        as argument. Therefore, in this case setting the dataset property
        within the Plotter object is not necessary.

        The actual plotting should be implemented within the private
        method :meth:`_create_plot`. Besides that, the applicability of the
        plotting to the given dataset will be checked automatically.

        Parameters
        ----------
        dataset : :class:`aspecd.dataset.Dataset`
            dataset to perform plot for

        Raises
        ------
        PlotNotApplicableToDatasetError
            Raised when plotting is not applicable to dataset
        MissingDatasetError
            Raised when no dataset exists to act on

        """
        if not dataset:
            if self.dataset:
                self.dataset.plot(self)
            else:
                raise MissingDatasetError
        else:
            self.dataset = dataset
        if not self.applicable(self.dataset):
            raise PlotNotApplicableToDatasetError
        self._create_figure_and_axes()
        self._create_plot()

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
        applicable : `bool`
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
        """Perform the actual plotting of the data of the dataset.

        The implementation of the actual plotting goes in here in all
        classes inheriting from Plotter. This method is automatically
        called by :meth:`plot` after some background checks.

        The reference to the figure object is stored in :attr:`figure`. By
        default, the backend is set to non-interactive, and to actually
        display the figure, you would need to call :meth:`show()` on the
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
        MissingSaverError
            Raised if no Saver is provided as parameter.

        """
        if not saver:
            raise MissingSaverError
        saver.save(self)
        return saver


class Saver:
    """Base class for saving plots.

    Raises
    ------
    MissingFilenameError
        Raised if no filename is provided for saver.
    MissingPlotError
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

        The actual saving should be implemented within the private method
        :meth:`_save_plot`.

        Parameters
        ----------
        plotter : `aspecd.plotting.Plotter`
            plot to be saved

        Raises
        ------
        MissingFilenameError
            Raised if no filename is provided for saver.
        MissingPlotError
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
        pass
