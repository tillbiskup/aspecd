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
import numpy as np

import aspecd.exceptions
import aspecd.history
import aspecd.utils


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

    .. admonition:: When is a processing step undoable?

        Sometimes, the question arises what distinguishes an undoable
        processing step from one that isn't, particularly in light of having
        the original data stored in the dataset.

        One simple case of a processing step that cannot easily be undone and
        *redone* afterwards (undo needs always to be thought in light of an
        inverting redo) is adding data of two datasets together. From the
        point of view of the single dataset, the other dataset is not
        accessible. Therefore, such a step is undoable (subtracting two
        datasets as well, of course).


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
        Dataset the processing step should be performed on

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
        history_record : :class:`aspecd.history.ProcessingHistoryRecord`
            history record for processing step

        """
        history_record = aspecd.history.ProcessingHistoryRecord(
            package=self.dataset.package_name, processing_step=self)
        return history_record

    def _assign_dataset(self, dataset=None):
        if not dataset:
            if not self.dataset:
                raise aspecd.exceptions.MissingDatasetError
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
            raise aspecd.exceptions.ProcessingNotApplicableToDatasetError

    # noinspection PyUnusedLocal
    @staticmethod
    def applicable(dataset):  # pylint: disable=unused-argument
        """Check whether processing step is applicable to the given dataset.

        Returns `True` by default and needs to be implemented in classes
        inheriting from ProcessingStep according to their needs.

        This is a static method that gets called automatically by each class
        inheriting from :class:`aspecd.processing.ProcessingStep`. Hence,
        if you need to override it in your own class, make the method static
        as well. An example of an implementation testing for two-dimensional
        data is given below::

            @staticmethod
            def applicable(dataset):
                return len(dataset.data.axes) == 3


        Parameters
        ----------
        dataset : :class:`aspecd.dataset.Dataset`
            dataset to check

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

    def _perform_task(self):
        """Perform the actual processing step on the dataset.

        The implementation of the actual processing goes in here in all
        classes inheriting from ProcessingStep. This method is automatically
        called by :meth:`self.processing` after some background checks.

        """


class Normalisation(ProcessingStep):
    """
    Normalise data.

    There are different kinds of normalising data:

    * maximum
    * minimum
    * amplitude
    * area

    You can set these kinds using the attribute :attr:`parameters["kind"]`.

    .. todo::
        Handle noisy data, at least for normalising to maximum, minimum,
        and amplitude.

    Attributes
    ----------
    parameters["kind"] : :class:`str`
        Kind of normalisation to use

        Valid values: "maximum", "minimum", "amplitude", "area"

        Note that the first three can be abbreviated, everything containing
        "max", "min", "amp" will be understood respectively.

        Defaults to "maximum"

    """

    def __init__(self):
        super().__init__()
        self.undoable = True
        self.description = 'Normalise data'
        self.parameters["kind"] = 'maximum'

    def _perform_task(self):
        if "max" in self.parameters["kind"].lower():
            self.dataset.data.data /= self.dataset.data.data.max()
        elif "min" in self.parameters["kind"].lower():
            self.dataset.data.data /= self.dataset.data.data.min()
        elif "amp" in self.parameters["kind"].lower():
            self.dataset.data.data /= (self.dataset.data.data.max() -
                                       self.dataset.data.data.min())
        elif "area" in self.parameters["kind"].lower():
            self.dataset.data.data /= np.sum(self.dataset.data.data)
