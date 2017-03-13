from distutils.core import setup

import os

with open(os.path.join(mypackage_root_dir, 'VERSION')) as version_file:
    version = version_file.read().strip()

with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()


setup(
    name='ASpecD',
    version=version,
    description='Framework for handling spectroscopic data.',
    long_description=readme,
    author='Till Biskup',
    author_email='till@till-biskup.de',
    url='https://aspecd.de/',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)
