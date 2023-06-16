"""
Disable command class for SDPMasterLeafNode.
"""

import threading
from typing import Callable, Optional

from ska_tango_base.commands import ResultCode
from ska_tango_base.executor import TaskStatus

from ska_tmc_sdpmasterleafnode.commands.abstract_command import SdpMLNCommand


class Disable(SdpMLNCommand):
    """
    A class for SdpMasterLeafNode's Disable() command.

    Disable command on SdpMasterLeafNode invokes disable command on
    Sdp Master device.

    """

    # pylint: disable=unused-argument
    def disable(
        self,
        logger,
        task_callback: Callable = None,
        task_abort_event: Optional[threading.Event] = None,
    ) -> None:
        """A method to invoke the Disable command.
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
                "The Disable command is invoked successfully on %s",
                self.sdp_master_adapter.dev_name,
            )
            task_callback(
                status=TaskStatus.COMPLETED,
                result=ResultCode.OK,
            )

    def do(self, argin=None):
        """
        Method to invoke Disable command on Sdp Master.

        """
        ret_code, message = self.init_adapter()
        if ret_code == ResultCode.FAILED:
            return ret_code, message
        result = self.call_adapter_method(
            "Sdp Master", self.sdp_master_adapter, "Disable"
        )
        return result
