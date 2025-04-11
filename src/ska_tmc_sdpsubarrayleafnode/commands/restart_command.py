"""Restart command class for Sdp Subarray."""

import logging
import time
from typing import Callable, Dict, Optional, Tuple, Union

from ska_control_model.task_status import TaskStatus
from ska_ser_logging.configuration import configure_logging
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsState
from ska_tmc_common import TimeKeeper, TimeoutCallback, TimeoutState
from ska_tmc_common.v1.error_propagation_tracker import (
    error_propagation_tracker,
)
from ska_tmc_common.v1.timeout_tracker import timeout_tracker

from ska_tmc_sdpsubarrayleafnode.commands.sdp_sln_command import SdpSLNCommand

configure_logging()
LOGGER = logging.getLogger(__name__)


class Restart(SdpSLNCommand):
    """
    A class for Sdp Subarray Restart command.
    Restarts the Sdp Subarray device.
    """

    def __init__(
        self,
        component_manager,
        logger: logging.Logger = LOGGER,
    ) -> None:
        super().__init__(component_manager, logger)
        self.timeout_id: str = f"{time.time()}_{__class__.__name__}"
        self.timeout_callback: Callable[
            [str, TimeoutState], Optional[ValueError]
        ] = TimeoutCallback(self.timeout_id, self.logger)
        self.timekeeper = TimeKeeper(
            self.component_manager.command_timeout, logger
        )

    @timeout_tracker
    @error_propagation_tracker(
        "get_obs_state", [ObsState.RESTARTING, ObsState.EMPTY]
    )
    def restart(self) -> Tuple[ResultCode, str]:
        """
        This is a long running method for Restart command, it
        executes do hook, invokes Restart command on the CspSubarray.
        """
        return self.do()

    def update_task_status(
        self,
        **kwargs: Dict[str, Union[Tuple[ResultCode, str], TaskStatus, str]],
    ) -> None:
        """
        Update the status of a task.

        Args:
            **kwargs: Keyword arguments for task status update.
        """
        result = kwargs.get("result")
        status = kwargs.get("status", TaskStatus.COMPLETED)
        message = kwargs.get("exception")
        self.logger.debug("Result of Restart execution: %s", result[0])
        self.logger.debug("Restart command execution status: %s", status)
        self.logger.debug("Restart command execution message: %s", message)

        if result:
            if result[0] == ResultCode.OK and status == TaskStatus.COMPLETED:
                self.task_callback(status=status, result=result)
            else:
                self.task_callback(
                    status=status, result=result, exception=message
                )
        self.component_manager.command_in_progress = ""

    # pylint: disable=arguments-differ
    def do(self) -> Tuple[ResultCode, str]:
        """
        Method to invoke Restart command on Sdp Subarray.

        :param  None:

        Note: Enter the json string without spaces as a input.

        :return: (ResultCode, message)

        """
        result_code, message = self.init_adapter()
        if result_code == ResultCode.FAILED:
            return result_code, message

        try:
            self.logger.info(
                "Invoking Restart command on Sdp Subarray: %s",
                self.sdp_subarray_adapter.dev_name,
            )
            self.sdp_subarray_adapter.Restart()
        except Exception as exception:
            self.logger.exception(
                "Command Restart invocation failed with exception: %s",
                exception,
            )

            return (
                ResultCode.FAILED,
                "Execution of Restart command is failed."
                + " Reason: Error in invoking Restart "
                + "command on Sdp Subarray - "
                + f"{self.sdp_subarray_adapter.dev_name}: {exception}",
            )

        self.logger.info(
            "Restart command successfully invoked on Device : %s",
            self.sdp_subarray_adapter.dev_name,
        )
        return (ResultCode.OK, "Command Completed")
