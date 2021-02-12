"""
Scan Command class for SubarrayNode
"""

# Third party imports
# Tango imports
import tango
from tango import DevFailed

# Additional import
from ska.base.commands import ResultCode
from ska.base import SKASubarray
from tmc.common.tango_server_helper import TangoServerHelper
from tmc.common.tango_client import TangoClient
from . import const
from subarraynode.device_data import DeviceData


class Scan(SKASubarray.ScanCommand):
    """
    A class for SubarrayNode's Scan() command.

    This command accepts id as input. And it Schedule scan on subarray
    from where scan command is invoked on respective CSP and SDP subarray node for the
    provided interval of time. It checks whether the scan is already in progress. If yes it
    throws error showing duplication of command.

    """

    def do(self, argin):
        """
        :param argin: DevString. JSON string containing id.

        JSON string example as follows:

        {"id": 1}

        Note: Above JSON string can be used as an input argument while invoking this command from JIVE.

        :return: A tuple containing a return code and a string message indicating status.
        The message is for information purpose only.

        :rtype: (ReturnCode, str)

        :raises: DevFailed if the command execution is not successful
        """
        device_data = DeviceData.get_instance()
        device_data.is_scan_completed = False
        device_data.is_release_resources = False
        device_data.is_restart_command = False
        device_data.is_abort_command = False
        device_data.is_obsreset_command = False
        this_device_server = TangoServerHelper.get_instance()
        try:
            log_msg = const.STR_SCAN_IP_ARG + str(argin)
            self.logger.debug(log_msg)
            device_data._read_activity_message = log_msg
            device_data.isScanRunning = True
            self.scan_sdp(device_data, argin)
            self.scan_csp(device_data, argin)
            # TODO: Update observation state aggregation logic
            # if self._csp_sa_obs_state == ObsState.IDLE and self._sdp_sa_obs_state ==\
            #         ObsState.IDLE:
            #     if len(self.dishPointingStateMap.values()) != 0:
            #         self.calculate_observation_state()

            # Set timer to invoke EndScan command after scan duration is complete.
            self.logger.info("Setting scan timer")
            device_data.scan_timer_handler.start_scan_timer(device_data.scan_duration)
            this_device_server.set_status(const.STR_SA_SCANNING)
            self.logger.info(const.STR_SA_SCANNING)
            device_data._read_activity_message = const.STR_SCAN_SUCCESS

            return (ResultCode.STARTED, const.STR_SCAN_SUCCESS)
        except DevFailed as dev_failed:
            log_msg = const.ERR_SCAN_CMD + str(dev_failed)
            self.logger.exception(dev_failed)
            tango.Except.throw_exception(const.STR_SCAN_EXEC,
                                         log_msg,
                                         "SubarrayNode.Scan",
                                         tango.ErrSeverity.ERR)

    def scan_sdp(self, device_data, argin):
        """
        set up sdp devices
        """
        # Invoke scan command on Sdp Subarray Leaf Node with input argument as scan id
        sdp_client = TangoClient(device_data.sdp_subarray_ln_fqdn)
        sdp_client.send_command(const.CMD_SCAN, argin)
        self.logger.info(const.STR_SDP_SCAN_INIT)
        device_data._read_activity_message = const.STR_SDP_SCAN_INIT

    def scan_csp(self, device_data, argin):
        """
        set up csp devices
        """
        # Invoke Scan command on CSP Subarray Leaf Node
        csp_argin = [argin]
        csp_client = TangoClient(device_data.csp_subarray_ln_fqdn)
        csp_client.send_command(const.CMD_START_SCAN, csp_argin)
        self.logger.info(const.STR_CSP_SCAN_INIT)
        device_data._read_activity_message = const.STR_CSP_SCAN_INIT
