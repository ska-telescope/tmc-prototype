# -*- coding: utf-8 -*-
#
# This file is part of the DishLeafNode project
#
#
#
# Distributed under the terms of the BSD-3-Clause license.
# See LICENSE.txt for more info.


"""
SetOperateMode class for DishLeafNode.
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


class SetOperateMode(BaseCommand):
    """
    A class for DishLeafNode's SetOperateMode() command.

    Invokes SetOperateMode command on DishMaster.
    """

    def do(self):
        """
        Method to invoke SetOperateMode command on DishMaster.

        param argin:
            None

        return:
            None

        raises:
            DevFailed If error occurs while invoking SetOperateMode command on DishMaster.

        """
        cmd_ended_cb = CommandCallBack(self.logger).cmd_ended_cb

        attributes_to_subscribe_to = (
            "dishMode",
            "capturing",
            "achievedPointing",
            "desiredPointing",
        )
        command_name = "SetOperateMode"
        cmd_ended_cb = CommandCallBack(self.logger).cmd_ended_cb
        try:
            self.this_server = TangoServerHelper.get_instance()

            self.dish_master_fqdn = ""
            property_value = self.this_server.read_property("DishMasterFQDN")
            self.dish_master_fqdn = self.dish_master_fqdn.join(property_value)
            dish_client = TangoClient(self.dish_master_fqdn)
            # Subscribe the DishMaster attributes
            self._subscribe_to_attribute_events(attributes_to_subscribe_to, dish_client)
            dish_client.send_command_async(command_name, callback_method=cmd_ended_cb)
            self.logger.info("'%s' command executed successfully.", command_name)

        except DevFailed as dev_failed:
            self.logger.exception(dev_failed)
            log_message = (
                f"Exception occured while executing the '{command_name}' command."
            )
            self.this_server.write_attr("activityMessage", log_message, False)
            tango.Except.re_throw_exception(
                dev_failed,
                f"Exception in '{command_name}' command.",
                log_message,
                f"DishLeafNode.{command_name}Command",
                tango.ErrSeverity.ERR,
            )

    def _subscribe_to_attribute_events(self, attributes, dish_client):
        device_data = DeviceData.get_instance()
        device_data.attr_event_map["dish_client"] = dish_client
        for attribute_name in attributes:
            try:
                device_data.attr_event_map[
                    attribute_name
                ] = dish_client.subscribe_attribute(
                    attribute_name, self.attribute_event_handler
                )
            except DevFailed as dev_failed:
                self.logger.exception(dev_failed)
                log_message = f"Exception occurred while subscribing to Dish attribute: {attribute_name}"
                self.this_server.write_attr("activityMessage", log_message, False)
                tango.Except.re_throw_exception(
                    dev_failed,
                    "Exception in Init command",
                    log_message,
                    "DishLeafNode.{}Command".format("Init"),
                    tango.ErrSeverity.ERR,
                )

    def attribute_event_handler(self, event_data):
        """
        Retrieves the subscribed attribute of DishMaster.

        :param evt: A TANGO_CHANGE event on attribute.
        """
        if event_data.err:
            log_message = (
                f"Event system DevError(s) occured!!! {str(event_data.errors)}"
            )
            self.this_server.write_attr("activityMessage", log_message, False)
            self.logger.error(log_message)
            return

        fqdn_attr_name = event_data.attr_name
        # tango://monctl.devk4.camlab.kat.ac.za:4000/mid_dish_0000/elt/
        # master/<attribute_name>#dbase=no
        # We process the FQDN of the attribute to extract just the
        # attribute name. Also handle the issue with the attribute name being
        # converted to lowercase in subsequent callbacks.
        attr_name = fqdn_attr_name.split("/")[-1].split("#")[0]
        log_message = f"{attr_name} is {event_data.attr_value.value}."
        self.this_server.write_attr("activityMessage", log_message, False)
        self.logger.info(log_message)