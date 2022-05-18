"""
Off command class for SDPSubarrayLeafNode.
"""

from ska_tmc_sdpsubarrayleafnode.commands.abstract_command import AbstractOnOff


class Off(AbstractOnOff):
    """
    A class for SdpsubarrayLeafNode's Off() command.

    Off command on SdpsubarrayLeafNode enables the telescope to perform
    further operations and observations.
    It Invokes Off command on Sdp Subarray device.

    """

    def __init__(
        self, target, op_state_model, adapter_factory=None, logger=None
    ):
        super().__init__(target, op_state_model, adapter_factory, logger)
        self.init_adapter()

    def do(self, argin=None):
        """
        Method to invoke Telescope Off command on Sdp Subarray.

        """
        result = self.call_adapter_method(
            "Sdp Subarray", self.sdp_subarray_adapter, "Off"
        )
        return result