# Tango imports
import tango
from tango import DeviceProxy, ApiUtil, DevState, AttrWriteType, DevFailed
from tango.server import run,command, device_property, attribute

# Additional import
from ska.base import SKABaseDevice
from ska.base.commands import ResultCode, BaseCommand
from . import const, release
from tmc.common.tango_client import TangoClient
from .device_data import DeviceData
# PROTECTED REGION END #    //  SdpMasterLeafNode.additionnal_import


class OnCommand(SKABaseDevice.OnCommand):
    """
    A class for SDP master's On() command.
    """

    def on_cmd_ended_cb(self, event):

        """
        Callback function immediately executed when the asynchronous invoked
        command returns. Checks whether the On command has been successfully invoked on SDP Master.

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
        """ Informs the SDP that it can start executing Processing Blocks. Sets the OperatingState to ON.

        :param argin: None.

        :return: A tuple containing a return code and a string message indicating status.
        The message is for information purpose only.

        :rtype: (ResultCode, str)

        """
        device = self.target
        try:
            sdp_mln_client_obj = TangoClient(device.sdp_master_ln_fqdn)
            sdp_mln_client_obj.send_command_async(const.CMD_ON, [], self.on_cmd_ended_cb)
            # device._sdp_proxy.command_inout_asynch(const.CMD_ON, self.on_cmd_ended_cb)
            log_msg = const.STR_ON_CMD_SUCCESS
            self.logger.debug(log_msg)
            return (ResultCode.OK, log_msg)

        except DevFailed as dev_failed:
            self.logger.exception(dev_failed)
            log_msg = const.ERR_ON_CMD_FAIL + str(dev_failed)
            tango.Except.re_throw_exception(dev_failed, const.ERR_INVOKING_CMD, log_msg,
                                            "SdpMasterLeafNode.OnCommand()",
                                            tango.ErrSeverity.ERR)

