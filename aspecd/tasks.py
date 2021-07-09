"""
Constituents of a recipe-driven data analysis.

.. sidebar:: Contents

    .. contents::
        :local:
        :depth: 1


One main aspect of tasks is to provide the constituents of a
:ref:`recipe-driven data analysis <recipes>`, i.e.
:class:`aspecd.tasks.Recipe` and :class:`aspecd.tasks.Chef`. In its
simplest form, a recipe gets cooked by a chef, resulting in a series of
tasks being performed on a list of datasets.

The idea of recipes here is to provide all necessary information for data
processing and analysis in a simple, human-readable and human-writable form.
This allows users not familiar with programming to perform even complex
tasks. In addition, recipes can even be "executed" using the command line,
not needing to start a Python interpreter.

From a user's perspective, a recipe is usually stored in a `YAML
<https://yaml.org/>`_ file. This allows to easily create and modify recipes
without knowing too much about the underlying processes. For an accessible
overview of the YAML syntax, see the `introduction provided by ansible
<https://docs.ansible.com/ansible/reference_appendices/YAMLSyntax.html>`_ .


Recipe-driven data analysis by example
======================================

Recipes always consist of two major parts: A list of datasets to operate
on, and a list of tasks to be performed on the datasets. Of course, you can
specify for each task on which datasets it should be performed, and if
possible, whether it should be performed on each dataset separately or
combined. The latter is particularly interesting for representations (e.g.,
plots) consisting of multiple datasets, or analysis steps spanning multiple
datasets.


A first recipe
--------------

To give a first impression of how such a recipe may look like:

.. code-block:: yaml

    datasets:
      - loi:xxx
      - loi:yyy

    tasks:
      - kind: processing
        type: SingleProcessingStep
        properties:
          parameters:
            param1: bar
            param2: foo
          prop2: blub
      - kind: singleanalysis
        type: SingleAnalysisStep
        properties:
          parameters:
            param1: bar
            param2: foo
          prop2: blub
        apply_to:
          - loi:xxx
        result: new_dataset

Here, ``tasks`` is a list of dictionary-style entries. The key ``kind``
determines which kind of task should be performed. For each kind, a class
subclassing :class:`aspecd.tasks.Task` needs to exist. For details,
see below. The key ``type`` stores the name of the actual class, such as a
concrete processing step derived from
:class:`aspecd.processing.SingleProcessingStep`. The dictionary ``properties``
contains keys corresponding to the attributes of the respective class.
Depending on the type of task, additional keys can be used, such as
``apply_to`` to determine the datasets this task should be applied to,
or ``result`` providing a label for a dataset created newly by an analysis
task.


.. note::
    The use of ``loi:`` markers in the example above points to a situation
    in which every dataset can be accessed by a unique identifier. For
    details, see the `LabInform documentation <https://www.labinform.de/>`_.


Base directory for dataset import
---------------------------------

There are different ways to refer to datasets, but the most common (for now)
is to specify the (relative or absolute) path to the datasets within the
local file system.

At the same time, the "paths" listed in the ``datasets`` list are used as
internal references within the recipe. Therefore, short names are preferrable.

To make things a bit easier, there is a way to define the source directory
for datasets:

.. code-block:: yaml

    datasets_source_directory: /path/to/my/datasets/

    datasets:
        - dataset1
        - dataset2

    tasks:
      - kind: processing
        type: SingleProcessingStep


In this case, all dataset names will be treated relative to the source
directory. Note that if you provide the option
``datasets_source_directory``, this can be both, an absolute path, as shown
here for unixoid file systems, and a relative path, as shown in the second
example below.

.. code-block:: yaml

    datasets_source_directory: relative/path/to/my/datasets/

    datasets:
        - dataset1
        - dataset2

    tasks:
      - kind: processing
        type: SingleProcessingStep

Here, paths have been given for unixoid file systems, using ``/`` as a
separator. Adjust to your needs if necessary.


Output directory
----------------

Some tasks, namely plotting and report tasks, can save their results to
files. This will usually be the directory you cook the recipe from. However,
sometimes it is quite convenient to specify an output directory, either
relative or absolute.

To do so, simply add the ``output_directory`` key to the top level of your
recipe:

.. code-block:: yaml

    output_directory: /absolute/path/for/the/outputs

    datasets:
        - dataset

    tasks:
      - kind: singleplot
        type: SinglePlotter
        properties:
          filename:
            - fancyfigure.pdf

As said, this path can as well be a relative path with respect to the
directory you cook your recipes from:

.. code-block:: yaml

    output_directory: relative/path/for/the/outputs

    datasets:
        - dataset

    tasks:
      - kind: singleplot
        type: SinglePlotter
        properties:
          filename:
            - fancyfigure.pdf

Here, paths have been given for unixoid file systems, using ``/`` as a
separator. Adjust to your needs if necessary.


Tasks from other packages
-------------------------

Usually, you will use classes to perform the individual tasks that come
from your own package. There is a a simple way of doing that, not having to
prefix the kind property of every single task: define the default package
name like so:

.. code-block:: yaml

    default_package: my_package

    datasets:
      - loi:xxx
      - loi:yyy

    tasks:
      - kind: processing
        type: SingleProcessingStep


If you would like to use a class from a different package for only one task,
feel free to prefix the "kind" attribute of the respective task, as shown:

.. code-block:: yaml

    tasks:
      - kind: some_other_package.processing
        type: SingleProcessingStep


Of course, in order to work, this package termed here "some_other_package"
needs to follow the same basic rules and layout as the ASpecD framework and
packages derived from it. In particular, if you use the "default_package"
directive in your recipe, the given package needs to implement a child of
the :class:`aspecd.dataset.DatasetFactory` class.

To state the obvious: You can, of course, combine both strategies, defining
a default package and overriding this for a particular task:

.. code-block:: yaml

    default_package: my_package

    datasets:
      - loi:xxx
      - loi:yyy

    tasks:
      - kind: some_other_package.processing
        type: SingleProcessingStep


Setting own labels (and properties) for datasets
------------------------------------------------

Usually, you specify the path (or any other unique and supported identifier) to
your dataset(s) in the list of datasets at the beginning of a recipe, like this:

.. code-block:: yaml

    datasets:
      - /lengthly/path/to/dataset1
      - /lengthly/path/to/dataset2


In this case, you will have to refer to the datasets by their path (or
whatever other identifier you used). Usually, these identifiers are quite
lengthly, hence not necessarily convenient for use as labels within a
recipe. However, you can set your own ids for datasets:

.. code-block:: yaml

    datasets:
      - source: /lengthly/path/to/dataset1
        id: dataset1
      - source: /lengthly/path/to/dataset2
        id: dataset2


Make sure to set the ``source`` value to the identifier of your dataset. For
your id, you are free to choose, as long as it is a valid key for a
:class:`dict`. From now on, refer to the datasets by their respective ids
throughout the recipe.

.. note::

    If you use the ``source`` key but don't specify a ``id`` key as well,
    the source will be used as id, as before.


However, you can even drive the whole thing one step further: Suppose you
are bored from having always the dataset label (that is by default identical
to the source it is imported from) appearing in a figure legend, as it simply
does not fit to what you need. How about that:

.. code-block:: yaml

    datasets:
      - source: /lengthly/path/to/dataset1
        id: dataset1
        label: low concentration
      - source: /lengthly/path/to/dataset2
        id: dataset2
        label: high concentration


In this case, you assign the ``label`` field of your datasets upon loading
them. The idea behind: When specifying which dataset to load, you usually
know best about such things, and you don't want to need to deal with this
later on when plotting.

.. important::

    Generally, each property of a dataset can be set this way. However,
    be careful not to override properties that are not scalar and cannot
    easily be represented in YAML in the recipe, as you will most certainly
    break things otherwise. A good example of how to definitely break
    things would be to override the ``data`` property of a dataset.


Import datasets from other packages
-----------------------------------

Sounds strange in the first place, but appears to be more common than you
may imagine: Sometimes, you need to compare datasets recorded using
different methods that are in turn handled by different ASpecD-derived
packages.

So how to import a dataset using the importer of a different package than
the current one? The syntax for the recipe is much the same as the one
described above for setting other properties of a dataset:

.. code-block:: yaml

    datasets:
      - source: /lengthly/path/to/dataset1
      - source: /lengthly/path/to/dataset2
        package: other_package


In this example, the first dataset will be imported using the default
package set for the recipe, but the second dataset will be loaded using the
:class:`aspecd.dataset.DatasetFactory` and
:class:`aspecd.io.DatasetImporterFactory` classes from ``other_package``. Of
course, you need to make sure that ``other_package`` exists and contains
both, a dataset factory and dataset importer factory. Furthermore, these two
classes need to reside in the same modules as in the ASpecD framework,
*i.e.*, the dataset factory needs to reside in the "dataset" module and the
dataset importer factory in the "io" module.


Specify importer for datasets
-----------------------------

Sometimes it may be necessary to explicitly provide the importer class that
shall be used to import a dataset. In this case, you can explicitly say
which importer to use:

.. code-block:: yaml

    datasets:
      - source: /lengthly/path/to/dataset1
      - source: /lengthly/path/to/dataset2
        importer: TxtImporter

However, be careful to match data format and importer, as you are overriding
the automatic importer determination of the
:class:`aspecd.io.DatasetImporterFactory` this way. Furthermore, make sure
the respective importer class exists. Of course, this works as
well with providing an alternative package:

.. code-block:: yaml

    datasets:
      - source: /lengthly/path/to/dataset1
      - source: /lengthly/path/to/dataset2
        package: other_package
        importer: TxtImporter

In this particular example, the importer located in
``other_package.io.TxtImporter`` would be used to import your dataset. The
parameters will be directly passed to the importer without further checking,
and it is the sole responsibility of the importer class to make sense of the
parameters provided. Have a look at the documentation of the actual importer
class you intend to use for parameters you can set (if any). Note that many
parameters will not recognise additional parameters.


Specify importer parameters for datasets
----------------------------------------

Furthermore, sometimes you may want to provide parameters for an importer,
*e.g.* in case of importing text files with headers, and you can do this as
well:

.. code-block:: yaml

    datasets:
      - source: /lengthly/path/to/dataset1
      - source: /lengthly/path/to/dataset2
        importer: TxtImporter
        importer_parameters:
          skiprows: 3

You can even provide ``importer_parameters`` without explicitly specifying
an importer to use, although this may lead to hard to detect behaviour,
as you rely on the automatism of choosing the importer class implemented in
the :class:`aspecd.io.DatasetImporterFactory` in this case.


Referring to other datasets and results
---------------------------------------

Some tasks yield results you usually would want to use later on in the
recipe. Prime examples are analysis steps and plots. While analysis steps
have a property ``result`` that can refer to either a dataset or something
else, depending on the actual type of analysis step, plots have a ``label``
that can be used to refer to them.

While analysis steps always yield results, processing steps usually operate
on a dataset that gets modified in turn. However, sometimes it is desired to
return the modified dataset as a *new dataset*, independent of the original
one. In this case, specify a ``result`` here, too. For details, see the
:class:`aspecd.tasks.ProcessingTask` documentation below.


Variable replacement
--------------------

Additionally to the labels described above, variables will be parsed and
replaced. Currently, the following types of variables are understood:

.. code-block:: yaml

    key1: {{ basename(id) }}
    key2: {{ path(id) }}
    key3: {{ id(id) }}

Here, ``id`` is the id used internally for referring to a dataset,
``{{ basename(id) }}`` will be replaced with the file basename of the
respective dataset source, ``{{ path(id) }}`` will be replaced by the path
of the respective dataset source, and  ``{{ id(id) }}`` will be replaced by
the id itself.

Note: The spaces within the double curly brackets are only for better
readability, they can be omitted, although this is not recommended.

Why is this interesting? Suppose you would like to create a rather generic
recipe always performing the same tasks, but for different datasets. A
rather minimal example is given below:

.. code-block:: yaml

    datasets:
      - source: /path/to/my_dataset.txt
        id: first_measurement

    tasks:
      - kind: processing
        type: SubtractBaseline
        properties:
          parameters:
            kind: polynomial
            order: 0
      - kind: singleplot
        type: SinglePlotter
        properties:
          filename:
            - {{ basename(first_measurement) }}.pdf

Here, you can see that all you would need to do is to replace the ``source``
with the actual path to your dataset. This will automatically perform the
tasks of the recipe on the given dataset, storing the plot to a
file named ``my_dataset.pdf``.


Executing recipes: serving the cooked results
=============================================

As stated above, a recipe gets cooked by a chef, resulting in a series of
tasks being performed on a list of datasets. However, as an (end) user you
usually don't care about chefs and recipes besides the human-readable and
writable representation of a recipe in YAML format. Therefore, there is a
fairly simple way to get a recipe executed, or, in terms of the metaphor of
recipe and cook, to get the meal served:

.. code-block:: bash

    serve <my-recipe>.yaml

No need of running a Python terminal, no need of instantiating any class.
Simply executing a command from a terminal, that's all that is to it. In
this particular example, ``<my-recipe>`` is a placeholder for your recipe
file name.

Of course, you can do the same from within Python::

    serve(recipe_filename='<my-recipe>.yaml')

And if you insist, of course there is an object-oriented way to do it::

    chef_de_service = ChefDeService()
    chef_de_service.serve(recipe_filename='<my-recipe>.yaml')

The good news with all this: It should work for every package derived from
the ASpecD framework, as long as you specify the ``default_package``
directive within the recipe. And of course, calling the recipe from the
command-line will only help you if it creates some kind of output.


History of a recipe
===================

The :class:`aspecd.tasks.Chef` class takes care of automatically creating a
history of the recipe cooked, with a full list of parameters for each task.
This history is a dict that follows the same structure as the original
recipe. Therefore, you can save this history to a YAML file and use it as a
recipe again, perhaps after some modifications.

If you use the :class:`aspecd.tasks.ChefDeService` class, you need not care
about actually writing the history to a YAML file. Therefore, using this
class or even the command-line call to ``serve`` as described above,
is highly recommended. In this case, you will have a full history of all
your tasks contained in a human-readable YAML file, together with some
additional information on the system and package versions used to cook the
recipe, as well as the time for start and end of cooking.

To make it short: The history of the recipe allows you to perform a fully
reproducible data analysis even of multiple datasets and arbitrarily
complex tasks without having to care about the details. You get it all for
free. That's what the ASpecD framework is all about. Care about the results
of your data analysis and what this means in terms of answering the
scientific questions that originally triggered obtaining and analysing the
data. Reproducibility is been taken care of for you.


Kinds of tasks
==============

.. sidebar:: Kind and type

    The "kind" of a task usually refers to the module the class belongs to,
    the "type" is the actual class name.


Tasks can be grouped similarly to the way classes of the ASpecD framework
are grouped into different modules. Hence, there are different *kinds* of
tasks. Each task is internally represented by an :obj:`aspecd.tasks.Task`
object, more precisely an object instantiated from a subclass of
:class:`aspecd.tasks.Task`. This polymorphism of task classes makes it
possible to easily extend the scope of recipe-driven data analysis.
Therefore, to allow ASpecD to know how to handle your task (*i.e.*,
what task object to create), you need to specify the *kind* of your task
within the recipe, besides the *type* that is the class name of the actual
class performing the respective task.

Currently, the following subclasses are implemented:

  * :class:`aspecd.tasks.ProcessingTask`

     * :class:`aspecd.tasks.SingleprocessingTask`
       (alias of :class:`aspecd.tasks.ProcessingTask`)
     * :class:`aspecd.tasks.MultiprocessingTask`

  * :class:`aspecd.tasks.AnalysisTask`

     * :class:`aspecd.tasks.SingleanalysisTask`
     * :class:`aspecd.tasks.MultianalysisTask`

  * :class:`aspecd.tasks.AnnotationTask`
  * :class:`aspecd.tasks.PlotTask`

     * :class:`aspecd.tasks.SingleplotTask`
     * :class:`aspecd.tasks.MultiplotTask`
     * :class:`aspecd.tasks.CompositeplotTask`

  * :class:`aspecd.tasks.ReportTask`
  * :class:`aspecd.tasks.ModelTask`
  * :class:`aspecd.tasks.ExportTask`

As you can see from the above list, there are (currently) two special cases
of kinds of tasks: analysis and plot tasks. Usually, you will set the
``kind`` of a task in a recipe to the module the class eventually performing
the task resides in. As both, analyses and plots can either span one or
several datasets, here we have to discriminate. Therefore, it is *essential*
that you take care to set the ``kind`` value in your recipe for these kinds
of tasks to ``singleanalysis`` or ``multianalysis``, respectively. the same
is true for plots. To make this a bit easier to follow, see the example below.

.. code-block:: yaml

    tasks:
      - kind: processing
        type: SingleProcessingStep

      - kind: singleanalysis
        type: AnalysisStep

      - kind: multiplot
        type: MultiPlotter1D


.. important::
    As long as there is no automatic syntax checking of recipes before they
    get executed, you are entirely responsible on your own to provide
    correct syntax. From own experience, there are a few problems frequently
    arising: Don't use **analysis**, but either **singleanalysis** or
    **multianalysis** as kind in an analysis step. The same applies to
    plots. Don't use **plotting**, but either **singleplot** or
    **multiplot** as kind.


Properties of tasks
===================

For each task, you can set all attributes of the underlying class using the
``properties`` dictionary in the recipe. Therefore, to know which
parameters can be set for what kind of task means simply to check the
documentation for the respective classes. I.e., for a task represented by
an :obj:`aspecd.tasks.ProcessingTask` object, check out the appropriate
class from the :mod:`aspecd.processing` module. The same is true for
packages derived from ASpecD.

A simple example is the normalisation processing step using the
:class:`aspecd.processing.Normalisation` class:

.. code-block:: yaml

    tasks:
      - kind: processing
        type: Normalisation
        properties:
          parameters:
            kind: amplitude

How to know what properties can be set? Have a look at the
:class:`aspecd.processing.Normalisation` documentation. Note that all
properties that are documented there can be set using a recipe. As
processing steps always have a property ``parameters`` that is a
:class:`dict`, you need to set the individual keys of this dictionary.

Additionally, for each task, you can explicitly state to which of the
datasets it should be applied to. Note that not only the datasets initially
loaded can be used here, but all labels referring to datasets that originate
from other tasks.

Furthermore, depending on the kind of task, you may be able to set
additional parameters controlling in more detail how the particular task is
performed. For details, see the documentation of the respective task
subclass in this module below.


Prerequisites for recipe-driven data analysis
=============================================

.. note::

    This section is mostly relevant for those developing packages based on
    the ASpecD framework. Users of recipe-driven data analysis usually need
    not bother about these details (as others did for them already).


To be able to use recipe-driven data analysis in packages derived from the
ASpecD framework, a series of prerequisites needs to be met, *i.e.*, classes
implemented. Besides the usual suspects such as
:class:`aspecd.dataset.Dataset` and its constituents as well as the
different processing and analysis steps based on
:class:`aspecd.processing.SingleProcessingStep` and
:class:`aspecd.analysis.SingleAnalysisStep`, two different factory
classes need to be implemented in particular, subclassing

  * :class:`aspecd.dataset.DatasetFactory` and
  * :class:`aspecd.io.DatasetImporterFactory`,

respectively. Actually, only :class:`aspecd.dataset.DatasetFactory` is
directly used by :class:`aspecd.tasks.Recipe`, however, internally it relies
on the existence of :class:`aspecd.io.DatasetImporterFactory` to return a
dataset based solely on a (unique) ID.

Besides implementing these classes, the facilities provided by the
:mod:`aspecd.tasks` module should be fully sufficient for regular
recipe-driven data analysis. In particular, normally there should be no need
to subclass any of the classes within this module in a package derived from
the ASpecD framework. One particular design goal of recipe-driven data
analysis is to decouple the actual tasks being performed from the
general handling of recipes. The former is implemented within each
respective package built upon the ASpecD framework, the latter is taken care
of fully by the ASpecD framework itself. You might want to implement a simple
proxy within a derived package to prevent the user from having to call out to
functionality provided directly by the ASpecD framework. The latter might be
confusing for those unfamiliar with the underlying details, *i.e.*,
most common users. More explicit, you may want to create proxy classes in
the processing and analysis modules of your package, subclassing all the
concrete processing and analysis steps already provided with the ASpecD
framework.


Notes for developers
====================

.. note::

    This section is only relevant for those further developing the ASpecD
    framework. Users of recipe-driven data analysis as well as developers of
    packages derived from the ASpecD framework usually need not bother about
    these details (as others did for them already).

Recipe-driven data analysis introduces another level of abstraction and
indirection with its use of recipes in YAML format. Based on this analogy,
we have a :class:`aspecd.tasks.Recipe` consisting of a list of datasets and a
list of :class:`aspecd.tasks.Task` to be performed on the datasets. Such recipe
gets "cooked" by a :class:`aspecd.tasks.Chef`, and for the convenience of
the user of recipe-driven data analysis, the result gets "served" by the
:class:`aspecd.tasks.ChefDeService`. An actual user will not see any of
this, but simply call ``serve <recipe-name.yaml>`` from the command line.

Internally, recipes are represented by an instance of
:class:`aspecd.tasks.Recipe`, and this representation takes care already to
import the datasets specified in the ``datasets`` block of a recipe.
Therefore, all handling of data import needs to be done here. Similarly,
upon populating a recipe (from dict or by importing), the tasks will already
be created using a :class:`aspecd.tasks.TaskFactory`.

The actual tasks are represented by instances of
subclasses of :class:`aspecd.tasks.Task`, and they in turn create an
instance of the actual object internally, applying this to the dataset(s).

"Cooking" a recipe is done by :class:`aspecd.tasks.Chef`, and this class
takes care of writing a history in form of an executable recipe, thus ensuring
reproducibility and good scientific practice.

"Serving" the results of a cooked recipe is eventually the responsibility of
the :class:`aspecd.tasks.ChefDeService`, and it is this class calling out to
the :class:`aspecd.tasks.Chef` and writing the history to an actual file
that can be used as recipe again. For the convenience of the user, an entry
point (console script) is included in the ``setup.py`` file calling
:func:`aspecd.tasks.serve` that in turn takes care of loading the recipe and
instantiating a :class:`aspecd.tasks.ChefDeService`.


Module documentation
====================


.. todo::
    There is a number of things that are not yet implemented, but highly
    recommended for a working recipe-driven data analysis that follows good
    practice for reproducible research. This includes (but may not be
    limited to):

      * Parser for recipes performing a static analysis of their syntax.
        Useful particularly for larger datasets and/or longer lists of tasks.

"""

