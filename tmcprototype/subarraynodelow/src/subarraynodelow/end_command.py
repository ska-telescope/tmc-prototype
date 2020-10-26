"""
EndCommand class for SubarrayNodeLow.
"""

# Third party imports
# Tango imports
import tango
from tango import DevFailed

# Additional import
from ska.base.commands import ResultCode
from ska.base import SKASubarray
from . import const


class EndCommand(SKASubarray.EndCommand):
    """
    A class for SubarrayNodeLow's End() command.
    """
    def do(self):
        """
        This command on Subarray Node Low invokes End command on MCCS Subarray Leaf Node.

        :return: A tuple containing a return code and a string message indicating status.
        The message is for information purpose only.

        :rtype: (ResultCode, str)

        :raises: DevFailed if the command execution is not successful.
        """
        device = self.target
        device.is_end_command = False
        device.is_release_resources = False

        try:
            self.logger.info(const.STR_END_CMD_INVOKED_SA_LOW)
            device._mccs_subarray_ln_proxy.command_inout(const.CMD_END)
            self.logger.info(const.STR_CMD_END_INV_MCCS)
            device._read_activity_message = const.STR_END_SUCCESS
            self.logger.info(const.STR_END_SUCCESS)
            device.set_status(const.STR_END_SUCCESS)
            device.is_end_command = True
            return (ResultCode.OK, const.STR_END_SUCCESS)

        except DevFailed as dev_failed:
            log_msg = const.ERR_END_INVOKING_CMD + str(dev_failed)
            self.logger.exception(log_msg)
            device.set_status(const.ERR_END_INVOKING_CMD)
            tango.Except.re_throw_exception(const.STR_END_EXEC,
                                         log_msg,
                                         "SubarrayNode.EndCommand",
                                         tango.ErrSeverity.ERR)
