# PROTECTED REGION ID(MccSubarrayLeafNode.additional_import) ENABLED START #
# Standard python imports

# Third party imports
import tango
from tango import DevState, DevFailed

# Additional import
from ska.base.commands import BaseCommand

from tmc.common.tango_client import TangoClient
from tmc.common.tango_server_helper import TangoServerHelper

from . import const

# PROTECTED REGION END #    //  MccsSubarrayLeafNode.additional_import


class Scan(BaseCommand):
    """
    A class for MccsSubarrayLeafNode's Scan() command.

    This command invokes Scan command on Mccs Subarray. It is allowed only when MccsSubarray is in
    ObsState READY.
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
                f"Scan() is not allowed in current state {self.state_model.op_state}",
                "Failed to invoke Scan command on mccssubarrayleafnode.",
                "mccssubarrayleafnode.Scan()",
                tango.ErrSeverity.ERR,
            )

        return True

    def scan_cmd_ended_cb(self, event):
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
        this_server = TangoServerHelper.get_instance()
        if event.err:
            log_msg = f"{const.ERR_INVOKING_CMD}{event.cmd_name}\n{event.errors}"
            self.logger.error(log_msg)
            this_server.write_attr("activityMessage", log_msg, False)
        else:
            log_msg = f"{const.STR_COMMAND}{event.cmd_name}{const.STR_INVOKE_SUCCESS}"
            self.logger.info(log_msg)
            this_server.write_attr("activityMessage", log_msg, False)


    def do(self, argin):
        """
        Method to invoke Scan command on MCCS Subarray.

        :param argin: JSON string consists of scan id (int) and scan_time.

        Example:
        {"interface":"https://schema.skatelescope.org/ska-low-mccs-scan/1.0","scan_id":1,"start_time":0.0}


        Note: Enter the json string without spaces as a input.

        return:
            None

        raises:
            DevFailed if the command execution is not successful
        """
        this_server = TangoServerHelper.get_instance()
        try:
            mccs_subarray_fqdn = ""
            property_value = this_server.read_property("MccsSubarrayFQDN")
            mccs_subarray_fqdn = mccs_subarray_fqdn.join(property_value)
            mccs_subarray_client = TangoClient(mccs_subarray_fqdn)
            # TODO: Mock obs_state issue to be resolved
            # assert mccs_subarray_client.get_attribute("obsState") == ObsState.READY
            mccs_subarray_client.send_command_async(
                const.CMD_SCAN, argin, self.scan_cmd_ended_cb
            )
            this_server.write_attr("activityMessage", const.STR_SCAN_SUCCESS, False)
            self.logger.info(const.STR_SCAN_SUCCESS)

        # TODO: Mock obs_state issue to be resolved
        # except AssertionError as assertion_error:
        #     log_msg = f"{const.ERR_DEVICE_NOT_READY}{assertion_error}"
        #     device_data._read_activity_message = log_msg
        #     self.logger.exception(log_msg)
        #     tango.Except.throw_exception(const.STR_SCAN_EXEC, log_msg,
        #                                  "MccsSubarrayLeafNode.Scan",
        #                                  tango.ErrSeverity.ERR)

        except DevFailed as dev_failed:
            log_msg = f"{const.ERR_SCAN_RESOURCES}{dev_failed}"
            this_server.write_attr("activityMessage", log_msg, False)
            self.logger.exception(dev_failed)
            tango.Except.throw_exception(
                const.STR_SCAN_EXEC,
                log_msg,
                "MccsSubarrayLeafNode.Scan",
                tango.ErrSeverity.ERR,
            )
