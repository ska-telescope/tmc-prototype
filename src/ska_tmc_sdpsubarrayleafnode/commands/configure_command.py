# flake8: noqa:E501
"""
Configure command class for SdpSubarrayLeafNode.
"""
from __future__ import annotations

import json
import logging
import threading
import time
from json import JSONDecodeError
from typing import TYPE_CHECKING, Callable, Tuple

from ska_ser_logging import configure_logging
from ska_tango_base.base import TaskCallbackType
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsState
from ska_tango_base.executor import TaskStatus
from ska_tmc_common.timeout_callback import TimeoutCallback

from ska_tmc_sdpsubarrayleafnode.commands.sdp_sln_command import SdpSLNCommand

configure_logging()
LOGGER = logging.getLogger(__name__)


if TYPE_CHECKING:
    from ..manager.component_manager import SdpSLNComponentManager


class Configure(SdpSLNCommand):
    """
    This class implements the Configure command for SdpSubarray.

    It provides methods to configure the SdpSubarray device and
    handle the execution
    of the Configure command.
    """

    def __init__(
        self,
        component_manager: SdpSLNComponentManager,
        logger: logging.Logger = LOGGER,
    ) -> None:
        super().__init__(component_manager, logger)
        self.component_manager = component_manager
        self.timeout_id: str = f"{time.time()}_{__class__.__name__}"
        self.timeout_callback: Callable = TimeoutCallback(
            self.timeout_id, self.logger
        )

    def configure(
        self,
        argin: str,
        task_callback: TaskCallbackType,
        task_abort_event: threading.Event,
    ) -> None:
        """This is a long running method for Configure command, it
        executes do hook, invokes Configure command on SdpSubarray.

        :param task_callback: Update task state, defaults to None
        :type task_callback: TaskCallbackType
        :param task_abort_event: Check for abort, defaults to None
        :type task_abort_event: Event
        """
        self.component_manager.abort_event = task_abort_event
        self.component_manager.command_in_progress = "Configure"
        self.task_callback = task_callback
        task_callback(status=TaskStatus.IN_PROGRESS)
        self.component_manager.start_timer(
            self.timeout_id,
            self.component_manager.command_timeout,
            self.timeout_callback,
        )
        result_code, message = self.do(argin)

        if result_code == ResultCode.FAILED:
            self.update_task_status(
                result=(result_code, message), exception=message
            )
            self.component_manager.stop_timer()
        else:
            self.start_tracker_thread(
                state_function="get_obs_state",
                expected_state=[ObsState.READY],
                abort_event=task_abort_event,
                timeout_id=self.timeout_id,
                timeout_callback=self.timeout_callback,
                command_id=self.component_manager.configure_id,
                lrcr_callback=(
                    self.component_manager.long_running_result_callback
                ),
            )

    def do(self, argin: str = "") -> Tuple[ResultCode, str]:
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
        except JSONDecodeError as json_error:
            log_msg = (
                "Execution of Configure command is failed."
                + "Reason: JSON parsing failed with exception: {}".format(
                    json_error
                )
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

        self.logger.info(
            "Invoking Configure command on:"
            "{}".format(self.sdp_subarray_adapter.dev_name)
        )
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
            self.sdp_subarray_adapter.Configure(
                json.dumps(json_argument), self.component_manager.cmd_ended_cb
            )

        except Exception as exception:
            self.logger.exception(
                "Configure command invocation failed: %s", exception
            )
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
        self.logger.info(
            "Configure command successfully invoked on:"
            + "{}".format(self.sdp_subarray_adapter.dev_name)
        )
        return (
            ResultCode.OK,
            "Command Completed",
        )
