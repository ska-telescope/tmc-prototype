"""
health_state_aggregator class for CentralNode.
"""
# PROTECTED REGION ID(CentralNode.additionnal_import) ENABLED START #
import logging

import tango
from tango import DevFailed

# Additional import
from ska.base.control_model import HealthState

from tmc.common.tango_client import TangoClient
from tmc.common.tango_server_helper import TangoServerHelper

from . import const
from centralnode.device_data import DeviceData

# PROTECTED REGION END #    //  CentralNode.additional_import


class HealthStateAggregator:
    """
    Aggrergator class for health state event supscription and health state
    callback.
    """

    def __init__(self, logger=None):
        if logger is None:
            self.logger = logging.getLogger(__name__)
        else:
            self.logger = logger
        self.device_data = DeviceData.get_instance()
        self.subarray_health_state_map = {}
        self.this_server = TangoServerHelper.get_instance()
        # FQDN are passed as string here. Once tangoserverhelper is updated in tmccommonpackage, then this will be updated.
        self.csp_master_ln_fqdn = "ska_mid/tm_leaf_node/csp_master"
        self.sdp_master_ln_fqdn = "ska_mid/tm_leaf_node/sdp_master"
        self.health_state_event_map = {}

    def subscribe_event(self):
        """
        Method for event subscription. Calls separate subscribe event methods for CSP Master, SDP Master and
        Subarray health state attribute subscription.
        """
        self.csp_health_subscribe_event()
        self.sdp_health_subscribe_event()
        self.subarray_health_subscribe_event()

    def csp_health_subscribe_event(self):
        """
        Method to subscribe to health state change event on CspMasterLeafNode.

        :raises: Devfailed exception if error occures while subscribing event.
        """
        csp_mln_client = TangoClient(self.device_data.csp_master_ln_fqdn)
        try:
            self.csp_event_id = csp_mln_client.subscribe_attribute(
                const.EVT_SUBSR_CSP_MASTER_HEALTH, self.health_state_cb
            )
            self.health_state_event_map[csp_mln_client] = self.csp_event_id
        except DevFailed as dev_failed:
            log_msg = f"{const.ERR_SUBSR_CSP_MASTER_LEAF_HEALTH}{dev_failed}"
            self.logger.exception(dev_failed)
            self._read_activity_message = const.ERR_SUBSR_CSP_MASTER_LEAF_HEALTH
            tango.Except.throw_exception(
                const.STR_CMD_FAILED,
                log_msg,
                "CentralNode.HealthStateSubscribeEvent",
                tango.ErrSeverity.ERR,
            )

    def sdp_health_subscribe_event(self):
        """
        Method to subscribe to health state change event on SdpMasterLeafNode.

        :raises: Devfailed exception if error occures while subscribing event.
        """
        sdp_mln_client = TangoClient(self.device_data.sdp_master_ln_fqdn)
        try:
            self.sdp_event_id = sdp_mln_client.subscribe_attribute(
                const.EVT_SUBSR_SDP_MASTER_HEALTH, self.health_state_cb
            )
            self.health_state_event_map[sdp_mln_client] = self.sdp_event_id
        except DevFailed as dev_failed:
            log_msg = f"{const.ERR_SUBSR_SDP_MASTER_LEAF_HEALTH}{dev_failed}"
            self.logger.exception(dev_failed)
            self._read_activity_message = const.ERR_SUBSR_SDP_MASTER_LEAF_HEALTH
            tango.Except.throw_exception(
                const.STR_CMD_FAILED,
                log_msg,
                "CentralNode.HealthStateSubscribeEvent",
                tango.ErrSeverity.ERR,
            )

    def subarray_health_subscribe_event(self):
        """
        Method to subscribe to health state change event on SubarrayNode.

        :raises: Devfailed exception if erroe occures while subscribing event.
        """
        for subarray_fqdn in self.device_data.tm_mid_subarray:
            subarray_client = TangoClient(subarray_fqdn)
            # updating the subarray_health_state_map with device name (as ska_mid/tm_subarray_node/1) and its value which is required in callback
            self.subarray_health_state_map[subarray_fqdn] = -1
            try:
                event_id = subarray_client.subscribe_attribute(
                    const.EVT_SUBSR_HEALTH_STATE, self.health_state_cb
                )
                self.health_state_event_map[subarray_client] = event_id
            except DevFailed as dev_failed:
                log_msg = f"{const.ERR_SUBSR_SA_HEALTH_STATE}{dev_failed}"
                self.logger.exception(dev_failed)
                self._read_activity_message = const.ERR_SUBSR_SA_HEALTH_STATE
                tango.Except.throw_exception(
                    const.STR_CMD_FAILED,
                    log_msg,
                    "CentralNode.HealthStateSubscribeEvent",
                    tango.ErrSeverity.ERR,
                )

    def unsubscribe_event(self):
        """
        Method to unsubscribe to health state change event on CspMasterLeafNode, SdpMasterLeafNode and SubarrayNode
        """
        for tango_client in self.health_state_event_map:
            log_message = "Unsubscribing ObsState of: {}".format(
                tango_client.get_device_fqdn
            )
            self.logger.debug(log_message)
            tango_client.unsubscribe_attribute(
                self.health_state_event_map[tango_client]
            )
        self.health_state_event_map.clear()

    def health_state_cb(self, event):
        """
        Retrieves the subscribed Subarray health state, aggregates them to calculate the
        telescope health state.

        :param event: A TANGO_CHANGE event on Subarray healthState.

        :return: None
        """
        device_data = DeviceData.get_instance()
        self._read_activity_message = "Within health callback"
        self.logger.info(self._read_activity_message)
        log_msg = f'Health state attribute change event is : {event.attr_name}'
        self.logger.info(log_msg)
        log_msg = f'Health state attribute change event is .....................: {event.attr_value.value}'
        self.logger.info(log_msg)

        def _update_health_state(self, fqdn_device_health_state_map: dict):
            health_state = event.attr_value.value
            attr_name = event.attr_name
            self.logger.info(f"Health state is: {health_state}")
            for fqdn, dd_health_state in fqdn_device_health_state_map.items():
                if fqdn in attr_name:
                    setattr(device_data, dd_health_state, health_state)
                    if "subarray" in fqdn:
                        self.subarray_health_state_map[attr_name] = health_state
                    elif "csp" in fqdn:
                        self.logger.info(f"Health state msg in CSP Master....: {attr_name}")
                        self.logger.info(f"CSP Master health is....: {health_state}")
                    break
            else:
                self.logger.debug(const.event_UNKNOWN)
                # TODO: update read_activity message for unknown events

        def _generate_health_state_log_msg(self, health_state):
            health_state_string_map = {
                HealthState.OK: const.STR_OK,
                HealthState.DEGRADED: const.STR_DEGRADED,
                HealthState.FAILED: const.STR_FAILED,
                HealthState.UNKNOWN: const.STR_UNKNOWN
            }
            log_msg = f"{const.STR_HEALTH_STATE}{event.device}{health_state_string_map[health_state]}"                       
            self.logger.info(log_msg)
            self._read_activity_message = log_msg

        def _calculate_health_state(health_states):
            unique_states = set(health_states)
            if unique_states == set([HealthState.OK]):
                device_data._telescope_health_state = HealthState.OK
                _generate_health_state_log_msg(self, HealthState.OK)
            elif HealthState.FAILED in unique_states:
                device_data._telescope_health_state = HealthState.FAILED
                _generate_health_state_log_msg(self, HealthState.FAILED)
            elif HealthState.DEGRADED in unique_states:
                device_data._telescope_health_state = HealthState.DEGRADED
                _generate_health_state_log_msg(self, HealthState.DEGRADED)
            else:
                device_data._telescope_health_state = HealthState.UNKNOWN
                _generate_health_state_log_msg(self, HealthState.UNKNOWN)
            
        if not event.err:
            fqdn_device_health_state_map = {
                const.PROP_DEF_VAL_TM_MID_SA1: "_subarray1_health_state",
                const.PROP_DEF_VAL_TM_MID_SA2: "._subarray2_health_state",
                const.PROP_DEF_VAL_TM_MID_SA3: "_subarray3_health_state",
                self.csp_master_ln_fqdn: "_csp_master_leaf_health",
                self.sdp_master_ln_fqdn: "_sdp_master_leaf_health"
            }
            _update_health_state(self, fqdn_device_health_state_map)

            health_states = [
                device_data._csp_master_leaf_health,
                device_data._sdp_master_leaf_health
            ]
            health_states = health_states + list(self.subarray_health_state_map.values())
            _calculate_health_state(health_states)

        else:
            # TODO: For future reference
            self._read_activity_message = f"{const.ERR_SUBSR_SA_HEALTH_STATE}{event}"
            log_msg = self._read_activity_message
            self.logger.info(log_msg)
            self.logger.critical(const.ERR_SUBSR_SA_HEALTH_STATE)
