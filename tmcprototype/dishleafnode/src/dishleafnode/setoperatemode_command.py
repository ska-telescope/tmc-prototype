# -*- coding: utf-8 -*-
#
# This file is part of the DishLeafNode project
#
#
#
# Distributed under the terms of the BSD-3-Clause license.
# See LICENSE.txt for more info.

"""
A Leaf control node for DishMaster.
"""
import json
import importlib.resources
import math
import datetime
import time
import threading

import tango
from tango import DeviceProxy, EventType, ApiUtil, DevState, AttrWriteType, DevFailed
from tango.server import run, command, device_property, attribute
import katpoint

from ska.base.commands import ResultCode, BaseCommand
from ska.base import SKABaseDevice
from tmc.common.tango_client import TangoClient
from ska.base.control_model import HealthState, SimulationMode
from .utils import UnitConverter
from . import release
from .device_data import DeviceData
from .command_callback import CommandCallBack

class SetOperateMode(BaseCommand):
    """
    A class for DishLeafNode's SetOperateMode() command.
    """

    def do(self):
        """
        Invokes SetOperateMode command on DishMaster.

        :raises DevFailed: If error occurs while invoking SetOperateMode command on DishMaster.
        """
        device_data = self.target
        cmd_ended_cb = CommandCallBack(self.logger).cmd_ended_cb


        attributes_to_subscribe_to = (
                "dishMode",
                "capturing",
                "achievedPointing",
                "desiredPointing",
            )
        command_name = "SetOperateMode"
        try:
            # Subscribe the DishMaster attributes
            self._subscribe_to_attribute_events(attributes_to_subscribe_to)

            dish_client = TangoClient(device_data._dish_master_fqdn)
            print("*********************************** dish client proxy is *******************************", dish_client)
            cmd_ended_cb = CommandCallBack(self.logger).cmd_ended_cb

            # dish_client.send_command_async(command_name, None, cmd_ended_cb)
            # self.logger.info("'%s' command executed successfully.", command_name)
            # time.sleep(0.5)
            #device._dish_proxy.command_inout_asynch(command_name, device.cmd_ended_cb)
            dish_client.send_command_async(command_name, None, cmd_ended_cb)
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

    def _subscribe_to_attribute_events(self, attributes):
        device_data = DeviceData.get_instance()
        dish_client = TangoClient(device_data._dish_master_fqdn)


        for attribute_name in attributes:
            try:
                device_data.attr_event_map[attribute_name] = dish_client.subscribe_attribute(
                    attribute_name,
                    self.attribute_event_handler)
                    
            except DevFailed as dev_failed:
                self.logger.exception(dev_failed)
                log_message = (
                    f"Exception occurred while subscribing to Dish attribute: {attribute_name}"
                )
                device_data._read_activity_message = log_message
                tango.Except.re_throw_exception(
                    dev_failed,
                    "Exception in Init command",
                    log_message,
                    "DishLeafNode.{}Command".format("Init"),
                    tango.ErrSeverity.ERR,
                )
        print("*********************************** attribute map is *******************************", device_data.attr_event_map[attribute_name])

    def attribute_event_handler(self, event_data):
        """
        Retrieves the subscribed attribute of DishMaster.

        :param evt: A TANGO_CHANGE event on attribute.
        """
        device_data = DeviceData.get_instance()
        if event_data.err:
            log_message = f"Event system DevError(s) occured!!! {str(event_data.errors)}"
            device_data._read_activity_message = log_message
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
        device_data._read_activity_message = log_message
        self.logger.debug(log_message)