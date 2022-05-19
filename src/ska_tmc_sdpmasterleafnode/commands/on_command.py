"""
On command class for SDPMasterLeafNode.

"""

from ska_tmc_sdpmasterleafnode.commands.abstract_command import SdpMLNCommand


class On(SdpMLNCommand):
    """
    A class for SdpMasterLeafNode's On() command.

    On command on SdpmasterLeafNode enables the telescope to perform
    further operations and observations.
    It Invokes On command on Sdp Master device.

    """

    def do(self, argin=None):
        """
        Method to invoke On command on Sdp Master.

        """
        self.init_adapter()
        result = self.call_adapter_method(
            "Sdp Master", self.sdp_master_adapter, "On"
        )
        return result
