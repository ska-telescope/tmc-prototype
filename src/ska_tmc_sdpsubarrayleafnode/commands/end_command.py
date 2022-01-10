"""
End class for SDPSubarrayLeafNode.
"""
# PROTECTED REGION ID(sdpsubarrayleafnode.additionnal_import) ENABLED START #
# Tango imports
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
        pop_state_model,
        adapter_factory=AdapterFactory(),
        logger=None,
    ):
        super().__init__(target, pop_state_model, adapter_factory, logger)

    def do_mid(self, argin=None):
        """
        Method to invoke End command on SDP Subarray.

        :param argin: None

        return:
            None

        raises:
            DevFailed if the command execution is not successful
        """
        ret_code, message = self.init_adapters()

        if ret_code == ResultCode.FAILED:
            return ret_code, message

        try:
            self.logger.info("Invoking End command on sdp subarray device")
            self.sdp_subarray_adapter.End()
            self.logger.info("End command is successful on Sdp Subarray")

        except Exception as e:
            return self.generate_command_result(
                ResultCode.FAILED,
                (
                    "Error in calling End on subarray %s: %s",
                    self.sdp_subarray_adapter.dev_name,
                    e,
                ),
            )
        return (ResultCode.OK, "")
