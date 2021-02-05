"""
Off class for SDPSubarrayLeafNode.
"""
# PROTECTED REGION ID(sdpsubarrayleafnode.additionnal_import) ENABLED START #
# Tango imports
import tango
from tango import DevFailed

# Additional import
from ska.base import SKABaseDevice
from ska.base.commands import ResultCode

from tmc.common.tango_client import TangoClient

from . import const


class Off(SKABaseDevice.OffCommand):
    """
    A class for SDP Subarray's Off() command.
    """

    def off_cmd_ended_cb(self, event):
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
        device_data = self.target
        if event.err:
            log = (
                const.ERR_INVOKING_CMD + str(event.cmd_name) + "\n" + str(event.errors)
            )
            device_data._read_activity_message = log
            self.logger.error(log)
        else:
            log = const.STR_COMMAND + event.cmd_name + const.STR_INVOKE_SUCCESS
            device_data._read_activity_message = log
            self.logger.info(log)

    def do(self):
        """
        Invokes Off command on the SDP Subarray.

        :param argin: None.

        :return: A tuple containing a return code and a string message indicating status.
        The message is for information purpose only.

        :rtype: (ResultCode, str)

        """
        device_data = self.target
        try:
            sdp_sa_ln_client_obj = TangoClient(device_data._sdp_sa_fqdn)
            sdp_sa_ln_client_obj.send_command_async(
                const.CMD_OFF, None, self.off_cmd_ended_cb
            )
            log_msg = const.CMD_OFF + const.STR_COMMAND + const.STR_INVOKE_SUCCESS
            self.logger.debug(log_msg)

            return (ResultCode.OK, log_msg)

        except DevFailed as dev_failed:
            log_msg = const.ERR_INVOKING_OFF_CMD + str(dev_failed)
            device_data._read_activity_message = log_msg
            self.logger.exception(dev_failed)
            tango.Except.throw_exception(
                const.STR_OFF_EXEC,
                log_msg,
                "SdpSubarrayLeafNode.Off()",
                tango.ErrSeverity.ERR,
            )
