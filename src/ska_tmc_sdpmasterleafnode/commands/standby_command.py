"""
Standby command class for SDP Master Leaf Node
"""
import threading
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
        logger,
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

        return_code, message = self.do()

        logger.info(message)
        if return_code == ResultCode.FAILED:
            task_callback(
                status=TaskStatus.COMPLETED,
                result=ResultCode.FAILED,
                exception=message,
            )
        else:
            logger.info(
                "The Standby command is invoked successfully on %s",
                self.sdp_master_adapter.dev_name,
            )
            task_callback(
                status=TaskStatus.COMPLETED,
                result=ResultCode.OK,
            )

    # pylint: enable=unused-argument

    def do(self, argin=None):
        """
        Method to invoke Standby command on SDP Master.
        """
        return_code, message = self.init_adapter()
        if return_code == ResultCode.FAILED:
            return return_code, message

        result, message = self.call_adapter_method(
            "SDP Master", self.sdp_master_adapter, "Standby"
        )
        return result, message
