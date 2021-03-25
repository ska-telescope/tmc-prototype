# Tango imports
import tango
from tango import DevFailed

# Additional import
from ska.base import SKABaseDevice
from ska.base.commands import ResultCode

from tmc.common.tango_client import TangoClient
from tmc.common.tango_server_helper import TangoServerHelper

from . import const

class Off(SKABaseDevice.OffCommand):
    """
    A class for SDP master's Off() command. Off command is inherited from SKABaseDevice.

    It Sets the State  to Off.

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
        if event.err:
            log_msg = f"{const.ERR_INVOKING_CMD}{event.cmd_name}\n{event.errors}"
            self.logger.error(log_msg)
            self.this_server.write_attr("activityMessage", log_msg)

        else:
            log_msg = f"{const.STR_COMMAND}{event.cmd_name}{const.STR_INVOKE_SUCCESS}"
            self.logger.info(log_msg)
            self.this_server.write_attr("activityMessage", log_msg)

    def do(self):
        """
        Method to invoke Off command on SDP Master.

        :param argin: None.

        return:
            A tuple containing a return code and a string message indicating status.
            The message is for information purpose only.

        rtype:
            (ResultCode, str)

        """
        self.this_server = TangoServerHelper.get_instance()
        try:
            # sdp_mln_client_obj = TangoClient(device_data.sdp_master_ln_fqdn)
            sdp_master_ln_fqdn = ""
            property_val = self.this_server.read_property("SdpMasterFQDN")
            sdp_master_ln_fqdn = sdp_master_ln_fqdn.join(property_val)
            sdp_mln_client_obj = TangoClient(sdp_master_ln_fqdn)
            sdp_mln_client_obj.send_command_async(
                const.CMD_OFF, None, self.off_cmd_ended_cb
            )
            self.logger.debug(const.STR_OFF_CMD_SUCCESS)
            self.this_server.write_attr("activityMessage", const.STR_OFF_CMD_SUCCESS)
            return (ResultCode.OK, const.STR_OFF_CMD_SUCCESS)

        except DevFailed as dev_failed:
            self.logger.exception(dev_failed)
            log_msg = f"{const.ERR_OFF_CMD_FAIL}{dev_failed}"
            tango.Except.re_throw_exception(
                dev_failed,
                const.ERR_INVOKING_CMD,
                log_msg,
                "SdpMasterLeafNode.OffCommand()",
                tango.ErrSeverity.ERR,
            )
