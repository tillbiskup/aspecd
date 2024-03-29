"""General purpose functions and classes used in other modules.

To avoid circular dependencies, this module does *not* depend on any other
modules of the ASpecD package, but it can be imported into every other module.

"""

import collections
import contextlib
import datetime
import hashlib
import importlib
import inspect
import logging
import os
import pkgutil
import re

import numpy as np
import oyaml as yaml
import pkg_resources

import aspecd.exceptions


def full_class_name(object_):
    """
    Return full class name of an object including packages and modules.

    Parameters
    ----------
    object_ : `object`
        object the class name should be inferred for

    Returns
    -------
    class_name : :class:`str`
        string with full class name of object

    """
    class_name = "".join(
        [object_.__class__.__module__, ".", object_.__class__.__name__]
    )
    return class_name


def object_from_class_name(full_class_name_string):
    """
    Create object from full class name.

    To obtain the full class name of an object, you might want to use the
    function :func:`full_class_name`

    Parameters
    ----------
    full_class_name_string : :class:`str`
        string with full class name of an object that shall be instantiated

    Returns
    -------
    object_ : `object`
        object instantiated from the class given in `full_class_name_string`

    """
    class_name_parts = full_class_name_string.split(".")
    class_name = class_name_parts[-1]
    module_name = ".".join(class_name_parts[0:-1])
    module = importlib.import_module(module_name)
    object_ = getattr(module, class_name)()
    return object_


