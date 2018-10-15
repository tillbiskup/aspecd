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
        self.message = message


class AxisValuesTypeError(Error):
    """Exception raised for wrong type of values

    Attributes
    ----------
    message : `str`
        explanation of the error
    """

    def __init__(self, message=''):
        self.message = message


class Axis:
    """
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
        self.quantity = ''
        self.unit = ''
        self.label = ''

    @property
    def values(self):
        """
        Get or set the numerical axis values.

        Values require to be a one-dimensional numpy array. Trying to set
        values to either a different type or a numpy array with more than one
        dimension will raise a corresponding errors.
        """
        return self._values

    @values.setter
    def values(self, values):
        if not isinstance(values, type(self._values)):
            raise AxisValuesTypeError
        if values.ndim > 1:
            raise AxisValuesDimensionError
        self._values = values
