"""Tests for input and output (IO)."""
import copy
import os
import unittest
import zipfile

import numpy as np

import aspecd.exceptions
import aspecd.processing
from aspecd import io, dataset, tasks, utils, history


class TestDatasetImporter(unittest.TestCase):
    def setUp(self):
        self.importer = io.DatasetImporter()

    def test_instantiate_class(self):
        pass

    def test_instantiate_with_source_sets_source(self):
        source = "filename"
        importer = io.DatasetImporter(source)
        self.assertEqual(importer.source, source)

    def test_has_import_into_method(self):
        self.assertTrue(hasattr(self.importer, "import_into"))
        self.assertTrue(callable(self.importer.import_into))

    def test_import_into_without_dataset_raises(self):
        with self.assertRaises(aspecd.exceptions.MissingDatasetError):
            self.importer.import_into()

    def test_import_into_with_dataset_sets_dataset(self):
        test_dataset = dataset.Dataset()
        self.importer.source = "filename"
        self.importer.import_into(test_dataset)
        self.assertIs(self.importer.dataset, test_dataset)

    def test_import_into_with_dataset_sets_id(self):
        test_dataset = dataset.Dataset()
        self.importer.source = "filename"
        self.importer.import_into(test_dataset)
        self.assertEqual(test_dataset.id, self.importer.source)

    def test_import_into_with_dataset_sets_label(self):
        test_dataset = dataset.Dataset()
        self.importer.source = "filename"
        self.importer.import_into(test_dataset)
        self.assertEqual(test_dataset.label, self.importer.source)

    def test_import_into_sets_label_without_path(self):
        test_dataset = dataset.Dataset()
        self.importer.source = "/path/to/filename.ext"
        self.importer.import_into(test_dataset)
        self.assertEqual(
            test_dataset.label, os.path.split(self.importer.source)[-1]
        )

    def test_import_into_does_not_override_label(self):
        test_dataset = dataset.Dataset()
        test_dataset.label = "foobar"
        self.importer.source = "/path/to/filename.ext"
        self.importer.import_into(test_dataset)
        self.assertEqual("foobar", test_dataset.label)


class TestDatasetExporter(unittest.TestCase):
    def setUp(self):
        self.exporter = io.DatasetExporter()

    def test_instantiate_class(self):
        pass

    def test_has_comment_property(self):
        self.assertTrue(hasattr(self.exporter, "comment"))

    def test_instantiate_with_target_sets_target(self):
        target = "filename"
        exporter = io.DatasetExporter(target=target)
        self.assertEqual(exporter.target, target)

    def test_has_export_from_method(self):
        self.assertTrue(hasattr(self.exporter, "export_from"))
        self.assertTrue(callable(self.exporter.export_from))

    def test_export_from_without_dataset_raises(self):
        with self.assertRaises(aspecd.exceptions.MissingDatasetError):
            self.exporter.export_from()

    def test_export_from_with_dataset_sets_dataset(self):
        test_dataset = dataset.Dataset()
        self.exporter.export_from(test_dataset)
        self.assertIs(self.exporter.dataset, test_dataset)

    def test_has_create_history_record_method(self):
        self.assertTrue(hasattr(self.exporter, "create_history_record"))
        self.assertTrue(callable(self.exporter.create_history_record))

    def test_create_history_record_returns_history_record(self):
        self.exporter.dataset = aspecd.dataset.Dataset()
        history_record = self.exporter.create_history_record()
        self.assertTrue(
            isinstance(
                history_record, aspecd.history.DatasetExporterHistoryRecord
            )
        )


