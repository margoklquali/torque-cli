from typing import Any

from colorama import Fore, Style
from docopt import DocoptExit, docopt

from torque.base import ResourceManager
from torque.client import TorqueClient
from torque.models.connection import TorqueConnection
from torque.parsers.command_input_parsers import CommandInputParser
from torque.parsers.global_input_parser import GlobalInputParser
from torque.services.output_formatter import OutputFormatter


class BaseCommand(object):
    """
    usage: torque
    """

    RESOURCE_MANAGER = ResourceManager
    OUTPUT_FORMATTER = OutputFormatter

    def __init__(self, command_args: list, connection: TorqueConnection = None):
        if connection:
            self.client = TorqueClient(space=connection.space, token=connection.token, account=connection.account)
            self.manager = self.RESOURCE_MANAGER(client=self.client)
        else:
            self.client = None
            self.manager = None

        self.args = docopt(self.__doc__, argv=command_args)
        self.input_parser = CommandInputParser(self.args)
        self.global_input_parser = GlobalInputParser(self.args)
        self.output_formatter = self.OUTPUT_FORMATTER(self.global_input_parser)

    def execute(self) -> bool:
        """Finds a subcommand passed to with command in
        object actions table and executes mapped method"""

        actions_table = self.get_actions_table()
        for action in actions_table:
            if self.args.get(action, False):
                # call action
                success, output = actions_table[action]()
                if output:
                    self.output_formatter.yield_output(success, output)
                return success

        # if subcommand was specified without args (actions), just show usage
        raise DocoptExit

    def get_actions_table(self) -> dict:
        return {}

    def styled_text(self, style, message: str = "", newline=True):
        self.output_formatter.styled_text(style, message, newline)

    def message(self, message: str = "", newline=True):
        self.output_formatter.yield_output(True, message)

    def error(self, message: str = "") -> bool:
        self.styled_text(Fore.RED, message)
        return False

    def success(self, message: str = "") -> (bool, Any):
        self.styled_text(Fore.GREEN, message)
        return True, None

    def die(self, message: str = "") -> (bool, str):
        return False, message

    # Unimportant info that can be de-emphasized
    def fyi_info(self, message: str = ""):
        self.styled_text(Style.DIM, message)

    # Something active is being performed
    def action_announcement(self, message: str = ""):
        self.styled_text(Fore.YELLOW, message)

    # Unimportant info that can be de-emphasized
    def info(self, message: str = ""):
        self.styled_text(Fore.LIGHTBLUE_EX, message)

    # Unimportant info that can be de-emphasized
    def important_value(self, prefix_message: str = "", value: str = ""):
        if prefix_message:
            self.styled_text(Style.DIM, prefix_message, False)
        self.styled_text(Fore.CYAN, value)

    def url(self, prefix_message, message: str = ""):
        if prefix_message:
            self.styled_text(Style.DIM, prefix_message, False)
        self.styled_text(Fore.BLUE, message)
