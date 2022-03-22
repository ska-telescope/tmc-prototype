"""
On command class for CSPMasterLeafNode.

"""
from ska_tango_base.commands import ResultCode

from ska_tmc_cspmasterleafnode.commands.abstract_command import CspMLNCommand


class On(CspMLNCommand):
    """
    A class for CspMasterLeafNode's On() command.

    On command on CspmasterLeafNode enables the telescope to perform further operations
    and observations. It Invokes On command on Csp Master device.

    """

    def do(self, argin=None):
        """
        Method to invoke On command on Csp Master.

        """
        self.logger.info(
            f"Invoking On command on:{self.csp_master_adapter.dev_name}"
        )
        try:
            self.csp_master_adapter.On()
        except Exception as e:
            self.logger.exception(e)
            return self.generate_command_result(
                ResultCode.FAILED,
                f"""The invocation of the On command is failed on csp Master Device {self.csp_master_adapter.dev_name}.
                This device will continue with normal operation.""",
            )

        self.logger.info("On command is successful on Csp Master device.")
        return (ResultCode.OK, "")
