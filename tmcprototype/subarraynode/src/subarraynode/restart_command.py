"""
RestartCommand for SubarrayNode.
"""

# Third party imports
# Tango imports
import tango
from tango import DevFailed

# Additional import
from . import const
from ska.base.commands import ResultCode
from ska.base import SKASubarray
from subarraynode.tango_group_client import TangoGroupClient
from subarraynode.tango_client import TangoClient
from subarraynode.DeviceData import DeviceData


class RestartCommand(SKASubarray.RestartCommand):
    """
    A class for SubarrayNode's Restart() command.
    """

    def do(self):
        """
        This command invokes Restart command on CSPSubarrayLeafNode, SDpSubarrayLeafNode and DishLeafNode.

        :return: A tuple containing a return code and a string
            message indicating status. The message is for
            information purpose only.

        :rtype: (ResultCode, str)

        :raises: DevFailed if error occurs while invoking command on CSPSubarrayLeafNode, SDpSubarrayLeafNode or
                DishLeafNode.
        """
        device_data = DeviceData.get_instance()
        device_data.is_release_resources = False
        device_data.is_abort_command = False
        device_data.is_obsreset_command = False
        try:
            self.logger.info("Restart command invoked on SubarrayNode.")
            # As a part of Restart clear the attributes on SubarrayNode
            device_data._scan_id = ""
            device_data._sb_id = ""
            device_data.scan_duration = 0
            device_data._scan_type = ''
            # device._sdp_subarray_ln_proxy.command_inout(const.CMD_RESTART)
            sdp_client = TangoClient(device_data.sdp_subarray_ln_fqdn)
            sdp_client.send_command(const.CMD_RESTART)
            self.logger.info(const.STR_CMD_RESTART_INV_SDP)
            # device._csp_subarray_ln_proxy.command_inout(const.CMD_RESTART)
            csp_client = TangoClient(device_data.csp_subarray_ln_fqdn)
            csp_client.send_command(const.CMD_RESTART)
            self.logger.info(const.STR_CMD_RESTART_INV_CSP)
            #TODO: 
            # device._dish_leaf_node_group.command_inout(const.CMD_RESTART)
            self.logger.info(const.STR_CMD_RESTART_INV_DISH_GROUP)
            # Remove the group for receptors.
            device.remove_receptors_from_group()
            device_data._read_activity_message = const.STR_RESTART_SUCCESS
            self.logger.info(const.STR_RESTART_SUCCESS)
            device_data.set_status(const.STR_RESTART_SUCCESS)
            device_data.is_restart_command = True
            return (ResultCode.STARTED, const.STR_RESTART_SUCCESS)

        except DevFailed as dev_failed:
            log_msg = const.ERR_RESTART_INVOKING_CMD + str(dev_failed)
            self.logger.exception(log_msg)
            tango.Except.throw_exception(const.STR_RESTART_EXEC,
                                         log_msg,
                                         "SubarrayNode.RestartCommand",
                                         tango.ErrSeverity.ERR)
