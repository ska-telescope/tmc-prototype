"""
Scan command class for SdpSubarrayLeafNode.
"""
from __future__ import annotations

import json
import logging
import time
from json import JSONDecodeError
from typing import TYPE_CHECKING, Callable, Tuple

from ska_ser_logging import configure_logging
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsState
from ska_tmc_common import TimeoutCallback
from ska_tmc_common.v1.error_propagation_tracker import (
    error_propagation_tracker,
)
from ska_tmc_common.v1.timeout_tracker import timeout_tracker

from ska_tmc_sdpsubarrayleafnode.commands.sdp_sln_command import SdpSLNCommand

configure_logging()
LOGGER = logging.getLogger(__name__)


if TYPE_CHECKING:
    from ..manager.component_manager import SdpSLNComponentManager


class Scan(SdpSLNCommand):
    """
    This class implements the Scan command for SdpSubarray.

    It provides methods to Scan the SdpSubarray device and
    handle the execution
    of the Scan command.
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
        self.component_manager.command_in_progress = "Scan"

    @timeout_tracker
    @error_propagation_tracker("get_obs_state", [ObsState.SCANNING])
    def scan(
        self,
        argin: str,
    ) -> Tuple[ResultCode, str]:
        """This is a long running method for Scan command, it
        executes do hook, invokes Scan command on SdpSubarray.

        :param argin : Input json string for Configure Command.
        :type argin  : str
        """
        return self.do(argin)

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
