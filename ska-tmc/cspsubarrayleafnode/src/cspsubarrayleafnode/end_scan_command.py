# PyTango imports
import tango
from tango import DevState, DevFailed

# Additional import
from ska.base.commands import BaseCommand

from tmc.common.tango_client import TangoClient
from tmc.common.tango_server_helper import TangoServerHelper

from . import const


class EndScanCommand(BaseCommand):
    """
    A class for CspSubarrayLeafNode's EndScan() command. EndScan command is inherited from BaseCommand.

    It invokes EndScan command on CSP Subarray. This command is allowed when CSP Subarray is in
    obsState SCANNING.

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
                "Failed to invoke EndScan command on cspsubarrayleafnode.",
                "cspsubarrayleafnode.EndScan()",
                tango.ErrSeverity.ERR,
            )

        # if device._csp_subarray_proxy.obsState != ObsState.SCANNING:
        #     tango.Except.throw_exception(const.ERR_DEVICE_NOT_IN_SCAN, "Failed to invoke EndScan command on cspsubarrayleafnode.",
        #                                     "CspSubarrayLeafNode.EndScanCommand",
        #                                     tango.ErrSeverity.ERR)

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
        Method to invoke Endscan command on CSP Subarray.

        return:
            None

        raises:
            DevFailed if the command execution is not successful

        """
        try:
            this_server = TangoServerHelper.get_instance()
            csp_subarray_fqdn = ""
            property_val = this_server.read_property("CspSubarrayFQDN")
            csp_subarray_fqdn = csp_subarray_fqdn.join(property_val)
            csp_sub_client_obj = TangoClient(csp_subarray_fqdn)
            csp_sub_client_obj.send_command_async(
                const.CMD_ENDSCAN, None, self.endscan_cmd_ended_cb
            )
            this_server.write_attr("activityMessage", const.STR_ENDSCAN_SUCCESS, False)
            self.logger.info(const.STR_ENDSCAN_SUCCESS)

        except DevFailed as dev_failed:
            log_msg = f"{const.ERR_ENDSCAN_INVOKING_CMD}{dev_failed}"
            this_server.write_attr("activityMessage", log_msg, False)
            self.logger.exception(dev_failed)
            tango.Except.throw_exception(
                const.STR_ENDSCAN_EXEC,
                log_msg,
                "CspSubarrayLeafNode.EndScanCommand",
                tango.ErrSeverity.ERR,
            )
