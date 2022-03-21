"""
Off command class for CSPMasterLeafNode.
"""
from ska_tango_base.commands import ResultCode

from ska_tmc_cspmasterleafnode.commands.abstract_command import CspMLNCommand


class Off(CspMLNCommand):
    """
    A class for CspMasterLeafNode's Off() command.

    Off command on CspMasterLeafNode enables the telescope to perform further operations
    and observations. It Invokes Off command on Csp Master device.

    """

    def do(self, argin=None):
        """
        Method to invoke Off command on Csp Master.

        """
        return_code, message = self.init_adapter()
        if return_code == ResultCode.FAILED:
            return (return_code, message)

        self.logger.info(
            f"""Invoking Off command on:
            {self.csp_master_adapter.dev_name}"""
        )
        try:
            self.csp_master_adapter.Standby()
        except Exception as e:
            self.logger.exception(e)
            return self.generate_command_result(
                ResultCode.FAILED,
                f"""The invocation of the Off command is failed on Csp Master Device {self.csp_master_adapter.dev_name}.
                Reason: Error in calling the Off command on Csp Master.
                The command has NOT been executed.
                This device will continue with normal operation.""",
            )

        self.logger.info("Off command is successful on Csp Master device.")
        return (ResultCode.OK, "")
