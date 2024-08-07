"""
Scan command class for SdpSubarrayLeafNode.
"""
import json
import threading
from json import JSONDecodeError
from logging import Logger
from typing import Optional, Tuple

from ska_tango_base.base import TaskCallbackType
from ska_tango_base.commands import ResultCode
from ska_tango_base.executor import TaskStatus

from ska_tmc_sdpsubarrayleafnode.commands.sdp_sln_command import SdpSLNCommand


class Scan(SdpSLNCommand):
    """
    This class implements the Scan command for SdpSubarray.

    It provides methods to Scan the SdpSubarray device and
    handle the execution
    of the Scan command.
    """

    def scan(
        self,
        argin: str,
        logger: Logger,
        task_callback: TaskCallbackType,
        # pylint: disable=unused-argument
        task_abort_event: Optional[threading.Event] = None,
    ) -> None:
        """This is a long running method for Scan command, it
        executes do hook, invokes Scan command on SdpSubarray.

        :param logger: logger
        :type logger: logging.Logger
        :param task_callback: Update task state, defaults to None
        :type task_callback: TaskCallbackType
        :param task_abort_event: Check for abort, defaults to None
        :type task_abort_event: Event, optional
        """
        task_callback(status=TaskStatus.IN_PROGRESS)
        result_code, message = self.do(argin)
        logger.info(
            "Scan command invoked on: %s: Result: %s, %s",
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

    def do(self, argin: str = "") -> Tuple[ResultCode, str]:
        """
        Method to invoke Scan command on SDP Subarray. \

        :param argin: The string in JSON format. The JSON contains following \
        values: \

        Example: \
            { \
             "interface": "https://schema.skao.int/ska-sdp-scan/0.4", \
             "scan_id": 1 \
            } \

        return: \
            None
        """
        result_code, message = self.init_adapter()
        if result_code == ResultCode.FAILED:
            return result_code, message
        try:
            json_argument = json.loads(argin)
        except JSONDecodeError as json_error:
            self.logger.exception(
                "Execution of Scan command is failed. "
                "Reason: JSON parsing failed with exception: %s. "
                "The command is not executed successfully. "
                "The device will continue with normal operation.",
                json_error,
            )

            return self.component_manager.generate_command_result(
                ResultCode.FAILED,
                (
                    """Exception occurred while parsing the JSON.
                    Please check the logs for details."""
                ),
            )

        self.logger.info(
            "Invoking Scan command on: %s", self.sdp_subarray_adapter.dev_name
        )

        try:
            # As, SKA logtransaction is not utilised in scan command across
            # tmc devices.
            # Hence, Interface URL needs to be updated explicitly for SDP.
            # pylint: disable=fixme
            # TODO: Incorporate transaction id implementation for scan
            # command across TMC.
            json_argument[
                "interface"
            ] = "https://schema.skao.int/ska-sdp-scan/0.4"
            self.logger.debug(
                "Input JSON for Scan command for SDP subarray %s: %s",
                self.sdp_subarray_adapter.dev_name,
                json_argument,
            )
            self.sdp_subarray_adapter.Scan(json.dumps(json_argument))
        except Exception as exception:
            self.logger.exception(
                "Command Scan invocation failed with exception: %s", exception
            )
            return self.component_manager.generate_command_result(
                ResultCode.FAILED,
                "The invocation of the Scan command is failed on Sdp"
                + "Subarray Device {}".format(
                    self.sdp_subarray_adapter.dev_name
                )
                + "Reason: Error in calling the Scan command on Sdp Subarray."
                + "The command has NOT been executed."
                + "This device will continue with normal operation.",
            )
        self.logger.info(
            "Scan command successfully invoked on: %s",
            self.sdp_subarray_adapter.dev_name,
        )

        return (
            ResultCode.OK,
            "Command Completed",
        )
