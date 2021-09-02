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

* :class:`BlindSNREstimation`

  Blind, *i.e.* parameter-free, estimation of the signal-to-noise ratio

* :class:`PeakFinding`

  Find peaks in 1D datasets

* :class:`PowerDensitySpectrum`

  Calculate power density spectrum of 1D dataset, useful, *e.g.* for
  analysing the statistics of noise (*i.e.*, its colour)

* :class:`PolynomialFit`

  Perform polynomial fit on 1D data

* :class:`LinearRegressionWithFixedIntercept`

  Perform linear regression without fitting the intercept on 1D data. Note
  that this is mathematically different from a polynomial fit of first order.


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
  details of the latter, see the :mod:`aspecd.tasks` module). Additionally,
  this way, if you return a (calculated) dataset, these parameters get
  automatically added to the metadata of the calculated dataset.

* Always set the ``description`` property to a sensible value. Be as concise
  as possible. The first line of the class docstring may be a good inspiration.

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


Adding parameters upon analysis
-------------------------------

Sometimes there is the need to persist values that are only obtained during
analysis of the data. These parameters should end up in the
:attr:`aspecd.analysis.AnalysisStep.parameters` dictionary. Thus,
they are added to the dataset history and available for reports and alike.


Changing the length of your data
--------------------------------

When changing the length of the data, always change the corresponding axes
values *first*, and only afterwards the data, as changing the data will
change the axes values and adjust their length to the length of the
corresponding dimension of the data.


Returning calculated datasets as result
---------------------------------------

The type of the attribute :attr:`aspecd.analysis.AnalysisStep.result`
depends strongly on the specific analysis step. Sometimes, a calculated
dataset will be returned. A typical example is
:class:`aspecd.analysis.PeakFinding`, where you can explicitly ask for a
calculated dataset to be returned and use this result later for plotting
both, original data and detected peaks overlaid. To have the minimal
metadata of the calculated dataset set correctly, use the method
:meth:`aspecd.analysis.AnalysisStep.create_dataset` to obtain the calculated
dataset. This will set both, type of calculation (to the full class name of
the analysis step) and parameters. Of course, you are solely responsible to
set the data and axes values (and further metadata, if applicable).


Module documentation
====================


