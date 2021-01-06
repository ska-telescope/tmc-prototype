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



class SetStandbyLPModeCommand(BaseCommand):
    """
    A class for DishLeafNode's SetStandbyLPMode() command.
    """

    def do(self):
        """
        Invokes SetStandbyLPMode (i.e. Low Power State) command on DishMaster.

        :raises DevFailed: If error occurs while invoking SetStandbyLPMode command on DishMaster.
        """
        device = self.target
        command_name = "SetStandbyFPMode"
        try:
            self._unsubscribe_attribute_events() 
            # ----------------------------------------------------
            device._dish_proxy.command_inout_asynch(command_name, device.cmd_ended_cb)
            self.logger.info("'%s' command executed successfully.", command_name)

            command_name = "SetStandbyLPMode"
            device._dish_proxy.command_inout_asynch(command_name, device.cmd_ended_cb)
            self.logger.info("'%s' command executed successfully.", command_name)
        except DevFailed as dev_failed:
            self.logger.exception(dev_failed)
            log_message = f"Exception occured while executing the '{command_name}' command."
            device._read_activity_message = log_message
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
        dish_client = TangoClient(device_data._dish_master_fqdn)
        device_data = DeviceData.get_instance()

        for attr_name in device_data.attr_event_map:
            log_message = "Unsubscribing attributes of: {}".format(dish_client.get_device_fqdn)
            self.logger.debug(log_message)
            dish_client.unsubscribe_attribute(device_data.attr_event_map[attr_name])
        device_data.attr_event_map.clear()

