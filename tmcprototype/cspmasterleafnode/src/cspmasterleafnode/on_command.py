# Tango import
import tango
from tango import DevFailed

# Additional import
from ska.base import SKABaseDevice
from ska.base.commands import ResultCode

from tmc.common.tango_client import TangoClient
from tmc.common.tango_server_helper import TangoServerHelper

from . import const
from .attribute_callbacks import (
    CbfHealthStateAttributeUpdator,
    PssHealthStateAttributeUpdator,
    PstHealthStateAttributeUpdator,
)


class On(SKABaseDevice.OnCommand):
    """
    A class for CspMasterLeafNode's On() command. On command is inherited from SKABaseDevice.

    It Sets the State to On.
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
        this_device = TangoServerHelper.get_instance()
        if event.err:
            log_msg = f"{const.ERR_INVOKING_CMD}{event.cmd_name}\n{event.errors}"
            self.logger.error(log_msg)
            this_device.write_attr("activityMessage", log_msg)
        else:
            log_msg = f"{const.STR_COMMAND}{event.cmd_name}{const.STR_INVOKE_SUCCESS}"
            self.logger.info(log_msg)
            this_device.write_attr("activityMessage", log_msg)

    def do(self):
        """
        Method to invoke On command on CSP Element.

        param argin:
            None

        return:
            A tuple containing a return code and a string message indicating status.
            The message is for information purpose only.

        rtype:
            (ResultCode, str)

        raises:
            DevFailed on communication failure with CspMaster or CspMaster is in error state.

        """
        device_data = self.target
        this_device = TangoServerHelper.get_instance()
        try:
            csp_mln_client_obj = TangoClient(self.this_server.read_property("CspMasterFQDN")[0])
            csp_mln_client_obj.send_command_async(
                const.CMD_ON, [], self.on_cmd_ended_cb
            )
            self.logger.debug(const.STR_ON_CMD_ISSUED)
            this_device.write_attr("activityMessage", const.STR_ON_CMD_ISSUED)
            device_data.cbf_health_updator = CbfHealthStateAttributeUpdator()
            device_data.cbf_health_updator.start()
            device_data.pss_health_updator = PssHealthStateAttributeUpdator()
            device_data.pss_health_updator.start()
            device_data.pst_health_updator = PstHealthStateAttributeUpdator()
            device_data.pst_health_updator.start()
            return (ResultCode.OK, const.STR_ON_CMD_ISSUED)

        except DevFailed as dev_failed:
            log_msg = f"{const.ERR_EXE_ON_CMD}{dev_failed}"
            self.logger.exception(dev_failed)
            this_device.write_attr("activityMessage", const.ERR_EXE_ON_CMD)
            tango.Except.re_throw_exception(
                dev_failed,
                const.STR_ON_EXEC,
                log_msg,
                "CspMasterLeafNode.OnCommand",
                tango.ErrSeverity.ERR,
            )
