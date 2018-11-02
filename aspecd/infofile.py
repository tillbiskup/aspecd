"""
Handle infofile files containing meta data for (experimental) data.

The infofile format is a special format dedicated to storing meta data
accompanying experimental data. Further information can be found online:

http://till-biskup.de/en/software/info/format

This module reads and parses files complying with the infofile file format.

Further plans are to include functionality to map the information contained
in the info file to datasets.
"""

import collections
import string


class Error(Exception):
    """Base class for exceptions in this module."""

    pass


class InfofileTypeError(Error):
    """Exception raised for wrong file format.

    Attributes
    ----------
    message : `str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class InfofileEmptyError(Error):
    """Exception raised for empty file.

    Attributes
    ----------
    message : `str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class Infofile:
    """Reading metadata contained in info files.

    Attributes
    ----------
    parameters : `collections.OrderedDict`
        Structure containing parameters read from info file.
    filename : `str`
        Name of the info file read

    Parameters
    ----------
    filename : `str`
        Name of the info file to read

    Raises
    ------
    InfofileEmptyError
        Raised if info file is empty
    InfofileTypeError
        Raised if file provided is no info file

    """

    def __init__(self, filename=None):
        self.parameters = collections.OrderedDict()
        self.filename = filename

        self._file_contents = []
        self._comment_char = '%'
        self._escape_char = '\\'

    def parse(self):
        """Parse info file.

        Raises
        ------
        InfofileEmptyError
            Raised if info file is empty
        InfofileTypeError
            Raised if file provided is no info file

        """
        self._file_contents = self._read()

        if not self._file_contents:
            raise InfofileEmptyError

        if not self._is_infofile():
            raise InfofileTypeError

        blockname = ''
        key = ''
        value = ''
        tmp_block = collections.OrderedDict()

        for line in self._file_contents[1:]:
            if self._is_comment_block(blockname):
                if blockname not in self.parameters:
                    self.parameters[blockname] = []
                self.parameters[blockname].append(line)
                continue
            if self._is_comment_line(line):
                continue
            line = self._remove_inline_comment(line)
            if self._is_continuation_line(line):
                if key:
                    tmp_block[key] = " ".join([value, line.strip()])
                continue
            line = line.strip()
            if not line:
                if blockname:
                    self.parameters[blockname] = tmp_block
                    blockname = ''
                    tmp_block = {}
                continue
            if not blockname:
                blockname = line.strip()
                continue
            [key, value] = [i.strip() for i in line.split(':', maxsplit=1)]
            tmp_block[key] = value

        # In case last block has not been assigned
        # (file didn't end with COMMENT block or empty line)
        if blockname and not self._is_comment_block(blockname):
            self.parameters[blockname] = tmp_block

    def _is_infofile(self):
        return 'info file' in self._file_contents[0].lower()

    def _read(self):
        import os
        if not self.filename:
            raise FileExistsError
        if not os.path.exists(self.filename):
            raise FileNotFoundError
        with open(self.filename) as file:
            file_contents = list(file)
        return file_contents

    def _is_comment_line(self, line):
        return line.strip().startswith(self._comment_char)

    def _remove_inline_comment(self, line):
        # Get all occurrences (positions) of COMMENTCHAR in line
        occur = [i for i, j in enumerate(line) if j == self._comment_char]
        # Remove those occurrences prepended with ESCAPE character
        occur = [i for i in occur if line[i - 1] != self._escape_char]
        # If there is an inline comment, remove it from line
        if occur:
            line = line[:occur[0]]
        # Replace escaped comment char with comment char
        return line.replace("".join([self._escape_char, self._comment_char]),
                            self._comment_char)

    @staticmethod
    def _is_continuation_line(line):
        return line[0] in string.whitespace and line.strip()

    @staticmethod
    def _is_comment_block(blockname):
        return blockname.lower() == 'comment'


def parse(filename=''):
    """Parse info file.

    Parameters
    ----------
    filename : `str`
        Name of the info file to parse

    """
    ifile = Infofile(filename)
    ifile.parse()
    return ifile.parameters
