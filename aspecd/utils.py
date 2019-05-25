"""General purpose functions and classes used in other modules.

To avoid circular dependencies, this module does *not* depend on any other
modules of the ASpecD package, but it can be imported into every other module.

"""

import collections
import datetime
import importlib
import inspect
import os

import oyaml as yaml
import pkg_resources


class Error(Exception):
    """Base class for exceptions in this module."""

    pass


class MissingFilenameError(Error):
    """Exception raised when expecting a filename but none is provided

    Attributes
    ----------
    message : :class:`str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class MissingDictError(Error):
    """Exception raised when expecting a dict but none is provided

    Attributes
    ----------
    message : :class:`str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


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
    class_name = ''.join([object_.__class__.__module__, '.',
                          object_.__class__.__name__])
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
    module_name = '.'.join(class_name_parts[0:-1])
    module = importlib.import_module(module_name)
    object_ = getattr(module, class_name)()
    return object_


class ToDictMixin:
    """Mixin class for returning all public attributes as dict.

    Attributes
    ----------
    __odict__ : `collections.OrderedDict`
        Dictionary of attributes preserving the order of their definition

    """

    def __init__(self):
        if '__odict__' not in self.__dict__:
            self.__odict__ = collections.OrderedDict()

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
        if '__odict__' not in self.__dict__:
            super().__setattr__('__odict__', collections.OrderedDict())
        self.__odict__[attribute] = value
        super().__setattr__(attribute, value)

    def to_dict(self):
        """
        Create dictionary containing public attributes of an object.

        Returns
        -------
        public_attributes : `collections.OrderedDict`
            Ordered dictionary containing the public attributes of the object

            The order of attribute definition is preserved

        """
        if hasattr(self, '__odict__'):
            result = self._traverse_dict(self.__odict__)
        else:
            result = self._traverse_dict(self.__dict__)
        return result

    def _traverse_dict(self, instance_dict):
        output = collections.OrderedDict()
        for key, value in instance_dict.items():
            if str(key).startswith('_'):
                pass
            else:
                output[key] = self._traverse(key, value)
        return output

    def _traverse(self, key, value):
        if isinstance(value, ToDictMixin):
            result = value.to_dict()
        elif hasattr(value, '__odict__'):
            result = self._traverse_dict(value.__odict__)
        elif hasattr(value, '__dict__'):
            result = self._traverse_dict(value.__dict__)
        elif isinstance(value, list):
            result = [self._traverse(key, i) for i in value]
        elif isinstance(value, dict):
            result = self._traverse_dict(value)
        elif isinstance(value, (datetime.datetime, datetime.date,
                                datetime.time)):
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
    version_file_path = os.path.join(os.path.dirname(__file__),
                                     "..", 'VERSION')
    if os.path.exists(version_file_path):
        with open(version_file_path) as version_file:
            version = version_file.read().strip()
    else:
        version = package_version("aspecd")
    return version


def package_version(name=''):
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
    obj : `object`
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
        'XDG_CONFIG_HOME',
        os.path.join(os.path.expanduser('~'), '.config')
    )
    return config_dir_


class Yaml:
    """
    Handle reading from and writing to YAML files.

    YAML file contents are read into an ordered dict, making use of the
    oyaml package. This preserves the order of the entries of any dict.

    Attributes
    ----------
    dict : :class:`collections.OrderedDict`
        Contents read from/written to a YAML file

    Raises
    ------
    aspecd.utils.MissingFilenameError
        Raised if no filename is given to read from/write to

    """

    def __init__(self):
        self.dict = collections.OrderedDict()

    def read_from(self, filename=''):
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
            raise MissingFilenameError
        with open(filename, 'r') as file:
            self.dict = yaml.load(file)

    def write_to(self, filename=''):
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
            raise MissingFilenameError
        with open(filename, 'w') as file:
            yaml.dump(self.dict, file)


def replace_value_in_dict(replacement=None, target=None):
    """
    Replace value for given key in a dictionary, traversing recursively.

    The key in ``replacement`` needs to correspond to the value in
    ``target_dict`` that should be replaced. Keys inthe dict ``replacement``
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
        if isinstance(target[key], dict):
            target[key] = replace_value_in_dict(replacement, target[key])
        elif isinstance(target[key], list):
            for list_index, list_element in enumerate(target[key]):
                if isinstance(list_element, dict):
                    target[key][list_index] = \
                        replace_value_in_dict(replacement, list_element)
                elif list_element in replacement:
                    target[key][list_index] = replacement[list_element]
        elif value in replacement:
            target[key] = replacement[value]
    return target


def copy_values_between_dicts(source=None, target=None):
    """
    Copy values between two dicts in case of identical keys.

    Each value in ``source`` is copied to ``target`` in case of matching
    keys in a recursive manner. Non-matching keys in ``source`` are
    silently ignored.

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
        if key in target and isinstance(target[key], dict):
            target[key] = copy_keys_between_dicts(source[key], target[key])
        else:
            target[key] = source[key]
    return target


def all_equal(list_=None):
    """
    Check whether all elements of a list are equal.

    Parameters
    ----------
    list_ : :class:`list`
        List whose elements should be checked for being equal

    Returns
    -------
    result : :class:`boolean`

    """
    return list_.count(list_[0]) == len(list_)


class Properties(ToDictMixin):
    """
    General properties class allowing to set properties from dict.

    Properties classes often need to set their properties from dicts,
    and additionally, they should be able to convert themselves into dicts
    for persistence.
    """

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
            raise MissingDictError
        for key in dict_:
            if hasattr(self, key):
                if isinstance(getattr(self, key), list):
                    if isinstance(dict_[key], list):
                        for element in dict_[key]:
                            getattr(self, key).append(element)
                    else:
                        getattr(self, key).append(dict_[key])
                else:
                    setattr(self, key, dict_[key])

    def get_properties(self):
        """
        Return (public) properties, i.e. attributes that are *not* methods.

        Returns
        -------
        properties: :class:`list`
            public properties

        """
        props = []
        for prop in list(self.__dict__['__odict__'].keys()):
            if not str(prop).startswith('_'):
                props.append(prop)
        return props
