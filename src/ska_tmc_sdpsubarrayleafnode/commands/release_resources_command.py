"""
ReleaseAllResources command class for SdpSubarrayLeafNode.
"""
import threading
import time
from logging import Logger
from typing import Callable, Optional, Tuple

from ska_control_model.task_status import TaskStatus
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsState
from ska_tmc_common.timeout_callback import TimeoutCallback
from tango import DevFailed

from ska_tmc_sdpsubarrayleafnode.commands.abstract_command import SdpSLNCommand


class ReleaseAllResources(SdpSLNCommand):
    """
    A class for SdpSubarayLeafNode's ReleaseAllResources() command.

    Releases all the resources of given SDP Subarray Leaf Node.
    It accepts the subarray id, releaseALL flag and receptorIDList in
    JSON string format.
    """

    def __init__(self, component_manager, logger=None) -> None:
        super().__init__(component_manager, logger)
        self.timeout_id = f"{time.time()}_{__class__.__name__}"
        self.timeout_callback = TimeoutCallback(self.timeout_id, self.logger)
        self.task_callback: Callable

    def release_resources(
        self,
        logger: Logger,
        task_callback: Callable = None,
        # pylint: disable=unused-argument
        task_abort_event: Optional[threading.Event] = None,
    ) -> None:
        """This is a long running method for ReleaseAllResources command, it
        executes do hook, invokes ReleaseAllResources command on SdpSubarray.

        :param logger: logger
        :type logger: logging.Logger
        :param task_callback: Update task state, defaults to None
        :type task_callback: Callable, optional
        :param task_abort_event: Check for abort, defaults to None
        :type task_abort_event: Event, optional
        """
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
            self.update_task_status(result_code, message)
            self.component_manager.stop_timer()
        else:
            lrcr_callback = self.component_manager.long_running_result_callback
            self.start_tracker_thread(
                self.component_manager.get_obs_state,
                ObsState.EMPTY,
                self.timeout_id,
                self.timeout_callback,
                command_id=self.component_manager.release_id,
                lrcr_callback=lrcr_callback,
            )

    #  pylint: disable=arguments-differ
    def update_task_status(self, result: ResultCode, message: str = ""):
        if result == ResultCode.FAILED:
            self.task_callback(
                status=TaskStatus.COMPLETED,
                result=result,
                exception=message,
            )
        else:
            self.task_callback(status=TaskStatus.COMPLETED, result=result)
        self.component_manager.command_in_progress = ""

    #  pylint: enable=arguments-differ

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
        except (AttributeError, ValueError, TypeError, DevFailed) as e:
            self.logger.exception(
                "Command invocation failed on ReleaseAllResources: %s", e
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
