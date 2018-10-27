"""System.

One key aspect of reproducibility is to record sufficient details of the
system used to perform analysis. Therefore, each
:class:`aspecd.history.HistoryRecord` contains a field with system
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

import aspecd.utils


class SystemInfo(aspecd.utils.ToDictMixin):
    """
    General information on the system used.

    Attributes
    ----------
    python : `dict`
        Version of Python (and potentially further information)
    modules : `dict`
        Relevant modules and their version numbers
    platform : `string`
        Identifier of the platform
    user : `dict`
        Currently only the login name of the currently logged-in user
    """

    def __init__(self):
        self.python = dict()
        self.modules = dict()
        self.platform = platform.platform
        self.user = dict()
        # Set some properties of dicts
        self.python["version"] = sys.version
        self.modules["aspecd"] = aspecd.utils.get_version()
        self.user["login"] = getpass.getuser()
