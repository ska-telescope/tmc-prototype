"""
Abort Command for SubarrayNode.
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
from subarraynode.device_data import DeviceData
from . import const

class Abort(SKASubarray.AbortCommand):
    """
    A class for SubarrayNode's Abort() command.

    This command on Subarray Node invokes Abort command on CSP Subarray Leaf Node and SDP
    Subarray Leaf Node, and stops tracking of all the assigned dishes.

    """
    def do(self):
        """
        Method to invoke Abort command.

        return:
            A tuple containing a return code and a string
            message indicating status. The message is for
            information purpose only.

        rtype:
            (ResultCode, str)

        raises:
            DevFailed if error occurs in invoking command on any of the devices like CSPSubarrayLeafNode,
            SDPSubarrayLeafNode or DishLeafNode
        """
        device_data = DeviceData.get_instance()
        device_data.is_release_resources = False
        device_data.is_restart_command = False
        device_data.is_end_command = False
        device_data.is_obsreset_command = False
        try:
            if device_data.scan_timer_handler.is_scan_running():
                device_data.scan_timer_handler.stop_scan_timer()
            self.abort_sdp(device_data)
            self.abort_csp(device_data)
            self.abort_dishes(device_data)
            self.logger.info(const.STR_ABORT_SUCCESS)
            device_data._read_activity_message = const.STR_ABORT_SUCCESS
            tango_server_helper = TangoServerHelper.get_instance()
            tango_server_helper.set_status(const.STR_ABORT_SUCCESS)
            device_data.is_abort_command = True
            return (ResultCode.STARTED, const.STR_ABORT_SUCCESS)

        except DevFailed as dev_failed:
            log_msg = const.ERR_ABORT_INVOKING_CMD + str(dev_failed)
            self.logger.exception(dev_failed)
            tango.Except.throw_exception(const.ERR_ABORT_INVOKING_CMD,
                                         log_msg,
                                         "SubarrayNode.Abort",
                                         tango.ErrSeverity.ERR)

    def abort_sdp(self, device_data):
        """
        set up sdp devices
        """
        #Invoke Abort command on SDP Subarray Leaf Node.
        sdp_client = TangoClient(device_data.sdp_subarray_ln_fqdn)
        sdp_client.send_command(const.CMD_ABORT)
        self.logger.info(const.STR_CMD_ABORT_INV_SDP)

    def abort_csp(self, device_data):
        """
        set up csp devices
        """
         #Invoke Abort command on CSP Subarray Leaf Node.
        csp_client = TangoClient(device_data.csp_subarray_ln_fqdn)
        csp_client.send_command(const.CMD_ABORT)
        self.logger.info(const.STR_CMD_ABORT_INV_CSP)

    def abort_dishes(self, device_data):
         # Create proxy for Dish Leaf Node Group
        device_data._dish_leaf_node_group_client.send_command(const.CMD_ABORT)