import os
import unittest
from unittest import mock

from torque.client import TorqueClient


class TestClient(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TorqueClient()
        self.client_with_account = TorqueClient(account="my_account")

    def test_default_api_path(self):
        client = TorqueClient()
        expected = "https://qtorque.io/api/"
        self.assertEqual(client.base_url, expected)

    @mock.patch.dict(os.environ, {"TORQUE_HOSTNAME": "example.com"})
    def test_default_api_path_custom_url(self):
        client = TorqueClient()
        expected = "https://example.com/api/"
        self.assertEqual(client.base_url, expected)

    def test_request_wrong_method(self):
        endpoint = "blueprints/"
        with self.assertRaises(ValueError):
            self.client.request(endpoint=endpoint, method="UPDATE")

    def test_if_account_provided_client_base_url_includes_it(self):
        self.assertEqual(self.client_with_account.base_url, "https://qtorque.io/api/")


if __name__ == "__main__":
    unittest.main()
