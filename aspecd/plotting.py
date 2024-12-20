"""
Plotting: Graphical representations of data extracted from datasets.

.. sidebar:: Contents

    .. contents::
        :local:
        :depth: 1


Plotting relies on `matplotlib <https://matplotlib.org/>`_, and mainly its
object-oriented interface should be used for the actual plotting. Each
plotter contains references to the respective figure and axes created usually
by a call similar to::

    fig, ax = matplotlib.pyplot.subplots()

For convenience, short hands for the :attr:`figure` and :attr:`axes`
properties of a plotter are available, named :attr:`fig` and :attr:`ax`,
respectively. For details on handling (own) figure and axes objects, see below.


Overview
========

As there are a lot of different plotters available, each for different
purposes, :numref:`Fig. %s <fig-uml_plotting.plotter-overview_api>` gives a
first overview of the different :class:`Plotter` classes.


.. _fig-uml_plotting.plotter-overview_api:

.. figure:: /uml/aspecd.plotting.Plotter-overview.*
    :align: center

    First overview of the different :class:`Plotter` classes available in
    the :mod:`plotting <aspecd.plotting>` module. The three classes marked
    as abstract (with the "A", *i.e.* :class:`Plotter`,
    :class:`SinglePlotter`, and :class:`MultiPlotter`) are not true abstract
    classes, but nevertheless base classes that shall not used directly for
    plotting purposes.


For each :class:`Plotter` class, there exists a dedicated
:class:`PlotProperties` class, besides further properties classes for those
plot elements independent of a concrete plotter. For a first overview,
see :numref:`Fig. %s <fig-uml_plotting.plotproperties-overview_api>`.


.. _fig-uml_plotting.plotproperties-overview_api:

.. figure:: /uml/aspecd.plotting.PlotProperties-overview.*
    :align: center

    First overview of the different :class:`PlotProperties` classes
    available in the :mod:`plotting <aspecd.plotting>` module. For each
    :class:`Plotter`, there is a separate :class:`PlotProperties` class.
    Furthermore, there are additional classes for properties of elements of
    plots, such as :class:`FigureProperties` and :class:`DrawingProperties`.
    Note that :class:`SinglePlot2DStackedProperties` inherits from
    :class:`MultiPlot1DProperties`. This is due to the very similar
    behaviour of the two plotters, with respect to the resulting plots.


For more explanation and details on the individual classes and how to best
make use of them, continue reading.


Types of abstract plotters
==========================

Abstract plotters are the base classes for all plotters actually used to
graphically display data. If you are mire interested in actually plotting
data rather than the overall concepts, have a look at :ref:`the concrete
plotters <sec:plotting:concrete_plotters>`.

Generally, two types of plotters can be distinguished:

* Plotters for handling single datasets

  Shall be derived from :class:`aspecd.plotting.SinglePlotter`.

* Plotters for handling multiple datasets

  Shall be derived from :class:`aspecd.plotting.MultiPlotter`.

In the first case, the plot is usually handled using the :meth:`plot` method
of the respective :obj:`aspecd.dataset.Dataset` object. Additionally,
those plotters always only operate on the data of a single dataset, and the
plot can easily be attached as a representation to the respective dataset.
Plotters handling single datasets should always inherit from the
:class:`aspecd.plotting.SinglePlotter` class.

In the second case, the plot is handled using the :meth:`plot` method of the
:obj:`aspecd.plotting.Plotter` object, and the datasets are stored as a list
within the plotter. As these plots span several datasets, there is no easy
connection between a single dataset and such a plot in sense of
representations stored in datasets. Plotters handling multiple datasets should
always inherit from the :class:`aspecd.plotting.MultiPlotter` class.

In a certain sense, there is a third type of plotters:

* Plotters consisting of more than one axes

  Shall be derived from :class:`aspecd.plotting.CompositePlotter`.

However, practically mostly these composite plotters will behave like
plotters handling either single or multiple datasets. Generally,
these composite plotters will use other types of plotters to perform the
actual plot tasks. This modular approach allows for great flexibility.

Regardless of the type of plotter, **saving plots** is always done using
objects of the :class:`aspecd.plotting.Saver` class. The actual task of
saving a plot is as easy as calling the :meth:`save` method of a plotter
with a saver object as its argument.


A note on array dimensions and axes
===================================

Something often quite confusing is the apparent inconsistency between the
order of array dimensions and the order of axes. While we are used to assigning
axes in the order *x*, *y*, *z*, and assuming *x* to be horizontal,
*y* vertical (and *z* sticking out of the paper plane), arrays are usually
(at least in the C world as compared to the FORTRAN world) indexed row-first,
column-second. That means, however, that if you simply plot a 2D array in
axes, your *first* dimension is along the *y* axis, the *second* dimension
along the *x* axis.

Therefore, as the axes of your datasets will always correspond to the array
dimensions of your data, in case of 2D plots you will need to *either* use
the information contained in the second axis object for your *x* axis label,
and the information from the first axis object for your *y* axis label,
*or* to transpose the data array.

Another aspect to have in mind is the position of the origin. Usually,
in a Cartesian coordinate system, convention is to have the origin (0,
0) in the *lower left* of the axes (for the positive quadrant). However,
for images, convention is to have the corresponding (0, 0) pixel located in
the *upper left* edge of your image. Therefore, those plotting methods
dealing with images will usually *revert* the direction of your *y* axis.
Most probably, eventually you will have to check with real data and ensure
the plotters to plot data and axes in a consistent fashion.


.. _sec:plotting:concrete_plotters:

Types of concrete plotters
==========================

The ASpecD framework comes with a series of concrete plotters included ready
to be used. As stated above, plotters can generally be divided into two
types: plotters operating on single datasets and plotters combining the data
of multiple datasets into a single figure.

Additionally, plotters can be categorised with regard to creating figures
consisting of a single or multiple axes. The latter are plotters inheriting
from the :class:`aspecd.plotting.CompositePlotter` class. The latter can be
thought of as templates for the other plotters to operate on, *i.e.* they
provide the axes for other plotters to display their results.


Concrete plotters for single datasets
-------------------------------------

* :class:`aspecd.plotting.SinglePlotter1D`

  Basic line plots for single datasets, allowing to plot a series of
  line-type plots, including (semi)log plots

* :class:`aspecd.plotting.SinglePlotter2D`

  Basic 2D plots for single datasets, allowing to plot a series of 2D plots,
  including contour plots and image-type display

* :class:`aspecd.plotting.SinglePlotter2DStacked`

  Stacked plots of 2D data, converting a 2D display into a series of 1D line
  plots stacked on top of each other.

* :class:`aspecd.plotting.SingleCompositePlotter`

  Composite plotter for single datasets, allowing to plot different views of
  one and the same datasets by using existing plotters for single datasets.

* :class:`aspecd.plotting.MultiDeviceDataPlotter1D`

  Basic line plots for multiple device data of a single dataset, allowing to
  plot a series of line-type plots, including (semi)log plots


Concrete plotters for multiple datasets
---------------------------------------

* :class:`aspecd.plotting.MultiPlotter1D`

  Basic line plots for multiple datasets, allowing to plot a series of
  line-type plots, including (semi)log plots

* :class:`aspecd.plotting.MultiPlotter1DStacked`

  Stacked line plots for multiple datasets, allowing to plot a series of
  line-type plots, including (semi)log plots


Properties of plot(ter)s
========================

Plots can be controlled extensively regarding their appearance. While
Matplotlib provides both, sensible defaults and an extensive list of
customisation options for the plot appearance, the ASpecD framework tries
to homogenise these settings and currently provides only a subset of the
possibilities the underlying Matplotlib library would allow.

The properties of plots and their individual components are reflected in a
hierarchy of objects. Each plotter has a corresponding :attr:`properties`
attribute that contains an object of the respective
:class:`aspecd.plotting.PlotProperties` class.

To give you an idea of the hierarchy of classes handling the plot
properties, below is a (hopefully complete) list:

  * :class:`aspecd.plotting.PlotProperties`

    * :class:`aspecd.plotting.SinglePlotProperties`

      * :class:`aspecd.plotting.SinglePlot1DProperties`
      * :class:`aspecd.plotting.SinglePlot2DProperties`

    * :class:`aspecd.plotting.MultiPlotProperties`

      * :class:`aspecd.plotting.MultiPlot1DProperties`

        * :class:`aspecd.plotting.SinglePlot2DStackedProperties`

    * :class:`aspecd.plotting.CompositePlotProperties`

  * :class:`aspecd.plotting.FigureProperties`

  * :class:`aspecd.plotting.AxesProperties`

  * :class:`aspecd.plotting.LegendProperties`

  * :class:`aspecd.plotting.DrawingProperties`

    * :class:`aspecd.plotting.LineProperties`
    * :class:`aspecd.plotting.SurfaceProperties`
    * :class:`aspecd.plotting.TextProperties`

  * :class:`aspecd.plotting.GridProperties`

  * :class:`aspecd.plotting.ColorbarProperties`

  * :class:`aspecd.plotting.SubplotGridSpecs`

Each of the plot properties classes, *i.e.* all subclasses of
:class:`aspecd.plotting.PlotProperties`, contain other properties classes as
attributes.

Getting and setting plot properties is somewhat complicated by the fact
that Matplotlib usually allows setting properties only when instantiating
objects, or sometimes with explicit setter methods. Similarly, there may
or may not be getter methods for the relevant attributes.

In any case, while you can set and get properties of plots
programmatically within the ASpecD framework, using :doc:`recipe-driven data
analysis <../recipes>` is highly recommended.


.. _sec:plotting:tips_tricks:

General tips and tricks
=======================

Plotting can become horribly complicated, simply due to the complexity of
the matter involved and the parameters one can (and often want to) control.
For the convenience of the user, a few more general cases are discussed
below and example recipes provided for each case. For details on
recipe-driven data analysis, see either the :doc:`introduction </recipes>`
or the documentation of the :mod:`aspecd.tasks` module.


Overall figure properties
-------------------------

On the figure level, *i.e.* the level of the overall graphical
representation, only a few properties can be set, namely size (in inches),
resolution (in dots per inch), and title:


.. code-block:: yaml

    - kind: singleplot
      type: SinglePlotter1D
      properties:
        properties:
          figure:
            size: [8, 5]
            resolution: 600
            title: My fancy figure
        filename: output.pdf


.. important::

    If you have a second axis on top of the axes, setting the figure title
    will result in the figure title clashing with the upper axis. Hence,
    in such case, try setting the axis title.



Overall axes properties
-----------------------

Axes properties can be set for :class:`SinglePlotter` and
:class:`MultiPlotter`, but for obvious reasons not for
:class:`CompositePlotter`. In case of the latter, the properties of the axes
are set for the individual plotters that are used to plot in the different
axes.

Below is a demonstration of just a subset of the properties that can be set.
For further details, see the :class:`AxesProperties` class. Note in
particular that all the settings shown here for the *x* axis can be applied to
the *y* axis analogously.


.. code-block:: yaml

    - kind: singleplot
      type: SinglePlotter1D
      properties:
        properties:
          axes:
            title: My fancy plot
            aspect: equal
            facecolor: darkgreen
            xlabel: $foo$ / bar
            xlim: [-5, 5]
            xticklabelangle: 45
            invert: x
        filename: output.pdf


.. important::

    If you have a second axis on top of the axes, setting the figure title
    will result in the figure title clashing with the upper axis. Hence,
    in such case, try setting the axis title.


Removing axes labels
--------------------

Generally, axes labels are set according to the settings in the dataset
plotted. However, sometimes you would like to remove a label entirely. To
do so, set the label to ``None``. The equivalent in YAML, hence in
recipes, is ``null``. Hence, removing the *y* axis label in a plot
translates to:


.. code-block:: yaml

    - kind: singleplot
      type: SinglePlotter1D
      properties:
        properties:
          axes:
            ylabel: null


Of course, you can do the same with the *x* axis label and with all kinds
of plotters.

.. versionadded:: 0.9.3


Type of plot for 1D plotters
----------------------------

When plotting one-dimensional (1D) data, there is of course more than the
usual line plot. For the actual types of plots that you can use, see the
:attr:`SinglePlotter1D.allowed_types` and :attr:`MultiPlotter1D.allowed_types`
attributes.

To make a semilogy plot (*i.e.*, with logarithmic *y* axis), invoke the
plotter as follows:

.. code-block:: yaml

    - kind: singleplot
      type: SinglePlotter1D
      properties:
        type: semilogy
        filename: output.pdf

And analogous for the MultiPlot1D plotter:

.. code-block:: yaml

    - kind: multiplot
      type: MultiPlotter1D
      properties:
        type: semilogy
        filename: output.pdf


.. important::

    As the logarithm of negative values is not defined, usually having a
    logarithmic axis with negative values will lead to unexpected
    results. Matplotlib defaults to clipping the invalid values. To help
    you with debugging the unexpected results, a warning will be logged
    (and printed to the terminal when serving a recipe) in case a
    logarithmic axis is affected by negative values. In such case,
    the easiest is to add an offset to your data, using
    :class:`aspecd.processing.ScalarAlgebra`.


Appearance of individual drawings
---------------------------------

The individual drawings within the axes of a plot can be controlled in quite
some detail. Depending on the overall type, be it a line or a surface,
there are different classes responsible for setting the properties:
:class:`LineProperties` and :class:`SurfaceProperties`. The general class is
:class:`DrawingProperties`.

Below is a (real-world) example of a multiplotter containing two lines,
and in this particular case with standard settings.

.. code-block:: yaml

    - kind: multiplot
      type: MultiPlotter1D
      properties:
        properties:
          drawings:
          - label: Substance 1
            color: '#1f77b4'
            drawstyle: default
            linestyle: '-'
            linewidth: 1.5
            marker: None
          - label: Substance 2
            color: '#ff7f0e'
            drawstyle: default
            linestyle: '-'
            linewidth: 1.5
            marker: None


Controlling the appearance of zero lines
----------------------------------------

While a grid is not shown by default, zero lines are, as long as the zero
value is present in either or both axes ranges. While it is a sensible
default to display zero lines, and switching them off is a matter of
setting the parameter ``show_zero_lines`` to ``False``, controlling the
appearance of these lines is often useful. Below is a (real-world) example
of the available settings for the zero lines (with default values).

.. code-block:: yaml

    - kind: multiplot
      type: MultiPlotter1D
      properties:
        parameters:
          show_zero_lines: true
        properties:
          zero_lines:
            label: ''
            color: '#cccccc'
            drawstyle: default
            linestyle: solid
            linewidth: 1.0
            marker: ''


While it rarely makes sense to set line markers for these lines, the line
properties are simply all properties that can be set using the
:class:`LineProperties` class. Besides controlling the appearance of zero
lines, you can display a grid and control the appearance of these lines.
See below for more details.


Adding a grid
-------------

Particularly when comparing plots or when you want to extract values from a
plot, a grid can come in quite handy. As a grid is already quite complicated
-- for which axis (*x*, *y*, or both) to set the grid, for which ticks (minor,
major, or both) -- and as you may even want to control the appearance of the
grid lines, all these properties are handled by the :class:`GridProperties`
class. You can add a grid to both, :class:`SinglePlotter` and
:class:`MultiPlotter` instances.

.. code-block:: yaml

    - kind: singleplot
      type: SinglePlotter1D
      properties:
        properties:
          grid:
            show: True
            ticks: major
            axis: both

If you now even want to control the appearance of the grid lines (you can
not, however, control individual grid lines, only all grid lines at once),
things get even more complex:

.. code-block:: yaml

    - kind: singleplot
      type: SinglePlotter1D
      properties:
        properties:
          grid:
            show: True
            ticks: major
            axis: both
            lines:
              color: #123456
              linestyle: dashed
              linewidth: 3
              marker: triangle_up

Note that the values for the lines are not necessarily sensible for grid
lines. For a full list of possible properties, see the
:class:`LineProperties` class. The same as shown here for a
:class:`SinglePlotter` can be done for a :class:`MultiPlotter` accordingly.


Adding a legend
---------------

As soon as there is more than one line in a plot, adding a legend comes in
quite handy. Again, a legend can be controlled in quite some detail. An
example showing some of the properties that can be set is given below:


.. code-block:: yaml

    - kind: multiplot
      type: MultiPlotter1D
      properties:
        parameters:
          show_legend: True
        properties:
          legend:
            location: upper right
            frameon: False
            labelspacing: 0.75
            fontsize: small
            ncol: 2
            title: some explanation


Important here is to note that you need to set the ``show_legend`` parameter
on a higher level of the overall plotter properties to ``True`` in order to
have a legend be shown. Of course, you need not set all (or even any) of the
properties explicitly. For details, see the :class:`LegendProperties` class.


Removing a line from the legend
-------------------------------

Sometimes, you may want to have certain lines in your plot not showing up in
the legend. By default, all lines ("drawings") will enter the legend, either
by the explicit label you provide or by the label of the corresponding
dataset. To have a line not showing up in the legend, set its label to
either the empty string or to ``null`` (the YAML equivalent of :obj:`None`).
A minimal example is given below:


.. code-block:: yaml

    - kind: multiplot
      type: MultiPlotter1D
      properties:
        parameters:
          show_legend: True
        properties:
          drawings:
          - label: "one line"
          - label: ""
          - label: "another line"


Here, there should be three lines in the plot, and the second would not
appear in the legend, as its label is set to the empty string.


Annotating plots
----------------

Annotations of plots are something that cannot be automated. However,
they can be quite important for the analysis and hence for providing new
scientific insight. Typical simple examples of plot annotations are
horizontal or vertical lines to compare peak positions or intensities. You
may as well think of highlighted areas or symbols pointing to distinct
characteristics.

When annotating plots, for obvious reasons you need to have both, a plot task
and a plotannotation task. It does not really matter which task you define
first, the plot or the plot annotation. There are only marginal
differences, and both ways are shown below.

.. code-block:: yaml

    - kind: multiplot
      type: MultiPlotter1DStacked
      properties:
        filename: plot1Dstacked.pdf
      result: plot1Dstacked

    - kind: plotannotation
      type: VerticalLine
      properties:
        parameters:
          positions: [35, 42]
        properties:
          color: green
          linewidth: 1
          linestyle: dotted
      plotter: plot1Dstacked


In this case, the plotter is defined first, and the annotation second.
To refer to the plotter from within the plotannotation task, you need to
set the ``result`` attribute in the plotting task and refer to it within
the ``plotter`` attribute of the plotannotation task. Although defining
the plotter before the annotation, the user still expects the annotation
to be included in the file containing the actual plot, despite the fact
that the figure has been saved (for the first time) before the
annotation has been added.

Sometimes, it might be convenient to go the other way round and first
define an annotation and afterwards add it to a plot(ter). This can be
done as well:

.. code-block:: yaml

    - kind: plotannotation
      type: VerticalLine
      properties:
        parameters:
          positions:
            - 21
            - 42
        properties:
          color: green
          linewidth: 1
          linestyle: dotted
      result: vlines

    - kind: multiplot
      type: MultiPlotter1DStacked
      properties:
        filename: plot1Dstacked.pdf
      annotations:
        - vlines


In this way, you can add the same annotation to several plots,
and be sure that each annotation is handled as a separate object.

Suppose you have more than one plotter you want to apply an annotation
to. In this case, the ``plotter`` property of the plotannotation task is
a list rather than a string:

.. code-block:: yaml

    - kind: multiplot
      type: MultiPlotter1DStacked
      result: plot1

    - kind: multiplot
      type: MultiPlotter1DStacked
      result: plot2

    - kind: plotannotation
      type: VerticalLine
      properties:
        parameters:
          positions: [35, 42]
      plotter:
        - plot1
        - plot2

In this case, the annotation will be applied to both plots
independently. Note that the example has been reduced to the key
aspects. In a real situation, the two plotters will differ much more.


Adding a colorbar
-----------------

For two-dimensional (2D) plots, adding a colorbar that provides some
information on the intensity values encoded in different colors is usually a
good idea. The properties of the colorbar can be set via the
:class:`ColorbarProperties` class.


.. code-block:: yaml

    - kind: singleplot
      type: SinglePlotter2D
      properties:
        parameters:
          show_colorbar: True
        properties:
          colorbar:
            location: top
            fraction: 0.1
            aspect: 30
            pad: 0.2
            format: "%4.2e"
            label:
              text: $intensity$ / a.u.
              location: right


Again, you need not to set any of the properties explicitly, besides setting
the parameter ``show_colorbar`` to ``True``. If none of the properties are
set explicitly, the defaults provided by Matplotlib will be used.


Plotting device data rather than primary data
---------------------------------------------

Datasets may contain additional data as device data in
:attr:`aspecd.dataset.Dataset.device_data`. For details,
see the :ref:`section on device data in the dataset module
<sec:dataset:device_data>`. To conveniently plot those device data instead
of the primary data of the dataset, provide the key(s) to the device(s) the
data should be plotted for:


.. code-block:: yaml

    - kind: singleplot
      type: SinglePlotter1D
      properties:
        parameters:
          device_data: timestamp
        filename: output.pdf


Basically, all plotters understand device data and will plot the device data
rather than the primary data of the dataset accordingly.


Plotting to existing axes
=========================

Figure and axes properties of a plotter object will only be populated upon
calling the method :meth:`aspecd.plotting.Plotter.plot`, therefore by using
the :meth:`plot` method of the respective plotter class.

Furthermore, figure and axes properties will only be populated if both are not
existing already. Therefore, if you like to use a plotter to plot to an
existing axis, set its figure and axes properties before calling  the
:meth:`aspecd.plotting.Plotter.plot` method.

.. important::
    If you do so, make sure to set *both*, figure and axes properties,
    as failing to set a valid figure property will cause matplotlib to throw
    exceptions.


A simple example may look like this::

    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    plotter = aspecd.plotting.SinglePlotter1D()
    plotter.figure = fig
    plotter.axes = ax
    plotter.plot()

In this case, the plotter will plot to the axis specified before calling its
:meth:`plot` method. Thus, it should be straight-forward to write plotter
classes that create complex plots consisting of several subplots by reusing
available plotter classes. This is what the
:class:`aspecd.plotting.CompositePlotter` class is for, and how it basically
works.


For developers
==============

A bit of conceptual documentation for both, developers of the ASpecD
framework and derived packages, including general hints how to implement
plotters.


When and how to subclass plotters
---------------------------------

ASpecD comes with a list and hierarchy of plotters. For details, see the
:ref:`section on types of concrete plotters
<sec:plotting:concrete_plotters>`. The question therefore arises: when and
how to subclass plotters, particularly in derived packages?

Generally, you nearly always want to subclass directly one of the concrete
plotters, such as :class:`SinglePlotter1D` or :class:`MultiPlotter1D`,
but rarely if ever parent classes such as :class:`SinglePlotter` or even
:class:`Plotter`. The reason is simply that only the concrete plotters can
be used directly.

Reasons for subclassing plotters in derived packages are:

* Adding new kinds of (specific) plotters,
* Adding functionality to otherwise generic plotters,
* Change certain functionality to otherwise generic plotters.

A typical use case for the last case would be to revert the *x* axis by
default, perhaps depending on the axis unit. For this, you would
probably want to subclass all relevant concrete ASpecD plotter, *i.e.*
:class:`SinglePlotter1D`, :class:`SinglePlotter2D`,
:class:`SinglePlotter2DStacked`, :class:`MultiPlotter1D`,
and :class:`MultiPlotter1DStacked`. For each of these, there would only be
a few relevant lines of code, and as this would look fairly similar for each
of the plotters, the following stripped-down example shows just the case
for the :class:`SinglePlotter1D`:

.. code-block::

    class SinglePlotter1D(aspecd.plotting.SinglePlotter1D):

        def _create_plot(self):
            super()._create_plot()
            if self.data.axes[0].unit == "<Some Unit>":
                self.properties.axes.invert = ["x"]


Here, the unit of the *x* axis is checked and if it is set to a certain
value (replace the placeholder ``<Some Unit>`` with a reasonable value in
your code), the *x* axis is inverted. This is all functional code
necessary to achieve the requested behaviour. In a real class, you would
need to add a proper class docstring including examples how to use the
class. Get inspiration from either the ASpecD framework itself or one of
the derived packages.


.. _sec:plotting:developers_data:

Access to data for plotting
---------------------------

Datasets may contain additional data as device data in
:attr:`aspecd.dataset.Dataset.device_data`. For details, see the
:ref:`section on device data in the dataset module
<sec:dataset:device_data>`. When implementing a plotter, you should not
need to care about whether device data or data should be plotted. For this
to work, do *not* access :attr:`aspecd.dataset.Dataset.data` directly
in your plotter, but use instead :attr:`aspecd.plotting.SinglePlotter.data`
or :attr:`aspecd.plotting.MultiPlotter.data`, respectively.


.. important::
    Support for device data has been added in ASpecD v0.9. Developers of
    packages based on the ASpecD framework should update their code
    accordingly.


In a simplistic scenario, your plotter (here, a class derived from
:class:`SinglePlotter`) may contain the following code:

.. code-block::

    def _create_plot(self):
        self.drawing, = self.axes.plot(
            self.data.axes[0].values,
            self.data.data,
            label=self.properties.drawing.label
        )


A few comments on this code snippet:

* All actual plotting is implemented in the private method
  ``_create_plot()``.

* The actual object returned by the plot function is stored in
  ``self.drawing``.

* The actual plot function gets the data to be plotted by accessing 
  ``self.data`` (and *not* ``self.dataset.data``).

Of course, usually there is more that is handled in a plotter. For
details, have a look at the actual source code of different ASpecD plotters.


Module API documentation
========================

"""

