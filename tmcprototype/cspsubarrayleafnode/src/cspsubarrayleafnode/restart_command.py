# PyTango imports
import tango
from tango import DevState, DevFailed

# Additional import
from ska.base.commands import BaseCommand

from tmc.common.tango_client import TangoClient
from tmc.common.tango_server_helper import TangoServerHelper

from . import const


class RestartCommand(BaseCommand):
    """
    A class for CSPSubarrayLeafNode's Restart() command. Restart command is inherited from BaseCommand.

    This command invokes Restart command on CSP Subarray.

    """

    def check_allowed(self):
        """
        Checks whether this command is allowed to be run in current device state

        return:
            True if this command is allowed to be run in current device state

        rtype:
            boolean

        raises:
            DevFailed if this command is not allowed to be run in current device state

        """
        if self.state_model.op_state in [DevState.UNKNOWN, DevState.DISABLE]:
            tango.Except.throw_exception(
                f"Restart() is not allowed in current state {self.state_model.op_state}",
                "Failed to invoke Restart command on CspSubarrayLeafNode.",
                "cspsubarrayleafnode.Restart()",
                tango.ErrSeverity.ERR,
            )

        # if device._csp_subarray_proxy.obsState not in [ObsState.FAULT, ObsState.ABORTED]:
        #     tango.Except.throw_exception(const.ERR_UNABLE_RESTART_CMD, const.ERR_RESTART_INVOKING_CMD,
        #                                     "CspSubarrayLeafNode.RestartCommand",
        #                                     tango.ErrSeverity.ERR)

        return True

    def restart_cmd_ended_cb(self, event):
        """
        Callback function immediately executed when the asynchronous invoked
        command returns.

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
        # Update logs and activity message attribute with received event
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
        Method to invoke Restart command on CSP Subarray.

        return:
            None

        raises:
            DevFailed if error occurs while invoking the command on CSP Subarray.

        """
        try:
            this_server = TangoServerHelper.get_instance()
            csp_subarray_fqdn = ""
            property_val = this_server.read_property("CspSubarrayFQDN")
            csp_subarray_fqdn = csp_subarray_fqdn.join(property_val)
            csp_sub_client_obj = TangoClient(csp_subarray_fqdn)
            csp_sub_client_obj.send_command_async(
                const.CMD_RESTART, None, self.restart_cmd_ended_cb
            )
            this_server.write_attr("activityMessage", const.STR_RESTART_SUCCESS, False)
            self.logger.info(const.STR_RESTART_SUCCESS)

        except DevFailed as dev_failed:
            log_msg = f"{const.ERR_RESTART_INVOKING_CMD}{dev_failed}"
            this_server.write_attr("activityMessage", log_msg, False)
            self.logger.exception(dev_failed)
            tango.Except.throw_exception(
                const.ERR_RESTART_INVOKING_CMD,
                log_msg,
                "CspSubarrayLeafNode.RestartCommand",
                tango.ErrSeverity.ERR,
            )
