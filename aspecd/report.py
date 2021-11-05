"""General facilities for generating reports.

.. sidebar:: Contents

    .. contents::
        :local:
        :depth: 1

To do scientific research in terms of reproducibility and traceability it's
highly necessary to report all the steps done on a given dataset and never
separate the dataset from its metadata. Similarly, a recipe in context
of recipe-driven data analysis stores a lot of relevant information on what
tasks have been performed on a series of datasets (and even more so the
recipe history). However, having a dataset (or recipe history) containing
all these metadata is only useful if there are easy ways to retrieve and
present the information stored. This is the task of reports. This module
provides functionality to create reports based on templates provided either
by the user or by the package as such.


"Batteries included": Templates contained in the package
========================================================

The "batteries included" approach of Python itself is probably responsible
to a great deal for the success of Python as a language. ASpecD, similarly,
tries to provide you with a sensible set of tools you need for your routine
data analysis in spectroscopy. Reports are no exception to that rule.

Hence, ASpecD comes bundled with a (growing) series of templates allowing
you to create reports of datasets and alike. Thus, getting access to all
information stored in a single dataset is as simple as calling a single
reporter, and in context of recipe-driven data analysis, it is even simpler:

.. code-block:: yaml

    - kind: report
      type: LaTeXReporter
      properties:
        template: dataset.tex
        filename: report.tex
      compile: true

This would create a report of a dataset that is then stored in the file
``report.tex``, using the template ``dataset.tex`` bundled with the ASpecD
package. As you even set ``compile`` to true, it would even compile the
LaTeX report, including all figures generated during cooking the recipe and
referenced from within the report. Hence, you end up in your current
directory with both, a LaTeX file ``report.tex`` and a PDF file ``report.pdf``.

But what if you don't like the way the bundled templates look like? Don't
worry, we've got you covered: Simply provide a relative or absolute path to
your own template, even with the same name. Hence, in the above example,
if you place a file ``dataset.tex`` in the directory you serve the recipe
from, it will be used instead of the bundled one.


Output formats
==============

Template engines provide means of a "separation of concerns" (a term coined
by Edsger W. Dijkstra and highly important not only in software
development): The data source is entirely independent of the formatting of
the report, and one and the same template engine can be used to create
reports in a multitude of output formats.

Currently, the ASpecD framework supports two output formats (more may be
added in the future): plain text (txt) and LaTeX. The respective reporter
classes are:

  * :class:`TxtReporter`
  * :class:`LaTeXReporter`

The bundled templates used with the respective reporters are stored within
the ``templates/report/`` directory of the ASpecD package, and here within
subdirectories (``txt``, ``latex``) for each of the formats. This makes it
easy to add additional formats and to shorten the template paths when using
the reporters.


Background: Jinja2
==================

The report functionality relies heavily on the `Jinja2 template engine
<http://jinja.pocoo.org/>`_ . Therefore, it is very useful to be generally
familiar with the concepts of Jinja2. Basically, this template engine
allows users to specify rather complicated replacements and logic within
the template. However, logic within templates should be used sparingly,
and the template should always be rendered correctly even without
processing it by the template engine. Only then templates are easy to
develop and adapt.

Two concepts used by Jinja2 the user of the report facilities of the ASpecD
framework should be familiar with are "environment" and "context". The
former is a list of settings determining the type of delimiters used within
a certain template for the control structures that are understood by
Jinja2. As Jinja2 is developed with web applications (and hence HTML) in
mind, those delimiters may not be feasible for other types of languages a
template may be written in, such as LaTeX.

Currently, the :mod:`aspecd.report` module of the ASpecD framework provides
a generic environment as well as dedicated Txt and LaTeX environments,
implemented as respective classes:

  * :class:`GenericEnvironment`
  * :class:`TxtEnvironment`
  * :class:`LaTeXEnvironment`

These environments get automatically loaded by the respective reporter
classes:

  * :class:`Reporter`
  * :class:`TxtReporter`
  * :class:`LaTeXReporter`

While the :class:`TxtEnvironment` and :class:`TxtReporter` classes are
basically identical to the :class:`GenericEnvironment` and :class:`Reporter`
classes, respectively, the :class:`LaTeXEnvironment` and
:class:`LaTeXReporter` provide some heavy adaptations to rendering and even
compiling LaTeX templates.

The second important concept of Jinja2 is that of the "context": Think of
it as a dictionary containing all the key--value pairs you can use to
replace placeholders within a template with their actual values. In the
simplest of all cases within the context of the ASpecD framework,
this could be the metadata of an :class:`aspecd.dataset.Dataset`.


Module documentation
====================

"""

