"""Metadata."""

import datetime


class PhysicalQuantity:
    """
    Class for storing all relevant informations about a physical quantity.

    A physical quantity, Q, consists always of a value, {Q} and a
    corresponding unit, [Q], hence:

    Q = {Q} [Q] .

    See, e.g., the "IUPAC Green Book" for further details.

    To get a string representation of a physical quantity, i.e., its value
    and unit separated by a single space, simply use :func:`str()`

    Attributes
    ----------
    unit : `str`
        symbol of the unit of the corresponding value

        SI units are preferred
    dimension : `str`
        dimension of the corresponding value

        useful for (automatic) conversions
    name : `str`
        name of the physical quantity in a given context

    Parameters
    ----------
    string : `str`
        String containing value and unit, separated by whitespace

        Will be used to set value and unit correspondingly.

        If no second element separated by whitespace is present,
        only :attr:`value` will be set.
    value : `float`
        Numerical value
    unit : `str`
        String containing the unit of the corresponding value.

        SI units are preferred, and their abbreviations should be used.

    Raises
    ------
    ValueError
        Raised if value is not a float
    """

    def __init__(self, string=None, value=None, unit=None):
        self._value = 0.
        self.unit = ''
        self.dimension = ''
        self.name = ''
        if string:
            self._set_value_unit_from_string(string)
        if value:
            self.value = value
        if unit:
            self.unit = unit

    def __str__(self):
        if not self.unit and self.value == 0.0:
            string = ''
        else:
            string = " ".join([str(self.value), self.unit])
        return string

    @property
    def value(self):
        """
        Get or set the value of a physical quantity.

        A value is always a float.

        Raises
        ------
        ValueError
            Raised if value is not a (scalar) float
        """
        return self._value

    @value.setter
    def value(self, value):
        if not isinstance(value, type(self._value)):
            raise TypeError
        self._value = value

    def _set_value_unit_from_string(self, string):
        parts = string.split()
        self.value = float(parts[0].strip())
        if len(parts) > 1:
            self.unit = parts[1].strip()

    def commensurable(self, physical_quantity):
        """
        Check whether two physical quantities are commensurable.

        There are two criteria for physical quantities to be commensurable.
        Either they have the same unit, or they have the same dimension. In
        the latter case, a unit conversion is generally possible.

        Parameters
        ----------
        physical_quantity : :obj:`aspecd.metadata.PhysicalQuantity`
            physical quantity to test commensurability with

        Returns
        -------
        commensurable : `boolean`
            True if both physical quantities have the same unit or
            dimension, False otherwise
        """
        commensurable = False
        if self.unit and hasattr(physical_quantity, 'unit') and \
                physical_quantity.unit and self.unit == physical_quantity.unit:
            commensurable = True
        if self.dimension and hasattr(physical_quantity, 'dimension') and \
                physical_quantity.dimension and self.dimension\
                == physical_quantity.dimension:
            commensurable = True
        return commensurable

    def from_string(self, string):
        """
        Set value and unit from string.

        Parameters
        ----------
        string : `str`
            String containing value and unit, separated by whitespace

            Will be used to set value and unit correspondingly.

            If no second element separated by whitespace is present,
            only :attr:`value` will be set.

            If an empty string is provided, value and unit are cleared.
        """
        if string:
            self._set_value_unit_from_string(string)
        else:
            self.value = 0.
            self.unit = ''


class TemperatureControl:
    """
    Temperature control is very often found in spectroscopy.

    This class provides general means of storing relevant parameters for
    temperature control.

    Attributes
    ----------
    temperature : :class:`aspecd.metadata.PhysicalQuantity`
        value and unit of the temperature set
    controller : `str`
        type and name of the temperature controller used
    """

    def __init__(self, dict_=None, temperature=''):
        """
        Instantiate TemperatureControl object.

        If both, temperature and dictionary containing a temperature key are
        given, the dictionary key will overwrite the temperature parameter.

        Parameters
        ----------
        dict_ : `dict`
            Dictionary containing properties to set
        temperature : `str`
            Value and unit of temperature
        """
        self.temperature = PhysicalQuantity(temperature)
        self.controller = ''
        if dict_:
            self.from_dict(dict_)

    @property
    def controlled(self):
        """
        Has temperature been actively controlled during measurement?

        Read-only property automatically set when setting a temperature value.
        """
        return self.temperature.value

    def from_dict(self, dict_):
        """
        Set properties from dictionary, e.g., from metadata.

        Only parameters in the dictionary that are valid properties of the
        class are set accordingly.

        If "controlled" is set to False in the dictionary, the temperature
        value and unit will be cleared.

        The value of the temperature key needs to be a string.

        Parameters
        ----------
        dict_ : `dict`
            Dictionary with keys corresponding to properties of the class.
        """
        for key in dict_:
            if hasattr(self, key):
                if key is "temperature":
                    self.temperature.from_string(dict_[key])
                elif key is "controlled":
                    pass
                else:
                    setattr(self, key, dict_[key])
        # Checking "controlled" needs to be done after assigning other keys
        if "controlled" in dict_ and not dict_["controlled"]:
            self.temperature.from_string('')


class Measurement:
    """
    General information available for each type of measurement.

    Attributes
    ----------
    start : `datetime`
        Date and time of start of measurement
    end : `datetime`
        Date and time of end of measurement
    purpose: `str`
        Purpose of measurement, often quite helpful to know
    operator : `str`
        Name of the operator performing the measurement
        Beware of the implications for privacy protection
    labbook : `str`
        Identifier for lab book entry (usually either LOI or URL)

    Parameters
    ----------
    dict_ : `dict`
        Dictionary containing fields corresponding to attributes of the class
    """

    def __init__(self, dict_=None):
        self.start = None
        self.end = None
        self.purpose = ''
        self.operator = ''
        self.labbook = ''
        if dict_:
            self.from_dict(dict_)

    def from_dict(self, dict_):
        """
        Set properties from dictionary, e.g., from metadata.

        Only parameters in the dictionary that are valid properties of the
        class are set accordingly.

        Parameters
        ----------
        dict_ : `dict`
            Dictionary with keys corresponding to properties of the class.
        """
        for key in dict_:
            if key in ("start", "end"):
                self._set_datetime_from_dict(key, dict_[key])
                continue
            if hasattr(self, key):
                setattr(self, key, dict_[key])

    def _set_datetime_from_dict(self, key, dict_):
        """
        Set start and end properties from dictionary containing values.

        The dictionary will usually be obtained from reading a metadata file.
        Date and time formats are restricted, following "%Y-%m-%d" for date
        and "%H:%M:%S" for time.

        Note that datetime objects are immutable.

        Parameters
        ----------
        key : `str`
            Property of class to set
        dict_ : `dict`
            Dictionary with fields "date" and "time"
        """
        fmt = "%Y-%m-%d %H:%M:%S"
        datetime_string = " ".join([dict_["date"], dict_["time"]])
        setattr(self, key, datetime.datetime.strptime(datetime_string, fmt))
