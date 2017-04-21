"""Axis"""


import numpy as np


class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class AxisValuesDimensionError(Error):
    """Exception raised for wrong dimension of values

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message=''):
        self.message = message


class AxisValuesTypeError(Error):
    """Exception raised for wrong type of values

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message=''):
        self.message = message


class Axis:

    def __init__(self):
        self._values = np.zeros(0)
        self.quantity = ''
        self.unit = ''
        self.label = ''

    @property
    def values(self):
        return self._values

    @values.setter
    def values(self, values):
        if not isinstance(values, type(self._values)):
            raise AxisValuesTypeError
        if values.ndim > 1:
            raise AxisValuesDimensionError
        self._values = values
