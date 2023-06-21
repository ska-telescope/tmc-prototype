"""
Off command class for SdpSubarrayLeafNode.
"""
import threading
from typing import Callable, Optional

from ska_tango_base.commands import ResultCode
from ska_tango_base.executor import TaskStatus

from ska_tmc_sdpsubarrayleafnode.commands.abstract_command import SdpSLNCommand


class Off(SdpSLNCommand):
    """
    A class for SdpSubarrayLeafNode's Off() command.

    This command turns off SDP Subarray device.
    """

    # pylint: disable=unused-argument
    def off(
        self,
        logger,
        task_callback: Callable = None,
        task_abort_event: Optional[threading.Event] = None,
    ) -> None:
        """A method to invoke the Off command.
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
        logger.info(message)
        if result_code == ResultCode.FAILED:
            task_callback(
                status=TaskStatus.COMPLETED,
                result=ResultCode.FAILED,
                exception=message,
            )
            logger.info(
                "The Off command is failed on %s",
                self.sdp_subarray_adapter.dev_name,
            )
        else:
            logger.info(
                "The Off command is invoked successfully on %s",
                self.sdp_subarray_adapter.dev_name,
            )
            task_callback(
                status=TaskStatus.COMPLETED,
                result=ResultCode.OK,
            )

    # pylint: enable=unused-argument

    def do(self, argin=None):
        """
        Method to invoke Off command on SdpSubarray.

        """
        return_code, message = self.init_adapter()
        if return_code == ResultCode.FAILED:
            return return_code, message

        result, message = self.call_adapter_method(
            "SDP Subarray", self.sdp_subarray_adapter, "Off"
        )
        return result, message
