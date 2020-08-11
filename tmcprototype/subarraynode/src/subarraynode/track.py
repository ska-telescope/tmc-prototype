"""
TrackCommand class for SubarrayNode.
"""
from __future__ import print_function
from __future__ import absolute_import

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
        if self.state_model.dev_state in [DevState.FAULT, DevState.UNKNOWN, DevState.DISABLE]:
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
        exception_message = []
        exception_count = 0
        log_msg = "Track:", argin
        self.logger.debug(log_msg)
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
            exception_message.append(const.ERR_TRACK_CMD + ": " + \
                                     str(devfailed.args[0].desc))
            exception_count += 1
        except Exception as except_occured:
            str_log = const.ERR_TRACK_CMD + "\n" + str(except_occured)
            self.logger.error(str_log)
            self._read_activity_message = const.ERR_TRACK_CMD + str(except_occured)
            self.logger.error(const.ERR_TRACK_CMD)
            exception_message.append(const.ERR_TRACK_CMD + ": " + \
                                     str(except_occured.args[0].desc))
            exception_count += 1
        # throw exception
        if exception_count > 0:
            err_msg = ' '
            for item in exception_message:
                err_msg += item + "\n"
            tango.Except.throw_exception(const.STR_CMD_FAILED, err_msg,
                                         const.STR_TRACK_EXEC, tango.ErrSeverity.ERR)
