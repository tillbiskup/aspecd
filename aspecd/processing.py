"""Data processing functionality.

Key to reproducible science is automatic documentation of each processing
step applied to the data of a dataset. Such a processing step each is
self-contained, meaning it contains every necessary information to perform
the processing task on a given dataset.

Each real processing step should inherit from
:class:`aspecd.processing.ProcessingStep` as documented there.

"""

from aspecd import utils


class Error(Exception):
    """Base class for exceptions in this module."""

    pass


class ProcessingNotApplicableToDatasetError(Error):
    """Exception raised when processing step is not applicable to dataset

    Attributes
    ----------
    message : `str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


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


class MissingProcessingStepError(Error):
    """Exception raised when no processing step exists to act on

    Attributes
    ----------
    message : `str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class ProcessingStep:
    """Base class for processing steps.

    Each class actually performing a processing step should inherit from this
    class. Furthermore, all parameters, implicit and explicit, necessary to
    perform the processing step, should eventually be stored in the property
    "self.parameters" (currently a dictionary).

    To perform the processing step, call the :func:`process` method of the
    dataset the processing should be applied to, and provide a reference to the
    actual processing_step object to it.

    Further things that need to be changed upon inheriting from this class
    are the string stored in ``description``, being basically a one-liner,
    and the flag ``undoable`` if necessary.

    The actual implementation of the processing step is done in the private
    method :func:`_perform_task` that in turn gets called by :func:`process`
    which is called by the :func:`aspecd.dataset.Dataset.process` method of the
    dataset object.

    Attributes
    ----------
    undoable : `bool`
        Can this processing step be reverted?
    name : `str`
        Name of the analysis step.

        Defaults to the lower-case class name, don't change!
    parameters : `dict`
        Parameters required for performing the processing step

        All parameters, implicit and explicit.
    info : `dict`
        Additional information used, e.g., in a report (derived values, ...)
    description : `str`
        Short description, to be set in class definition
    comment : `str`
        User-supplied comment describing intent, purpose, reason, ...
    dataset : :class:`aspecd.dataset.Dataset`
        Dataset the analysis step should be performed on

    Raises
    ------
    ProcessingNotApplicableToDatasetError
        Raised when processing step is not applicable to dataset
    MissingDatasetError
        Raised when no dataset exists to act on

    """

    def __init__(self):
        self.undoable = False
        # Name defaults always to the full class name, don't change!
        self.name = utils.full_class_name(self)
        # All parameters, implicit and explicit
        self.parameters = dict()
        # Additional information used, e.g., in a report (derived values, ...)
        self.info = dict()
        # Short description, to be set in class definition
        self.description = 'Abstract processing step'
        # User-supplied comment describing intent, purpose, reason, ...
        self.comment = ''
        # Reference to the dataset the processing step should be performed on
        self.dataset = None

    def process(self, dataset=None):
        """Perform the actual processing step on the given dataset.

        If no dataset is provided at method call, but is set as property in the
        ProcessingStep object, the :func:`aspecd.dataset.Dataset.process`
        method of the dataset will be called and thus the history written.

        If no dataset is provided at method call nor as property in the object,
        the method will raise a respective exception.

        The Dataset object always calls this method with the respective dataset
        as argument. Therefore, in this case setting the dataset property
        within the ProcessingStep object is not necessary.

        The actual processing step should be implemented within the private
        method :func:`_perform_task`. Besides that, the applicability of the
        processing step to the given dataset will be checked automatically and
        the parameters will be sanitised.

        Parameters
        ----------
        dataset : :class:`aspecd.dataset.Dataset`
            dataset to apply processing step to

        Returns
        -------
        dataset : :class:`aspecd.dataset.Dataset`
            dataset the processing step has been applied to

        Raises
        ------
        ProcessingNotApplicableToDatasetError
            Raised when processing step is not applicable to dataset
        MissingDatasetError
            Raised when no dataset exists to act on

        """
        if not dataset:
            if self.dataset:
                self.dataset.process(self)
            else:
                raise MissingDatasetError
        else:
            self.dataset = dataset
        if not self.applicable(self.dataset):
            raise ProcessingNotApplicableToDatasetError
        self._sanitise_parameters()
        self._perform_task()
        return self.dataset

    @staticmethod
    def applicable(dataset):
        """Check whether processing step is applicable to the given dataset.

        Returns `True` by default and needs to be implemented in classes
        inheriting from ProcessingStep according to their needs.

        Returns
        -------
        applicable : `bool`
            `True` if successful, `False` otherwise.

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
        called by :func:`self.processing` after some background checks.

        """
        pass


class ProcessingStepRecord:
    """Base class for processing step records stored in the dataset history.

    The history of a :class:`aspecd.dataset.Dataset` should *not* contain
    references to :class:`aspecd.processing.ProcessingStep` objects, but rather
    records that contain all necessary information to create the respective
    objects inherited from :class:`aspecd.processing.ProcessingStep`. One
    reason for this is simply that we want to import datasets containing
    processing steps in their history for which no corresponding processing
    class exists in the current installation of the application.

    .. note::
        Each history entry in a dataset stores the processing as a
        :class:`aspecd.processing.ProcessingStepRecord`, even in applications
        inheriting from the ASpecD framework. Hence, subclassing of this class
        should normally not be necessary.

    Attributes
    ----------
    undoable : `bool`
        Can this processing step be reverted?
    description : `str`
        Short description, to be set in class definition
    parameters : `dict`
        Parameters required for performing the processing step

        All parameters, implicit and explicit.
    comment : `str`
        User-supplied comment describing intent, purpose, reason, ...
    class_name : `str`
        Fully qualified name of the class of the corresponding processing step

    Parameters
    ----------
    processing_step : :class:`aspecd.processing.ProcessingStep`
        Processing step the record should be created for.

    Raises
    ------
    MissingProcessingStepError
        Raised when no processing step exists to act on

    """

    def __init__(self, processing_step=None):
        if not processing_step:
            raise MissingProcessingStepError
        self.undoable = False
        self.description = ''
        self.parameters = dict()
        self.comment = ''
        self.class_name = ''
        self._copy_fields_from_processing_step(processing_step)

    def _copy_fields_from_processing_step(self, processing_step):
        self.description = processing_step.description
        self.parameters = processing_step.parameters
        self.undoable = processing_step.undoable
        self.comment = processing_step.comment
        self.class_name = processing_step.name

    def create_processing_step(self):
        """Return a processing step object.

        Returns
        -------
        processing_step : :class:`aspecd.processing.ProcessingStep`
            actual processing step object that can be used for processing,
            e.g., in context of undo/redo

        """
        processing_step = utils.object_from_class_name(self.class_name)
        processing_step.undoable = self.undoable
        processing_step.parameters = self.parameters
        processing_step.description = self.description
        processing_step.comment = self.comment
        return processing_step
