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


class AssignResources(BaseCommand):
    """
    A class for MccsMasterLeafNode's AssignResources() command.

     It accepts stationiDList list, channels and stationBeamiDList in JSON string format and invokes allocate command on MccsMaster
     with JSON string as an input argument.
    """

    def check_allowed(self):
        """
        Checks whether the command is allowed to be run in the current state

        :return: True if this command is allowed to be run in current device state

        :rtype: boolean

        :raises: DevFailed if this command is not allowed to be run
            in current device state

        """
        if self.state_model.op_state in [
            DevState.FAULT,
            DevState.UNKNOWN,
            DevState.DISABLE,
        ]:
            tango.Except.throw_exception(
                f"AssignResources() is not allowed in current state {self.state_model.op_state}",
                "Failed to invoke AssignResources command on " "mccsmasterleafnode.",
                "mccsmasterleafnode.AssignResources()",
                tango.ErrSeverity.ERR,
            )
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
        self.logger.info("Executing callback allocate_ended")
        try:

            if event.err:
                self.this_server.write_attr("activityMessage",
                                    f"{const.ERR_INVOKING_CMD}{event.cmd_name}\n{event.errors}")
                log = const.ERR_INVOKING_CMD + event.cmd_name
                self.logger.error(log)
            else:
                log = const.STR_COMMAND + event.cmd_name + const.STR_INVOKE_SUCCESS
                self.this_server.write_attr("activityMessage", log)
                self.logger.info(log)

        except tango.DevFailed as df:
            self.logger.exception(df)
            tango.Except.re_throw_exception(
                df,
                "MCCS master gave an error response",
                "MCCS master threw error in Allocate MCCS LMC_CommandFailed",
                "Allocate",
                tango.ErrSeverity.ERR,
            )

    def do(self, argin):
        """
        Method to invoke AssignResources command on MCCS Master.

        :param argin:
                     StringType. The string in JSON format.

        Example:
                {
                  "interface": "https://schema.skatelescope.org/ska-low-mccs-assignresources/1.0",
                  "subarray_id": 1,
                  "subarray_beam_ids": [
                    1
                  ],
                  "station_ids": [
                    [
                      1,
                      2
                    ]
                  ],
                  "channel_blocks": [
                    3
                  ]
                }

        Note: Enter the json string without spaces as an input.

        return:
            None

        raises:
            ValueError if input argument json string contains invalid value

            KeyError if input argument json string contains invalid key

            DevFailed if the command execution is not successful
        """
        try:
            self.this_server = TangoServerHelper.get_instance()
            log_msg = (
                "Input JSON for MCCS master leaf node AssignResources command is: "
                + argin
            )
            self.logger.debug(log_msg)

            mccs_master_fqdn = ""
            property_value = self.this_server.read_property("MccsMasterFQDN")
            mccs_master_fqdn = mccs_master_fqdn.join(property_value)
            mccs_master_client = TangoClient(mccs_master_fqdn)
            mccs_master_client.send_command_async(
                const.CMD_ALLOCATE, argin, self.allocate_ended
            )
            self.this_server.write_attr("activityMessage", const.STR_ALLOCATE_SUCCESS)
            self.logger.info(const.STR_ALLOCATE_SUCCESS)

        except DevFailed as dev_failed:
            log_msg = f"{const.ERR_ASSGN_RESOURCE_MCCS}{dev_failed}"
            self.this_server.write_attr("activityMessage", log_msg)
            self.logger.exception(dev_failed)
            tango.Except.re_throw_exception(
                dev_failed,
                const.STR_ASSIGN_RES_EXEC,
                log_msg,
                "MccsMasterLeafNode.AssignResources",
                tango.ErrSeverity.ERR,
            )
