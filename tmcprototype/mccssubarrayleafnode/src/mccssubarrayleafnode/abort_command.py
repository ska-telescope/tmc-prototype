# Third party imports
import tango
from tango import DevState, DevFailed

# Additional import
from ska.base.commands import BaseCommand
from tmc.common.tango_client import TangoClient
from . import const

class Abort(BaseCommand):
    """
    A class for MccsSubarrayLeafNode's Abort() command.
    """

    def check_allowed(self):
        """
        Checks whether the command is allowed to be run in the current state

        :return: True if this command is allowed to be run in
            current device state

        :rtype: boolean

        :raises: DevFailed if this command is not allowed to be run
            in current device state

        """
        if self.state_model.op_state in [
            DevState.FAULT, DevState.UNKNOWN, DevState.DISABLE,
        ]:
            tango.Except.throw_exception("Abort() is not allowed in current state",
                                         "Failed to invoke Abort command on MccsSubarrayLeafNode.",
                                         "Mccssubarrayleafnode.Abort()",
                                         tango.ErrSeverity.ERR)

        # mccs_subarray_client = TangoClient(device_data._mccs_subarray_fqdn)
        # if mccs_subarray_client.get_attribute("obsState") not in [ObsState.IDLE, ObsState.READY,
        #                                     ObsState.CONFIGURING, ObsState.SCANNING, ObsState.RESETTING]:
        #     tango.Except.throw_exception(const.ERR_DEVICE_NOT_IN_VALID_OBSTATE, const.ERR_ABORT_COMMAND,
        #                                     "Mccssubarrayleafnode.Abort()",
        #                                     tango.ErrSeverity.ERR)
        return True

    def abort_cmd_ended_cb(self, event):
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
            log_msg = const.ERR_INVOKING_CMD + str(event.cmd_name) + "\n" + str(event.errors)
            self.logger.error(log_msg)
            device_data._read_activity_message = log_msg
        else:
            log_msg = const.STR_COMMAND + str(event.cmd_name) + const.STR_INVOKE_SUCCESS
            self.logger.info(log_msg)
            device_data._read_activity_message = log_msg

    def do(self):
        """
        This command invokes Abort command on MCCS Subarray.
        :return: None

        :rtype: Void

        :raises: DevFailed if the command execution is not successful
        """
        device_data = self.target
        try:
            mccs_subarray_client = TangoClient(device_data._mccs_subarray_fqdn)
            # TODO: Mock obs_state issue to be resolved
            # assert mccs_subarray_client.get_attribute("obsState") == ObsState.READY
            mccs_subarray_client.send_command_async(const.CMD_ABORT, None, self.abort_cmd_ended_cb)
            device_data._read_activity_message = const.STR_ABORT_SUCCESS
            self.logger.info(const.STR_ABORT_SUCCESS)

        except DevFailed as dev_failed:
            log_msg = const.ERR_ABORT_COMMAND + str(dev_failed)
            device_data._read_activity_message = log_msg
            self.logger.exception(dev_failed)
            tango.Except.throw_exception(const.ERR_ABORT_COMMAND, log_msg,
                                         "MccsSubarrayLeafNode.Abort",
                                         tango.ErrSeverity.ERR)
