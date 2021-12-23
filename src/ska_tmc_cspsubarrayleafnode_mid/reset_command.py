# Third Party imports
# PyTango imports
import tango

# Additional import
from ska.base import SKABaseDevice
from ska.base.commands import ResultCode
from tango import DevFailed, DevState
from tmc.common.tango_server_helper import TangoServerHelper

from . import const
from .delay_model import DelayManager


class ResetCommand(SKABaseDevice.ResetCommand):
    """
    A class for CSPSubarrayLeafNode's Reset() command.

    Command to reset the current operation being done on the CSP Subarray Leaf Node.

    """

    def check_allowed(self):
        """
        Checks whether this command is allowed to be run in current device state

        :return: True if this command is allowed to be run in current device state

        :rtype: boolean

        :raises: DevFailed if this command is not allowed to be run in current device state

        """
        if self.state_model.op_state in [
            DevState.ON,
            DevState.OFF,
            DevState.DISABLE,
        ]:
            tango.Except.throw_exception(
                f"Reset() is not allowed in current state {self.state_model.op_state}",
                "Failed to invoke Reset command on CspSubarrayLeafNode.",
                "cspsubarrayleafnode.Reset()",
                tango.ErrSeverity.ERR,
            )
        return True

    def do(self):
        """
        This command invokes Reset command on CSP Subarray.

        return:
            None

        raises:
            DevFailed if error occurs while invoking command on CSP Subarray.

        """
        try:
            this_server = TangoServerHelper.get_instance()
            log_msg = (
                const.CMD_RESET + const.STR_COMMAND + const.STR_INVOKE_SUCCESS
            )
            self.logger.debug(log_msg)
            delay_manager_obj = DelayManager.get_instance()
            delay_manager_obj.stop()
            self.logger.info(const.STR_RESET_SUCCESS)
            return (ResultCode.OK, const.STR_RESET_SUCCESS)

        except DevFailed as dev_failed:
            log_msg = f"{const.ERR_RESET_INVOKING_CMD}{dev_failed}"
            this_server.write_attr("activityMessage", log_msg, False)
            self.logger.exception(dev_failed)
            tango.Except.throw_exception(
                const.STR_RESET_EXEC,
                log_msg,
                "CspSubarrayLeafNode.ResetCommand",
                tango.ErrSeverity.ERR,
            )