class TestDatasetImporterFactory(unittest.TestCase):
    def setUp(self):
        self.factory = io.DatasetImporterFactory()
        self.source = "/foo"

    def test_instantiate_class(self):
        pass

    def test_get_importer_returns_importer(self):
        importer = self.factory.get_importer(source=self.source)
        self.assertTrue(isinstance(importer, io.DatasetImporter))

    def test_get_importer_sets_source_in_importer(self):
        importer = self.factory.get_importer(source=self.source)
        self.assertEqual(self.source, importer.source)

    def test_get_importer_with_relative_source_sets_absolute_path(self):
        source = "foo"
        root_path = os.path.abspath(os.curdir)
        importer = self.factory.get_importer(source=source)
        self.assertEqual(os.path.join(root_path, source), importer.source)

    def test_get_importer_without_source_raises(self):
        with self.assertRaises(aspecd.exceptions.MissingSourceError):
            self.factory.get_importer()

    def test_get_importer_with_adf_extension_returns_adf_importer(self):
        source = "/foo.adf"
        importer = self.factory.get_importer(source=source)
        self.assertTrue(isinstance(importer, io.AdfImporter))

    def test_get_importer_with_asdf_extension_returns_asdf_importer(self):
        source = "/foo.asdf"
        importer = self.factory.get_importer(source=source)
        self.assertTrue(isinstance(importer, io.AsdfImporter))

    def test_get_importer_with_txt_extension_returns_txt_importer(self):
        source = "/foo.txt"
        importer = self.factory.get_importer(source=source)
        self.assertTrue(isinstance(importer, io.TxtImporter))

    def test_get_importer_with_importer_returns_specific_importer(self):
        source = "/foo"
        importer = "TxtImporter"
        importer = self.factory.get_importer(source=source, importer=importer)
        self.assertTrue(isinstance(importer, io.TxtImporter))

    def test_get_importer_with_parameters_sets_parameters(self):
        source = "/foo"
        parameters = {"foo": "bla", "bar": "blub"}
        importer = self.factory.get_importer(
            source=source, parameters=parameters
        )
        self.assertDictEqual(parameters, importer.parameters)

    def test_returning_abstract_importer_logs_warning(self):
        with self.assertLogs(__package__, level="WARNING") as captured:
            self.factory.get_importer(source=self.source)
        self.assertEqual(len(captured.records), 1)
        self.assertIn("default importer", captured.output[0].lower())


class TestRecipeImporter(unittest.TestCase):
    def setUp(self):
        self.importer = io.RecipeImporter()
        self.source = "filename"

    def test_instantiate_class(self):
        pass

    def test_instantiate_with_source_sets_source(self):
        importer = io.RecipeImporter(source=self.source)
        self.assertEqual(importer.source, self.source)

    def test_has_import_into_method(self):
        self.assertTrue(hasattr(self.importer, "import_into"))
        self.assertTrue(callable(self.importer.import_into))

    def test_import_into_without_recipe_raises(self):
        with self.assertRaises(aspecd.exceptions.MissingRecipeError):
            self.importer.import_into()

    def test_import_into_without_parameter_but_recipe_preset(self):
        recipe = tasks.Recipe()
        self.importer.recipe = recipe
        self.importer.import_into()
        self.assertIs(self.importer.recipe, recipe)

    def test_import_into_with_recipe_sets_recipe(self):
        recipe = tasks.Recipe()
        self.importer.import_into(recipe=recipe)
        self.assertIs(self.importer.recipe, recipe)

    def test_import_into_with_source_sets_filename_in_recipe(self):
        recipe = tasks.Recipe()
        importer = io.RecipeImporter(source=self.source)
        importer.recipe = recipe
        importer.import_into()
        self.assertEqual(importer.recipe.filename, self.source)


class TestRecipeExporter(unittest.TestCase):
    def setUp(self):
        self.exporter = io.RecipeExporter()
        self.target = "filename"

    def test_instantiate_class(self):
        pass

    def test_instantiate_with_target_sets_target(self):
        exporter = io.RecipeExporter(target=self.target)
        self.assertEqual(exporter.target, self.target)

    def test_has_export_from_method(self):
        self.assertTrue(hasattr(self.exporter, "export_from"))
        self.assertTrue(callable(self.exporter.export_from))

    def test_export_from_without_recipe_raises(self):
        with self.assertRaises(aspecd.exceptions.MissingRecipeError):
            self.exporter.export_from()

    def test_export_from_with_recipe_sets_recipe(self):
        recipe = tasks.Recipe()
        self.exporter.export_from(recipe)
        self.assertIs(self.exporter.recipe, recipe)


