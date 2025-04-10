"""
Abort Command for Sdp Subarray.
"""
import threading
import time
from logging import Logger
from typing import Callable, Dict, Optional, Tuple, Union

from ska_control_model.task_status import TaskStatus
from ska_tango_base.base import TaskCallbackType
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsState
from ska_tmc_common import TimeKeeper, TimeoutCallback, TimeoutState
from ska_tmc_common.v1.error_propagation_tracker import (
    error_propagation_tracker,
)
from ska_tmc_common.v1.timeout_tracker import timeout_tracker

from ska_tmc_sdpsubarrayleafnode.commands.sdp_sln_command import (
    SdpSLNCommand,
    task_callback_default,
)


class Abort(SdpSLNCommand):
    """
    A class for Sdp Subarray Abort() command.
    Aborts the Sdp Subarray device.
    """

    def __init__(
        self,
        component_manager,
        logger: Logger,
    ):
        super().__init__(
            component_manager=component_manager,
            logger=logger,
        )
        self.component_manager = component_manager
        self.logger = logger
        self.timeout_id: str = f"{time.time()}_{__class__.__name__}"
        self.timeout_callback: Callable[
            [str, TimeoutState], Optional[ValueError]
        ] = TimeoutCallback(self.timeout_id, self.logger)
        self.timekeeper = TimeKeeper(
            self.component_manager.command_timeout, logger
        )

    # pylint: disable=unused-argument
    @timeout_tracker
    @error_propagation_tracker(
        "get_obs_state", [ObsState.ABORTING, ObsState.ABORTED]
    )
    def invoke_abort(
        self,
        task_callback: TaskCallbackType = task_callback_default,
        task_abort_event: Optional[threading.Event] = None,
    ):
        """This method calls do for Abort command"""
        result_code, message = self.do()
        return result_code, message

    # pylint: enable=unused-argument

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

        self.logger.debug("Result of Abort execution: %s", result[0])
        self.logger.debug("Abort command execution status: %s", status)
        self.logger.debug("Abort command execution message: %s", message)

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
        This method invokes Abort command on Sdp Subarray

        return:
            A tuple containing a return code and a string
            message indicating status.
            The message is for information purpose only.

        rtype:
            (ResultCode, str)

        raises:
            Exception if error occurs in invoking command
            on any of the devices like Sdp Subarray
        """
        result_code, message = self.init_adapter()
        if result_code == ResultCode.FAILED:
            return result_code, message
        try:
            self.logger.info(
                "Invoking Abort command on Sdp Subarray:%s",
                self.sdp_subarray_adapter.dev_name,
            )
            self.sdp_subarray_adapter.Abort()
        except Exception as exception:
            self.logger.exception(
                "Command Abort invocation failed with exception: %s", exception
            )

            return self.component_manager.generate_command_result(
                ResultCode.FAILED,
                "Execution of Abort command is failed."
                + "Reason: Error in invoking Abort command on Sdp Subarray -"
                + f"{self.sdp_subarray_adapter.dev_name}: {exception}",
            )
        return (ResultCode.OK, "Command Completed")
