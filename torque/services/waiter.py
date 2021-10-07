import datetime
import time

from yaspin import yaspin

from torque.branch.branch_context import ContextBranch
from torque.branch.branch_utils import can_temp_branch_be_deleted, logger
from torque.commands.base import BaseCommand
from torque.constants import DEFAULT_TIMEOUT, FINAL_SB_STATUSES
from torque.sandboxes import SandboxesManager


class Waiter(object):
    @staticmethod
    def wait_for_sandbox_to_launch(
        command: BaseCommand,
        sb_manager: SandboxesManager,
        sandbox_id: str,
        timeout: int,
        context_branch: ContextBranch,
        wait: bool,
    ) -> bool:

        if not wait and not context_branch.temp_branch_exists:
            return False
        try:
            if context_branch.temp_branch_exists:
                context_branch.revert_from_local_temp_branch()

            if not timeout:
                timeout = DEFAULT_TIMEOUT

            start_time = datetime.datetime.now()
            sandbox = sb_manager.get(sandbox_id)
            status = getattr(sandbox, "sandbox_status")

            sandbox_start_wait_output(command, sandbox_id, context_branch.temp_branch_exists)

            spinner_class = NullSpinner if command.global_input_parser.output_json else yaspin

            with spinner_class(text="Starting...", color="yellow") as spinner:
                while (datetime.datetime.now() - start_time).seconds < timeout * 60:
                    if status in FINAL_SB_STATUSES:
                        spinner.green.ok("✔")
                        break
                    if context_branch.temp_branch_exists and can_temp_branch_be_deleted(sandbox):
                        context_branch.delete_temp_branch()
                        if not wait:
                            spinner.green.ok("✔")
                            break

                    time.sleep(5)
                    spinner.text = f"[{int((datetime.datetime.now() - start_time).total_seconds())} sec]"
                    sandbox = sb_manager.get(sandbox_id)
                    status = getattr(sandbox, "sandbox_status")
                else:
                    logger.error(f"Timeout Reached - Sandbox {sandbox_id} was not active after {timeout} minutes")
                    return True
            return False

        except Exception as e:
            logger.error(f"There was an issue with waiting for sandbox deployment -> {str(e)}")


def sandbox_start_wait_output(command: BaseCommand, sandbox_id, temp_branch_exists):
    if temp_branch_exists:
        logger.debug(f"Waiting before deleting temp branch that was created for this sandbox (id={sandbox_id})")
        command.fyi_info("Canceling or exiting before the process completes may cause the sandbox to fail")
        command.info("Waiting for the Sandbox to start with local changes. This may take some time.")
    else:
        logger.debug(f"Waiting for the Sandbox {sandbox_id} to finish launching...")
        command.info("Waiting for the Sandbox to start. This may take some time.")


class NullSpinner:
    text: str

    def __init__(self, text, color):
        self.green = NullSpinnerOut()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class NullSpinnerOut:
    def ok(self, text) -> None:
        pass
