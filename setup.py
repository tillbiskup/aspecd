import os
import setuptools


def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as f:
        content = f.read()
    return content


setuptools.setup(
    name="aspecd",
    version=read('VERSION').strip(),
    description="Framework for handling spectroscopic data.",
    long_description=read('README.rst'),
    long_description_content_type="text/x-rst",
    author="Till Biskup",
    author_email="till@till-biskup.de",
    url="https://www.aspecd.de",
    project_urls={
        "Documentation": "https://docs.aspecd.de/",
        "Source": "https://github.com/tillbiskup/aspecd",
    },
    packages=setuptools.find_packages(exclude=('tests', 'docs')),
    keywords=[
        "spectroscopy",
        "data processing and analysis",
        "reproducible science",
        "good scientific practice",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
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
        'jinja2',
        'matplotlib',
        'numpy',
        'oyaml',
    ],
    extras_require={
        'dev': ['prospector'],
        'docs': ['sphinx', 'sphinx-rtd-theme'],
    },
    python_requires='>=3.5',
)
