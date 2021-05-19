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
from tmc.common.tango_server_helper import TangoServerHelper

from . import const
from .device_data import DeviceData


class EndScan(SKASubarray.EndScanCommand):
    """
    A class for SubarrayNodeLow's EndScan() command.

    Ends the scan. It is invoked on Subarray Node Low after completion of the scan duration. It can
    also be invoked by an external client while a scan is in progress, Which stops the scan
    immediately irrespective of the provided scan duration.

    """

    def do(self):
        """
        Method to invoke EndScan command.

        return:
            A tuple containing a return code and a string message indicating status.
            The message is for information purpose only.

        rtype:
            (ReturnCode, str)

        raises:
            DevFailed if the command execution is not successful.
        """
        device_data = DeviceData.get_instance()
        device_data.is_release_resources = False
        device_data.is_abort_command_executed = False
        device_data.is_obsreset_command_executed = False
        device_data.is_restart_command_executed = False
        this_server = TangoServerHelper.get_instance()
        try:
            if device_data.scan_timer_handler.is_scan_running():
                device_data.scan_timer_handler.stop_scan_timer()  # stop timer when EndScan command is called
            device_data.isScanRunning = False
            device_data.is_scan_completed = True
            mccs_subarray_ln_fqdn = ""
            property_val = this_server.read_property("MccsSubarrayLNFQDN")
            mccs_subarray_ln_fqdn = mccs_subarray_ln_fqdn.join(property_val)
            mccs_subarray_ln_client = TangoClient(mccs_subarray_ln_fqdn)
            mccs_subarray_ln_client.send_command(const.CMD_END_SCAN)
            self.logger.debug(const.STR_MCCS_END_SCAN_INIT)
            this_server.write_attr("activityMessage", const.STR_MCCS_END_SCAN_INIT, False)
            this_server.write_attr("scanID", "")
            self.logger.info(const.STR_SCAN_COMPLETE)
            this_server.write_attr("activityMessage", const.STR_END_SCAN_SUCCESS, False)
            return (ResultCode.OK, const.STR_END_SCAN_SUCCESS)

        except DevFailed as dev_failed:
            log_msg = f"{const.ERR_END_SCAN_CMD_ON_MCCS}{dev_failed}"
            self.logger.exception(dev_failed)
            tango.Except.throw_exception(
                const.STR_END_SCAN_EXEC,
                log_msg,
                "SubarrayNode.EndScanCommand",
                tango.ErrSeverity.ERR,
            )
