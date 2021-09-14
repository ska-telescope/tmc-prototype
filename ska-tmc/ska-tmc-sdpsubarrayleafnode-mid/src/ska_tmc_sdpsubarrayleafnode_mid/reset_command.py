# Third Party imports
# PyTango imports
import tango
from tango import DevState, DevFailed

# Additional import
from ska.base.commands import BaseCommand
from ska.base.control_model import ObsState

from tmc.common.tango_client import TangoClient
from tmc.common.tango_server_helper import TangoServerHelper
from ska.base.commands import ResultCode


from . import const

class ResetCommand(BaseCommand):
    """
    A class for SDPSubarrayLeafNode's Reset() command.

    Command to reset the current operation being done on the SDP Subarray.

    """
    def check_allowed(self):
        """
        Checks whether this command is allowed to be run in current device state

        :return: True if this command is allowed to be run in current device state

        :rtype: boolean

        :raises: DevFailed if this command is not allowed to be run in current device state

        """
        if self.state_model.op_state in [
            DevState.UNKNOWN,
            DevState.DISABLE,
        ]:
            tango.Except.throw_exception(
                f"Reset() is not allowed in current state {self.state_model.op_state}",
                "Failed to invoke Reset command on SdpSubarrayLeafNode.",
                "sdpsubarrayleafnode.Reset()",
                tango.ErrSeverity.ERR,
            )

        this_server = TangoServerHelper.get_instance()
        sdp_subarray_fqdn = this_server.read_property("SdpSubarrayFQDN")[0]
        sdp_sa_client = TangoClient(sdp_subarray_fqdn)
        if sdp_sa_client.get_attribute("obsState").value not in [ObsState.READY, ObsState.CONFIGURING, ObsState.SCANNING,
                                                        ObsState.IDLE, ObsState.RESETTING, ObsState.FAULT]:
            tango.Except.throw_exception(const.ERR_UNABLE_RESET_CMD, const.ERR_RESET_INVOKING_CMD,
                                        "SdpSubarrayLeafNode.ResetCommand",
                                        tango.ErrSeverity.ERR)
        return True


    def reset_cmd_ended_cb(self, event):
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
        This command invokes Reset command on SDP Subarray.

        return:
            None

        raises:
            DevFailed if error occurs while invoking command on SDP Subarray.

        """
        try:
            this_server = TangoServerHelper.get_instance()
            sdp_subarray_fqdn = ""
            property_val = this_server.read_property("SdpSubarrayFQDN")
            sdp_subarray_fqdn = sdp_subarray_fqdn.join(property_val)
            sdp_sub_client_obj = TangoClient(sdp_subarray_fqdn)
            sdp_sub_client_obj.send_command_async(
                const.CMD_RESET, None, self.reset_cmd_ended_cb
            )
            this_server.write_attr("activityMessage", const.STR_RESET_SUCCESS, False)
            self.logger.info(const.STR_RESET_SUCCESS)
            return (ResultCode.OK, const.STR_RESET_SUCCESS)

        except DevFailed as dev_failed:
            log_msg = f"{const.ERR_RESET_INVOKING_CMD}{dev_failed}"
            this_server.write_attr("activityMessage", log_msg, False)
            self.logger.exception(dev_failed)
            tango.Except.throw_exception(
                const.STR_RESET_EXEC,
                log_msg,
                "sdpSubarrayLeafNode.ResetCommand",
                tango.ErrSeverity.ERR,
            )
