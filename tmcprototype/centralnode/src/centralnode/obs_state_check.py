"""
ObsStateCheck class for CentralNode.
"""
# PROTECTED REGION ID(CentralNode.additionnal_import) ENABLED START #
import tango
# Additional import
from ska.base.control_model import ObsState
from . import const
from tmc.common.tango_client import TangoClient
import logging
# PROTECTED REGION END #    //  CentralNode.additional_import

# TODO: this class is created separate from CentralNode class. Data from DeviceData class is required here.
class ObsStateAggregator:
    """
    Class to perform aggregation of health state of the telescope
    """
    def __init__(self, subarray_fqdn_list, logger = None):
        if logger == None:
            self.logger = logging.getLogger(__name__)
        else:
            self.logger = logger

        self.subarray_fqdn_list = subarray_fqdn_list
        self.event_subscription_map = {}

    def start_aggregation(self):
        """
        Method to start ObsState aggregation
        """
        try:
            for subarray_fqdn in self.subarray_fqdn_list:
                log_message = "Subscribing ObsState of: {}".format(subarray_fqdn)
                self.logger.debug(log_message)
                tango_client = TangoClient(subarray_fqdn)
                event_id = tango_client.subscribe_attribute(const.EVT_SUBSR_HEALTH_STATE,
                    self.obs_state_callback)
                self.event_subscription_map[tango_client] = event_id
        except tango.DevFailed:
            self.logger.exception("Error in aggregation.")

    def stop_aggregation(self):
        """
        Method to stop ObsState aggregation
        """
        for tango_client in self.event_subscription_map:
            log_message = "Unsubscribing ObsState of: {}".format(tango_client.get_device_fqdn)
            self.logger.debug(log_message)
            tango_client.unsubscribe_attribute(self.event_subscription_map[tango_client])
        self.event_subscription_map.clear()

    def obs_state_callback(self, evt):
        """
        Retrieves the subscribed Subarray observation state. 
        When the Subarray obsState is EMPTY, the resource
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
                    device_data.resource_manager.update_resource_deallocation(subarray_id)
                    # for dish, subarray in self._subarray_allocation.items():
                    #     if subarray == subarray_id:
                    #         self._subarray_allocation[dish] = "NOT_ALLOCATED"
            else:
                # TODO: For future reference
                self._read_activity_message = const.ERR_SUBSR_SA_OBS_STATE + str(evt)
                self.logger.critical(const.ERR_SUBSR_SA_OBS_STATE)
        except KeyError as key_error:
            self._read_activity_message = const.ERR_SUBARRAY_HEALTHSTATE + str(key_error)
            log_msg = const.ERR_SUBARRAY_HEALTHSTATE + ": " + str(key_error)
            self.logger.critical(log_msg)