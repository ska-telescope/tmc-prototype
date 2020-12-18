
from . import const
from subarraynode.device_data import DeviceData
from ska.base.control_model import HealthState

class HealthStateAggregator:
    """
    Health State Aggregator class
    """
    def __init__(self):
        self.subarray_ln_health_state_map = {}

    def health_state_cb(self, event):
        """
        Retrieves the subscribed health states, aggregates them
        to calculate the overall subarray health state.

        :param event: A TANGO_CHANGE event on Subarray healthState.

        :return: None
        """
        device_name = event.device.dev_name()
        log_msg= "Device name is : " + str(device_name)
        # self.logger.debug(log_msg)
        if not event.err:
            event_health_state = event.attr_value.value
            self.subarray_ln_health_state_map[device_name] = event_health_state

            log_message = self.generate_health_state_log_msg(
                event_health_state, device_name, event)
            # self._read_activity_message = log_message
            self.activityMessage = log_message
            self._health_state = self.calculate_health_state(
                self.subarray_ln_health_state_map.values())
        else:
            log_message = const.ERR_SUBSR_SA_HEALTH_STATE + str(device_name) + str(event)
            # self._read_activity_message = log_message
            self.activityMessage = log_message

    def generate_health_state_log_msg(self, health_state, device_name, event):
        if isinstance(health_state, HealthState):
            return (
                const.STR_HEALTH_STATE + str(device_name) + const.STR_ARROW + str(health_state.name.upper()))
        else:
            return const.STR_HEALTH_STATE_UNKNOWN_VAL + str(event)

    def calculate_health_state(self, health_states):
        """
        Calculates aggregated health state of Subarray.
        """
        unique_states = set(health_states)
        if unique_states == set([HealthState.OK]):
            return HealthState.OK
        elif HealthState.FAILED in unique_states:
            return HealthState.FAILED
        elif HealthState.DEGRADED in unique_states:
            return HealthState.DEGRADED
        else:
            return HealthState.UNKNOWN
