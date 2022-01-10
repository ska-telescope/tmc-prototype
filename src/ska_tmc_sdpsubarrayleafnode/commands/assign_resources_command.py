"""
AssignResouces class for SDPSubarrayLeafNode.
"""
# Tango imports
import json

from ska_tango_base.commands import ResultCode
from ska_tmc_common.adapters import AdapterFactory

from ska_tmc_sdpsubarrayleafnode.commands.abstract_command import (
    AbstractAssignResources,
)


class AssignResources(AbstractAssignResources):
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
        super().__init__(target, op_state_model, adapter_factory, logger)

    def do_mid(self, argin):
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

        raises:
            KeyError if input argument json string contains invalid key.

            DevFailed if the command execution is not successful.
        """
        ret_code, message = self.init_adapters_mid()
        if ret_code == ResultCode.FAILED:
            return ret_code, message

        try:
            json_argument = json.loads(argin)
        except Exception as e:
            return self.generate_command_result(
                ResultCode.FAILED,
                ("Problem in loading the JSON string: %s", e),
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

        try:
            f"Invoking AssignResources command on:{self.sdp_subarray_adapter.dev_name}"
            self.sdp_subarray_adapter.AssignResources(
                json.dumps(json_argument.copy())
            )
        except Exception as e:
            return self.generate_command_result(
                ResultCode.FAILED,
                (
                    "Error in calling AssignResources on subarray %s: %s",
                    self.sdp_subarray_adapter.dev_name,
                    e,
                ),
            )
        return (ResultCode.OK, "")
