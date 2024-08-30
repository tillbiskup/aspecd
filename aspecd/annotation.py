"""
Annotations of data, *e.g.* characteristics, that cannot be automated.

Annotations of data (and plots, *i.e.* graphical representations of data) are
eventually something that cannot be automated. Nevertheless, they can be
quite important for the analysis and hence for providing new scientific
insight. Furthermore, annotations of data can sometimes be added to a
graphical representation. A typical example would be to mark an artefact
with an asterisk or to highlight a characteristic. Therefore, dataset
annotations may have graphical realisations as plot annotations.


Dataset annotations
===================

All dataset annotations inherit from the
:class:`aspecd.annotation.DatasetAnnotation` base class.

Concrete dataset annotations are:

* :obj:`aspecd.annotation.Comment`

    The simplest form of an annotation is a comment applying to an entire
    dataset, such as comments stored in the metadata written during data
    acquisition. Hence, those comments do *not* belong to the metadata part of
    a dataset, but are stored as an annotation using this class.

Other frequent types of annotations are artefacts and characteristics,
for which dedicated classes are available within the ASpecD framework:

* :class:`aspecd.annotation.Artefact`
* :class:`aspecd.annotation.Characteristic`.


.. todo::

    Flesh out these additional DatasetAnnotation classes, particularly in
    light of the newly created PlotAnnotation classes that may eventually be
    a way to graphically display the dataset annotations.


For other types of annotations, simply subclass the
:class:`aspecd.annotation.DatasetAnnotation` base class.


.. _:sec:annotation:plot:

Plot(ter) annotations
=====================

Similar to datasets, plots, *i.e.* graphical representations of the data of
one or multiple datasets, can be annotated as well. Plot annotations will
always result in a graphical object of some kind added to the plot created
by a :class:`aspecd.plotting.Plotter`. Additionally, each plotter has a list
of annotations attached to it. As such, plot annotations are independent of
individual datasets and can span multiple datasets in case of plotters
involving the data of multiple datasets.

While generally, it should not matter whether a plot annotation gets added
to the plotter object before or after the actual plotting process, adding
the graphical elements annotations consist eventually of to the plot is only
possible once the :meth:`aspecd.plotting.Plotter.plot` method has been
called and the respective :attr:`aspecd.plotting.Plotter.figure` and
:attr:`aspecd.plotting.Plotter.axes` attributes are set. To this end, a plot
annotation will only actually add graphical elements if the plot exists
already, and the plotter will in turn add any annotations added prior to
plotting when its :meth:`aspecd.plotting.Plotter.plot` method is called.
This avoids side effects, as annotating a plotter does *not* create a
graphical representation that did not exist before.

All plot annotations inherit from the :class:`aspecd.annotation.PlotAnnotation`
base class.

Concrete plot annotations are:

* :class:`aspecd.annotation.VerticalLine`

    Add vertical line(s) to a plot(ter).

* :class:`aspecd.annotation.HorizontalLine`

    Add horizontal line(s) to a plot(ter).

* :class:`aspecd.annotation.VerticalSpan`

    Add vertical span(s) (rectangles) to a plot(ter).

* :class:`aspecd.annotation.HorizontalSpan`

    Add horizontal span(s) (rectangles) to a plot(ter).

* :class:`aspecd.annotation.Text`

    Add text(s) to a plot(ter).

* :class:`aspecd.annotation.TextWithLine`

    Add text(s) with a connecting line to a plot(ter).

* :class:`aspecd.annotation.Marker`

    Add marker(s) to a plot(ter).

* :class:`aspecd.annotation.FillBetween`

    Coloured surface under a curve or between curves.


Module documentation
====================

"""

import matplotlib
import numpy as np

import aspecd.dataset
import aspecd.exceptions
import aspecd.history
import aspecd.plotting
from aspecd.utils import ToDictMixin


class DatasetAnnotation(ToDictMixin):
    """
    Annotations are user-supplied additional information to datasets.

    Whereas many processing steps of data can be fully automated, annotations
    are mostly the domain of human interaction, looking at the data of a
    dataset and providing some sort of comments, trying to make sense of the
    data.

    Annotations can have different types, such as simple "comments",
    e.g. saying that a dataset is not useful as something during measurement
    went wrong, they can highlight "characteristics" of the data, they can
    point to "artefacts". Each of these types is represented by a class on
    its own that is derived from the :class:`DatasetAnnotation` base class.
    Additionally, the type is reflected in the "type" property that gets
    set automatically to the class name in lower-case letters.

    Each annotation has a scope (such as "point", "slice", "area", "distance",
    "dataset") it belongs to, and a "contents" property (dict) containing the
    actual content of the annotation.

    Attributes
    ----------
    type : :class:`str`
        Textual description of the type of annotation: lowercase class name

        Set automatically, don't change
    content : :class:`dict`
        Actual content of the annotation

        Generic place for more information
    dataset : :obj:`aspecd.dataset.Dataset`
        Dataset the annotation belongs to

    Raises
    ------
    aspecd.annotation.NoContentError
        Raised when annotation contains no content(s)
    aspecd.annotation.MissingDatasetError
        Raised when no dataset exists to act on

    """

    def __init__(self):
        super().__init__()
        self.type = self.__class__.__name__.lower()
        self.content = {}
        self.dataset = None
        # Scope of the annotation; see list of allowed scopes below
        self._scope = ""
        # List of allowed scopes
        self._allowed_scopes = [
            "dataset",
            "slice",
            "point",
            "area",
            "distance",
        ]
        # Default scope if none is set explicitly
        self._default_scope = self._allowed_scopes[0]
        self._exclude_from_to_dict = ["dataset", "type"]
        self.__kind__ = "annotation"

    @property
    def scope(self):
        """
        Get or set the scope the annotation applies to.

        The list of allowed scopes is stored in the private property
        `_allowed_scopes`, and if no scope is set when the annotation is
        finally applied to a dataset, a default scope will be used that is
        stored in the private property `_default_scope` (and is defined as
        one element of the list of allowed scopes)

        Currently, allowed scopes are: ``dataset``, ``slice``, ``point``,
        ``area``, ``distance``.

        """
        return self._scope

    @scope.setter
    def scope(self, scope):
        if scope not in self._allowed_scopes:
            raise aspecd.exceptions.UnknownScopeError(
                "Allowed scopes are: " + " ".join(self._allowed_scopes)
            )
        self._scope = scope

    def annotate(self, dataset=None, from_dataset=False):
        """
        Annotate a dataset with the given annotation.

        If no dataset is provided at method call, but is set as property in
        the Annotation object, the :meth:`aspecd.dataset.Dataset.annotate`
        method of the dataset will be called and thus the history written.

        If no dataset is provided at method call nor as property in the
        object, the method will raise a respective exception.

        If no scope is set in the :obj:`aspecd.annotation.Annotation`
        object, a default value will be used that can be set in derived
        classes in the private property ``_default_scope``. A full list of
        scopes is contained in the private property ``_allowed_scopes``.
        See the :attr:`scope` property for details.

        The :obj:`aspecd.dataset.Dataset` object always calls this method
        with the respective dataset as argument. Therefore, in this case
        setting the dataset property within the Annotation object is not
        necessary.

        Parameters
        ----------
        dataset : :class:`aspecd.dataset.Dataset`
            dataset to annotate

        from_dataset : :class:`bool`
            whether we are called from within a dataset

            Defaults to "False" and shall never be set manually.

        Returns
        -------
        dataset : :class:`aspecd.dataset.Dataset`
            dataset that has been annotated

        """
        self._check_prerequisites()
        self._set_scope()
        self._assign_dataset(dataset)
        self._call_from_dataset(from_dataset)
        return self.dataset

    def create_history_record(self):
        """
        Create history record to be added to the dataset.

        Usually, this method gets called from within the
        :meth:`aspecd.dataset.Dataset.annotate` method of the
        :class:`aspecd.dataset.Dataset` class and ensures the history of
        each annotation step to get written properly.

        Returns
        -------
        history_record : :class:`aspecd.history.AnnotationHistoryRecord`
            history record for annotation step

        """
        history_record = aspecd.history.AnnotationHistoryRecord(
            annotation=self, package=self.dataset.package_name
        )
        return history_record

    def _check_prerequisites(self):
        if not self.content:
            raise aspecd.exceptions.NoContentError

    def _set_scope(self):
        if not self.scope:
            self._scope = self._default_scope

    def _assign_dataset(self, dataset):
        if not dataset:
            if not self.dataset:
                raise aspecd.exceptions.MissingDatasetError
        else:
            self.dataset = dataset

    def _call_from_dataset(self, from_dataset):
        if not from_dataset:
            self.dataset.annotate(self)


