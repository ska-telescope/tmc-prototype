"""
EndScan class for SDPSubarrayLeafNode.
"""
# PROTECTED REGION ID(sdpsubarrayleafnode.additionnal_import) ENABLED START #

from ska_tango_base.commands import ResultCode
from ska_tmc_common.adapters import AdapterFactory

from ska_tmc_sdpsubarrayleafnode.commands.abstract_command import (
    AbstractEndScan,
)


class EndScan(AbstractEndScan):
    """
    A class for SdpSubarrayLeafNode's EndScan() command.

    It invokes EndScan command on Sdp Subarray.
    This command is allowed when Sdp Subarray is in SCANNING state.
    """

    def __init__(
        self,
        target,
        op_state_model,
        adapter_factory=AdapterFactory(),
        logger=None,
    ):
        super().__init__(
            target,
            op_state_model,
            adapter_factory,
            logger,
        )

    def do_mid(self, argin):
        """
        Method to invoke EndScan command on SDP Subarray.

        """

        res_code, message = self.init_adapters_mid()
        if res_code == ResultCode.FAILED:
            return res_code, message

        try:
            f"Invoking EndScan command on:{self.sdp_subarray_adapter.dev_name}"
            self.sdp_subarray_adapter.EndScan()

        except Exception as e:
            return self.generate_command_result(
                ResultCode.FAILED,
                ("Error in calling EndScan Sdp Subarray Device: %s", e),
            )
        return (ResultCode.OK, "")
