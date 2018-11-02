"""Axis"""


import numpy as np


class Error(Exception):
    """Base class for exceptions in this module."""

    pass


class AxisValuesDimensionError(Error):
    """Exception raised for wrong dimension of values

    Attributes
    ----------
    message : `str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class AxisValuesTypeError(Error):
    """Exception raised for wrong type of values

    Attributes
    ----------
    message : `str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class Axis:
    """Axis for data in a dataset.

    An axis contains always both, numerical values as well as the metadata
    necessary to create axis labels and to make sense of the numerical
    information.

    Attributes
    ----------
    quantity : `string`
        quantity of the numerical data, usually used as first part of an
        automatically generated axis label
    unit : `string`
        unit of the numerical data, usually used as second part of an
        automatically generated axis label
    label : `string`
        manual label for the axis, particularly useful in cases where no
        quantity and unit are provided or should be overwritten.

    Raises
    ------
    AxisValuesTypeError
        Raised when trying to set axis values to another type than numpy array
    AxisValuesDimensionError
        Raised when trying to set axis values to an array with more than one
        dimension.

    """

    def __init__(self):
        self._values = np.zeros(0)
        self._equidistant = None
        self.quantity = ''
        self.unit = ''
        self.label = ''

    @property
    def values(self):
        """
        Get or set the numerical axis values.

        Values require to be a one-dimensional numpy array. Trying to set
        values to either a different type or a numpy array with more than one
        dimension will raise a corresponding error.

        """
        return self._values

    @values.setter
    def values(self, values):
        if not isinstance(values, type(self._values)):
            raise AxisValuesTypeError
        if values.ndim > 1:
            raise AxisValuesDimensionError
        self._values = values
        self._set_equidistant_property()

    @property
    def equidistant(self):
        """Return whether the axes values are equidistant.

        True if the axis values are equidistant, False otherwise. None in
        case of no axis values.

        The property is set automatically if axis values are set and
        therefore read-only.

        While simple plotting of data values against non-uniform axes with
        non-equidistant values is usually straightforward, many processing
        steps rely on equidistant axis values in their simplest possible
        implementation.

        """
        return self._equidistant

    def _set_equidistant_property(self):
        if not self.values.size:
            return
        differences = self.values[1:] - self.values[0:-1]
        self._equidistant = (differences == differences[0]).all()
