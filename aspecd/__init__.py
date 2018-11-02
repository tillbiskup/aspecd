"""ASpecD framework

Tools for reproducible and traceable analysis of spectral data.

Available modules
-----------------
dataset
    Unit containing data and metadata
importer
    Import data into datasets
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
