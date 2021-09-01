import getpass
import logging

from docopt import DocoptExit

from torque.commands.base import BaseCommand
from torque.constants import TorqueConfigKeys
from torque.exceptions import ConfigFileMissingError
from torque.parsers.global_input_parser import GlobalInputParser
from torque.sandboxes import SandboxesManager
from torque.services.config import TorqueConfigProvider
from torque.view.configure_list_view import ConfigureListView
from torque.view.view_helper import mask_token

logger = logging.getLogger(__name__)


class ConfigureCommand(BaseCommand):
    """
    usage:
        torque configure set
        torque configure list
        torque configure remove <profile>
        torque configure [--help|-h]

    options:
        -h --help                   Show this message
    """

    RESOURCE_MANAGER = SandboxesManager

    def get_actions_table(self) -> dict:
        return {"set": self.do_configure, "list": self.do_list, "remove": self.do_remove}

    def do_list(self):
        config = None
        try:
            config_file = GlobalInputParser.get_config_path()
            config = TorqueConfigProvider(config_file).load_all()
            result_table = ConfigureListView(config).render()

        except ConfigFileMissingError:
            raise DocoptExit("Config file doesn't exist. Use 'torque configure set' to configure Torque CLI.")
        except Exception as e:
            logger.exception(e, exc_info=False)
            return self.die()

        self.message(result_table)
        return self.success()

    def do_remove(self):
        profile_to_remove = self.input_parser.configure_remove.profile
        if not profile_to_remove:
            raise DocoptExit("Please provide a profile name to remove")

        try:
            config_file = GlobalInputParser.get_config_path()
            config_provider = TorqueConfigProvider(config_file)
            config_provider.remove_profile(profile_to_remove)
        except Exception as e:
            logger.exception(e, exc_info=False)
            return self.die()

        return self.success()

    def do_configure(self):
        config_file = GlobalInputParser.get_config_path()
        config_provider = TorqueConfigProvider(config_file)
        config = {}
        try:
            config = config_provider.load_all()
        except Exception:
            pass

        # read profile
        profile = input("Profile Name [default]: ")
        profile = profile or "default"

        # if profile exists set current values from profile
        current_account = config.get(profile, {}).get(TorqueConfigKeys.ACCOUNT, "")
        current_space = config.get(profile, {}).get(TorqueConfigKeys.SPACE, "")
        current_token = config.get(profile, {}).get(TorqueConfigKeys.TOKEN, "")

        # read account
        account = input(f"Torque Account (optional) [{current_account}]: ")
        account = account or current_account

        # read space name
        space = input(f"Torque Space [{current_space}]: ")
        space = space or current_space
        if not space:
            return self.die("Space cannot be empty")

        # read token
        token = getpass.getpass(f"Torque Token [{mask_token(current_token)}]: ")
        token = token or current_token
        if not token:
            return self.die("Token cannot be empty")

        # save user inputs
        config_provider.save_profile(profile, token, space, account)

        return self.success()
