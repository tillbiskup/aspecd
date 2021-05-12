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


Generally, two types of analysis steps can be distinguished:

* Analysis steps for handling single datasets

  Shall be derived from :class:`aspecd.analysis.SingleAnalysisStep`.

* Analysis steps for handling multiple datasets

  Shall be derived from :class:`aspecd.analysis.MultiAnalysisStep`.

In the first case, the analysis is usually handled using the
:meth:`analyse` method of the respective :obj:`aspecd.dataset.Dataset`
object. Additionally, those analysis steps always only operate on the data
of a single dataset. Analysis steps handling single datasets should always
inherit from the :class:`aspecd.analysis.SingleAnalysisStep` class.

In the second case, the analysis step is handled using the :meth:`analyse`
method of the :obj:`aspecd.analysis.AnalysisStep` object, and the datasets
are stored as a list within the analysis step. As these analysis steps span
several datasets. Analysis steps handling multiple datasets should
always inherit from the :class:`aaspecd.analysis.MultiAnalysisStep` class.

The module contains both, base classes for analysis steps (as detailed
above) as well as a series of generally applicable analysis steps for all
kinds of spectroscopic data. The latter are an attempt to relieve the
developers of packages derived from the ASpecD framework from the task to
reinvent the wheel over and over again.

The next section gives an overview of the concrete analysis steps
implemented within the ASpecD framework. For details of how to implement
your own analysis steps, see the section below.


Concrete analysis steps
=======================

Besides providing the basis for analysis steps for the ASpecD framework,
ensuring full reproducibility and traceability, hence reproducible science
and good scientific practice, this module comes with a (growing) number of
general-purpose analysis steps useful for basically all kinds of
spectroscopic data.

Here is a list as a first overview. For details, see the detailed
documentation of each of the classes, readily accessible by the link.


Analysis steps operating on individual datasets
-----------------------------------------------

The following analysis steps operate each on individual datasets
independently.

* :class:`BasicCharacteristics`

  Extract basic characteristics of a dataset

* :class:`BasicStatistics`

  Extract basic statistical measures of a dataset


Writing own analysis steps
==========================

Each real analysis step should inherit from either
:class:`aspecd.processing.SingleProcessingStep` in case of operating on a
single dataset only or from :class:`aspecd.processing.MultiProcessingStep` in
case of operating on several datasets at once. Furthermore, all analysis
steps should be contained in one module named "analysis". This allows for
easy automation and replay of analysis steps, particularly in context of
recipe-driven data analysis (for details, see the :mod:`aspecd.tasks` module).


General advice
--------------

A few hints on writing own analysis step classes:

* Always inherit from :class:`aspecd.analysis.SingleAnalysisStep` or
  :class:`aspecd.analysis.MultiAnalysisStep`, depending on your needs.

* Store all parameters, implicit and explicit, in the dict ``parameters`` of
  the :class:`aspecd.analysis.AnalysisStep` class, *not* in separate
  properties of the class. Only this way, you can ensure full
  reproducibility and compatibility of recipe-driven data analysis (for
  details of the latter, see the :mod:`aspecd.tasks` module).

* Always set the ``description`` property to a sensible value.

* Implement the actual analysis in the ``_perform_task`` method of the
  analysis step. For sanitising parameters and checking general
  applicability of the analysis step to the dataset(s) at hand, continue
  reading.

* Make sure to implement the
  :meth:`aspecd.analysis.AnalysisStep.applicable` method according to your
  needs. Typical cases would be to check for the dimensionality of the
  underlying data, as some analysis steps may work only for 1D data (or
  vice versa). Don't forget to declare this as a static method, using the
  ``@staticmethod`` decorator.

* With the ``_sanitise_parameters`` method, the input parameters are
  automatically checked and an appropriate exception can be thrown in order to
  describe the error source to the user.

Some more special cases are detailed below. For further advice, consult the
source code of this module, and have a look at the concrete processing steps
whose purpose is described below in more detail.

.. todo::
    Add description of special cases as applicable


Module documentation
====================


