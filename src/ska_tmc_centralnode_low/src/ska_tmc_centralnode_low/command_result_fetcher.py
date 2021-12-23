"""
cmd_res_subscriber_unsubscriber class
"""
import logging

# Tango imports
import tango
from tango import DevFailed
from tmc.common.tango_client import TangoClient
from tmc.common.tango_server_helper import TangoServerHelper

# Additional import
from . import const
from .device_data import DeviceData


class CommandResultFetcher:
    """A class for commandResult attribute subscription and unsubscription methods"""

    def __init__(self, logger=None):
        if logger == None:
            self.logger = logging.getLogger(__name__)

        self.this_server = TangoServerHelper.get_instance()

    def command_result_cb(self, event):
        """
        Attribute callback for commandResult.
        """
        device_data = DeviceData.get_instance()
        try:
            device_data.cmd_res_evt_val = event.attr_value.value
            log_msg = "commandResult attribute value is" + str(
                device_data.cmd_res_evt_val
            )
            self.logger.info(log_msg)
        except Exception as exp:
            self.logger.exception(const.ERR_SUB_CMD_RES_ATTR)
            self.logger.exception(exp)

    def _subscribe_cmd_res_attribute_events(self, attributes):
        """Method to subscribe the commandResult attributes"""
        device_data = DeviceData.get_instance()
        mccs_controller_client = TangoClient(device_data.mccs_controller_fqdn)
        device_data.attr_event_map[
            "mccs_controller_client"
        ] = mccs_controller_client

        for attribute_name in attributes:
            try:
                device_data.attr_event_map[
                    attribute_name
                ] = mccs_controller_client.subscribe_attribute(
                    attribute_name, self.command_result_cb
                )
            except DevFailed as dev_failed:
                self.logger.exception(dev_failed)
                log_message = f"Exception occurred while subscribing to mccs attribute: {attribute_name}"
                self.this_server.write_attr(
                    "activityMessage", log_message, False
                )
                tango.Except.re_throw_exception(
                    dev_failed,
                    "Exception in StartupTelescope command",
                    log_message,
                    "CentralNode.{}Command".format("StartUpTelescope"),
                    tango.ErrSeverity.ERR,
                )

    def _unsubscribe_cmd_res_attribute_events(self):
        """
        Method to unsubscribe to commandResult attribute event on MccsController
        """
        device_data = DeviceData.get_instance()
        mccs_controller_client = device_data.attr_event_map[
            "mccs_controller_client"
        ]
        device_data.attr_event_map.pop("mccs_controller_client")
        for attr_name in device_data.attr_event_map:
            log_message = "Unsubscribing attributes of: {}".format(
                mccs_controller_client.get_device_fqdn
            )
            self.logger.debug(log_message)
            mccs_controller_client.unsubscribe_attribute(
                device_data.attr_event_map[attr_name]
            )
        device_data.attr_event_map.clear()
