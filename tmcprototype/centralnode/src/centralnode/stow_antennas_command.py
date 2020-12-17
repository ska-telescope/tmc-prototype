class StowAntennasCommand(BaseCommand):
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
        device = self.target
        try:
            for leafId in range(0, len(argin)):
                input_type_check = float(argin[leafId])

            log_msg = const.STR_STOW_CMD_ISSUED_CN
            self.logger.info(log_msg)
            device._read_activity_message = log_msg
            for i in range(0, len(argin)):
                device_name = device.DishLeafNodePrefix + argin[i]
                try:
                    device_proxy = DeviceProxy(device_name)
                    device_proxy.command_inout(const.CMD_SET_STOW_MODE)
                except DevFailed as dev_failed:
                    log_msg = const.ERR_EXE_STOW_CMD + str(dev_failed)
                    self.logger.exception(dev_failed)
                    device._read_activity_message = const.ERR_EXE_STOW_CMD
                    tango.Except.throw_exception(const.STR_CMD_FAILED, log_msg,
                                                 "CentralNode.StowAntennasCommand",
                                                 tango.ErrSeverity.ERR)

        except ValueError as value_error:
            log_msg = const.ERR_STOW_ARGIN + str(value_error)
            self.logger.exception(value_error)
            device._read_activity_message = const.ERR_STOW_ARGIN
            tango.Except.throw_exception(const.STR_CMD_FAILED, log_msg,
                                         "CentralNode.StowAntennasCommand",
                                         tango.ErrSeverity.ERR)

        except DevFailed as dev_failed:
            log_msg = const.ERR_EXE_STOW_CMD + str(dev_failed)
            self.logger.exception(dev_failed)
            device._read_activity_message = const.ERR_EXE_STOW_CMD
            tango.Except.throw_exception(const.STR_CMD_FAILED, log_msg,
                                         "CentralNode.StowAntennasCommand",
                                         tango.ErrSeverity.ERR)

    # pylint: enable=unused-variable


def is_StowAntennas_allowed(self):
    """
    Checks whether this command is allowed to be run in current device state.

    :return: True if this command is allowed to be run in current device state.

    :rtype: boolean

    :raises: DevFailed if this command is not allowed to be run in current device state.

    """
    handler = self.get_command_object("StowAntennas")
    return handler.check_allowed()


@command(
    dtype_in=('str',),
    doc_in="List of Receptors to be stowed",
)
def StowAntennas(self, argin):
    """
    This command stows the specified receptors.
    """
    handler = self.get_command_object("StowAntennas")
    handler(argin)
