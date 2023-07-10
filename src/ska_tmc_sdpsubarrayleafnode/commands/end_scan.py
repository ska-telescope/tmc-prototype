"""
EndScan command class for SDPSubarrayLeafNode.
"""
import threading
from logging import Logger
from typing import Callable, Optional

from ska_tango_base.commands import ResultCode
from ska_tango_base.executor import TaskStatus

from ska_tmc_sdpsubarrayleafnode.commands.abstract_command import SdpSLNCommand


class EndScan(SdpSLNCommand):
    """
    A class for SdpSubarrayLeafNode's EndScan() command.

    It invokes EndScan command on Sdp Subarray.
    This command is allowed when Sdp Subarray is in SCANNING state.
    """

    def end_scan(
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
        result_code, message = self.do()
        logger.info(
            "EndScan command invoked on: %s: Result: %s, %s",
            self.sdp_subarray_adapter.dev_name,
            result_code,
            message,
        )

        task_callback(
            status=TaskStatus.COMPLETED,
            result=result_code,
            exception=message,
        )

    def do(self, argin=None):
        """
        Method to invoke EndScan command on SDP Subarray.

        """
        return_code, message = self.init_adapter()
        if return_code == ResultCode.FAILED:
            return return_code, message
        result, message = self.call_adapter_method(
            "SdpSubarray", self.sdp_subarray_adapter, "EndScan"
        )
        return result, message
