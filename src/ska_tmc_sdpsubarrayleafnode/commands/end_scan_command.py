"""
EndScan command class for SDPSubarrayLeafNode.
"""
from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING, Tuple

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


class EndScan(SdpSLNCommand):
    """
    A class for SdpSubarrayLeafNode's EndScan() command.

    It invokes EndScan command on Sdp Subarray.
    This command is allowed when Sdp Subarray is in SCANNING obsState.
    """

    def __init__(
        self,
        component_manager: SdpSLNComponentManager,
        logger: logging.Logger = LOGGER,
    ) -> None:
        super().__init__(component_manager, logger)
        self.timeout_id = f"{time.time()}_{__class__.__name__}"
        self.timeout_callback = TimeoutCallback(self.timeout_id, self.logger)
        self.component_manager = component_manager
        self.component_manager.command_in_progress = "EndScan"

    @timeout_tracker
    @error_propagation_tracker("get_obs_state", [ObsState.READY])
    def end_scan(
        self,
    ) -> Tuple[ResultCode, str]:
        """
        This is a long running method for EndScan command, it
        executes do hook, invokes EndScan command on SdpSubarray.
        """
        return self.do()

    # pylint: disable=arguments-differ
    def do(self) -> Tuple[ResultCode, str]:
        """
        Method to invoke EndScan command on SDP Subarray.

        """
        return_code, message = self.init_adapter()
        if return_code == ResultCode.FAILED:
            return return_code, message
        try:
            self.sdp_subarray_adapter.EndScan()
        except Exception as exception:
            self.logger.exception(
                "Failed to invoke EndScan Command "
                + "on device: {}".format(self.sdp_subarray_adapter.dev_name)
                + " with exception: %s",
                exception,
            )
            return (
                ResultCode.FAILED,
                f"The invocation of the EndScan"
                " command is failed on SDP Subarray "
                "Device "
                f"{self.sdp_subarray_adapter.dev_name} "
                "Reason: Error in invoking "
                "EndScan command on SDP Subarray",
            )
        return (
            ResultCode.OK,
            "Command Completed",
        )