import copy
import errno
import hashlib
import logging
import os

import matplotlib as mpl
import matplotlib.pyplot as plt

# pylint: disable=unused-import
import matplotlib.collections
from matplotlib import ticker
import numpy as np

import aspecd.dataset
import aspecd.exceptions
import aspecd.history
import aspecd.utils


logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class Plotter(aspecd.utils.ToDictMixin):
    """Base class for plots.

    Each class actually plotting data should inherit from this class.
    Furthermore, all parameters, implicit and explicit, necessary to
    perform the plot, should eventually be stored in the property
    :attr:`parameters` (currently a dictionary).

    Further things that need to be changed upon inheriting from this class
    are the string stored in :attr:`description`, being basically a one-liner.

    The actual implementation of the plotting is done in the private method
    :meth:`_create_plot` that in turn gets called by :meth:`plot`.

    .. note::
        Usually, you will never implement an instance of this class for
        actual plotting tasks, but rather one of the child classes.


    Attributes
    ----------
    name : :class:`str`
        Name of the plotter.

        Defaults always to the full class name, don't change!

    parameters : :class:`dict`
        All parameters necessary for the plot, implicit and explicit

        The following keys exist:

        show_legend : :class:`bool`
            Whether to show a legend in the plot

            Default: False

        show_zero_lines : :class:`bool`
            Whether to show zero lines in the plot

            Regardless of whether you set this to true, zero lines will only be
            added to the final plot if the zero value is within the current
            axes limits.

            Zero line properties can be set via the
            :attr:`aspecd.plotting.Plotter.properties` attribute.

            Default: True

        tight_layout : :class:`bool`
            Whether to adjust the plot to fit into the figure area

            For details see :meth:`matplotlib.figure.Figure.tight_layout`.

            Use with care, as this will automatically adjust the padding
            around the axes and might lead to unexpected results.

            Default: False

        device_data : :class:`str` or :class:`list`
            Name(s) of the device(s) the data should be plotted for.

            Datasets may contain additional data as device data in
            :attr:`aspecd.dataset.Dataset.device_data`. For details,
            see :class:`aspecd.dataset.DeviceData`. To conveniently plot
            those device data instead of the primary data of the dataset,
            provide the key(s) to the device(s) the data should be plotted
            for.

            Will be a string (*i.e.* data of a single device) in all cases
            except of specific plotters for plotting data of multiple
            devices.

            Default: ''

    properties : :class:`aspecd.plotting.PlotProperties`
        Properties of the plot, defining its appearance

    description : :class:`str`
        Short description, to be set in class definition

    filename : :class:`str`
        Name of file to save the plot to

        Actual saving is done using an :obj:`aspecd.plotting.Saver` object.

    caption : :class:`aspecd.plotting.Caption`
        User-supplied information for the figure.

    legend : :class:`matplotlib.legend.Legend`
        Legend object

    label : :class:`str`
        Label used to reference figure, *e.g.* in context of a report

    style : :class:`str`
        plotting style to use

        You can use all plotting styles understood by matplotlib. See
        :mod:`matplotlib.style` for details.

        Note that the style will only be applied for the current plot and
        reset to the values before the plot, at least as long as applying
        the style (only) affects the rcParams of matplotlib.

    comment : :class:`str`
        User-supplied comment describing intent, purpose, reason, ...

    annotations : :class:`list`
        List of annotations added to the plotter.

        Each annotation is an object of class
        :class:`aspecd.annotation.PlotAnnotation`.


    Raises
    ------
    aspecd.exceptions.MissingSaverError
        Raised when no saver is provided when trying to save


    .. versionchanged:: 0.6
        New attribute :attr:`label`

    .. versionchanged:: 0.6.2
        New parameter ``tight_layout``

    .. versionchanged:: 0.6.4
        New attribute :attr:`comment`

    .. versionchanged:: 0.9
        New parameter ''device_data''

    """

    def __init__(self):
        # Name defaults always to the full class name, don't change!
        self.name = aspecd.utils.full_class_name(self)
        self.parameters = {
            "show_legend": False,
            "show_zero_lines": True,
            "tight_layout": False,
            "device_data": "",
        }
        self.properties = PlotProperties()
        self.description = "Abstract plotting step"
        self._figure = None
        self._axes = None
        self.filename = ""
        self.caption = Caption()
        self.legend = None
        self.label = ""
        self.style = ""
        self.comment = ""
        self.annotations = []
        super().__init__()
        #
        self._original_rcparams = None
        self._exclude_from_to_dict = [
            "name",
            "description",
            "figure",
            "axes",
            "legend",
        ]
        self._figure_set_externally = False
        self._axes_set_externally = False

    @property
    def figure(self):
        """
        Reference to figure object.

        Returns
        -------
        figure : :class:`matplotlib.figure.Figure`
            Reference to figure object

        """
        return self._figure

    @figure.setter
    def figure(self, figure=None):
        self._figure_set_externally = True
        self._figure = figure

    @property
    def fig(self):
        """
        Shorthand for :attr:`figure`.

        Returns
        -------
        figure : :class:`matplotlib.figure.Figure`
            Reference to figure object

        """
        return self._figure

    @property
    def axes(self):
        """
        Reference to axes object used for actual plotting.

        Returns
        -------
        axes : :class:`matplotlib.axes.Axes`
            Reference to axes object used for actual plotting

        """
        return self._axes

    @axes.setter
    def axes(self, axes=None):
        self._axes_set_externally = True
        self._axes = axes

    @property
    def ax(self):  # pylint: disable=invalid-name
        """
        Shorthand for :attr:`axes`.

        Returns
        -------
        axes : :class:`matplotlib.axes.Axes`
            Reference to axes object used for actual plotting

        """
        return self._axes

    def plot(self):
        """Perform the actual plotting.

        The actual plotting should be implemented within the private
        method :meth:`_create_plot`.

        """
        self._set_style()
        self._create_figure_and_axes()
        self._apply_figure_properties()
        self._apply_axes_properties()
        self._create_plot()
        self._add_annotations()
        self.properties.apply(plotter=self)
        self._set_legend()
        self._add_zero_lines()
        self._tight_layout()
        self._reset_style()

    # noinspection PyUnusedLocal
    @staticmethod
    def applicable(data):  # pylint: disable=unused-argument
        """Check whether plot is applicable to the dataset.

        Returns `True` by default and needs to be implemented in classes
        inheriting from Plotter according to their needs.

        A typical example would be a 2D plot applied to a 1D dataset that will
        most probably not be possible/sensible.

        Returns
        -------
        applicable : :class:`bool`
            `True` if successful, `False` otherwise.

        """
        return True

    def annotate(self, annotation=None):
        """Add annotation to dataset.

        Parameters
        ----------
        annotation : :obj:`aspecd.annotation.PlotAnnotation`
            Annotation to add to the plotter

        Returns
        -------
        annotation : :class:`aspecd.annotation.PlotAnnotation`
            Annotation added to the plot(ter)

        """
        annotation = copy.copy(annotation)
        annotation.annotate(self, from_plotter=True)
        self.annotations.append(annotation)
        return annotation

    def delete_annotation(self, index=None):
        """Remove annotation record from dataset.

        Parameters
        ----------
        index : `int`
            Number of analysis in analyses to delete

        """
        del self.annotations[index]

    def _set_style(self):
        self._original_rcparams = mpl.rcParams.copy()
        if self.style:
            if self.style not in plt.style.available + ["default", "xkcd"]:
                message = f'Cannot find matplotlib style "{self.style}".'
                raise aspecd.exceptions.StyleNotFoundError(message=message)
            if self.style == "xkcd":
                self._set_xkcd_style()
            else:
                plt.style.use(self.style)

    def _reset_style(self):
        dict.update(mpl.rcParams, self._original_rcparams)

    @staticmethod
    def _set_xkcd_style():
        """
        Set plot style similar to XKCD web comics.

        The code below is taken from the official matplotlib.pyplot module
        and slightly adapted. The reason for not using the original code
        is that it is only available from the pyplot submodule.

        Original source:

        https://matplotlib.org/stable/_modules/matplotlib/pyplot.html#xkcd

        """
        from matplotlib import patheffects  # noqa

        mpl.rcParams.update(
            {
                "font.family": [
                    "xkcd",
                    "xkcd Script",
                    "Humor Sans",
                    "Comic Neue",
                    "Comic Sans MS",
                ],
                "font.size": 14.0,
                "path.sketch": (1, 100, 2),  # (scale, length, randomness),
                "path.effects": [
                    patheffects.withStroke(linewidth=4, foreground="w")
                ],
                "axes.linewidth": 1.5,
                "lines.linewidth": 2.0,
                "figure.facecolor": "white",
                "grid.linewidth": 0.0,
                "axes.grid": False,
                "axes.unicode_minus": False,
                "axes.edgecolor": "black",
                "xtick.major.size": 8,
                "xtick.major.width": 3,
                "ytick.major.size": 8,
                "ytick.major.width": 3,
                "text.usetex": False,
            }
        )

    def _create_figure_and_axes(self):
        """Create figure and axes and assign to attributes.

        Figure and axes will only be created upon calling the method
        :meth:`plot`. If you need to change the way figure and axes are
        created, override this method.

        .. note::
            Figure and axes will only be created if both are not existing
            already. Therefore, if you like to use a plotter to plot to an
            existing axis, set its figure and axes properties before calling
            the :meth:`plot` method.

            If you do so, make sure to set *both*, figure and axes
            properties, as failing to set a valid figure property will cause
            matplotlib to throw exceptions.


        In any case, figure and axes need to be assigned to the
        :attr:`figure` and :attr:`axes` properties of the plotter class.
        """
        if not self.figure and not self.axes:
            mpl.interactive(
                False
            )  # Mac OS X: prevent plot window from opening
            self._figure, self._axes = plt.subplots()

    def _apply_figure_properties(self):
        """
        Apply the properties of the figure.

        While generally, all properties are applied calling out to
        :meth:`PlotProperties.apply` in the :meth:`plot` method, having the
        figure properties applied early on, *i.e.* **before the actual
        plotting**, is sometimes crucial, particularly if the plotting
        itself relies on the actual figure size.

        """
        if not self._figure_set_externally:
            self.properties.figure.apply(figure=self.figure)

    def _apply_axes_properties(self):
        """
        Apply the properties of the axes.

        While generally, all properties are applied calling out to
        :meth:`PlotProperties.apply` in the :meth:`plot` method, having the
        axes properties applied early on, *i.e.* **before the actual
        plotting**, is sometimes crucial, particularly if the plotting
        itself relies on the actual axes limits.

        """
        if not self._axes_set_externally:
            self.properties.axes.apply(axes=self.axes)

    def _create_plot(self):
        """Perform the actual plotting of the data of the dataset(s).

        The implementation of the actual plotting goes in here in all
        classes inheriting from Plotter. This method is automatically
        called by :meth:`plot` after some background checks.

        The reference to the figure object is stored in :attr:`figure`. By
        default, the backend is set to non-interactive, and to actually
        display the figure, you would need to call :meth:`show` on the
        figure object stored in :attr:`figure`.

        Plotting should be done using a method of the
        :class:`matplotlib.axes.Axes` class accessible via the :attr:`axes`
        attribute of the plotter.

        """

    def _add_annotations(self):
        for annotation in self.annotations:
            annotation.annotate(self, from_plotter=True)

    def save(self, saver=None):
        """Save the plot to a file.

        The actual saving is postponed to an object of class
        :class:`aspecd.plotting.Saver` that is submitted as parameter.

        Parameters
        ----------
        saver : `aspecd.plotting.Saver`
            Saver handling the actual saving of the plot

        Returns
        -------
        saver : `aspecd.plotting.Saver`
            Saver used to save the plot

        Raises
        ------
        aspecd.exceptions.MissingSaverError
            Raised if no Saver is provided as parameter.

        """
        if not saver:
            raise aspecd.exceptions.MissingSaverError
        saver.save(self)
        self.filename = saver.filename
        return saver

    # @staticmethod
    def _create_axis_label_string(self, axis):
        """Create axis label conforming to conventions used in science

        Here, the quantity is set in italics, and the unit in upright font,
        with a slash separating both, quantity and unit. In case the
        quantity contains spaces, these will be escaped thus that they are
        contained in the final string (using the math mode of matplotlib).

        .. note::
            It might be worth discussing whether a proper axis label
            conforming to scientific conventions sets the symbol in italics,
            but not the quantity (name) as such. Therefore, a full label might
            look like this: "magnetic field, B_0 / mT" with the term
            "magnetic field" set in upright font, and only the symbol,
            here $B_0$, in italics. For this, a property for the symbol has
            been added to the axis class.


        This method is called automatically and indirectly by :meth:`plot`.

        If you ever need to change the appearance of your axes labels,
        override this method in a child class.

        Returns
        -------
        label: :class:`str`
            label for the axis

        """
        label = ""
        if axis.quantity:
            if self.style == "xkcd":
                label = axis.quantity
            else:
                label = "$" + axis.quantity.replace(" ", "\\ ") + "$"
            if axis.unit:
                label += " / " + axis.unit
        return label

    def _set_legend(self):
        if self.parameters["show_legend"]:
            # noinspection PyArgumentList
            self.legend = self.axes.legend(**self.properties.legend.to_dict())

    def _add_zero_lines(self):
        if self.parameters["show_zero_lines"]:
            if isinstance(self.axes, list):
                for axes in self.axes:
                    if axes.get_ylim()[0] <= 0 <= axes.get_ylim()[1]:
                        properties = self.properties.zero_lines.to_dict()
                        # noinspection PyUnresolvedReferences
                        properties.update({"zorder": 1})
                        # noinspection PyArgumentList
                        axes.axhline(**properties)
                    if axes.get_xlim()[0] <= 0 <= axes.get_xlim()[1]:
                        properties = self.properties.zero_lines.to_dict()
                        # noinspection PyUnresolvedReferences
                        properties.update({"zorder": 1})
                        # noinspection PyArgumentList
                        axes.axvline(**properties)
            else:
                if self.axes.get_ylim()[0] <= 0 <= self.axes.get_ylim()[1]:
                    properties = self.properties.zero_lines.to_dict()
                    # noinspection PyUnresolvedReferences
                    properties.update({"zorder": 1})
                    # noinspection PyArgumentList
                    self.axes.axhline(**properties)
                if self.axes.get_xlim()[0] <= 0 <= self.axes.get_xlim()[1]:
                    properties = self.properties.zero_lines.to_dict()
                    # noinspection PyUnresolvedReferences
                    properties.update({"zorder": 1})
                    # noinspection PyArgumentList
                    self.axes.axvline(**properties)

    def _tight_layout(self):
        if self.parameters["tight_layout"]:
            self.figure.set_layout_engine(layout="tight")


class SinglePlotter(Plotter):
    """Base class for plots of single datasets.

    Each class actually plotting data of a dataset should inherit from this
    class. Furthermore, all parameters, implicit and explicit, necessary to
    perform the plot, should eventually be stored in the property
    :attr:`parameters` (currently a dictionary).

    There are two concrete classes available for conveniently performing
    plots of single datasets:

    * :class:`aspecd.plotting.SinglePlotter1D`

      1D plots, such as line, scatter, log, semilog

    * :class:`aspecd.plotting.SinglePlotter2D`

      2D plots, such as contour, image

    To perform the plot, call the :meth:`plot` method of the dataset the plot
    should be performed for, and provide a reference to the actual plotter
    object to it.

    Further things that need to be changed upon inheriting from this class
    are the string stored in :attr:`description`, being basically a one-liner.

    The actual implementation of the plotting is done in the private method
    :meth:`_create_plot` that in turn gets called by :meth:`plot`
    which is called by the :meth:`aspecd.dataset.Dataset.plot` method of the
    dataset object.

    Attributes
    ----------
    properties : :class:`aspecd.plotting.SinglePlotProperties`
        Properties of the plot, defining its appearance

    dataset : :class:`aspecd.dataset.Dataset`
        Dataset the plotting should be done for

    data : :class:`aspecd.dataset.Data`
        Actual data that should be plotted

        Defaults to the primary data of a dataset, but can be the device
        data. See the key ``device_data`` of :attr:`Plotter.parameters` for
        details.

    drawing : :class:`matplotlib.artist.Artist`
        Actual graphical representation of the data


    Raises
    ------
    aspecd.exceptions.MissingDatasetError
        Raised when no dataset exists to act on

    aspecd.exceptions.NotApplicableToDatasetError
        Raised when plotter is not applicable to dataset


    .. versionchanged:: 0.9
        New attribute ''data''

    """

    def __init__(self):
        super().__init__()
        self.properties = SinglePlotProperties()
        self.dataset = None
        self.data = None
        self.drawing = None
        self.description = "Abstract plotting step for single dataset"
        self.__kind__ = "singleplot"
        self._exclude_from_to_dict.extend(["dataset", "data", "drawing"])

    def plot(self, dataset=None, from_dataset=False):
        """Perform the actual plotting on the given dataset.

        If no dataset is set as property in the object, the method will
        raise a respective exception. The Dataset object :meth:`plot` method
        always assigns its dataset as the respective dataset attribute of
        the plotter class.

        The actual plotting should be implemented within the non-public
        method :meth:`_create_plot`. Besides that, the applicability of the
        plotting to the given dataset will be checked automatically. These
        checks should be implemented in the method :meth:`applicable`.

        Note that the axis labels are added automatically. If you ever need
        to change the handling or appearance of your axis labels, you may
        want to override the corresponding methods :meth:`_set_axes_labels`
        and :meth:`_create_axis_label_string`, respectively.

        Parameters
        ----------
        dataset : :class:`aspecd.dataset.Dataset`
            dataset to perform plot for

        from_dataset : `boolean`
            whether we are called from within a dataset

            Defaults to "False" and shall never be set manually.

        Returns
        -------
        dataset : :class:`aspecd.dataset.Dataset`
            dataset plot has been performed for

        Raises
        ------
        aspecd.exceptions.NotApplicableToDatasetError
            Raised when plotting is not applicable to dataset
        aspecd.exceptions.MissingDatasetError
            Raised when no dataset exists to act on

        """
        self._assign_dataset(dataset)
        self._assign_data()
        self._call_from_dataset(from_dataset)
        return self.dataset

    def create_history_record(self):
        """
        Create history record to be added to the dataset.

        Usually, this method gets called from within the
        :meth:`aspecd.dataset.Dataset.plot` method of the
        :class:`aspecd.dataset.Dataset` class and ensures the history of
        each plotting step to get written properly.

        Returns
        -------
        history_record : :class:`aspecd.history.PlotHistoryRecord`
            history record for plotting step

        """
        history_record = aspecd.history.PlotHistoryRecord(
            package=self.dataset.package_name
        )
        history_record.plot = aspecd.history.SinglePlotRecord(plotter=self)
        history_record.plot.preprocessing = copy.deepcopy(
            self.dataset.history
        )
        return history_record

    def _assign_dataset(self, dataset):
        if not dataset:
            if not self.dataset:
                raise aspecd.exceptions.MissingDatasetError
        else:
            self.dataset = dataset

    def _call_from_dataset(self, from_dataset):
        if not from_dataset:
            self.dataset.plot(self)
        else:
            self._check_applicability()
            super().plot()
            self._set_axes_labels()
            self.properties.apply(plotter=self)

    def _assign_data(self):
        if self.parameters["device_data"]:
            device = self.parameters["device_data"]
            if device not in self.dataset.device_data:
                raise KeyError(f"Device '{device}' not found in dataset.")
            self.data = self.dataset.device_data[device]
        else:
            self.data = self.dataset.data

    def _check_applicability(self):
        if not self.applicable(self.data):
            message = (
                f"{self.name} not applicable to dataset with id "
                f"{self.dataset.id}"
            )
            raise aspecd.exceptions.NotApplicableToDatasetError(
                message=message
            )

    def _set_axes_labels(self):
        """Set axes labels from axes in dataset.

        This method is called automatically by :meth:`plot`.

        If you ever need to change the handling of your axes labels,
        override this method in a child class.
        """
        xlabel = self._create_axis_label_string(self.data.axes[0])
        ylabel = self._create_axis_label_string(self.data.axes[1])
        self.axes.set_xlabel(xlabel)
        self.axes.set_ylabel(ylabel)


class SinglePlotter1D(SinglePlotter):
    # noinspection PyUnresolvedReferences
    """1D plots of single datasets.

    Convenience class taking care of 1D plots of single datasets. The type
    of plot can be set in its :attr:`aspecd.plotting.SinglePlotter1D.type`
    attribute. Allowed types are stored in the
    :attr:`aspecd.plotting.SinglePlotter1D.allowed_types` attribute.

    Quite a number of properties for figure, axes, and line can be set
    using the :attr:`aspecd.plotting.SinglePlotter1D.properties` attribute.
    For details, see the documentation of its respective class,
    :class:`aspecd.plotting.SinglePlot1DProperties`.

    To perform the plot, call the :meth:`plot` method of the dataset the plot
    should be performed for, and provide a reference to the actual plotter
    object to it.

    Attributes
    ----------
    properties : :class:`aspecd.plotting.SinglePlot1DProperties`
        Properties of the plot, defining its appearance

        For the properties that can be set this way, see the documentation
        of the :class:`aspecd.plotting.SinglePlot1DProperties` class.

    parameters : :class:`dict`
        All parameters necessary for the plot, implicit and explicit

        The following keys exist, in addition to those of the superclass:

        tight: :class:`str`
            Whether to set the axes limits tight to the data

            Possible values: 'x', 'y', 'both'

            Default: ''

        switch_axes : :class:`bool`
            Whether to switch *x* and *y* axes

            Normally, the first axis is used as *x* axis, and the second
            as *y* axis. Sometimes, switching this assignment is
            necessary or convenient.

            Default: False

    Raises
    ------
    TypeError
        Raised when wrong plot type is set

    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. Of course, all parameters settable
    for the superclasses can be set as well. The examples focus each on a
    single aspect.

    In the simplest case, just invoke the plotter with default values:

    .. code-block:: yaml

       - kind: singleplot
         type: SinglePlotter1D
         properties:
           filename: output.pdf

    Of course, line plots are not the only plot type available. Check the
    :attr:`SinglePlotter1D.allowed_types` attribute for further details. To
    make a semilogy plot (*i.e.*, with logarithmic *y* axis), invoke the
    plotter as follows:

    .. code-block:: yaml

       - kind: singleplot
         type: SinglePlotter1D
         properties:
           type: semilogy
           filename: output.pdf

    .. important::

        As the logarithm of negative values is not defined, usually having a
        logarithmic axis with negative values will lead to unexpected
        results. Matplotlib defaults to clipping the invalid values. To help
        you with debugging the unexpected results, a warning will be logged
        (and printed to the terminal when serving a recipe) in case a
        logarithmic axis is affected by negative values. In such case,
        the easiest is to add an offset to your data, using
        :class:`aspecd.processing.ScalarAlgebra`.

    Sometimes it is convenient to switch the *x* and *y* axes, *e.g.* in
    context of 2D datasets where slices along both dimensions should be
    displayed together with the 2D data and next to the respective axes. To
    achieve this, set the ``switch_axes`` parameter accordingly:

    .. code-block:: yaml

       - kind: singleplot
         type: SinglePlotter1D
         properties:
           parameters:
             switch_axes: true
           filename: output.pdf

    If the dataset contains additional device data, and you want to plot
    data of a single device rather than the primary data of the dataset (
    and the device data are 1D), provide the name of the device (*i.e.*,
    the key the device data are stored in the dataset). Assuming the
    device data are stored as ``timestamp`` in the dataset:

    .. code-block:: yaml

        - kind: singleplot
          type: SinglePlotter1D
          properties:
            parameters:
              device_data: timestamp
            filename: output.pdf

    .. versionchanged:: 0.7
        New parameter ``switch_axes``

    .. versionchanged:: 0.9
        Issue warning with log plotters and negative values

    """

    def __init__(self):
        super().__init__()
        self.description = "1D plotting step for single dataset"
        self.properties = SinglePlot1DProperties()
        # noinspection PyTypeChecker
        self.parameters["tight"] = ""
        self.parameters["switch_axes"] = False
        self._type = "plot"
        self._allowed_types = [
            "plot",
            "scatter",
            "step",
            "loglog",
            "semilogx",
            "semilogy",
            "stemplot",
        ]

    @property
    def type(self):
        """
        Get or set the plot type.

        Types need to be methods of the :class:`matplotlib.axes.Axes` class.

        Allowed plot types are stored in the
        :attr:`aspecd.plotting.SinglePlotter1D.allowed_types` attribute.

        Default: 'plot'

        Raises
        ------
        TypeError
            Raised in case of wrong type

        """
        return self._type

    @property
    def allowed_types(self):
        """
        Return the allowed plot types.

        Currently, the allowed types are: ``plot``, ``scatter``, ``step``,
        ``loglog``, ``semilogx``, ``semilogy``, ``stemplot``.

        Returns
        -------
        allowed_types: :class:`list`
            List of strings

        """
        return self._allowed_types

    @type.setter
    def type(self, plot_type=None):
        if plot_type not in self.allowed_types:
            raise TypeError
        self._type = plot_type

    def _create_plot(self):
        plot_function = getattr(self.axes, self.type)
        self._check_values_for_logplot()
        if not self.properties.drawing.label:
            self.properties.drawing.label = self.dataset.label
        if self.parameters["switch_axes"]:
            (self.drawing,) = plot_function(
                self.data.data,
                self.data.axes[0].values,
                label=self.properties.drawing.label,
            )
        else:
            (self.drawing,) = plot_function(
                self.data.axes[0].values,
                self.data.data,
                label=self.properties.drawing.label,
            )
        if self.parameters["tight"]:
            if self.parameters["tight"] in ("x", "both"):
                self.axes.set_xlim(
                    [
                        self.data.axes[0].values.min(),
                        self.data.axes[0].values.max(),
                    ]
                )
            if self.parameters["tight"] in ("y", "both"):
                self.axes.set_ylim(
                    [self.data.data.min(), self.data.data.max()]
                )

    def _check_values_for_logplot(self):
        issue_warning = False
        if self.parameters["switch_axes"]:
            xvalues = self.data.data
            yvalues = self.data.axes[0].values
        else:
            xvalues = self.data.axes[0].values
            yvalues = self.data.data
        if "semilogy" in self.type and np.min(yvalues) < 0:
            issue_warning = True
        if "semilogx" in self.type and np.min(xvalues) < 0:
            issue_warning = True
        if "loglog" in self.type and (
            np.min(xvalues) < 0 or np.min(yvalues) < 0
        ):
            issue_warning = True
        if issue_warning:
            logger.warning(
                "Negative values with %s plot detected.", self.type
            )

    def _set_axes_labels(self):
        super()._set_axes_labels()
        if self.parameters["switch_axes"]:
            old_xlabel = self.axes.get_xlabel()
            old_ylabel = self.axes.get_ylabel()
            self.axes.set_xlabel(old_ylabel)
            self.axes.set_ylabel(old_xlabel)

    @staticmethod
    def applicable(data):
        """Check whether plot is applicable to the dataset.

        Checks for the dimension of the data of the dataset, i.e. the
        :attr:`aspecd.dataset.Data.data` attribute. Returns `True` if data
        are one-dimensional, and `False` otherwise.

        Returns
        -------
        applicable : :class:`bool`
            `True` if successful, `False` otherwise.

        """
        return data.data.ndim == 1


