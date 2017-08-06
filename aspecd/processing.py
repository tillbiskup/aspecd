"""Processing."""


class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class ProcessingNotApplicableToDataset(Error):
    """Exception raised trying to undo with empty history

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message=''):
        self.message = message


class ProcessingStep:
    def __init__(self):
        self.undoable = False
        # Name defaults always to the class name, don't change!
        self.name = self.__class__.__name__
        # All parameters, implicit and explicit
        self.parameters = dict()
        # Short description, to be set in class definition
        self.description = 'Abstract processing step'
        # User-supplied comment describing intent, purpose, reason, ...
        self.comment = ''

    def process(self, dataset):
        """
        Perform the actual processing step on the given dataset.

        This method should always only be called by the dataset itself and its
        corresponding "processing" method, as otherwise no history would get
        written.

        The actual processing step should be coded within the private method
        "_perform_task". Besides that, the applicability of the processing step
        to the given dataset will be checked automatically and the parameters
        will be sanitised.

        :param dataset:
        :return:
        """
        if not self._applicable(dataset):
            raise ProcessingNotApplicableToDataset
        self._sanitise_parameters(dataset)
        self._perform_task(dataset)

    @staticmethod
    def _applicable(dataset):
        return True

    def _sanitise_parameters(self, dataset):
        pass

    def _perform_task(self, dataset):
        pass