class TestRecipeYamlImporter(unittest.TestCase):
    def setUp(self):
        self.importer = io.RecipeYamlImporter()
        self.recipe_filename = "filename"
        self.recipe_dict = dict()

    def tearDown(self):
        if os.path.exists(self.recipe_filename):
            os.remove(self.recipe_filename)

    def create_recipe(self):
        self.recipe_dict = {
            "datasets": ["foo"],
            "tasks": [
                {
                    "kind": "singleplot",
                    "type": "SinglePlotter",
                    "properties": {"filename": "foo"},
                }
            ],
        }
        yaml = utils.Yaml()
        yaml.dict = self.recipe_dict
        yaml.write_to(self.recipe_filename)

    def create_recipe_with_numpy_array(self):
        self.recipe_dict = {
            "datasets": ["foo"],
            "tasks": [
                {
                    "kind": "processing",
                    "type": "ScalarAlgebra",
                    "properties": {"value": np.random.random(1)},
                }
            ],
        }
        yaml = utils.Yaml()
        yaml.dict = copy.deepcopy(self.recipe_dict)
        yaml.serialise_numpy_arrays()
        yaml.write_to(self.recipe_filename)

    def create_recipe_from_dict(self):
        yaml = utils.Yaml()
        yaml.dict = self.recipe_dict
        yaml.write_to(self.recipe_filename)

    def test_instantiate_class(self):
        pass

    def test_is_recipe_importer(self):
        self.assertTrue(isinstance(self.importer, io.RecipeImporter))

    def test_import_sets_task_in_recipe(self):
        self.create_recipe()
        self.importer.source = self.recipe_filename
        recipe = tasks.Recipe()
        recipe.import_from(self.importer)
        self.assertTrue(recipe.tasks[0])

    def test_import_with_numpy_array_sets_task_in_recipe(self):
        self.create_recipe_with_numpy_array()
        self.importer.source = self.recipe_filename
        recipe = tasks.Recipe()
        recipe.import_from(self.importer)
        self.assertEqual(
            self.recipe_dict["tasks"][0]["properties"]["value"],
            recipe.tasks[0].properties["value"],
        )

    def test_import_sets_recipe_version(self):
        self.create_recipe()
        self.importer.source = self.recipe_filename
        recipe = tasks.Recipe()
        self.importer.import_into(recipe)
        self.assertTrue(self.importer.recipe_version)

    def test_import_old_version_detects_old_version(self):
        old_keys = [
            "default_package",
            "autosave_plots",
            "output_directory",
            "datasets_source_directory",
        ]
        for key in old_keys:
            with self.subTest(key=key):
                self.recipe_dict = {
                    key: "",
                    "datasets": ["foo"],
                    "tasks": [
                        {
                            "kind": "singleplot",
                            "type": "SinglePlotter",
                            "properties": {"filename": "foo"},
                        }
                    ],
                }
                self.create_recipe_from_dict()
                self.importer.source = self.recipe_filename
                recipe = tasks.Recipe()
                self.importer.import_into(recipe)
                self.assertEqual("0.1", self.importer.recipe_version)

    def test_import_with_explicit_version_sets_recipe_version(self):
        self.recipe_dict = {
            "format": {"version": "0.1"},
            "datasets": ["foo"],
            "tasks": [
                {
                    "kind": "singleplot",
                    "type": "SinglePlotter",
                    "properties": {"filename": "foo"},
                }
            ],
        }
        self.create_recipe_from_dict()
        self.importer.source = self.recipe_filename
        recipe = tasks.Recipe()
        self.importer.import_into(recipe)
        self.assertEqual(
            self.recipe_dict["format"]["version"],
            self.importer.recipe_version,
        )

    def test_import_version_0_1_converts_to_current_version(self):
        self.recipe_dict = {
            "default_package": "aspecd",
            "autosave_plots": False,
            "output_directory": "/bar",
            "datasets_source_directory": "/foobar",
            "datasets": ["foo"],
            "tasks": [
                {
                    "kind": "singleplot",
                    "type": "SinglePlotter",
                    "properties": {"filename": "foo"},
                }
            ],
        }
        self.create_recipe_from_dict()
        self.importer.source = self.recipe_filename
        recipe = tasks.Recipe()
        recipe.import_from(self.importer)
        self.assertEqual(
            self.recipe_dict["default_package"],
            recipe.settings["default_package"],
        )
        self.assertEqual(
            self.recipe_dict["autosave_plots"],
            recipe.settings["autosave_plots"],
        )
        self.assertEqual(
            self.recipe_dict["output_directory"], recipe.directories["output"]
        )
        self.assertEqual(
            self.recipe_dict["datasets_source_directory"],
            recipe.directories["datasets_source"],
        )


