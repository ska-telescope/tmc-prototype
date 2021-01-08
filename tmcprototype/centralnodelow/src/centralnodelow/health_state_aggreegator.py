"""
StartUpTelescope class for CentralNodelow.
"""
# Tango imports
import logging
import tango
from tango import  DevFailed
# Additional import
from ska.base.control_model import HealthState
from . import const
from .device_data import DeviceData
from tmc.common.tango_client import TangoClient
from tmc.common.tango_server_helper import TangoServerHelper

class HealthStateAggreegator:
    """
    Aggrergator class for health state event supscription and health state
    callback.
    """
    def __init__(self, logger=None):
        if logger == None:
            self.logger = logging.getLogger(__name__)
        else:
            self.logger = logger
        self.device_data = DeviceData.get_instance()
        self.subarray_health_state_map = {}
        self.this_server = TangoServerHelper.get_instance()
        # FQDN are passed as string here. Once tangoserverhelper is updated in tmccommonpackage, then this will be updated.
        self.mccs_master_ln_fqdn = "ska_low/tm_leaf_node/mccs_master"
        self.health_state_event_map = {}

    def subscribe_event(self):
        """
        Method for event subscription. Calls separate subscribe event methods for CSP Master, SDP Master and
        Subarray health state attribute subscription.
        """
        self.mccs_health_subscribe_event()
        self.subarray_health_subscribe_event()
        
        
    def mccs_health_subscribe_event(self):
        """
        Method to subscribe to health state change event on MccsMasterLeafNode.

        :raises: Devfailed exception if erroe occures while subscribing event.
        """
        mccs_mln_client = TangoClient(self.device_data.mccs_master_ln_fqdn)
        try:
            self.mccs_event_id = mccs_mln_client.subscribe_attribute(const.EVT_SUBSR_MCCS_MASTER_HEALTH,
                                                                   self.health_state_cb)
            self.health_state_event_map[mccs_mln_client] = self.mccs_event_id

        except DevFailed as dev_failed:
            log_msg = const.ERR_SUBSR_MCCS_MASTER_LEAF_HEALTH + str(dev_failed)
            self.logger.exception(dev_failed)
            self.device_data._read_activity_message = const.ERR_SUBSR_MCCS_MASTER_LEAF_HEALTH
            tango.Except.throw_exception(const.STR_CMD_FAILED, log_msg, "CentralNode.HealthStateSubscribeEvent",
                                         tango.ErrSeverity.ERR)

    def subarray_health_subscribe_event(self):
        """
        Method to subscribe to health state change event on SubarrayNode.

        :raises: Devfailed exception if erroe occures while subscribing event.
        """
        for subarray_fqdn in self.device_data.subarray_low:
            subarray_client = TangoClient(subarray_fqdn)
            # updating the subarray_health_state_map with device name (as ska_mid/tm_subarray_node/1) and its value which is required in callback
            self.subarray_health_state_map[subarray_fqdn] = -1
            try:
                event_id = subarray_client.subscribe_attribute(const.EVT_SUBSR_HEALTH_STATE,
                                                               self.health_state_cb)
                self.health_state_event_map[subarray_client] = event_id

            except DevFailed as dev_failed:
                log_msg = const.ERR_SUBSR_SA_HEALTH_STATE + str(dev_failed)
                self.logger.exception(dev_failed)
                self.device_data._read_activity_message = const.ERR_SUBSR_SA_HEALTH_STATE
                tango.Except.throw_exception(const.STR_CMD_FAILED, log_msg, "CentralNode.HealthStateSubscribeEvent",
                                             tango.ErrSeverity.ERR)

    def unsubscribe_event(self):
        """
        Method to unsubscribe to health state change event on MccsMasterLeafNode and SubarrayNode
        """
        for tango_client in self.health_state_event_map:
            log_message = "Unsubscribing ObsState of: {}".format(tango_client.get_device_fqdn)
            self.logger.debug(log_message)
            tango_client.unsubscribe_attribute(self.health_state_event_map[tango_client])
        self.health_state_event_map.clear()


    def health_state_cb(self, evt):
        """
        Receives the subscribed Subarray health state and MCCS Master Leaf Node health state,
        aggregates them to calculate the telescope health state.

        :param evt: A event on Subarray healthState and MCCSMasterLeafNode healthstate.

        :type: Event object
            It has the following members:

                - date (event timestamp)

                - reception_date (event reception timestamp)

                - type (event type)

                - dev_name (device name)

                - name (attribute name)

                - value (event value)

        :return: None

        :raises: KeyError if error occurs while setting telescope healthState
        """
        device_data = DeviceData.get_instance()
        try:
            log_msg = 'Health state attribute change event is : ' + str(evt)
            self.logger.info(log_msg)
            if not evt.err:
                health_state = evt.attr_value.value
                if const.PROP_DEF_VAL_TM_LOW_SA1 in evt.attr_name:
                    device_data._subarray1_health_state = health_state
                    self.subarray_health_state_map[evt.device] = health_state
                elif self.mccs_master_ln_fqdn in evt.attr_name:
                    device_data._mccs_master_leaf_health = health_state
                else:
                    self.logger.debug(const.EVT_UNKNOWN)

                counts = {
                    HealthState.OK: 0,
                    HealthState.DEGRADED: 0,
                    HealthState.FAILED: 0,
                    HealthState.UNKNOWN: 0
                }

                # TODO: For Future use
                for subsystem_health_field_name in ['mccs_master_leaf_health']:
                    health_state = getattr(device_data, f"_{subsystem_health_field_name}")
                    counts[health_state] += 1

                for subarray_health_state in self.subarray_health_state_map.values():
                    counts[subarray_health_state] += 1

                # Calculating health_state for SubarrayNode, MCCSMasterLeafNode
                if counts[HealthState.OK] == len(self.subarray_health_state_map.values()) + 1:
                    device_data._telescope_health_state = HealthState.OK
                    str_log = const.STR_HEALTH_STATE + str(evt.device) + const.STR_OK
                    self.logger.info(str_log)
                    device_data._read_activity_message = const.STR_HEALTH_STATE + str(evt.device
                                                                               ) + const.STR_OK
                elif counts[HealthState.FAILED] != 0:
                    device_data._telescope_health_state = HealthState.FAILED
                    str_log = const.STR_HEALTH_STATE + str(evt.device) + const.STR_FAILED
                    self.logger.info(str_log)
                    device_data._read_activity_message = const.STR_HEALTH_STATE + str(evt.device
                                                                               ) + const.STR_FAILED
                elif counts[HealthState.DEGRADED] != 0:
                    device_data._telescope_health_state = HealthState.DEGRADED
                    str_log = const.STR_HEALTH_STATE + str(evt.device) + const.STR_DEGRADED
                    self.logger.info(str_log)
                    device_data._read_activity_message = const.STR_HEALTH_STATE + str(evt.device
                                                                               ) + const.STR_DEGRADED
                else:
                    device_data._telescope_health_state = HealthState.UNKNOWN
                    str_log = const.STR_HEALTH_STATE + str(evt.device) + const.STR_UNKNOWN
                    self.logger.info(str_log)
                    device_data._read_activity_message = const.STR_HEALTH_STATE + str(evt.device
                                                                               ) + const.STR_UNKNOWN
            else:
                device_data._read_activity_message = const.ERR_SUBSR_SA_HEALTH_STATE + str(evt)
                self.logger.critical(const.ERR_SUBSR_SA_HEALTH_STATE)
        except KeyError as key_error:
            device_data._read_activity_message = const.ERR_SUBARRAY_HEALTHSTATE + str(key_error)
            log_msg = const.ERR_SUBARRAY_HEALTHSTATE + ": " + str(key_error)
            self.logger.error(log_msg)



