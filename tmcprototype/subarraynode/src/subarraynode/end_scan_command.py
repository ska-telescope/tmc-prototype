"""
EndScanCommand class for SubarrayNode.
"""

from __future__ import print_function
from __future__ import absolute_import

# Tango imports
from tango import DevFailed

# Additional import
from . import const
from ska.base.commands import ResultCode
from ska.base import SKASubarray


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

        :raises: Exception if command execution throws any type of exception
                DevFailed if the command execution is not successful
        """
        device = self.target
        exception_count = 0
        exception_message = []

        try:
            if device.scan_thread:
                if device.scan_thread.is_alive():
                    device.scan_thread.cancel()  # stop timer when EndScan command is called
            device.isScanRunning = False
            device.is_scan_completed = True
            # Invoke EndScan command on SDP Subarray Leaf Node
            device._sdp_subarray_ln_proxy.command_inout(const.CMD_END_SCAN)
            self.logger.debug(const.STR_SDP_END_SCAN_INIT)
            device._read_activity_message = const.STR_SDP_END_SCAN_INIT

            # Invoke EndScan command on CSP Subarray Leaf Node
            device._csp_subarray_ln_proxy.command_inout(const.CMD_END_SCAN)
            self.logger.debug(const.STR_CSP_END_SCAN_INIT)
            device._read_activity_message = const.STR_CSP_END_SCAN_INIT
            device._scan_id = ""
            # TODO: For Future Use
            # if device._csp_sa_obs_state == ObsState.IDLE and device._sdp_sa_obs_state ==\
            #         ObsState.IDLE:
            #     if len(device.dishPointingStateMap.values()) != 0:
            #         device.calculate_observation_state()
            device.set_status(const.STR_SCAN_COMPLETE)
            self.logger.info(const.STR_SCAN_COMPLETE)
            device._read_activity_message = const.STR_END_SCAN_SUCCESS
            return (ResultCode.OK, const.STR_END_SCAN_SUCCESS)

        except DevFailed as dev_failed:
            [exception_message, exception_count] = device._handle_devfailed_exception(dev_failed,
                                                                                      exception_message,
                                                                                      exception_count,
                                                                                      const.ERR_END_SCAN_CMD_ON_GROUP)

        except Exception as except_occurred:
            [exception_message, exception_count] = device._handle_generic_exception(except_occurred,
                                                                                    exception_message,
                                                                                    exception_count,
                                                                                    const.ERR_END_SCAN_CMD)

        # Throw Exception
        if exception_count > 0:
            device.throw_exception(exception_message, const.STR_END_SCAN_EXEC)
