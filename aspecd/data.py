"""Data."""


import numpy as np
from aspecd import axis


class Error(Exception):
    """Base class for exceptions in this module."""

    pass


class AxesCountError(Error):
    """Exception raised for wrong number of axes

    Attributes
    ----------
    message : `str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class AxesValuesInconsistentWithDataError(Error):
    """Exception raised for axes values inconsistent with data

    Attributes
    ----------
    message : `str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class Data:
    """
    Unit containing both, numeric data and corresponding axes.

    The data class ensures consistency in terms of dimensions between
    numerical data and axes.

    Parameters
    ----------
    data : `numpy.array`
        Numerical data
    axes : `list`
        List of objects of type :class:`aspecd.axis.Axis`

        The number of axes needs to be consistent with the dimensions of data.

        Axes will be set automatically when setting data. Hence,
        the easiest is to first set data and only afterwards set axis values.
    calculated : `bool`
        Indicator for the origin of the numerical data (calculation or
        experiment).

    Attributes
    ----------
    calculated : `bool`
        Indicate whether numeric data are calculated rather than
        experimentally recorded

    Raises
    ------
    AxesCountError
        Raised if number of axes is inconsistent with data dimensions
    AxesValuesInconsistentWithDataError
        Raised if axes values are inconsistent with data

    """

    def __init__(self, data=np.zeros(0), axes=None, calculated=False):
        self._data = data
        self._axes = []
        if axes is None:
            self._create_axes()
        else:
            self.axes = axes
        self.calculated = calculated

    @property
    def data(self):
        """Get (numeric) data.

        Returns
        -------
        data : `numpy.array`
            Numerical data

        """
        return self._data

    @data.setter
    def data(self, data):
        self._data = data
        self._create_axes()

    @property
    def axes(self):
        """Get axes.

        Returns
        -------
        axes : `list`
            List of objects of type :class:`aspecd.axis.Axis`

        """
        return self._axes

    @axes.setter
    def axes(self, axes):
        self._axes = axes
        self._check_axes()

    def _create_axes(self):
        self._axes = []
        missing_axes = self.data.ndim + 1
        for ax in range(missing_axes):
            self._axes.append(axis.Axis())

    def _check_axes(self):
        if len(self._axes) > self.data.ndim + 1:
            raise AxesCountError
        data_shape = self.data.shape
        for index in range(self.data.ndim):
            if len(self.axes[index].values) != data_shape[index]:
                raise AxesValuesInconsistentWithDataError
