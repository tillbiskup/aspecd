"""General facilities for generating reports.

To do scientific research in terms of reproducibility and traceability it's
highly necessary to report all the steps done on a given dataset and never
separate the dataset from its metadata. However, having a dataset containing
all these metadata is only useful if there are easy ways to retrieve and
present the information stored. This is the task of reports.

This module provides functionality to create reports based on templates
provided either by the user or by the package as such.

"""

import collections
import os

import jinja2


class Error(Exception):
    """Base class for exceptions in this module."""

    pass


class MissingFilenameError(Error):
    """Exception raised when no filename is provided

    Attributes
    ----------
    message : `str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class Reporter:
    """Base class for reports.

    To generate a report from a template, you will need a template in the
    first place. The path to the template (including its filename) is set in
    the :attr:`template` attribute that is either provided as parameter at
    initialisation or assigned later on. Similarly, you should specify an
    output filename, stored in the :attr:`filename` attribute. The variables
    known to the template that should be replaced by appropriate content,
    termed "context" in Jinja2 language, are stored in the :attr:`context`
    attribute. This is, by default, an ordered dict to preserve the order of
    the keys it contains. This is sometimes very useful.

    Next, you want to render the template, and most often, save it to a file
    afterwards. If you would like to separate those steps, you can call the
    :meth:`render` and :meth:`save` methods separately. For convenience,
    simply call :meth:`create` to render the report and save it to the file
    whose name you have provided.

    The whole procedure may look as follows::

        template = "/path/to/my/template.tex"
        filename = "/path/to/my/final/report.tex"
        report_ = aspecd.report.Reporter(template=template, filename=filename)
        report_.create()


    Attributes
    ----------
    template : `str`
        Template file used to generate report.

    filename : `str`
        Name of the resulting template file.

    context : :class:`collections.OrderedDict`
        Variables of a template that are replaced with the given content.

    environment : :class:`aspecd.report.LaTeXEnvironment`
        Jinja2 environment used for rendering the template.

        Defaults to a :obj:`aspecd.report.LaTeXEnvironment` object with
        settings for rendering LaTeX-based templates.

    Parameters
    ----------
    template : `str`
        Path to template file used to generate report.

    Raises
    ------
    FileNotFoundError
        Raised if the template file provided does not exist.

    MissingFilenameError
        Raised if no output file for the report is provided.

    """

    def __init__(self, template='', filename=''):
        self.template = template
        self.filename = filename
        self.context = collections.OrderedDict()
        self.environment = LaTeXEnvironment()
        self.report = ''

    def render(self):
        """Render the template.

        The actual rendering of the template should be implemented within the
        non-public method :meth:`_render`.

        Before calling the non-public method :meth:`_render`,
        the renderer checks the existence of the file provided as attribute
        :attr:`template` as well as whether an output filename has been
        provided. If this is not the case, a corresponding exception will be
        raised.

        Raises
        ------
        FileNotFoundError
            Raised if the template file provided does not exist.

        """
        if not self.template or not os.path.exists(self.template):
            message = ' '.join(['Cannot find template file', self.template])
            raise FileNotFoundError(message)
        self._render()

    def _render(self):
        """Perform the actual rendering of the template.

        The implementation of the actual rendering goes in here in all
        classes inheriting from Report. This method is automatically
        called by :meth:`render` after some background checks.

        By default, the Jinja2 environment set in the :attr:`environment`
        attribute is used together with the template provided in the
        :attr:`template` attribute and the context provided in the
        :attr:`context` attribute. The result of the rendering is stored in
        the :attr:`report` attribute.

        If you need to change anything here, simply override this method in
        a child class according to your needs.
        """
        template = self.environment.get_template(self.template)
        self.report = template.render(self.context)

    def save(self):
        """Save report to file.

        Raises
        ------
        MissingFilenameError
            Raised if no output file for the report is provided.

        """
        if not self.filename:
            raise MissingFilenameError('No output file for report')
        with open(self.filename, mode='w+') as output_file:
            output_file.write(self.report)

    def create(self):
        """Create report, thus rendering template and saving result to file.

        Convenience method to render the template and save the generated
        report to a file, thus simply calling :meth:`render` and
        :meth:`save` subsequently.

        """
        self.render()
        self.save()


class LaTeXEnvironment(jinja2.Environment):
    """Jinja2 environment for rendering LaTeX-based templates.

    .. todo::
        Describe the settings in more detail, thus providing users of this
        class and in turn the :class:`aspecd.report.Reporter` class with
        ideas of how to create their templates.

    """

    def __init__(self):
        env = {
            "block_start_string": '%{',
            "block_end_string": '}%',
            "variable_start_string": '{@',
            "variable_end_string": '}',
            "comment_start_string": '%#{',
            "comment_end_string": '}',
            "line_statement_prefix": '%%',
            "line_comment_prefix": '%#',
            "trim_blocks": True,
            "autoescape": False,
            "loader": jinja2.FileSystemLoader(os.path.abspath('.')),
        }
        super().__init__(**env)
