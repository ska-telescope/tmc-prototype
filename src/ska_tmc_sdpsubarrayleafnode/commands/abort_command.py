"""
Abort Command for CspSubarrayLeafNode.
"""
from ska_tango_base.commands import ResultCode

from ska_tmc_sdpsubarrayleafnode.commands.abstract_command import SdpSLNCommand


class Abort(SdpSLNCommand):
    """
    A class for CspSubarrayLeafNode's Abort() command.
    Aborts the CSP Subarray device.
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
        Method to invoke Abort command on SDP Subarray.

        :param argin: None

        return:
            None

        raises:
            Exception if error occurs while invoking command on SDP Subarray.

        """
        ret_code, message = self.init_adapter()
        if ret_code == ResultCode.FAILED:
            return ret_code, message

        result = self.call_adapter_method(
            "Sdp Subarray", self.sdp_subarray_adapter, "Abort"
        )
        return result
