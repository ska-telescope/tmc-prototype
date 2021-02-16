"""
On class for CspSubarrayLeafNode.
"""
# PROTECTED REGION ID(cspsubarrayleafnode.additionnal_import) ENABLED START #
# Standard Python imports
# Additional import
from ska.base import SKABaseDevice
from ska.base.commands import ResultCode

from tmc.common.tango_server_helper import TangoServerHelper

from . import const
from .delay_model import DelayManager


class On(SKABaseDevice.OnCommand):
    """
    A class for CSP Subarray's On() command.

    Invokes On command on the CSP Subarray.
    """

    def on_cmd_ended_cb(self, event):
        """
        Callback function executes when the command invoked asynchronously returns from the server.

        :param event: A CmdDoneEvent object. This class is used to pass data to the callback method in asynchronous
                        callback model for command execution.

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
        device_data = self.target
        if event.err:
            log = f"{const.ERR_INVOKING_CMD}{event.cmd_name}\n{event.errors}"
            device_data._read_activity_message = log
            self.logger.error(log)
        else:
            log = const.STR_COMMAND + event.cmd_name + const.STR_INVOKE_SUCCESS
            device_data._read_activity_message = log
            self.logger.info(log)

    def do(self):
        """
        Method to invoke On command on CSP Subarray.

        param argin:
            None

        return:
            A tuple containing a return code and a string message indicating status.
            The message is for information purpose only.

        rtype:
            (ResultCode, str)

        """
        # device_data = self.target
        log_msg = const.CMD_ON + const.STR_COMMAND + const.STR_INVOKE_SUCCESS
        self.logger.debug(log_msg)
        delay_manager_obj = DelayManager.get_instance()
        delay_manager_obj.start()
        this_server = TangoServerHelper.get_instance()
        this_server.set_status(log_msg)
        return (ResultCode.OK, log_msg)
