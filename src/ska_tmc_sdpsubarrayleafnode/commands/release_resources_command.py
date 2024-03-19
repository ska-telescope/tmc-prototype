"""
ReleaseAllResources command class for SdpSubarrayLeafNode.
"""
from __future__ import annotations

import logging
import threading
import time
from typing import TYPE_CHECKING, Tuple

from ska_control_model.task_status import TaskStatus
from ska_ser_logging import configure_logging
from ska_tango_base.base import TaskCallbackType
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsState
from ska_tmc_common.timeout_callback import TimeoutCallback

from ska_tmc_sdpsubarrayleafnode.commands.sdp_sln_command import SdpSLNCommand

configure_logging()
LOGGER = logging.getLogger(__name__)
if TYPE_CHECKING:
    from ..manager.component_manager import SdpSLNComponentManager


class ReleaseAllResources(SdpSLNCommand):
    """
    A class for SdpSubarayLeafNode's ReleaseAllResources() command.

    Releases all the resources of given SDP Subarray Leaf Node.
    It accepts the subarray id, releaseALL flag and receptorIDList in
    JSON string format.
    """

    def __init__(
        self,
        component_manager: SdpSLNComponentManager,
        logger: logging.Logger = LOGGER,
    ) -> None:
        super().__init__(component_manager, logger)
        self.timeout_id = f"{time.time()}_{__class__.__name__}"
        self.timeout_callback = TimeoutCallback(self.timeout_id, self.logger)
        self.component_manager = component_manager

    def release_resources(
        self,
        task_callback: TaskCallbackType,
        task_abort_event: threading.Event,
    ) -> None:
        """This is a long running method for ReleaseAllResources command, it
        executes do hook, invokes ReleaseAllResources command on SdpSubarray.

        :param task_callback: Update task state, defaults to None
        :type task_callback: Callable
        :param task_abort_event: Check for abort, defaults to None
        :type task_abort_event: Event
        """
        self.component_manager.abort_event = task_abort_event
        self.component_manager.command_in_progress = "ReleaseAllResources"
        self.task_callback = task_callback
        task_callback(status=TaskStatus.IN_PROGRESS)
        self.component_manager.start_timer(
            self.timeout_id,
            self.component_manager.command_timeout,
            self.timeout_callback,
        )
        result_code, message = self.do()
        if result_code == ResultCode.FAILED:
            self.update_task_status(result=result_code, message=message)
            self.component_manager.stop_timer()
        else:
            lrcr_callback = self.component_manager.long_running_result_callback
            self.start_tracker_thread(
                state_function="get_obs_state",
                expected_state=[ObsState.EMPTY],
                abort_event=task_abort_event,
                timeout_id=self.timeout_id,
                timeout_callback=self.timeout_callback,
                command_id=self.component_manager.release_id,
                lrcr_callback=lrcr_callback,
            )

    # pylint: disable=arguments-differ
    def do(self) -> Tuple[ResultCode, str]:
        """
        Method to invoke ReleaseAllResources command on SDP Subarray.

        :param argin: None.

        return:
            None
        """
        result_code, message = self.init_adapter()
        if result_code == ResultCode.FAILED:
            return result_code, message
        try:
            log_msg = (
                "Invoking ReleaseAllResources command on "
                + "{}".format(self.sdp_subarray_adapter.dev_name),
            )
            self.logger.debug(log_msg)
            self.sdp_subarray_adapter.ReleaseAllResources(
                self.component_manager.cmd_ended_cb
            )
        except Exception as exception:
            self.logger.exception(
                "Command invocation failed on ReleaseAllResources: %s",
                exception,
            )
            return self.component_manager.generate_command_result(
                ResultCode.FAILED,
                "The invocation of the ReleaseAllResources command is failed"
                + "on {}".format(self.sdp_subarray_adapter.dev_name)
                + "Reason: Error in invoking the ReleaseAllResourcescommand"
                "on Sdp"
                + "Subarray. The command has NOT been executed."
                + "This device will continue with normal operation.",
            )
        log_msg = (
            "ReleaseAllResources command successfully invoked on:"
            + "{}".format(self.sdp_subarray_adapter.dev_name)
        )
        self.logger.info(log_msg)
        return (ResultCode.OK, "")
