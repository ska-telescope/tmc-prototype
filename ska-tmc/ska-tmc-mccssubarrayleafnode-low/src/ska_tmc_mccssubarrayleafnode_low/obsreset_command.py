# PyTango imports
import tango
from tango import DevState, DevFailed

# Additional import
from ska.base.commands import BaseCommand
from ska.base.control_model import ObsState

from tmc.common.tango_client import TangoClient
from tmc.common.tango_server_helper import TangoServerHelper

from . import const


class ObsReset(BaseCommand):
    """
    A class for MccsSubarrayLeafNode's ObsReset() command.

    Command to reset the MCCS subarray and bring it to its RESETTING state.

    """

    def check_allowed(self):
        """
        Checks whether this command is allowed to be run in current device state

        :return: True if this command is allowed to be run in current device state

        :rtype: boolean

        :raises: DevFailed if this command is not allowed to be run in current device state

        """
        if self.state_model.op_state in [DevState.UNKNOWN, DevState.DISABLE]:
            log_msg = f"ObsReset() is not allowed in {self.state_model.op_state}"
            tango.Except.throw_exception(
                log_msg,
                "Failed to invoke ObsReset command on MccsSubarrayLeafNode.",
                "mccssubarrayleafnode.ObsReset()",
                tango.ErrSeverity.ERR,
            )
        self.this_server = TangoServerHelper.get_instance()
        self.mccs_sa_fqdn = self.this_server.read_property("MccsSubarrayFQDN")[0]
        self.mccs_sa_client = TangoClient(self.mccs_sa_fqdn)
        if self.mccs_sa_client.get_attribute("obsState").value not in [ObsState.ABORTED, ObsState.FAULT]:
            tango.Except.throw_exception(const.ERR_DEVICE_NOT_IN_VALID_OBSTATE, const.ERR_OBSRESET_INVOKING_CMD,
                                            "MccsSubarrayLeafNode.ObsResetCommand",
                                            tango.ErrSeverity.ERR)

        return True

    def obsreset_cmd_ended_cb(self, event):
        """
        Callback function immediately executed when the asynchronous invoked
        command returns.

        :param event: a CmdDoneEvent object. This class is used to pass data
            to the callback method in asynchronous callback model for command
            execution.

        :type: CmdDoneEvent object
            It has the following members:
                - device     : (DeviceProxy) The DeviceProxy object on which the call was executed.
                - cmd_name   : (str) The command name
                - argout_raw : (DeviceData) The command argout
                - argout     : The command argout
                - err        : (bool) A boolean flag set to true if the command failed. False otherwise
                - errors     : (sequence<DevError>) The error stack
                - ext

        :return: none
        """
        # Update logs and activity message attribute with received event
        if event.err:
            log_msg = f"{const.ERR_INVOKING_CMD}{event.cmd_name}\n{event.errors}"
            self.logger.error(log_msg)
            self.this_server.write_attr("activityMessage", log_msg, False)
        else:
            log_msg = f"{const.STR_COMMAND}{event.cmd_name}{const.STR_INVOKE_SUCCESS}"
            self.logger.info(log_msg)
            self.this_server.write_attr("activityMessage", log_msg, False)

    def do(self):
        """
        Method to invoke ObsReset command on MCCS Subarray.

        :param argin: None

        return:
            None

        raises:
            DevFailed if error occurs while invoking the command on MccsSubarray.
        """
        try:
            self.mccs_sa_client.send_command_async(
                const.CMD_OBSRESET, None, self.obsreset_cmd_ended_cb
            )
            self.this_server.write_attr("activityMessage", const.STR_OBSRESET_SUCCESS, False)
            self.logger.info(const.STR_OBSRESET_SUCCESS)

        except DevFailed as dev_failed:
            log_msg = f"{const.ERR_OBSRESET_INVOKING_CMD}{dev_failed}"
            self.this_server.write_attr("activityMessage", log_msg, False)
            self.logger.exception(log_msg)
            tango.Except.throw_exception(
                const.ERR_OBSRESET_INVOKING_CMD,
                log_msg,
                "MccsSubarrayLeafNode.ObsResetCommand",
                tango.ErrSeverity.ERR,
            )