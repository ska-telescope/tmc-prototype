"""
Configure class for SDPSubarrayLeafNode.
"""
# PROTECTED REGION ID(SDPSubarrayLeafNode.additionnal_import) ENABLED START #
import json

# Tango imports
from ska_tango_base.commands import ResultCode
from ska_tmc_common.adapters import AdapterFactory

from ska_tmc_sdpsubarrayleafnode.commands.abstract_command import (
    AbstractConfigure,
)


class Configure(AbstractConfigure):
    """
    A class for SdpSubarrayLeafNode's Configure() command.

    Configures the SDP Subarray device by providing the SDP PB
    configuration needed to execute the receive workflow

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
        Method to invoke Configure command on SDP Subarray.

        :param argin: The string in JSON format. The JSON contains following values:

        Example:
        {
          "interface": "https://schema.skao.int/ska-sdp-configure/0.3",
          "scan_type": "science_A"
        }

        return:
            None

        raises:
            ValueError if input argument json string contains invalid value.

            KeyError if input argument json string contains invalid key.

            DevFailed if the command execution is not successful
        """
        ret_code, message = self.init_adapters()
        if ret_code == ResultCode.FAILED:
            return ret_code, message

        try:
            json_argument = json.loads(argin)
        except Exception as e:
            return self.generate_command_result(
                ResultCode.FAILED,
                ("Problem in loading the JSON string: %s", e),
            )

        if "interface" not in json_argument:
            return self.generate_command_result(
                ResultCode.FAILED,
                "interface key is not present in the input json argument.",
            )

        if "scan_type" not in json_argument:
            return self.generate_command_result(
                ResultCode.FAILED,
                "scan_type key is not present in the input json argument.",
            )

        if json_argument["scan_type"] != "science_A":
            return self.generate_command_result(
                ResultCode.FAILED,
                "science_A value is not present in the input json argument.",
            )

        try:
            self.logger.info(
                "Invoking Configure command on sdp subarray device"
            )
            self.sdp_subarray_adapter.Configure(
                json.dumps(json_argument.copy())
            )
            self.logger.info("Configure command is successful on Sdp Subarray")

        except Exception as e:
            return self.generate_command_result(
                ResultCode.FAILED,
                (
                    "Error in calling Configure on subarray %s: %s",
                    self.sdp_subarray_adapter.dev_name,
                    e,
                ),
            )
        return (ResultCode.OK, "")
