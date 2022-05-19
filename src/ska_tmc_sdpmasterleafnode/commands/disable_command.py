"""
Disable command class for SDPMasterLeafNode.
"""

from ska_tmc_sdpmasterleafnode.commands.abstract_command import SdpMLNCommand


class Disable(SdpMLNCommand):
    """
    A class for SdpMasterLeafNode's Disable() command.

    Disable command on SdpMasterLeafNode invokes disable command on
    Sdp Master device.

    """

    def do(self, argin=None):
        """
        Method to invoke Disable command on Sdp Master.

        """
        self.init_adapter()
        result = self.call_adapter_method(
            "Sdp Master", self.sdp_master_adapter, "Disable"
        )
        return result
