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
        if self.value == 0.0 and not self.unit:
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

        Keys in the dictionary are converted to lower case and spaces
        converted to underscores to fit the naming scheme of attributes.

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
                if isinstance(dict_[key], dict):
                    self._set_datetime_from_dict(key, dict_.pop(key))
                else:
                    self._set_datetime_from_string(key, dict_.pop(key))
        super().from_dict(dict_=dict_)

    def _set_datetime_from_dict(self, key='', dict_=None):
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
        datetime_string = " ".join([dict_["date"], dict_["time"]])
        self._set_datetime_from_string(key=key, string=datetime_string)

    def _set_datetime_from_string(self, key='', string=''):
        """
        Set start and end properties from string containing values.

        The string will usually be obtained from reading a metadata file.
        Date and time formats are restricted, following "%Y-%m-%d" for date
        and "%H:%M:%S" for time, separated by a single space.

        Note that datetime objects are immutable.

        Parameters
        ----------
        key : `str`
            Property of class to set
        string : `str`
            String containing date and time in format described above

        """
        fmt = "%Y-%m-%d %H:%M:%S"
        setattr(self, key, datetime.datetime.strptime(string, fmt))


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

        Keys in the dictionary are converted to lower case and spaces
        converted to underscores to fit the naming scheme of attributes.

        Parameters
        ----------
        dict_ : `dict`
            Dictionary with metadata.

            Each key of this dictionary corresponds to a class attribute and
            is in itself a dictionary with the correct set of attributes for
            the particular class.

        """
        for key in dict_:
            attr = key.replace(' ', '_').lower()
            if hasattr(self, attr):
                getattr(self, attr).from_dict(dict_[key])


class MetadataMapper:
    """
    Mapper for metadata.

    Allows to convert a dictionary containing metadata read, e.g., from a
    metadata file to a dictionary that corresponds to the internal
    structure of the metadata in a dataset stored in
    :class:`aspecd.metadata.DatasetMetadata`.

    If all you need is to convert the dictionary keys to proper variable
    names conforming to the naming scheme proposed by `PEP 8
    <https://pep8.org/>`_, you may simply use the method
    :meth:`keys_to_variable_names`.

    Tasks that can be currently performed to map a dictionary to the
    internal structure of the metadata representation in a dataset contain
    renaming of keys via :meth:`rename_key` and combining items via
    :meth:`combine_items`.

    Rather than performing the mappings by hand, calling these methods
    repeatedly, you may use a mapping table contained in the
    :attr:`mappings` attribute. If you pre-define such mapping tables,
    you can easily apply different mappings depending on the version of
    your original metadata structure. Once you assigned the appropriate
    mapping table to the :attr:`mappings` attribute, simply call
    :meth:`map`. If everything turns out well, this should map your
    metadata contained in :attr:`metadata` according to the mapping table
    contained in :meth:`mappings`. Finally, you may want to assing this
    converted data structure to your dataset's metadata attribute,
    using :meth:`DatasetMetadata.from_dict()`.

    Attributes
    ----------
    metadata : `dict`
        Dictionary containing the metadata that are converted in place
    mappings : `list`
        Tasks to perform to map dictionary

        Each task is a list containing three entries:

        (1) an optional key of a "sub-dictionary" to operate on
        (2) the action to carry out
        (3) a list containing the necessary parameters to carry out the action

        For examples, see the documentation of the :meth:`map` method.

    """

    def __init__(self):
        self.metadata = dict()
        self.mappings = []

    def rename_key(self, old_key='', new_key=''):
        """
        Rename key in dictionary.

        Note that this method does *not* preserve the order of keys in an
        ordered dictionary.

        Parameters
        ----------
        old_key : str
            Name of original key that shall be renamed
        new_key : str
            New name of key to be renamed

        """
        self._rename_key_in_dict(old_key, new_key, self.metadata)

    @staticmethod
    def _rename_key_in_dict(old_key='', new_key='', dict_=None):
        dict_[new_key] = dict_.pop(old_key)
        return dict_

    def combine_items(self, old_keys=None, new_key='', pattern=''):
        """
        Combine two items in a dictionary.

        Parameters
        ----------
        old_keys : list
            Keys that should be combined
        new_key : str
            Name of new key
        pattern : str
            Pattern to use to join the keys together.

            Defaults to the empty string.

        """
        self._combine_items_in_dict(old_keys, new_key, pattern, self.metadata)

    @staticmethod
    def _combine_items_in_dict(old_keys=None, new_key='', pattern='',
                               dict_=None):
        value_tmp = list()
        for key in old_keys:
            value_tmp.append(dict_.pop(key))
        dict_[new_key] = pattern.join(value_tmp)
        return dict_

    def keys_to_variable_names(self):
        """
        Convert keys in :attr:`metadata` to proper variable names.

        Variable names in Python should be all lower case, with words
        joined by underscores.

        Due to recursively traversing through the :attr:`metadata`
        dictionary, conversion is performed for (near) arbitrary depth.
        """
        self.metadata = self._traverse_keys_to_variable_names(self.metadata)

    def _traverse_keys_to_variable_names(self, dict_=None):
        for key, value in dict_.items():
            if isinstance(value, dict):
                dict_[key] = \
                    self._traverse_keys_to_variable_names(value)
            new_key = key.replace(' ', '_').lower()
            dict_[new_key] = dict_.pop(key)
        return dict_

    def copy_key(self, old_key='', new_key=''):
        """
        Copy key in dictionary to new key.

        This method is particularly useful in cases where keys need to be
        combined using :meth:`combine_keys`, but where one of the keys
        should be combined several times with another key.

        Parameters
        ----------
        old_key : str
            Name of original key that shall be copied
        new_key : str
            Name of new key to be added

        """
        self._copy_key_in_dict(old_key=old_key, new_key=new_key,
                               dict_=self.metadata)

    @staticmethod
    def _copy_key_in_dict(old_key='', new_key='', dict_=None):
        dict_[new_key] = dict_[old_key]

    def map(self):
        """
        Map according to mappings in :attr:`mappings`.

        Each mapping is defined as a list containing optionally a key for a
        sub-dictionary as first element, the method to be performed as
        second element, and the parameters for this method as third element.

        An example for a mapping may look like this::

            mapping = [['', 'rename_key', ['old', 'new']]]

        This would rename the key ``old`` in :attr:`metadata` to ``new``.

        To do the same for a key in a "sub-dictionary", you may provide a
        mapping similar to the following::

            mapping = [['test', 'rename_key', ['old', 'new']]]

        This would rename the key ``old`` in the dictionary ``test`` in
        :attr:`metadata` to ``new``.

        Similarly, you can join two items to a new item. In this case,
        a mapping may look like this::

            mapping = [['', 'combine_items', [['key1', 'key2'], 'new']]]

        This would join the values corresponding to the two keys ``key1`` and
        ``key2`` and assign them to the new key ``new``. If you would like
        to join the values with a particular string, this can be done as well::

            mapping = [['', 'combine_items', [['key1', 'key2'], 'new', ' ']]]

        Here, the two values will be joined using a space.

        Sometimes you want to combine keys, but need one of the two keys
        several times. Hence, you would like to *first* copy this key to
        another one. This can be done in the following way::

            mapping = [['', 'copy_key', ['old', 'new']]]

        """
        for mapping in self.mappings:
            if mapping[0]:
                method = getattr(self, ''.join(['_', mapping[1], '_in_dict']))
                method(*mapping[2], dict_=self.metadata[mapping[0]])
            else:
                method = getattr(self, mapping[1])
                method(*mapping[2])