class SinglePlotter2D(SinglePlotter):
    # noinspection PyUnresolvedReferences
    """2D plots of single datasets.

    Convenience class taking care of 2D plots of single datasets. The type
    of plot can be set in its :attr:`aspecd.plotting.SinglePlotter2D.type`
    attribute. Allowed types are stored in the
    :attr:`aspecd.plotting.SinglePlotter2D.allowed_types` attribute.

    Quite a number of properties for figure, axes, and surface can be set
    using the :attr:`aspecd.plotting.SinglePlotter2D.properties` attribute.
    For details, see the documentation of its respective class,
    :class:`aspecd.plotting.SinglePlot2DProperties`.

    To perform the plot, call the :meth:`plot` method of the dataset the
    plot should be performed for, and provide a reference to the actual
    plotter object to it.

    .. important::
        Due to the difference between axes conventions in plots,
        with axes being labelled *x*, *y*, *z* accordingly, and the
        convention of indexing arrays (first index refers to the row,
        converting to the *y* axis, the second index to the column,
        *i.e*. the *x* axis), the *x* axis in the plot will be the second
        axis, the *y* axis the first axis of your dataset. If you need to
        change this, you can set the ``switch_axes`` parameter to True.

        While usually, it is only a matter of convention how to display
        your 2D data, it is often confusing, as we intuitively think in *x*,
        *y*, *z* axes, not in row-column indices.


    Attributes
    ----------
    parameters : :class:`dict`
        All parameters necessary for the plot, implicit and explicit

        The following keys exist, in addition to those of the superclasses:

        switch_axes : :class:`bool`
            Whether to switch *x* and *y* axes

            Normally, the first axis is used as *x* axis, and the second
            as *y* axis. Sometimes, switching this assignment is
            necessary or convenient.

            Default: False

        levels : :class:`int`
            Number of levels of a contour plot

            If None, the number of levels will be determined automatically.

            Default: None

        threshold : :class:`float`
            Threshold for determining the levels of a contour plot.

            Sometimes, you want to control explicitly the lowest level of a
            contour plot. This can be done setting a threshold value here.

            Internally, a :class:`matplotlib.ticker.MaxNLocator` will be
            used to determine the levels.

            .. versionadded:: 0.12

        show_contour_lines : :class:`bool`
            Whether to show contour lines in case of contourf plot

        show_colorbar : :class:`bool`
            Whether to show a colorbar

            .. versionadded:: 0.9


    properties : :class:`aspecd.plotting.SinglePlot2DProperties`
        Properties of the plot, defining its appearance

        For the properties that can be set this way, see the documentation
        of the :class:`aspecd.plotting.SinglePlot2DProperties` class.

    Raises
    ------
    TypeError
        Raised when wrong plot type is set

    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. Of course, all parameters settable
    for the superclasses can be set as well. The examples focus each on a
    single aspect.

    In the simplest case, just invoke the plotter with default values:

    .. code-block:: yaml

       - kind: singleplot
         type: SinglePlotter2D
         properties:
           filename: output.pdf

    To change the axes (flip *x* and *y* axis):

    .. code-block:: yaml

       - kind: singleplot
         type: SinglePlotter2D
         properties:
           filename: output.pdf
           parameters:
             switch_axes: True

    To use another type (here: contour):

    .. code-block:: yaml

       - kind: singleplot
         type: SinglePlotter2D
         properties:
           filename: output.pdf
           type: contour

    To set the number of levels of a contour plot to 10:

    .. code-block:: yaml

       - kind: singleplot
         type: SinglePlotter2D
         properties:
           filename: output.pdf
           type: contour
           parameters:
             levels: 10

    To change the colormap (cmap) used:

    .. code-block:: yaml

       - kind: singleplot
         type: SinglePlotter2D
         properties:
           filename: output.pdf
           properties:
             drawing:
               cmap: RdGy

    To plot both, filled contours and contour lines, setting the appearance
    of the contour lines as well:

    .. code-block:: yaml

       - kind: singleplot
         type: SinglePlotter2D
         properties:
           type: contourf
           filename: output.pdf
           parameters:
             show_contour_lines: True
           properties:
             drawing:
               cmap: RdGy
               linewidths: 0.5
               linestyles: '-'
               colors: k

    In this particular case, the contour lines are thin black solid lines.

    Make sure to check the documentation for further parameters that can be
    set.

    """

    def __init__(self):
        super().__init__()
        self.description = "2D plotting step for single dataset"
        self.parameters["switch_axes"] = False
        # noinspection PyTypeChecker
        self.parameters["levels"] = None
        self.parameters["threshold"] = None
        self.parameters["show_contour_lines"] = False
        self.parameters["show_colorbar"] = False
        self.properties = SinglePlot2DProperties()
        self.colorbar = None
        self._type = "imshow"
        self._allowed_types = ["contour", "contourf", "imshow"]
        self._exclude_from_to_dict.append("colorbar")

    @property
    def type(self):
        """
        Get or set the plot type.

        Types need to be methods of the :class:`matplotlib.axes.Axes` class.

        Allowed plot types are stored in the
        :attr:`aspecd.plotting.SinglePlotter2D.allowed_types` attribute.

        Default: 'imshow'

        Raises
        ------
        TypeError
            Raised in case of wrong type

        """
        return self._type

    @property
    def allowed_types(self):
        """
        Return the allowed plot types.

        Currently allowed types are: ``contour``, ``contourf``, ``imshow``

        Returns
        -------
        allowed_types: :class:`list`
            List of strings

        """
        return self._allowed_types

    @type.setter
    def type(self, plot_type=None):
        if plot_type not in self.allowed_types:
            raise TypeError
        self._type = plot_type

    @staticmethod
    def applicable(data):
        """Check whether plot is applicable to the given dataset.

        Checks for the dimension of the data of the dataset, i.e. the
        :attr:`aspecd.dataset.Data.data` attribute. Returns `True` if data
        are two-dimensional, and `False` otherwise.

        Returns
        -------
        applicable : :class:`bool`
            `True` if successful, `False` otherwise.

        """
        return data.data.ndim == 2

    def _create_plot(self):
        """Create actual plot.

        Due to ``imshow`` and ``contour`` needing slightly different
        handling, the plotting is a bit more complex. Many parameters such
        as extent and levels can *only* be set during  invoking the actual
        plotting class.

        """
        # matplotlib imshow and contour have incompatible properties
        if self.type == "imshow":
            self._plot_imshow()
        else:
            self._plot_contour()
        if self.parameters["show_colorbar"]:
            self.colorbar = self.fig.colorbar(
                self.drawing, ax=self.ax, **self.properties.colorbar.kwargs
            )

    def _plot_imshow(self):
        plot_function = getattr(self.axes, self.type)
        data = self._shape_data()
        self.drawing = plot_function(
            data, extent=self._get_extent(), aspect="auto"
        )

    def _plot_contour(self):
        plot_function = getattr(self.axes, self.type)
        data = self._shape_data()
        level_ticker = ticker.MaxNLocator(self.parameters["levels"])
        if self.parameters["threshold"]:
            levels = level_ticker.tick_values(
                self.parameters["threshold"], np.max(data)
            )
        else:
            levels = level_ticker.tick_values(np.min(data), np.max(data))
        self.drawing = plot_function(
            data, extent=self._get_extent(), levels=levels
        )
        if self.type == "contourf" and self.parameters["show_contour_lines"]:
            self.axes.contour(
                self.drawing, colors="k", linewidths=0.5, linestyles="-"
            )

    def _shape_data(self):
        if self.parameters["switch_axes"]:
            data = self.data.data
        else:
            data = self.data.data.T
        if self.type == "imshow":
            data = np.flipud(data)
        return data

    def _get_extent(self):
        if self.parameters["switch_axes"]:
            extent = [
                self.data.axes[1].values[0],
                self.data.axes[1].values[-1],
                self.data.axes[0].values[0],
                self.data.axes[0].values[-1],
            ]
        else:
            extent = [
                self.data.axes[0].values[0],
                self.data.axes[0].values[-1],
                self.data.axes[1].values[0],
                self.data.axes[1].values[-1],
            ]
        return extent

    def _set_axes_labels(self):
        """Set axes labels from axes in dataset.

        This method is called automatically by :meth:`plot`.

        .. note::
            Due to the difference between axes conventions in plots,
            with axes being labelled *x*, *y*, *z* accordingly, and the
            convention of indexing arrays (first index refers to the row,
            converting to the *y* axis, the second index to the column,
            *i.e*. the *x* axis), labels have to be reverted for *x* and *y*
            axis with respect to the situation with 1D data.

        If you ever need to change the handling of your axes labels,
        override this method in a child class.
        """
        if self.parameters["switch_axes"]:
            xlabel = self._create_axis_label_string(self.data.axes[1])
            ylabel = self._create_axis_label_string(self.data.axes[0])
        else:
            xlabel = self._create_axis_label_string(self.data.axes[0])
            ylabel = self._create_axis_label_string(self.data.axes[1])
        self.axes.set_xlabel(xlabel)
        self.axes.set_ylabel(ylabel)


class SinglePlotter2DStacked(SinglePlotter):
    # noinspection PyUnresolvedReferences
    """Stacked plots of 2D data

    A stackplot creates a series of lines stacked on top of each other from
    a 2D dataset.

    Attributes
    ----------
    dataset : :class:`aspecd.dataset.Dataset`
        Dataset the plotting should be done for

    drawing : :class:`list`
        Actual graphical representation of the data.

        List of , one for each of the
        actual lines of the plot

    parameters : :class:`dict`
        All parameters necessary for the plot, implicit and explicit

        The following keys exist, in addition to the keys inherited from the
        superclass:

        show_legend : :class:`bool`
            Whether to show a legend in the plot

            Default: False

        show_zero_lines : :class:`bool`
            Whether to show zero lines in the plot

            Regardless of whether you set this to true, zero lines will
            only be added to the final plot if the zero value is within
            the current axes limits.

            Zero line properties can be set via the
            :attr:`aspecd.plotting.Plotter.properties` attribute.

            Default: False

        stacking_dimension : :class:`int`
            dimension of data along which to stack the plot

            Default: 1

        offset : :class:`float`
            offset between lines

            If not explicitly set, the plotter will try its best to determine a
            sensible value, by using ``self.dataset.data.data.max() * 1.05``.

            Default: 0

        yticklabelformat : :class:`string`
            format for tick labels on the y axis

            Useful in case of too many decimals displayed on the y axis.
            Uses (currently) the "old-style" formatting syntax familiar from
            the C programming language, *e.g.* "%.2f" would format your
            labels with two decimals (including rounding).

            If "None", no explicit formatting will be performed and the
            defaults of Matplotlib applied.

            Default: None

        ytickcount : :class:`int`
            number of tick labels on the y axis

            Useful in case of too many ticks displayed on the y axis.

            If "None", as many ticks as plotted lines will be displayed.

            If the number is larger than the number of plotted lines,
            only one tick per line will be shown, not more.

            Default: None

        tight: :class:`str`
            Whether to set the axes limits tight to the data

            Possible values: 'x', 'y', 'both'

            Default: ''

    properties : :class:`aspecd.plotting.SinglePlot2DStackedProperties`
        Properties of the plot, defining its appearance

        For the properties that can be set this way, see the documentation
        of the :class:`aspecd.plotting.SinglePlot2DStackedProperties` class.


    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. Of course, all parameters settable
    for the superclasses can be set as well. The examples focus each on a
    single aspect.

    In the simplest case, just invoke the plotter with default values:

    .. code-block:: yaml

       - kind: singleplot
         type: SinglePlotter2DStacked
         properties:
           filename: output.pdf

    If you need to more precisely control the formatting of the y tick
    labels, particularly the number of decimals shown, you can set the
    formatting accordingly:

    .. code-block:: yaml

       - kind: singleplot
         type: SinglePlotter2DStacked
         properties:
           filename: output.pdf
           parameters:
             yticklabelformat: '%.2f'

    In this particular case, the y tick labels will appear with only two
    decimals. Note that currently, the "old style" formatting specifications
    are used due to their widespread use in other programming languages and
    hence the familiarity of many users with this particular notation.

    Sometimes you want to have horizontal "zero lines" appear for each
    individual trace of the stacked plot. This can be achieved explicitly
    setting the "show_zero_lines" parameter to "True" that is set to "False"
    by default:

    .. code-block:: yaml

       - kind: singleplot
         type: SinglePlotter2DStacked
         properties:
           filename: output.pdf
           parameters:
             show_zero_lines: True

    As always, you can set the appearance of the plot in quite some detail.
    If you would like to style the individual lines, *i.e.* ``drawings``,
    provide a list of properties for each individual drawing and make sure
    to provide as many items in the list as there are lines in the plot:

    .. code-block:: yaml

       - kind: singleplot
         type: SinglePlotter2DStacked
         properties:
           properties:
             drawings:
               - color: '#FF0000'
                 label: foo
               - color: '#00FF00'
                 label: bar
               - color: '#0000FF'
                 label: foobar

    .. important::
        If you set colours using the hexadecimal RGB triple prefixed by
        ``#``, you need to explicitly tell YAML that these are strings,
        surrounding the values by quotation marks.

    Suppose you want to set identical properties for all lines. This is
    possible as well, by not providing the ``drawings`` key (plural) but
    the ``drawing`` key (singular) - and of course, this time not a list:

    .. code-block:: yaml

       - kind: singleplot
         type: SinglePlotter2DStacked
         properties:
           properties:
             drawing:
               color: '#FF0000'


    .. versionchanged:: 0.6
        ylabel is set to third axis if offset = 0; new parameter "tight"

    .. versionchanged:: 0.6.2
        New parameter ``ytickcount``

    .. versionchanged:: 0.10
        Properties changed to :class:`SinglePlot2DStackedProperties`

    """

    # noinspection PyTypeChecker
    def __init__(self):
        super().__init__()
        self.description = "2D stackplot for a single dataset"
        self.dataset = None
        self.parameters.update(
            {
                "show_legend": False,
                "show_zero_lines": False,
                "stacking_dimension": 1,
                "offset": None,
                "yticklabelformat": None,
                "ytickcount": None,
                "tight": "",
            }
        )
        self.drawing = []
        self.properties = SinglePlot2DStackedProperties()

    @property
    def drawings(self):
        """
        Actual graphical representation of the data.

        List of :obj:`matplotlib.artist.Artist` objects, one for each of the
        actual lines of the plot

        This is identical to :attr:`drawing` and has been added to work
        conveniently with :class:`SinglePlot2DStackedProperties`.

        Returns
        -------
        drawings : :class:`list`
            Actual graphical representation of the data.


        .. versionadded:: 0.10

        """
        return self.drawing

    @drawings.setter
    def drawings(self, drawings=None):
        self.drawing = drawings

    @staticmethod
    def applicable(data):
        """Check whether plot is applicable to the dataset.

        Checks for the dimension of the data of the dataset, i.e. the
        :attr:`aspecd.dataset.Data.data` attribute. Returns `True` if data
        are two-dimensional, and `False` otherwise.

        Returns
        -------
        applicable : :class:`bool`
            `True` if successful, `False` otherwise.

        """
        return data.data.ndim == 2

    def _set_drawing_properties(self):
        if len(self.properties.drawings) < len(self.drawing):
            for _ in range(len(self.properties.drawings), len(self.drawing)):
                self.properties.add_drawing()

    def _create_plot(self):
        if self.parameters["offset"] is None:
            self.parameters["offset"] = abs(self.data.data).max() * 1.05
        yticks = []
        if self.parameters["stacking_dimension"] == 0:
            for idx in range(self.dataset.data.data.shape[0]):
                # noinspection PyTypeChecker
                handle = self.axes.plot(
                    self.data.axes[1].values,
                    self.data.data[idx, :] + idx * self.parameters["offset"],
                )
                self.drawing.append(handle[0])
                # noinspection PyTypeChecker
                yticks.append(idx * self.parameters["offset"])
            yticklabels = self.data.axes[0].values.astype(float)
        else:
            for idx in range(self.data.data.shape[1]):
                # noinspection PyTypeChecker
                handle = self.axes.plot(
                    self.data.axes[0].values,
                    self.data.data[:, idx] + idx * self.parameters["offset"],
                )
                self.drawing.append(handle[0])
                # noinspection PyTypeChecker
                yticks.append(idx * self.parameters["offset"])
            yticklabels = self.data.axes[1].values.astype(float)
        if self.parameters["ytickcount"]:
            # noinspection PyTypeChecker
            ytickcount = min(len(self.drawing), self.parameters["ytickcount"])
            yticklabels = np.linspace(
                yticklabels[0], yticklabels[-1], num=ytickcount
            )
            yticks = np.linspace(yticks[0], yticks[-1], num=ytickcount)
        if self.parameters["offset"]:
            self.properties.axes.yticks = yticks
            self.properties.axes.yticklabels = self._format_yticklabels(
                yticklabels
            )
        self._handle_tight_settings()
        self._set_drawing_properties()

    def _handle_tight_settings(self):
        if self.parameters["tight"]:
            if self.parameters["tight"] in ("x", "both"):
                self.axes.set_xlim(
                    [
                        self.data.axes[0].values.min(),
                        self.data.axes[0].values.max(),
                    ]
                )
            if self.parameters["tight"] in ("y", "both"):
                if self.parameters["offset"] == 0:
                    self.axes.set_ylim(
                        [self.data.data.min(), self.data.data.max()]
                    )

    def _format_yticklabels(self, yticklabels):
        if self.parameters["yticklabelformat"]:
            formatting = self.parameters["yticklabelformat"]
            # noinspection PyUnresolvedReferences
            yticklabels = [formatting % label for label in yticklabels]
        return yticklabels

    def _set_axes_labels(self):
        """Set axes labels from axes in dataset.

        This method is called automatically by :meth:`plot`.

        .. note::
            Due to the difference between axes conventions in plots,
            with axes being labelled *x*, *y*, *z* accordingly, and the
            convention of indexing arrays (first index refers to the row,
            converting to the *y* axis, the second index to the column,
            *i.e*. the *x* axis), labels have to be reverted for *x* and *y*
            axis with respect to the situation with 1D data.

        If you ever need to change the handling of your axes labels,
        override this method in a child class.
        """
        if self.parameters["stacking_dimension"] == 0:
            xlabel = self._create_axis_label_string(self.data.axes[1])
            ylabel = self._create_axis_label_string(self.data.axes[0])
        else:
            xlabel = self._create_axis_label_string(self.data.axes[0])
            ylabel = self._create_axis_label_string(self.data.axes[1])
        if self.parameters["offset"] == 0:
            ylabel = self._create_axis_label_string(self.data.axes[2])
        self.axes.set_xlabel(xlabel)
        self.axes.set_ylabel(ylabel)

    def _add_zero_lines(self):
        if self.parameters["show_zero_lines"]:
            dimension = self.parameters["stacking_dimension"]
            for idx in range(self.data.data.shape[dimension]):
                # noinspection PyTypeChecker
                offset = idx * self.parameters["offset"]
                properties = self.properties.zero_lines.to_dict()
                # noinspection PyUnresolvedReferences
                properties.update({"zorder": 1})
                self.axes.axhline(
                    y=offset,
                    **properties,  # noqa
                )


