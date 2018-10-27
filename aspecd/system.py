"""System."""

import os
import sys

import aspecd.utils


class SystemInfo(aspecd.utils.ToDictMixin):

    def __init__(self):
        self.python = dict()
        self.modules = dict()
        self.platform = sys.platform
        self.user = dict()
        # Set some properties of dicts
        self.python["version"] = sys.version
        self.modules["aspecd"] = aspecd.utils.get_version()
        self.user["login"] = os.getlogin()
