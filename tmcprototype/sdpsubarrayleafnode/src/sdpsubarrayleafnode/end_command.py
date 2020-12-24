"""
End class for SDPSubarrayLeafNode.
"""
# PROTECTED REGION ID(sdpsubarrayleafnode.additionnal_import) ENABLED START #
# Standard Python imports
import json
import ast
import tango
from tango import DevState, DevFailed
# Additional import
from ska.base import SKABaseDevice
from ska.base.commands import ResultCode, BaseCommand
from . import const
from sdpsubarrayleafnode.device_data import DeviceData
#from sdpsubarrayleafnode.tango_client import TangoClient


class End(BaseCommand):
    """
    A class for SdpSubarrayLeafNode's End() command.
    """

    def check_allowed(self):
        """
        Checks whether this command is allowed to be run in current device state.

        :return: True if this command is allowed to be run in current device state.

        :rtype: boolean

        :raises: Exception if command execution throws any type of exception.

        """
        device = self.target
        if self.state_model.op_state in [DevState.FAULT, DevState.UNKNOWN, DevState.DISABLE]:
            tango.Except.throw_exception("End() is not allowed in current state",
                                            "Failed to invoke End command on SdpSubarrayLeafNode.",
                                            "sdpsubarrayleafnode.End()",
                                            tango.ErrSeverity.ERR)

        if device._sdp_subarray_proxy.obsState != ObsState.READY:
            tango.Except.throw_exception(const.ERR_DEVICE_NOT_READY, "Failed to invoke End command on SdpSubarrayLeafNode.",
                                            "SdpSubarrayLeafNode.EndCommand()",
                                            tango.ErrSeverity.ERR)
        return True

    def end_cmd_ended_cb(self, event):
        """
        Callback function immediately executed when the asynchronous invoked command returns.
        Checks whether the end command has been successfully invoked on SDP Subarray.

        :param event: A CmdDoneEvent object.
        This class is used to pass data to the callback method in asynchronous callback model
        for command execution.

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
        device = self.target
        if event.err:
            log = const.ERR_INVOKING_CMD + str(event.cmd_name) + "\n" + str(event.errors)
            device._read_activity_message = log
            self.logger.error(log)
        else:
            log = const.STR_COMMAND + event.cmd_name + const.STR_INVOKE_SUCCESS
            device._read_activity_message = log
            self.logger.info(log)

    def do(self):
        """
        This command invokes End command on SDP subarray to end the current Scheduling block.

        :return: None

        :raises: DevFailed if the command execution is not successful.
        """
        device = self.target
        try:
            device._sdp_subarray_proxy.command_inout_asynch(const.CMD_END, self.end_cmd_ended_cb)
            device._read_activity_message = const.STR_END_SUCCESS
            self.logger.info(const.STR_END_SUCCESS)

        except DevFailed as dev_failed:
            log_msg = const.ERR_END_INVOKING_CMD + str(dev_failed)
            device._read_activity_message = log_msg
            self.logger.exception(dev_failed)
            tango.Except.throw_exception(const.STR_END_EXEC, log_msg,
                                            "SdpSubarrayLeafNode.EndCommand()",
                                            tango.ErrSeverity.ERR)
