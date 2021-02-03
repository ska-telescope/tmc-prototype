"""
Track Command class for SubarrayNode.
"""

# Standard python imports
import random
import string

# Third party imports
# Tango imports
import tango
from tango import DevState

# Additional import
from . import const
from ska.base.commands import ResultCode, ResponseCommand
from .device_data import DeviceData


class Track(ResponseCommand):
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
        if self.state_model.op_state in [
            DevState.FAULT,
            DevState.UNKNOWN,
            DevState.DISABLE,
        ]:
            tango.Except.throw_exception(
                "Command Track is not allowed in current state.",
                "Failed to invoke Track command on DishLeafNode.",
                "SubarrayNode.Track()",
                tango.ErrSeverity.ERR,
            )
        return True

    def do(self, argin):
        """Invokes Track command on the Dishes assigned to the Subarray.

        :param argin: DevString

        Example:
        radec|21:08:47.92|-88:57:22.9 as argin
        Argin to be provided is the Ra and Dec values where first value is tag that is radec, second value is Ra
        in Hr:Min:Sec, and third value is Dec in Deg:Min:Sec.

        :return: A tuple containing a return code and a string message indicating status.
        The message is for information purpose only.

        :rtype: (ResultCode, str)

        """
        device_data = DeviceData.get_instance()
        log_msg = "Track:", argin
        self.logger.debug(log_msg)
        device_data.is_restart_command_executed = False
        device_data.is_release_resources_command_executed = False
        device_data.is_abort_command_executed = False
        device_data.is_obsreset_command_executed = False
        try:
            device_data._read_activity_message = f"{const.STR_TRACK_IP_ARG}{argin}"
            cmd_input = [argin]
            cmdData = tango.DeviceData()
            cmdData.insert(tango.DevVarStringArray, cmd_input)
            device_data._dish_leaf_node_group_client.send_command(
                const.CMD_TRACK, cmdData
            )
            device_data._scan_id = "".join(
                random.choice(string.ascii_uppercase + string.digits) for _ in range(4)
            )
            self.logger.info(const.STR_TRACK_CMD_INVOKED_SA)
            return (ResultCode.OK, const.STR_TRACK_CMD_INVOKED_SA)
        except tango.DevFailed as devfailed:
            log_msg = f"{const.ERR_TRACK_CMD}{devfailed}"
            self.logger.exception(devfailed)
            tango.Except.throw_exception(
                const.STR_CMD_FAILED,
                log_msg,
                "SubarrayNode.Track()",
                tango.ErrSeverity.ERR,
            )
