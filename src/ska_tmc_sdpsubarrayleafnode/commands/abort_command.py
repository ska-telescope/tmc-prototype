"""
Abort Command for Sdp Subarray.
"""

from typing import Tuple

from ska_tango_base.commands import ResultCode

from ska_tmc_sdpsubarrayleafnode.commands.sdp_sln_command import SdpSLNCommand


class Abort(SdpSLNCommand):
    """
    A class for Sdp Subarray Abort() command.
    Aborts the Sdp Subarray device.
    """

    # pylint: disable=arguments-differ
    def do(self) -> Tuple[ResultCode, str]:
        """
        This method invokes Abort command on Sdp Subarray

        return:
            A tuple containing a return code and a string
            message indicating status.
            The message is for information purpose only.

        rtype:
            (ResultCode, str)

        raises:
            Exception if error occurs in invoking command
            on any of the devices like Sdp Subarray
        """
        result_code, message = self.init_adapter()
        if result_code == ResultCode.FAILED:
            return result_code, message
        try:
            self.logger.info(
                "Command Id : %s | Invoking Abort command on Sdp Subarray:%s",
                self.component_manager.command_id,
                self.sdp_subarray_adapter.dev_name,
            )
            self.sdp_subarray_adapter.Abort()
        except Exception as exception:
            self.logger.exception(
                "Command Id : %s | "
                "Failed to invoke Abort Command "
                + "on device: %s."
                + " with exception: %s",
                self.component_manager.command_id,
                self.sdp_subarray_adapter.dev_name,
                exception,
            )

            return self.component_manager.generate_command_result(
                ResultCode.FAILED,
                "Execution of Abort command is failed."
                + "Reason: Error in invoking Abort command on Sdp Subarray -"
                + f"{self.sdp_subarray_adapter.dev_name}: {exception}",
            )
        return (ResultCode.OK, "Command Completed")
