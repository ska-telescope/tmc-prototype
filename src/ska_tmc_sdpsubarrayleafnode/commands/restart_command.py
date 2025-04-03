"""Restart command class for Sdp Subarray."""

import threading
from logging import Logger
from typing import Optional, Tuple

from ska_tango_base.base import TaskCallbackType
from ska_tango_base.commands import ResultCode
from ska_tango_base.executor import TaskStatus

from ska_tmc_sdpsubarrayleafnode.commands.sdp_sln_command import SdpSLNCommand


class Restart(SdpSLNCommand):
    """
    A class for Sdp Subarray Restart command.
    Restarts the Sdp Subarray device.
    """

    # pylint: disable=unused-argument
    def restart(
        self,
        logger: Logger,
        task_callback: TaskCallbackType,
        task_abort_event: Optional[threading.Event] = None,
    ) -> None:
        """This is a long-running method for a Restart command, it
        executes do hook
        :param logger: logger
        :type logger: logging.Logger
        :param task_callback: Update task state, defaults to None
        :type task_callback: TaskCallbackType
        :param task_abort_event: Check for abort, defaults to None
        :type task_abort_event: Event, optional
        """
        # Indicate that the task has started
        task_callback(status=TaskStatus.IN_PROGRESS)
        result_code, message = self.do()
        logger.info(
            "Restart command invoked on: %s: Result: %s, %s",
            self.sdp_subarray_adapter.dev_name,
            result_code,
            message,
        )
        if result_code == ResultCode.FAILED:
            task_callback(
                status=TaskStatus.COMPLETED,
                result=(result_code, message),
                exception=message,
            )
        else:
            task_callback(
                status=TaskStatus.COMPLETED,
                result=(result_code, message),
            )

    # pylint: disable=arguments-differ
    def do(self) -> Tuple[ResultCode, str]:
        """
        Method to invoke Restart command on Sdp Subarray.

        :param  None:

        Note: Enter the json string without spaces as a input.

        :return: (ResultCode, message)

        """
        result_code, message = self.init_adapter()
        if result_code == ResultCode.FAILED:
            return result_code, message

        try:
            self.logger.info(
                "Invoking Restart command on Sdp Subarray: %s",
                self.sdp_subarray_adapter.dev_name,
            )
            self.sdp_subarray_adapter.Restart()
        except Exception as exception:
            self.logger.exception(
                "Failed to invoke Restart Command "
                + "on device: {}".format(self.sdp_subarray_adapter.dev_name)
                + " with exception: %s",
                exception,
            )

            return (
                ResultCode.FAILED,
                "Execution of Restart command is failed."
                + "Reason: Error in invoking Restart\
                 command on Sdp Subarray - "
                + f"{self.sdp_subarray_adapter.dev_name}: {exception}",
            )

        self.logger.info(
            "Restart command successfully invoked on Device : %s",
            self.sdp_subarray_adapter.dev_name,
        )
        return (ResultCode.OK, "Command Completed")
