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

import tango
from tango import DevFailed

from ska.base.commands import  BaseCommand
from tmc.common.tango_client import TangoClient
from .command_callback import CommandCallBack
from .device_data import DeviceData


class SetStandbyLPMode(BaseCommand):
    """
    A class for DishLeafNode's SetStandbyLPMode() command.
    """

    def do(self):
        """
        Invokes SetStandbyLPMode (i.e. Low Power State) command on DishMaster.
        :param argin: None

        :return:None

        :raises DevFailed: If error occurs while invoking SetStandbyLPMode command on DishMaster.
        """
        device_data = self.target
        command_name = "SetStandbyLPMode"
        try:
            dish_client = TangoClient(device_data._dish_master_fqdn)
            cmd_ended_cb = CommandCallBack(self.logger).cmd_ended_cb
            # Unsubscribe the DishMaster attributes
            self._unsubscribe_attribute_events() 
            dish_client.send_command_async(command_name, callback_method=cmd_ended_cb)
            self.logger.info("'%s' command executed successfully.", command_name)
        except DevFailed as dev_failed:
            self.logger.exception(dev_failed)
            log_message = f"Exception occured while executing the '{command_name}' command."
            device_data._read_activity_message = log_message
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
        device_data = DeviceData.get_instance()
        dish_client = device_data.attr_event_map["dish_client"]
        device_data.attr_event_map.pop("dish_client")
        for attr_name in device_data.attr_event_map:
            log_message = "Unsubscribing attributes of: {}".format(dish_client.get_device_fqdn)
            self.logger.debug(log_message)
            dish_client.unsubscribe_attribute(device_data.attr_event_map[attr_name])
        device_data.attr_event_map.clear()
       
