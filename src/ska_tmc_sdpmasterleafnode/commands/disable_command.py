"""
Disable command class for SdpMasterLeafNode.
"""

import threading
from logging import Logger
from typing import Any, Optional, Tuple

from ska_tango_base.base import TaskCallbackType
from ska_tango_base.commands import ResultCode
from ska_tango_base.executor import TaskStatus

from ska_tmc_sdpmasterleafnode.commands.sdp_mln_command import SdpMLNCommand


class Disable(SdpMLNCommand):
    """
    A class for SdpMasterLeafNode's Disable() command.

    Disable command on SdpMasterLeafNode invokes disable command on
    Sdp Master device.

    """

    # pylint: disable=unused-argument
    def disable(
        self,
        logger: Logger,
        task_callback: TaskCallbackType,
        task_abort_event: Optional[threading.Event] = None,
    ) -> None:
        """A method to invoke the Disable command.
        It sets the task_callback status according to command progress.

        :param logger: logger
        :type logger: logging.Logger
        :param task_callback: Update task state, defaults to None
        :type task_callback: TaskCallbackType
        :param task_abort_event: Check for abort, defaults to None
        :type task_abort_event: Event, optional
        """

        task_callback(status=TaskStatus.IN_PROGRESS)
        exception = ""
        result_code, message = self.do()

        logger.info(
            "Disable command invoked on: %s: Result: %s, %s",
            self.sdp_master_adapter.dev_name,
            result_code,
            message,
        )
        if result_code == ResultCode.FAILED:
            exception = message
            task_callback(
                status=TaskStatus.COMPLETED,
                result=(result_code, message),
                exception=exception,
            )

        else:
            logger.info(
                "The Disable command is invoked successfully on %s",
                self.sdp_master_adapter.dev_name,
            )
            task_callback(
                status=TaskStatus.COMPLETED,
                result=(result_code, message),
            )

    def do(self, argin: Optional[Any] = None) -> Tuple[ResultCode, str]:
        """
        Method to invoke Disable command on Sdp Master.

        """
        result_code, message = self.init_adapter()
        if result_code == ResultCode.FAILED:
            return result_code, message
        try:
            self.sdp_master_adapter.Disable()
        except Exception as exception:
            message = (
                "Disable Command invocation"
                + " failed on device: %s."
                + " with exception: %s"
            ) % (self.sdp_master_adapter.dev_name, exception)
            self.logger.exception(message)
            return (ResultCode.FAILED, message)
        return (ResultCode.OK, "Command Completed")
