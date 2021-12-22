# PROTECTED REGION ID(MccSubarrayLeafNode.additional_import) ENABLED START #
# Standard python imports

# Third party imports
import tango
from tango import DevState, DevFailed

# Additional import
from ska.base.commands import BaseCommand
from ska.base.control_model import ObsState

from tmc.common.tango_client import TangoClient
from tmc.common.tango_server_helper import TangoServerHelper
from .device_data import DeviceData

from . import const

# PROTECTED REGION END #    //  MccsSubarrayLeafNode.additional_import


class EndScan(BaseCommand):
    """
    A class for MccsSubarrayLeafNode's EndScan() command.

    This command invokes EndScan command on MCCS Subarray. It is allowed only when MccsSubarray is in
    ObsState SCANNING.

    """

    def check_allowed(self):
        """
        Checks whether the command is allowed to be run in the current state

        :return: True if this command is allowed to be run in
            current device state

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
                f"EndScan() is not allowed in current state {self.state_model.op_state}",
                "Failed to invoke EndScan command on mccssubarrayleafnode.",
                "mccssubarrayleafnode.EndScan()",
                tango.ErrSeverity.ERR,
            )
        return True

    def endscan_cmd_ended_cb(self, event):
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
        this_server = TangoServerHelper.get_instance()
        # Update logs and activity message attribute with received event
        if event.err:
            log_msg = f"{const.ERR_INVOKING_CMD}{event.cmd_name}\n{event.errors}"
            self.logger.error(log_msg)
            this_server.write_attr("activityMessage", log_msg, False)
        else:
            log_msg = f"{const.STR_COMMAND}{event.cmd_name}{const.STR_INVOKE_SUCCESS}"
            self.logger.info(log_msg)
            this_server.write_attr("activityMessage", log_msg, False)

    def do(self):
        """
        Method to invoke EndScan command on MCCS Subarray.

        raises:
            DevFailed if the command execution is not successful.

            AssertionError if MccsSubarray is not in SCANNING obsState.

        """
        this_server = TangoServerHelper.get_instance()
        device_data = DeviceData.get_instance()
        try:
            mccs_subarray_fqdn = ""
            property_value = this_server.read_property("MccsSubarrayFQDN")[0]
            mccs_subarray_fqdn = mccs_subarray_fqdn.join(property_value)
            mccs_subarray_client = TangoClient(mccs_subarray_fqdn)
            assert mccs_subarray_client.get_attribute("obsState").value == ObsState.SCANNING
            mccs_subarray_client.send_command_async(
                const.CMD_ENDSCAN, None, self.endscan_cmd_ended_cb
            )
            this_server.write_attr("activityMessage", const.STR_ENDSCAN_SUCCESS, False)
            self.logger.info(const.STR_ENDSCAN_SUCCESS)

        except AssertionError:
            device_data._read_activity_message = const.ERR_DEVICE_NOT_SCANNING
            self.logger.error(const.ERR_DEVICE_NOT_SCANNING)
            tango.Except.throw_exception(const.STR_END_SCAN_EXEC, const.ERR_DEVICE_NOT_SCANNING,
                                         "MCCSSubarrayLeafNode.EndScan",
                                         tango.ErrSeverity.ERR)

        except DevFailed as dev_failed:
            log_msg = f"{const.ERR_ENDSCAN_COMMAND}{dev_failed}"
            this_server.write_attr("activityMessage", log_msg, False)
            self.logger.exception(dev_failed)
            tango.Except.throw_exception(
                const.STR_END_SCAN_EXEC,
                log_msg,
                "MccsSubarrayLeafNode.EndScan",
                tango.ErrSeverity.ERR,
            )
