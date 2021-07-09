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


Primitive models
----------------

Primitive models are mainly used to create test datasets that can be
operated on afterwards. The particular strength and beauty of wrapping
essential one-liners of code with a full-fledged model class is twofold:
These classes return ASpecD datasets, and you can work completely in context
of recipe-driven data analysis, requiring no actual programming skills.

If nothing else, these primitive models can serve as a way to create
datasets with fixed data dimensions. Those datasets may be used as templates
for more advanced models, by using the :meth:`aspecd.model.Model.from_dataset`
method.

Having that said, here you go with a list of primitive models:


* :class:`aspecd.model.Zeros`

  Dataset consisting entirely of zeros (in N dimensions)

* :class:`aspecd.model.Ones`

  Dataset consisting entirely of ones (in N dimensions)


Mathematical models
-------------------

Besides the primitive models listed above, there is a growing number of
mathematical models implementing comparably simple mathematical equations
that are often used. Packages derived from the ASpecD framework may well
define more specific models as well.


* :class:`aspecd.model.Polynomial`

  Polynomial (of arbitrary degree/order, depending on the number of
  coefficients)

* :class:`aspecd.model.Gaussian`

  Generalised Gaussian where amplitude, position, and width can be
  set explicitly. Hence, this is usually *not* identical to the probability
  density function (PDF) of a normally distributed random variable.

* :class:`aspecd.model.NormalisedGaussian`

  Normalised Gaussian with an integral of one, identical to the probability
  density function (PDF) of a normally distributed random variable.

* :class:`aspecd.model.Lorentzian`

  Generalised Lorentzian where amplitude, position, and width can be
  set explicitly. Hence, this is usually *not* identical to the probability
  density function (PDF) of the Cauchy distribution.

* :class:`aspecd.model.NormalisedLorentzian`

  Normalised Lorentzian with an integral of one, identical to the probability
  density function (PDF) of the Cauchy distribution.

* :class:`aspecd.model.Sine`

  Sine wave with adjustable amplitude, frequency, and phase.

* :class:`aspecd.model.Exponential`

  Exponential function with adjustable prefactor and rate.


Composite models consisting of a sum of individual models
---------------------------------------------------------

Often you encounter situations where a model consists of a (weighted) sum of
individual models. A simple example would be a damped oscillation. Or think
of a spectral line consisting of several overlapping individual lines
(Lorentzian or Gaussian).

All this can be easily set up using the :class:`aspecd.model.CompositeModel`
class that lets you conveniently specify a list of models, their individual
parameters, and optional weights.


Family of curves
----------------

Systematically varying one parameter at a time for a given model is key
to understanding the impact this parameter has. Therefore, automatically
creating a family of curves with one parameter varied is quite convenient.

To achieve this, use the class :class:`aspecd.model.FamilyOfCurves` that will
take the name of a model (needs to be the name of an existing model class)
and create a family of curves for this model, adding the name of the
parameter as quantity to the additional axis.


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

* The ``_origdata`` property of the dataset is automatically set accordingly.
  This is crucially important to have the resulting dataset work as
  expected, including undo and redo functionality within the ASpecD framework.


Make sure your models do not raise errors such as :class:`ZeroDivisionError`
depending on the parameters set. Use the :func:`aspecd.utils.not_zero`
function where appropriate. This is particularly important in light of using
models in the context of automated fitting.


Module documentation
====================

