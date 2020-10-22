"""
ScanCommand class for SubarrayNode
"""
# Standard python imports
import threading
# Tango imports
import tango
from tango import DevFailed

# Additional import
from . import const
from ska.base.commands import ResultCode
from ska.base import SKASubarray


class ScanCommand(SKASubarray.ScanCommand):
    """
    A class for SubarrayNode's Scan() command.
    """

    def do(self, argin):
        """
        This command accepts id as input. And it Schedule scan on subarray
        from where scan command is invoked on respective CSP and SDP subarray node for the
        provided interval of time. It checks whether the scan is already in progress. If yes it
        throws error showing duplication of command.

        :param argin: DevString. JSON string containing id.

        JSON string example as follows:

        {"id": 1}

        Note: Above JSON string can be used as an input argument while invoking this command from JIVE.

        :return: A tuple containing a return code and a string message indicating status.
        The message is for information purpose only.

        :rtype: (ReturnCode, str)

        :raises: DevFailed if the command execution is not successful
        """
        device = self.target
        device.is_scan_completed = False
        device.is_release_resources = False
        device.is_restart_command = False
        device.is_abort_command = False
        device.is_obsreset_command = False
        try:
            log_msg = const.STR_SCAN_IP_ARG + str(argin)
            self.logger.info(log_msg)
            device._read_activity_message = log_msg
            device.isScanRunning = True
            # Invoke scan command on Sdp Subarray Leaf Node with input argument as scan id
            device._sdp_subarray_ln_proxy.command_inout(const.CMD_SCAN, argin)
            self.logger.info(const.STR_SDP_SCAN_INIT)
            device._read_activity_message = const.STR_SDP_SCAN_INIT
            # Invoke Scan command on CSP Subarray Leaf Node
            csp_argin = [argin]
            device._csp_subarray_ln_proxy.command_inout(const.CMD_START_SCAN, csp_argin)
            self.logger.info(const.STR_CSP_SCAN_INIT)
            device._read_activity_message = const.STR_CSP_SCAN_INIT
            # TODO: Update observation state aggregation logic
            # if self._csp_sa_obs_state == ObsState.IDLE and self._sdp_sa_obs_state ==\
            #         ObsState.IDLE:
            #     if len(self.dishPointingStateMap.values()) != 0:
            #         self.calculate_observation_state()
            device.set_status(const.STR_SA_SCANNING)
            self.logger.info(const.STR_SA_SCANNING)
            device._read_activity_message = const.STR_SCAN_SUCCESS
            # Once Scan Duration is complete call EndScan Command
            self.logger.info("Starting Scan Thread")
            device.scan_thread = threading.Timer(device.scan_duration, self.call_end_scan_command)
            device.scan_thread.start()
            self.logger.info("Scan thread started")
            return (ResultCode.STARTED, const.STR_SCAN_SUCCESS)
        except DevFailed as dev_failed:
            log_msg = const.ERR_SCAN_CMD + str(dev_failed)
            self.logger.exception(dev_failed)
            tango.Except.throw_exception(const.STR_SCAN_EXEC,
                                         log_msg,
                                         "SubarrayNode.ScanCommand",
                                         tango.ErrSeverity.ERR)

    def call_end_scan_command(self):
        device = self.target
        device.endscan_obj.do()