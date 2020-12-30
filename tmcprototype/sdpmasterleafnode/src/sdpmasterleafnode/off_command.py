# Tango imports
import tango
from tango import DeviceProxy, ApiUtil, DevState, AttrWriteType, DevFailed
from tango.server import run,command, device_property, attribute

# Additional import
from ska.base import SKABaseDevice
from ska.base.commands import ResultCode, BaseCommand
from . import const, release
# PROTECTED REGION END #    //  SdpMasterLeafNode.additionnal_import

class OffCommand(SKABaseDevice.OffCommand):
    """
    A class for SDP master's Off() command.
    """

    def off_cmd_ended_cb(self, event):

        """
        Callback function immediately executed when the asynchronous invoked
        command returns. Checks whether the OFF command has been successfully invoked on SDP Master.

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
        device =self.target
        if event.err:
            log_msg = const.ERR_INVOKING_CMD + str(event.cmd_name) + "\n" + str(event.errors)
            self.logger.error(log_msg)
            device._read_activity_message = log_msg

        else:
            log_msg = const.STR_COMMAND + str(event.cmd_name) + const.STR_INVOKE_SUCCESS
            self.logger.info(log_msg)
            device._read_activity_message = log_msg

    def do(self):
        """
        Sets the OperatingState to Off.

        :param argin: None.

        :return: A tuple containing a return code and a string message indicating status.
        The message is for information purpose only.

        :rtype: (ResultCode, str)

        """
        device =self.target
        try:
            device._sdp_proxy.command_inout_asynch(const.CMD_OFF, self.off_cmd_ended_cb)
            self.logger.debug(const.STR_OFF_CMD_SUCCESS)
            device._read_activity_message = const.STR_OFF_CMD_SUCCESS
            return (ResultCode.OK, const.STR_OFF_CMD_SUCCESS)

        except DevFailed as dev_failed:
            self.logger.exception(dev_failed)
            log_msg = const.ERR_OFF_CMD_FAIL + str(dev_failed)
            tango.Except.re_throw_exception(dev_failed, const.ERR_INVOKING_CMD, log_msg,
                                            "SdpMasterLeafNode.OffCommand()",
                                            tango.ErrSeverity.ERR)
