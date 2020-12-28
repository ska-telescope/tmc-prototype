"""
EndCommand class for SubarrayNode.
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


class EndCommand(SKASubarray.EndCommand):
    """
    A class for SubarrayNode's End() command.
    """
    def do(self):
        """
        This command on Subarray Node invokes EndSB command on CSP Subarray Leaf Node and SDP
        Subarray Leaf Node, and stops tracking of all the assigned dishes.

        :return: A tuple containing a return code and a string message indicating status.
        The message is for information purpose only.

        :rtype: (ResultCode, str)

        :raises: DevFailed if the command execution is not successful.
        """
        self.logger.info(type(self.target))
        device_data = DeviceData.get_instance()
        device_data = self.target
        device_data.is_end_command = False
        device_data.is_release_resources = False
        device_data.is_restart_command = False
        device_data.is_abort_command = False
        device_data.is_obsreset_command = False
        
        try:
            self.logger.info("End command invoked on SubarrayNode.")
            self.end_sdp(device_data)
            self.end_csp(device_data)
            self.stop_dish_tracking()
            device_data._read_activity_message = const.STR_ENDSB_SUCCESS
            self.logger.info(const.STR_ENDSB_SUCCESS)
            device_data.set_status(const.STR_ENDSB_SUCCESS)
            device_data.is_end_command = True
            return (ResultCode.OK, const.STR_ENDSB_SUCCESS)
        except DevFailed as dev_failed:
            log_msg = const.ERR_ENDSB_INVOKING_CMD + str(dev_failed)
            self.logger.exception(log_msg)
            tango.Except.throw_exception(const.STR_ENDSB_EXEC,
                                         log_msg,
                                         "SubarrayNode.EndCommand",
                                         tango.ErrSeverity.ERR)

    def end_sdp(self, device_data):
        """
        set up sdp devices
        """
        #To read device proxy from device.SdpSubarrayLNFQDN
        sdp_saln_client = TangoClient(device_data.sdp_subarray_ln_fqdn)
        sdp_saln_client.send_command(const.CMD_END)
        self.logger.info(const.STR_CMD_END_INV_SDP)

    def end_csp(self, device_data):
        """
        set up csp devices
        """
        #To read device proxy from device.CspSubarrayLNFQDN
        csp_saln_client = TangoClient(device_data.csp_subarray_ln_fqdn)
        csp_saln_client.send_command(const.CMD_GOTOIDLE)
        self.logger.info(const.STR_CMD_GOTOIDLE_INV_CSP)

    def stop_dish_tracking(self, device_data):
        # TODO: Getting exception while running test cases using device mocking
        dsh_leaf_node_client = TangoGroupClient(device_data._dish_leaf_node_group)
        dsh_leaf_node_client.send_command(const.CMD_STOP_TRACK)
        self.logger.info(const.STR_CMD_STOP_TRACK_INV_DLN)

    