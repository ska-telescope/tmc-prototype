"""
CheckReceptorReassignment class for CentralNode.
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

@DebugIt()
class CheckReceptorReassignment:
    """
    Checks if any of the receptors are already allocated to other subarray when AssignResources command is called.

    :param: argin: The input receptor list

    :return: None

    :throws:
        ResourceReassignmentError: Thrown when an already assigned resource is received
        in Assignresources command.

    """
    #
    def do(self,input_receptors_list):
        self.logger.info(type(self.target))
        self.logger.info("Checking for duplicate allocation of dishes.")
        duplicate_allocation_count = 0
        duplicate_allocation_dish_ids = []
        self.logger.info(self._subarray_allocation)

        for receptor in input_receptors_list:
            dish_ID = "dish" + receptor
            self.logger.info("Checking allocation status of dish %s.", dish_ID)
            if device_data._subarray_allocation[dish_ID] != "NOT_ALLOCATED":
                self.logger.info("Dish %s is already allocated.", dish_ID)
                # duplicate_allocation_dish_ids.append(dish_ID)
                duplicate_allocation_dish_ids.append(receptor)
                duplicate_allocation_count = duplicate_allocation_count + 1
        self.logger.info("No of dishes already allocated: %d", duplicate_allocation_count)
        self.logger.info("List of dishes already allocated: %s", str(duplicate_allocation_dish_ids))

        if duplicate_allocation_count > 0:
            exception_message = const.ERR_RECEPTOR_ID_REALLOCATION + (str(duplicate_allocation_dish_ids))
            raise ResourceReassignmentError(exception_message)
