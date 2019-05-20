"""Tests for reports."""

import collections
import os
import shutil
import unittest

from aspecd import report


class TestReporter(unittest.TestCase):
    def setUp(self):
        self.report = report.Reporter()
        self.template = 'test_template.tex'
        self.template2 = os.path.abspath('test_template.tex')
        self.filename = 'test_report.tex'

    def tearDown(self):
        if os.path.exists(self.template):
            os.remove(self.template)
        if os.path.exists(self.template2):
            os.remove(self.template2)
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def test_instantiate_class(self):
        pass

    def test_has_template_property(self):
        self.assertTrue(hasattr(self.report, 'template'))

    def test_has_filename_property(self):
        self.assertTrue(hasattr(self.report, 'filename'))

    def test_has_context_property(self):
        self.assertTrue(hasattr(self.report, 'context'))

    def test_context_is_ordered_dict(self):
        self.assertTrue(isinstance(self.report.context,
                                   collections.OrderedDict))

    def test_context_has_sysinfo_key(self):
        self.assertIn('sysinfo', self.report.context)

    def test_context_has_sysinfo_packages_key(self):
        self.assertIn('packages', self.report.context['sysinfo'])

    def test_has_environment_property(self):
        self.assertTrue(hasattr(self.report, 'environment'))

    def test_environment_is_jinja_environment(self):
        self.assertTrue(isinstance(self.report.environment,
                                   report.GenericEnvironment))

    def test_has_report_property(self):
        self.assertTrue(hasattr(self.report, 'report'))

    def test_has_render_method(self):
        self.assertTrue(hasattr(self.report, 'render'))
        self.assertTrue(callable(self.report.render))

    def test_render_without_template_raises(self):
        with self.assertRaises(FileNotFoundError):
            self.report.render()

    def test_render_with_nonexistent_template_raises(self):
        self.report.template = 'foo.bar'
        with self.assertRaises(FileNotFoundError):
            self.report.render()

    def test_render_with_template(self):
        with open(self.template, 'w+') as f:
            f.write('')
        self.report.template = self.template
        self.report.render()

    def test_render_with_template_with_absolute_path(self):
        with open(self.template2, 'w+') as f:
            f.write('')
        self.report.template = self.template2
        self.report.render()

    def test_render_with_template_provided_at_initialisation(self):
        with open(self.template, 'w+') as f:
            f.write('')
        report_ = report.Reporter(template=self.template)
        report_.render()

    def test_render_fills_report_property(self):
        content = 'bla'
        with open(self.template, 'w+') as f:
            f.write(content)
        report_ = report.Reporter(template=self.template)
        report_.render()
        self.assertEqual(content, report_.report)

    def test_has_save_method(self):
        self.assertTrue(hasattr(self.report, 'save'))
        self.assertTrue(callable(self.report.save))

    def test_save_without_filename_raises(self):
        with self.assertRaises(report.MissingFilenameError):
            self.report.save()

    def test_save_with_filename(self):
        self.report.filename = self.filename
        self.report.save()

    def test_save_with_filename_provided_at_initialisation(self):
        report_ = report.Reporter(filename=self.filename)
        report_.save()

    def test_save_writes_file(self):
        self.report.filename = self.filename
        self.report.save()
        self.assertTrue(os.path.exists(self.filename))

    def test_save_writes_file_with_correct_content(self):
        content = 'bla'
        with open(self.template, 'w+') as f:
            f.write(content)
        self.report.template = self.template
        self.report.filename = self.filename
        self.report.render()
        self.report.save()
        with open(self.filename) as f:
            read_content = f.read()
        self.assertEqual(content, read_content)

    def test_has_create_method(self):
        self.assertTrue(hasattr(self.report, 'create'))
        self.assertTrue(callable(self.report.create))

    def test_create_without_template_raises(self):
        with self.assertRaises(FileNotFoundError):
            self.report.create()

    def test_create_without_filename_raises(self):
        with open(self.template, 'w+') as f:
            f.write('')
        self.report.template = self.template
        with self.assertRaises(report.MissingFilenameError):
            self.report.create()

    def test_render_replaces_variable_from_context_dict(self):
        template_content = '{{bar}}'
        with open(self.template, 'w+') as f:
            f.write(template_content)
        self.report.template = self.template
        self.report.filename = self.filename
        self.report.context = {'bar': 'foo'}
        self.report.create()
        with open(self.filename) as f:
            read_content = f.read()
        self.assertEqual(self.report.context['bar'], read_content)


class TestLaTeXEnvironment(unittest.TestCase):
    def setUp(self):
        self.env = report.LaTeXEnvironment()

    def test_instantiate_class(self):
        pass