class Comment(DatasetAnnotation):
    """The most basic form of annotation: a simple textual comment."""

    def __init__(self):
        super().__init__()
        self.content["comment"] = ""

    @property
    def comment(self):
        """
        Get comment of annotation.

        Returns
        -------
        comment : :class:`str`
            Actual comment string

        """
        return self.content["comment"]

    @comment.setter
    def comment(self, comment=""):
        self.content["comment"] = comment


class Artefact(DatasetAnnotation):
    """Mark something as an artefact."""

    def __init__(self):
        super().__init__()
        self.content["comment"] = ""


class Characteristic(DatasetAnnotation):
    """Base class for characteristics."""


class PlotAnnotation(ToDictMixin):
    """
    Base class for annotations for graphical representations (plots).

    Whereas many processing steps of data can be fully automated, annotations
    are mostly the domain of human interaction, looking at the graphical
    representation of the data of a dataset and providing some sort of
    comments, trying to make sense of the data. Often, being able to add
    some kind of annotation to these graphical representations is both,
    tremendously helpful and required for further analysis.

    Annotations can have different types, such as horizontal and vertical
    lines added to a plot for comparing different data.

    Each of these types is represented by a class on
    its own that is derived from the :class:`PlotAnnotation` base class.
    Additionally, the type is reflected in the "type" property that gets
    set automatically to the class name in lower-case letters.

    While generally, it should not matter whether a plot annotation gets
    added to the plotter object before or after the actual plotting process,
    adding the graphical elements annotations consist eventually of to the
    plot is only possible once the :meth:`aspecd.plotting.Plotter.plot`
    method has been called and the respective
    :attr:`aspecd.plotting.Plotter.figure` and
    :attr:`aspecd.plotting.Plotter.axes` attributes are set. To this end,
    a plot annotation will only actually add graphical elements if the plot
    exists already, and the plotter will in turn add any annotations added
    prior to plotting when its :meth:`aspecd.plotting.Plotter.plot` method
    is called. This avoids side effects, as annotating a plotter does *not*
    create a graphical representation that did not exist before.

    Attributes
    ----------
    plotter : :class:`aspecd.plotting.Plotter`
        Plotter the annotation belongs to

    type : :class:`str`
        Textual description of the type of annotation: lowercase class name

        Set automatically, don't change

    parameters : :class:`dict`
        All parameters necessary for the annotation, implicit and explicit

    properties : :class:`None`
        Properties of the annotation, defining its appearance

    drawings : :class:`list`
        Actual graphical representations of the annotation within the plot

    Examples
    --------
    For examples of how such a report task may be included into a recipe,
    see below:

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


    .. versionadded:: 0.9

    """

    def __init__(self):
        super().__init__()
        self.plotter = None
        self.type = self.__class__.__name__.lower()
        self.parameters = {}
        self.properties = None
        self.drawings = []
        self._exclude_from_to_dict = ["plotter", "type", "drawings"]

    def annotate(self, plotter=None, from_plotter=False):
        """
        Annotate a plot(ter) with the given annotation.

        If no plotter is provided at method call, but is set as property in
        the Annotation object, the :meth:`aspecd.plotting.Plotter.annotate`
        method of the plotter will be called and thus the history written.

        If no plotter is provided at method call nor as property in the
        object, the method will raise a respective exception.

        Parameters
        ----------
        plotter : :class:`aspecd.plotting.Plotter`
            Plot(ter) to annotate

        from_plotter : :class:`bool`
            whether we are called from within a plotter

            Defaults to "False" and shall never be set manually.

        Returns
        -------
        plotter : :class:`aspecd.plotting.Plotter`
            Plotter that has been annotated

        """
        self._assign_plotter(plotter)
        self._call_from_plotter(from_plotter)
        if self.plotter.figure:
            self._perform_task()
            for drawing in self.drawings:
                self.properties.apply(drawing=drawing)
        return self.plotter

    def _assign_plotter(self, plotter):
        if not plotter:
            if not self.plotter:
                raise aspecd.exceptions.MissingPlotterError
        else:
            self.plotter = plotter

    def _call_from_plotter(self, from_plotter):
        if not from_plotter:
            self.plotter.annotate(self)

    def _perform_task(self):
        pass


