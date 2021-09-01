import unittest
from unittest.mock import Mock, patch

from docopt import DocoptExit

from torque.constants import TorqueConfigKeys
from torque.exceptions import ConfigError
from torque.services.connection import TorqueConnectionProvider


class TestTorqueConnectionProvider(unittest.TestCase):
    def setUp(self) -> None:
        self.input_parser_mock = Mock()
        self.connection_provider = TorqueConnectionProvider(self.input_parser_mock)

    def test_get_connection_with_all_arg_inputs(self):
        # arrange - basic setup is sufficient for this test, nothing to do arrange

        # act
        connection = self.connection_provider.get_connection()

        # assert
        self.assertEqual(connection.token, self.input_parser_mock.token)
        self.assertEqual(connection.space, self.input_parser_mock.space)
        self.assertEqual(connection.account, self.input_parser_mock.account)

    @patch("torque.services.connection.TorqueConfigProvider")
    def test_get_connection_with_token_and_space_in_arg_inputs(self, config_provider):
        # arrange
        self.input_parser_mock.account = None

        # act
        connection = self.connection_provider.get_connection()

        # assert
        config_provider.assert_not_called()
        self.assertEqual(connection.token, self.input_parser_mock.token)
        self.assertEqual(connection.space, self.input_parser_mock.space)
        self.assertIsNone(connection.account)

    @patch("torque.services.connection.TorqueConfigProvider")
    def test_get_connection_with_no_arg_inputs(self, config_provider):
        # arrange
        TestTorqueConnectionProviderHelper.set_input_parse_return_values(self.input_parser_mock)
        token = Mock()
        space = Mock()
        account = Mock()
        torque_conn_dict = TestTorqueConnectionProviderHelper.build_connection_dict(account, space, token)
        load_connection_method_mock = Mock(return_value=torque_conn_dict)
        config_provider.return_value = Mock(load_connection=load_connection_method_mock)

        # act
        connection = self.connection_provider.get_connection()

        # assert
        load_connection_method_mock.assert_called_once_with(self.input_parser_mock.profile)
        self.assertEqual(connection.token, token)
        self.assertEqual(connection.space, space)
        self.assertEqual(connection.account, account)

    @patch("torque.services.connection.TorqueConfigProvider")
    def test_get_connection_with_no_arg_inputs_no_account_in_conf_file(self, config_provider):
        TestTorqueConnectionProviderHelper.set_input_parse_return_values(self.input_parser_mock)
        token = Mock()
        space = Mock()
        account = None
        torque_conn_dict = TestTorqueConnectionProviderHelper.build_connection_dict(account, space, token)
        load_connection_method_mock = Mock(return_value=torque_conn_dict)
        config_provider.return_value = Mock(load_connection=load_connection_method_mock)

        # act
        connection = self.connection_provider.get_connection()

        # assert
        load_connection_method_mock.assert_called_once_with(self.input_parser_mock.profile)
        self.assertEqual(connection.token, token)
        self.assertEqual(connection.space, space)
        self.assertEqual(connection.account, account)

    @patch("torque.services.connection.TorqueConfigProvider")
    def test_get_connection_space_arg_input_overrides_conf_file(self, config_provider):
        TestTorqueConnectionProviderHelper.set_input_parse_return_values(self.input_parser_mock, space=Mock())
        token = Mock()
        space = Mock()
        account = None
        torque_conn_dict = TestTorqueConnectionProviderHelper.build_connection_dict(account, space, token)
        load_connection_method_mock = Mock(return_value=torque_conn_dict)
        config_provider.return_value = Mock(load_connection=load_connection_method_mock)

        # act
        connection = self.connection_provider.get_connection()

        # assert
        load_connection_method_mock.assert_called_once_with(self.input_parser_mock.profile)
        self.assertEqual(connection.token, token)
        self.assertEqual(connection.space, self.input_parser_mock.space)
        self.assertEqual(connection.account, account)

    @patch("torque.services.connection.TorqueConfigProvider")
    def test_get_connection_token_arg_input_overrides_conf_file(self, config_provider):
        TestTorqueConnectionProviderHelper.set_input_parse_return_values(self.input_parser_mock, token=Mock())
        token = Mock()
        space = Mock()
        account = None
        torque_conn_dict = TestTorqueConnectionProviderHelper.build_connection_dict(account, space, token)
        load_connection_method_mock = Mock(return_value=torque_conn_dict)
        config_provider.return_value = Mock(load_connection=load_connection_method_mock)

        # act
        connection = self.connection_provider.get_connection()

        # assert
        load_connection_method_mock.assert_called_once_with(self.input_parser_mock.profile)
        self.assertEqual(connection.token, self.input_parser_mock.token)
        self.assertEqual(connection.space, space)
        self.assertEqual(connection.account, account)

    @patch("torque.services.connection.TorqueConfigProvider")
    def test_get_connection_config_provider_raises(self, config_provider):
        # arrange
        TestTorqueConnectionProviderHelper.set_input_parse_return_values(self.input_parser_mock)
        config_provider.side_effect = ConfigError()

        # act
        with self.assertRaises(DocoptExit):
            self.connection_provider.get_connection()


class TestTorqueConnectionProviderHelper:
    @staticmethod
    def build_connection_dict(account, space, token):
        torque_conn_dict = {
            TorqueConfigKeys.TOKEN: token,
            TorqueConfigKeys.SPACE: space,
        }
        if account:
            torque_conn_dict.update({TorqueConfigKeys.ACCOUNT: account})
        return torque_conn_dict

    @staticmethod
    def set_input_parse_return_values(
        input_parser_mock: Mock, space: str = None, token: str = None, account: str = None
    ):
        input_parser_mock.token = token
        input_parser_mock.space = space
        input_parser_mock.account = account
