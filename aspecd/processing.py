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

Generally, two types of processing steps can be distinguished:

* Processing steps for handling single datasets

  Shall be derived from :class:`aspecd.processing.SingleProcessingStep`.

* Processing steps for handling multiple datasets

  Shall be derived from :class:`aspecd.processing.MultiProcessingStep`.

In the first case, the processing is usually handled using the
:meth:`processing` method of the respective :obj:`aspecd.dataset.Dataset`
object. Additionally, those processing steps always only operate on the data
of a single dataset. Processing steps handling single datasets should always
inherit from the :class:`aspecd.processing.SingleProcessingStep` class.

In the second case, the processing step is handled using the :meth:`processing`
method of the :obj:`aspecd.processing.ProcessingStep` object, and the datasets
are stored as a list within the processing step. As these processing steps span
several datasets. Processing steps handling multiple datasets should
always inherit from the :class:`aspecd.processing.MultiProcessingStep` class.

The module contains both, base classes for processing steps (as detailed
above) as well as a series of generally applicable processing steps for all
kinds of spectroscopic data. The latter are an attempt to relieve the
developers of packages derived from the ASpecD framework from the task to
reinvent the wheel over and over again.

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


Processing steps operating on individual datasets
-------------------------------------------------

The following processing steps operate each on individual datasets
independently.

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

* :class:`aspecd.processing.ScalarAxisAlgebra`

  Perform scalar algebraic operation on axis values of a dataset.

  Operations available: add, subtract, multiply, divide, power (by given scalar)

* :class:`aspecd.processing.DatasetAlgebra`

  Perform scalar algebraic operation on two datasets.

  Operations available: add, subtract

* :class:`aspecd.processing.Projection`

  Project data, *i.e.* reduce dimensions along one axis.

* :class:`aspecd.processing.SliceExtraction`

  Extract slice along one or more dimensions from dataset.

* :class:`aspecd.processing.SliceRemoval`

  Remove slice along one or more dimensions from dataset.

* :class:`aspecd.processing.SliceRearrangement`

  Rearrange slices of a dataset along one dimension.

* :class:`aspecd.processing.RangeExtraction`

  Extract range of data from a dataset.

* :class:`aspecd.processing.BaselineCorrection`

  Correct baseline of dataset.

* :class:`aspecd.processing.Averaging`

  Average data over given range along given axis.

* :class:`aspecd.processing.Interpolation`

  Interpolate data.

* :class:`aspecd.processing.Filtering`

  Filter data.

* :class:`aspecd.processing.Noise`

  Add (coloured) noise to data.

* :class:`aspecd.processing.Denoising1DSVD`

  Denoise 1D data using singular value decomposition (SVD).

* :class:`aspecd.processing.ChangeAxesValues`

  Change values of individual axes.

* :class:`aspecd.processing.RelativeAxis`

  Create relative axis, centred about a given value.


Processing steps operating on multiple datasets at once
-------------------------------------------------------

The following processing steps operate each on more than one dataset at the
same time, requiring at least two datasets as an input to work.

* :class:`aspecd.processing.CommonRangeExtraction`

  Extract the common range of data for multiple datasets using interpolation.

  Useful (and often necessary) for performing algebraic operations on datasets.


Writing own processing steps
============================

Each real processing step should inherit from either
:class:`aspecd.processing.SingleProcessingStep` in case of operating on a
single dataset only or from :class:`aspecd.processing.MultiProcessingStep` in
case of operating on several datasets at once. Furthermore, all processing
steps should be contained in one module named "processing". This allows for
easy automation and replay of processing steps, particularly in context of
recipe-driven data analysis (for details, see the :mod:`aspecd.tasks` module).


General advice
--------------

A few hints on writing own processing step classes:

* Always inherit from :class:`aspecd.processing.SingleProcessingStep` or
  :class:`aspecd.processing.MultiProcessingStep`, depending on your needs.

* Store all parameters, implicit and explicit, in the dict ``parameters`` of
  the :class:`aspecd.processing.ProcessingStep` class, *not* in separate
  properties of the class. Only this way, you can ensure full
  reproducibility and compatibility of recipe-driven data analysis (for
  details of the latter, see the :mod:`aspecd.tasks` module).

* Always set the ``description`` property to a sensible value.

* Always set the ``undoable`` property appropriately. In most cases,
  processing steps can be undone.

* Implement the actual processing in the ``_perform_task`` method of the
  processing step. For sanitising parameters and checking general
  applicability of the processing step to the dataset(s) at hand, continue
  reading.

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


Changing the length of your data
--------------------------------

When changing the length of the data, always change the corresponding axes
values *first*, and only afterwards the data, as changing the data will
change the axes values and adjust their length to the length of the
corresponding dimension of the data.


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

import copy
import logging
import math
import operator

import numpy as np
import scipy.ndimage
import scipy.signal
from scipy import interpolate

import bibrecord.record as bib

import aspecd.exceptions
import aspecd.history
import aspecd.utils

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class ProcessingStep(aspecd.utils.ToDictMixin):
    """Base class for processing steps.

    Each class actually performing a processing step should inherit from this
    class. Furthermore, all parameters, implicit and explicit, necessary to
    perform the processing step, should eventually be stored in the property
    "self.parameters" (currently a dictionary).

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

    .. note::
        Usually, you will never implement an instance of this class for
        actual processing tasks, but rather one of the child classes, namely
        :class:`aspecd.processing.SingleProcessingStep` and
        :class:`aspecd.processing.MultiProcessingStep`, depending on whether
        your processing step operates on a single dataset or requires
        multiple datasets.

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

    references : :class:`list`
        List of references with relevance for the implementation of the
        processing step.

        Use appropriate record types from the `bibrecord package
        <https://bibrecord.docs.till-biskup.de/>`_.

    Raises
    ------
    aspecd.exceptions.NotApplicableToDatasetError
        Raised when processing step is not applicable to dataset
    aspecd.exceptions.MissingDatasetError
        Raised when no dataset exists to act on


    .. versionchanged:: 0.4
        New attribute :attr:`references`

    """

    def __init__(self):
        super().__init__()
        self.undoable = False
        self.name = aspecd.utils.full_class_name(self)
        self.parameters = {}
        self.info = {}
        self.description = "Abstract processing step"
        self.comment = ""
        self.references = []
        self.__kind__ = "processing"
        self._exclude_from_to_dict = [
            "undoable",
            "name",
            "description",
            "references",
        ]

    def process(self):
        """Perform the actual processing step.

        The actual processing step should be implemented within the non-public
        method :meth:`_perform_task`. Besides that, the applicability of the
        processing step to the given dataset(s) will be checked
        automatically using the non-public method :meth:`_check_applicability`,
        default parameter values will be set calling the non-public method
        :meth:`_set_defaults`, and the parameters will be sanitised by
        calling the non-public method :meth:`_sanitise_parameters` prior to
        calling :meth:`_perform_task`.

        """
        self._check_applicability()
        self._set_defaults()
        self._sanitise_parameters()
        self._perform_task()

    # noinspection PyUnusedLocal
    @staticmethod
    def applicable(dataset):  # pylint: disable=unused-argument
        """Check whether processing step is applicable to the given dataset.

        Returns `True` by default and needs to be implemented in classes
        inheriting from SingleProcessingStep according to their needs.

        This is a static method that gets called automatically by each class
        inheriting from :class:`aspecd.processing.SingleProcessingStep`. Hence,
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

    def _check_applicability(self):
        """Check that processing step is applicable to dataset(s)

        Needs to be implemented in classes inheriting from ProcessingStep
        according to their needs.

        """

    def _set_defaults(self):
        """Set default values for parameters.

        Needs to be implemented in classes inheriting from ProcessingStep
        according to their needs. Note that this method will be called after
        checking for general applicability, but before sanitising
        parameters. Therefore, you can set default parameters and afterwards
        continue with sanitising as usual.

        """

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


class SingleProcessingStep(ProcessingStep):
    """Base class for processing steps operating on single datasets.

    Each class actually performing a processing step involving only a
    single dataset should inherit from this class. Furthermore,
    all parameters, implicit and explicit, necessary to perform the
    processing step, should eventually be stored in the property
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
    dataset : :class:`aspecd.dataset.Dataset`
        Dataset the processing step should be performed on

    Raises
    ------
    aspecd.exceptions.NotApplicableToDatasetError
        Raised when processing step is not applicable to dataset
    aspecd.exceptions.MissingDatasetError
        Raised when no dataset exists to act on

    """

    def __init__(self):
        super().__init__()
        self.description = "Abstract singleprocessing step"
        self.dataset = None

    def to_dict(self, remove_empty=False):
        """
        Create dictionary containing public attributes of an object.

        In this particular case, the key "dataset" from the top level of the
        resulting dictionary will be removed, but not keys with the same
        name on lower levels of the resulting dict.

        Parameters
        ----------
        remove_empty : :class:`bool`
            Whether to remove keys with empty values

            Default: False

        Returns
        -------
        public_attributes : :class:`collections.OrderedDict`
            Ordered dictionary containing the public attributes of the object

            The order of attribute definition is preserved

        """
        dict_ = super().to_dict(remove_empty=remove_empty)
        # noinspection PyUnresolvedReferences
        dict_.pop("dataset")
        return dict_

    def process(self, dataset=None, from_dataset=False):
        """Perform the actual processing step on the given dataset.

        If no dataset is provided at method call, but is set as property in
        the SingleProcessingStep object,
        the :meth:`aspecd.dataset.Dataset.process` method of the dataset
        will be called and thus the history written.

        If no dataset is provided at method call nor as property in the
        object, the method will raise a respective exception.

        The :obj:`aspecd.dataset.Dataset` object always call this method with
        the respective dataset as argument. Therefore, in this case setting
        the dataset property within the
        :obj:`aspecd.processing.SingleProcessingStep` object is not necessary.

        The actual processing step should be implemented within the non-public
        method :meth:`_perform_task`. Besides that, the applicability of the
        processing step to the given dataset(s) will be checked
        automatically using the non-public method :meth:`_check_applicability`,
        default parameter values will be set calling the non-public method
        :meth:`_set_defaults`, and the parameters will be sanitised by
        calling the non-public method :meth:`_sanitise_parameters` prior to
        calling :meth:`_perform_task`.

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
        aspecd.exceptions.NotApplicableToDatasetError
            Raised when processing step is not applicable to dataset
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
            self.dataset.process(self)
        else:
            super().process()

    def _check_applicability(self):
        if not self.applicable(self.dataset):
            message = (
                f"{self.name} not applicable to dataset with id "
                f"{self.dataset.id}"
            )
            raise aspecd.exceptions.NotApplicableToDatasetError(
                message=message
            )

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
            package=self.dataset.package_name, processing_step=self
        )
        return history_record


class MultiProcessingStep(ProcessingStep):
    """Base class for processing steps operating on multiple datasets.

    Each class actually performing a processing step involving multiple
    datasets should inherit from this class. Furthermore,
    all parameters, implicit and explicit, necessary to perform the
    processing step, should eventually be stored in the property
    "self.parameters" (currently a dictionary).

    To perform the processing step, call the :meth:`process` method
    directly. This will take care of writing the history to each individual
    dataset as well.

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
    datasets : :class:`list`
        List of :class:`aspecd.dataset.Dataset` objects the processing step
        should act on

    Raises
    ------
    aspecd.exceptions.NotApplicableToDatasetError
        Raised when processing step is not applicable to dataset
    aspecd.exceptions.MissingDatasetError
        Raised when no dataset exists to act on


    .. versionadded:: 0.2

    """

    def __init__(self):
        super().__init__()
        self.description = "Abstract multiprocessing step"
        self.datasets = []
        self.__kind__ = "multiprocessing"
        self._exclude_from_to_dict.extend(["datasets"])

    def process(self):
        """Perform the actual processing step.

        The actual processing step should be implemented within the non-public
        method :meth:`_perform_task`. Besides that, the applicability of the
        processing step to the given dataset(s) will be checked
        automatically using the non-public method :meth:`_check_applicability`,
        default parameter values will be set calling the non-public method
        :meth:`_set_defaults`, and the parameters will be sanitised by
        calling the non-public method :meth:`_sanitise_parameters` prior to
        calling :meth:`_perform_task`.

        Raises
        ------
        aspecd.exceptions.NotApplicableToDatasetError
            Raised when processing step is not applicable to dataset
        aspecd.exceptions.MissingDatasetError
            Raised when no dataset exists to act on

        """
        if not self.datasets:
            raise aspecd.exceptions.MissingDatasetError
        super().process()
        history_record = self.create_history_record()
        for dataset in self.datasets:
            dataset.append_history_record(history_record)

    def _check_applicability(self):
        for dataset in self.datasets:
            if not self.applicable(dataset):
                message = (
                    f"{self.name} not applicable to dataset with id "
                    f"{dataset.id}"
                )
                raise aspecd.exceptions.NotApplicableToDatasetError(
                    message=message
                )

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
            package=self.datasets[0].package_name, processing_step=self
        )
        return history_record


