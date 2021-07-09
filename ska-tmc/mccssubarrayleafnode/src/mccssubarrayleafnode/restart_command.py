import json
# Third party imports
import tango
from tango import DevState, DevFailed

# Additional import
from ska.base.commands import BaseCommand
from ska.base.control_model import ObsState

from tmc.common.tango_client import TangoClient
from tmc.common.tango_server_helper import TangoServerHelper

from . import const


class Restart(BaseCommand):
    """
    A class for MccsSubarrayLeafNode's Restart() command.

    Restart command is inherited from BaseCommand. This command Invokes Restart command on MCCS Controller.
    """

    def check_allowed(self):
        """
        Checks whether the command is allowed to be executed in the current state

        :return: True if this command is allowed to be run in
            current device state

        :rtype: boolean

        :raises: DevFailed if this command is not allowed to be run
            in current device state

        """
        if self.state_model.op_state in [
            DevState.FAULT,
            DevState.UNKNOWN,
            DevState.DISABLE,
        ]:
            tango.Except.throw_exception(
                f"Restart() is not allowed in current state {self.state_model.op_state}",
                "Failed to invoke Restart command on MccsSubarrayLeafNode.",
                "Mccssubarrayleafnode.Restart()",
                tango.ErrSeverity.ERR,
            )
        self.this_server = TangoServerHelper.get_instance()
        self.mccs_sa_fqdn = self.this_server.read_property("MccsSubarrayFQDN")[0]
        self.mccs_sa_client = TangoClient(self.mccs_sa_fqdn)
        if self.mccs_sa_client.get_attribute("obsState").value not in [ObsState.ABORTED, ObsState.FAULT]:
            tango.Except.throw_exception(const.ERR_INVOKING_CMD, const.ERR_RESTART_COMMAND,
                                            "MccsSubarrayLeafNode.RestartCommand",
                                            tango.ErrSeverity.ERR)
        
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
        # Update logs and activity message attribute with received event
        if event.err:
            log_msg = f"{const.ERR_INVOKING_CMD}{event.cmd_name}\n{event.errors}"
            self.logger.error(log_msg)
            self.this_server.write_attr("activityMessage", log_msg, False)
        else:
            log_msg = f"{const.STR_COMMAND}{event.cmd_name}{const.STR_INVOKE_SUCCESS}"
            self.logger.info(log_msg)
            self.this_server.write_attr("activityMessage", log_msg, False)

    def do(self):
        """
         Method to invoke Restart command on MCCS Controller.

        :param argin: None

        return:
            None

        raises:
            DevFailed if the command execution is not successful

        """
        try:
            # On mccs side this implementation is not finalize yet modifications are expected.
            # Hence hardcoded controller FQDN and input arguement (subarray ID).
            mccs_controller_fqdn = "low-mccs/control/control"
            input_to_mccs_controller = {"subarray_id":1}
            argin = json.dumps(input_to_mccs_controller)
            mccs_controller_client = TangoClient(mccs_controller_fqdn)
            mccs_controller_client.send_command_async(
                const.CMD_RESTART, argin, self.restart_cmd_ended_cb
            )
            self.this_server.write_attr("activityMessage", const.STR_RESTART_SUCCESS, False)
            self.logger.info(const.STR_RESTART_SUCCESS)

        except DevFailed as dev_failed:
            log_msg = f"{const.ERR_RESTART_COMMAND}{dev_failed}"
            self.this_server.write_attr("activityMessage", log_msg, False)
            self.logger.exception(dev_failed)
            tango.Except.throw_exception(
                const.ERR_RESTART_COMMAND,
                log_msg,
                "MccsSubarrayLeafNode.Restart",
                tango.ErrSeverity.ERR,
            )
