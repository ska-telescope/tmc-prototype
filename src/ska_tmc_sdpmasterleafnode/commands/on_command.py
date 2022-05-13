"""
On command class for SDPMasterLeafNode.

"""
from ska_tango_base.commands import ResultCode

from ska_tmc_sdpmasterleafnode.commands.abstract_command import SdpMLNCommand


class On(SdpMLNCommand):
    """
    A class for SdpMasterLeafNode's On() command.

    On command on SdpmasterLeafNode enables the telescope to perform
    further operations and observations.
    It Invokes On command on Sdp Master device.

    """

    def do(self, argin=None):
        """
        Method to invoke On command on Sdp Master.

        """
        return_code, message = self.init_adapter()
        if return_code == ResultCode.FAILED:
            return (return_code, message)
        self.logger.info(
            f"""Invoking On command on:
            {self.sdp_master_adapter.dev_name}"""
        )
        try:
            self.sdp_master_adapter.On()
        except Exception as e:
            self.logger.exception(e)
            return self.generate_command_result(
                ResultCode.FAILED,
                f"""The invocation of the On command is failed on Sdp
                Master Device {self.sdp_master_adapter.dev_name}.
                Reason: Error in calling the On command on Sdp Master.
                The command has NOT been executed.
                This device will continue with normal operation.""",
            )

        self.logger.info("On command is successful on Sdp Master device.")
        return (ResultCode.OK, "")
