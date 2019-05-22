"""Tests for infofile."""

import os
import unittest

from aspecd import infofile


class TestInfofileParser(unittest.TestCase):

    def setUp(self):
        self.ifile = infofile.Infofile()

    def test_instantiate_class(self):
        pass

    def test_has_parameters_property(self):
        self.assertTrue(hasattr(self.ifile, 'parameters'))

    def test_parameters_is_dict(self):
        self.assertTrue(isinstance(self.ifile.parameters, dict))

    def test_has_filename_property(self):
        self.assertTrue(hasattr(self.ifile, 'filename'))

    def test_constructor_sets_filename(self):
        ifile = infofile.Infofile('test')
        self.assertEqual(ifile.filename, 'test')


class TestInfofileParserParse(unittest.TestCase):

    @staticmethod
    def write_list_to_file(contents, filename):
        with open(filename, 'w') as f:
            for line in contents:
                f.write(line)

    def setUp(self):
        self.ifile = infofile.Infofile('test.info')

    def tearDown(self):
        if os.path.isfile('test.info'):
            os.remove('test.info')

    def test_parse_fails_without_filename(self):
        self.ifile.filename = ''
        with self.assertRaises(FileExistsError):
            self.ifile.parse()

    def test_parse_fails_with_nonexisting_file(self):
        self.ifile.filename = 'nonexisting.info'
        with self.assertRaises(FileNotFoundError):
            self.ifile.parse()

    def test_parse_fails_with_empty_file(self):
        self.write_list_to_file([], self.ifile.filename)
        with self.assertRaises(infofile.InfofileEmptyError):
            self.ifile.parse()

    def test_parse_fails_if_not_infofile(self):
        self.write_list_to_file([' '], self.ifile.filename)
        with self.assertRaises(infofile.InfofileTypeError):
            self.ifile.parse()

    def test_parse_minimal_file(self):
        file_content = [
            'test Info File - v. 0.1.0 (0000-00-00)\n'
            '\n'
            'GENERAL\n'
            'bla: blub\n'
        ]
        self.write_list_to_file(file_content, self.ifile.filename)
        self.ifile.parse()
        self.assertTrue('GENERAL' in self.ifile.parameters)
        self.assertTrue('bla' in self.ifile.parameters['GENERAL'])
        self.assertEqual(self.ifile.parameters['GENERAL']['bla'], 'blub')

    def test_parse_different_minimal_file(self):
        file_content = [
            'test Info File - v. 0.1.0 (0000-00-00)\n'
            '\n'
            'SAMPLE\n'
            'foo: bar\n'
        ]
        self.write_list_to_file(file_content, self.ifile.filename)
        self.ifile.parse()
        self.assertTrue('SAMPLE' in self.ifile.parameters)
        self.assertTrue('foo' in self.ifile.parameters['SAMPLE'])
        self.assertEqual(self.ifile.parameters['SAMPLE']['foo'], 'bar')

    def test_parse_inline_comment(self):
        file_content = [
            'test Info File - v. 0.1.0 (0000-00-00)\n'
            '\n'
            'SAMPLE\n'
            'foo: bar % some comment\n'
        ]
        self.write_list_to_file(file_content, self.ifile.filename)
        self.ifile.parse()
        self.assertEqual(self.ifile.parameters['SAMPLE']['foo'], 'bar')

    def test_parse_escaped_comment_character(self):
        file_content = [
            'test Info File - v. 0.1.0 (0000-00-00)\n'
            '\n'
            'SAMPLE\n'
            'foo: bar \%\n'
        ]
        self.write_list_to_file(file_content, self.ifile.filename)
        self.ifile.parse()
        self.assertEqual(self.ifile.parameters['SAMPLE']['foo'], 'bar %')

    def test_parse_comment_line(self):
        file_content = [
            'test Info File - v. 0.1.0 (0000-00-00)\n'
            '\n'
            '% Some comment line\n'
            'SAMPLE\n'
            'foo: bar\n'
        ]
        self.write_list_to_file(file_content, self.ifile.filename)
        self.ifile.parse()
        self.assertTrue('SAMPLE' in self.ifile.parameters)
        self.assertTrue('foo' in self.ifile.parameters['SAMPLE'])
        self.assertEqual(self.ifile.parameters['SAMPLE']['foo'], 'bar')

    def test_parse_continuation_line(self):
        file_content = [
            'test Info File - v. 0.1.0 (0000-00-00)\n'
            '\n'
            'SAMPLE\n'
            'foo: bar\n'
            ' bla blub'
        ]
        self.write_list_to_file(file_content, self.ifile.filename)
        self.ifile.parse()
        self.assertTrue('SAMPLE' in self.ifile.parameters)
        self.assertTrue('foo' in self.ifile.parameters['SAMPLE'])
        self.assertEqual(self.ifile.parameters['SAMPLE']['foo'],
                         'bar bla blub')

    def test_parse_file_with_comment_block(self):
        file_content = [
            'test Info File - v. 0.1.0 (0000-00-00)\n'
            '\n'
            'GENERAL\n'
            'bla: blub\n'
            '\n'
            'COMMENT\n'
            'And here some comment without colon in line\n'
        ]
        self.write_list_to_file(file_content, self.ifile.filename)
        self.ifile.parse()
        self.assertTrue('COMMENT' in self.ifile.parameters)
        self.assertEqual(self.ifile.parameters['COMMENT'],
                         ['And here some comment without colon in line\n'])

    def test_parse_file_with_empty_comment_block(self):
        file_content = [
            'test Info File - v. 0.1.0 (0000-00-00)\n'
            '\n'
            'GENERAL\n'
            'bla: blub\n'
            '\n'
            'COMMENT'
        ]
        self.write_list_to_file(file_content, self.ifile.filename)
        self.ifile.parse()
        self.assertTrue('COMMENT' in self.ifile.parameters)

    def test_parameters_preserve_order_of_blocks_in_file(self):
        file_content = [
            'test Info File - v. 0.1.0 (0000-00-00)\n'
            '\n'
            'SAMPLE\n'
            'foo: bar\n'
            'bla: blub\n'
            '\n'
            'GENERAL\n'
            'baz: frobnicate\n'
        ]
        self.write_list_to_file(file_content, self.ifile.filename)
        self.ifile.parse()
        self.assertEqual(['SAMPLE', 'GENERAL'],
                         list(self.ifile.parameters.keys()))
        self.assertEqual(['foo', 'bla'],
                         list(self.ifile.parameters['SAMPLE'].keys()))

    def test_parse_reads_version_info(self):
        file_content = [
            'trEPR Info file - v. 0.1.6 (2016-01-18)'
        ]
        self.write_list_to_file(file_content, self.ifile.filename)
        self.ifile.parse()
        self.assertEqual('trEPR Info file', self.ifile.infofile_info['kind'])
        self.assertEqual('0.1.6', self.ifile.infofile_info['version'])
        self.assertEqual('2016-01-18', self.ifile.infofile_info['date'])