import collections
import copy
import datetime
import os
import re
import sys

import matplotlib.pyplot as plt

import aspecd.dataset
import aspecd.exceptions
import aspecd.io
import aspecd.plotting
import aspecd.system
import aspecd.utils


class Recipe:
    """
    Recipes get cooked by chefs in recipe-driven data analysis.

    A recipe contains a list of tasks to be performed on a list of
    datasets. To actually carry out all tasks in a recipe, it is handed
    over to a :obj:`aspecd.tasks.Chef` object for cooking using the
    respective :meth:`aspecd.tasks.Chef.cook` method.

    From a user's perspective, recipes reside usually in YAML files from
    where they are imported into an :obj:`aspecd.tasks.Recipe` object using
    its respective :meth:`import_into` method and an object of class
    :class:`aspecd.io.RecipeYamlImporter`. Similarly, a given recipe can be
    exported back to a YAML file using the :meth:`export_to` method and an
    object of class :class:`aspecd.io.RecipeYamlExporter`.

    In contrast to the persistent form of a recipe (e.g., as file on the
    file system), the object contains actual datasets and tasks that are
    objects of the respective classes. Therefore, the attributes of a
    recipe are normally set by the respective methods from either a file or
    a dictionary (that in turn will normally be created from contents of a
    file).

    Retrieving datasets is delegated to an
    :class:`aspecd.dataset.DatasetFactory` instance stored in
    :attr:`dataset_factory`. This provides a maximum of flexibility but
    makes it necessary to specify (and first implement) such factory in
    packages derived from the ASpecD framework.

    .. todo::
        Can recipes have LOIs themselves and therefore be retrieved from
        the extended data safe? Might be a sensible option, although
        generic (and at the same time unique) LOIs for recipes are much
        harder to create than LOIs for datasets and alike.

        Generally, the concept of a LOI is nothing a recipe needs to know
        about. But it does know about an ID of any kind. Whether this ID
        is a (local) path or a LOI doesn't matter. Somewhere in the ASpecD
        framework there may exist a resolver (factory) for handling IDs of
        any kind and eventually retrieving the respective information.


    Attributes
    ----------
    datasets : :class:`collections.OrderedDict`
        Ordered dictionary of datasets the tasks should be performed for

        Each dataset is an object of class :class:`aspecd.dataset.Dataset`.

        The keys are the dataset ids.

    tasks : :class:`list`
        List of tasks to be performed on the datasets

        Each task is an object of class :class:`aspecd.tasks.Task`.

    results : :class:`collections.OrderedDict`
        Ordered dictionary of results originating from analysis tasks

        Results can be of any type, but are mostly either instances of
        :class:`aspecd.dataset.Dataset` or
        :class:`aspecd.metadata.PhysicalQuantity`.

        The keys are those defined by
        :attr:`aspecd.tasks.SingleanalysisTask.result` and
        :attr:`aspecd.tasks.MultianalysisTask.result`, respectively.

    figures : :class:`collections.OrderedDict`
        Ordered dictionary of figures originating from plotting tasks

        Each entry is an object of class :class:`aspecd.tasks.FigureRecord`.

    plotters : :class:`collections.OrderedDict`
        Ordered dictionary of plotters originating from plotting tasks

        Each entry is an object of class :class:`aspecd.plotting.Plotter`.

        To end up in the list of plotters, the plot task needs to define a
        result. This is mainly used for tasks involving CompositePlotters,
        to define the plotters for each individual plot panel.

    dataset_factory : :class:`aspecd.dataset.DatasetFactory`
        Factory for datasets used to retrieve datasets

        If no factory is set, but a recipe imported from a file or set from
        a dictionary, an exception will be raised.

    task_factory : :class:`aspecd.tasks.TaskFactory`
        Factory for tasks

        Defaults to an object of class :class:`aspecd.tasks.TaskFactory`.

        If no factory is set, but a recipe imported from a file or set from
        a dictionary, an exception will be raised.

    default_package: :class:`str`
        Name of the package the task objects are obtained from

        If no name for a default package is supplied, "aspecd" is used.

    datasets_source_directory: :class:`str`
        Root directory for the datasets.

        Interpreted as absolute path if starting with the system-specific file
        separator. Otherwise, interpreted as relative to the current
        directory. If provided, all output resulting from cooking a recipe
        will be saved to this path.

    output_directory: :class:`str`
        Directory to save output (plots, reports, ...) to.

        Interpreted as absolute path if starting with the system-specific file
        separator. Otherwise, interpreted as relative to the current
        directory. If provided, all output resulting from cooking a recipe
        will be saved to this path.

        Make sure the path actually exists. Otherwise, you may run into
        trouble when tasks try to save their output.

    autosave_plots: :class:`bool`
        Whether to save plots automatically even if no filename is provided.

        If true, each :class:`aspecd.tasks.SingleplotTask` and
        :class:`aspecd.tasks.MultiplotTask` will save the plots to default
        file names. For details, see the documentation of the respective
        classes.

        Default: True

        .. versionadded:: 0.2

    filename : :class:`str`
        Name of the (YAML) file the recipe was loaded from.

        Empty string if recipe was loaded from a dictionary instead.

        The filename can be used to persist the history of a cooked recipe
        in form of a YAML file for full reproducibility. This will be done
        when using the :class:`aspecd.tasks.ChefDeService` class and its
        :meth:`aspecd.tasks.ChefDeService.serve` method.

    Raises
    ------
    aspecd.tasks.MissingDictError
        Raised if no dict is provided.
    aspecd.tasks.MissingImporterError
        Raised if no importer is provided.
    aspecd.tasks.MissingExporterError
        Raised if no exporter is provided.
    aspecd.tasks.MissingDatasetFactoryError
        Raised if :attr:`dataset_factory` is invalid.
    aspecd.tasks.MissingTaskFactoryError
        Raised if :attr:`task_factory` is invalid.

    """

    def __init__(self):
        super().__init__()
        self.datasets = collections.OrderedDict()
        self.results = collections.OrderedDict()
        self.figures = collections.OrderedDict()
        self.plotters = collections.OrderedDict()
        self.tasks = list()
        self.dataset_factory = None
        self.task_factory = TaskFactory()
        self.default_package = ''
        self.datasets_source_directory = ''
        self.output_directory = ''
        self.autosave_plots = True
        self.filename = ''

    def from_dict(self, dict_=None):  # noqa: MC0001
        """
        Set attributes from dictionary.

        Loads datasets and creates :obj:`aspecd.tasks.Task` objects that
        are stored as lists respectively.

        Parameters
        ----------
        dict_ : :class:`dict`
            Dictionary containing information of a recipe.

        Raises
        ------
        aspecd.tasks.MissingDictError
            Raised if no dict is provided.
        aspecd.tasks.MissingDatasetFactoryError
            Raised if :attr:`importer_factory` is invalid.
        aspecd.tasks.MissingTaskFactoryError
            Raised if :attr:`task_factory` is invalid.

        """
        if not dict_:
            raise aspecd.exceptions.MissingDictError
        if not self.dataset_factory:
            raise aspecd.exceptions.MissingDatasetFactoryError
        if not self.task_factory:
            raise aspecd.exceptions.MissingTaskFactoryError
        for keyword in ["default_package", "datasets_source_directory",
                        "output_directory", "autosave_plots"]:
            if keyword in dict_:
                setattr(self, keyword, dict_[keyword])
        if self.output_directory and not self.output_directory.startswith('/'):
            self.output_directory = \
                self._get_absolute_path(self.output_directory)
        if 'datasets' in dict_:
            for key in dict_['datasets']:
                self._append_dataset(key)
        if 'tasks' in dict_:
            for key in dict_['tasks']:
                self._append_task(key)

    @staticmethod
    def _get_absolute_path(path_=''):
        return os.path.join(os.path.abspath(os.path.curdir), path_)

    def _append_dataset(self, key):
        properties = dict()
        importer = None
        importer_parameters = None
        if isinstance(key, dict):
            properties = copy.copy(key)
            source = key['source']
            properties.pop('source')
            if 'id' in key:
                label = key['id']
                properties.pop('id')
            else:
                label = key['source']
            if 'importer' in key:
                importer = key['importer']
            if 'importer_parameters' in key:
                importer_parameters = key['importer_parameters']
        else:
            source = key
            label = key
        if self.datasets_source_directory:
            source = os.path.join(self.datasets_source_directory, source)
        if 'package' in properties:
            dataset_factory = \
                self._get_dataset_factory(package=properties['package'])
            # noinspection PyUnresolvedReferences
            dataset = \
                dataset_factory.get_dataset(source=source,
                                            importer=importer,
                                            parameters=importer_parameters)
        else:
            dataset = \
                self.dataset_factory.get_dataset(source=source,
                                                 importer=importer,
                                                 parameters=importer_parameters)
        for property_key, value in properties.items():
            if hasattr(dataset, property_key):
                setattr(dataset, property_key, value)
        self.datasets[label] = dataset

    @staticmethod
    def _get_dataset_factory(package=''):
        dataset_factory_name = '.'.join([package, 'dataset', 'DatasetFactory'])
        dataset_factory = \
            aspecd.utils.object_from_class_name(dataset_factory_name)
        importer_factory_name = '.'.join([package, 'io',
                                          'DatasetImporterFactory'])
        importer_factory = \
            aspecd.utils.object_from_class_name(importer_factory_name)
        dataset_factory.importer_factory = importer_factory
        return dataset_factory

    def _append_task(self, key):
        task = self.task_factory.get_task_from_dict(key)
        task.from_dict(key)
        task.recipe = self
        if self.default_package and not task.package:
            task.package = self.default_package
        self.tasks.append(task)

    def to_dict(self):
        """
        Return dict from attributes.

        Returns
        -------
        dict_ : :class:`dict`
            Dictionary with fields "datasets" and "tasks"

        """
        dict_ = {'datasets': [], 'tasks': []}
        for dataset in self.datasets:
            dataset_dict = {}
            if not self.datasets[dataset].id == dataset:
                dataset_dict['source'] = self.datasets[dataset].id
                dataset_dict['id'] = dataset
            if not self.datasets[dataset].label == self.datasets[dataset].id:
                dataset_dict['source'] = self.datasets[dataset].id
                dataset_dict['label'] = self.datasets[dataset].label
            if self._dataset_from_foreign_package(self.datasets[dataset]):
                dataset_dict['source'] = self.datasets[dataset].id
                dataset_dict['package'] = \
                    aspecd.utils.full_class_name(dataset).split('.')[0]
            if dataset_dict:
                dict_['datasets'].append(dataset_dict)
            else:
                dict_['datasets'].append(self.datasets[dataset].id)
        for task in self.tasks:
            dict_['tasks'].append(task.to_dict())
        return dict_

    def _dataset_from_foreign_package(self, dataset=None):
        package_names = ['aspecd']
        if self.default_package:
            package_names.append(self.default_package)
        return not aspecd.utils.full_class_name(dataset).startswith(tuple(
            package_names))

    def import_from(self, importer=None):
        """
        Import recipe using importer.

        Importers can be created to read recipes from different sources.
        Thus the recipe as such is entirely independent of the persistence
        layer.

        Parameters
        ----------
        importer : :class:`aspecd.io.RecipeImporter`
            importer used to actually import recipe

        Raises
        ------
        aspecd.tasks.MissingImporterError
            Raised if no importer is provided

        """
        if not importer:
            raise aspecd.exceptions.MissingImporterError(
                'An importer instance is needed to import a recipe.')
        importer.import_into(self)

    def export_to(self, exporter=None):
        """
        Export recipe using exporter.

        Exporters can be created to write recipes to different targets.
        Thus the recipe as such is entirely independent of the persistence
        layer.

        Parameters
        ----------
        exporter : :class:`aspecd.io.RecipeExporter`
            exporter used to actually export recipe

        Raises
        ------
        aspecd.tasks.MissingExporterError
            Raised if no exporter is provided

        """
        if not exporter:
            raise aspecd.exceptions.MissingExporterError(
                'An exporter instance is needed to export a recipe.')
        exporter.export_from(self)

    def get_dataset(self, identifier=''):
        """
        Return dataset corresponding to given identifier.

        In case of having a list of identifiers, use the similar method
        :meth:`aspecd.tasks.Recipe.get_datasets`.

        Parameters
        ----------
        identifier : :class:`str`
            Identifier matching the :attr:`aspecd.dataset.Dataset.id`
            attribute.

        Returns
        -------
        dataset : :class:`aspecd.dataset.Dataset`
            Dataset corresponding to given identifier

            If no dataset corresponding to the given identifier could be
            found, :obj:`None` is returned.

        Raises
        ------
        aspecd.tasks.MissingDatasetIdentifierError
            Raised if no identifier is provided.

        """
        if not identifier:
            raise aspecd.exceptions.MissingDatasetIdentifierError
        matching_dataset = None
        if identifier in self.datasets:
            matching_dataset = self.datasets[identifier]
        if identifier in self.results:
            if isinstance(self.results[identifier], aspecd.dataset.Dataset):
                matching_dataset = self.results[identifier]
        return matching_dataset

    def get_datasets(self, identifiers=None):
        """
        Return datasets corresponding to given list of identifiers.

        In case of having a single identifier, use the similar method
        :meth:`aspecd.tasks.Recipe.get_dataset`.

        Parameters
        ----------
        identifiers : :class:`list`
            Identifiers matching the :attr:`aspecd.dataset.Dataset.id`
            attribute.

        Returns
        -------
        datasets : :class:`list`
            Datasets corresponding to given identifier

            Each dataset is an instance of :class:`aspecd.dataset.Dataset`.

            If no datasets corresponding to the given identifiers could be
            found, an empty list is returned.

        Raises
        ------
        aspecd.tasks.MissingDatasetIdentifierError
            Raised if no identifiers are provided.

        """
        if not identifiers:
            raise aspecd.exceptions.MissingDatasetIdentifierError
        matching_datasets = [self.datasets[key] for key in identifiers if
                             key in self.datasets]
        for identifier in identifiers:
            if identifier in self.results:
                if isinstance(self.results[identifier],
                              aspecd.dataset.Dataset):
                    matching_datasets.append(self.results[identifier])
        return matching_datasets


