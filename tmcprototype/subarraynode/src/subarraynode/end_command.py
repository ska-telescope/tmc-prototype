"""
End Command class for SubarrayNode.
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
from subarraynode.device_data import DeviceData


class End(SKASubarray.EndCommand):
    """
    A class for SubarrayNode's End() command.

    This command on Subarray Node invokes End command on CSP Subarray Leaf Node and SDP
    Subarray Leaf Node, and stops tracking of all the assigned dishes.

    """

    def do(self):
        """
        Method to invoke End command.

        return:
            A tuple containing a return code and a string message indicating status.
            The message is for information purpose only.

        rtype:
            (ResultCode, str)

        raises:
            DevFailed if the command execution is not successful.
        """
        self.logger.debug(type(self.target))
        device_data = DeviceData.get_instance()
        device_data.is_end_command_executed = False
        device_data.is_release_resources_command_executed = False
        device_data.is_restart_command_executed = False
        device_data.is_abort_command_executed = False
        device_data.is_obsreset_command_executed = False

        try:
            self.logger.info("End command invoked on SubarrayNode.")
            self.end_sdp(device_data)
            self.end_csp(device_data)
            self.stop_dish_tracking(device_data)
            device_data._read_activity_message = const.STR_ENDSB_SUCCESS
            self.logger.info(const.STR_ENDSB_SUCCESS)
            tango_server_helper_obj = TangoServerHelper.get_instance()
            tango_server_helper_obj.set_status(const.STR_ENDSB_SUCCESS)
            device_data.is_end_command_executed = True
            return (ResultCode.OK, const.STR_ENDSB_SUCCESS)
        except DevFailed as dev_failed:
            log_msg = f"{const.ERR_ENDSB_INVOKING_CMD}{dev_failed}"
            self.logger.exception(log_msg)
            tango.Except.throw_exception(
                const.STR_ENDSB_EXEC, log_msg, "SubarrayNode.End", tango.ErrSeverity.ERR
            )

    def end_sdp(self, device_data):
        """
        End command on sdp devices
        """
        sdp_saln_client = TangoClient(device_data.sdp_subarray_ln_fqdn)
        sdp_saln_client.send_command(const.CMD_END)
        # TODO: Unsubscribe ReceiveAddressesMap from SDP in End command instead of OFF command.
        self.logger.info(const.STR_CMD_END_INV_SDP)

    def end_csp(self, device_data):
        """
        End command on csp devices
        """
        csp_saln_client = TangoClient(device_data.csp_subarray_ln_fqdn)
        csp_saln_client.send_command(const.CMD_GOTOIDLE)
        self.logger.info(const.STR_CMD_GOTOIDLE_INV_CSP)

    def stop_dish_tracking(self, device_data):
        # TODO: Getting exception while running test cases using device mocking
        device_data._dish_leaf_node_group_client.send_command(const.CMD_STOP_TRACK)
        self.logger.info(const.STR_CMD_STOP_TRACK_INV_DLN)
