import unittest
from unittest.mock import patch, MagicMock
import json
from model.item import Item


class TestRecipe(unittest.TestCase):
    @patch("zipfile.ZipFile")  # Patcher für zipfile.ZipFile
    def test_get_group1(self, mock_zipfile):
        mock_data = json.dumps({"name": "mock_mod:mock_item1",
                                "type":"minecraft:crafting_shapeless",
                                "ingredients": [{"tag": "mock_mod:mock_item2"}, {"tag": "mock_mod:mock_item2"}],
                                "result": {"count": 3}}).encode("utf-8")
        mock_archive = MagicMock()
        mock_archive.read.return_value = mock_data
        mock_zipfile.return_value = mock_archive

        item = Item("mock_mod:mock_item1")
        item.get_group()

        self.assertIsNotNone(item)
        self.assertEqual(item.name, "mock_mod:mock_item1")

        mock_zipfile.assert_called_once_with("./data/recipes/mock_mod.zip")
        mock_archive.read.assert_called_once_with("mock_item1.json")

        self.assertEqual(item.group, "")

    @patch("zipfile.ZipFile")  # Patcher für zipfile.ZipFile
    def test_get_group2(self, mock_zipfile):
        mock_data = json.dumps({"name": "mock_mod:mock_item2",
                                "group": "mock_mod:mock_group1",
                                "type": "minecraft:crafting_shapeless",
                                "ingredients": [{"tag": "mock_mod:mock_item2"}, {"tag": "mock_mod:mock_item2"}],
                                "result": {"count": 3}}).encode("utf-8")
        mock_archive = MagicMock()
        mock_archive.read.return_value = mock_data
        mock_zipfile.return_value = mock_archive

        item = Item("mock_mod:mock_item2")
        item.get_group()

        self.assertIsNotNone(item)
        self.assertEqual("mock_mod:mock_item2", item.name)

        mock_zipfile.assert_called_once_with("./data/recipes/mock_mod.zip")
        mock_archive.read.assert_called_once_with("mock_item2.json")

        self.assertEqual("mock_mod:mock_group1", item.group)