class Chef:
    """
    Chefs cook recipes in recipe-driven data analysis.

    As a result, they create a full history of the tasks performed,
    including all parameters, implicit and explicit. In this respect,
    they make the history independent of a singe dataset and allow to trace
    processing and analysis of multiple datasets.

    .. note::

        One necessary prerequisite for full reproducibility is therefore
        some kind of persistent and unique identifier for each dataset. The
        "Lab Object Identifier" (LOI) as used within the `LabInform
        <https://www.labinform.de/>`_ framework, is one solution of such
        identifier.


    For persisting the history of cooking a recipe, the contents of the
    ``history`` attribute should be saved as a YAML file. There are two ways
    how to do that: manually and fully automated. If you manually
    instantiate an object of the :class:`aspecd.tasks.Chef` class, you would
    need to do that on your own, as follows::

        chef = aspecd.tasks.Chef()
        # ... obtaining recipe from file
        chef.cook(recipe)

        yaml = aspecd.utils.Yaml()
        yaml.dict = chef.history
        yaml.write_to(filename='<my-recipe-history>.yaml')

    The other way is to use an instance of the
    :class:`aspecd.tasks.ChefDeService` class and its
    :meth:`aspecd.tasks.ChefDeService.serve` method::

        chef_de_service = ChefDeService()
        chef_de_service.serve(recipe_filename='my_recipe.yaml')

    This will automatically save the recipe history for you as a YAML file
    with its filename derived from the original recipe name. For details,
    see the documentation of the :class:`aspecd.tasks.ChefDeService` class.

    The YAML files generated from saving the history should work as recipes
    themselves, therefore allowing a full turnover, as well as easy
    modification of a recipe.

    Attributes
    ----------
    recipe : :class:`aspecd.tasks.Recipe`
        Recipe to cook, i.e. to carry out

    history : :class:`collections.OrderedDict`
        History of cooking the recipe

        Contains a complete record of each task performed, including all
        parameters, implicit and explicit. Additionally, contains system
        information as collected by the :class:`aspecd.system.SystemInfo`
        class.

        Can be exported to a YAML file that works as a recipe.

    Parameters
    ----------
    recipe : :class:`aspecd.tasks.Recipe`
        Recipe to cook, i.e. to carry out

    Raises
    ------
    aspecd.tasks.MissingRecipeError
        Raised if no recipe is available to be cooked

    """

    def __init__(self, recipe=None):
        self.history = collections.OrderedDict()
        self.recipe = recipe
        self._timespec = 'seconds'  # Format used for time stamps

    def cook(self, recipe=None):
        """
        Cook recipe, i.e. carry out tasks contained therein.

        A recipe is an object of class :class:`aspecd.tasks.Recipe` and
        contains both, a list of datasets and a list of tasks to be
        performed on these datasets.

        Parameters
        ----------
        recipe : :class:`aspecd.tasks.Recipe`
            Recipe to cook, i.e. tasks to carry out on particular datasets

        Raises
        ------
        aspecd.tasks.MissingRecipeError
            Raised if no recipe is available to be cooked

        """
        self._assign_recipe(recipe)
        self._prepare_history()
        for task in self.recipe.tasks:
            task.perform()
            self.history["tasks"].append(task.to_dict())
        try:
            self.history["info"]["end"] = \
                datetime.datetime.now().isoformat(timespec=self._timespec)
        except TypeError:
            self.history["info"]["end"] = \
                datetime.datetime.now().isoformat(sep='T')

    def _assign_recipe(self, recipe):
        if not recipe:
            if not self.recipe:
                raise aspecd.exceptions.MissingRecipeError
        else:
            self.recipe = recipe

    def _prepare_history(self):
        try:
            timestamp = datetime.datetime.now().isoformat(
                timespec=self._timespec)
        except TypeError:
            timestamp = datetime.datetime.now().isoformat(sep='T')
        self.history["info"] = {'start': timestamp, 'end': ''}
        system_info = aspecd.system.SystemInfo(self.recipe.default_package)
        self.history["system_info"] = system_info.to_dict()
        for key in ['default_package', 'datasets_source_directory',
                    'output_directory', 'autosave_plots']:
            if getattr(self.recipe, key):
                self.history[key] = getattr(self.recipe, key)
        recipe_dict = self.recipe.to_dict()
        self.history["datasets"] = recipe_dict['datasets']
        if self.recipe.datasets_source_directory:
            source_dir = self.recipe.datasets_source_directory
            if not source_dir.endswith('/'):
                source_dir += "/"
            for dataset in self.history["datasets"]:
                if isinstance(dataset, dict):
                    dataset["source"] = \
                        dataset["source"].replace(source_dir, '')
                else:
                    dataset.replace(source_dir, '')
        self.history["tasks"] = []


