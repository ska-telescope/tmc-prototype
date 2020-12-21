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
from .device_data import DeviceData
class OnCommand(SKABaseDevice.OnCommand):
    """
    A class for CspMasterLeafNode's On() command.
    """

    def on_cmd_ended_cb(self, event):
        """
        Callback function immediately executed when the asynchronous invoked
        command returns. Checks whether the On command has been successfully invoked on CSPMaster.

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
        Invokes On command on the CSP Element.

        :param argin: None

        :return: A tuple containing a return code and a string message indicating status.
            The message is for information purpose only.

        :rtype: (ResultCode, str)

        :raises: DevFailed on communication failure with CspMaster or CspMaster is in error state.

        """
        device_data = self.target
        try:
            # Pass argin to csp master .
            # If the array length is 0, the command applies to the whole CSP Element.
            # If the array length is > 1 each array element specifies the FQDN of the CSP SubElement to switch ON.
            # device._csp_proxy.command_inout_asynch(const.CMD_ON, [], self.on_cmd_ended_cb)
            # device_data = DeviceData.get_instance()
            csp_mln_client_obj = TangoClient(device_data.csp_master_ln_fqdn)
            csp_mln_client_obj.send_command_async(const.CMD_ON, self.on_cmd_ended_cb, [])
            self.logger.debug(const.STR_ON_CMD_ISSUED)
            return (ResultCode.OK, const.STR_ON_CMD_ISSUED)

        except DevFailed as dev_failed:
            log_msg = const.ERR_EXE_ON_CMD + str(dev_failed)
            self.logger.exception(dev_failed)
            device_data._read_activity_message = const.ERR_EXE_ON_CMD
            tango.Except.re_throw_exception(dev_failed, const.STR_ON_EXEC, log_msg,
                                            "CspMasterLeafNode.OnCommand",
                                            tango.ErrSeverity.ERR)