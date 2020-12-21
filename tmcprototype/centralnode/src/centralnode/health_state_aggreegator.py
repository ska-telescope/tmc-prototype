"""
health_state_aggreegator class for CentralNode.
"""
# PROTECTED REGION ID(CentralNode.additionnal_import) ENABLED START #
# Additional import
from ska.base.control_model import HealthState
from . import const
from centralnode.device_data import DeviceData
from centralnode.tango_client import TangoClient
# PROTECTED REGION END #    //  CentralNode.additional_import

class HealthStateAggreegator:
    """
    Aggrergator class for health state event supscription and health state
    callback.
    """
    def subscribe_event(self):
        """
        Method for event subscription. Calls separate subscribe event methods for CSP Master, SDP Master and
        Subarray health state attribute subscription.
        """
        device_data.unsubscribe_flag = False
        self.csp_health_subscribe_event()
        self.sdp_health_subscribe_event()
        self.subarray_health_subscribe_event() 

   def unsubscribe_event(self):
        """
        Method for event subscription. Calls separate subscribe event methods for CSP Master, SDP Master and
        Subarray health state attribute subscription.
        """
        device_data.unsubscribe_flag=True
        self.csp_health_subscribe_event()
        self.sdp_health_subscribe_event()
        self.subarray_health_subscribe_event() 

    
    def csp_health_subscribe_event(self):
        """
        Method for event subscription on CspMasterLeafNode.

        :raises: Devfailed exception if erroe occures while subscribing event.
        """
        self.logger.info(type(self.target))
        device_data = DeviceData.get_instance()
        csp_mln_client = TangoClient(device_data.csp_master_ln_fqdn)
        if not device_data.unsubscribe_flag:
            try:
                device_data.csp_event_id = csp_mln_client.subscribe_attribute(const.EVT_SUBSR_CSP_MASTER_HEALTH,
                                                                        self.health_state_cb)
            except DevFailed as dev_failed:
                log_msg = const.ERR_SUBSR_CSP_MASTER_LEAF_HEALTH + str(dev_failed)
                self.logger.exception(dev_failed)
                device_data._read_activity_message = const.ERR_SUBSR_CSP_MASTER_LEAF_HEALTH
                tango.Except.throw_exception(const.STR_CMD_FAILED, log_msg, "CentralNode.HealthStateSubscribeEvent",
                                            tango.ErrSeverity.ERR)
        else:
            csp_mln_client.unsubscribe_attr(device_data.csp_event_id)


    def sdp_health_subscribe_event(self):
        """
        Method for event subscription on SdpMasterLeafNode.

        :raises: Devfailed exception if erroe occures while subscribing event.
        """
        device_data = DeviceData.get_instance()
        sdp_mln_client = TangoClient(device_data.csp_master_ln_fqdn)
        if not device_data.unsubscribe_flag:
            try:
                device_data.sdp_event_id = sdp_mln_client.subscribe_attribute(const.EVT_SUBSR_SDP_MASTER_HEALTH,
                                                                        self.health_state_cb)
            except DevFailed as dev_failed:
                log_msg = const.ERR_SUBSR_SDP_MASTER_LEAF_HEALTH + str(dev_failed)
                self.logger.exception(dev_failed)
                device_data._read_activity_message = const.ERR_SUBSR_SDP_MASTER_LEAF_HEALTH
                tango.Except.throw_exception(const.STR_CMD_FAILED, log_msg, "CentralNode.HealthStateSubscribeEvent",
                                            tango.ErrSeverity.ERR)
        else:
            sdp_mln_client.unsubscribe_attr(device_data.sdp_event_id)

    def subarray_health_subscribe_event(self):
        """
        Method for event subscription on SubarrayNode.

        :raises: Devfailed exception if erroe occures while subscribing event.
        """
        for subarrayID in range(1, len(device_data.tm_mid_subarray) + 1):
            subarray_client = TangoClient(subarrayID)
            #updating the subarray_health_state_map with device name (as ska_mid/tm_subarray_node/1) and its value which is required in callback
            device_data.subarray_health_state_map[device_data.tm_mid_subarray(subarrayID-1)] = -1
            if not device_data.unsubscribe_flag:
                try:
                    event_id = subarray_client.subscribe_attribute(const.EVT_SUBSR_HEALTH_STATE,
                                            self.health_state_cb)
                    device_data.subarray_event_id_list.append[event_id]
                except DevFailed as dev_failed:
                    log_msg = const.ERR_SUBSR_SA_HEALTH_STATE + str(dev_failed)
                    self.logger.exception(dev_failed)
                    device_data._read_activity_message = const.ERR_SUBSR_SA_HEALTH_STATE
                    tango.Except.throw_exception(const.STR_CMD_FAILED, log_msg, "CentralNode.HealthStateSubscribeEvent",
                                            tango.ErrSeverity.ERR)
            else:
                subarray_client.unsubscribe_attr(device_data.subarray_event_id_list[subarrayID-1])

    def health_state_cb(self, evt):
        """
        Retrieves the subscribed Subarray health state, aggregates them to calculate the
        telescope health state.

        :param evt: A TANGO_CHANGE event on Subarray healthState.

        :return: None

        :raises: KeyError if error occurs while setting Subarray healthState
        """
        device_data = self.target
        try:
            log_msg = 'Health state attribute change event is : ' + str(evt)
            self.logger.info(log_msg)
            if not evt.err:
                health_state = evt.attr_value.value
                if const.PROP_DEF_VAL_TM_MID_SA1 in evt.attr_name:
                    device_data._subarray1_health_state = health_state
                    device_data.subarray_health_state_map[evt.attr_name] = health_state
                elif const.PROP_DEF_VAL_TM_MID_SA2 in evt.attr_name:
                    device_data._subarray2_health_state = health_state
                    device_data.subarray_health_state_map[evt.attr_name] = health_state
                elif const.PROP_DEF_VAL_TM_MID_SA3 in evt.attr_name:
                    device_data._subarray3_health_state = health_state
                    device_data.subarray_health_state_map[evt.attr_name] = health_state
                elif device_data.CspMasterLeafNodeFQDN in evt.attr_name:
                    device_data._csp_master_leaf_health = health_state
                elif device_data.SdpMasterLeafNodeFQDN in evt.attr_name:
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
                    health_state = getattr(self, f"_{subsystem_health_field_name}")
                    counts[health_state] += 1

                for subarray_health_state in list(device_data.subarray_health_state_map.values()):
                    counts[subarray_health_state] += 1

                # Calculating health_state for SubarrayNode, CspMasterLeafNode, SdpMasterLeafNode
                if counts[HealthState.OK] == len(list(device_data.subarray_health_state_map.values())) + 2:
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
                # TODO: For future reference
                device_data._read_activity_message = const.ERR_SUBSR_SA_HEALTH_STATE + str(evt)
                self.logger.critical(const.ERR_SUBSR_SA_HEALTH_STATE)
        except KeyError as key_error:
            # TODO: For future reference
            device_data._read_activity_message = const.ERR_SUBARRAY_HEALTHSTATE + str(key_error)
            log_msg = const.ERR_SUBARRAY_HEALTHSTATE + ": " + str(key_error)
            self.logger.critical(log_msg)
