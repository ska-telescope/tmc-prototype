"""
On class for SDPSubarrayLeafNode.
"""
# PROTECTED REGION ID(sdpsubarrayleafnode.additionnal_import) ENABLED START #
# Tango imports
import tango
from tango import DevFailed
# Additional import
from ska.base import SKABaseDevice
from ska.base.commands import ResultCode
from tmc.common.tango_client import TangoClient
from tmc.common.tango_server_helper import TangoServerHelper
from . import const


class On(SKABaseDevice.OnCommand):
    """
    A class for SDP Subarray's On() command.

    Invokes On command on the SDP Subarray.
    """

    def on_cmd_ended_cb(self, event):
        """
        Callback function executes when the command invoked asynchronously returns from the server.

        :param event: A CmdDoneEvent object. This class is used to pass data to the callback method in asynchronous
                        callback model for command execution.

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
        sdp_sa_ln_server = TangoServerHelper.get_instance()
        if event.err:
            log = const.ERR_INVOKING_CMD + str(event.cmd_name) + "\n" + str(event.errors)
            device_data._read_activity_message = log
            sdp_sa_ln_server.set_status(log)
            self.logger.error(log)
        else:
            log = const.STR_COMMAND + event.cmd_name + const.STR_INVOKE_SUCCESS
            device_data._read_activity_message = log
            sdp_sa_ln_server.set_status(log)
            self.logger.info(log)

    def do(self):
        """
        Method to invoke On command on SDP Subarray.

        :param argin: None.

        :return: A tuple containing a return code and a string message indicating status.
        The message is for information purpose only.

        :rtype: (ResultCode, str)

        :raises: DevFailed if error occurs while invoking command on SDPSubarray.

        """
        device_data = self.target
        try:
            sdp_sa_ln_server = TangoServerHelper.get_instance()
            sdp_sa_ln_client_obj = TangoClient(device_data._sdp_sa_fqdn)
            sdp_sa_ln_client_obj.send_command_async(const.CMD_ON, None, self.on_cmd_ended_cb)
            log_msg = const.CMD_ON + const.STR_COMMAND + const.STR_INVOKE_SUCCESS
            sdp_sa_ln_server.set_status(log_msg)
            self.logger.debug(log_msg)

            return (ResultCode.OK, log_msg)

        except DevFailed as dev_failed:
            log_msg = const.ERR_INVOKING_ON_CMD + str(dev_failed)
            device_data._read_activity_message = log_msg
            sdp_sa_ln_server.set_status(log_msg)
            self.logger.exception(dev_failed)
            tango.Except.throw_exception(const.STR_ON_EXEC, log_msg,
                                            "SdpSubarrayLeafNode.On()",
                                            tango.ErrSeverity.ERR)
