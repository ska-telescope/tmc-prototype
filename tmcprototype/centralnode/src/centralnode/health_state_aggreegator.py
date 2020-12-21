"""
health_state_aggreegator class for CentralNode.
"""
# PROTECTED REGION ID(CentralNode.additionnal_import) ENABLED START #
from tango import DevFailed
# Additional import
from ska.base.control_model import HealthState
from . import const
from centralnode.tango_client import TangoClient
from centralnode.tango_server import TangoServerHelper
# PROTECTED REGION END #    //  CentralNode.additional_import

class HealthStateAggreegator:
    """
    Aggrergator class for health state event supscription and health state
    callback.
    """
    def __init__(self):
        self.subarray_ln_health_state_map = {}
        self.csp_sdp_ln_health_event_id = {}
        self.this_server = TangoServerHelper.get_instance()
        # How to pass fqdn here? 
        self.csp_master_ln_fqdn = TangoClient("ska_mid/tm_leaf_node/csp_master")
        self.sdp_master_ln_fqdn = TangoClient("ska_mid/tm_leaf_node/sdp_master")
        self.subarray_ln_fqdn_list= ["ska_mid/tm_subarray_node/1","ska_mid/tm_subarray_node/2","ska_mid/tm_subarray_node/3"]
        self.sdp_event_id = ""
        self.csp_event_id = ""
        self.subarray_event_id_list = []
        self.subarray_health_state_map = {}
        self._subarray1_health_state = None
        self._subarray2_health_state = None
        self._subarray3_health_state = None
        self._telescope_health_state = None
        self.unsubscribe_flag = False


    def subscribe_event(self):
        """
        Method for event subscription. Calls separate subscribe event methods for CSP Master, SDP Master and
        Subarray health state attribute subscription.
        """
        self.unsubscribe_flag = False
        self.csp_health_subscribe_event()
        self.sdp_health_subscribe_event()
        self.subarray_health_subscribe_event() 

    def unsubscribe_event(self):
        """
        Method for event subscription. Calls separate subscribe event methods for CSP Master, SDP Master and
        Subarray health state attribute subscription.
        """
        self.unsubscribe_flag=True
        self.csp_health_subscribe_event()
        self.sdp_health_subscribe_event()
        self.subarray_health_subscribe_event() 

    
    def csp_health_subscribe_event(self):
        """
        Method for event subscription on CspMasterLeafNode.

        :raises: Devfailed exception if erroe occures while subscribing event.
        """
        self.logger.info(type(self.target))
        # device_data = DeviceData.get_instance()
        csp_mln_client = TangoClient(self.csp_master_ln_fqdn)
        if not self.unsubscribe_flag:
            try:
                self.csp_event_id = csp_mln_client.subscribe_attribute(const.EVT_SUBSR_CSP_MASTER_HEALTH,
                                                                        self.health_state_cb)
            except DevFailed as dev_failed:
                log_msg = const.ERR_SUBSR_CSP_MASTER_LEAF_HEALTH + str(dev_failed)
                self.logger.exception(dev_failed)
                self._read_activity_message = const.ERR_SUBSR_CSP_MASTER_LEAF_HEALTH
                tango.Except.throw_exception(const.STR_CMD_FAILED, log_msg, "CentralNode.HealthStateSubscribeEvent",
                                            tango.ErrSeverity.ERR)
        else:
            csp_mln_client.unsubscribe_attribute(self.csp_event_id)


    def sdp_health_subscribe_event(self):
        """
        Method for event subscription on SdpMasterLeafNode.

        :raises: Devfailed exception if erroe occures while subscribing event.
        """
        sdp_mln_client = TangoClient(self.sdp_master_ln_fqdn)
        if not self.unsubscribe_flag:
            try:
                self.sdp_event_id = sdp_mln_client.subscribe_attribute(const.EVT_SUBSR_SDP_MASTER_HEALTH,
                                                                        self.health_state_cb)
            except DevFailed as dev_failed:
                log_msg = const.ERR_SUBSR_SDP_MASTER_LEAF_HEALTH + str(dev_failed)
                self.logger.exception(dev_failed)
                self._read_activity_message = const.ERR_SUBSR_SDP_MASTER_LEAF_HEALTH
                tango.Except.throw_exception(const.STR_CMD_FAILED, log_msg, "CentralNode.HealthStateSubscribeEvent",
                                            tango.ErrSeverity.ERR)
        else:
            sdp_mln_client.unsubscribe_attribute(self.sdp_event_id)

    def subarray_health_subscribe_event(self):
        """
        Method for event subscription on SubarrayNode.

        :raises: Devfailed exception if erroe occures while subscribing event.
        """
        for subarrayID in range(1, len(self.subarray_ln_fqdn_list) + 1):
            subarray_client = TangoClient(subarrayID)
            #updating the subarray_health_state_map with device name (as ska_mid/tm_subarray_node/1) and its value which is required in callback
            self.subarray_health_state_map[self.subarray_ln_fqdn_list(subarrayID-1)] = -1
            if not self.unsubscribe_flag:
                try:
                    event_id = subarray_client.subscribe_attribute(const.EVT_SUBSR_HEALTH_STATE,
                                            self.health_state_cb)
                    self.subarray_event_id_list.append[event_id]
                except DevFailed as dev_failed:
                    log_msg = const.ERR_SUBSR_SA_HEALTH_STATE + str(dev_failed)
                    self.logger.exception(dev_failed)
                    self._read_activity_message = const.ERR_SUBSR_SA_HEALTH_STATE
                    tango.Except.throw_exception(const.STR_CMD_FAILED, log_msg, "CentralNode.HealthStateSubscribeEvent",
                                            tango.ErrSeverity.ERR)
            else:
                subarray_client.unsubscribe_attribute(self.subarray_event_id_list[subarrayID-1])

    def health_state_cb(self, evt):
        """
        Retrieves the subscribed Subarray health state, aggregates them to calculate the
        telescope health state.

        :param evt: A TANGO_CHANGE event on Subarray healthState.

        :return: None

        :raises: KeyError if error occurs while setting Subarray healthState
        """
        # device_data = self.target
        try:
            log_msg = 'Health state attribute change event is : ' + str(evt)
            self.logger.info(log_msg)
            if not evt.err:
                health_state = evt.attr_value.value
                if const.PROP_DEF_VAL_TM_MID_SA1 in evt.attr_name:
                    self._subarray1_health_state = health_state
                    self.subarray_health_state_map[evt.attr_name] = health_state
                elif const.PROP_DEF_VAL_TM_MID_SA2 in evt.attr_name:
                    self._subarray2_health_state = health_state
                    self.subarray_health_state_map[evt.attr_name] = health_state
                elif const.PROP_DEF_VAL_TM_MID_SA3 in evt.attr_name:
                    self._subarray3_health_state = health_state
                    self.subarray_health_state_map[evt.attr_name] = health_state
                elif self.csp_master_ln_fqdn in evt.attr_name:
                    self._csp_master_leaf_health = health_state
                elif self.sdp_master_ln_fqdn in evt.attr_name:
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
                    log_msg = const.STR_HEALTH_STATE + str(evt.device) + const.STR_OK
                    self._read_activity_message = log_msg
                    self.logger.info(log_msg)
                elif counts[HealthState.FAILED] != 0:
                    self._telescope_health_state = HealthState.FAILED
                    str_log = const.STR_HEALTH_STATE + str(evt.device) + const.STR_FAILED
                    self.logger.info(str_log)
                    log_msg = const.STR_HEALTH_STATE + str(evt.device) + const.STR_FAILED
                    self._read_activity_message = log_msg
                    self.logger.info(log_msg)
                elif counts[HealthState.DEGRADED] != 0:
                    self._telescope_health_state = HealthState.DEGRADED
                    str_log = const.STR_HEALTH_STATE + str(evt.device) + const.STR_DEGRADED
                    self.logger.info(str_log)
                    log_msg = const.STR_HEALTH_STATE + str(evt.device) + const.STR_DEGRADED
                    self._read_activity_message = log_msg
                    self.logger.info(log_msg)
                else:
                    self._telescope_health_state = HealthState.UNKNOWN
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
