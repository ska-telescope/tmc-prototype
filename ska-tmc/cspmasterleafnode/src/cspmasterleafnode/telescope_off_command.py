# Tango import
import tango
from tango import DevFailed

# Additional import
from ska.base.commands import BaseCommand
from tmc.common.tango_server_helper import TangoServerHelper
from tmc.common.tango_client import TangoClient


from . import const


class TelescopeOff(BaseCommand):
    """
    A class for CspMasterLeafNode's TelescopeOff() command. TelescopeOff command is inherited from BaseCommand.

    It Sets the State to Off.
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
        Method to invoke Off command on CSP Element.

        param argin:
            None.

        """
        device_data = self.target  
        this_device = TangoServerHelper.get_instance()
        try:
            csp_mln_client_obj = TangoClient(this_device.read_property("CspMasterFQDN")[0])
            csp_mln_client_obj.send_command_async(
                const.CMD_OFF, [], self.telescope_off_cmd_ended_cb
            )
            self.logger.debug(const.STR_OFF_CMD_ISSUED)
            this_device.write_attr("activityMessage", const.STR_OFF_CMD_ISSUED, False)
            device_data.cbf_health_updator.stop()
            device_data.pss_health_updator.stop()
            device_data.pst_health_updator.stop()

        except DevFailed as dev_failed:
            log_msg = f"{const.ERR_EXE_OFF_CMD}{dev_failed}"
            self.logger.exception(dev_failed)
            this_device.write_attr("activityMessage", const.ERR_EXE_OFF_CMD, False)
            tango.Except.re_throw_exception(
                dev_failed,
                const.STR_ON_EXEC,
                log_msg,
                "CspMasterLeafNode.TelescopeOffCommand",
                tango.ErrSeverity.ERR,
            )