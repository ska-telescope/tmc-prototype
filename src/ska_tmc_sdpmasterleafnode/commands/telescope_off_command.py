"""
TelescopeOff command class for SDPMasterLeafNode.
"""
from ska_tango_base.commands import ResultCode
from ska_tmc_common.adapters import AdapterFactory

from ska_tmc_sdpmasterleafnode.commands.abstract_command import SdpMLNCommand


class TelescopeOff(SdpMLNCommand):
    """
    A class for SdpMasterLeafNode's TelescopeOff() command.

    TelescopeOff command on SdpMasterLeafNode enables the telescope to perform further operations
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

    def do_mid(self, argin=None):
        """
        Method to invoke Telescope Off command on Sdp Master.

        """
        ret_code, message = self.init_adapters()
        if ret_code == ResultCode.FAILED:
            return ret_code, message

        try:
            self.logger.info(
                f"Invoking TelescopeOff command on:{self.sdp_master_adapter.dev_name}"
            )
            self.sdp_master_adapter.Off()
            self.logger.info("Off command is successful on Sdp Master device.")
        except Exception as e:
            self.logger.exception(e)
            return self.generate_command_result(
                ResultCode.FAILED,
                f"Error in calling Telescope Off Sdp Master Device {self.sdp_master_adapter.dev_name}",
            )
        return (ResultCode.OK, "")
