"""
Data processing functionality.

Key to reproducible science is automatic documentation of each processing
step applied to the data of a dataset. Such a processing step each is
self-contained, meaning it contains every necessary information to perform
the processing task on a given dataset.

Processing steps, in contrast to analysis steps (see :mod:`aspecd.analysis`
for details), not only operate on data of a :class:`aspecd.dataset.Dataset`,
but change its data. The information necessary to reproduce each processing
step gets added to the :attr:`aspecd.dataset.Dataset.history` attribute of a
dataset.

Each real processing step should inherit from
:class:`aspecd.processing.ProcessingStep` as documented there. Furthermore,
each processing step should be contained in one module named "processing".
This allows for easy automation and replay of processing steps, particularly
in context of recipe-driven data analysis (for details, see the
:mod:`aspecd.tasks` module).

"""

import aspecd.utils
import aspecd.dataset


class Error(Exception):
    """Base class for exceptions in this module."""

    pass


class ProcessingNotApplicableToDatasetError(Error):
    """Exception raised when processing step is not applicable to dataset

    Attributes
    ----------
    message : :class:`str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class MissingDatasetError(Error):
    """Exception raised when no dataset exists to act on

    Attributes
    ----------
    message : :class:`str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class MissingProcessingStepError(Error):
    """Exception raised when no processing step exists to act on

    Attributes
    ----------
    message : :class:`str`
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

    To perform the processing step, call the :meth:`process` method of the
    dataset the processing should be applied to, and provide a reference to the
    actual processing_step object to it.

    Further things that need to be changed upon inheriting from this class
    are the string stored in ``description``, being basically a one-liner,
    and the flag ``undoable`` if necessary.

    The actual implementation of the processing step is done in the private
    method :meth:`_perform_task` that in turn gets called by :meth:`process`
    which is called by the :meth:`aspecd.dataset.Dataset.process` method of the
    dataset object.

    Attributes
    ----------
    undoable : :class:`bool`
        Can this processing step be reverted?
    name : :class:`str`
        Name of the analysis step.

        Defaults to the lower-case class name, don't change!
    parameters : :class:`dict`
        Parameters required for performing the processing step

        All parameters, implicit and explicit.
    info : :class:`dict`
        Additional information used, e.g., in a report (derived values, ...)
    description : :class:`str`
        Short description, to be set in class definition
    comment : :class:`str`
        User-supplied comment describing intent, purpose, reason, ...
    dataset : :class:`aspecd.dataset.Dataset`
        Dataset the analysis step should be performed on

    Raises
    ------
    aspecd.processing.ProcessingNotApplicableToDatasetError
        Raised when processing step is not applicable to dataset
    aspecd.processing.MissingDatasetError
        Raised when no dataset exists to act on

    """

    def __init__(self):
        self.undoable = False
        self.name = aspecd.utils.full_class_name(self)
        self.parameters = dict()
        self.info = dict()
        self.description = 'Abstract processing step'
        self.comment = ''
        self.dataset = None

    def process(self, dataset=None, from_dataset=False):
        """Perform the actual processing step on the given dataset.

        If no dataset is provided at method call, but is set as property in
        the ProcessingStep object, the :meth:`aspecd.dataset.Dataset.process`
        method of the dataset will be called and thus the history written.

        If no dataset is provided at method call nor as property in the
        object, the method will raise a respective exception.

        The :obj:`aspecd.dataset.Dataset` object always call this method with
        the respective dataset as argument. Therefore, in this case setting
        the dataset property within the
        :obj:`aspecd.processing.ProcessingStep` object is not necessary.

        The actual processing step should be implemented within the non-public
        method :meth:`_perform_task`. Besides that, the applicability of the
        processing step to the given dataset will be checked automatically and
        the parameters will be sanitised by calling the non-public method
        :meth:`_sanitise_parameters`.

        Parameters
        ----------
        dataset : :class:`aspecd.dataset.Dataset`
            dataset to apply processing step to

        from_dataset : `boolean`
            whether we are called from within a dataset

            Defaults to "False" and shall never be set manually.

        Returns
        -------
        dataset : :class:`aspecd.dataset.Dataset`
            dataset the processing step has been applied to

        Raises
        ------
        aspecd.processing.ProcessingNotApplicableToDatasetError
            Raised when processing step is not applicable to dataset
        aspecd.processing.MissingDatasetError
            Raised when no dataset exists to act on

        """
        self._assign_dataset(dataset=dataset)
        self._call_from_dataset(from_dataset=from_dataset)
        return self.dataset

    def create_history_record(self):
        """
        Create history record to be added to the dataset.

        Usually, this method gets called from within the
        :meth:`aspecd.dataset.process` method of the
        :class:`aspecd.dataset.Dataset` class and ensures the history of
        each processing step to get written properly.

        Returns
        -------
        history_record : :class:`aspecd.processing.ProcessingHistoryRecord`
            history record for processing step

        """
        history_record = ProcessingHistoryRecord(
            package=self.dataset.package_name, processing_step=self)
        return history_record

    def _assign_dataset(self, dataset=None):
        if not dataset:
            if not self.dataset:
                raise MissingDatasetError
        else:
            self.dataset = dataset

    def _call_from_dataset(self, from_dataset=False):
        if not from_dataset:
            self.dataset.process(self)
        else:
            self._check_applicability()
            self._sanitise_parameters()
            self._perform_task()

    def _check_applicability(self):
        if not self.applicable(self.dataset):
            raise ProcessingNotApplicableToDatasetError

    # noinspection PyUnusedLocal
    @staticmethod
    def applicable(dataset):  # pylint: disable=unused-argument
        """Check whether processing step is applicable to the given dataset.

        Returns `True` by default and needs to be implemented in classes
        inheriting from ProcessingStep according to their needs.

        Returns
        -------
        applicable : :class:`bool`
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
        called by :meth:`self.processing` after some background checks.

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
    undoable : :class:`bool`
        Can this processing step be reverted?
    description : :class:`str`
        Short description, to be set in class definition
    parameters : :class:`dict`
        Parameters required for performing the processing step

        All parameters, implicit and explicit.
    comment : :class:`str`
        User-supplied comment describing intent, purpose, reason, ...
    class_name : :class:`str`
        Fully qualified name of the class of the corresponding processing step

    Parameters
    ----------
    processing_step : :class:`aspecd.processing.ProcessingStep`
        Processing step the record should be created for.

    Raises
    ------
    aspecd.processing.MissingProcessingStepError
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
        """Create a processing step object from the parameters stored.

        Returns
        -------
        processing_step : :class:`aspecd.processing.ProcessingStep`
            actual processing step object that can be used for processing,
            e.g., in context of undo/redo

        """
        processing_step = aspecd.utils.object_from_class_name(self.class_name)
        processing_step.undoable = self.undoable
        processing_step.parameters = self.parameters
        processing_step.description = self.description
        processing_step.comment = self.comment
        return processing_step


class ProcessingHistoryRecord(aspecd.dataset.HistoryRecord):
    """History record for processing steps on datasets.

    Attributes
    ----------
    processing : `aspecd.processing.ProcessingStepRecord`
        record of the processing step

    Parameters
    ----------
    processing_step : :class:`aspecd.processing.ProcessingStep`
        processing step the history is saved for

    package : :class:`str`
        Name of package the hstory record gets recorded for

        Prerequisite for reproducibility, gets stored in the
        :attr:`aspecd.dataset.HistoryRecord.sysinfo` attribute.
        Will usually be provided automatically by the dataset.

    """

    def __init__(self, processing_step=None, package=''):
        super().__init__(package=package)
        self.processing = ProcessingStepRecord(processing_step)

    @property
    def undoable(self):
        """Can this processing step be reverted?"""
        return self.processing.undoable

    def replay(self, dataset):
        """Replay the processing step saved in the history record.

        Parameters
        ----------
        dataset : :class:`aspecd.dataset.Dataset`
            dataset the processing step should be replayed to

        """
        processing_step = self.processing.create_processing_step()
        processing_step.process(dataset=dataset)
