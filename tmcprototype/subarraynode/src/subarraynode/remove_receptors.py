
# Tango imports
import tango
from tango import DevFailed

# Additional import
from . import const

from subarraynode.tango_group_client import TangoGroupClient
from subarraynode.tango_client import TangoClient
from subarraynode.device_data import DeviceData
import logging

class RemoveReceptors:
    """
    Remove Receptors class
    """
    logger = logging.getLogger(__name__)
    def remove_receptors_from_group(self):
        """
        Deletes tango group of the resources allocated in the subarray.

        Note: Currently there are only receptors allocated so the group contains only receptor ids.

        :param argin:
            DevVoid
        :return:
            DevVoid
        """
        device_data = DeviceData.get_instance()
        if not device_data._dishLnVsHealthEventID or not device_data._dishLnVsPointingStateEventID:
            return
        try:
            # self._dish_leaf_node_group.remove_all()
            device_data._dish_leaf_node_group_client.remove_all_device()
            # log_message = const.STR_GRP_DEF + (device_data._dish_leaf_node_group.get_group_device_list(True))
            log_message = const.STR_GRP_DEF
            self.logger.debug(log_message)
            device_data._read_activity_message = log_message
            self.logger.info(const.RECEPTORS_REMOVE_SUCCESS)
        except DevFailed as dev_failed:
            log_message = "Failed to remove receptors from the group. {}".format(dev_failed)
            self.logger.error(log_message)
            device_data._read_activity_message = log_message
            return

        # self._unsubscribe_resource_events(self._dishLnVsHealthEventID)
        # self._unsubscribe_resource_events(self._dishLnVsPointingStateEventID)
        device_data.health_state_aggr.unsubscribe_dish_health_state()
        device_data.obs_state_aggr.unsubscribe_dish_pointing_state()

        # clearing dictonaries and lists
        device_data._dishLnVsHealthEventID.clear()  # Clear eventID dictionary
        device_data._dishLnVsPointingStateEventID.clear()  # Clear eventID dictionary
        # self._health_event_id.clear()
        # self._remove_subarray_dish_lns_health_states()
        # self.dishPointingStateMap.clear()
        # self._pointing_state_event_id.clear()
        # self._dish_leaf_node_proxy.clear()
        # self._receptor_id_list.clear()
        self.logger.info(const.STR_RECEPTORS_REMOVE_SUCCESS)


    # def _unsubscribe_resource_events(self, proxy_event_id_map):
    #     """
    #     This function unsubscribes all events given by the event ids and their
    #     corresponding DeviceProxy objects.

    #     :param proxy_event_id_map: dict
    #         A mapping of '<DeviceProxy>': <event_id>.

    #     :return: None

    #     """
    #     for device_proxy, event_id in proxy_event_id_map.items():
    #         try:
    #             device_proxy.unsubscribe_event(event_id)
    #         except DevFailed as dev_failed:
    #             log_message = "Failed to unsubscribe event {}.".format(dev_failed)
    #             self.logger.error(log_message )
    #             device_data = DeviceData()
    #             device_data._read_activity_message = log_message

    # def _unsubscribe_csp_sdp_state_events(self, proxy_event_id_map):
    #     """
    #     This function unsubscribes all events given by the event ids and their
    #     corresponding DeviceProxy objects.

    #     :param
    #         device_proxy: Device Proxy
    #         proxy_event_id: <event_id>

    #     :return: None

    #     """
    #     for device_proxy, event_id in proxy_event_id_map.items():
    #         try:
    #             device_proxy.unsubscribe_event(event_id)
    #         except DevFailed as dev_failed:
    #             log_message = "Failed to unsubscribe health state event {}.".format(dev_failed)
    #             self.logger.error(log_message )
    #             device_data = DeviceData()
    #             device_data._read_activity_message = log_message
    #             device_data._read_activity_message = log_message

    def _remove_subarray_dish_lns_health_states(self):
        subarray_ln_health_state_map_copy = self.subarray_ln_health_state_map.copy()
        for dev_name in subarray_ln_health_state_map_copy:
            if dev_name.startswith(const.PROP_DEF_VAL_LEAF_NODE_PREFIX):
                _ = self.subarray_ln_health_state_map.pop(dev_name)
