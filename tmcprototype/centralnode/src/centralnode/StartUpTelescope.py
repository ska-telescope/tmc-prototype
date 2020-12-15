"""
StartUpTelescope class for CentralNode.
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
from centralnode.tango_client import tango_client
# PROTECTED REGION END #    //  CentralNode.additional_import

class StartUpTelescope(SKABaseDevice.OnCommand):
    """
    A class for CentralNode's StartupCommand() command.
    """

    def check_allowed(self):
        """
        Checks whether this command is allowed to be run in current device state

        :return: True if this command is allowed to be run in current device state

        :rtype: boolean

        :raises: DevFailed if this command is not allowed to be run in current device state

        """
        if self.state_model.op_state in [DevState.FAULT, DevState.UNKNOWN, DevState.DISABLE]:
            tango.Except.throw_exception("Command StartUpTelescope is not allowed in current state.",
                                         "Failed to invoke StartUpTelescope command on CentralNode.",
                                         "CentralNode.StartUpTelescope()",
                                         tango.ErrSeverity.ERR)
        return True

    def do(self):
        """
        Setting the startup state to TRUE enables the telescope to accept subarray commands as per the subarray
        model. Set the CentralNode into ON state.

        :param argin: None.

        :return: A tuple containing a return code and a string message indicating status.
        The message is for information purpose only.

        :rtype: (ResultCode, str)

        :raises: DevFailed if error occurs while invoking command on any of the devices like SubarrayNode,
                DishLeafNode, CSPMasterLeafNode or SDpMasterLeafNode

        """
        self.logger.info(type(self.target))
        device_data = DeviceData.get_instance()
        log_msg = const.STR_ON_CMD_ISSUED
        self.logger.info(log_msg)
        device_data._read_activity_message = log_msg
        sdp_mln_client = TangoClient(device_data.sdp_master_ln_fqdn)
        csp_mln_client = TangoClient(device_data.csp_master_ln_fqdn)

        for name in range(0, len(device_data._dish_leaf_node_devices)):
            try:
                device_data._leaf_device_proxy[name].command_inout(const.CMD_ON)
                device_data._leaf_device_proxy[name].command_inout(const.CMD_SET_OPERATE_MODE)
                log_msg = const.CMD_SET_OPERATE_MODE + 'invoked on' + str(device_data._leaf_device_proxy[name])
                self.logger.info(log_msg)
            except DevFailed as dev_failed:
                log_msg = const.ERR_EXE_ON_CMD + str(dev_failed)
                self.logger.exception(dev_failed)
                device_data._read_activity_message = const.ERR_EXE_ON_CMD
                tango.Except.throw_exception(const.STR_ON_EXEC, log_msg,
                                             "CentralNode.StartUpTelescopeCommand",
                                             tango.ErrSeverity.ERR)
        try:
            csp_mln_client.command_inout(const.CMD_ON)
            self.logger.info(const.STR_CMD_ON_CSP_DEV)

        except DevFailed as dev_failed:
            log_msg = const.ERR_EXE_ON_CMD + str(dev_failed)
            self.logger.exception(dev_failed)
            device_data._read_activity_message = const.ERR_EXE_ON_CMD
            tango.Except.throw_exception(const.STR_ON_EXEC, log_msg,
                                         "CentralNode.StartUpTelescopeCommand",
                                         tango.ErrSeverity.ERR)
        try:
            sdp_mln_client.command_inout(const.CMD_ON)
            self.logger.info(const.STR_CMD_ON_SDP_DEV)
        except DevFailed as dev_failed:
            log_msg = const.ERR_EXE_ON_CMD + str(dev_failed)
            self.logger.exception(dev_failed)
            device_data._read_activity_message = const.ERR_EXE_ON_CMD
            tango.Except.throw_exception(const.STR_ON_EXEC, log_msg,
                                         "CentralNode.StartUpTelescopeCommand",
                                         tango.ErrSeverity.ERR)
        try:
            for subarrayID in range(1, len(device_data.TMMidSubarrayNodes) + 1):
                device_data.subarray_FQDN_dict[subarrayID].command_inout(const.CMD_ON)
                self.logger.info(const.STR_CMD_ON_SA_DEV)
        except DevFailed as dev_failed:
            log_msg = const.ERR_EXE_ON_CMD + str(dev_failed)
            self.logger.exception(dev_failed)
            device_data._read_activity_message = const.ERR_EXE_ON_CMD
            tango.Except.throw_exception(const.STR_ON_EXEC, log_msg,
                                         "CentralNode.StartUpTelescopeCommand",
                                         tango.ErrSeverity.ERR)
        return (ResultCode.OK, device_data._read_activity_message)

    def is_StartUpTelescope_allowed(self):
        """
        Checks whether this command is allowed to be run in current device state.

        :return: True if this command is allowed to be run in current device state.

        :rtype: boolean

        :raises: DevFailed if this command is not allowed to be run in current device state.

        """
        handler = self.get_command_object("StartUpTelescope")
        return handler.check_allowed()

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="[ResultCode, information-only string]",
    )
    @DebugIt()
    def StartUpTelescope(self):
        """
        This command invokes SetOperateMode() command on DishLeadNode, On() command on CspMasterLeafNode,
        SdpMasterLeafNode and SubarrayNode and sets the Central Node into ON state.
        """
        handler = self.get_command_object("StartUpTelescope")
        (result_code, message) = handler()
        return [[result_code], [message]]


