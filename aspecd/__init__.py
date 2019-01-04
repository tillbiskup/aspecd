"""ASpecD framework

Tools for reproducible and traceable analysis of spectral data.

Available modules
-----------------
:mod:`aspecd.dataset`
    Unit containing data and metadata
:mod:`aspecd.metadata`
    Organise metadata in a dataset
:mod:`aspecd.io`
    Import and export data into and from datasets
:mod:`aspecd.infofile`
    Import and parse info files
:mod:`aspecd.processing`
    Process data in datasets
:mod:`aspecd.analysis`
    Analyse data in datasets
:mod:`aspecd.annotation`
    Annotate datasets
:mod:`aspecd.plotting`
    Plot data in datasets
:mod:`aspecd.report`
    General facilities for generating reports
:mod:`aspecd.tasks`
    Recipe-driven data analysis

Utilities
---------
:mod:`aspecd.system`
    Information about the system used
:mod:`aspecd.utils`
    Basic functionality used by several modules.

"""

from . import infofile  # noqa: F401
from . import dataset   # noqa: F401
from . import plotting  # noqa: F401
from . import utils     # noqa: F401
