"""
ObsReset class for SDPSubarrayLeafNode.
"""
# PROTECTED REGION ID(sdpsubarrayleafnode.additionnal_import) ENABLED START #
# Tango imports
import tango
from tango import DevState, DevFailed
# Additional import
from ska.base.commands import  BaseCommand
# from ska.base.control_model import ObsState
from tmc.common.tango_client import TangoClient
from . import const

class ObsReset(BaseCommand):
    """
    A class for SdpSubarrayLeafNode's ObsResetCommand() command.
    """

    def check_allowed(self):
        """
        Checks whether this command is allowed to be run in current device state

        :return: True if this command is allowed to be run in current device state

        :rtype: boolean

        :raises: DevFailed if this command is not allowed to be run in current device state

        """
        if self.state_model.op_state in [DevState.UNKNOWN, DevState.DISABLE]:
            tango.Except.throw_exception("ObsResetCommand() is not allowed in current state",
                                            "Failed to invoke ObsReset command on SdpSubarrayLeafNode.",
                                            "sdpsubarrayleafnode.ObsResetCommand()",
                                            tango.ErrSeverity.ERR)

        # TODO: Mock obs_state issue to be resolved
        # device_data = self.target
        # sdp_sa_ln_client = TangoClient(device_data._sdp_sa_fqdn)
        # if sdp_sa_ln_client.get_attribute("obsState") not in [ObsState.ABORTED, ObsState.FAULT]:
        #     tango.Except.throw_exception(const.ERR_DEVICE_NOT_ABORTED_FAULT, "Failed to invoke ObsReset command on SdpSubarrayLeafNode."
        #                                     "SdpSubarrayLeafNode.ObsReset()",
        #                                     tango.ErrSeverity.ERR)
        return True

    def obsreset_cmd_ended_cb(self, event):
        """
        Callback function immediately executed when the asynchronous invoked command returns.
        Checks whether the ObsResetCommand has been successfully invoked on SDP Subarray.

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
            log = const.ERR_INVOKING_CMD + str(event.cmd_name) + "\n" + str(event.errors)
            device_data._read_activity_message = log
            self.logger.error(log)
        else:
            log = const.STR_COMMAND + event.cmd_name + const.STR_INVOKE_SUCCESS
            device_data._read_activity_message = log
            self.logger.info(log)

    def do(self):
        """
        Command to reset the SDP subarray and bring it to its RESETTING state.

        :param argin: None
        
        :return: None

        :raises: DevFailed if error occurs while invoking command on SDPSubarray.

        """
        device_data = self.target
        try:    
            sdp_sa_ln_client_obj = TangoClient(device_data._sdp_sa_fqdn)
            sdp_sa_ln_client_obj.send_command_async(const.CMD_OBSRESET, None, self.obsreset_cmd_ended_cb)
            device_data._read_activity_message = const.STR_OBSRESET_SUCCESS
            self.logger.info(const.STR_OBSRESET_SUCCESS)

        except DevFailed as dev_failed:
            log_msg = const.ERR_OBSRESET_INVOKING_CMD + str(dev_failed)
            device_data._read_activity_message = log_msg
            self.logger.exception(dev_failed)
            tango.Except.throw_exception(const.STR_OBSRESET_EXEC, log_msg,
                                            "SdpSubarrayLeafNode.ObsReset()",
                                            tango.ErrSeverity.ERR)

