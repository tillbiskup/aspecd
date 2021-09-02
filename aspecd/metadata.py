"""Metadata: Information on numeric data stored in a structured way.

Metadata are one key concept of the ASpecD framework, and they come in
different flavours. Perhaps the easiest to grasp is metadata that accompany
measurements---and are often stored separately from the data in metadata
files. Other types of metadata are those of processing steps or
representations. This module is only concerned with the first kind of
metadata, information accompanying data and usually recorded at the same
time as the numeric data.

Each :class:`aspecd.dataset.Dataset` contains a
:attr:`aspecd.dataset.Dataset.metadata` attribute that is in turn an object
of class :class:`aspecd.metadata.DatasetMetadata`. This latter object is
composed of different metadata objects each inheriting from
:class:`aspecd.metadata.Metadata`. Upon import of a dataset, the importer
class needs to make sure that as many metadata as possible are read and
imported to the dataset as well.

Generally speaking, metadata can be thought of as key--value stores that
might be hierarchically structured and thus cascaded. Nevertheless, classes
have some advantages over using simple dictionaries, as there are certain
operations that are common to some or all types of metadata.


Metadata classes
================

The classes implemented in this module can be grouped into general metadata
classes, concrete metadata classes, and metadata classes for datasets. Each
will be described shortly below.


General metadata classes
------------------------

The most basic class is :class:`aspecd.metadata.PhysicalQuantity` storing
all relevant information about a physical quantity in an easily accessible
way, eventually allowing to test for commensurable quantities and
converting between units.

Next is :class:`aspecd.metadata.Metadata` as a generic class for all
metadata containers. All other classes storing metadata, particularly those
storing metadata accompanying measurements and therefore ending up in the
metadata of a :class:`aspecd.dataset.Dataset`, should inherit from this class.


Concrete metadata classes
-------------------------

Currently, three classes for actual metadata of experimental datasets and
one class for calculated datasets are contained in the ASpecD framework,
namely :class:`aspecd.metadata.Measurement` for storing
general information about a given measurement,
:class:`aspecd.metadata.Sample` for all information regarding the sample
investigated, and :class:`aspecd.metadata.TemperatureControl` for
information about the temperature control (including whether temperature has
been actively controlled at all during the measurement) for experimental
datasets and :class:`aspecd.metadata.Calculation` for storing details about
the calculation underlying the (numeric) data for calculated datasets.


Metadata classes for datasets
-----------------------------

The attribute `metadata` in the :class:`aspecd.dataset.ExperimentalDataset`
is of type :class:`aspecd.metadata.ExperimentalDatasetMetadata` and
contains the three metadata classes for experimental datasets named above.
Derived packages should extend this class accordingly.

Similarly, the attribute `metadata` in the
:class:`aspecd.dataset.CalculatedDataset` is of type
:class:`aspecd.metadata.CalculatedDatasetMetadata` and contains the respective
metadata class named above. Derived packages should extend this class
accordingly wherever necessary.


Converting metadata from and to dictionaries
============================================

All classes inheriting from :class:`aspecd.metadata.Metadata` provide a
method :meth:`from_dict` allowing to set the attributes of the objects. This
allows for easy use with metadata read from a file into a `dict`.

Similiarly, all classes inheriting from :class:`aspecd.metadata.Metadata` as
well as :class:`aspecd.metadata.PhysicalQuantity` provide a method
:meth:`to_dict` that returns a dictionary of all public attributes of the
respective object. This allows to write metadata to a file.


Mapping metadata read from external sources
===========================================

Generally, the representation and structure of metadata within the dataset
of the ASpecD framework and each application derived from it is separate
from the way the very same metadata are organised in files written mostly
during data acquisition. To map the structure obtained by reading a
metadata file to the internal representation within the dataset, as given
by the :class:`aspecd.metadata.ExperimentalDatasetMetadata` class,
there exists a generic mapper class :class:`aspecd.metadata.MetadataMapper`.
This way, you can separate the representations of metadata and support
mapping for different versions of metadata files.


.. note::

    As mappings can become quite complicated and specifying lists of
    mappings for the :class:`aspecd.metadata.MetadataMapper` by hand can
    become quite tedious, you can specify metadata mapping recipes in YAML
    files in a rather simple syntax. See the documentation of the
    :class:`aspecd.metadata.MetadataMapper` class and its
    :meth:`aspecd.metadata.MetadataMapper.create_mappings` method for details.

    This method and the underlying ideas are heavily based on concepts
    and code developed by J. Popp for use within the `trEPR Python package
    <https://docs.trepr.de/>`_.


Metadata in packages based on the ASpecD framework
==================================================

The dataset as unit of (numerical) data and metadata is a key concept of the
ASpecD framework and a necessary prerequisite for a semantic understanding
within the routines. Every measurement (or calculation) produces (raw) data
that are useless without additional information, such as experimental
parameters. This additional information is termed "metadata" within the
ASpecD framework.

Additionally to combining numerical data and metadata, a dataset provides a
common structure, unifying the different file formats used as source for
both, data and metadata. Hence, the actual data format does not matter,
greatly facilitating dealing with data from different sources (and even
different kinds of data).

Therefore, if you develop a new package based on the ASpecD framework,
one of the first and most important steps is to create a (hierarchical)
metadata structure for your datasets. This requires a thorough understanding
of the spectroscopic method you develop the package for and most probably
several years of practical experience in the lab. Good sources of
inspiration are the vendor file formats usually storing instrument
parameters and alike in some form. If you are lucky, you can actually access
this information. If not, you may need to store these metadata in an
additional external file that gets written manually during data recording.

Some basic metadata that are rarely contained within vendor file formats,
as they concern the actual sample measured, as well as metadata for
calculated datasets can be found in the
:class:`aspecd.metadata.ExperimentalDatasetMetadata` and
:class:`aspecd.metadata.CalculatedDatasetMetadata`.


Module documentation
====================

"""

