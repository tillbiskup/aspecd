"""Metadata."""


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
        """
        if string:
            self._set_value_unit_from_string(string)


class TemperatureControl:

    def __init__(self, dict_=None, temperature=''):
        self.temperature = PhysicalQuantity(temperature)
        self.controller = ''
        if dict_:
            self.from_dict(dict_)

    @property
    def controlled(self):
        return self.temperature.value

    def from_dict(self, dict_):
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
            self.temperature.value = 0.
            self.temperature.unit = ''