class TestRecipeYamlExporter(unittest.TestCase):
    def setUp(self):
        self.exporter = io.RecipeYamlExporter()
        self.recipe_filename = "filename"

    def tearDown(self):
        if os.path.exists(self.recipe_filename):
            os.remove(self.recipe_filename)

    def test_instantiate_class(self):
        pass

    def test_is_recipe_exporter(self):
        self.assertTrue(isinstance(self.exporter, io.RecipeExporter))

    def test_export_can_be_reimported(self):
        recipe_dict = {
            "datasets": ["foo"],
            "tasks": [
                {
                    "kind": "singleplot",
                    "type": "SinglePlotter",
                    "properties": {"filename": "foo"},
                }
            ],
        }
        recipe = tasks.Recipe()
        recipe.from_dict(recipe_dict)
        self.exporter.target = self.recipe_filename
        recipe.export_to(self.exporter)
        new_recipe = tasks.Recipe()
        importer = io.RecipeYamlImporter(source=self.recipe_filename)
        new_recipe.import_from(importer)
        self.assertTrue(new_recipe.to_dict())

    def test_export_with_numpy_array_can_be_reimported(self):
        recipe_dict = {
            "datasets": ["foo"],
            "tasks": [
                {
                    "kind": "processing",
                    "type": "ScalarAlgebra",
                    "properties": {"value": np.random.random(1)},
                }
            ],
        }
        recipe = tasks.Recipe()
        recipe.from_dict(recipe_dict)
        self.exporter.target = self.recipe_filename
        recipe.export_to(self.exporter)
        new_recipe = tasks.Recipe()
        importer = io.RecipeYamlImporter(source=self.recipe_filename)
        new_recipe.import_from(importer)
        self.assertTrue(new_recipe.to_dict())

    def test_export_with_small_numpy_array_converts_array_to_list(self):
        recipe_dict = {
            "datasets": ["foo"],
            "tasks": [
                {
                    "kind": "processing",
                    "type": "ScalarAlgebra",
                    "properties": {"value": np.random.random(1)},
                }
            ],
        }
        recipe = tasks.Recipe()
        recipe.from_dict(recipe_dict)
        self.exporter.target = self.recipe_filename
        recipe.export_to(self.exporter)
        yaml = utils.Yaml()
        yaml.read_from(self.recipe_filename)
        self.assertIsInstance(
            yaml.dict["tasks"][0]["properties"]["value"], list
        )


