"""
End command class for SdpSubarrayLeafNode.
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


class End(SdpSLNCommand):
    """
    A class for SdpSubarrayLeafNode's End() command.

    Invokes End command on SdpSubarray to end the current Scheduling Block.

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
        self.component_manager.command_in_progress = "End"

    @timeout_tracker
    @error_propagation_tracker("get_obs_state", [ObsState.IDLE])
    def end(
        self,
    ) -> Tuple[ResultCode, str]:
        """This is a long running method for End command, it
        executes do hook, invokes End command on SdpSubarray.
        """
        return self.do()

    # pylint: disable=arguments-differ
    def do(self) -> Tuple[ResultCode, str]:
        """
        Method to invoke End command on SdpSubarray.

        :param argin: None

        return:
            None

        """
        return_code, message = self.init_adapter()
        if return_code == ResultCode.FAILED:
            return return_code, message
        try:
            self.sdp_subarray_adapter.End()
        except Exception as exception:
            self.logger.exception(
                "Command End "
                + f"invocation failed with exception: {exception}"
            )
            return (
                ResultCode.FAILED,
                f"The invocation of the End"
                " command is failed on SDP Subarray "
                "Device "
                f"{self.sdp_subarray_adapter.dev_name} "
                "Reason: Error in invoking "
                "End command on SDP Subarray"
                ".The command has NOT been executed. "
                "This device will continue with normal operation.",
            )
        return (
            ResultCode.OK,
            "Command Completed",
        )
