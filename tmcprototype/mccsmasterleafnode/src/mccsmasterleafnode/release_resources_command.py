# PROTECTED REGION ID(MccsMasterLeafNode.import) ENABLED START #
# Tango imports
import tango
from tango import DevState, DevFailed

# Additional import
from ska.base.commands import BaseCommand

from tmc.common.tango_client import TangoClient
from tmc.common.tango_server_helper import TangoServerHelper

from . import const

# PROTECTED REGION END #    //  MccsMasterLeafNode imports


class ReleaseResources(BaseCommand):
    """
    A class for MccsMasterLeafNode's ReleaseResources() command.

    It invokes ReleaseResources command on MccsMaster and releases all the resources assigned to
    MccsMaster.
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
        # Update logs and activity message attribute with received event
        if event.err:
            log_msg = f"{const.ERR_INVOKING_CMD}{event.cmd_name}\n{event.errors}"
            self.logger.error(log_msg)
            self.this_server.write_attr("activityMessage", log_msg, False)
        else:
            log_msg = f"{const.STR_COMMAND}{event.cmd_name}{const.STR_INVOKE_SUCCESS}"
            self.logger.info(log_msg)
            self.this_server.write_attr("activityMessage", log_msg, False)

    def do(self, argin):
        """
        Method to invoke ReleaseResources command on Mccs Master.

        :param argin:
                     StringType. The string in JSON format.

        Example:
             {
                "subarray_id": 1,
                "release_all": true
               }

        return:
            None.

        raises:
            DevFailed if the command execution is not successful

            ValueError if invalid json string.

        """
        log_msg = "Input JSON for MCCS master leaf node Release command is: " + argin
        self.logger.debug(log_msg)
        self.logger.info("Invoking Release on MCCS master")

        try:
            self.this_server = TangoServerHelper.get_instance()
            mccs_master_fqdn = ""
            property_value = self.this_server.read_property("MccsMasterFQDN")
            mccs_master_fqdn = mccs_master_fqdn.join(property_value)
            mccs_master_client = TangoClient(mccs_master_fqdn)
            mccs_master_client.send_command_async(
                const.CMD_Release, argin, self.releaseresources_cmd_ended_cb
            )
            self.this_server.write_attr("activityMessage", const.STR_REMOVE_ALL_RECEPTORS_SUCCESS, False)
            self.logger.info(const.STR_REMOVE_ALL_RECEPTORS_SUCCESS)

        except ValueError as value_error:
            log_msg = f"{const.ERR_INVALID_JSON_RELEASE_RES_MCCS}{value_error}"
            self.this_server.write_attr("activityMessage",
                                        f"{const.ERR_INVALID_JSON_RELEASE_RES_MCCS}{value_error}", False)
            self.logger.exception(value_error)
            tango.Except.re_throw_exception(
                value_error,
                const.STR_RELEASE_RES_EXEC,
                log_msg,
                "MccsMasterLeafNode.ReleaseResources",
                tango.ErrSeverity.ERR,
            )

        except DevFailed as dev_failed:
            log_msg = f"{const.ERR_RELEASE_ALL_RESOURCES} {dev_failed}"
            self.this_server.write_attr("activityMessage", log_msg, False)
            self.logger.exception(dev_failed)
            tango.Except.re_throw_exception(
                dev_failed,
                const.STR_RELEASE_RES_EXEC,
                log_msg,
                "MccsMasterLeafNode.ReleaseAllResources",
                tango.ErrSeverity.ERR,
            )
