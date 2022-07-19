"""
Reset command class for SDPSubarrayLeafNode.
"""
from ska_tango_base.commands import ResultCode
from ska_tmc_common.adapters import AdapterFactory

from ska_tmc_sdpsubarrayleafnode.commands.abstract_command import SdpSLNCommand


class Reset(SdpSLNCommand):
    """
    A class for SdpSubarrayLeafNode's Reset() command.

    Command to reset the SDP Subarray and bring it to its initial state.
    """

    def __init__(
        self,
        target,
        op_state_model,
        adapter_factory=None,
        logger=None,
    ):
        super().__init__(target, logger)
        self.op_state_model = op_state_model
        self._adapter_factory = adapter_factory or AdapterFactory()

    def check_allowed(self):
        """
        Checks whether this command is allowed
        It checks that the device is in the right state
        to execute this command and that all the
        component needed for the operation are not unresponsive

        :return: True if this command is allowed

        :rtype: boolean

        """

        self.check_op_state("Reset")
        self.check_unresponsive()

        return True

    def do(self, argin=None):
        """
        Method to invoke Reset command on SDP Subarray.

        :param argin: None

        return:
            None

        """
        ret_code, message = self.init_adapter()
        if ret_code == ResultCode.FAILED:
            return ret_code, message
        try:
            self.logger.info("Resetting Sdp Subarray Leaf Node")
        except Exception as e:
            self.logger.exception("Command invocation failed: %s", e)
            return self.generate_command_result(
                ResultCode.FAILED,
                f"""The invocation of the Reset command is failed on Sdp
                Subarray Device {self.sdp_subarray_adapter.dev_name}.
                Reason: Error in calling the Reset command on Sdp Subarray.
                The command has NOT been executed.
                This device will continue with normal operation.""",
            )
        return (ResultCode.OK, "")
