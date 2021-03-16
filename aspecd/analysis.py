"""
Data analysis functionality.

.. sidebar:: Processing vs. analysis steps

    The key difference between processing and analysis steps: While a
    processing step *modifies* the data of the dataset it operates on,
    an analysis step returns a result based on data of a dataset, but leaves
    the original dataset unchanged.


Key to reproducible science is automatic documentation of each analysis
step applied to the data of a dataset. Such an analysis step each is
self-contained, meaning it contains every necessary information to perform
the analysis task on a given dataset.

Analysis steps, in contrast to processing steps (see
:mod:`aspecd.processing` for details), operate on data of a
:class:`aspecd.dataset.Dataset`, but don't change its data. Rather,
some result is obtained that is stored separately, together with the
parameters of the analysis step, in the
:attr:`aspecd.dataset.Dataset.analyses` attribute of the dataset.

Each real analysis step should inherit from
:class:`aspecd.analysis.SingleAnalysisStep` as documented there. Furthermore,
each analysis step should be contained in one module named "analysis".
This allows for easy automation and replay of analysis steps, particularly
in context of recipe-driven data analysis (for details, see the
:mod:`aspecd.tasks` module).

"""


import copy

import aspecd.exceptions
import aspecd.history
import aspecd.utils
from aspecd.history import AnalysisHistoryRecord