class Task(aspecd.utils.ToDictMixin):
    """
    Base class storing information for a single task.

    Different underlying objects used to actually perform the respective
    task have different requirements and different signatures. In order to
    generically perform a task, for each kind of task -- such as
    processing, analysis, plotting -- this class needs to be subclassed.
    For a number of basic tasks available in the ASpecD package, this has
    already been done. See:

        * :class:`aspecd.tasks.ProcessingTask`
        * :class:`aspecd.tasks.AnalysisTask`

           * :class:`aspecd.tasks.SingleanalysisTask`
           * :class:`aspecd.tasks.MultianalysisTask`

        * :class:`aspecd.tasks.AnnotationTask`
        * :class:`aspecd.tasks.PlotTask`

           * :class:`aspecd.tasks.SingleplotTask`
           * :class:`aspecd.tasks.MultiplotTask`

        * :class:`aspecd.tasks.ReportTask`

    Note that imports of datasets are usually not handled using tasks,
    as this is taken care of automatically by defining a list of datasets
    in a :class:`aspecd.tasks.Recipe`.

    Usually, you need not care to instantiate objects of the correct type,
    as this is done automatically by the :class:`aspecd.tasks.Recipe` using
    the :class:`aspecd.tasks.TaskFactory`.


    Attributes
    ----------
    kind : :class:`str`
        Kind of task.

        Usually corresponds to the module name the type (class) is defined in.
        See the note below for special cases.
    type : :class:`str`
        Type of task.

        Corresponds to the class name eventually responsible for performing
        the task.
    package : :class:`str`
        Name of the package the class eventually responsible for performing the
        task belongs to.
    properties : :class:`dict`
        Properties necessary to perform the task.

        Should have keys corresponding to the properties of the class given
        as :attr:`type` attribute.

        Generally, all keys in :attr:`aspecd.tasks.Task.properties` will be
        mapped to the underlying object created to perform the actual task.

        In contrast, all additional attributes of a given task object
        subclassing :class:`aspecd.tasks.Task` that are specific to the task
        object as such and its operation, but not for the object created by
        the task object to perform the task, are not part of the
        :attr:`aspecd.tasks.Task.properties` dict. For a recipe, this means
        that these additional attributes are at the same level as
        :attr:`aspecd.tasks.Task.properties`.
    apply_to : :class:`list`
        List of datasets the task should be applied to.

        Defaults to an empty list, meaning that the task will be performed
        for all datasets contained in a :class:`aspecd.tasks.Recipe`.

        Each dataset is referred to by the value of its
        :attr:`aspecd.dataset.Dataset.source` attribute. This should be
        unique and can consist of a filename, path, URL/URI, LOI, or alike.
    recipe : :class:`aspecd.tasks.Recipe`
        Recipe containing the task and the list of datasets the task refers to


    .. note::
        A note to developers: Usually, the :attr:`aspecd.tasks.Task.kind`
        attribute is identical to the module name the respective class
        resides in. However, sometimes this is not the case, as with the
        plotters. In this case, an additional, non-public attribute
        :attr:`aspecd.tasks.Task._module` can be set in classes derived from
        :class:`aspecd.tasks.Task`.


    Raises
    ------
    aspecd.tasks.MissingDictError
        Raised if no dict is provided when calling :meth:`from_dict`.
    aspecd.tasks.MissingRecipeError
        Raised if no recipe is available upon performing the task.

    """

    def __init__(self, recipe=None):
        super().__init__()
        self.kind = ''
        self.type = ''
        self.package = ''
        self.properties = dict()
        self.apply_to = []
        self.recipe = recipe
        self._module = ''
        self._exclude_from_to_dict = ['recipe']
        self._task = None

    def from_dict(self, dict_=None):
        """
        Set attributes from dictionary.

        Parameters
        ----------
        dict_ : :class:`dict`
            Dictionary containing information of a task.

        Raises
        ------
        aspecd.tasks.MissingDictError
            Raised if no dict is provided.

        """
        if not dict_:
            raise aspecd.exceptions.MissingDictError
        for key, value in dict_.items():
            if hasattr(self, key) and value:
                if isinstance(getattr(self, key), list):
                    if isinstance(value, list):
                        for element in value:
                            getattr(self, key).append(element)
                    else:
                        getattr(self, key).append(value)
                else:
                    setattr(self, key, value)

    def to_dict(self):
        """
        Create dictionary containing public attributes of an object.

        Furthermore, replace certain objects with their respective labels
        provided in the recipe. These objects currently include datasets,
        results, figures (*i.e.* figure records), and plotters.

        Returns
        -------
        public_attributes : :class:`collections.OrderedDict`
            Ordered dictionary containing the public attributes of the object

            The order of attribute definition is preserved

        """
        if 'parameters' in self.properties:
            self._replace_objects_with_labels(self.properties["parameters"])
        self._replace_objects_with_labels(self.properties)
        return super().to_dict()

    def _replace_objects_with_labels(self, dict_=None):
        for property_key, property_value in dict_.items():
            for dataset_key, dataset_value in self.recipe.datasets.items():
                if property_value is dataset_value:
                    dict_[property_key] = dataset_key
            for dataset_key, dataset_value in self.recipe.results.items():
                if property_value is dataset_value:
                    dict_[property_key] = dataset_key
            for figure_key, figure_value in self.recipe.figures.items():
                if property_value is figure_value:
                    dict_[property_key] = figure_key
            for plotter_key, plotter_value in self.recipe.plotters.items():
                if property_value is plotter_value:
                    dict_[property_key] = plotter_key

    def perform(self):
        """
        Call the appropriate method of the underlying object.

        The actual implementation is contained in the non-public method
        :meth:`aspecd.tasks.Task._perform`.

        Different underlying objects have different methods used to
        actually perform the respective task. In order to generically
        perform a task, classes derived from the :class:`aspecd.tasks.Task`
        base class need to override :meth:`aspecd.tasks.Task._perform`
        accordingly.

        Use :meth:`aspecd.tasks.Task.get_object` to get an instance of the
        actual object necessary to perform the task, and afterwards call
        its appropriate method.

        Similarly, to get the actual dataset using the dataset id stored in
        :attr:`aspecd.tasks.Task.apply_to`, use the method
        :meth:`aspecd.tasks.Recipe.get_dataset` of the recipe stored in
        :attr:`aspecd.tasks.Task.recipe`.

        Raises
        ------
        aspecd.tasks.MissingRecipeError
            Raised if no recipe is available.

        """
        if not self.recipe:
            raise aspecd.exceptions.MissingRecipeError
        if not self.apply_to:
            self.apply_to = list(self.recipe.datasets.keys())
        self._perform()

    def _perform(self):
        """
        Call the appropriate method of the underlying object.

        Classes derived from :class:`aspecd.tasks.Task` need to override
        this method and provide the actual implementation.

        """
        self._task = self.get_object()

    def get_object(self):
        """
        Return object for a particular task including all attributes.

        Returns
        -------
        obj : :class:`object`
            Object of a class defined in the :attr:`type` attribute of a task

        """
        obj = self._create_object()
        self._set_object_attributes(obj)
        return obj

    def _create_object(self):
        """
        Create object for a particular task.

        In case no object can be retrieved from the class name provided,
        the current package is prepended to kind and type stored in
        :attr:`kind' and :attr:`type`, respectively. This allows for
        specifying explicit class names including packages, but at the same
        time to omit the package name for classes from the current package.

        Returns
        -------
        obj : `object`
            Object of a class defined in the :attr:`type` attribute of a task

        """
        if self._module:
            class_name = '.'.join([self._module, self.type])
        else:
            class_name = '.'.join([self.kind, self.type])
        try:
            obj = aspecd.utils.object_from_class_name(class_name)
        except (ImportError, AttributeError):
            if self.package:
                package_name = self.package
            else:
                package_name = aspecd.utils.package_name(self)
            class_name = '.'.join([package_name, class_name])
            obj = aspecd.utils.object_from_class_name(class_name)
        return obj

    def _set_object_attributes(self, obj):
        """
        Set attributes in object from the keys of the :attr:`properties` dict.

        Only those keys that have a matching attribute in the object are
        actually mapped, all others silently ignored.

        Properties or values of dicts in properties that correspond to keys
        in :attr:`aspecd.recipe.results` of the recipe stored in
        :attr:`aspecd.task.recipe` will be replaced accordingly. The same is
        true for properties corresponding to keys in
        :attr:`aspecd.recipe.datasets` of the recipe stored in
        :attr:`aspecd.task.recipe`. Thus, dataset references can be used in
        properties and get replaced by the actual datasets. Similarly,
        figures stored in :attr:`aspecd.recipe.figures` can be referenced
        and will be replaced by the actual :obj:`aspecd.tasks.FigureRecord`
        objects.

        .. todo::
            Eventually, with the advent of logging in the ASpecD framework,
            it might be sensible to at least add a log message if a key
            gets ignored, such that it is no longer silently ignored. This
            might be helpful for debugging purposes.

        Parameters
        ----------
        obj : `object`
            Object of a class defined in the :attr:`type` attribute of a task

        """
        properties = self._parse_properties()
        for key in properties:
            if hasattr(obj, key):
                attr = getattr(obj, key)
                if hasattr(attr, 'from_dict'):
                    attr.from_dict(properties[key])
                elif isinstance(attr, dict) and attr:
                    prop = self._set_attributes_in_dict(
                        source=properties[key], target=attr)
                    setattr(obj, key, prop)
                else:
                    setattr(obj, key, properties[key])

    def _set_attributes_in_dict(self, source=None, target=None):
        # pylint: disable=too-many-nested-blocks
        for key in source:
            if key in target:
                if isinstance(target[key], dict):
                    target[key] = self._set_attributes_in_dict(
                        source[key], target[key])
                elif isinstance(target[key], list):
                    for idx, element in enumerate(target[key]):
                        if len(source[key]) >= idx + 1:
                            if hasattr(element, 'from_dict'):
                                element.from_dict(source[key][idx])
                            elif isinstance(element, dict):
                                target[key][idx] = self._set_attributes_in_dict(
                                    source=source[key][idx], target=element)
                            else:
                                target[key][idx] = source[key][idx]
                else:
                    target[key] = source[key]
            else:
                target[key] = source[key]
        return target

    def _parse_properties(self):
        """
        Replace labels for datasets, results, figures, plotters in properties.

        Additionally to labels, variables will be parsed and replaced.
        Currently, the following types of variables are understood:

        .. code-block:: yaml

            key1: {{ basename(id) }}
            key2: {{ path(id) }}
            key3: {{ id(id) }}

        Here, ``id`` is the id used internally for referring to a dataset,
        ``{{ basename(id) }}`` will be replaced with the file basename of
        the respective dataset source, ``{{ path(id) }}`` will be replaced
        by the path of the respective dataset source, and  ``{{ id(id) }}``
        will be replaced by the id itself.

        Returns
        -------
        properties : :class:`dict`
            properties with labels replaced by actual object references

        """
        if self.recipe:
            properties = aspecd.utils.replace_value_in_dict(
                self.recipe.datasets, self.properties)
            if self.recipe.results:
                properties = aspecd.utils.replace_value_in_dict(
                    self.recipe.results, properties)
            if self.recipe.figures:
                properties = aspecd.utils.replace_value_in_dict(
                    self.recipe.figures, properties)
            if self.recipe.plotters:
                properties = aspecd.utils.replace_value_in_dict(
                    self.recipe.plotters, properties)
            properties = self._replace_variables_in_properties(properties)
        else:
            properties = self.properties
        return properties

    def _replace_variables_in_properties(self, properties):
        pattern = r'{{([^}]*)}}'
        for key, value in properties.items():
            if isinstance(value, dict):
                self._replace_variables_in_properties(value)
            elif isinstance(value, str):
                matches = re.findall(pattern, value)
                for match in matches:
                    match_pattern = '{{' + match + '}}'
                    value = value.replace(match_pattern,
                                          self._parse_variable(match.strip()))
                properties[key] = value
        return properties

    def _parse_variable(self, variable):
        replacement = ''
        function, argument = re.findall(r'(\w*)\((\w*)\)', variable)[0]
        if function == 'id':
            replacement = argument
        elif function == 'basename':
            if argument in self.recipe.datasets.keys():
                replacement = \
                    aspecd.utils.basename(self.recipe.datasets[argument].id)
        elif function == 'path':
            if argument in self.recipe.datasets.keys():
                replacement = \
                    aspecd.utils.path(self.recipe.datasets[argument].id)
        return replacement


