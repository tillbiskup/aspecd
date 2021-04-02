"""
Data processing functionality.

.. sidebar:: Processing vs. analysis steps

    The key difference between processing and analysis steps: While a
    processing step *modifies* the data of the dataset it operates on,
    an analysis step returns a result based on data of a dataset, but leaves
    the original dataset unchanged.


Key to reproducible science is automatic documentation of each processing
step applied to the data of a dataset. Such a processing step each is
self-contained, meaning it contains every necessary information to perform
the processing task on a given dataset.

Processing steps, in contrast to analysis steps (see :mod:`aspecd.analysis`
for details), not only operate on data of a :class:`aspecd.dataset.Dataset`,
but change its data. The information necessary to reproduce each processing
step gets added to the :attr:`aspecd.dataset.Dataset.history` attribute of a
dataset.

The module contains both, a base class for processing steps (
:class:`aspecd.processing.ProcessingStep`) as well as a series of generally
applicable processing steps for all kinds of spectroscopic data. The latter
are an attempt to relieve the developers of packages derived from the ASpecD
framework from the task to reinvent the wheel over and over again.

The next section gives an overview of the concrete processing steps
implemented within the ASpecD framework. For details of how to implement
your own processing steps, see the section below.


Concrete processing steps
=========================

Besides providing the basis for processing steps for the ASpecD framework,
ensuring full reproducibility and traceability, hence reproducible science
and good scientific practice, this module comes with a (growing) number of
general-purpose processing steps useful for basically all kinds of
spectroscopic data.

Here is a list as a first overview. For details, see the detailed
documentation of each of the classes, readily accessible by the link.

* :class:`aspecd.processing.Normalisation`

  Normalise data.

  There are different kinds of normalising data: maximum, minimum,
  amplitude, area

* :class:`aspecd.processing.Integration`

  Integrate data

* :class:`aspecd.processing.Differentiation`

  Differentiate data, *i.e.*, return discrete first derivative

* :class:`aspecd.processing.ScalarAlgebra`

  Perform scalar algebraic operation on one dataset.

  Operations available: add, subtract, multiply, divide (by given scalar)

* :class:`aspecd.processing.Projection`

  Project data, *i.e.* reduce dimensions along one axis.

* :class:`aspecd.processing.SliceExtraction`

  Extract slice along one dimension from dataset.

* :class:`aspecd.processing.BaselineCorrection`

  Correct baseline of dataset.

* :class:`aspecd.processing.Averaging`

  Average data over given range along given axis.


Writing own processing steps
============================

Each real processing step should inherit from
:class:`aspecd.processing.ProcessingStep` as documented there. Furthermore,
all processing steps should be contained in one module named "processing".
This allows for easy automation and replay of processing steps, particularly
in context of recipe-driven data analysis (for details, see the
:mod:`aspecd.tasks` module).


General advice
--------------

A few hints on writing own processing step classes:

* Always inherit from :class:`aspecd.processing.ProcessingStep`.

* Store all parameters, implicit and explicit, in the dict ``parameters`` of
  the :class:`aspecd.processing.ProcessingStep` class, *not* in separate
  properties of the class. Only this way, you can ensure full
  reproducibility and compatibility of recipe-driven data analysis (for
  details, see the :mod:`aspecd.tasks` module).

* Always set the ``description`` property to a sensible value.

* Always set the ``undoable`` property appropriately. In most cases,
  processing steps can be undone.

* Implement the actual processing in the ``_perform_task`` method of the
  processing step.

* Make sure to implement the
  :meth:`aspecd.processing.ProcessingStep.applicable` method according to your
  needs. Typical cases would be to check for the dimensionality of the
  underlying data, as some processing steps may work only for 1D data (or
  vice versa). Don't forget to declare this as a static method, using the
  ``@staticmethod`` decorator.

* With the ``_sanitise_parameters`` method, the input parameters are
  automatically checked and an appropriate exception can be thrown in order to
  describe the error source to the user.

Some more special cases are detailed below. For further advice, consult the
source code of this module, and have a look at the concrete processing steps
whose purpose is described below in more detail.


Changing the dimensions of your data
------------------------------------

If your processing step changes the dimensions of your data, it is your
responsibility to ensure the axes values to be consistent with the data.
Note that upon changing the dimension of your data, the axes *values* will
be reset to indices along the data dimensions. Hence, you need to *first*
make a (deep) copy of your axes, then change the dimension of your data,
and afterwards restore the remaining values from the temporarily stored axes.


Adding parameters upon processing
---------------------------------

Sometimes there is the need to persist values that are only obtained during
processing the data. A typical example may be averaging 2D data along one
dimension and wanting to store both, range of indices and actual axis units.
While in this case, typically the axis value of the centre of the averaging
window will be stored as new axis value, the other parameters should end up
in the :attr:`aspecd.processing.ProcessingStep.parameters` dictionary. Thus,
they are added to the dataset history and available for reports and alike.


Module documentation
====================

"""
import math
import operator

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
    aspecd.processing.NotApplicableToDatasetError
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
        aspecd.processing.NotApplicableToDatasetError
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
            raise aspecd.exceptions.NotApplicableToDatasetError

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

      Data are divided by their maximum value

    * minimum

      Data are divided by their minimum value

    * amplitude

      Data are divided by the difference between their maximum and minimum

    * area

      Data are divided by the sum of their *absolute* values

    You can set these kinds using the attribute :attr:`parameters["kind"]`.

    .. important::
        Before normalising your data, make sure they have a proper baseline,
        as otherwise, your normalisation will lead to strange results.

    .. note::
        Normalisation can be used for N-D data as well. In this case,
        the data as a whole are normalised accordingly.

    .. todo::
        Handle noisy data, at least for normalising to maximum, minimum,
        and amplitude.

    .. todo::
        How to handle noisy data in case of area normalisation, as this would
        probably account for double the noise if simply taking the absolute?

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
            self.dataset.data.data /= np.sum(np.abs(self.dataset.data.data))


