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
        mccs_subarray_ln_fqdn = ""
        property_val = self.this_server.read_property("MccsSubarrayLNFQDN")
        mccs_subarray_ln_fqdn = mccs_subarray_ln_fqdn.join(property_val)
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

        :param evt: A event on MCCS Subarray assigned_resources attribute.

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
        log_msg = "Event on assigned_resources attribute is: " + str(event)
        self.logger.debug(log_msg)
        if not event.err:
            event_assigned_resources = event.attr_value.value
            self.update_assigned_resources_attribute(event_assigned_resources)
            self.logger.info("assigned_resources attribute subscribed successfully.")
            log_msg = "MccsSubarray.assigned_resources attribute value is: " + str(event_assigned_resources)
            self.logger.info(log_msg)
        else:
            log_message = f"{const.ERR_SUBSR_MCCSSA_ASSIGNED_RES_ATTR}{device_name}{event}"
            self.logger.info(log_message)
            self.this_server.write_attr("activityMessage", log_message, False)

    def update_assigned_resources_attribute(self, mccs_assigned_resources):
        """
        This method modifies assigned_resources value coming from MCCS Subarray and assignes to
         SubarrayNode.assigned_resources attribute.
        """
        json_argument = json.loads(mccs_assigned_resources)
        interface_value = json_argument.pop("interface")
        assigned_resources_dict = {"interface": interface_value, "mccs": json_argument}
        assigned_resources_attr_value = json.dumps(assigned_resources_dict)
        self.this_server.write_attr("assigned_resources", assigned_resources_attr_value, False)
        log_msg = "assigned_resources attribute value is: " + str(assigned_resources_attr_value)
        self.logger.info(log_msg)

    def unsubscribe(self):
        """
        This function unsubscribes MccsSubarray.assigned_resources attribute.

        :param : None

        :return: None
        """
        for tango_client, event_id in self.mccs_ln_asigned_res_event_id.items():
            tango_client.unsubscribe_attribute(event_id)