class ToDictMixin:
    """Mixin class for returning all public attributes as dict.

    Sometimes there is the need to either exclude public attributes (in case
    of infinite loops created by trying to apply ``to_dict`` in this case)
    or to add (public) attributes, particularly those used by getters and
    setters that are otherwise not included.

    To do so, there are two non_public attributes of this class each class
    inheriting from it will be able to set as well:

    * :attr:`_exclude_from_to_dict`
    * :attr:`_include_in_to_dict`

    The names should be rather telling. For details, see below.

    Attributes
    ----------
    __odict__ : :class:`collections.OrderedDict`
        Dictionary of attributes preserving the order of their definition

    _exclude_from_to_dict : :class:`list`
        Names of (public) attributes to exclude from dictionary

        Usually, the reason to exclude public attributes from being added to
        the dictionary is to avoid infinite loops, as sometimes an object
        may contain a reference to another object that in turn references
        back.

    _include_in_to_dict : :class:`list`
        Names of (public) attributes to include into dictionary

        Usual reasons for actively including (public) attributes into the
        dictionary are those attributes accessed by getters and setters and
        hence not automatically included in the list otherwise.


    .. versionchanged: 0.6.3
        Added superclass call to preserve mro in dependent subclasses

    """

    def __init__(self):
        super().__init__()
        if "__odict__" not in self.__dict__:
            self.__odict__ = collections.OrderedDict()
        self._exclude_from_to_dict = []
        self._include_in_to_dict = []

    def __setattr__(self, attribute, value):
        """
        Add attributes to :attr:`__odict__` to preserve order of definition.

        Parameters
        ----------
        attribute : :class:`str`
            Name of attribute
        value : :class:`str`
            Value of attribute

        """
        if "__odict__" not in self.__dict__:
            super().__setattr__("__odict__", collections.OrderedDict())
        self.__odict__[attribute] = value
        super().__setattr__(attribute, value)

    def to_dict(self, remove_empty=False):
        """
        Create dictionary containing public attributes of an object.

        Parameters
        ----------
        remove_empty : :class:`bool`
            Whether to remove keys with empty values

            Default: False

        Returns
        -------
        public_attributes : :class:`collections.OrderedDict`
            Ordered dictionary containing the public attributes of the object

            The order of attribute definition is preserved


        .. versionchanged:: 0.6
            New parameter `remove_empty`

        .. versionchanged:: 0.9
            Settings for properties to exclude and include are not traversed

        .. versionchanged:: 0.9.1
            Dictionaries get copied before traversing, as otherwise,
            the special variables ``__dict__`` and  ``__0dict__`` are
            modified, what may result in strange behaviour.

        .. versionchanged:: 0.9.2
            Dictionaries do not get copied by default, but there is a
            private method that can be overridden in derived classes to
            copy the dictionary.

        """
        if hasattr(self, "__odict__"):
            result = self._traverse_dict(
                self._clean_dict(
                    self._return_copy(self.__odict__), traversing=False
                )
            )
        else:
            result = self._traverse_dict(
                self._clean_dict(
                    self._return_copy(self.__dict__), traversing=False
                )
            )
        if remove_empty:
            result = remove_empty_values_from_dict(result)
        return result

    @staticmethod
    def _return_copy(dictionary):
        """
        Return (a copy of) the dictionary.

        Some derived classes need to operate on a (deep)copy of the
        dictionary, while others don't. Generally, (deep)copying slows down
        things, hence should be avoided wherever possible.

        Parameters
        ----------
        dictionary : :class:`dict`
            The dictionary to be copied

        Returns
        -------
        dictionary : class:`dict`
            The (copy of the) dictionary

        """
        return dictionary

    def _clean_dict(self, dictionary, traversing=True):
        to_remove = []
        for key in dictionary:
            if (
                (
                    str(key).startswith("_")
                    and key not in self._include_in_to_dict
                )
                or str(key) in self._exclude_from_to_dict
                and not traversing
            ):
                to_remove.append(key)
        for key in to_remove:
            dictionary.pop(key, None)
        if not traversing:
            for key in self._include_in_to_dict:
                dictionary[key] = getattr(self, key)
        return dictionary

    def _traverse_dict(self, instance_dict):
        output = collections.OrderedDict()
        for key, value in instance_dict.items():
            output[key] = self._traverse(key, value)
        return output

    def _traverse(self, key, value):
        if isinstance(value, ToDictMixin):
            result = value.to_dict()
        elif isinstance(value, (dict, collections.OrderedDict)):
            result = self._traverse_dict(self._clean_dict(value))
        elif hasattr(value, "__odict__"):
            result = self._traverse_dict(self._clean_dict(value.__odict__))
        elif hasattr(value, "__dict__"):
            result = self._traverse_dict(self._clean_dict(value.__dict__))
        elif isinstance(value, list):
            result = [self._traverse(key, i) for i in value]
        elif isinstance(
            value, (datetime.datetime, datetime.date, datetime.time)
        ):
            result = str(value)
        else:
            result = value
        return result


def get_aspecd_version():
    """
    Get version of ASpecD package.

    The function directly reads the contents of the file VERSION in the root
    directory of the package installation, not relying on introspection.

    Returns
    -------
    version : :class:`str`
        Version number as string

    """
    version_file_path = os.path.join(
        os.path.dirname(__file__), "..", "VERSION"
    )
    if os.path.exists(version_file_path):
        with open(version_file_path, encoding="utf8") as version_file:
            version = version_file.read().strip()
    else:
        version = package_version("aspecd")
    return version


def package_version(name=""):
    """
    Get version of arbitrary package.

    The function relies on introspection using :mod:`pkg_resources`.

    Parameters
    ----------
    name : :class:`str`
        Name of package the version should be obtained for

    Returns
    -------
    version : :class:`str`
        Version number as string

    """
    version = None
    if name:
        try:
            version = pkg_resources.get_distribution(name).version
        except pkg_resources.DistributionNotFound:
            pass
    return version


def package_name(obj=None):
    """
    Get name of package an object resides in.

    Parameters
    ----------
    obj : :class:`object`
        Object the package it resides in should be returned.

        If no object is given, the name of the package this function is
        defined in ("aspecd") will be returned.

    Returns
    -------
    package_name : :class:`str`
        Name of the package

    """
    if not obj:
        obj = package_name
    module = inspect.getmodule(obj)
    return module.__package__


