"""General purpose functions and classes used in other modules."""

import collections
import datetime
import importlib
import inspect
import os
import pkg_resources


def full_class_name(object_):
    """
    Return full class name of an object including packages and modules.

    Parameters
    ----------
    object_ : `object`
        object the class name should be inferred for

    Returns
    -------
    class_name : `str`
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
    full_class_name_string : `str`
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
        attribute : `str`
            Name of attribute
        value : `str`
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
    version : `str`
        Version number as string

    """
    with open(os.path.join(os.path.dirname(__file__), "..",
                           'VERSION')) as version_file:
        version = version_file.read().strip()
    return version


def package_version(name=''):
    """
    Get version of arbitrary package.

    The function relies on introspection using :mod:`pkg_resources`.

    Parameters
    ----------
    name : `str`
        Name of package the version should be obtained for

    Returns
    -------
    version : `str`
        Version number as string

    """
    version = None
    if name:
        version = pkg_resources.get_distribution(name).version
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
    package_name : `str`
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
    config_dir : `str`
        Path to config directory, usually in the user's directory

    """
    config_dir_ = os.environ.get(
        'XDG_CONFIG_HOME',
        os.path.join(os.path.expanduser('~'), '.config')
    )
    return config_dir_
