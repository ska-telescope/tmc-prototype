"""
End command class for SDPSubarrayLeafNode.
"""

from ska_tmc_sdpsubarrayleafnode.commands.abstract_command import (
    AbstractScanEnd,
)


class End(AbstractScanEnd):
    """
    A class for SdpSubarrayLeafNode's End() command.

    Invokes End command on SDP Subarray to end the current Scheduling Block.

    """

    def __init__(
        self, target, op_state_model, adapter_factory=None, logger=None
    ):
        super().__init__(target, op_state_model, adapter_factory, logger)
        self.init_adapter()

    def do(self, argin=None):
        """
        Method to invoke End command on SDP Subarray.

        :param argin: None

        return:
            None

        """
        result = self.call_adapter_method(
            "Sdp Subarray", self.sdp_subarray_adapter, "End"
        )
        return result