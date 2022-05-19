"""
Standby command class for SDPMasterLeafNode.
"""

from ska_tmc_sdpmasterleafnode.commands.abstract_command import SdpMLNCommand


class Standby(SdpMLNCommand):
    """
    A class for SdpMasterLeafNode's Standby() command.

    Standby command on SdpMasterLeafNode invokes Standby command on Sdp
    Master device.

    """

    def do(self, argin=None):
        """
        Method to invoke Standby command on Sdp Master.

        """
        self.init_adapter()
        result = self.call_adapter_method(
            "Sdp Master", self.sdp_master_adapter, "Standby"
        )
        return result
