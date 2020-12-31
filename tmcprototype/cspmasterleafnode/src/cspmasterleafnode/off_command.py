from ska.base import SKABaseDevice
from ska.base.commands import ResultCode
from . import const
from tmc.common.tango_client import TangoClient
from .attribute_callbacks import CbfHealthStateAttributeUpdator, PssHealthStateAttributeUpdator, \
                                                                            PstHealthStateAttributeUpdator

class OffCommand(SKABaseDevice.OffCommand):
    """
    A class for CspMasterLeafNode's Off() command.
    """

    def off_cmd_ended_cb(self, event):
        """
        Callback function immediately executed when the asynchronous invoked
        command returns. Checks whether the Off command has been successfully invoked on CSPMaster.

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
        Invokes Off command on the CSP Element.

        :param argin: None.

        :return: A tuple containing a return code and a string message indicating status.
            The message is for information purpose only.

        :rtype: (ResultCode, str)

        """
        device_data = self.target
        # pass argin to csp master.
        # If the array length is 0, the command applies to the whole CSP Element.
        # If the array length is >, each array element specifies the FQDN of the CSP SubElement to switch OFF.
        csp_mln_client_obj = TangoClient(device_data.csp_master_ln_fqdn)
        csp_mln_client_obj.send_command_async(const.CMD_OFF,[], self.off_cmd_ended_cb)
        self.logger.debug(const.STR_ON_CMD_ISSUED)
        device_data.cbf_health_updator = CbfHealthStateAttributeUpdator()
        device_data.cbf_health_updator.stop()
        device_data.pss_health_updator = PssHealthStateAttributeUpdator()
        device_data.pss_health_updator.stop()
        device_data.pst_health_updator = PstHealthStateAttributeUpdator()
        device_data.pst_health_updator.stop()

        return (ResultCode.OK, const.STR_OFF_CMD_ISSUED)
