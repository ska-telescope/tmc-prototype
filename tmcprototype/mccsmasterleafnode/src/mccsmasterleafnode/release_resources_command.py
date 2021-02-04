# PROTECTED REGION ID(MccsMasterLeafNode.import) ENABLED START #
# Tango imports
import tango
from tango import DevState, DevFailed

# Additional import
from ska.base.commands import BaseCommand
from tmc.common.tango_client import TangoClient
from . import const

# PROTECTED REGION END #    //  MccsMasterLeafNode imports


class ReleaseResources(BaseCommand):
    """
    A class for MccsMasterLeafNode's ReleaseResources() command.
    """

    def check_allowed(self):
        """
        Checks whether the command is allowed to be run in the current state

        :return: True if this command is allowed to be run in current device state

        :rtype: boolean

        :raises: ValueError if input argument json string contains invalid value
                DevFailed if this command is not allowed to be run in current device state

        """
        if self.state_model.op_state in [
            DevState.FAULT,
            DevState.UNKNOWN,
            DevState.DISABLE,
        ]:
            tango.Except.throw_exception(
                f"ReleaseResources() is not allowed in current state {self.state_model.op_state}",
                "Failed to invoke ReleaseResources command on " "mccsmasterleafnode.",
                "mccsmasterleafnode.ReleaseResources()",
                tango.ErrSeverity.ERR,
            )
        return True

    def releaseresources_cmd_ended_cb(self, event):
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
            log_msg = (
                const.ERR_INVOKING_CMD + str(event.cmd_name) + "\n" + str(event.errors)
            )
            self.logger.error(log_msg)
            device_data._read_activity_message = log_msg
        else:
            log_msg = const.STR_COMMAND + str(event.cmd_name) + const.STR_INVOKE_SUCCESS
            self.logger.info(log_msg)
            device_data._read_activity_message = log_msg

    def do(self, argin):
        """
        It invokes ReleaseResources command on MccsMaster and releases all the resources assigned to
        MccsMaster.

        :param argin:StringType. The string in JSON format.

        Example:
             {
                "subarray_id": 1,
                "release_all": true
               }


        :return: None.

        :raises: DevFailed if the command execution is not successful


        """
        device_data = self.target
        log_msg = "Input JSON for MCCS master leaf node Release command is: " + argin
        self.logger.debug(log_msg)
        self.logger.info("Invoking Release on MCCS master")

        try:
            mccs_master_client = TangoClient(device_data._mccs_master_fqdn)
            mccs_master_client.send_command_async(
                const.CMD_Release, argin, self.releaseresources_cmd_ended_cb
            )
            device_data._read_activity_message = const.STR_REMOVE_ALL_RECEPTORS_SUCCESS
            self.logger.info(const.STR_REMOVE_ALL_RECEPTORS_SUCCESS)

        except ValueError as value_error:
            log_msg = const.ERR_INVALID_JSON_RELEASE_RES_MCCS + str(value_error)
            device_data._read_activity_message = (
                const.ERR_INVALID_JSON_RELEASE_RES_MCCS + str(value_error)
            )
            self.logger.exception(value_error)
            tango.Except.re_throw_exception(
                value_error,
                const.STR_RELEASE_RES_EXEC,
                log_msg,
                "MccsMasterLeafNode.ReleaseResources",
                tango.ErrSeverity.ERR,
            )

        except DevFailed as dev_failed:
            log_msg = const.ERR_RELEASE_ALL_RESOURCES + str(dev_failed)
            device_data._read_activity_message = log_msg
            self.logger.exception(dev_failed)
            tango.Except.re_throw_exception(
                dev_failed,
                const.STR_RELEASE_RES_EXEC,
                log_msg,
                "MccsMasterLeafNode.ReleaseAllResources",
                tango.ErrSeverity.ERR,
            )
