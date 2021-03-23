"""
ObsReset Command for SubarrayNode.
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


class ObsReset(SKASubarray.ObsResetCommand):
    """
    A class for Low SubarrayNode's ObsReset() command.

    This command invokes ObsReset command on Mccs Subarray Leaf Node.

    """

    def do(self):
        """
        Method to invoke ObsReset command.

        return:
            A tuple containing a return code and a string
            message indicating status. The message is for
            information purpose only.

        rtype:
            (ResultCode, str)

        raises:
            DevFailed if error occurs while invoking command on MccsSubarrayLeafNode.
        """
        device_data = self.target
        device_data.is_abort_command_executed = False
        this_server = TangoServerHelper.get_instance()
        try:
            self.logger.info("ObsReset command invoked on SubarrayNodeLow.")
            mccs_subarray_ln_fqdn = this_server.read_property("MccsSubarrayLNFQDN")
            mccs_subarray_ln_client = TangoClient(mccs_subarray_ln_fqdn)
            mccs_subarray_ln_client.send_command(const.CMD_OBSRESET)
            this_server.write_attr("activityMessage", const.STR_OBSRESET_SUCCESS)
            self.logger.info(const.STR_OBSRESET_SUCCESS)
            this_server.set_status(const.STR_OBSRESET_SUCCESS)
            device_data.is_obsreset_command_executed = True
            return (ResultCode.STARTED, const.STR_OBSRESET_SUCCESS)

        except DevFailed as dev_failed:
            log_msg = f"{const.ERR_OBSRESET_INVOKING_CMD}{dev_failed}"
            self.logger.exception(log_msg)
            tango.Except.throw_exception(
                const.STR_OBSRESET_EXEC,
                log_msg,
                "SKASubarrayLow.ObsReset",
                tango.ErrSeverity.ERR,
            )
