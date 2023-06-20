"""
Off command class for SDPMasterLeafNode.
"""
import threading
from logging import Logger
from typing import Callable, Optional

from ska_tango_base.commands import ResultCode
from ska_tango_base.executor import TaskStatus

from ska_tmc_sdpmasterleafnode.commands.abstract_command import SdpMLNCommand


class Off(SdpMLNCommand):
    """
    A class for SdpMasterLeafNode's Off() command.

    Off command on SdpMasterLeafNode enables the telescope to perform
    further operations and observations.
    It Invokes Off command on Sdp Master device.

    """

    def off(
        self,
        logger: Logger,
        task_callback: Callable = None,
        # pylint: disable= unused-argument
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
        exception = ""
        return_code, message = self.do()

        logger.info(
            "Off command invoked on: %s: Result: %s, %s",
            self.sdp_master_adapter.dev_name,
            return_code,
            message,
        )
        if return_code == ResultCode.FAILED:
            exception = message
            task_callback(
                status=TaskStatus.COMPLETED,
                result=return_code,
                exception=exception,
            )

        else:
            logger.info(
                "The Off command is invoked successfully on %s",
                self.sdp_master_adapter.dev_name,
            )
            task_callback(
                status=TaskStatus.COMPLETED,
                result=return_code,
            )

    def do(self, argin=None):
        """
        Method to invoke Off command on Sdp Master.

        """
        ret_code, message = self.init_adapter()
        if ret_code == ResultCode.FAILED:
            return ret_code, message
        result, message = self.call_adapter_method(
            "Sdp Master", self.sdp_master_adapter, "Off"
        )
        return result, message
