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

The simplest form of an annotation is a comment applying to an entire
dataset, such as comments stored in the metadata written during data
acquisition. Hence, those comments do *not* belong to the metadata part of
a dataset, but to the annotations in form of a

* :obj:`aspecd.annotation.Comment`

object.

Other frequent types of annotations are artefacts and characteristics,
for which dedicated classes are available within the ASpecD framework, are:

* :class:`aspecd.annotation.Artefact`
* :class:`aspecd.annotation.Characteristic`.

For other types of annotations, simply subclass the
:class:`aspecd.annotation.DatasetAnnotation` base class.


.. _:sec:annotation:plot:

Plot(ter) annotations
=====================

Similar to datasets, plots, *i.e.* graphical representations of the data of
one or multiple datasets, can be annotated as well. Plot annotations will
always result in a graphical object of some kind added to the plot created
by a :class:`aspecd.plotting.Plotter`. Additionally, each plotter has a list
of annotations attached to it.

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


Module documentation
====================

"""

import aspecd.exceptions
import aspecd.history
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
        self._scope = ''
        # List of allowed scopes
        self._allowed_scopes = ['dataset', 'slice', 'point', 'area',
                                'distance']
        # Default scope if none is set explicitly
        self._default_scope = self._allowed_scopes[0]
        self._exclude_from_to_dict = ['dataset', 'type']
        self.__kind__ = 'annotation'

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
                "Allowed scopes are: " + ' '.join(self._allowed_scopes))
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
            annotation=self, package=self.dataset.package_name)
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
        self.content['comment'] = ''

    @property
    def comment(self):
        """
        Get comment of annotation.

        Returns
        -------
        comment : :class:`str`
            Actual comment string

        """
        return self.content['comment']

    @comment.setter
    def comment(self, comment=''):
        self.content['comment'] = comment


class Artefact(DatasetAnnotation):
    """Mark something as an artefact."""

    def __init__(self):
        super().__init__()
        self.content['comment'] = ''


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


    .. versionadded:: 0.9

    """

    def __init__(self):
        super().__init__()
        self.plotter = None
        self.type = self.__class__.__name__.lower()
        self.parameters = {}
        self.properties = None
        self.drawings = []
        self._exclude_from_to_dict = ['plotter', 'type', 'drawings']

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

    def _perform_task(self):
        line = self.plotter.ax.axvline(x=self.parameters['positions'][0])
        self.drawings.append(line)