class Integration(ProcessingStep):
    """
    Integrate data

    Currently, the data are integrated using the :func:`numpy.cumsum`
    function. This may change in the future, and you may be able to choose
    between different algorithms. A potential candidate would be using FFT/IFFT
    and performing the operation in Fourier space.

    .. note::
        N-D arrays can be integrated as well. In this case,
        :func:`np.cumsum` will operate on the last axis.

    """

    def __init__(self):
        super().__init__()
        self.undoable = True
        self.description = 'Integrate data'

    def _perform_task(self):
        dim = np.ndim(self.dataset.data.data)
        self.dataset.data.data = \
            np.cumsum(self.dataset.data.data, axis=dim - 1)


class Differentiation(ProcessingStep):
    """
    Differentiate data, *i.e.*, return discrete first derivative

    Currently, the data are differentiated using the :func:`numpy.diff`
    function. This may change in the future, and you may be able to choose
    between different algorithms. A potential candidate would be using FFT/IFFT
    and performing the operation in Fourier space.

    .. important::
        As using :func:`numpy.diff` results in a vector being one element
        shorter than the original vector, here, the last element of the
        resulting vector is appended to the result, thus being doubled.

    .. note::
        N-D arrays can be integrated as well. In this case,
        :func:`np.diff` will operate on the last axis.

    """

    def __init__(self):
        super().__init__()
        self.undoable = True
        self.description = 'Differentiate data'

    def _perform_task(self):
        self.dataset.data.data = np.diff(self.dataset.data.data)
        if self.dataset.data.data.ndim == 1:
            self.dataset.data.data = \
                np.concatenate((self.dataset.data.data,
                                self.dataset.data.data[-1]), axis=None)
        else:
            self.dataset.data.data = \
                np.concatenate((self.dataset.data.data,
                                self.dataset.data.data[:, [-1]]), axis=1)