class TestInfofileParserNonOOP(unittest.TestCase):

    @staticmethod
    def write_list_to_file(contents, filename):
        with open(filename, 'w') as f:
            for line in contents:
                f.write(line)

    def tearDown(self):
        import os
        if os.path.isfile('test.info'):
            os.remove('test.info')

    def test_parse_fails_without_filename(self):
        with self.assertRaises(FileExistsError):
            infofile.parse()

    def test_parse_fails_with_nonexisting_file(self):
        with self.assertRaises(FileNotFoundError):
            infofile.parse('nonexisting.info')

    def test_parse_fails_with_empty_file(self):
        self.write_list_to_file([], 'test.info')
        with self.assertRaises(infofile.InfofileEmptyError):
            infofile.parse('test.info')

    def test_parse_fails_if_not_infofile(self):
        self.write_list_to_file([' '], 'test.info')
        with self.assertRaises(infofile.InfofileTypeError):
            infofile.parse('test.info')

    def test_parse_minimal_file(self):
        file_content = [
            'test Info File - v. 0.1.0 (0000-00-00)\n'
            '\n'
            'GENERAL\n'
            'bla: blub\n'
        ]
        self.write_list_to_file(file_content, 'test.info')
        parameters = infofile.parse('test.info')
        self.assertTrue('GENERAL' in parameters)
        self.assertTrue('bla' in parameters['GENERAL'])
        self.assertEqual(parameters['GENERAL']['bla'], 'blub')


if __name__ == '__main__':
    unittest.main()
