"""
ScanCommand class for SubarrayNodeLow
"""

# Standard python imports
import threading

# Third party imports
# Tango imports
import tango
from tango import DevFailed

# Additional import
from ska.base.commands import ResultCode
from ska.base import SKASubarray
from . import const
from subarraynodelow.device_data import DeviceData
from tmc.common.tango_client import TangoClient


class Scan(SKASubarray.ScanCommand):
    """
    A class for SubarrayNodeLow's Scan() command.
    """

    def do(self, argin):
        """
        This command accepts id as input. And it Schedule scan on subarray
        from where scan command is invoked on MCCS subarray Leaf Node for the
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
        device_data = DeviceData.get_instance()
        device_data.is_scan_completed = False
        device_data.is_release_resources = False
        try:
            log_msg = const.STR_SCAN_IP_ARG + str(argin)
            self.logger.info(log_msg)
            device_data.activity_message = log_msg
            device_data.isScanRunning = True
            # Invoke scan command on MCCS Subarray Leaf Node with input argument as scan id
            mccs_leaf_node_client = TangoClient(device_data.mccs_subarray_ln_fqdn)
            mccs_leaf_node_client.send_command(const.CMD_SCAN, argin)
            # device._mccs_subarray_ln_proxy.command_inout(const.CMD_SCAN, argin)
            self.logger.info(const.STR_MCCS_SCAN_INIT)
            device_data.activity_message = const.STR_MCCS_SCAN_INIT
            # device_data.set_status(const.STR_SA_SCANNING)
            self.logger.info(const.STR_SA_SCANNING)
            device_data.activity_message = const.STR_SCAN_SUCCESS
            # Once Scan Duration is complete call EndScan Command
            self.logger.info("Starting Scan Thread")
            device_data.scan_thread = threading.Timer(device_data.scan_duration, self.call_end_scan_command)
            device_data.scan_thread.start()
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
        device_data = DeviceData.get_instance()
        device_data.end_scan.do()