class VerticalLine(PlotAnnotation):
    # noinspection PyUnresolvedReferences
    """
    Vertical line(s) added to a plot.

    Vertical lines are often useful to compare peak positions or as a
    general guide to the eye of the observer.

    The properties of the lines can be controlled in quite some detail using
    the :attr:`properties` property. Note that all lines will share the same
    properties. If you need to add lines with different properties to the
    same plot, use several :class:`VerticalLine` objects and annotate
    separately.

    Attributes
    ----------
    parameters : :class:`dict`
        All parameters necessary for the annotation, implicit and explicit

        The following keys exist:

        positions : :class:`list`
            List of the positions vertical lines should appear at

            Values are in axis (data) units.

        limits : :class:`list`
            Limits of the vertical lines

            If not given, the vertical lines will span the entire range of
            the current axes.

            Values are in relative units, within a range of [0, 1].

    properties : :class:`aspecd.plotting.LineProperties`
        Properties of the line(s) within a plot

        For the properties that can be set this way, see the documentation
        of the :class:`aspecd.plotting.LineProperties` class.


    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. The examples focus each on a single
    aspect.

    Generally and for obvious reasons, you need to have both, a plot task
    and a plotannotation task. It does not really matter which task you
    define first, the plot or the plot annotation. There are only marginal
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


    .. versionadded:: 0.9

    """

    def __init__(self):
        super().__init__()
        self.parameters["positions"] = []
        self.parameters["limits"] = []
        self.properties = aspecd.plotting.LineProperties()

    def _perform_task(self):
        for position in self.parameters["positions"]:
            if self.parameters["limits"]:
                line = self.plotter.ax.axvline(
                    x=position,
                    ymin=self.parameters["limits"][0],
                    ymax=self.parameters["limits"][1],
                )
            else:
                line = self.plotter.ax.axvline(x=position)
            self.drawings.append(line)


class HorizontalLine(PlotAnnotation):
    # noinspection PyUnresolvedReferences
    """
    Horizontal line(s) added to a plot.

    Horizontal lines are often useful to compare peak positions or as a
    general guide to the eye of the observer.

    The properties of the lines can be controlled in quite some detail using
    the :attr:`properties` property. Note that all lines will share the same
    properties. If you need to add lines with different properties to the
    same plot, use several :class:`HorizontalLine` objects and annotate
    separately.

    Attributes
    ----------
    parameters : :class:`dict`
        All parameters necessary for the annotation, implicit and explicit

        The following keys exist:

        positions : :class:`list`
            List of the positions horizontal lines should appear at

            Values are in axis (data) units.

        limits : :class:`list`
            Limits of the horizontal lines

            If not given, the horizontal lines will span the entire range of
            the current axes.

            Values are in relative units, within a range of [0, 1].

    properties : :class:`aspecd.plotting.LineProperties`
        Properties of the line(s) within a plot

        For the properties that can be set this way, see the documentation
        of the :class:`aspecd.plotting.LineProperties` class.


    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. The examples focus each on a single
    aspect.

    Generally and for obvious reasons, you need to have both, a plot task
    and a plotannotation task. It does not really matter which task you
    define first, the plot or the plot annotation. There are only marginal
    differences, and both ways are shown below.

    .. code-block:: yaml

        - kind: multiplot
          type: MultiPlotter1DStacked
          properties:
            filename: plot1Dstacked.pdf
          result: plot1Dstacked

        - kind: plotannotation
          type: HorizontalLine
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
          type: HorizontalLine
          properties:
            parameters:
              positions:
                - 21
                - 42
            properties:
              color: green
              linewidth: 1
              linestyle: dotted
          result: hlines

        - kind: multiplot
          type: MultiPlotter1DStacked
          properties:
            filename: plot1Dstacked.pdf
          annotations:
            - hlines


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
          type: HorizontalLine
          properties:
            parameters:
              positions: [35, 42]
          plotter:
            - plot1
            - plot2

    In this case, the annotation will be applied to both plots
    independently. Note that the example has been reduced to the key
    aspects. In a real situation, the two plotters will differ much more.


    .. versionadded:: 0.9

    """

    def __init__(self):
        super().__init__()
        self.parameters["positions"] = []
        self.parameters["limits"] = []
        self.properties = aspecd.plotting.LineProperties()

    def _perform_task(self):
        for position in self.parameters["positions"]:
            if self.parameters["limits"]:
                line = self.plotter.ax.axhline(
                    y=position,
                    xmin=self.parameters["limits"][0],
                    xmax=self.parameters["limits"][1],
                )
            else:
                line = self.plotter.ax.axhline(y=position)
            self.drawings.append(line)


