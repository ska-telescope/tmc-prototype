"""
Restart command class for SDPSubarrayLeafNode.
"""
# PROTECTED REGION ID(sdpsubarrayleafnode.additionnal_import) ENABLED START #

# Additional import
from ska_tango_base.commands import ResultCode
from ska_tmc_common.adapters import AdapterFactory

from ska_tmc_sdpsubarrayleafnode.commands.abstract_command import (
    AbstractRestartObsReset,
)


class Restart(AbstractRestartObsReset):
    """
    A class for SdpSubarrayLeafNode's RestartCommand() command.

    Command to reset the SDP Subarray and bring it to its RESTARTING state.
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
        Method to invoke Restart command on SDP Subarray.

        :param argin: None

        return:
            None
        """
        res_code, message = self.init_adapters_mid()
        if res_code == ResultCode.FAILED:
            return res_code, message

        try:
            self.logger.info(
                f"Invoking Restart command on:{self.sdp_subarray_adapter.dev_name}"
            )
            self.sdp_subarray_adapter.Restart()
        except Exception as e:
            return self.generate_command_result(
                ResultCode.FAILED,
                (
                    "Error in calling Restart on sdp subarray %s: %s",
                    self.sdp_subarray_adapter.dev_name,
                    e,
                ),
            )
        return (ResultCode.OK, "")