import datetime
import os

import aspecd.exceptions
import aspecd.utils


class PhysicalQuantity(aspecd.utils.ToDictMixin):
    """
    Class for storing all relevant informations about a physical quantity.

    A physical quantity, Q, consists always of a value, {Q} and a
    corresponding unit, [Q], hence:

    Q = {Q} [Q] .

    See, e.g., the "IUPAC Green Book" for further details.

    To get a string representation of a physical quantity, i.e., its value
    and unit separated by a single space, simply use :meth:`str()`.

    To set value (and unit) from a string, either use :meth:`from_string` or
    supply the string as argument while instantiating the object. Make sure
    the value part of the string to be convertible to float. Otherwise,
    a :class:`ValueError` will be raised.

    Attributes
    ----------
    unit : :class:`str`
        symbol of the unit of the corresponding value

        SI units are preferred
    dimension : :class:`str`
        dimension of the corresponding value

        useful for (automatic) conversions
    name : :class:`str`
        name of the physical quantity in a given context

    Parameters
    ----------
    string : :class:`str`
        String containing value and unit, separated by whitespace

        Will be used to set value and unit correspondingly.

        If no second element separated by whitespace is present,
        only :attr:`value` will be set.
    value : `float`
        Numerical value
    unit : :class:`str`
        String containing the unit of the corresponding value.

        SI units are preferred, and their abbreviations should be used.

    Raises
    ------
    ValueError
        Raised if value is not a float

    """

    def __init__(self, string=None, value=None, unit=None):
        super().__init__()
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
        self._include_in_to_dict = ['value']

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
        commensurable : :class:`bool`
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
        string : :class:`str`
            String containing value and unit, separated by whitespace

            Will be used to set value and unit correspondingly.

            If no second element separated by whitespace is present,
            only :attr:`value` will be set.

            If an empty string is provided, value and unit are cleared.

        """
        if string and not string.lower() == "n/a":
            self._set_value_unit_from_string(string)
        else:
            self.value = 0.
            self.unit = ''

    def from_dict(self, dict_=None):
        """
        Set properties from dictionary.

        Only parameters in the dictionary that are valid properties of the
        class are set accordingly.

        Parameters
        ----------
        dict_ : :class:`dict`
            Dictionary containing properties to set

        """
        for key in dict_:
            if hasattr(self, key):
                setattr(self, key, dict_[key])


class Metadata(aspecd.utils.ToDictMixin):
    """
    General metadata class.

    Metadata can be set from dict upon initialisation.

    Metadata can be converted to dict via
    :meth:`aspecd.utils.ToDictMixin.to_dict()`.

    """

    def __init__(self, dict_=None):
        """
        Instantiate Metadata object.

        Parameters
        ----------
        dict_ : :class:`dict`
            Dictionary containing properties to set

        """
        super().__init__()
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
        dict_ : :class:`dict`
            Dictionary containing properties to set

        """
        for key in dict_:
            attribute_name = key.replace(' ', '_').lower()
            if hasattr(self, attribute_name):
                if isinstance(getattr(self, attribute_name), PhysicalQuantity):
                    if isinstance(dict_[key], dict):
                        getattr(self, attribute_name).from_dict(dict_[key])
                    else:
                        getattr(self, attribute_name).from_string(dict_[key])
                else:
                    setattr(self, attribute_name, dict_[key])


