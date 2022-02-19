"""
AssignResouces command class for SDPSubarrayLeafNode.
"""
import json

from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsState
from ska_tmc_common.adapters import AdapterFactory
from ska_tmc_common.exceptions import InvalidObsStateError

from ska_tmc_sdpsubarrayleafnode.commands.abstract_command import SdpSLNCommand


class AssignResources(SdpSLNCommand):
    """
    A class for SdpSubarayLeafNode's AssignResources() command.

    Assigns resources to given SDP Subarray.
    This command is provided as a noop placeholder from SDP Subarray.
    Eventually this will likely take a JSON string specifying the resource request.
    """

    def __init__(
        self,
        target,
        op_state_model,
        adapter_factory=AdapterFactory(),
        logger=None,
    ):
        super().__init__(target, logger)
        self.op_state_model = op_state_model
        self._adapter_factory = adapter_factory

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

        obs_state_val = component_manager.get_device().obsState
        self.logger.info("sdp_subarray_obs_state: %s", obs_state_val)

        if obs_state_val not in [ObsState.IDLE, ObsState.EMPTY]:
            message = f"""AssignResources command is not allowed in current observation state on device {component_manager.get_device().dev_name}.
            Reason: The current observation state for observation is {obs_state_val}.
            The \"AssignResources\" command has NOT been executed. This device will continue with normal operation."""
            raise InvalidObsStateError(message)

        return True

    def do(self, argin):
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
            {"interface":"https://schema.skao.int/ska-sdp-assignres/0.3",
            "eb_id":"eb-mvp01-20200325-00001","max_length":100.0,"scan_types":[{"scan_type_id":"science_A",
            "reference_frame":"ICRS","ra":"02:42:40.771","dec":"-00:00:47.84","channels":[{"count":744,"start":0,
            "stride":2,"freq_min":0.35e9,"freq_max":0.368e9,"link_map":[[0,0],[200,1],[744,2],[944,3]]},
            {"count":744,"start":2000,"stride":1,"freq_min":0.36e9,"freq_max":0.368e9,"link_map":[[2000,4],[2200,5]]}]}
            ,{"scan_type_id":"calibration_B","reference_frame":"ICRS","ra":"12:29:06.699","dec":"02:03:08.598",
            "channels":[{"count":744,"start":0,"stride":2,"freq_min":0.35e9,"freq_max":0.368e9,"link_map":[[0,0],
            [200,1],[744,2],[944,3]]},{"count":744,"start":2000,"stride":1,"freq_min":0.36e9,"freq_max":0.368e9,
            "link_map":[[2000,4],[2200,5]]}]}],"processing_blocks":[{"pb_id":"pb-mvp01-20200325-00001","workflow":
            {"kind":"realtime","name":"vis_receive","version":"0.1.0"},"parameters":{}},{"pb_id":
            "pb-mvp01-20200325-00002","workflow":{"kind":"realtime","name":"test_realtime","version":"0.1.0"},
            "parameters":{}},{"pb_id":"pb-mvp01-20200325-00003","workflow":{"kind":"batch","name":"ical",
            "version":"0.1.0"},"parameters":{},"dependencies":[{"pb_id":"pb-mvp01-20200325-00001",
            "kind":["visibilities"]}]},{"pb_id":"pb-mvp01-20200325-00004","workflow":{"kind":"batch","name":"dpreb",
            "version":"0.1.0"},"parameters":{},"dependencies":[{"pb_id":"pb-mvp01-20200325-00003","kind":
            ["calibration"]}]}]}

        Note: Enter input without spaces

        return:
            None
        """
        ret_code, message = self.init_adapter()
        if ret_code == ResultCode.FAILED:
            return ret_code, message

        try:
            json_argument = json.loads(argin)
        except Exception as e:
            log_msg = f"""Execution of AssignResources command is failed.
            Reason: JSON parsing failed with exception: {e}
            The command is not executed successfully.
            The device will continue with normal operation"""
            self.logger.exception(log_msg)
            return self.generate_command_result(
                ResultCode.FAILED,
                (
                    "Exception occurred while parsing the JSON. Please check the logs for details."
                ),
            )

        if "eb_id" not in json_argument:
            return self.generate_command_result(
                ResultCode.FAILED,
                "eb_id key is not present in the input json argument.",
            )

        if "scan_types" not in json_argument:
            return self.generate_command_result(
                ResultCode.FAILED,
                "scan_types key is not present in the input json argument.",
            )

        log_msg = f"Invoking AssignResources command on:{self.sdp_subarray_adapter.dev_name}"
        self.logger.info(log_msg)
        try:
            json_argument[
                "interface"
            ] = "https://schema.skao.int/ska-sdp-assignres/0.3"
            log_msg = (
                "Input JSON for AssignResources command for SDP subarray %s: %s, ",
                self.sdp_subarray_adapter.dev_name,
                json_argument,
            )
            self.logger.debug(log_msg)
            self.sdp_subarray_adapter.AssignResources(
                json.dumps(json_argument)
            )

        except Exception as e:
            self.logger.exception("Command invocation failed: %s", e)
            return self.generate_command_result(
                ResultCode.FAILED,
                f"""The invocation of the AssignResources command is failed on Sdp Subarray Device {self.sdp_subarray_adapter.dev_name}.
                Reason: Error in calling the AssignResources command on Sdp Subarray.
                The command has NOT been executed.
                This device will continue with normal operation.""",
            )
        log_msg = f"AssignResources command successfully invoked on:{self.sdp_subarray_adapter.dev_name}"
        self.logger.info(log_msg)
        return (ResultCode.OK, "")