def config_dir():
    """
    Get config directory for per-user configurations.

    Configuration on a per-user level should be stored within a directory
    (only) readable by the currently logged-in user.

    Returns
    -------
    config_dir : :class:`str`
        Path to config directory, usually in the user's directory

    """
    config_dir_ = os.environ.get(
        "XDG_CONFIG_HOME", os.path.join(os.path.expanduser("~"), ".config")
    )
    return config_dir_


class Yaml:
    """
    Handle reading from and writing to YAML files.

    YAML file contents are read into an ordered dict, making use of the
    oyaml package. This preserves the order of the entries of any dict.

    .. note::
        The PyYAML package cannot handle NumPy arrays by default. Hence,
        there are two methods in this class for serialising and
        deserialising NumPy arrays:

        * :meth:`aspecd.utils.Yaml.serialise_numpy_arrays` and
        * :meth:`aspecd.utils.Yaml.deserialise_numpy_arrays`.

        Have a look at their documentation for details of the implementation
        and how to use them. In particular, larger NumPy arrays are saved to
        files using the NumPy binary format.

    Attributes
    ----------
    dict : :class:`collections.OrderedDict`
        Contents read from/written to a YAML file

    numpy_array_size_threshold : :class:`int`
        Maximum size of NumPy array that is converted into a list using
        :meth:`aspecd.utils.Yaml.serialise_numpy_arrays`.

        Larger NumPy arrays are saved to a file in NumPy format using
        :func:`numpy.save`.

        Default: 100 -- *i.e.*, arrays with >100 elements are stored in files.

    numpy_array_to_list : class:`bool`
        Whether to convert (small) NumPy arrays to a list or to a dict

        Default: False

    binary_files : :class:`list`
        List of names of the binary files containing large arrays

    binary_directory : :class:`str`
        Directory the binary files should be stored in

        Default: ''

    loader : :class:`yaml.loader`
        Type of loader used for loading the YAML file

        The type of loader used is crucial for the safety of your
        application. See the documentation of the PyYAML package for details.

        Default: :class:`yaml.SafeLoader`

    dumper : :class:`yaml.Dumper`
        Type of dumper used for loading the YAML file

        The type of dumper used is should be compatible to the type of loader.

        Default: :class:`yaml.SafeDumper`

    Raises
    ------
    aspecd.utils.MissingFilenameError
        Raised if no filename is given to read from/write to


    .. versionchanged:: 0.4
        Added :attr:`numpy_array_to_list`

    .. versionchanged:: 0.5
        Added :attr:`dumper` and set dumper to SafeDumper

    """

    def __init__(self):
        self.binary_files = []
        self.binary_directory = ""
        self.dict = collections.OrderedDict()
        self.numpy_array_size_threshold = 100
        self.numpy_array_to_list = False
        self.loader = yaml.SafeLoader
        self.dumper = yaml.SafeDumper
        self.loader.add_implicit_resolver(
            "tag:yaml.org,2002:float",
            re.compile(
                """^(?:
             [-+]?(?:[0-9][0-9_]*)\\.[0-9_]*(?:[eE][-+]?[0-9]+)?
            |[-+]?(?:[0-9][0-9_]*)(?:[eE][-+]?[0-9]+)
            |\\.[0-9_]+(?:[eE][-+][0-9]+)?
            |[-+]?[0-9][0-9_]*(?::[0-5]?[0-9])+\\.[0-9_]*
            |[-+]?\\.(?:inf|Inf|INF)
            |\\.(?:nan|NaN|NAN))$""",
                re.X,
            ),
            list("-+0123456789."),
        )
        self.dumper.add_representer(np.float64, self._numpy_float_representer)
        self.dumper.add_representer(np.int64, self._numpy_int_representer)

    def read_from(self, filename=""):
        """
        Read from YAML file.

        Parameters
        ----------
        filename : :class:`str`
            Name of the YAML file to read from.

        Raises
        ------
        aspecd.processing.MissingFilenameError
            Raised if no filename is given to read from.

        """
        if not filename:
            raise aspecd.exceptions.MissingFilenameError
        with open(filename, "r", encoding="utf8") as file:
            self.dict = yaml.load(file, Loader=self.loader)

    def write_to(self, filename=""):
        """
        Write to YAML file.

        Parameters
        ----------
        filename : :class:`str`
            Name of the YAML file to write to.

        Raises
        ------
        aspecd.processing.MissingFilenameError
            Raised if no filename is given to write to.

        """
        if not filename:
            raise aspecd.exceptions.MissingFilenameError
        with open(filename, "w", encoding="utf8") as file:
            yaml.dump(self.dict, file, Dumper=self.dumper)

    def read_stream(self, stream=None):
        """
        Read from stream.

        Parameters
        ----------
        stream : :class:`bytes`
            binary stream to read from

        """
        self.dict = yaml.load(stream, Loader=self.loader)

    def write_stream(self):
        """
        Write to from stream.

        Returns
        -------
        stream : :class:`str`
            string representation of YAML file

        """
        return yaml.dump(self.dict, Dumper=self.dumper)

    def serialise_numpy_arrays(self):
        """
        Serialise numpy arrays in a simple form, using a dict.

        Background: The PyYAML package cannot easily handle NumPy arrays out
        of the box. However, datasets and alike should sometimes be
        serialised in form of YAML files. Hence the need for a simple
        method of serialising NumPy arrays. Furthermore, larger NumPy
        arrays should not be serialised in text form in YAML directly,
        but rather be stored in binary form, probably in a separate file.

        The reason for saving (larger) NumPy arrays in binary rather than
        text form is twofold: The size of a binary file is much smaller,
        and the original precision is retained. Those interested in the
        representation of floating-point values in computers should consult:

        * David Goldberg. What every computer scientist should know about
          floating-point arithmetic. *ACM Comput. Surv.* **23** (1991):5--48.
          DOI:`10.1145/103162.103163 <https://doi.org/10.1145/103162.103163>`_

        As binary format, the NumPy format (see :mod:`numpy.lib.format`)
        gets used.

        As filename, the SHA256 hash of the array will be used. Thus,
        the names are unique with respect to the content. In the event of
        having several identical arrays within one dict that gets
        serialised, this should not be a problem, as the hashes should be
        reasonably unique. *I.e.*, identical files should have identical
        content. Thus, having several identical arrays will lead to less
        files written, eventually saving space and overall file size.

        """
        self._traverse_serialise_numpy_arrays(dict_=self.dict)

    def _traverse_serialise_numpy_arrays(self, dict_=None):  # noqa: MC0001
        for key in dict_.keys():
            if isinstance(dict_[key], list):
                for element in dict_[key]:
                    if isinstance(element, (dict, collections.OrderedDict)):
                        self._traverse_serialise_numpy_arrays(dict_=element)
            elif isinstance(dict_[key], np.ndarray):
                if dict_[key].size > self.numpy_array_size_threshold:
                    self._create_binary_directory()
                    try:
                        filename = (
                            hashlib.sha256(dict_[key]).hexdigest() + ".npy"
                        )
                    except ValueError:
                        filename = (
                            hashlib.sha256(dict_[key].copy()).hexdigest()
                            + ".npy"
                        )
                    np.save(
                        os.path.join(self.binary_directory, filename),
                        dict_[key],
                        allow_pickle=False,
                    )
                    dict_[key] = {
                        "type": "numpy.ndarray",
                        "dtype": str(dict_[key].dtype),
                        "file": filename,
                    }
                    self.binary_files.append(filename)
                elif self.numpy_array_to_list:
                    dict_[key] = dict_[key].tolist()
                else:
                    dict_[key] = {
                        "type": "numpy.ndarray",
                        "dtype": str(dict_[key].dtype),
                        "array": dict_[key].tolist(),
                    }
            elif isinstance(dict_[key], (dict, collections.OrderedDict)):
                self._traverse_serialise_numpy_arrays(dict_=dict_[key])
            # make list of binary_files unique
            self.binary_files = list(set(self.binary_files))

    def serialize_numpy_arrays(self):
        """
        Serialise numpy arrays for our AE speaking friends.

        See :meth:`aspecd.utils.Yaml.serialise_numpy_arrays` for details.
        """
        self.serialise_numpy_arrays()

    def deserialise_numpy_arrays(self):
        """
        Deserialise specially crafted dicts into NumPy arrays.

        For reasons given in the documentation of
        :meth:`aspecd.utils.Yaml.serialise_numpy_arrays`, NumPy arrays are
        handled separately and converted into dicts with some special
        fields. This method deserialises them back into NumPy arrays,
        as they were originally.

        """
        self._traverse_deserialise_numpy_arrays(dict_=self.dict)

    def _traverse_deserialise_numpy_arrays(self, dict_=None):
        for key in dict_.keys():
            if isinstance(dict_[key], list):
                for element in dict_[key]:
                    if type(element) in [dict, collections.OrderedDict]:
                        self._traverse_deserialise_numpy_arrays(dict_=element)
            elif isinstance(dict_[key], (dict, collections.OrderedDict)):
                if (
                    "type" in dict_[key].keys()
                    and dict_[key]["type"] == "numpy.ndarray"
                ):
                    if "file" in dict_[key].keys():
                        self._create_binary_directory()
                        dict_[key] = np.load(
                            os.path.join(
                                self.binary_directory, dict_[key]["file"]
                            )
                        )
                    else:
                        dict_[key] = np.asarray(dict_[key]["array"])
                else:
                    self._traverse_deserialise_numpy_arrays(dict_=dict_[key])

    def deserialize_numpy_arrays(self):
        """
        Deserialise numpy arrays for our AE speaking friends.

        See :meth:`aspecd.utils.Yaml.deserialise_numpy_arrays` for details.
        """
        self.deserialise_numpy_arrays()

    def _create_binary_directory(self):
        if self.binary_directory and not os.path.exists(
            self.binary_directory
        ):
            os.mkdir(self.binary_directory)

    @staticmethod
    def _numpy_float_representer(dumper, data):
        return dumper.represent_float(float(data))

    @staticmethod
    def _numpy_int_representer(dumper, data):
        return dumper.represent_int(int(data))


