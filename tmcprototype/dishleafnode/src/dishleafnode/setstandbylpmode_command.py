# -*- coding: utf-8 -*-
#
# This file is part of the DishLeafNode project
#
#
#
# Distributed under the terms of the BSD-3-Clause license.
# See LICENSE.txt for more info.


"""
SetStandbyLPMode class for DishLeafNode.
"""
# Tango import
import tango
from tango import DevFailed

# Additional import
from ska.base.commands import BaseCommand

from tmc.common.tango_client import TangoClient
from tmc.common.tango_server_helper import TangoServerHelper
from .command_callback import CommandCallBack
from .device_data import DeviceData


class SetStandbyLPMode(BaseCommand):
    """
    A class for DishLeafNode's SetStandbyLPMode() command.

    Invokes SetStandbyLPMode (i.e. Low Power State) command on DishMaster.

    """

    def do(self):
        """
        Method to invoke SetStandbyLPMode command on DishMaster.

        param argin:
            None

        return:
            None

        raises:
            DevFailed If error occurs while invoking SetStandbyLPMode command on DishMaster.

        """
        command_name = "SetStandbyLPMode"
        try:
            this_server = TangoServerHelper.get_instance()
            self.dish_master_fqdn = ""
            property_value = this_server.read_property("DishMasterFQDN")
            self.dish_master_fqdn = self.dish_master_fqdn.join(property_value)
            dish_client = TangoClient(self.dish_master_fqdn)
            cmd_ended_cb = CommandCallBack(self.logger).cmd_ended_cb
            dish_client.send_command_async(command_name, callback_method=cmd_ended_cb)
            # Unsubscribe the DishMaster attributes
            self._unsubscribe_attribute_events()
            self.logger.info("'%s' command executed successfully.", command_name)
        except DevFailed as dev_failed:
            self.logger.exception(dev_failed)
            log_message = (
                f"Exception occured while executing the '{command_name}' command."
            )
            # this_server.write_attr("activityMessage", log_message)
            tango.Except.re_throw_exception(
                dev_failed,
                f"Exception in '{command_name}' command.",
                log_message,
                f"DishLeafNode.{command_name}Command",
                tango.ErrSeverity.ERR,
            )

    def _unsubscribe_attribute_events(self):
        """
        Method to unsubscribe to health state change event on CspMasterLeafNode, SdpMasterLeafNode and SubarrayNode
        """
        try:
            device_data = DeviceData.get_instance()
            dish_client = device_data.attr_event_map["dish_client"]
            device_data.attr_event_map.pop("dish_client")
            for attr_name in device_data.attr_event_map:
                log_message = "Unsubscribing attributes of: {}".format(
                    dish_client.get_device_fqdn
                )
                self.logger.debug(log_message)
                dish_client.unsubscribe_attribute(device_data.attr_event_map[attr_name])
            device_data.attr_event_map.clear()
        except Exception as e:
            log_message = "Exception occured while unsubscribing attribute events command. {}".format(e)
            self.logger.exception(log_message)
            

