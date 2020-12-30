# Tango imports
import tango
from tango import DeviceProxy, ApiUtil, DevState, AttrWriteType, DevFailed
from tango.server import run,command, device_property, attribute

# Additional import
from ska.base import SKABaseDevice
from ska.base.commands import ResultCode, BaseCommand
from . import const, release
# PROTECTED REGION END #    //  SdpMasterLeafNode.additionnal_import

class DisableCommand(BaseCommand):
    """
    A class for SDP master's Disable() command.
    """

    def check_allowed(self):
        """
        Check Whether this command is allowed to be run in current device
        state.

         :return: True if this command is allowed to be run in
             current device state.
         :rtype: boolean
         :raises: DevFailed if this command is not allowed to be run
             in current device state.
        """
        if self.state_model.op_state in [DevState.FAULT, DevState.UNKNOWN, DevState.ON]:
            tango.Except.throw_exception("Disable() is not allowed in current state",
                                         "Failed to invoke Disable command on SdpMasterLeafNode.",
                                         "SdpMasterLeafNode.Disable() ",
                                         tango.ErrSeverity.ERR)
        return True

    def disable_cmd_ended_cb(self, event):

        """
        Callback function immediately executed when the asynchronous invoked
        command returns. Checks whether the disable command has been successfully invoked on SDP Master.

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
        device = self.target
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
        Sets the OperatingState to Disable.

        :param argin: None.

        :return: None

        """
        device = self.target
        try:
            device._sdp_proxy.command_inout_asynch(const.CMD_Disable, self.disable_cmd_ended_cb)
            self.logger.debug(const.STR_DISABLE_CMS_SUCCESS)
            device._read_activity_message = const.STR_DISABLE_CMS_SUCCESS

        except DevFailed as dev_failed:
            self.logger.exception(dev_failed)
            log_msg = const.ERR_DISABLE_CMD_FAIL + str(dev_failed)
            tango.Except.re_throw_exception(dev_failed, const.ERR_INVOKING_CMD, log_msg,
                                            "SdpMasterLeafNode.DisableCommand()",
                                            tango.ErrSeverity.ERR)