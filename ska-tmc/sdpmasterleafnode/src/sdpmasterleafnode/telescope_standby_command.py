# Tango imports
import tango
from tango import DevState, DevFailed

# Additional import
from ska.base.commands import BaseCommand

from tmc.common.tango_client import TangoClient
from tmc.common.tango_server_helper import TangoServerHelper

from . import const

class TelescopeStandby(BaseCommand):
    """
    A class for SDP Master's Standby() command. Standby command is inherited from BaseCommand.

    Informs the SDP to stop any executing Processing. To get into the STANDBY state all running
    PBs will be aborted. In normal operation we expect diable should be triggered without first going
    into STANDBY.
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
            tango.Except.throw_exception(
                f"Standby() is not allowed in current state {self.state_model.op_state}",
                "Failed to invoke Standby command on SdpMasterLeafNode.",
                "SdpMasterLeafNode.TelescopeStandby() ",
                tango.ErrSeverity.ERR,
            )
        return True

    def telescope_standby_cmd_ended_cb(self, event):

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
        this_server = TangoServerHelper.get_instance()
        if event.err:
            log_msg = f"{const.ERR_INVOKING_CMD}{event.cmd_name}\n{event.errors}"
            self.logger.error(log_msg)
            this_server.write_attr("activityMessage", log_msg, False)

        else:
            log_msg = f"{const.STR_COMMAND}{event.cmd_name}{const.STR_INVOKE_SUCCESS}"
            self.logger.info(log_msg)
            this_server.write_attr("activityMessage", log_msg, False)

    def do(self):
        """
        Method to invoke TelescopeStandby command on SDP Master.

        :param argin: None.

        return:
            None
        """
        this_server = TangoServerHelper.get_instance()
        try:
            sdp_master_ln_fqdn = ""
            property_val = this_server.read_property("SdpMasterFQDN")[0]
            sdp_master_ln_fqdn = sdp_master_ln_fqdn.join(property_val)
            sdp_mln_client_obj = TangoClient(sdp_master_ln_fqdn)
            sdp_mln_client_obj.send_command_async(
                const.CMD_TELESCOPE_STANDBY, callback_method=self.telescope_standby_cmd_ended_cb
                )
            log_msg = const.CMD_TELESCOPE_STANDBY + const.STR_COMMAND + const.STR_INVOKE_SUCCESS
            self.logger.debug(log_msg)

        except DevFailed as dev_failed:
            self.logger.exception(dev_failed)
            log_msg = f"{const.ERR_TELESCOPE_STANDBY_CMD_FAIL}{dev_failed}"
            tango.Except.re_throw_exception(
                dev_failed,
                const.ERR_INVOKING_CMD,
                log_msg,
                "SdpMasterLeafNode.TelescopeStandby()",
                tango.ErrSeverity.ERR,
            )
