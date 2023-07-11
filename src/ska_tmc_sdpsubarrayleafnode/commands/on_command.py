"""
On command class for SdpSubarrayLeafNode.
"""
import threading
from typing import Callable, Optional

from ska_tango_base.commands import ResultCode
from ska_tango_base.executor import TaskStatus

from ska_tmc_sdpsubarrayleafnode.commands.abstract_command import SdpSLNCommand


class On(SdpSLNCommand):
    """
    A class for SdpSubarrayLeafNode's On() command.

    This command turns on SDP Subarray device.
    """

    # pylint: disable=unused-argument
    def on(
        self,
        logger,
        task_callback: Callable = None,
        task_abort_event: Optional[threading.Event] = None,
    ) -> None:
        """A method to invoke the On command.
        It sets the task_callback status according to command progress.

        :param logger: logger
        :type logger: logging.Logger
        :param task_callback: Update task state, defaults to None
        :type task_callback: Callable, optional
        :param task_abort_event: Check for abort, defaults to None
        :type task_abort_event: Event, optional
        """
        task_callback(status=TaskStatus.IN_PROGRESS)
        result_code, message = self.do()
        logger.info(
            "On command invoked on: %s: Result: %s, %s",
            self.sdp_subarray_adapter.dev_name,
            result_code,
            message,
        )
        task_callback(
            status=TaskStatus.COMPLETED,
            result=result_code,
            exception=message,
        )

    # pylint: enable=unused-argument

    def do(self, argin=None):
        """
        Method to invoke On command on SdpSubarray.

        """
        return_code, message = self.init_adapter()
        if return_code == ResultCode.FAILED:
            return return_code, message
        try:
            self.sdp_subarray_adapter.On()
        except Exception as e:
            self.logger.exception(f"Command invocation failed: {e}")
            return (
                ResultCode.FAILED,
                f"The invocation of the On"
                " command is failed on SDP Subarray "
                "Device "
                f"{self.sdp_subarray_adapter.dev_name} "
                "Reason: Error in invoking "
                "On command on SDP Subarray"
                ".The command has NOT been executed. "
                "This device will continue with normal operation.",
            )
        return ResultCode.OK, ""