class Text(PlotAnnotation):
    """
    Text added to a plot.

    One of the most versatile ways to annotate a plot is adding text labels
    at defined positions. Basically, this class is the ASpecD wrapper to
    :meth:`matplotlib.axes.Axes.text`. In short, you provide coordinates
    (*x*, *y*) for the location and a text label. By default, coordinates
    are data coordinates and specify the bottom left corner of the text.

    The properties of the texts can be controlled in quite some detail using
    the :attr:`properties` property. Note that all texts will share the same
    properties. If you need to add texts with different properties to the
    same plot, use several :class:`Text` objects and annotate separately.


    Attributes
    ----------
    parameters : :class:`dict`
        All parameters necessary for the annotation, implicit and explicit

        The following keys exist:

        positions : :class:`list`
            List of the positions texts should appear at.

            Note that each position is itself a list: [*x*, *y*]

            Values are in axis (data) units.

        xpositions : :class:`list`
            List of the *x* positions texts should appear at.

            This allows to set *x* positions from the result of other tasks,
            *e.g.* a peak finding analysis step.

            If ``xpositions`` is set, you need to set ``ypositions`` as well.
            However, you can set either a single element or even a scalar
            (not a list). In this case, the single *y* position is expanded
            to match the number of *x* positions, *i.e.*, all texts will
            appear with the same *y* position.

            If you provide both, ``positions`` and
            ``xpositions``/``ypositions``, the latter couple wins.

            Values are in axis (data) units.

        ypositions : :class:`list` or :class:`float`
            List of the *y* positions texts should appear at.

            If ``xpositions`` is set, you need to set ``ypositions`` as well.
            However, you can set either a single element or even a scalar
            (not a list). In this case, the single *y* position is expanded
            to match the number of *x* positions, *i.e.*, all texts will
            appear with the same *y* position.

            If you provide both, ``positions`` and
            ``xpositions``/``ypositions``, the latter couple wins.

            Values are in axis (data) units.

        texts : :class:`list`
            Texts that should appear at the individual positions.

            Each text is a :class:`str`, obviously.

    properties : :class:`aspecd.plotting.TextProperties`
        Properties of the text(s) within a plot

        For the properties that can be set this way, see the documentation
        of the :class:`aspecd.plotting.TextProperties` class.

    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. The examples focus each on a single
    aspect.

    Generally and for obvious reasons, you need to have both, a plot task
    and a plotannotation task. It does not really matter which task you
    define first, the plot or the plot annotation. There are only marginal
    differences, and both ways are shown below.

    .. code-block:: yaml

        - kind: singleplot
          type: SinglePlotter1D
          properties:
            filename: plot1D.pdf
          result: plot1D

        - kind: plotannotation
          type: Text
          properties:
            parameters:
              positions:
                - [0.5, 0.5]
                - [1.0, 0.5]
              texts:
                - "Lorem ipsum"
                - "dolor sit amet"
            properties:
              color: green
              fontsize: large
              fontstyle: oblique
              rotation: 30
          plotter: plot1D


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
          type: Text
          properties:
            parameters:
              positions:
                - [0.5, 0.5]
                - [1.0, 0.5]
              texts:
                - "Lorem ipsum"
                - "dolor sit amet"
            properties:
              color: green
              fontsize: large
              fontstyle: oblique
              rotation: 30
          result: text

        - kind: singleplot
          type: SinglePlotter1D
          properties:
            filename: plot1D.pdf
          annotations:
            - text


    In this way, you can add the same annotation to several plots,
    and be sure that each annotation is handled as a separate object.

    Suppose you have more than one plotter you want to apply an annotation
    to. In this case, the ``plotter`` property of the plotannotation task is
    a list rather than a string:

    .. code-block:: yaml

        - kind: singleplot
          type: SinglePlotter1D
          result: plot1

        - kind: singleplot
          type: SinglePlotter1D
          result: plot2

        - kind: plotannotation
          type: Text
          properties:
            parameters:
              positions:
                - [0.5, 0.5]
                - [1.0, 0.5]
              texts:
                - "Lorem ipsum"
                - "dolor sit amet"
          plotter:
            - plot1
            - plot2

    In this case, the annotation will be applied to both plots
    independently. Note that the example has been reduced to the key
    aspects. In a real situation, the two plotters will differ much more.


    .. versionadded:: 0.10

    """

    def __init__(self):
        super().__init__()
        self.parameters["positions"] = []
        self.parameters["xpositions"] = []
        self.parameters["ypositions"] = []
        self.parameters["texts"] = []
        self.properties = aspecd.plotting.TextProperties()

    def _perform_task(self):
        if isinstance(self.parameters["xpositions"], np.ndarray):
            self.parameters["xpositions"] = self.parameters[
                "xpositions"
            ].tolist()
        if self.parameters["xpositions"] and (
            self.parameters["ypositions"]
            or self.parameters["ypositions"] == 0
        ):
            xpositions = self.parameters["xpositions"]
            ypositions = self.parameters["ypositions"]
            if np.isscalar(ypositions):
                ypositions = [ypositions] * len(xpositions)
            if len(ypositions) == 1:
                ypositions = ypositions * len(xpositions)
            positions = []
            for idx, xposition in enumerate(xpositions):
                positions.append([xposition, ypositions[idx]])
        else:
            positions = self.parameters["positions"]
        for idx, position in enumerate(positions):
            text = self.plotter.ax.text(
                position[0], position[1], self.parameters["texts"][idx]
            )
            self.drawings.append(text)


class VerticalSpan(PlotAnnotation):
    """
    Vertical span(s) (rectangle) added to a plot.

    Vertical spans are often useful to highlight areas of a plot, such as
    peaks.

    The properties of the spans can be controlled in quite some detail using
    the :attr:`properties` property. Note that all spans will share the same
    properties. If you need to add spans with different properties to the
    same plot, use several :class:`VerticalSpan` objects and annotate
    separately.

    Attributes
    ----------
    parameters : :class:`dict`
        All parameters necessary for the annotation, implicit and explicit

        The following keys exist:

        positions : :class:`list`
            List of the positions vertical spans should appear at.

            Each span needs two coordinates: [xmin, xmax].

            If you want to have more than one span, provide a list of lists.

            Values are in axis (data) units.

        limits : :class:`list`
            Limits of the vertical spans

            If not given, the vertical spans will span the entire range of
            the current axes.

            Values are in relative units, within a range of [0, 1].

    properties : :class:`aspecd.plotting.PatchProperties`
        Properties of the span(s) within a plot

        For the properties that can be set this way, see the documentation
        of the :class:`aspecd.plotting.PatchProperties` class.


    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. The examples focus each on a single
    aspect.

    Generally and for obvious reasons, you need to have both, a plot task
    and a plotannotation task. It does not really matter which task you
    define first, the plot or the plot annotation. There are only marginal
    differences, and both ways are shown below.

    .. code-block:: yaml

        - kind: singleplot
          type: SinglePlotter1D
          properties:
            filename: plot1D.pdf
          result: plot1D

        - kind: plotannotation
          type: VerticalSpan
          properties:
            parameters:
              positions: [[35, 42]]
            properties:
              edgecolor: Null
              facecolor: green
              alpha: 0.5
          plotter: plot1D


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
          type: VerticalSpan
          properties:
            parameters:
              positions:
                - [35, 42]
                - [21, 24]
            properties:
              edgecolor: Null
              facecolor: green
              alpha: 0.5
          result: vspans

        - kind: singleplot
          type: SinglePlotter1D
          properties:
            filename: plot1D.pdf
          annotations:
            - vspans


    In this way, you can add the same annotation to several plots,
    and be sure that each annotation is handled as a separate object.

    Suppose you have more than one plotter you want to apply an annotation
    to. In this case, the ``plotter`` property of the plotannotation task is
    a list rather than a string:

    .. code-block:: yaml

        - kind: singleplot
          type: SinglePlotter1D
          result: plot1

        - kind: singleplot
          type: SinglePlotter1D
          result: plot2

        - kind: plotannotation
          type: VerticalSpan
          properties:
            parameters:
              positions:
                - [35, 42]
          plotter:
            - plot1
            - plot2

    In this case, the annotation will be applied to both plots
    independently. Note that the example has been reduced to the key
    aspects. In a real situation, the two plotters will differ much more.


    .. versionadded:: 0.11


    """

    def __init__(self):
        super().__init__()
        self.parameters["positions"] = []
        self.parameters["limits"] = []
        self.properties = aspecd.plotting.PatchProperties()

    def _perform_task(self):
        for position in self.parameters["positions"]:
            if self.parameters["limits"]:
                span = self.plotter.ax.axvspan(
                    xmin=position[0],
                    xmax=position[1],
                    ymin=self.parameters["limits"][0],
                    ymax=self.parameters["limits"][1],
                )
            else:
                span = self.plotter.ax.axvspan(
                    xmin=position[0], xmax=position[1]
                )
            self.drawings.append(span)


