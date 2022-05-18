"""
On command class for SDPSubarrayLeafNode.

"""

from ska_tmc_sdpsubarrayleafnode.commands.abstract_command import AbstractOnOff


class On(AbstractOnOff):
    """
    A class for SdpsubarrayLeafNode's On() command.

    On command on SdpsubarrayLeafNode enables the telescope to perform further
    operations and observations.
    It Invokes On command on Sdp Subarray device.

    """

    def __init__(
        self, target, op_state_model, adapter_factory=None, logger=None
    ):
        super().__init__(target, op_state_model, adapter_factory, logger)
        self.init_adapter()

    def do(self, argin=None):
        """
        Method to invoke Telescope On command on Sdp Subarray.

        """
        result = self.call_adapter_method(
            "Sdp Subarray", self.sdp_subarray_adapter, "On"
        )
        return result