import collections
import os
import shutil
import subprocess  # nosec
import tempfile
from datetime import datetime

import jinja2

import aspecd.exceptions
import aspecd.system
import aspecd.utils


class Reporter(aspecd.utils.ToDictMixin):
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
    template : :class:`str`
        Template file used to generate report.

    filename : :class:`str`
        Name of the resulting template file.

    context : :class:`collections.OrderedDict`
        Variables of a template that are replaced with the given content.

        It contains a key "sysinfo" containing system-related
        information, i.e. the information contained in the
        :class:`aspecd.system.SystemInfo` class.

        Furthermore, the key "template_dir" contains the (relative or
        absolute) path to the template provided in :attr:`template`. This is
        particularly useful for including subtemplates.

        A key "timestamp" contains the current timestamp when starting to
        render the report.

    environment : :class:`aspecd.report.GenericEnvironment`
        Jinja2 environment used for rendering the template.

        Defaults to a :obj:`aspecd.report.GenericEnvironment` object with
        settings for rendering generic templates.

    report : :class:`str`
        Actual report, i.e. rendered template

    Parameters
    ----------
    template : :class:`str`
        Path to template file used to generate report.

    filename : :class:`str`
        Path to the output file the report should be rendered to.

    Raises
    ------
    aspecd.report.FileNotFoundError
        Raised if the template file provided does not exist.

    aspecd.report.MissingFilenameError
        Raised if no output file for the report is provided.


    .. versionadded:: 0.6
        New parameter ``label`` to add label to calculated dataset

    """

    def __init__(self, template='', filename=''):
        super().__init__()
        self.template = template
        self.filename = filename
        self.context = collections.OrderedDict()
        self.environment = GenericEnvironment()
        self.report = ''
        self.context['sysinfo'] = \
            aspecd.system.SystemInfo(package=aspecd.utils.package_name(
                self)).to_dict()
        self.__kind__ = 'report'
        self._exclude_from_to_dict = ['context', 'environment', 'report']

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
        if not self.template:
            raise FileNotFoundError('No template provided')
        # noinspection PyTypeChecker
        self.context['template_dir'] = os.path.split(self.template)[0]
        if self.context['template_dir']:
            self.context['template_dir'] += os.path.sep
        self.context['timestamp'] = \
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
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
        try:
            template = self.environment.get_template(self.template)
        except jinja2.exceptions.TemplateError:
            self.template = os.path.realpath(self.template)
            template = self.environment.get_template(self.template)
        self.report = template.render(self.context)

    def save(self):
        """Save report to file.

        Raises
        ------
        aspecd.report.MissingFilenameError
            Raised if no output file for the report is provided.

        """
        if not self.filename:
            raise aspecd.exceptions.MissingFilenameError(
                'No output file for report')
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


class TxtReporter(Reporter):
    """Plain text reporter.

    The most basic format for a report is plain text. Its probably biggest
    advantage is that it is intrinsically platform-independent (except of
    the encoding, but UTF-8 should not pose any problems any more in 2021
    and after).

    The perhaps biggest disadvantage is the lack of standard formatting and
    the overall limited formatting options, not to speak of including figures.

    As such, the plain text reporter can be used for a first overview and
    for maximum portability. For well-formatted reports, have a look at the
    :class:`LaTeXReporter`.

    Attributes
    ----------
    environment : :class:`aspecd.report.TxtEnvironment`
        Jinja2 environment used for rendering the template.

        Similar to the :class:`aspecd.report.GenericEnvironment`, but with
        the package path for template lookup set to the path for txt
        templates within the ASpecD package.


    .. versionadded:: 0.6

    """

    def __init__(self, template='', filename=''):
        super().__init__()
        self.environment = TxtEnvironment()


class LaTeXReporter(Reporter):
    """LaTeX Reporter.

    Often, templates for reports are written in LaTeX, and the results
    typeset as PDF file upon a (pdf)LaTeX run. For convenience, this class
    offers the necessary facilities to compile the template once written.

    The whole procedure may look as follows::

        template = "template.tex"
        filename = "report.tex"
        report_ = aspecd.report.LaTeXReporter(template=template,
                                              filename=filename)
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

    .. important::
        For enhanced security, the temporary directory used for compiling
        the template will be removed after successful compilation.
        Therefore, no traces of your report should remain outside the
        current directory controlled by the user.

    .. note::
        Due to problems with LaTeX rendering text containing underscores,
        the keys in the context dict are recursively parsed and each
        key containing underscores converted to camel case (but preserving
        the case of the first character: "foo_bar" => "fooBar"). Thus,
        the template can be compiled using LaTeX without having to replace
        the placeholder variables beforehand.

    Attributes
    ----------
    environment : :class:`aspecd.report.LaTeXEnvironment`
        Jinja2 environment used for rendering the template.

        Defaults to a :obj:`aspecd.report.LaTeXEnvironment` object with
        settings for rendering LaTeX templates.

    includes : :class:`list`
        List of files that need to be present for compiling the template.

        These files will be copied into the temporary directory used for
        compiling the template.

    latex_executable : :class:`str`
        Name of/path to the LaTeX executable.

        Defaults to "pdflatex"

    Parameters
    ----------
    template : :class:`str`
        Path to template file used to generate report.

    filename : :class:`str`
        Path to the output file the report should be rendered to.

    Raises
    ------
    aspecd.report.LaTeXExecutableNotFoundError
        Raised if the LaTeX executable could not be found

    """

    def __init__(self, template='', filename=''):
        super().__init__(template=template, filename=filename)
        self.environment = LaTeXEnvironment()
        self.includes = list()
        self.latex_executable = 'pdflatex'

        self._temp_dir = tempfile.mkdtemp()
        self._pwd = os.getcwd()
        self._exclude_from_to_dict.extend(['latex_executable'])

    def _render(self):
        """Perform the actual rendering of the template.

        Additionally to the usual tasks performed in the base class,
        for LaTeX templates, each key containing underscores is converted to
        camel case (but preserving the case of the first character:
        "foo_bar" => "fooBar"). Thus, the template can be compiled using
        LaTeX without having to replace the placeholder variables beforehand.

        """
        template = self.environment.get_template(self.template)
        self.context = self._change_keys_in_dict_recursively(self.context)
        self.report = template.render(self.context)

    def _change_keys_in_dict_recursively(self, dict_=None):
        tmp_dict = collections.OrderedDict()
        for key, value in dict_.items():
            if isinstance(value, dict):
                dict_[key] = self._change_keys_in_dict_recursively(value)
            if '_' in key:
                tmp_key = \
                    ''.join([x.capitalize() for x in key.split(sep='_')])
                tmp_key = ''.join([tmp_key[0].lower(), tmp_key[1:]])
            else:
                tmp_key = key
            tmp_dict[tmp_key] = dict_[key]
        return tmp_dict

    def compile(self):
        """Compile LaTeX template.

        The template is copied to a temporary directory and the LaTeX
        executable specified in :attr:`latex_executable` called on the
        report. Afterwards, the result is copied back to the original
        directory.

        Additionally, all files necessary to compile the report are copied
        to the temporary directory as well.

        Raises
        ------
        aspecd.report.LaTeXExecutableNotFoundError
            Raised if the LaTeX executable could not be found

        """
        if not shutil.which(self.latex_executable):
            raise aspecd.exceptions.LaTeXExecutableNotFoundError
        self._copy_files_to_temp_dir()
        self._compile()
        # Note: In order to resolve references in LaTeX, compile twice.
        #       There might be a better option, automatically detecting
        #       whether compiling twice is necessary, but for now...
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
        with aspecd.utils.change_working_dir(self._temp_dir):
            _, filename_wo_path = os.path.split(self.filename)
            # Path stripped, there should be no security implications.
            process = subprocess.run([self.latex_executable,  # nosec
                                      '-output-directory', self._temp_dir,
                                      '-interaction=nonstopmode',
                                      filename_wo_path],
                                     check=False,
                                     capture_output=True)
            print(process.stdout.decode())
            print(process.stderr.decode())

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

    The environment does not change any of the jinja settings except of the
    loaders. Here, a list of loaders using :class:`jinja2.ChoiceLoader` is
    implemented. Using this loader makes it possible to search subsequently
    in different places for a template. Here, the first hit is used,
    therefore, the sequence of loaders is *crucial*.

    Currently, there are two loaders implemented, in exactly this sequence:

    #. :class:`jinja2.FileSystemLoader`

        Looking for templates in the current directory and using an absolute
        path

    #. :class:`jinja2.PackageLoader`

        Looking for templates in the aspecd package in the package path
        "templates/report/", *i.e.* the base directory for all report
        templates of the ASpecD package.

    """

    def __init__(self):
        env = {
            "loader": jinja2.ChoiceLoader([
                jinja2.FileSystemLoader(
                    [
                        os.path.abspath('.'),
                        os.path.abspath('/')
                    ]
                ),
                jinja2.PackageLoader(
                    "aspecd", package_path="templates/report/")
            ])
        }
        super().__init__(**env)


