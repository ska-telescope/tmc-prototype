"""
OnCommand class for SubarrayNode
"""
# Tango imports
import tango
from tango import DevFailed

# Additional import
from subarraynode import const
from ska.base.commands import ResultCode
from ska.base import SKASubarray


class OnCommand(SKASubarray.OnCommand):
    """
    A class for the SubarrayNode's On() command.
    """

    def do(self):
        """
        This command invokes On Command on MCCS Subarray Leaf Node nodes. This comamnd
        changes Subaray device state from OFF to ON.

        :return: A tuple containing a return code and a string message indicating status. 
                The message is for information purpose only.

        :rtype: (ResultCode, str)

        :raises: DevFailed if the command execution is not successful
        """
        device = self.target
        device.is_restart_command = False
        device.is_release_resources = False
        device.is_abort_command = False
        try:
            self.logger.info("Invokiing On command on MCCS Subarray Leaf Node")
            mccs_leaf_node_proxy = tango.DeviceProxy("sys/tg_test/1")
            result = mccs_leaf_node_proxy.Status()
            message = "On command sent to MCCS Subarray Leaf Node"
            self.logger.info(message)
            self.logger.info(result)
            return (ResultCode.OK, message)
        except DevFailed as dev_failed:
            log_msg = const.ERR_INVOKING_ON_CMD + str(dev_failed)
            self.logger.error(log_msg)
            self._read_activity_message = log_msg
            tango.Except.throw_exception(dev_failed, "Failed to invoke On command on SubarrayNode.",
                                         "SubarrayNode.On()", tango.ErrSeverity.ERR)

