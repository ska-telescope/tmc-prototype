"""
Scan command class for SDPSubarrayLeafNode.
"""
import json

from ska_tango_base.commands import ResultCode
from ska_tmc_common.adapters import AdapterFactory

from ska_tmc_sdpsubarrayleafnode.commands.abstract_command import (
    AbstractScanEnd,
)


class Scan(AbstractScanEnd):
    """
    A class for SdpSubarrayLeafNode's Scan() command.

    Invoke Scan command to SDP Subarray.
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
        Method to invoke Scan command on SDP Subarray.

        :param argin: The string in JSON format. The JSON contains following values:

        Example:
        {
             "interface": "https://schema.skao.int/ska-sdp-scan/0.3",
             "scan_id": 1
        }

        Note: Enter input as without spaces: {"interface":"https://schema.skao.int/ska-sdp-scan/0.3","scan_id":1}

        return:
            None

        """

        res_code, message = self.init_adapters()
        if res_code == ResultCode.FAILED:
            return res_code, message

        try:
            json_argument = json.loads(argin)
        except Exception as e:
            return self.generate_command_result(
                ResultCode.FAILED,
                (
                    "Problem in loading JSON string in Scan command on SDP Subarray Leaf Node: %s",
                    e,
                ),
            )

        log_msg = (
            "Input JSON for SDP Subarray Leaf Node Scan command is: " + argin
        )
        self.logger.debug(log_msg)

        try:
            # As, SKA logtransaction is not utilised in scan command across tmc devices.
            # Hence, Interface URL needs to be updated explicitly for SDP.
            # TODO: Incorporate transaction id implementation for scan command across TMC.
            json_argument[
                "interface"
            ] = "https://schema.skao.int/ska-sdp-scan/0.3"
            log_msg = (
                "Updated Input JSON for SDP Subarray Leaf Node Scan command is: %s",
                json_argument,
            )
            self.logger.debug(log_msg)
            self.sdp_subarray_adapter.Scan(json.dumps(json_argument.copy()))
        except Exception as e:
            return self.generate_command_result(
                ResultCode.FAILED,
                (
                    "Error in calling Scan on sdp subarray %s: %s",
                    self.sdp_subarray_adapter.dev_name,
                    e,
                ),
            )
        return (ResultCode.OK, "")
