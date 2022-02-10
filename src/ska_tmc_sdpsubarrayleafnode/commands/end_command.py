"""
End command class for SDPSubarrayLeafNode.
"""
from ska_tango_base.commands import ResultCode
from ska_tmc_common.adapters import AdapterFactory

from ska_tmc_sdpsubarrayleafnode.commands.abstract_command import (
    AbstractScanEnd,
)


class End(AbstractScanEnd):
    """
    A class for SdpSubarrayLeafNode's End() command.

    Invokes End command on SDP Subarray to end the current Scheduling Block.

    """

    def __init__(
        self,
        target,
        op_state_model,
        adapter_factory=AdapterFactory(),
        logger=None,
    ):
        super().__init__(target, op_state_model, adapter_factory, logger)

    def do(self, argin=None):
        """
        Method to invoke End command on SDP Subarray.

        :param argin: None

        return:
            None

        """
        ret_code, message = self.init_adapter()

        if ret_code == ResultCode.FAILED:
            return ret_code, message

        try:
            self.logger.info(
                f"Invoking End command on:{self.sdp_subarray_adapter.dev_name}"
            )
            self.sdp_subarray_adapter.End()

        except Exception as e:
            self.logger.exception("Command invocation failed: %s", e)
            return self.generate_command_result(
                ResultCode.FAILED,
                (
                    "Error in calling End on subarray %s",
                    self.sdp_subarray_adapter.dev_name,
                ),
            )
        return (ResultCode.OK, "")