"""


import copy

import numpy as np

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
    aspecd.exceptions.MissingDatasetError
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
    aspecd.exceptions.MissingDatasetError
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
        aspecd.exceptions.NotApplicableToDatasetError
            Raised when analysis step is not applicable to dataset

        aspecd.exceptions.MissingDatasetError
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
        aspecd.exceptions.MissingDatasetError
            Raised when no datasets exist to act on

        aspecd.exceptions.NotApplicableToDatasetError
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


class BasicCharacteristics(SingleAnalysisStep):
    # noinspection PyUnresolvedReferences
    """
    Extract basic characteristics of a dataset.

    Extracting basic characteristics (minimum, maximum, area, amplitude) of
    a dataset is programmatically quite simple. This class provides a
    working solution from within the ASpecD framework.


    Attributes
    ----------
    parameters : :class:`dict`
        All parameters necessary for this step.

        kind : :class:`str`
            Kind of the characteristic to extract from the data

            Valid values are "min", "max", "amplitude", and "area".

        output : :class:`str`
            Kind of output: (intensity) value, axes value(s), or axes indices

            Valid values are "value" (default), "axes", and "indices". For
            amplitude and area, as these characteristics have no analogon on
            the axes, only "value" is a valid output option.

            Default: "value"

    result :
        Characteristic(s) of the dataset.

        The actual return type depends on the type of characteristics and
        output selected.

        ========================= ============= ==============
        kind (characteristic)     output        return type
        ========================= ============= ==============
        min, max, amplitude, area value         :class:`float`
        min, max                  axes, indices :class:`list`
        all                       value         :class:`dict`
        ========================= ============= ==============


    Raises
    ------
    ValueError
        Raised if no kind of characteristics is provided.

        Raised if kind of characteristics is unknown.

        Raised if output type is unknown.

        Raised if output type is not available for kind of characteristics.


    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. The examples focus each on a single
    aspect.

    Extracting the characteristic of a dataset is quite simple:

    .. code-block:: yaml

       - kind: singleanalysis
         type: BasicCharacteristics
         properties:
           parameters:
             type: min
         result: min_of_dataset

    This would simply return the minimum (value) of a given dataset in the
    result assigned to the recipe-internal variable ``min_of_dataset``.
    Similarly, you can extract "max", "area", and "amplitude" from your
    dataset. In case you are interested in the axes values or indices,
    set the output parameter appropriately:

    .. code-block:: yaml

       - kind: singleanalysis
         type: BasicCharacteristics
         properties:
           parameters:
             type: min
             output: axes
         result: min_of_dataset

    In this particular case, this would return the axes values of the
    global minimum of your dataset in the result. Note that those other
    output types are only available for "min" and "max", as "area" and
    "amplitude" have no analogon on the axes.

    Sometimes, you are interested in getting the values of all
    characteristics at once in form of a dictionary:

    .. code-block:: yaml

       - kind: singleanalysis
         type: BasicCharacteristics
         properties:
           parameters:
             type: all
         result: min_of_dataset

    Make sure to understand the different types the result has depending on
    the characteristic and output type chosen. For details, see the table
    above.

    .. versionadded:: 0.2

    """

    def __init__(self):
        super().__init__()
        self.description = 'Obtain basic characteristics'
        self.parameters["kind"] = None
        self.parameters["output"] = "value"

    def _sanitise_parameters(self):
        if not self.parameters["kind"]:
            raise ValueError("No kind of characteristics given")
        if self.parameters["kind"] not in ['min', 'max', 'amplitude', 'area',
                                           'all']:
            raise ValueError("Unknown kind %s" % self.parameters["kind"])
        if self.parameters["output"] not in ['value', 'axes', 'indices']:
            raise ValueError("Unknown output type %s"
                             % self.parameters["output"])
        if self.parameters["output"] in ["axes", "indices"] and \
                self.parameters["kind"] in ["area", "amplitude"]:
            raise ValueError("Output %s not available for characteristic %s."
                             % (self.parameters["output"],
                                self.parameters["kind"]))

    def _perform_task(self):
        if self.parameters["kind"] in ['min', 'max', 'amplitude', 'area']:
            self.result = self._get_characteristic(
                kind=self.parameters["kind"],
                output=self.parameters["output"])
        if self.parameters["kind"] == "all":
            self.result = {
                'min': self._get_characteristic("min"),
                'max': self._get_characteristic("max"),
                'amplitude': self._get_characteristic("amplitude"),
                'area': self._get_characteristic("area"),
            }

    def _get_characteristic(self, kind=None, output="value"):  # noqa: MC0001
        result = None
        if output == "value":
            if kind == "min":
                result = self.dataset.data.data.min()
            if kind == "max":
                result = self.dataset.data.data.max()
            if kind == "amplitude":
                result = \
                    self.dataset.data.data.max() - self.dataset.data.data.min()
            if kind == "area":
                result = self.dataset.data.data.sum()
        if output == "axes":
            if kind == "min":
                result = []
                idx = np.unravel_index(self.dataset.data.data.argmin(),
                                       self.dataset.data.data.shape)
                for dim in range(self.dataset.data.data.ndim):
                    result.append(self.dataset.data.axes[dim].values[idx[dim]])
            if kind == "max":
                result = []
                idx = np.unravel_index(self.dataset.data.data.argmax(),
                                       self.dataset.data.data.shape)
                for dim in range(self.dataset.data.data.ndim):
                    result.append(self.dataset.data.axes[dim].values[idx[dim]])
        if output == "indices":
            if kind == "min":
                result = list(np.unravel_index(self.dataset.data.data.argmin(),
                                               self.dataset.data.data.shape))
            if kind == "max":
                result = list(np.unravel_index(self.dataset.data.data.argmax(),
                                               self.dataset.data.data.shape))
        return result


class BasicStatistics(SingleAnalysisStep):
    # noinspection PyUnresolvedReferences
    """
    Extract basic statistical measures of a dataset.

    Extracting basic statistical measures (mean, median, std, var) of
    a dataset is programmatically quite simple. This class provides a
    working solution from within the ASpecD framework.


    Attributes
    ----------
    parameters : :class:`dict`
        All parameters necessary for this step.

        kind : :class:`str`
            Kind of the statistical measure to extract from the data

            Valid values are "mean", "median", "std", and "var".


    Raises
    ------
    ValueError
        Raised if no kind of statistical measure is provided.

        Raised if kind of statistical measure is unknown.


    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. The examples focus each on a single
    aspect.

    Extracting the statistical measure of a dataset is quite simple:

    .. code-block:: yaml

       - kind: singleanalysis
         type: BasicStatistics
         properties:
           parameters:
             type: median
         result: median_of_dataset

    This would simply return the minimum (value) of a given dataset in the
    result assigned to the recipe-internal variable ``median_of_dataset``.
    Similarly, you can extract "mean", "std" (standard deviation), and "var"
    (variance) from your dataset.

    .. versionadded:: 0.2

    """

    def __init__(self):
        super().__init__()
        self.description = 'Obtain basic statistics'
        self.parameters["kind"] = None

    def _sanitise_parameters(self):
        if not self.parameters["kind"]:
            raise ValueError("No kind of statistics given")
        if self.parameters["kind"] not in ['mean', 'median', 'std', 'var']:
            raise ValueError("Unknown kind %s" % self.parameters["kind"])

    def _perform_task(self):
        function = getattr(np, self.parameters["kind"])
        self.result = function(self.dataset.data.data)


class SignalToNoiseRatio(SingleAnalysisStep):
    """
    Determine the signal-to-noise ratio of a dataset.

    Needs perhaps to be moved to another module, if it turns out that
    analysis and processing steps depend on each other sometimes.

    One possibility would be to create two modules complex_processing and
    complex_analysis that both import processing and analysis and that are
    searched for by the respective analysis and processing task (to have an
    easier user interface).
    """

    def __init__(self):
        super().__init__()
        self.description = 'Determine signal-to-noise ratio'
