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

        Returns
        -------
        applicable : `bool`
            `True` if successful, `False` otherwise.
        """
        return True

    def _create_plot(self):
        pass

    def save(self):
        pass
