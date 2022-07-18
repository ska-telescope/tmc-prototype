"""
Disable command class for SDPMasterLeafNode.
"""

from ska_tango_base.commands import ResultCode

from ska_tmc_sdpmasterleafnode.commands.abstract_command import SdpMLNCommand


class Disable(SdpMLNCommand):
    """
    A class for SdpMasterLeafNode's Disable() command.

    Disable command on SdpMasterLeafNode invokes disable command on
    Sdp Master device.

    """

    def __init__(
        self, target, op_state_model, adapter_factory=None, logger=None
    ):
        super().__init__(target, op_state_model, adapter_factory, logger)

    def do(self, argin=None):
        """
        Method to invoke Disable command on Sdp Master.

        """
        ret_code, message = self.init_adapter()
        if ret_code == ResultCode.FAILED:
            return ret_code, message

        result = self.call_adapter_method(
            "Sdp Master", self.sdp_master_adapter, "Disable"
        )
        return result
