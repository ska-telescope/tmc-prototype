# PyTango imports
import tango
from tango import DevState, DevFailed

# Additional import
from ska.base.commands import BaseCommand

from tmc.common.tango_client import TangoClient

from . import const


class ObsResetCommand(BaseCommand):
    """
    A class for CSPSubarrayLeafNode's ObsReset() command.
    """

    def check_allowed(self):
        """
        Checks whether this command is allowed to be run in current device state

        :return: True if this command is allowed to be run in current device state

        :rtype: boolean

        :raises: DevFailed if this command is not allowed to be run in current device state

        """
        # device = self.target
        if self.state_model.op_state in [DevState.UNKNOWN, DevState.DISABLE]:
            log_msg = f"ObsReset() is not allowed in {self.state_model.op_state}"
            tango.Except.throw_exception(
                log_msg,
                "Failed to invoke ObsReset command on CspSubarrayLeafNode.",
                "cspsubarrayleafnode.ObsReset()",
                tango.ErrSeverity.ERR,
            )

        # if device._csp_subarray_proxy.obsState not in [ObsState.ABORTED, ObsState.FAULT]:
        #     tango.Except.throw_exception(const.ERR_UNABLE_OBSRESET_CMD, const.ERR_OBSRESET_INVOKING_CMD,
        #                                     "CspSubarrayLeafNode.ObsResetCommand",
        #                                     tango.ErrSeverity.ERR)

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
        Command to reset the CSP subarray and bring it to its RESETTING state.

        :param argin: None

        :return: None

        :raises: DevFailed if error occurs while invoking the command on CSpSubarray.
        """
        device_data = self.target
        try:
            csp_sub_client_obj = TangoClient(device_data.csp_subarray_fqdn)
            csp_sub_client_obj.send_command_async(
                const.CMD_OBSRESET, None, self.obsreset_cmd_ended_cb
            )
            device_data._read_activity_message = const.STR_OBSRESET_SUCCESS
            self.logger.info(const.STR_OBSRESET_SUCCESS)

        except DevFailed as dev_failed:
            log_msg = f"{const.ERR_OBSRESET_INVOKING_CMD}{dev_failed}"
            device_data._read_activity_message = log_msg
            self.logger.exception(log_msg)
            tango.Except.throw_exception(
                const.ERR_OBSRESET_INVOKING_CMD,
                log_msg,
                "CspSubarrayLeafNode.ObsResetCommand",
                tango.ErrSeverity.ERR,
            )
