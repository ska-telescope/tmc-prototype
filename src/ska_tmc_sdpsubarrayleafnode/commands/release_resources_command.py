"""
ReleaseAllResources command class for SdpSubarrayLeafNode.
"""

from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING, Tuple

from ska_ser_logging import configure_logging
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsState
from ska_tmc_common import TimeKeeper, TimeoutCallback
from ska_tmc_common.v1.error_propagation_tracker import (
    error_propagation_tracker,
)
from ska_tmc_common.v1.timeout_tracker import timeout_tracker

from ska_tmc_sdpsubarrayleafnode.commands.sdp_sln_command import SdpSLNCommand

configure_logging()
LOGGER = logging.getLogger(__name__)
if TYPE_CHECKING:
    from ..manager.component_manager import SdpSLNComponentManager


class ReleaseAllResources(SdpSLNCommand):
    """
    A class for SdpSubarayLeafNode's ReleaseAllResources() command.

    Releases all the resources of given SDP Subarray Leaf Node.
    It accepts the subarray id, releaseALL flag and receptorIDList in
    JSON string format.
    """

    def __init__(
        self,
        component_manager: SdpSLNComponentManager,
        logger: logging.Logger = LOGGER,
    ) -> None:
        super().__init__(component_manager, logger)
        self.timeout_id = f"{time.time()}_{__class__.__name__}"
        self.timeout_callback = TimeoutCallback(self.timeout_id, self.logger)
        self.timekeeper = TimeKeeper(
            self.component_manager.command_timeout, logger
        )
        self.component_manager = component_manager
        self.component_manager.command_in_progress = "ReleaseAllResources"

    @timeout_tracker
    @error_propagation_tracker("get_obs_state", [ObsState.EMPTY])
    def release_resources(
        self,
    ) -> Tuple[ResultCode, str]:
        """This is a long running method for ReleaseAllResources command, it
        executes do hook, invokes ReleaseAllResources command on SdpSubarray.
        """

        return self.do()

    # pylint: disable=arguments-differ
    def do(self) -> Tuple[ResultCode, str]:
        """
        Method to invoke ReleaseAllResources command on SDP Subarray.

        :param argin: None.

        return:
            None
        """
        result_code, message = self.init_adapter()
        if result_code == ResultCode.FAILED:
            return result_code, message
        try:
            self.logger.info(
                "Command Id : %s | "
                + "Invoking ReleaseAllResources command on %s",
                self.component_manager.command_id,
                self.sdp_subarray_adapter.dev_name,
            )

            self.sdp_subarray_adapter.ReleaseAllResources(
                self.component_manager.cmd_ended_cb
            )
        except Exception as exception:
            self.logger.exception(
                "Command Id : %s | "
                + "Failed to invoke ReleaseResource Command "
                + "on device: {}".format(self.sdp_subarray_adapter.dev_name)
                + " with exception: %s",
                self.component_manager.command_id,
                exception,
            )

            return self.component_manager.generate_command_result(
                ResultCode.FAILED,
                "The invocation of the ReleaseAllResources command is failed"
                + "on {}".format(self.sdp_subarray_adapter.dev_name)
                + "Reason: Error in invoking the ReleaseAllResourcescommand"
                "on Sdp"
                + "Subarray. The command has NOT been executed."
                + "This device will continue with normal operation.",
            )

        self.logger.info(
            "Command Id : %s | "
            "ReleaseAllResources command successfully invoked on: %s",
            self.component_manager.command_id,
            self.sdp_subarray_adapter.dev_name,
        )

        return (
            ResultCode.OK,
            "Command Completed",
        )