"""


import copy

import numpy as np
import scipy.signal

import aspecd.dataset
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
    can be found in the :attr:`aspecd.analysis.AnalysisStep.result`
    attribute.

    In case :attr:`aspecd.analysis.AnalysisStep.result` is a dataset,
    it is a calculated dataset (:class:`aspecd.dataset.CalculatedDataset`),
    and the idea behind storing the result in form of a dataset is to be
    able to plot and further process these results in a fully generic
    manner. To create such a calculated dataset, use the method
    :meth:`create_dataset` that will automatically set minimal metadata for
    you.

    The actual implementation of the analysis step is done in the private
    method :meth:`_perform_task` that in turn gets called by :meth:`analyse`
    which is called by the :meth:`aspecd.dataset.Dataset.analyse` method of the
    dataset object.

    .. note::
        Usually, you will never implement an instance of this class for
        actual analysis tasks, but rather one of the child classes, namely
        :class:`aspecd.analysis.SingleAnalysisStep` and
        :class:`aspecd.analysis.MultiAnalysisStep`, depending on whether
        your analysis step operates on a single dataset or requires
        multiple datasets.

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

    def create_dataset(self):
        """
        Create calculated dataset containing minimal metadata.

        The following metadata are set:

        ======================= ==================
        Metadata                Value
        ======================= ==================
        calculation.type        :attr:`name`
        calculation.parameters  :attr:`parameters`
        ======================= ==================

        Returns
        -------
        dataset : :class:`aspecd.dataset.CalculatedDataset`
            (Calculated) dataset containing minimal metadata.


        .. versionadded:: 0.2

        """
        dataset = aspecd.dataset.CalculatedDataset()
        dataset.metadata.calculation.type = self.name
        dataset.metadata.calculation.parameters = self.parameters
        return dataset

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

    The actual implementation of the analysis step is done in the private
    method :meth:`_perform_task` that in turn gets called by :meth:`analyse`
    which is called by the :meth:`aspecd.dataset.Dataset.analyse` method of the
    dataset object.

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
        the SingleAnalysisStep object, the analysd method of the dataset
        will be called and thus the analysis added to the list of analyses
        of the dataset.

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
            message = "%s not applicable to dataset with id %s" \
                      % (self.name, self.dataset.id)
            raise aspecd.exceptions.NotApplicableToDatasetError(message=message)

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

    The actual implementation of the analysis step is done in the private
    method :meth:`_perform_task` that in turn gets called by :meth:`analyse`.

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
                message = "%s not applicable to dataset with id %s" \
                          % (self.name, dataset.id)
                raise aspecd.exceptions.NotApplicableToDatasetError(
                    message=message)


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
         result: characteristics_of_dataset

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

    def _get_characteristic(self, kind=None, output="value"):
        function = getattr(self, '_get_characteristic_' + output)
        return function(kind=kind)

    def _get_characteristic_value(self, kind=None):
        result = None
        if kind == "min":
            result = self.dataset.data.data.min()
        if kind == "max":
            result = self.dataset.data.data.max()
        if kind == "amplitude":
            result = np.ptp(self.dataset.data.data)
        if kind == "area":
            result = self.dataset.data.data.sum()
        return result

    def _get_characteristic_axes(self, kind=None):
        result = None
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
        return result

    def _get_characteristic_indices(self, kind=None):
        result = None
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

    This would simply return the median of the data of a given dataset in the
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


class BlindSNREstimation(SingleAnalysisStep):
    # noinspection PyUnresolvedReferences
    r"""
    Blind, *i.e.* parameter-free, estimation of the signal-to-noise ratio.

    In spectroscopy, the signal-to-noise ratio (SNR) is usually defined as the
    ratio of mean (of the signal) to standard deviation (of the noise) of a
    signal or measurement.

    For accurate estimations, this requires to be able to separate noise and
    signal, hence to define a part of the overall measurement not including
    signal. As this is not always possible, there are different ways to make
    a blind estimate of the SNR, *i.e.* without additional parameters.

    The simplest possible approach of a blind estimate is the ratio of mean to
    standard deviation of the whole signal (method ``simple``):

    .. math::

        \mbox{SNR} = \frac{\mu}{\sigma}

    An alternative version sometimes used is to take the suqare of both,
    mean and standard deviation (method ``simple_squared``):

    .. math::

        \mbox{SNR} = \frac{\mu^2}{\sigma^2}

    This is equivalent to the more common definition using the ratio of the
    (average) power of signal and noise.

    Yet another algorithm, the "DER_SNR" algorithm proposed by Stoehr et al.
    for use in astronomic data (for details see Czesla et al., 2018, details
    below) makes use of the median and a numeric second derivative (method
    ``der_snr``):

    .. math::

        \mbox{SNR} &= \mbox{med} / \sigma

        \sigma &=\frac{1.482602}{\sqrt{6}}\mbox{med}_i(|-x_{i-2}+2x_i-x_{ i+2}|)


    Other options would be to fit a polynomial to the data, subtract the
    fitted polynomial and estimate the noise this way. A Savitzky-Golay
    filter could be used for this.

    An article dealing with SNR estimation for (astronomic) spectral data
    that provides a lot of details is:

    * S. Czesla, T. Molle, and J. H. M. M. Schmitt: A posteriori noise
      estimation in variable data sets. With applications to spectra and
      light curves. Astronomy and Astrophysics 609(2018):A39.
      `<https://doi.org/10.1051/0004-6361/201730618>`_

    For more information, the following resources may as well be useful:

    * `<https://en.wikipedia.org/wiki/Signal-to-noise_ratio>`_

    * `<http://nipy.org/nitime/examples/snr_example.html>`_

    * `<https://github.com/hrtlacek/SNR>`_

    * `<https://arxiv.org/abs/2011.05113>`_


    .. important::

        While all methods currently implemented are "parameter-free",
        the estimates are based on a number of assumptions, the most
        important being normally distributed noise. Furthermore, your data
        need to be sampled appropriately, with the highest frequency
        component of your signal being well resolved.


    Attributes
    ----------
    parameters : :class:`dict`
        All parameters necessary for this step.

        method : :class:`str`
            Method used to blindly estimate the SNR

            Valid values are "simple", "simple_squared", "der_snr".

            Default: "simple"


    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. The examples focus each on a single
    aspect.

    Obtaining a blind estimate of the SNR of a dataset is quite simple:

    .. code-block:: yaml

       - kind: singleanalysis
         type: BlindSNREstimation
         result: SNR_of_dataset

    This would simply return the SNR of the data of a given dataset in the
    result assigned to the recipe-internal variable ``SNR_of_dataset``.

    To have more control over the method used to blindly estimate the SNR,
    explicitly provide a method:

    .. code-block:: yaml

       - kind: singleanalysis
         type: BlindSNREstimation
         properties:
           parameters:
             method: der_snr
         result: SNR_of_dataset

    This would use the DER_SNR method as described above.

    .. versionadded:: 0.2

    .. versionchanged:: 0.3
        Added methods: "simple_squared", "der_snr"

    """

    def __init__(self):
        super().__init__()
        self.description = 'Blind signal-to-noise ratio estimation'
        self.parameters["method"] = None

    def _sanitise_parameters(self):
        if not self.parameters["method"]:
            self.parameters["method"] = "simple"
        if self.parameters["method"] == "der_snr" \
                and len(self.dataset.data.data) < 4:
            raise ValueError("Too few samples")

    def _perform_task(self):
        if self.parameters["method"] == "simple":
            self.result = \
                self.dataset.data.data.mean() / self.dataset.data.data.std()
        if self.parameters["method"] == "simple_squared":
            self.result = self.dataset.data.data.mean()**2 \
                / self.dataset.data.data.std()**2
        if self.parameters["method"] == "der_snr":
            data = self.dataset.data.data
            signal = np.median(data)
            noise = 1.482602 / np.sqrt(6) \
                * np.median(np.abs(2 * data[2:-2] - data[0:-4] - data[4:]))
            self.result = signal / noise


class PeakFinding(SingleAnalysisStep):
    # noinspection PyUnresolvedReferences
    """
    Peak finding in one dimension.

    Finding peaks is a use case often encountered in analysing spectroscopic
    data, but it is far from trivial and usually requires careful choosing
    of parameters to yield sensible results.

    The peak finding relies on the :func:`scipy.signal.find_peaks` function,
    hence you can set most of the parameters this function understands. For
    details of the parameters, see as well the SciPy documentation.

    .. important::
        Peak finding can only be applied to 1D datasets, due to the
        underlying algorithm.


    Attributes
    ----------
    parameters : :class:`dict`
        All parameters necessary for this step.

        negative_peaks : :class:`bool`
            Whether to include negative peaks in peak finding as well.

            Negative peaks are searched for by inverting the sign of the
            signal, and the list of peak positions is sorted.

            Default: False

        return_properties : :class:`bool`
            Whether to return properties together with the peak positions.

            If properties shall be returned as well, the attribute
            :attr:`result` will be a tuple containing the list of peak
            positions as first element and a dictionary  with peak
            properties as second element.

            Note: If negative peaks shall be returned as well, this option
            will be silently ignored and only the peak positions returned.

            Default: False

        return_dataset : :class:`bool`
            Whether to return a calculated dataset as result.

            In this case, the result will be an object of class
            :class:`aspecd.dataset.CalculatedDataset`, with the data
            containing the peak intensities and the corresponding axis
            values the peak positions. Thus, this can be used to plot the
            peaks on top of the original data.

            Default: False

        height : number or ndarray or sequence
            Required height of peaks. Either a number, None, an array
            matching x or a 2-element sequence of the former. The first
            element is always interpreted as the minimal and the second,
            if supplied, as the maximal required height.

            Default: None

        threshold : number or ndarray or sequence
            Required threshold of peaks, the vertical distance to its
            neighboring samples. Either a number, None, an array matching x
            or a 2-element sequence of the former. The first element is
            always interpreted as the minimal and the second, if supplied,
            as the maximal required threshold.

            Default: None

        distance : number
            Required minimal horizontal distance (>= 1) in samples between
            neighbouring peaks. Smaller peaks are removed first until the
            condition is fulfilled for all remaining peaks.

            Default: None

        prominence : number or ndarray or sequence
            Required prominence of peaks. Either a number, None, an array
            matching x or a 2-element sequence of the former. The first
            element is always interpreted as the minimal and the second,
            if supplied, as the maximal required prominence.

            Default: None

        width : number or ndarray or sequence
            Required width of peaks in samples. Either a number, None,
            an array matching x or a 2-element sequence of the former. The
            first element is always interpreted as the minimal and the
            second, if supplied, as the maximal required width.

            Default: None


    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. The examples focus each on a single
    aspect.

    Finding the peak positions of a basically noise-free dataset is quite
    simple:

    .. code-block:: yaml

       - kind: singleanalysis
         type: PeakFinding
         result: peaks

    This would simply return the peak positions of the data of a given dataset
    in the result assigned to the recipe-internal variable ``peaks``.

    To have more control over the method used to find peaks, you can set a
    number of parameters. To get the negative peaks as well (normally,
    only positive peaks will be looked for):

    .. code-block:: yaml

       - kind: singleanalysis
         type: PeakFinding
         properties:
           parameters:
             negative_peaks: True
         result: peaks

    Sometimes it is convenient to have the peaks returned as a dataset,
    to plot the data and highlight the peaks found:

    .. code-block:: yaml

       - kind: singleanalysis
         type: PeakFinding
         properties:
           parameters:
             return_dataset: True
         result: peaks

    From the options that can be set for the function
    :func:`scipy.signal.find_peaks`, you can set "height", "threshold",
    "distance", "prominence", and "width". For details, see the SciPy
    documentation.

    For noisy data, "prominence" can be a good option to only find "true" peaks:

    .. code-block:: yaml

       - kind: singleanalysis
         type: PeakFinding
         properties:
           parameters:
             prominence: 0.2
         result: peaks

    If you supply one of these additional options, you might be interested
    not only in the peak positions, but in the properties of the peaks found
    as well.

    .. code-block:: yaml

       - kind: singleanalysis
         type: PeakFinding
         properties:
           parameters:
             prominence: 0.2
             return_properties: True
         result: peaks

    In this case, the result, here stored in the variable "peaks", will be a
    tuple with the peak positions as first element and a dictionary with
    properties as the second element. Note that if you ask for negative
    peaks as well, this option will silently be ignored and only the peak
    positions returned.

    .. versionadded:: 0.2

    """

    def __init__(self):
        super().__init__()
        self.description = 'Peak finding in 1D'
        self.parameters["negative_peaks"] = False
        self.parameters["return_properties"] = False
        self.parameters["return_dataset"] = False
        self.parameters["height"] = None
        self.parameters["threshold"] = None
        self.parameters["distance"] = None
        self.parameters["prominence"] = None
        self.parameters["width"] = None

    @staticmethod
    def applicable(dataset):
        """
        Check whether analysis step is applicable to the given dataset.

        Peak finding can only be applied to 1D datasets.

        Parameters
        ----------
        dataset : :class:`aspecd.dataset.Dataset`
            Dataset to check

        Returns
        -------
        applicable : :class:`bool`
            Whether dataset is applicable

        """
        return dataset.data.data.ndim == 1

    def _perform_task(self):
        peaks, properties = scipy.signal.find_peaks(
            self.dataset.data.data,
            height=self.parameters["height"],
            threshold=self.parameters["threshold"],
            distance=self.parameters["distance"],
            prominence=self.parameters["prominence"],
            width=self.parameters["width"],
        )
        if self.parameters["negative_peaks"]:
            negative, _ = scipy.signal.find_peaks(
                -self.dataset.data.data,
                height=self.parameters["height"],
                threshold=self.parameters["threshold"],
                distance=self.parameters["distance"],
                prominence=self.parameters["prominence"],
                width=self.parameters["width"],
            )
            peaks = np.sort(np.concatenate((peaks, negative)))
        if self.parameters["return_dataset"]:
            dataset = self.create_dataset()
            dataset.data.data = self.dataset.data.data[peaks]
            dataset.data.axes[0] = self.dataset.data.axes[0]
            dataset.data.axes[0].values = \
                self.dataset.data.axes[0].values[peaks]
            dataset.data.axes[1] = self.dataset.data.axes[1]
            self.result = dataset
        elif self.parameters["return_properties"] \
                and not self.parameters["negative_peaks"]:
            self.result = (peaks, properties)
        else:
            self.result = self.dataset.data.axes[0].values[peaks]


class PowerDensitySpectrum(SingleAnalysisStep):
    # noinspection PyUnresolvedReferences
    """
    Calculate power density spectrum of given 1D dataset.

    The power density spectrum is the log10 of the power for each frequency
    component as function of the log10 of the frequency. For mathematical
    reasons, the power of the DC component (*f* = 0) is omitted.

    The power density spectrum (sometimes called power spectral density,
    PSD) can be used to analyse the nature of noise, *e.g.* whether it is
    Gaussian (white, normally distributed) noise or "coloured" noise with
    the frequencies of the noise components differently weighted.

    In spectroscopy, often coloured noise (most frequently pink or 1/*f* noise)
    rather than white noise is encountered. The characteristics of white
    noise is an equal distribution of all frequencies, related to a constant
    in the power density spectrum. Pink or 1/*f* noise, in contrast, exhibits a
    linear damping of higher frequencies with a slope of -1 in the power
    density spectrum. For more details regarding noise in spectroscopy,
    the interested reader is referred to the documentation of the
    :class:`aspecd.processing.Noise` class.

    Attributes
    ----------
    result : :class:`aspecd.dataset.CalculatedDataset`
        power density spectrum of the corresponding 1D dataset analysed

    parameters : :class:`dict`
        All parameters necessary for this step.

        method : :class:`str`
            Method to use to calculate the power density spectrum

            Possible methods must exist in the :mod:`scipy.signal` module.
            Currently, you can choose between "periodogram" and "welch". See
            their respective documentation, *i.e.*
            :func:`scipy.signal.periodogram` and :func:`scipy.signal.welch`
            for details.

            Default: periodogram

    Raises
    ------
    aspecd.exceptions.NotApplicableToDatasetError
        Raised if applied to a ND dataset (with N>1)


    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. The examples focus each on a single
    aspect.

    Computing the power density spectrum of a 1D dataset (let's assume you
    use a trace of pure noise for this) is quite simple:

    .. code-block:: yaml

       - kind: singleanalysis
         type: PowerDensitySpectrum
         result: power_density_spectrum

    This would simply return the power density spectrum of the data of a given
    dataset in the result assigned to the recipe-internal variable
    ``power_density_spectrum``. Note that the result is itself a calculated
    dataset, hence you can easily plot it for graphical representation and
    manual inspection:

    .. code-block:: yaml

        - kind: singleplot
          type: SinglePlotter1D
          properties:
            filename: power_density_spectrum.pdf
          apply_to: power_density_spectrum

    You may even want to calculate the power density spectrum, perform a
    polynomial fit (of first order), evaluate the polynomial for the
    coefficients obtained by the fit, and plot both together in one figure:

    .. code-block:: yaml

       - kind: singleanalysis
         type: PowerDensitySpectrum
         result: power_density_spectrum

       - kind: singleanalysis
         type: PolynomialFit
         result: coefficients
         apply_to: power_density_spectrum

       - kind: model
         type: Polynomial
         properties:
           parameters:
             coefficients: coefficients
         from_dataset: power_density_spectrum
         result: linear_fit

       - kind: multiplot
         type: MultiPlotter1D
         properties:
           filename: power_density_spectrum.pdf
         apply_to:
           - power_density_spectrum
           - linear_fit


    To have more control over the method used to calculate the power density
    spectrum, you can explicitly provide a method name here:

    .. code-block:: yaml

       - kind: singleanalysis
         type: PowerDensitySpectrum
         properties:
           parameters:
             method: welch
         result: power_density_spectrum

    Note that the methods need to reside in the :mod:`scipy.signal` module.


    .. versionadded:: 0.3

    """

    def __init__(self):
        super().__init__()
        self.description = 'Calculate power density spectrum'
        self.result = aspecd.dataset.CalculatedDataset()
        self.parameters["method"] = "periodogram"

    @staticmethod
    def applicable(dataset):
        """
        Check whether analysis step is applicable to the given dataset.

        Power density spectrum calculation can only be applied to 1D datasets.

        Parameters
        ----------
        dataset : :class:`aspecd.dataset.Dataset`
            Dataset to check

        Returns
        -------
        applicable : :class:`bool`
            Whether dataset is applicable

        """
        return dataset.data.data.ndim == 1

    def _perform_task(self):
        method = getattr(scipy.signal, self.parameters["method"])
        frequencies, psd = method(self.dataset.data.data)
        self.result.data.data = np.log10(psd[1:])
        self.result.data.axes[0].values = np.log10(frequencies[1:])
        self.result.data.axes[0].quantity = 'log frequency'
        self.result.data.axes[1].quantity = 'log power'


class PolynomialFit(SingleAnalysisStep):
    # noinspection PyUnresolvedReferences
    """
    Perform polynomial fit on 1D data.

    The coefficients obtained can be used to evaluate a model that can be
    plotted together with the data the polynomial has been fitted to
    originally. At the same time, you can tabulate the coefficients.

    Attributes
    ----------
    result : :class:`list`
        coefficients of the fitted polynomial in *increasing* order

        As the new :mod:`numpy.polynomial` package is used, particularly the
        :class:`numpy.polynomial.polynomial.Polynomial` class,
        the coefficients are given in increasing order, with the first
        element corresponding to x**0. Furthermore, the coefficients are
        given in the unscaled data domain (using the
        :meth:`numpy.polynomial.polynomial.Polynomial.convert` method).

    parameters : :class:`dict`
        All parameters necessary for this step.

        order : :class:`int`
            Order (degree) of the polynomial to be fitted to the data

            Default: 1


    Raises
    ------
    aspecd.exceptions.NotApplicableToDatasetError
        Raised if applied to a ND dataset (with N>1)


    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. The examples focus each on a single
    aspect.

    Fitting a polynomial of first order to your 1D dataset is quite simple:

    .. code-block:: yaml

       - kind: singleanalysis
         type: PolynomialFit
         result: polynomial_coefficients_1st_order

    This would simply return the polynomial coefficients (in *increasing*
    order) as a list in the result assigned to the recipe-internal variable
    ``polynomial_coefficients_1st_order``.

    If you would like to fit a polynomial of different order, simply provide
    the desired order as an additional parameter:

    .. code-block:: yaml

       - kind: singleanalysis
         type: PolynomialFit
         properties:
           parameters:
             order: 3
         result: polynomial_coefficients_3rd_order

    In this case, the result will contain a list of four coefficients of the
    fitted polynomial of third order, again in *increasing* order.


    .. versionadded:: 0.3

    """

    def __init__(self):
        super().__init__()
        self.description = 'Polynomial fit'
        self.parameters["order"] = 1

    @staticmethod
    def applicable(dataset):
        """
        Check whether analysis step is applicable to the given dataset.

        Polynomial fits can (currently) only be applied to 1D datasets.

        Parameters
        ----------
        dataset : :class:`aspecd.dataset.Dataset`
            Dataset to check

        Returns
        -------
        applicable : :class:`bool`
            Whether dataset is applicable

        """
        return dataset.data.data.ndim == 1

    def _perform_task(self):
        polynomial = np.polynomial.Polynomial.fit(
            self.dataset.data.axes[0].values,
            self.dataset.data.data,
            deg=self.parameters['order'])
        # noinspection PyUnresolvedReferences
        self.result = list(polynomial.convert().coef)


class LinearRegressionWithFixedIntercept(SingleAnalysisStep):
    # noinspection PyUnresolvedReferences
    """
    Perform linear regression with fixed intercept on 1D data

    In contrast to a regular polynomial fit of first order, where two
    parameters (slope and intercept) are fitted, there are mathematical
    models where the intercept is fixed, *i.e.* not to be fitted as well. In
    these cases, using a polynomial fit of first order is simply wrong. Of
    course, which of these approaches is valid depends on the underlying
    model and the physical reality to be modelled.

    .. note::

        A prime example of a linear model with only a slope and no intercept
        is Hooke's law stating that the force *F* needed to extend or
        compress a spring by some distance *x* scales linearly with respect
        to that distance, *i.e.*, *F* = *kx*. Here, *k* is the
        characteristic of the spring, sometimes called "spring constant".

    The approach taken here is to use linear algebra and solve the system
    of equations by calling :func:`numpy.linalg.lstsq`. In case of a
    vertical offset (*i.e.*, intercept not zero), the offset is first
    subtracted from the function values and afterwards the regression
    performed.

    Attributes
    ----------
    result : :class:`float`
        slope of the linear regression

        If you set the parameter ``polynomial_coefficients`` to True, a list
        with (fixed) intercept and (fitted) slope will be returned (see below).

    parameters : :class:`dict`
        All parameters necessary for this step.

        offset : :class:`float`
            Vertical offset of the data, *i.e.* f(0)

            Useful in cases where the model defines an intercept f(0) != 0.

            Default: 0

        polynomial_coefficients : :class:`bool`
            Whether to return both, intercept and slope for compatibility
            with polynomial model, :class:`aspecd.model.Polynomial`

            Default: False

    Raises
    ------
    aspecd.exceptions.NotApplicableToDatasetError
        Raised if applied to a ND dataset (with N>1)


    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. The examples focus each on a single
    aspect.

    Performing a linear regression without intercept to your 1D dataset is
    quite simple:

    .. code-block:: yaml

       - kind: singleanalysis
         type: LinearRegressionWithFixedIntercept
         result: slope

    Sometimes, you may have the situation that the (fixed) intercept is not
    zero, hence your data are "offset" by a scalar value. To account for
    that, provide a value for this offset, here 3.14:

    .. code-block:: yaml

       - kind: singleanalysis
         type: LinearRegressionWithFixedIntercept
         properties:
           parameters:
             offset: 3.14
         result: slope

    As you sometimes want to graphically display both, data and the
    resulting linear regression, you may use the
    :class:`aspecd.model.Polynomial` model to do just that. However,
    for this to work, you would need to get the (fixed) intercept returned
    as first coefficient as well. Here you go:

    .. code-block:: yaml

       - kind: singleanalysis
         type: LinearRegressionWithFixedIntercept
         properties:
           parameters:
             polynomial_coefficients: True
         result: regression_coefficients

    The full story may look something like that, with "experimental_data"
    referring to the actual dataset to be analysed:

    .. code-block:: yaml

       - kind: singleanalysis
         type: LinearRegressionWithFixedIntercept
         properties:
           parameters:
             polynomial_coefficients: True
         result: coefficients
         apply_to:
           - experimental_data

       - kind: model
         type: Polynomial
         properties:
           parameters:
             coefficients: coefficients
         from_dataset: experimental_data
         result: linear_regression_without_intercept

       - kind: multiplot
         type: MultiPlotter1D
         properties:
           filename: linear_regression_without_intercept.pdf
         apply_to:
           - experimental_data
           - linear_regression_without_intercept

    With this, you should have your plot with data and linear regression
    together saved in the file ``linear_regression_without_intercept.pdf``.


    .. versionadded:: 0.3

    """

    def __init__(self):
        super().__init__()
        self.description = 'Linear regression without intercept'
        self.parameters["offset"] = 0
        self.parameters["polynomial_coefficients"] = False

    @staticmethod
    def applicable(dataset):
        """
        Check whether analysis step is applicable to the given dataset.

        Polynomial fits can (currently) only be applied to 1D datasets.

        Parameters
        ----------
        dataset : :class:`aspecd.dataset.Dataset`
            Dataset to check

        Returns
        -------
        applicable : :class:`bool`
            Whether dataset is applicable

        """
        return dataset.data.data.ndim == 1

    def _perform_task(self):
        xdata = self.dataset.data.axes[0].values
        xdata = xdata[:, None]
        ydata = self.dataset.data.data - self.parameters["offset"]
        results = np.linalg.lstsq(xdata, ydata, rcond=None)
        if self.parameters["polynomial_coefficients"]:
            self.result = [self.parameters["offset"], float(results[0])]
        else:
            self.result = float(results[0])
