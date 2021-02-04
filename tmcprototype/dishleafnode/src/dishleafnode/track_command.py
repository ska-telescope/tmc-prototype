# -*- coding: utf-8 -*-
#
# This file is part of the DishLeafNode project
#
#
#
# Distributed under the terms of the BSD-3-Clause license.
# See LICENSE.txt for more info.

"""
Track class for DishLeafNode.
"""
import threading
import datetime
import time

import tango
from tango import DevState, DevFailed

from ska.base.commands import BaseCommand
from tmc.common.tango_client import TangoClient
from .command_callback import CommandCallBack
from .az_el_converter import AzElConverter


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
        if self.state_model.op_state in [
            DevState.FAULT,
            DevState.UNKNOWN,
            DevState.DISABLE,
        ]:
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
            json_argin = device_data._load_config_string(argin)
            ra_value, dec_value = device_data._get_targets(json_argin)
            radec_value = f"radec,{ra_value},{dec_value}"
            self.logger.info(
                "Track command ignores RA dec coordinates passed in: %s. "
                "Uses coordinates from Configure command instead.",
                radec_value,
            )

            dish_client = TangoClient(device_data._dish_master_fqdn)
            cmd_ended_cb = CommandCallBack(self.logger).cmd_ended_cb

            dish_client.send_command_async(command_name, callback_method=cmd_ended_cb)
            self.logger.info("'%s' command executed successfully.", command_name)
        except DevFailed as dev_failed:
            self.logger.exception(dev_failed)
            log_message = (
                f"Exception occured while executing the '{command_name}' command."
            )
            device_data._read_activity_message = log_message
            tango.Except.re_throw_exception(
                dev_failed,
                f"Exception in '{command_name}' command.",
                log_message,
                f"DishLeafNode.{command_name}Command",
                tango.ErrSeverity.ERR,
            )

        device_data.event_track_time.clear()
        self.tracking_thread = threading.Thread(None, self.track_thread, "DishLeafNode")
        self.tracking_thread.start()

    # pylint: disable=logging-fstring-interpolation
    def track_thread(self):
        """This thread writes coordinates to desiredPointing on DishMaster at the rate of 20 Hz."""
        self.logger.info(
            f"print track_thread thread name:{threading.currentThread().getName()}"
            f"{threading.get_ident()}"
        )
        device_data = self.target
        dish_client = TangoClient(device_data._dish_master_fqdn)

        while device_data.event_track_time.is_set() is False:
            now = datetime.datetime.utcnow()
            timestamp = str(now)
            # pylint: disable=unbalanced-tuple-unpacking
            azel_converter = AzElConverter(self.logger)
            device_data.az, device_data.el = azel_converter.convert_radec_to_azel(
                device_data.radec_value,
                timestamp,
                device_data.dish_name,
                device_data.observer_location["latitude"],
                device_data.observer_location["latitude"],
                device_data.observer_location["altitude"],
            )

            if not self._is_elevation_within_mechanical_limits():
                time.sleep(0.05)
                continue

            if device_data.az < 0:
                device_data.az = 360 - abs(device_data.az)

            if device_data.event_track_time.is_set():
                log_message = f"Break loop: {device_data.event_track_time.is_set()}"
                self.logger.debug(log_message)
                break

            # TODO (kmadisa 11-12-2020) Add a pointing lead time to the current time (like we do on MeerKAT)
            desired_pointing = [
                now.timestamp(),
                round(device_data.az, 12),
                round(device_data.el, 12),
            ]
            self.logger.debug("desiredPointing coordinates: %s", desired_pointing)
            dish_client.deviceproxy.desiredPointing = desired_pointing
            time.sleep(0.05)

    # pylint: enable=logging-fstring-interpolation, unbalanced-tuple-unpacking

    def _is_elevation_within_mechanical_limits(self):
        device_data = self.target

        if not (device_data.ele_min_lim <= device_data.el <= device_data.ele_max_lim):
            device_data.el_limit = True
            log_message = "Minimum/maximum elevation limit has been reached."
            device_data._read_activity_message = log_message
            self.logger.info(log_message)
            log_message = "Source is not visible currently."
            device_data._read_activity_message = log_message
            self.logger.info(log_message)
            return False

        device_data.el_limit = False
        return True
