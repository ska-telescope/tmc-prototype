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
        device_data = self.target
        log_msg = const.STR_STANDBY_CMD_ISSUED
        self.logger.info(log_msg)
        device_data._read_activity_message = log_msg
        self.standby_dish()
        self.standby_csp()
        self.standby_sdp()
        self.standby_subarray()
        return (ResultCode.OK, device_data._read_activity_message)

    def standby_csp(self):
        csp_mln_client = TangoClient(device_data.csp_master_ln_fqdn)
        self.standby_leaf_node(csp_mln_client, const.CMD_OFF)
        self.standby_leaf_node(csp_mln_client, const.CMD_STANDBY, [])

    def standby_sdp(self):
        sdp_mln_client = TangoClient(device_data.sdp_master_ln_fqdn)
        self.standby_leaf_node(sdp_mln_client, const.CMD_OFF)
        self.standby_leaf_node(sdp_mln_client, const.CMD_STANDBY)


    def standby_dish(self):
        for name in range(0, len(device_data._dish_leaf_node_devices)):
            dish_ln_client = TangoClient(device_data._dish_leaf_node_devices[name])
            self.standby_leaf_node(dish_ln_client, const.CMD_SET_STANDBY_MODE)

    def standby_subarray(self):
        for subarrayID in range(1, len(device_data.tm_mid_subarray) + 1):
            subarray_client = TangoClient(subarrayID)
            self.standby_leaf_node(subarray_client, const.CMD_OFF)
            self.standby_leaf_node(subarray_client, const.CMD_STANDBY)

    def standby_leaf_node(self,tango_client, cmd_name, param=None):
        device_data = self.target
        try:
            tango_client.send_command(cmd_name, param)
            log_msg = 'Command {} invoked successfully on {}'.format(cmd_name, tango_client.get_device_fqdn)
            self.logger.debug(log_msg)
            device_data._read_activity_message = log_msg

        except DevFailed as dev_failed:
            log_msg = const.ERR_EXE_STANDBY_CMD + str(dev_failed)
            self.logger.exception(dev_failed)
            device_data._read_activity_message = const.ERR_EXE_STANDBY_CMD
            tango.Except.throw_exception(const.STR_STANDBY_EXEC, log_msg,
                                         "CentralNode.StandByTelescopeCommand",
                                         tango.ErrSeverity.ERR)






