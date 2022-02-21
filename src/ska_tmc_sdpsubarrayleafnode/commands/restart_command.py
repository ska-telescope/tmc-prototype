"""
Restart command class for SDPSubarrayLeafNode.
"""
from ska_tango_base.commands import ResultCode
from ska_tmc_common.adapters import AdapterFactory

from ska_tmc_sdpsubarrayleafnode.commands.abstract_command import (
    AbstractRestartObsReset,
)


class Restart(AbstractRestartObsReset):
    """
    A class for SdpSubarrayLeafNode's Restart() command.

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

    def do(self, argin=None):
        """
        Method to invoke Restart command on SDP Subarray.

        :param argin: None

        return:
            None
        """
        res_code, message = self.init_adapter()
        if res_code == ResultCode.FAILED:
            return res_code, message

        log_msg = (
            f"Invoking Restart command on:{self.sdp_subarray_adapter.dev_name}"
        )
        self.logger.info(log_msg)
        try:
            log_msg = (
                "Invoking Restart command on SDP Subarray %s: ",
                self.sdp_subarray_adapter.dev_name,
            )
            self.logger.debug(log_msg)
            self.sdp_subarray_adapter.Restart()
        except Exception as e:
            self.logger.exception("Command invocation failed: %s", e)
            return self.generate_command_result(
                ResultCode.FAILED,
                f"""The invocation of the Restart command is failed on Sdp Subarray Device {self.sdp_subarray_adapter.dev_name}.
                Reason: Error in calling the Restart command on Sdp Subarray.
                The command has NOT been executed.
                This device will continue with normal operation.""",
            )
        log_msg = f"Restart command successfully invoked on:{self.sdp_subarray_adapter.dev_name}"
        self.logger.info(log_msg)
        return (ResultCode.OK, "")
