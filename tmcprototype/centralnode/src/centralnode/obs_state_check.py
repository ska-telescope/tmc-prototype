"""
ObsStateCheck class for CentralNode.
"""
# PROTECTED REGION ID(CentralNode.additionnal_import) ENABLED START #
from tango import DevFailed
# Additional import
from ska.base.control_model import ObsState
from . import const
from centralnode.tango_client import TangoClient
from centralnode.tango_server import TangoServerHelper
# PROTECTED REGION END #    //  CentralNode.additional_import

# TODO: this class is created separate from CentralNode class. Data from DeviceData class is required here.
# Need to finalise how the data can be accessed in this class.

class ObsStateCheck:
    """
    Observation state change event supscription and observation state
    callback.
    """
    def __init__(self):
        self._subarray_allocation = {}
        self.subarray_ln_fqdn_list= ["ska_mid/tm_subarray_node/1","ska_mid/tm_subarray_node/2","ska_mid/tm_subarray_node/3"]

    
    def subscribe_event(self):
        """
        Method for event subscription. Calls subscribe event methods for Subarray observation state attribute subscription.
        """
        self.unsubscribe_flag = False
        self.subarray_obs_state_subscribe_event() 

    def unsubscribe_event(self):
        """
        Method for event subscription. Calls separate unsubscribe event methods for Subarray observation state attribute unsubscription.
        """
        self.unsubscribe_flag=True
        self.subarray_obs_state_subscribe_event() 

    
    def subarray_obs_state_subscribe_event(self):
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


    def obs_state_cb(self, evt):
        """
        Retrieves the subscribed Subarray observation state. When the Subarray obsState is EMPTY, the resource
        allocation list gets cleared.

        :param evt: A TANGO_CHANGE event on Subarray obsState.

        :return: None

        :raises: KeyError in Subarray obsState callback
        """
        try:
            log_msg = 'Observation state attribute change event is : ' + str(evt)
            self.logger.info(log_msg)
            if not evt.err:
                obs_state = evt.attr_value.value
                subarray_device = evt.device
                subarray_device_list = list(str(subarray_device))
                # Identify the Subarray ID
                for index in range(0, len(subarray_device_list)):
                    if subarray_device_list[index].isdigit():
                        id = subarray_device_list[index]

                subarray_id = "SA" + str(id)
                self.logger.info(log_msg)
                if obs_state == ObsState.EMPTY or obs_state == ObsState.RESTARTING:
                    for dish, subarray in self._subarray_allocation.items():
                        if subarray == subarray_id:
                            self._subarray_allocation[dish] = "NOT_ALLOCATED"
                log_msg = "Subarray_allocation is: " + str(self._subarray_allocation)
                self.logger.info(log_msg)
            else:
                # TODO: For future reference
                self._read_activity_message = const.ERR_SUBSR_SA_OBS_STATE + str(evt)
                self.logger.critical(const.ERR_SUBSR_SA_OBS_STATE)
        except KeyError as key_error:
            self._read_activity_message = const.ERR_SUBARRAY_HEALTHSTATE + str(key_error)
            log_msg = const.ERR_SUBARRAY_HEALTHSTATE + ": " + str(key_error)
            self.logger.critical(log_msg)