"""
ObsReset class for SDPSubarrayLeafNode.
"""
# PROTECTED REGION ID(sdpsubarrayleafnode.additionnal_import) ENABLED START #

# Additional import
from ska_tango_base.commands import ResultCode
from ska_tmc_common.adapters import AdapterFactory

from ska_tmc_sdpsubarrayleafnode.commands.abstract_command import (
    AbstractRestartObsReset,
)


class ObsReset(AbstractRestartObsReset):
    """
    A class for SdpSubarrayLeafNode's ObsResetCommand() command.

    Command to reset the SDP Subarray and bring it to its RESETTING state.
    """

    def __init__(
        self,
        target,
        op_state_model,
        adapter_factory=AdapterFactory(),
        logger=None,
    ):
        super().__init__(target, op_state_model, adapter_factory, logger)

    def do_mid(self, argin=None):
        """
        Method to invoke ObsReset command on SDP Subarray.

        :param argin: None

        return:
            None

        raises:
            DevFailed if error occurs while invoking command on SDP Subarray.

        """
        res_code, message = self.init_adapters_mid()
        if res_code == ResultCode.FAILED:
            return res_code, message

        try:
            self.logger.info(
                "Invoking ObsReset command on sdp subarray device"
            )
            self.sdp_subarray_adapter.ObsReset()
            self.logger.info("ObsReset command is successful on Sdp Subarray")
        except Exception as e:
            return self.generate_command_result(
                ResultCode.FAILED,
                (
                    "Error in calling ObsReset on sdp subarray %s: %s",
                    self.sdp_subarray_adapter.dev_name,
                    e,
                ),
            )
        return (ResultCode.OK, "")