class Normalisation(SingleProcessingStep):
    # noinspection PyUnresolvedReferences
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

      Data are divided by the sum of their *absolute* values, the number of
      points is also taken into account.

    You can set these kinds using the attribute :attr:`parameters["kind"]`.

    .. important::
        Before normalising your data, make sure they have a proper baseline,
        as otherwise, your normalisation will lead to strange results.

    .. note::
        Normalisation can be used for N-D data as well. In this case,
        the data as a whole are normalised accordingly.

    .. todo::
        How to handle noisy data in case of area normalisation, as this would
        probably account for double the noise if simply taking the absolute?

    Attributes
    ----------
    parameters : :class:`dict`
        All parameters necessary for this step.

        kind : :class:`str`
            Kind of normalisation to use

            Valid values: "maximum", "minimum", "amplitude", "area"

            Note that the first three can be abbreviated, everything containing
            "max", "min", "amp" will be understood respectively.

            Defaults to "maximum"

        range : :class:`list`
            Range of the data of the dataset to normalise for.

            This can be quite useful if you want to normalise for a specific
            feature, *e.g.* an artifact that you've recorded separately and
            want to subtract from the data, or more generally to normalise
            to certain features of your data irrespective of other parts.

            Ranges can be given as indices or in axis units, and for ND
            datasets, you need to provide as many ranges as dimensions of
            your data. Units default to indices, but can be specified using
            the parameter ``range_unit``, see below.

            As internally, :class:`RangeExtraction` is used, see there for
            more details of how to provide ranges.

        range_unit : :class:`str`
            Unit used for the range.

            Can be either "index" (default) or "axis".

        noise_range : :class:`list`
            Data range to use for determining noise level

            If provided, the normalisation will account for the noise in
            case of normalising to minimum, maximum, and amplitude.

            In case of ND datasets with N>1, you need to provide as many
            ranges as dimensions of your data.

            Numbers are interpreted by default as percentage.

            Default: None

        noise_range_unit : :class:`str`
            Unit for specifying noise range

            Valid units are "index", "axis", "percentage", with the latter
            being default. As internally, :class:`RangeExtraction` gets
            used, see there for further details.

            Default: percentage


    Raises
    ------
    ValueError :
        Raised if unknown kind is provided


    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. The examples focus each on a single
    aspect.

    In the simplest case, just invoke the normalisation with default values:

    .. code-block:: yaml

       - kind: processing
         type: Normalisation

    This will normalise your data to their maximum.

    Sometimes, normalising to maximum is not what you need, hence you can
    control in more detail the criterion using the appropriate parameter:

    .. code-block:: yaml

       - kind: processing
         type: Normalisation
         properties:
           parameters:
             kind: amplitude

    In this case, you would normalise to the amplitude, meaning setting the
    difference between minimum and maximum to one. For other kinds, see above.

    If you want to normalise not over the entire range of the dataset,
    but only over a dedicated range, simply provide the necessary parameters:

    .. code-block:: yaml

       - kind: processing
         type: Normalisation
         properties:
           parameters:
             range: [50, 150]

    In this case, we assume a 1D dataset and use indices, requiring the data
    to span at least over 150 points. Of course, it is often more convenient
    to provide axis units. Here you go:

    .. code-block:: yaml

       - kind: processing
         type: Normalisation
         properties:
           parameters:
             range: [340, 350]
             range_unit: axis

    And in case of ND datasets with N>1, make sure to provide as many ranges
    as dimensions of your dataset, in case of a 2D dataset:

    .. code-block:: yaml

       - kind: processing
         type: Normalisation
         properties:
           parameters:
             range:
               - [50, 150]
               - [30, 40]

    Here as well, the range can be given in indices or axis units,
    but defaults to indices if no unit is explicitly given.

    .. note::
        A note for developers: If you inherit from this class and plan to
        implement further kinds of normalisation, first test for your
        specific kind of normalisation, and in the ``else`` block add a call
        to ``super()._perform_task()``. This way, you ensure the
        :class:`ValueError` will still be raised in case of an unknown kind.


    .. versionadded:: 0.2
       Normalising over range of data

    .. versionadded:: 0.2
       Accounting for noise for ND data with N>1

    .. versionchanged:: 0.2
       noise_range changed to list from integer

    """

    def __init__(self):
        super().__init__()
        self.undoable = True
        self.description = "Normalise data"
        self.parameters["kind"] = "maximum"
        self.parameters["range"] = None
        self.parameters["range_unit"] = "index"
        self.parameters["noise_range"] = None
        self.parameters["noise_range_unit"] = "percentage"
        self._noise_amplitude = 0

    def _perform_task(self):
        self._determine_noise_amplitude()
        if self.parameters["range"]:
            range_extraction = RangeExtraction()
            range_extraction.parameters["range"] = self.parameters["range"]
            range_extraction.parameters["unit"] = self.parameters[
                "range_unit"
            ]
            dataset_copy = copy.deepcopy(self.dataset)
            dataset_copy.process(range_extraction)
            data = dataset_copy.data.data
        else:
            data = self.dataset.data.data
        if "max" in self.parameters["kind"].lower():
            self.dataset.data.data /= data.max() - self._noise_amplitude / 2
            self.dataset.data.axes[-1].unit = ""
        elif "min" in self.parameters["kind"].lower():
            self.dataset.data.data /= (
                abs(data.min()) - self._noise_amplitude / 2
            )
            self.dataset.data.axes[-1].unit = ""
        elif "amp" in self.parameters["kind"].lower():
            self.dataset.data.data /= (
                data.max() - data.min()
            ) - self._noise_amplitude
            self.dataset.data.axes[-1].unit = ""
        elif "area" in self.parameters["kind"].lower():
            # might be written better
            self.dataset.data.data /= np.sum(np.abs(data)) / data.shape[0]
            self.dataset.data.data /= np.sum(np.abs(data))
            self.dataset.data.axes[-1].unit = ""
        else:
            raise ValueError(
                f'Kind {self.parameters["kind"]} not recognised.'
            )

    def _determine_noise_amplitude(self):
        if self.parameters["noise_range"]:
            range_extraction = RangeExtraction()
            range_extraction.parameters["unit"] = self.parameters[
                "noise_range_unit"
            ]
            range_extraction.parameters["range"] = self.parameters[
                "noise_range"
            ]
            dataset_copy = copy.deepcopy(self.dataset)
            dataset_copy.process(range_extraction)
            data_range = dataset_copy.data.data
            self._noise_amplitude = data_range.max() - data_range.min()


class Integration(SingleProcessingStep):
    """
    Integrate data

    Currently, the data are integrated using the :func:`numpy.cumsum`
    function. This may change in the future, and you may be able to choose
    between different algorithms. A potential candidate would be using FFT/IFFT
    and performing the operation in Fourier space.

    .. note::
        N-D arrays can be integrated as well. In this case,
        :func:`np.cumsum` will operate on the last axis.


    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. The examples focus each on a single
    aspect.

    As currently, there are no parameters you can set, integrating is as
    simple as this:

    .. code-block:: yaml

       - kind: processing
         type: Integration

    """

    def __init__(self):
        super().__init__()
        self.undoable = True
        self.description = "Integrate data"

    def _perform_task(self):
        dim = np.ndim(self.dataset.data.data)
        self.dataset.data.data = np.cumsum(
            self.dataset.data.data, axis=dim - 1
        )


class Differentiation(SingleProcessingStep):
    """
    Differentiate data, *i.e.*, return discrete first derivative

    Currently, the data are differentiated using the :func:`numpy.gradient`
    function. This may change in the future, and you may be able to choose
    between different algorithms. A potential candidate would be using FFT/IFFT
    and performing the operation in Fourier space.

    .. note::
        N-D arrays can be differentiated as well. In this case,
        differentiation will operate on the last axis.


    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. The examples focus each on a single
    aspect.

    As currently, there are no parameters you can set, differentiating is as
    simple as this:

    .. code-block:: yaml

       - kind: processing
         type: Differentiation


    .. versionchanged:: 0.3
       Method changed from :func:`numpy.diff` to :func:`numpy.gradient`

    """

    def __init__(self):
        super().__init__()
        self.undoable = True
        self.description = "Differentiate data"

    def _perform_task(self):
        if self.dataset.data.data.ndim == 1:
            self.dataset.data.data = np.gradient(self.dataset.data.data)
        else:
            self.dataset.data.data = np.gradient(self.dataset.data.data)[0]


class ScalarAlgebra(SingleProcessingStep):
    # noinspection PyUnresolvedReferences
    """Perform scalar algebraic operation on one dataset.

    To compare datasets (by eye), it might be useful to adapt their intensity
    by algebraic operations. Adding, subtracting, multiplying and dividing
    are implemented here.

    Attributes
    ----------
    parameters : :class:`dict`
        All parameters necessary for this step.

        kind : :class:`str`
            Kind of scalar algebra to use

            Valid values: "plus", "minus", "times", "by", "add", "subtract",
            "multiply", "divide", "+", "-", "*", "/"

        value : :class:`float`
            Parameter of the scalar algebraic operation

            Default value: 1.0

    Raises
    ------
    ValueError
        Raised if no or wrong kind is provided


    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. The examples focus each on a single
    aspect.

    In case you would like to add a fixed value of 42 to your dataset:

    .. code-block:: yaml

       - kind: processing
         type: ScalarAlgebra
         properties:
           parameters:
             kind: add
             value: 42

    Similarly, you could use "minus", "times", "by", "add", "subtract",
    "multiply", or "divide" as kind - resulting in the given algebraic
    operation.

    """

    def __init__(self):
        super().__init__()
        self.undoable = True
        self.description = "Perform scalar algebra on one dataset."
        self.parameters["kind"] = None
        self.parameters["value"] = 1.0
        self._kinds = {
            "plus": operator.add,
            "add": operator.add,
            "+": operator.add,
            "minus": operator.sub,
            "subtract": operator.sub,
            "-": operator.sub,
            "times": operator.mul,
            "multiply": operator.mul,
            "*": operator.mul,
            "by": operator.truediv,
            "divide": operator.truediv,
            "/": operator.truediv,
        }

    def _sanitise_parameters(self):
        if not self.parameters["kind"]:
            raise ValueError("No kind of scalar operation given")
        if self.parameters["kind"].lower() not in self._kinds:
            # pylint: disable=consider-using-f-string
            raise ValueError(
                'Scalar operation "%s" not understood'
                % self.parameters["kind"]
            )

    def _perform_task(self):
        operator_ = self._kinds[self.parameters["kind"].lower()]
        self.dataset.data.data = operator_(
            self.dataset.data.data, self.parameters["value"]
        )


class Projection(SingleProcessingStep):
    # noinspection PyUnresolvedReferences
    """
    Project data, *i.e.* reduce dimensions along one axis.

    There is many reasons to project along one axis, if nothing else
    increasing signal-to-noise ratio if multiple scans have been recorded as
    2D dataset.

    While projection can be considered a special case of averaging as
    performed by :class:`aspecd.processing.Averaging` and using the whole
    range of one axis, averaging is usually performed over part of an axis
    only. Hence, projection is semantically different and therefore
    implemented as a separate processing step.

    Attributes
    ----------
    parameters : :class:`dict`
        All parameters necessary for this step.

        axis : :class:`int`
            Axis to average along

            Default value: 0

    Raises
    ------
    aspecd.exceptions.NotApplicableToDatasetError
        Raised if dataset has not enough dimensions

    IndexError
        Raised if axis is out of bounds for given dataset


    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. The examples focus each on a single
    aspect.

    In the simplest case, just invoke the projection with default values:

    .. code-block:: yaml

       - kind: processing
         type: Projection

    This will project the data along the first axis (index 0), yielding a 1D
    dataset.

    If you would like to project along the second axis (index 1), simply set
    the appropriate parameter:

    .. code-block:: yaml

       - kind: processing
         type: Projection
         properties:
           parameters:
             axis: 1

    This will project the data along the second axis (index 1), yielding a 1D
    dataset.

    """

    def __init__(self):
        super().__init__()
        self.undoable = True
        self.description = (
            "Project data, i.e. reduce dimensions along one axis."
        )
        self.parameters["axis"] = 0

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
        self.dataset.data.data = np.average(
            self.dataset.data.data, axis=self.parameters["axis"]
        )
        del self.dataset.data.axes[self.parameters["axis"]]

    def _sanitise_parameters(self):
        if self.parameters["axis"] > self.dataset.data.data.ndim - 1:
            raise IndexError(f"Axis {self.parameters['axis']} out of bounds")


class SliceExtraction(SingleProcessingStep):
    # noinspection PyUnresolvedReferences
    """
    Extract slice along one or more dimensions from dataset.

    With multidimensional datasets, there are use cases where you would like
    to operate only on a slice along a particular axis. One example may be
    to compare the first and last trace of a 2D dataset.

    Note that "slice" can be anything from 1D to a ND array with at least
    one dimension less than the original array. If you want to extract a 1D
    slice from a ND dataset with N>2, you need to provide N-1 values for
    ``position`` and ``axis``. Make sure to always provide as many values
    for ``position`` than you provide for ``axis``.

    You can either provide indices or axis values for ``position``. For the
    latter, set the parameter "unit" accordingly. For details, see below.

    Attributes
    ----------
    parameters : :class:`dict`
        All parameters necessary for this step.

        axis :
            Index of the axis or list of indices of the axes to take the
            position from to extract the slice

            If you provide a list of axes, you need to provide as many
            positions as axes.

            If an invalid axis is provided, an IndexError is raised.

            Default: 0

        position :
            Position(s) of the slice to extract

            Positions can be given as axis indices (default) or axis values,
            if the parameter "unit" is set accordingly. For details, see below.

            If you provide a list of positions, you need to provide as many
            axes as positions.

            If no position is provided or the given position is out of
            bounds for the given axis, a ValueError is raised.

        unit : :class:`str`
            Unit used for specifying the range: either "axis" or "index".

            If an invalid value is provided, a ValueError is raised.

            Default: "index"

    Raises
    ------
    aspecd.exceptions.NotApplicableToDatasetError
        Raised if dataset has not enough dimensions (*i.e.*, 1D dataset).

    ValueError
        Raised if index is out of bounds for given axis.

        Raised if wrong unit is given.

        Raised if too many values for axis are given.

        Raised if number of values for position and axis differ.

    IndexError
        Raised if axis is out of bounds for given dataset.


    .. versionchanged:: 0.2
        Parameter "index" renamed to "position" to reflect values to be
        either indices or axis values

    .. versionadded:: 0.2
        Slice positions can be given both, as axis indices and axis values

    .. versionadded:: 0.2
        Works for ND datasets with N>1

    .. versionchanged:: 0.7
        Sets dataset label to slice position (in axes units)


    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. The examples focus each on a single
    aspect.

    In the simplest case, just invoke the slice extraction with an index only:

    .. code-block:: yaml

       - kind: processing
         type: SliceExtraction
         properties:
           parameters:
             position: 5

    This will extract the sixth slice (index five) along the first axis (index
    zero).

    If you would like to extract a slice along the second axis (with index
    one), simply provide both parameters, index and axis:

    .. code-block:: yaml

       - kind: processing
         type: SliceExtraction
         properties:
           parameters:
             position: 5
             axis: 1

    This will extract the sixth slice along the second axis.

    And as it is sometimes more convenient to give ranges in axis values
    rather than indices, even this is possible. Suppose the axis you would
    like to extract a slice from runs from 340 to 350, and you would like to
    extract the slice corresponding to 343:

    .. code-block:: yaml

       - kind: processing
         type: SliceExtraction
         properties:
           parameters:
             position: 343
             unit: axis

    In case of you providing the range in axis units rather than indices,
    the value closest to the actual axis value will be chosen automatically.

    For ND datasets with N>2, you can either extract a 1D or ND slice,
    with N always at least one dimension less than the original data. To
    extract a 2D slice from a 3D dataset, simply proceed as above, providing
    one value each for position and axis. If, however, you want to extract a
    1D slice from a 3D dataset, you need to provide two values each for
    position and axis:

    .. code-block:: yaml

       - kind: processing
         type: SliceExtraction
         properties:
           parameters:
             position: [21, 42]
             axis: [0, 2]

    This particular case would be equivalent to ``data[21, :, 42]`` assuming
    ``data`` to contain the numeric data, besides, of course, that the
    processing step takes care of removing the axes as well.

    """

    def __init__(self):
        super().__init__()
        self.undoable = True
        self.description = "Extract slice from dataset"
        self.parameters["position"] = None
        self.parameters["axis"] = 0
        self.parameters["unit"] = "index"

    @staticmethod
    def applicable(dataset):
        """
        Check whether processing step is applicable to the given dataset.

        Slice extraction is only applicable to datasets with at least
        two-dimensional data.

        Parameters
        ----------
        dataset : :class:`aspecd.dataset.Dataset`
            dataset to check

        Returns
        -------
        applicable : :class:`bool`
            `True` if successful, `False` otherwise.

        """
        return len(dataset.data.axes) >= 3

    def _sanitise_parameters(self):
        if (
            not self.parameters["position"]
            and self.parameters["position"] != 0
        ):
            raise IndexError("No position provided for slice extraction")
        self.parameters["position"] = np.atleast_1d(
            self.parameters["position"]
        )
        self.parameters["axis"] = np.atleast_1d(self.parameters["axis"])
        if self.parameters["axis"].size > self.dataset.data.data.ndim - 1:
            # pylint: disable=consider-using-f-string
            raise ValueError(
                "Too many axes (%i) provided for %iD dataset"
                % (self.parameters["axis"].size, self.dataset.data.data.ndim)
            )
        if self.parameters["axis"].size != self.parameters["position"].size:
            raise ValueError(
                "Need same number of values for position and axis"
            )
        for axis in self.parameters["axis"]:
            if axis > self.dataset.data.data.ndim - 1:
                # pylint: disable=consider-using-f-string
                raise IndexError("Axis %i out of bounds" % axis)
        self.parameters["unit"] = self.parameters["unit"].lower()
        if self.parameters["unit"] not in ["index", "axis"]:
            raise ValueError("Wrong unit, needs to be either index or axis.")
        if self._out_of_range():
            raise ValueError("Position out of axis range.")

    def _perform_task(self):
        self.dataset.label = self._set_dataset_label()
        slice_object = self._get_slice()
        self.dataset.data.data = self.dataset.data.data[slice_object]
        for axis in self.parameters["axis"]:
            del self.dataset.data.axes[axis]

    def _out_of_range(self):
        out_of_range = False
        for idx, axis in enumerate(self.parameters["axis"]):
            position = self.parameters["position"][idx]
            if self.parameters["unit"] == "index":
                axis_length = self.dataset.data.data.shape[axis]
                if abs(position) > axis_length:
                    out_of_range = True
            else:
                if position < min(
                    self.dataset.data.axes[axis].values
                ) or position > max(self.dataset.data.axes[axis].values):
                    out_of_range = True
        return out_of_range

    def _get_slice(self):
        # Create empty slice object
        slice_object = []
        for _ in range(self.dataset.data.data.ndim):
            slice_object.append(slice(None))
        # Extract position(s) and overwrite slice object
        for idx, axis in enumerate(self.parameters["axis"]):
            if self.parameters["unit"] == "index":
                slice_ = self.parameters["position"][idx]
            else:
                slice_ = self._get_index(
                    self.dataset.data.axes[axis].values,
                    self.parameters["position"][idx],
                )
            slice_object[axis] = slice_
        return tuple(slice_object)

    @staticmethod
    def _get_index(vector, value):
        return np.abs(vector - value).argmin()

    def _set_dataset_label(self):
        label = ""
        for idx, axis in enumerate(self.parameters["axis"]):
            if label:
                label += ", "
            if self.parameters["unit"] == "index":
                value = self.dataset.data.axes[axis].values[
                    self.parameters["position"][idx]
                ]
            else:
                index = self._get_index(
                    self.dataset.data.axes[axis].values,
                    self.parameters["position"][idx],
                )
                value = self.dataset.data.axes[axis].values[index]
            label += f"{value} {self.dataset.data.axes[axis].unit}"
        return label


class SliceRemoval(SingleProcessingStep):
    # noinspection PyUnresolvedReferences
    """
    Remove slice along one dimension from dataset.

    With multidimensional datasets, there are use cases where you would like
    to remove a slice along a particular axis, mostly due to artifacts
    contained in this slice that impair downstream processing and analysis.

    You can either provide indices or axis values for ``position``. For the
    latter, set the parameter "unit" accordingly. For details, see below.

    Attributes
    ----------
    parameters : :class:`dict`
        All parameters necessary for this step.

        axis :
            Index of the axis or list of indices of the axes to take the
            position from to remove the slice

            If you provide a list of axes, you need to provide as many
            positions as axes.

            If an invalid axis is provided, an IndexError is raised.

            Default: 0

        position :
            Position(s) of the slice to remove

            Positions can be given as axis indices (default) or axis values,
            if the parameter "unit" is set accordingly. For details, see below.

            If you provide a list of positions, you need to provide as many
            axes as positions.

            If no position is provided or the given position is out of
            bounds for the given axis, a ValueError is raised.

        unit : :class:`str`
            Unit used for specifying the range: either "axis" or "index".

            If an invalid value is provided, a ValueError is raised.

            Default: "index"

    Raises
    ------
    aspecd.exceptions.NotApplicableToDatasetError
        Raised if dataset has not enough dimensions (*i.e.*, 1D dataset).

    ValueError
        Raised if index is out of bounds for given axis.

        Raised if wrong unit is given.

        Raised if too many values for axis are given.

        Raised if number of values for position and axis differ.

    IndexError
        Raised if axis is out of bounds for given dataset.


    .. versionadded:: 0.8


    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. The examples focus each on a single
    aspect.

    In the simplest case, just invoke the slice removal with an index only:

    .. code-block:: yaml

       - kind: processing
         type: SliceRemoval
         properties:
           parameters:
             position: 5

    This will remove the sixth slice (index five) along the first axis (index
    zero).

    If you would like to remove a slice along the second axis (with index
    one), simply provide both parameters, index and axis:

    .. code-block:: yaml

       - kind: processing
         type: SliceRemoval
         properties:
           parameters:
             position: 5
             axis: 1

    This will remove the sixth slice along the second axis.

    And as it is sometimes more convenient to give ranges in axis values
    rather than indices, even this is possible. Suppose the axis you would
    like to remove a slice from runs from 340 to 350, and you would like to
    remove the slice corresponding to 343:

    .. code-block:: yaml

       - kind: processing
         type: SliceRemoval
         properties:
           parameters:
             position: 343
             unit: axis

    In case of you providing the range in axis units rather than indices,
    the value closest to the actual axis value will be chosen automatically.

    For ND datasets with N>2, you can currently only remove a slice along
    one axis.

    """

    def __init__(self):
        super().__init__()
        self.description = "Remove slice from data of dataset"
        self.undoable = True
        self.parameters["position"] = None
        self.parameters["axis"] = 0
        self.parameters["unit"] = "index"

    @staticmethod
    def applicable(dataset):
        """
        Check whether processing step is applicable to the given dataset.

        Slice removal is only applicable to datasets with at least
        two-dimensional data.

        Parameters
        ----------
        dataset : :class:`aspecd.dataset.Dataset`
            dataset to check

        Returns
        -------
        applicable : :class:`bool`
            `True` if successful, `False` otherwise.

        """
        return len(dataset.data.axes) >= 3

    def _sanitise_parameters(self):
        if isinstance(self.parameters["position"], int):
            self.parameters["position"] = [self.parameters["position"]]
        if (
            not self.parameters["position"]
            and self.parameters["position"] != 0
        ):
            raise IndexError("No position provided for slice extraction")
        if self.parameters["axis"] > self.dataset.data.data.ndim - 1:
            # pylint: disable=consider-using-f-string
            raise IndexError(
                "Axis %i out of bounds" % self.parameters["axis"]
            )
        self.parameters["unit"] = self.parameters["unit"].lower()
        if self.parameters["unit"] not in ["index", "axis"]:
            raise ValueError("Wrong unit, needs to be either index or axis.")
        if self._out_of_range():
            raise ValueError("Position out of axis range.")

    def _out_of_range(self):
        out_of_range = False
        position = self.parameters["position"]
        axis = self.parameters["axis"]
        if self.parameters["unit"] == "index":
            axis_length = self.dataset.data.data.shape[axis]
            if any(abs(x) > axis_length for x in position):
                out_of_range = True
        else:
            min_value = min(self.dataset.data.axes[axis].values)
            max_value = max(self.dataset.data.axes[axis].values)
            if any(x < min_value or x > max_value for x in position):
                out_of_range = True
        return out_of_range

    def _perform_task(self):
        axis = self.parameters["axis"]
        if self.parameters["unit"] == "index":
            position = self.parameters["position"]
        else:
            position = self._get_index(
                self.dataset.data.axes[axis].values,
                self.parameters["position"],
            )
        original_axis = self.dataset.data.axes[axis].values
        self.dataset.data.data = np.delete(
            self.dataset.data.data, position, axis
        )
        self.dataset.data.axes[axis].values = np.delete(
            original_axis, position
        )

    @staticmethod
    def _get_index(vector, value):
        index = []
        for _index in value:
            index.append(np.abs(vector - _index).argmin())
        return index


class RangeExtraction(SingleProcessingStep):
    # noinspection PyUnresolvedReferences
    """
    Extract range of data from dataset.

    There are many reasons to look only at a certain range of data of a
    given dataset. For a ND array, one would use slicing, but for a dataset,
    one needs to have the axes adjusted as well, hence this processing step.

    Attributes
    ----------
    parameters : :class:`dict`
        All parameters necessary for this step.

        range : :class:`list`
            List of lists with indices for the slicing

            For each dimension of the data of the dataset, one list of
            indices needs to be provided that are used for start, stop [,
            step] of :class:`slice`.

        unit : :class:`str`
            Unit used for specifying the range: "axis", "index", "percentage".

            If an invalid value is provided, a ValueError is raised.

            Default: "index"

    Raises
    ------
    ValueError
        Raised if index is out of bounds for given axis.

        Raised if wrong unit is given.

    IndexError
        Raised if no range is provided.

        Raised if number of ranges does not fit data dimensions.


    .. versionadded:: 0.2

    .. versionchanged:: 0.9.2
        Range extraction with axis values sets correct upper boundary


    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. The examples focus each on a single
    aspect.

    In the simplest case, just invoke the range extraction with one range
    only, assuming a 1D dataset:

    .. code-block:: yaml

       - kind: processing
         type: RangeExtraction
         properties:
           parameters:
             range: [5, 10]

    This will extract the range ``data[5:10]`` from your data (and adjust
    the axis accordingly). In case of 2D data, it would be fairly similar,
    except of now providing two ranges:

    .. code-block:: yaml

       - kind: processing
         type: RangeExtraction
         properties:
           parameters:
             range:
              - [5, 10]
              - [3, 6]

    Additionally, you can provide step sizes, just as you can do when
    slicing in Python:

    .. code-block:: yaml

       - kind: processing
         type: RangeExtraction
         properties:
           parameters:
             range: [5, 10, 2]

    This is equivalent to ``data[5:10:2]`` or ``data[(slice(5, 10, 2))]``,
    accordingly. Note that in Python, ranges *exclude* the upper limit.

    Sometimes, it is more convenient to give ranges in axis values rather
    than indices. This can be achieved by setting the parameter ``unit`` to
    "axis":

    .. code-block:: yaml

       - kind: processing
         type: RangeExtraction
         properties:
           parameters:
             range: [5, 10]
             unit: axis

    Note that in this case, setting a step is meaningless and will be
    silently ignored. Furthermore, the nearest axis values will be used for
    the range. Furthermore, for more intuitive use, the given range
    *includes* the upper limit, in contrast to using indices. This is to be
    consistent with Python's handling of ranges as weell as  with the
    intuition of most scientists regarding the ranges for axis values.

    In some cases you may want to extract a range by providing percentages
    instead of indices or axis values. Even this can be done:

    .. code-block:: yaml

       - kind: processing
         type: RangeExtraction
         properties:
           parameters:
             range: [0, 10]
             unit: percentage

    Here, the first ten percent of the data of the 1D dataset will be
    extracted, or more exactly the indices falling within the first ten
    percent. Note that in this case, setting a step is meaningless and will be
    silently ignored. Furthermore, the nearest axis values will be used for
    the range.

    """

    def __init__(self):
        super().__init__()
        self.description = "Extract range from data of dataset"
        self.undoable = True
        self.parameters["range"] = []
        self.parameters["unit"] = "index"

    def _sanitise_parameters(self):
        if not self.parameters["range"]:
            raise IndexError("No range provided for range extraction")
        self.parameters["range"] = np.atleast_2d(self.parameters["range"])
        if len(self.parameters["range"]) < self.dataset.data.data.ndim:
            raise IndexError(
                f'Got only {len(self.parameters["range"])} range '
                f"for {self.dataset.data.data.ndim}D data"
            )
        self.parameters["unit"] = self.parameters["unit"].lower()
        if self.parameters["unit"] not in ["index", "axis", "percentage"]:
            raise ValueError("Wrong unit, needs to be either index or axis.")
        if self._out_of_range():
            raise ValueError("Range out of axis range.")

    def _perform_task(self):
        slice_object = []
        for dim in range(self.dataset.data.data.ndim):
            if (
                len(self.parameters["range"][dim]) > 2
                and self.parameters["unit"] == "index"
            ):
                slice_ = slice(
                    self.parameters["range"][dim][0],
                    self.parameters["range"][dim][1],
                    self.parameters["range"][dim][2],
                )
            else:
                if self.parameters["unit"] == "index":
                    slice_ = slice(
                        self.parameters["range"][dim][0],
                        self.parameters["range"][dim][1],
                    )
                elif self.parameters["unit"] == "axis":
                    start = self._get_index(
                        self.dataset.data.axes[dim].values,
                        self.parameters["range"][dim][0],
                    )
                    stop = self._get_index(
                        self.dataset.data.axes[dim].values,
                        self.parameters["range"][dim][1],
                    )
                    slice_ = slice(start, stop + 1)
                else:
                    start = math.ceil(
                        self.dataset.data.axes[dim].values.size
                        * self.parameters["range"][dim][0]
                        / 100.0
                    )
                    stop = (
                        math.ceil(
                            self.dataset.data.axes[dim].values.size
                            * self.parameters["range"][dim][1]
                            / 100.0
                        )
                        + 1
                    )
                    slice_ = slice(start, stop + 1)
            # Important: Change axes first, then data
            self.dataset.data.axes[dim].values = self.dataset.data.axes[
                dim
            ].values[slice_]
            slice_object.append(slice_)
        self.dataset.data.data = self.dataset.data.data[tuple(slice_object)]

    def _out_of_range(self):
        out_of_range = False
        for dim in range(len(self.parameters["range"])):
            for index in self.parameters["range"][dim]:
                if self.parameters["unit"] == "index":
                    if (
                        abs(index)
                        > self.dataset.data.axes[dim].values.size + 1
                    ):
                        out_of_range = True
                elif self.parameters["unit"] == "axis":
                    axis_values = self.dataset.data.axes[dim].values
                    for value in self.parameters["range"][dim]:
                        if (
                            value < axis_values.min()
                            or value > axis_values.max()
                        ):
                            out_of_range = True
                else:
                    for value in self.parameters["range"][dim]:
                        if value < 0 or value > 100:
                            out_of_range = True
        return out_of_range

    @staticmethod
    def _get_index(vector, value):
        return np.abs(vector - value).argmin()


class BaselineCorrection(SingleProcessingStep):
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


    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. The examples focus each on a single
    aspect.

    In the simplest case, just invoke the baseline correction with default
    values:

    .. code-block:: yaml

       - kind: processing
         type: BaselineCorrection

    In this case, a zeroth-order polynomial baseline will be subtracted from
    your dataset using ten percent to the left and right, and in case of a
    2D dataset, the baseline correction will be performed along the first
    axis (index zero) for all indices of the second axis (index 1).

    Of course, often you want to control a little bit more how the baseline
    will be corrected. This can be done by explicitly setting some parameters.

    Suppose you want to perform a baseline correction with a polynomial of
    first order:

    .. code-block:: yaml

       - kind: processing
         type: BaselineCorrection
         properties:
           parameters:
             order: 1

    If you want to change the (percental) area used for fitting the
    baseline, and even specify different ranges left and right:

    .. code-block:: yaml

       - kind: processing
         type: BaselineCorrection
         properties:
           parameters:
             fit_area: [5, 20]

    Here, five percent from the left and 20 percent from the right are used.

    Finally, suppose you have a 2D dataset and want to average along the
    second axis (index one):

    .. code-block:: yaml

       - kind: processing
         type: BaselineCorrection
         properties:
           parameters:
             axis: 1

    Of course, you can combine the different options.


    .. versionchanged:: 0.3
        Coefficients are returned in unscaled data domain

    .. versionchanged:: 0.6.3
        Zero values in range properly handled

    """

    def __init__(self):
        super().__init__()
        self.undoable = True
        self.description = "Correct baseline of dataset"
        self.parameters["kind"] = "polynomial"
        self.parameters["order"] = 0
        self.parameters["coefficients"] = []
        self.parameters["fit_area"] = [10, 10]
        self.parameters["axis"] = 0
        self._data_points_left = None
        self._data_points_right = None
        self._axis_values = []
        self._intensity_values = []

    @staticmethod
    def applicable(dataset):
        """
        Check whether processing step is applicable to the given dataset.

        Baseline correction is (currently) only applicable to datasets with
        one- and two-dimensional data.

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
        if isinstance(self.parameters["fit_area"], (float, int)):
            fit_area = self.parameters["fit_area"]
            self.parameters["fit_area"] = [fit_area, fit_area]
        if (
            isinstance(self.parameters["fit_area"], list)
            and len(self.parameters["fit_area"]) == 1
        ):
            fit_area = self.parameters["fit_area"][0]
            self.parameters["fit_area"] = [fit_area, fit_area]
        if sum(self.parameters["fit_area"]) > 100:
            # pylint: disable=consider-using-f-string,logging-not-lazy
            logger.warning(
                "Baseline to consider spans over %s %%. It "
                "has been readjusted to 50 %% on each side."
                % sum(self.parameters["fit_area"])
            )
            self.parameters["fit_area"] = [50, 50]

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
        self._data_points_left = math.ceil(
            number_of_points * self.parameters["fit_area"][0] / 100.0
        )
        self._data_points_right = math.ceil(
            number_of_points * self.parameters["fit_area"][1] / 100.0
        )

    # pylint: disable=invalid-unary-operand-type
    def _get_axis_values(self):
        left_values = right_values = []
        axis = self.parameters["axis"]
        if self._data_points_left:
            left_values = self.dataset.data.axes[axis].values[
                : self._data_points_left
            ]
        if self._data_points_right:
            right_values = self.dataset.data.axes[axis].values[
                -self._data_points_right :
            ]
        self._axis_values = np.concatenate((left_values, right_values))

    def _get_intensity_values(self, data):
        left_values = right_values = []
        if self._data_points_left:
            left_values = data[: self._data_points_left]
        if self._data_points_right:
            right_values = data[-self._data_points_right :]
        self._intensity_values = np.concatenate((left_values, right_values))

    # noinspection PyUnresolvedReferences,PyCallingNonCallable
    def _get_values_to_subtract(self):
        polynomial = np.polynomial.Polynomial.fit(
            self._axis_values,
            self._intensity_values,
            self.parameters["order"],
        )
        self.parameters["coefficients"] = polynomial.convert().coef
        axis = self.parameters["axis"]
        return polynomial(self.dataset.data.axes[axis].values)

    def _is_n_dimensional(self):
        return len(self.dataset.data.axes) > 2


class Averaging(SingleProcessingStep):
    # noinspection PyUnresolvedReferences
    """
    Average data over given range along given axis.

    While projection as performed by :class:`aspecd.processing.Projection`
    can be considered a special case of averaging using the whole range of
    one axis, averaging is usually performed over part of an axis only.

    .. note::
        Currently, averaging works *only* for **2D** datasets, not for
        higher-dimensional datasets. This may, however, change in the future.

    .. important::
        Indices for the range work slightly different from Python: While
        still zero-based, a range of [2, 3] will result in having the third
        and fourth column/row averaged. This seems more intuitive to the
        average scientist than sticking with Python (and having in this case
        the third column/row returned).

    You can use negative indices as well, as long as the resulting indices
    are still within the range of the corresponding data dimension.

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

        unit : :class:`str`
            Unit used for specifying the range: either "axis" or "index".

            Default: "index"

    Raises
    ------
    ValueError
        Raised if range is out of range for given axis or empty

        Raised if unit is not either "axis" or "index"

    IndexError
        Raised if axis is out of bounds for given dataset


    .. versionchanged:: 0.7
        Sets dataset label to averaging range (in axes units)


    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. The examples focus each on a single
    aspect.

    In the simplest case, just invoke the averaging with a range only:

    .. code-block:: yaml

       - kind: processing
         type: Averaging
         properties:
           parameters:
             range: [2, 3]

    In this case, you will get your dataset averaged along the first axis
    (index zero), and averaged over the indices 2 and 3 of the second axis.

    If you would like to average over the second axis (index 1),
    just specify this axis:

    .. code-block:: yaml

       - kind: processing
         type: Averaging
         properties:
           parameters:
             range: [2, 3]
             axis: 1

    And as it is sometimes more convenient to give ranges in axis values
    rather than indices, even this is possible. Suppose the axis you would
    like to average over runs from 340 to 350, and you would like to average
    from 342 to 344:

    .. code-block:: yaml

       - kind: processing
         type: Averaging
         properties:
           parameters:
             range: [342, 344]
             unit: axis

    In case of you providing the range in axis units rather than indices,
    the value closest to the actual axis value will be chosen automatically.

    """

    def __init__(self):
        super().__init__()
        self.undoable = True
        self.description = "Average data over given range along given axis."
        self.parameters["range"] = None
        self.parameters["axis"] = 0
        self.parameters["unit"] = "index"

    @staticmethod
    def applicable(dataset):
        """
        Check whether processing step is applicable to the given dataset.

        Averaging is only applicable to datasets with two-dimensional data.

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
        if self.parameters["axis"] > self.dataset.data.data.ndim - 1:
            # pylint: disable=consider-using-f-string
            raise IndexError(
                "Axis %i out of bounds" % self.parameters["axis"]
            )
        self.parameters["unit"] = self.parameters["unit"].lower()
        if self.parameters["unit"] not in ["index", "axis"]:
            raise ValueError("Wrong unit, needs to be either index or axis.")
        if self._out_of_range():
            raise ValueError("Given range out of axis range.")

    def _perform_task(self):
        self.dataset.label = self._set_dataset_label()
        range_ = self._get_range()
        if self.parameters["axis"] == 0:
            self.dataset.data.data = np.average(
                self.dataset.data.data[range_[0] : range_[1], :],
                axis=self.parameters["axis"],
            )
        else:
            self.dataset.data.data = np.average(
                self.dataset.data.data[:, range_[0] : range_[1]],
                axis=self.parameters["axis"],
            )
        del self.dataset.data.axes[self.parameters["axis"]]

    def _out_of_range(self):
        out_of_range = False
        if self.parameters["unit"] == "index":
            axis_length = self.dataset.data.data.shape[
                self.parameters["axis"]
            ]
            if abs(self.parameters["range"][0]) > axis_length:
                out_of_range = True
            elif self.parameters["range"][1] > axis_length:
                out_of_range = True
        else:
            axis = self.parameters["axis"]
            if self.parameters["range"][0] < min(
                self.dataset.data.axes[axis].values
            ) or self.parameters["range"][0] > max(
                self.dataset.data.axes[axis].values
            ):
                out_of_range = True
            if self.parameters["range"][1] < min(
                self.dataset.data.axes[axis].values
            ) or self.parameters["range"][1] > max(
                self.dataset.data.axes[axis].values
            ):
                out_of_range = True
        return out_of_range

    def _get_range(self):
        if self.parameters["unit"] == "index":
            range_ = copy.copy(self.parameters["range"])
        else:
            axis = self.parameters["axis"]
            range_ = [
                self._get_index(
                    self.dataset.data.axes[axis].values,
                    self.parameters["range"][0],
                ),
                self._get_index(
                    self.dataset.data.axes[axis].values,
                    self.parameters["range"][1],
                ),
            ]
        if min(range_) > 0:
            range_ = sorted(range_)
        if range_[1] > 0:
            range_[1] += 1
        return range_

    @staticmethod
    def _get_index(vector, value):
        return np.abs(vector - value).argmin()

    def _set_dataset_label(self):
        range_ = self._get_range()
        range_[1] -= 1
        values = self.dataset.data.axes[self.parameters["axis"]].values[
            range_
        ]
        unit = self.dataset.data.axes[self.parameters["axis"]].unit
        label = f"{values[0]}-{values[1]} {unit}"
        return label


