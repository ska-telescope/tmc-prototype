"""
EndScanCommand class for SubarrayNode.
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


class EndScanCommand(SKASubarray.EndScanCommand):
    """
    A class for SubarrayNode's EndScan() command.
    """
    def do(self):
        """
        Ends the scan. It is invoked on subarray after completion of the scan duration. It can
        also be invoked by an external client while a scan is in progress, Which stops the scan
        immediately irrespective of the provided scan duration.

        :return: A tuple containing a return code and a string message indicating status.
        The message is for information purpose only.

        :rtype: (ReturnCode, str)

        :raises: DevFailed if the command execution is not successful.
        """
        device_data = DeviceData.get_instance()
        device_data.is_release_resources = False
        device_data.is_restart_command = False
        device_data.is_abort_command = False
        device_data.is_obsreset_command = False
        try:
            if device_data.scan_thread:
                if device_data.scan_thread.is_alive():
                    device_data.scan_thread.cancel()  # stop timer when EndScan command is called
            device_data.isScanRunning = False
            device_data.is_scan_completed = True
            
            self.endscan_sdp()
            self.endscan_csp()
            device_data._scan_id = ""
            # TODO: For Future Use
            # if device._csp_sa_obs_state == ObsState.IDLE and device._sdp_sa_obs_state ==\
            #         ObsState.IDLE:
            #     if len(device.dishPointingStateMap.values()) != 0:
            #         device.calculate_observation_state()
            device_data.set_status(const.STR_SCAN_COMPLETE)
            self.logger.info(const.STR_SCAN_COMPLETE)
            device_data._read_activity_message = const.STR_END_SCAN_SUCCESS
            return (ResultCode.OK, const.STR_END_SCAN_SUCCESS)

        except DevFailed as dev_failed:
            log_msg = const.ERR_END_SCAN_CMD_ON_GROUP + str(dev_failed)
            self.logger.exception(dev_failed)
            tango.Except.throw_exception(const.STR_END_SCAN_EXEC,
                                         log_msg,
                                         "SubarrayNode.EndScanCommand",
                                         tango.ErrSeverity.ERR)

    def endscan_sdp(self, device_data):
        """
        set up sdp devices
        """
        # Invoke EndScan command on SDP Subarray Leaf Node
        sdp_client = TangoClient(device_data.sdp_subarray_ln_fqdn)
        sdp_client.send_command(const.CMD_END_SCAN)
        self.logger.debug(const.STR_SDP_END_SCAN_INIT)
        device_data._read_activity_message = const.STR_SDP_END_SCAN_INIT

    def endscan_csp(self, device_data):
        """
        set up csp devices
        """
        # Invoke EndScan command on CSP Subarray Leaf Node
        csp_client = TangoClient(device_data.csp_subarray_ln_fqdn)
        csp_client.send_command(const.CMD_END_SCAN)
        self.logger.debug(const.STR_CSP_END_SCAN_INIT)
        device_data._read_activity_message = const.STR_CSP_END_SCAN_INIT