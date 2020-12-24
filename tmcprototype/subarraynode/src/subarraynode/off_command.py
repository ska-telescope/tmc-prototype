"""
OffCommand class for SubarrayNode
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


class OffCommand(SKASubarray.OffCommand):
    """
    A class for the SubarrayNodes's Off() command.
    """
    def do(self):
        """
        This command invokes Off Command on CSPSubarray and SDPSubarray through respective leaf nodes. This comamnd
        changes Subaray device state from ON to OFF.

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
            device_data._csp_subarray_ln_proxy.Off()
            device_data._sdp_subarray_ln_proxy.Off()
            message = "Off command completed OK"
            self.logger.info(message)

            # TODO unsubscribe health obsState events from CSP and SDP
            device_data._unsubscribe_csp_sdp_state_events(device_data._cspSdpLnHealthEventID)
            device_data._unsubscribe_csp_sdp_state_events(device_data._cspSdpLnObsStateEventID)
            device_data._cspSdpLnHealthEventID.clear()  # Clear eventID dictionary
            device_data._cspSdpLnObsStateEventID.clear()
            return (ResultCode.OK, message)

        except DevFailed as dev_failed:
            log_msg = const.ERR_INVOKING_OFF_CMD + str(dev_failed)
            self.logger.error(log_msg)
            self._read_activity_message = log_msg
            tango.Except.throw_exception(dev_failed[0].desc, "Failed to invoke Off command on SubarrayNode.",
                                         "SubarrayNode.Off()", tango.ErrSeverity.ERR)
