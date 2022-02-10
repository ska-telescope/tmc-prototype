"""
Reset command class for SDPSubarrayLeafNode.
"""
from ska_tango_base.commands import ResultCode
from ska_tmc_common.adapters import AdapterFactory

from ska_tmc_sdpsubarrayleafnode.commands.abstract_command import AbstractReset


class Reset(AbstractReset):
    """
    A class for SdpSubarrayLeafNode's Reset() command.

    Command to reset the SDP Subarray and bring it to its initial state.
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
        Method to invoke Reset command on SDP Subarray.

        :param argin: None

        return:
            None

        """
        res_code, message = self.init_adapter()
        if res_code == ResultCode.FAILED:
            return res_code, message

        try:
            self.logger.info(
                "Invoking Reset command on Sdp Subarray Leaf Node"
            )
            self.logger.info(
                "Reset command is successful on Sdp Subarray Leaf Node"
            )
        except Exception as e:
            self.logger.exception("Command invocation failed: %s", e)
            return self.generate_command_result(
                ResultCode.FAILED,
                (
                    "Error in calling Reset on sdp subarray %s",
                    self.sdp_subarray_adapter.dev_name,
                ),
            )
        return (ResultCode.OK, "")
