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
    def __init__(self, logger =None):
        if logger == None:
            self.logger = logging.getLogger(__name__)
        else:
            self.logger = logger
        
        self.device_data = DeviceData.get_instance()
        self.this_server = TangoServer.get_instance()
        self.event_id = None
        self.csp_master = None

    def start(self, attribute):
        try:
            self.csp_master = TangoClient(self.device_data.csp_master_ln_fqdn)
            self.event_id = self.csp_master.subscribe_attribute("cspCbfHealthState", callback)
        except tango.DevFailed as df:
            self.logger.exception("Exception in attribute subscription")
    
    def stop(self):
        try:
            self.csp_master.unsubscribe_attr(self.event_id)
        except tango.DevFailed as df:
            self.logger.exception("Exception in unsubscribing the attribute.")

    def callback(self, evt):
        log_msg = 'CspCbfHealthState attribute change event is : ' + str(evt)
        self.logger.debug(log_msg)
        if not evt.err:
            log_message = "CBF Health state: {}".format(evt.attr_value.value)
            self.device_data._csp_cbf_health = evt.attr_value.value
            self.logger.debug(log_message)
            self.device_data._read_activity_message = log_message
        else:
            log_msg = const.ERR_ON_SUBS_CSP_CBF_HEALTH + str(evt.errors)
            self.logger.error(log_msg)
            self.device_data._read_activity_message = log_msg
            self.logger.error(const.ERR_ON_SUBS_CSP_CBF_HEALTH)




class AttributeCallbacks:
    
    """
     **Attributes:**

    - cspHealthState  - Forwarded attribute to provide CSP Master Health State
    - activityMessage - Attribute to provide activity message

    """
    
    def __init__(self):
        self.device_data = DeviceData.get_instance()
        self.this_server = TangoServer.get_instance()
        # How to pass fqdn here? 
        # self.csp_master_fqdn = TangoClient("ska_mid/tm_leaf_node/csp_master")
        self.csp_event_id = ""
        self.unsubscribe_flag = False
        
    def subscribe_event(self):
        """
        Method for event subscription. Calls separate subscribe event methods for CSP Master, SDP Master and
        Subarray health state attribute subscription.
        """
        self.unsubscribe_flag = False
        self.csp_subscribe_event()


    def unsubscribe_event(self):
        """
        Method for event subscription. Calls separate subscribe event methods for CSP Master, SDP Master and
        Subarray health state attribute subscription.
        """
        self.unsubscribe_flag=True
        self.csp_subscribe_event()
        

    def csp_subscribe_event(self):
        """
        Method for event subscription on CSP Master.

        :raises: Devfailed exception if error occures while subscribing event.
        """

        csp_mln_client = TangoClient(self.device_data.csp_master_ln_fqdn)
        if not self.unsubscribe_flag:
            # Subscribing to CSPMaster Attributes
            try:
                self.csp_event_id = csp_mln_client.subscribe_attribute(const.EVT_CBF_HEALTH, 
                                                                    self.csp_cbf_health_state_cb)
                self.csp_event_id = csp_mln_client.subscribe_attribute(const.EVT_PSS_HEALTH, 
                                                                    self.csp_pss_health_state_cb)
                self.csp_event_id = csp_mln_client.subscribe_attribute(const.EVT_PST_HEALTH, 
                                                                    self.csp_pst_health_state_cb)

            except DevFailed as dev_failed:
                log_msg = const.ERR_SUBS_CSP_MASTER_LEAF_ATTR + str(dev_failed)
                self.logger.debug(log_msg)
                # device.set_status(const.ERR_CSP_MASTER_LEAF_INIT)
                device_data._read_activity_message = log_msg
                tango.Except.throw_exception(const.STR_CMD_FAILED, log_msg, "CspMasterLeafNode.InitCommand.do()",
                                                tango.ErrSeverity.ERR)

        else:
            csp_mln_client.unsubscribe_attr(self.csp_event_id)

        
    # PROTECTED REGION ID(CspMasterLeafNode.class_variable) ENABLED START #\
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
                self.device_data._read_activity_message = const.STR_CSP_PSS_HEALTH_OK
            elif self._csp_pss_health == HealthState.DEGRADED:
                self.logger.debug(const.STR_CSP_PSS_HEALTH_DEGRADED)
                self.device_data._read_activity_message = const.STR_CSP_PSS_HEALTH_DEGRADED
            elif self._csp_pss_health == HealthState.FAILED:
                self.logger.debug(const.STR_CSP_PSS_HEALTH_FAILED)
                self.device_data._read_activity_message = const.STR_CSP_PSS_HEALTH_FAILED
            else:
                self.logger.debug(const.STR_CSP_PSS_HEALTH_UNKNOWN)
                self.device_data._read_activity_message = const.STR_CSP_PSS_HEALTH_UNKNOWN
        else:
            log_msg = const.ERR_ON_SUBS_CSP_PSS_HEALTH + str(evt.errors)
            self.logger.error(log_msg)
            self.device_data._read_activity_message = log_msg


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
                self.device_data._read_activity_message = const.STR_CSP_PST_HEALTH_OK
            elif self._csp_pst_health == HealthState.DEGRADED:
                self.logger.debug(const.STR_CSP_PST_HEALTH_DEGRADED)
                self.device_data._read_activity_message = const.STR_CSP_PST_HEALTH_DEGRADED
            elif self._csp_pst_health == HealthState.FAILED:
                self.logger.debug(const.STR_CSP_PST_HEALTH_FAILED)
                self.device_data._read_activity_message = const.STR_CSP_PST_HEALTH_FAILED
            else:
                self.logger.debug(const.STR_CSP_PST_HEALTH_UNKNOWN)
                self.device_data._read_activity_message = const.STR_CSP_PST_HEALTH_UNKNOWN
        else:
            log_msg = const.ERR_ON_SUBS_CSP_PST_HEALTH + str(evt.errors)
            self.logger.error(log_msg)
            self.device_data._read_activity_message = log_msg

    # PROTECTED REGION END #    //  CspMasterLeafNode.class_variable

    