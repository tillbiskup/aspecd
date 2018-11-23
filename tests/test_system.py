"""Tests for system."""

import os
import platform
import sys
import unittest

from aspecd import system, utils


class TestSystemInfo(unittest.TestCase):
    def setUp(self):
        self.sysinfo = system.SystemInfo()

    def test_instantiate_class(self):
        pass

    def test_instantiate_class_with_package_name(self):
        system.SystemInfo(package="aspecd")

    def test_python_property_version_key(self):
        python_version = sys.version
        self.assertEqual(self.sysinfo.python["version"], python_version)

    def test_platform_property(self):
        platform_ = platform.platform
        self.assertEqual(self.sysinfo.platform, platform_)

    def test_user_property_login_key(self):
        login_name = os.getlogin()
        self.assertEqual(self.sysinfo.user["login"], login_name)

    def test_modules_property_contains_aspecd_key(self):
        self.assertTrue("aspecd" in self.sysinfo.packages.keys())

    def test_instantiate_class_with_package_name_adds_key_to_modules(self):
        sysinfo = system.SystemInfo(package="numpy")
        self.assertTrue("numpy" in sysinfo.packages.keys())

    def test_instantiate_class_with_package_name_adds_package_version(self):
        package_name = "numpy"
        sysinfo = system.SystemInfo(package=package_name)
        self.assertEqual(utils.package_version(package_name),
                         sysinfo.packages[package_name])

    def test_modules_property_aspecd_key_has_correct_version(self):
        version = utils.get_aspecd_version()
        self.assertEqual(self.sysinfo.packages["aspecd"], version)

    def test_to_dict(self):
        self.assertTrue(isinstance(self.sysinfo.to_dict(), dict))
