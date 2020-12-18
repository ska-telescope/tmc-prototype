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
from subarraynode.subarray_node import SubarrayNode


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
            self.restart_sdp(device_data)
            self.restart_csp(device_data)
            self.restart_dsh_grp(device_data)
            self.remove_receptors_when_restart()
            # device.remove_receptors_from_group()
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

    def restart_sdp(self, device_data):
        """
        set up sdp devices
        """
        #Invoke Restart command on SDP Subarray Leaf Node.
        sdp_client = TangoClient(device_data.sdp_subarray_ln_fqdn)
        sdp_client.send_command(const.CMD_RESTART)
        self.logger.info(const.STR_CMD_RESTART_INV_SDP)

    def restart_csp(self, device_data):
        """
        set up csp devices
        """
         #Invoke Restart command on CSP Subarray Leaf Node.
        csp_client = TangoClient(device_data.csp_subarray_ln_fqdn)
        csp_client.send_command(const.CMD_RESTART)
        self.logger.info(const.STR_CMD_RESTART_INV_CSP)

    def restart_dsh_grp(self, device_data):
        # Create proxy for Dish Leaf Node Group 
        dsh_ln_grp_client = TangoGroupClient(device_data._dish_leaf_node_group)
        dsh_ln_grp_client.send_command(const.CMD_RESTART)
        self.logger.info(const.STR_CMD_RESTART_INV_DISH_GROUP)

    def remove_receptors_when_restart(self, device_data):
        # Remove the group for receptors.
        subaraynode_obj = SubarrayNode()
        device_data.subaraynode_obj.remove_receptors_from_group()