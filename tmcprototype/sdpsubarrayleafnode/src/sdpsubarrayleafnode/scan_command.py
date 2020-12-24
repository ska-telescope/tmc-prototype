"""
Scan class for SDPSubarrayLeafNode.
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

class Scan(BaseCommand):
    """
    A class for SdpSubarrayLeafNode's Scan() command.
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
            tango.Except.throw_exception("Scan() is not allowed in current state",
                                            "Failed to invoke Scan command on SdpSubarrayLeafNode.",
                                            "sdpsubarrayleafnode.Scan()",
                                            tango.ErrSeverity.ERR)

        if device._sdp_subarray_proxy.obsState != ObsState.READY:
            tango.Except.throw_exception(const.ERR_DEVICE_NOT_READY, "Failed to invoke Scan command on SdpSubarrayLeafNode.",
                                            "SdpSubarrayLeafNode.ScanCommand()",
                                            tango.ErrSeverity.ERR)
        return True

    def scan_cmd_ended_cb(self, event):
        """
        Callback function immediately executed when the asynchronous invoked command returns.
        Checks whether the scan command has been successfully invoked on SDP Subarray.

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

    def do(self, argin):
        """
        Invoke Scan command to SDP subarray.

        :param argin: The string in JSON format. The JSON contains following values:

        Example:
        {“id”:1}

        Note: Enter input as without spaces:{“id”:1}

        :return: None

        :raises: DevFailed if the command execution is not successful.
        """
        device = self.target
        try:
            log_msg = "Input JSON for SDP Subarray Leaf Node Scan command is: " + argin
            self.logger.debug(log_msg)
            device._sdp_subarray_proxy.command_inout_asynch(const.CMD_SCAN, argin,
                                                            self.scan_cmd_ended_cb)
            device._read_activity_message = const.STR_SCAN_SUCCESS
            self.logger.info(const.STR_SCAN_SUCCESS)

        except DevFailed as dev_failed:
            log_msg = const.ERR_SCAN + str(dev_failed)
            device._read_activity_message = log_msg
            self.logger.exception(dev_failed)
            tango.Except.throw_exception(const.STR_SCAN_EXEC, log_msg,
                                            "SdpSubarrayLeafNode.ScanCommand()",
                                            tango.ErrSeverity.ERR)

def is_Scan_allowed(self):
    """
    Checks whether this command is allowed to be run in current device state.

    :return: True if this command is allowed to be run in current device state.

    :rtype: boolean

    """
    handler = self.get_command_object("Scan")
    return handler.check_allowed()

@command(
    dtype_in=('str'),
    doc_in="The JSON input string consists of SB ID.",
)
@DebugIt()
def Scan(self, argin):
    """Invoke Scan command to SDP subarray. """

    handler = self.get_command_object("Scan")
    handler(argin)