class ProcessingTask(Task):
    """
    Processing step defined as task in recipe-driven data analysis.

    Processing steps will always be performed individually for each dataset.

    For more information on the underlying general class,
    see :class:`aspecd.processing.SingleProcessingStep`.

    For an example of how such a processing task may be included into a
    recipe, see the YAML listing below:

    .. code-block:: yaml

        kind: processing
        type: SingleProcessingStep
        properties:
          parameters:
            param1: bar
            param2: foo
          comment: >
            Some free text describing in more details the processing step
        apply_to:
          - loi:xxx

    Note that you can refer to datasets and results created during cooking
    of a recipe using their respective labels. Those labels will
    automatically be replaced by the actual dataset/result prior to
    performing the task.

    Sometimes it can come in quite handy to compare different processing
    steps on the same original dataset, *e.g.* a series of different
    parameters. Think of a polynomial baseline correction where you would
    like to compare the effect of polynomials of different order. Here,
    what you are interested in is to work on *copies* of the original
    dataset and get the results stored additionally. Here you go:

    .. code-block:: yaml

        kind: processing
        type: SingleProcessingStep
        result: label


    And if you now want to do that for multiple datasets, you can do that as
    well. However, make sure to provide as many result labels as you have
    datasets to perform the processing step on, as otherwise no result will
    be stored and the processing step will operate on the original datasets:

    .. code-block:: yaml

        kind: processing
        type: SingleProcessingStep
        apply_to:
          - loi:xxx
          - loi:yyy
        result:
          - label1
          - label2


    Another thing that can be very useful for data processing is to add a
    comment to an individual step, *e.g.* with an explanation why this step
    has been performed:

    .. code-block:: yaml

        kind: processing
        type: SingleProcessingStep
        comment: >
          Lorem ipsum dolor sit amet,
          consectetur adipiscing elit.


    Note that using the ``>`` sign will replace newline characters with
    spaces. If you want to preserve the newline characters, use ``|`` instead.


    Attributes
    ----------
    result : :class:`str`
        Label for the results of a processing step.

        Processing steps always operate on datasets. However, sometimes it
        is useful to have a processing task return a copy of the processed
        dataset, in order to compare different processings afterwards.
        Therefore, you can specify a ``result`` label. In this case,
        the dataset will be copied first, the processing step performed on
        it, and afterwards the result returned as a *new* dataset that is
        accessible throughout the rest of the recipe with the label provided.

        In case you perform the processing on several datasets, you may want
        to provide as many result labels as there are datasets. Otherwise,
        no result will be assigned.

    comment : :class:`str`
        Textual comment regarding the processing step


    .. versionchanged: 0.3
        New attribute :attr:`comment`

    """

    def __init__(self, recipe=None):
        super().__init__(recipe=recipe)
        self.result = ''
        self.comment = ''

    def _perform(self):
        result_labels = None
        if self.result and isinstance(self.result, list):
            if len(self.result) == len(self.apply_to):
                result_labels = self.result
            else:
                self.result = None
        for number, dataset_id in enumerate(self.apply_to):
            dataset = self.recipe.get_dataset(dataset_id)
            self._task = self.get_object()
            if self.comment:
                self._task.comment = self.comment
            if self.result:
                dataset_copy = copy.deepcopy(dataset)
                dataset_copy.process(processing_step=self._task)
                if result_labels:
                    dataset_copy.id = self.result[number]
                    self.recipe.results[self.result[number]] = dataset_copy
                else:
                    dataset_copy.id = self.result
                    self.recipe.results[self.result] = dataset_copy
            else:
                dataset.process(processing_step=self._task)


class SingleprocessingTask(ProcessingTask):
    """
    Singleprocessing step defined as task in recipe-driven data analysis.

    This is a convenience alias class for :class:`ProcessingTask`.
    Therefore, the following two tasks are identical:

    .. code-block:: yaml

        - kind: processing
          type: SingleProcessingStep

        - kind: singleprocessing
          type: SingleProcessingStep

    """

    def __init__(self, recipe=None):
        super().__init__(recipe=recipe)
        self._module = 'processing'


class MultiprocessingTask(Task):
    """
    Multiprocessing step defined as task in recipe-driven data analysis.

    Processing steps will always be performed individually for each dataset.
    Nevertheless, in this particular case, the processing depends on the
    list of datasets provided in the ``apply_to`` field

    For more information on the underlying general class,
    see :class:`aspecd.processing.MultiProcessingStep`.

    For an example of how such a processing task may be included into a
    recipe, see the YAML listing below:

    .. code-block:: yaml

        kind: multiprocessing
        type: MultiProcessingStep
        properties:
          parameters:
            param1: bar
            param2: foo
        apply_to:
          - loi:xxx
          - loi:yyy

    Note that you can refer to datasets and results created during cooking
    of a recipe using their respective labels. Those labels will
    automatically be replaced by the actual dataset/result prior to
    performing the task.

    Sometimes it can come in quite handy to compare different processing
    steps on the same original dataset, *e.g.* a series of different
    parameters. Here, what you are interested in is to work on *copies* of
    the original dataset and get the results stored additionally. Here you go:

    .. code-block:: yaml

        kind: multiprocessing
        type: MultiProcessingStep
        apply_to:
          - loi:xxx
          - loi:yyy
        result:
          - label1
          - label2


    Attributes
    ----------
    result : :class:`list`
        Labels for the results of a processing step.

        Processing steps always operate on datasets. However, sometimes it
        is useful to have a processing task return a copy of the processed
        dataset, in order to compare different processings afterwards.
        Therefore, you can specify a ``result`` label. In this case,
        the dataset will be copied first, the processing step performed on
        it, and afterwards the result returned as a *new* dataset that is
        accessible throughout the rest of the recipe with the label provided.

        In case you perform the processing on several datasets, you may want
        to provide as many result labels as there are datasets. Otherwise,
        no result will be assigned.

    """

    def __init__(self, recipe=None):
        super().__init__(recipe=recipe)
        self._module = 'processing'
        self.result = ''

    def _perform(self):
        self._task = self.get_object()
        if self.result:
            datasets = []
            for dataset in self.recipe.get_datasets(self.apply_to):
                datasets.append(copy.deepcopy(dataset))
            self._task.datasets = datasets
            # noinspection PyUnresolvedReferences
            self._task.process()
            for number, dataset in enumerate(self._task.datasets):
                self.recipe.results[self.result[number]] = dataset
        else:
            self._task.datasets = self.recipe.get_datasets(self.apply_to)
            # noinspection PyUnresolvedReferences
            self._task.process()