def replace_value_in_dict(replacement=None, target=None):  # noqa: MC0001
    """
    Replace value for given key in a dictionary, traversing recursively.

    The key in ``replacement`` needs to correspond to the value in
    ``target_dict`` that should be replaced. Keys in the dict ``replacement``
    that have no corresponding value in ``target_dict`` are silently ignored.

    Parameters
    ----------
    replacement : :class:`dict`
        dict containing key corresponding to the value in ``target_dict``
        that should be replaced by the associated value
    target : :class:`dict`
        dict containing the key whose value should be replaced by the value
        of the key in ``replacement`` named identical to the value

    Returns
    -------
    target : :class:`dict`
        dict containing the key whose value has been replaced by the value
        of the corresponding key in ``replacement``

    """
    for key, value in target.items():
        if isinstance(value, np.ndarray):
            continue
        if isinstance(target[key], dict):
            target[key] = replace_value_in_dict(replacement, target[key])
        elif isinstance(target[key], list):
            if target[key]:
                for list_index, list_element in enumerate(target[key]):
                    if isinstance(list_element, dict):
                        target[key][list_index] = replace_value_in_dict(
                            replacement, list_element
                        )
                    elif (
                        list_element.__hash__ and list_element in replacement
                    ):
                        target[key][list_index] = replacement[list_element]
                    else:
                        target[key][list_index] = list_element
            elif key in replacement:
                target[key] = replacement[key]
        elif value in replacement:
            target[key] = replacement[value]
    return target


