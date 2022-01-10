"""
TelescopeOff command class for SDPSubarrayLeafNode.
"""
from ska_tango_base.commands import ResultCode
from ska_tmc_common.adapters import AdapterFactory

from ska_tmc_sdpsubarrayleafnode.commands.abstract_command import (
    AbstractTelescopeOnOff,
)


class TelescopeOff(AbstractTelescopeOnOff):
    """
    A class for SdpsubarrayLeafNode's TelescopeOff() command.

    TelescopeOff command on SdpsubarrayLeafNode enables the telescope to perform further operations
    and observations. It Invokes Off command on Sdp Subarray device.

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
        Method to invoke Telescope Off command on Sdp Subarray.

        """
        ret_code, message = self.init_adapters()
        if ret_code == ResultCode.FAILED:
            return ret_code, message

        try:
            self.logger.info(
                f"Invoking TelescopeOff command on:{self.sdp_subarray_adapter.dev_name}"
            )
            self.sdp_subarray_adapter.Off()
            self.logger.info(
                "Off command is successful on Sdp Subarray device."
            )
        except Exception as e:
            return self.generate_command_result(
                ResultCode.FAILED,
                f"Error in calling Telescope Off Sdp Subarray Device {self.sdp_subarray_adapter.dev_name}: {e}",
            )
        return (ResultCode.OK, "")
