"""
Data analysis functionality.

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

.. todo::
    Add capabilities of handling analysis steps spanning multiple datasets,
    in a similar fashion to what has been done for plots (see the
    :mod:`plotting` module for details). In contrast to processing steps,
    analysis steps can span multiple datasets. Prominent examples would be
    comparing intensities of different datasets or global fits of multiple
    datasets.

"""


import copy

import aspecd.dataset
import aspecd.utils


class Error(Exception):
    """Base class for exceptions in this module."""

    pass


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


class MissingAnalysisStepError(Error):
    """Exception raised when no analysis step exists to act on

    Attributes
    ----------
    message : :class:`str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


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
        pass

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
        pass

    def _perform_task(self):
        """Perform the actual analysis step on the dataset.

        The implementation of the actual analysis step goes in here in all
        classes inheriting from SingleAnalysisStep. This method is
        automatically called by :meth:`self.analyse` after some background
        checks.

        """
        pass


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

        """
        self._assign_dataset(dataset=dataset)
        self._call_from_dataset(from_dataset=from_dataset)
        return self.dataset

    def _assign_dataset(self, dataset=None):
        if not dataset:
            if not self.dataset:
                raise MissingDatasetError
        else:
            self.dataset = dataset

    def _call_from_dataset(self, from_dataset=False):
        if not from_dataset:
            self.dataset.analyse(self)
        else:
            self._sanitise_parameters()
            self._perform_task()

    # pylint: disable=arguments-differ
    def analyze(self, dataset=None):
        """Perform the actual analysis step on the given dataset.

        Same method as self.analyse, but for those preferring AE over BE

        """
        return self.analyse(dataset)

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
        history_record : :class:`aspecd.analysis.AnalysisHistoryRecord`
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

        Raises
        ------
        aspecd.analysis.MissingDatasetError
            Raised when no datasets exist to act on

        """
        if not self.datasets:
            raise MissingDatasetError
        super().analyse()
        self._sanitise_parameters()
        self._perform_task()


class AnalysisStepRecord:
    """Base class for analysis step records.

    The analysis of a :class:`aspecd.dataset.Dataset` should *not* contain
    references to :class:`aspecd.analysis.AnalysisStep` objects, but rather
    records that contain all necessary information to create the respective
    objects inherited from :class:`aspecd.analysis.AnalysisStep`. One
    reason for this is simply that we want to import datasets containing
    analysis steps in their analyses for which no corresponding analysis
    class exists in the current installation of the application. Another is
    to not have an infinite recursion of datasets, as the dataset is stored
    in an :obj:`aspecd.analysis.AnalysisStep` object.

    Attributes
    ----------
    description : :class:`str`
        Short description, to be set in class definition
    parameters : :class:`dict`
        Parameters required for performing the analysis step

        All parameters, implicit and explicit.
    comment : :class:`str`
        User-supplied comment describing intent, purpose, reason, ...
    class_name : :class:`str`
        Fully qualified name of the class of the corresponding analysis step

    Parameters
    ----------
    analysis_step : :class:`aspecd.analysis.SingleAnalysisStep`
        Analysis step the record should be created for.

    Raises
    ------
    aspecd.analysis.MissingAnalysisStepError
        Raised when no analysis step exists to act on

    """

    def __init__(self, analysis_step=None):
        if not analysis_step:
            raise MissingAnalysisStepError
        self.description = ''
        self.parameters = dict()
        self.comment = ''
        self.class_name = ''
        self._copy_fields_from_analysis_step(analysis_step)

    def _copy_fields_from_analysis_step(self, analysis_step):
        self.description = analysis_step.description
        self.parameters = analysis_step.parameters
        self.comment = analysis_step.comment
        self.class_name = analysis_step.name

    def create_analysis_step(self):
        """Create an analysis step object from the parameters stored.

        Returns
        -------
        analysis_step : :class:`aspecd.analysis.SingleAnalysisStep`
            actual analysis step object that can be used for analysis

        """
        analysis_step = aspecd.utils.object_from_class_name(self.class_name)
        analysis_step.comment = self.comment
        analysis_step.parameters = self.parameters
        analysis_step.description = self.description
        return analysis_step


class SingleAnalysisStepRecord(AnalysisStepRecord):
    """Base class for analysis step records stored in the dataset analyses.

    The analysis of a :class:`aspecd.dataset.Dataset` should *not* contain
    references to :class:`aspecd.analysis.AnalysisStep` objects, but rather
    records that contain all necessary information to create the respective
    objects inherited from :class:`aspecd.analysis.AnalysisStep`. One
    reason for this is simply that we want to import datasets containing
    analysis steps in their analyses for which no corresponding analysis
    class exists in the current installation of the application. Another is
    to not have an infinite recursion of datasets, as the dataset is stored
    in an :obj:`aspecd.analysis.AnalysisStep` object.

    .. note::
        Each analyses entry in a dataset stores the analysis step as a
        :class:`aspecd.analysis.SingleAnalysisStepRecord`, even in applications
        inheriting from the ASpecD framework. Hence, subclassing of this class
        should normally not be necessary.

    Attributes
    ----------
    preprocessing : :class:`list`
        List of processing steps

        The actual processing steps are objects of the class
        :class:`aspecd.processing.ProcessingStepRecord`.

    Parameters
    ----------
    analysis_step : :class:`aspecd.analysis.SingleAnalysisStep`
        Analysis step the record should be created for.

    """

    def __init__(self, analysis_step=None):
        super().__init__(analysis_step=analysis_step)
        self.preprocessing = []

    def _copy_fields_from_analysis_step(self, analysis_step):
        super()._copy_fields_from_analysis_step(analysis_step)
        self.preprocessing = analysis_step.preprocessing


class AnalysisHistoryRecord(aspecd.dataset.HistoryRecord):
    """History record for analysis steps on datasets.

    Attributes
    ----------
    analysis : :class:`aspecd.analysis.SingleAnalysisStep`
        Analysis step the history is saved for

    package : :class:`str`
        Name of package the history record gets recorded for

        Prerequisite for reproducibility, gets stored in the
        :attr:`aspecd.dataset.HistoryRecord.sysinfo` attribute.
        Will usually be provided automatically by the dataset.

    Parameters
    ----------
    analysis_step : :class:`aspecd.analysis.SingleAnalysisStep`
        Analysis step the history is saved for

    package : :class:`str`
        Name of package the history record gets recorded for

    """

    def __init__(self, analysis_step=None, package=''):
        super().__init__(package=package)
        self.analysis = SingleAnalysisStepRecord(analysis_step)

    def replay(self, dataset):
        """Replay the analysis step saved in the history record.

        Parameters
        ----------
        dataset : :class:`aspecd.dataset.Dataset`
            dataset the analysis step should be replayed to

        """
        analysis_step = self.analysis.create_analysis_step()
        dataset.analyse(analysis_step=analysis_step)
