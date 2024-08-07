"""
End command class for SdpSubarrayLeafNode.
"""

import threading
from logging import Logger
from typing import Any, Optional, Tuple

from ska_tango_base.base import TaskCallbackType
from ska_tango_base.commands import ResultCode
from ska_tango_base.executor import TaskStatus

from ska_tmc_sdpsubarrayleafnode.commands.sdp_sln_command import SdpSLNCommand


class End(SdpSLNCommand):
    """
    A class for SdpSubarrayLeafNode's End() command.

    Invokes End command on SdpSubarray to end the current Scheduling Block.

    """

    # pylint: disable=unused-argument
    def end(
        self,
        logger: Logger,
        task_callback: TaskCallbackType,
        task_abort_event: Optional[threading.Event] = None,
    ) -> None:
        """This is a long running method for End command, it
        executes do hook, invokes End command on SdpSubarray.

        :param logger: logger
        :type logger: logging.Logger
        :param task_callback: Update task state, defaults to None
        :type task_callback: TaskCallbackType
        :param task_abort_event: Check for abort, defaults to None
        :type task_abort_event: Event, optional
        """
        task_callback(status=TaskStatus.IN_PROGRESS)
        result_code, message = self.do()
        logger.info(
            "End command invoked on: %s: Result: %s, %s",
            self.sdp_subarray_adapter.dev_name,
            result_code,
            message,
        )

        if result_code == ResultCode.FAILED:
            task_callback(
                status=TaskStatus.COMPLETED,
                result=(result_code, message),
                exception=message,
            )
        else:
            task_callback(
                status=TaskStatus.COMPLETED,
                result=(result_code, message),
            )

    def do(self, argin: Optional[Any] = None) -> Tuple[ResultCode, str]:
        """
        Method to invoke End command on SdpSubarray.

        :param argin: None

        return:
            None

        """
        return_code, message = self.init_adapter()
        if return_code == ResultCode.FAILED:
            return return_code, message
        try:
            self.sdp_subarray_adapter.End()
        except Exception as exception:
            self.logger.exception(
                "Command End "
                + f"invocation failed with exception: {exception}"
            )
            return (
                ResultCode.FAILED,
                f"The invocation of the End"
                " command is failed on SDP Subarray "
                "Device "
                f"{self.sdp_subarray_adapter.dev_name} "
                "Reason: Error in invoking "
                "End command on SDP Subarray"
                ".The command has NOT been executed. "
                "This device will continue with normal operation.",
            )
        return (
            ResultCode.OK,
            "Command Completed",
        )
