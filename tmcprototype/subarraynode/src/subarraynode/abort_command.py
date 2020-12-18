"""
AbortCommand for SubarrayNode.
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


class AbortCommand(SKASubarray.AbortCommand):
    """
    A class for SubarrayNode's Abort() command.
    """
    def do(self):
        """
        This command on Subarray Node invokes Abort command on CSP Subarray Leaf Node and SDP
        Subarray Leaf Node, and stops tracking of all the assigned dishes.

        :return: A tuple containing a return code and a string
            message indicating status. The message is for
            information purpose only.
        :rtype: (ResultCode, str)

        :raises: DevFailed if error occurs in invoking command on any of the devices like CSPSubarrayLeafNode,
                SDPSubarrayLeafNode or DishLeafNode
        """
        device_data = DeviceData.get_instance()
        device_data.is_release_resources = False
        device_data.is_restart_command = False
        device_data.is_end_command = False
        device_data.is_obsreset_command = False
        try:
            if device_data.scan_thread:
                if device_data.scan_thread.is_alive():
                    device_data.scan_thread.cancel()  # stop timer when EndScan command is called
            self.abort_sdp(device_data)
            self.abort_csp(device_data)
            self.abort_dish_grp(device_data)
            self.logger.info(const.STR_ABORT_SUCCESS)
            device_data._read_activity_message = const.STR_ABORT_SUCCESS
            
            device_data.set_status(const.STR_ABORT_SUCCESS)
            device_data.is_abort_command = True
            return (ResultCode.STARTED, const.STR_ABORT_SUCCESS)

        except DevFailed as dev_failed:
            log_msg = const.ERR_ABORT_INVOKING_CMD + str(dev_failed)
            self.logger.exception(dev_failed)
            tango.Except.throw_exception(const.ERR_ABORT_INVOKING_CMD,
                                         log_msg,
                                         "SubarrayNode.AbortCommand",
                                         tango.ErrSeverity.ERR)

    def abort_sdp(self, device_data):
        """
        set up sdp devices
        """
        #Invoke Abort command on SDP Subarray Leaf Node.
        sdp_client = TangoClient(device_data.sdp_subarray_ln_fqdn)
        sdp_client.send_command(CMD_ABORT)
        self.logger.info(const.STR_CMD_ABORT_INV_SDP)

    def abort_csp(self, device_data):
        """
        set up csp devices
        """
         #Invoke Abort command on CSP Subarray Leaf Node.
        csp_client = TangoClient(device_data.csp_subarray_ln_fqdn)
        csp_client.send_command(CMD_ABORT)
        self.logger.info(const.STR_CMD_ABORT_INV_CSP)

    def abort_dish_grp(self, device_data):
         # Create proxy for Dish Leaf Node Group 
        dsh_ln_grp_client = TangoGroupClient(device_data._dish_leaf_node_group)
        dsh_ln_grp_client.send_command(const.CMD_ABORT)