class HorizontalSpan(PlotAnnotation):
    """
    Horizontal span(s) (rectangle) added to a plot.

    Horizontal spans are often useful to highlight areas of a plot.

    The properties of the spans can be controlled in quite some detail using
    the :attr:`properties` property. Note that all spans will share the same
    properties. If you need to add spans with different properties to the
    same plot, use several :class:`HorizontalSpan` objects and annotate
    separately.

    Attributes
    ----------
    parameters : :class:`dict`
        All parameters necessary for the annotation, implicit and explicit

        The following keys exist:

        positions : :class:`list`
            List of the positions hoizontal spans should appear at.

            Each span needs two coordinates: [ymin, ymax].

            If you want to have more than one span, provide a list of lists.

            Values are in axis (data) units.

        limits : :class:`list`
            Limits of the hoizontal spans

            If not given, the hoizontal spans will span the entire range of
            the current axes.

            Values are in relative units, within a range of [0, 1].

    properties : :class:`aspecd.plotting.PatchProperties`
        Properties of the span(s) within a plot

        For the properties that can be set this way, see the documentation
        of the :class:`aspecd.plotting.PatchProperties` class.


    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. The examples focus each on a single
    aspect.

    Generally and for obvious reasons, you need to have both, a plot task
    and a plotannotation task. It does not really matter which task you
    define first, the plot or the plot annotation. There are only marginal
    differences, and both ways are shown below.

    .. code-block:: yaml

        - kind: singleplot
          type: SinglePlotter1D
          properties:
            filename: plot1D.pdf
          result: plot1D

        - kind: plotannotation
          type: HorizontalSpan
          properties:
            parameters:
              positions: [[35, 42]]
            properties:
              edgecolor: Null
              facecolor: green
              alpha: 0.5
          plotter: plot1D


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
          type: HorizontalSpan
          properties:
            parameters:
              positions:
                - [35, 42]
                - [21, 24]
            properties:
              edgecolor: Null
              facecolor: green
              alpha: 0.5
          result: vspans

        - kind: singleplot
          type: SinglePlotter1D
          properties:
            filename: plot1D.pdf
          annotations:
            - vspans


    In this way, you can add the same annotation to several plots,
    and be sure that each annotation is handled as a separate object.

    Suppose you have more than one plotter you want to apply an annotation
    to. In this case, the ``plotter`` property of the plotannotation task is
    a list rather than a string:

    .. code-block:: yaml

        - kind: singleplot
          type: SinglePlotter1D
          result: plot1

        - kind: singleplot
          type: SinglePlotter1D
          result: plot2

        - kind: plotannotation
          type: HorizontalSpan
          properties:
            parameters:
              positions:
                - [35, 42]
          plotter:
            - plot1
            - plot2

    In this case, the annotation will be applied to both plots
    independently. Note that the example has been reduced to the key
    aspects. In a real situation, the two plotters will differ much more.


    .. versionadded:: 0.11

    """

    def __init__(self):
        super().__init__()
        self.parameters["positions"] = []
        self.parameters["limits"] = []
        self.properties = aspecd.plotting.PatchProperties()

    def _perform_task(self):
        for position in self.parameters["positions"]:
            if self.parameters["limits"]:
                span = self.plotter.ax.axhspan(
                    ymin=position[0],
                    ymax=position[1],
                    xmin=self.parameters["limits"][0],
                    xmax=self.parameters["limits"][1],
                )
            else:
                span = self.plotter.ax.axhspan(
                    ymin=position[0], ymax=position[1]
                )
            self.drawings.append(span)


