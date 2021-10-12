"""Tests for exceptions."""

import unittest

import aspecd.exceptions


class TestMissingParameterError(unittest.TestCase):

    def setUp(self):
        self.exception = aspecd.exceptions.MissingParameterError

    def test_prints_message(self):
        with self.assertRaisesRegex(self.exception, 'bla'):
            raise self.exception('bla')


class TestMissingPlotterError(unittest.TestCase):

    def setUp(self):
        self.exception = aspecd.exceptions.MissingPlotterError

    def test_prints_message(self):
        with self.assertRaisesRegex(self.exception, 'bla'):
            raise self.exception('bla')


class TestMissingDatasetError(unittest.TestCase):

    def setUp(self):
        self.exception = aspecd.exceptions.MissingDatasetError

    def test_prints_message(self):
        with self.assertRaisesRegex(self.exception, 'bla'):
            raise self.exception('bla')


class TestMissingSaverError(unittest.TestCase):

    def setUp(self):
        self.exception = aspecd.exceptions.MissingSaverError

    def test_prints_message(self):
        with self.assertRaisesRegex(self.exception, 'bla'):
            raise self.exception('bla')


class TestMissingFilenameError(unittest.TestCase):

    def setUp(self):
        self.exception = aspecd.exceptions.MissingFilenameError

    def test_prints_message(self):
        with self.assertRaisesRegex(self.exception, 'bla'):
            raise self.exception('bla')


class TestMissingPlotError(unittest.TestCase):

    def setUp(self):
        self.exception = aspecd.exceptions.MissingPlotError

    def test_prints_message(self):
        with self.assertRaisesRegex(self.exception, 'bla'):
            raise self.exception('bla')


class TestMissingFigureError(unittest.TestCase):

    def setUp(self):
        self.exception = aspecd.exceptions.MissingFigureError

    def test_prints_message(self):
        with self.assertRaisesRegex(self.exception, 'bla'):
            raise self.exception('bla')


class TestMissingAxisError(unittest.TestCase):

    def setUp(self):
        self.exception = aspecd.exceptions.MissingAxisError

    def test_prints_message(self):
        with self.assertRaisesRegex(self.exception, 'bla'):
            raise self.exception('bla')


class TestMissingLegendError(unittest.TestCase):

    def setUp(self):
        self.exception = aspecd.exceptions.MissingLegendError

    def test_prints_message(self):
        with self.assertRaisesRegex(self.exception, 'bla'):
            raise self.exception('bla')


class TestMissingDrawingError(unittest.TestCase):

    def setUp(self):
        self.exception = aspecd.exceptions.MissingDrawingError

    def test_prints_message(self):
        with self.assertRaisesRegex(self.exception, 'bla'):
            raise self.exception('bla')


class TestMissingTargetError(unittest.TestCase):

    def setUp(self):
        self.exception = aspecd.exceptions.MissingTargetError

    def test_prints_message(self):
        with self.assertRaisesRegex(self.exception, 'bla'):
            raise self.exception('bla')


class TestMissingRecipeError(unittest.TestCase):

    def setUp(self):
        self.exception = aspecd.exceptions.MissingRecipeError

    def test_prints_message(self):
        with self.assertRaisesRegex(self.exception, 'bla'):
            raise self.exception('bla')


class TestMissingSourceError(unittest.TestCase):

    def setUp(self):
        self.exception = aspecd.exceptions.MissingSourceError

    def test_prints_message(self):
        with self.assertRaisesRegex(self.exception, 'bla'):
            raise self.exception('bla')


class TestMissingProcessingStepError(unittest.TestCase):

    def setUp(self):
        self.exception = aspecd.exceptions.MissingProcessingStepError

    def test_prints_message(self):
        with self.assertRaisesRegex(self.exception, 'bla'):
            raise self.exception('bla')


class TestUndoWithEmptyHistoryError(unittest.TestCase):

    def setUp(self):
        self.exception = aspecd.exceptions.UndoWithEmptyHistoryError

    def test_prints_message(self):
        with self.assertRaisesRegex(self.exception, 'bla'):
            raise self.exception('bla')


class TestUndoAtBeginningOfHistoryError(unittest.TestCase):

    def setUp(self):
        self.exception = aspecd.exceptions.UndoAtBeginningOfHistoryError

    def test_prints_message(self):
        with self.assertRaisesRegex(self.exception, 'bla'):
            raise self.exception('bla')


class TestUndoStepUndoableError(unittest.TestCase):

    def setUp(self):
        self.exception = aspecd.exceptions.UndoStepUndoableError

    def test_prints_message(self):
        with self.assertRaisesRegex(self.exception, 'bla'):
            raise self.exception('bla')


class TestRedoAlreadyAtLatestChangeError(unittest.TestCase):

    def setUp(self):
        self.exception = aspecd.exceptions.RedoAlreadyAtLatestChangeError

    def test_prints_message(self):
        with self.assertRaisesRegex(self.exception, 'bla'):
            raise self.exception('bla')


