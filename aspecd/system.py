"""Obtaining information on the system used for data processing and analysis.

One key aspect of reproducibility is to record sufficient details of the
system used to perform processing and analysis. Therefore, each
:class:`aspecd.dataset.HistoryRecord` contains a field with system
information that is an :obj:`aspecd.system.SystemInfo` object.

General information stored within the :class:`aspecd.system.SystemInfo`
class are the Python version, the platform, as well as the login name of the
user currently logged in. Therefore, this is a relevant aspect for personal
data protection, and each and every user of the system should be made
available of this fact.

"""

import getpass
import platform
import sys

import pkg_resources

import aspecd.utils


class SystemInfo(aspecd.utils.ToDictMixin):
    """
    General information on the system used.

    Attributes
    ----------
    python : :class:`dict`
        Version of Python (and potentially further information)
    packages : :class:`dict`
        Relevant modules and their version numbers
    platform : :class:`string`
        Identifier of the platform
    user : :class:`dict`
        Currently only the login name of the currently logged-in user

    Parameters
    ----------
    package : :class:`str`
        Name of package whose version shall be added to the :attr:`modules`
        dictionary

        Useful (and necessary) for packages derived from the ASpecD
        framework to store their version number in the SystemInfo class and
        hence in the history records. Prerequisite for reproducibility.

    """

    def __init__(self, package=''):
        super().__init__()
        self.python = dict()
        self.packages = dict()
        self.platform = platform.platform()
        self.user = dict()
        # Set some properties of dicts
        self._set_values(package)

    def _set_values(self, package):
        self.python["version"] = sys.version
        self.packages["aspecd"] = aspecd.utils.get_aspecd_version()
        self._add_requirements_to_packages(package="aspecd")
        if package and package != "aspecd":
            self.packages[package] = aspecd.utils.package_version(package)
            self._add_requirements_to_packages(package=package)
        self.user["login"] = getpass.getuser()

    def _add_requirements_to_packages(self, package="aspecd"):
        requirements = [requirement.name for requirement in
                        pkg_resources.get_distribution(package).requires()]
        for requirement in requirements:
            self.packages[requirement] = \
                pkg_resources.get_distribution(requirement).version

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
        for key, value in dict_.items():
            if hasattr(self, key):
                if isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        getattr(self, key)[sub_key] = sub_value
                else:
                    setattr(self, key, value)