class ScalarAlgebra(ProcessingStep):
    """Perform scalar algebraic operation on one dataset.

    To compare datasets (by eye), it might be useful to adapt its intensity
    by algebraic operations. Adding, subtracting, multiplying and dividing
    are implemented here.

    Attributes
    ----------
    parameters["kind"] : :class:`str`
        Kind of scalar algebra to use

        Valid values: "plus", "minus", "times", "by", "add", "subtract",
        "multiply", "divide", "+", "-", "*", "/"

    parameters["value"] : :class:`float`
        Parameter of the scalar algebraic operation

        Default value: 1

    Raises
    ------
    ValueError
        Raised if no or wrong kind is provided

    """

    def __init__(self):
        super().__init__()
        self.undoable = True
        self.description = 'Perform scalar algebra on one dataset.'
        self.parameters['kind'] = None
        self.parameters['value'] = 1
        self._kinds = {
            'plus': operator.add,
            'add': operator.add,
            '+': operator.add,
            'minus': operator.sub,
            'subtract': operator.sub,
            '-': operator.sub,
            'times': operator.mul,
            'multiply': operator.mul,
            '*': operator.mul,
            'by': operator.truediv,
            'divide': operator.truediv,
            '/': operator.truediv
        }

    def _perform_task(self):
        if not self.parameters['kind']:
            raise ValueError('No kind of scalar operation given')
        if self.parameters['kind'].lower() not in self._kinds:
            raise ValueError('Scalar operation "%s" not understood'
                             % self.parameters['kind'])
        operator_ = self._kinds[self.parameters['kind'].lower()]
        self.dataset.data.data = operator_(self.dataset.data.data,
                                           self.parameters['value'])


class Projection(ProcessingStep):
    """
    Project data, *i.e.* reduce dimensions along one axis.

    There is many reasons to project along one axis, if nothing else
    increasing signal-to-noise ratio if multiple scans have been recorded as
    2D dataset.

    Attributes
    ----------
    parameters["axis"] : :class:`int`
        Axis to average along

        Default value: 0

    Raises
    ------
    aspecd.exceptions.NotApplicableToDatasetError
        Raised if dataset has not enough dimensions

    IndexError
        Raised if axis is out of bounds for given dataset

    """

    def __init__(self):
        super().__init__()
        self.undoable = True
        self.description = \
            'Project data, i.e. reduce dimensions along one axis.'
        self.parameters['axis'] = 0

    @staticmethod
    def applicable(dataset):
        """
        Check whether processing step is applicable to the given dataset.

        Projection is only applicable to datasets with data of at least two
        dimensions.

        Parameters
        ----------
        dataset : :class:`aspecd.dataset.Dataset`
            dataset to check

        Returns
        -------
        applicable : :class:`bool`
            `True` if successful, `False` otherwise.

        """
        return len(dataset.data.axes) > 2

    def _perform_task(self):
        if self.parameters['axis'] > self.dataset.data.data.ndim - 1:
            raise IndexError("Axis %i out of bounds" % self.parameters['axis'])
        self.dataset.data.data = np.average(self.dataset.data.data,
                                            axis=self.parameters['axis'])
        del self.dataset.data.axes[self.parameters['axis']]


class SliceExtraction(ProcessingStep):
    """
    Extract slice along one dimension from dataset.

    With multidimensional datasets, there are use cases where you would like
    to operate only on a slice along a particular axis. One example may be
    to compare first and last trace of a 2D dataset.

    .. important::
        Currently, slice extraction works *only* for **2D** datasets,
        not for higher-dimensional datasets. This may, however, change in
        the future.

    Attributes
    ----------
    parameters["index"] : :class:`int`
        Index of the slice to extract

        If no index is provided or the given index is out of bounds for the
        given axis, an IndexError is raised.

    parameters["axis"] : :class:`int`
        Axis to average along

        Default value: 0

    Raises
    ------
    aspecd.exceptions.NotApplicableToDatasetError
        Raised if dataset has not enough dimensions

    IndexError
        Raised if index is out of bounds for given axis

        Raised if axis is out of bounds for given dataset

    """

    def __init__(self):
        super().__init__()
        self.undoable = True
        self.description = 'Extract slice from dataset'
        self.parameters['index'] = None
        self.parameters['axis'] = 0

    @staticmethod
    def applicable(dataset):
        """
        Check whether processing step is applicable to the given dataset.

        Projection is only applicable to datasets with two-dimensional data.

        Parameters
        ----------
        dataset : :class:`aspecd.dataset.Dataset`
            dataset to check

        Returns
        -------
        applicable : :class:`bool`
            `True` if successful, `False` otherwise.

        """
        return len(dataset.data.axes) == 3

    def _perform_task(self):
        if not self.parameters['index']:
            raise IndexError('No index provided for slice extraction')
        if self.parameters['index'] > self.dataset.data.data.shape[0]:
            raise IndexError('Index %i out of bounds' % self.parameters[
                'index'])
        if self.parameters['axis'] > self.dataset.data.data.ndim - 1:
            raise IndexError("Axis %i out of bounds" % self.parameters['axis'])

        if self.parameters['axis'] == 0:
            self.dataset.data.data = \
                self.dataset.data.data[self.parameters['index'], :]
        else:
            self.dataset.data.data = \
                self.dataset.data.data[:, self.parameters['index']]
        del self.dataset.data.axes[self.parameters['axis'] + 1]