class TextWithLine(PlotAnnotation):
    r"""
    Text with connecting line added to a plot.

    One of the most versatile ways to annotate a plot is adding text labels
    at defined positions. However, if you intend to annotate data points,
    sometimes it is helpful to have a connecting line between data point and
    text. This class uses :meth:`matplotlib.axes.Axes.annotate` under the hood.
    Basically, you provide coordinates (*x*, *y*) for the location,
    an offset (*dx*, *dy*), and a text label. By default, coordinates are
    data coordinates.

    Depending on the horizontal offset *dx*, the connecting line is either a
    straight line (*dx* = 0), or it has a 45° hook in the upper part to the
    left (*dx* < 0) or to the right (*dx* > 0). Similarly, if you set a
    *negative* vertical  offset, the hook is obviously in the lower part.

    In ASCII art, this may look like this::

        foo  foo  foo            | | |
          \   |   /              | | |
           \  |  /               | | |
            | | |               /  |  \
            | | |              /   |   \
            | | |            foo  foo  foo

    The properties of the texts and the connecting line can be controlled in
    quite some detail using the :attr:`properties` property. Note that all
    texts will share the same properties. If you need to add texts with
    different properties to the same plot, use several :class:`TextWithLine`
    objects and annotate separately.


    Attributes
    ----------
    parameters : :class:`dict`
        All parameters necessary for the annotation, implicit and explicit

        The following keys exist:

        positions : :class:`list`
            List of the positions the lines should point to.

            Note that each position is itself a list: [*x*, *y*]

            Values are in axis (data) units.

        offsets : :class:`list`
            List of the offsets texts should appear at.

            Note that each position is itself a list: [*dx*, *dy*]

            Depending on the horizontal offset *dx*, the connecting line is
            either a straight line (*dx* = 0), or it has a 45° hook in the
            upper part to the left (*dx* < 0) or to the right (*dx* > 0).
            Similarly, if you set a *negative* vertical  offset, the hook is
            obviously in the lower part.

            Values are in axis (data) units.

        xpositions : :class:`list`
            List of the *x* positions texts should appear at.

            This allows to set *x* positions from the result of other tasks,
            *e.g.* a peak finding analysis step.

            If ``xpositions`` is set, you need to set ``ypositions`` as well.
            However, you can set either a single element or even a scalar
            (not a list). In this case, the single *y* position is expanded
            to match the number of *x* positions, *i.e.*, all texts will
            appear with the same *y* position.

            If you provide both, ``positions`` and
            ``xpositions``/``ypositions``, the latter couple wins.

            Values are in axis (data) units.

        ypositions : :class:`list` or :class:`float`
            List of the *y* positions texts should appear at.

            If ``xpositions`` is set, you need to set ``ypositions`` as well.
            However, you can set either a single element or even a scalar
            (not a list). In this case, the single *y* position is expanded
            to match the number of *x* positions, *i.e.*, all texts will
            appear with the same *y* position.

            If you provide both, ``positions`` and
            ``xpositions``/``ypositions``, the latter couple wins.

            Values are in axis (data) units.

        texts : :class:`list`
            Texts that should appear at the individual positions.

            Each text is a :class:`str`, obviously.

    properties : :class:`aspecd.plotting.AnnotationProperties`
        Properties of the text(s) and line(s) within a plot

        For the properties that can be set this way, see the documentation
        of the :class:`aspecd.plotting.AnnotationProperties` class.


    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. The examples focus each on a single
    aspect.

    Generally and for obvious reasons, you need to have both, a plot task
    and a plotannotation task. It does not really matter which task you
    define first, the plot or the plot annotation. There are only marginal
    differences, and both ways are shown below.

    .. code-block:: yaml

        - kind: singleplot
          type: SinglePlotter1D
          properties:
            filename: plot1D.pdf
          result: plot1D

        - kind: plotannotation
          type: TextWithLine
          properties:
            parameters:
              positions:
                - [0.5, 0.5]
                - [0.55, 0.5]
              offsets:
                - [0.5, 2]
                - [0.8, 2]
              texts:
                - "Lorem ipsum"
                - "dolor sit amet"
            properties:
              text:
                color: green
                fontsize: large
                fontstyle: oblique
              line:
                linestyle: ":"
          plotter: plot1D


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
          type: TextWithLine
          properties:
            parameters:
              positions:
                - [0.5, 0.5]
                - [0.55, 0.5]
              offsets:
                - [0.5, 2]
                - [0.8, 2]
              texts:
                - "Lorem ipsum"
                - "dolor sit amet"
            properties:
              text:
                color: green
                fontsize: large
                fontstyle: oblique
              line:
                linestyle: ":"
          result: text

        - kind: singleplot
          type: SinglePlotter1D
          properties:
            filename: plot1D.pdf
          annotations:
            - text


    In this way, you can add the same annotation to several plots,
    and be sure that each annotation is handled as a separate object.

    Suppose you have more than one plotter you want to apply an annotation
    to. In this case, the ``plotter`` property of the plotannotation task is
    a list rather than a string:

    .. code-block:: yaml

        - kind: singleplot
          type: SinglePlotter1D
          result: plot1

        - kind: singleplot
          type: SinglePlotter1D
          result: plot2

        - kind: plotannotation
          type: TextWithLine
          properties:
            parameters:
              positions:
                - [0.5, 0.5]
                - [0.55, 0.5]
              offsets:
                - [0.5, 2]
                - [0.8, 2]
              texts:
                - "Lorem ipsum"
                - "dolor sit amet"
          plotter:
            - plot1
            - plot2

    In this case, the annotation will be applied to both plots
    independently. Note that the example has been reduced to the key
    aspects. In a real situation, the two plotters will differ much more.


    .. versionadded:: 0.11


    """

    def __init__(self):
        super().__init__()
        self.parameters["positions"] = []
        self.parameters["offsets"] = []
        self.parameters["xpositions"] = []
        self.parameters["ypositions"] = []
        self.parameters["texts"] = []
        self.properties = aspecd.plotting.AnnotationProperties()

    def _perform_task(self):
        if isinstance(self.parameters["xpositions"], np.ndarray):
            self.parameters["xpositions"] = self.parameters[
                "xpositions"
            ].tolist()
        if self.parameters["xpositions"] and self.parameters["ypositions"]:
            xpositions = self.parameters["xpositions"]
            ypositions = self.parameters["ypositions"]
            if np.isscalar(ypositions):
                ypositions = [ypositions] * len(xpositions)
            if len(ypositions) == 1:
                ypositions = ypositions * len(xpositions)
            positions = []
            for idx, xposition in enumerate(xpositions):
                positions.append([xposition, ypositions[idx]])
        else:
            positions = self.parameters["positions"]
        for idx, position in enumerate(positions):
            horizontalalignment = "center"
            connectionstyle = None
            relpos = [0.5, 0.5]
            if self.parameters["offsets"]:
                offset = []
                for i_value, value in enumerate(
                    self.parameters["offsets"][idx]
                ):
                    offset.append(position[i_value] + value)
                if self.parameters["offsets"][idx][0] > 0:
                    if self.parameters["offsets"][idx][1] > 0:
                        connectionstyle = (
                            "angle, angleA=-135, angleB=90, rad=0"
                        )
                        relpos = [0, 0]
                    else:
                        connectionstyle = (
                            "angle, angleA=-45, angleB=90, rad=0"
                        )
                        relpos = [0, 1]
                    horizontalalignment = "left"
                elif self.parameters["offsets"][idx][0] < 0:
                    if self.parameters["offsets"][idx][1] > 0:
                        connectionstyle = (
                            "angle, angleA=-45, angleB=90, rad=0"
                        )
                        relpos = [1, 0]
                    else:
                        connectionstyle = (
                            "angle, angleA=-135, angleB=90, rad=0"
                        )
                        relpos = [1, 1]
                    horizontalalignment = "right"
            else:
                offset = position
            annotation = self.plotter.ax.annotate(
                self.parameters["texts"][idx],
                position,
                horizontalalignment=horizontalalignment,
                xytext=offset,
                arrowprops={
                    "arrowstyle": "-",
                    "relpos": relpos,
                    "connectionstyle": connectionstyle,
                },
            )
            self.drawings.append(annotation)


