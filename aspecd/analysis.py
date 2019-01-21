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
:class:`aspecd.analysis.AnalysisStep` as documented there. Furthermore,
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


class AnalysisStep(aspecd.utils.ExecuteOnDatasetMixin):
    """
    Base class for analysis steps.

    Attributes
    ----------
    name : :class:`str`
        Name of the analysis step.

        Defaults to the lower-case class name, don't change!
    parameters : :class:`dict`
        Parameters required for performing the analysis step

        All parameters, implicit and explicit.
    results : :class:`dict`
        Results of the analysis step
    preprocessing : :class:`list`
        List of necessary preprocessing steps to perform the analysis.
    description : :class:`str`
        Short description, to be set in class definition
    comment : :class:`str`
        User-supplied comment describing intent, purpose, reason, ...
    dataset : :class:`aspecd.dataset.Dataset`
        Dataset the analysis step should be performed on

    Raises
    ------
    MissingDatasetError
        Raised when no dataset exists to act on

    """

    def __init__(self):
        self.name = aspecd.utils.full_class_name(self)
        self.parameters = dict()
        self.results = dict()
        self.preprocessing = []
        self.description = 'Abstract analysis step'
        self.comment = ''
        self.dataset = None

    def analyse(self, dataset=None, from_dataset=False):
        """Perform the actual analysis step on the given dataset.

        If no dataset is provided at method call, but is set as property in
        the AnalysisStep object, the process method of the dataset will be
        called and thus the history written.

        If no dataset is provided at method call nor as property in the
        object, the method will raise a respective exception.

        The :obj:`aspecd.dataset.Dataset` object always call this method with
        the respective dataset as argument. Therefore, in this case setting
        the dataset property within the :obj:`aspecd.analysis.AnalysisStep`
        object is not necessary.

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

    def analyze(self, dataset=None):
        """Perform the actual analysis step on the given dataset.

        Same method as self.analyse, but for those preferring AE over BE

        """
        return self.analyse(dataset)

    def execute(self, dataset=None):
        """
        Execute task on dataset.

        Used mainly in recipe-driven data analysis requiring generically
        executing tasks independent of their type. For details of
        recipe-driven data analysis, see the :mod:`tasks` module.

        Parameters
        ----------
        dataset : :class:`aspecd.dataset.Dataset`
            dataset to act on

        Returns
        -------
        dataset : :class:`aspecd.dataset.Dataset`
            dataset acted on

        """
        return self.analyse(dataset=dataset)

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
        classes inheriting from AnalysisStep. This method is automatically
        called by :meth:`self.analyse` after some background checks.

        """
        pass