class BaselineCorrection(ProcessingStep):
    # noinspection PyUnresolvedReferences
    """
    Subtract baseline from dataset.

    Currently, only polynomial baseline corrections are supported.

    The coefficients used to calculate the baseline will be written to the
    ``parameters`` dictionary upon processing.

    If no order is explicitly given, a polynomial baseline of zeroth order
    will be used.

    .. important::
        Baseline correction works *only* for **1D and 2D** datasets,
        not for higher-dimensional datasets.

    Attributes
    ----------
    parameters : :class:`dict`
        All parameters necessary for this step.

        kind : :class:`str`
            The kind of baseline correction to be performed.

            Default: polynomial

        order : :class:`int`
            The order for the baseline correction if no coefficients are given.

            Default: 0

        fit_area :
            Parts of the spectrum to be considered as baseline, can be given
            as list or single number. If one number is given, it takes that
            percentage from both sides, respectively, i.e. 10 means 10% left
            and 10% right. If a list of two numbers is provided,
            the corresponding percentages are taken from each side of the
            spectrum, i.e. ``[5, 20]`` takes 5% from the left side and 20%
            from the right.

            Default: [10, 10]

        coefficients:
            Coefficients used to calculate the baseline.

        axis : :class:`int`
            Axis along which to perform the baseline correction.

            Only necessary in case of 2D data.

            Default: 0

        """

    def __init__(self):
        super().__init__()
        self.undoable = True
        self.description = 'Correct baseline of dataset'
        self.parameters['kind'] = 'polynomial'
        self.parameters['order'] = 0
        self.parameters['coefficients'] = []
        self.parameters['fit_area'] = [10, 10]
        self.parameters['axis'] = 0
        self._data_points_left = None
        self._data_points_right = None
        self._axis_values = []
        self._intensity_values = []

    @staticmethod
    def applicable(dataset):
        """
        Check whether processing step is applicable to the given dataset.

        Baseline correction is (currently) only applicable to datasets with
        one-dimensional data.

        Parameters
        ----------
        dataset : :class:`aspecd.dataset.Dataset`
            dataset to check

        Returns
        -------
        applicable : :class:`bool`
            `True` if successful, `False` otherwise.

        """
        return len(dataset.data.axes) < 4

    def _sanitise_parameters(self):
        if isinstance(self.parameters['fit_area'], (float, int)):
            fit_area = self.parameters['fit_area']
            self.parameters['fit_area'] = [fit_area, fit_area]
        if isinstance(self.parameters['fit_area'], list) \
                and len(self.parameters['fit_area']) == 1:
            fit_area = self.parameters['fit_area'][0]
            self.parameters['fit_area'] = [fit_area, fit_area]

    def _perform_task(self):
        self._get_fit_range()
        self._get_axis_values()
        if self._is_n_dimensional():
            axis = 1 if self.parameters["axis"] == 0 else 0
            if self.parameters["axis"] == 0:
                for idx in range(self.dataset.data.data.shape[axis]):
                    self._get_intensity_values(self.dataset.data.data[:, idx])
                    values_to_subtract = self._get_values_to_subtract()
                    self.dataset.data.data[:, idx] -= values_to_subtract
            else:
                for idx in range(self.dataset.data.data.shape[axis]):
                    self._get_intensity_values(self.dataset.data.data[idx, :])
                    values_to_subtract = self._get_values_to_subtract()
                    self.dataset.data.data[idx, :] -= values_to_subtract
        else:
            self._get_intensity_values(self.dataset.data.data)
            values_to_subtract = self._get_values_to_subtract()
            self.dataset.data.data -= values_to_subtract

    def _get_fit_range(self):
        number_of_points = len(self.dataset.data.data)
        self._data_points_left = \
            math.ceil(number_of_points * self.parameters["fit_area"][0] / 100.0)
        self._data_points_right = \
            math.ceil(number_of_points * self.parameters["fit_area"][1] / 100.0)

    def _get_axis_values(self):
        axis = self.parameters["axis"]
        self._axis_values = np.concatenate(
            (self.dataset.data.axes[axis].values[:self._data_points_left],
             self.dataset.data.axes[axis].values[-self._data_points_right:])
        )

    def _get_intensity_values(self, data):
        self._intensity_values = np.concatenate(
            (data[:self._data_points_left],
             data[-self._data_points_right:])
        )

    # noinspection PyUnresolvedReferences,PyCallingNonCallable
    def _get_values_to_subtract(self):
        polynomial = np.polynomial.Polynomial.fit(self._axis_values,
                                                  self._intensity_values,
                                                  self.parameters['order'])
        self.parameters['coefficients'] = polynomial.coef
        axis = self.parameters["axis"]
        return polynomial(self.dataset.data.axes[axis].values)

    def _is_n_dimensional(self):
        return len(self.dataset.data.axes) > 2