class ScalarAxisAlgebra(SingleProcessingStep):
    # noinspection PyUnresolvedReferences
    """Perform scalar algebraic operation on the axis of a dataset.

    Sometimes, changing the values of an axis can be quite useful,
    for example to apply corrections obtained by some analysis step.
    Usually, this requires scalar algebraic operations on the axis values.

    Attributes
    ----------
    parameters : :class:`dict`
        All parameters necessary for this step.

        kind : :class:`str`
            Kind of scalar algebra to use

            Valid values: "plus", "minus", "times", "by", "add", "subtract",
            "multiply", "divide", "+", "-", "*", "/", "power", "pow", "**"

        axis : :class:`int`
            Axis to operate on

            Default value: 0

        value : :class:`float`
            Parameter of the scalar algebraic operation

            Default value: None

    Raises
    ------
    ValueError
        Raised if no or wrong kind is provided


    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. The examples focus each on a single
    aspect.

    In case you would like to add a fixed value of 42 to the first axis
    (index 0) your dataset:

    .. code-block:: yaml

       - kind: processing
         type: ScalarAxisAlgebra
         properties:
           parameters:
             kind: plus
             axis: 0
             value: 42

    Similarly, you could use "minus", "times", "by", "add", "subtract",
    "multiply", "divide", and "power" as kind - resulting in the given
    algebraic operation.


    .. versionadded:: 0.2

    """

    def __init__(self):
        super().__init__()
        self.description = "Scalar algebra on the axis of a dataset"
        self.undoable = True
        self.parameters["kind"] = None
        self.parameters["axis"] = 0
        self.parameters["value"] = None
        self._kinds = {
            "plus": operator.add,
            "add": operator.add,
            "+": operator.add,
            "minus": operator.sub,
            "subtract": operator.sub,
            "-": operator.sub,
            "times": operator.mul,
            "multiply": operator.mul,
            "*": operator.mul,
            "by": operator.truediv,
            "divide": operator.truediv,
            "/": operator.truediv,
            "power": operator.pow,
            "pow": operator.pow,
            "**": operator.pow,
        }

    def _sanitise_parameters(self):
        if not self.parameters["kind"]:
            raise ValueError("No kind of scalar operation given")
        if self.parameters["kind"].lower() not in self._kinds:
            # pylint: disable=consider-using-f-string
            raise ValueError(
                'Scalar operation "%s" not understood'
                % self.parameters["kind"]
            )

    def _perform_task(self):
        operator_ = self._kinds[self.parameters["kind"].lower()]
        self.dataset.data.axes[self.parameters["axis"]].values = operator_(
            self.dataset.data.axes[0].values, self.parameters["value"]
        )