class TemperatureControl(Metadata):
    """
    Temperature control is very often found in spectroscopy.

    This class provides general means of storing relevant parameters for
    temperature control.

    Attributes
    ----------
    temperature : :class:`aspecd.metadata.PhysicalQuantity`
        value and unit of the temperature set
    controller : :class:`str`
        type and name of the temperature controller used

    """

    def __init__(self, dict_=None, temperature=''):
        """
        Instantiate TemperatureControl object.

        If both, temperature and dictionary containing a temperature key are
        given, the dictionary key will overwrite the temperature parameter.

        Parameters
        ----------
        dict_ : :class:`dict`
            Dictionary containing properties to set
        temperature : :class:`str`
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
        dict_ : :class:`dict`
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
    purpose: :class:`str`
        Purpose of measurement, often quite helpful to know
    operator : :class:`str`
        Name of the operator performing the measurement
        Beware of the implications for privacy protection
    labbook_entry : :class:`str`
        Identifier for lab book entry (usually either LOI or URL)

    Parameters
    ----------
    dict_ : :class:`dict`
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

        For the "start" and "end" items, there are two different conventions
        available how the dictionary can be structured. Either those fields
        are dictionaries themselves, with fields "date" and "time"
        accordingly, such as::

            {"start": {"date": "yyyy-mm-dd", "time": "HH:MM:SS"},
             "end": {"date": "yyyy-mm-dd", "time": "HH:MM:SS"}}

        Alternatively, those fields can be strings containing a
        representation of both, date and time::

            {"start": "yyyy-mm-dd HH:MM:SS", "end": "yyyy-mm-dd HH:MM:SS"}

        Use whichever is more appropriate for you.

        Parameters
        ----------
        dict_ : :class:`dict`
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
        key : :class:`str`
            Property of class to set
        dict_ : :class:`dict`
            Dictionary with fields "date" and "time"

        """
        if isinstance(dict_["date"], datetime.date):
            dict_["date"] = dict_["date"].isoformat()
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
        key : :class:`str`
            Property of class to set
        string : :class:`str`
            String containing date and time in format described above

        """
        if string:
            fmt = "%Y-%m-%d %H:%M:%S"
            setattr(self, key, datetime.datetime.strptime(string, fmt))


class Sample(Metadata):
    """
    Information on the sample measured.

    Attributes
    ----------
    name : :class:`str`
        Short name of the sample
    id : :class:`str` or `int`
        Unique identifier of the sample
    loi : :class:`str`
        Lab Object Identifier (LOI) for the sample

    Parameters
    ----------
    dict_ : :class:`dict`
        Dictionary containing fields corresponding to attributes of the class

    """

    def __init__(self, dict_=None):
        self.name = ''
        self.id = None  # pylint: disable=invalid-name
        self.loi = ''
        super().__init__(dict_=dict_)


class Calculation(Metadata):
    """
    Information on the calculation.

    Attributes
    ----------
    type : :class:`str`
        Type of the calculation -- usually the full class name
    parameters : :class:`dict`
        Parameters of the calculation

    Parameters
    ----------
    dict_ : :class:`dict`
        Dictionary containing fields corresponding to attributes of the class

    """

    def __init__(self, dict_=None):
        self.type = ''
        self.parameters = dict()
        super().__init__(dict_=dict_)


class DatasetMetadata(aspecd.utils.ToDictMixin):
    """
    Metadata for dataset.

    This class contains the minimal set of metadata for a dataset.

    Metadata of actual datasets should extend this class by adding
    properties that are themselves classes inheriting from
    :class:`aspecd.metadata.Metadata`.

    Metadata can be converted to dict via
    :meth:`aspecd.utils.ToDictMixin.to_dict()`, e.g., for generating
    reports using templates and template engines.

    """

    # pylint: disable=useless-super-delegation
    def __init__(self):
        super().__init__()

    def from_dict(self, dict_=None):
        """
        Set properties from dictionary, e.g., from metadata.

        Only parameters in the dictionary that are valid properties of the
        class are set accordingly.

        Keys in the dictionary are converted to lower case and spaces
        converted to underscores to fit the naming scheme of attributes.

        Parameters
        ----------
        dict_ : :class:`dict`
            Dictionary with metadata.

            Each key of this dictionary corresponds to a class attribute and
            is in itself a dictionary with the correct set of attributes for
            the particular class.

        """
        for key in dict_:
            attr = key.replace(' ', '_').lower()
            if hasattr(self, attr):
                getattr(self, attr).from_dict(dict_[key])


class ExperimentalDatasetMetadata(DatasetMetadata):
    """
    Metadata for an experimental dataset.

    This class contains the minimal set of metadata for an experimental
    dataset, i.e., :class:`aspecd.dataset.ExperimentalDataset`.

    Metadata of actual datasets should extend this class by adding
    properties that are themselves classes inheriting from
    :class:`aspecd.metadata.Metadata`.

    Metadata can be converted to dict via
    :meth:`aspecd.utils.ToDictMixin.to_dict()`, e.g., for generating
    reports using templates and template engines.

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
        super().__init__()
        self.measurement = Measurement()
        self.sample = Sample()
        self.temperature_control = TemperatureControl()