class MultiDeviceDataPlotter1D(SinglePlotter1D):
    """1D plots of multiple device data of a single dataset.

    Convenience class taking care of 1D plots of multiple device data
    of a single dataset. The type of plot can be set in its
    :attr:`SinglePlotter1D.type` attribute. Allowed types are stored in the
    :attr:`SinglePlotter1D.allowed_types` attribute.

    Quite a number of properties for figure, axes, and line can be set
    using the :attr:`MultiDeviceDataPlotter1D.properties` attribute.
    For details, see the documentation of its respective class,
    :class:`MultiPlot1DProperties`.

    To perform the plot, call the :meth:`plot` method of the dataset the plot
    should be performed for, and provide a reference to the actual plotter
    object to it.

    Attributes
    ----------
    dataset : :class:`aspecd.dataset.Dataset`
        Dataset the plotting should be done for

    data : :class:`list`
        Actual data that should be plotted.

        List of :class:`aspecd.dataset.DeviceData` objects corresponding
        to the device data selected using the parameter ``device_data``.

    drawing : :class:`list`
        List of :obj:`matplotlib.artist.Artist` objects, one for each of the
        actual lines of the plot

    properties : :class:`aspecd.plotting.MultiPlot1DProperties`
        Properties of the plot, defining its appearance

        For the properties that can be set this way, see the documentation
        of the :class:`aspecd.plotting.MultiPlot1DProperties` class.

    parameters : :class:`dict`
        All parameters necessary for the plot, implicit and explicit

        The following keys exist, in addition to those of the superclass:

        axes : :class:`list`
            List of objects of class :class:`aspecd.dataset.Axis`

            There is two ways of setting axes labels: The user may provide
            the information required here. Alternatively, if no such
            information is provided, the axes of each dataset are checked
            for consistency, and if they are found to be identical,
            this information is used.

        tight: :class:`str`
            Whether to set the axes limits tight to the data

            Possible values: 'x', 'y', 'both'

            Default: ''

        switch_axes : :class:`bool`
            Whether to switch *x* and *y* axes

            Normally, the first axis is used as *x* axis, and the second
            as *y* axis. Sometimes, switching this assignment is
            necessary or convenient.

            Default: False


    Raises
    ------
    TypeError
        Raised when wrong plot type is set

    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. Of course, all parameters settable
    for the superclasses can be set as well. The examples focus each on a
    single aspect.

    In the simplest case, just invoke the plotter with default values.
    Note, however, that in any case, you need to provide a list of devices
    whose data should be plotted:

    .. code-block:: yaml

        - kind: singleplot
          type: MultiDeviceDataPlotter1D
          properties:
            parameters:
              device_data:
                - device_1
                - device_2
            filename: output.pdf

    Often, it is convenient to have a legend to know for which devices the
    data are plotted:

    .. code-block:: yaml

        - kind: singleplot
          type: MultiDeviceDataPlotter1D
          properties:
            parameters:
              device_data:
                - device_1
                - device_2
              show_legend: True
            filename: output.pdf

    Here, it is interesting to note what labels will be used: Usually,
    the data for each device will have the attribute
    :class:`aspecd.metadata.Device.label` set, and if so, this label will
    be used as label in the legend. If this attribute is not set, and you
    do not provide an alternative label in the
    :attr:`MultiPlot1DProperties.drawing` attribute, the key the device
    data are known within the dataset will be used in the legend.

    To explicitly set (or override) the labels of your device data:

    .. code-block:: yaml

        - kind: singleplot
          type: MultiDeviceDataPlotter1D
          properties:
            parameters:
              device_data:
                - device_1
                - device_2
              show_legend: True
            properties:
              drawings:
                - label: first device
                - label: second device
            filename: output.pdf

    As axes are only labelled in case the axes of all devices are
    compatible, there may be situations where you want to set the axes
    properties explicitly:

    .. code-block:: yaml

        - kind: singleplot
          type: MultiDeviceDataPlotter1D
          properties:
            parameters:
              device_data:
                - device_1
                - device_2
              axes:
                - quantity: time
                  unit: s
                - quantity: intensity
                  unit: a.u.
            filename: output.pdf

    .. versionadded:: 0.9

    """

    def __init__(self):
        super().__init__()
        self.description = "1D plotting step for multiple device data"
        self.data = []
        self.drawing = []
        self.parameters["axes"] = [
            aspecd.dataset.Axis(),
            aspecd.dataset.Axis(),
        ]
        self.parameters["tight"] = ""
        self.parameters["switch_axes"] = False
        self.properties = MultiPlot1DProperties()

    @property
    def drawings(self):
        """Alias for drawing property.

        As the plotter uses :class:`MultiPlot1DProperties` as
        :attr:`properties`, this alias is necessary to apply the drawings
        settings.

        """
        return self.drawing

    @staticmethod
    def applicable(data):
        """Check whether plot is applicable to the given dataset.

        Checks for the dimension of the data of the dataset, i.e. the
        :attr:`aspecd.dataset.Data.data` attribute. Returns `True` if data
        are one-dimensional, and `False` otherwise.

        Returns
        -------
        applicable : :class:`bool`
            `True` if successful, `False` otherwise.

        """
        return data.data.ndim == 1

    def _check_applicability(self):
        for data in self.data:
            if not self.applicable(data):
                message = (
                    f"{self.name} not applicable to dataset with id "
                    f"{self.dataset.id}"
                )
                raise aspecd.exceptions.NotApplicableToDatasetError(
                    message=message
                )

    def _assign_data(self):
        if not self.parameters["device_data"]:
            raise KeyError("No device data provided")
        if not isinstance(self.parameters["device_data"], list):
            # noinspection PyTypedDict
            self.parameters["device_data"] = [self.parameters["device_data"]]
        devices = self.parameters["device_data"]
        for device in devices:
            if device not in self.dataset.device_data:
                raise KeyError(f"Device '{device}' not found in dataset.")
            self.data.append(self.dataset.device_data[device])

    def _create_plot(self):
        self._set_drawing_properties()
        plot_function = getattr(self.axes, self.type)
        for idx, data in enumerate(self.data):
            label = data.metadata.label or self.parameters["device_data"][idx]
            if not self.properties.drawings[idx].label:
                self.properties.drawings[idx].label = label
            if self.parameters["switch_axes"]:
                (drawing,) = plot_function(
                    data.data, data.axes[0].values, label=label
                )
            else:
                (drawing,) = plot_function(
                    data.axes[0].values, data.data, label=label
                )
            self.drawing.append(drawing)
        if self.parameters["tight"]:
            axes_limits = [
                min(data.axes[0].values.min() for data in self.data),
                max(data.axes[0].values.max() for data in self.data),
            ]
            data_limits = [
                min(data.data.min() for data in self.data),
                max(data.data.max() for data in self.data),
            ]
            if self.parameters["tight"] in ("x", "both"):
                if self.parameters["switch_axes"]:
                    self.axes.set_xlim(data_limits)
                else:
                    self.axes.set_xlim(axes_limits)
            if self.parameters["tight"] in ("y", "both"):
                if self.parameters["switch_axes"]:
                    self.axes.set_ylim(axes_limits)
                else:
                    self.axes.set_ylim(data_limits)

    def _set_drawing_properties(self):
        for _ in range(len(self.properties.drawings), len(self.data)):
            self.properties.add_drawing()

    # noinspection PyUnresolvedReferences
    def _set_axes_labels(self):
        """Set axes labels from axes.

        This method is called automatically by :meth:`plot`.

        There is two ways of setting axes labels: The user may provide the
        information required in the "axes" key of the
        :attr:`aspecd.plotting.Plotter.parameters` property containing a
        list of :obj:`aspecd.dataset.Axis` objects. Alternatively,
        if no such information is provided, the axes of each dataset are
        checked for consistency, and if they are found to be identical,
        this information is used.

        If you ever need to change the handling of your axes labels,
        override this method in a child class.
        """
        xquantities = [data.axes[0].quantity for data in self.data]
        xunits = [data.axes[0].unit for data in self.data]
        yquantities = [data.axes[1].quantity for data in self.data]
        yunits = [data.axes[1].unit for data in self.data]
        if self.parameters["axes"][0].quantity:
            xlabel = self._create_axis_label_string(
                self.parameters["axes"][0]
            )
        elif aspecd.utils.all_equal(xquantities) and aspecd.utils.all_equal(
            xunits
        ):
            xlabel = self._create_axis_label_string(self.data[0].axes[0])
        elif self.properties.axes.xlabel:
            xlabel = self.properties.axes.xlabel
        else:
            xlabel = ""
        if self.parameters["axes"][1].quantity:
            ylabel = self._create_axis_label_string(
                self.parameters["axes"][1]
            )
        elif aspecd.utils.all_equal(yquantities) and aspecd.utils.all_equal(
            yunits
        ):
            ylabel = self._create_axis_label_string(self.data[0].axes[1])
        elif self.properties.axes.ylabel:
            ylabel = self.properties.axes.ylabel
        else:
            ylabel = ""
        self.axes.set_xlabel(xlabel)
        self.axes.set_ylabel(ylabel)
        if self.parameters["switch_axes"]:
            old_xlabel = self.axes.get_xlabel()
            old_ylabel = self.axes.get_ylabel()
            self.axes.set_xlabel(old_ylabel)
            self.axes.set_ylabel(old_xlabel)


class SingleBarPlotter(SinglePlotter):
    """
    Bar plots of single datasets.

    Bar plots can be used for both, 1D and 2D datasets. In case of a 1D
    dataset, bars will be created whose height corresponds to the individual
    data points. For a 2D dataset, groups of bars will be created, with one
    bar per column in each bar group.


    Attributes
    ----------
    dataset : :class:`aspecd.dataset.Dataset`
        Dataset the plotting should be done for

    drawing : :class:`list`
        Actual graphical representation of the data.

        List of :obj:`matplotlib.container.BarContainer` objects, one for
        each column of the dataset. The actual
        :obj:`matplotlib.artist.Artist` objects are the children of the
        :obj:`matplotlib.container.BarContainer` objects.

    properties : :class:`aspecd.plotting.BarPlotProperties`
        Properties of the plot, defining its appearance

        For the properties that can be set this way, see the documentation
        of the :class:`aspecd.plotting.BarPlotProperties` class.

    parameters : :class:`dict`
        All parameters necessary for the plot, implicit and explicit

        The following keys exist, in addition to those of the superclass:

        show_zero_lines : :class:`bool`
            Whether to show zero lines in the plot

            Regardless of whether you set this to true, zero lines will only be
            added to the final plot if the zero value is within the current
            axes limits.

            Zero line properties can be set via the
            :attr:`aspecd.plotting.Plotter.properties` attribute.

            Default: False

        width : :class:`float`
            Total width of one group of bars.

            In case of a 1D dataset, this is identical to the width of a
            single bar. For 2D datasets, this is identical to the width of
            each group of bars, *i.e.* a single bar will be width/columns wide.

            As (groups of) bars are equally spaced, with a difference of two
            ticks of 1, width should be in the interval [0, 1]. Setting the
            width to 1 will leave no space between bars. While a width > 1
            is technically possible, this would lead to overlapping bars.

            Default: 0.8

        labels : :class:`list`
            Labels used for the individual columns of the dataset.

            In case of a 2D dataset, each column is treated similarly to an
            individual dataset, hence a label for the legend seems sensible.
            If the dataset does not provide the necessary information,
            you can set the label here.

            Default: []

    Raises
    ------
    aspecd.exceptions.NotApplicableToDatasetError
        Raised if the dataset data are >2D


    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. Of course, all parameters settable
    for the superclasses can be set as well. The examples focus each on a
    single aspect.

    In the simplest case, just invoke the plotter with default values:

    .. code-block:: yaml

       - kind: singleplot
         type: SingleBarPlotter
         properties:
           filename: output.pdf


    .. versionadded:: 0.12


    """

    def __init__(self):
        super().__init__()
        self.description = "Bar plot for single dataset"
        self.parameters.update(
            {"show_zero_lines": False, "width": 0.8, "labels": []}
        )
        self.drawing = []
        self.properties = BarPlotProperties()

    @property
    def drawings(self):
        """
        Actual graphical representation of the data.

        List of :obj:`matplotlib.container.BarContainer` objects, one for
        each column of the dataset. The actual
        :obj:`matplotlib.artist.Artist` objects are the children of the
        :obj:`matplotlib.container.BarContainer` objects.

        This is identical to :attr:`drawing` and has been added to work
        conveniently with :class:`BarPlotProperties`.

        Returns
        -------
        drawings : :class:`list`
            Actual graphical representation of the data.

        """
        return self.drawing

    @drawings.setter
    def drawings(self, drawings=None):
        self.drawing = drawings

    @staticmethod
    def applicable(data):
        """Check whether plot is applicable to the given dataset.

        Checks for the dimension of the data of the dataset, i.e. the
        :attr:`aspecd.dataset.Data.data` attribute. Returns `True` if data
        are one- or two-dimensional, and `False` otherwise.

        Returns
        -------
        applicable : :class:`bool`
            `True` if successful, `False` otherwise.

        """
        return data.data.ndim <= 2

    def _create_plot(self):
        labels = self._get_labels()
        if self.dataset.data.data.ndim == 1:
            position = np.arange(len(self.dataset.data.data))
            width = self.parameters["width"]
            drawing = self.axes.bar(
                position, self.dataset.data.data, width=width, label=labels[0]
            )
            self.drawing.append(drawing)
            self._set_drawing_properties()
            if labels[0]:
                self.properties.drawing[0].label = labels[0]
        else:
            position = np.arange(len(self.dataset.data.data[:, 1]))
            columns = self.dataset.data.data.shape[1]
            width = self.parameters["width"] / columns
            multiplier = -(columns - 1) / 2
            for column in range(columns):
                offset = width * multiplier
                drawing = self.axes.bar(
                    position + offset,
                    self.dataset.data.data[:, column],
                    width=width,
                    label=labels[column],
                )
                multiplier += 1
                self.drawing.append(drawing)
                self._set_drawing_properties()
                if labels[column]:
                    self.properties.drawing[column].label = labels[column]
        self.axes.set_xticks(position, self.dataset.data.axes[0].data)

    def _get_labels(self):
        labels = self.parameters["labels"]
        if self.dataset.data.data.ndim > 1:
            while len(labels) < self.dataset.data.data.shape[1]:
                labels.append("")
        elif not labels:
            labels = [""]
        return labels

    def _set_axes_labels(self):
        """Set axes labels from axes in dataset.

        This method is called automatically by :meth:`plot`.

        The special aspect with the SingleBarPlotter: Use the *last* axis
        for the *y* axis labels, as in all cases (1D and 2D datasets), we need
        the last axis.
        """
        xlabel = self._create_axis_label_string(self.data.axes[0])
        ylabel = self._create_axis_label_string(self.data.axes[-1])
        self.axes.set_xlabel(xlabel)
        self.axes.set_ylabel(ylabel)

    def _set_drawing_properties(self):
        if len(self.properties.drawings) < len(self.drawing):
            for _ in range(len(self.properties.drawings), len(self.drawing)):
                self.properties.add_drawing()


class MultiPlotter(Plotter):
    """Base class for plots of multiple datasets.

    Each class actually plotting data of multiple datasets should inherit from
    this class. Furthermore, all parameters, implicit and explicit,
    necessary to perform the plot, should eventually be stored in the property
    :attr:`parameters` (currently a dictionary).

    To perform the plot, call the :meth:`plot` method of the plotter directly.

    Further things that need to be changed upon inheriting from this class
    are the string stored in :attr:`description`, being basically a one-liner.

    The actual implementation of the plotting is done in the private method
    :meth:`_create_plot` that in turn gets called by :meth:`plot` that
    needs to be called directly (not from a dataset).

    Attributes
    ----------
    properties : :class:`aspecd.plotting.MultiPlotProperties`
        Properties of the plot, defining its appearance

    datasets : :class:`list`
        List of dataset the plotting should be done for

    data : :class:`list`
        List of actual data that should be plotted

        Each element is of type :class:`aspecd.dataset.Data`.

        Defaults to the primary data of a dataset, but can be the device
        data. See the key ``device_data`` of :attr:`Plotter.parameters` for
        details.

    parameters : :class:`dict`
        All parameters necessary for the plot, implicit and explicit

        The following keys exist, in addition to the keys inherited from the
        superclass:

        axes : :class:`list`
            List of objects of class :class:`aspecd.dataset.Axis`

            There is two ways of setting axes labels: The user may provide
            the information required here. Alternatively, if no such
            information is provided, the axes of each dataset are checked
            for consistency, and if they are found to be identical,
            this information is used.


    Raises
    ------
    aspecd.exceptions.MissingDatasetError
        Raised when no dataset exists to act on
    aspecd.exceptions.NotApplicableToDatasetError
        Raised when processing step is not applicable to dataset


    .. versionchanged:: 0.9
        New attribute ''data''

    """

    def __init__(self):
        super().__init__()
        self.properties = MultiPlotProperties()
        self.datasets = []
        self.data = []
        self.description = "Abstract plotting step for multiple dataset"
        # noinspection PyTypeChecker
        self.parameters["axes"] = [
            aspecd.dataset.Axis(),
            aspecd.dataset.Axis(),
        ]
        self.__kind__ = "multiplot"
        self._exclude_from_to_dict.extend(["datasets", "drawings", "data"])

    def plot(self):
        """Perform the actual plotting on the given list of datasets.

        If no dataset is added to the list of datasets of the
        object, the method will raise a respective exception.

        The actual plotting should be implemented within the non-public
        method :meth:`_create_plot`. Besides that, the applicability of the
        plotting to the given list of datasets will be checked automatically.
        These checks should be implemented in the method :meth:`applicable`.

        .. note::
            There is two ways of setting axes labels: The user may provide the
            information required in the "axes" key of the
            :attr:`aspecd.plotting.Plotter.parameters` property containing a
            list of :obj:`aspecd.dataset.Axis` objects. Alternatively,
            if no such information is provided, the axes of each dataset are
            checked for consistency, and if they are found to be identical,
            this information is used.

        Raises
        ------
        aspecd.exceptions.NotApplicableToDatasetError
            Raised when plotting is not applicable to at least one of the
            datasets listed in :attr:`datasets`
        aspecd.exceptions.MissingDatasetError
            Raised when no datasets exist to act on

        """
        self._assign_data()
        self._check_for_applicability()
        self._set_drawing_properties()
        super().plot()
        self._set_axes_labels()
        self.properties.apply(plotter=self)
        # Update/redraw legend after having set properties
        self._set_legend()

    def _assign_data(self):
        self.data = []  # Important, e.g., for CompositePlotter
        if self.parameters["device_data"]:
            device = self.parameters["device_data"]
            for dataset in self.datasets:
                if device not in dataset.device_data:
                    raise KeyError(f"Device '{device}' not found in dataset.")
                self.data.append(dataset.device_data[device])
        else:
            for dataset in self.datasets:
                self.data.append(dataset.data)

    def _check_for_applicability(self):
        if not self.datasets:
            raise aspecd.exceptions.MissingDatasetError
        if not all(self.applicable(data) for data in self.data):
            raise aspecd.exceptions.NotApplicableToDatasetError(
                f"{self.name} not applicable to one or more datasets"
            )

    def _set_drawing_properties(self):
        if len(self.properties.drawings) < len(self.datasets):
            for _ in range(len(self.properties.drawings), len(self.datasets)):
                self.properties.add_drawing()

    # noinspection PyUnresolvedReferences
    def _set_axes_labels(self):
        """Set axes labels from axes.

        This method is called automatically by :meth:`plot`.

        There is two ways of setting axes labels: The user may provide the
        information required in the "axes" key of the
        :attr:`aspecd.plotting.Plotter.parameters` property containing a
        list of :obj:`aspecd.dataset.Axis` objects. Alternatively,
        if no such information is provided, the axes of each dataset are
        checked for consistency, and if they are found to be identical,
        this information is used.

        If you ever need to change the handling of your axes labels,
        override this method in a child class.
        """
        xquantities = [ds.data.axes[0].quantity for ds in self.datasets]
        xunits = [ds.data.axes[0].unit for ds in self.datasets]
        yquantities = [ds.data.axes[1].quantity for ds in self.datasets]
        yunits = [ds.data.axes[1].unit for ds in self.datasets]
        if self.parameters["axes"][0].quantity:
            xlabel = self._create_axis_label_string(
                self.parameters["axes"][0]
            )
        elif aspecd.utils.all_equal(xquantities) and aspecd.utils.all_equal(
            xunits
        ):
            xlabel = self._create_axis_label_string(
                self.datasets[0].data.axes[0]
            )
        elif self.properties.axes.xlabel:
            xlabel = self.properties.axes.xlabel
        else:
            xlabel = ""
        if self.parameters["axes"][1].quantity:
            ylabel = self._create_axis_label_string(
                self.parameters["axes"][1]
            )
        elif aspecd.utils.all_equal(yquantities) and aspecd.utils.all_equal(
            yunits
        ):
            ylabel = self._create_axis_label_string(
                self.datasets[0].data.axes[1]
            )
        elif self.properties.axes.ylabel:
            ylabel = self.properties.axes.ylabel
        else:
            ylabel = ""
        self.axes.set_xlabel(xlabel)
        self.axes.set_ylabel(ylabel)


class MultiPlotter1D(MultiPlotter):
    # noinspection PyUnresolvedReferences
    """
    1D plots of multiple datasets.

    Convenience class taking care of 1D plots of multiple datasets. The type
    of plot can be set in its :attr:`aspecd.plotting.MultiPlotter1D.type`
    attribute. Allowed types are stored in the
    :attr:`aspecd.plotting.MultiPlotter1D.allowed_types` attribute.

    Quite a number of properties for figure, axes, and line can be set
    using the :attr:`aspecd.plotting.MultiPlotter1D.properties` attribute.
    For details, see the documentation of its respective class,
    :class:`aspecd.plotting.MultiPlot1DProperties`.

    To perform the plot, call the :meth:`plot` method of the plotter directly.

    Attributes
    ----------
    drawings : :class:`list`
        Actual graphical representations of the data of the datasets

    properties : :class:`aspecd.plotting.MultiPlot1DProperties`
        Properties of the plot, defining its appearance

        For the properties that can be set this way, see the documentation
        of the :class:`aspecd.plotting.MultiPlotProperties` class.

    parameters : :class:`dict`
        All parameters necessary for this step.

        Additionally, to those from :class:`aspecd.plotting.MultiPlotter`,
        the following parameters are allowed:

        switch_axes : :class:`bool`
            Whether to switch *x* and *y* axes

            Normally, the first axis is used as *x* axis, and the second
            as *y* axis. Sometimes, switching this assignment is
            necessary or convenient.

            Default: False

        tight: :class:`str`
            Whether to set the axes limits tight to the data

            Possible values: 'x', 'y', 'both'

            Default: ''

    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. Of course, all parameters settable
    for the superclasses can be set as well. The examples focus each on a
    single aspect.

    In the simplest case, just invoke the plotter with default values:

    .. code-block:: yaml

       - kind: multiplot
         type: MultiPlotter1D
         properties:
           filename: output.pdf

    To change the settings of each individual line (here the colour and label),
    supposing you have three lines, you need to specify the properties in a
    list for each of the drawings:

    .. code-block:: yaml

       - kind: multiplot
         type: MultiPlotter1D
         properties:
           filename: output.pdf
           properties:
             drawings:
               - color: '#FF0000'
                 label: foo
               - color: '#00FF00'
                 label: bar
               - color: '#0000FF'
                 label: foobar

    .. important::
        If you set colours using the hexadecimal RGB triple prefixed by
        ``#``, you need to explicitly tell YAML that these are strings,
        surrounding the values by quotation marks.

    Suppose you want to set identical properties for all lines. This is
    possible as well, by not providing the ``drawings`` key (plural) but
    the ``drawing`` key (singular) - and of course, this time not a list:

    .. code-block:: yaml

       - kind: multiplot
         type: MultiPlotter1D
         properties:
           properties:
             drawing:
               color: '#FF0000'

    Of course, line plots are not the only plot type available. Check the
    :attr:`MultiPlotter1D.allowed_types` attribute for further details. To
    make a semilogy plot (*i.e.*, with logarithmic *y* axis), invoke the
    plotter as follows:

    .. code-block:: yaml

       - kind: multiplot
         type: MultiPlotter1D
         properties:
           type: semilogy
           filename: output.pdf

    .. important::

        As the logarithm of negative values is not defined, usually having a
        logarithmic axis with negative values will lead to unexpected
        results. Matplotlib defaults to clipping the invalid values. To help
        you with debugging the unexpected results, a warning will be logged
        (and printed to the terminal when serving a recipe) in case a
        logarithmic axis is affected by negative values. In such case,
        the easiest is to add an offset to your data, using
        :class:`aspecd.processing.ScalarAlgebra`.

    Sometimes it is convenient to switch the *x* and *y* axes, *e.g.* in
    context of 2D datasets where slices along both dimensions should be
    displayed together with the 2D data and next to the respective axes. To
    achieve this, set the ``switch_axes`` parameter accordingly:

    .. code-block:: yaml

       - kind: multiplot
         type: MultiPlotter1D
         properties:
           parameters:
             switch_axes: true
           filename: output.pdf


    .. versionchanged:: 0.7
        New parameters ``switch_axes`` and ``tight``

    .. versionchanged:: 0.9
        Issue warning with log plotters and negative values

    """

    def __init__(self):
        super().__init__()
        self.description = "1D plotting step for multiple datasets"
        self.drawings = []
        self.properties = MultiPlot1DProperties()
        self.parameters["switch_axes"] = False
        self.parameters["tight"] = ""
        self._type = "plot"
        self._allowed_types = [
            "plot",
            "step",
            "loglog",
            "semilogx",
            "semilogy",
        ]

    @property
    def type(self):
        """
        Get or set the plot type.

        Types need to be methods of the :class:`matplotlib.axes.Axes` class.

        Allowed plot types are stored in the
        :attr:`aspecd.plotting.SinglePlotter1D.allowed_types` attribute.

        Default: 'plot'

        Raises
        ------
        TypeError
            Raised in case of wrong type

        """
        return self._type

    @property
    def allowed_types(self):
        """
        Return the allowed plot types.

        Currently, the allowed types are: ``plot``, ``step``, ``loglog``,
        ``semilogx``, ``semilogy``.

        Returns
        -------
        allowed_types: :class:`list`
            List of strings

        """
        return self._allowed_types

    @type.setter
    def type(self, plot_type=None):
        if plot_type not in self.allowed_types:
            raise TypeError
        self._type = plot_type

    @staticmethod
    def applicable(data):
        """Check whether plot is applicable to the given dataset.

        Checks for the dimension of the data of the dataset, i.e. the
        :attr:`aspecd.dataset.Data.data` attribute. Returns `True` if data
        are one-dimensional, and `False` otherwise.

        Returns
        -------
        applicable : :class:`bool`
            `True` if successful, `False` otherwise.

        """
        return data.data.ndim == 1

    def _create_plot(self):
        """Actual drawing of datasets"""
        plot_function = getattr(self.axes, self.type)
        self._check_values_for_logplot()
        self.drawings = []
        for idx, data in enumerate(self.data):
            if not self.properties.drawings[idx].label:
                self.properties.drawings[idx].label = self.datasets[idx].label
            if self.parameters["switch_axes"]:
                (drawing,) = plot_function(
                    data.data,
                    data.axes[0].values,
                    label=self.properties.drawings[idx].label,
                )
            else:
                (drawing,) = plot_function(
                    data.axes[0].values,
                    data.data,
                    label=self.properties.drawings[idx].label,
                )
            self.drawings.append(drawing)
        if self.parameters["tight"]:
            axes_limits = [
                min(data.axes[0].values.min() for data in self.data),
                max(data.axes[0].values.max() for data in self.data),
            ]
            data_limits = [
                min(data.data.min() for data in self.data),
                max(data.data.max() for data in self.data),
            ]
            if self.parameters["tight"] in ("x", "both"):
                if self.parameters["switch_axes"]:
                    self.axes.set_xlim(data_limits)
                else:
                    self.axes.set_xlim(axes_limits)
            if self.parameters["tight"] in ("y", "both"):
                if self.parameters["switch_axes"]:
                    self.axes.set_ylim(axes_limits)
                else:
                    self.axes.set_ylim(data_limits)

    def _check_values_for_logplot(self):
        issue_warning = False
        for data in self.data:
            if self.parameters["switch_axes"]:
                xvalues = data.data
                yvalues = data.axes[0].values
            else:
                xvalues = data.axes[0].values
                yvalues = data.data
            if "semilogy" in self.type and np.min(yvalues) < 0:
                issue_warning = True
            if "semilogx" in self.type and np.min(xvalues) < 0:
                issue_warning = True
            if "loglog" in self.type and (
                np.min(xvalues) < 0 or np.min(yvalues) < 0
            ):
                issue_warning = True
        if issue_warning:
            logger.warning(
                "Negative values with %s plot detected.", self.type
            )

    def _set_axes_labels(self):
        super()._set_axes_labels()
        if self.parameters["switch_axes"]:
            old_xlabel = self.axes.get_xlabel()
            old_ylabel = self.axes.get_ylabel()
            self.axes.set_xlabel(old_ylabel)
            self.axes.set_ylabel(old_xlabel)


