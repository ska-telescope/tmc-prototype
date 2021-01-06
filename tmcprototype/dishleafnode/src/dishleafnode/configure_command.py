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



class ConfigureCommand(BaseCommand):
    """
    A class for DishLeafNode's Configure() command.
    """

    def check_allowed(self):
        """
        Checks whether this command is allowed to be run in the current device state.

        :return: True if this command is allowed to be run in current device state.
        :rtype: boolean
        """
        if self.state_model.op_state in [
            DevState.FAULT,
            DevState.UNKNOWN,
            DevState.DISABLE,
            DevState.INIT,
        ]:
            return False

        return True

    def do(self, argin):
        """
        Configures the Dish by setting pointing coordinates for a given scan.
        This function accepts the input json and calculate pointing parameters of Dish- Azimuth
        and Elevation Angle. Calculated parameters are again converted to json and fed to the
        dish master.

        :param argin:
            A String in a JSON format that includes pointing parameters of Dish- Azimuth and
            Elevation Angle.

                Example:
                {"pointing":{"target":{"system":"ICRS","name":"Polaris Australis","RA":"21:08:47.92","dec":"-88:57:22.9"}},
                "dish":{"receiverBand":"1"}}
        :raises DevFailed: If error occurs while invoking ConfigureBand<> command on DishMaster or
            if the json string contains invalid data.
        """

        device = self.target
        command_name = "Configure"

        try:
            json_argument = device._load_config_string(argin)
            ra_value, dec_value = device._get_targets(json_argument)
            device.radec_value = f"radec,{ra_value},{dec_value}"
            receiver_band = json_argument["dish"]["receiverBand"]
            self._set_desired_pointing(device.radec_value)
            self._configure_band(receiver_band)
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

        self.logger.info("'%s' command executed successfully.", command_name)

    def _configure_band(self, band):
        """"Send the ConfigureBand<band-number> command to Dish Master"""
        device = self.target
        command_name = f"ConfigureBand{band}"

        try:
            device._dish_proxy.command_inout_asynch(command_name, device.cmd_ended_cb)
        except DevFailed as dev_failed:
            raise dev_failed

    def _set_desired_pointing(self, radec):
        device = self.target
        now = datetime.datetime.utcnow()
        timestamp = str(now)

        try:
            device.az, device.el = device.convert_radec_to_azel(radec, timestamp)
        except ValueError as valuerr:
            tango.Except.throw_exception(
                str(valuerr),
                f"Error converting radec '{radec}' to az and el coordinates, respectively.",
                "_set_desired_pointing",
                tango.ErrSeverity.ERR,
            )

        # Set desiredPointing on Dish Master (it won't move until asked to
        # track or scan, but provide initial coordinates for interest)
        time_az_el = [now.timestamp(), device.az, device.el]
        device._dish_proxy.desiredPointing = time_az_el

