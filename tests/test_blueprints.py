import json
import unittest
from unittest import mock

from torque.models.blueprints import Blueprint


class TestBlueprintJsonLoad(unittest.TestCase):
    def setUp(self) -> None:
        manager = mock.Mock()
        bp_json_file = "tests/fixtures/test_bp.json"
        with open(bp_json_file) as f:
            json_obj = json.load(f)
            self.blueprint = Blueprint.json_deserialize(manager=manager, json_obj=json_obj)

    def test_has_errors_attr(self):
        self.assertTrue(hasattr(self.blueprint, "errors"))

    def test_has_desc_attr(self):
        self.assertTrue(hasattr(self.blueprint, "description"))

    def test_bp_has_correct_desc(self):
        expected = "A dev environment for both local and offshore teams"
        self.assertEqual(expected, self.blueprint.description)

    def test_bp_has_no_errors(self):
        self.assertFalse(self.blueprint.errors)


class TestBlueprintSerialize(unittest.TestCase):
    def test_bp_serialize(self):
        manager = mock.Mock()
        bp_json_file = "tests/fixtures/test_bp_serialize.json"
        blueprint = Blueprint(manager, "Name1", "http://example.com", True)
        json_dict = blueprint.json_serialize()
        json_text = json.dumps(json_dict, indent=True)

        with open(bp_json_file) as f:
            expected = f.read()

        self.assertEqual(expected, json_text)


if __name__ == "__main__":
    unittest.main()
