"""Metadata.

Metadata are one key concept of the ASpecD framework, and they come in
different flavours. Perhaps the easiest to grasp is metadata that accompany
measurements---and are often stored separately from the data in metadata
files. Other types of metadata are those of processing steps or
representations.

Generally speaking, metadata can be thought of as key--value stores that
might be hierarchically structured and thus cascaded. Nevertheless, classes
have some advantages over using simple dictionaries, as there are certain
operations that are common to some or all types of metadata.

The most basic class is :class:`aspecd.metadata.PhysicalQuantity` storing
all relevant information about a physical quantity in an easily accessible
way, eventually allowing to test for commensurable quantities and
converting between units.

Next is :class:`aspecd.metadata.Metadata` as a generic class for all
metadata containers. All other classes storing metadata, particularly those
storing metadata accompanying measurements and therefore ending up in the
metadata of a :class:`aspecd.dataset.Dataset`, should inherit from this class.

Currently, three classes for actual metadata of datasets are contained in the
ASpecD framework, namely :class:`aspecd.metadata.Measurement` for storing
general information about a given measurement,
:class:`aspecd.metadata.Sample` for all information regarding the sample
investigated, and :class:`aspecd.metadata.TemperatureControl` for
information about the temperature control (including whether temperature has
been actively controlled at all during the measurement).

The attribute `metadata` in the :class:`aspecd.dataset.Dataset` is of type
:class:`aspecd.metadata.DatasetMetadata` and contains the three metadata
classes named above. Derived packages should extend this class accordingly.

All classes inheriting from :class:`aspecd.metadata.Metadata` provide a
method :meth:`from_dict` allowing to set the attributes of the objects. This
allows for easy use with metadata read from a file into a `dict`.

Similiarly, all classes inheriting from :class:`aspecd.metadata.Metadata` as
well as :class:`aspecd.metadata.PhysicalQuantity` provide a method
:meth:`to_dict` that returns a dictionary of all public attributes of the
respective object. This allows to write metadata to a file.
"""

import datetime

import aspecd.utils


class PhysicalQuantity(aspecd.utils.ToDictMixin):
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
        """String representation of object."""
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
    def value(self, value=None):
        if not isinstance(value, type(self._value)):
            raise TypeError
        self._value = value

    def _set_value_unit_from_string(self, string):
        parts = string.split(maxsplit=1)
        self.value = float(parts[0].strip())
        if len(parts) > 1:
            self.unit = parts[1].strip()

    def commensurable(self, physical_quantity=None):
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

    def to_dict(self):
        """
        Create dictionary containing public attributes of an object.

        Returns
        -------
        public_attributes : `dict`
            Dictionary containing the public attributes of the object

        """
        output = super().to_dict()
        # Add "value" attribute only accessible via getter/setter
        output["value"] = self.value
        return output


class Metadata(aspecd.utils.ToDictMixin):
    """
    General metadata class.

    Metadata can be set from dict upon initialisation.

    """

    def __init__(self, dict_=None):
        """
        Instantiate Metadata object.

        Parameters
        ----------
        dict_ : `dict`
            Dictionary containing properties to set

        """
        if dict_:
            self.from_dict(dict_)

    def from_dict(self, dict_=None):
        """
        Set properties from dictionary, e.g., from metadata.

        Only parameters in the dictionary that are valid properties of the
        class are set accordingly.

        If a property is of class :class:`aspecd.metadata.PhysicalQuantity`,
        it is set accordingly.

        Parameters
        ----------
        dict_ : `dict`
            Dictionary containing properties to set

        """
        for key in dict_:
            attr = key.replace(' ', '_').lower()
            if hasattr(self, attr):
                if isinstance(getattr(self, attr),
                              type(PhysicalQuantity())):
                    getattr(self, attr).from_string(dict_[key])
                else:
                    setattr(self, attr, dict_[key])


class TemperatureControl(Metadata):
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
        super().__init__(dict_=dict_)

    @property
    def controlled(self):
        """
        Has temperature been actively controlled during measurement?

        Read-only property automatically set when setting a temperature value.

        """
        return self.temperature.value

    def from_dict(self, dict_=None):
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
        # Get value for key "controlled" if it exists, and delete it from dict_
        controlled_in_dict = "controlled" in dict_
        if controlled_in_dict:
            controlled_in_dict = True
            controlled = dict_["controlled"]
            del dict_["controlled"]
        else:
            controlled = False
        super(TemperatureControl, self).from_dict(dict_)
        # Checking "controlled" needs to be done after assigning other keys
        if controlled_in_dict and not controlled:
            self.temperature.from_string('')


class Measurement(Metadata):
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
    labbook_entry : `str`
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
        self.labbook_entry = ''
        super().__init__(dict_=dict_)

    def from_dict(self, dict_=None):
        """
        Set properties from dictionary, e.g., from metadata.

        Only parameters in the dictionary that are valid properties of the
        class are set accordingly.

        Parameters
        ----------
        dict_ : `dict`
            Dictionary with keys corresponding to properties of the class.

        """
        for key in ("start", "end"):
            if key in dict_:
                self._set_datetime_from_dict(key, dict_[key])
                del dict_[key]
        super().from_dict(dict_=dict_)

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


class Sample(Metadata):
    """
    Information on the sample measured.

    Attributes
    ----------
    name : `str`
        Short name of the sample
    id : `str` or `int`
        Unique identifier of the sample
    loi : `str`
        Lab Object Identifier (LOI) for the sample

    Parameters
    ----------
    dict_ : `dict`
        Dictionary containing fields corresponding to attributes of the class

    """

    def __init__(self, dict_=None):
        self.name = ''
        self.id = None  # pylint: disable=invalid-name
        self.loi = ''
        super().__init__(dict_=dict_)


class DatasetMetadata:
    """
    Metadata for dataset.

    This class contains the minimal set of metadata for a dataset.

    Metadata of actual datasets should extend this class by adding
    properties that are themselves classes inheriting from
    :class:`aspecd.metadata.Metadata`.

    Attributes
    ----------
    measurement : :class:`aspecd.metadata.Measurement`
        Metadata of measurement
    sample : :class:`aspecd.metadata.Sample`
        Metadata of sample
    temperature_control : :class:`aspecd.metadata.TemperatureControl`
        Metadata of temperature control

    """

    def __init__(self):
        self.measurement = Measurement()
        self.sample = Sample()
        self.temperature_control = TemperatureControl()

    def from_dict(self, dict_=None):
        """
        Set properties from dictionary, e.g., from metadata.

        Only parameters in the dictionary that are valid properties of the
        class are set accordingly.

        Parameters
        ----------
        dict_ : `dict`
            Dictionary with metadata.

            Each key of this dictionary corresponds to a class attribute and
            is in itself a dictionary with the correct set of attributes for
            the particular class.

        """
        for key in dict_:
            if hasattr(self, key.lower()):
                getattr(self, key.lower()).from_dict(dict_[key])
