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
from centralnode.device_data import DeviceData
from centralnode.HealthStateCb import HealthStateCb
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
