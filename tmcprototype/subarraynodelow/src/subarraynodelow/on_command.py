"""
OnCommand class for SubarrayNodeLow
"""
# Tango imports
import tango
from tango import DevFailed

# Additional import
from ska.base.commands import ResultCode
from ska.base import SKASubarray
from . import const


class OnCommand(SKASubarray.OnCommand):
    """
    A class for the SubarrayNodeLow's On() command.
    """

    def do(self):
        """
        This command invokes On Command on MCCSSubarray through MCCS Subarray Leaf node. This comamnd
        changes Subarray device state from OFF to ON.

        :return: A tuple containing a return code and a string message indicating status. The message is for
                information purpose only.

        :rtype: (ResultCode, str)

        :raises: DevFailed if the command execution is not successful
        """
        device = self.target
        try:
            device._mccs_subarray_ln_proxy.On()
            message = "On command completed OK"
            self.logger.info(message)
            return (ResultCode.OK, message)
        except DevFailed as dev_failed:
            log_msg = const.ERR_INVOKING_ON_CMD + str(dev_failed)
            self.logger.error(log_msg)
            self._read_activity_message = log_msg
            tango.Except.throw_exception(dev_failed[0].desc, "Failed to invoke On command on SubarrayNode.",
                                         "SubarrayNode.On()", tango.ErrSeverity.ERR)
