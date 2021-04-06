"""
EndScan class for SDPSubarrayLeafNode.
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


class EndScan(BaseCommand):
    """
    A class for SdpSubarrayLeafNode's EndScan() command.

    It invokes EndScan command on Sdp Subarray.
    This command is allowed when Sdp Subarray is in SCANNING state.
    """

    def check_allowed(self):
        """
        Checks whether this command is allowed to be run in current device
        state

        :return: True if this command is allowed to be run in current device state

        :rtype: boolean

        :raises: Exception if command execution throws any type of exception.

        """
        if self.state_model.op_state in [
            DevState.FAULT,
            DevState.UNKNOWN,
            DevState.DISABLE,
        ]:
            tango.Except.throw_exception(
                f"EndScan() is not allowed in current state{self.state_model.op_state}",
                "Failed to invoke EndScan command on SdpSubarrayLeafNode.",
                "sdpsubarrayleafnode.EndScan()",
                tango.ErrSeverity.ERR,
            )

        # TODO: Mock obs_state issue to be resolved
        # device_data = self.target
        # sdp_sa_ln_client = TangoClient(device_data._sdp_sa_fqdn)
        # if sdp_sa_ln_client.get_attribute("obsState") != ObsState.SCANNING:
        #     tango.Except.throw_exception(const.ERR_DEVICE_NOT_IN_SCAN, "Failed to invoke EndScan command on SdpSubarrayLeafNode."
        #                                     "SdpSubarrayLeafNode.EndScan()",
        #                                     tango.ErrSeverity.ERR)
        return True

    def endscan_cmd_ended_cb(self, event):
        """
        Callback function immediately executed when the asynchronous invoked command returns.
        Checks whether the endscan command has been successfully invoked on SDP Subarray.

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
        Method to invoke EndScan command on SDP Subarray.

        :param argin: None

        return:
            None

        raises:
            DevFailed if the command execution is not successful.
        """
        this_server = TangoServerHelper.get_instance()
        try:
            sdp_sa_ln_client_obj=TangoClient(this_server.read_property("SdpSubarrayFQDN")[0])
            sdp_sa_ln_client_obj.send_command_async(
                const.CMD_ENDSCAN, None, self.endscan_cmd_ended_cb
            )
            this_server.write_attr("activityMessage", const.STR_ENDSCAN_SUCCESS, False)
            self.logger.info(const.STR_ENDSCAN_SUCCESS)

        except DevFailed as dev_failed:
            log_msg = f"{const.ERR_ENDSCAN_INVOKING_CMD}{dev_failed}"
            this_server.write_attr("activityMessage", log_msg, False)
            self.logger.exception(dev_failed)
            tango.Except.throw_exception(
                const.STR_ENDSCAN_EXEC,
                log_msg,
                "SdpSubarrayLeafNode.EndScan()",
                tango.ErrSeverity.ERR,
            )
