# PROTECTED REGION ID(MccsMasterLeafNode.import) ENABLED START #
# Third party imports
# Tango imports
import tango
from tango import DevFailed

# Additional import
from ska.base import SKABaseDevice
from ska.base.commands import ResultCode 
from tmc.common.tango_client import TangoClient
from . import const
# PROTECTED REGION END #    //  MccsMasterLeafNode imports


class On(SKABaseDevice.OnCommand):
    """
    A class for MccsMasterLeafNode's On() command.
    """

    def on_cmd_ended_cb(self, event):
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
        device_data = self.target
        # Update logs and activity message attribute with received event
        if event.err:
            log_msg = const.ERR_INVOKING_CMD + str(event.cmd_name) + "\n" + str(event.errors)
            self.logger.error(log_msg)
            device_data._read_activity_message = log_msg
        else:
            log_msg = const.STR_COMMAND + str(event.cmd_name) + const.STR_INVOKE_SUCCESS
            self.logger.info(log_msg)
            device_data._read_activity_message = log_msg

    def do(self):
        """
        Invokes On command on the MCCS Element.

        :param argin: None

        :return: A tuple containing a return code and a string message indicating status.
            The message is for information purpose only.

        :rtype: (ResultCode, str)

        """
        device_data = self.target
        # Pass argin to mccs master .
        # If the array length is 0, the command applies to the whole MCCS Element.
        # If the array length is > 1 each array element specifies the FQDN of the MCCS SubElement to switch ON.
        try:
            print("************************ before object creation ***************************")
            mccs_mln_client_obj = TangoClient(device_data._mccs_master_ln_fqdn)
            mccs_mln_client_obj.send_command_async(const.CMD_ON, None, self.on_cmd_ended_cb)
            print("************************ after object creation ***************************")

            # device._mccs_master_proxy.command_inout_asynch(const.CMD_ON, self.on_cmd_ended_cb)
            self.logger.debug(const.STR_ON_CMD_ISSUED)
            return (ResultCode.OK, const.STR_ON_CMD_ISSUED)

        except DevFailed as dev_failed:
            log_msg = const.ERR_ON_RESOURCES + str(dev_failed)
            device_data._read_activity_message = log_msg
            self.logger.exception(dev_failed)
            tango.Except.throw_exception(const.STR_ON_EXEC, log_msg,
                                            "MccsMasterLeafNode.On",
                                            tango.ErrSeverity.ERR)

