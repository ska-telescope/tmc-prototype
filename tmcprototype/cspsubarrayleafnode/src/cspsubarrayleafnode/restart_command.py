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

class RestartCommand(BaseCommand):
        """
        A class for CSPSubarrayLeafNode's Restart() command.
        """

        def check_allowed(self):
            """
            Checks whether this command is allowed to be run in current device state

            :return: True if this command is allowed to be run in current device state

            :rtype: boolean

            :raises: DevFailed if this command is not allowed to be run in current device state

            """
            device = self.target
            if self.state_model.op_state in [DevState.UNKNOWN, DevState.DISABLE]:
                tango.Except.throw_exception("Restart() is not allowed in current state",
                                             "Failed to invoke Restart command on CspSubarrayLeafNode.",
                                             "cspsubarrayleafnode.Restart()",
                                             tango.ErrSeverity.ERR)

            if device._csp_subarray_proxy.obsState not in [ObsState.FAULT, ObsState.ABORTED]:
                tango.Except.throw_exception(const.ERR_UNABLE_RESTART_CMD, const.ERR_RESTART_INVOKING_CMD,
                                             "CspSubarrayLeafNode.RestartCommand",
                                             tango.ErrSeverity.ERR)

            return True


        def restart_cmd_ended_cb(self, event):
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
            device = self.target
            # Update logs and activity message attribute with received event
            if event.err:
                log_msg = const.ERR_INVOKING_CMD + str(event.cmd_name) + "\n" + str(event.errors)
                self.logger.error(log_msg)
                device._read_activity_message = log_msg
            else:
                log_msg = const.STR_COMMAND + str(event.cmd_name) + const.STR_INVOKE_SUCCESS
                self.logger.info(log_msg)
                device._read_activity_message = log_msg

        def do(self):
            """
            This command invokes Restart command on CSPSubarray.

            :return: None

            :raises: DevFailed if error occurs while invoking the command on CSpSubarray.
            """
            device = self.target
            try:
                device._csp_subarray_proxy.command_inout_asynch(const.CMD_RESTART, self.restart_cmd_ended_cb)
                device._read_activity_message = const.STR_RESTART_SUCCESS
                self.logger.info(const.STR_RESTART_SUCCESS)

            except DevFailed as dev_failed:
                log_msg = const.ERR_RESTART_INVOKING_CMD + str(dev_failed)
                device._read_activity_message = log_msg
                self.logger.exception(dev_failed)
                tango.Except.throw_exception(const.ERR_RESTART_INVOKING_CMD, log_msg,
                                             "CspSubarrayLeafNode.RestartCommand",
                                             tango.ErrSeverity.ERR)
