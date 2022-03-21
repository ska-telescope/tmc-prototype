from ska_tango_base.commands import ResultCode

from ska_tmc_cspmasterleafnode.commands.abstract_command import CspMLNCommand


class Standby(CspMLNCommand):
    """
    A class for CspMasterLeafNode's Standby() command.

    Standby command on CspMasterLeafNode invokes Standby command on Csp Master device.

    """

    def do(self, argin=None):
        """
        Method to invoke Standby command on Csp Master.

        """
        return_code, message = self.init_adapter()
        if return_code == ResultCode.FAILED:
            return (return_code, message)
        self.logger.info(
            f"Invoking Standby command on:{self.csp_master_adapter.dev_name}"
        )
        try:
            self.csp_master_adapter.Standby()
        except Exception as e:
            self.logger.exception(e)
            return self.generate_command_result(
                ResultCode.FAILED,
                f"""The invocation of the Standby command is failed on Csp Master Device {self.csp_master_adapter.dev_name}.
                Reason: Error in calling the Standby command on Csp Master.
                The command has NOT been executed.
                This device will continue with normal operation.""",
            )
        self.logger.info("Standby command is successful on Csp Master device.")
        return (ResultCode.OK, "")
