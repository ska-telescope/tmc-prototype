# Standard Python imports
import logging
import json
# Additional import
from tmc.common.tango_client import TangoClient
from tmc.common.tango_server_helper import TangoServerHelper

from .device_data import DeviceData
from . import const


class AssignedResourcesMaintainer:
    """
    Assigned Resources Maintainer class for tmc Low.
    """

    def __init__(self, logger=None):
        if logger == None:
            self.logger = logging.getLogger(__name__)
        else:
            self.logger = logger

        self.mccs_ln_asigned_res_event_id = {}
        self.this_server = TangoServerHelper.get_instance()
        self.device_data = DeviceData.get_instance()
        mccs_subarray_ln_fqdn = self.this_server.read_property("MccsSubarrayLNFQDN")[0]
        self.mccs_client = TangoClient(mccs_subarray_ln_fqdn)

    def subscribe(self):
        # Subscribe assignedResources (forwarded attribute) of MccsSubarrayLeafNode
        mccs_event_id = self.mccs_client.subscribe_attribute(
            const.EVT_MCCSSA_ASSIGNED_RESOURCES, self.assigned_resources_cb
        )
        self.mccs_ln_asigned_res_event_id[self.mccs_client] = mccs_event_id
        log_msg = f"{const.STR_SUB_ATTR_MCCS_SALN_ASSIGNED_RESOURCES_SUCCESS}" \
                  f"{self.mccs_ln_asigned_res_event_id}"
        self.logger.debug(log_msg)
        self.logger.info(const.STR_SUB_ATTR_MCCS_SALN_ASSIGNED_RESOURCES_SUCCESS)

    def assigned_resources_cb(self, event):
        """
        Receives the subscribed assigned_resources attribute value.

        :param evt: Tango event on MCCS Subarray assigned_resources attribute.

        :type: Event object
            It has the following members:

                - date (event timestamp) 

                - reception_date (event reception timestamp)

                - type (event type)

                - dev_name (device name)

                - name (attribute name)

                - value (event value)

        :return: None
        """
        device_name = event.device.dev_name()
        log_msg = "Event on assigned_resources attribute is: {}".format(str(event))
        self.logger.debug(log_msg)
        if not event.err:
            self.device_data.assignd_resources_by_mccs = event.attr_value.value
            self.update_assigned_resources_attribute(self.device_data.assignd_resources_by_mccs)
            self.logger.info(const.STR_SUB_ATTR_MCCS_SALN_ASSIGNED_RESOURCES_SUCCESS)
            log_msg = "MccsSubarray.assigned_resources attribute value is: {}".format(
                      str(self.device_data.assignd_resources_by_mccs))
            self.logger.info(log_msg)
        else:
            log_message = f"{const.ERR_SUBSR_MCCSSA_ASSIGNED_RES_ATTR}{device_name}{event}"
            self.logger.info(log_message)
            self.this_server.write_attr("activityMessage", log_message, False)

    def update_assigned_resources_attribute(self, mccs_assigned_resources):
        """
        This method updates the SubarrayNode.assigned_resources attribute.
        """
        json_argument = json.loads(mccs_assigned_resources)
        del json_argument["interface"]
        json_argument["interface"] = "https://schema.skatelescope.org/ska-low-tmc-assignedresources/1.0"
        self.this_server.write_attr("assigned_resources", json.dumps(json_argument))
        log_msg = "assigned_resources attribute value is: {}".format(str(json.dumps(json_argument)))
        self.logger.info(log_msg)

    def unsubscribe(self):
        """
        This function unsubscribes MccsSubarray.assigned_resources attribute.

        :param : None

        :return: None
        """
        for tango_client, event_id in self.mccs_ln_asigned_res_event_id.items():
            tango_client.unsubscribe_attribute(event_id)
