# flake8: noqa:E501
"""AssignResouces command class for SDPSubarrayLeafNode."""
from __future__ import annotations

import json
import logging
import time
from json import JSONDecodeError
from typing import TYPE_CHECKING, Callable, Optional, Tuple

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


class AssignResources(SdpSLNCommand):
    """
    A class for SdpSubarayLeafNode's AssignResources() command.
    Assigns resources to given SDP Subarray.
    """

    def __init__(
        self,
        component_manager: SdpSLNComponentManager,
        logger: logging.Logger = LOGGER,
    ):
        super().__init__(component_manager, logger)
        self.component_manager = component_manager
        self.timeout_id: str = f"{time.time()}_{__class__.__name__}"
        self.timeout_callback: Optional[
            Callable[[str, logging.Logger], None]
        ] = TimeoutCallback(self.timeout_id, self.logger)
        self.timekeeper = TimeKeeper(
            self.component_manager.command_timeout, logger
        )
        self.component_manager.command_in_progress = "AssignResources"

    @timeout_tracker
    @error_propagation_tracker(
        "get_obs_state", [ObsState.RESOURCING, ObsState.IDLE]
    )
    def assign_resources(
        self,
        argin: str,
    ) -> Tuple[ResultCode, str]:
        """
        This is a long running method for AssignResources command, it
        executes do hook, invokes AssignResources command on Sdp Subarray.

        :param argin : Input json string for AssignResources Command.
        :type argin: str
        """

        return self.do(argin)

    def do(self, argin: str = "") -> Tuple[ResultCode, str]:
        """
        Method to invoke AssignResources command on SDP Subarray.

        :param argin: The string in JSON format. The JSON contains
            following values:

            eb_id and maximum length of the SBI:
            Mandatory JSON object consisting of

            eb_id :
                String

            max_length:
                Float

        scan_types:
            Consist of Scan type id name

            scan_type:
                DevVarStringArray

        Processing blocks:
            Mandatory JSON object consisting of

                processing_blocks:
                    DevVarStringArray

        Example:
        "{"interface":"https://schema.skao.int/ska-sdp-assignres/0.4",
        "execution_block": {"eb_id": "eb-mvp01-20200325-00001",
        "max_length": 100,"context":{},"beams":[{"beam_id": "vis0",
        "function":"visibilities"},{"beam_id": "pss1","search_beam_id": 1,
        "function": "pulsar search"}, {"beam_id": "pss2","search_beam_id": 2,
        "function":"pulsar search"},{"beam_id": "pst1", "timing_beam_id": 1,
        "function": "pulsar timing"},{"beam_id":"pst2","timing_beam_id":2,
        "function": "pulsar timing"},{"beam_id": "vlbi1","vlbi_beam_id":1,
        "function": "vlbi"}], "channels": [{"channels_id":"vis_channels",
        "spectral_windows":[{"spectral_window_id": "fsp_1_channels",
        "count": 744,"start": 0,"stride": 2,"freq_min":350000000,"freq_max":
        368000000,"link_map": [[0,0],[200,1],[744,2],[944,3]]},
        {"spectral_window_id":"fsp_2_channels", "count": 744,"start": 2000,
        "stride": 1,"freq_min": 360000000,"freq_max":368000000,  "link_map":
        [[2000,4],[2200,5]]},{"spectral_window_id":"zoom_window_1",
        "count": 744,"start": 4000,"stride": 1,"freq_min": 360000000,
        "freq_max": 361000000,"link_map": [[4000,6],[4200,7]]}]},
        {"channels_id":"pulsar_channels","spectral_windows":
        [{"spectral_window_id": "pulsar_fsp_channels","count": 744,"start": 0,
        "freq_min": 350000000,"freq_max": 368000000}]}], "polarisations":
        [{"polarisations_id": "all","corr_type":["XX","XY","YY","YX"]}],
        "fields": [{"field_id": "field_a","phase_dir":{"ra":[123,0.1],
        "dec":[123,0.1],"reference_time": "...", "reference_frame": "ICRF3"},
        "pointing_fqdn":"low-tmc/telstate/0/pointing"}]}, "processing_blocks":
        [{"pb_id": "pb-mvp01-20200325-00001","sbi_ids":
        ["sbi-mvp01-20200325-00001"],"script":{},"parameters":{},"dependencies"
        :{}},{"pb_id":"pb-mvp01-20200325-00002","sbi_ids":
        ["sbi-mvp01-20200325-00002"],"script":{},"parameters":{},"dependencies"
        :{}},{"pb_id": "pb-mvp01-20200325-00003","sbi_ids":
        ["sbi-mvp01-20200325-00001","sbi-mvp01-20200325-00002"],
        "script":{},"parameters": {},"dependencies":{}}],
        "resources":{"csp_links":[1,2,3,4], "receptors":["FS4","FS8"],
        "receive_nodes":10}}

        Note: Enter input without spaces

        return:
            None
        """
        result_code, message = self.init_adapter()

        if result_code == ResultCode.FAILED:
            return result_code, message
        try:
            json_argument = json.loads(argin)
        except JSONDecodeError as json_error:
            log_msg = (
                "Failed to execute AssignResources command "
                + "Reason: JSON parsing failed with exception: {}".format(
                    json_error
                )
            )
            self.logger.exception(log_msg)
            return (
                ResultCode.FAILED,
                f"Exception occurred while parsing the JSON: {json_error}",
            )

        try:
            json_argument[
                "interface"
            ] = "https://schema.skao.int/ska-sdp-assignres/0.4"

            self.sdp_subarray_adapter.AssignResources(
                json.dumps(json_argument), self.component_manager.cmd_ended_cb
            )

        except Exception as exception:
            self.logger.exception(
                "Failed to invoke AssignResource Command "
                + "on device: {}".format(self.sdp_subarray_adapter.dev_name)
                + " with exception: %s",
                exception,
            )
            return self.component_manager.generate_command_result(
                ResultCode.FAILED,
                "The invocation of the AssignResources command is failed "
                + "on Sdp Subarray Device {} ".format(
                    self.sdp_subarray_adapter.dev_name
                )
                + "Reason: Error in calling the "
                + "AssignResources command on Sdp "
                + "Subarray ",
            )

        return (
            ResultCode.OK,
            "Command Completed",
        )
