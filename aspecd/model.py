"""
Numerical models

Models are defined by (constant) parameters and variables the model is
evaluated for. The variables can be thought of as the axes values of the
resulting (calculated) dataset.

As a simple example, consider a polynomial defined by its (constant)
coefficients. The model will evaluate the polynomial for the values,
and the result will be a :obj:`aspecd.dataset.CalculatedDataset` object
containing the values of the evaluated model in its data, and the
variables as its axes values.

Models can be seen as abstraction to simulations in some regard. In this
respect, they will play a central role in conjunction with fitting
models to data by adjusting their respective parameters, a quite general
approach in science and particularly in spectroscopy.


A bit of terminology
====================

parameters :
    constant parameters (sometimes termed coefficients) characterising the model

    Example: In case of a polynomial, the coefficients would be the
    parameters of the model.

variables :
    values to evaluate the model for

    Example: In case of a polynomial, the *x* values the model is
    evaluated for would be the variables, with the *y* values being the
    corresponding depending values dictated by the model and its parameters.


Models provided within this module
==================================

Besides providing the basis for models for the ASpecD framework, this module
comes with a (growing) number of general-purpose models useful for basically
all kinds of spectroscopic data.

Here is a list as a first overview. For details, see the detailed
documentation of each of the classes, readily accessible by the link.

* :class:`aspecd.model.Polynomial`

  Polynomial (of arbitrary degree/order, depending on the number of
  coefficients)


.. todo::
    Implement further models, including, but probably not limited to:
    exponentials, sine, Gaussian, Lorentzian


Writing your own models
=======================

All models should inherit from the :class:`aspecd.model.Model` class.
Furthermore, they should conform to a series of requirements:

* Parameters are stored in the :attr:`aspecd.model.Model.parameters` dict.

  Note that this is a :class:`dict`. In the simplest case, you may name the
  corresponding key "coefficients", as in case of a polynomial. In other
  cases, there are common names for parameters, such as "mu" and "sigma" for
  a Gaussian. Whether the keys should be named this way or describe the
  actual meaning of the parameter is partly a matter of personal taste. Use
  whatever is more common in the given context, but tend to be descriptive.
  Usually, implementing mathematical equations by simply naming every
  variable according to the mathematical notation is a bad idea, as the
  programmer will not know what these variables represent.

* Models create calculated datasets of class
  :class:`aspecd.dataset.CalculatedDataset`.

  The data of these datasets need to have dimensions corresponding to the
  variables set for the model. Think of the variables as being the axes
  values of the resulting dataset.

  The ``_origdata`` property of the dataset is automatically set accordingly
  (see below for details). This is crucially important to have the resulting
  dataset work as expected, including undo and redo functionality within the
  ASpecD framework. Remember: A calculated dataset is a regular dataset,
  and you can perform all the tasks with you would do with other datasets,
  including processing, analysis and alike.

* Model creation takes place entirely in the non-public ``_perform_task``
  method of the model.

  This method gets called from :meth:`aspecd.model.Model.create`, but not
  before some background checks have been performed, including preparing the
  metadata of the :obj:`aspecd.dataset.CalculatedDataset` object returned by
  :meth:`aspecd.model.Model.create`.

  After calling out to ``_perform_task``, the axes of the
  :obj:`aspecd.dataset.CalculatedDataset` object returned by
  :meth:`aspecd.model.Model.create` are set accordingly, *i.e.* fitting to
  the shape of the data.


On the other hand, a series of things will be automatically taken care of
for you:

* Metadata of the resulting :obj:`aspecd.dataset.CalculatedDataset` object
  are automatically set, including ``type`` (set to the full class name of
  the model) and ``parameters`` (copied over from the parameters attribute
  of the model).

* Axes of the resulting :obj:`aspecd.dataset.CalculatedDataset` object are
  automatically adjusted according to the size and content of
  the :attr:`aspecd.model.Model.variables` attribute.

  In case you used :meth:`aspecd.model.Model.from_dataset`, the axes from
  the dataset will be copied over from there.

* The ``_origdata`` property of the dataset is automatically set accordingly
  (see below for details). This is crucially important to have the resulting
  dataset work as expected, including undo and redo functionality within the
  ASpecD framework.


Module documentation
====================

"""

