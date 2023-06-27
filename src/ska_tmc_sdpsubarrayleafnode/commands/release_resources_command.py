"""
ReleaseAllResources command class for SdpSubarrayLeafNode.
"""
import threading
from logging import Logger
from typing import Callable, Optional

from ska_tango_base.commands import ResultCode
from ska_tango_base.executor import TaskStatus
from tango import DevFailed

from ska_tmc_sdpsubarrayleafnode.commands.abstract_command import SdpSLNCommand


class ReleaseAllResources(SdpSLNCommand):
    """
    A class for SdpSubarayLeafNode's ReleaseAllResources() command.

    Releases all the resources of given SDP Subarray Leaf Node.
    It accepts the subarray id, releaseALL flag and receptorIDList in
    JSON string format.
    """

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
        task_callback(status=TaskStatus.IN_PROGRESS)
        exception = ""
        result_code, message = self.do()
        logger.info(
            "ReleaseAllResource command invoked on: %s: Result: %s, %s",
            self.sdp_subarray_adapter.dev_name,
            result_code,
            message,
        )
        if result_code == ResultCode.FAILED:
            exception = message
            task_callback(
                status=TaskStatus.COMPLETED,
                result=ResultCode.FAILED,
                exception=exception,
            )
        else:
            task_callback(
                status=TaskStatus.COMPLETED,
                result=ResultCode.OK,
            )

    def do(self, argin=None):
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
            self.sdp_subarray_adapter.ReleaseAllResources()
        except (AttributeError, ValueError, TypeError, DevFailed) as e:
            self.logger.exception(
                "Command invocation failed on ReleaseAllResources: %s", e
            )
            return self.component_manager.generate_command_result(
                ResultCode.FAILED,
                "The invocation of the ReleaseAllResources command isfailed"
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
