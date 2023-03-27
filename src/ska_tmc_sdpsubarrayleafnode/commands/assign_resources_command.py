# flake8: noqa:E501
"""
AssignResouces command class for SDPSubarrayLeafNode.
"""
import json
from json import JSONDecodeError

from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsState
from ska_tmc_common.adapters import AdapterFactory
from ska_tmc_common.exceptions import InvalidObsStateError
from tango import DevFailed

from ska_tmc_sdpsubarrayleafnode.commands.abstract_command import SdpSLNCommand


class AssignResources(SdpSLNCommand):
    """
    A class for SdpSubarayLeafNode's AssignResources() command.

    Assigns resources to given SDP Subarray.
    """

    def __init__(
        self,
        target,
        op_state_model,
        adapter_factory=None,
        logger=None,
    ):
        super().__init__(target, logger)
        self.op_state_model = op_state_model
        self._adapter_factory = adapter_factory or AdapterFactory()

    def check_allowed(self):
        """
        Checks whether this command is allowed
        It checks that the device is in the right state
        to execute this command and that all the
        component needed for the operation are not unresponsive

        :return: True if this command is allowed

        :rtype: boolean

        """
        component_manager = self.target
        self.check_op_state("AssignResources")
        self.check_unresponsive()

        obs_state_val = component_manager.get_device().obs_state
        self.logger.info("sdp_subarray_obs_state: %s", obs_state_val)

        if obs_state_val not in [ObsState.IDLE, ObsState.EMPTY]:
            message = (
                "AssignResources command is not allowed in current"
                + "observation state on device"
                + "{}".format(component_manager._sdp_subarray_dev_name)
                + "Reason: The current observation state for observation is"
                + "{}".format(obs_state_val)
                + 'The "AssignResources" command has NOT been executed.'
                + "This device will continue with normal operation."
            )
            raise InvalidObsStateError(message)

        return True

    # pylint: disable=line-too-long
    def do(self, argin=None):
        """
        Method to invoke AssignResources command on SDP Subarray.

        :param argin: The string in JSON format. The JSON contains following values:

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
           "sdp":{"interface":"https://schema.skao.int/ska-sdp-assignres/0.4","execution_block": {"eb_id":
        "eb-mvp01-20200325-00001","max_length": 100,"context":{},"beams":[{"beam_id": "vis0",
        "function":"visibilities"},{"beam_id": "pss1","search_beam_id": 1,"function": "pulsar search"},
        {"beam_id": "pss2","search_beam_id": 2,"function":"pulsar search"},{"beam_id": "pst1",
        "timing_beam_id": 1,"function": "pulsar timing"},{"beam_id":"pst2","timing_beam_id":2,
        "function": "pulsar timing"},{"beam_id": "vlbi1","vlbi_beam_id":1,"function": "vlbi"}],
        "channels": [{"channels_id":"vis_channels","spectral_windows":[{"spectral_window_id":
        "fsp_1_channels","count": 744,"start": 0,"stride": 2,"freq_min": 350000000,"freq_max":
        368000000,"link_map": [[0,0],[200,1],[744,2],[944,3]]},{"spectral_window_id":"fsp_2_channels",
        "count": 744,"start": 2000,"stride": 1,"freq_min": 360000000,"freq_max":368000000,
        "link_map": [[2000,4],[2200,5]]},{"spectral_window_id": "zoom_window_1","count": 744,"start":
        4000,"stride": 1,"freq_min": 360000000,"freq_max": 361000000,"link_map": [[4000,6],[4200,7]]}]},
        {"channels_id":"pulsar_channels","spectral_windows":[{"spectral_window_id":
        "pulsar_fsp_channels","count": 744,"start": 0,"freq_min": 350000000,"freq_max": 368000000}]}],
        "polarisations": [{"polarisations_id": "all","corr_type":["XX","XY","YY","YX"]}],"fields":
        [{"field_id": "field_a","phase_dir":{"ra":[123,0.1],"dec":[123,0.1],"reference_time": "...",
        "reference_frame": "ICRF3"},"pointing_fqdn": "low-tmc/telstate/0/pointing"}]},
        "processing_blocks":[{"pb_id": "pb-mvp01-20200325-00001","sbi_ids":["sbi-mvp01-20200325-00001"],
        "script":{},"parameters":{},"dependencies":{}},{"pb_id": "pb-mvp01-20200325-00002","sbi_ids":
        ["sbi-mvp01-20200325-00002"],"script":{},"parameters":{},"dependencies":{}},{"pb_id":
        "pb-mvp01-20200325-00003","sbi_ids":["sbi-mvp01-20200325-00001","sbi-mvp01-20200325-00002"],
        "script":{},"parameters": {},"dependencies":{}}],"resources":{"csp_links":[1,2,3,4],
        "receptors":["FS4","FS8"],"receive_nodes":10}}}

        Note: Enter input without spaces

        return:
            None
        """
        # pylint: enable=line-too-long
        ret_code, message = self.init_adapter()
        if ret_code == ResultCode.FAILED:
            return ret_code, message
        try:
            json_argument = json.loads(argin)
        except JSONDecodeError as e:
            log_msg = (
                "Execution of AssignResources command is failed."
                + "Reason: JSON parsing failed with exception: {}".format(e)
                + "The command is not executed successfully."
                + "The device will continue with normal operation"
            )
            self.logger.exception(log_msg)
            return self.generate_command_result(
                ResultCode.FAILED,
                (
                    """Exception occurred while parsing the JSON.
                    Please check the logs for details."""
                ),
            )

        if "eb_id" not in json_argument["execution_block"]:
            return self.generate_command_result(
                ResultCode.FAILED,
                "eb_id key is not present in the input json argument.",
            )

        if "scan_types" not in json_argument["execution_block"]:
            return self.generate_command_result(
                ResultCode.FAILED,
                "scan_types key is not present in the input json argument.",
            )

        log_msg = "Invoking AssignResources command on:" + "{}".format(
            self.sdp_subarray_adapter.dev_name
        )
        self.logger.info(log_msg)
        try:
            json_argument[
                "interface"
            ] = "https://schema.skao.int/ska-sdp-assignres/0.4"
            log_msg = (
                "Input JSON for AssignResources command for SDP"
                + "subarray {}: {}".format(
                    self.sdp_subarray_adapter.dev_name, json_argument
                )
            )
            self.logger.debug(log_msg)
            self.sdp_subarray_adapter.AssignResources(
                json.dumps(json_argument)
            )

        except (AttributeError, ValueError, TypeError, DevFailed) as e:
            self.logger.exception("Command invocation failed: %s", e)
            return self.generate_command_result(
                ResultCode.FAILED,
                "The invocation of the AssignResources command is failed on"
                + "Sdp Subarray Device {}".format(
                    self.sdp_subarray_adapter.dev_name
                )
                + "Reason: Error in calling the AssignResources command on Sdp"
                + "Subarray."
                + "The command has NOT been executed."
                + "This device will continue with normal operation.",
            )
        log_msg = (
            "AssignResources command successfully invoked on:"
            + "{}".format(self.sdp_subarray_adapter.dev_name)
        )
        self.logger.info(log_msg)
        return (ResultCode.OK, "")
