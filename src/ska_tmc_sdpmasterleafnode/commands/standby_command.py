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

    def __init__(
        self, target, op_state_model, adapter_factory=None, logger=None
    ):
        super().__init__(target, op_state_model, adapter_factory, logger)
        try:
            self.init_adapter()
        except Exception as e:
            logger.info(f"Exception:, {e}")

    def do(self, argin=None):
        """
        Method to invoke Standby command on Sdp Master.

        """
        result = self.call_adapter_method(
            "Sdp Master", self.sdp_master_adapter, "Standby"
        )
        return result
