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
# Standard Python imports
import katpoint
import math
from .utils import UnitConverter


class AzElConverter:
    def __init__(self, log):
        self.logger = log

    def convert_radec_to_azel(
        self,
        target,
        timestamp,
        dish_name,
        observer_location_lat,
        observer_location_long,
        observer_altitude,
    ):
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
        
        dish_antenna = katpoint.Antenna(
            name=dish_name,
            latitude=observer_location_lat,
            longitude=observer_location_long,
            altitude=observer_altitude,
        )  
        # obtain az el co-ordinates for dish
        azel = target.azel(timestamp, dish_antenna)
        # list of az el co-ordinates 
        az_el_coordinates = [azel.az.deg, azel.alt.deg]
        return az_el_coordinates
