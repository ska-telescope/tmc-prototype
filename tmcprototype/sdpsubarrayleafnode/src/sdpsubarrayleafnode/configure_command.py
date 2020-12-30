"""
Configure class for SDPSubarrayLeafNode.
"""
# PROTECTED REGION ID(SDPSubarrayLeafNode.additionnal_import) ENABLED START #
# Standard Python imports
import tango
from tango import DevState, DevFailed
# Additional import
from ska.base.commands import BaseCommand
from ska.base.control_model import ObsState
from . import const
from .transaction_id import identify_with_id
from tmc.common.tango_client import TangoClient


class Configure(BaseCommand):
    """
    A class for SdpSubarrayLeafNode's Configure() command.
    """

    def check_allowed(self):
        """
        Checks whether this command is allowed to be run in current device state

        :return: True if this command is allowed to be run in current device state

        :rtype: boolean

        :raises: Exception if command execution throws any type of exception

        """
        device_data = self.target
        if self.state_model.op_state in [DevState.FAULT, DevState.UNKNOWN, DevState.DISABLE]:
            tango.Except.throw_exception("Configure() is not allowed in current state",
                                            "Failed to invoke Configure command on SdpSubarrayLeafNode.",
                                            "sdpsubarrayleafnode.Configure()",
                                        tango.ErrSeverity.ERR)

        sdp_sa_ln_client = TangoClient(device_data._sdp_sa_fqdn)
        if sdp_sa_ln_client.get_attribute("obsState") not in [ObsState.IDLE, ObsState.READY]:
            tango.Except.throw_exception(const.ERR_DEVICE_NOT_READY_IDLE, "Failed to invoke Configure command on SdpSubarrayLeafNode."
                                            "SdpSubarrayLeafNode.Configure()",
                                            tango.ErrSeverity.ERR)

        # if device._sdp_subarray_proxy.obsState not in [ObsState.IDLE, ObsState.READY]:
        #     tango.Except.throw_exception(const.ERR_DEVICE_NOT_READY_IDLE, "Failed to invoke Configure command on SdpSubarrayLeafNode.",
        #                                     "SdpSubarrayLeafNode.ConfigureCommand()",
        #                                     tango.ErrSeverity.ERR)
        return True

    def configure_cmd_ended_cb(self, event):
        """
        Callback function immediately executed when the asynchronous invoked command returns.
        Checks whether the configure command has been successfully invoked on SDP Subarray.

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
        if event.err:
            log = const.ERR_INVOKING_CMD + str(event.cmd_name) + "\n" + str(event.errors)
            device_data._read_activity_message = log
            self.logger.error(log)
        else:
            log = const.STR_COMMAND + event.cmd_name + const.STR_INVOKE_SUCCESS
            device_data._read_activity_message = log
            self.logger.info(log)

    @identify_with_id('configure','argin')
    def do(self, argin):
        """
        Configures the SDP Subarray device by providing the SDP PB
        configuration needed to execute the receive workflow

        :param argin: The string in JSON format. The JSON contains following values:

        Example:

        { "scan_type": "science_A" }

        :return: None

        :raises: ValueError if input argument json string contains invalid value.
                    KeyError if input argument json string contains invalid key.
                    DevFailed if the command execution is not successful
        """
        device_data = self.target
        try:
            log_msg = "Input JSON for SDP Subarray Leaf Node Configure command is: " + argin
            self.logger.debug(log_msg)
            sdp_sa_ln_client_obj = TangoClient(device_data._sdp_sa_fqdn)
            sdp_sa_ln_client_obj.send_command_async(const.CMD_CONFIGURE, argin, self.configure_cmd_ended_cb)
            # device._sdp_subarray_proxy.command_inout_asynch(const.CMD_CONFIGURE, argin,
            #                                                 self.configure_cmd_ended_cb)
            device_data._read_activity_message = const.STR_CONFIGURE_SUCCESS
            self.logger.info(const.STR_CONFIGURE_SUCCESS)

        except DevFailed as dev_failed:
            log_msg = const.ERR_CONFIGURE + str(dev_failed)
            device_data._read_activity_message = log_msg
            self.logger.exception(dev_failed)
            tango.Except.throw_exception(const.STR_CONFIG_EXEC, log_msg,
                                            "SdpSubarrayLeafNode.Configure()",
                                            tango.ErrSeverity.ERR)
