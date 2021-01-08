# -*- coding: utf-8 -*-
#
# This file is part of the DishLeafNode project
#
#
#
# Distributed under the terms of the BSD-3-Clause license.
# See LICENSE.txt for more info.
""" Az El Converter
This module performs Ra-Dec to Az-El coordinates conversion.
"""
import threading
import datetime
import katpoint
import math
import time
from .utils import UnitConverter
from tmc.common.tango_client import TangoClient
from .device_data import DeviceData


class AzElConverter:

    __instance = None
    
    def __init__(self):
        """Private constructor of the class"""
        if AzElConverter.__instance != None:
            raise Exception("This is singletone class")
        else:
            AzElConverter.__instance = self

    @staticmethod
    def get_instance():
        if AzElConverter.__instance == None:
            AzElConverter()
        return AzElConverter.__instance

    def convert_radec_to_azel(self, target, timestamp):
        """Converts RaDec coordinate in to AzEl coordinate using KATPoint library.

        :param target: str
            Argin to be provided is the Ra and Dec values in the following format:
            radec,21:08:47.92,89:15:51.4
        :param timestamp: str
            2020-12-11 10:06:34.970731
        :return: list
            Azimuth and elevation angle, in degrees
        :raises ValueError: If error occurs when creating katpoint Target or Timestamp.
        """
        device_data = DeviceData.get_instance()


        dish_antenna = katpoint.Antenna(
            name=device_data.dish_name,
            latitude=device_data.observer_location_lat,
            longitude=device_data.observer_location_long,
            altitude=device_data.observer_altitude,
        )

        dish_antenna_latitude = dish_antenna.ref_observer.lat
        try:
            desired_target = katpoint.Target(str(target))
            timestamp = katpoint.Timestamp(timestamp=timestamp)
            target_apparnt_radec = katpoint.Target.apparent_radec(
                desired_target, timestamp=timestamp, antenna=dish_antenna
            )
        except ValueError as value_err:
            self.logger.error(
                "Error creating instances of katpoint Target/Timestamp from target: '%s' and timestamp: '%s'.",
                target,
                timestamp,
            )
            raise value_err

        sidereal_time = dish_antenna.local_sidereal_time(timestamp=timestamp)
        sidereal_time_radian = katpoint.deg2rad(math.degrees(sidereal_time))

        # converting ra to ha
        hour_angle = sidereal_time_radian - target_apparnt_radec[0]

        # Geodetic latitude of the observer
        latitude_degree_decimal = UnitConverter().dms_to_dd(str(dish_antenna_latitude))
        latitude_radian = katpoint.deg2rad(latitude_degree_decimal)

        # Calculate enu coordinates
        enu_array = katpoint.hadec_to_enu(hour_angle, target_apparnt_radec[1], latitude_radian)

        # Calculate Az El coordinates
        az_el_coordinates = list(katpoint.enu_to_azel(enu_array[0], enu_array[1], enu_array[2]))
        az_el_coordinates[0] = katpoint.rad2deg(az_el_coordinates[0])
        az_el_coordinates[1] = katpoint.rad2deg(az_el_coordinates[1])
        return az_el_coordinates

    def track_thread(self):
        """This thread writes coordinates to desiredPointing on DishMaster at the rate of 20 Hz."""
        self.logger.info(
            f"print track_thread thread name:{threading.currentThread().getName()}"
            f"{threading.get_ident()}"
        )
        device_data = DeviceData.get_instance()
        dish_client = TangoClient(device_data._dish_master_fqdn)

        while device_data.event_track_time.is_set() is False:
            now = datetime.datetime.utcnow()
            timestamp = str(now)
            # pylint: disable=unbalanced-tuple-unpacking
            device_data.az, device_data.el = self.convert_radec_to_azel(device_data.radec_value, timestamp)

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
            desired_pointing = [now.timestamp(), round(device_data.az, 12), round(device_data.el, 12)]
            self.logger.debug("desiredPointing coordinates: %s", desired_pointing)
            # self._dish_proxy.desiredPointing = desired_pointing
            dish_client.deviceproxy.desiredPointing = desired_pointing
            time.sleep(0.05)

    def _is_elevation_within_mechanical_limits(self):
        device_data = DeviceData.get_instance()
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

        
