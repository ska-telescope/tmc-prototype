from . import const
from ska.base.control_model import HealthState
from tmc.common.tango_client import TangoClient
from tmc.common.tango_server_helper import TangoServerHelper
from .device_data import DeviceData
import logging

class HealthStateAggregator:
    """
    Health State Aggregator class
    """
    def __init__(self, logger = None):
        if logger == None:
            self.logger = logging.getLogger(__name__)
        else:
            self.logger = logger

        self.mccs_ln_health_event_id = {}
        self.this_server = TangoServerHelper.get_instance()
        self.device_data = DeviceData.get_instance()
        self.mccs_client = TangoClient(self.device_data.mccs_subarray_ln_fqdn)


    def subscribe(self):
        # Subscribe cspsubarrayHealthState (forwarded attribute) of CspSubarray
        mccs_event_id = self.mccs_client.subscribe_attribute(const.EVT_MCCSSA_HEALTH, self.health_state_cb)
        self.mccs_ln_health_event_id[self.mccs_client] = mccs_event_id
        log_msg = const.STR_SUB_ATTR_MCCS_SALN_HEALTH_SUCCESS + str(self.mccs_ln_health_event_id)
        self.logger.debug(log_msg)
        # tango_server_helper_obj = TangoServerHelper.get_instance()
        # tango_server_helper_obj.set_status(const.STR_SUB_ATTR_MCCS_SALN_HEALTH_SUCCESS)
        self.logger.info(const.STR_SUB_ATTR_MCCS_SALN_HEALTH_SUCCESS)

    def health_state_cb(self, event):
        """
        Receives the subscribed health states, aggregates them
        to calculate the overall subarray health state.

        :param evt: A event on MCCS Subarray healthState.

        :type: Event object
            It has the following members:

                - date (event timestamp)

                - reception_date (event reception timestamp)

                - type (event type)

                - dev_name (device name)

                - name (attribute name)

                - value (event value)

        :return: None
        """

        device_name = event.device.dev_name()
        if not event.err:
            event_health_state = event.attr_value.value
            self.mccs_ln_health_event_id[device_name] = event_health_state

            log_message = self.generate_health_state_log_msg(
                event_health_state, device_name, event)
            self.device_data.activity_message = log_message
            self.device_data._subarray_health_state = self.calculate_health_state(self.mccs_ln_health_event_id.values())
        else:
            log_message = const.ERR_SUBSR_SA_HEALTH_STATE + str(device_name) + str(event)
            self.device_data.activity_message = log_message


    def generate_health_state_log_msg(self, health_state, device_name, event):
        if isinstance(health_state, HealthState):
            return (
                const.STR_HEALTH_STATE + str(device_name) + const.STR_ARROW + str(health_state.name.upper()))
        else:
            return const.STR_HEALTH_STATE_UNKNOWN_VAL + str(event)

    def calculate_health_state(self, health_states):
        """
        Calculates aggregated health state of SubarrayLow.
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

    def unsubscribe(self):
        """
        This function unsubscribes all health state events given by the event ids and their
        corresponding DeviceProxy objects.

        :param : None

        :return: None

        """
        for tango_client, event_id in self.mccs_ln_health_event_id.items():
            tango_client.unsubscribe_attribute(event_id)

