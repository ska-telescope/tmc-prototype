"""
On command class for SdpMasterLeafNode.

"""
import threading
from logging import Logger
from typing import Any, Optional, Tuple

from ska_tango_base.base import TaskCallbackType
from ska_tango_base.commands import ResultCode
from ska_tango_base.executor import TaskStatus

from ska_tmc_sdpmasterleafnode.commands.sdp_mln_command import SdpMLNCommand


class On(SdpMLNCommand):
    """
    A class for SdpMasterLeafNode's On() command.

    On command on SdpmasterLeafNode enables the telescope to perform
    further operations and observations.
    It Invokes On command on Sdp Master device.

    """

    def on(
        self,
        logger: Logger,
        task_callback: TaskCallbackType,
        # pylint: disable= unused-argument
        task_abort_event: Optional[threading.Event] = None,
    ) -> None:
        """A method to invoke the On command.
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
            "On command invoked on: %s: Result: %s, %s",
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
                "The On command is invoked successfully on %s",
                self.sdp_master_adapter.dev_name,
            )
            task_callback(
                status=TaskStatus.COMPLETED,
                result=result_code,
            )

    def do(self, argin: Optional[Any] = None) -> Tuple[ResultCode, str]:
        """
        Method to invoke On command on Sdp Master.

        """

        result_code, message = self.init_adapter()
        if result_code == ResultCode.FAILED:
            return result_code, message
        try:
            self.sdp_master_adapter.On()

        except Exception as exception:
            self.logger.exception(f"Command invocation failed: {exception}")
            return (
                ResultCode.FAILED,
                f"The invocation of the On"
                " command failed on SDP master "
                "Device "
                f"{self.sdp_master_adapter.dev_name} "
                "Reason: Error in invoking "
                "On command on SDP master"
                ".The command has NOT been executed. "
                "This device will continue with normal operation.",
            )
        return (ResultCode.OK, "On command completed")
