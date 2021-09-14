# Third Party imports
# PyTango imports
import tango
from tango import DevState, DevFailed

# Additional import
from ska.base.commands import BaseCommand
from ska.base.control_model import ObsState

from tmc.common.tango_client import TangoClient
from tmc.common.tango_server_helper import TangoServerHelper
from ska.base.commands import ResultCode

from . import const

class ResetCommand(BaseCommand.Reset):
    """
    A class for SDPSubarrayLeafNode's Reset() command.

    Command to reset the current operation being done on the SDP Subarray.

    """
    def check_allowed(self):
        """
        Checks whether this command is allowed to be run in current device state

        :return: True if this command is allowed to be run in current device state

        :rtype: boolean

        :raises: DevFailed if this command is not allowed to be run in current device state

        """
        if self.state_model.op_state in [
            DevState.OFF,
            DevState.DISABLE,
            DevState.ON
        ]:
            tango.Except.throw_exception(
                f"Reset() is not allowed in current state {self.state_model.op_state}",
                "Failed to invoke Reset command on SdpSubarrayLeafNode.",
                "sdpsubarrayleafnode.Reset()",
                tango.ErrSeverity.ERR,
            )
        return True

    def do(self):
        """
        This command invokes Reset command on SDP Subarray.

        return:
            None

        raises:
            DevFailed if error occurs while invoking command on SDP Subarray.

        """
        try:
            self.logger.info(const.STR_RESET_SUCCESS)
            return (ResultCode.OK, const.STR_RESET_SUCCESS)

        except DevFailed as dev_failed:
            log_msg = f"{const.ERR_RESET_INVOKING_CMD}{dev_failed}"
            self.logger.exception(dev_failed)
            tango.Except.throw_exception(
                const.STR_RESET_EXEC,
                log_msg,
                "sdpSubarrayLeafNode.ResetCommand",
                tango.ErrSeverity.ERR,
            )
