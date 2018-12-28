"""
Tasks.

One main aspect of tasks is the constituents of a recipe-driven data
analysis, i.e. :class:`aspecd.tasks.Recipe` and :class:`aspecd.tasks.Chef`.
In its simplest form, a recipe gets cooked by a chef, resulting in a series
of tasks being performed on a list of datasets.

From a user's perspective, a recipe is usually stored in a YAML file. This
allows to easily create and modify recipes without knowing too much about
the underlying processes.
"""

import aspecd.io
import aspecd.utils


class Error(Exception):
    """Base class for exceptions in this module."""

    pass


class MissingRecipeError(Error):
    """Exception raised trying to cook without recipe

    Attributes
    ----------
    message : `str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class MissingFilenameError(Error):
    """Exception raised when expecting a filename but none is provided

    Attributes
    ----------
    message : `str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class Recipe(aspecd.utils.ToDictMixin):
    """
    Recipes get cooked by chefs in recipe-driven data analysis.

    A recipe contains a list of tasks to be performed on a list of
    datasets. From a user's perspective, recipes "live" usually in YAML
    files from where they are read into a :obj:`aspecd.tasks.Recipe` object.
    """

    def __init__(self):
        super().__init__()
        self.datasets = []
        self.tasks = []

    def read_from(self, filename=''):
        """
        Read recipe from YAML file.

        Parameters
        ----------
        filename : `str`
            Name of the YAML file to read from.

        Raises
        ------
        MissingFilenameError
            Raised if no filename is given to read from.

        """
        if not filename:
            raise MissingFilenameError
        yaml = aspecd.io.Yaml()
        yaml.read_from(filename=filename)
        if 'datasets' in yaml.dict:
            self.datasets = yaml.dict['datasets']

    def write_to(self, filename=''):
        """
        Write recipe to YAML file.

        Parameters
        ----------
        filename : `str`
            Name of the YAML file to write to.

        Raises
        ------
        MissingFilenameError
            Raised if no filename is given to write to.

        """
        if not filename:
            raise MissingFilenameError
        yaml = aspecd.io.Yaml()
        yaml.dict = self.to_dict()
        yaml.write_to(filename=filename)


class Chef:
    """
    Chefs cook recipes in recipe-driven data analysis.

    Parameters
    ----------
    recipe : `class:aspecd.tasks.Recipe`
        Recipe to cook, i.e. to carry out

    Raises
    ------
    MissingRecipeError
        Raised if no recipe is available to be cooked

    """

    def __init__(self, recipe=None):
        self.recipe = recipe

    def cook(self, recipe=None):
        """
        Cook recipe, i.e. carry out tasks contained therein.

        Parameters
        ----------
        recipe : `class:aspecd.tasks.Recipe`
            Recipe to cook, i.e. to carry out

        Raises
        ------
        MissingRecipeError
            Raised if no recipe is available to be cooked

        """
        self.recipe = recipe
        if not self.recipe:
            raise MissingRecipeError
