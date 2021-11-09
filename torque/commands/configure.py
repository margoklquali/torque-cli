import getpass
import logging

from docopt import DocoptExit

from torque.client import TorqueClient
from torque.commands.base import BaseCommand
from torque.constants import TorqueConfigKeys
from torque.exceptions import ConfigFileMissingError
from torque.parsers.global_input_parser import GlobalInputParser
from torque.services.config import TorqueConfigProvider
from torque.view.configure_list_view import ConfigureListView
from torque.view.view_helper import mask_token

logger = logging.getLogger(__name__)


class ConfigureCommand(BaseCommand):
    """
    usage:
        torque configure set [options]
        torque configure list
        torque configure remove <profile>
        torque configure [--help|-h]

    options:
        -P --profile <profile>      Set profile name

        -a --account <name>         Set account name

        -s --space <space>          Set space name

        -t --token <token>          Set token

        -l --login                  Retrieves an authentication token from server using account, email and password.
                                    Does not work for SSO

        -e --email <email>          Set email for authentication (when --login is set)

        -p --password <password>    Set password for authentication (when --login is set)

        -h --help                   Show this message
    """

    def get_actions_table(self) -> dict:
        return {"set": self.do_configure, "list": self.do_list, "remove": self.do_remove}

    def do_list(self):
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

        login = self.input_parser.configure_set.login

        config_provider = TorqueConfigProvider(config_file)
        config = {}
        try:
            config = config_provider.load_all()
        except Exception:
            pass

        # read profile
        profile = self.input_parser.configure_set.profile or input("Profile Name [default]: ")
        profile = profile or "default"

        # if profile exists set current values from profile
        current_account = config.get(profile, {}).get(TorqueConfigKeys.ACCOUNT, "")
        current_space = config.get(profile, {}).get(TorqueConfigKeys.SPACE, "")
        current_token = config.get(profile, {}).get(TorqueConfigKeys.TOKEN, "")

        # read account
        login_msg = (
            "Torque Account [{current_account}]: " if login else f"Torque Account (optional) [{current_account}]: "
        )
        account = self.input_parser.configure_set.account or input(login_msg)

        if login and not account:  # required if login using email and password
            return self.die("Account cannot be empty")
        account = account or current_account

        # read space name
        space = self.input_parser.configure_set.space or input(f"Torque Space [{current_space}]: ")
        space = space or current_space
        if not space:
            return self.die("Space cannot be empty")

        if login:
            # read email
            email = self.input_parser.configure_set.email or input("Email: ")
            if not email:
                return self.die("Email cannot be empty")

            # read password
            password = self.input_parser.configure_set.password or getpass.getpass("Password: ")

            # get token
            try:
                client = TorqueClient()
                access_token = client.login(account, email, password)
                client.session.init_bearer_auth(access_token)
                token = client.longtoken()
            except Exception as e:
                logger.exception(e, exc_info=False)
                return self.die()
        else:
            # read token
            token = self.input_parser.configure_set.token or getpass.getpass(
                f"Torque Token [{mask_token(current_token)}]: "
            )
            token = token or current_token
            if not token:
                return self.die("Token cannot be empty")

        # save user inputs
        config_provider.save_profile(profile, token, space, account)

        return self.success()
