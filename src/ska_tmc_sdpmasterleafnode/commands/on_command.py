"""
On command class for SDPMasterLeafNode.

"""
import threading
from logging import Logger
from typing import Callable, Optional

from ska_tango_base.commands import ResultCode
from ska_tango_base.executor import TaskStatus

from ska_tmc_sdpmasterleafnode.commands.abstract_command import SdpMLNCommand


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
        task_callback: Callable = None,
        # pylint: disable= unused-argument
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
        return_code, message = self.do()
        logger.info(message)
        if return_code == ResultCode.FAILED:
            task_callback(
                status=TaskStatus.COMPLETED,
                result=return_code,
                exception=message,
            )
        else:
            logger.info(
                "The On command is invoked successfully on %s",
                self.sdp_master_adapter.dev_name,
            )
            task_callback(
                status=TaskStatus.COMPLETED,
                result=return_code,
            )

    def do(self, argin=None):
        """
        Method to invoke On command on Sdp Master.

        """

        return_code, message = self.init_adapter()
        if return_code == ResultCode.FAILED:
            return return_code, message
        result, msg = self.call_adapter_method(
            "Sdp Master", self.sdp_master_adapter, "On"
        )
        return result, msg
