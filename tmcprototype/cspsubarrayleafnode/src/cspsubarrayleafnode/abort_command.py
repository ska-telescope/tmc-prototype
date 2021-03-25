# Third Party imports
# PyTango imports
import tango
from tango import DevState, DevFailed

# Additional import
from ska.base.commands import BaseCommand

from tmc.common.tango_client import TangoClient

from . import const


class AbortCommand(BaseCommand):
    """
    A class for CSPSubarrayLeafNode's Abort() command.

    Command to abort the current operation being done on the CSP Subarray.

    """

    def check_allowed(self):
        """
        Checks whether this command is allowed to be run in current device state

        :return: True if this command is allowed to be run in current device state

        :rtype: boolean

        :raises: DevFailed if this command is not allowed to be run in current device state

        """
        # device = self.target
        if self.state_model.op_state in [
            DevState.FAULT,
            DevState.UNKNOWN,
            DevState.DISABLE,
        ]:
            tango.Except.throw_exception(
                f"Abort() is not allowed in current state {self.state_model.op_state}",
                "Failed to invoke Abort command on CspSubarrayLeafNode.",
                "cspsubarrayleafnode.Abort()",
                tango.ErrSeverity.ERR,
            )

        # TODO: Need to get ObsState issue resolved.
        # if device._csp_subarray_proxy.obsState not in [ObsState.READY, ObsState.CONFIGURING, ObsState.SCANNING,
        #                                                 ObsState.IDLE, ObsState.RESETTING]:
        #     tango.Except.throw_exception(const.ERR_UNABLE_ABORT_CMD, const.ERR_ABORT_INVOKING_CMD,
        #                                 "CspSubarrayLeafNode.AbortCommand",
        #                                 tango.ErrSeverity.ERR)

        return True

    def abort_cmd_ended_cb(self, event):
        """
        Callback function immediately  executed when the asynchronous invoked
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
        device_data = self.target
        # Update logs and activity message attribute with received event
        if event.err:
            log_msg = f"{const.ERR_INVOKING_CMD}{event.cmd_name}\n{event.errors}"
            self.logger.error(log_msg)
            device_data._read_activity_message = log_msg
        else:
            log_msg = f"{const.STR_COMMAND}{event.cmd_name}{const.STR_INVOKE_SUCCESS}"
            self.logger.info(log_msg)
            device_data._read_activity_message = log_msg

    def do(self):
        """
        This command invokes Abort command on CSP Subarray.

        return:
            None

        raises:
            DevFailed if error occurs while invoking command on CSP Subarray.

        """
        device_data = self.target
        try:
            csp_sub_client_obj = TangoClient(device_data.csp_subarray_fqdn)
            csp_sub_client_obj.send_command_async(
                const.CMD_ABORT, None, self.abort_cmd_ended_cb
            )
            device_data._read_activity_message = const.STR_ABORT_SUCCESS
            self.logger.info(const.STR_ABORT_SUCCESS)

        except DevFailed as dev_failed:
            log_msg = f"{const.ERR_ABORT_INVOKING_CMD}{dev_failed}"
            device_data._read_activity_message = log_msg
            self.logger.exception(dev_failed)
            tango.Except.throw_exception(
                const.STR_ABORT_EXEC,
                log_msg,
                "CspSubarrayLeafNode.AbortCommand",
                tango.ErrSeverity.ERR,
            )
