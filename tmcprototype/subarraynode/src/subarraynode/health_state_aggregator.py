
from . import const
from ska.base.control_model import HealthState
from subarraynode.tango_client import TangoClient
from subarraynode.tango_server_helper import TangoServerHelper

class HealthStateAggregator:
    """
    Health State Aggregator class
    """
    def __init__(self):
        self.subarray_ln_health_state_map = {}
        self.csp_sdp_ln_health_event_id = {}
        self.this_server = TangoServerHelper.get_instance()
        # How to pass fqdn here? 
        self.csp_client = TangoClient("")
        self.sdp_client = TangoClient("")
        
    
    def subscribe(self):
        # TODO: dev_name() where to keep this API?
        self.subarray_ln_health_state_map[self.csp_client.get_device_fqdn()] = (HealthState.UNKNOWN)
        # Subscribe cspsubarrayHealthState (forwarded attribute) of CspSubarray
        csp_event_id = self.csp_client.subscribe_attribute(const.EVT_CSPSA_HEALTH, self.health_state_cb)
        self.csp_sdp_ln_health_event_id[self.csp_client] = csp_event_id
        log_msg = const.STR_CSP_LN_VS_HEALTH_EVT_ID + str(self.csp_sdp_ln_health_event_id)
        self.logger.debug(log_msg)
        self.this_server.set_status(const.STR_CSP_SA_LEAF_INIT_SUCCESS)
        self.logger.info(const.STR_CSP_SA_LEAF_INIT_SUCCESS)

        self.subarray_ln_health_state_map[self.sdp_client.get_device_fqdn()] = (HealthState.UNKNOWN)
        # Subscribe sdpSubarrayHealthState (forwarded attribute) of SdpSubarray
        sdp_event_id = self.sdp_client.subscribe_attribute(const.EVT_SDPSA_HEALTH, self.health_state_cb)   
        self.csp_sdp_ln_health_event_id[self.sdp_client] = sdp_event_id
        log_msg = const.STR_SDP_LN_VS_HEALTH_EVT_ID + str(self.csp_sdp_ln_health_event_id)
        self.logger.debug(log_msg)
        self.this_server.set_status(const.STR_SDP_SA_LEAF_INIT_SUCCESS)

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
            health_state = self.calculate_health_state(
                self.subarray_ln_health_state_map.values())

            self.this_server._health_state = health_state
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

    def unsubscribe(self):
        """
        This function unsubscribes all health state events given by the event ids and their
        corresponding DeviceProxy objects.

        :param proxy_event_id_map: dict
            A mapping of '<DeviceProxy>': <event_id>.

        :return: None

        """
        for tango_client, event_id in self.csp_sdp_ln_health_event_id.items():
            tango_client.unsubscribe_attr(event_id)