class TxtEnvironment(jinja2.Environment):
    """Jinja2 environment for rendering generic text templates.

    The environment does not change any of the jinja settings except of the
    loaders. Here, a list of loaders using :class:`jinja2.ChoiceLoader` is
    implemented. Using this loader makes it possible to search subsequently
    in different places for a template. Here, the first hit is used,
    therefore, the sequence of loaders is *crucial*.

    Currently, there are two loaders implemented, in exactly this sequence:

    #. :class:`jinja2.FileSystemLoader`

        Looking for templates in the current directory and using an absolute
        path

    #. :class:`jinja2.PackageLoader`

        Looking for templates in the aspecd package in the package path
        "templates/report/txt/", *i.e.* the directory for all bare text report
        templates of the ASpecD package.

    """

    def __init__(self):
        env = {
            "loader": jinja2.ChoiceLoader([
                jinja2.FileSystemLoader(
                    [
                        os.path.abspath('.'),
                        os.path.abspath('/')
                    ]
                ),
                jinja2.PackageLoader(
                    "aspecd", package_path="templates/report/txt/")
            ])
        }
        super().__init__(**env)


class LaTeXEnvironment(jinja2.Environment):
    """Jinja2 environment for rendering LaTeX-based templates.

    This environment is designed for using templates written in LaTeX that
    can be rendered by LaTeX without having their control code replaced by
    Jinja2. While variables are usually output in LaTeX, control structures
    are prefixed by a LaTeX comment character (``%``). For convenience,
    the following table lists all the variables currently set within this
    environment.

    ===================== =====
    Variable              Value
    ===================== =====
    block_start_string    %{
    block_end_string      }%
    variable_start_string {@
    variable_end_string   }
    comment_start_string  %#{
    comment_end_string    }
    line_statement_prefix %%
    line_comment_prefix   %#
    trim_blocks           True
    autoescape            False
    ===================== =====

    While every measure is taken to keep the above information as accurate
    as possible, for authoritative information the reader is referred to
    the actual source code.

    Besides extensively modifying the control codes used within the
    template, the environment implements a list of loaders using
    :class:`jinja2.ChoiceLoader`. Using this loader makes it possible to
    search subsequently in different places for a template. Here, the first
    hit is used, therefore, the sequence of loaders is *crucial*.

    Currently, there are two loaders implemented, in exactly this sequence:

    #. :class:`jinja2.FileSystemLoader`

        Looking for templates in the current directory and using an absolute
        path

    #. :class:`jinja2.PackageLoader`

        Looking for templates in the aspecd package in the package path
        "templates/report/latex/", *i.e.* the directory for all bare text report
        templates of the ASpecD package.


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
            "loader": jinja2.ChoiceLoader([
                jinja2.FileSystemLoader(
                    [
                        os.path.abspath('.'),
                        os.path.abspath('/')
                    ]
                ),
                jinja2.PackageLoader(
                    "aspecd", package_path="templates/report/latex/")
            ])
        }
        super().__init__(**env)
