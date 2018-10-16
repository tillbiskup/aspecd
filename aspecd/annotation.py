"""Annotation."""


class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class MissingDatasetError(Error):
    """Exception raised when no dataset exists to act on

    Attributes
    ----------
    message : `str`
        explanation of the error
    """

    def __init__(self, message=''):
        self.message = message


class NoContentError(Error):
    """Exception raised when no content was provided

    Attributes
    ----------
    message : `str`
        explanation of the error
    """

    def __init__(self, message=''):
        self.message = message


class UnknownScopeError(Error):
    """Exception raised when unknown scope was tried to set

    Attributes
    ----------
    message : `str`
        explanation of the error
    """

    def __init__(self, message=''):
        self.message = message


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
    point to "artifacts". Each of these types is represented by a class on
    its own that is derived from the "Annotation" base class. Additionally,
    the type is reflected in the "type" property that gets set automatically to
    the class name in lower-case letters.

    Each annotation has a scope (such as "point", "slice", "area", "distance",
    "dataset") it belongs to, and a "contents" property (dict) containing the
    actual content of the annotation.

    Attributes
    ----------
    type : `str`
        Textual description of the type of annotation: lowercase class name
    content : `dict`
        Actual content of the annotation
    dataset : :obj:`aspecd.dataset.Dataset`
        Dataset the annotation belongs to

    Raises
    ------
    NoContentError
        Raised when annotation contains no content(s)
    MissingDatasetError
        Raised when no dataset exists to act on
    """

    def __init__(self):
        # Type is used as easy identifier: lower-case version of class name
        self.type = self.__class__.__name__.lower()
        # Generic place for more information, therefore dictionary
        self.content = dict()
        # Reference to dataset the annotation is for
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
            raise UnknownScopeError("Allowed scopes are: " +
                                    ' '.join(self._allowed_scopes))
        self._scope = scope

    def annotate(self, dataset=None):
        """
        Annotate a dataset with the given annotation.

        If no dataset is provided at method call, but is set as property in the
        Annotation object, the process method of the dataset will be called and
        thus the history written.

        If no dataset is provided at method call nor as property in the object,
        the method will raise a respective exception.

        If no scope is set in the :obj:`aspecd.annotation.Annotation`
        object, a default value will be used that can be set in derived
        classes in the private property `_default_scope`. A full list of
        scopes is contained in the private property `_allowed_scopes`

        The Dataset object always calls this method with the respective dataset
        as argument. Therefore, in this case setting the dataset property
        within the Annotation object is not necessary.
        """
        if not self.content:
            raise NoContentError
        if not self.scope:
            self._scope = self._default_scope
        if not dataset:
            if self.dataset:
                self.dataset.annotate(self)
            else:
                raise MissingDatasetError


class Comment(Annotation):
    """
    Comments are the most basic form of annotation: a simple textual comment.
    """

    def __init__(self):
        super().__init__()
        self.content['comment'] = ''

    @property
    def comment(self):
        return self.content['comment']

    @comment.setter
    def comment(self, comment=''):
        self.content['comment'] = comment


class Artefact(Annotation):

    def __init__(self):
        super().__init__()
        self.content['comment'] = ''


class Characteristic(Annotation):
    pass
