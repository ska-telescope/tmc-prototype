# PyTango imports
import tango
from tango import DevState, DevFailed
# Additional import
from tmc.common.tango_client import TangoClient
from ska.base.commands import BaseCommand
from . import const


class ReleaseAllResourcesCommand(BaseCommand):
    """
    A class for CspSubarrayLeafNode's ReleaseAllResources() command. ReleaseAllResources command is inherited from BaseCommand.

    It invokes RemoveAllReceptors command on CspSubarray and releases all the resources assigned to
    CspSubarray.

    """

    def check_allowed(self):
        """
        Checks whether the command is allowed to be run in the current state

        :return: True if this command is allowed to be run in current device state

        :rtype: boolean

        :raises: DevFailed if this command is not allowed to be run in current device state

        """
        if self.state_model.op_state in [DevState.FAULT, DevState.UNKNOWN, DevState.DISABLE]:
            tango.Except.throw_exception("ReleaseAllResources() is not allowed in current state",
                                            "Failed to invoke ReleaseAllResources command on "
                                            "cspsubarrayleafnode.",
                                            "cspsubarrayleafnode.ReleaseAllResources()",
                                            tango.ErrSeverity.ERR)
        #TODO: When ObsState check related issue is resolved
        # csp_sa_client = TangoClient(device_data.csp_subarray_fqdn)
        # if csp_sa_client.get_attribute("obsState") != ObsState.IDLE:
        #     tango.Except.throw_exception(const.ERR_DEVICE_NOT_IDLE, "Failed to invoke ReleaseAllResourcesCommand command on cspsubarrayleafnode.",
        #                                     "CspSubarrayLeafNode.ReleaseAllResourcesCommand",
        #                                     tango.ErrSeverity.ERR)

        return True

    def releaseallresources_cmd_ended_cb(self, event):
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
        device_data = self.target
        # Update logs and activity message attribute with received event
        if event.err:
            log_msg = const.ERR_INVOKING_CMD + str(event.cmd_name) + "\n" + str(event.errors)
            self.logger.error(log_msg)
            device_data._read_activity_message = log_msg
        else:
            log_msg = const.STR_COMMAND + str(event.cmd_name) + const.STR_INVOKE_SUCCESS
            self.logger.info(log_msg)
            device_data._read_activity_message = log_msg

    def do(self):
        """
        Method to invoke ReleaseAllResources command on CSP Subarray.

        return:
            None

        raises:
            DevFailed if the command execution is not successful

        """
        device_data = self.target
        try:
            # Invoke RemoveAllResources command on CspSubarray
            device_data.receptorIDList = []
            device_data.fsids_list = []
            csp_sub_client_obj = TangoClient(device_data.csp_subarray_fqdn)
            csp_sub_client_obj.send_command_async(const.CMD_RELEASE_ALL_RESOURCES, None , self.releaseallresources_cmd_ended_cb)
            device_data._read_activity_message = const.STR_RELEASE_ALL_RESOURCES_SUCCESS
            self.logger.info(const.STR_RELEASE_ALL_RESOURCES_SUCCESS)

        except DevFailed as dev_failed:
            log_msg = const.ERR_RELEASE_ALL_RESOURCES + str(dev_failed)
            device_data._read_activity_message = log_msg
            self.logger.exception(dev_failed)
            tango.Except.throw_exception(const.STR_RELEASE_RES_EXEC, log_msg,
                                            "CspSubarrayLeafNode.ReleaseAllResourcesCommand",
                                            tango.ErrSeverity.ERR)
