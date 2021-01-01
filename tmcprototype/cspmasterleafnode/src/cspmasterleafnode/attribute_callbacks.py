import tango
from ska.base.control_model import HealthState
from tmc.common.tango_server_helper import TangoServerHelper
from tmc.common.tango_client import TangoClient
from . import const
from .device_data import DeviceData
import logging

class CbfHealthStateAttributeUpdator:
    """
    - CbfHealthStateAttribute  - Forwarded attribute to provide CSP Master Health State
    - _csp_cbf_health_state_log - Variable to provide activity log

    """
    def __init__(self, logger =None):
        if logger == None:
            self.logger = logging.getLogger(__name__)
        else:
            self.logger = logger
        
        self.device_data = DeviceData.get_instance()
        self.this_server = TangoServerHelper.get_instance()
        self.event_id = None
        self.csp_master = TangoClient(self.device_data.csp_master_ln_fqdn)

    def start(self):
        try:
            self.event_id = self.csp_master.subscribe_attribute("cspCbfHealthState", self.csp_cbf_health_state_cb)
        except tango.DevFailed:
            self.logger.exception("Exception in attribute subscription")
    
    def stop(self):
        try:
            self.csp_master.unsubscribe_attribute(self.event_id)
        except tango.DevFailed:
            self.logger.exception("Exception in unsubscribing the attribute.")

                
    def csp_cbf_health_state_cb(self, evt):
        """
        Retrieves the subscribed cspCbfHealthState attribute of CSPMaster.

        :param evt: A TANGO_CHANGE event on cspCbfHealthState attribute.

        :return: None

        """
        log_msg = 'CspCbfHealthState attribute change event is : ' + str(evt)
        self.logger.info(log_msg)
        if not evt.err:
            self._csp_cbf_health = evt.attr_value.value
            if self._csp_cbf_health == HealthState.OK:
                self.logger.debug(const.STR_CSP_CBF_HEALTH_OK)
                self.device_data._csp_cbf_health_state_log = const.STR_CSP_CBF_HEALTH_OK
            elif self._csp_cbf_health == HealthState.DEGRADED:
                self.logger.debug(const.STR_CSP_CBF_HEALTH_DEGRADED)
                self.device_data._csp_cbf_health_state_log = const.STR_CSP_CBF_HEALTH_DEGRADED
            elif self._csp_cbf_health == HealthState.FAILED:
                self.logger.debug(const.STR_CSP_CBF_HEALTH_FAILED)
                self.device_data._csp_cbf_health_state_log = const.STR_CSP_CBF_HEALTH_FAILED
            else:
                self.logger.debug(const.STR_CSP_CBF_HEALTH_UNKNOWN)
                self.device_data._csp_cbf_health_state_log = const.STR_CSP_CBF_HEALTH_UNKNOWN
        else:
            self.device_data._csp_cbf_health_state_log = const.ERR_ON_SUBS_CSP_CBF_HEALTH + str(evt.errors)
            self.logger.error(const.ERR_ON_SUBS_CSP_CBF_HEALTH)
           

