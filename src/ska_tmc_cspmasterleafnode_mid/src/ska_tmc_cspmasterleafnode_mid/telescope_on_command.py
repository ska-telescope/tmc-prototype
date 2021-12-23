# Tango import
import tango

# Additional import
from ska.base.commands import BaseCommand
from tango import DevFailed, DevState
from tmc.common.tango_client import TangoClient
from tmc.common.tango_server_helper import TangoServerHelper

from . import const
from .attribute_callbacks import (
    CbfHealthStateAttributeUpdator,
    PssHealthStateAttributeUpdator,
    PstHealthStateAttributeUpdator,
)


class TelescopeOn(BaseCommand):
    """
    A class for CspMasterLeafNode's TelescopeOn() command. On command is inherited from BaseCommand.

    It Sets the State to On.
    """

    def check_allowed(self):
        """
        Checks whether this command is allowed to be run in current device state

        :return: True if this command is allowed to be run in current device state

        :rtype: boolean

        :raises: DevFailed if this command is not allowed to be run in current device state

        """
        if self.state_model.op_state in [DevState.FAULT, DevState.UNKNOWN]:
            tango.Except.throw_exception(
                f"Command TelescopeOn is not allowed in current state {self.state_model.op_state}.",
                "Failed to invoke On command on CspMasterLeafNode.",
                "CspMasterLeafNode.TelescopeOn()",
                tango.ErrSeverity.ERR,
            )

        return True

    def telescope_on_cmd_ended_cb(self, event):
        """
        Callback function immediately executed when the asynchronous invoked
        command returns. Checks whether the Telescope On command has been successfully invoked on CSPMaster.

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
        this_device = TangoServerHelper.get_instance()
        if event.err:
            log_msg = (
                f"{const.ERR_INVOKING_CMD}{event.cmd_name}\n{event.errors}"
            )
            self.logger.error(log_msg)
            this_device.write_attr("activityMessage", log_msg, False)
        else:
            log_msg = f"{const.STR_COMMAND}{event.cmd_name}{const.STR_INVOKE_SUCCESS}"
            self.logger.info(log_msg)
            this_device.write_attr("activityMessage", log_msg, False)

    def do(self):
        """
        Method to invoke On command on CSP Element.

        param argin:
            None

        raises:
            DevFailed on communication failure with CspMaster or CspMaster is in error state.

        """
        device_data = self.target
        this_device = TangoServerHelper.get_instance()
        try:
            csp_mln_client_obj = TangoClient(
                this_device.read_property("CspMasterFQDN")[0]
            )
            csp_mln_client_obj.send_command_async(
                const.CMD_ON, [], self.telescope_on_cmd_ended_cb
            )
            self.logger.debug(const.STR_ON_CMD_ISSUED)
            this_device.write_attr(
                "activityMessage", const.STR_ON_CMD_ISSUED, False
            )
            device_data.cbf_health_updator = CbfHealthStateAttributeUpdator()
            device_data.cbf_health_updator.start()
            device_data.pss_health_updator = PssHealthStateAttributeUpdator()
            device_data.pss_health_updator.start()
            device_data.pst_health_updator = PstHealthStateAttributeUpdator()
            device_data.pst_health_updator.start()

        except DevFailed as dev_failed:
            log_msg = f"{const.ERR_EXE_ON_CMD}{dev_failed}"
            self.logger.exception(dev_failed)
            this_device.write_attr(
                "activityMessage", const.ERR_EXE_ON_CMD, False
            )
            tango.Except.re_throw_exception(
                dev_failed,
                const.STR_ON_EXEC,
                log_msg,
                "CspMasterLeafNode.TelescopeOnCommand",
                tango.ErrSeverity.ERR,
            )
