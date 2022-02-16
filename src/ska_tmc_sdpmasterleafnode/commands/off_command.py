"""
Off command class for SDPMasterLeafNode.
"""
from ska_tango_base.commands import ResultCode
from ska_tmc_common.adapters import AdapterFactory

from ska_tmc_sdpmasterleafnode.commands.abstract_command import SdpMLNCommand


class Off(SdpMLNCommand):
    """
    A class for SdpMasterLeafNode's Off() command.

    Off command on SdpMasterLeafNode enables the telescope to perform further operations
    and observations. It Invokes Off command on Sdp Master device.

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
        Method to invoke Off command on Sdp Master.

        """
        ret_code, message = self.init_adapter()
        if ret_code == ResultCode.FAILED:
            return (ret_code, message)

        try:
            self.logger.info(
                f"Invoking Off command on:{self.sdp_master_adapter.dev_name}"
            )
            self.sdp_master_adapter.Off()
            self.logger.info("Off command is successful on Sdp Master device.")
        except Exception as e:
            self.logger.exception(e)
            return self.generate_command_result(
                ResultCode.FAILED,
                f"""The invocation of the Off command is failed on Sdp Master Device {self.sdp_master_adapter.dev_name}.
                Reason: Error in calling the Off command on Sdp Master.
                The command has NOT been executed.
                This device will continue with normal operation.""",
            )
        return (ResultCode.OK, "")
