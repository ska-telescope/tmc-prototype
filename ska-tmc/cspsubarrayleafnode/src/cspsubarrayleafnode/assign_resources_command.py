import json

# PyTango imports
import tango
from tango import DevState, DevFailed

# Additional import
from ska.base.commands import BaseCommand

from tmc.common.tango_client import TangoClient
from tmc.common.tango_server_helper import TangoServerHelper

from . import const
from .transaction_id import identify_with_id
from .delay_model import DelayManager


class AssignResourcesCommand(BaseCommand):
    """
    A class for CspSubarrayLeafNode's AssignResources() command.

    It accepts subarrayID and receptor ids in JSON string format and invokes AssignResources command on CSP Subarray.

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
                "Failed to invoke AssignResources command on " "cspsubarrayleafnode.",
                "cspsubarrayleafnode.AssignResources()",
                tango.ErrSeverity.ERR,
            )

        return True

    def assign_resources_ended(self, event):
        """
        Callback function immediately executed when the asynchronous invoked
        command returns.

        :param: CmdDoneEvent object
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
        self.logger.info("Executing callback assign_resources_ended_cb")
        this_server = TangoServerHelper.get_instance()
        try:
            if event.err:
                this_server.write_attr("activityMessage", f"{const.ERR_INVOKING_CMD}{event.cmd_name}\n{event.errors}", False)
                log = const.ERR_INVOKING_CMD + event.cmd_name
                self.logger.error(log)
            else:
                log = const.STR_COMMAND + event.cmd_name + const.STR_INVOKE_SUCCESS
                this_server.write_attr("activityMessage", log, False)
                self.logger.info(log)

        except tango.DevFailed as df:
            self.logger.exception(df)
            tango.Except.re_throw_exception(
                df,
                "CSP subarray gave an error response",
                "CSP subarray threw error in AddReceptors CSP LMC_CommandFailed",
                "AddReceptors",
                tango.ErrSeverity.ERR,
            )

    @identify_with_id("assign", "argin")
    def do(self, argin):
        """
        Method to invoke AssignResources command on CSP Subarray.

        :param argin:DevString. The string in JSON format. The JSON contains following values:
            subarrayID: integer

            dish:
                Mandatory JSON object consisting of

                receptorIDList:
                    DevVarString
                    The individual string should contain dish numbers in string format
                    with preceding zeroes upto 3 digits. E.g. 0001, 0002.

        Example:
            {
                    "subarrayID":1,
                    "dish": {
                    "receptorIDList": [
                        "0001",
                        "0002"
                    ]
                    }
            }


        Note: Enter the json string without spaces as an input.

        return:
            None

        raises:
            ValueError if input argument json string contains invalid value

            KeyError if input argument json string contains invalid key

            DevFailed if the command execution is not successful
        """
        device_data = self.target
        try:
            json_argument = json.loads(argin)
            device_data.receptorIDList_str = json_argument[const.STR_DISH][const.STR_RECEPTORID_LIST]
            delay_manager_obj = DelayManager.get_instance()
            delay_manager_obj.update_config_params()
            # Invoke AssignResources command on CspSubarray
            self.logger.info("Invoking AssignResources on CSP subarray")
            this_server = TangoServerHelper.get_instance()
            csp_subarray_fqdn = ""
            property_val = this_server.read_property("CspSubarrayFQDN")
            csp_subarray_fqdn = csp_subarray_fqdn.join(property_val)
            csp_sub_client_obj = TangoClient(csp_subarray_fqdn)
            csp_sub_client_obj.send_command_async(
                const.CMD_ASSIGN_RESOURCES, argin, self.assign_resources_ended
            )
            self.logger.info("After invoking AssignResources on CSP subarray")
            this_server.write_attr("activityMessage", const.STR_ASSIGN_RESOURCES_SUCCESS, False)
            self.logger.info(const.STR_ASSIGN_RESOURCES_SUCCESS)

        except DevFailed as dev_failed:
            log_msg = f"{const.ERR_ASSGN_RESOURCES}{dev_failed}"
            this_server.write_attr("activityMessage", log_msg, False)
            self.logger.exception(dev_failed)
            tango.Except.throw_exception(
                const.STR_ASSIGN_RES_EXEC,
                log_msg,
                "CspSubarrayLeafNode.AssignResourcesCommand",
                tango.ErrSeverity.ERR,
            )
