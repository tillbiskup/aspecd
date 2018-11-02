"""Analysis."""


import copy

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


class AnalysisStep:
    """
    Base class for analysis steps.

    Attributes
    ----------
    name : `str`
        Name of the analysis step.

        Defaults to the lower-case class name, don't change!
    parameters : `dict`
        Parameters required for performing the analysis step

        All parameters, implicit and explicit.
    results : `dict`
        Results of the analysis step
    preprocessing : `list`
        List of necessary preprocessing steps to perform the analysis.
    description : `str`
        Short description, to be set in class definition
    comment : `str`
        User-supplied comment describing intent, purpose, reason, ...
    dataset : :class:`aspecd.dataset.Dataset`
        Dataset the analysis step should be performed on

    Raises
    ------
    MissingDatasetError
        Raised when no dataset exists to act on

    """

    def __init__(self):
        # Name defaults always to the full class name, don't change!
        self.name = utils.full_class_name(self)
        # All parameters, implicit and explicit
        self.parameters = dict()
        # Results of the analysis step
        self.results = dict()
        # List of necessary preprocessing steps to perform analysis
        self.preprocessing = []
        # Short description, to be set in class definition
        self.description = 'Abstract analysis step'
        # User-supplied comment describing intent, purpose, reason, ...
        self.comment = ''
        # Reference to the dataset the analysis step should be performed on
        self.dataset = None

    def analyse(self, dataset=None):
        """Perform the actual analysis step on the given dataset.

        If no dataset is provided at method call, but is set as property in the
        AnalysisStep object, the process method of the dataset will be called
        and thus the history written.

        If no dataset is provided at method call nor as property in the object,
        the method will raise a respective exception.

        The Dataset object always call this method with the respective dataset
        as argument. Therefore, in this case setting the dataset property
        within the Analysis object is not necessary.

        Parameters
        ----------
        dataset : :class:`aspecd.dataset.Dataset`
            dataset to perform analysis for

        """
        if not dataset:
            if self.dataset:
                self.dataset.analyse(self)
            else:
                raise MissingDatasetError

    def analyze(self, dataset=None):
        """Perform the actual analysis step on the given dataset.

        Same method as self.analyse, but for those preferring AE over BE

        """
        self.analyse(dataset)

    def add_preprocessing_step(self, processingstep=None):
        """
        Add a preprocessing step to the internal list.

        Some analyses need some preprocessing of the data. These
        preprocessing steps are contained in the ``preprocessing``
        attribute.

        Parameters
        ----------
        processingstep : :class:`aspecd.processing.ProcessingStep`
            processing step to be added to the list of preprocessing steps

        """
        # Important: Need a copy, not the reference to the original object
        processingstep = copy.deepcopy(processingstep)
        self.preprocessing.append(processingstep)
