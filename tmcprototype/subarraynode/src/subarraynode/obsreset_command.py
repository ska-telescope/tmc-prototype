"""
ObsResetCommand for SubarrayNode.
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
from subarraynode.device_data import DeviceData
from .tango_server_helper import TangoServerHelper


class ObsResetCommand(SKASubarray.ObsResetCommand):
    """
    A class for SubarrayNode's ObsReset() command.
    """

    def do(self):
        """
        This command invokes ObsReset command on CspSubarrayLeafNode, SdpSubarrayLeafNode and DishLeafNode.

        :return: A tuple containing a return code and a string
            message indicating status. The message is for
            information purpose only.

        :rtype: (ResultCode, str)

        :raises: DevFailed if error occurs while invoking command on CspSubarrayLeafNode, SdpSubarrayLeafNode or
                DishLeafNode.
        """
        device_data = DeviceData.get_instance()
        device_data.is_abort_command = False
        try:
            self.logger.info("ObsReset command invoked on SubarrayNode.")
            # As a part of ObsReset clear the attributes on SubarrayNode
            device_data._scan_id = ""
            device_data._sb_id = ""
            device_data.scan_duration = 0
            device_data._scan_type = ""
            self.obsreset_sdp(device_data)
            self.obsreset_csp(device_data)
            self.obsreset_dsh_grp(device_data)
            
            #TODO:
            # device._dish_leaf_node_group.command_inout(const.CMD_OBSRESET)
            self.logger.info(const.STR_CMD_OBSRESET_INV_DISH_GROUP)
            device_data._read_activity_message = const.STR_OBSRESET_SUCCESS
            self.logger.info(const.STR_OBSRESET_SUCCESS)
            tango_server_helper_obj = TangoServerHelper.get_instance()
            tango_server_helper_obj.set_status(const.STR_OBSRESET_SUCCESS)
            device_data.is_obsreset_command = True
            return (ResultCode.STARTED, const.STR_OBSRESET_SUCCESS)

        except DevFailed as dev_failed:
            log_msg = const.ERR_OBSRESET_INVOKING_CMD + str(dev_failed)
            self.logger.exception(log_msg)
            tango.Except.throw_exception(const.STR_OBSRESET_EXEC,
                                         log_msg,
                                         "SKASubarray.ObsResetCommand",
                                         tango.ErrSeverity.ERR)

    def obsreset_sdp(self, device_data):
        """
        set up sdp devices
        """
        #Invoke ObsReset command on SDP Subarray Leaf Node.
        sdp_client = TangoClient(device_data.sdp_subarray_ln_fqdn)
        sdp_client.send_command(const.CMD_OBSRESET)
        self.logger.info(const.STR_CMD_OBSRESET_INV_SDP)

    def obsreset_csp(self, device_data):
        """
        set up csp devices
        """
        #Invoke ObsReset command on CSP Subarray Leaf Node.
        csp_client = TangoClient(device_data.csp_subarray_ln_fqdn)
        csp_client.send_command(const.CMD_OBSRESET)
        self.logger.info(const.STR_CMD_OBSRESET_INV_CSP)

    def obsreset_dsh_grp(self, device_data):
        # Invoke ObsReset command on group of Dishes.
        # dsh_leaf_node_client = TangoGroupClient(device_data._dish_leaf_node_group)
        device_data._dish_leaf_node_group_client.send_command(const.CMD_OBSRESET)
        self.logger.info(const.STR_CMD_OBSRESET_INV_DISH_GROUP)