"""
ReleaseResources class for SDPSubarrayLeafNode.
"""
# PROTECTED REGION ID(CentralNode.additionnal_import) ENABLED START #
# Standard Python imports
import json
import ast
import tango
from tango import DevState, DevFailed
# Additional import
from ska.base import SKABaseDevice
from ska.base.commands import ResultCode, BaseCommand
from . import const
from centralnode.device_data import DeviceData
from centralnode.tango_client import TangoClient

class ReleaseAllResources(BaseCommand):
    """
    A class for SdpSubarayLeafNode's ReleaseAllResources() command.
    """

    def check_allowed(self):
        """
        Checks whether this command is allowed to be run in current device state

        :return: True if this command is allowed to be run in current device state

        :rtype: boolean

        :raises: Exception if command execution throws any type of exception

        """
        device = self.target
        if self.state_model.op_state in [DevState.FAULT, DevState.UNKNOWN, DevState.DISABLE]:
            tango.Except.throw_exception("ReleaseAllResources() is not allowed in current state",
                                            "Failed to invoke ReleaseAllResources command on "
                                            "SdpSubarrayLeafNode.",
                                            "SdpSubarrayLeafNode.ReleaseAllResources()",
                                            tango.ErrSeverity.ERR)
        
        if device._sdp_subarray_proxy.obsState != ObsState.IDLE:
            tango.Except.throw_exception(const.STR_RELEASE_RES_EXEC, "Failed to invoke ReleaseAllResources command on "
                                            "SdpSubarrayLeafNode.",
                                            "SdpSubarrayLeafNode.ReleaseAllResourcesCommand()",
                                            tango.ErrSeverity.ERR)
        return True

    def releaseallresources_cmd_ended_cb(self, event):
        """
        Callback function immediately executed when the asynchronous invoked command returns.
        Checks whether the releaseallresources command has been successfully invoked on SDP Subarray.

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
        device = self.target
        if event.err:
            log = const.ERR_INVOKING_CMD + str(event.cmd_name) + str(event.errors)
            device._read_activity_message = log
            self.logger.error(log)
        else:
            log = const.STR_COMMAND + event.cmd_name + const.STR_INVOKE_SUCCESS
            device._read_activity_message = log
            self.logger.info(log)


    def do(self):
        """
        Releases all the resources of given SDPSubarrayLeafNode. It accepts the subarray id,
        releaseALL flag and receptorIDList in JSON string format.

        :param argin: None.

        :return: None

        :raises: DevFailed if the command execution is not successful.
        """
        device = self.target
        try:
            # Call SDP Subarray Command asynchronously
            device._sdp_subarray_proxy.command_inout_asynch(const.CMD_RELEASE_RESOURCES,
                                                            self.releaseallresources_cmd_ended_cb)
            # Update the status of command execution status in activity message
            device._read_activity_message = const.STR_REL_RESOURCES
            self.logger.info(const.STR_REL_RESOURCES)

        except DevFailed as dev_failed:
            log_msg = const.ERR_RELEASE_RESOURCES + str(dev_failed)
            device._read_activity_message = log_msg
            self.logger.exception(dev_failed)
            tango.Except.throw_exception(const.STR_RELEASE_RES_EXEC, log_msg,
                                            "SdpSubarrayLeafNode.ReleaseAllResourcesCommand()",
                                            tango.ErrSeverity.ERR)