def copy_values_between_dicts(source=None, target=None):
    """
    Copy values between two dicts in case of identical keys.

    Each value in ``source`` is copied to ``target`` in case of matching
    keys in a recursive manner. Non-matching keys in ``source`` are
    silently ignored.

    Both, source and target are parallel recursively traversed in case of
    identical overall structure.

    Parameters
    ----------
    source : :class:`dict`
        Dictionary the values should be copied from in case of matching keys
    target : :class:`dict`
        Dictionary the values should be copied to in case of matching keys

    Returns
    -------
    target : :class:`dict`
        Dictionary the values have been copied to in case of matching keys

    """
    for key in target:
        if isinstance(target[key], dict):
            if key in source and isinstance(source[key], dict):
                target[key] = copy_values_between_dicts(
                    source[key], target[key]
                )
            else:
                target[key] = copy_values_between_dicts(source, target[key])
        elif key in source:
            target[key] = source[key]
    return target


def copy_keys_between_dicts(source=None, target=None):
    """
    Copy keys between two dicts.

    Each key in ``source`` is copied to ``target`` in a recursive manner.
    If the key in ``source`` is a dict and exists in ``target``, the two
    dicts will be joined, not loosing keys in ``target``.

    If, however, the key in ``source`` is *not* a dict, but the
    corresponding key in ``target`` is a dict, the corresponding value in
    ``target`` will be replaced with that from ``source``.

    Parameters
    ----------
    source : :class:`dict`
        Dictionary the keys should be copied from
    target : :class:`dict`
        Dictionary the keys should be copied to

    Returns
    -------
    target : :class:`dict`
        Dictionary the keys have been copied to

    """
    for key in source:
        if (
            key in target
            and isinstance(target[key], dict)
            and isinstance(source[key], dict)
        ):
            target[key] = copy_keys_between_dicts(source[key], target[key])
        else:
            target[key] = source[key]
    return target


