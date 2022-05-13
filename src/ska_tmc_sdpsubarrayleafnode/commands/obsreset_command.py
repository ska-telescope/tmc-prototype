"""
ObsReset command class for SDPSubarrayLeafNode.
"""
from ska_tango_base.commands import ResultCode

from ska_tmc_sdpsubarrayleafnode.commands.abstract_command import (
    AbstractRestartObsReset,
)


class ObsReset(AbstractRestartObsReset):
    """
    A class for SdpSubarrayLeafNode's ObsReset() command.

    Command to reset the SDP Subarray and bring it to its RESETTING state.
    """

    def do(self, argin=None):
        """
        Method to invoke ObsReset command on SDP Subarray.

        :param argin: None

        return:
            None

        """
        res_code, message = self.init_adapter()
        if res_code == ResultCode.FAILED:
            return res_code, message

        log_msg = f"""Invoking ObsReset command on:
        {self.sdp_subarray_adapter.dev_name}"""
        self.logger.info(log_msg)
        try:
            log_msg = f"""Invoking ObsReset command on SDP Subarray
                {self.sdp_subarray_adapter.dev_name}: """
            self.logger.debug(log_msg)
            self.sdp_subarray_adapter.ObsReset()
        except Exception as e:
            self.logger.exception("Command invocation failed: %s", e)
            return self.generate_command_result(
                ResultCode.FAILED,
                f"""The invocation of the ObsReset command is failed on Sdp
                Subarray Device {self.sdp_subarray_adapter.dev_name}.
                Reason: Error in calling the ObsReset command on Sdp Subarray.
                The command has NOT been executed.
                This device will continue with normal operation.""",
            )
        log_msg = f"""ObsReset command successfully invoked on:
        {self.sdp_subarray_adapter.dev_name}"""
        self.logger.info(log_msg)
        return (ResultCode.OK, "")