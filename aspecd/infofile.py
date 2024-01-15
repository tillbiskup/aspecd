"""
Handle Infofile files containing metadata for (experimental) data.

The Infofile format is a special format dedicated to storing metadata
accompanying experimental data. Further information on the format
including the full specification can be found in the following publication:

  * Bernd Paulus, Till Biskup: Towards more reproducible and FAIRer
    research data: documenting provenance during data acquisition using the
    Infofile format.
    *Digital Discovery* **2**:234–244, 2023,
    doi:`10.1039/D2DD00131D <https://doi.org/10.1039/D2DD00131D>`_

For actual Infofile example files, see the git repository available at GitHub:

  * https://github.com/tillbiskup/infofile

Development of the templates for specific methods will always be closely
connected to the respective data model, *e.g.* in context of the `trepr
<https://docs.trepr.de/>`_ and `cwepr <https://docs.cwepr.de/>`_ Python
packages.

This module reads and parses files complying with the infofile file
format. At the same time, it contains the **reference implementation of
the parser for the Infofile format**.

.. note::
    For own purposes, you may prefer using YAML files to store metadata
    that are collected in parallel to recording data over the infofile
    format. For more information on this format and it specification,
    consult its webpage: `<https://yaml.org/>`_.

    However, you may still be interested in the discussion of the Infofile
    format and its advantages and disadvantages compared to formats such
    as YAML and JSON. For this, you are kindly referred to the reference
    given above, describing and discussing the Infofile format in more detail.

    As the lead developer of the ASpecD framework originally invented the
    infofile format for own purposes, there are quite some datasets floating
    around in his lab using this format for the corresponding metadata.
    Hence the need of a module handling this particular file type.

To map the information contained in the info file to datasets, have a look
at the :class:`aspecd.metadata.MetadataMapper` class. You can define rather
elaborate mapping tables, allowing to rename keys as well as to combine
items of a dictionary.
"""

import collections
import os
import string

import aspecd.exceptions


class Infofile:
    """Reading metadata contained in info files.

    Attributes
    ----------
    parameters : :class:`collections.OrderedDict`
        Structure containing parameters read from info file.
    filename : :class:`str`
        Name of the info file read
    infofile_info : :class:`dict`
        Information about the infofile, such as kind, version, and date.

        Helpful for mapping metadata contained in an infofile to datasets.

    Parameters
    ----------
    filename : :class:`str`
        Name of the info file to read

    Raises
    ------
    aspecd.exceptions.InfofileEmptyError
        Raised if info file is empty
    aspecd.exceptions.InfofileTypeError
        Raised if file provided is no info file


    .. versionchanged:: 0.6.3
        Comment gets converted into a single string.

    """

    def __init__(self, filename=None):
        self.parameters = collections.OrderedDict()
        self.filename = filename
        self.infofile_info = {}

        self.infofile_info["kind"] = ""
        self.infofile_info["version"] = ""
        self.infofile_info["date"] = ""

        self._file_contents = []
        self._comment_char = "%"
        self._escape_char = "\\"

    def parse(self):
        """Parse info file.

        Raises
        ------
        aspecd.exceptions.InfofileEmptyError
            Raised if info file is empty
        aspecd.exceptions.InfofileTypeError
            Raised if file provided is no info file

        """
        self._file_contents = self._read()

        if not self._file_contents:
            raise aspecd.exceptions.InfofileEmptyError

        if not self._is_infofile():
            raise aspecd.exceptions.InfofileTypeError

        self._parse_infofile_info()
        self._parse_infofile_body()

    def _parse_infofile_body(self):  # noqa: MC0001
        blockname = ""
        key = ""
        value = ""
        tmp_block = collections.OrderedDict()

        # Start with second line of file, omitting format and version info
        for line in self._file_contents[1:]:
            if self._is_comment_block(blockname):
                if blockname not in self.parameters:
                    self.parameters[blockname] = line.rstrip()
                else:
                    self.parameters[blockname] = " ".join(
                        [self.parameters[blockname], line.rstrip()]
                    )
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
                    blockname = ""
                    tmp_block = collections.OrderedDict()
                continue
            if not blockname:
                blockname = line.strip()
                continue
            [key, value] = [i.strip() for i in line.split(":", maxsplit=1)]
            tmp_block[key] = value
        # In case last block has not been assigned
        # (file didn't end with COMMENT block or empty line)
        if blockname:
            if not self._is_comment_block(blockname):
                self.parameters[blockname] = tmp_block
            # noinspection PyUnboundLocalVariable
            # pylint: disable=undefined-loop-variable
            if self._is_comment_block(blockname) and self._is_comment_block(
                line
            ):
                self.parameters[blockname] = ""

    def _is_infofile(self):
        return "info file" in self._file_contents[0].lower()

    def _read(self):
        if not self.filename:
            raise FileExistsError
        if not os.path.exists(self.filename):
            raise FileNotFoundError
        with open(self.filename, encoding="utf8") as file:
            file_contents = list(file)
        return file_contents

    def _parse_infofile_info(self):
        info_line = self._file_contents[0]
        info_parts = info_line.split(" - ")
        _, version, version_date = info_parts[1].split()
        self.infofile_info["kind"] = info_parts[0].strip()
        self.infofile_info["version"] = version
        self.infofile_info["date"] = version_date[1:-1]

    def _is_comment_line(self, line):
        return line.strip().startswith(self._comment_char)

    def _remove_inline_comment(self, line):
        # Get all occurrences (positions) of COMMENTCHAR in line
        occur = [i for i, j in enumerate(line) if j == self._comment_char]
        # Remove those occurrences prepended with ESCAPE character
        occur = [i for i in occur if line[i - 1] != self._escape_char]
        # If there is an inline comment, remove it from line
        if occur:
            line = line[: occur[0]]
        # Replace escaped comment char with comment char
        return line.replace(
            "".join([self._escape_char, self._comment_char]),
            self._comment_char,
        )

    @staticmethod
    def _is_continuation_line(line):
        return line[0] in string.whitespace and line.strip()

    @staticmethod
    def _is_comment_block(blockname):
        return blockname.lower() == "comment"


def parse(filename=""):
    """Parse info file.

    Conventional interface provided for convenience that gives easy access
    to the metadata stored in an infofile. For full use of the capabilities
    of the :class:`Infofile` class, use its object-oriented interface.

    .. warning::
        This will only return the metadata read from the info file, not the
        version information that is read and parsed as well. To obtain this
        version information, e.g., for mapping of metadata onto other
        structures, you should use the object-oriented interface of the
        :class:`Infofile` class.

    Parameters
    ----------
    filename : :class:`str`
        Name of the info file to parse

    Returns
    -------
    metadata : :class:`dict`
        Dictionary with metadata read from info file

    """
    ifile = Infofile(filename)
    ifile.parse()
    return ifile.parameters