"""

import copy

import numpy as np

import aspecd.dataset
import aspecd.exceptions
import aspecd.utils
from aspecd.utils import not_zero, iterable


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
        self._sanitise_parameters()
        self._check_prerequisites()
        self._set_dataset_metadata()
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
            self._dataset.data.axes[0].values = np.asarray(self.variables)

    def _set_dataset_metadata(self):
        """
        Set calculation metadata of calculated dataset

        Calculation type is set to the full class name of the respective
        model, and parameters are copied over from the model parameters.
        """
        self._dataset.metadata.calculation.type = self.name
        self._dataset.metadata.calculation.parameters = self.parameters

    def _set_dataset_origdata(self):
        # pylint: disable=protected-access
        self._dataset._origdata = copy.deepcopy(self._dataset.data)


class CompositeModel(Model):
    """
    Composite model consisting of a weighted contributions of individual models.

    Individual models can either be added up (default) or multiplied,
    depending on which operators are provided. Both situations occur
    frequently. If you would like to describe a spectrum as sum of Gaussian
    or Lorentzian lines, you need to add the individual contributions. If
    you would like to model a damped oscillation, you would need to multiply
    the exponential decay onto the oscillation.

    Attributes
    ----------
    models : :class:`list`
        Names of the models the composite model consists of

        Each name needs to be the name of an existing model class.

    parameters : :class:`list`
        Constant parameters characterising each individual model

        For the parameters that can (and need to) be set, consult the
        documentation of each of the respective model classes specified in
        the :attr:`models` attribute.

    weights : :class:`list`
        Factors used to weight the individual models.

        Default: no weighting

    operators : :class:`list`
        Operators to be used for the individual models.

        Addition ("+", "add", "plus") and multiplication ("*", "multiply",
        "times") are supported.

        Note that one operator less than models needs to be provided.

        Default: add


    Raises
    ------
    IndexError
        Raised if number of models, parameter sets, operators, and weights are
        incompatible


    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. The examples focus each on a single
    aspect.

    Suppose you would want to describe your data with a model consisting of
    two Lorentzian line shapes. Starting from scratch, you need to create a
    dummy dataset (using, *e.g.*, :class:`aspecd.model.Zeros`) of given
    length and axes range. Based on that you can create your model:

    .. code-block:: yaml

       - kind: model
         type: Zeros
         properties:
           parameters:
             shape: 1001
             range: [0, 20]
         result: dummy

       - kind: model
         type: CompositeModel
         from_dataset: dummy
         properties:
           models:
             - Lorentzian
             - Lorentzian
           parameters:
             - position: 3
             - position: 5
         result: multiple_lorentzians

    Note that you need to provide parameters for each of the individual
    models, even if the class for a model would work without explicitly
    providing parameters.

    Of course, if you start with an existing dataset (*e.g.*, loaded from
    some real data), you could use the label to this dataset directly in
    ``from_dataset``, without needing to create a dummy dataset first.

    While adding up the contributions of the individual components works
    well for describing spectra, sometimes you need to multiply contributions.
    Suppose you would want to create a damped oscillation consisting of a
    sine and an exponential. Starting from scratch, you need to create a
    dummy dataset (using, *e.g.*, :class:`aspecd.model.Zeros`) of given
    length and axes range. Based on that you can create your model:

    .. code-block:: yaml

       - kind: model
         type: Zeros
         properties:
           parameters:
             shape: 1001
             range: [0, 20]
         result: dummy

       - kind: model
         type: CompositeModel
         from_dataset: dummy
         properties:
           models:
             - Sine
             - Exponential
           parameters:
             - frequency: 1
               phase: 1.57
             - rate: -1
           operators:
             - multiply
         result: damped_oscillation

    Again, you need to provide parameters for each of the individual
    models, even if the class for a model would work without explicitly
    providing parameters.


    .. versionadded:: 0.3

    """

    def __init__(self):
        super().__init__()
        self.description = \
            'Composite model consisting of several weighted models'
        self.models = []
        self.parameters = []
        self.weights = []
        self.operators = []

    def _sanitise_parameters(self):
        if not self.weights:
            self.weights = np.ones(len(self.models))
        if not self.operators:
            for _ in self.models:
                self.operators.append('+')
        else:
            self.operators.insert(0, '+')
        if len(self.parameters) != len(self.models):
            raise IndexError('Models and parameters count differs')
        if len(self.weights) != len(self.models):
            raise IndexError('Models and weights count differs')
        if len(self.operators) != len(self.models):
            raise IndexError('Models and operators count differs')

    def _perform_task(self):
        data = np.zeros(len(self.variables))
        for idx, model_name in enumerate(self.models):
            model = self._get_model(model_name)
            for key in self.parameters[idx]:
                # noinspection PyUnresolvedReferences
                model.parameters[key] = self.parameters[idx][key]
            model.variables = self.variables
            # noinspection PyUnresolvedReferences
            dataset = model.create()
            if self.operators[idx] in ('+', 'plus', 'add'):
                data += dataset.data.data * self.weights[idx]
            if self.operators[idx] in ('*', 'times', 'multiply'):
                data *= dataset.data.data * self.weights[idx]
        self._dataset.data.data = data

    @staticmethod
    def _get_model(model_name):
        try:
            model = aspecd.utils.object_from_class_name(model_name)
        except (ValueError, AttributeError):
            model = aspecd.utils.object_from_class_name('aspecd.model.' +
                                                        model_name)
        return model


class FamilyOfCurves(Model):
    """
    Create a family of curves for a model, varying a single parameter.

    Systematically varying one parameter at a time for a given model is key
    to understanding the impact this parameter has. Therefore, automatically
    creating a family of curves with one parameter varied is quite convenient.

    This class will take the name of a model (needs to be the name of an
    existing model class) and create a family of curves for this model,
    adding the name of the parameter as quantity to the additional axis.


    Attributes
    ----------
    model : :class:`str`
        Name of the model the family of curves should be calculated for

        Needs to be the name of an existing model class.

    vary : :class:`dict`
        Name and values of the parameter to be varied

        parameter : :class:`str`
            Name of the parameter that should be varied

        values : :class:`list`
            Values of the parameter to be varied


    Raises
    ------
    ValueError
        Raised if no model is provided


    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. The examples focus each on a single
    aspect.

    Suppose you would want to create a family of curves of a Gaussian with
    varying the width. Starting from scratch, you need to create a
    dummy dataset (using, *e.g.*, :class:`aspecd.model.Zeros`) of given
    length and axes range. Based on that you can create your family of curves:

    .. code-block:: yaml

       - kind: model
         type: Zeros
         properties:
           parameters:
             shape: 1001
             range: [0, 20]
         result: dummy

       - kind: model
         type: FamilyOfCurves
         from_dataset: dummy
         properties:
           model: Gaussian
           vary:
             parameter: width
             values: [1., 1.5, 2., 2.5, 3]
         result: gaussian_with_varied_width

    This would create a 2D dataset with a Gaussian with standard values for
    amplitude and position and the value for the width varied as given.

    Of course, if you start with an existing dataset (*e.g.*, loaded from
    some real data), you could use the label to this dataset directly in
    ``from_dataset``, without needing to create a dummy dataset first.

    If you would like to control additional parameters of the Gaussian,
    you can do that as well:

    .. code-block:: yaml

       - kind: model
         type: FamilyOfCurves
         from_dataset: dummy
         properties:
           model: Gaussian
           parameters:
             amplitude: 3.
             position: -1
           vary:
             parameter: width
             values: [1., 1.5, 2., 2.5, 3]
         result: gaussian_with_varied_width

    Note that if you provide a value for the parameter to be varied in the
    list of parameters, it will be silently overwritten by the values
    provided with ``vary``.


    .. versionadded:: 0.3

    """

    def __init__(self):
        super().__init__()
        self.description = 'Family of curves for a model with one parameter ' \
                           'varied'
        self.model = None
        self.vary = dict()

    def _sanitise_parameters(self):
        if not self.model:
            raise ValueError('Missing a model')
        if not iterable(self.vary["values"]):
            self.vary["values"] = [self.vary["values"]]
        if not self.parameters:
            self.parameters[self.vary["parameter"]] = self.vary["values"][0]

    # noinspection PyUnresolvedReferences
    def _perform_task(self):
        self._dataset.data.data = \
            np.zeros([len(self.variables), len(self.vary["values"])])
        model = self._get_model(self.model)
        model.variables = self.variables
        for key in self.parameters:
            model.parameters[key] = self.parameters[key]
        for idx, value in enumerate(self.vary["values"]):
            model.parameters[self.vary["parameter"]] = value
            dataset = model.create()
            self._dataset.data.data[:, idx] = dataset.data.data
        self._dataset.data.axes[-1].quantity = self.vary["parameter"]

    @staticmethod
    def _get_model(model_name):
        try:
            model = aspecd.utils.object_from_class_name(model_name)
        except (ValueError, AttributeError):
            model = aspecd.utils.object_from_class_name('aspecd.model.' +
                                                        model_name)
        return model


class Zeros(Model):
    # noinspection PyUnresolvedReferences
    """
    Zeros of given shape.

    One of the most primitive models: zeros in N dimensions.

    This model is quite helpful for creating test datasets, *e.g.* with
    added noise (of different colour). Basically, it can be thought of as a
    wrapper for :func:`numpy.zeros`. Its particular strength is that using
    this model, creating test datasets becomes straight-forward in context
    of recipe-driven data analysis.


    Attributes
    ----------
    parameters : :class:`dict`
        All parameters necessary for this step.

        shape : :class:`list`
            shape of the data

            Have in mind that ND datasets get huge very fast. Therefore,
            it is *not* the best idea to create an 3D dataset with zeros
            with 2**12 elements along each dimension.

        range : :class:`list`
            range of each of the axes

            Useful if you want to specify the axes values as well.

            If the data are multidimensional, one range for each axis needs
            to be provided.

    Raises
    ------
    aspecd.exceptions.MissingParameterError
        Raised if no shape is given

    IndexError
        Raised if elements in shape and range are incompatible


    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. The examples focus each on a single
    aspect.

    Creating a dataset consisting of 2**10 zeros is quite simple:

    .. code-block:: yaml

       - kind: model
         type: Zeros
         properties:
           parameters:
             shape: 1024
         result: 1d_zeros

    Of course, you are not limited to 1D datasets, and you can easily create
    ND datasets as well:

    .. code-block:: yaml

       - kind: model
         type: Zeros
         properties:
           parameters:
             shape: [1024, 256, 256]
         result: 3d_zeros

    Please have in mind that the memory of your computer is usually limited
    and that ND datasets become huge very fast. Hence, creating a 3D array
    with 2**10 elements along each dimension is most probably *not* the best
    idea.

    Suppose you not only want to create a dataset with a given shape,
    but set the axes values (*i.e.*, their range) as well:

    .. code-block:: yaml

       - kind: model
         type: Zeros
         properties:
           parameters:
             shape: 1024
             range: [35, 42]
         result: 1d_zeros

    This would create a 1D dataset with 1024 values, with the axes
    values spanning a range from 35 to 42. Of course, the same can be done
    with ND datasets.

    Now, let's assume that you would want to play around with the different
    types of (coloured) noise. Therefore, you would want to first create a
    dataset and afterwards add noise to it:

    .. code-block:: yaml

       - kind: model
         type: Zeros
         properties:
           parameters:
             shape: 8192
         result: 1d_zeros

       - kind: processing
         type: Noise
         properties:
           parameters:
             normalise: True

    This would create a dataset consisting of 2**14 zeros and add pink
    (1/*f*) noise to it that is normalised (has an amplitude of 1). To check
    that the noise is really 1/*f* noise, you may look at its power density.
    See :class:`aspecd.analysis.PowerDensitySpectrum` for details, including
    how to even plot both, the power density spectrum and a linear fit
    together in one figure.


    .. versionadded:: 0.3

    """

    def __init__(self):
        super().__init__()
        self.description = "Model containing only zeros"
        self.parameters["shape"] = None
        self.parameters["range"] = None

    def _sanitise_parameters(self):
        if not self.variables:
            self.variables = [0]
            if not self.parameters["shape"]:
                raise aspecd.exceptions.MissingParameterError(
                    message="Parameter 'shape' missing")
        if not self.parameters["shape"]:
            self.parameters["shape"] = []
            if iterable(self.variables[0]):
                for index in range(len(self.variables)):
                    # noinspection PyTypeChecker
                    self.parameters["shape"].append(len(self.variables[index]))
            else:
                self.parameters["shape"] = len(self.variables)
        if not iterable(self.parameters["shape"]):
            self.parameters["shape"] = [self.parameters["shape"]]
        if self.parameters["range"]:
            if not iterable(self.parameters["range"][0]):
                self.parameters["range"] = [self.parameters["range"]]
            if len(self.parameters["shape"]) != len(self.parameters["range"]):
                raise IndexError('Shape and range must be compatible')

    def _perform_task(self):
        self._dataset.data.data = np.zeros(self.parameters["shape"])
        if self.parameters["range"]:
            self._set_variables()

    def _set_variables(self):
        self.variables = []
        shape = self.parameters["shape"]
        range_ = self.parameters["range"]
        for dim in range(self._dataset.data.data.ndim):
            axis_values = \
                np.linspace(range_[dim][0], range_[dim][1], shape[dim])
            self.variables.append(axis_values)


class Ones(Model):
    # noinspection PyUnresolvedReferences
    """
    Ones of given shape.

    One of the most primitive models: ones in N dimensions.

    This model is quite helpful for creating test datasets, *e.g.* with
    added noise (of different colour). Basically, it can be thought of as a
    wrapper for :func:`numpy.ones`. Its particular strength is that using
    this model, creating test datasets becomes straight-forward in context
    of recipe-driven data analysis.


    Attributes
    ----------
    parameters : :class:`dict`
        All parameters necessary for this step.

        shape : :class:`list`
            shape of the data

            Have in mind that ND datasets get huge very fast. Therefore,
            it is *not* the best idea to create an 3D dataset with ones
            with 2**12 elements along each dimension.

        range : :class:`list`
            range of each of the axes

            Useful if you want to specify the axes values as well.

            If the data are multidimensional, one range for each axis needs
            to be provided.

    Raises
    ------
    aspecd.exceptions.MissingParameterError
        Raised if no shape is given

    IndexError
        Raised if elements in shape and range are incompatible


    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. The examples focus each on a single
    aspect.

    Creating a dataset consisting of 2**10 ones is quite simple:

    .. code-block:: yaml

       - kind: model
         type: Ones
         properties:
           parameters:
             shape: 1024
         result: 1d_ones

    Of course, you are not limited to 1D datasets, and you can easily create
    ND datasets as well:

    .. code-block:: yaml

       - kind: model
         type: Ones
         properties:
           parameters:
             shape: [1024, 256, 256]
         result: 3d_ones

    Please have in mind that the memory of your computer is usually limited
    and that ND datasets become huge very fast. Hence, creating a 3D array
    with 2**10 elements along each dimension is most probably *not* the best
    idea.

    Suppose you not only want to create a dataset with a given shape,
    but set the axes values (*i.e.*, their range) as well:

    .. code-block:: yaml

       - kind: model
         type: Ones
         properties:
           parameters:
             shape: 1024
             range: [35, 42]
         result: 1d_zeros

    This would create a 1D dataset with 1024 values, with the axes
    values spanning a range from 35 to 42. Of course, the same can be done
    with ND datasets.

    Now, let's assume that you would want to play around with the different
    types of (coloured) noise. Therefore, you would want to first create a
    dataset and afterwards add noise to it:

    .. code-block:: yaml

       - kind: model
         type: Ones
         properties:
           parameters:
             shape: 8192
         result: 1d_ones

       - kind: processing
         type: Noise
         properties:
           parameters:
             normalise: True

    This would create a dataset consisting of 2**14 ones and add pink
    (1/*f*) noise to it that is normalised (has an amplitude of 1). To check
    that the noise is really 1/*f* noise, you may look at its power density.
    See :class:`aspecd.analysis.PowerDensitySpectrum` for details, including
    how to even plot both, the power density spectrum and a linear fit
    together in one figure.


    .. versionadded:: 0.3

    """

    def __init__(self):
        super().__init__()
        self.description = "Model containing only ones"
        self.parameters["shape"] = None
        self.parameters["range"] = None

    def _sanitise_parameters(self):
        if not self.variables:
            self.variables = [0]
            if not self.parameters["shape"]:
                raise aspecd.exceptions.MissingParameterError(
                    message="Parameter 'shape' missing")
        if not self.parameters["shape"]:
            self.parameters["shape"] = []
            if iterable(self.variables[0]):
                for index in range(len(self.variables)):
                    # noinspection PyTypeChecker
                    self.parameters["shape"].append(len(self.variables[index]))
            else:
                self.parameters["shape"] = len(self.variables)
        if not iterable(self.parameters["shape"]):
            self.parameters["shape"] = [self.parameters["shape"]]
        if self.parameters["range"]:
            if not iterable(self.parameters["range"][0]):
                self.parameters["range"] = [self.parameters["range"]]
            if len(self.parameters["shape"]) != len(self.parameters["range"]):
                raise IndexError('Shape and range must be compatible')

    def _perform_task(self):
        self._dataset.data.data = np.ones(self.parameters["shape"])
        if self.parameters["range"]:
            self._set_variables()

    def _set_variables(self):
        self.variables = []
        shape = self.parameters["shape"]
        range_ = self.parameters["range"]
        for dim in range(self._dataset.data.data.ndim):
            axis_values = \
                np.linspace(range_[dim][0], range_[dim][1], shape[dim])
            self.variables.append(axis_values)


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


    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. The examples focus each on a single
    aspect.

    Suppose you would want to create a Polynomial of first order with a
    slope of 42 and an intercept of -3. Starting from scratch, you need to
    create a dummy dataset (using, *e.g.*, :class:`aspecd.model.Zeros`) of
    given length and axes range. Based on that you can create your Polynomial:

    .. code-block:: yaml

       - kind: model
         type: Zeros
         properties:
           parameters:
             shape: 1001
             range: [-5, 5]
         result: dummy

       - kind: model
         type: Polynomial
         from_dataset: dummy
         properties:
           parameters:
             coefficients: [-3, 42]
         result: polynomial

    Note that the coefficients are given in *increasing* order of the
    exponent, here intercept first, followed by the slope.

    Of course, if you start with an existing dataset (*e.g.*, loaded from
    some real data), you could use the label to this dataset directly in
    ``from_dataset``, without needing to create a dummy dataset first.


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


class Gaussian(Model):
    # noinspection PyUnresolvedReferences
    r"""
    Generalised Gaussian.

    Creates a Gaussian function or Gaussian, with its characteristic
    symmetric "bell curve" shape.

    The underlying mathematical equation may be written as follows:

    .. math::

        f(x) = a \exp\left(-\frac{(x-b)^2}{2c^2}\right)

    with :math:`a` being the amplitude, :math:`b` the position,
    and :math:`c` the width of the Gaussian.

    .. important::
        Note that this is a generalised Gaussian where you can set
        amplitude, position, and width independently. Hence, it is *not*
        normalised to an integral of one, and therefore *not* to be confused
        with the the probability density function (PDF) of a normally
        distributed random variable. If you are interested in this, see the
        :class:`aspecd.model.NormalisedGaussian` class.


    Attributes
    ----------
    parameters : :class:`dict`
        All parameters necessary for this step.

        amplitude : :class:`float`
            Amplitude or height of the Gaussian

            Default: 1

        position : :class:`float`
            Position (of the maximum) of the Gaussian

            Default: 0

        width : :class:`float`
            Width of the Gaussian

            The full width at half maximum (FWHM) is related to the width
            *b* by: :math:`2 \sqrt{2 \log(2)} b`.

            Default: 1


    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. The examples focus each on a single
    aspect.

    Suppose you would want to create a Gaussian with standard values
    (amplitude=1, position=0, width=1). Starting from scratch, you need to
    create a dummy dataset (using, *e.g.*, :class:`aspecd.model.Zeros`) of
    given length and axes range. Based on that you can create your Gaussian:

    .. code-block:: yaml

       - kind: model
         type: Zeros
         properties:
           parameters:
             shape: 1001
             range: [-5, 5]
         result: dummy

       - kind: model
         type: Gaussian
         from_dataset: dummy
         result: gaussian

    Of course, if you start with an existing dataset (*e.g.*, loaded from
    some real data), you could use the label to this dataset directly in
    ``from_dataset``, without needing to create a dummy dataset first.

    Of course, you can control all three parameters (amplitude, position,
    width) explicitly:

    .. code-block:: yaml

       - kind: model
         type: Gaussian
         properties:
           parameters:
             amplitude: 5
             position: 1.5
             width: 0.5
         from_dataset: dummy
         result: gaussian

    This would create a Gaussian with an amplitude (height) of 5, situated
    at a value of 1.5 at the *x* axis, and with a width of 0.5.

    .. versionadded:: 0.3

    """

    def __init__(self):
        super().__init__()
        self.description = "Generalised Gaussian"
        self.parameters["amplitude"] = 1
        self.parameters["position"] = 0
        self.parameters["width"] = 1

    def _perform_task(self):
        x = np.asarray(self.variables)  # pylint: disable=invalid-name
        amplitude = self.parameters["amplitude"]
        position = self.parameters["position"]
        width = self.parameters["width"]
        gaussian = \
            amplitude * np.exp(-(x - position)**2 / not_zero(2 * width**2))
        self._dataset.data.data = gaussian


class NormalisedGaussian(Model):
    # noinspection PyUnresolvedReferences
    r"""
    Normalised Gaussian.

    Creates a Gaussian function or Gaussian, with its characteristic
    symmetric "bell curve" shape, normalised to an integral of one. Thus,
    it is the probability density function (PDF) of a normally distributed
    random variable.

    The underlying mathematical equation may be written as follows:

    .. math::

        f(x) = \frac{1}{\sigma\sqrt{2\pi}} \exp\left(-\frac{(x-\mu)^2}{
        2\sigma^2}\right)

    with :math:`\mu` being the position and :math:`\sigma` the width of the
    Gaussian, and :math:`\sigma^2` the variance.

    .. note::

        This class creates a normalised Gaussian, equivalent to the PDF of a
        normally distributed random variable. If you are interested in a
        Gaussian where you can set all three parameters (amplitude,
        position, width) independently, see the
        :class:`aspecd.model.Gaussian` class.


    Attributes
    ----------
    parameters : :class:`dict`
        All parameters necessary for this step.

        position : :class:`float`
            Position (of the maximum) of the Gaussian

            For a normally distributed random variable :math:`x`,
            the position is identical to its expected value :math:`E(x)` or
            mean :math:`\mu`. Other names include first moment and average.

            Default: 0

        width : :class:`float`
            Width of the Gaussian

            The full width at half maximum (FWHM) is related to the width
            :math:`\sigma` by: :math:`2 \sqrt{2 \log(2)} \sigma`. The
            squared value of the width is better known the variance
            :math:`\sigma^2`.

            Default: 1


    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. The examples focus each on a single
    aspect.

    Suppose you would want to create a normalised Gaussian with standard values
    (position=0, width=1). Starting from scratch, you need to create a dummy
    dataset (using, *e.g.*, :class:`aspecd.model.Zeros`) of given length and
    axes range. Based on that you can create your normalised Gaussian:

    .. code-block:: yaml

       - kind: model
         type: Zeros
         properties:
           parameters:
             shape: 1001
             range: [-5, 5]
         result: dummy

       - kind: model
         type: NormalisedGaussian
         from_dataset: dummy
         result: normalised_gaussian

    Of course, if you start with an existing dataset (*e.g.*, loaded from
    some real data), you could use the label to this dataset directly in
    ``from_dataset``, without needing to create a dummy dataset first.

    Of course, you can control position and width explicitly:

    .. code-block:: yaml

       - kind: model
         type: NormalisedGaussian
         properties:
           parameters:
             position: 1.5
             width: 0.5
         from_dataset: dummy
         result: normalised_gaussian

    This would create a normalised Gaussian with its maximum situated
    at a value of 1.5 at the *x* axis, and with a width of 0.5.

    .. versionadded:: 0.3

    """

    def __init__(self):
        super().__init__()
        self.description = "Normalised Gaussian"
        self.parameters["position"] = 0
        self.parameters["width"] = 1

    def _perform_task(self):
        x = np.asarray(self.variables)  # pylint: disable=invalid-name
        position = self.parameters["position"]
        width = self.parameters["width"]
        amplitude = 1 / not_zero(width * np.sqrt(2 * np.pi))
        gaussian = \
            amplitude * np.exp(-(x - position)**2 / not_zero(2 * width**2))
        self._dataset.data.data = gaussian


class Lorentzian(Model):
    # noinspection PyUnresolvedReferences
    r"""
    Generalised Lorentzian.

    Creates a Lorentzian function or Lorentzian often used in spectroscopy,
    as the line shape of a purely lifetime-broadened spectral line is
    identical to such a Lorentzian.

    The underlying mathematical equation may be written as follows:

    .. math::

        f(x) = a \left[\frac{c^2}{(x-b)^2 + c^2}\right]

    with :math:`a` being the amplitude, :math:`b` the position,
    and :math:`c` the width of the Lorentzian.

    .. important::
        Note that this is a generalised Lorentzian where you can set
        amplitude, position, and width independently. Hence, it is *not*
        normalised to an integral of one, and therefore *not* to be confused
        with the the probability density function (PDF) of the Cauchy
        distribution. If you are interested in this, see the
        :class:`aspecd.model.NormalisedLorentzian` class.


    Attributes
    ----------
    parameters : :class:`dict`
        All parameters necessary for this step.

        amplitude : :class:`float`
            Amplitude or height of the Lorentzian

            Default: 1

        position : :class:`float`
            Position (of the maximum) of the Lorentzian

            Default: 0

        width : :class:`float`
            Width of the Lorentzian

            The full width at half maximum (FWHM) is related to the width
            :math:`b` by: :math:`2b`.

            Default: 1


    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. The examples focus each on a single
    aspect.

    Suppose you would want to create a Lorentzian with standard values
    (amplitude=1, position=0, width=1). Starting from scratch, you need to
    create a dummy dataset (using, *e.g.*, :class:`aspecd.model.Zeros`) of
    given length and axes range. Based on that you can create your Lorentzian:

    .. code-block:: yaml

       - kind: model
         type: Zeros
         properties:
           parameters:
             shape: 1001
             range: [-5, 5]
         result: dummy

       - kind: model
         type: Lorentzian
         from_dataset: dummy
         result: lorentzian

    Of course, if you start with an existing dataset (*e.g.*, loaded from
    some real data), you could use the label to this dataset directly in
    ``from_dataset``, without needing to create a dummy dataset first.

    Of course, you can control all three parameters (amplitude, position,
    width) explicitly:

    .. code-block:: yaml

       - kind: model
         type: Lorentzian
         properties:
           parameters:
             amplitude: 5
             position: 1.5
             width: 0.5
         from_dataset: dummy
         result: lorentzian

    This would create a Lorentzian with an amplitude (height) of 5, situated
    at a value of 1.5 at the *x* axis, and with a width of 0.5.

    .. versionadded:: 0.3

    """

    def __init__(self):
        super().__init__()
        self.description = "Generalised Lorentzian"
        self.parameters["amplitude"] = 1
        self.parameters["position"] = 0
        self.parameters["width"] = 1

    def _perform_task(self):
        x = np.asarray(self.variables)  # pylint: disable=invalid-name
        amplitude = self.parameters["amplitude"]
        position = self.parameters["position"]
        width = self.parameters["width"]
        lorentzian = \
            amplitude * (width**2 / ((x - position)**2 + not_zero(width**2)))
        self._dataset.data.data = lorentzian


class NormalisedLorentzian(Model):
    # noinspection PyUnresolvedReferences
    r"""
    Normalised Lorentzian.

    Creates a normalised Lorentzian function or Lorentzian with an integral
    of one, *i.e.* the probability density function (PDF) of the Cauchy
    distribution.

    The underlying mathematical equation may be written as follows:

    .. math::

        f(x) = \frac{1}{\pi b} \left[\frac{c^2}{(x-b)^2 + c^2}\right]

    with :math:`b` being the position and :math:`c` the width of the
    Lorentzian.

    .. note::

        This class creates a normalised Lorentzian, equivalent to the PDF of
        the Cauchy distribution. If you are interested in a Lorentzian where
        you can set all three parameters (amplitude, position, width)
        independently, see the :class:`aspecd.model.Lorentzian` class.


    Attributes
    ----------
    parameters : :class:`dict`
        All parameters necessary for this step.

        position : :class:`float`
            Position (of the maximum) of the Lorentzian

            Default: 0

        width : :class:`float`
            Width of the Lorentzian

            The full width at half maximum (FWHM) is related to the width
            :math:`b` by: :math:`2b`.

            Default: 1


    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. The examples focus each on a single
    aspect.

    Suppose you would want to create a normalised Lorentzian with standard
    values (position=0, width=1). Starting from scratch, you need to create
    a dummy dataset (using, *e.g.*, :class:`aspecd.model.Zeros`) of given
    length and axes range. Based on that you can create your Lorentzian:

    .. code-block:: yaml

       - kind: model
         type: Zeros
         properties:
           parameters:
             shape: 1001
             range: [-5, 5]
         result: dummy

       - kind: model
         type: NormalisedLorentzian
         from_dataset: dummy
         result: normalised_lorentzian

    Of course, if you start with an existing dataset (*e.g.*, loaded from
    some real data), you could use the label to this dataset directly in
    ``from_dataset``, without needing to create a dummy dataset first.

    Of course, you can control position and width explicitly:

    .. code-block:: yaml

       - kind: model
         type: NormalisedLorentzian
         properties:
           parameters:
             position: 1.5
             width: 0.5
         from_dataset: dummy
         result: normalised_lorentzian

    This would create a normalised Lorentzian with its maximum situated at a
    value of 1.5 at the *x* axis, and with a width of 0.5.

    .. versionadded:: 0.3

    """

    def __init__(self):
        super().__init__()
        self.description = "Normalised Lorentzian, PDF of a Cauchy distribution"
        self.parameters["position"] = 0
        self.parameters["width"] = 1

    def _perform_task(self):
        x = np.asarray(self.variables)  # pylint: disable=invalid-name
        position = self.parameters["position"]
        width = self.parameters["width"]
        amplitude = 1 / (np.pi * not_zero(width))
        lorentzian = \
            amplitude * (width**2 / ((x - position)**2 + not_zero(width**2)))
        self._dataset.data.data = lorentzian


class Sine(Model):
    # noinspection PyUnresolvedReferences
    r"""
    Sine wave.

    Creates a sine function with given amplitude, frequency, and phase.

    The underlying mathematical equation may be written as follows:

    .. math::

        f(x) = a \sin(fx + \phi)

    with :math:`a` being the amplitude, :math:`f` the frequency,
    and :math:`\phi` the phase of the sine.


    Attributes
    ----------
    parameters : :class:`dict`
        All parameters necessary for this step.

        amplitude : :class:`float`
            Amplitude of the sine.

            Note that the real amplitude (max-min) is twice the value given
            here. Nevertheless, calling this factor "amplitude" seems to be
            common.

            Default: 1

        frequency : :class:`float`
            Frequency of the sine (in radians).

            Default: 1

        phase : :class:`float`
            Phase (*i.e.*, shift) of the sine (in radians).

            Setting the phase to :math:`\pi/2` would result in a cosine.

            Default: 0


    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. The examples focus each on a single
    aspect.

    Suppose you would want to create a sine with standard values (amplitude=1,
    frequency=1, shift=0). Starting from scratch, you need to create
    a dummy dataset (using, *e.g.*, :class:`aspecd.model.Zeros`) of given
    length and axes range. Based on that you can create your sine:

    .. code-block:: yaml

       - kind: model
         type: Zeros
         properties:
           parameters:
             shape: 1001
             range: [-5, 5]
         result: dummy

       - kind: model
         type: Sine
         from_dataset: dummy
         result: sine

    Of course, if you start with an existing dataset (*e.g.*, loaded from
    some real data), you could use the label to this dataset directly in
    ``from_dataset``, without needing to create a dummy dataset first.

    Of course, you can control all three parameters (amplitude, frequency,
    and shift) explicitly:

    .. code-block:: yaml

       - kind: model
         type: Sine
         properties:
           parameters:
             amplitude: 42
             frequency: 4.2
             shift: 1.57
         from_dataset: dummy
         result: sine

    This would create a sine with an amplitude of 42 (the actual amplitude,
    defined as max-min, would be twice this value), a frequency of 4.2 and a
    shift of about pi/2.

    .. versionadded:: 0.3

    """

    def __init__(self):
        super().__init__()
        self.description = 'Sine function'
        self.parameters['amplitude'] = 1
        self.parameters['frequency'] = 1
        self.parameters['phase'] = 0

    def _perform_task(self):
        x = np.asarray(self.variables)  # pylint: disable=invalid-name
        amplitude = self.parameters["amplitude"]
        frequency = self.parameters["frequency"]
        phase = self.parameters["phase"]
        sine = amplitude * np.sin(frequency * x + phase)
        self._dataset.data.data = sine


class Exponential(Model):
    # noinspection PyUnresolvedReferences
    r"""
    Exponential function.

    Creates an exponential with given prefactor and rate.

    The underlying mathematical equation may be written as follows:

    .. math::

        f(x) = a \exp(bx)

    with :math:`a` being the prefactor and :math:`b` the rate of the
    exponential.


    Attributes
    ----------
    parameters : :class:`dict`
        All parameters necessary for this step.

        prefactor : :class:`float`
            Intercept of the exponential.

            Default: 1

        rate : :class:`float`
            Rate of the exponential.

            Default: 1


    .. note::
        In case of modelling exponential decays, the rate constant will
        become negative. This rate constant (decay rate) is the inverse of the
        lifetime. Lifetime and half-life are related by a factor of ln(2).


    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. The examples focus each on a single
    aspect.

    Suppose you would want to create an exponential with standard values
    (prefactor=1, rate=1). Starting from scratch, you need to create
    a dummy dataset (using, *e.g.*, :class:`aspecd.model.Zeros`) of given
    length and axes range. Based on that you can create your exponential:

    .. code-block:: yaml

       - kind: model
         type: Zeros
         properties:
           parameters:
             shape: 1001
             range: [-5, 5]
         result: dummy

       - kind: model
         type: Exponential
         from_dataset: dummy
         result: exponential

    Of course, if you start with an existing dataset (*e.g.*, loaded from
    some real data), you could use the label to this dataset directly in
    ``from_dataset``, without needing to create a dummy dataset first.

    Of course, you can control all parameters (prefactor, rate) explicitly:

    .. code-block:: yaml

       - kind: model
         type: Exponential
         properties:
           parameters:
             prefactor: 42
             rate: 4.2
         from_dataset: dummy
         result: exponential

    This would create an exponential with a prefactor of 42 (*i.e.* the
    intercept) and a rate of 4.2.

    .. versionadded:: 0.3

    """

    def __init__(self):
        super().__init__()
        self.description = 'Exponential function'
        self.parameters["prefactor"] = 1
        self.parameters["rate"] = 1

    def _perform_task(self):
        x = np.asarray(self.variables)  # pylint: disable=invalid-name
        prefactor = self.parameters["prefactor"]
        rate = self.parameters["rate"]
        exponential = prefactor * np.exp(rate * x)
        self._dataset.data.data = exponential
