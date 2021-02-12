"""
Off Command class for SubarrayNode
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

class Off(SKASubarray.OffCommand):
    """
    A class for the SubarrayNodes's Off() command.

    This command invokes Off Command on CSPSubarray and SDPSubarray through respective leaf nodes. This comamnd
    changes Subaray device state from ON to OFF.

    """
    def do(self):
        """
        Method to invoke Off command.

        :return: A tuple containing a return code and a string message indicating status.
                 The message is for information purpose only.

        :rtype: (ResultCode, str)

        :raises: DevFailed if the command execution is not successful

        """
        device_data = DeviceData.get_instance()
        device_data.is_restart_command = False
        device_data.is_release_resources = False
        device_data.is_abort_command = False
        device_data.is_obsreset_command = False
        try:
            csp_subarray_proxy = TangoClient(device_data.csp_subarray_ln_fqdn)
            csp_subarray_proxy.send_command("Off")
            sdp_subarray_proxy = TangoClient(device_data.sdp_subarray_ln_fqdn)
            sdp_subarray_proxy.send_command("Off")
            
            message = "Off command completed OK"
            self.logger.info(message)

            # TODO unsubscribe health obsState events from CSP and SDP
            device_data.health_state_aggr.unsubscribe()
            device_data.obs_state_aggr.unsubscribe()
            device_data.receive_addresses.unsubscribe()
            return (ResultCode.OK, message)

        except DevFailed as dev_failed:
            log_msg = const.ERR_INVOKING_OFF_CMD + str(dev_failed)
            self.logger.error(log_msg)
            device_data._read_activity_message = log_msg
            tango.Except.throw_exception(dev_failed[0].desc, "Failed to invoke Off command on SubarrayNode.",
                                         "SubarrayNode.Off()", tango.ErrSeverity.ERR)