class AnalysisStep:
    """
    Base class for analysis steps.

    Analysis steps, in contrast to processing steps (see
    :mod:`aspecd.processing` for details), operate on data of a
    :class:`aspecd.dataset.Dataset`, but don't change its data. Rather,
    some result is obtained. This result is stored separately,
    together with the parameters of the analysis step, in the
    :attr:`aspecd.dataset.Dataset.analyses` attribute of the dataset and
    can be found in the :attr:`aspecd.analysis.SingleAnalysisStep.result`
    attribute.

    In case :attr:`aspecd.analysis.SingleAnalysisStep.result` is a dataset,
    it is a calculated dataset (:class:`aspecd.dataset.CalculatedDataset`),
    and the idea behind storing the result in form of a dataset is to be
    able to plot and further process these results in a fully generic manner.

    Attributes
    ----------
    name : :class:`str`
        Name of the analysis step.

        Defaults to the lower-case class name, don't change!
    parameters : :class:`dict`
        Parameters required for performing the analysis step

        All parameters, implicit and explicit.
    result
        Results of the analysis step

        Can be either a :class:`aspecd.dataset.Dataset` or some other
        class, *e.g.*, :class:`aspecd.metadata.PhysicalQuantity`.

        In case of a dataset, it is a calculated dataset
        (:class:`aspecd.dataset.CalculatedDataset`)
    description : :class:`str`
        Short description, to be set in class definition
    comment : :class:`str`
        User-supplied comment describing intent, purpose, reason, ...

    Raises
    ------
    aspecd.analysis.MissingDatasetError
        Raised when no dataset exists to act on

    """

    def __init__(self):
        self.name = aspecd.utils.full_class_name(self)
        self.parameters = dict()
        self.result = None
        self.description = 'Abstract analysis step'
        self.comment = ''

    def analyse(self):
        """Perform the actual analysis step on the given dataset.

        The actual analysis step should be implemented within the non-public
        method :meth:`_perform_task`. Besides that, the applicability of the
        analysis step to the given dataset will be checked automatically and
        the parameters will be sanitised by calling the non-public method
        :meth:`_sanitise_parameters`.

        """

    def analyze(self):
        """Perform the actual analysis step on the given dataset.

        Same method as self.analyse, but for those preferring AE over BE

        """
        return self.analyse()

    def _sanitise_parameters(self):
        """Ensure parameters provided for analysis step are correct.

        Needs to be implemented in classes inheriting from AnalyisStep
        according to their needs. Most probably, you want to check for
        correct types of all parameters as well as values within sensible
        borders.

        """

    def _perform_task(self):
        """Perform the actual analysis step on the dataset.

        The implementation of the actual analysis step goes in here in all
        classes inheriting from SingleAnalysisStep. This method is
        automatically called by :meth:`self.analyse` after some background
        checks.

        """

    # noinspection PyUnusedLocal
    @staticmethod
    def applicable(dataset):  # pylint: disable=unused-argument
        """Check whether analysis step is applicable to the given dataset.

        Returns `True` by default and needs to be implemented in classes
        inheriting from SingleAnalysisStep according to their needs.

        This is a static method that gets called automatically by each class
        inheriting from :class:`aspecd.analysis.AnalysisStep`. Hence,
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


class SingleAnalysisStep(AnalysisStep):
    """
    Base class for analysis steps operating on single datasets.

    Analysis steps, in contrast to processing steps (see
    :mod:`aspecd.processing` for details), operate on data of a
    :class:`aspecd.dataset.Dataset`, but don't change its data. Rather,
    some result is obtained. This result is stored separately,
    together with the parameters of the analysis step, in the
    :attr:`aspecd.dataset.Dataset.analyses` attribute of the dataset and
    can be found in the :attr:`aspecd.analysis.SingleAnalysisStep.result`
    attribute.

    In case :attr:`aspecd.analysis.SingleAnalysisStep.result` is a dataset,
    it is a calculated dataset (:class:`aspecd.dataset.CalculatedDataset`),
    and the idea behind storing the result in form of a dataset is to be
    able to plot and further process these results in a fully generic manner.

    Attributes
    ----------
    preprocessing : :class:`list`
        List of necessary preprocessing steps to perform the analysis.
    description : :class:`str`
        Short description, to be set in class definition
    dataset : :class:`aspecd.dataset.Dataset`
        Dataset the analysis step should be performed on

    Raises
    ------
    aspecd.analysis.MissingDatasetError
        Raised when no dataset exists to act on

    """

    def __init__(self):
        super().__init__()
        # self.name = aspecd.utils.full_class_name(self)
        self.preprocessing = []
        self.description = 'Abstract single analysis step'
        self.dataset = None

    # pylint: disable=arguments-differ
    def analyse(self, dataset=None, from_dataset=False):
        """Perform the actual analysis step on the given dataset.

        If no dataset is provided at method call, but is set as property in
        the SingleAnalysisStep object, the process method of the dataset
        will be called and thus the history written.

        If no dataset is provided at method call nor as property in the
        object, the method will raise a respective exception.

        The :obj:`aspecd.dataset.Dataset` object always call this method with
        the respective dataset as argument. Therefore, in this case setting
        the dataset property within the
        :obj:`aspecd.analysis.SingleAnalysisStep` object is not necessary.

        The actual analysis step should be implemented within the non-public
        method :meth:`_perform_task`. Besides that, the applicability of the
        analysis step to the given dataset will be checked automatically and
        the parameters will be sanitised by calling the non-public method
        :meth:`_sanitise_parameters`.

        Additionally, each dataset will be automatically checked for
        applicability, using the
        :meth:`aspecd.analysis.AnalysisStep.applicable` method. Make sure to
        override this method according to your needs.

        Parameters
        ----------
        dataset : :class:`aspecd.dataset.Dataset`
            dataset to perform analysis for

        from_dataset : `boolean`
            whether we are called from within a dataset

            Defaults to "False" and shall never be set manually.

        Returns
        -------
        dataset : :class:`aspecd.dataset.Dataset`
            dataset analysis has been performed for

        Raises
        ------
        aspecd.processing.NotApplicableToDatasetError
            Raised when analysis step is not applicable to dataset

        aspecd.processing.MissingDatasetError
            Raised when no dataset exists to act on

        """
        self._assign_dataset(dataset=dataset)
        self._call_from_dataset(from_dataset=from_dataset)
        return self.dataset

    def _assign_dataset(self, dataset=None):
        if not dataset:
            if not self.dataset:
                raise aspecd.exceptions.MissingDatasetError
        else:
            self.dataset = dataset

    def _call_from_dataset(self, from_dataset=False):
        if not from_dataset:
            self.dataset.analyse(self)
        else:
            self._check_applicability()
            self._sanitise_parameters()
            self._perform_task()

    def _check_applicability(self):
        if not self.applicable(self.dataset):
            raise aspecd.exceptions.NotApplicableToDatasetError

    def analyze(self, dataset=None, from_dataset=False):
        """Perform the actual analysis step on the given dataset.

        Same method as self.analyse, but for those preferring AE over BE

        """
        return self.analyse(dataset, from_dataset)

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

    def create_history_record(self):
        """
        Create history record to be added to the dataset.

        Usually, this method gets called from within the
        :meth:`aspecd.dataset.analyse` method of the
        :class:`aspecd.dataset.Dataset` class and ensures the history of
        each analysis step to get written properly.

        Returns
        -------
        history_record : :class:`aspecd.history.AnalysisHistoryRecord`
            history record for analysis step

        """
        history_record = AnalysisHistoryRecord(
            analysis_step=self,
            package=self.dataset.package_name)
        history_record.analysis.preprocessing = copy.deepcopy(
            self.dataset.history)
        return history_record


class MultiAnalysisStep(AnalysisStep):
    """
    Base class for analysis steps operating on multiple datasets.

    Analysis steps, in contrast to processing steps (see
    :mod:`aspecd.processing` for details), operate on data of a
    :class:`aspecd.dataset.Dataset`, but don't change its data. Rather,
    some result is obtained. This result is stored separately,
    together with the parameters of the analysis step, in the
    :attr:`aspecd.dataset.Dataset.analyses` attribute of the dataset and
    can be found in the :attr:`aspecd.analysis.MultiAnalysisStep.result`
    attribute.

    Attributes
    ----------
    datasets : :class:`list`
        List of dataset the analysis step should be performed for

    """

    def __init__(self):
        super().__init__()
        self.datasets = []
        self.description = 'Abstract analysis step for multiple dataset'

    def analyse(self):
        """Perform the actual analysis on the given list of datasets.

        If no dataset is added to the list of datasets of the
        object, the method will raise a respective exception.

        The actual analysis step should be implemented within the non-public
        method :meth:`_perform_task`. Besides that, the parameters will be
        sanitised by calling the non-public method
        :meth:`_sanitise_parameters`.

        Additionally, each dataset will be automatically checked for
        applicability, using the
        :meth:`aspecd.analysis.AnalysisStep.applicable` method. Make sure to
        override this method according to your needs.

        Raises
        ------
        aspecd.analysis.MissingDatasetError
            Raised when no datasets exist to act on

        aspecd.processing.NotApplicableToDatasetError
            Raised when analysis step is not applicable to dataset

        """
        if not self.datasets:
            raise aspecd.exceptions.MissingDatasetError
        super().analyse()
        self._check_applicability()
        self._sanitise_parameters()
        self._perform_task()

    def _check_applicability(self):
        for dataset in self.datasets:
            if not self.applicable(dataset):
                raise aspecd.exceptions.NotApplicableToDatasetError
