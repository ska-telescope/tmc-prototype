# PROTECTED REGION ID(MccsMasterLeafNode.import) ENABLED START #
# Tango imports
import tango
from tango import DevState, DevFailed

# Additional import
from ska.base.commands import BaseCommand
from tmc.common.tango_client import TangoClient
from . import const
# PROTECTED REGION END #    //  MccsMasterLeafNode imports


class AssignResources(BaseCommand):
    """
    A class for MccsMasterLeafNode's AssignResources() command.
    """

    def check_allowed(self):
        """
        Checks whether the command is allowed to be run in the current state

        :return: True if this command is allowed to be run in current device state

        :rtype: boolean

        :raises: DevFailed if this command is not allowed to be run
            in current device state

        """
        if self.state_model.op_state in [DevState.FAULT, DevState.UNKNOWN, DevState.DISABLE]:
            tango.Except.throw_exception("AssignResources() is not allowed in current state",
                                            "Failed to invoke AssignResources command on "
                                            "mccsmasterleafnode.",
                                            "mccsmasterleafnode.AssignResources()",
                                            tango.ErrSeverity.ERR)
        return True

    def allocate_ended(self, event):
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

        :raises: DevFailed if this command is not allowed to be run
        in current device state

        """
        device_data = self.target
        self.logger.info("Executing callback allocate_ended")
        try:
            if event.err:
                device_data._read_activity_message = const.ERR_INVOKING_CMD + str(event.cmd_name) + "\n" + str(
                    event.errors)
                log = const.ERR_INVOKING_CMD + event.cmd_name
                self.logger.error(log)
            else:
                log = const.STR_COMMAND + event.cmd_name + const.STR_INVOKE_SUCCESS
                device_data._read_activity_message = log
                self.logger.info(log)

        except tango.DevFailed as df:
            self.logger.exception(df)
            tango.Except.re_throw_exception(df, "MCCS master gave an error response",
                                            "MCCS master threw error in Allocate MCCS LMC_CommandFailed",
                                            "Allocate", tango.ErrSeverity.ERR)

    def do(self, argin):
        """
        It accepts stationiDList list, channels and stationBeamiDList in JSON string format and invokes allocate command on MccsMaster
        with JSON string as an input argument.

        :param argin:StringType. The string in JSON format.
            
        Example:
        {
            "subarray_id": 1,
            "station_ids": [1,2],
            "channels": [1,2,3,4,5,6,7,8],
            "station_beam_ids": [1]
        }

        :return: None

        Note: Enter the json string without spaces as an input.

        :raises: ValueError if input argument json string contains invalid value
                    KeyError if input argument json string contains invalid key
                    DevFailed if the command execution is not successful
        """
        device_data = self.target
        try:
            log_msg = "Input JSON for MCCS master leaf node AssignResources command is: " + argin
            self.logger.debug(log_msg)
            self.logger.info("Invoking Allocate on MCCS master")
            mccs_mln_client_obj = TangoClient(device_data._mccs_master_ln_fqdn)
            mccs_mln_client_obj.send_command_async(const.CMD_ALLOCATE, None, self.allocate_ended)
            self.logger.info("After invoking Allocate on MCCS master")
            device_data._read_activity_message = const.STR_ALLOCATE_SUCCESS
            self.logger.info(const.STR_ALLOCATE_SUCCESS)

        except ValueError as value_error:
            log_msg = const.ERR_INVALID_JSON_ASSIGN_RES_MCCS + str(value_error)
            device_data._read_activity_message = const.ERR_INVALID_JSON_ASSIGN_RES_MCCS + str(value_error)
            self.logger.exception(value_error)
            tango.Except.re_throw_exception(value_error, const.STR_ASSIGN_RES_EXEC, log_msg,
                                            "MccsMasterLeafNode.AssignResources",
                                            tango.ErrSeverity.ERR)

        except KeyError as key_error:
            log_msg = const.ERR_JSON_KEY_NOT_FOUND + str(key_error)
            device_data._read_activity_message = const.ERR_JSON_KEY_NOT_FOUND + str(key_error)
            self.logger.exception(key_error)
            tango.Except.re_throw_exception(key_error,const.STR_ASSIGN_RES_EXEC, log_msg,
                                            "MccsMasterLeafNode.AssignResources",
                                            tango.ErrSeverity.ERR)
        except DevFailed as dev_failed:
            log_msg = const.ERR_ASSGN_RESOURCE_MCCS + str(dev_failed)
            device_data._read_activity_message = log_msg
            self.logger.exception(dev_failed)
            tango.Except.re_throw_exception(dev_failed, const.STR_ASSIGN_RES_EXEC, log_msg,
                                            "MccsMasterLeafNode.AssignResources",
                                            tango.ErrSeverity.ERR)