def remove_empty_values_from_dict(dict_):
    """
    Remove empty values and their keys from dict recursively.

    Parameters
    ----------
    dict_ : :class:`dict`
        Dictionary the keys with empty values should be removed from

    Returns
    -------
    dict_ : :class:`dict`
        Dictionary the keys with empty values have been removed from


    .. versionadded:: 0.2.1

    """
    if isinstance(dict_, dict):
        dict_ = dict(
            (key, remove_empty_values_from_dict(value))
            for key, value in dict_.items()
            if value and remove_empty_values_from_dict(value)
        )
    return dict_


def convert_keys_to_variable_names(dict_):
    """
    Change keys in dict to comply with PEP8 for variable names.

    Keys are converted to all lower case and spaces replaced with underscores.

    Parameters
    ----------
    dict_ : :class:`dict`
        Dictionary the keys should be renamed in

    Returns
    -------
    new_dict : :class:`dict`
        Dictionary the keys have been renamed in


    .. versionadded:: 0.2.1

    """
    new_dict = {}
    for key, value in dict_.items():
        new_key = key.replace(" ", "_").lower()
        if isinstance(value, dict):
            new_dict[new_key] = convert_keys_to_variable_names(dict_[key])
        else:
            new_dict[new_key] = dict_[key]
    return new_dict


def all_equal(list_=None):
    """
    Check whether all elements of a list are equal.

    Parameters
    ----------
    list_ : :class:`list`
        List whose elements should be checked for being equal

    Returns
    -------
    result : :class:`bool`

    """
    return list_.count(list_[0]) == len(list_)


