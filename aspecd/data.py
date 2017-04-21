"""Data."""


import numpy as np
from aspecd import axis


class Data:

    def __init__(self, data=np.zeros(0), axes=[], calculated=False):
        self._data = data
        self._axes = axes
        self._set_axes()
        self.calculated = calculated

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        self._data = data
        self._set_axes()

    @property
    def axes(self):
        return self._axes

    def _set_axes(self):
        missing_axes = self.data.ndim+1 - len(self._axes)
        for ax in range(missing_axes):
            self._axes.append(axis.Axis)
