import datetime
import importlib.resources
import threading
from datetime import datetime, timedelta
import pytz
import numpy as np
import json

# Third Party imports
# PyTango imports
import tango
from tango import DebugIt, AttrWriteType, DeviceProxy, DevState, DevFailed
from tango.server import run, attribute, command, device_property
import katpoint

# Additional import
from ska.base.commands import ResultCode, BaseCommand
from ska.base import SKABaseDevice
from ska.base.control_model import HealthState, ObsState
from .transaction_id import identify_with_id
from . import const, release
from .exceptions import InvalidObsStateError

class AssignResourcesCommand(BaseCommand):
        """
        A class for CspSubarrayLeafNode's AssignResources() command.
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
                                             "cspsubarrayleafnode.",
                                             "cspsubarrayleafnode.AssignResources()",
                                             tango.ErrSeverity.ERR)

            return True

        def add_receptors_ended(self, event):
            """
            Callback function immediately executed when the asynchronous invoked
            command returns.

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
            device = self.target
            self.logger.info("Executing callback add_receptors_ended")
            try:
                if event.err:
                    device._read_activity_message = const.ERR_INVOKING_CMD + str(event.cmd_name) + "\n" + str(
                        event.errors)
                    log = const.ERR_INVOKING_CMD + event.cmd_name
                    self.logger.error(log)
                else:
                    log = const.STR_COMMAND + event.cmd_name + const.STR_INVOKE_SUCCESS
                    device._read_activity_message = log
                    self.logger.info(log)

            except tango.DevFailed as df:
                self.logger.exception(df)
                tango.Except.re_throw_exception(df, "CSP subarray gave an error response",
                                                "CSP subarray threw error in AddReceptors CSP LMC_CommandFailed",
                                                "AddReceptors", tango.ErrSeverity.ERR)

        @identify_with_id('assign','argin') 
        def do(self, argin):
            """
            It accepts receptor id list in JSON string format and invokes AddReceptors command on CspSubarray
            with receptorIDList (list of integers) as an input argument.

            :param argin:DevString. The string in JSON format. The JSON contains following values:

                dish:
                    Mandatory JSON object consisting of

                    receptorIDList:
                        DevVarString
                        The individual string should contain dish numbers in string format
                        with preceding zeroes upto 3 digits. E.g. 0001, 0002.
            Example:
            {
              "dish": {
                "receptorIDList": [
                  "0001",
                  "0002"
                ]
              }
            }

            Note: Enter the json string without spaces as an input.

            :return: None

            :raises: ValueError if input argument json string contains invalid value
                     KeyError if input argument json string contains invalid key
                     DevFailed if the command execution is not successful
            """
            device = self.target
            receptorIDList = []
            try:
                # Parse receptorIDList from JSON string.
                json_argument = json.loads(argin)
                device.receptorIDList_str = json_argument[const.STR_DISH][const.STR_RECEPTORID_LIST]
                # convert receptorIDList from list of string to list of int
                for receptor in device.receptorIDList_str:
                    receptorIDList.append(int(receptor))
                self.logger.info("receptorIDList: %s", str(receptorIDList))
                device.update_config_params()
                # Invoke AddReceptors command on CspSubarray
                self.logger.info("Invoking AddReceptors on CSP subarray")

                device._csp_subarray_proxy.command_inout_asynch(const.CMD_ADD_RECEPTORS, receptorIDList,
                                                           self.add_receptors_ended)

                self.logger.info("After invoking AddReceptors on CSP subarray")
                device._read_activity_message = const.STR_ADD_RECEPTORS_SUCCESS
                self.logger.info(const.STR_ADD_RECEPTORS_SUCCESS)

            except ValueError as value_error:
                log_msg = const.ERR_INVALID_JSON_ASSIGN_RES + str(value_error)
                device._read_activity_message = const.ERR_INVALID_JSON_ASSIGN_RES + str(value_error)
                self.logger.exception(value_error)
                tango.Except.throw_exception(const.ERR_INVALID_JSON_ASSIGN_RES, log_msg,
                                             "CspSubarrayLeafNode.AssignResourcesCommand",
                                             tango.ErrSeverity.ERR)

            except KeyError as key_error:
                log_msg = const.ERR_JSON_KEY_NOT_FOUND + str(key_error)
                device._read_activity_message = const.ERR_JSON_KEY_NOT_FOUND + str(key_error)
                self.logger.exception(key_error)
                tango.Except.throw_exception(const.STR_ASSIGN_RES_EXEC, log_msg,
                                             "CspSubarrayLeafNode.AssignResourcesCommand",
                                             tango.ErrSeverity.ERR)

            except DevFailed as dev_failed:
                log_msg = const.ERR_ASSGN_RESOURCES + str(dev_failed)
                device._read_activity_message = log_msg
                self.logger.exception(dev_failed)
                tango.Except.throw_exception(const.STR_ASSIGN_RES_EXEC, log_msg,
                                             "CspSubarrayLeafNode.AssignResourcesCommand",
                                             tango.ErrSeverity.ERR)