class AnalysisTask(Task):
    """
    Analysis step defined as task in recipe-driven data analysis.

    Analysis steps can be performed individually for each dataset or the
    results combined, depending on the type of analysis step.

    .. important::

        An AnalysisTask should not be used directly but rather the two
        classes derived from this class, namely:

          * :class:`aspecd.tasks.SingleanalysisTask` and
          * :class:`aspecd.tasks.MultianalysisTask`.


    For more information on the underlying general class,
    see :class:`aspecd.analysis.AnalysisStep`.


    Attributes
    ----------
    result : :class:`str`
        Label for the result of an analysis step.

        The result of an analysis step can be everything from a scalar to an
        entire (new) dataset.

        This label will be used to refer to the result later on when
        further processing the recipe.

    comment : :class:`str`
        Textual comment regarding the analysis step


    .. versionchanged: 0.3
        New attribute :attr:`comment`

    """

    def __init__(self, recipe=None):
        super().__init__(recipe=recipe)
        self.result = ''
        self.comment = ''
        self._module = 'analysis'


class SingleanalysisTask(AnalysisTask):
    """
    Analysis step defined as task in recipe-driven data analysis.

    Singleanalysis steps can only be performed individually for each dataset.
    For analyses combining multiple datasets,
    see :class:`aspecd.tasks.MultianalyisTask`.

    For more information on the underlying general class,
    see :class:`aspecd.analysis.SingleAnalysisStep`.

    For an example of how such an analysis task may be included into a
    recipe, see the YAML listing below:

    .. code-block:: yaml

        kind: singleanalysis
        type: SingleAnalysisStep
        properties:
          parameters:
            param1: bar
            param2: foo
          comment: >
            Some free text describing in more details the analysis step
        apply_to:
          - loi:xxx
        result: label

    Note that you can refer to datasets and results created during cooking
    of a recipe using their respective labels. Those labels will
    automatically be replaced by the actual dataset/result prior to
    performing the task.

    And if you now want to do that for multiple datasets, you can do that as
    well. However, make sure to provide as many result labels as you have
    datasets to perform the analysis step on, as otherwise no result will
    be stored:

    .. code-block:: yaml

        kind: singleanalysis
        type: SingleAnalysisStep
        apply_to:
          - loi:xxx
          - loi:yyy
        result:
          - label1
          - label2

    In case you perform the analysis on several datasets, you may want to
    provide as many result labels as there are datasets. Otherwise,
    no result will be assigned.


    Another thing that can be very useful for data analysis is to add a
    comment to an individual step, *e.g.* with an explanation why this step
    has been performed:

    .. code-block:: yaml

        kind: singleanalysis
        type: SingleAnalysisStep
        comment: >
          Lorem ipsum dolor sit amet,
          consectetur adipiscing elit.


    Note that using the ``>`` sign will replace newline characters with
    spaces. If you want to preserve the newline characters, use ``|`` instead.

    """

    # noinspection PyUnresolvedReferences
    def _perform(self):
        result_labels = None
        if self.result and isinstance(self.result, list):
            if len(self.result) == len(self.apply_to):
                result_labels = self.result
            else:
                self.result = None
        for number, dataset_id in enumerate(self.apply_to):
            dataset = self.recipe.get_dataset(dataset_id)
            self._task = self.get_object()
            if self.comment:
                self._task.comment = self.comment
            self._task = dataset.analyse(analysis_step=self._task)
            if self.result:
                if result_labels:
                    if isinstance(self._task.result, aspecd.dataset.Dataset):
                        self._task.result.id = self.result[number]
                    self.recipe.results[self.result[number]] = \
                        self._task.result
                else:
                    if isinstance(self._task.result, aspecd.dataset.Dataset):
                        self._task.result.id = self.result
                    self.recipe.results[self.result] = self._task.result


class MultianalysisTask(AnalysisTask):
    """
    Analysis step defined as task in recipe-driven data analysis.

    Multianalysis steps are performed on a list of datasets and combine
    them in one single analysis. For analyses performed on individual
    datasets, see :class:`aspecd.tasks.SingleanalysisTask`.

    For more information on the underlying general class,
    see :class:`aspecd.analysis.MultiAnalysisStep`.

    For an example of how such an analysis task may be included into a
    recipe, see the YAML listing below:

    .. code-block:: yaml

        kind: multianalysis
        type: MultiAnalysisStep
        properties:
          parameters:
            param1: bar
            param2: foo
          comment: >
            Some free text describing in more details the analysis step
        apply_to:
          - loi:xxx
        result:
          - label1
          - label2

    Note that you can refer to datasets and results created during cooking
    of a recipe using their respective labels. Those labels will
    automatically be replaced by the actual dataset/result prior to
    performing the task.

    In case such a multianalysis step results in a list of resulting
    datasets, result should be a list of labels, not a single label.

    Raises
    ------
    IndexError
        Raised if list of result labels and results are not of same length

    """

    # noinspection PyUnresolvedReferences
    def _perform(self):
        self._task = self.get_object()
        self._task.datasets = self.recipe.get_datasets(self.apply_to)
        self._task.analyse()
        if self.result:
            # NOTE: This code is currently widely untested due to lack of
            # ideas of how to test it properly.
            if isinstance(self.result, list):
                if len(self.result) != len(self._task.result):
                    raise IndexError('List of result labels and results '
                                     ' must be of same length')
                for index, label in enumerate(self.result):
                    self._assign_result(label=label,
                                        result=self._task.result[index])
            else:
                self._assign_result(label=self.result, result=self._task.result)

    def _assign_result(self, label='', result=None):
        if isinstance(result, aspecd.dataset.Dataset):
            result.id = label
        self.recipe.results[label] = result


class AnnotationTask(Task):
    """
    Annotation step defined as task in recipe-driven data analysis.

    Annotation steps will always be performed individually for each dataset.

    For more information on the underlying general class,
    see :class:`aspecd.processing.Annotation`.

    """

    def _perform(self):
        for dataset_id in self.apply_to:
            dataset = self.recipe.get_dataset(dataset_id)
            self._task = self.get_object()
            dataset.annotate(annotation_=self._task)


class PlotTask(Task):
    """
    Plot step defined as task in recipe-driven data analysis.

    .. important::

        A PlotTask should not be used directly but rather the two classes
        derived from this class, namely:

          * :class:`aspecd.tasks.SingleplotTask` and
          * :class:`aspecd.tasks.MultiplotTask`.


    For more information on the underlying general class,
    see :class:`aspecd.plotting.Plotter`.


    Attributes
    ----------
    label : :class:`str`
        Label for the figure resulting from a plotting step.

        This label will be used to refer to the plot later on when
        further processing the recipe. Actually, in the recipe's
        :attr:`aspecd.tasks.Recipe.figures` dict, this label is used as a
        key and a :obj:`aspecd.tasks.FigureRecord` object stored containing
        all information necessary for further handling the results of the plot.

    result : :class:`str`
        Label for the plotter of a plotting step.

        This is useful in case of CompositePlotters, where different
        plotters need to be defined for each of the panels.

    """

    def __init__(self):
        super().__init__()
        self.label = ''
        self.result = ''
        self._module = 'plotting'

    def perform(self):
        """
        Call the appropriate method of the underlying object.

        For details, see the method :meth:`aspecd.tasks.Task.perform` of the
        base class.

        Additionally to what is done in the base class, a PlotTask adds a
        :obj:`aspecd.tasks.FigureRecord` object to the
        :attr:`aspecd.tasks.Recipe.figures` property of the underlying
        recipe in case an :attr:`aspecd.tasks.PlotTask.label` has been set.

        """
        super().perform()
        if self.label:
            self._add_figure_to_recipe()
        if self.result:
            self._add_plotter_to_recipe()

    def _add_figure_to_recipe(self):
        figure_record = FigureRecord()
        # noinspection PyTypeChecker
        figure_record.from_plotter(self.get_object())
        self.recipe.figures[self.label] = figure_record

    def _add_plotter_to_recipe(self):
        self.recipe.plotters[self.result] = self._task

    def save_plot(self, plot=None):
        """
        Save the figure of the plot created by the task.

        Parameters
        ----------
        plot : :class:`aspecd.plotting.Plotter`
            Plot whose figure should be saved

        """
        filename = None
        if plot.filename:
            filename = plot.filename
        elif 'filename' in self.properties and self.properties['filename']:
            filename = self.properties['filename']
        if filename:
            if self.recipe.output_directory:
                filename = os.path.join(self.recipe.output_directory, filename)
            saver = aspecd.plotting.Saver(filename=filename)
            plot.save(saver)


class SingleplotTask(PlotTask):
    """
    Singleplot step defined as task in recipe-driven data analysis.

    Singleplot steps can only be performed individually for each dataset.
    For plots combining multiple datasets,
    see :class:`aspecd.tasks.MultiplotTask`.

    For more information on the underlying general class,
    see :class:`aspecd.plotting.SinglePlotter`.

    For an example of how such a analysis task may be included into a
    recipe, see the YAML listing below:

    .. code-block:: yaml

        kind: singleplot
        type: SinglePlotter
        properties:
          properties:
            figure:
              title: My fancy figure title
            drawing:
              color: darkorange
              label: my data
              linewidth: 4
              linestyle: dashed
            legend:
              location: northeast
          parameters:
            show_legend: True
          caption:
            title: >
              Ideally a single sentence summarising the intend of the figure
            text: >
              More text for the figure caption
            parameters:
              - a list of parameters
              - that shall (additionally) be listed
              - in the figure caption
          filename: fancyfigure.pdf
        apply_to:
          - loi:xxx
        label: label

    Note that you can refer to datasets and results created during cooking
    of a recipe using their respective labels. Those labels will
    automatically be replaced by the actual dataset/result prior to
    performing the task.

    .. note::
        As soon as you provide a filename in the properties of your recipe,
        the resulting plot will automatically be saved to that filename,
        inferring the file format from the extension of the filename. For
        details of how the format is inferred see the documentation for the
        :meth:`matplotlib.figure.Figure.savefig` method.

    In case you apply the single plotter to more than one dataset and would
    like to save individual plots, you can do that by supplying a list of
    filenames instead of only a single filename. In this case, the plots get
    saved to the filenames in the list. A minmal example may look like this:

    .. code-block:: yaml

        kind: singleplot
        type: SinglePlotter
        properties:
          filename:
            - fancyfigure1.pdf
            - fancyfigure2.pdf
        apply_to:
          - loi:xxx
          - loi:yyy

    .. important::
        Make sure to provide the same number of file names in your recipe as
        the number of datasets you apply the plotter to. Otherwise you may
        run into trouble.

    .. note::
        If the recipe contains the ``output_directory`` key on the top
        level, the figure(s) will be saved to this directory.

    As long as ``autosave_plots`` in the recipe is set to True, the plots
    will be saved automatically, even if no filename is provided. These
    automatically generated filenames consist of the last part of the
    dataset source (excluding a potential file extension) and the name of
    the plotter used. To prevent the plotters in a recipe from automatically
    saving the plots, include the ``autosave_plots`` directive on the top
    level of your recipe and set it to False.

    """

    def _perform(self):
        filenames = []
        if "filename" in self.properties \
                and isinstance(self.properties["filename"], list) \
                and len(self.apply_to) == len(self.properties["filename"]):
            filenames = self.properties["filename"]
        for number, dataset_id in enumerate(self.apply_to):
            dataset = self.recipe.get_dataset(dataset_id)
            self._task = self.get_object()
            if filenames:
                self._task.filename = filenames[number]
            elif "filename" not in self.properties \
                    and self.recipe.autosave_plots:
                dataset_basename = \
                    os.path.splitext(os.path.split(dataset.id)[-1])[0]
                # noinspection PyUnresolvedReferences
                plotter_name = self._task.name.split(".")[-1]
                self._task.filename = \
                    "".join([dataset_basename, "_", plotter_name, ".pdf"])
            dataset.plot(plotter=self._task)
            # noinspection PyTypeChecker
            self.save_plot(plot=self._task)
            # noinspection PyUnresolvedReferences
            plt.close(self._task.figure)