import copy

import numpy as np

import aspecd.dataset
import aspecd.exceptions
import aspecd.utils


class Model:
    """
    Base class for numerical models.

    Models are defined by (constant) parameters and variables the model is
    evaluated for. The variables can be thought of as the axes values of the
    resulting (calculated) dataset.

    As a simple example, consider a polynomial defined by its (constant)
    coefficients. The model will evaluate the polynomial for the values,
    and the result will be a :obj:`aspecd.dataset.CalculatedDataset` object
    containing the values of the evaluated model in its data, and the
    variables as its axes values.

    Models can be seen as abstraction to simulations in some regard. In this
    respect, they will play a central role in conjunction with fitting
    models to data by adjusting their respective parameters, a quite general
    approach in science and particularly in spectroscopy.

    Attributes
    ----------
    name : :class:`str`
        Name of the model.

        Defaults to the lower-case class name, don't change!
    parameters : :class:`dict`
        constant parameters characterising the model

    variables : :class:`list`
       values to evaluate the model for

       Usually :class:`numpy.ndarray` arrays, one for each variable

       The variables will become the values of the respective axes.

    description : :class:`str`
        Short description, to be set in class definition


    .. versionchanged:: 0.3
        New attribute :attr:`description`

    .. versionchanged:: 0.3
        New non-public method :meth:`_sanitise_parameters`

    """

    def __init__(self):
        self.name = aspecd.utils.full_class_name(self)
        self.parameters = dict()
        self.variables = []
        self.description = 'Abstract model'
        self._dataset = aspecd.dataset.CalculatedDataset()
        self._axes_from_dataset = []

    def create(self):
        """
        Create dataset containing the evaluated model as data

        The actual model creation should be implemented within the non-public
        method :meth:`_perform_task`. Furthermore, you should make sure your
        model will be evaluated for the values given in
        :attr:`aspecd.model.Model.values` and the resulting dataset having set
        the axes appropriately.

        Furthermore, don't forget to set the ``_origdata`` property of the
        dataset, usually simply by copying the ``data`` property over there
        after it has been filled with content. This is crucially important
        to have the resulting dataset work as expected, including undo and
        redo functionality within the ASpecD framework. Remember: A
        calculated dataset is a regular dataset, and you can perform all the
        tasks with you would do with other datasets, including processing,
        analysis and alike.

        Returns
        -------
        dataset : :class:`aspecd.dataset.CalculatedDataset`
            Calculated dataset containing the evaluated model as data

        Raises
        ------
        aspecd.exceptions.MissingParameterError
            Raised if either parameters or values are not set

        """
        self._check_prerequisites()
        self._set_dataset_metadata()
        self._sanitise_parameters()
        self._perform_task()
        self._set_dataset_axes()
        self._set_dataset_origdata()
        return self._dataset

    def from_dataset(self, dataset=None):
        """
        Obtain crucial information from an existing dataset.

        Often, models should be calculated for the same values as an
        existing dataset. Therefore, you can set the
        :attr:`aspecd.model.Model.values` property from a given dataset.

        If you get the variables from an existing dataset, the calculated
        dataset containing the evaluated model will have the same axes
        settings. Thus, it is pretty convenient to get a model with
        identical axes, including quantity etcetera. This helps a lot with
        plotting both, an (experimental) dataset and the model, in one plot.

        Parameters
        ----------
        dataset : :class:`aspecd.dataset.Dataset`
            Dataset to obtain crucial information for building the model from

        Raises
        ------
        aspecd.exceptions.MissingDatasetError
            Raised if no dataset is provided

        """
        if not dataset:
            raise aspecd.exceptions.MissingDatasetError
        for index in range(len(dataset.data.axes)):
            self.variables.append(dataset.data.axes[index].values)
        self._axes_from_dataset = dataset.data.axes

    def from_dict(self, dict_=None):
        """
        Set attributes from dictionary.

        Parameters
        ----------
        dict_ : :class:`dict`
            Dictionary containing information of a task.

        Raises
        ------
        aspecd.plotting.MissingDictError
            Raised if no dict is provided.

        """
        if not dict_:
            raise aspecd.exceptions.MissingDictError(
                'Need a dict to read from, but none given')
        for key, value in dict_.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def _check_prerequisites(self):
        if not self.parameters:
            raise aspecd.exceptions.MissingParameterError(
                'No parameters for model provided')
        if len(self.variables) == 0:
            raise aspecd.exceptions.MissingParameterError(
                'No variables to evaluate model for provided')

    def _sanitise_parameters(self):
        """Ensure parameters provided for model are correct.

        Needs to be implemented in classes inheriting from Model
        according to their needs. Most probably, you want to check for
        correct types of all parameters as well as values within sensible
        borders.

        """

    def _perform_task(self):
        """Create the actual model and evaluate it for the given values.

        The implementation of the actual model goes in here in all
        classes inheriting from Model. This method is automatically
        called by :meth:`self.create` after some background checks.

        """
        # dummy to get tests to run
        self._dataset.data.data = self.variables[0]

    def _set_dataset_axes(self):
        """
        Set axes of calculated dataset

        In case a dataset has been used to obtain the variables for,
        the axes get set from this dataset.
        """
        if self._axes_from_dataset:
            self._dataset.data.axes = self._axes_from_dataset
        elif isinstance(self.variables[0], (list, np.ndarray)):
            for index in range(len(self.variables)):
                self._dataset.data.axes[index].values = self.variables[index]
        else:
            self._dataset.data.axes[0].values = self.variables

    def _set_dataset_metadata(self):
        """
        Set calculation metadata of calculated dataset

        Calculation type is set to the full class name of the respective
        model, and parameters are copied over from the model parameters.
        """
        self._dataset.metadata.calculation.type = self.name
        self._dataset.metadata.calculation.parameters = self.parameters

    def _set_dataset_origdata(self):
        self._dataset._origdata = copy.deepcopy(self._dataset.data)


