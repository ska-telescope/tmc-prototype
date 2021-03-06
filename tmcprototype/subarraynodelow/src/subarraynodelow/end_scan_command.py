"""
EndScanCommand class for SubarrayNodeLow.
"""

# Third party imports
# Tango imports
import tango
from tango import DevFailed

# Additional import
from ska.base.commands import ResultCode
from ska.base import SKASubarray
from tmc.common.tango_client import TangoClient
from . import const


class EndScan(SKASubarray.EndScanCommand):
    """
    A class for SubarrayNodeLow's EndScan() command.
    """
    def do(self):
        """
        Ends the scan. It is invoked on subarrayLow after completion of the scan duration. It can
        also be invoked by an external client while a scan is in progress, Which stops the scan
        immediately irrespective of the provided scan duration.

        :return: A tuple containing a return code and a string message indicating status.
        The message is for information purpose only.

        :rtype: (ReturnCode, str)

        :raises: DevFailed if the command execution is not successful.
        """
        device_data = self.target
        device_data.is_release_resources = False
        try:
            if device_data.scan_timer_handler.is_scan_running():
                device_data.scan_timer_handler.stop_scan_timer() # stop timer when EndScan command is called
            device_data.isScanRunning = False
            device_data.is_scan_completed = True
            mccs_subarray_ln_client = TangoClient(device_data.mccs_subarray_ln_fqdn)
            mccs_subarray_ln_client.send_command(const.CMD_END_SCAN)
            self.logger.debug(const.STR_MCCS_END_SCAN_INIT)
            device_data.activity_message = const.STR_MCCS_END_SCAN_INIT
            device_data._scan_id = ""
            # device.set_status(const.STR_SCAN_COMPLETE)
            self.logger.info(const.STR_SCAN_COMPLETE)
            device_data.activity_message = const.STR_END_SCAN_SUCCESS
            return (ResultCode.OK, const.STR_END_SCAN_SUCCESS)

        except DevFailed as dev_failed:
            log_msg = const.ERR_END_SCAN_CMD_ON_MCCS + str(dev_failed)
            self.logger.exception(dev_failed)
            tango.Except.throw_exception(const.STR_END_SCAN_EXEC,
                                         log_msg,
                                         "SubarrayNode.EndScanCommand",
                                         tango.ErrSeverity.ERR)
