"""Annotation."""


class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class MissingDatasetError(Error):
    """Exception raised when no dataset exists to act on

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message=''):
        self.message = message


class NoContentError(Error):
    """Exception raised when no content was provided

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message=''):
        self.message = message


class Annotation:
    """
    Annotations are user-supplied additional information to datasets.

    Whereas many processing steps of data can be fully automated, annotations
    are mostly the domain of human interaction, looking at the data of a dataset
    and providing some sort of comments, trying to make sense of the data.

    Annotations can have different types, such as simple "comments", e.g. saying
    that a dataset is not useful as something during measurement went wrong,
    they can highlight "characteristics" of the data, they can point to
    "artifacts". Each of these types is represented by a class on its own that
    is derived from the "Annotation" base class. Additionally, the type is
    reflected in the "type" property that gets set automatically to the class
    name in lower-case letters.

    Each annotation has a scope (such as "point", "slice", "area", "distance",
    "dataset") it belongs to, and a "contents" property (dict) containing the
    actual content of the annotation.
    """

    def __init__(self):
        self.type = ''
        self.scope = ''
        self.content = dict()
        self.dataset = None
        self._settype()

    def annotate(self, dataset=None):
        if not self.content:
            raise NoContentError
        if not dataset:
            if self.dataset:
                self.dataset.annotate(self)
            else:
                raise MissingDatasetError

    def _settype(self):
        self.type = self.__class__.__name__.lower()


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