class MultiPlotter1DStacked(MultiPlotter1D):
    # noinspection PyUnresolvedReferences
    """
    Stacked 1D plots of multiple datasets.

    Convenience class taking care of 1D plots of multiple datasets. The type
    of plot can be set in its :attr:`aspecd.plotting.MultiPlotter1D.type`
    attribute. Allowed types are stored in the
    :attr:`aspecd.plotting.MultiPlotter1D.allowed_types` attribute.

    Quite a number of properties for figure, axes, and line can be set
    using the :attr:`aspecd.plotting.MultiPlotter1D.properties` attribute.
    For details, see the documentation of its respective class,
    :class:`aspecd.plotting.MultiPlot1DProperties`.

    To perform the plot, call the :meth:`plot` method of the plotter directly.

    Attributes
    ----------
    parameters : :class:`dict`
        All parameters necessary for this step.

        offset : :class:`float`
            The offset used for stacking the individual lines of the plot.

            If not provided, automatically a best fit will be calculated.

            Default: None

        show_zero_lines : :class:`bool`
            Whether to show zero lines in the plot

            Regardless of whether you set this to true, zero lines will
            only be added to the final plot if the zero value is within
            the current axes limits.

            Zero line properties can be set via the
            :attr:`aspecd.plotting.Plotter.properties` attribute.

            Default: False

    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. Of course, all parameters settable
    for the superclasses can be set as well. The examples focus each on a
    single aspect.

    In the simplest case, just invoke the plotter with default values:

    .. code-block:: yaml

       - kind: multiplot
         type: MultiPlotter1DStacked
         properties:
           filename: output.pdf

    To change the settings of each individual line (here the colour and label),
    supposing you have three lines, you need to specify the properties in a
    list for each of the drawings:

    .. code-block:: yaml

       - kind: multiplot
         type: MultiPlotter1DStacked
         properties:
           filename: output.pdf
           properties:
             drawings:
               - color: '#FF0000'
                 label: foo
               - color: '#00FF00'
                 label: bar
               - color: '#0000FF'
                 label: foobar

    .. important::
        If you set colours using the hexadecimal RGB triple prefixed by
        ``#``, you need to explicitly tell YAML that these are strings,
        surrounding the values by quotation marks.

    Sometimes you want to have horizontal "zero lines" appear for each
    individual trace of the stacked plot. This can be achieved explicitly
    setting the "show_zero_lines" parameter to "True" that is set to "False"
    by default. The offset is automatically set that spectra don't overlap
    but can also be chosen freely (in units of the intensity):

    .. code-block:: yaml

       - kind: multiplot
         type: MultiPlotter1DStacked
         properties:
           filename: output.pdf
           parameters:
             show_zero_lines: True
             offset: 0.3

    """

    def __init__(self):
        super().__init__()
        self.description = (
            "1D plotter for stacked display of multiple datasets"
        )
        self.parameters["show_zero_lines"] = False
        # noinspection PyTypeChecker
        self.parameters["offset"] = None

    def _create_plot(self):
        """Actual drawing of datasets"""
        if not self.parameters["offset"]:
            offset = (
                max(
                    [
                        abs(self.datasets[0].data.data.min()),
                        abs(self.datasets[0].data.data.max()),
                    ]
                )
                * 1.05
            )
            self.parameters["offset"] = offset
        else:
            offset = self.parameters["offset"]
        plot_function = getattr(self.axes, self.type)
        self.drawings = []
        for idx, dataset in enumerate(self.datasets):
            if not self.properties.drawings[idx].label:
                self.properties.drawings[idx].label = dataset.label
            if self.parameters["switch_axes"]:
                (drawing,) = plot_function(
                    dataset.data.data - idx * offset,
                    dataset.data.axes[0].values,
                    label=self.properties.drawings[idx].label,
                )
            else:
                (drawing,) = plot_function(
                    dataset.data.axes[0].values,
                    dataset.data.data - idx * offset,
                    label=self.properties.drawings[idx].label,
                )
            self.drawings.append(drawing)
        self.axes.tick_params(
            axis="y",
            which="both",
            left=False,
            right=False,
            labelleft=False,
            labelright=False,
        )
        if self.parameters["tight"]:
            axes_limits = [
                min(
                    dataset.data.axes[0].values.min()
                    for dataset in self.datasets
                ),
                max(
                    dataset.data.axes[0].values.max()
                    for dataset in self.datasets
                ),
            ]
            data_limits = [
                min(dataset.data.data.min() for dataset in self.datasets),
                max(dataset.data.data.max() for dataset in self.datasets),
            ]
            data_limits[0] -= offset * (len(self.datasets) - 1)
            if self.parameters["tight"] in ("x", "both"):
                if self.parameters["switch_axes"]:
                    self.axes.set_xlim(data_limits)
                else:
                    self.axes.set_xlim(axes_limits)
            if self.parameters["tight"] in ("y", "both"):
                if self.parameters["switch_axes"]:
                    self.axes.set_ylim(axes_limits)
                else:
                    self.axes.set_ylim(data_limits)

    def _add_zero_lines(self):
        if self.parameters["show_zero_lines"]:
            for idx in range(len(self.datasets)):
                offset = -idx * self.parameters["offset"]
                properties = self.properties.zero_lines.to_dict()
                # noinspection PyUnresolvedReferences
                properties.update({"zorder": 1})
                self.axes.axhline(
                    y=offset,
                    **properties,  # noqa
                )


class CompositePlotter(Plotter):
    """Base class for plots consisting of multiple axes.

    The underlying idea of composite plotters is to use a dedicated
    existing plotter for each axis and assign this plotter to the list of
    plotters of the CompositePlotter object. Thus the actual plotting task
    is left to the individual plotter and the CompositePlotter only takes
    care of the specifics of plots consisting of more than one axis.

    In the framework of the CompositePlotter you can define the grid within
    which the axes are arranged. First, you define the grid dimension as a
    two-element vector, and second you define the subplot locations as list
    of four-element vectors. For details, see the documentation of the
    attributes :attr:`grid_dimensions` and :attr:`subplot_locations` below.

    For each of the subplots, define a plotter and add the object to the
    list of plotters, the attribute :attr:`plotter`. Make sure to equip each
    of these plotters with the necessary information. To actually plot,
    use the :meth:`plot` method of the CompositePlotter object.

    If you would like to display a single dataset in several ways within one
    and the same figure window, have a look at the
    :class:`SingleCompositePlotter` class. This class pretty much behaves
    like an ordinary SinglePlotter, where you can (and should) use the
    :meth:`aspecd.dataset.Dataset.plot` method to plot.

    .. note::
        When writing classes based on this class, do *not* override the
        :meth:`_create_plot` method. Generally, providing a list of plotters
        for each of the axes should be sufficient, and the CompositePlotter
        will call the :meth:`plot` property of each of these plotters
        automatically for you.

    Examples
    --------
    A quick example how a recipe part using a composite plotter may look like.
    Both plotters ``raw-data`` and ``processed-data`` are previously defined
    figures using *different datasets*. Therefore, it is important to give
    results of a processing task a unique identifier if it is used in such a
    composite plotter.

    .. code-block:: yaml

        - kind: compositeplot
          type: CompositePlotter
          properties:
            plotter:
            - raw-data
            - processed-data
            filename: comparison.pdf
            grid_dimensions: [1, 2]
            subplot_locations:
            - [0, 0, 1, 1]
            - [0, 1, 1, 1]

    Suppose you have a more complex plot with three axes, and you want to
    share the *x* axes only for those axes in the same column(s).

    .. code-block:: yaml

        - kind: compositeplot
          type: CompositePlotter
          properties:
            properties:
              grid_spec:
                hspace: 0
            plotter:
            - plotter1
            - plotter2
            - plotter3
            filename: comparison.pdf
            grid_dimensions: [2, 2]
            subplot_locations:
            - [0, 0, 1, 1]
            - [1, 0, 1, 1]
            - [0, 1, 2, 1]
            sharex: True

    In this case, only the two axes in the left column will share their
    *x* axes, and as you have defined the top axes *first*, the axes below
    will share their *x* axis with the top axes. Further note that
    ``hspace``, *i.e.* the vertical space between the axes, has been set
    to zero (the property starts with a "h" for height).

    You could do the same for three axes where you would like to have the
    *y* axes of those plots in the same row shared:

    .. code-block:: yaml

        - kind: compositeplot
          type: CompositePlotter
          properties:
            properties:
              grid_spec:
                wspace: 0
            plotter:
            - plotter1
            - plotter2
            - plotter3
            filename: comparison.pdf
            grid_dimensions: [2, 2]
            subplot_locations:
            - [0, 0, 1, 1]
            - [1, 1, 1, 1]
            - [1, 0, 1, 2]
            sharey: True

    In this case, only the two axes in the top row will share their *y*
    axes, and as you have defined the left axes *first*, the axes to the
    right will share their *y* axis with the left axes. Further note that
    ``wspace``, *i.e.* the horizontal space between the axes, has been set
    to zero (the property starts with a "w" for width).

    Attributes
    ----------
    grid_dimensions : :class:`list`
        Dimensions of the grid used to layout the figure

        two elements: number of rows, number of columns

        Default: [1, 1]

    grid_spec : :class:`matplotlib.gridspec.GridSpec`
        Grid layout used to place the subplots within the figure.

        The properties of the grid layout can be controlled using the
        :attr:`CompositePlotProperties.grid_spec` attribute that is part of
        :attr:`properties` attribute.

    subplot_locations : :class:`list`
        List of subplot locations

        Each subplot location is a list with four numeric elements:
        [start_row, start_column, row_span, column_span]

        Default: [[0, 0, 1, 1]]

    axes_positions: :class:`list`
        List of axes positions for fine-adjustment

        Each axes position is a list with four numeric elements:
        [left_scale, bottom_scale, width_scale, height_scale] that are
        applied in the following way to the position of the individual axes::

            [left, bottom, width, height] = ax[idx].get_position().bounds
            new_position = [
                left + left_scale * width, bottom + bottom_scale * height,
                width * width_scale, height * height_scale
            ]
            ax[idx].set_position(new_position)

        Values can be both, positive and negative floats. Note, however,
        that negative values for the width and height parameter will mirror
        the axes accordingly.

        Default: []

    plotter : :class:`list`
        List of plotters

        Plotters are objects of type :class:`aspecd.plotting.Plotter`.

        Upon calling :meth:`aspecd.plotting.Plotter.plot`, for each axes in
        the list of axes, the corresponding plotter will be accessed and its
        :meth:`aspecd.plotting.Plotter.plot` method called.

        .. note::
            When the plotters are operating on the same dataset which got
            processed in between, both will use and display the dataset *after*
            processing. To prevent this, assign the result of the processing
            step a unique name.

    sharex : :class:`bool` | :class:`str`
        Whether to share the *x* axes of all subplots.

        If set to ``True`` or ``all``, all *x* axes are shared, starting with
        the first defined axes.

        If set to one of ``["col", "columns", "column-wise"]``, the *x*
        axes in each column are shared, starting with the first defined
        axes in each column.

        In both cases, only the outer *x* axes will be shown.

        Typically, you will want to set the ``hspace`` property in
        :attr:`CompositePlotProperties.grid_spec` to a small value.

        .. versionadded:: 0.10

    sharey : :class:`bool` | :class:`str`
        Whether to share the *y* axes of all subplots.

        If set to ``True`` or ``all``, all *y* axes are shared, starting with
        the first defined axes.

        If set to one of ``["row", "rows", "row-wise"]``, the *y* axes in
        each row are shared, starting with the first defined axes in each
        row.

        In both cases, only the outer *y* axes will be shown.

        Typically, you will want to set the ``wspace`` property in
        :attr:`CompositePlotProperties.grid_spec` to a small value.

        .. versionadded:: 0.10

    properties : :class:`aspecd.plotting.CompositePlotProperties`
        Properties of the plot, defining its appearance

        These properties are used for the CompositePlot as such, and if set
        will override those properties of the individual plotters used to
        fill the axes of the CompositePlot. For details, see the
        documentation of the :class:`aspecd.plotting.CompositePlotProperties`
        class.

    Raises
    ------
    aspecd.exceptions.MissingPlotterError
        Raised if the number of plotters does not match the number of axes

        Note that for each axes you need a corresponding plotter.

    """

    def __init__(self):
        super().__init__()
        self.description = "Composite plotter displaying several axes"
        self.axes = []
        self.grid_dimensions = [1, 1]
        self.grid_spec = None
        self.subplot_locations = [[0, 0, 1, 1]]
        self.axes_positions = []
        self.plotter = []
        self.sharex = False
        self.sharey = False
        self.properties = CompositePlotProperties()
        self.__kind__ = "compositeplot"

    @property
    def axes(self):
        """
        Axes of the composite plotter.

        Will eventually be objects of subtypes of
        :class:`matplotlib.axes.Axes` and populated upon calling
        :meth:`aspecd.plotting.Plotter.plot`.

        Returns
        -------
        axes : :class:`list`
            List of axes

        """
        return self._axes

    @axes.setter
    def axes(self, axes=None):
        self._axes_set_externally = True
        self._axes = axes

    def to_dict(self, remove_empty=False):
        """
        Create dictionary containing public attributes of an object.

        For some reason, :class:`matplotlib.gridspec.GridSpec` leads to an
        infinite recursion, hence the attribute is emptied before creating
        the dict, and afterwards readded.

        Parameters
        ----------
        remove_empty : :class:`bool`
            Whether to remove keys with empty values

            Default: False

        Returns
        -------
        public_attributes : :class:`collections.OrderedDict`
            Ordered dictionary containing the public attributes of the object

            The order of attribute definition is preserved

        """
        grid_spec = copy.copy(self.grid_spec)
        self.grid_spec = []
        dict_ = super().to_dict(remove_empty=remove_empty)
        self.grid_spec = grid_spec
        return dict_

    def _create_figure_and_axes(self):
        self._figure = plt.figure()
        # noinspection PyArgumentList
        self.grid_spec = self.figure.add_gridspec(
            self.grid_dimensions[0],
            self.grid_dimensions[1],
            **self.properties.grid_spec.to_dict(),
        )
        for subplot in self.subplot_locations:
            self.axes.append(
                self.figure.add_subplot(
                    self.grid_spec[
                        subplot[0] : subplot[0] + subplot[2],
                        subplot[1] : subplot[1] + subplot[3],
                    ]
                )
            )

    def _create_plot(self):
        if not self.plotter or len(self.plotter) < len(self.axes):
            raise aspecd.exceptions.MissingPlotterError
        plotter_copy = [copy.copy(plotter) for plotter in self.plotter]
        for plotter in plotter_copy:
            plotter.style = self.style
            if hasattr(plotter, "drawings"):
                plotter.drawings = []
        # Needs to be applied before plotting for certain plotters
        self._share_axes()
        for idx, axes in enumerate(self.axes):
            plotter_copy[idx].figure = self.figure
            plotter_copy[idx].axes = axes
            plotter_copy[idx].properties.axes.apply(axes)
            plotter_copy[idx].plot()
            self._apply_figure_properties()
        # Needs to be reapplied after plotting again to remove labels
        self._share_axes()
        for idx, position in enumerate(self.axes_positions):
            left, bottom, width, height = self.axes[idx].get_position().bounds
            new_position = [
                left + position[0] * width,
                bottom + position[1] * height,
                position[2] * width,
                position[3] * height,
            ]
            self.axes[idx].set_position(new_position)

    def _share_axes(self):
        if self.sharex:
            if isinstance(self.sharex, bool) or self.sharex == "all":
                self._sharex()
            elif self.sharex in ["col", "column", "column-wise"]:
                self._sharex_column_wise()
        if self.sharey:
            if isinstance(self.sharey, bool) or self.sharey == "all":
                self._sharey()
            elif self.sharey in ["row", "rows", "row-wise"]:
                self._sharey_row_wise()

    def _sharex(self):
        for axes in self.axes:
            axes._label_outer_xaxis(skip_non_rectangular_axes=False)  # noqa
        for idx, axes in enumerate(self.axes[:-1]):
            self.axes[idx + 1].sharex(axes)

    def _sharex_column_wise(self):
        columns = []
        for col in range(self.grid_dimensions[1]):
            axes = []
            for idx, location in enumerate(self.subplot_locations):
                if location[1] == col:
                    axes.append(self.ax[idx])
            columns.append(axes)

        for column in columns:
            if len(column) > 1:
                for axes in column:
                    axes._label_outer_xaxis(  # noqa
                        skip_non_rectangular_axes=False
                    )
                for idx, axes in enumerate(column[:-1]):
                    column[idx + 1].sharex(axes)

    def _sharey(self):
        for axes in self.axes:
            axes._label_outer_yaxis(skip_non_rectangular_axes=False)  # noqa
        for idx, axes in enumerate(self.axes[:-1]):
            self.axes[idx + 1].sharey(axes)

    def _sharey_row_wise(self):
        rows = []
        for row in range(self.grid_dimensions[0]):
            axes = []
            for idx, location in enumerate(self.subplot_locations):
                if location[0] == row:
                    axes.append(self.ax[idx])
            rows.append(axes)

        for row in rows:
            if len(row) > 1:
                for axes in row:
                    axes._label_outer_yaxis(  # noqa
                        skip_non_rectangular_axes=False
                    )
                for idx, axes in enumerate(row[:-1]):
                    row[idx + 1].sharey(axes)


class SingleCompositePlotter(CompositePlotter):
    """Composite plotter for single datasets

    This composite plotter is used for different representations of one and the
    same dataset in multiple axes contained in one figure. In this respect,
    it works like all the other ordinary single plotters derived from
    :class:`SinglePlotter`, *i.e.* it usually gets called by using the dataset's
    :meth:`aspecd.dataset.Dataset.plot` method.

    As with the generic :class:`CompositePlotter`, specify both the axes
    grid and locations as well as the plotters to use for each individual
    plot. Calling :meth:`plot` by means of
    :meth:`aspecd.dataset.Dataset.plot` will assign the dataset to each of
    the individual plotters and make them plot the data contained in the
    dataset.

    Attributes
    ----------
    dataset : :class:`aspecd.dataset.Dataset`
        Dataset the plotting should be done for

    Raises
    ------
    aspecd.exceptions.MissingDatasetError
        Raised when no dataset exists to act on

    aspecd.exceptions.NotApplicableToDatasetError
        Raised when processing step is not applicable to dataset

    """

    def __init__(self):
        super().__init__()
        self.dataset = None
        self.description = "Composite plotter for single dataset"

    def plot(self, dataset=None, from_dataset=False):
        """Perform the actual plotting on the given dataset.

        If no dataset is set as property in the object, the method will
        raise a respective exception. The dataset object :meth:`plot` method
        always assigns its dataset as the respective dataset attribute of
        the plotter class.

        The actual plotting should be implemented within the non-public
        method :meth:`_create_plot`. Besides that, the applicability of the
        plotting to the given dataset will be checked automatically. These
        checks should be implemented in the method :meth:`applicable`.

        Parameters
        ----------
        dataset : :class:`aspecd.dataset.Dataset`
            dataset to perform plot for

        from_dataset : `boolean`
            whether we are called from within a dataset

            Defaults to "False" and shall never be set manually.

        Returns
        -------
        dataset : :class:`aspecd.dataset.Dataset`
            dataset plot has been performed for

        Raises
        ------
        aspecd.exceptions.NotApplicableToDatasetError
            Raised when plotting is not applicable to dataset
        aspecd.exceptions.MissingDatasetError
            Raised when no dataset exists to act on

        """
        self._assign_dataset(dataset)
        self._call_from_dataset(from_dataset)
        return self.dataset

    def create_history_record(self):
        """
        Create history record to be added to the dataset.

        Usually, this method gets called from within the
        :meth:`aspecd.dataset.plot` method of the
        :class:`aspecd.dataset.Dataset` class and ensures the history of
        each plotting step to get written properly.

        Returns
        -------
        history_record : :class:`aspecd.history.PlotHistoryRecord`
            history record for plotting step

        """
        history_record = aspecd.history.PlotHistoryRecord(
            package=self.dataset.package_name
        )
        history_record.plot = aspecd.history.SinglePlotRecord(plotter=self)
        history_record.plot.preprocessing = copy.deepcopy(
            self.dataset.history
        )
        return history_record

    def _assign_dataset(self, dataset):
        if not dataset:
            if not self.dataset:
                raise aspecd.exceptions.MissingDatasetError
        else:
            self.dataset = dataset
        for plotter in self.plotter:
            if hasattr(plotter, "dataset"):
                plotter.dataset = self.dataset

    def _call_from_dataset(self, from_dataset):
        if not from_dataset:
            self.dataset.plot(self)
        else:
            self._check_applicability()
            tasks = copy.copy(self.dataset.tasks)
            representations = copy.copy(self.dataset.representations)
            super().plot()
            self.dataset.representations = representations
            self.dataset.tasks = tasks

    def _check_applicability(self):
        if not self.applicable(self.dataset):
            message = (
                f"{self.name} not applicable to dataset with id "
                f"{self.dataset.id}"
            )
            raise aspecd.exceptions.NotApplicableToDatasetError(
                message=message
            )


class Saver:
    """Base class for saving plots.

    For basic saving of plots, no subclassing is necessary, as the
    :meth:`save` method uses :meth:`matplotlib.figure.Figure.savefig` and
    can cope with all possible parameters via the :attr:`parameters` property.

    Attributes
    ----------
    filename : :class:`str`
        Name of the file the plot should get saved to
    parameters : :class:`dict`
        Key-value store of parameters for saving.

        See :meth:`matplotlib.figure.Figure.savefig` for details and
        available options.
    plotter : :class:`aspecd.plotting.Plotter`
        Plotter whose plot should be saved.

    Raises
    ------
    aspecd.exceptions.MissingFilenameError
        Raised if no filename is provided for saver.
    aspecd.exceptions.MissingPlotError
        Raised if no plot is provided to act upon.

    """

    def __init__(self, filename=None):
        self.filename = filename
        self.parameters = {}
        self.plotter = None

    def save(self, plotter=None):
        """Save the plot to a file.

        If no plotter is provided at method call, but is set as property in the
        Saver object, the :meth:`aspecd.plotting.Plotter.save` method of the
        plotter will be called.

        If no plotter is provided at method call nor as property of the object,
        the method will raise a respective exception.

        The actual saving is implemented within the private method
        :meth:`_save_plot`.

        Parameters
        ----------
        plotter : `aspecd.plotting.Plotter`
            plot to be saved

        Raises
        ------
        aspecd.exceptions.MissingFilenameError
            Raised if no filename is provided for saver.
        aspecd.exceptions.MissingPlotError
            Raised if no plot is provided to act upon.

        """
        if not self.filename:
            raise aspecd.exceptions.MissingFilenameError
        if not plotter:
            if self.plotter:
                self.plotter.save(self)
            else:
                raise aspecd.exceptions.MissingPlotError
        else:
            self.plotter = plotter
        self._save_plot()

    def _save_plot(self):
        """Perform the actual saving of the plot.

        The implementation of the actual saving goes in here in all
        classes inheriting from Saver. This method is automatically
        called by :meth:`save`.

        In the simplest case, saving is a call to :meth:`savefig` of the
        figure to save. To access this figure, use the property
        :attr:`plotter.figure`.

        As filenames cannot be of arbitrary length (and the limits depend on
        operating and probably file system), if the respective error is
        raised, the file basename is replaced by the MD5 hash of itself.

        .. versionchanged:: 0.8.2
            Handling of too long filenames

        """
        self._add_file_extension()
        try:
            self.plotter.figure.savefig(
                self.filename, dpi=self.plotter.figure.dpi, **self.parameters
            )
        except OSError as os_error:
            if os_error.errno == errno.ENAMETOOLONG:
                file_basename, file_extension = os.path.splitext(
                    self.filename
                )
                self.filename = "".join(
                    [
                        hashlib.md5(
                            file_basename.encode(), usedforsecurity=False
                        ).hexdigest(),
                        file_extension,
                    ]
                )
            else:
                raise

    def _add_file_extension(self):
        """Add file extension to filename if available.

        Check whether an export file format has been explicitly given,
        and if so, add proper extension to filename.

        Two cases are possible, and are dealt with as follows:

        (1) No file extension, but format specified.

        The appropriate file extension (same as format) will be added.

        (2) File extension does not match format specifier.

        The file extension will be replaced by the one specified in format.

        """
        file_basename, file_extension = os.path.splitext(self.filename)
        if "format" in self.parameters:
            if file_extension != self.parameters["format"]:
                self.filename = ".".join(
                    [file_basename, self.parameters["format"]]
                )
            elif not file_extension:
                self.filename = ".".join(
                    [self.filename, self.parameters["format"]]
                )


