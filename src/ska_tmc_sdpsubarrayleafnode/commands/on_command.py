"""
On command class for SDPSubarrayLeafNode.

"""
from ska_tango_base.commands import ResultCode
from ska_tmc_common.adapters import AdapterFactory

from ska_tmc_sdpsubarrayleafnode.commands.abstract_command import AbstractOnOff


class On(AbstractOnOff):
    """
    A class for SdpsubarrayLeafNode's On() command.

    On command on SdpsubarrayLeafNode enables the telescope to perform further operations
    and observations. It Invokes On command on Sdp Subarray device.

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

    def do(self, argin=None):
        """
        Method to invoke Telescope On command on Sdp Subarray.

        """
        ret_code, message = self.init_adapter()
        if ret_code == ResultCode.FAILED:
            return ret_code, message

        try:
            self.logger.info(
                f"Invoking On command on:{self.sdp_subarray_adapter.dev_name}"
            )
            self.sdp_subarray_adapter.On()
            self.logger.info(
                "On command is successful on Sdp Subarray device."
            )
        except Exception as e:
            self.logger.exception("Command invocation failed: %s", e)
            return self.generate_command_result(
                ResultCode.FAILED,
                (
                    "Error in invoking On command on %s",
                    self.sdp_subarray_adapter.dev_name,
                ),
            )
        return (ResultCode.OK, "")
