# PyTango imports
import tango
from tango import DeviceProxy, EventType, ApiUtil, DebugIt, DevState, AttrWriteType, DevFailed
from tango.server import run, command, device_property, attribute

# Additional import
from ska.base import SKABaseDevice
from ska.base.commands import ResultCode, BaseCommand
from ska.base.control_model import HealthState, SimulationMode, TestMode
from . import const, release, tango_client, device_data
from .tango_client import TangoClient

class StandbyCommand(BaseCommand):
    """
    A class for CspMasterLeafNode's Standby() command.
    """

    def check_allowed(self):
        """
        Checks whether this command is allowed to be run in current device state.

        :return: True if this command is allowed to be run in current device state.

        :rtype: boolean

        :raises: DevFailed if this command is not allowed to be run in current device state.

        """
        if self.state_model.op_state in [DevState.FAULT, DevState.UNKNOWN]:
            tango.Except.throw_exception("Command Standby is not allowed in current state.",
                                            "Failed to invoke Standby command on CspMasterLeafNode.",
                                            "CspMasterLeafNode.Standby()",
                                            tango.ErrSeverity.ERR)

        return True

    def standby_cmd_ended_cb(self, event):
        """
        Callback function immediately executed when the asynchronous invoked
        command returns. Checks whether the StandBy command has been successfully invoked on CSPMaster.

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

    def do(self, argin):
        """
        It invokes the STANDBY command on CSP Master.

        :param argin: DevStringArray.

        If the array length is 0, the command applies to the whole CSP Element. If the array length is > 1
        , each array element specifies the FQDN of the CSP SubElement to put in STANDBY mode.


        :return: None

        :raises: DevFailed on communication failure with CspMaster or CspMaster is in error state.

        """
        device_data = self.target

        try:
            csp_mln_client_obj = TangoClient(device_data.csp_master_ln_fqdn)
            csp_mln_client_obj.send_command_async(const.CMD_STANDBY, self.standby_cmd_ended_cb, argin)
            self.logger.debug(const.STR_STANDBY_CMD_ISSUED)

        except DevFailed as dev_failed:
            log_msg = const.ERR_EXE_STANDBY_CMD + str(dev_failed)
            self.logger.exception(dev_failed)
            device_data._read_activity_message = const.ERR_EXE_STANDBY_CMD
            tango.Except.re_throw_exception(dev_failed, const.STR_STANDBY_EXEC, log_msg,
                                            "CspMasterLeafNode.StandbyCommand",
                                            tango.ErrSeverity.ERR)
