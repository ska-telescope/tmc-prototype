"""
Abort class for SDPSubarrayLeafNode.
"""
# Tango imports
import tango
from tango import DevState, DevFailed

# Additional import
from ska.base.commands import BaseCommand
from ska.base.control_model import ObsState
from tmc.common.tango_client import TangoClient
from . import const
from tmc.common.tango_server_helper import TangoServerHelper


class Abort(BaseCommand):
    """
    A class for sdpSubarrayLeafNode's Abort() command.

    Command to abort the current operation being done on the SDP Subarray.
    """

    def check_allowed(self):
        """
        Checks whether this command is allowed to be run in current device state

        :return: True if this command is allowed to be run in current device state

        :rtype: boolean

        :raises: DevFailed if this command is not allowed to be run in current device state

        """
        this_server = TangoServerHelper.get_instance()
        sdp_subarray_fqdn = this_server.read_property("SdpSubarrayFQDN")[0]
        sdp_sa_client = TangoClient(sdp_subarray_fqdn)

        if self.state_model.op_state in [
            DevState.FAULT,
            DevState.UNKNOWN,
            DevState.DISABLE,
        ]:
            tango.Except.throw_exception(
                f"Abort() is not allowed in current state {self.state_model.op_state}",
                "Failed to invoke Abort command on SdpSubarrayLeafNode.",
                "sdpsubarrayleafnode.Abort()",
                tango.ErrSeverity.ERR,
            )

        if sdp_sa_client.get_attribute("obsState").value not in [ObsState.READY, ObsState.CONFIGURING,
                                                                 ObsState.SCANNING,
                                                                 ObsState.IDLE, ObsState.RESETTING]:
            tango.Except.throw_exception(const.ERR_ABORT_INVOKING_CMD, const.ERR_ABORT_INVOKING_CMD,
                                         "SdpSubarrayLeafNode.AbortCommand",
                                         tango.ErrSeverity.ERR)

        return True

    def abort_cmd_ended_cb(self, event):
        """
        Callback function immediately executed when the asynchronous invoked command returns.
        Checks whether the abort command has been successfully invoked on SDP Subarray.

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
        Method to invoke Abort command on SDP Subarray.

        return:
            None

        raises:
            DevFailed if error occurs while invoking command on SDP Subarray.

        """
        this_server = TangoServerHelper.get_instance()
        try:
            sdp_sa_ln_client_obj=TangoClient(this_server.read_property("SdpSubarrayFQDN")[0])
            sdp_sa_ln_client_obj.send_command_async(
                const.CMD_ABORT, callback_method=self.abort_cmd_ended_cb
                )
            this_server.write_attr("activityMessage", const.STR_ABORT_SUCCESS, False)
            self.logger.info(const.STR_ABORT_SUCCESS)

        except DevFailed as dev_failed:
            log_msg = f"{const.ERR_ABORT_INVOKING_CMD}{dev_failed}"
            this_server.write_attr("activityMessage", log_msg, False)
            self.logger.exception(dev_failed)
            tango.Except.throw_exception(
                const.STR_ABORT_EXEC,
                log_msg,
                "SdpSubarrayLeafNode.Abort()",
                tango.ErrSeverity.ERR,
            )
