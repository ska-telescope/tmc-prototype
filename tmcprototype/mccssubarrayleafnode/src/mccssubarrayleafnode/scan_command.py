# PROTECTED REGION ID(MccSubarrayLeafNode.additional_import) ENABLED START #
# Standard python imports

# Third party imports
import tango
from tango import DevState, DevFailed

# Additional import
from ska.base.commands import ResultCode, BaseCommand
from tmc.common.tango_client import TangoClient
from . import const, release
# PROTECTED REGION END #    //  MccsSubarrayLeafNode.additional_import

class Scan(BaseCommand):
    """
    A class for MccsSubarrayLeafNode's Scan() command.
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
        if self.state_model.op_state in [DevState.FAULT, DevState.UNKNOWN, DevState.DISABLE]:
            tango.Except.throw_exception("Scan() is not allowed in current state",
                                         "Failed to invoke Scan command on mccssubarrayleafnode.",
                                         "mccssubarrayleafnode.Scan()",
                                         tango.ErrSeverity.ERR)

        return True

    def scan_cmd_ended_cb(self, event):
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

    def do(self, argin):
        """
        This command invokes Scan command on MccsSubarray. It is allowed only when MccsSubarray is in
        ObsState READY.

        :param argin: JSON string consists of scan id (int).

        Example:
        {"id":1}

        Note: Enter the json string without spaces as a input.

        :return: None

        :rtype: Void

        :raises: DevFailed if the command execution is not successful
        """
        device_data = self.target
        tango_client_object = TangoClient(device_data._mccs_subarray_fqdn)
        try:
            # TODO: Mock obs_state issue to be resolved
            # assert tango_client_object.get_attribute("obsState") == ObsState.READY
            tango_client_object.send_command_async(const.CMD_SCAN, argin, self.scan_cmd_ended_cb)
            device_data._read_activity_message = const.STR_SCAN_SUCCESS
            self.logger.info(const.STR_SCAN_SUCCESS)

        # TODO: Mock obs_state issue to be resolved
        # except AssertionError as assertion_error:
        #     log_msg = const.ERR_DEVICE_NOT_READY + str(assertion_error)
        #     device_data._read_activity_message = log_msg
        #     self.logger.exception(log_msg)
        #     tango.Except.throw_exception(const.STR_SCAN_EXEC, log_msg,
        #                                  "MccsSubarrayLeafNode.ScanCommand",
        #                                  tango.ErrSeverity.ERR)

        except DevFailed as dev_failed:
            log_msg = const.ERR_SCAN_RESOURCES + str(dev_failed)
            device_data._read_activity_message = log_msg
            self.logger.exception(dev_failed)
            tango.Except.throw_exception(const.STR_SCAN_EXEC, log_msg,
                                         "MccsSubarrayLeafNode.ScanCommand",
                                         tango.ErrSeverity.ERR)
