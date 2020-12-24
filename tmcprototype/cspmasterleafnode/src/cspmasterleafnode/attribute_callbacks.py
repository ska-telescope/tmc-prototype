# Additional import
import tango
from tango import DeviceProxy, EventType, ApiUtil, DebugIt, DevState, AttrWriteType, DevFailed
from tango.server import run, command, device_property, attribute

from ska.base.control_model import HealthState
from .tango_server import TangoServer
from . import const, release, On, Off, StandBy, tango_client, device_data
from .device_data import DeviceData
from .tango_client import TangoClient
import logging
LOGGER = logging.getLogger(__name__)

class CbfHealthStateAttributeUpdator:
    """
     **Attributes:**

    - cspHealthState  - Forwarded attribute to provide CSP Master Health State
    - activityMessage - Attribute to provide activity message

    """
    def __init__(self, logger =None):
        if logger == None:
            self.logger = logging.getLogger(__name__)
        else:
            self.logger = logger
        
        self.device_data = DeviceData.get_instance()
        self.this_server = TangoServer.get_instance()
        self.event_id = None
        self.csp_master = None

    def start(self):
        try:
            print("Inide++++++++++++Start")
            self.csp_master = TangoClient(self.device_data.csp_master_ln_fqdn)
            self.event_id = self.csp_master.subscribe_attribute("cspCbfHealthState", self.csp_cbf_health_state_cb)
            # self.event_id = self.csp_master.subscribe_attribute("cspPssHealthState", self.csp_pss_health_state_cb)
            # self.event_id = self.csp_master.subscribe_attribute("cspPstHealthState", self.csp_pst_health_state_cb)
        except tango.DevFailed as df:
            self.logger.exception("Exception in attribute subscription")
    
    def stop(self):
        try:
            self.csp_master.unsubscribe_attr(self.event_id)
        except tango.DevFailed as df:
            self.logger.exception("Exception in unsubscribing the attribute.")

    # def callback(self, evt):
    #     log_msg = 'CspCbfHealthState attribute change event is : ' + str(evt)
    #     self.logger.debug(log_msg)
    #     if not evt.err:
    #         log_message = "CBF Health state: {}".format(evt.attr_value.value)
    #         self.device_data._csp_cbf_health = evt.attr_value.value
    #         self.logger.debug(log_message)
    #         self.device_data._read_activity_message = log_message
    #     else:
    #         log_msg = const.ERR_ON_SUBS_CSP_CBF_HEALTH + str(evt.errors)
    #         self.logger.error(log_msg)
    #         self.device_data._read_activity_message = log_msg
    #         self.logger.error(const.ERR_ON_SUBS_CSP_CBF_HEALTH)

    # def csp_pss_health_state_cb(self, evt):
    #     """
    #     Retrieves the subscribed cspPssHealthState attribute of CSPMaster.

    #     :param evt: A TANGO_CHANGE event on cspPssHealthState attribute.

    #     :return: None

    #     """
    #     log_msg = 'CspPssHealthState Attribute change event is : ' + str(evt)
    #     self.logger.info(log_msg)
    #     if not evt.err:
    #         self._csp_pss_health = evt.attr_value.value
    #         if self._csp_pss_health == HealthState.OK:
    #             self.logger.debug(const.STR_CSP_PSS_HEALTH_OK)
    #             self.device_data._read_activity_message = const.STR_CSP_PSS_HEALTH_OK
    #         elif self._csp_pss_health == HealthState.DEGRADED:
    #             self.logger.debug(const.STR_CSP_PSS_HEALTH_DEGRADED)
    #             self.device_data._read_activity_message = const.STR_CSP_PSS_HEALTH_DEGRADED
    #         elif self._csp_pss_health == HealthState.FAILED:
    #             self.logger.debug(const.STR_CSP_PSS_HEALTH_FAILED)
    #             self.device_data._read_activity_message = const.STR_CSP_PSS_HEALTH_FAILED
    #         else:
    #             self.logger.debug(const.STR_CSP_PSS_HEALTH_UNKNOWN)
    #             self.device_data._read_activity_message = const.STR_CSP_PSS_HEALTH_UNKNOWN
    #     else:
    #         log_msg = const.ERR_ON_SUBS_CSP_PSS_HEALTH + str(evt.errors)
    #         self.logger.error(log_msg)
    #         self.device_data._read_activity_message = log_msg

            
    def csp_cbf_health_state_cb(self, evt):
        """
        Retrieves the subscribed cspCbfHealthState attribute of CSPMaster.

        :param evt: A TANGO_CHANGE event on cspCbfHealthState attribute.

        :return: None

        """
        log_msg = 'CspCbfHealthState attribute change event is : ' + str(evt)
        self.logger.info(log_msg)
        print("INSIDE ++++++++++++++++++++++++++++Callback.")
        if not evt.err:
            self._csp_cbf_health = evt.attr_value.value
            if self._csp_cbf_health == HealthState.OK:
                self.logger.debug(const.STR_CSP_CBF_HEALTH_OK)
                self.device_data._read_activity_message = const.STR_CSP_CBF_HEALTH_OK
            elif self._csp_cbf_health == HealthState.DEGRADED:
                self.logger.debug(const.STR_CSP_CBF_HEALTH_DEGRADED)
                self.device_data._read_activity_message = const.STR_CSP_CBF_HEALTH_DEGRADED
            elif self._csp_cbf_health == HealthState.FAILED:
                self.logger.debug(const.STR_CSP_CBF_HEALTH_FAILED)
                self.device_data._read_activity_message = const.STR_CSP_CBF_HEALTH_FAILED
            else:
                self.logger.debug(const.STR_CSP_CBF_HEALTH_UNKNOWN)
                self.device_data._read_activity_message = const.STR_CSP_CBF_HEALTH_UNKNOWN
        else:
            log_msg = const.ERR_ON_SUBS_CSP_CBF_HEALTH + str(evt.errors)
            self.logger.error(log_msg)
            self.device_data._read_activity_message = log_msg
            self.logger.error(const.ERR_ON_SUBS_CSP_CBF_HEALTH)

    # def csp_pst_health_state_cb(self, evt):
    #     """
    #     Retrieves the subscribed cspPstHealthState attribute of CSPMaster.

    #     :param evt: A TANGO_CHANGE event on cspPstHealthState attribute.

    #     :return: None

    #     """
    #     log_msg = 'CspPstHealthState Attribute change event is : ' + str(evt)
    #     self.logger.info(log_msg)
    #     if not evt.err:
    #         self._csp_pst_health = evt.attr_value.value
    #         if self._csp_pst_health == HealthState.OK:
    #             self.logger.debug(const.STR_CSP_PST_HEALTH_OK)
    #             self.device_data._read_activity_message = const.STR_CSP_PST_HEALTH_OK
    #         elif self._csp_pst_health == HealthState.DEGRADED:
    #             self.logger.debug(const.STR_CSP_PST_HEALTH_DEGRADED)
    #             self.device_data._read_activity_message = const.STR_CSP_PST_HEALTH_DEGRADED
    #         elif self._csp_pst_health == HealthState.FAILED:
    #             self.logger.debug(const.STR_CSP_PST_HEALTH_FAILED)
    #             self.device_data._read_activity_message = const.STR_CSP_PST_HEALTH_FAILED
    #         else:
    #             self.logger.debug(const.STR_CSP_PST_HEALTH_UNKNOWN)
    #             self.device_data._read_activity_message = const.STR_CSP_PST_HEALTH_UNKNOWN
    #     else:
    #         log_msg = const.ERR_ON_SUBS_CSP_PST_HEALTH + str(evt.errors)
    #         self.logger.error(log_msg)
    #         self.device_data._read_activity_message = log_msg

