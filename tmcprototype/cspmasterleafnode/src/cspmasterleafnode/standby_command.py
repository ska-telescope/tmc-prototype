# Tango import
import tango
from tango import DevState, DevFailed

# Additional import
from ska.base.commands import BaseCommand

from tmc.common.tango_client import TangoClient
from tmc.common.tango_server_helper import TangoServerHelper

from . import const


class Standby(BaseCommand):
    """
    A class for CspMasterLeafNode's Standby() command. Standby command is inherited from BaseCommand.

    It Sets the OpState to Standby.
    """

    def check_allowed(self):
        """
        Checks whether this command is allowed to be run in current device state.

        return:
            True if this command is allowed to be run in current device state.

        rtype:
            boolean

        raises:
            DevFailed if this command is not allowed to be run in current device state.

        """
        if self.state_model.op_state in [DevState.FAULT, DevState.UNKNOWN]:
            tango.Except.throw_exception(
                f"Command Standby is not allowed in current state {self.state_model.op_state}.",
                "Failed to invoke Standby command on CspMasterLeafNode.",
                "CspMasterLeafNode.Standby()",
                tango.ErrSeverity.ERR,
            )

        return True

    def standby_cmd_ended_cb(self, event):
        """
        Callback function immediately executed when the asynchronous invoked
        command returns. Checks whether the StandBy command has been successfully invoked on CSPMaster.

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
        this_device = TangoServerHelper.get_instance()
        if event.err:
            log_msg = f"{const.ERR_INVOKING_CMD}{event.cmd_name}\n{event.errors}"
            self.logger.error(log_msg)
            this_device.write_attr("activityMessage", log_msg)
        else:
            log_msg = f"{const.STR_COMMAND}{event.cmd_name}{const.STR_INVOKE_SUCCESS}"
            self.logger.info(log_msg)
            this_device.write_attr("activityMessage", log_msg)

    def do(self, argin):
        """
        Method to invoke Standby command on CSP Element.

        :param argin: DevStringArray.
        If the array length is 0, the command applies to the whole CSP Element. If the array length is > 1
        , each array element specifies the FQDN of the CSP SubElement to put in STANDBY mode.

        return:
            None

        raises:
            DevFailed on communication failure with CspMaster or CspMaster is in error state.

        """
        device_data = self.target
        this_device = TangoServerHelper.get_instance()

        try:
            csp_mln_client_obj = TangoClient(device_data.csp_master_ln_fqdn)
            csp_mln_client_obj.send_command_async(
                const.CMD_STANDBY, command_data=argin, callback_method=self.standby_cmd_ended_cb
            )
            self.logger.debug(const.STR_STANDBY_CMD_ISSUED)

        except DevFailed as dev_failed:
            log_msg = f"{const.ERR_EXE_STANDBY_CMD}{dev_failed}"
            self.logger.exception(dev_failed)
            this_device.write_attr("activityMessage", const.ERR_EXE_STANDBY_CMD)
            tango.Except.re_throw_exception(
                dev_failed,
                const.STR_STANDBY_EXEC,
                log_msg,
                "CspMasterLeafNode.StandbyCommand",
                tango.ErrSeverity.ERR,
            )
