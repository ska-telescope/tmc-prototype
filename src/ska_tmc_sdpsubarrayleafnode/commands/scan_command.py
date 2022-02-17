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

    def do(self, argin):
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

        res_code, message = self.init_adapter()
        if res_code == ResultCode.FAILED:
            return res_code, message

        try:
            json_argument = json.loads(argin)
        except Exception as e:
            log_msg = f"JSON parsing error: {e}"
            self.logger.error(log_msg)
            return self.generate_command_result(
                ResultCode.FAILED,
                ("JSON parsing error"),
            )

        log_msg = (
            f"Invoking Scan command on:{self.sdp_subarray_adapter.dev_name}"
        )
        self.logger.info(log_msg)

        try:
            # As, SKA logtransaction is not utilised in scan command across tmc devices.
            # Hence, Interface URL needs to be updated explicitly for SDP.
            # TODO: Incorporate transaction id implementation for scan command across TMC.
            json_argument[
                "interface"
            ] = "https://schema.skao.int/ska-sdp-scan/0.3"
            log_msg = (
                "SDP Subarray input JSON: %s",
                json_argument,
            )
            self.logger.debug(log_msg)
            self.sdp_subarray_adapter.Scan(json.dumps(json_argument))
        except Exception as e:
            self.logger.exception("Command invocation failed: %s", e)
            return self.generate_command_result(
                ResultCode.FAILED,
                f"""The invocation of the Scan command is failed on Sdp Subarray Device {self.sdp_subarray_adapter.dev_name}.
                Reason: Error in calling the Scan command on Sdp Subarray.
                The command has NOT been executed.
                This device will continue with normal operation.""",
            )
        log_msg = f"Scan command successfully invoked on:{self.sdp_subarray_adapter.dev_name}"
        self.logger.info(log_msg)
        return (ResultCode.OK, "")
