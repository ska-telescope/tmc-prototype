"""
TelescopeOff class for SDPSubarrayLeafNode.
"""
# PROTECTED REGION ID(sdpsubarrayleafnode.additionnal_import) ENABLED START #
# Tango imports
import tango
from tango import DevFailed, DevState

# Additional import
from ska.base.commands import BaseCommand
from tmc.common.tango_client import TangoClient
from tmc.common.tango_server_helper import TangoServerHelper

from . import const


class TelescopeOff(BaseCommand):
    """
    A class for SDP Subarray's Off() command.

    Invokes Off command on the SDP Subarray.
    """

    def check_allowed(self):
        """
        Checks whether this command is allowed to be run in current device state

        :return: True if this command is allowed to be run in current device state

        :rtype: boolean

        :raises: DevFailed if this command is not allowed to be run in current device state

        """
        if self.state_model.op_state in [DevState.FAULT, DevState.UNKNOWN]:
            tango.Except.throw_exception(
                f"Command TelescopeOff is not allowed in current state {self.state_model.op_state}.",
                "Failed to invoke Off command on SdpSubarrayLeafNode.",
                "SdpSubarrayLeafNode.TelescopeOff()",
                tango.ErrSeverity.ERR,
            )

        return True

    def telescopeoff_cmd_ended_cb(self, event):
        """
        Callback function executes when the command invoked asynchronously returns from the server.

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
        this_server = TangoServerHelper.get_instance()
        if event.err:
            log = f"{const.ERR_INVOKING_CMD}{event.cmd_name}\n{event.errors}"
            this_server.write_attr("activityMessage", log, False)
            self.logger.error(log)
        else:
            log = const.STR_COMMAND + event.cmd_name + const.STR_INVOKE_SUCCESS
            this_server.write_attr("activityMessage", log, False)
            self.logger.info(log)

    def do(self):
        """
        Method to invoke Off command on SDP Subarray.

        :param argin: None.

        return: None

        raises:
            DevFailed if error occurs while invoking command on SDPSubarray.

        """
        this_server = TangoServerHelper.get_instance()
        try:
            sdp_sa_ln_client_obj=TangoClient(this_server.read_property("SdpSubarrayFQDN")[0])
            sdp_sa_ln_client_obj.send_command_async(
                const.CMD_OFF, None, self.telescopeoff_cmd_ended_cb
            )
            log_msg = const.CMD_OFF + const.STR_COMMAND + const.STR_INVOKE_SUCCESS
            self.logger.debug(log_msg)


        except DevFailed as dev_failed:
            log_msg = f"{const.ERR_INVOKING_OFF_CMD}{dev_failed}"
            this_server.write_attr("activityMessage", log_msg, False)
            self.logger.exception(dev_failed)
            tango.Except.throw_exception(
                const.STR_OFF_EXEC,
                log_msg,
                "SdpSubarrayLeafNode.TelescopeOff()",
                tango.ErrSeverity.ERR,
            )
