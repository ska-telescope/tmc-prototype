"""
Abort Command for SdpSubarrayLeafNode.
"""
from typing import Tuple

from ska_tango_base.commands import ResultCode

from ska_tmc_sdpsubarrayleafnode.commands.abstract_command import SdpSLNCommand


class Abort(SdpSLNCommand):
    """
    A class for SdpSubarrayLeafNode's Abort() command.
    Aborts the SDP Subarray device.
    """

    # pylint: disable=arguments-differ
    def do(self) -> Tuple[ResultCode, str]:
        """
        This method invokes Abort command on SDP Subarray

        return:
            A tuple containing a return code and a string
            message indicating status.
            The message is for information purpose only.

        rtype:
            (ResultCode, str)

        raises:
            Exception if error occurs in invoking command
            on any of the devices like SdpSubarrayLeafNode
        """
        result_code, message = self.init_adapter()
        if result_code == ResultCode.FAILED:
            return result_code, message
        try:
            self.logger.info(
                "Invoking Abort command on SDP Subarray:%s",
                self.sdp_subarray_adapter.dev_name,
            )
            self.sdp_subarray_adapter.Abort()
        except Exception as ex:
            self.logger.exception(
                "Execution of Abort command is failed."
                + "Reason: Error in invoking Abort command on SDP Subarray"
                + f"{ex}"
            )
            return self.component_manager.generate_command_result(
                ResultCode.FAILED,
                f"Error in calling Abort command on SDP Subarray  \
                {self.sdp_subarray_adapter.dev_name}",
            )
        return ResultCode.OK, ""
