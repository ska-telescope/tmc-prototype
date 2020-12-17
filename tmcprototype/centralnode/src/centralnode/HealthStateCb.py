"""
HealthStateCb class for CentralNode.
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

class HealthStateCb:
    """
    Retrieves the subscribed Subarray health state, aggregates them to calculate the
    telescope health state.

    :param evt: A TANGO_CHANGE event on Subarray healthState.

    :return: None

    :raises: KeyError if error occurs while setting Subarray healthState
    """
    def do(self, evt):
        self.logger.info(type(self.target))
        device_data = DeviceData.get_instance()
        try:
            log_msg = 'Health state attribute change event is : ' + str(evt)
            self.logger.info(log_msg)
            if not evt.err:
                health_state = evt.attr_value.value
                if const.PROP_DEF_VAL_TM_MID_SA1 in evt.attr_name:
                    self._subarray1_health_state = health_state
                    self.subarray_health_state_map[evt.device] = health_state
                elif const.PROP_DEF_VAL_TM_MID_SA2 in evt.attr_name:
                    self._subarray2_health_state = health_state
                    self.subarray_health_state_map[evt.device] = health_state
                elif const.PROP_DEF_VAL_TM_MID_SA3 in evt.attr_name:
                    self._subarray3_health_state = health_state
                    self.subarray_health_state_map[evt.device] = health_state
                elif self.CspMasterLeafNodeFQDN in evt.attr_name:
                    self._csp_master_leaf_health = health_state
                elif self.SdpMasterLeafNodeFQDN in evt.attr_name:
                    self._sdp_master_leaf_health = health_state
                else:
                    self.logger.debug(const.EVT_UNKNOWN)
                    # TODO: For future reference
                    # self._read_activity_message = const.EVT_UNKNOWN

                counts = {
                    HealthState.OK: 0,
                    HealthState.DEGRADED: 0,
                    HealthState.FAILED: 0,
                    HealthState.UNKNOWN: 0
                }

                for subsystem_health_field_name in ['csp_master_leaf_health', 'sdp_master_leaf_health']:
                    health_state = getattr(self, f"_{subsystem_health_field_name}")
                    counts[health_state] += 1

                for subarray_health_state in list(self.subarray_health_state_map.values()):
                    counts[subarray_health_state] += 1

                # Calculating health_state for SubarrayNode, CspMasterLeafNode, SdpMasterLeafNode
                if counts[HealthState.OK] == len(list(self.subarray_health_state_map.values())) + 2:
                    self._telescope_health_state = HealthState.OK
                    str_log = const.STR_HEALTH_STATE + str(evt.device) + const.STR_OK
                    self.logger.info(str_log)
                    self._read_activity_message = const.STR_HEALTH_STATE + str(evt.device
                                                                               ) + const.STR_OK
                elif counts[HealthState.FAILED] != 0:
                    self._telescope_health_state = HealthState.FAILED
                    str_log = const.STR_HEALTH_STATE + str(evt.device) + const.STR_FAILED
                    self.logger.info(str_log)
                    self._read_activity_message = const.STR_HEALTH_STATE + str(evt.device
                                                                               ) + const.STR_FAILED
                elif counts[HealthState.DEGRADED] != 0:
                    self._telescope_health_state = HealthState.DEGRADED
                    str_log = const.STR_HEALTH_STATE + str(evt.device) + const.STR_DEGRADED
                    self.logger.info(str_log)
                    self._read_activity_message = const.STR_HEALTH_STATE + str(evt.device
                                                                               ) + const.STR_DEGRADED
                else:
                    self._telescope_health_state = HealthState.UNKNOWN
                    str_log = const.STR_HEALTH_STATE + str(evt.device) + const.STR_UNKNOWN
                    self.logger.info(str_log)
                    self._read_activity_message = const.STR_HEALTH_STATE + str(evt.device
                                                                               ) + const.STR_UNKNOWN
            else:
                # TODO: For future reference
                self._read_activity_message = const.ERR_SUBSR_SA_HEALTH_STATE + str(evt)
                self.logger.critical(const.ERR_SUBSR_SA_HEALTH_STATE)
        except KeyError as key_error:
            # TODO: For future reference
            self._read_activity_message = const.ERR_SUBARRAY_HEALTHSTATE + str(key_error)
            log_msg = const.ERR_SUBARRAY_HEALTHSTATE + ": " + str(key_error)
            self.logger.critical(log_msg)