class TestProcessingWithLeadingHistoryError(unittest.TestCase):

    def setUp(self):
        self.exception = aspecd.exceptions.ProcessingWithLeadingHistoryError

    def test_prints_message(self):
        with self.assertRaisesRegex(self.exception, 'bla'):
            raise self.exception('bla')


class TestMissingImporterFactoryError(unittest.TestCase):

    def setUp(self):
        self.exception = aspecd.exceptions.MissingImporterFactoryError

    def test_prints_message(self):
        with self.assertRaisesRegex(self.exception, 'bla'):
            raise self.exception('bla')


class TestAxesCountError(unittest.TestCase):

    def setUp(self):
        self.exception = aspecd.exceptions.AxesCountError

    def test_prints_message(self):
        with self.assertRaisesRegex(self.exception, 'bla'):
            raise self.exception('bla')


class TestAxesValuesInconsistentWithDataError(unittest.TestCase):

    def setUp(self):
        self.exception = aspecd.exceptions.AxesValuesInconsistentWithDataError

    def test_prints_message(self):
        with self.assertRaisesRegex(self.exception, 'bla'):
            raise self.exception('bla')


class TestMissingImporterError(unittest.TestCase):

    def setUp(self):
        self.exception = aspecd.exceptions.MissingImporterError

    def test_prints_message(self):
        with self.assertRaisesRegex(self.exception, 'bla'):
            raise self.exception('bla')


class TestMissingExporterError(unittest.TestCase):

    def setUp(self):
        self.exception = aspecd.exceptions.MissingExporterError

    def test_prints_message(self):
        with self.assertRaisesRegex(self.exception, 'bla'):
            raise self.exception('bla')


class TestNoContentError(unittest.TestCase):

    def setUp(self):
        self.exception = aspecd.exceptions.NoContentError

    def test_prints_message(self):
        with self.assertRaisesRegex(self.exception, 'bla'):
            raise self.exception('bla')


class TestUnknownScopeError(unittest.TestCase):

    def setUp(self):
        self.exception = aspecd.exceptions.UnknownScopeError

    def test_prints_message(self):
        with self.assertRaisesRegex(self.exception, 'bla'):
            raise self.exception('bla')


class TestMissingAnnotationError(unittest.TestCase):

    def setUp(self):
        self.exception = aspecd.exceptions.MissingAnnotationError

    def test_prints_message(self):
        with self.assertRaisesRegex(self.exception, 'bla'):
            raise self.exception('bla')


class TestInfofileTypeError(unittest.TestCase):

    def setUp(self):
        self.exception = aspecd.exceptions.InfofileTypeError

    def test_prints_message(self):
        with self.assertRaisesRegex(self.exception, 'bla'):
            raise self.exception('bla')


class TestInfofileEmptyError(unittest.TestCase):

    def setUp(self):
        self.exception = aspecd.exceptions.InfofileEmptyError

    def test_prints_message(self):
        with self.assertRaisesRegex(self.exception, 'bla'):
            raise self.exception('bla')


class TestNotApplicableToDatasetError(unittest.TestCase):

    def setUp(self):
        self.exception = aspecd.exceptions.NotApplicableToDatasetError

    def test_prints_message(self):
        with self.assertRaisesRegex(self.exception, 'bla'):
            raise self.exception('bla')


class TestStyleNotFoundError(unittest.TestCase):

    def setUp(self):
        self.exception = aspecd.exceptions.StyleNotFoundError

    def test_prints_message(self):
        with self.assertRaisesRegex(self.exception, 'bla'):
            raise self.exception('bla')


class TestLaTeXExecutableNotFoundError(unittest.TestCase):

    def setUp(self):
        self.exception = aspecd.exceptions.LaTeXExecutableNotFoundError

    def test_prints_message(self):
        with self.assertRaisesRegex(self.exception, 'bla'):
            raise self.exception('bla')


class TestMissingDictError(unittest.TestCase):

    def setUp(self):
        self.exception = aspecd.exceptions.MissingDictError

    def test_prints_message(self):
        with self.assertRaisesRegex(self.exception, 'bla'):
            raise self.exception('bla')


class TestMissingDatasetFactoryError(unittest.TestCase):

    def setUp(self):
        self.exception = aspecd.exceptions.MissingDatasetFactoryError

    def test_prints_message(self):
        with self.assertRaisesRegex(self.exception, 'bla'):
            raise self.exception('bla')


class TestMissingTaskFactoryError(unittest.TestCase):

    def setUp(self):
        self.exception = aspecd.exceptions.MissingTaskFactoryError

    def test_prints_message(self):
        with self.assertRaisesRegex(self.exception, 'bla'):
            raise self.exception('bla')


class TestMissingTaskDescriptionError(unittest.TestCase):

    def setUp(self):
        self.exception = aspecd.exceptions.MissingTaskDescriptionError

    def test_prints_message(self):
        with self.assertRaisesRegex(self.exception, 'bla'):
            raise self.exception('bla')


class TestMissingDatasetIdentifierError(unittest.TestCase):

    def setUp(self):
        self.exception = aspecd.exceptions.MissingDatasetIdentifierError

    def test_prints_message(self):
        with self.assertRaisesRegex(self.exception, 'bla'):
            raise self.exception('bla')