class Polynomial(Model):
    # noinspection PyUnresolvedReferences
    """
    Polynomial.

    Evaluate a polynomial with given coefficients for the data provided in
    :attr:`aspecd.model.Model.variables`.

    .. note::
        As the new :mod:`numpy.polynomial` package is used, particularly
        the :class:`numpy.polynomial.polynomial.Polynomial` class,
        the coefficients are given in increasing order, with the first
        element corresponding to x**0.

        Furthermore, the coefficients are assumed to be provided in the
        unscaled data domain (by using the
        :meth:`numpy.polynomial.polynomial.Polynomial.convert` method).


    Attributes
    ----------
    parameters : :class:`dict`
        All parameters necessary for this step.

        coefficients : :class:`list`
            coefficients of the polynomial to be evaluated

            The number of coefficients determines the order (degree) of the
            polynomial. The coefficients have to be given in *increasing*
            order (see note above). Furthermore, you need to provide the
            coefficients in the unscaled data domain (using the
            :meth:`numpy.polynomial.polynomial.Polynomial.convert` method).

    Raises
    ------
    aspecd.exceptions.MissingParameterError
        Raised if no coefficients are given


    .. versionadded:: 0.3

    """

    def __init__(self):
        super().__init__()
        self.description = "Polynomial"
        self.parameters["coefficients"] = None

    def _sanitise_parameters(self):
        if not self.parameters["coefficients"]:
            raise aspecd.exceptions.MissingParameterError(
                message="Parameter 'coefficients' missing")

    def _perform_task(self):
        polynomial = np.polynomial.Polynomial(self.parameters["coefficients"])
        self._dataset.data.data = polynomial(self.variables)