class TestAdfExporter(unittest.TestCase):
    def setUp(self):
        self.exporter = io.AdfExporter()
        self.dataset = dataset.Dataset()
        self.target = "target"
        self.extension = ".adf"

    def tearDown(self):
        if os.path.exists(self.target + self.extension):
            os.remove(self.target + self.extension)

    def test_instantiate_class(self):
        pass

    def test_export_from_without_target_raises(self):
        with self.assertRaises(aspecd.exceptions.MissingTargetError):
            self.exporter.export_from(dataset=self.dataset)

    def test_export_with_target_creates_file(self):
        self.exporter.target = self.target
        self.exporter.export_from(self.dataset)
        self.assertTrue(os.path.exists(self.target + self.extension))

    def test_export_creates_zip_file(self):
        self.exporter.target = self.target
        self.exporter.export_from(self.dataset)
        self.assertTrue(zipfile.is_zipfile(self.target + self.extension))

    def test_created_zipfile_contains_correct_files(self):
        self.exporter.target = self.target
        self.exporter.export_from(self.dataset)
        expected_list_of_files = [
            "dataset.yaml",
            "VERSION",
            "README",
            "binaryData/",
        ]
        expected_list_of_files.sort()
        with zipfile.ZipFile(
            self.target + self.extension, "r"
        ) as zipped_file:
            actual_list_of_files = zipped_file.namelist()
        actual_list_of_files.sort()
        self.assertListEqual(expected_list_of_files, actual_list_of_files)

    def test_export_with_large_array_adds_binary_files(self):
        self.exporter.target = self.target
        self.dataset.data.data = np.random.random(1001)
        self.exporter.export_from(self.dataset)
        with zipfile.ZipFile(
            self.target + self.extension, "r"
        ) as zipped_file:
            list_of_files = zipped_file.namelist()
        binary_files = [
            x for x in list_of_files if x.startswith("binaryData")
        ]
        self.assertEqual(3, len(binary_files))

    def test_export_sets_version(self):
        self.exporter.target = self.target
        self.exporter.export_from(self.dataset)
        with zipfile.ZipFile(
            self.target + self.extension, "r"
        ) as zipped_file:
            version = zipped_file.read("VERSION")
        self.assertEqual(self.exporter._version, version.decode("ascii"))

    def test_export_writes_readme(self):
        self.exporter.target = self.target
        self.exporter.export_from(self.dataset)
        with zipfile.ZipFile(
            self.target + self.extension, "r"
        ) as zipped_file:
            readme = zipped_file.read("README")
        self.assertTrue(readme)


class TestAdfImporter(unittest.TestCase):
    def setUp(self):
        self.importer = io.AdfImporter()
        self.dataset = dataset.ExperimentalDataset()
        self.source = "target"
        self.extension = ".adf"
        self.exporter = io.AdfExporter()
        self.exporter.target = self.source

    def tearDown(self):
        if os.path.exists(self.source + self.extension):
            os.remove(self.source + self.extension)

    def test_instantiate_class(self):
        pass

    def test_import_sets_data_and_origdata(self):
        dataset_ = dataset.Dataset()
        dataset_.data.data = np.asarray([1.0])
        dataset_._origdata.data = np.asarray([1.0])
        dataset_.export_to(self.exporter)

        self.importer.source = self.source
        self.dataset.import_from(self.importer)
        self.assertEqual(dataset_.data.data, self.dataset.data.data)
        self.assertEqual(dataset_._origdata.data, self.dataset._origdata.data)

    def test_import_sets_metadata(self):
        dataset_ = dataset.ExperimentalDataset()
        dataset_.metadata.sample.name = "foo"
        dataset_.export_to(self.exporter)
        self.importer.source = self.source
        self.dataset.import_from(self.importer)
        self.assertEqual(
            dataset_.metadata.sample.name, self.dataset.metadata.sample.name
        )

    def test_import_sets_history(self):
        dataset_ = dataset.ExperimentalDataset()
        processing_step = aspecd.processing.SingleProcessingStep()
        processing_step.comment = "foo"
        dataset_.process(processing_step)
        dataset_.export_to(self.exporter)
        self.importer.source = self.source
        self.dataset.import_from(self.importer)
        self.assertDictEqual(
            dataset_.history[0].to_dict(), self.dataset.history[0].to_dict()
        )

    def test_import_with_large_array(self):
        dataset_ = dataset.Dataset()
        dataset_.data.data = np.random.random(1001)
        dataset_.export_to(self.exporter)

        self.importer.source = self.source
        self.dataset.import_from(self.importer)
        np.testing.assert_allclose(dataset_.data.data, self.dataset.data.data)


