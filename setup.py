import os
import setuptools

with open(os.path.join(os.path.dirname(__file__), 'VERSION')) as version_file:
    version = version_file.read().strip()

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as f:
    readme = f.read()

with open(os.path.join(os.path.dirname(__file__), 'LICENSE')) as f:
    license_ = f.read()


setuptools.setup(
    name='ASpecD',
    version=version,
    description='Framework for handling spectroscopic data.',
    long_description=readme,
    long_description_content_type='text/x-rst',
    author='Till Biskup',
    author_email='till@till-biskup.de',
    url='https://www.aspecd.de/',
    project_urls={
        'Documentation': 'https://docs.aspecd.de/',
        'Source': 'https://github.com/tillbiskup/aspecd-python',
    },
    license=license_,
    packages=setuptools.find_packages(exclude=('tests', 'docs')),
    keywords=[
        'spectroscopy',
        'data processing and analysis',
        'reproducible science',
        'good scientific practice',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Development Status :: 3 - Alpha",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Libraries :: Application Frameworks"
    ],
    install_requires=[
        'numpy'
    ],
    python_requires='>=3',
)
