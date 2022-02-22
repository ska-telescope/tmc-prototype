"""
Standby command class for SDPMasterLeafNode.
"""
from ska_tango_base.commands import ResultCode

from ska_tmc_sdpmasterleafnode.commands.abstract_command import SdpMLNCommand


class Standby(SdpMLNCommand):
    """
    A class for SdpMasterLeafNode's Standby() command.

    Standby command on SdpMasterLeafNode invokes Standby command on Sdp Master device.

    """

    def do(self, argin=None):
        """
        Method to invoke Standby command on Sdp Master.

        """
        return_code, message = self.init_adapter()
        if return_code == ResultCode.FAILED:
            return (return_code, message)

        try:
            self.logger.info(
                f"Invoking Standby command on:{self.sdp_master_adapter.dev_name}"
            )
            self.sdp_master_adapter.Standby()
            self.logger.info(
                "Standby command is successful on Sdp Master device."
            )
        except Exception as e:
            self.logger.exception(e)
            return self.generate_command_result(
                ResultCode.FAILED,
                f"""The invocation of the Standby command is failed on Sdp Master Device {self.sdp_master_adapter.dev_name}.
                Reason: Error in calling the Standby command on Sdp Master.
                The command has NOT been executed.
                This device will continue with normal operation.""",
            )
        return (ResultCode.OK, "")
