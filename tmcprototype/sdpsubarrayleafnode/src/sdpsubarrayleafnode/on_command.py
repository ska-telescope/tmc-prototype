"""
On class for SDPSubarrayLeafNode.
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
from tmc.common.tango_client import TangoClient



class On(SKABaseDevice.OnCommand):
    """
    A class for SDP Subarray's On() command.
    """

    def on_cmd_ended_cb(self, event):
        """
        Callback function immediately executed when the asynchronous invoked command returns.
        Checks whether the On command has been successfully invoked on SDP Subarray.

        :param event: A CmdDoneEvent object. This class is used to pass data to the callback method in asynchronous
                        callback model for command execution.

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

        :param argin: None.

        :return: A tuple containing a return code and a string message indicating status.
        The message is for information purpose only.

        :rtype: (ResultCode, str)

        """
        try:
            device = self.target
            device._sdp_subarray_proxy.command_inout_asynch(const.CMD_ON, self.on_cmd_ended_cb)
            log_msg = const.CMD_ON + const.STR_COMMAND + const.STR_INVOKE_SUCCESS
            self.logger.debug(log_msg)
            return (ResultCode.OK, log_msg)

        except DevFailed as dev_failed:
            log_msg = const.ERR_INVOKING_ON_CMD + str(dev_failed)
            device._read_activity_message = log_msg
            self.logger.exception(dev_failed)
            tango.Except.throw_exception(const.STR_ON_EXEC, log_msg,
                                            "SdpSubarrayLeafNode.OnCommand()",
                                            tango.ErrSeverity.ERR)
