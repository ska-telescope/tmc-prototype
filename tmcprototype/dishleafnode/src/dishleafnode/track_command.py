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


class Track(BaseCommand):
    """
    A class for DishLeafNode's Track() command.
    """

    def check_allowed(self):
        """
        Checks whether this command is allowed to be run in the current device state.

        :return: True if this command is allowed to be run in current device state.
        :rtype: boolean
        """
        if self.state_model.op_state in [DevState.FAULT, DevState.UNKNOWN, DevState.DISABLE]:
            return False

        return True

    def do(self, argin):
        """Invokes Track command on the DishMaster.

        :param argin: DevString
            The elevation limit thread allows Dish to track a source till the observation capacity i.e.
            elevation limit of dish.

            The tracking time thread allows dish to track a source for the prespecified Track Duration
            (provided elevation limit is not reached).

            For Track command, argin to be provided is the Ra and Dec values in the following JSON format:

            {"pointing":{"target":{"system":"ICRS","name":"Polaris Australis","RA":"21:08:47.92","dec":"-88:57:22.9"}},
            "dish":{"receiverBand":"1"}}
        :raises DevFailed: If error occurs while invoking Track command on DishMaster.
        """
        device_data = self.target
        device_data.el_limit = False
        command_name = "Track"

        try:
            json_argin = self._load_config_string(argin)
            ra_value, dec_value = self._get_targets(json_argin)
            radec_value = f"radec,{ra_value},{dec_value}"
            self.logger.info(
                "Track command ignores RA dec coordinates passed in: %s. "
                "Uses coordinates from Configure command instead.",
                radec_value,
            )

            dish_client = TangoClient(device_data._dish_master_fqdn)
            cmd_ended_cb = CommandCallBack(self.logger).cmd_ended_cb
            azel_converter = AzElConverter.get_instance()

            dish_client.send_command_async(command_name, None, cmd_ended_cb)
            # device._dish_proxy.command_inout_asynch(command_name, device.cmd_ended_cb)
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

        device_data.event_track_time.clear()
        self.tracking_thread = threading.Thread(None, azel_converter.track_thread, "DishLeafNode")
        self.tracking_thread.start()

    
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