class Marker(PlotAnnotation):
    r"""
    Marker added to a plot.

    One very common way to annotate a plot is adding markers at defined
    positions. Basically, this class is the ASpecD wrapper to
    :meth:`matplotlib.axes.Axes.plot` with only a marker used and no line
    drawn. Basically, you provide coordinates (*x*, *y*) for the location
    and a marker. By default, coordinates are data coordinates and specify
    the centre of the marker.

    The properties of the markers can be controlled in quite some detail using
    the :attr:`properties` property. Note that all markers will share the same
    properties. If you need to add markers with different properties to the
    same plot, use several :class:`Marker` objects and annotate separately.

    Attributes
    ----------
    parameters : :class:`dict`
        All parameters necessary for the annotation, implicit and explicit

        The following keys exist:

        positions : :class:`list`
            List of the positions markers should appear at.

            Note that each position is itself a list: [*x*, *y*]

            Values are in axis (data) units.

        xpositions : :class:`list`
            List of the *x* positions markers should appear at.

            This allows to set *x* positions from the result of other tasks,
            *e.g.* a peak finding analysis step.

            If ``xpositions`` is set, you need to set ``ypositions`` as well.
            However, you can set either a single element or even a scalar
            (not a list). In this case, the single *y* position is expanded
            to match the number of *x* positions, *i.e.*, all markers will
            appear with the same *y* position.

            If you provide both, ``positions`` and
            ``xpositions``/``ypositions``, the latter couple wins.

            Values are in axis (data) units.

        ypositions : :class:`list` or :class:`float`
            List of the *y* positions markers should appear at.

            If ``xpositions`` is set, you need to set ``ypositions`` as well.
            However, you can set either a single element or even a scalar
            (not a list). In this case, the single *y* position is expanded
            to match the number of *x* positions, *i.e.*, all markers will
            appear with the same *y* position.

            If you provide both, ``positions`` and
            ``xpositions``/``ypositions``, the latter couple wins.

            Values are in axis (data) units.

        yoffset : :class:`float`
            Additional offset for the *y* direction added to the *y* position.

            Useful, *e.g.*, when you want to mark peaks, but not on the line
            itself, but slightly above (positive offset values) or below (
            negative offset values).

            Default: 0

        marker : :class:`str`
            Marker that shall be added to the plot.

            There is a large list of predefined markers available. For
            details, see :mod:`matplotlib.markers`. Note that you can use
            both, the code and the keyword of a specific marker, as returned
            by the :attr:`matplotlib.lines.Line2D.markers` attribute:

            ========  ================
            code      keyword
            ========  ================
            ``"."``   point
            ``","``   pixel
            ``"o"``   circle
            ``"v"``   triangle_down
            ``"^"``   triangle_up
            ``"<"``   triangle_left
            ``">"``   triangle_right
            ``"1"``   tri_down
            ``"2"``   tri_up
            ``"3"``   tri_left
            ``"4"``   tri_right
            ``"8"``   octagon
            ``"s"``   square
            ``"p"``   pentagon
            ``"*"``   star
            ``"h"``   hexagon1
            ``"H"``   hexagon2
            ``"+"``   plus
            ``"x"``   x
            ``"D"``   diamond
            ``"d"``   thin_diamond
            ``"|"``   vline
            ``"_"``   hline
            ``"P"``   plus_filled
            ``"X"``   x_filled
            ``0``     tickleft
            ``1``     tickright
            ``2``     tickup
            ``3``     tickdown
            ``4``     caretleft
            ``5``     caretright
            ``6``     caretup
            ``7``     caretdown
            ``8``     caretleftbase
            ``9``     caretrightbase
            ``10``    caretupbase
            ``11``    caretdownbase
            ========  ================

            Please note the difference between the string ``"1"`` and the
            number ``1`` that result in triangle down and tick right
            markers, respectively.

            Furthermore, you can use markers created from TeX symbols using
            MathText (LaTeX needs not to be installed). Just surround your
            marker with ``$`` signs, such as ``"$\u266B$"`` or
            ``"$\mathcal{A}$"``.

            If you provide multiple positions, the same marker will be added
            multiple times.

    properties : :class:`aspecd.plotting.MarkerProperties`
        Properties of the marker(s) within a plot

        For the properties that can be set this way, see the documentation
        of the :class:`aspecd.plotting.MarkerProperties` class.

    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. The examples focus each on a single
    aspect.

    Generally and for obvious reasons, you need to have both, a plot task
    and a plotannotation task. It does not really matter which task you
    define first, the plot or the plot annotation. There are only marginal
    differences, and both ways are shown below.

    .. code-block:: yaml

        - kind: singleplot
          type: SinglePlotter1D
          properties:
            filename: plot1D.pdf
          result: plot1D

        - kind: plotannotation
          type: Marker
          properties:
            parameters:
              positions:
                - [0.5, 0.5]
                - [1.0, 0.5]
              marker: o
            properties:
              edgecolor: green
              size: 12
          plotter: plot1D


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
          type: Marker
          properties:
            parameters:
              positions:
                - [0.5, 0.5]
                - [1.0, 0.5]
              marker: o
            properties:
              edgecolor: green
              size: 12
          result: text

        - kind: singleplot
          type: SinglePlotter1D
          properties:
            filename: plot1D.pdf
          annotations:
            - text


    In this way, you can add the same annotation to several plots,
    and be sure that each annotation is handled as a separate object.

    Suppose you have more than one plotter you want to apply an annotation
    to. In this case, the ``plotter`` property of the plotannotation task is
    a list rather than a string:

    .. code-block:: yaml

        - kind: singleplot
          type: SinglePlotter1D
          result: plot1

        - kind: singleplot
          type: SinglePlotter1D
          result: plot2

        - kind: plotannotation
          type: Marker
          properties:
            parameters:
              positions:
                - [0.5, 0.5]
                - [1.0, 0.5]
              marker: o
          plotter:
            - plot1
            - plot2

    In this case, the annotation will be applied to both plots
    independently. Note that the example has been reduced to the key
    aspects. In a real situation, the two plotters will differ much more.

    .. versionadded:: 0.11


    """

    def __init__(self):
        super().__init__()
        self.parameters["positions"] = []
        self.parameters["xpositions"] = []
        self.parameters["ypositions"] = []
        self.parameters["yoffset"] = 0
        self.parameters["marker"] = ""
        self.properties = aspecd.plotting.MarkerProperties()

    def _perform_task(self):
        if isinstance(self.parameters["xpositions"], np.ndarray):
            self.parameters["xpositions"] = self.parameters[
                "xpositions"
            ].tolist()
        if self.parameters["xpositions"] and (
            self.parameters["ypositions"]
            or self.parameters["ypositions"] == 0
        ):
            xpositions = self.parameters["xpositions"]
            ypositions = self.parameters["ypositions"]
            if np.isscalar(ypositions):
                ypositions = [ypositions] * len(xpositions)
            if len(ypositions) == 1:
                ypositions = ypositions * len(xpositions)
            positions = []
            for idx, xposition in enumerate(xpositions):
                positions.append([xposition, ypositions[idx]])
        else:
            positions = self.parameters["positions"]
        keywords = {
            val: key
            for key, val in matplotlib.markers.MarkerStyle.markers.items()
        }
        if self.parameters["marker"] in keywords.keys():
            marker_symbol = keywords[self.parameters["marker"]]
        else:
            marker_symbol = self.parameters["marker"]
        for position in positions:
            marker = self.plotter.axes.plot(
                position[0],
                position[1] + self.parameters["yoffset"],
                marker=marker_symbol,
                linestyle="",
            )
            self.drawings.append(marker[0])


