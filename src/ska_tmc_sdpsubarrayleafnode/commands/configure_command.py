"""
Configure command class for SdpSubarrayLeafNode.
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


class Configure(SdpSLNCommand):
    """
    This class implements the Configure command for SdpSubarray.

    It provides methods to configure the SdpSubarray device and
    handle the execution
    of the Configure command.
    """

    def configure(
        self,
        argin: str,
        logger: Logger,
        task_callback: Callable = None,
        # pylint: disable=unused-argument
        task_abort_event: Optional[threading.Event] = None,
    ) -> None:
        """This is a long running method for Configure command, it
        executes do hook, invokes Configure command on SdpSubarray.

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
            "Configure command invoked on: %s: Result: %s, %s",
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
        Method to invoke Configure command on SDP Subarray. \

        :param argin: The string in JSON format. \
        The JSON contains following values: \

        Example: \
            { \
            "interface": "https://schema.skao.int/ska-sdp-configure/0.4", \
            "scan_type": "science_A" \
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
                "Execution of Configure command is failed."
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

        if "interface" not in json_argument:
            return self.component_manager.generate_command_result(
                ResultCode.FAILED,
                "Missing interface key",
            )

        if "scan_type" not in json_argument:
            return self.component_manager.generate_command_result(
                ResultCode.FAILED,
                "Missing scan_type key",
            )

        if json_argument["scan_type"] == "":
            return self.component_manager.generate_command_result(
                ResultCode.FAILED,
                "Missing scan_type value.",
            )

        log_msg = "Invoking Configure command on:"
        "{}".format(self.sdp_subarray_adapter.dev_name)
        self.logger.info(log_msg)
        try:
            json_argument[
                "interface"
            ] = "https://schema.skao.int/ska-sdp-configure/0.3"
            log_msg = (
                "Input JSON for Configure command for SDP subarray"
                + "{}: {}".format(
                    self.sdp_subarray_adapter.dev_name, json_argument
                )
            )
            self.logger.debug(log_msg)
            self.sdp_subarray_adapter.Configure(json.dumps(json_argument))

        except (AttributeError, ValueError, TypeError, DevFailed) as e:
            self.logger.exception("Configure command invocation failed: %s", e)
            return self.component_manager.generate_command_result(
                ResultCode.FAILED,
                "The Sdp Subarray Device has failed to invoke"
                + "the Configure command {}".format(
                    self.sdp_subarray_adapter.dev_name
                )
                + "Reason: Error in invoking the Configure command on"
                "Sdp Subarray."
                + "The command has NOT been executed."
                + "This device will continue with normal operation.",
            )
        log_msg = "Configure command successfully invoked on:" + "{}".format(
            self.sdp_subarray_adapter.dev_name
        )
        self.logger.info(log_msg)
        return (ResultCode.OK, "")
