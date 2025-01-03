import unittest
from unittest.mock import patch, MagicMock
import json
from model.recipe import Recipe

class TestRecipe(unittest.TestCase):
    @patch("zipfile.ZipFile")  # Patcher für zipfile.ZipFile
    def test_create_recipe1(self, mock_zipfile):
        mock_data = json.dumps({"name": "mock_mod:mock_item1",
                                "type":"minecraft:crafting_shapeless",
                                "ingredients": [{"tag": "mock_mod:mock_item2"}, {"tag": "mock_mod:mock_item2"}],
                                "result": {"count": 3}}).encode("utf-8")

        mock_archive = MagicMock()
        mock_archive.read.return_value = mock_data
        mock_zipfile.return_value = mock_archive

        result = Recipe.create_recipe("mock_mod:mock_item1")

        self.assertIsNotNone(result)
        mock_zipfile.assert_called_once_with("./data/recipes/mock_mod.zip")
        mock_archive.read.assert_called_once_with("mock_item1.json")

    @patch("zipfile.ZipFile")  # Patcher für zipfile.ZipFile
    def test_create_recipe2(self, mock_zipfile):
        mock_data = json.dumps({"name": "mock_mod:mock_item2",
                                 "type": "minecraft:crafting_shapeless",
                                 "ingredients": [{"item": "mock_mod:mock_item3"}, {"item": "mock_mod:mock_item3"}],
                                 "result": {"count": 10}}).encode("utf-8")

        mock_archive = MagicMock()
        mock_archive.read.return_value = mock_data
        mock_zipfile.return_value = mock_archive

        result = Recipe.create_recipe("mock_mod:mock_item2")

        self.assertIsNotNone(result)
        mock_zipfile.assert_called_once_with("./data/recipes/mock_mod.zip")
        mock_archive.read.assert_called_once_with("mock_item2.json")

    @patch("zipfile.ZipFile")  # Patcher für zipfile.ZipFile
    def test_create_recipe3(self, mock_zipfile):
        mock_data = json.dumps({"name": "mock_mod:mock_item3",
                                 "type": "minecraft:crafting_shaped",
                                 "pattern": ["XXX", "XOX", "XXX"],
                                 "key": {"X":{"tag": "mock_mod:mock_item4"}, "O":{"tag": "mock_mod:mock_item1"}},
                                 "result": {"count": 2}}).encode("utf-8")

        mock_archive = MagicMock()
        mock_archive.read.return_value = mock_data
        mock_zipfile.return_value = mock_archive

        result = Recipe.create_recipe("mock_mod:mock_item3")

        self.assertIsNotNone(result)
        mock_zipfile.assert_called_once_with("./data/recipes/mock_mod.zip")
        mock_archive.read.assert_called_once_with("mock_item3.json")

    @patch("zipfile.ZipFile")  # Patcher für zipfile.ZipFile
    def test_create_recipe4(self, mock_zipfile):
        mock_data = json.dumps({"name": "mock_mod:mock_item4",
                                 "type": "minecraft:crafting_shaped",
                                 "group": "mock_mod:mock_group",
                                 "pattern": [" X ", "XOX", " O "],
                                 "key": {"X": {"item": "mock_mod:mock_item6"}, "O": {"item": "mock_mod:mock_item5"}},
                                 "result": {}}).encode("utf-8")

        mock_archive = MagicMock()
        mock_archive.read.return_value = mock_data
        mock_zipfile.return_value = mock_archive

        result = Recipe.create_recipe("mock_mod:mock_item4")

        self.assertIsNotNone(result)
        mock_zipfile.assert_called_once_with("./data/recipes/mock_mod.zip")
        mock_archive.read.assert_called_once_with("mock_item4.json")
        self.assertEqual(result.pattern, ["", "mock_mod:mock_item6", "", "mock_mod:mock_item6", "mock_mod:mock_item5", "mock_mod:mock_item6", "", "mock_mod:mock_item5", ""])