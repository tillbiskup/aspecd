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


class Plotter:
    """Base class for plots.

    Each class actually plotting data of a dataset should inherit from this
    class. Furthermore, all parameters, implicit and explicit, necessary to
    perform the plot, should eventually be stored in the property
    "self.parameters" (currently a dictionary).

    To perform the plot, call the :func:`plot` method of the dataset the plot
    should be performed for, and provide a reference to the actual plotter
    object to it.

    Further things that need to be changed upon inheriting from this class
    are the string stored in ``description``, being basically a one-liner.

    The actual implementation of the plotting is done in the private method
    :func:`_perform_plot` that in turn gets called by :func:`plot`
    which is called by the :func:`aspecd.dataset.Dataset.plot` method of the
    dataset object.

    Raises
    ------
    MissingDatasetError
        Raised when no dataset exists to act on
    PlotNotApplicableToDatasetError
        Raised when processing step is not applicable to dataset
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

    def plot(self, dataset=None):
        """Perform the actual plotting on the given dataset.

        If no dataset is provided at method call, but is set as property in the
        Plotter object, the :func:`aspecd.dataset.Dataset.plot` method of the
        dataset will be called and thus the history written.

        If no dataset is provided at method call nor as property in the object,
        the method will raise a respective exception.

        The Dataset object always calls this method with the respective dataset
        as argument. Therefore, in this case setting the dataset property
        within the Plotter object is not necessary.

        The actual plotting should be implemented within the private
        method :func:`_create_plot`. Besides that, the applicability of the
        plotting to the given dataset will be checked automatically.

        Parameters
        ----------
        dataset : :class:`aspecd.dataset.Dataset`
            dataset to perform plot for

        Raises
        ------
        PlottingNotApplicableToDatasetError
            Raised when plotting is not applicable to dataset
        MissingDatasetError
            Raised when no dataset exists to act on
        """
        if not dataset:
            if self.dataset:
                self.dataset.plot()
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
        called by :func:`self.plot` after some background checks.
        """
        pass

    def save(self):
        """Save the plot to a file.

        .. todo::
            The actual way of how plots are saved has to be figured out, as
            well as the way this is implemented here.

            One way would be similar to the implementation of :func:`plot` with
            a private method doing all the special stuff. Somehow it would be
            nice as well to be able to apply a consistent styling from an
            external source of configuration--clearly future stuff to deal
            with.

            Another idea would be to postpone the actual saving to another
            class that can explicitly deal with all sorts of parameters and
            settings necessary for that.
        """
        pass