class Caption(aspecd.utils.Properties):
    """
    Caption for figures.

    Attributes
    ----------
    title: :class:`str`
        usually one sentence describing the intent of the figure

        Often plotted bold-face in a figure caption.

    text: :class:`str`
        additional text directly following the title

        Contains more information about the plot. Ideally, a figure caption
        is self-contained such that it explains the figure sufficiently to
        understand its intent and content without needing to read all the
        surrounding text.

    parameters: :class:`list`
        names of parameters that should be included in the figure caption

        Usually, these parameters get included at the very end of a figure
        caption.

    """

    def __init__(self):
        super().__init__()
        self.title = ""
        self.text = ""
        self.parameters = []


class PlotProperties(aspecd.utils.Properties):
    """
    Properties of a plot, defining its appearance.

    Attributes
    ----------
    figure : :class:`aspecd.plotting.FigureProperties`
        Properties of the figure as such

        For the properties that can be set this way, see the documentation
        of the :class:`aspecd.plotting.FigureProperties` class.

    axes : :class:`aspecd.plotting.AxesProperties`
        Properties of the axes.

        For the properties that can be set this way, see the documentation
        of the :class:`aspecd.plotting.AxesProperties` class.

    legend : :class:`aspecd.plotting.LegendProperties`
        Properties of the legend.

        For the properties that can be set this way, see the documentation
        of the :class:`aspecd.plotting.LegendProperties` class.

    zero_lines : :class:`aspecd.plotting.LineProperties`
        Properties of the zero lines.

        For the properties that can be set this way, see the documentation
        of the :class:`aspecd.plotting.LineProperties` class.

        Default values for the zero lines are:

        * color: #cccccc


    Raises
    ------
    aspecd.exceptions.MissingPlotterError
        Raised if no plotter is provided.


    .. versionchanged:: 0.12
        Moved :attr:`axes` up to this class from subclasses.

    """

    def __init__(self):
        super().__init__()
        self.figure = FigureProperties()
        self.axes = AxesProperties()
        self.legend = LegendProperties()
        self.zero_lines = LineProperties()
        # Set default properties
        self.zero_lines.color = "#cccccc"

    def apply(self, plotter=None):
        """
        Apply properties to plot.

        In this generic class having only figure properties, only these
        properties are set. Classes derived from
        :class:`aspecd.plotting.PlotProperties` need to take care of
        setting all available properties.

        Parameters
        ----------
        plotter: :class:`aspecd.plotting.Plotter`
            Plotter the properties should be applied to.

        Raises
        ------
        aspecd.exceptions.MissingPlotterError
            Raised if no plotter is provided.

        """
        if not plotter:
            raise aspecd.exceptions.MissingPlotterError
        self.figure.apply(figure=plotter.figure)
        if isinstance(plotter.axes, list):
            for axes in plotter.axes:
                self.axes.apply(axes=axes)
        else:
            self.axes.apply(axes=plotter.axes)


class SinglePlotProperties(PlotProperties):
    """
    Properties of a single plot, defining its appearance.

    Attributes
    ----------
    figure : :class:`aspecd.plotting.FigureProperties`
        Properties of the figure as such

        For the properties that can be set this way, see the documentation
        of the :class:`aspecd.plotting.FigureProperties` class.

    axes : :class:`aspecd.plotting.AxesProperties`
        Properties of the axes.

        For the properties that can be set this way, see the documentation
        of the :class:`aspecd.plotting.AxesProperties` class.

    grid : :class:`aspecd.plotting.GridProperties`
        Properties of the grid.

        For the properties that can be set this way, see the documentation
        of the :class:`aspecd.plotting.GridProperties` class.

    drawing : :class:`aspecd.plotting.DrawingProperties`
        Properties of the line within a plot

        For the properties that can be set this way, see the documentation
        of the :class:`aspecd.plotting.DrawingProperties` class.

    Raises
    ------
    aspecd.exceptions.MissingPlotterError
        Raised if no plotter is provided.

    """

    def __init__(self):
        super().__init__()
        self.grid = GridProperties()
        self.drawing = DrawingProperties()

    def apply(self, plotter=None):
        """
        Apply properties to plot.

        Parameters
        ----------
        plotter: :class:`aspecd.plotting.SinglePlotter`
            Plotter the properties should be applied to.

        Raises
        ------
        aspecd.exceptions.MissingPlotterError
            Raised if no plotter is provided.

        """
        super().apply(plotter=plotter)
        self.axes.apply(axes=plotter.axes)
        self.grid.apply(axes=plotter.axes)
        if plotter.drawing:
            self.drawing.apply(drawing=plotter.drawing)


class SinglePlot1DProperties(SinglePlotProperties):
    """
    Properties of a 1D single plot, defining its appearance.

    Attributes
    ----------
    drawing : :class:`aspecd.plotting.LineProperties`
        Properties of the line within a plot

        For the properties that can be set this way, see the documentation
        of the :class:`aspecd.plotting.LineProperties` class.

    Raises
    ------
    aspecd.exceptions.MissingPlotterError
        Raised if no plotter is provided.

    """

    def __init__(self):
        super().__init__()
        self.drawing = LineProperties()


class SinglePlot2DProperties(SinglePlotProperties):
    """
    Properties of a 2D single plot, defining its appearance.

    Attributes
    ----------
    drawing : :class:`aspecd.plotting.SurfaceProperties`
        Properties of the surface within a plot

        For the properties that can be set this way, see the documentation
        of the :class:`aspecd.plotting.SurfaceProperties` class.

    colorbar : :class:`aspecd.plotting.ColorbarProperties`
        Properties of the colorbar (optionally) added to a plot

        For the properties that can be set this way, see the documentation
        of the :class:`aspecd.plotting.ColorbarProperties` class.

        .. versionadded:: 0.9


    Raises
    ------
    aspecd.exceptions.MissingPlotterError
        Raised if no plotter is provided.

    """

    def __init__(self):
        super().__init__()
        self.drawing = SurfaceProperties()
        self.colorbar = ColorbarProperties()
        self._colormap = ""
        self._include_in_to_dict = ["colormap"]

    @property
    def colormap(self):
        """
        Name of the colormap to use for colouring the surface.

        If not given, the default colormap set via the property ``cmap`` in
        :class:`aspecd.plotting.SurfaceProperties` will be used. Querying
        this property will only return a non-empty string if the property
        itself was set, not the default value set via the property ``cmap`` in
        :class:`aspecd.plotting.SurfaceProperties`. However, setting a value
        will be propagated to the property ``cmap`` in
        :class:`aspecd.plotting.SurfaceProperties`. This behaviour is
        necessary to allow for setting a default colormap in a recipe and
        having it propagated by default to 2D surface plots as well.

        For a full list of colormaps available with Matplotlib, see
        https://matplotlib.org/stable/gallery/color/colormap_reference.html.

        Note that appending ``_r`` to the name of a colormap will reverse it.

        .. versionadded:: 0.8.2

        """
        return self._colormap

    @colormap.setter
    def colormap(self, colormap):
        self._colormap = colormap
        self.drawing.cmap = self._colormap

    def apply(self, plotter=None):
        """
        Apply properties to plot.

        Parameters
        ----------
        plotter: :class:`aspecd.plotting.SinglePlotter2D`
            Plotter the properties should be applied to.

        Raises
        ------
        aspecd.exceptions.MissingPlotterError
            Raised if no plotter is provided.

        """
        super().apply(plotter=plotter)
        if plotter.colorbar:
            self.colorbar.apply(colorbar=plotter.colorbar)


class MultiPlotProperties(PlotProperties):
    """
    Properties of a multiplot, defining its appearance.

    Attributes
    ----------
    figure : :class:`aspecd.plotting.FigureProperties`
        Properties of the figure as such

        For the properties that can be set this way, see the documentation
        of the :class:`aspecd.plotting.FigureProperties` class.

    axes : :class:`aspecd.plotting.AxesProperties`
        Properties of the axes.

        For the properties that can be set this way, see the documentation
        of the :class:`aspecd.plotting.AxesProperties` class.

    grid : :class:`aspecd.plotting.GridProperties`
        Properties of the grid.

        For the properties that can be set this way, see the documentation
        of the :class:`aspecd.plotting.GridProperties` class.

    drawings : :class:`list`
        Properties of the lines within a plot.

        Each element is a :obj:`aspecd.plotting.DrawingProperties` object

        For the properties that can be set this way, see the documentation
        of the :class:`aspecd.plotting.DrawingProperties` class.

    Raises
    ------
    aspecd.plotting.MissingPlotterError
        Raised if no plotter is provided.

    """

    def __init__(self):
        super().__init__()
        self.grid = GridProperties()
        self.drawings = []

    def from_dict(self, dict_=None):
        """
        Set attributes from dictionary.

        The key ``drawings`` is handled in a special way: First of all,
        :attr:`aspecd.plotting.MultiPlotProperties.drawings` is a list,
        hence we need to iterate over the entries of the list. Furthermore,
        a new element of the list is appended only if it does not exist
        already.

        As different MultiPlotter objects will use different properties
        classes for their drawing, adding a new drawing is handled by a
        separate method,
        :meth:`aspecd.plotting.MultiPlotProperties.add_drawing`.
        Additionally, each MultiPlotter class can use this method as well,
        to add drawing properties for each plotted item.

        Parameters
        ----------
        dict_ : :class:`dict`
            Dictionary containing information of a task.

        Raises
        ------
        aspecd.exceptions.MissingDictError
            Raised if no dict is provided.

        """
        if "drawings" in dict_:
            for idx in range(len(self.drawings), len(dict_["drawings"])):
                self.add_drawing()
            for idx, drawing in enumerate(dict_["drawings"]):
                self.drawings[idx].from_dict(drawing)
            dict_.pop("drawings")
        if dict_:
            super().from_dict(dict_)

    def add_drawing(self):
        """
        Add a :obj:`aspecd.plotting.DrawingProperties` object to the list.

        As different MultiPlotter objects will use different properties
        classes for their drawing, adding a new drawing is handled by this
        method. Additionally, each MultiPlotter class can use this method as
        well, to add drawing properties for each plotted item.

        .. note::
            A note for developers: Concrete MultiPlotter classes will use
            classes derived from :class:`aspecd.plotting.MultiPlotProperties`
            for their ``properties`` property. These properties classes
            should override this method to ensure the correct type of
            :class:`aspecd.plotting.DrawingProperties` is instantiated.
            Furthermore, make sure to set default values according to the
            current cycler.

        """
        drawing_properties = DrawingProperties()
        self.drawings.append(drawing_properties)

    def apply(self, plotter=None):
        """
        Apply properties to plot.

        Parameters
        ----------
        plotter: :class:`aspecd.plotting.MultiPlotter`
            Plotter the properties should be applied to.

        Raises
        ------
        aspecd.exceptions.MissingPlotterError
            Raised if no plotter is provided.

        """
        super().apply(plotter=plotter)
        self.axes.apply(axes=plotter.axes)
        self.grid.apply(axes=plotter.axes)
        self._apply_legend_properties(plotter=plotter)
        self._apply_legend_properties(plotter)
        self._apply_drawings_properties(plotter)

    def _apply_legend_properties(self, plotter=None):
        if hasattr(plotter, "legend") and plotter.legend:
            self.legend.apply(legend=plotter.legend)

    def _apply_drawings_properties(self, plotter=None):
        if hasattr(plotter, "drawings"):
            for idx, drawing in enumerate(plotter.drawings):
                self.drawings[idx].apply(drawing=drawing)


class MultiPlot1DProperties(MultiPlotProperties):
    """
    Properties of a 1D multiplot, defining its appearance.

    Attributes
    ----------
    drawings : :class:`list`
        Properties of the lines within a plot.

        Each element is a :obj:`aspecd.plotting.LineProperties` object

        For the properties that can be set this way, see the documentation
        of the :class:`aspecd.plotting.LineProperties` class.

    colormap : :class:`str`
        Name of the colormap to use for colouring the individual drawings.

        For a full list of colormaps available with Matplotlib, see
        https://matplotlib.org/stable/gallery/color/colormap_reference.html.

        Note that appending ``_r`` to the name of a colormap will reverse it.

        If set to :obj:`None`, the default colormap from your Matplotlib
        settings will be used.

        Default: :obj:`None`

    number_of_colors : :class:`int`
        Number of colors taken from the colormap.

        This setting is useful if you provide a colormap (probably globally
        in a recipe) and would like to have always the same colour
        succession in your figures, regardless of the number of actual
        drawings within one figure.

        If there are more drawings than colors, the colors will be cycled,
        *i.e.*, several drawings will have the same color.

        Has only an effect if a :attr:`colormap` is provided.

    first_color : :class:`int`
        First color of a chosen colormap to use.

        Particularly with colormaps starting with white or fairly light
        colors, setting an offset within the colormap is often necessary.

        Default: 0

    Raises
    ------
    aspecd.exceptions.MissingPlotterError
        Raised if no plotter is provided.


    .. versionchanged:: 0.8
        Added attribute :attr:`colormap`

    .. versionchanged:: 0.12
        Added attributes :attr:`number_of_colors` and  :attr:`first_color`

    """

    def __init__(self):
        super().__init__()
        self.colormap = None
        self.number_of_colors = None
        self.first_color = 0
        self._drawing = False

    def from_dict(self, dict_=None):
        """
        Set attributes from dictionary.

        The key ``drawing`` (singular!) is handled in a special way: If it
        exists in the dictionary, it gets used to set *all* drawings to
        this one set of properties.

        Otherwise, the behaviour is identical to that of the superclass
        method: see :meth:`MultiPlotProperties.from_dict` for details.

        Parameters
        ----------
        dict_ : :class:`dict`
            Dictionary containing information of a task.


        .. versionadded:: 0.10

        """
        if "drawing" in dict_:
            self._drawing = True
            dict_["drawings"] = [dict_["drawing"]]
            dict_.pop("drawing")
        super().from_dict(dict_=dict_)

    def add_drawing(self):
        """
        Add a :obj:`aspecd.plotting.LineProperties` object to the list.

        The default properties are set as well, as obtained from
        :obj:`matplotlib.pyplot.rcParams`. These contain at least colour,
        width, marker, and style of a line.

        .. note::

            If you provide a key "drawing" (singular!) in the dictionary with
            the properties, instead of setting default properties the
            properties of this dict will be set to *all* drawings.
            Thus, you can conveniently set identical settings for all lines.


        .. versionchanged:: 0.10
            Handling of the ``drawing`` key.

        """
        if self._drawing and self.drawings:
            drawing_properties = self.drawings[-1]
        else:
            drawing_properties = LineProperties()
            self._set_default_properties(drawing_properties)
        self.drawings.append(drawing_properties)

    def _set_default_properties(self, drawing_properties):
        property_cycle = mpl.rcParams["axes.prop_cycle"].by_key()
        length_properties = len(property_cycle["color"])
        idx = len(self.drawings)
        for key, value in property_cycle.items():
            setattr(drawing_properties, key, value[idx % length_properties])
        for key in ["linewidth", "linestyle", "marker"]:
            rc_property = "lines." + key
            if rc_property in mpl.rcParams.keys():
                setattr(drawing_properties, key, mpl.rcParams[rc_property])

    def apply(self, plotter=None):
        """
        Apply properties to plot.

        The main difference to the parent class: if you set a colormap
        property, the lines will be coloured according to the colormap.
        Note that this needs to be done on this level, as we need to know
        how many drawings (i.e. lines) there are to colour.

        Parameters
        ----------
        plotter: :class:`aspecd.plotting.MultiPlotter`
            Plotter the properties should be applied to.

        Raises
        ------
        aspecd.exceptions.MissingPlotterError
            Raised if no plotter is provided.

        """
        super().apply(plotter=plotter)
        if hasattr(plotter, "drawings") and self.colormap:
            if self.number_of_colors:
                number_of_colors = self.number_of_colors
            else:
                number_of_colors = len(self.drawings)
            colors = plt.get_cmap(
                self.colormap, number_of_colors + self.first_color
            )
            default_colors = mpl.rcParams["axes.prop_cycle"].by_key()["color"]
            for idx, _ in enumerate(plotter.drawings):
                if (
                    self.drawings[idx].color
                    == default_colors[idx % len(default_colors)]
                ):
                    self.drawings[idx].color = colors(
                        (idx % number_of_colors) + self.first_color
                    )


class SinglePlot2DStackedProperties(MultiPlot1DProperties):
    """
    Properties of a 2D stacked singleplot, defining its appearance.

    Attributes
    ----------
    drawings : :class:`list`
        Properties of the lines within a plot.

        Each element is a :obj:`aspecd.plotting.LineProperties` object

        For the properties that can be set this way, see the documentation
        of the :class:`aspecd.plotting.LineProperties` class.

    colormap : :class:`str`
        Name of the colormap to use for colouring the individual drawings

        For a full list of colormaps available with Matplotlib, see
        https://matplotlib.org/stable/gallery/color/colormap_reference.html.

        Note that appending ``_r`` to the name of a colormap will reverse it.

    Raises
    ------
    aspecd.exceptions.MissingPlotterError
        Raised if no plotter is provided.


    .. versionadded:: 0.10

    """

    @property
    def drawing(self):
        """
        Properties of the lines within a plot.

        Each element is a :obj:`aspecd.plotting.LineProperties` object

        For the properties that can be set this way, see the documentation
        of the :class:`aspecd.plotting.LineProperties` class.

        This is identical to :attr:`drawings` and has been added to work
        conveniently with :class:`SinglePlotter2DStacked`.

        Returns
        -------
        drawing : :class:`list`
            Properties of the lines within a plot.


        .. versionadded:: 0.10

        """
        return self.drawings


class BarPlotProperties(MultiPlot1DProperties):
    """
    Properties of a bar plot, defining its appearance.

    Attributes
    ----------
    drawings : :class:`list`
        Properties of the bars within a plot.

        Each element is a :obj:`aspecd.plotting.PatchProperties` object

        For the properties that can be set this way, see the documentation
        of the :class:`aspecd.plotting.PatchProperties` class.

    colormap : :class:`str`
        Name of the colormap to use for colouring the individual drawings

        For a full list of colormaps available with Matplotlib, see
        https://matplotlib.org/stable/gallery/color/colormap_reference.html.

        Note that appending ``_r`` to the name of a colormap will reverse it.

    Raises
    ------
    aspecd.exceptions.MissingPlotterError
        Raised if no plotter is provided.


    .. versionadded:: 0.12

    """

    @property
    def drawing(self):
        """
        Properties of the bars within a plot.

        Each element is a :obj:`aspecd.plotting.PatchProperties` object

        For the properties that can be set this way, see the documentation
        of the :class:`aspecd.plotting.PatchProperties` class.

        This is identical to :attr:`drawings` and has been added to work
        conveniently with :class:`SingleBarPlotter`.

        Returns
        -------
        drawing : :class:`list`
            Properties of the bars within a plot.

        """
        return self.drawings

    def add_drawing(self):
        """
        Add a :obj:`aspecd.plotting.PatchProperties` object to the list.

        .. note::

            If you provide a key "drawing" (singular!) in the dictionary with
            the properties, instead of setting default properties the
            properties of this dict will be set to *all* drawings.
            Thus, you can conveniently set identical settings for all patches.


        """
        if self._drawing and self.drawings:
            drawing_properties = self.drawings[-1]
        else:
            drawing_properties = PatchProperties()
        self.drawings.append(drawing_properties)

    def _apply_drawings_properties(self, plotter=None):
        if hasattr(plotter, "drawings"):
            for idx, drawing in enumerate(plotter.drawings):
                if self.drawings[idx].label:
                    drawing.set_label(self.drawings[idx].label)
                for bar in drawing.get_children():  # noqa
                    drawing_properties = copy.copy(self.drawings[idx])
                    drawing_properties.label = ""
                    drawing_properties.apply(drawing=bar)


class CompositePlotProperties(PlotProperties):
    """
    Properties of a composite plot, defining its appearance.

    For the plotter class, see :class:`CompositePlotter`.

    Attributes
    ----------
    figure : :class:`aspecd.plotting.FigureProperties`
        Properties of the figure as such

        For the properties that can be set this way, see the documentation
        of the :class:`aspecd.plotting.FigureProperties` class.

    axes : :class:`AxesProperties`
        Properties for all axes of the CompositePlotter.

        This property is used to set properties for all axes of a
        CompositePlotter at once. This will override the settings of the
        individual plotters.

        For the properties that can be set this way, see the documentation
        of the :class:`AxesProperties` class.

    grid_spec : :class:`SubplotGridSpecs`
        Properties for the subplot grid specs.

        This property is used to set properties for the subplot grid.

        For the properties that can be set this way, see the documentation
        of the :class:`SubplotGridSpecs` class.

        .. versionadded:: 0.10


    Raises
    ------
    aspecd.exceptions.MissingPlotterError
        Raised if no plotter is provided.


    .. versionchanged:: 0.10
        Property :attr:`grid_spec` added.

    """

    def __init__(self):
        super().__init__()
        self.axes = AxesProperties()
        self.grid_spec = SubplotGridSpecs()

    def apply(self, plotter=None):
        """
        Apply properties to plot.

        Parameters
        ----------
        plotter: :class:`aspecd.plotting.CompositePlotter`
            Plotter the properties should be applied to.

        Raises
        ------
        aspecd.exceptions.MissingPlotterError
            Raised if no plotter is provided.

        """
        super().apply(plotter=plotter)
        if hasattr(plotter, "axes"):
            for axes in plotter.axes:
                self.axes.apply(axes=axes)


class FigureProperties(aspecd.utils.Properties):
    """
    Properties of a figure of a plot, i.e., the most general aspects.

    Basically, the attributes are a subset of what :mod:`matplotlib` defines
    for :obj:`matplotlib.figure.Figure` objects.

    Attributes
    ----------
    size: :class:`tuple`
        Figure dimension (width, height) in inches.

        2-tuple of floats

        In order to not prevent users from setting the default figure size
        in their matplotlibrc file, the default is ``None``.

        Default: None

    dpi: :class:`float`
        Figure resolution in dots per inch.

        Default: 100

    title: :class:`str`
        Title for the figure as a whole

        .. important::

            If you have a second axis on top of the axes, setting the
            figure title will result in the figure title clashing with the
            upper axis. Hence, in such case, try setting the axis title.

    Raises
    ------
    aspecd.exceptions.MissingFigureError
        Raised if no figure is provided.


    .. versionchanged:: 0.6
        Default figure size set to (6., 4.)

    .. versionchanged:: 0.11
        Default figure size set to None to allow setting from matplotlibrc file.

    """

    def __init__(self):
        super().__init__()
        self.size = None
        self.dpi = 100.0
        self.title = ""

    def apply(self, figure=None):
        """
        Apply properties to figure.

        Parameters
        ----------
        figure: :class:`matplotlib.figure.Figure`
            Plotter the properties should be applied to.

        Raises
        ------
        aspecd.exceptions.MissingFigureError
            Raised if no figure is provided.

        """
        if not figure:
            raise aspecd.exceptions.MissingFigureError
        for prop in self.get_properties():
            setattr(figure, prop, getattr(self, prop))
        # Need to set size and title manually
        if self.size:
            figure.set_size_inches(self.size)
        figure.suptitle(self.title)


