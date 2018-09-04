"""Processing."""


class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class ProcessingNotApplicableToDatasetError(Error):
    """Exception raised when processing step is not applicable to dataset

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message=''):
        self.message = message


class MissingDatasetError(Error):
    """Exception raised when no dataset exists to act on

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
        # Reference to the dataset the processing step should be performed on
        self.dataset = None

    def process(self, dataset=None):
        """Perform the actual processing step on the given dataset.

        If no dataset is provided at method call, but is set as property in the
        ProcessingStep object, the process method of the dataset will be called
        and thus the history written.

        If no dataset is provided at method call nor as property in the object,
        the method will raise a respective exception.

        The Dataset object always calls this method with the respective dataset
        as argument. Therefore, in this case setting the dataset property
        within the Processing object is not necessary.

        The actual processing step should be coded within the private method
        "_perform_task". Besides that, the applicability of the processing step
        to the given dataset will be checked automatically and the parameters
        will be sanitised.

        :param dataset:
        :return:
        """
        if not dataset:
            if self.dataset:
                self.dataset.process(self)
            else:
                raise MissingDatasetError
        else:
            self.dataset = dataset
        if not self._applicable(dataset):
            raise ProcessingNotApplicableToDatasetError
        self._sanitise_parameters()
        self._perform_task()

    @staticmethod
    def _applicable(dataset):
        return True

    def _sanitise_parameters(self):
        pass

    def _perform_task(self):
        pass
