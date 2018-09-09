"""Plotting."""

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
        self.message = message


class PlotNotApplicableToDatasetError(Error):
    """Exception raised when processing step is not applicable to dataset

    Attributes
    ----------
    message : `str`
        explanation of the error
    """

    def __init__(self, message=''):
        self.message = message


class MissingSaverError(Error):
    """Exception raised when no saver is provided.

    Attributes
    ----------
    message : `str`
        explanation of the error
    """

    def __init__(self, message=''):
        self.message = message


class MissingFilenameError(Error):
    """Exception raised when no filename was provided

    Attributes
    ----------
    message : `str`
        explanation of the error
    """

    def __init__(self, message=''):
        self.message = message


class MissingPlotError(Error):
    """Exception raised when no plot exists to save.

    Attributes
    ----------
    message : `str`
        explanation of the error
    """

    def __init__(self, message=''):
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
        # All parameters, implicit and explicit
        self.parameters = dict()
        # Short description, to be set in class definition
        self.description = 'Abstract plotting step'
        # Reference to the dataset the plot should be performed for
        self.dataset = None
        # Reference to figure object (:class:`matplotlib.figure.Figure`)
        self.figure = None

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
        self._create_plot()

    @staticmethod
    def applicable(dataset):
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

    def _create_plot(self):
        """Perform the actual plotting of the data of the dataset.

        The implementation of the actual plotting goes in here in all
        classes inheriting from Plotter. This method is automatically
        called by :meth:`plot` after some background checks.

        The reference to the figure object should be stored in :attr:`figure`.
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

    def __init__(self):
        self.filename = None
        self.parameters = dict()
        self.plotter = None
        pass

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
        """
        pass
