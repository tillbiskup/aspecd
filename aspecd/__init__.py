"""ASpecD framework

Tools for reproducible and traceable analysis of spectral data.

Available modules
-----------------
dataset
    Unit containing data and metadata
io
    Import and export data into and from datasets
metadata
    Organise metadata in a dataset
infofile
    Import and parse info files
processing
    Process data in datasets
analysis
    Analyse data in datasets
annotation
    Annotate datasets
plotting
    Plot data in datasets

Utilities
---------
system
    Information about the system used
utils
    Basic functionality used by several modules.

"""

from . import infofile
from . import dataset
from . import plotting
from . import utils
