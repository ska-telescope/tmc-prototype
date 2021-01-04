# PyTango imports
import tango
from tango import DevState, DevFailed
# Additional import
from tmc.common.tango_client import TangoClient
from ska.base.commands import BaseCommand
from ska.base.control_model import ObsState
from . import const

class EndScanCommand(BaseCommand):
    """
    A class for CspSubarrayLeafNode's EndScan() command.
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
        # device = self.target
        if self.state_model.op_state in [DevState.FAULT, DevState.UNKNOWN, DevState.DISABLE]:
            tango.Except.throw_exception("EndScan() is not allowed in current state",
                                            "Failed to invoke EndScan command on cspsubarrayleafnode.",
                                            "cspsubarrayleafnode.EndScan()",
                                            tango.ErrSeverity.ERR)

        # if device._csp_subarray_proxy.obsState != ObsState.SCANNING:
        #     tango.Except.throw_exception(const.ERR_DEVICE_NOT_IN_SCAN, "Failed to invoke EndScan command on cspsubarrayleafnode.",
        #                                     "CspSubarrayLeafNode.EndScanCommand",
        #                                     tango.ErrSeverity.ERR)

        return True

    def endscan_cmd_ended_cb(self, event):
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
        It invokes EndScan command on CspSubarray. This command is allowed when CspSubarray is in
        obsState SCANNING

        :return: A tuple containing a return code and a string message indicating status.
                The message is for information purpose only.

        :rtype: (ReturnCode, str)

        :raises: DevFailed if the command execution is not successful
        """
        device_data = self.target
        try:
            csp_sub_client_obj = TangoClient(device_data.csp_subarray_fqdn)
            csp_sub_client_obj.send_command_async(const.CMD_ENDSCAN, None, self.endscan_cmd_ended_cb)
            device_data._read_activity_message = const.STR_ENDSCAN_SUCCESS
            self.logger.info(const.STR_ENDSCAN_SUCCESS)

        except DevFailed as dev_failed:
            log_msg = const.ERR_ENDSCAN_INVOKING_CMD + str(dev_failed)
            device_data._read_activity_message = log_msg
            self.logger.exception(dev_failed)
            tango.Except.throw_exception(const.STR_ENDSCAN_EXEC, log_msg,
                                            "CspSubarrayLeafNode.EndScanCommand",
                                            tango.ErrSeverity.ERR)
