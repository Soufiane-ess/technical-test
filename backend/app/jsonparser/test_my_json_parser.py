import unittest

from app.jsonparser.my_json_parser import MyJsonParser


class TestJsonParser(unittest.TestCase):

    def setUp(self) -> None:
        self.example_mf_json_file_path = './configuration-files/millennium-falcon.json'
        self.example_malformed_mf_json_file_path = './configuration-files/malformed-millennium-falcon.json'
        self.example_empire_json_file_path = './configuration-files/empire.json'

    def test_parse_empire_file_from_location(self):
        parsed_example_json_file = MyJsonParser.parse_json_file_from_location(self.example_empire_json_file_path)
        self.assertTrue(parsed_example_json_file)
        self.assertIsInstance(parsed_example_json_file, dict)

    def test_parse_file_from_location(self):
        parsed_example_json_file = MyJsonParser.parse_json_file_from_location(self.example_mf_json_file_path)
        self.assertTrue(parsed_example_json_file)
        self.assertIsInstance(parsed_example_json_file, dict)

    def test_parse_file_from_wrong_location(self):
        self.assertFalse(MyJsonParser.parse_json_file_from_location('/some/custom/path'))

    def test_parse_file_from_empty_location(self):
        self.assertFalse(MyJsonParser.parse_json_file_from_location(''))

    def test_parse_malformed_json_file(self):
        self.assertFalse(MyJsonParser.parse_json_file_from_location(self.example_malformed_mf_json_file_path))
