"""Analysis."""


import copy


class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class MissingDatasetError(Error):
    """Exception raised when no dataset exists to act on

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message=''):
        self.message = message


class AnalysisStep:

    def __init__(self):
        # Name defaults always to the class name, don't change!
        self.name = self.__class__.__name__
        # All parameters, implicit and explicit
        self.parameters = dict()
        # Results of the analysis step
        self.results = dict()
        # List of necessary preprocessing steps to perform analysis
        self.preprocessing = []
        # Short description, to be set in class definition
        self.description = 'Abstract processing step'
        # User-supplied comment describing intent, purpose, reason, ...
        self.comment = ''
        # Reference to the dataset the analysis step should be performed on
        self.dataset = None

    def analyse(self, dataset=None):
        if not dataset:
            if self.dataset:
                self.dataset.analyse(self)
            else:
                raise MissingDatasetError

    def analyze(self, dataset):
        """Same method as self.analyse, but for those preferring AE over BE"""
        self.analyse(dataset)

    def add_preprocessing_step(self, processingstep):
        # Important: Need a copy, not the reference to the original object
        processingstep = copy.deepcopy(processingstep)
        self.preprocessing.append(processingstep)
