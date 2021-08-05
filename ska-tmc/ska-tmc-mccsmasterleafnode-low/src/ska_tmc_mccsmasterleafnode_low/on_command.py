# PROTECTED REGION ID(MccsMasterLeafNode.import) ENABLED START #
# Tango imports
import tango
from tango import DevFailed

# Additional import
from ska.base import SKABaseDevice
from ska.base.commands import ResultCode

from tmc.common.tango_client import TangoClient
from tmc.common.tango_server_helper import TangoServerHelper

from . import const

# PROTECTED REGION END #    //  MccsMasterLeafNode imports


class On(SKABaseDevice.OnCommand):
    """
    A class for MccsMasterLeafNode's On() command. On command is inherited from SKABaseDevice.

    It Sets the State to On.

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
        # Update logs and activity message attribute with received event
        if event.err:
            log_msg = f"{const.ERR_INVOKING_CMD}{event.cmd_name}\n{event.errors}"
            self.logger.error(log_msg)
            self.this_server.write_attr("activityMessage", log_msg, False)
        else:
            log_msg = f"{const.STR_COMMAND}{event.cmd_name}{const.STR_INVOKE_SUCCESS}"
            self.logger.info(log_msg)
            self.this_server.write_attr("activityMessage", log_msg, False)

    def do(self):
        """
        Method to invoke On command on the MCCS.

        param argin:
            None

        return:
            A tuple containing a return code and a string message indicating status.
            The message is for information purpose only.

        rtype:
            (ResultCode, str)

        """
        # Pass argin to mccs master .
        # If the array length is 0, the command applies to the whole MCCS Element.
        # If the array length is > 1 each array element specifies the FQDN of the MCCS SubElement to switch ON.
        try:
            self.this_server = TangoServerHelper.get_instance()
            mccs_master_fqdn = ""
            property_value = self.this_server.read_property("MccsMasterFQDN")
            mccs_master_fqdn = mccs_master_fqdn.join(property_value)
            mccs_master_client = TangoClient(mccs_master_fqdn)
            mccs_master_client.send_command_async(
                const.CMD_ON, None, self.on_cmd_ended_cb
            )
            self.logger.debug(const.STR_ON_CMD_ISSUED)
            return (ResultCode.OK, const.STR_ON_CMD_ISSUED)

        except DevFailed as dev_failed:
            log_msg = f"{const.ERR_ON_RESOURCES}{dev_failed}"
            self.this_server.write_attr("activityMessage", log_msg, False)
            self.logger.exception(dev_failed)
            tango.Except.throw_exception(
                const.STR_ON_EXEC,
                log_msg,
                "MccsMasterLeafNode.On",
                tango.ErrSeverity.ERR,
            )