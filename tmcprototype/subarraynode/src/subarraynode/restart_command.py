"""
Restart Command for SubarrayNode.
"""

# Third party imports
# Tango imports
import tango
from tango import DevFailed

# Additional import
from . import const
from ska.base.commands import ResultCode
from ska.base import SKASubarray
from tmc.common.tango_client import TangoClient
from subarraynode.device_data import DeviceData
from tmc.common.tango_server_helper import TangoServerHelper
# from subarraynode.remove_receptors import RemoveReceptors


class Restart(SKASubarray.RestartCommand):
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
            self.restart_leaf_nodes(device_data.csp_subarray_ln_fqdn, const.STR_CMD_RESTART_INV_CSP)
            self.restart_leaf_nodes(device_data.sdp_subarray_ln_fqdn, const.STR_CMD_RESTART_INV_SDP)
            self.restart_dsh_grp(device_data)
            # remove_receptors = RemoveReceptors()
            # remove_receptors.remove_receptors_from_group()
            device_data.clean_up_dict(self.logger)
            device_data._read_activity_message = const.STR_RESTART_SUCCESS
            self.logger.info(const.STR_RESTART_SUCCESS)
            tango_server_helper_obj = TangoServerHelper.get_instance()
            tango_server_helper_obj.set_status(const.STR_RESTART_SUCCESS)
            device_data.is_restart_command = True
            return (ResultCode.STARTED, const.STR_RESTART_SUCCESS)

        except DevFailed as dev_failed:
            log_msg = const.ERR_RESTART_INVOKING_CMD + str(dev_failed)
            self.logger.exception(log_msg)
            tango.Except.throw_exception(const.STR_RESTART_EXEC,
                                         log_msg,
                                         "SubarrayNode.Restart",
                                         tango.ErrSeverity.ERR)

    def restart_leaf_nodes(self, leaf_node_fqdn, info_string):
        """
        set up sdp devices
        """
        #Invoke Restart command on SDP Subarray Leaf Node.
        sdp_client = TangoClient(leaf_node_fqdn)
        sdp_client.send_command(const.CMD_RESTART)
        self.logger.info(info_string)

    def restart_dsh_grp(self, device_data):
        # Create proxy for Dish Leaf Node Group
        device_data._dish_leaf_node_group_client.send_command(const.CMD_RESTART)
        self.logger.info(const.STR_CMD_RESTART_INV_DISH_GROUP)
