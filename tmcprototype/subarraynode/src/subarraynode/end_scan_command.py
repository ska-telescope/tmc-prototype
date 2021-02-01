"""
EndScan Command class for SubarrayNode.
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
from tmc.common.tango_server_helper import TangoServerHelper
from subarraynode.device_data import DeviceData


class EndScan(SKASubarray.EndScanCommand):
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
            if device_data.scan_timer_handler.is_scan_running():
                device_data.scan_timer_handler.stop_scan_timer()
            device_data.isScanRunning = False
            device_data.is_scan_completed = True

            self.endscan_sdp(device_data)
            self.endscan_csp(device_data)
            device_data._scan_id = ""
            # TODO: For Future Use
            # check whether csp and sdp are in idle ObsState and if dishes are assigned calculate ObsState.
            tango_server_helper_obj = TangoServerHelper.get_instance()
            tango_server_helper_obj.set_status(const.STR_SCAN_COMPLETE)
            self.logger.info(const.STR_SCAN_COMPLETE)
            device_data._read_activity_message = const.STR_END_SCAN_SUCCESS
            return (ResultCode.OK, const.STR_END_SCAN_SUCCESS)

        except DevFailed as dev_failed:
            log_msg = f"{const.ERR_END_SCAN_CMD_ON_GROUP}{dev_failed}"
            self.logger.exception(dev_failed)
            tango.Except.throw_exception(
                const.STR_END_SCAN_EXEC,
                log_msg,
                "SubarrayNode.EndScan",
                tango.ErrSeverity.ERR,
            )

    def endscan_sdp(self, device_data):
        """
        EndScan command on SDP Subarray Leaf Node
        """
        sdp_client = TangoClient(device_data.sdp_subarray_ln_fqdn)
        sdp_client.send_command(const.CMD_END_SCAN)
        self.logger.debug(const.STR_SDP_END_SCAN_INIT)
        device_data._read_activity_message = const.STR_SDP_END_SCAN_INIT

    def endscan_csp(self, device_data):
        """
        EndScan command on CSP Subarray Leaf Node
        """
        csp_client = TangoClient(device_data.csp_subarray_ln_fqdn)
        csp_client.send_command(const.CMD_END_SCAN)
        self.logger.debug(const.STR_CSP_END_SCAN_INIT)
        device_data._read_activity_message = const.STR_CSP_END_SCAN_INIT