class AxesProperties(aspecd.utils.Properties):
    """
    Properties of an axis of a plot.

    Basically, the attributes are a subset of what :mod:`matplotlib` defines
    for :obj:`matplotlib.axes.Axes` objects.

    Attributes
    ----------
    aspect: {'auto', 'equal'} or num
        aspect of the axis scaling, i.e. the ratio of y-unit to x-unit

        Default: ''

    facecolor: color
        facecolor of the axes

        Default: None

    position: :class:`list`
        position of the axes: left, bottom, width, height

        four numbers in the interval [0..1]

        Default: []

    title: :class:`str`
        title for the axis

        Note that this is a per-axis title, unlike the figure title set for
        the whole figure.

        .. important::

            If you have a second axis on top of the axes, setting the
            figure title will result in the figure title clashing with the
            upper axis. Hence, in such case, try setting the axis title.

        Default: ''

    xlabel: :class:`str`
        label for the x-axis

        To remove the xlabel entirely, set it to ``None`` (or ``null`` in
        YAML).

        Default: ''

    xlabelposition : :class:`str`
        Position of the label for the x-axis.

        Possible values are: "left", "center", "right".

        Default: "center"

        .. versionadded:: 0.11

    xlim: :class:`list`
        x-axis view limits, two floats

        Default: []

    xscale: :class:`str`
        x-axis scale

        possible values: "linear", "log", "symlog", "logit"

        Default: ''

    xticks:
        y ticks with list of ticks

        Default: None

    xticklabels: :class:`list`
        x-tick labels: list of string labels

        Default: None

    xticklabelangle: :class:`float`
        Angle of the x-tick labels

        Default: None

        .. versionadded:: 0.6

    ylabel: :class:`str`
        label for the y-axis

        To remove the xlabel entirely, set it to ``None`` (or ``null`` in
        YAML).

        Default: ''

    ylabelposition : :class:`str`
        Position of the label for the y-axis.

        Possible values are: "left", "center", "right", "bottom", "top",
        where "left"/"bottom" and "right"/"top" are equivalent.

        Default: "center"

        .. versionadded:: 0.11

    ylim: :class:`list`
        y-axis view limits, two floats

        Default: []

    yscale: :class:`str`
        y-axis scale

        possible values: "linear", "log", "symlog", "logit"

        Default: ''

    yticks:
        y ticks with list of ticks

        Default: None

    yticklabels: :class:`list`
        y-tick labels: list of string labels

        Default: None

    yticklabelangle: :class:`float`
        Angle of the y-tick labels

        Default: None

        .. versionadded:: 0.6

    label_fontsize : :class:`int` or :class:`str`
        Font size of the axes labels.

        If numeric the size will be the absolute font size in points. String
        values are relative to the current default font size. Valid string
        values are: ``xx-small``, ``x-small``, ``small``, ``medium``,
        ``large``, ``x-large``, ``xx-large``

        Default: ``plt.rcParams['font.size']``

        .. versionadded:: 0.9

    invert: :class:`list` or :class:`str`
        Axes to invert

        Sometimes, inverted axes are the default, *e.g.* the wavenumber
        axis in FTIR spectroscopy. While dedicated packages for such
        method based on the ASpecD framework will take care of these
        specialties, this option allows for full flexibility.

        Can either be a single value, such as 'x' or 'y', or a list,
        such as ['x'] or even ['x', 'y'].

        .. note::

            An alternative option to invert an axis is to provide
            descending values for axis limits. However, this may be
            inconvenient if you don't want to explicitly provide axis limits.

        .. versionadded:: 0.9

    frame_on : :class:`bool`
        Whether to draw the "frame" (aka "spines") around the axes.

        Note that setting this attribute to ``False`` will remove the entire
        frame, hence it is usually not what you intended.

        Default: ``True``

        .. versionadded:: 0.11

    spines : :class:`Spines`
        Settings for axes spines.

        Axes spines are basically the four lines in the four edges of an
        axes, where the tick marks are attached.

        See class :class:`Spines` and :class:`SpineProperties` for details.

        .. versionadded:: 0.11

    Raises
    ------
    aspecd.exceptions.MissingAxisError
        Raised if no axis is provided.


    .. versionchanged:: 0.6
        New properties ``xticklabelangle`` and ``yticklabelangle``

    .. versionchanged:: 0.9
        New property ``invert``

    .. versionchanged:: 0.9
        New property ``label_fontsize``

    .. versionchanged:: 0.9.3
        Properties ``xlabel`` and ``ylabel`` can be removed by setting to
        ``Null``

    .. versionchanged:: 0.11
        New properties ``frame_on``, ``spines``, ``xlabelposition``,
        and ``ylabelposition``

    """

    # pylint: disable=too-many-instance-attributes
    def __init__(self):
        super().__init__()
        self.aspect = ""
        self.facecolor = None
        self.position = []
        self.title = ""
        self.xlabel = ""
        self.xlabelposition = "center"
        self.xlim = []
        self.xscale = ""
        self.xticklabels = None
        self.xticklabelangle = 0.0
        self.xticks = None
        self.ylabel = ""
        self.ylabelposition = "center"
        self.ylim = []
        self.yscale = ""
        self.yticklabels = None
        self.yticklabelangle = 0.0
        self.yticks = None
        self.label_fontsize = plt.rcParams["font.size"]
        self.invert = None
        self.frame_on = True
        self.spines = Spines()

    def apply(self, axes=None):
        """
        Apply settable properties to axis.

        Only properties that are not None or empty will be set, in order to
        prevent problems. The underlying method used to set the axis
        properties is :meth:`matplotlib.axes.Axes.update`.

        Parameters
        ----------
        axes: :class:`matplotlib.axes.Axes`
            axis to set properties for

        Raises
        ------
        aspecd.exceptions.MissingAxisError
            Raised if no axis is provided.

        """
        if not axes:
            raise aspecd.exceptions.MissingAxisError
        axes.update(self._get_settable_properties())
        for property_, value in self._get_settable_properties().items():
            if hasattr(axes, "set_" + property_):
                getattr(axes, "set_" + property_)(value)
        self._set_axes_ticks(axes)
        self._set_axes_label_properties(axes)
        if self.invert:
            self._invert_axes(axes)
        self.spines.apply(axes=axes)

    def _get_settable_properties(self):
        """
        Return properties that can be applied to an axis.

        Properties that are either None or empty often cause problems.
        Therefore, the properties of
        :class:`aspecd.plotting.AxesProperties` are reduced accordingly to
        those properties that are neither None nor empty.

        Currently, the only exception are those properties ending with
        "label" and set to ``None``, to be able to remove x or y axis labels.

        Returns
        -------
        properties: :class:`dict`
            Properties that are neither None nor empty

        """
        all_properties = self.to_dict()
        properties = {}
        for prop in all_properties:
            if (
                prop.startswith(("xtick", "ytick", "invert"))
                or "fontsize" in prop
                or "spines" in prop
                or prop.endswith("labelposition")
            ):
                pass
            elif isinstance(all_properties[prop], np.ndarray):
                if any(all_properties[prop]):
                    properties[prop] = all_properties[prop]
            elif all_properties[prop] or all_properties[prop] is False:
                properties[prop] = all_properties[prop]
            elif prop.endswith("label") and all_properties[prop] is None:
                properties[prop] = all_properties[prop]
        return properties

    def _set_axes_ticks(self, axes):
        if self.xticks is not None:
            axes.xaxis.set_major_locator(ticker.FixedLocator(self.xticks))
        if self.yticks is not None:
            axes.yaxis.set_major_locator(ticker.FixedLocator(self.yticks))
        if self.xticklabels is not None:
            axes.set_xticklabels(self.xticklabels)
        if self.yticklabels is not None:
            axes.set_yticklabels(self.yticklabels)
        for tick in axes.get_xticklabels():
            tick.set_rotation(self.xticklabelangle)
        for tick in axes.get_yticklabels():
            tick.set_rotation(self.yticklabelangle)

    def _set_axes_label_properties(self, axes):
        axes.get_xaxis().get_label().set_fontsize(self.label_fontsize)
        axes.get_yaxis().get_label().set_fontsize(self.label_fontsize)
        xlabel = axes.get_xaxis().get_label()
        ylabel = axes.get_yaxis().get_label()
        if self.ylabelposition == "bottom":
            self.ylabelposition = "left"
        if self.ylabelposition == "top":
            self.ylabelposition = "right"
        position = {"left": 0, "center": 0.5, "right": 1}
        xlabel.set_horizontalalignment(self.xlabelposition)
        ylabel.set_horizontalalignment(self.ylabelposition)
        xlabel.set_position(
            [position[self.xlabelposition], xlabel.get_position()[1]]
        )
        ylabel.set_position(
            [ylabel.get_position()[1], position[self.ylabelposition]]
        )

    def _invert_axes(self, axes):
        if isinstance(self.invert, str):
            self.invert = [self.invert]
        for axis in self.invert:
            if axis.lower().startswith("x"):
                if not axes.xaxis_inverted():
                    axes.invert_xaxis()
            if axis.lower().startswith("y"):
                if not axes.yaxis_inverted():
                    axes.invert_yaxis()


class LegendProperties(aspecd.utils.Properties):
    """
    Properties of a legend of a plot, i.e., the most general aspects.

    Basically, the attributes are a subset of what :mod:`matplotlib` defines
    for :obj:`matplotlib.legend.Legend` objects.

    Attributes
    ----------
    loc : :class:`str`
        Location of the legend

        For possible values, see :class:`matplotlib.legend.Legend`

    frameon : :class:`bool`
        Whether to plot a box around the legend

        Default: True

    labelspacing : :class:`float`
        Vertical space between the legend entries, in font-size units.

        Default: 0.5

    fontsize : :class:`int` or :class:`str`
        Font size of the legend.

        If numeric the size will be the absolute font size in points. String
        values are relative to the current default font size. Valid string
        values are: ``xx-small``, ``x-small``, ``small``, ``medium``,
        ``large``, ``x-large``, ``xx-large``

        Default: ``plt.rcParams['font.size']``

    ncol : :class:`int`
        Number of columns of the legend

        Default: 1

    title : :class:`str`
        Title of the legend

        Default: empty

    Raises
    ------
    aspecd.exceptions.MissingLegendError
        Raised if no legend is provided.


    .. versionchanged:: 0.7
        Added attributes :attr:`labelspacing` and :attr:`fontsize`

    .. versionchanged:: 0.8
        Added attribute :attr:`ncol`

    .. versionchanged:: 0.9
        Added attribute :attr:`title`

    """

    def __init__(self):
        super().__init__()
        self.loc = "best"
        self.frameon = True
        self.labelspacing = 0.5
        self.fontsize = plt.rcParams["font.size"]
        self.ncol = 1
        self.title = ""
        self._exclude = ["location"]
        self._exclude_from_to_dict = ["location"]

    @property
    def location(self):
        """Alias for :attr:`aspecd.plotting.LegendProperties.loc`"""
        return self.loc

    @location.setter
    def location(self, value=""):
        self.loc = value

    def apply(self, legend=None):
        """
        Apply properties to legend.

        Parameters
        ----------
        legend: :class:`matplotlib.legend.Legend`
            Legend the properties should be applied to.

        Raises
        ------
        aspecd.exceptions.MissingLegendError
            Raised if no legend is provided.

        """
        if not legend:
            raise aspecd.exceptions.MissingLegendError
        for prop in self.get_properties():
            setattr(legend, prop, getattr(self, prop))


class DrawingProperties(aspecd.utils.Properties):
    """
    Properties of a drawing within a plot.

    A drawing is the most abstract object representing data within axes,
    such as a line, contour, etcetera.

    While a base class for more specific kinds of drawings, such as lines,
    surfaces, or even text, drawing properties come with two essential
    attributes: a label and the zorder.

    The latter means that you can control the z stacking of the different
    parts of a plot. Artists with lower zorder are drawn first.

    For specific kinds of drawings and their respective properties,
    see :class:`LineProperties`, :class:`SurfaceProperties`,
    and :class:`TextProperties`.

    Attributes
    ----------
    label: :class:`str`
        Label of a drawing that gets used within a legend.

         Default: ''

    alpha : :class:`float`
        Alpha value used for blending

        Must be within the 0-1 range, inclusive, or :class:`None`.

        .. versionadded:: 0.11

    zorder : :class:`float`
        Zorder for the artist.

        Artists with lower zorder are drawn first.

        For a summary of the default zorder values, see the `Matplotlib
        documentation <https://matplotlib.org/stable/gallery/misc
        /zorder_demo.html>`_

        .. versionadded:: 0.10

    Raises
    ------
    aspecd.exceptions.MissingDrawingError
        Raised if no drawing is provided.


    Examples
    --------
    Drawing properties are always set in context of concrete plotters,
    and furthermore, the individual main elements of a plot are always
    referred to as ``drawing`` or ``drawings`` within their respective
    :class:`PlotProperties`.

    An example for setting the drawing properties of a
    :class:`SinglePlotter1D` are given below:

    .. code-block:: yaml

        - kind: singleplot
          type: SinglePlotter1D
          properties:
            properties:
              drawings:
                label: Substance 1
                zorder: 3

    In context of a plotter with a legend, the label would appear in this
    legend, and in this particular case, the zorder is set to 3, *i.e.*
    the line in the plotter would appear behind other elements.


    .. versionchanged:: 0.10
        New property :attr:`zorder`

    .. versionchanged:: 0.11
        New property :attr:`alpha`

    """

    def __init__(self):
        super().__init__()
        self.label = ""
        self.zorder = 2
        self.alpha = None

    def apply(self, drawing=None):
        """
        Apply properties to drawing.

        For each property, the corresponding "set_<property>" method of the
        artist will be called.

        Parameters
        ----------
        drawing: :class:`matplotlib.artist.Artist`
            Artist to set properties for

        Raises
        ------
        aspecd.exceptions.MissingDrawingError
            Raised if no artist is provided.

        """
        if not drawing:
            raise aspecd.exceptions.MissingDrawingError
        for prop in self.get_properties():
            if isinstance(drawing, list):
                for element in drawing:
                    self._safe_set_drawing_property(element, prop)
            else:
                self._safe_set_drawing_property(drawing, prop)

    def _safe_set_drawing_property(self, drawing=None, prop=None):
        """Safe setting of drawing properties.

        The method first checks whether the corresponding setter for the
        property exists and only in this case sets the property.


        Parameters
        ----------
        drawing : :class:`matplotlib.artist.Artist`
            Artist to set properties for

        prop : :class:`str`
            Name of the property to set

        """
        if hasattr(drawing, "".join(["set_", prop])):
            try:
                getattr(drawing, "".join(["set_", prop]))(getattr(self, prop))
            except TypeError:
                logger.debug(
                    'Cannot set attribute "%s" for "%s"',
                    prop,
                    drawing.__class__,
                )
        else:
            logger.debug(
                '"%s" has no setter for attribute "%s", hence not set',
                drawing.__class__,
                prop,
            )


class LineProperties(DrawingProperties):
    """
    Properties of a line within a plot.

    Basically, the attributes are a subset of what :mod:`matplotlib` defines
    for :obj:`matplotlib.lines.Line2D` objects.

    Attributes
    ----------
    color: color
        color of the line

        For details see :mod:`matplotlib.colors`

    drawstyle: :class:`str`
        drawing style of the line, default: 'default'

        For details see :meth:`matplotlib.lines.Line2D.set_drawstyle`

    linestyle: :class:`str`
        style of the line, default: 'solid'

        For details see :meth:`matplotlib.lines.Line2D.set_linestyle`

    linewidth: :class:`float`
        width of the line, float value in points, default: 1.5

    marker: :class:`str`
        marker used for the line, default: ''

        For details see :mod:`matplotlib.markers`

    zorder : :class:`float`
        Zorder for the artist.

        Artists with lower zorder are drawn first.

        For a summary of the default zorder values, see the `Matplotlib
        documentation <https://matplotlib.org/stable/gallery/misc
        /zorder_demo.html>`_

        .. versionadded:: 0.10

    Raises
    ------
    aspecd.exceptions.MissingDrawingError
        Raised if no line is provided.


    Examples
    --------
    Drawing properties are always set in context of concrete plotters,
    and furthermore, the individual main elements of a plot are always
    referred to as ``drawing`` or ``drawings`` within their respective
    :class:`PlotProperties`.

    An example for setting the line properties of a
    :class:`SinglePlotter1D` are given below:

    .. code-block:: yaml

        - kind: singleplot
          type: SinglePlotter1D
          properties:
            properties:
              drawings:
                label: Substance 1
                zorder: 3
                color: '#1f77b4'
                drawstyle: default
                linestyle: '-'
                linewidth: 1.5
                marker: None

    Here, all currently possible properties are shown.

    """

    def __init__(self):
        super().__init__()
        self.color = "#000000"
        self.drawstyle = "default"
        self.linestyle = "solid"
        self.linewidth = 1.0
        self.marker = ""

    def settable_properties(self):
        """
        Return properties that are not empty or None.

        Returns
        -------
        properties : :class:`dict`
            Dictionary containing all settable properties, *i.e.* properties
            that are neither empty nor None.

        """
        properties = {}
        for prop in self.get_properties():
            if getattr(self, prop):
                properties[prop] = getattr(self, prop)
        return properties


class SurfaceProperties(DrawingProperties):
    """
    Properties of a surface within a plot.

    Basically, the attributes are a subset of what :mod:`matplotlib` defines
    for :obj:`matplotlib.contour.ContourSet` and
    :obj:`matplotlib.image.AxesImage` objects.

    Attributes
    ----------
    cmap : :class:`str`
        Name of the colormap to use

        For details see :class:`matplotlib.colors.Colormap`

    clim : :class:`tuple`
        Norm limits for image scaling: ``(vmin, vmax)``

        The corresponding parameters of the
        :meth:`matplotlib.axes.Axes.contour` method are ``vmin`` and
        ``vmax``. If you would like to set only one of them, set the other
        to ``None``.

        .. versionadded:: 0.12

    linewidths : :class:`float`
        Width of the contour lines (if present)

    linestyles : :class:`str`
        Style of the contour lines (if present)

    colors : :class:`str`
        Colour of the contour lines (if present)

    norm : :class:`str`
        The normalization method used to scale scalar data to the [0, 1]
        range before mapping to colors using cmap. By default, a linear
        scaling is used, mapping the lowest value to 0 and the highest to 1.

        For a list of available scales, call
        :func:`matplotlib.scale.get_scale_names`. Besides these names,
        you can use the names of all subclasses of
        :class:`matplotlib.colors.Normalize`. If the resulting object needs
        any additional parameter or if you want to change the defaults,
        set the :attr:`norm_parameters` attribute accordingly.

        .. versionadded:: 0.12

    norm_parameters : :class:`dict`
        Additional parameters for the norm set using the attribute
        :attr:`norm`.

        For details which parameters can be set, see the Matplotlib
        documentation of the respective subclass of
        :class:`matplotlib.colors.Normalize`.

        .. versionadded:: 0.12

    zorder : :class:`float`
        Zorder for the artist.

        Artists with lower zorder are drawn first.

        For a summary of the default zorder values, see the `Matplotlib
        documentation <https://matplotlib.org/stable/gallery/misc
        /zorder_demo.html>`_

        .. versionadded:: 0.10

    """

    def __init__(self):
        super().__init__()
        self.cmap = "viridis"
        self.linewidths = None
        self.linestyles = None
        self.colors = None
        self.clim = None
        self.norm = None
        self.norm_parameters = {}
        self._original_norm = None

    def apply(self, drawing=None):
        """
        Apply properties to drawing.

        Parameters
        ----------
        drawing:
            matplotlib object to set properties for

        """
        self._check_norm()
        super().apply(drawing=drawing)
        self._apply_norm(drawing=drawing)
        self._set_norm_parameters(drawing=drawing)
        children = drawing.axes.get_children()
        for child in children:
            if isinstance(
                child,
                (
                    mpl.collections.LineCollection,
                    mpl.collections.PathCollection,
                    mpl.contour.QuadContourSet,
                ),
            ):
                if self.linewidths:
                    child.set_linewidth(self.linewidths)
                if self.linestyles:
                    child.set_linestyle(self.linestyles)
                if self.colors:
                    child.set_color(self.colors)

    def _check_norm(self):
        if self.norm and self.norm not in mpl.scale.get_scale_names():
            self._original_norm = self.norm
            self.norm = None

    def _apply_norm(self, drawing):
        if self._original_norm:
            self.norm = self._original_norm
            norm = getattr(mpl.colors, f"{self.norm.capitalize()}Norm")()
            drawing.set_norm(norm)

    def _set_norm_parameters(self, drawing):
        if self.norm_parameters:
            for key, value in self.norm_parameters.items():
                if hasattr(drawing.norm, key):
                    setattr(drawing.norm, key, value)


class GridProperties(aspecd.utils.Properties):
    """
    Properties of the grid of a plot.

    Attributes
    ----------
    show: :class:`bool`
        whether to show grids

    ticks: :class:`str`
        ticks to set grid lines for: {'major', 'minor', 'both'}

        For details see the ``which`` parameter of
        :meth:`matplotlib.axes.Axes.grid`

    axis: :class:`str`
        axis to set grid lines for: {'both', 'x', 'y'}

        For details see :meth:`matplotlib.axes.Axes.grid`

    lines: :class:`aspecd.plotting.LineProperties`
        line properties of the grid

    Raises
    ------
    TypeError
        Raised if no axes is provided.

    """

    def __init__(self):
        super().__init__()
        self.show = False
        self.ticks = ""
        self.axis = ""
        self.lines = LineProperties()
        # Set default properties
        self.lines.color = "#cccccc"

    def apply(self, axes=None):
        """
        Apply properties to axes.

        If :attr:`show` is false, no grid will be displayed. Otherwise,
        the properties will be set, including the line properties.

        Parameters
        ----------
        axes: :class:`matplotlib.axes.Axes`
            axis to set properties for

        Raises
        ------
        TypeError
            Raised if called without axes object

        """
        if not axes:
            raise TypeError("Missing 1 positional argument: axes")
        # Partly untested code: no plan how to test that a grid is present
        if not self.show:
            axes.grid(False)
        else:
            if self.ticks and self.axis:
                axes.grid(
                    True,
                    which=self.ticks,
                    axis=self.axis,
                    **self.lines.settable_properties(),
                )
            elif self.ticks:
                axes.grid(
                    True, which=self.ticks, **self.lines.settable_properties()
                )
            elif self.axis:
                axes.grid(
                    True, axis=self.axis, **self.lines.settable_properties()
                )
            else:
                axes.grid(True, **self.lines.settable_properties())


class ColorbarProperties(aspecd.utils.Properties):
    """
    Properties of the colorbar of a plot.

    Basically, a subset of what :meth:`matplotlib.figure.Figure.colorbar`
    defines for a colorbar.

    Note that Matplotlib does not usually have an interface that easily
    allows to both, set and query properties. For colorbars in particular,
    many parameters can only be set when instantiating the colorbar object.

    Attributes
    ----------
    location : :class:`str`
        Location of the colorbar.

        Valid parameters: None or {'left', 'right', 'top', 'bottom'}

    fraction : :class:`float`
        Fraction of original axes to use for colorbar.

        Default: 0.15

    aspect : :class:`float`
        Ratio of long to short dimensions.

        Default: 20.

    pad : :class:`float`
        Fraction of original axes between colorbar and new image axes.

        Default: 0.05 if vertical, 0.15 if horizontal

    format : :class:`str`
        Format of the tick labels

    label : :class:`dict`
        The label on the colorbar's long axis and its properties.

        The following keys exist:

        text : :class:`str`
            The label text

        location : :class:`str`
            The location of the label

            Valid values depend on the orientation of the colorbar.

            * For horizontal orientation one of {'left', 'center', 'right'}
            * For vertical orientation one of {'bottom', 'center', 'top'}


    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class.

    Generally, the ColorbarProperties are set within the properties of the
    respective plotter.

    .. code-block:: yaml

        - kind: singleplot
          type: SinglePlotter2D
          properties:
            properties:
              colorbar:
                location: top
                fraction: 0.1
                pad: 0.1
                format: "%4.2e"
                label:
                  text: $foo$ / bar
                  location: left


    .. versionadded:: 0.9

    """

    def __init__(self):
        super().__init__()
        self.location = None
        self.fraction = 0.15
        self.aspect = 20.0
        self.pad = None
        self.format = ""
        self.label = {"text": "", "location": None}
        self._exclude_from_kwargs = ["label"]

    @property
    def kwargs(self):
        """
        Properties that can/need to be set during colorbar object creation.

        Many parameters can only be set when instantiating the colorbar
        object. For convenience, this property returns a dict with the
        subset of properties that can (and need to) be set this way.

        Those properties of the class that cannot be set this way are listed
        in the private attribute ``_exclude_from_kwargs``. Actually setting
        the properties to a colorbar looks like:

        .. code-block::

            fig.colorbar(drawing, ax=ax, **kwargs)

        Here, ``**kwargs`` is the expansion of the returned dictionary.

        Returns
        -------
        kwargs : :class:`dict`
            dict with kwargs that can be set when instantiating the colorbar.

        """
        kwargs = self.to_dict()
        for key in self._exclude_from_kwargs:
            kwargs.pop(key, None)
        keys_to_drop = [key for key, value in kwargs.items() if not value]
        for key in keys_to_drop:
            kwargs.pop(key)
        return kwargs

    def apply(self, colorbar=None):
        """
        Apply properties to colorbar.

        Parameters
        ----------
        colorbar: :class:`matplotlib.colorbar.Colorbar`
            Colorbar the properties should be applied to.

        """
        self._set_colorbar_label(colorbar=colorbar)

    def _set_colorbar_label(self, colorbar=None):
        if "location" in self.label and self.label["location"]:
            location = self.label["location"]
        else:
            location = None
        colorbar.set_label(self.label["text"], loc=location)


