import logging
from collections import OrderedDict

import tabulate

from torque.blueprints import BlueprintsManager
from torque.branch.branch_context import ContextBranch
from torque.branch.branch_utils import get_and_check_folder_based_repo
from torque.commands.base import BaseCommand
from torque.parsers.command_input_validators import CommandInputValidator

logger = logging.getLogger(__name__)


class BlueprintsCommand(BaseCommand):
    """
    usage:
        torque (bp | blueprint) list
        torque (bp | blueprint) validate <name> [--branch <branch>] [--commit <commitId>]
        torque (bp | blueprint) [--help]

    options:
       -b --branch <branch>     Specify the name of the remote git branch. If not provided, the CLI will attempt to
                                automatically detect the current working branch. The latest branch commit will be used
                                by default unless the commit parameter is also specified.

       -c --commit <commitId>   Specify the commit ID. This can be used to validate a blueprint from an historic commit.
                                This option can be used together with the branch parameter.

       -h --help                Show this message
    """

    RESOURCE_MANAGER = BlueprintsManager

    def get_actions_table(self) -> dict:
        return {"list": self.do_list, "validate": self.do_validate}

    def do_list(self) -> bool:
        try:
            blueprint_list = self.manager.list()
        except Exception as e:
            logger.exception(e, exc_info=False)
            return self.die()

        result_table = []
        for bp in blueprint_list:

            result_table.append({"Name": bp.name, "Description": bp.description, "Enabled": bp.enabled})

        self.message(tabulate.tabulate(result_table, headers="keys"))
        return False

    def do_validate(self) -> bool:
        blueprint_name = self.input_parser.blueprint_validate.blueprint_name
        branch = self.input_parser.blueprint_validate.branch
        commit = self.input_parser.blueprint_validate.commit

        CommandInputValidator.validate_commit_and_branch_specified(branch, commit)

        repo = get_and_check_folder_based_repo(blueprint_name)
        with ContextBranch(repo, branch) as context_branch:
            if not context_branch:
                return self.error("Unable to Validate BP")
            try:
                bp = self.manager.validate(
                    blueprint=blueprint_name, branch=context_branch.validation_branch, commit=commit
                )
            except Exception as e:
                logger.exception(e, exc_info=False)
                return self.die()

        errors = getattr(bp, "errors")

        if errors:
            # We don't need error code
            err_table = [OrderedDict([("NAME", err["name"]), ("MESSAGE", err["message"])]) for err in errors]

            logger.error("Blueprint validation failed")
            return self.die(tabulate.tabulate(err_table, headers="keys"))

        else:
            return self.success("Blueprint is valid")
