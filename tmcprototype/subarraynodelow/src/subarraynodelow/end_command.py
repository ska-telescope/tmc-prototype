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
    A class for SubarrayNodelow's End() command.
    """
    def do(self):
        """
        This command on Subarray Node low invokes End command on Mccs Subarray Leaf Node.

        :return: A tuple containing a return code and a string message indicating status.
        The message is for information purpose only.

        :rtype: (ResultCode, str)

        :raises: DevFailed if the command execution is not successful.
        """
        device = self.target
        device.is_end_command = False
        device.is_release_resources = False

        try:
            self.logger.info("End command invoked on SubarrayNodelow.")
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
            tango.Except.throw_exception(const.STR_END_EXEC,
                                         log_msg,
                                         "SubarrayNodelow.EndCommand",
                                         tango.ErrSeverity.ERR)