class PssHealthStateAttributeUpdator:
    """
    - PssHealthStateAttribute  - Forwarded attribute to provide CSP Master Health State
    - _csp_pss_health_state_log - Variable to provide activity log

    """
    def __init__(self, logger =None):
        if logger == None:
            self.logger = logging.getLogger(__name__)
        else:
            self.logger = logger
        
        self.device_data = DeviceData.get_instance()
        self.this_server = TangoServerHelper.get_instance()
        self.event_id = None
        self.csp_master = TangoClient(self.device_data.csp_master_ln_fqdn)

    def start(self):
        try:
            self.event_id = self.csp_master.subscribe_attribute("cspPssHealthState", self.csp_pss_health_state_cb)
        except tango.DevFailed:
            self.logger.exception("Exception in attribute subscription")
    
    def stop(self):
        try:
            self.csp_master.unsubscribe_attribute(self.event_id)
        except tango.DevFailed:
            self.logger.exception("Exception in unsubscribing the attribute.")

    def csp_pss_health_state_cb(self, evt):
        """
        Retrieves the subscribed cspPssHealthState attribute of CSPMaster.

        :param evt: A TANGO_CHANGE event on cspPssHealthState attribute.

        :return: None

        """
        log_msg = 'CspPssHealthState Attribute change event is : ' + str(evt)
        self.logger.info(log_msg)
        if not evt.err:
            self._csp_pss_health = evt.attr_value.value
            if self._csp_pss_health == HealthState.OK:
                self.logger.debug(const.STR_CSP_PSS_HEALTH_OK)
                self.device_data._csp_pss_health_state_log = const.STR_CSP_PSS_HEALTH_OK
            elif self._csp_pss_health == HealthState.DEGRADED:
                self.logger.debug(const.STR_CSP_PSS_HEALTH_DEGRADED)
                self.device_data._csp_pss_health_state_log = const.STR_CSP_PSS_HEALTH_DEGRADED
            elif self._csp_pss_health == HealthState.FAILED:
                self.logger.debug(const.STR_CSP_PSS_HEALTH_FAILED)
                self.device_data._csp_pss_health_state_log = const.STR_CSP_PSS_HEALTH_FAILED
            else:
                self.logger.debug(const.STR_CSP_PSS_HEALTH_UNKNOWN)
                self.device_data._csp_pss_health_state_log = const.STR_CSP_PSS_HEALTH_UNKNOWN
        else:
            self.device_data._csp_pss_health_state_log = const.ERR_ON_SUBS_CSP_PSS_HEALTH + str(evt.errors)
            self.logger.error(const.ERR_ON_SUBS_CSP_PSS_HEALTH)

class PstHealthStateAttributeUpdator:
    """
    - PstHealthStateAttribute  - Forwarded attribute to provide CSP Master Health State
    - _csp_pst_health_state_log - Variable to provide activity log

    """
    def __init__(self, logger =None):
        if logger == None:
            self.logger = logging.getLogger(__name__)
        else:
            self.logger = logger
        
        self.device_data = DeviceData.get_instance()
        self.this_server = TangoServerHelper.get_instance()
        self.event_id = None
        self.csp_master = TangoClient(self.device_data.csp_master_ln_fqdn)

    def start(self):
        try:
            self.event_id = self.csp_master.subscribe_attribute("cspPstHealthState", self.csp_pst_health_state_cb)
        except tango.DevFailed:
            self.logger.exception("Exception in attribute subscription")
    
    def stop(self):
        try:
            self.csp_master.unsubscribe_attribute(self.event_id)
        except tango.DevFailed:
            self.logger.exception("Exception in unsubscribing the attribute.")

    def csp_pst_health_state_cb(self, evt):
        """
        Retrieves the subscribed cspPstHealthState attribute of CSPMaster.

        :param evt: A TANGO_CHANGE event on cspPstHealthState attribute.

        :return: None

        """
        log_msg = 'CspPstHealthState Attribute change event is : ' + str(evt)
        self.logger.info(log_msg)
        if not evt.err:
            self._csp_pst_health = evt.attr_value.value
            if self._csp_pst_health == HealthState.OK:
                self.logger.debug(const.STR_CSP_PST_HEALTH_OK)
                self.device_data._csp_pst_health_state_log = const.STR_CSP_PST_HEALTH_OK
            elif self._csp_pst_health == HealthState.DEGRADED:
                self.logger.debug(const.STR_CSP_PST_HEALTH_DEGRADED)
                self.device_data._csp_pst_health_state_log = const.STR_CSP_PST_HEALTH_DEGRADED
            elif self._csp_pst_health == HealthState.FAILED:
                self.logger.debug(const.STR_CSP_PST_HEALTH_FAILED)
                self.device_data._csp_pst_health_state_log = const.STR_CSP_PST_HEALTH_FAILED
            else:
                self.logger.debug(const.STR_CSP_PST_HEALTH_UNKNOWN)
                self.device_data._csp_pst_health_state_log = const.STR_CSP_PST_HEALTH_UNKNOWN
        else:
            self.device_data._csp_pst_health_state_log = const.ERR_ON_SUBS_CSP_PST_HEALTH + str(evt.errors)
            self.logger.error(const.ERR_ON_SUBS_CSP_PST_HEALTH)