class MultiplotTask(PlotTask):
    """
    Multiplot step defined as task in recipe-driven data analysis.

    Multiplot steps are performed on a list of datasets and combine them in
    one single plot. For plots performed on individual datasets,
    see :class:`aspecd.tasks.SingleplotTask`.

    For more information on the underlying general class,
    see :class:`aspecd.plotting.MultiPlotter`.

    For an example of how such a multiplot task may be included into a
    recipe, see the YAML listing below:

    .. code-block:: yaml

        kind: multiplot
        type: MultiPlotter
        properties:
          parameters:
            axes:
              - quantity: wavelength
                unit: nm
              - quantity: intensity
                unit:
            show_legend: True
          caption:
            title: >
              Ideally a single sentence summarising the intend of the figure
            text: >
              More text for the figure caption
            parameters:
              - a list of parameters
              - that shall (additionally) be listed
              - in the figure caption
          filename: fancyfigure.pdf
        apply_to:
          - loi:xxx
          - loi:yyy
        label: label

    Note that you can refer to datasets and results created during cooking
    of a recipe using their respective labels. Those labels will
    automatically be replaced by the actual dataset/result prior to
    performing the task.

    A specialty of plots of multiple datasets is that you cannot
    necessarily infer the axis labels from the datasets, hence may be
    interested to set them directly. This is done using the ``axes`` key of
    the ``parameters`` property of the :class:`aspecd.plotting.MultiPlotter`
    class, as shown in the recipe example above.

    .. note::
        As soon as you provide a filename in the properties of your recipe,
        the resulting plot will automatically be saved to that filename,
        inferring the file format from the extension of the filename. For
        details of how the format is inferred see the documentation for the
        :meth:`matplotlib.figure.Figure.savefig` method.

    .. note::
        If the recipe contains the ``output_directory`` key on the top
        level, the figure(s) will be saved to this directory.

    As long as ``autosave_plots`` in the recipe is set to True, the plots
    will be saved automatically, even if no filename is provided. These
    automatically generated filenames consist of the last part of the
    dataset sources (excluding a potential file extension) joint by underscores
    and the name of the plotter used. To prevent the plotters in a recipe
    from automatically saving the plots, include the ``autosave_plots``
    directive on the top level of your recipe and set it to False.

    """

    def _perform(self):
        self._task = self.get_object()
        self._task.datasets = self.recipe.get_datasets(self.apply_to)
        # noinspection PyUnresolvedReferences
        self._task.plot()
        if "filename" not in self.properties and self.recipe.autosave_plots:
            basenames = []
            for dataset in self._task.datasets:
                basenames.append(
                    os.path.splitext(os.path.split(dataset.id)[-1])[0])
            # noinspection PyUnresolvedReferences
            plotter_name = self._task.name.split(".")[-1]
            self._task.filename = \
                "".join(["_".join(basenames), "_", plotter_name, ".pdf"])
            self.properties["filename"] = self._task.filename
        # noinspection PyTypeChecker
        self.save_plot(plot=self._task)
        # noinspection PyUnresolvedReferences
        plt.close(self._task.figure)


class CompositeplotTask(PlotTask):
    """
    Compositeplot step defined as task in recipe-driven data analysis.

    Compositeplot steps are performed on a list of plots and combine them in
    one single figure. For more common plots employing only a single axes,
    see :class:`aspecd.tasks.SingleplotTask` and
    :class:`aspecd.tasks.MultiplotTask`.

    For more information on the underlying general class,
    see :class:`aspecd.plotting.CompositePlotter`.

    For an example of how such a compositeplot task may be included into a
    recipe, see the YAML listing below:

    .. code-block:: yaml

        - kind: singleplot
          type: SinglePlotter1D
          apply_to:
            - dataset1
          result: 1D_plot

        - kind: singleplot
          type: SinglePlotter2D
          apply_to:
            - dataset2
          result: 2D_plot

        - kind: compositeplot
          type: CompositePlotter
          properties:
            grid_dimensions: [1, 2]
            subplot_locations:
              - [0, 0, 1, 1]
              - [0, 1, 1, 1]
            plotter:
              - 1D_plot
              - 2D_plot
            filename: composed_plot.pdf

    The crucial aspect here is to first define the individual plotters that
    get used for the respective panels of the CompositePlotter. In this
    particular example, two different plots on two different datasets are
    created and afterwards combined into the CompositePlotter. Furthermore,
    for a CompositePlot you need to specify both, grid dimensions and
    subplot locations, as they will be set to one single axis by default.

    .. note::
        As long as the ``autosave_plots`` directive at the top level of the
        recipe is set to True, the results of the individual plotters
        combined in the CompositePlotter will be saved to generic filenames.
        To prevent this from happening, set ``autosave_plots`` to false.

    """

    def to_dict(self):
        """
        Create dictionary containing public attributes of the object.

        Returns
        -------
        public_attributes : :class:`collections.OrderedDict`
            Ordered dictionary containing the public attributes of the object

            The order of attribute definition is preserved

        """
        # Replace plotter objects with reference name
        for plotter in self.properties['plotter']:
            for key, value in self.recipe.plotters.items():
                if plotter is value:
                    self.properties['plotter'] = key
        super().to_dict()

    def _perform(self):
        self._task = self.get_object()
        # noinspection PyUnresolvedReferences
        self._task.plot()
        # noinspection PyTypeChecker
        self.save_plot(plot=self._task)


class ReportTask(Task):
    """
    Reporting step defined as task in recipe-driven data analysis.

    For more information on the underlying general class,
    see :class:`aspecd.report.Reporter`.

    For an example of how such an analysis task may be included into a
    recipe, see the YAML listing below:

    .. code-block:: yaml

        kind: report
        type: LaTeXReporter
        properties:
          template: my-fancy-latex-template.tex
          filename: some-filename-for-final-report.tex
          context:
            general:
              title: Some fancy title
              author: John Doe
            free_text:
              intro: >
                Short introduction of the experiment performed
              metadata: >
                Tabular and customisable overview of the dataset's metadata
              history: >
                Presentation of all processing, analysis and representation
                steps
            figures:
              title: my_fancy_figure
        compile: True
        apply_to:
          - loi:xxx

    Note that you can refer to datasets, results, and figures created during
    cooking of a recipe using their respective labels. Those labels will
    automatically be replaced by the actual dataset/result prior to
    performing the task.

    Whatever fields you set as property ``context`` can be accessed
    directly from within the template using the usual Python syntax for
    accessing keys of dictionaries. The fields shown here assume
    a certain structure of your template containing user-supplied free text
    for the introduction to several sections.

    Additionally, the context will contain the key ``dataset`` containing the
    result of the :meth:`aspecd.dataset.Dataset.to_dict` method, thus the full
    information contained in the dataset.

    You can, of course, apply the report task to multiple datasets
    individually. In this case, you most probably would like to have your
    reports saved to individual files. This means that the property
    ``filename`` needs to become a list:

    .. code-block:: yaml

        datasets:
          - foo
          - bar

        tasks:
          - kind: report
            type: LaTeXReporter
            properties:
              template: my-fancy-latex-template.tex
              filename:
                - report1.tex
                - report2.tex


    .. important::
        Make sure to provide the same number of file names in your recipe as
        the number of datasets you apply the report to. Otherwise you may
        run into trouble.

    .. note::
        If the recipe contains the ``output_directory`` key on the top
        level, the reports will be written to this directory.


    Attributes
    ----------
    compile : :class:`bool`
        Option for compiling a template.

        Some types of templates need an additional "compile" step to create
        output, most prominently LaTeX templates. If the Reporter class does
        not support compiling, but :attr:`compile` is set to True, it gets
        silently ignored.

    """

    def __init__(self):
        super().__init__()
        self.compile = False

    # noinspection PyUnresolvedReferences
    def _perform(self):
        self._add_figure_filenames_to_includes()
        for idx, dataset_id in enumerate(self.apply_to):
            dataset = self.recipe.get_dataset(dataset_id)
            task = self.get_object()
            task.context['dataset'] = dataset.to_dict()
            if isinstance(self.properties["filename"], list):
                task.filename = self.properties["filename"][idx]
            if self.recipe.output_directory:
                task.filename = os.path.join(self.recipe.output_directory,
                                             task.filename)
            task.create()
            if self.compile and hasattr(task, 'compile'):
                task.compile()

    def _add_figure_filenames_to_includes(self):
        if 'includes' in self.properties:
            self.properties['includes'].append(
                self._get_filenames_of_figures())
        else:
            self.properties['includes'] = self._get_filenames_of_figures()

    def _get_filenames_of_figures(self):
        filenames = []
        for figure in self.recipe.figures:
            filenames.append(self.recipe.figures[figure].filename)
        return filenames


class ModelTask(Task):
    """
    Building a model defined as task in recipe-driven data analysis.

    For more information on the underlying general class,
    see :class:`aspecd.model.Model`.

    For an example of how such a model task may be included into a recipe,
    see the YAML listing below:

    .. code-block:: yaml

        kind: model
        type: Model
        properties:
          parameters:
            foo: 42
            bar: 21
        from_dataset: dataset_label
        result: foo

    Note that you can refer to datasets and results created during cooking
    of a recipe using their respective labels. Those labels will
    automatically be replaced by the actual dataset/result prior to
    performing the task.

    Here, we have used this for the parameter ``from_dataset`` in the above
    recipe excerpt. For an :obj:`aspecd.model.Model` object, you can set the
    variables explicitly. However, in context of a recipe, this is rarely
    useful. Therefore, the ``from_dataset`` parameter lets you refer to a
    dataset (by its label used within the recipe) that is used to call the
    :meth:`aspecd.model.Model.from_dataset` method with to obtain the
    variables from this dataset.

    Attributes
    ----------
    result : :class:`str`
        Label for the dataset resulting from the model creation

        The result will always be an :obj:`aspecd.dataset.CalculatedDataset`
        object.

        This label will be used to refer to the result later on when
        further processing the recipe.

    from_dataset : :class:`str`
        Label of a dataset to obtain variables from

        The label needs to be a valid label to a dataset within the given
        recipe. The underlying dataset is obtained from the recipe and used
        to call the :meth:`aspecd.model.Model.from_dataset` method with to
        obtain the variables from this dataset.

    """

    def __init__(self, recipe=None):
        super().__init__(recipe=recipe)
        self.result = ''
        self.from_dataset = ''

    # noinspection PyUnresolvedReferences
    def _perform(self):
        task = self.get_object()
        if self.from_dataset:
            task.from_dataset(self.recipe.get_dataset(self.from_dataset))
        result = task.create()
        if self.result:
            self.recipe.results[self.result] = result


class ExportTask(Task):
    """
    Export of datasets.

    Sometimes, datasets need to be exported and stored as file.

    For more information on the underlying general class,
    see :class:`aspecd.io.DatasetExporter`.

    For an example of how such an export task may be included into a recipe,
    see the YAML listing below:

    .. code-block:: yaml

        kind: export
        type: AdfExporter
        properties:
          target:
            - dataset.adf
        apply_to:
          - loi:xxx

    Note that you can refer to datasets and results created during cooking
    of a recipe using their respective labels. Those labels will
    automatically be replaced by the actual dataset/result prior to
    performing the task.

    In case you apply the task to more than one dataset, you will need to
    supply a list of filenames instead of only a single filename. A minimal
    example may look like this:

    .. code-block:: yaml

        kind: export
        type: AdfExporter
        properties:
          target:
            - dataset1.adf
            - dataset2.adf
        apply_to:
          - loi:xxx
          - loi:yyy

    .. important::
        Make sure to provide the same number of file names in your recipe as
        the number of datasets you apply the exporter to. Otherwise you may
        run into trouble.

    .. note::
        If the recipe contains the ``output_directory`` key on the top
        level, the datasets will be saved to this directory.

    """

    def __init__(self):
        super().__init__()
        self._module = 'io'

    def _perform(self):
        targets = []
        if "target" in self.properties \
                and isinstance(self.properties["target"], list) \
                and len(self.apply_to) == len(self.properties["target"]):
            targets = self.properties["target"]
        for idx, dataset_id in enumerate(self.apply_to):
            dataset = self.recipe.get_dataset(dataset_id)
            task = self.get_object()
            if targets:
                task.target = targets[idx]
            if self.recipe.output_directory:
                task.target = os.path.join(self.recipe.output_directory,
                                           task.target)
            dataset.export_to(task)


