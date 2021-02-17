"""
Abort Command for SubarrayNodeLow.
"""
# Tango imports
import tango
from tango import DevFailed

# Additional import
from ska.base.commands import ResultCode
from ska.base import SKASubarray

from tmc.common.tango_client import TangoClient
from tmc.common.tango_server_helper import TangoServerHelper

from . import const


class Abort(SKASubarray.AbortCommand):
    """
    A class for SubarrayNode's Abort() command.

    This command on Subarray Node Low invokes Abort command on MCCS Subarray Leaf Node and aborts ongoing
    activity.

    """

    def do(self):
        """
        Method to invoke Abort command.

        return:
            A tuple containing a return code and a string
            message indicating status. The message is for
            information purpose only.

        rtype:
            (ResultCode, str)

        raises:
            DevFailed if error occurs in invoking command on MCCS Subarrayleaf node.

        """
        device_data = self.target
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
            log_msg = f"{const.ERR_ABORT_INVOKING_CMD}{dev_failed}"
            self.logger.exception(dev_failed)
            tango.Except.throw_exception(
                const.ERR_ABORT_INVOKING_CMD,
                log_msg,
                "SubarrayNode.Abort",
                tango.ErrSeverity.ERR,
            )

    def abort_mccs(self, mccs_sa_ln_fqdn):
        """
        Create client of MCCS subarray leaf node and invoke abort command on client.

        :param argin: MCCS SubarrayLeafNode FQDN

        return:
            None
        """
        mccs_client = TangoClient(mccs_sa_ln_fqdn)
        mccs_client.send_command(const.CMD_ABORT)
        self.logger.info(const.STR_CMD_ABORT_INV_MCCS)
