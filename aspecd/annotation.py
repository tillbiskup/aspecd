"""
Annotations of data, e.g. characteristics, that cannot be automated.

Annotations of data are eventually something that cannot be automated.
Nevertheless, they can be quite important for the analysis and hence for
providing new scientific insight.

The simplest form of an annotation is a comment applying to an entire
dataset, such as comments stored in the metadata written during data
acquisition. Hence, those comments do *not* belong to the metadata part of
a dataset, but to the annotations in form of a
:obj:`aspecd.annotation.Comment` object.

Other frequent types of annotations are artefacts and characteristics,
for which dedicated classes are available within the ASpecD framework:
:class:`aspecd.annotations.Artefact` and
:class:`aspecd.annotations.Characteristic`. For other types of annotations,
simply subclass the :class:`aspecd.annotations.Annotation` base class.

"""

import aspecd.exceptions
import aspecd.history


class Annotation:
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
    its own that is derived from the "Annotation" base class. Additionally,
    the type is reflected in the "type" property that gets set automatically to
    the class name in lower-case letters.

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
        self.type = self.__class__.__name__.lower()
        self.content = dict()
        self.dataset = None
        # Scope of the annotation; see list of allowed scopes below
        self._scope = ''
        # List of allowed scopes
        self._allowed_scopes = ['dataset', 'slice', 'point', 'area',
                                'distance']
        # Default scope if none is set explicitly
        self._default_scope = self._allowed_scopes[0]

    @property
    def scope(self):
        """
        Get or set the scope the annotation applies to.

        The list of allowed scopes is stored in the private property
        `_allowed_scopes`, and if no scope is set when the annotation is
        finally applied to a dataset, a default scope will be used that is
        stored in the private property `_default_scope` (and is defined as
        one element of the list of allowed scopes)

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
        the Annotation object, the process method of the dataset will be
        called and thus the history written.

        If no dataset is provided at method call nor as property in the
        object, the method will raise a respective exception.

        If no scope is set in the :obj:`aspecd.annotation.Annotation`
        object, a default value will be used that can be set in derived
        classes in the private property `_default_scope`. A full list of
        scopes is contained in the private property `_allowed_scopes`

        The Dataset object always calls this method with the respective
        dataset as argument. Therefore, in this case setting the dataset
        property within the Annotation object is not necessary.

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
        :meth:`aspecd.dataset.annotate` method of the
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


class Comment(Annotation):
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


class Artefact(Annotation):
    """Mark something as an artefact."""

    def __init__(self):
        super().__init__()
        self.content['comment'] = ''


class Characteristic(Annotation):
    """Base class for characteristics."""
