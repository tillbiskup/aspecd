from setuptools import setup, find_packages

import os

with open(os.path.join(os.path.dirname(__file__), 'VERSION')) as version_file:
    version = version_file.read().strip()

with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license_ = f.read()


setup(
    name='ASpecD',
    version=version,
    description='Framework for handling spectroscopic data.',
    long_description=readme,
    author='Till Biskup',
    author_email='till@till-biskup.de',
    url='https://aspecd.de/',
    license=license_,
    packages=find_packages(exclude=('tests', 'docs'))
)
