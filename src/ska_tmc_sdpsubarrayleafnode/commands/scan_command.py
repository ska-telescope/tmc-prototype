"""
Scan command class for SdpSubarrayLeafNode.
"""
import json
import threading
from json import JSONDecodeError
from logging import Logger
from typing import Callable, Optional

from ska_tango_base.commands import ResultCode
from ska_tango_base.executor import TaskStatus
from tango import DevFailed

from ska_tmc_sdpsubarrayleafnode.commands.abstract_command import SdpSLNCommand


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
        task_callback: Callable = None,
        # pylint: disable=unused-argument
        task_abort_event: Optional[threading.Event] = None,
    ) -> None:
        """This is a long running method for Scan command, it
        executes do hook, invokes Scan command on SdpSubarray.

        :param logger: logger
        :type logger: logging.Logger
        :param task_callback: Update task state, defaults to None
        :type task_callback: Callable, optional
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
        task_callback(
            status=TaskStatus.COMPLETED,
            result=result_code,
            exception=message,
        )

    def do(self, argin=None):
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
        except JSONDecodeError as e:
            log_msg = (
                "Execution of Scan command is failed."
                + "Reason: JSON parsing failed with exception: {}".format(e)
                + "The command is not executed successfully."
                + "The device will continue with normal operation"
            )
            self.logger.exception(log_msg)
            return self.component_manager.generate_command_result(
                ResultCode.FAILED,
                (
                    """Exception occurred while parsing the JSON.
                    Please check the logs for details."""
                ),
            )

        log_msg = (
            f"Invoking Scan command on:{self.sdp_subarray_adapter.dev_name}"
        )
        self.logger.info(log_msg)

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
            log_msg = (
                "Input JSON for Scan command for SDP subarray"
                "{}: {} ".format(
                    self.sdp_subarray_adapter.dev_name, json_argument
                )
            )
            self.logger.debug(log_msg)
            self.sdp_subarray_adapter.Scan(json.dumps(json_argument))
        except (AttributeError, ValueError, TypeError, DevFailed) as e:
            self.logger.exception("Command invocation failed: %s", e)
            return self.component_manager.generate_command_result(
                ResultCode.FAILED,
                "The invocation of the Scan command is failed on Sdp"
                + "Subarray Device {}".format(
                    self.sdp_subarray_adapter.dev_name
                )
                + "Reason: Error in calling the Scan command on Sdp Subarray."
                + "The command has NOT been executed."
                + "This device will continue with normal operation."
                "",
            )
        log_msg = "Scan command successfully invoked on:" + "{}".format(
            self.sdp_subarray_adapter.dev_name
        )
        self.logger.info(log_msg)
        return (ResultCode.OK, "")