class DatasetAlgebra(SingleProcessingStep):
    # noinspection PyUnresolvedReferences
    """Perform scalar algebraic operation on two datasets.

    To improve the signal-to-noise ratio, adding the data of two datasets
    can sometimes be useful. Alternatively, adding or subtracting the data
    of two datasets can be used to help to interpret the signals.

    .. important::
        The data of the two datasets to perform the scalar algebraic
        operation on need to have the same dimension (that is checked for),
        and to obtain meaningful results, usually the axes values need to be
        identical as well. For this purpose, use the
        :class:`CommonRangeExtraction` processing step.

    .. note::
        Metadata of the dataset are not touched by this operation at all.
        This means that the metadata in the dataset are still those of the
        dataset the processing step operated on. This may, however, lead to
        confusion or misinterpretation if somewhere in the metadata the
        number of accumulations or measurements per point or similar is
        encoded.

    Attributes
    ----------
    parameters : :class:`dict`
        All parameters necessary for this step.

        kind : :class:`str`
            Kind of scalar algebra to use

            Valid values: "plus", "minus", "add", "subtract", "+", "-"

            Note that in contrast to scalar algebra, multiply and divide are
            not implemented for operation on two datasets.

        dataset : :class:`aspecd.dataset.Dataset`
            Dataset whose data to add or subtract

    Raises
    ------
    ValueError
        Raised if no or wrong kind is provided

        Raised if data of datasets have different shapes


    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. The examples focus each on a single
    aspect.

    In case you would like to add the data of the dataset referred to by its
    label ``label_to_other_dataset`` to your dataset:

    .. code-block:: yaml

       - kind: processing
         type: DatasetAlgebra
         properties:
           parameters:
             kind: plus
             dataset: label_to_other_dataset

    Similarly, you could use "minus", "add", "subtract" as kind - resulting
    in the given algebraic operation.

    As mentioned already, the data of both datasets need to have identical
    shape, and comparison is only meaningful if the axes are compatible as
    well. Hence, you will usually want to perform a CommonRangeExtraction
    processing step before doing algebra with two datasets:

    .. code-block:: yaml

       - kind: multiprocessing
         type: CommonRangeExtraction
         result:
           - label_to_dataset
           - label_to_other_dataset

       - kind: processing
         type: DatasetAlgebra
         properties:
           parameters:
             kind: plus
             dataset: label_to_other_dataset
         apply_to:
           - label_to_dataset

    Sometimes, you have recorded multiple datasets and want to add them all
    up. While technically speaking, this would be possible with consecutive
    steps, it is much more convenient to provide a list of datasets:

    .. code-block:: yaml

       - kind: processing
         type: DatasetAlgebra
         properties:
           parameters:
             kind: plus
             dataset:
             - label_to_other_dataset
             - label_to_yet_another_dataset

    This will add the data of both datasets provided to the dataset operated
    upon. Of course, you can subtract the data in the same way.


    .. versionadded:: 0.2

    .. versionchanged:: 0.12
        Handles a list of datasets in parameter "dataset".

    """

    def __init__(self):
        super().__init__()
        self.description = "Perform algebra using two datasets"
        self.parameters["dataset"] = None
        self.parameters["kind"] = ""
        self._kinds = {
            "plus": operator.add,
            "add": operator.add,
            "+": operator.add,
            "minus": operator.sub,
            "subtract": operator.sub,
            "-": operator.sub,
        }

    def _sanitise_parameters(self):
        if not self.parameters["dataset"]:
            raise aspecd.exceptions.MissingDatasetError
        if not self.parameters["kind"]:
            raise ValueError("No kind of scalar operation given")
        if self.parameters["kind"].lower() not in self._kinds:
            # pylint: disable=consider-using-f-string
            raise ValueError(
                'Scalar operation "%s" not understood'
                % self.parameters["kind"]
            )
        if not isinstance(self.parameters["dataset"], list):
            self.parameters["dataset"] = [self.parameters["dataset"]]

    def _perform_task(self):
        self._check_shape()
        operator_ = self._kinds[self.parameters["kind"].lower()]
        for index, dataset in enumerate(self.parameters["dataset"]):
            self.dataset.data.data = operator_(
                self.dataset.data.data, dataset.data.data
            )
            self.parameters["dataset"][index] = dataset.id
        if len(self.parameters["dataset"]) == 1:
            self.parameters["dataset"] = self.parameters["dataset"][0]

    def _check_shape(self):
        for dataset in self.parameters["dataset"]:
            if self.dataset.data.data.shape != dataset.data.data.shape:
                raise ValueError(
                    f"Data of datasets have different shapes: "
                    f"{self.dataset.data.data.shape}, "
                    f"{dataset.data.data.shape}."
                )


