# Standard Python imports
import logging

# Additional import
from ska.base.control_model import HealthState

from tmc.common.tango_client import TangoClient
from tmc.common.tango_server_helper import TangoServerHelper

from .device_data import DeviceData
from . import const


class HealthStateAggregator:
    """
    Health State Aggregator class
    """

    def __init__(self, logger=None):
        if logger == None:
            self.logger = logging.getLogger(__name__)
        else:
            self.logger = logger

        self.subarray_ln_health_state_map = {}
        self.csp_sdp_ln_health_event_id = {}
        self._health_event_id = []
        self.this_server = TangoServerHelper.get_instance()
        self.device_data = DeviceData.get_instance()
        self.csp_client = TangoClient(self.device_data.csp_subarray_ln_fqdn)
        self.sdp_client = TangoClient(self.device_data.sdp_subarray_ln_fqdn)
        self.subarray_ln_health_state_map[
            self.csp_client.get_device_fqdn()
        ] = HealthState.UNKNOWN
        self.subarray_ln_health_state_map[
            self.sdp_client.get_device_fqdn()
        ] = HealthState.UNKNOWN

    def subscribe(self):
        # TODO: dev_name() where to keep this API?
        # Subscribe cspsubarrayHealthState (forwarded attribute) of CspSubarray
        csp_event_id = self.csp_client.subscribe_attribute(
            const.EVT_CSPSA_HEALTH, self.health_state_cb
        )
        self.csp_sdp_ln_health_event_id[self.csp_client] = csp_event_id
        log_msg = f"{const.STR_CSP_LN_HEALTH_EVT_ID}{self.csp_sdp_ln_health_event_id}"
        self.logger.debug(log_msg)
        tango_server_helper_obj = TangoServerHelper.get_instance()
        tango_server_helper_obj.set_status(const.STR_CSP_SA_LEAF_SUB_SUCCESS)
        # Subscribe sdpSubarrayHealthState (forwarded attribute) of SdpSubarray
        sdp_event_id = self.sdp_client.subscribe_attribute(
            const.EVT_SDPSA_HEALTH, self.health_state_cb
        )
        self.csp_sdp_ln_health_event_id[self.sdp_client] = sdp_event_id
        log_msg = f"{const.STR_SDP_LN_HEALTH_EVT_ID}{self.csp_sdp_ln_health_event_id}"
        self.logger.debug(log_msg)
        tango_server_helper_obj.set_status(const.STR_SDP_SA_LEAF_SUB_SUCCESS)

    def health_state_cb(self, event):
        """
        Retrieves the subscribed health states, aggregates them
        to calculate the overall subarray health state.
        :param event: A TANGO_CHANGE event on Subarray healthState.

        :return: None
        """
        device_name = event.device.dev_name()
        log_msg = f"Device name is : {device_name}"
        self.logger.debug(log_msg)
        if not event.err:
            event_health_state = event.attr_value.value
            self.subarray_ln_health_state_map[device_name] = event_health_state
            if isinstance(event_health_state, HealthState):
                log_message = f"{const.STR_HEALTH_STATE}{device_name} \
                {const.STR_ARROW}{event_health_state.name.upper()}"
            else:
                log_message = f"{const.STR_HEALTH_STATE_UNKNOWN_VAL}{event}"
            self.device_data._read_activity_message = log_message
            self.device_data.health_state = self.calculate_health_state(
                self.subarray_ln_health_state_map.values()
            )
        else:
            log_message = f"{const.ERR_SUBSR_SA_HEALTH_STATE}{device_name}{event}"
            self.device_data._read_activity_message = log_message

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

        :param : None

        :return: None

        """
        for tango_client, event_id in self.csp_sdp_ln_health_event_id.items():
            log_msg = f"Unsubscribe Health State event for {tango_client}"
            self.logger.debug(log_msg)
            try:
                tango_client.unsubscribe_attribute(event_id)
            except KeyError as error:
                log_msg = f"{const.ERR_UNSUBSR_ATTRIBUTE}{error}"
                self.logger.exception(log_msg)
                self._read_activity_message = log_msg
                 

    def subscribe_dish_health_state(self, dish_ln_client):
        dish_event_id = dish_ln_client.subscribe_attribute(
            const.EVT_DISH_HEALTH_STATE, self.health_state_cb
        )
        self.device_data.dish_ln_health_even_id[dish_ln_client] = dish_event_id
        log_msg = f"{const.STR_DISH_LN_HEALTH_EVT_ID}{self.device_data.dish_ln_health_even_id}"
        self.logger.debug(log_msg)

    def unsubscribe_dish_health_state(self):
        for dish_ln_client in self.device_data.dish_ln_health_even_id:
            try:
                dish_ln_client.unsubscribe_attribute(
                    self.device_data.dish_ln_health_even_id[dish_ln_client]
                )
            except KeyError as error:
                log_msg = f"{const.ERR_UNSUBSR_ATTRIBUTE}{error}"
                self.logger.exception(log_msg)
                self._read_activity_message = log_msg

    def _remove_subarray_dish_lns_health_states(self):
        subarray_ln_health_state_map_copy = self.subarray_ln_health_state_map.copy()
        for dev_name in subarray_ln_health_state_map_copy:
            if dev_name.startswith(const.PROP_DEF_VAL_LEAF_NODE_PREFIX):
                _ = self.subarray_ln_health_state_map.pop(dev_name)
