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
    """Base class for processing steps.

    Each class actually performing a processing step should inherit from this
    class. Furthermore, all parameters, implicit and explicit, necessary to
    perform the processing step, should eventually be stored in the property
    "self.parameters" (currently a dictionary).

    To perform the processing step, call the "process" method of the dataset
    the processing should be applied to, and provide a reference to the
    actual processing_step object to it.

    Further things that need to be changed upon inheriting from this class
    are the string stored in "self.description", being basically a one-liner,
    and the flag "self.undoable" if necessary.

    The actual implementation of the processing step is done in the private
    method "self._perform_task()" that in turn gets called by "self.process()"
    which is called by the "process()" method of the dataset object.
    """

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
        """Check whether processing step is applicable to the given dataset.

        Returns "True" by default and needs to be implemented in classes
        inheriting from ProcessingStep according to their needs.
        """
        return True

    def _sanitise_parameters(self):
        """Ensure parameters provided for processing step are correct.

        Needs to be implemented in classes inheriting from ProcessingStep
        according to their needs. Most probably, you want to check for
        correct types of all parameters as well as values within sensible
        borders.
        """
        pass

    def _perform_task(self):
        """Perform the actual processing step on the dataset.

        The implementation of the actual processing goes in here in all
        classes inheriting from ProcessingStep. This method is automatically
        called by self.processing() after some background checks.
        """
        pass
