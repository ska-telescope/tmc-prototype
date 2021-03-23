"""
EndCommand class for SubarrayNodeLow.
"""

# Third party imports
# Tango imports
import tango
from tango import DevFailed

# Additional import
from ska.base.commands import ResultCode
from ska.base import SKASubarray

from tmc.common.tango_client import TangoClient
from tmc.common.tango_server_helper import TangoServerHelper

from . import const


class End(SKASubarray.EndCommand):
    """
    A class for SubarrayNodeLow's End() command.

    This command on Subarray Node Low invokes End command on MCCS Subarray Leaf Node.

    """

    def do(self):
        """
        Method to invoke End command.

        return:
            A tuple containing a return code and a string message indicating status.
            The message is for information purpose only.

        rtype:
            (ResultCode, str)

        raises:
            DevFailed if the command execution is not successful.
        """
        device = self.target
        device.is_end_command = False
        device.is_release_resources = False
        device.is_abort_command_executed = False
        device.is_obsreset_command_executed = False
        this_server = TangoServerHelper.get_instance()
        try:
            self.logger.info(const.STR_END_CMD_INVOKED_SA_LOW)
            mccs_subarray_ln_fqdn = this_server.read_property("MccsSubarrayLNFQDN")
            mccs_subarray_ln_client = TangoClient(mccs_subarray_ln_fqdn)
            mccs_subarray_ln_client.send_command(const.CMD_END)
            self.logger.info(const.STR_CMD_END_INV_MCCS)
            this_server.write_attr("activityMessage", const.STR_END_SUCCESS)
            self.logger.info(const.STR_END_SUCCESS)
            device.is_end_command = True
            return (ResultCode.OK, const.STR_END_SUCCESS)

        except DevFailed as dev_failed:
            log_msg = f"{const.ERR_END_INVOKING_CMD}{dev_failed}"
            self.logger.exception(log_msg)
            tango.Except.throw_exception(
                const.STR_END_EXEC,
                log_msg,
                "SubarrayNode.EndCommand",
                tango.ErrSeverity.ERR,
            )
