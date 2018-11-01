========
Concepts
========

ASpecD is built around a small set of general concepts, each aiming at complete reproducibility---and whereever possible replicability---of data acquisition, processing, and analysis. Despite its origin in spectroscopy, ASpecD is generally agnostic with respect to the data processed.


Dataset
=======

*Unit of data and metadata, prerequisite for a semantic understanding within the routines.*

Every measurement (or calculation) produces (raw) data that are useless without additional information, such as experimental parameters. This additional information is termed "metadata" within the ASpecD framework. A dataset is the unit of (numerical) data and metadata. Another integral aspect is the `history`_ containing all relevant information regarding each single processing step performed on the data of the dataset.


Metadata
========

*Information on data(sets), can exist separately from datasets.*

Metadata are stored outside the ASpecD framework in simple yet structured text files that focus on human readability and writability, while retaining machine readability.

The simplest incarnation of metadata is all necessary information obtained during data acquisition that usually gets stored in a file and read upon data import. A `dataset`_ contains these metadata together with the numerical data.


History
=======

*Complete list of all processing steps, allows for reproducibility.*

Reproducibility is an essential aspect of good scientific practice. In the context of data processing and analysis, this means that each processing step performed on data (of a dataset) should be stored in an reproducible way and preferably in a consistent format.

To be of actual use, an entry of the history needs to contain all information necessary to reproduce the processing step in its original form. This includes as a minimum the name of the processing routine used, the complete list of necessary parameters for that routine, and a unique version information of the routine. Additional useful aspects contain information about the operating system used, the name of the operator, and the date the processing step has been performed.


Representations
===============

*Graphical or tabular representations of data extracted from datasets.*

Representing data---both graphically as well as in tabular form---is an integral aspect of analysis as well as publication of results in science.

Already graphically representing one-dimensional data leaves nearly endless possibilities, considering line styles, colours, and alike. Multi-dimensional data add an additional level of complexity. Here, the slice or view chosen is often crucial.

The key idea behind representations is to store the necessary metadata to (automatically) reproduce a representation starting from the data. Representations can generally be both, graphically or tabular in character.


Annotations
===========

*Annotations of data, e.g. characteristics, that cannot be automated.*

Annotations of data are eventually something that cannot be automated. Nevertheless, they can be quite important for the analysis and hence for providing new scientific insight.

The simplest form of an annotation is a comment applying to an entire dataset, such as comments stored in the metadata written during data acquisition.


Reports
=======

*Overview of information available on a dataset that can be created automatically.*

The ASpecD framework aims at storing as much information as possible in a simple format, often within a dataset. However, such system can only show its strengths if this information is easily accessible and can be presented in an appealing way.

The idea behind reports is to create well formatted representations of crucial aspects of a dataset or, eventually, several datasets. This is based on templates provided or adjusted by the user.
