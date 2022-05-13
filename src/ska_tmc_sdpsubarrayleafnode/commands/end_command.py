"""
End command class for SDPSubarrayLeafNode.
"""
from ska_tango_base.commands import ResultCode

from ska_tmc_sdpsubarrayleafnode.commands.abstract_command import (
    AbstractScanEnd,
)


class End(AbstractScanEnd):
    """
    A class for SdpSubarrayLeafNode's End() command.

    Invokes End command on SDP Subarray to end the current Scheduling Block.

    """

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

        log_msg = (
            f"Invoking End command on:{self.sdp_subarray_adapter.dev_name}"
        )
        self.logger.info(log_msg)
        try:
            log_msg = (
                "Invoking End command on SDP Subarray %s: ",
                self.sdp_subarray_adapter.dev_name,
            )
            self.logger.debug(log_msg)
            self.sdp_subarray_adapter.End()

        except Exception as e:
            self.logger.exception("Command invocation failed: %s", e)
            return self.generate_command_result(
                ResultCode.FAILED,
                f"""The invocation of the End command is failed on device
                {self.sdp_subarray_adapter.dev_name}.
                Reason: Error in calling the End command on Sdp Subarray.
                The command has NOT been executed.
                This device will continue with normal operation.""",
            )
        log_msg = f"""End command successfully invoked on:
        {self.sdp_subarray_adapter.dev_name}"""
        self.logger.info(log_msg)
        return (ResultCode.OK, "")