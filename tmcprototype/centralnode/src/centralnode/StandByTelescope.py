"""
StandByTelescope class for CentralNode.
"""
# PROTECTED REGION ID(CentralNode.additionnal_import) ENABLED START #
# Standard Python imports
import json
import ast

# Tango imports
import tango
from tango import DebugIt, AttrWriteType, DeviceProxy, EventType, DevState, DevFailed
from tango.server import run, attribute, command, device_property

# Additional import
from ska.base import SKABaseDevice
from ska.base.commands import ResultCode, BaseCommand
from ska.base.control_model import HealthState, ObsState
from . import const, release
# from centralnode.input_validator import AssignResourceValidator
# from centralnode.exceptions import ResourceReassignmentError, ResourceNotPresentError
# from centralnode.exceptions import SubarrayNotPresentError, InvalidJSONError
from centralnode.DeviceData import DeviceData
from centralnode.tango_client import TangoClient
# PROTECTED REGION END #    //  CentralNode.additional_import

class StandByTelescope(SKABaseDevice.OffCommand):
    """
    A class for CentralNode's StandByTelescope() command.
    """

    def check_allowed(self):

        """
        Checks whether this command is allowed to be run in current device state

        :return: True if this command is allowed to be run in current device state

        :rtype: boolean

        :raises: DevFailed if this command is not allowed to be run in current device state
        """
        if self.state_model.op_state in [DevState.FAULT, DevState.UNKNOWN, DevState.DISABLE]:
            tango.Except.throw_exception("Command StandByTelescope is not allowed in current state.",
                                         "Failed to invoke StandByTelescope command on CentralNode.",
                                         "CentralNode.StandByTelescope()",
                                         tango.ErrSeverity.ERR)
        return True

    def do(self):
        """
        Sets the CentralNode into OFF state. Invokes the respective command on lower level nodes adn devices.

        :return: A tuple containing a return code and a string message indicating status.
        The message is for information purpose only.

        :rtype: (ResultCode, str)

        :raises: DevFailed if error occurs while invoking command on any of the devices like SubarrayNode,
                DishLeafNode, CSPMasterLeafNode or SDpMasterLeafNode

        """
        self.logger.info(type(self.target))
        device_data = DeviceData.get_instance()
        log_msg = const.STR_STANDBY_CMD_ISSUED
        self.logger.info(log_msg)
        device_data._read_activity_message = log_msg

        for name in range(0, len(device_data._dish_leaf_node_devices)):
            try:
                dish_ln_client = TangoClient(device_data._dish_leaf_node_devices[name])
                dish_ln_client.send_command(const.CMD_SET_STANDBY_MODE)
                log_msg = const.CMD_SET_STANDBY_MODE + "invoked on" + str(dish_local_proxy)
                self.logger.info(log_msg)
                dish_ln_client.send_command(const.CMD_OFF)
            except DevFailed as dev_failed:
                log_msg = const.ERR_EXE_STANDBY_CMD + str(dev_failed)
                self.logger.exception(dev_failed)
                device_data._read_activity_message = const.ERR_EXE_STANDBY_CMD
                tango.Except.throw_exception(const.STR_STANDBY_EXEC, log_msg,
                                             "CentralNode.StandByTelescopeCommand",
                                             tango.ErrSeverity.ERR)

        try:
            csp_mln_client = TangoClient(device_data.csp_master_ln_fqdn)
            csp_mln_client.send_command(const.CMD_OFF)
            csp_mln_client.send_command(const.CMD_STANDBY, [])
            self.logger.info(const.STR_CMD_STANDBY_CSP_DEV)
        except DevFailed as dev_failed:
            log_msg = const.ERR_EXE_STANDBY_CMD + str(dev_failed)
            self.logger.exception(dev_failed)
            device_data._read_activity_message = const.ERR_EXE_STANDBY_CMD
            tango.Except.throw_exception(const.STR_STANDBY_EXEC, log_msg,
                                         "CentralNode.StandByTelescopeCommand",
                                         tango.ErrSeverity.ERR)

        try:
            sdp_mln_client = TangoClient(device_data.sdp_master_ln_fqdn)
            sdp_mln_client.send_command(const.CMD_OFF)
            sdp_mln_client.send_command(const.CMD_STANDBY)
            self.logger.info(const.STR_CMD_STANDBY_SDP_DEV)
        except DevFailed as dev_failed:
            log_msg = const.ERR_EXE_STANDBY_CMD + str(dev_failed)
            self.logger.exception(dev_failed)
            device_data._read_activity_message = const.ERR_EXE_STANDBY_CMD
            tango.Except.throw_exception(const.STR_STANDBY_EXEC, log_msg,
                                         "CentralNode.StandByTelescopeCommand",
                                         tango.ErrSeverity.ERR)
        try:
            for subarrayID in range(1, len(device_data.tm_mid_subarray) + 1):
                subarray_client = TangoClient(subarrayID)
                subarray_client.send_command(const.CMD_OFF)
                self.logger.info(const.STR_CMD_STANDBY_SA_DEV)

        except DevFailed as dev_failed:
            log_msg = const.ERR_EXE_STANDBY_CMD + str(dev_failed)
            self.logger.exception(dev_failed)
            device_data._read_activity_message = const.ERR_EXE_STANDBY_CMD
            tango.Except.throw_exception(const.STR_STANDBY_EXEC, log_msg,
                                         "CentralNode.StandByTelescopeCommand",
                                         tango.ErrSeverity.ERR)
        return (ResultCode.OK, device_data._read_activity_message)


    def is_StandByTelescope_allowed(self):
        """
        Checks whether this command is allowed to be run in current device state.

        :return: True if this command is allowed to be run in current device state.

        :rtype: boolean

        :raises: DevFailed if this command is not allowed to be run in current device state.

        """
        handler = self.get_command_object("StandByTelescope")
        return handler.check_allowed()


    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="[ResultCode, information-only string]",
    )
    def StandByTelescope(self):
        """
        This command invokes SetStandbyLPMode() command on DishLeafNode, StandBy() command on CspMasterLeafNode and
        SdpMasterLeafNode and Off() command on SubarrayNode and sets CentralNode into OFF state.

        """
        handler = self.get_command_object("StandByTelescope")
        (result_code, message) = handler()
        return [[result_code], [message]]