class Averaging(ProcessingStep):
    # noinspection PyUnresolvedReferences
    """
    Average data over given range along given axis.

    .. important::
        Currently, baseline correction works *only* for **2D** datasets,
        not for higher-dimensional datasets. This may, however, change in
        the future.

    .. todo::
        Implement averaging with range given in axis values rather than indices.

    Attributes
    ----------
    parameters : :class:`dict`
        All parameters necessary for this step.

        axis : :class:`int`
            The axis to average along.

            Default: 0

        range : :class:`list`
            The range (start, end) to average over.

            Default: []

    Raises
    ------
    ValueError
        Raised if range is out of range for given axis or empty

    IndexError
        Raised if axis is out of bounds for given dataset

    """

    def __init__(self):
        super().__init__()
        self.undoable = True
        self.description = \
            'Average data over given range along given axis.'
        self.parameters["range"] = None
        self.parameters['axis'] = 0

    @staticmethod
    def applicable(dataset):
        """
        Check whether processing step is applicable to the given dataset.

        Averaging is only applicable to datasets with data of at least two
        dimensions.

        Parameters
        ----------
        dataset : :class:`aspecd.dataset.Dataset`
            dataset to check

        Returns
        -------
        applicable : :class:`bool`
            `True` if successful, `False` otherwise.

        """
        return len(dataset.data.axes) == 3

    def _sanitise_parameters(self):
        if not self.parameters["range"]:
            raise ValueError("No range given in parameters to average over.")
        if self.parameters['axis'] > self.dataset.data.data.ndim - 1:
            raise IndexError("Axis %i out of bounds" % self.parameters['axis'])
        if self._out_of_range():
            raise ValueError("Given range out of axis range.")

    def _perform_task(self):
        range_ = self.parameters["range"]
        if self.parameters["axis"] == 0:
            self.dataset.data.data = \
                np.average(self.dataset.data.data[range_[0]:range_[1], :],
                           axis=self.parameters["axis"])
        else:
            self.dataset.data.data = \
                np.average(self.dataset.data.data[:, range_[0]:range_[1]],
                           axis=self.parameters["axis"])
        del self.dataset.data.axes[self.parameters['axis']]

    def _out_of_range(self):
        out_of_range = False
        if self.parameters["range"][0] < 0:
            out_of_range = True
        elif self.parameters["range"][1] > \
                self.dataset.data.data.shape[self.parameters["axis"]]:
            out_of_range = True
        return out_of_range
