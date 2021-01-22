# PyTango imports
import tango
from tango import DevState, DevFailed
# Additional import
from tmc.common.tango_client import TangoClient
from ska.base.commands import BaseCommand
from . import const


class ObsReset(BaseCommand):
    """
    A class for MccsSubarrayLeafNode's ObsReset() command.
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
            log_msg= "ObsReset() is not allowed in " + str(self.state_model.op_state)
            tango.Except.throw_exception(log_msg ,
                                            "Failed to invoke ObsReset command on MccsSubarrayLeafNode.",
                                            "mccssubarrayleafnode.ObsReset()",
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
        Command to reset the MCCS subarray and bring it to its RESETTING state.

        :param argin: None

        :return: None

        :raises: DevFailed if error occurs while invoking the command on MccsSubarray.
        """
        device_data = self.target
        try:
            mccs_subarray_client = TangoClient(device_data._mccs_subarray_fqdn)
            mccs_subarray_client.send_command_async(const.CMD_OBSRESET, None, self.obsreset_cmd_ended_cb)
            device_data._read_activity_message = const.STR_OBSRESET_SUCCESS
            self.logger.info(const.STR_OBSRESET_SUCCESS)

        except DevFailed as dev_failed:
            log_msg = const.ERR_OBSRESET_INVOKING_CMD + str(dev_failed)
            device_data._read_activity_message = log_msg
            self.logger.exception(log_msg)
            tango.Except.throw_exception(const.ERR_OBSRESET_INVOKING_CMD, log_msg,
                                            "MccsSubarrayLeafNode.ObsResetCommand",
                                            tango.ErrSeverity.ERR)
