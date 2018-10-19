"""Metadata."""


class PhysicalQuantity:
    """
    Class for storing all relevant informations about a physical quantity

    A physical quantity, Q, consists always of a value, {Q} and a
    corresponding unit, [Q], hence

        Q = {Q} [Q]

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
        self.unit = parts[1].strip()