class Interpolation(SingleProcessingStep):
    # noinspection PyUnresolvedReferences
    r"""Interpolate data.

    As soon as data of different datasets should be arithmetically combined,
    they need to have an identical grid. Often, this can only be achieved by
    interpolating one or both datasets.

    Take care not to use interpolation to artificially smooth your data.

    For an in-depth discussion of interpolating ND data, see the
    following discussions on Stack Overflow, particularly the answers by Joe
    Kington providing both, theoretical insight and Python code:

    * `<https://stackoverflow.com/a/6238859>`_

    * `<https://stackoverflow.com/a/32763635>`_


    .. todo::
        * Make type of interpolation controllable


    Attributes
    ----------
    parameters : :class:`dict`
        All parameters necessary for this step.

        range : :class:`list`
            Range of the axis to interpolate for

            Needs to be a list of lists in case of ND datasets with N>1,
            containing N two-element vectors as ranges for each of the axes.

        npoints : :class:`list`
            Number of points to interpolate for

            Needs to be a list in case of ND datasets with N>1, containing N
            elements, one for each of the axes.

        unit : :class:`str`
            Unit the ranges are given in

            Can be either "index" (default) or "axis".

    Raises
    ------
    ValueError
        Raised if no range to interpolate for is provided.

        Raised if no number of points to interpolate for is provided.

        Raised if unit is unknown.

    IndexError
        Raised if list of ranges does not fit data dimensions.

        Raised if list of npoints does not fit data dimensions.

        Raised if given range is out of range of data/axes


    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. The examples focus each on a single
    aspect.

    Generally, interpolating requires to provide both, a range and a number
    of points:

    .. code-block:: yaml

       - kind: processing
         type: Interpolation
         properties:
           parameters:
             range: [10, 100]
             npoints: 901

    This would interpolate your data between their indices 10 and 100 using
    901 points. As it is sometimes (often) more convenient to work with
    axis units, you can tell the processing step to use axis values instead
    of indices:

    .. code-block:: yaml

       - kind: processing
         type: Interpolation
         properties:
           parameters:
             range: [340, 350]
             npoints: 1001
             unit: axis

    This would interpolate your (1D) data between the axis values 340 and
    350 using 1001 points.

    .. versionadded:: 0.2

    .. versionchanged:: 0.8.3
        Interpolation for *N*\ D datasets with arbitrary dimension *N*

    .. versionchanged:: 0.8.3
        Change interpolation method for 2D data from deprecated
        :class:`scipy.interpolate.interp2d` to
        :class:`scipy.interpolate.RegularGridInterpolator`

    """

    def __init__(self):
        super().__init__()
        self.description = "Interpolate data of dataset"
        self.undoable = True
        self.parameters["range"] = None
        self.parameters["npoints"] = None
        self.parameters["unit"] = "index"
        self._axis_values = []

    def _sanitise_parameters(self):
        if not self.parameters["range"]:
            raise ValueError("No range provided to interpolate for")
        if not self.parameters["npoints"]:
            raise ValueError(
                "No number of points provided to interpolate for"
            )
        if self.parameters["unit"] not in ("index", "axis"):
            raise ValueError(f'Unknown unit {self.parameters["unit"]}')
        self.parameters["range"] = np.atleast_2d(self.parameters["range"])
        if len(self.parameters["range"]) < self.dataset.data.data.ndim:
            raise IndexError("List of ranges does not fit data dimensions")
        self.parameters["npoints"] = np.atleast_1d(self.parameters["npoints"])
        if len(self.parameters["npoints"]) < self.dataset.data.data.ndim:
            raise IndexError("List of npoints does not fit data dimensions")
        if self._out_of_range():
            raise IndexError("Range out of range.")

    def _perform_task(self):
        self._get_axis_values()
        interp = interpolate.RegularGridInterpolator(
            [x.values for x in self.dataset.data.axes[:-1]],
            self.dataset.data.data,
        )
        grid = np.meshgrid(*self._axis_values, indexing="ij")
        test_points = np.array([x.ravel() for x in grid]).T
        shape = [len(x) for x in self._axis_values]
        self.dataset.data.data = interp(test_points).reshape(shape)
        for dim in range(self.dataset.data.data.ndim):
            self.dataset.data.axes[dim].values = self._axis_values[dim]

    def _out_of_range(self):
        out_of_range = False
        for dim in range(self.dataset.data.data.ndim):
            axes_values = self.dataset.data.axes[dim].values
            if self.parameters["unit"] == "index":
                if abs(self.parameters["range"][dim][0]) > len(axes_values):
                    out_of_range = True
            else:
                for value in self.parameters["range"][dim]:
                    if value < axes_values.min() or value > axes_values.max():
                        out_of_range = True
        return out_of_range

    def _get_axis_values(self):
        for dim in range(self.dataset.data.data.ndim):
            if self.parameters["unit"] == "index":
                range_ = self.parameters["range"][dim]
                start = self.dataset.data.axes[dim].values[range_[0]]
                stop = self.dataset.data.axes[dim].values[range_[1]]
            else:
                start, stop = self.parameters["range"][dim]
            self._axis_values.append(
                np.linspace(start, stop, self.parameters["npoints"][dim])
            )


