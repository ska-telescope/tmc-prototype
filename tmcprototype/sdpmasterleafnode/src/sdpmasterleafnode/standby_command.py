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

class StandbyCommand(BaseCommand):
    """
    A class for SDP Master's Standby() command.
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

        if self.state_model.op_state in [DevState.FAULT, DevState.UNKNOWN]:
            tango.Except.throw_exception("Standby() is not allowed in current state",
                                         "Failed to invoke Standby command on SdpMasterLeafNode.",
                                         "SdpMasterLeafNode.Standby() ",
                                         tango.ErrSeverity.ERR)
        return True

    def standby_cmd_ended_cb(self, event):

        """
        Callback function immediately executed when the asynchronous invoked
        command returns. Checks whether the standby command has been successfully invoked on SDP Master.

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
        device_data = DeviceData.get_instance()
        if event.err:
            log_msg = const.ERR_INVOKING_CMD + str(event.cmd_name) + "\n" + str(event.errors)
            self.logger.error(log_msg)
            device_data._read_activity_message = log_msg

        else:
            log_msg = const.STR_COMMAND + str(event.cmd_name) + const.STR_INVOKE_SUCCESS
            self.logger.info(log_msg)
            device_data._read_activity_message = log_msg

    def do(self):
        """ Informs the SDP to stop any executing Processing. To get into the STANDBY state all running
        PBs will be aborted. In normal operation we expect diable should be triggered without first going
        into STANDBY.

        :param argin: None.

        :return: None

        """
        device_data = DeviceData.get_instance()
        try:
            sdp_mln_client_obj = TangoClient(device_data.sdp_master_ln_fqdn)
            sdp_mln_client_obj.send_command_async(const.CMD_STANDBY, [], self.standby_cmd_ended_cb)
            # device._sdp_proxy.command_inout_asynch(const.CMD_STANDBY, self.standby_cmd_ended_cb)
            log_msg = const.CMD_STANDBY + const.STR_COMMAND + const.STR_INVOKE_SUCCESS
            self.logger.debug(log_msg)

        except DevFailed as dev_failed:
            self.logger.exception(dev_failed)
            log_msg = const.ERR_STANDBY_CMD_FAIL + str(dev_failed)
            tango.Except.re_throw_exception(dev_failed, const.ERR_INVOKING_CMD, log_msg,
                                            "SdpMasterLeafNode.StandbyCommand()",
                                            tango.ErrSeverity.ERR)

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

        if self.state_model.op_state in [DevState.FAULT, DevState.UNKNOWN]:
            tango.Except.throw_exception("Standby() is not allowed in current state",
                                         "Failed to invoke Standby command on SdpMasterLeafNode.",
                                         "SdpMasterLeafNode.Standby() ",
                                         tango.ErrSeverity.ERR)
        return True