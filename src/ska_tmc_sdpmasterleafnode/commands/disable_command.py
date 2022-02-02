"""
Disable command class for SDPMasterLeafNode.
"""
from ska_tango_base.commands import ResultCode
from ska_tmc_common.adapters import AdapterFactory

from ska_tmc_sdpmasterleafnode.commands.abstract_command import (
    AbstractCommand,
)


class Disable(AbstractCommand):
    """
    A class for SdpMasterLeafNode's Disable() command.

    Disable command on SdpMasterLeafNode invokes disable command on Sdp Master device.

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
        Method to invoke Disable command on Sdp Master.

        """
        ret_code, message = self.init_adapters()
        if ret_code == ResultCode.FAILED:
            return ret_code, message

        try:
            self.logger.info(
                f"Invoking Disable command on:{self.sdp_master_adapter.dev_name}"
            )
            self.sdp_master_adapter.Disable()
            self.logger.info(
                "Disable command is successful on Sdp Master device."
            )
        except Exception as e:
            return self.generate_command_result(
                ResultCode.FAILED,
                f"Error in calling Disable command on Sdp Master Device {self.sdp_master_adapter.dev_name}: {e}",
            )
        return (ResultCode.OK, "")
