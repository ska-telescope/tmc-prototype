"""
Abort Command for SdpSubarrayLeafNode.
"""
from ska_tango_base.commands import ResultCode

from ska_tmc_sdpsubarrayleafnode.commands.abstract_command import SdpSLNCommand


class Abort(SdpSLNCommand):
    """
    A class for SdpSubarrayLeafNode's Abort() command.
    Aborts the Sdp Subarray device.
    """

    def __init__(
        self,
        component_manager,
        logger=None,
    ):
        super().__init__(
            component_manager=component_manager,
            logger=logger,
        )
        self.component_manager = component_manager
        self.logger = logger

    def invoke_abort(self, argin=None):
        """This method calls do for Abort command"""

        res_code, message = self.do(argin)
        self.logger.info(message)
        return res_code, message

    def do(self, argin=None):
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
        res_code, message = self.init_adapter()
        if res_code == ResultCode.FAILED:
            return res_code, message
        try:
            self.logger.info(
                "Invoking Abort command on SDP Subarray:%s",
                self.sdp_subarray_adapter.dev_name,
            )
            self.sdp_subarray_adapter.Abort()
        except Exception as e:
            self.logger.exception(
                "Execution of Abort command is failed."
                + "Reason: Error in invoking Abort command on SDP Subarray"
                + f"Leaf Node : {e}\n"
                + "The command is not executed successfully."
                + "The device will continue with normal operation"
            )
            return self.component_manager.generate_command_result(
                ResultCode.FAILED,
                f"Error in calling Abort command on SDP Subarray Leaf Node \
                {self.sdp_subarray_adapter.dev_name}",
            )
        return ResultCode.OK, ""
