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