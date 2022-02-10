"""
Abort command class for SDPSubarrayLeafNode.
"""
from ska_tango_base.commands import ResultCode
from ska_tmc_common.adapters import AdapterFactory

from ska_tmc_sdpsubarrayleafnode.commands.abstract_command import AbstractAbort


class Abort(AbstractAbort):
    """
    A class for SdpSubarrayLeafNode's Abort() command.

    Command to abort the SDP Subarray and bring it to its ABORTED state.
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
        Method to invoke Abort command on SDP Subarray.

        :param argin: None

        return:
            None

        raises:
            Exception if error occurs while invoking command on SDP Subarray.

        """
        res_code, message = self.init_adapter()
        if res_code == ResultCode.FAILED:
            return res_code, message

        try:
            self.logger.info(
                f"Invoking Abort command on:{self.sdp_subarray_adapter.dev_name}"
            )
            self.sdp_subarray_adapter.Abort()
        except Exception as e:
            self.logger.exception("Command invocation failed: %s", e)
            return self.generate_command_result(
                ResultCode.FAILED,
                (
                    "Error in calling Abort on sdp subarray %s",
                    self.sdp_subarray_adapter.dev_name,
                ),
            )
        return (ResultCode.OK, "")