class TextProperties(DrawingProperties):
    """
    Properties of text within a plot.

    Basically, the attributes are a subset of what :mod:`matplotlib` defines
    for :obj:`matplotlib.text.Text` objects.


    Attributes
    ----------
    alpha : :class:`float`
        Alpha value used for blending

        Must be within the 0-1 range, inclusive, or :class:`None`.

    backgroundcolor : :class:`str`
        Color used as background for the text

        If set to :class:`None`, no background will be set (and the bbox
        removed from the Matplotlib artist)

    color : :class:`str`
        Color used for the text

    fontfamily : :class:`str`
        Font family or font name

        Font family can be one of: 'serif', 'sans-serif', 'cursive', 'fantasy',
        'monospace'

    fontsize : :class:`float` or :class:`str`
        Size of the font

        Either a numeric value or one of 'xx-small', 'x-small', 'small',
        'medium', 'large', 'x-large', 'xx-large'

    fontstretch : :class:`int` or :class:`str`
        Stretch of the font

        A numeric value in range 0-1000 or one of 'ultra-condensed',
        'extra-condensed', 'condensed', 'semi-condensed', 'normal',
        'semi-expanded', 'expanded', 'extra-expanded', 'ultra-expanded'

    fontstyle : :class:`str`
        Style of the font

        One of: 'normal', 'italic', 'oblique'

    fontvariant : :class:``
        Variant of the font

        One of: 'normal', 'small-caps'

    fontweight : :class:`int` or :class:`str`
        Weight of the font

        A numeric value in range 0-1000 or one of 'ultralight', 'light',
        'normal', 'regular', 'book', 'medium', 'roman', 'semibold',
        'demibold', 'demi', 'bold', 'heavy', 'extra bold', 'black'.

    horizontalalignment : :class:`str`
        Horizontal alignment of the text

        One of: 'left', 'center', 'right'

    in_layout : :class:`bool`
        Set if artist is to be included in layout calculations.

    linespacing : :class:`float`
        Line spacing of the text

        The value is interpreted as multiple of the font size

    math_fontfamily : :class:`str`
        Font family or fontname used for math fonts

    multialignment : :class:`str`
        Text alignment for multiline texts

        One of: 'left', 'right', 'center'

    parse_math : :class:`bool`
        Set mathtext parsing for text

        If False, no mathtext will be used. If True, mathtext will be used if
        there is an even number of unescaped dollar signs.

    rotation : :class:`float` or :class:`str`
        Rotation of the text

        Either a scalar number or one of: 'vertical', 'horizontal'

    rotation_mode : :class:`str`
        Rotation mode of the text

        One of: 'default', 'anchor'

        If "default", the text will be first rotated, then aligned according
        to their horizontal and vertical alignments. If "anchor",
        then alignment occurs before rotation.

    usetex : :class:`bool` or :class:`None`
        Whether to render using TeX

        None means to use ``rcParams["text.usetex"]`` (default: False).

    verticalalignment : :class:`str`
        Vertical alignment of the text

        One of: 'baseline', 'bottom', 'center', 'center_baseline', 'top'

    wrap : :class:`bool`
        Set whether the text can be wrapped.

        Wrapping makes sure the text is confined to the (sub)figure box. It
        does not take into account any other artists.

    zorder : :class:`float`
        Zorder for the artist.

        Artists with lower zorder values are drawn first.

        For a summary of the default zorder values, see the `Matplotlib
        documentation <https://matplotlib.org/stable/gallery/misc
        /zorder_demo.html>`_


    Raises
    ------
    aspecd.exceptions.MissingDrawingError
        Raised if no text is provided.


    .. versionadded:: 0.10

    """

    # pylint: disable=too-many-instance-attributes
    def __init__(self):
        super().__init__()
        self.alpha = None
        self.backgroundcolor = None
        self.color = "#000000"
        self.fontfamily = None
        self.fontsize = None
        self.fontstretch = None
        self.fontstyle = None
        self.fontvariant = None
        self.fontweight = None
        self.horizontalalignment = "left"
        self.in_layout = True
        self.linespacing = None
        self.math_fontfamily = None
        self.multialignment = "left"
        self.parse_math = None
        self.rotation = None
        self.rotation_mode = None
        self.usetex = False
        self.verticalalignment = "bottom"
        self.wrap = None
        self.zorder = None

    def apply(self, drawing=None):
        """Apply properties to text."""
        super().apply(drawing=drawing)
        if self.backgroundcolor is None:
            drawing._bbox_patch = None  # pylint: disable=protected-access


class SubplotGridSpecs(aspecd.utils.Properties):
    """
    Properties for the subplot grid specs.

    This class is used to set properties for the subplot grid of
    the :class:`CompositePlotter` class. As such, it is part of the
    :class:`CompositePlotProperties` class. For further details, see the
    :class:`matplotlib.gridspec.GridSpec` documentation.


    Attributes
    ----------
    left : :class:`float`
        Left extent of the subplots as a fraction of figure width.

        Left cannot be larger than right, and bottom cannot be larger than
        top. If not given, the values will be inferred from a figure or
        rcParams at draw time.

    bottom : :class:`float`
        Bottom extent of the subplots as a fraction of figure height.

        Left cannot be larger than right, and bottom cannot be larger than
        top. If not given, the values will be inferred from a figure or
        rcParams at draw time.

    right : :class:`float`
        Right extent of the subplots as a fraction of figure width.

        Left cannot be larger than right, and bottom cannot be larger than
        top. If not given, the values will be inferred from a figure or
        rcParams at draw time.

    top : :class:`float`
        Top extent of the subplots as a fraction of figure height.

        Left cannot be larger than right, and bottom cannot be larger than
        top. If not given, the values will be inferred from a figure or
        rcParams at draw time.

    wspace : :class:`float`
        The amount of width reserved for space between subplots.

        Expressed as a fraction of the average axis width. If not given,
        the values will be inferred from a figure or rcParams when necessary.

    hspace : :class:`float`
        The amount of height reserved for space between subplots.

        Expressed as a fraction of the average axis height. If not given,
        the values will be inferred from a figure or rcParams when necessary.

    width_ratios : :class:`list`
        Relative width of the columns.

        Each column gets a relative width of
        ``width_ratios[i] / sum(width_ratios)``.
        If not given, all columns will have the same width.

    height_ratios : :class:`list`
        Relative height of the rows.

        Each row gets a relative height of
        ``height_ratios[i] / sum(height_ratios)``.
        If not given, all rows will have the same height.

    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class.

    Subplot grid spec properties are always set in context of a concrete
    :class:`CompositePlotter`.

    An example for setting the subplot grid specs of a
    :class:`CompositePlotter` are given below:

    .. code-block:: yaml

        - kind: compositeplot
          type: CompositePlotter
          properties:
            properties:
              grid_spec:
                wspace: 0
                hspace: 0
            plotter:
            - raw-data
            - processed-data
            filename: comparison.pdf
            grid_dimensions: [1, 2]
            subplot_locations:
            - [0, 0, 1, 1]
            - [0, 1, 1, 1]


    .. versionadded:: 0.10


    """

    def __init__(self):
        super().__init__()
        self.left = None
        self.bottom = None
        self.right = None
        self.top = None
        self.wspace = None
        self.hspace = None
        self.width_ratios = None
        self.height_ratios = None


class PatchProperties(DrawingProperties):
    r"""
    Properties of a patch within a plot.

    Basically, the attributes are a subset of what :mod:`matplotlib` defines
    for :obj:`matplotlib.patches.Patch` objects.

    Attributes
    ----------
    alpha : :class:`float` | :class:`None`
        Transparency value -- not supported on all backends.

        Valid range: [0, 1]

    color : color
        color of the patch

        For details see :mod:`matplotlib.colors`

    edgecolor : color
        edge color of the patch

        For details see :mod:`matplotlib.colors`

    facecolor : color
        face color of the patch

        For details see :mod:`matplotlib.colors`

    fill : :class:`bool`
        Whether to fill the patch

    hatch : :class:`str` | :class:`None`
        hatching pattern.

        hatch can be one of::

            /   - diagonal hatching
            \   - back diagonal
            |   - vertical
            -   - horizontal
            +   - crossed
            x   - crossed diagonal
            o   - small circle
            O   - large circle
            .   - dots
            *   - stars

        Letters can be combined, in which case all the specified hatchings
        are done. If same letter repeats, it increases the density of
        hatching of that pattern.

    in_layout : :class:`bool`
        Set if artist is to be included in layout calculations.

    joinstyle : :class:`str`
        Connection between two line segments.

        Default: 'miter'

    linestyle : :class:`str`
        Style of the line.

        Default: 'solid'

        For details see :meth:`matplotlib.lines.Line2D.set_linestyle`

    linewidth : :class:`float`
        Width of the line, float value in points.

        Default: 1.0

    rasterized : :class:`bool`
        Whether to force rasterized drawing for vector graphics output.

    snap : :class:`bool`
        Snapping behavior.

        Possible values:

        * True: Snap vertices to the nearest pixel center.
        * False: Do not modify vertex positions.
        * None: (auto) If the path contains only rectilinear line segments,
          round to the nearest pixel center.

    zorder : :class:`float`
        Zorder for the artist.

        Artists with lower zorder are drawn first.

        For a summary of the default zorder values, see the `Matplotlib
        documentation <https://matplotlib.org/stable/gallery/misc
        /zorder_demo.html>`_


    Examples
    --------
    A typical use case for patches are horizontal or vertical spans as used
    for plot annotations. For details, see the
    :class:`aspecd.annotation.VerticalSpan` class.


    .. versionadded:: 0.11


    """

    def __init__(self):
        super().__init__()
        self.alpha = None
        self.color = None
        self.edgecolor = None
        self.facecolor = None
        self.fill = True
        self.hatch = None
        self.in_layout = True
        self.joinstyle = "miter"
        self.linestyle = "-"
        self.linewidth = 1
        self.rasterized = False
        self.sketch_params = None
        self.snap = None
        self.zorder = None


class AnnotationTextProperties(DrawingProperties):
    """
    Properties of text of an annotation.

    Basically, the attributes are a subset of what :mod:`matplotlib` defines
    for :obj:`matplotlib.text.Text` objects. However, the alignment
    properties are missing that are present in :class:`TextProperties`,
    as they would interfere with the functionality of the
    :class:`aspecd.annotate.TextWithLine` class.


    Attributes
    ----------
    alpha : :class:`float`
        Alpha value used for blending

        Must be within the 0-1 range, inclusive, or :class:`None`.

    backgroundcolor : :class:`str`
        Color used as background for the text

        If set to :class:`None`, no background will be set (and the bbox
        removed from the Matplotlib artist)

    color : :class:`str`
        Color used for the text

    fontfamily : :class:`str`
        Font family or font name

        Font family can be one of: 'serif', 'sans-serif', 'cursive', 'fantasy',
        'monospace'

    fontsize : :class:`float` or :class:`str`
        Size of the font

        Either a numeric value or one of 'xx-small', 'x-small', 'small',
        'medium', 'large', 'x-large', 'xx-large'

    fontstretch : :class:`int` or :class:`str`
        Stretch of the font

        A numeric value in range 0-1000 or one of 'ultra-condensed',
        'extra-condensed', 'condensed', 'semi-condensed', 'normal',
        'semi-expanded', 'expanded', 'extra-expanded', 'ultra-expanded'

    fontstyle : :class:`str`
        Style of the font

        One of: 'normal', 'italic', 'oblique'

    fontvariant : :class:``
        Variant of the font

        One of: 'normal', 'small-caps'

    fontweight : :class:`int` or :class:`str`
        Weight of the font

        A numeric value in range 0-1000 or one of 'ultralight', 'light',
        'normal', 'regular', 'book', 'medium', 'roman', 'semibold',
        'demibold', 'demi', 'bold', 'heavy', 'extra bold', 'black'.

    in_layout : :class:`bool`
        Set if artist is to be included in layout calculations.

    linespacing : :class:`float`
        Line spacing of the text

        The value is interpreted as multiple of the font size

    math_fontfamily : :class:`str`
        Font family or fontname used for math fonts

    parse_math : :class:`bool`
        Set mathtext parsing for text

        If False, no mathtext will be used. If True, mathtext will be used if
        there is an even number of unescaped dollar signs.

    rotation : :class:`float` or :class:`str`
        Rotation of the text

        Either a scalar number or one of: 'vertical', 'horizontal'

    rotation_mode : :class:`str`
        Rotation mode of the text

        One of: 'default', 'anchor'

        If "default", the text will be first rotated, then aligned according
        to their horizontal and vertical alignments. If "anchor",
        then alignment occurs before rotation.

    usetex : :class:`bool` or :class:`None`
        Whether to render using TeX

        None means to use ``rcParams["text.usetex"]`` (default: False).

    wrap : :class:`bool`
        Set whether the text can be wrapped.

        Wrapping makes sure the text is confined to the (sub)figure box. It
        does not take into account any other artists.

    zorder : :class:`float`
        Zorder for the artist.

        Artists with lower zorder values are drawn first.

        For a summary of the default zorder values, see the `Matplotlib
        documentation <https://matplotlib.org/stable/gallery/misc
        /zorder_demo.html>`_


    Raises
    ------
    aspecd.exceptions.MissingDrawingError
        Raised if no text is provided.


    .. versionadded:: 0.11


    """

    def __init__(self):
        super().__init__()
        self.alpha = None
        self.backgroundcolor = None
        self.color = "#000000"
        self.fontfamily = None
        self.fontsize = None
        self.fontstretch = None
        self.fontstyle = None
        self.fontvariant = None
        self.fontweight = None
        self.in_layout = True
        self.linespacing = None
        self.math_fontfamily = None
        self.parse_math = None
        self.rotation = None
        self.rotation_mode = None
        self.usetex = False
        self.wrap = None
        self.zorder = None

    def apply(self, drawing=None):
        """Apply properties to text."""
        super().apply(drawing=drawing)
        if self.backgroundcolor is None:
            drawing._bbox_patch = None  # pylint: disable=protected-access


class AnnotationProperties(aspecd.utils.Properties):
    """
    Properties for the text and line of annotations.

    This class is used to set properties for the
    :class:`aspecd.annotation.TextWithLine` class.


    Attributes
    ----------
    text : :class:`AnnotationTextProperties`
        Properties of the text part of the annotation

    line : :class:`PatchProperties`
        Properties of the line part of the annotation

    Raises
    ------
    aspecd.exceptions.MissingDrawingError
        Raised if no text is provided.


    .. versionadded:: 0.11


    """

    def __init__(self):
        super().__init__()
        self.text = AnnotationTextProperties()
        self.line = PatchProperties()

    def apply(self, drawing=None):
        """
        Apply properties to drawing.

        Properties will be set independently for the text and line parts of
        the annotation, and the underlying
        :meth:`AnnotationTextProperties.apply` and
        :meth:`PatchProperties.apply` method be called.

        Parameters
        ----------
        drawing: :class:`matplotlib.axes.Axes`
            axis to set properties for

        Raises
        ------
        aspecd.exceptions.MissingDrawingError
            Raised if no line is provided.

        """
        if not drawing:
            raise aspecd.exceptions.MissingDrawingError
        self.text.apply(drawing=drawing)
        self.line.apply(drawing=drawing.arrow_patch)


class Spines(aspecd.utils.Properties):
    """
    Properties proxy for spines of an axes.

    Axes spines are basically the four lines in the four edges of an
    axes, where the tick marks are attached.

    This class serves as a "container" for the four individual spines.

    Attributes
    ----------
    left : :class:`SpineProperties`
        Properties of the left axes spine

    bottom : :class:`SpineProperties`
        Properties of the bottom axes spine

    right : :class:`SpineProperties`
        Properties of the right axes spine

    top : :class:`SpineProperties`
        Properties of the top axes spine

    Raises
    ------
    aspecd.exceptions.MissingDrawingError
        Raised if no drawing is provided.


    Examples
    --------
    For detailed examples on how to set the spine properties in a plot,
    see the documentation of the :class:`SpineProperties` class.


    .. versionadded:: 0.11

    """

    def __init__(self):
        super().__init__()
        self.left = SpineProperties(edge="left")
        self.bottom = SpineProperties(edge="bottom")
        self.right = SpineProperties(edge="right")
        self.top = SpineProperties(edge="top")

    def apply(self, axes=None):
        """
        Apply properties to spine.

        For each spine, the corresponding :meth:`SpineProperties.apply`
        method will be called.

        Parameters
        ----------
        axes: :class:`matplotlib.axes.Axes`
            Axis to set spine properties for

        Raises
        ------
        aspecd.exceptions.MissingAxisError
            Raised if no axes is provided.

        """
        if not axes:
            raise aspecd.exceptions.MissingAxisError
        for prop in self.get_properties():
            getattr(self, prop).apply(drawing=getattr(axes.spines, prop))


class SpineProperties(DrawingProperties):
    """
    Properties proxy for spines of an axes.

    Axes spines are basically the four lines in the four edges of an
    axes, where the tick marks are attached.

    For details, see the documentation of the :class:`matplotlib.spines.Spine`
    class.


    Attributes
    ----------
    visible : :class:`bool`
        Whether to show the spine.

        To remove a spine, set its visibility to ``False``.

    position : :class:`tuple`
        Type and value of the positioning of a spine.

        The position type is one of ``outward, axes, data``:

        outward
            Place the spine out from the data area by the specified number
            of points. (Negative values place the spine inwards.)

        axes
            Place the spine at the specified Axes coordinate (0 to 1).

        data
            Place the spine at the specified data coordinate.

        Two shorthand notations exist, where ``position`` is only a string,
        no longer a tuple (or list):

        center
            Sets spline at the centre of the axis.

            Same as ``('axes', 0.5)``

        zero
            Sets spline to the zero value of the data.

            Same as ``('data', 0.0)``


    bounds : :class:`tuple`
        Lower and higher spine bound in axes coordinates.

    arrow : :class:`bool`
        Whether to draw arrows at the tip of the spine

        Particularly with only two spines shown and perhaps with spines
        positioned at zero (the origin of the Cartesian coordinate system),
        adding arrow heads at the tips of the spines makes sense.

        Note that this is not a default property of the underlying
        :class:`matplotlib.spines.Spine`, but adds the arrow heads as
        additional plots.

        This functionality is inspired by an example in the Matplotlib
        documentation: `<https://matplotlib.org/stable/gallery/spines
        /centered_spines_with_arrows.html>`_


    Parameters
    ----------
    edge: :class:`str`
        Position the spline belongs to in an axis: left, bottom, right, top.

        This information is relevant for adding arrow heads.

    Raises
    ------
    aspecd.exceptions.MissingDrawingError
        Raised if no drawing is provided.


    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class.

    Spines are set within the axes properties, hence in the axes block. Note
    that there are four spines: ``left``, ``bottom``, ``right``,
    and ``top``, for whom you can (and need to) set the properties
    separately.

    To get rid of the top and right spine (a typical use case), just set the
    visibility of those two to ``False``:

    .. code-block:: yaml

        - kind: singleplot
          type: SinglePlotter1D
          properties:
            properties:
              axes:
                spines:
                  right:
                    visible: False
                  top:
                    visible: False

    If you want to detach the spines, you could explicitly set both, ``bounds``
    and ``positions``:

    .. code-block:: yaml

        - kind: singleplot
          type: SinglePlotter1D
          properties:
            properties:
              axes:
                spines:
                  left:
                    bounds: [0, 1]
                    position: ["outward", 5]
                  bottom:
                    bounds: [-10, 10]
                    position: ["outward", 5]
                  right:
                    visible: False
                  top:
                    visible: False

    Suppose you want to draw what the Matplotlib documentation calls a "math
    textbook style plot", where the spines are centred at zero (in the
    origin of the Cartesian coordinate system) and have arrows at their ends:

    .. code-block:: yaml

        - kind: singleplot
          type: SinglePlotter1D
          properties:
            properties:
              axes:
                xlabel: Null
                ylabel: Null
                invert:
                  - x
                  - y
                spines:
                  left:
                    position: zero
                    arrow: True
                  bottom:
                    position: zero
                    arrow: True
                  right:
                    visible: False
                  top:
                    visible: False


    .. versionadded:: 0.11

    """

    def __init__(self, edge="left"):
        super().__init__()
        self.visible = True
        self.position = None
        self.bounds = None
        self.arrow = False
        self._edge = edge

    def apply(self, drawing=None):
        """
        Apply properties to spine.

        For each property, the corresponding "set_<property>" method of the
        spine will be called.

        Parameters
        ----------
        drawing: :class:`matplotlib.spines.Spine`
            Spine of an axis to set properties for

        Raises
        ------
        aspecd.exceptions.MissingDrawingError
            Raised if no line is provided.

        """
        if not drawing:
            raise aspecd.exceptions.MissingDrawingError
        for prop in self.get_properties():
            if prop == "arrow" and getattr(self, prop):
                marker_normal = {
                    "left": "^",
                    "bottom": ">",
                    "right": "^",
                    "top": ">",
                }
                marker_inverted = {
                    "left": "v",
                    "bottom": "<",
                    "right": "v",
                    "top": "<",
                }
                positions_normal = {
                    "left": [0, 1],
                    "bottom": [1, 0],
                    "right": [0, 1],
                    "top": [1, 0],
                }
                positions_inverted = {
                    "left": [0, 0],
                    "bottom": [0, 0],
                    "right": [0, 0],
                    "top": [0, 0],
                }
                if self._edge in ("top", "bottom"):
                    inverted = drawing.axes.xaxis_inverted()
                    transform = drawing.axes.get_yaxis_transform()
                else:
                    inverted = drawing.axes.yaxis_inverted()
                    transform = drawing.axes.get_xaxis_transform()
                if inverted:
                    marker = marker_inverted
                    positions = positions_inverted
                else:
                    marker = marker_normal
                    positions = positions_normal
                drawing.axes.plot(
                    *positions[self._edge],
                    marker[self._edge],
                    color=drawing.get_edgecolor(),
                    transform=transform,
                    clip_on=False,
                    label=f"arrow_{self._edge}",
                )
            elif getattr(self, prop) is not None:
                self._safe_set_drawing_property(drawing, prop)


class MarkerProperties(DrawingProperties):
    """
    Properties for marker.

    Basically, the attributes are a subset of what :mod:`matplotlib` defines
    for the marker part of :obj:`matplotlib.lines.Line2D` objects.

    Attributes
    ----------
    alpha : :class:`float` | :class:`None`
        Transparency value -- not supported on all backends.

        Valid range: [0, 1]

    edgecolor : color
        edge color of the marker

        For details see :mod:`matplotlib.colors`

        To remove the color, set it to :data:`None` (or ``Null`` in YAML)

        Default: "#000000"

    edgewidth : :class:`float`
        Width of the marker edge

    facecolor : color
        face color of the marker

        For details see :mod:`matplotlib.colors`

        To remove the color, set it to :data:`None` (or ``Null`` in YAML)

        Default: "#000000"

    facecoloralt : color
        Alternative face color of the marker

        This color gets interesting depending on the fill style.

        For details see :mod:`matplotlib.colors`

        To remove the color, set it to :data:`None` (or ``Null`` in YAML)

        Default: "none"

    fillstyle : :class:`str`
        Style to use to fill the marker.

        Allowed values are: "full", "left", "right", "bottom", "top", "none"

    size : :class:`float`
        Size of the marker.

    zorder : :class:`float`
        Zorder for the artist.

        Artists with lower zorder are drawn first.

        For a summary of the default zorder values, see the `Matplotlib
        documentation <https://matplotlib.org/stable/gallery/misc
        /zorder_demo.html>`_

    Raises
    ------
    aspecd.exceptions.MissingDrawingError
        Raised if no marker is provided.


    Examples
    --------
    Markers are typically used for plot annotations. For details, see the
    :class:`aspecd.annotation.Marker` class.


    .. versionadded:: 0.11


    """

    def __init__(self):
        super().__init__()
        self.size = None
        self.edgecolor = "#000000"
        self.facecolor = "#000000"
        self.facecoloralt = None
        self.edgewidth = None
        self.fillstyle = None

    def _safe_set_drawing_property(self, drawing=None, prop=None):
        """Safe setting of drawing properties.

        The method first checks whether the corresponding setter for the
        property exists and only in this case sets the property.


        Parameters
        ----------
        drawing : :class:`matplotlib.artist.Artist`
            Artist to set properties for

        prop : :class:`str`
            Name of the property to set

        """
        if "color" in prop and getattr(self, prop) is None:
            set_value = "none"
        else:
            set_value = getattr(self, prop)
        if hasattr(drawing, "".join(["set_", prop])):
            try:
                getattr(drawing, "".join(["set_", prop]))(set_value)
            except TypeError:
                logger.debug(
                    'Cannot set attribute "%s" for "%s"',
                    prop,
                    drawing.__class__,
                )
        elif hasattr(drawing, "".join(["set_marker", prop])):
            try:
                getattr(drawing, "".join(["set_marker", prop]))(set_value)
            except TypeError:
                logger.debug(
                    'Cannot set attribute "%s" for "%s"',
                    prop,
                    drawing.__class__,
                )
        else:
            logger.debug(
                '"%s" has no setter for attribute "%s", hence not set',
                drawing.__class__,
                prop,
            )