class Properties(ToDictMixin):
    """
    General properties class allowing to set properties from dict.

    Properties classes often need to set their properties from dicts,
    and additionally, they should be able to convert themselves into dicts
    for persistence.
    """

    def __init__(self):
        super().__init__()
        self._exclude = []

    def from_dict(self, dict_=None):
        """
        Set attributes from dictionary.

        Parameters
        ----------
        dict_ : :class:`dict`
            Dictionary containing information of a task.

        Raises
        ------
        aspecd.plotting.MissingDictError
            Raised if no dict is provided.

        """
        if not dict_:
            raise aspecd.exceptions.MissingDictError
        for key, value in dict_.items():
            if hasattr(self, key):
                if hasattr(getattr(self, key), "from_dict"):
                    getattr(self, key).from_dict(value)
                elif isinstance(getattr(self, key), list):
                    if isinstance(value, list):
                        for element in value:
                            getattr(self, key).append(element)
                    else:
                        getattr(self, key).append(value)
                else:
                    setattr(self, key, value)

    def get_properties(self):
        """
        Return (public) properties, i.e. attributes that are *not* methods.

        Returns
        -------
        properties : :class:`list`
            public properties

        """
        props = []
        for prop in list(self.__dict__["__odict__"].keys()):
            if not str(prop).startswith("_") and prop not in self._exclude:
                props.append(prop)
        return props


def basename(filename):
    """
    Return basename of given filename.

    Parameters
    ----------
    filename : :class:`str`
        Name of the file (may contain absolute path and extension) the
        basename should be returned for.

    Returns
    -------
    basename : :class:`str`
        Basename corresponding to the filename provided as input.

    """
    return os.path.splitext(os.path.split(filename)[-1])[0]


def path(filename):
    """
    Return path of given filename, with trailing separator.

    Parameters
    ----------
    filename : :class:`str`
        Name of the file (may contain absolute path and extension) the path
        should be returned for.


    Returns
    -------
    path : :class:`str`
        path corresponding to the filename provided as input.

    """
    return os.path.split(filename)[:-1][0] + os.sep


def not_zero(value):
    """
    Return a value that is not zero to prevent DivisionByZero errors.

    Dividing by zero results in NaN values and often hinders evaluating
    mathematical models. A solution adopted from the lmfit Python package
    (https://doi.org/10.5281/zenodo.598352) returns a value equivalent to
    the resolution of a numpy float.

    .. note::

        If you use this function excessively within a module, mostly within
        rather complicated mathematical equations, it might be a good idea
        to import this function explicitly, to shorten the code, such as:
        ``from aspecd.utils import not_zero``. As usual, readability is king.

    Parameters
    ----------
    value : :class:`float`
        Value that can become (too close to) zero to trigger NaN values

    Returns
    -------
    value : :class:`float`
        Value guaranteed not to be zero


    .. versionadded:: 0.3

    """
    return np.copysign(
        max(abs(value), np.finfo(np.float64).resolution), value
    )


def isiterable(variable):
    """
    Check whether the given variable is iterable.

    Lists, tuples, NumPy arrays, but strings as well are iterable. Integers,
    however, are not.

    Parameters
    ----------
    variable :
        variable to check for being iterable

    Returns
    -------
    answer : :class:`bool`
        Whether the given variable is iterable

    """
    try:
        iter(variable)
        answer = True
    except TypeError:
        answer = False
    return answer


def get_package_data(name="", directory=""):
    """
    Obtain contents from a non-code file ("package data").

    A note on obtaining data from the distributed package: Rather than
    manually playing around with paths relative to the package root
    directory, contents of non-code files need to be obtained in a way that
    works with different kinds of package installation.

    Note that in Python, only files within the package, *i.e.* within the
    directory where all the modules are located, can be accessed, not files
    that reside on the root directory of the package.

    .. note::

        In case you would want to get package data from a package different
        than aspecd, you can prefix the name of the file to retrieve with
        the package name, using the '@' as a separator.

        Suppose you would want to retrieve the file ``__main__.py`` file
        from the "pip" package (why should you?):

        .. code-block::

            get_package_data('pip@__main__.py', directory='')

        This would return the contents of this file.


    Parameters
    ----------
    name : :class:`str`
        Name of the file whose contents should be accessed.

        In case the file should be retrieved from a different package,
        the package name can be prefixed, using '@' as a separator.

    directory : :class:`str`
        Directory within the package where the files are located.

        Default: ''

    Returns
    -------
    contents : :class:`str`
        String containing the contents of the non-code file.


    .. versionadded:: 0.5

    """
    if not name:
        raise ValueError("No filename given.")
    package = __package__
    if "@" in name:
        package, name = name.split("@")
    contents = pkgutil.get_data(package, "/".join([directory, name])).decode()
    return contents


