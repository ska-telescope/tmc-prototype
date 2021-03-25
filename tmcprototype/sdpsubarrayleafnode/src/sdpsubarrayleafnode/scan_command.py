"""
Scan class for SDPSubarrayLeafNode.
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


class Scan(BaseCommand):
    """
    A class for SdpSubarrayLeafNode's Scan() command.

    Invoke Scan command to SDP Subarray.
    """

    def check_allowed(self):
        """
        Checks whether this command is allowed to be run in current device state.

        :return: True if this command is allowed to be run in current device state.

        :rtype: boolean

        :raises: Exception if command execution throws any type of exception.

        """
        if self.state_model.op_state in [
            DevState.FAULT,
            DevState.UNKNOWN,
            DevState.DISABLE,
        ]:
            tango.Except.throw_exception(
                f"Scan() is not allowed in current state {self.state_model.op_state}",
                "Failed to invoke Scan command on SdpSubarrayLeafNode.",
                "sdpsubarrayleafnode.Scan()",
                tango.ErrSeverity.ERR,
            )

        # TODO: Mock obs_state issue to be resolved
        return True

    def scan_cmd_ended_cb(self, event):
        """
        Callback function immediately executed when the asynchronous invoked command returns.
        Checks whether the scan command has been successfully invoked on SDP Subarray.

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

    def do(self, argin):
        """
        Method to invoke Scan command on SDP Subarray.

        :param argin: The string in JSON format. The JSON contains following values:

        Example:
        {“id”:1}

        Note: Enter input as without spaces:{“id”:1}

        return:
            None

        raises:
            DevFailed if the command execution is not successful.
        """
        self.this_server = TangoServerHelper.get_instance()
        try:
            log_msg = "Input JSON for SDP Subarray Leaf Node Scan command is: " + argin
            self.logger.debug(log_msg)
            _sdp_sa_fqdn = ""
            input = self.this_server.read_property("SdpSubarrayFQDN")
            _sdp_sa_fqdn = _sdp_sa_fqdn.join(input)
            sdp_sa_ln_client_obj = TangoClient(_sdp_sa_fqdn)
            sdp_sa_ln_client_obj.send_command_async(
                const.CMD_SCAN, command_data=argin, callback_method=self.scan_cmd_ended_cb
                )
            self.this_server.write_attr("activityMessage", const.STR_SCAN_SUCCESS)
            self.logger.info(const.STR_SCAN_SUCCESS)

        except DevFailed as dev_failed:
            log_msg = f"{const.ERR_SCAN}{dev_failed}"
            self.this_server.write_attr("activityMessage", log_msg)
            self.logger.exception(dev_failed)
            tango.Except.throw_exception(
                const.STR_SCAN_EXEC,
                log_msg,
                "SdpSubarrayLeafNode.Scan()",
                tango.ErrSeverity.ERR,
            )