class TestLaTeXReporter(unittest.TestCase):
    def setUp(self):
        self.report = report.LaTeXReporter()
        self.template = 'test_template.tex'
        self.template2 = os.path.abspath('test_template.tex')
        self.filename = 'test_report.tex'
        self.result = 'test_report.pdf'
        self.include = 'include.tex'
        self.subdir = 'testdir'
        self.report.template = self.template
        self.report.filename = self.filename

    def tearDown(self):
        if os.path.exists(self.template):
            os.remove(self.template)
        if os.path.exists(self.template2):
            os.remove(self.template2)
        if os.path.exists(self.filename):
            os.remove(self.filename)
        if os.path.exists(self.result):
            os.remove(self.result)
        if os.path.exists(self.include):
            os.remove(self.include)
        if os.path.exists(self.subdir):
            shutil.rmtree(self.subdir)

    def test_instantiate_class(self):
        pass

    def test_instantiate_with_template_sets_template(self):
        report_ = report.LaTeXReporter(template=self.template)
        self.assertEqual(self.template, report_.template)

    def test_instantiate_with_filename_sets_filename(self):
        report_ = report.LaTeXReporter(filename=self.filename)
        self.assertEqual(self.filename, report_.filename)

    def test_environment_is_latex_environment(self):
        self.assertTrue(isinstance(self.report.environment,
                                   report.LaTeXEnvironment))

    def test_has_includes_property(self):
        self.assertTrue(hasattr(self.report, 'includes'))

    def test_has_compile_method(self):
        self.assertTrue(hasattr(self.report, 'compile'))
        self.assertTrue(callable(self.report.compile))

    def test_has_latex_executable_property(self):
        self.assertTrue(hasattr(self.report, 'latex_executable'))

    def test_render_with_template_with_absolute_path(self):
        with open(self.template2, 'w+') as f:
            f.write('')
        self.report.template = self.template2
        self.report.render()

    def test_compile_with_inexisting_latex_executable_raises(self):
        self.report.latex_executable = 'foo'
        with self.assertRaises(report.LaTeXExecutableNotFoundError):
            self.report.compile()

    def test_compile_creates_output(self):
        template_content = '\\documentclass{article}' \
                            '\\begin{document}' \
                            'test' \
                            '\\end{document}'
        with open(self.template, 'w+') as f:
            f.write(template_content)
        self.report.render()
        self.report.save()
        self.report.compile()
        self.assertTrue(os.path.exists(self.result))

    def test_compile_does_not_leave_temp_files(self):
        template_content = '\\documentclass{article}' \
                            '\\begin{document}' \
                            'test' \
                            '\\end{document}'
        with open(self.template, 'w+') as f:
            f.write(template_content)
        self.report.render()
        self.report.save()
        self.report.compile()
        basename, _ = os.path.splitext(self.result)
        logfile = ".".join([basename, 'log'])
        self.assertFalse(os.path.exists(logfile))

    def test_compile_with_includes_creates_output(self):
        include_name, _ = os.path.splitext(self.include)
        template_content = '\\documentclass{article}' \
                           '\\begin{document}' \
                           '\\include{' + include_name + '}' \
                           '\\end{document}'
        with open(self.template, 'w+') as f:
            f.write(template_content)
        include_content = 'foobar'
        with open(self.include, 'w+') as f:
            f.write(include_content)
        self.report.includes.append(self.include)
        self.report.render()
        self.report.save()
        self.report.compile()
        self.assertTrue(os.path.exists(self.result))

    def test_compile_with_includes_and_path_creates_output(self):
        os.mkdir(self.subdir)
        include_name, _ = os.path.splitext(self.include)
        template_content = '\\documentclass{article}' \
                           '\\begin{document}' \
                           '\\include{' + include_name + '}' \
                           '\\end{document}'
        with open(self.template, 'w+') as f:
            f.write(template_content)
        include_content = 'foobar'
        with open(os.path.join(self.subdir, self.include), 'w+') as f:
            f.write(include_content)
        self.report.includes.append(os.path.join(self.subdir, self.include))
        self.report.filename = os.path.join(self.subdir, self.filename)
        self.report.render()
        self.report.save()
        self.report.compile()
        self.assertTrue(os.path.exists(os.path.join(self.subdir, self.result)))

    def test_compile_with_absolute_path_for_report_creates_output(self):
        template_content = '\\documentclass{article}' \
                            '\\begin{document}' \
                            'test' \
                            '\\end{document}'
        with open(self.template, 'w+') as f:
            f.write(template_content)
        self.report.filename = os.path.join(os.getcwd(), self.filename)
        self.report.render()
        self.report.save()
        self.report.compile()
        self.assertTrue(os.path.exists(self.result))

    def test_render_replaces_underscore_with_camel_case_in_context_dict(self):
        template_content = '\\documentclass{article}' \
                            '\\begin{document}' \
                            'test' \
                            '\\end{document}'
        with open(self.template, 'w+') as f:
            f.write(template_content)
        self.report.context = {'bla_blub': 'foo'}
        self.report.render()
        self.assertTrue('blaBlub' in self.report.context)
