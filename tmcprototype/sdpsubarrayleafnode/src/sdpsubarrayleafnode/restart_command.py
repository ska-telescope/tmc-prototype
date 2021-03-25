"""
Restart class for SDPSubarrayLeafNode.
"""
# PROTECTED REGION ID(sdpsubarrayleafnode.additionnal_import) ENABLED START #
# Tango imports
import tango
from tango import DevState, DevFailed

# Additional import
from ska.base.commands import BaseCommand

from tmc.common.tango_client import TangoClient
from tmc.common.tango_server_helper import TangoServerHelper

from . import const


class Restart(BaseCommand):
    """
    A class for sdpSubarrayLeafNode's Restart() command.

    Command to restart the SDP Subarray and bring it to its ON state.

    """

    def check_allowed(self):
        """
        Checks whether this command is allowed to be run in current device state

        :return: True if this command is allowed to be run in current device state

        :rtype: boolean

        :raises: DevFailed if this command is not allowed to be run in current device state

        """
        if self.state_model.op_state in [DevState.UNKNOWN, DevState.DISABLE]:
            tango.Except.throw_exception(
                f"Restart() is not allowed in current state {self.state_model.op_state}",
                "Failed to invoke Restart command on SdpSubarrayLeafNode.",
                "sdpsubarrayleafnode.Restart()",
                tango.ErrSeverity.ERR,
            )

        # TODO: Mock obs_state issue to be resolved
        # device_data = self.target
        # sdp_sa_ln_client_obj = TangoClient(device_data._sdp_sa_fqdn)
        # if sdp_sa_ln_client_obj.get_attribute("obsState") not in [ObsState.ABORTED, ObsState.FAULT]:
        #     tango.Except.throw_exception(const.ERR_DEVICE_NOT_ABORTED_FAULT, "Failed to invoke Restart command on SdpSubarrayLeafNode.",
        #                                 "SdpSubarrayLeafNode.Restart()",
        #                                 tango.ErrSeverity.ERR)
        return True

    def restart_cmd_ended_cb(self, event):
        """
        Callback function immediately executed when the asynchronous invoked command returns.
        Checks whether the restart command has been successfully invoked on SDP Subarray.

        :param event: A CmdDoneEvent object.
        This class is used to pass data to the callback method in asynchronous callback model
        for command execution.

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
            log = f"{const.ERR_INVOKING_CMD}{event.cmd_name}\n{event.errors}"
            self.this_server.write_attr("activityMessage", log)
            self.logger.error(log)
        else:
            log = const.STR_COMMAND + event.cmd_name + const.STR_INVOKE_SUCCESS
            self.this_server.write_attr("activityMessage", log)
            self.logger.info(log)

    def do(self):
        """
        Method to invoke Restart command on SDP Subarray.

        return:
            None

        raises:
            DevFailed if error occurs while invoking command on SDPSubarray.

        """
        self.this_server = TangoServerHelper.get_instance()
        try:
            _sdp_sa_fqdn = ""
            input = self.this_server.read_property("SdpSubarrayFQDN")
            _sdp_sa_fqdn = _sdp_sa_fqdn.join(input)
            sdp_sa_ln_client_obj = TangoClient(_sdp_sa_fqdn)
            sdp_sa_ln_client_obj.send_command_async(
               const.CMD_RESTART, callback_method=self.restart_cmd_ended_cb
               )
            self.this_server.write_attr("activityMessage", const.STR_RESTART_SUCCESS)
            self.logger.info(const.STR_RESTART_SUCCESS)

        except DevFailed as dev_failed:
            log_msg = f"{const.ERR_RESTART_INVOKING_CMD}{dev_failed}"
            self.this_server.write_attr("activityMessage", log_msg)
            self.logger.exception(dev_failed)
            tango.Except.throw_exception(
                const.STR_RESTART_EXEC,
                log_msg,
                "SdpSubarrayLeafNode.RestartCommand()",
                tango.ErrSeverity.ERR,
            )
