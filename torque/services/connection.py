import logging

from docopt import DocoptExit

from torque.constants import TorqueConfigKeys
from torque.exceptions import ConfigError
from torque.models.connection import TorqueConnection
from torque.parsers.global_input_parser import GlobalInputParser
from torque.services.config import TorqueConfigProvider

logger = logging.getLogger(__name__)


class TorqueConnectionProvider:
    def __init__(self, args_parser: GlobalInputParser):
        self._args_parser = args_parser

    def get_connection(self) -> TorqueConnection:
        # first try to get them as options or from env variable
        token = self._args_parser.token
        space = self._args_parser.space
        account = self._args_parser.account

        # then try to load them from file
        if not all([token, space]):
            logger.debug("Couldn't fetch token/space neither from command line nor environment variables")
            profile = self._args_parser.profile
            config_file = self._args_parser.get_config_path()
            logger.debug("Trying to obtain unset values from configuration file")
            try:
                torque_conn = TorqueConfigProvider(config_file).load_connection(profile)
                token = token or torque_conn[TorqueConfigKeys.TOKEN]
                space = space or torque_conn[TorqueConfigKeys.SPACE]
                if TorqueConfigKeys.ACCOUNT in torque_conn:
                    account = torque_conn[TorqueConfigKeys.ACCOUNT]
            except ConfigError as e:
                raise DocoptExit(f"Unable to read Torque credentials. Reason: {e}")

        return TorqueConnection(token=token, space=space, account=account)
