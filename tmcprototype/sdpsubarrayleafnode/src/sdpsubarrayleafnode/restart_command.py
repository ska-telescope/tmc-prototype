"""
Restart class for SDPSubarrayLeafNode.
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


class Restart(BaseCommand):
    """
    A class for sdpSubarrayLeafNode's Restart() command.
    """

    def check_allowed(self):
        """
        Checks whether this command is allowed to be run in current device state

        :return: True if this command is allowed to be run in current device state

        :rtype: boolean

        :raises: DevFailed if this command is not allowed to be run in current device state

        """
        device = self.target
        if self.state_model.op_state in [DevState.UNKNOWN, DevState.DISABLE ]:
            tango.Except.throw_exception("Restart() is not allowed in current state",
                                            "Failed to invoke Restart command on SdpSubarrayLeafNode.",
                                            "sdpsubarrayleafnode.Restart()",
                                            tango.ErrSeverity.ERR)

        if device._sdp_subarray_proxy.obsState not in [ObsState.ABORTED, ObsState.FAULT]:
            tango.Except.throw_exception(const.ERR_DEVICE_NOT_ABORTED_FAULT, "Failed to invoke Restart command on SdpSubarrayLeafNode.",
                                        "SdpSubarrayLeafNode.RestartCommand()",
                                        tango.ErrSeverity.ERR)
        return True

    def restart_cmd_ended_cb(self, event):
        """
        Callback function immediately executed when the asynchronous invoked command returns.
        Checks whether the restart command has been successfully invoked on SDP Subarray.

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
        Command to restart the SDP subarray and bring it to its ON state.

        :return: None

        :raises: DevFailed if error occurs while invoking command on SDPSubarray.

        """
        device = self.target
        try:
            device._sdp_subarray_proxy.command_inout_asynch(const.CMD_RESTART,
                                                            self.restart_cmd_ended_cb)
            device._read_activity_message = const.STR_RESTART_SUCCESS
            self.logger.info(const.STR_RESTART_SUCCESS)

        except DevFailed as dev_failed:
            log_msg = const.ERR_RESTART_INVOKING_CMD + str(dev_failed)
            device._read_activity_message = log_msg
            self.logger.exception(dev_failed)
            tango.Except.throw_exception(const.STR_RESTART_EXEC, log_msg,
                                            "SdpSubarrayLeafNode.RestartCommand()",
                                            tango.ErrSeverity.ERR)