class Filtering(SingleProcessingStep):
    # noinspection PyUnresolvedReferences
    """Filter data.

    Generally, filtering is a large field of (digital) signal processing,
    and currently, this class only implements a very small subset of filters
    often applied in spectroscopy, namely low-pass filters that can be used
    for smoothing ("denoising") data.

    Filtering makes heavy use of the :mod:`scipy.ndimage` and
    :mod:`scipy.signal` modules of the SciPy package. For details, see there.

    Filtering works with data with arbitrary dimensions, in this case
    applying the filter in each dimension.

    Attributes
    ----------
    parameters : :class:`dict`
        All parameters necessary for this step.

        type : :class:`str`
            Type of the filter to use

            Currently, three types are supported: "uniform", "gaussian",
            "savitzky-golay". For convenience, a list of aliases exists for
            each of these types, and if you use one of these aliases,
            it will be replaced by its generic name:

            ================ ===============================================
            Generic          Alias
            ================ ===============================================
            'uniform'        'box', 'boxcar', 'moving-average', 'car'
            'gaussian'       'binom', 'binomial'
            'savitzky-golay' 'savitzky_golay', 'savitzky golay', 'savgol',
                             'savitzky'
            ================ ===============================================

        window_length : :class:`int`
            Length of the filter window

            The window needs to be smaller than the actual data. If you
            provide a window length that exceeds the data range,
            an exception will be raised.

        order : :class:`int`
            Polynomial order for the Savitzky-Golay filter

            Only necessary for this type of filter. If no order is given for
            this filter, an exception will be raised.


    Raises
    ------
    ValueError
        Raised if no or wrong filter type is provided.

        Raised if no filter window is provided.

        Raised if filter window exceeds data range.

        Raised in case of Savitzky-Golay filter when no order is provided.


    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. The examples focus each on a single
    aspect.

    Generally, filtering requires to provide both, a type of filter and a
    window length. Therefore, for uniform and Gaussian filters, this would be:

    .. code-block:: yaml

       - kind: processing
         type: Filtering
         properties:
           parameters:
             type: uniform
             window_length: 10

    Of course, at least uniform filtering (also known as boxcar or moving
    average) is strongly discouraged due to the artifacts introduced.
    Probably the best bet for applying a filter to smooth your data is the
    Savitzky-Golay filter:

    .. code-block:: yaml

       - kind: processing
         type: Filtering
         properties:
           parameters:
             type: savitzky-golay
             window_length: 9
             order: 3

    Note that for this filter, you need to provide the polynomial order as
    well. To get best results, you will need to experiment with the
    parameters a bit.


    .. versionadded:: 0.2

    """

    def __init__(self):
        super().__init__()
        self.description = "Apply filter to data"
        self.undoable = True
        self.parameters["type"] = None
        self.parameters["window_length"] = None
        self.parameters["order"] = None
        self._types = {
            "uniform": [
                "uniform",
                "box",
                "boxcar",
                "moving-average",
                "car",
            ],
            "gaussian": [
                "gaussian",
                "binom",
                "binomial",
            ],
            "savitzky-golay": [
                "savitzky-golay",
                "savitzky_golay",
                "savitzky golay",
                "savgol",
                "savitzky",
            ],
        }

    def _sanitise_parameters(self):
        if not self.parameters["type"]:
            raise ValueError("Missing filter type")
        self._convert_filter_type()
        if self.parameters["type"] not in self._types:
            raise ValueError(f'Wrong filter type {self.parameters["type"]}')
        if not self.parameters["window_length"]:
            raise ValueError("Missing filter window length")
        if self.parameters["window_length"] > min(
            self.dataset.data.data.shape
        ):
            raise ValueError("Filter window outside data range")
        if (
            self.parameters["type"] == "savitzky-golay"
            and not self.parameters["order"]
        ):
            raise ValueError("Missing order for this filter")

    def _perform_task(self):
        if self.parameters["type"] == "uniform":
            self.dataset.data.data = scipy.ndimage.uniform_filter(
                self.dataset.data.data, self.parameters["window_length"]
            )
        elif self.parameters["type"] == "gaussian":
            self.dataset.data.data = scipy.ndimage.gaussian_filter(
                self.dataset.data.data, self.parameters["window_length"]
            )
        elif self.parameters["type"] == "savitzky-golay":
            # Ensure window length to be odd
            if not self.parameters["window_length"] % 2:
                self.parameters["window_length"] += 1
            self.dataset.data.data = scipy.signal.savgol_filter(
                self.dataset.data.data,
                self.parameters["window_length"],
                self.parameters["order"],
            )

    def _convert_filter_type(self):
        for filter_type, aliases in self._types.items():
            if self.parameters["type"] in aliases:
                self.parameters["type"] = filter_type


class CommonRangeExtraction(MultiProcessingStep):
    # noinspection PyUnresolvedReferences
    r"""
    Extract the common range of data for multiple datasets using interpolation.

    One prerequisite for adding up multiple datasets in a meaningful way is to
    have their data dimensions as well as their respective axes values
    agree. This usually requires interpolating the data to a common set of
    axes.

    .. todo::
        * Make type of interpolation controllable

        * Make number of points controllable (in absolute numbers as well as
          minimum and maximum points with respect to datasets)

    Attributes
    ----------
    parameters : :class:`dict`
        All parameters necessary for this step.

        ignore_units : :class:`bool`
            Whether to ignore the axes units when checking the datasets for
            applicability.

            Usually, the axes units should be identical, but sometimes,
            they may be named differently or be compatible anyways. Use with
            care and only in case you exactly know what you do

            Default: False

        common_range : :class:`list`
            Common range of values for each axis as determined by the
            processing step.

            For >1D datasets, this will be a list of lists.

        npoints : :class:`list`
            Number of points used for the final grid the data are
            interpolated on.

            The length is identical to the dimensions of the data of the
            datasets.

    Raises
    ------
    ValueError
        Raised if datasets have axes with different units or disjoint values

        Raised if datasets have different dimensions

    IndexError
        Raised if axis is out of bounds for given dataset


    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. The examples focus each on a single
    aspect.

    In case you would like to bring all datasets currently loaded into your
    recipe to a common range (use with caution, however), things can be as
    simple as:

    .. code-block:: yaml

       - kind: multiprocessing
         type: CommonRangeExtraction

    Note that this will operate on *all* datasets currently available in
    your recipe, including results from other processing steps. Therefore,
    it is usually better to be explicit, using ``apply_to``. Otherwise,
    you can use this processing step early on in your recipe.

    Usually, however, you will want to restrict this to a subset using
    ``apply_to`` and provide labels for the results:

    .. code-block:: yaml

       - kind: multiprocessing
         type: CommonRangeExtraction
         result:
           - dataset1_cut
           - dataset2_cut
         apply_tp:
           - dataset1
           - dataset2

    If you want to perform algebraic operations on datasets, the data of both
    datasets need to have identical shape, and comparison is only meaningful
    if the axes are compatible as well. Hence, you will usually want to
    perform a CommonRangeExtraction processing step before doing algebra
    with two datasets:

    .. code-block:: yaml

       - kind: multiprocessing
         type: CommonRangeExtraction
         result:
           - label_to_dataset
           - label_to_other_dataset

       - kind: processing
         type: DatasetAlgebra
         properties:
           parameters:
             kind: plus
             dataset: label_to_other_dataset
         apply_to:
           - label_to_dataset

    For details of the algebraic operations on datasets,
    see :class:`DatasetAlgebra`.


    .. versionadded:: 0.2

    .. versionchanged:: 0.6.3
        Unit of last axis (*i.e.*, intensity) gets ignored when checking for
        same units

    .. versionchanged:: 0.9
        Works for *N*\ D datasets with arbitrary dimension *N*

    """

    def __init__(self):
        super().__init__()
        self.description = "Extract common data range of several datasets"
        self.undoable = True
        self.parameters["ignore_units"] = False
        self.parameters["common_range"] = []
        self.parameters["npoints"] = []

    def _sanitise_parameters(self):
        if len(self.datasets) < 2:
            raise IndexError("Need more than one dataset")

    def _perform_task(self):
        self._check_dimensions()
        self._check_common_range()
        if not self.parameters["ignore_units"]:
            self._check_axes_units()
        self._calculate_number_of_points()
        self._interpolate()

    def _check_dimensions(self):
        old_dimension = None
        for dataset in self.datasets:
            new_dimension = dataset.data.data.ndim
            if old_dimension and old_dimension != new_dimension:
                raise ValueError(
                    f"Datasets have different dimensions: "
                    f"{old_dimension} vs. {new_dimension}"
                )
            old_dimension = new_dimension

    def _check_common_range(self):
        for dim in range(self.datasets[0].data.data.ndim):
            minima = []
            maxima = []
            for dataset in self.datasets:
                minima.append(dataset.data.axes[dim].values[0])
                maxima.append(dataset.data.axes[dim].values[-1])
            if np.amax(minima) > np.amin(maxima):
                raise ValueError(
                    f"Datasets have disjoint axes values: "
                    f"{np.amax(minima)} > {np.amin(maxima)}"
                )
            self.parameters["common_range"].append(
                [np.amax(minima), np.amin(maxima)]
            )

    def _check_axes_units(self):
        old_units = None
        for dataset in self.datasets:
            new_units = []
            for axis in dataset.data.axes[:-1]:
                new_units.append(axis.unit)
            if old_units and old_units != new_units:
                raise ValueError(
                    f"Datasets have axes with different units: "
                    f"{old_units} vs. {new_units}"
                )
            old_units = new_units

    def _calculate_number_of_points(self):
        for dim in range(self.datasets[0].data.data.ndim):
            common_range = self.parameters["common_range"][dim]
            number_of_points = []
            for dataset in self.datasets:
                values = dataset.data.axes[dim].values
                # noinspection PyUnresolvedReferences
                number_of_points.append(
                    (values <= common_range[1]).nonzero()[0][-1]
                    - (values >= common_range[0]).nonzero()[0][0]
                    + 1
                )
            # TODO: Make this adjustable, not always taking the minimum (
            #  i.e., coarsest grid)
            self.parameters["npoints"].append(np.amin(number_of_points))

    def _interpolate(self):
        for dataset in self.datasets:
            interpolation = Interpolation()
            interpolation.parameters["range"] = self.parameters[
                "common_range"
            ]
            interpolation.parameters["npoints"] = self.parameters["npoints"]
            interpolation.parameters["unit"] = "axis"
            dataset.process(interpolation)


