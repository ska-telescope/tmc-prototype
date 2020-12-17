"""
ObsStateCb class for CentralNode.
"""

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

class ObsStateCb:
    """
    Retrieves the subscribed Subarray observation state. When the Subarray obsState is EMPTY, the resource
    allocation list gets cleared.

    :param evt: A TANGO_CHANGE event on Subarray obsState.

    :return: None

    :raises: KeyError in Subarray obsState callback
    """
    def do(self, evt):
        self.logger.info(type(self.target))
        device_data = DeviceData.get_instance()
        try:
            log_msg = 'Observation state attribute change event is : ' + str(evt)
            self.logger.info(log_msg)
            if not evt.err:
                obs_state = evt.attr_value.value
                subarray_device = evt.device
                subarray_device_list = list(str(subarray_device))
                # Identify the Subarray ID
                for index in range(0, len(subarray_device_list)):
                    if subarray_device_list[index].isdigit():
                        id = subarray_device_list[index]

                subarray_id = "SA" + str(id)
                self.logger.info(log_msg)
                if obs_state == ObsState.EMPTY or obs_state == ObsState.RESTARTING:
                    for dish, subarray in self._subarray_allocation.items():
                        if subarray == subarray_id:
                            device_data._subarray_allocation[dish] = "NOT_ALLOCATED"
                log_msg = "Subarray_allocation is: " + str(device_data._subarray_allocation)
                self.logger.info(log_msg)
            else:
                # TODO: For future reference
                device_data._read_activity_message = const.ERR_SUBSR_SA_OBS_STATE + str(evt)
                self.logger.critical(const.ERR_SUBSR_SA_OBS_STATE)
        except KeyError as key_error:
            device_data._read_activity_message = const.ERR_SUBARRAY_HEALTHSTATE + str(key_error)
            log_msg = const.ERR_SUBARRAY_HEALTHSTATE + ": " + str(key_error)
            self.logger.critical(log_msg)
