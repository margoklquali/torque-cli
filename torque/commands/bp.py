import logging
from typing import Any

from torque.branch.branch_context import ContextBranch
from torque.branch.branch_utils import get_and_check_folder_based_repo
from torque.commands.base import BaseCommand
from torque.models.blueprints import BlueprintsManager
from torque.parsers.command_input_validators import CommandInputValidator

logger = logging.getLogger(__name__)


class BlueprintsCommand(BaseCommand):
    """
    usage:
        torque (bp | blueprint) list [--output=json | --output=json --detail]
        torque (bp | blueprint) validate <name> [--branch <branch>] [--commit <commitId>] [--output=json]
        torque (bp | blueprint) [--help]

    options:
       -b --branch <branch>     Specify the name of the remote git branch. If not provided, the CLI will attempt to
                                automatically detect the current working branch. The latest branch commit will be used
                                by default unless the commit parameter is also specified.

       -c --commit <commitId>   Specify the commit ID. This can be used to validate a blueprint from an historic commit.
                                This option can be used together with the branch parameter.

       -o --output=json         Yield output in JSON format

       -d --detail              Obtain full blueprint data in JSON format

       -h --help                Show this message
    """

    RESOURCE_MANAGER = BlueprintsManager

    def get_actions_table(self) -> dict:
        return {"list": self.do_list, "validate": self.do_validate}

    def do_list(self) -> (bool, Any):
        detail = self.input_parser.blueprint_list.detail
        try:
            if detail:
                blueprint_list = self.manager.list_detailed()
            else:
                blueprint_list = self.manager.list()
        except Exception as e:
            logger.exception(e, exc_info=False)
            return self.die()

        return True, blueprint_list

    def do_validate(self) -> (bool, Any):
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
            logger.info("Blueprint validation failed")
            return self.die(errors)

        else:
            return self.success("Blueprint is valid")
