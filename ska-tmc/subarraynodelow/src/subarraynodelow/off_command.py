"""
OffCommand class for SubarrayNodeLow
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
from .assigned_resources_maintainer import AssignedResourcesMaintainer

from . import const


class Off(SKASubarray.OffCommand):
    """
    A class for the SubarrayNodes's Off() command.

    This command invokes Off Command on MCCS Subarray through Mccs Subarray leaf node. This comamnd
    changes Subaray device state from ON to OFF.

    """

    def do(self):
        """
        Method to invoke Off command.

        return:
            A tuple containing a return code and a string message indicating status.
            The message is for information purpose only.

        rtype:
            (ResultCode, str)

        raises:
            DevFailed if the command execution is not successful
        """
        device = self.target
        device.is_release_resources = False
        device.is_abort_command_executed = False
        device.is_obsreset_command_executed = False
        this_server = TangoServerHelper.get_instance()
        try:
            mccs_subarray_ln_fqdn = ""
            property_val = this_server.read_property("MccsSubarrayLNFQDN")
            mccs_subarray_ln_fqdn = mccs_subarray_ln_fqdn.join(property_val)
            mccs_subarray_ln_client = TangoClient(mccs_subarray_ln_fqdn)
            mccs_subarray_ln_client.send_command(const.CMD_OFF, None)
            message = "Off command completed OK"
            self.logger.info(message)
            this_server.write_attr("activityMessage", message, False)
            if device.assigned_resources_maintainer == None:
                device.assigned_resources_maintainer = AssignedResourcesMaintainer()
            device.assigned_resources_maintainer.unsubscribe()
            return (ResultCode.OK, message)

        except DevFailed as dev_failed:
            log_msg = f"{const.ERR_INVOKING_OFF_CMD}{dev_failed}"
            self.logger.error(log_msg)
            this_server.write_attr("activityMessage", log_msg, False)
            tango.Except.throw_exception(
                dev_failed[0].desc,
                "Failed to invoke Off command on SubarrayNode.",
                "SubarrayNode.Off()",
                tango.ErrSeverity.ERR,
            )