class TestAsdfExporter(unittest.TestCase):
    def setUp(self):
        self.exporter = io.AsdfExporter()
        self.dataset = dataset.Dataset()
        self.target = "target"
        self.extension = ".asdf"

    def tearDown(self):
        if os.path.exists(self.target + self.extension):
            os.remove(self.target + self.extension)

    def test_instantiate_class(self):
        pass

    def test_export_from_without_target_raises(self):
        with self.assertRaises(aspecd.exceptions.MissingTargetError):
            self.exporter.export_from(dataset=self.dataset)

    def test_export_with_target_creates_file(self):
        self.exporter.target = self.target
        self.exporter.export_from(self.dataset)
        self.assertTrue(os.path.exists(self.target + self.extension))


class TestAsdfImporter(unittest.TestCase):
    def setUp(self):
        self.importer = io.AsdfImporter()
        self.dataset = dataset.ExperimentalDataset()
        self.source = "target"
        self.extension = ".asdf"
        self.exporter = io.AsdfExporter()
        self.exporter.target = self.source

    def tearDown(self):
        if os.path.exists(self.source + self.extension):
            os.remove(self.source + self.extension)

    def test_instantiate_class(self):
        pass

    def test_import_sets_data_and_origdata(self):
        dataset_ = dataset.Dataset()
        dataset_.data.data = np.asarray([1.0])
        dataset_._origdata.data = np.asarray([1.0])
        dataset_.export_to(self.exporter)

        self.importer.source = self.source
        self.dataset.import_from(self.importer)
        self.assertEqual(dataset_.data.data, self.dataset.data.data)
        self.assertEqual(dataset_._origdata.data, self.dataset._origdata.data)

    def test_import_sets_metadata(self):
        dataset_ = dataset.ExperimentalDataset()
        dataset_.metadata.sample.name = "foo"
        dataset_.export_to(self.exporter)
        self.importer.source = self.source
        self.dataset.import_from(self.importer)
        self.assertEqual(
            dataset_.metadata.sample.name, self.dataset.metadata.sample.name
        )

    def test_import_sets_history(self):
        dataset_ = dataset.ExperimentalDataset()
        processing_step = aspecd.processing.SingleProcessingStep()
        processing_step.comment = "foo"
        dataset_.process(processing_step)
        dataset_.export_to(self.exporter)
        self.importer.source = self.source
        self.dataset.import_from(self.importer)
        self.assertDictEqual(
            dataset_.history[0].to_dict(), self.dataset.history[0].to_dict()
        )


