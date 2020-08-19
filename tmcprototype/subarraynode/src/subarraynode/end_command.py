"""
EndCommand class for SubarrayNode.
"""

# Tango imports
import tango
from tango import DevFailed

# Additional import
from . import const
from ska.base.commands import ResultCode
from ska.base import SKASubarray


class EndCommand(SKASubarray.EndCommand):
    """
    A class for SubarrayNode's End() command.
    """
    def do(self):
        """
        This command on Subarray Node invokes EndSB command on CSP Subarray Leaf Node and SDP
        Subarray Leaf Node, and stops tracking of all the assigned dishes.

        :return: A tuple containing a return code and a string message indicating status.
        The message is for information purpose only.

        :rtype: (ResultCode, str)

        :raises: DevFailed if the command execution is not successful.
        """
        device = self.target
        device.is_end_command = False
        try:
            self.logger.info("End command invoked on SubarrayNode.")
            device._sdp_subarray_ln_proxy.command_inout(const.CMD_ENDSB)
            self.logger.info(const.STR_CMD_ENDSB_INV_SDP)
            device._csp_subarray_ln_proxy.command_inout(const.CMD_GOTOIDLE)
            self.logger.info(const.STR_CMD_GOTOIDLE_INV_CSP)
            # TODO: Uncomment this after resolving issues
            self.stop_dish_tracking()
            device._read_activity_message = const.STR_ENDSB_SUCCESS
            self.logger.info(const.STR_ENDSB_SUCCESS)
            device.set_status(const.STR_ENDSB_SUCCESS)
            device.is_end_command = True
            return (ResultCode.OK, const.STR_ENDSB_SUCCESS)
        except DevFailed as dev_failed:
            log_msg = const.ERR_ENDSB_INVOKING_CMD + str(dev_failed)
            self.logger.exception(log_msg)
            tango.Except.throw_exception(const.STR_ENDSB_EXEC,
                                         log_msg,
                                         "SubarrayNode.EndCommand",
                                         tango.ErrSeverity.ERR)

    def stop_dish_tracking(self):
        # TODO: Getting exception while running test cases using device mocking
        device = self.target
        device._dish_leaf_node_group.command_inout(const.CMD_STOP_TRACK)
        self.logger.info(const.STR_CMD_STOP_TRACK_INV_DLN)