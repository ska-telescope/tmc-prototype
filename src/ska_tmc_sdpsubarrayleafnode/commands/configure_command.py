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
    A class for SdpSubarrayLeafNode's Configure() command.

    Configures the SDP Subarray device by providing the SDP PB
    configuration needed to execute the receive workflow

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
        if result_code == ResultCode.FAILED:
            exception = message
            task_callback(
                status=TaskStatus.COMPLETED,
                result=ResultCode.FAILED,
                exception=exception,
            )
        else:
            task_callback(
                status=TaskStatus.COMPLETED,
                result=ResultCode.OK,
            )

    def do(self, argin=None):
        """
        Method to invoke Configure command on SDP Subarray. \

        :param argin: The string in JSON format. \
        The JSON contains following values: \

        Example: \
            { \
            "interface": "https://schema.skao.int/ska-sdp-configure/0.3", \
            "scan_type": "science_A" \
            } \

        return: \
            None
        """
        ret_code, message = self.init_adapter()
        if ret_code == ResultCode.FAILED:
            return ret_code, message
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
                "interface key is not present in the input json argument.",
            )

        if "scan_type" not in json_argument:
            return self.component_manager.generate_command_result(
                ResultCode.FAILED,
                "scan_type key is not present in the input json argument.",
            )

        if json_argument["scan_type"] == "":
            return self.component_manager.generate_command_result(
                ResultCode.FAILED,
                "scan_type is not present in the input json argument.",
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
            self.logger.exception("Command invocation failed: %s", e)
            return self.component_manager.generate_command_result(
                ResultCode.FAILED,
                "The invocation of the Configure command is failed on"
                + "Sdp Subarray Device {}".format(
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
