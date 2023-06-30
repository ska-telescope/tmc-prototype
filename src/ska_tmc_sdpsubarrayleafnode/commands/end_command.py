"""
End command class for SdpSubarrayLeafNode.
"""

import threading
from logging import Logger
from typing import Callable, Optional

from ska_tango_base.commands import ResultCode
from ska_tango_base.executor import TaskStatus

from ska_tmc_sdpsubarrayleafnode.commands.abstract_command import SdpSLNCommand


class End(SdpSLNCommand):
    """
    A class for SdpSubarrayLeafNode's End() command.

    Invokes End command on SdpSubarray to end the current Scheduling Block.

    """

    def end(
        self,
        logger: Logger,
        task_callback: Callable = None,
        # pylint: disable=unused-argument
        task_abort_event: Optional[threading.Event] = None,
    ) -> None:
        """This is a long running method for End command, it
        executes do hook, invokes End command on SdpSubarray.

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
            "End command invoked on: %s: Result: %s, %s",
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
        Method to invoke End command on SdpSubarray.

        :param argin: None

        return:
            None

        """
        return_code, message = self.init_adapter()
        if return_code == ResultCode.FAILED:
            return return_code, message
        result, message = self.call_adapter_method(
            "SdpSubarray", self.sdp_subarray_adapter, "End"
        )
        return result, message
