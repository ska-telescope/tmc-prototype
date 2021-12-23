"""
Restart Command for SubarrayNode.
"""

# Third party imports
# Tango imports
import tango
from ska.base import SKASubarray

# Additional import
from ska.base.commands import ResultCode
from tango import DevFailed
from tmc.common.tango_client import TangoClient
from tmc.common.tango_server_helper import TangoServerHelper

from . import const


class Restart(SKASubarray.RestartCommand):
    """
    A class for SubarrayNode's Restart() command.

    This command on Subarray Node Low invokes Restart command on MCCS Subarray Leaf Node and restarts the ongoing
    activity.

    """

    def do(self):
        """
        Method to invoke Restart command.

        return:
            A tuple containing a return code and a string
            message indicating status. The message is for
            information purpose only.

        rtype:
            (ResultCode, str)

        raises:
            DevFailed if error occurs while invoking command on MCCS Subarray Leaf Node.
        """
        device_data = self.target
        device_data.is_release_resources_command_executed = False
        device_data.is_abort_command_executed = False
        device_data.is_obsreset_command_executed = False
        try:
            this_server = TangoServerHelper.get_instance()
            property_val = this_server.read_property("MccsSubarrayLNFQDN")[0]
            self.logger.info("Restart command invoked on SubarrayNodeLow")
            self.restart_leaf_nodes(
                property_val, const.STR_CMD_RESTART_INV_MCCS
            )
            device_data._read_activity_message = const.STR_RESTART_SUCCESS
            this_server.set_status(const.STR_RESTART_SUCCESS)
            device_data.is_restart_command_executed = True
            return (ResultCode.STARTED, const.STR_RESTART_SUCCESS)

        except DevFailed as dev_failed:
            log_msg = f"{const.ERR_RESTART_INVOKING_CMD}{dev_failed}"
            self.logger.exception(log_msg)
            tango.Except.throw_exception(
                const.STR_RESTART_EXEC,
                log_msg,
                "SubarrayNode.Restart",
                tango.ErrSeverity.ERR,
            )

    def restart_leaf_nodes(self, leaf_node_fqdn, info_string):
        """
        set up mccs devices
        """
        # Invoke Restart command on MCCS Subarray Leaf Node.
        mccs_subarray_client = TangoClient(leaf_node_fqdn)
        mccs_subarray_client.send_command(const.CMD_RESTART)
        self.logger.info(info_string)
        self.logger.info(const.STR_RESTART_SUCCESS)