class TestTxtImporter(unittest.TestCase):
    def setUp(self):
        self.importer = io.TxtImporter()
        self.dataset = dataset.ExperimentalDataset()
        self.source = "target.txt"

    def tearDown(self):
        if os.path.exists(self.source):
            os.remove(self.source)

    def test_instantiate_class(self):
        pass

    def test_import_sets_data_and_origdata(self):
        data = np.random.random(5)
        np.savetxt(self.source, data)

        self.importer.source = self.source
        self.dataset.import_from(self.importer)
        self.assertListEqual(list(data), list(self.dataset.data.data))
        self.assertListEqual(list(data), list(self.dataset._origdata.data))

    def test_import_two_column_data_sets_data_and_axis(self):
        data = np.random.random([5, 2])
        np.savetxt(self.source, data)

        self.importer.source = self.source
        self.dataset.import_from(self.importer)
        self.assertListEqual(list(data[:, 1]), list(self.dataset.data.data))
        self.assertListEqual(
            list(data[:, 1]), list(self.dataset._origdata.data)
        )
        self.assertListEqual(
            list(data[:, 0]), list(self.dataset.data.axes[0].values)
        )
        self.assertListEqual(
            list(data[:, 0]), list(self.dataset._origdata.axes[0].values)
        )

    def test_import_with_skiprows(self):
        data = np.random.random([5, 1])
        np.savetxt(self.source, data)

        skiprows = 2
        self.importer.source = self.source
        self.importer.parameters["skiprows"] = skiprows
        self.dataset.import_from(self.importer)
        self.assertEqual(len(data) - skiprows, len(self.dataset.data.data))

    def test_import_with_delimiter(self):
        with open(self.source, "w+") as file:
            file.write("1;5;1\n2;6;2\n3;7;3\n4;8;4\n5;9;5\n")

        self.importer.source = self.source
        self.importer.parameters["delimiter"] = ";"
        self.dataset.import_from(self.importer)
        self.assertEqual((5, 3), self.dataset.data.data.shape)

    def test_import_with_comments(self):
        with open(self.source, "w+") as file:
            file.write("% Lorem ipsum\n1 5 1\n2 6 2\n3 7 3\n4 8 4\n5 9 5\n")

        self.importer.source = self.source
        self.importer.parameters["comments"] = "%"
        self.dataset.import_from(self.importer)
        self.assertEqual((5, 3), self.dataset.data.data.shape)

    def test_import_with_separator(self):
        with open(self.source, "w+") as file:
            file.write("1,1\n2,2\n3,3\n4,4\n5,5\n")

        self.importer.source = self.source
        self.importer.parameters["separator"] = ","
        self.dataset.import_from(self.importer)
        self.assertEqual((5,), self.dataset.data.data.shape)


class TestTxtExporter(unittest.TestCase):
    def setUp(self):
        self.exporter = io.TxtExporter()
        self.dataset = dataset.ExperimentalDataset()
        self.target = "target.txt"

    def tearDown(self):
        if os.path.exists(self.target):
            os.remove(self.target)

    def test_instantiate_class(self):
        pass

    def test_export_from_without_target_raises(self):
        with self.assertRaises(aspecd.exceptions.MissingTargetError):
            self.exporter.export_from(dataset=self.dataset)

    def test_export_with_target_creates_file(self):
        self.exporter.target = self.target
        self.exporter.export_from(self.dataset)
        self.assertTrue(os.path.exists(self.target))

    def test_export_creates_file_with_correct_extension(self):
        self.exporter.target = os.path.splitext(self.target)[0]
        self.exporter.export_from(self.dataset)
        self.assertTrue(os.path.exists(self.target))

    def test_export_with_1D_dataset_adds_axis_as_first_column(self):
        self.dataset.data.data = np.linspace(3, 4, 11)
        self.exporter.target = self.target
        self.exporter.export_from(self.dataset)
        with open(self.target, "r") as file:
            first_line = file.readline()
        self.assertTrue(first_line.startswith("0."))
        self.assertIn("3.", first_line)

    def test_export_with_3D_dataset_raises(self):
        self.dataset.data.data = np.random.random([3, 3, 3])
        self.exporter.target = self.target
        with self.assertRaises(ValueError):
            self.exporter.export_from(self.dataset)

    def test_export_with_2D_dataset_adds_axes_as_first_column_row(self):
        self.dataset.data.data = np.random.random([3, 4])
        self.exporter.target = self.target
        self.exporter.export_from(self.dataset)
        with open(self.target, "r") as file:
            first_line = file.readline()
            second_line = file.readline()
            third_line = file.readline()
        self.assertTrue(first_line.startswith("0."))
        self.assertIn("3.", first_line)
        self.assertTrue(second_line.startswith("0."))
        self.assertTrue(third_line.startswith("1."))
