"""
TrackCommand class for SubarrayNode Low.
"""

import random
import string
# Tango imports
import tango
from tango import DevState

# Additional import
from . import const
from ska.base.commands import ResultCode, ResponseCommand


class TrackCommand(ResponseCommand):
    """
    A class for SubarrayNode's Track command.
    """

    def check_allowed(self):
        """
        Checks whether this command is allowed to be run in current device state.

        :return: True if this command is allowed to be run in current device state

        :rtype: boolean

        :raises: DevFailed if this command is not allowed to be run in current device state
        """
        if self.state_model.op_state in [DevState.FAULT, DevState.UNKNOWN, DevState.DISABLE]:
            tango.Except.throw_exception("Command TrackCommand is not allowed in current state.",
                                         "Failed to invoke TrackCommand command on DishLeafNode.",
                                         "SubarrayNode.TrackComamnd()",
                                         tango.ErrSeverity.ERR)
        return True

    def do(self, argin):
        """ Invokes Track command on the Dishes assigned to the Subarray.

        :param argin: DevString

        Example:
        radec|21:08:47.92|-88:57:22.9 as argin
        Argin to be provided is the Ra and Dec values where first value is tag that is radec, second value is Ra
        in Hr:Min:Sec, and third value is Dec in Deg:Min:Sec.

        :return: A tuple containing a return code and a string message indicating status.
        The message is for information purpose only.

        :rtype: (ResultCode, str)

        """
        device = self.target
        log_msg = "Track:", argin
        self.logger.debug(log_msg)
        device.is_restart_command = False
        device.is_release_resources = False
        device.is_abort_command = False
        device.is_obsreset_command = False
        try:
            device._read_activity_message = const.STR_TRACK_IP_ARG + argin
            cmd_input = [argin]
            cmdData = tango.DeviceData()
            cmdData.insert(tango.DevVarStringArray, cmd_input)
            device._dish_leaf_node_group.command_inout(const.CMD_TRACK, cmdData)
            device._scan_id = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(4))
            self.logger.info(const.STR_TRACK_CMD_INVOKED_SA)
            return (ResultCode.OK, const.STR_TRACK_CMD_INVOKED_SA)
        except tango.DevFailed as devfailed:
            log_msg = const.ERR_TRACK_CMD + str(devfailed)
            self.logger.exception(devfailed)
            tango.Except.throw_exception(const.STR_CMD_FAILED,
                                         log_msg,
                                         "SubarrayNode.TrackCommand()",
                                         tango.ErrSeverity.ERR)