class TaskFactory:
    """
    Factory for creating task objects based on the kind provided.

    The kind reflects the name of the module the actual object required for
    performing the task resides in. Furthermore, two ways are available for
    specifying the kind, either directly as argument provided to
    :meth:`aspecd.tasks.TaskFactory.get_task` or as key in a dict used as
    an argument for :meth:`aspecd.tasks.TaskFactory.get_task_from_dict`.

    The classes for the different tasks follow a simple convention:
    "<Module>Task" with "<Module>" being the capitalised module name the
    actual class necessary for performing the task resides in. Therefore,
    for each new module tasks should be available for, you will need to
    create an appropriate task class deriving from :class:`aspecd.tasks.Task`.

    Raises
    ------
    aspecd.tasks.MissingTaskDescriptionError
        Raised if no description is given necessary to create task.
    KeyError
        Raised if dict with task description does not contain "kind" key.

    """

    def get_task(self, kind=None):
        """
        Return task object specified by its kind.

        Parameters
        ----------
        kind : :class:`str`
            Kind of task to create

            Reflects the name of the module the actual object required for
            performing the task resides in.

        Returns
        -------
        task : :class:`aspecd.tasks.Task`
            Task object

            The actual subclass depends on the kind.

        Raises
        ------
        aspecd.tasks.MissingTaskDescriptionError
            Raised if no description is given necessary to create task.

        """
        if not kind:
            raise aspecd.exceptions.MissingTaskDescriptionError
        task = self._create_task_object(kind=kind)
        return task

    def get_task_from_dict(self, dict_=None):
        """
        Return task object specified by the "kind" key in the dict.

        Parameters
        ----------
        dict_ : :class:`dict`
            Dictionary containing "kind" key

            The "kind" key reflects the name of the module the actual object
            required for performing the task resides in.

        Returns
        -------
        task : :class:`aspecd.tasks.Task`
            Task object

            The actual subclass depends on the kind.

        Raises
        ------
        aspecd.tasks.MissingTaskDescriptionError
            Raised if no description is given necessary to create task.
        KeyError
            Raised if dict does not contain "kind" key.

        """
        if not dict_:
            raise aspecd.exceptions.MissingTaskDescriptionError
        if 'kind' not in dict_:
            raise KeyError
        task = self._create_task_object(kind=dict_['kind'])
        return task

    def _create_task_object(self, kind=None):
        """
        Create and return actual task object based on the kind provided.

        The classes for the different tasks follow a simple convention:
        "<Module>Task" with "<Module>" being the capitalised module name
        the actual class necessary for performing the task resides in.

        Parameters
        ----------
        kind : :class:`str`
            Kind of task to create

            Reflects the name of the module the actual object required for
            performing the task resides in.

            You can, however, prefix the module with the package. In such
            case, only the module name (the last element after splitting on
            the ".") is used.

        Returns
        -------
        task : :class:`aspecd.tasks.Task`
            Task object

            The actual subclass depends on the kind.

        .. todo::
            Check whether there are some ways to circumvent "package_name"
            to automatically be prefixed, as this would allow to use
            classes from different packages (if that is sensible to do).


        In case the kind string consists of several strings joined by ".",
        only the last part will be used as class name for obtaining the type
        of task, and the other parts stored in the ``package`` property of
        the task.

        """
        class_name = ''.join([kind.split('.')[-1].capitalize(), 'Task'])
        package_name = aspecd.utils.package_name(self)
        full_class_name = '.'.join([package_name, 'tasks', class_name])
        task = aspecd.utils.object_from_class_name(full_class_name)
        task.package = '.'.join(kind.split('.')[:-1])
        return task


class FigureRecord(aspecd.utils.ToDictMixin):
    """
    Information about a figure created by a PlotTask.

    Figures created during recipe-driven data analysis may need to be added,
    e.g., to a report. Therefore, the information contained in the PlotTask
    needs to be accessible by the recipe and other tasks in turn.

    Attributes
    ----------
    caption : :class:`dict`
        User-supplied information for the figure caption.

        Has three fields: "title", "text", and "parameters".

        "title" is usually one sentence describing the intent of the figure
        and often plotted bold-face in a figure caption.

        "text" is additional text directly following the title,
        containing more information about the plot.

        "parameters" is a list of parameter names that should be included in
        the figure caption, usually at the very end.
    parameters : :class:`dict`
        All parameters necessary for the plot, implicit and explicit
    label : :class:`str`
        Label the figure should be referred to from within the recipe

        Similar to the :attr:`aspecd.tasks.SingleanalysisTask.result`
        attribute of the :class:`aspecd.tasks.SingleanalysisTask` class.
    filename : :class:`str`
        Name of file to save the plot to

    Raises
    ------
    aspecd.tasks.MissingPlotterError
        Raised if no plotter is provided

    """

    def __init__(self):
        super().__init__()
        self.caption = {
            'title': '',
            'text': '',
            'parameters': []
        }
        self.parameters = dict()
        self.label = ''
        self.filename = ''

    def from_plotter(self, plotter=None):
        """
        Set attributes from plotter

        Usually, a plotter contains all information necessary for an
        :obj:`aspecd.tasks.FigureRecord` object.

        Parameters
        ----------
        plotter : :class:`aspecd.plotting.Plotter`
            Plotter the figure record should be created for.

        Raises
        ------
        aspecd.tasks.MissingPlotterError
            Raised if no plotter is provided

        """
        if not plotter:
            raise aspecd.exceptions.MissingPlotterError
        for attribute in ['caption', 'parameters', 'filename']:
            setattr(self, attribute, getattr(plotter, attribute))


class ChefDeService:
    """
    Wrapper for serving the results of recipes given a recipe file name.

    In recipe-driven data analysis, a recipe of class
    :class:`aspecd.tasks.Recipe` get cooked by a chef of class
    :class:`aspecd.tasks.Chef`. However, this requires to get the
    appropriate dataset factory of class
    :class:`aspecd.dataset.DatasetFactory` or a class inheriting from this one,
    depending on the package actually used.

    However, the (end) user would rather like to not care about those
    details and simply provide a recipe filename (of a YAML file) to an
    instance of a class and get the results back. This is where the
    ``ChefDeService`` comes in.

    Obtaining the results of a recipe will become as simple as::

        chef_de_service = ChefDeService()
        chef_de_service.serve(recipe_filename='my_recipe.yaml')

    Furthermore, the ``ChefDeService`` takes care of persisting the history
    of the cooked recipe in form of a YAML file. Therefore, an additional
    file gets created consisting of the filename of the recipe provided,
    extended by the timestamp of serving the results. These history files
    can be used as recipe again, allowing for full turnover.


    Attributes
    ----------
    recipe_filename : :class:`str`
        Name of the recipe file to serve the cooked results for

    Raises
    ------
    aspecd.tasks.MissingRecipeError
        Raised if no recipe filename is provided upon trying to serve

    """

    def __init__(self):
        self.recipe_filename = ''
        self._history_filename = ''
        self._recipe = aspecd.tasks.Recipe()
        self._chef = aspecd.tasks.Chef()
        self._recipe_dict = None
        self._dataset_factory = aspecd.dataset.DatasetFactory()

    def serve(self, recipe_filename=''):
        """
        Serve the results of cooking a recipe

        All you need to do is to provide the filename of a recipe YAML file.
        Additionally, the history will be served in a YAML file consisting
        of the name of the filename provided as recipe, with the timestamp
        of serving added to it.

        Parameters
        ----------
        recipe_filename : :class:`str`
            Name of the recipe YAML file to cook

        Raises
        ------
        aspecd.tasks.MissingRecipeError
            Raised if no recipe filename is provided upon trying to serve

        """
        if recipe_filename:
            self.recipe_filename = recipe_filename
        if not self.recipe_filename:
            message = "You need to provide a recipe filename."
            raise aspecd.exceptions.MissingRecipeError(message=message)
        self._create_recipe()
        self._cook_recipe()
        self._write_history()
        return self._history_filename

    def _cook_recipe(self):
        self._chef.recipe = self._recipe
        self._chef.cook()

    def _create_recipe(self):
        """
        Create recipe from imported YAML file with correct DatasetFactory.

        Simply loading the recipe using the
        :class:`aspecd.io.RecipeYamlImporter` class does *not* work,
        as we first need to obtain the recipe dict and parse for the
        ``default_package`` key to get the correct DatasetFactory class.
        """
        self._load_recipe_yaml()
        self._get_dataset_factory()
        self._recipe.dataset_factory = self._dataset_factory
        self._recipe.from_dict(self._recipe_dict)

    def _load_recipe_yaml(self):
        """Obtain dict from recipe YAML file."""
        yaml_importer = aspecd.utils.Yaml()
        yaml_importer.read_from(self.recipe_filename)
        yaml_importer.deserialise_numpy_arrays()
        self._recipe_dict = yaml_importer.dict

    def _get_dataset_factory(self):
        """
        Obtain correct DatasetFactory instance depending on default package.

        The default package can be set as key in the recipe. If no such key
        is found, the default :class:`aspecd.dataset.DatasetFactory` class
        is used. Otherwise, an instance of a class with the same name and
        location, but in the package specified in the recipe, is created.
        """
        if "default_package" in self._recipe_dict.keys():
            class_name = self._recipe_dict["default_package"] \
                + '.dataset.DatasetFactory'
            self._dataset_factory = aspecd.utils.object_from_class_name(
                class_name)
        else:
            self._dataset_factory.importer_factory = \
                aspecd.io.DatasetImporterFactory()

    def _write_history(self):
        self._create_history_filename()
        yaml = aspecd.utils.Yaml()
        yaml.dict = self._chef.history
        yaml.serialise_numpy_arrays()
        yaml.write_to(self._history_filename)

    def _create_history_filename(self):
        timestamp = datetime.datetime.now().strftime('%Y%m%dT%H%M%S')
        basename, extension = os.path.splitext(self.recipe_filename)
        self._history_filename = basename + '-' + timestamp + extension


def serve(recipe_filename=''):
    """
    Serve the results of cooking a recipe

    All you need to do is to provide the filename of a recipe YAML file.

    The ASpecD framework creates a console script entry point named "serve"
    that will allow you to even type ``serve <recipe_name.yaml>`` on the
    command line after installing the ASpecD framework.

    Thanks to the modular nature of the ASpecD framework, if your recipe
    contains the ``default_package`` key followed by the name of a package
    based on the ASpecD framework, the correct instance of the
    :class:`aspecd.dataset.DatasetFactory` class will be created
    and added to the recipe automatically, thus allowing you to serve
    recipes that rely on functionality of ASpecD-derived packages for their
    being cooked and served.

    Parameters
    ----------
    recipe_filename : :class:`str`
        Name of the recipe YAML file to cook

    Raises
    ------
    aspecd.exceptions.MissingRecipeError
        Raised if no recipe filename is provided upon trying to serve

    """
    if not recipe_filename:
        if len(sys.argv) < 2:
            message = "You need to specify a recipe to serve."
            raise aspecd.exceptions.MissingRecipeError(message=message)
        recipe_filename = sys.argv[1]
    chef_de_service = ChefDeService()
    chef_de_service.serve(recipe_filename=recipe_filename)
