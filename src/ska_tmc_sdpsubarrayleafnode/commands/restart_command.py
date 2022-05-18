"""
Restart command class for SDPSubarrayLeafNode.
"""

from ska_tmc_sdpsubarrayleafnode.commands.abstract_command import (
    AbstractRestartObsReset,
)


class Restart(AbstractRestartObsReset):
    """
    A class for SdpSubarrayLeafNode's Restart() command.

    Command to reset the SDP Subarray and bring it to its RESTARTING state.
    """

    def __init__(
        self, target, op_state_model, adapter_factory=None, logger=None
    ):
        super().__init__(target, op_state_model, adapter_factory, logger)
        self.init_adapter()

    def do(self, argin=None):
        """
        Method to invoke Restart command on SDP Subarray.

        :param argin: None

        return:
            None
        """
        result = self.call_adapter_method(
            "Sdp Subarray", self.sdp_subarray_adapter, "Restart"
        )
        return result