class FillBetween(PlotAnnotation):
    """
    Coloured surface under a curve or between curves.

    Particularly in signal decomposition, highlighting the individual
    components with coloured surfaces is a common task. But similarly,
    confidence intervals for a fit (between two lines or curves) can be
    marked this way.

    Basically, this class is the ASpecD wrapper to
    :meth:`matplotlib.axes.Axes.fill_between`, although (currently) with some
    restrictions.


    Attributes
    ----------
    parameters : :class:`dict`
        All parameters necessary for the annotation, implicit and explicit

        The following keys exist:

        data : :class:`aspecd.dataset.Dataset` | :class:`list`
            Dataset or list of datasets.

            Datasets used to fill the area below. Strictly speaking, without
            further parameters, the area between the data points and zero is
            filled.

        second : :class:`float` | :class:`aspecd.dataset.Dataset` | :class:`list`
            Scalar, dataset or list (of scalars or datasets).

            Second value used to fill the area between.

            If a scalar, the scalar value is broadcast to the length of the
            *y* values in ``data``.

            If a dataset, the data need to be of same shape as the
            data of the dataset in ``data``.

            If a list, it needs to contain at least as many elements as
            ``data``. Note that you can mix scalars and datasets in the list.

            Default: 0

    properties : :class:`aspecd.plotting.PatchProperties`
        Properties of the marker(s) within a plot

        For the properties that can be set this way, see the documentation
        of the :class:`aspecd.plotting.PatchProperties` class.


    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. The examples focus each on a single
    aspect.

    Generally and for obvious reasons, you need to have both, a plot task
    and a plotannotation task. It does not really matter which task you
    define first, the plot or the plot annotation. There are only marginal
    differences, and both ways are shown below.

    .. code-block:: yaml

        - kind: singleplot
          type: SinglePlotter1D
          properties:
            filename: plot1D.pdf
          result: plot1D

        - kind: plotannotation
          type: FillBetween
          properties:
            parameters:
              data: component
            properties:
              facecolor: green
              alpha: 0.3
          plotter: plot1D

    In this case, the plotter is defined first, and the annotation second.
    To refer to the plotter from within the plotannotation task, you need to
    set the ``result`` attribute in the plotting task and refer to it within
    the ``plotter`` attribute of the plotannotation task. Although defining
    the plotter before the annotation, the user still expects the annotation
    to be included in the file containing the actual plot, despite the fact
    that the figure has been saved (for the first time) before the
    annotation has been added.

    Note that ``component`` refers to a dataset available within your recipe.

    Sometimes, it might be convenient to go the other way round and first
    define an annotation and afterwards add it to a plot(ter). This can be
    done as well:

    .. code-block:: yaml

        - kind: plotannotation
          type: FillBetween
          properties:
            parameters:
              data: component
            properties:
              facecolor: green
              alpha: 0.3
          result: fillbetween

        - kind: singleplot
          type: SinglePlotter1D
          properties:
            filename: plot1D.pdf
          annotations:
            - fillbetween


    In this way, you can add the same annotation to several plots,
    and be sure that each annotation is handled as a separate object.

    Suppose you have more than one plotter you want to apply an annotation
    to. In this case, the ``plotter`` property of the plotannotation task is
    a list rather than a string:

    .. code-block:: yaml

        - kind: singleplot
          type: SinglePlotter1D
          result: plot1

        - kind: singleplot
          type: SinglePlotter1D
          result: plot2

        - kind: plotannotation
          type: FillBetween
          properties:
            parameters:
              data: component
            properties:
              facecolor: green
              alpha: 0.3
          plotter:
            - plot1
            - plot2

    In this case, the annotation will be applied to both plots
    independently. Note that the example has been reduced to the key
    aspects. In a real situation, the two plotters will differ much more.


    .. versionadded:: 0.11


    """

    def __init__(self):
        super().__init__()
        self.parameters["data"] = None
        self.parameters["second"] = 0
        self.properties = aspecd.plotting.PatchProperties()

    def _perform_task(self):
        if isinstance(self.parameters["data"], aspecd.dataset.Dataset):
            datasets = [self.parameters["data"]]
        else:
            datasets = self.parameters["data"]
        if isinstance(self.parameters["second"], aspecd.dataset.Dataset):
            second = self.parameters["second"].data.data
        elif isinstance(self.parameters["second"], list):
            second = []
            for item in self.parameters["second"]:
                try:
                    second.append(item.data.data)
                except AttributeError:
                    second.append(item)
        else:
            second = self.parameters["second"]
        for idx, dataset in enumerate(datasets):
            if isinstance(second, list):
                fill_between = self.plotter.axes.fill_between(
                    dataset.data.axes[0].values,
                    dataset.data.data,
                    second[idx],
                )
            else:
                fill_between = self.plotter.axes.fill_between(
                    dataset.data.axes[0].values,
                    dataset.data.data,
                    second,
                )
            self.drawings.append(fill_between)
