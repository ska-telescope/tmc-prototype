# -*- coding: utf-8 -*-
#
# This file is part of the DishLeafNode project
#
#
#
# Distributed under the terms of the BSD-3-Clause license.
# See LICENSE.txt for more info.

"""
Configure class for DishLeafNode.
"""
import json
import threading

import tango
from tango import DevState, DevFailed

from ska.base.commands import BaseCommand
from tmc.common.tango_client import TangoClient
from .az_el_converter import AzElConverter
from .device_data import DeviceData
from .command_callback import CommandCallBack


class Configure(BaseCommand):
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

        device_data = self.target
        command_name = "Configure"

        try:
            json_argument = self._load_config_string(argin)
            ra_value, dec_value = self._get_targets(json_argument)
            device_data.radec_value = f"radec,{ra_value},{dec_value}"
            receiver_band = json_argument["dish"]["receiverBand"]
            self._set_dish_desired_pointing_attribute(device_data.radec_value)
            self._configure_band(receiver_band)
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

        self.logger.info("'%s' command executed successfully.", command_name)

    def _configure_band(self, band):
        """"Send the ConfigureBand<band-number> command to Dish Master"""
        device_data = self.target
        command_name = f"ConfigureBand{band}"

        try:
            dish_client = TangoClient(device_data._dish_master_fqdn)
            cmd_ended_cb = CommandCallBack(self.logger).cmd_ended_cb
            dish_client.send_command_async(command_name, None, cmd_ended_cb)
        except DevFailed as dev_failed:
            raise dev_failed

    def _set_dish_desired_pointing_attribute(self, radec):
        device_data = self.target
        now = datetime.datetime.utcnow()
        timestamp = str(now)

        try:
            dish_client = TangoClient(device_data._dish_master_fqdn)
            azel_converter = AzElConverter(self.logger)
            device_data.az, device_data.el = azel_converter.convert_radec_to_azel(device_data.radec_value, timestamp, device_data.dish_name, device_data.observer_location["latitude"], device_data.observer_location["latitude"], device_data.observer_location["altitude"])
        except ValueError as valuerr:
            tango.Except.throw_exception(
                str(valuerr),
                f"Error converting radec '{radec}' to az and el coordinates, respectively.",
                "_set_dish_desired_pointing_attribute",
                tango.ErrSeverity.ERR,
            )

        # Set desiredPointing on Dish Master (it won't move until asked to
        # track or scan, but provide initial coordinates for interest)
        time_az_el = [now.timestamp(), device_data.az, device_data.el]
        dish_client.set_attribute("desiredPointing", time_az_el)
        
    def _get_targets(self, json_argument):
        try:
            ra_value = json_argument["pointing"]["target"]["RA"]
            dec_value = json_argument["pointing"]["target"]["dec"]
        except KeyError as key_error:
            tango.Except.throw_exception(
                str(key_error),
                "JSON key not found.",
                "_get_targets",
                tango.ErrSeverity.ERR,
            )

        return (ra_value, dec_value)

    def _load_config_string(self, argin):
        try:
            json_argument = json.loads(argin)
        except json.JSONDecodeError as jsonerr:
            tango.Except.throw_exception(
                str(jsonerr),
                "Invalid JSON format.",
                "_load_config_string",
                tango.ErrSeverity.ERR,
            )

        return json_argument