class CalculatedDatasetMetadata(DatasetMetadata):
    """
    Metadata for a dataset with calculated data.

    This class contains the minimal set of metadata for a dataset consisting
    of calculated data, i.e., :class:`aspecd.dataset.CalculatedDataset`.

    Metadata of actual datasets should extend this class by adding
    properties that are themselves classes inheriting from
    :class:`aspecd.metadata.Metadata`.

    Metadata can be converted to dict via
    :meth:`aspecd.utils.ToDictMixin.to_dict()`, e.g., for generating
    reports using templates and template engines.

    Attributes
    ----------
    calculation : :class:`aspecd.metadata.Calculation`
        Metadata of calculation underlying the numeric data

    """

    def __init__(self):
        super().__init__()
        self.calculation = aspecd.metadata.Calculation()


class MetadataMapper:
    """
    Mapper for metadata.

    Allows to convert a dictionary containing metadata read, e.g., from a
    metadata file to a dictionary that corresponds to the internal
    structure of the metadata in a dataset stored in
    :class:`aspecd.metadata.ExperimentalDatasetMetadata`.

    If all you need is to convert the dictionary keys to proper variable
    names conforming to the naming scheme proposed by `PEP 8
    <https://pep8.org/>`_, you may simply use the method
    :meth:`keys_to_variable_names`.

    Tasks that can be currently performed to map a dictionary to the
    internal structure of the metadata representation in a dataset contain
    renaming of keys via :meth:`rename_key` and combining items via
    :meth:`combine_items` as well as copying keys via :meth:`copy_key` and
    moving items via :meth:`move_item`.

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
    using :meth:`ExperimentalDatasetMetadata.from_dict()`.

    As it is often tedious to manually create the entries of the mapping
    table residing in :attr:`mappings`, you can use mapping recipes stored
    in YAML files together with the :meth:`create_mappings` method. For
    details of the structure of the mapping recipe YAML files, see the
    documentation of the :meth:`create_mappings` method. Note that you need
    to specify the filename for the mapping recipe used in
    :attr:`recipe_filename` as well as the version of the metadata file
    format in :attr:`version` to get this to work. The :meth:`create_mappings`
    method and the underlying ideas are heavily based on concepts and code
    developed by J. Popp for use within the `trEPR Python package
    <https://docs.trepr.de/>`_.

    Attributes
    ----------
    metadata : :class:`dict`
        Dictionary containing the metadata that are converted in place

    mappings : :class:`list`
        Tasks to perform to map dictionary

        Each task is a list containing three entries:

        (1) an optional key of a "sub-dictionary" to operate on
        (2) the action to carry out
        (3) a list containing the necessary parameters to carry out the action

        For examples, see the documentation of the :meth:`map` method.

    version : :class:`str`
        Version of the metadata to map

        Particularly important when you use :meth:`create_mappings` to
        create the mappings from mapping recipes stored in a YAML file.

    recipe_filename : :class:`str`
        Name of the YAML file containing the mapping recipes

        Needs to be specified when you use :meth:`create_mappings` to
        create the mappings from mapping recipes stored in a YAML file.

    """

    def __init__(self):
        self.metadata = dict()
        self.mappings = []
        self.version = ''
        self.recipe_filename = ''
        self._mapping_recipes = None
        self._mapping_recipe = None

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
        for key, value in dict_.copy().items():
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

    def move_item(self, key='', source_dict_name='', target_dict_name='',
                  create_target_dict=False):
        """
        Move item (i.e., key-value pair) between dictionaries.

        .. note::
            If the target dictionary does not exist, usually the method
            will *not* create it and raise an appropriate exception.
            However, if explicitly told to create the target dictionary,
            it will do so. This is to prevent accidental typos from
            messing up with the dictionary and resulting in hard to track bugs.

        Parameters
        ----------
        key : str
            Name of the key of the corresponding item to move
        source_dict_name : str
            Name of the dict the item should be moved from
        target_dict_name : str
            Name of the dict the item should be moved to
        create_target_dict : bool
            Whether to create target dictionary if it doesn't exist

        """
        self._move_item_in_dict(key=key,
                                source_dict_name=source_dict_name,
                                target_dict_name=target_dict_name,
                                create_target_dict=create_target_dict,
                                dict_=self.metadata)

    @staticmethod
    def _move_item_in_dict(key='', source_dict_name='',
                           target_dict_name='',
                           create_target_dict=False, dict_=None):
        if create_target_dict and target_dict_name not in dict_:
            dict_[target_dict_name] = {}
        dict_[target_dict_name][key] = dict_[source_dict_name].pop(key)

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
        :attr:`metadata` to ``new``. The same pattern optionally specifying
        a dictionary to operate on can be applied to all the other mappings
        detailed below.

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

        And finally, there are cases where you want to move an item from
        one dictionary to another. This can be done using the following
        mapping::

            mapping = [['', 'move_item', ['key', 'source', 'target']]]

        Here, "source" and "target" are the names of the respective
        dictionaries the item should be moved between. If the target
        dictionary does not exist, by default, the method will raise an
        exception. If, however, you decide to exactly know what you do,
        you can pass an additional parameter explicitly telling the method
        to create the target dictionary::

            mapping = [['', 'move_item', ['key', 'source', 'target', True]]]

        In this particular case, however, you are solely responsible for
        any typos when specifying the name of the target dictionary,
        as this will most probably mess up your dictionaries and result in
        hard to track bugs.

        """
        if self.recipe_filename:
            self.create_mappings()
        for mapping in self.mappings:
            if mapping[0]:
                method = getattr(self, ''.join(['_', mapping[1], '_in_dict']))
                method(*mapping[2], dict_=self.metadata[mapping[0]])
            else:
                method = getattr(self, mapping[1])
                method(*mapping[2])

    def create_mappings(self):
        """
        Create mappings from mapping recipe stored in YAML file.

        Mapping recipes are stored in an external file (currently a YAML
        file whose filename is stored in :attr:`recipe_filename`) in their
        own format described hereafter. From this file, the recipes are read
        and converted into mappings in the :attr:`mappings` attribute.

        Based on the version number of the format the metadata from an external
        source are stored in, the correct recipe is selected.

        Following is an example of a YAML file containing recipes. Each map can
        contain several types of mappings and the latter can contain several
        entries:

        .. code-block:: yaml

            ---

            format:
              type: metadata mapper
              version: 0.0.1

            map 1:
              metadata file versions:
                - 0.1.6
                - 0.1.5
              combine items:
                - old keys: ['Date start', 'Time start']
                  new key: start
                  pattern: ' '
                  in dict: GENERAL
              rename key:
                - old key: GENERAL
                  new key: measurement
                  in dict:

            map 2:
              metadata file versions:
                - 0.1.4
              copy key:
                - old key: Date
                  new key: Date end
                  in dict: GENERAL
              move item:
                - key: model
                  source dict: measurement
                  target dict: spectrometer
                - key: Runs
                  source dict: measurement
                  target dict: experiment
                  create target: True

        Unknown mappings are silently ignored. The difference between the
        two entries in ``move item`` is that in the latter case, the target
        dictionary will be created. Be careful with this option, as typos
        introduced in your mapping recipe will lead to hard-to-debug
        behaviour of your application. See :meth:`move_item` for details.

        Generally, the YAML file should be pretty self-explanatory. For
        details of the different mappings, see the documentation of the
        respective methods of the class, namely :meth:`combine_items`,
        :meth:`rename_key`, :meth:`copy_key`, and :meth:`move_item`.

        .. important::

            The sequence of operations can sometimes be crucial. They are
            called as follows: "copy key" -> "combine items" -> "rename key"
            -> "remove items"

        Note that you can name the mappings called here ``map 1`` and ``map 2``
        as you like. Use descriptive names wherever possible.

        A hint on the filenames for metadata recipe YAML files: Use
        descriptive names containing the format of the metadata files. For
        info files, something like ``infofile_metadata_mappings.yaml`` may
        be reasonable.

        This method and the underlying ideas are heavily based on concepts
        and code developed by J. Popp for use within the `trEPR Python package
        <https://docs.trepr.de/>`_.

        """
        if not self.recipe_filename:
            raise aspecd.exceptions.MissingFilenameError(
                message="You need to provide a recipe filename in "
                        "self.recipe_filename")
        self._load_mapping_recipe_from_file()
        self._choose_mapping_recipe()
        self._add_mappings_from_recipe()

    def _load_mapping_recipe_from_file(self):
        root_path = os.path.split(os.path.abspath(__file__))[0]
        yaml_file = aspecd.utils.Yaml()
        yaml_file.read_from(os.path.join(root_path, self.recipe_filename))
        self._mapping_recipes = yaml_file.dict

    def _choose_mapping_recipe(self):
        for key in self._mapping_recipes.keys():
            if key != 'format':
                if self.version in \
                        self._mapping_recipes[key]['metadata file versions']:
                    self._mapping_recipe = self._mapping_recipes[key]
        if not self._mapping_recipe:
            raise aspecd.exceptions.MissingRecipeError(
                message='No matching recipe found.')

    def _add_mappings_from_recipe(self):
        if 'copy key' in self._mapping_recipe.keys():
            for i in range(len(self._mapping_recipe['copy key'])):
                mapping = \
                    [self._mapping_recipe['copy key'][i]['in dict'],
                     'copy_key',
                     [self._mapping_recipe['copy key'][i]['old key'],
                      self._mapping_recipe['copy key'][i]['new key']
                      ]
                     ]
                self.mappings.append(mapping)
        if 'combine items' in self._mapping_recipe.keys():
            for i in range(len(self._mapping_recipe['combine items'])):
                mapping = \
                    [self._mapping_recipe['combine items'][i]['in dict'],
                     'combine_items',
                     [self._mapping_recipe['combine items'][i]['old keys'],
                      self._mapping_recipe['combine items'][i]['new key'],
                      self._mapping_recipe['combine items'][i]['pattern']]]
                self.mappings.append(mapping)
        if 'rename key' in self._mapping_recipe.keys():
            for i in range(len(self._mapping_recipe['rename key'])):
                mapping = \
                    [self._mapping_recipe['rename key'][i]['in dict'],
                     'rename_key',
                     [self._mapping_recipe['rename key'][i]['old key'],
                      self._mapping_recipe['rename key'][i]['new key']]]
                self.mappings.append(mapping)
        if 'move item' in self._mapping_recipe.keys():
            for i in range(len(self._mapping_recipe['move item'])):
                sub_mapping = [
                    self._mapping_recipe['move item'][i]['key'],
                    self._mapping_recipe['move item'][i]['source dict'],
                    self._mapping_recipe['move item'][i]['target dict'],
                ]
                if "create target" in self._mapping_recipe['move item'][i]:
                    sub_mapping.append(True)
                mapping = ['', 'move_item', sub_mapping]
                self.mappings.append(mapping)
