"""
health_state_aggreegator class for CentralNode.
"""
# PROTECTED REGION ID(CentralNode.additionnal_import) ENABLED START #
import logging
import tango
from tango import DevFailed
# Additional import
from ska.base.control_model import HealthState
from . import const
from tmc.common.tango_client import TangoClient
from tmc.common.tango_server_helper import TangoServerHelper
from centralnode.device_data import DeviceData
# PROTECTED REGION END #    //  CentralNode.additional_import

class HealthStateAggreegator:
    """
    Aggrergator class for health state event supscription and health state
    callback.
    """
    def __init__(self, logger =None):
        if logger == None:
            self.logger = logging.getLogger(__name__)
        else:
            self.logger = logger
        self.device_data = DeviceData.get_instance()
        self.subarray_health_state_map = {}
        self.this_server = TangoServerHelper.get_instance()
        # FQDN are passed as string here. Once tangoserverhelper is updated in tmccommonpackage, then this will be updated.  
        self.csp_master_ln_fqdn = "ska_mid/tm_leaf_node/csp_master"
        self.sdp_master_ln_fqdn = "ska_mid/tm_leaf_node/sdp_master"
        # self.subarray_ln_fqdn_list= ["ska_mid/tm_subarray_node/1","ska_mid/tm_subarray_node/2","ska_mid/tm_subarray_node/3"]
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

        :raises: Devfailed exception if erroe occures while subscribing event.
        """
        csp_mln_client = TangoClient(self.device_data.csp_master_ln_fqdn)
        try:
            self.csp_event_id = csp_mln_client.subscribe_attribute(const.EVT_SUBSR_CSP_MASTER_HEALTH,
                                                                        self.health_state_cb)
            self.health_state_event_map[csp_mln_client] = self.csp_event_id
        except DevFailed as dev_failed:
            log_msg = const.ERR_SUBSR_CSP_MASTER_LEAF_HEALTH + str(dev_failed)
            self.logger.exception(dev_failed)
            self._read_activity_message = const.ERR_SUBSR_CSP_MASTER_LEAF_HEALTH
            tango.Except.throw_exception(const.STR_CMD_FAILED, log_msg, "CentralNode.HealthStateSubscribeEvent",
                                        tango.ErrSeverity.ERR)


    def sdp_health_subscribe_event(self):
        """
        Method to subscribe to health state change event on SdpMasterLeafNode.

        :raises: Devfailed exception if erroe occures while subscribing event.
        """
        sdp_mln_client = TangoClient(self.device_data.sdp_master_ln_fqdn)
        try:
            self.sdp_event_id = sdp_mln_client.subscribe_attribute(const.EVT_SUBSR_SDP_MASTER_HEALTH,
                                                                        self.health_state_cb)
            self.health_state_event_map[sdp_mln_client] = self.sdp_event_id
        except DevFailed as dev_failed:
            log_msg = const.ERR_SUBSR_SDP_MASTER_LEAF_HEALTH + str(dev_failed)
            self.logger.exception(dev_failed)
            self._read_activity_message = const.ERR_SUBSR_SDP_MASTER_LEAF_HEALTH
            tango.Except.throw_exception(const.STR_CMD_FAILED, log_msg, "CentralNode.HealthStateSubscribeEvent",
                                        tango.ErrSeverity.ERR)

    def subarray_health_subscribe_event(self):
        """
        Method to subscribe to health state change event on SubarrayNode.

        :raises: Devfailed exception if erroe occures while subscribing event.
        """
        for subarray_fqdn in self.device_data.tm_mid_subarray:
            subarray_client = TangoClient(subarray_fqdn)
            #updating the subarray_health_state_map with device name (as ska_mid/tm_subarray_node/1) and its value which is required in callback
            self.subarray_health_state_map[subarray_fqdn] = -1
            try:
                event_id = subarray_client.subscribe_attribute(const.EVT_SUBSR_HEALTH_STATE,
                                            self.health_state_cb)
                self.health_state_event_map[subarray_client] = event_id
            except DevFailed as dev_failed:
                log_msg = const.ERR_SUBSR_SA_HEALTH_STATE + str(dev_failed)
                self.logger.exception(dev_failed)
                self._read_activity_message = const.ERR_SUBSR_SA_HEALTH_STATE
                tango.Except.throw_exception(const.STR_CMD_FAILED, log_msg, "CentralNode.HealthStateSubscribeEvent",
                                        tango.ErrSeverity.ERR)

    def unsubscribe_event(self):
        """
        Method to unsubscribe to health state change event on CspMasterLeafNode, SdpMasterLeafNode and SubarrayNode
        """
        for tango_client in self.health_state_event_map:
            log_message = "Unsubscribing ObsState of: {}".format(tango_client.get_device_fqdn)
            self.logger.debug(log_message)
            tango_client.unsubscribe_attribute(self.health_state_event_map[tango_client])
        self.health_state_event_map.clear()


    def health_state_cb(self, evt):
        """
        Retrieves the subscribed Subarray health state, aggregates them to calculate the
        telescope health state.

        :param evt: A TANGO_CHANGE event on Subarray healthState.

        :return: None

        :raises: KeyError if error occurs while setting Subarray healthState
        """
        device_data = DeviceData.get_instance()
        try:
            self._read_activity_message = "Within health callback"
            self.logger.info(self._read_activity_message)
            log_msg = 'Health state attribute change event is : ' + str(evt.attr_name)

            self.logger.info(log_msg)
            log_msg = 'Health state attribute change event is .....................: ' + str(evt.attr_value.value)

            self.logger.info(log_msg)
            if not evt.err:
                health_state = evt.attr_value.value
                log_msg = 'Health state is: ' + str(health_state)
                self.logger.info(log_msg)
                if const.PROP_DEF_VAL_TM_MID_SA1 in evt.attr_name:
                    device_data._subarray1_health_state = health_state
                    self.subarray_health_state_map[evt.attr_name] = health_state
                elif const.PROP_DEF_VAL_TM_MID_SA2 in evt.attr_name:
                    device_data._subarray2_health_state = health_state
                    self.subarray_health_state_map[evt.attr_name] = health_state
                elif const.PROP_DEF_VAL_TM_MID_SA3 in evt.attr_name:
                    device_data._subarray3_health_state = health_state
                    self.subarray_health_state_map[evt.attr_name] = health_state
                elif self.csp_master_ln_fqdn in evt.attr_name:
                    log_msg = 'Health state msg in CSP Master....: ' + str(evt.attr_name)
                    self.logger.info(log_msg)
                    device_data._csp_master_leaf_health = evt.attr_value.value
                    log_msg = 'CSP Master health is....: ' + str(device_data._csp_master_leaf_health)
                    self.logger.info(log_msg)
                elif self.sdp_master_ln_fqdn in evt.attr_name:
                    device_data._sdp_master_leaf_health = health_state
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
                    log_msg = 'inside first for loop...: ' + str(subsystem_health_field_name)
                    self.logger.info(log_msg)
    
                    health_state = getattr(device_data, f"_{subsystem_health_field_name}")
                    counts[health_state] += 1
                    log_msg = 'Conunt is .......: ' + str(counts[health_state])
                    self.logger.info(log_msg)
    

                for subarray_health_state in list(self.subarray_health_state_map.values()):
                    counts[subarray_health_state] += 1

                # Calculating health_state for SubarrayNode, CspMasterLeafNode, SdpMasterLeafNode
                if counts[HealthState.OK] == len(list(self.subarray_health_state_map.values())) + 2:
                    device_data._telescope_health_state = HealthState.OK
                    str_log = const.STR_HEALTH_STATE + str(evt.device) + const.STR_OK
                    self.logger.info(str_log)
                    log_msg = const.STR_HEALTH_STATE + str(evt.device) + const.STR_OK
                    self._read_activity_message = log_msg
                    self.logger.info(log_msg)
                elif counts[HealthState.FAILED] != 0:
                    device_data._telescope_health_state = HealthState.FAILED
                    str_log = const.STR_HEALTH_STATE + str(evt.device) + const.STR_FAILED
                    self.logger.info(str_log)
                    log_msg = const.STR_HEALTH_STATE + str(evt.device) + const.STR_FAILED
                    self._read_activity_message = log_msg
                    self.logger.info(log_msg)
                elif counts[HealthState.DEGRADED] != 0:
                    device_data._telescope_health_state = HealthState.DEGRADED
                    str_log = const.STR_HEALTH_STATE + str(evt.device) + const.STR_DEGRADED
                    self.logger.info(str_log)
                    log_msg = const.STR_HEALTH_STATE + str(evt.device) + const.STR_DEGRADED
                    self._read_activity_message = log_msg
                    self.logger.info(log_msg)
                else:
                    device_data._telescope_health_state = HealthState.UNKNOWN
                    str_log = const.STR_HEALTH_STATE + str(evt.device) + const.STR_UNKNOWN
                    self.logger.info(str_log)
                    log_msg = const.STR_HEALTH_STATE + str(evt.device) + const.STR_UNKNOWN
                    self._read_activity_message = log_msg
                    self.logger.info(log_msg)
            else:
                # TODO: For future reference
                self._read_activity_message = const.ERR_SUBSR_SA_HEALTH_STATE + str(evt)
                log_msg = self._read_activity_message
                self.logger.info(log_msg)
                self.logger.critical(const.ERR_SUBSR_SA_HEALTH_STATE)
        except KeyError as key_error:
            # TODO: For future reference
            self._read_activity_message = const.ERR_SUBARRAY_HEALTHSTATE + str(key_error)
            log_msg = const.ERR_SUBARRAY_HEALTHSTATE + ": " + str(key_error)
            self.logger.critical(log_msg)
