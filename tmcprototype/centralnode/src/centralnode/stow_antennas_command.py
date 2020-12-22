"""
StowAntennas class for CentralNode.
"""
# PROTECTED REGION ID(CentralNode.additionnal_import) ENABLED START #
# Standard Python imports
import tango
from tango import DevState, DevFailed
# Additional import
from ska.base.commands import ResultCode, BaseCommand
from . import const
from centralnode.device_data import DeviceData
from centralnode.tango_client import TangoClient
# PROTECTED REGION END #    //  CentralNode.additional_import


class StowAntennas(BaseCommand):
    """
    A class for CentralNode's StowAntennas() command.
    """

    def check_allowed(self):

        """
        Checks whether this command is allowed to be run in current device state

        :return: True if this command is allowed to be run in current device state

        :rtype: boolean

        :raises: DevFailed if this command is not allowed to be run in current device state

        """
        if self.state_model.op_state in [DevState.FAULT, DevState.UNKNOWN, DevState.DISABLE]:
            tango.Except.throw_exception("Command StowAntennas is not allowed in current state.",
                                         "Failed to invoke StowAntennas command on CentralNode.",
                                         "CentralNode.StowAntennas()",
                                         tango.ErrSeverity.ERR)
        return True

    def do(self, argin):
        """
        Invokes the command SetStowMode on the specified receptors.

        :param argin: List of Receptors to be stowed.

        :return: None

        :raises: DevFailed if error occurs while invoking command of DishLeafNode
                ValueError if error occurs if input argument json string contains invalid value
        """
        device_data = self.target
        self.logger.info(type(self.target))
        try:
            for leafId in range(0, len(argin)):
                input_type_check = float(argin[leafId])

            log_msg = const.STR_STOW_CMD_ISSUED_CN
            self.logger.info(log_msg)
            device_data._read_activity_message = log_msg
            for i in range(0, len(argin)):
                device_name = device_data.dln_prefix + argin[i]
                try:
                    device_proxy = TangoClient(device_name)
                    device_proxy.send_command(const.CMD_SET_STOW_MODE)

                except DevFailed as dev_failed:
                    log_msg = const.ERR_EXE_STOW_CMD + str(dev_failed)
                    self.logger.exception(dev_failed)
                    device_data._read_activity_message = const.ERR_EXE_STOW_CMD
                    tango.Except.throw_exception(const.STR_CMD_FAILED, log_msg,
                                                 "CentralNode.StowAntennasCommand",
                                                 tango.ErrSeverity.ERR)

        except ValueError as value_error:
            log_msg = const.ERR_STOW_ARGIN + str(value_error)
            self.logger.exception(value_error)
            device_data._read_activity_message = const.ERR_STOW_ARGIN
            tango.Except.throw_exception(const.STR_CMD_FAILED, log_msg,
                                         "CentralNode.StowAntennasCommand",
                                         tango.ErrSeverity.ERR)

        except DevFailed as dev_failed:
            log_msg = const.ERR_EXE_STOW_CMD + str(dev_failed)
            self.logger.exception(dev_failed)
            device_data._read_activity_message = const.ERR_EXE_STOW_CMD
            tango.Except.throw_exception(const.STR_CMD_FAILED, log_msg,
                                         "CentralNode.StowAntennasCommand",
                                         tango.ErrSeverity.ERR)


