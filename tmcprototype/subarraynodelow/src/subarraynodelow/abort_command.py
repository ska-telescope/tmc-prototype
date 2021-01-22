"""
Abort Command for SubarrayNodeLow.
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
from .device_data import DeviceData
from . import const

class Abort(SKASubarray.AbortCommand):
    """
    A class for SubarrayNode's Abort() command.
    """
    def do(self):
        """
        This command on Subarray Node invokes Abort command on MCCS Subarray Leaf Node and abort current
        functionality.

        :return: A tuple containing a return code and a string
            message indicating status. The message is for
            information purpose only.
        :rtype: (ResultCode, str)

        :raises: DevFailed if error occurs in invoking command on MCCS Subarrayleaf node.

        """
        device_data = DeviceData.get_instance()
        device_data.is_release_resources = False
        device_data.is_end_command = False
        try:
            if device_data.scan_timer_handler.is_scan_running():
                device_data.scan_timer_handler.stop_scan_timer()
                self.abort_mccs(device_data.mccs_subarray_ln_fqdn)
                self.logger.info(const.STR_ABORT_SUCCESS)
                device_data._read_activity_message = const.STR_ABORT_SUCCESS
                tango_server_helper = TangoServerHelper.get_instance()
                tango_server_helper.set_status(const.STR_ABORT_SUCCESS)
                device_data.is_abort_command = True
                return (ResultCode.STARTED, const.STR_ABORT_SUCCESS)

        except DevFailed as dev_failed:
            log_msg = const.ERR_ABORT_INVOKING_CMD + str(dev_failed)
            self.logger.exception(dev_failed)
            tango.Except.throw_exception(const.ERR_ABORT_INVOKING_CMD,
                                         log_msg,
                                         "SubarrayNode.Abort",
                                         tango.ErrSeverity.ERR)

    def abort_mccs(self, mccsln_fqdn):
        """
        Create client of mccs subarray leaf node and invoke abort command on clinet.
        """
        sdp_client = TangoClient(mccsln_fqdn)
        sdp_client.send_command(const.CMD_ABORT)
        self.logger.info(const.STR_CMD_ABORT_INV_MCCS)







