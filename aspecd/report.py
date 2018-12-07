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
import shutil
import subprocess
import tempfile

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


class LaTeXExecutableNotFoundError(Error):
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

    environment : :class:`aspecd.report.GenericEnvironment`
        Jinja2 environment used for rendering the template.

        Defaults to a :obj:`aspecd.report.GenericEnvironment` object with
        settings for rendering generic templates.

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
        self.environment = GenericEnvironment()
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


class LaTeXReporter(Reporter):
    """LaTeX Reporter.

    Often, templates for reports are written in LaTeX, and the results
    typeset as PDF file upon a (pdf)LaTeX run. For convenience, this class
    offers the necessary facilities to compile the template once written.

    The whole procedure may look as follows::

        template = "template.tex"
        filename = "report.tex"
        report_ = aspecd.report.Reporter(template=template, filename=filename)
        report_.create()
        report_.compile()

    This will result with a file "report.pdf" in the current directory. If
    you specify a relative or absolute path for the filename of the report,
    the resulting PDF file will be copied to that path accordingly.

    Note that for compiling a temporary directory is used, such as not to
    clutter the current working directory with all the auxiliary files
    usually created during a (pdf)LaTeX run. Furthermore, currently, only a
    single (pdf)LaTeX run is performed with option
    "-interaction=nonstopmode" passed in order to not block further execution.

    Attributes
    ----------
    environment : :class:`aspecd.report.LaTeXEnvironment`
        Jinja2 environment used for rendering the template.

        Defaults to a :obj:`aspecd.report.LaTeXEnvironment` object with
        settings for rendering LaTeX templates.

    includes : `list`
        List of files that need to be present for compiling the template.

        These files will be copied into the temporary directory used for
        compiling the template.

    latex_executable : `str`
        Name of/path to the LaTeX executable.

        Defaults to "pdflatex"

    Raises
    ------
    LaTeXExecutableNotFoundError
        Raised if the LaTeX executable could not be found

    """

    def __init__(self):
        super().__init__()
        self.environment = LaTeXEnvironment()
        self.includes = list()
        self.latex_executable = 'pdflatex'

        self._temp_dir = tempfile.mkdtemp()
        self._pwd = os.getcwd()

    def compile(self):
        """Compile LaTeX template.

        The template is copied to a temporary directory and the LaTeX
        executable specified in :attr:`latex_executable` called on the
        report. Afterwards, the result is copied back to the original
        directory.

        Additionally, all files necessary to compile the report are copied
        to the temporary directory as well.

        """
        if not shutil.which(self.latex_executable):
            raise LaTeXExecutableNotFoundError
        self._copy_files_to_temp_dir()
        self._compile()
        self._copy_files_from_temp_dir()
        self._remove_temp_dir()

    def _copy_files_to_temp_dir(self):
        """Copy all necessary files to compile the LaTeX report to temp_dir

        Takes care of relative or absolute paths of both, report and includes.
        """
        _, filename_wo_path = os.path.split(self.filename)
        shutil.copy2(self.filename,
                     os.path.join(self._temp_dir, filename_wo_path))
        for filename in self.includes:
            _, filename_wo_path = os.path.split(filename)
            shutil.copy2(filename,
                         os.path.join(self._temp_dir, filename_wo_path))

    def _compile(self):
        """Actual compiling of the report.

        The compiling takes place in a temporary directory that gets
        removed after the (successful) compile step using the
        :meth:`_remove_temp_dir` method.

        (pdf)LaTeX is currently called with the "-interaction=nonstopmode"
        option in order to not block further execution.
        """
        os.chdir(self._temp_dir)
        _, filename_wo_path = os.path.split(self.filename)
        subprocess.run([self.latex_executable,
                        '-output-directory', self._temp_dir,
                        '-interaction=nonstopmode',
                        filename_wo_path])
        os.chdir(self._pwd)

    def _copy_files_from_temp_dir(self):
        """Copy result of compile step from temporary to target directory

        Takes care of any relative or absolute paths provided for the
        report output file provided in :attr:`filename`.
        """
        basename, _ = os.path.splitext(self.filename)
        path, basename = os.path.split(basename)
        pdf_filename = ".".join([basename, 'pdf'])
        if os.path.isabs(path):
            shutil.copy2(os.path.join(self._temp_dir, pdf_filename),
                         os.path.join(path, pdf_filename))
        else:
            shutil.copy2(os.path.join(self._temp_dir, pdf_filename),
                         os.path.join(self._pwd, path, pdf_filename))

    def _remove_temp_dir(self):
        """Remove temporary directory used for compile step.

        The (pdf)LaTeX step is performed in a temporary directory such as
        not to clutter the current working directory with all the auxiliary
        files usually created during a (pdf)LaTeX run.

        This temporary directory is removed after the (successful) compile
        step. Note that therefore, all sometimes useful information stored,
        e.g., in the log file, is lost. However, manually compiling the
        report is probably the easiest way of figuring out if something
        gets wrong with the (pdf)LaTeX compile step
        """
        shutil.rmtree(self._temp_dir)


class GenericEnvironment(jinja2.Environment):
    """Jinja2 environment for rendering generic templates.

    .. todo::
        Describe the settings in more detail, thus providing users of this
        class and in turn the :class:`aspecd.report.Reporter` class with
        ideas of how to create their templates.

    """

    def __init__(self):
        env = {
            "loader": jinja2.FileSystemLoader(os.path.abspath('.')),
        }
        super().__init__(**env)


class LaTeXEnvironment(jinja2.Environment):
    """Jinja2 environment for rendering LaTeX-based templates.

    .. todo::
        Describe the settings in more detail, thus providing users of this
        class and in turn the :class:`aspecd.report.LaTeXReporter` class with
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
