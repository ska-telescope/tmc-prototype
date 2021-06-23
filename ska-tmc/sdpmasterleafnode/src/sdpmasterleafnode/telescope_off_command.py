# Tango imports
import tango
from tango import DevFailed

# Additional import
from ska.base import SKABaseDevice
from ska.base.commands import BaseCommand

from tmc.common.tango_client import TangoClient
from tmc.common.tango_server_helper import TangoServerHelper

from . import const

class TelescopeOff(BaseCommand):
    """
    A class for SDP master's TelescopeOff() command. TelescopeOff command is inherited from BaseCommand.

    It Sets the State  to Off.

    """

    def telescope_off_cmd_ended_cb(self, event):

        """
        Callback function immediately executed when the asynchronous invoked
        command returns. Checks whether the TelescopeOff command has been successfully invoked on SDP Master.

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
        Method to invoke TelescopeOff command on SDP Master.

        :param argin: None.

        return:
            A tuple containing a return code and a string message indicating status.
            The message is for information purpose only.

        rtype:
            (ResultCode, str)

        """
        this_server = TangoServerHelper.get_instance()
        try:
            sdp_master_ln_fqdn = ""
            property_val = this_server.read_property("SdpMasterFQDN")[0]
            sdp_master_ln_fqdn = sdp_master_ln_fqdn.join(property_val)
            sdp_mln_client_obj = TangoClient(sdp_master_ln_fqdn)
            sdp_mln_client_obj.send_command_async(
                const.CMD_TELESCOPE_OFF, None, self.telescope_off_cmd_ended_cb
            )
            self.logger.debug(const.STR_TELESCOPE_OFF_CMD_SUCCESS)
            this_server.write_attr("activityMessage", const.STR_TELESCOPE_OFF_CMD_SUCCESS, False)

        except DevFailed as dev_failed:
            self.logger.exception(dev_failed)
            log_msg = f"{const.ERR_TELESCOPE_OFF_CMD_FAIL}{dev_failed}"
            tango.Except.re_throw_exception(
                dev_failed,
                const.ERR_INVOKING_CMD,
                log_msg,
                "SdpMasterLeafNode.TelescopeOffCommand()",
                tango.ErrSeverity.ERR,
            )