class Noise(SingleProcessingStep):
    # noinspection PyUnresolvedReferences
    """
    Add (coloured) noise to data.

    Particularly for testing algorithms and hence creating test data, adding
    noise to these test data is crucial. Furthermore, the naive approach of
    adding white (Gaussian, normally distributed) noise often does not
    reflect the physical reality, as "real" noise often has a different
    power spectral density (PSD).

    Probably the kind of noise most often encountered in spectroscopy is 1/f
    noise or pink noise, with the PSD decreasing by 3 dB per octave or 10 dB
    per decade. For more details on the different kinds of noise,
    the following sources may be a good starting point:

    * https://en.wikipedia.org/wiki/Colors_of_noise
    * https://en.wikipedia.org/wiki/Pink_noise
    * https://en.wikipedia.org/wiki/Flicker_noise

    Different strategies exist to create coloured noise, and the
    implementation used here follows basically the ideas published by Timmer
    and König:

    * J. Timmer and M. König: On generating power law noise.
      *Astronomy and Astrophysics* **300**, 707--710 (1995)

    In short: In the Fourier space, normally distributed random numbers are
    drawn for power and phase of each frequency component, and the power scaled
    by the appropriate power law. Afterwards, the resulting frequency
    spectrum is back transformed using iFFT and ensuring real data.

    Further inspiration came from the following two sources:

    * https://gist.github.com/j-faria/7961488
    * https://github.com/felixpatzelt/colorednoise

    Note: The first is based on a MATLAB(R) code by Max Little and contains a
    number of errors in its Python translation that are *not* present in the
    original code.

    The added noise has always a mean of (close to) zero.

    Attributes
    ----------
    parameters : :class:`dict`
        All parameters necessary for this step.

        exponent : :class:`float`
            The exponent used for scaling the power of the frequency components

            0 -- white (Gaussian) noise
            -1 -- pink (1/f) noise
            -2 -- Brownian (1/f**2) noise

            Default: -1 (pink noise)

        normalise : :class:`bool`
            Whether to normalise the noise amplitude prior to adding to the
            data.

            In this case, the *amplitude* is normalised to 1.

        amplitude : :class:`float`
            Amplitude of the noise

            This is often useful to explicitly control the noise level and
            removes the need to first normalise and scale the data noise
            should be added to.


    .. note::
        The exponent for the noise is not restricted to integer values,
        nor to negative values. While for spectroscopic data, pink (1/*f*)
        noise usually prevails (exponent = -1), the opposite effect with
        high frequencies dominating can occur as well. A prominent example
        of naturally occurring "blue noise" with the density proportional to
        *f* is the Cherenkov radiation.

    .. note::
        In case of ND data, the coloured noise is calculated along the
        *first* dimension only, all other dimensions will exhibit (close to)
        white (Gaussian) noise. Generally, this should not be a problem in
        spectroscopy, as usually, data are recorded over time in one
        dimension only, and only in this (implicit) time dimension coloured
        noise will be relevant.


    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. The examples focus each on a single
    aspect.

    Generally, adding noise to a dataset can be quite simple. Without
    explicitly providing any parameter, 1/f or pink noise will be added to
    the data:

    .. code-block:: yaml

       - kind: processing
         type: Noise

    Of course, you can control in much more detail the kind of noise and its
    amplitude. To add Gaussian (white) noise to a dataset:

    .. code-block:: yaml

       - kind: processing
         type: Noise
         properties:
           parameters:
             exponent: 0

    Similarly, you could add Brownian (1/f**2) noise (with an exponent of
    -2), but you can give positive exponents as well. While this type of
    noise is less relevant in spectroscopy, it is relevant in other areas.

    To control the noise amplitude, there are two different strategies:
    normalising the amplitude to one, and providing an explicit amplitude.
    Normalising works as follows:

    .. code-block:: yaml

       - kind: processing
         type: Noise
         properties:
           parameters:
             normalise: true

    Providing an explicit amplitude can be quite helpful in case you want to
    control the signal-to-noise ratio and know the amplitude of your signal
    prior to adding noise. Adding noise with a noise amplitude of 0.01 would
    be done as follows:

    .. code-block:: yaml

       - kind: processing
         type: Noise
         properties:
           parameters:
             amplitude: 0.01

    Note that in case you do not provide an exponent, its default value will
    be used, resulting in pink (1/f) noise, as this is spectroscopically the
    most relevant.


    .. versionadded:: 0.3

    .. versionchanged:: 0.4
        Added reference to :attr:`references`

    .. versionchanged:: 0.6
        Added parameter ``amplitude``


    """

    def __init__(self):
        super().__init__()
        self.description = "Add (coloured) noise to data"
        self.undoable = True
        self.parameters["exponent"] = -1
        self.parameters["normalise"] = False
        self.parameters["amplitude"] = None
        self.references = [
            bib.Article(
                author=["J. Timmer", "M. König"],
                title="On generating power law noise",
                journal="Astronomy and Astrophysics",
                volume="300",
                pages="707--710",
                year="1995",
            )
        ]

    def _perform_task(self):
        noise = self._generate_noise()
        if self.parameters["normalise"] or self.parameters["amplitude"]:
            noise /= noise.max() - noise.min()
        if self.parameters["amplitude"]:
            noise *= self.parameters["amplitude"]
        self.dataset.data.data += noise

    def _generate_noise(self):
        size = list(self.dataset.data.data.shape)
        samples = size[0]
        frequencies = np.fft.rfftfreq(samples)
        frequencies[0] = 1 / len(frequencies)
        amplitudes = frequencies ** (self.parameters["exponent"] / 2)

        # Add dimensions to broadcast shape
        amplitudes = amplitudes[(Ellipsis,) + (np.newaxis,) * (len(size) - 1)]
        size[0] = len(frequencies)

        power = np.random.normal(scale=amplitudes, size=size)
        phase = np.random.normal(scale=amplitudes, size=size)

        # Nyquist frequency is real if length is even
        if not samples % 2:
            phase[-1, ...] = 0

        # DC component is real
        phase[0, ...] = 0

        components = power + 1j * phase

        noise = np.fft.irfft(components, n=samples, axis=0)
        return noise


class ChangeAxesValues(SingleProcessingStep):
    # noinspection PyUnresolvedReferences
    """
    Change values of individual axes.

    What sounds pretty much like data manipulation is sometimes a necessity
    due to the shortcoming of vendor file formats. Let's face it,
    but sometimes values read from raw data simply are wrong, due to wrong
    readout or wrong processing of these parameters within the device.
    Therefore, it seems much better to *transparently* change the respective
    axis values rather than having to modify raw data by hand. Using a
    processing step has two crucial advantages: (i) it allows for full
    reproducibility and traceability, and (ii) it can be done in context of
    recipe-driven data analysis, *i.e.* not requiring any programming skills.

    .. note::

        A real-world example: angular-dependent measurements recorded wrong
        angles in the raw data file, while the actual positions were correct.
        Assuming measurements from 0° to 180° in 10° steps, it is pretty
        straight-forward how to fix this problem: Assign equidistant values
        from 0° to 180° and use the information about the actual axis length.


    Attributes
    ----------
    parameters : :class:`dict`
        All parameters necessary for this step.

        range : :class:`list`
            The range of the axis, *i.e.* start and end value

        axes : :class:`list`
            The axes to set the new values for

            Can be an integer in case of a single axis, otherwise a list of
            integers. If omitted, all axes with values will be assumed
            (*i.e.*, one per data dimension).


    Raises
    ------
    IndexError
        Raised if index is out of range for axes or given number of axes and
        ranges is incompatible


    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. The examples focus each on a single
    aspect.

    In case you would like to change the axis range of a 1D dataset, things
    are as simple as:

    .. code-block:: yaml

       - kind: singleprocessing
         type: ChangeAxesValues
         properties:
           parameters:
             range: [35, 42]

    This would take the first axis (index 0) and set the range to linearly
    spaced data ranging from 35 to 42, of course with the same number of
    values as before.

    If you  want to change both axes in a 2D dataset, same here:

    .. code-block:: yaml

       - kind: singleprocessing
         type: ChangeAxesValues
         properties:
           parameters:
             range:
               - [35, 42]
               - [17.5, 21]

    This would set the range of the first axis (index 0) to the interval
    [35, 42], and the range of the second axis (index 1) to the interval
    [17.5, 21].

    More often, you may have a 2D dataset where you intend to change the
    values of only one axis. Suppose the example from above with
    angular-dependent measurements and the angles in the second dimension:

    .. code-block:: yaml

       - kind: singleprocessing
         type: ChangeAxesValues
         properties:
           parameters:
             range: [0, 180]
             axes: 1

    Here, the second axis (index 1) will be set accordingly.


    .. versionadded:: 0.3

    """

    def __init__(self):
        super().__init__()
        self.description = "Change axis values to given range"
        self.undoable = True
        self.parameters["range"] = None
        self.parameters["axes"] = None

    def _sanitise_parameters(self):
        if not isinstance(self.parameters["range"][0], list):
            self.parameters["range"] = [self.parameters["range"]]
        if self.parameters["axes"] is None:
            self.parameters["axes"] = list(
                range(len(self.parameters["range"]))
            )
        if not isinstance(self.parameters["axes"], list):
            self.parameters["axes"] = [self.parameters["axes"]]
        if max(self.parameters["axes"]) > (len(self.dataset.data.axes) - 2):
            # Note the -2 here: -1 for axes, -1 for zero-based indexing
            raise IndexError("Index out of range for axes")
        if len(self.parameters["axes"]) != len(self.parameters["range"]):
            raise IndexError("Axes and ranges must be compatible")

    def _perform_task(self):
        for idx in range(len(self.parameters["range"])):
            axis = self.parameters["axes"][idx]
            self.dataset.data.axes[axis].values = np.linspace(
                self.parameters["range"][idx][0],
                self.parameters["range"][idx][1],
                len(self.dataset.data.axes[axis].values),
            )


class RelativeAxis(SingleProcessingStep):
    # noinspection PyUnresolvedReferences
    """
    Create relative axis, centred about a given value.

    Sometimes, absolute axis values are less relevant than relative
    values, particularly if you're interested in differences in distances
    between several datasets, *e.g.* peak positions in spectroscopy.

    .. note::
        You can set an origin that is not within the range of the current
        axis values. In such case, you will see a warning, but as this may
        be a perfectly valid use case, no exception is thrown.


    Attributes
    ----------
    parameters : :class:`dict`
        All parameters necessary for this step.

        origin : :class:`float`
            The value the axis should be centred about

            This value is subtracted from the original axis values

            Default: centre value of the axis range

        axis : :class:`int`
            The index of the axis to be converted into a relative axis

            Default: 0


    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. The examples focus each on a single
    aspect.

    In case you would like to change the first axis to a relative axis and
    centre it about its central value, things are as simple as:

    .. code-block:: yaml

       - kind: singleprocessing
         type: RelativeAxis


    Of course, this is rarely a sensible use case, and you will usually
    want to provide a dedicated value for the origin of the new axis
    (*i.e.*, the axis value the current axis should be centred about).

    .. code-block:: yaml

       - kind: singleprocessing
         type: RelativeAxis
         properties:
           parameters:
             origin: 42


    Nothing prevents you from operating on multidimensional datasets,
    hence converting another axis than the first axis to a relative one.
    For making the second axis (with index 1) a relative axis,
    do something like that:

    .. code-block:: yaml

       - kind: singleprocessing
         type: RelativeAxis
         properties:
           parameters:
             origin: 42
             axis: 1


    .. versionadded:: 0.8

    """

    def __init__(self):
        super().__init__()
        self.description = "Change axis to relative axis"
        self.undoable = True
        self.parameters["origin"] = None
        self.parameters["axis"] = 0

    def _perform_task(self):
        axis = self.parameters["axis"]
        if not self.parameters["origin"]:
            origin_index = int(len(self.dataset.data.axes[axis].values) / 2)
            self.parameters["origin"] = self.dataset.data.axes[axis].values[
                origin_index
            ]
        self.dataset.data.axes[axis].values -= self.parameters["origin"]
        if not self._value_within_range(
            self.parameters["origin"], self.dataset.data.axes[axis].values
        ):
            logger.warning(
                "origin %f outside axis range [%f %f].",
                self.parameters["origin"],
                self.dataset.data.axes[axis].values[0],
                self.dataset.data.axes[axis].values[-1],
            )
        self.dataset.data.axes[axis].quantity = (
            "Δ" + self.dataset.data.axes[axis].quantity
        )

    @staticmethod
    def _value_within_range(value, range_):
        if value < min(range_) or value > max(range_):
            return False
        return True