# noinspection PyShadowingNames
@contextlib.contextmanager
def change_working_dir(path=""):  # pylint: disable=redefined-outer-name
    """
    Context manager for temporarily changing the working directory.

    Sometimes it is necessary to temporarily change the working directory,
    but one would like to ensure that the directory is reverted even in case
    an exception is raised.

    Due to its nature as a context manager, this function can be used with a
    ``with`` statement. See below for an example.


    Parameters
    ----------
    path : :class:`str`
        Path the current working directory should be changed to.


    Examples
    --------
    To temporarily change the working directory:

    .. code-block::

        with change_working_dir(os.path.join('some', 'path')):
            # Do something that may raise an exception

    This can come in quite handy in case of tests.


    .. versionadded:: 0.6

    """
    oldpwd = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(oldpwd)


def get_logger(name=""):
    """
    Get logger object for a given module.

    Logging in libraries is slightly different from standard logging with
    respect to the handler attached to the logger. The general advice from
    the `Python Logging HOWTO <https://docs.python.org/3/howto/logging.html
    #configuring-logging-for-a-library>`_ is to explicitly add the
    :class:`logging.Nullhandler` as a handler.

    Additionally, if you want to add loggers for a library that inherits
    from/builds upon a framework, in this particular case a library/package
    built atop the ASpecD framework, you want to have loggers being children
    of the framework logger in order to have the framework catch the log
    messages your library/package creates.

    Why does this matter, particularly for the ASpecD framework? If you want
    to have your log messages in a package based on the ASpecD framework appear
    when using :doc:`recipe-driven data analysis </recipes>`, you need to
    have your package loggers to be in the hierarchy below the root logger
    of the ASpecD framework. For convenience and in order not to make any
    informed guesses on how the ASpecD framework root logger is named,
    simply use this function to create the loggers in the modules of your
    package.

    Parameters
    ----------
    name : :class:`str`
        Name of the module to get the logger for.

        Usually, this will be set to ``__name__``, as this returns the
        current module (including the package name and separated with a
        ``.`` if present).

    Returns
    -------
    logger : :class:`logging.Logger`
        Logger object for the module

        The logger will have a :class:`logging.NullHandler` handler
        attached, in line with the advice from the `Python Logging HOWTO
        <https://docs.python.org/3/howto/logging.html#configuring-logging-for
        -a-library>`_.


    Examples
    --------
    To add a logger to a module in your library/package based on the ASpecD
    framework, add something like this to the top of your module:

    .. code-block::

        import aspecd.utils


        logger = aspecd.utils.get_logger(__name__)

    The important aspect here is to use ``__name__`` as the name of the
    logger. The reason is simple: ``__name__`` gets automatically expanded
    to the name of the current module, with the name of all parent
    modules/the package prefixed, using dot notation. The resulting logger
    will be situated in the hierarchy below the ``aspecd`` package logger.
    Suppose you have added the above lines to the module
    ``mypackage.processing`` in the ``processing`` module of your package
    ``mypackage``. This will result in a logger ``aspecd.mypackage.processing``.


    .. versionadded:: 0.9

    """
    if not name:
        name = package_name()
    else:
        name = ".".join([package_name(), name])
    logger = logging.getLogger(name=name)
    logger.addHandler(logging.NullHandler())
    return logger
