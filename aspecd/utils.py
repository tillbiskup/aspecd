"""General purpose functions used in other modules."""

import importlib


def full_class_name(object_):
    """Return full class name of an object including packages and modules.

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
    class_name_parts = full_class_name_string.split(".")
    class_name = class_name_parts[-1]
    module_name = '.'.join(class_name_parts[0:-1])
    module = importlib.import_module(module_name)
    object_ = getattr(module, class_name)()
    return object_
