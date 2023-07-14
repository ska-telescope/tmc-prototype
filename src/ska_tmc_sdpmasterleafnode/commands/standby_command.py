"""
Standby command class for SdpMaster Leaf Node
"""
import threading
from logging import Logger
from typing import Callable, Optional

from ska_tango_base.commands import ResultCode
from ska_tango_base.executor import TaskStatus

from ska_tmc_sdpmasterleafnode.commands.abstract_command import SdpMLNCommand


class Standby(SdpMLNCommand):
    """
    A class for SDP MasterLeafNode's Standby() command.

    Standby command on SDP MasterLeafNode invokes Standby command on
    SDP Master device.
    """

    # pylint: disable=unused-argument
    def standby(
        self,
        logger: Logger,
        task_callback: Callable = None,
        task_abort_event: Optional[threading.Event] = None,
    ) -> None:
        """A method to invoke the Standby command.
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
        result_code, message = self.do()

        logger.info(
            "Standby command invoked on: %s: Result: %s, %s",
            self.sdp_master_adapter.dev_name,
            result_code,
            message,
        )
        if result_code == ResultCode.FAILED:
            exception = message
            task_callback(
                status=TaskStatus.COMPLETED,
                result=result_code,
                exception=exception,
            )

        else:
            logger.info(
                "The Standby command is invoked successfully on %s",
                self.sdp_master_adapter.dev_name,
            )
            task_callback(
                status=TaskStatus.COMPLETED,
                result=result_code,
            )

    def do(self, argin=None):
        """
        Method to invoke Standby command on Sdp Master.

        """
        result_code, message = self.init_adapter()
        if result_code == ResultCode.FAILED:
            return result_code, message
        try:
            self.sdp_master_adapter.Standby()
        except Exception as e:
            self.logger.exception(f"Command invocation failed: {e}")
            return (
                ResultCode.FAILED,
                f"The invocation of the Standby"
                " command failed on SDP master "
                "Device "
                f"{self.sdp_master_adapter.dev_name} "
                "Reason: Error in invoking "
                "Standby command on SDP master"
                ".The command has NOT been executed. "
                "This device will continue with normal operation.",
            )
        return ResultCode.OK, ""
