
# Tango imports
import tango
from tango import DevFailed

# Additional import
from . import const

from tmc.common.tango_group_client import TangoGroupClient
from tmc.common.tango_client import TangoClient
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
            device_data._dish_leaf_node_group_client.remove_all_device()
            log_message = const.STR_GRP_DEF
            self.logger.debug(log_message)
            device_data._read_activity_message = log_message
            self.logger.info(const.RECEPTORS_REMOVE_SUCCESS)
        except DevFailed as dev_failed:
            log_message = "Failed to remove receptors from the group. {}".format(dev_failed)
            self.logger.error(log_message)
            device_data._read_activity_message = log_message
            return

        device_data.health_state_aggr.unsubscribe_dish_health_state()
        device_data.obs_state_aggr.unsubscribe_dish_pointing_state()

        # clearing dictonaries and lists
        device_data._dishLnVsHealthEventID.clear()  # Clear eventID dictionary
        device_data._dishLnVsPointingStateEventID.clear()  # Clear eventID dictionary
        self.logger.info(const.STR_RECEPTORS_REMOVE_SUCCESS)


    def _remove_subarray_dish_lns_health_states(self):
        subarray_ln_health_state_map_copy = self.subarray_ln_health_state_map.copy()
        for dev_name in subarray_ln_health_state_map_copy:
            if dev_name.startswith(const.PROP_DEF_VAL_LEAF_NODE_PREFIX):
                _ = self.subarray_ln_health_state_map.pop(dev_name)
