"""
Standby command class for SDPMasterLeafNode.
"""

from ska_tango_base.commands import ResultCode

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
        ret_code, message = self.init_adapter()
        if ret_code == ResultCode.FAILED:
            return ret_code, message
        self.check_unresponsive()
        result = self.call_adapter_method(
            "Sdp Master", self.sdp_master_adapter, "Standby"
        )
        return result