class SliceRearrangement(SingleProcessingStep):
    """
    Rearrange slices of a dataset along one dimension.

    With multidimensional datasets, there is sometimes the need to rearrange
    the slices. Suppose you have a dataset containing original data,
    individual fitted components and the sum of the fitted components.
    Tasks operating on such dataset typically expect the individual slices
    in a certain sequence. If, however, the datasets originate from an
    external source that has a different sorting, you can use this step to
    rearrange the slices accordingly.

    You can either provide indices or axis values for ``positions``. For the
    latter, set the parameter "unit" accordingly. For details, see below.

    If you provide less positions than slices along this dimension exist,
    the remaining slices not covered in the "positions" parameter are
    appended to the positions list.

    If you provide the same position for a slice several times, the slice
    will be repeatedly inserted into the dataset, resulting in a larger
    dataset along the given axis dimension than before.

    Attributes
    ----------
    parameters : :class:`dict`
        All parameters necessary for this step.

        axis : :class:`int`
            Index of the axis to take the position from to rearrange the slices

            If an invalid axis is provided, an IndexError is raised.

            Default: 0

        positions : :class:`list`
            Positions and intended order of the slices to rearrange

            Positions can be given as axis indices (default) or axis values,
            if the parameter "unit" is set accordingly. For details, see below.

            If no position is provided or the given position is out of
            bounds for the given axis, a ValueError is raised.

            If fewer positions are provided than present in this dimension,
            the remaining positions are simply appended to the list.

            If a position is given more than once, the corresponding slice
            is introduced multiple times and the dataset enlarged along the
            given dimension/axis.

        unit : :class:`str`
            Unit used for specifying the positions: either "axis" or "index".

            If an invalid value is provided, a ValueError is raised.

            Default: "index"

    Raises
    ------
    aspecd.exceptions.NotApplicableToDatasetError
        Raised if dataset has not enough dimensions (*i.e.*, 1D dataset).

    ValueError
        Raised if index is out of bounds for given axis.

        Raised if wrong unit is given.

    IndexError
        Raised if axis is out of bounds for given dataset.


    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. The examples focus each on a single
    aspect.

    In the simplest case, just invoke the slice rearrangement with a list of
    positions only:

    .. code-block:: yaml

       - kind: processing
         type: SliceRearrangement
         properties:
           parameters:
             positions: [1, 0, 4, 2, 3]

    This will rearrange the slices along the first axis (index zero) in the
    given sequence.

    Typically, with 2D datasets, you will want to rearrange along the
    *second* axis:

    .. code-block:: yaml

       - kind: processing
         type: SliceRearrangement
         properties:
           parameters:
             axis: 1
             positions: [1, 0, 4, 2, 3]

    This will rearrange the slices along the second axis (index one) in the
    given sequence.

    Suppose you have a dataset with ten slices along the second dimension,
    but you only care about the first three positions and want them to
    appear in reverse order:

    .. code-block:: yaml

       - kind: processing
         type: SliceRearrangement
         properties:
           parameters:
             axis: 1
             positions: [2, 1, 0]

    This will reverse the first three slices along the second dimension
    (with index one), but keep the overall shape of the dataset.

    What happens if you provide one slice several times? The slice is
    inserted several times into your dataset, thus *expanding* the dataset
    along the given axis dimension:

    .. code-block:: yaml

       - kind: processing
         type: SliceRearrangement
         properties:
           parameters:
             axis: 1
             positions: [1, 0, 1]

    This will add the second slice of the original dataset at the first and
    third position (indices 0 and 2, respectively), thus expanding your
    dataset by one slice along the given dimension.

    .. versionadded:: 0.12

    """

    def __init__(self):
        super().__init__()
        self.description = "Rearrange slices"
        self.undoable = True
        self.parameters["positions"] = []
        self.parameters["axis"] = 0
        self.parameters["unit"] = "index"

    @staticmethod
    def applicable(dataset):
        """
        Check whether processing step is applicable to the given dataset.

        Slice extraction is only applicable to datasets with at least
        two-dimensional data.

        Parameters
        ----------
        dataset : :class:`aspecd.dataset.Dataset`
            dataset to check

        Returns
        -------
        applicable : :class:`bool`
            `True` if successful, `False` otherwise.

        """
        return len(dataset.data.axes) >= 3

    def _sanitise_parameters(self):
        if (
            not self.parameters["positions"]
            and self.parameters["positions"] != 0
        ):
            raise IndexError("No positions provided for slice rearrangement")
        self.parameters["positions"] = np.atleast_1d(
            self.parameters["positions"]
        )
        # self.parameters["axis"] = np.atleast_1d(self.parameters["axis"])
        if self.parameters["axis"] > self.dataset.data.data.ndim - 1:
            # pylint: disable=consider-using-f-string
            raise IndexError(
                "Axis %i out of bounds" % self.parameters["axis"]
            )
        self.parameters["unit"] = self.parameters["unit"].lower()
        if self.parameters["unit"] not in ["index", "axis"]:
            raise ValueError("Wrong unit, needs to be either index or axis.")
        if self._out_of_range():
            raise ValueError("Position(s) out of axis range.")

    def _out_of_range(self):
        axis = self.parameters["axis"]
        positions = self.parameters["positions"]
        if self.parameters["unit"] == "index":
            axis_length = self.dataset.data.data.shape[axis]
            out_of_range = np.argwhere(abs(positions) > axis_length).size
        else:
            out_of_range = (
                np.argwhere(
                    positions < min(self.dataset.data.axes[axis].values)
                ).size
                or np.argwhere(
                    positions > max(self.dataset.data.axes[axis].values)
                ).size
            )
        return out_of_range

    def _perform_task(self):
        indices = self._get_slice()
        self.dataset.data.data = self.dataset.data.data[indices]
        axis = self.parameters["axis"]
        self.dataset.data.axes[axis].values = self.dataset.data.axes[
            axis
        ].values[indices[axis]]

    def _get_slice(self):
        # Create empty slice object
        slice_object = []
        for _ in range(self.dataset.data.data.ndim):
            slice_object.append(slice(None))
        # Extract positions and overwrite slice object
        axis = self.parameters["axis"]
        if self.parameters["unit"] == "index":
            slice_ = self.parameters["positions"]
        else:
            slice_ = self._get_index(
                self.dataset.data.axes[axis].values,
                self.parameters["positions"],
            )
        remaining_positions = [
            pos
            for pos in range(len(self.dataset.data.axes[axis].values))
            if pos not in slice_
        ]
        slice_object[axis] = np.append(slice_, remaining_positions).astype(
            int
        )
        return tuple(slice_object)

    @staticmethod
    def _get_index(array, values):
        return np.searchsorted(array, values)


class Denoising1DSVD(SingleProcessingStep):
    """
    Denoise 1D data using singular value decomposition (SVD).

    SVD has been shown to be a powerful method for denoising data and is
    used in several slightly different ways, mostly for image or
    more general 2D data denoising. To use SVD for denoising 1D data,
    one first needs to create a 2D matrix from the original data. One way is
    to create a (partial) circulant matrix or some variant thereof.

    Being a non-parametric method for denoising, basically no assumptions on
    the shape of the actual signal are necessary. This is one of the big
    advantages over other methods such as filtering (see :class:`Filtering`
    for details): Accidental distortions of the signal are very unlikely.

    To avoid ringing artifacts at the ends of the reconstructed signal,
    an adaptive intermediate detrending is performed as well.

    The algorithm implemented here is based on:

    * X. C. Chen, Yu. A. Litvinov, M. Wang, Q. Wang, and Y. H. Zhang:
      Denoising scheme based on singular-value decomposition for
      one-dimensional spectra and its application in precision storage-ring
      mass spectrometry.
      *Physical Review E* **99**, 063320 (2019)
    * Chen, X.: (2019). A generic denoising method for 1D spectra based on
      singular value decomposition (v2.1). Zenodo.
      https://doi.org/10.5281/zenodo.2603558

    Hence, if using this code leads to a scientific publication,
    strongly consider citing the appropriate publication(s).


    Attributes
    ----------
    parameters : :class:`dict`
        All parameters necessary for this step.

        rank : :class:`int`
            Rank of the approximating matrix of the constructed partial
            circulant matrix from the sequence. The rank will automatically be
            determined by the algorithm. Hence, this parameter is read-only.
            For details of the algorithm, see the cited reference.

        fraction : :class:`float`
            Fraction of the data length used as rows of the constructed matrix.

            Sensible values are in the interval [0.1...0.4]*n, with n the
            size of the data vector.

            Larger values than 0.4 are unnecessary, and generally smaller
            values will speed up the process, as the matrix to be
            constructed is smaller. Furthermore, it seems that larger
            matrices not necessarily result in better denoising. For
            details, see the cited reference.

            Default: 0.2

        noise_threshold : :class:`float`
            Threshold below which the singular components are considered noise.

            Noise components are detected using the normalized mean total
            variation of the left singular vectors as an indicator.

            Default: 0.1

    Raises
    ------
    aspecd.exceptions.NotApplicableToDatasetError
        Raised if dataset is not 1D or has <=10 data points.


    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. The examples focus each on a single
    aspect.

    In the simplest case, just invoke the denoising without any further
    parameters:

    .. code-block:: yaml

        - kind: processing
          type: Denoising1DSVD

    If you ever want to change some of the (few) available parameters,
    *e.g.*, the size of the constructed matrix in fractions of the signal
    length, this is of course possible as well:

    .. code-block:: yaml

        - kind: processing
          type: Denoising1DSVD
          properties:
            parameters:
              fraction: 0.3

    Note, however, that enlarging the size of the constructed partial
    circulant matrix does not necessarily provide better results and usually
    slows down processing.

    .. versionadded:: 0.12


    """

    def __init__(self):
        super().__init__()
        self.description = "Denoising 1D data using SVD"
        self.undoable = True
        self.references = [
            bib.Article(
                author=[
                    "X. C. Chen",
                    "Yu. A. Litvinov",
                    "M. Wang,",
                    "Q. Wang",
                    "Y. H. Zhang",
                ],
                title="Denoising scheme based on singular-value "
                "decomposition for one-dimensional spectra and its "
                "application in precision storage-ring mass spectrometry",
                journal="Physical Review E",
                volume="99",
                pages="063320",
                year="2019",
            ),
            bib.Dataset(
                author=["Chen, Xiangcheng"],
                title="A generic denoising method for 1D spectra based on "
                "singular value decomposition",
                publisher="Zenodo",
                year="2019",
                version="v2.1 (2019-03-23)",
                doi="10.5281/zenodo.2603558",
            ),
        ]
        self.parameters["rank"] = 0
        self.parameters["fraction"] = 0.2
        self.parameters["noise_threshold"] = 0.1
        self._n_rows = 0
        self._matrix = None
        self._U = None  # noqa
        self._s = None  # noqa
        self._Vh = None  # noqa
        self._trend = None
        self._points_for_detrending = 11

    @staticmethod
    def applicable(dataset):
        """
        Check whether processing step is applicable to the given dataset.

        This method is only applicable to 1D datasets with >10 data points.

        Parameters
        ----------
        dataset : :class:`aspecd.dataset.Dataset`
            dataset to check

        Returns
        -------
        applicable : :class:`bool`
            `True` if successful, `False` otherwise.

        """
        return len(dataset.data.axes) == 2 and len(dataset.data.data) > 10

    def _sanitise_parameters(self):
        if not self._n_rows:
            self._n_rows = int(
                self.dataset.data.data.size * self.parameters["fraction"]
            )
        self.parameters["rank"] = 0
        if self.parameters["fraction"] > 1:
            raise ValueError("Fraction exceeds signal dimensions")
        if self.parameters["fraction"] < 0.1:
            raise ValueError("Fraction too small, minimum: 0.1")

    def _perform_task(self):
        self._create_matrix()
        self._perform_svd()
        self._determine_rank()
        self._detrend()
        self._reconstruct_matrix()
        self._average_matrix()

    def _create_matrix(self):
        extended_vector = np.hstack(
            (
                self.dataset.data.data,
                self.dataset.data.data[: self._n_rows - 1],
            )
        )
        shape = (self._n_rows, self.dataset.data.data.size)
        strides = (extended_vector.strides[0], extended_vector.strides[0])
        self._matrix = np.lib.stride_tricks.as_strided(
            extended_vector, shape, strides
        )

    def _perform_svd(self):
        self._U, self._s, self._Vh = np.linalg.svd(self._matrix)

    def _determine_rank(self):
        while True:
            left_singular_vectors = self._U[
                :, self.parameters["rank"] : self.parameters["rank"] + 10
            ]
            normalised_mean_total_variation = np.mean(
                np.abs(np.diff(left_singular_vectors, axis=0)), axis=0
            ) / (
                np.amax(left_singular_vectors, axis=0)
                - np.amin(left_singular_vectors, axis=0)
            )
            try:
                self.parameters["rank"] += np.argwhere(
                    normalised_mean_total_variation
                    > self.parameters["noise_threshold"]
                )[0, 0]
                break
            except IndexError:
                self.parameters["rank"] += 10

    def _detrend(self):
        self._trend = np.zeros_like(self.dataset.data.data)
        while self._needs_detrending():
            self._points_for_detrending -= 2
            self._trend = np.linspace(
                0,
                self.dataset.data.data[-self._points_for_detrending :].mean()
                - self.dataset.data.data[
                    : self._points_for_detrending
                ].mean(),
                self.dataset.data.data.size,
            )
            self.dataset.data.data -= self._trend
            self._create_matrix()
            self._perform_svd()
            self._determine_rank()

    def _needs_detrending(self):
        noise_stddev = np.sqrt(
            np.sum(self._s[self.parameters["rank"] :] ** 2)
            / self.dataset.data.data.size
        )
        gap = np.abs(
            self.dataset.data.data[-self._points_for_detrending :].mean()
            - self.dataset.data.data[: self._points_for_detrending].mean()
        )
        return gap > noise_stddev

    def _reconstruct_matrix(self):
        self._matrix = (
            self._U[:, : self.parameters["rank"]]
            @ np.diag(self._s[: self.parameters["rank"]])
            @ self._Vh[: self.parameters["rank"]]
        )

    def _average_matrix(self):
        extended_matrix = np.hstack(
            (self._matrix[:, -self._n_rows + 1 :], self._matrix)
        )
        strides = (
            extended_matrix.strides[0] - extended_matrix.strides[1],
            extended_matrix.strides[1],
        )
        self.dataset.data.data = np.mean(
            np.lib.stride_tricks.as_strided(
                extended_matrix[:, self._n_rows - 1 :],
                self._matrix.shape,
                strides,
            ),
            axis=0,
        )
        self.dataset.data.data += self._trend
