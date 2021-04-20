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
        target_input,
        timestamp,
        dish_name,
        observer_location_lat,
        observer_location_long,
        observer_altitude,
    ):
        """Converts RaDec coordinate in to AzEl coordinate using KATPoint library.

        :param target_input: str
            Argin to be provided is the Ra and Dec values in the following format:
            radec,21:08:47.92,89:15:51.4
        :param timestamp: str
            2020-12-11 10:06:34.970731
        :return: list
            Azimuth and elevation angle, in degrees
        :raises ValueError: If error occurs when creating katpoint Target or Timestamp.
        """
        print("dish_name -----------", dish_name, type(dish_name))
        print("observer_location_lat -----------", observer_location_lat, type(observer_location_lat))
        print("observer_location_long ----------", observer_location_long, type(observer_location_long))
        print("observer_altitude ----------", observer_altitude, type(observer_altitude))
        print("timestamp ----------", timestamp)

        dish_antenna = katpoint.Antenna(f'{dish_name}, {observer_location_lat}, {observer_location_long}, {observer_altitude}')
        
        
        
        # test 1
        # descriptions = '''
        # 0001, -30:42:39.8, 21:26:38.0, 1086, 13.5, 0 0 0 0 0 0,0, 0
        # '''.strip().split('\n')
        # antennas = [katpoint.Antenna(line) for line in descriptions]
        # dish_antenna = antennas[0]

        # test 2
        # dish_antenna = katpoint.Antenna('0001, -30:42:39.8, 21:26:38.0, 1086, 13.5, 0 0 0 0 0 0,0, 0')
        # print("dish_antenna -----------", dish_antenna)
        # timestamp1 = '2021-04-20 11:47:59.787580'
        # print("timestamp1 ---------", timestamp1)

        text_input_array = target_input.split(",")
        print("text_input_array -------------", text_input_array)
        
        ra = text_input_array[1]
        print("ra -------------", ra)
        dec = text_input_array[2]
        print("dec ------------", dec)
        target = katpoint.Target.from_radec(ra, dec)


        # obtain az el co-ordinates for dish
        azel = target.azel(timestamp, dish_antenna)
        # list of az el co-ordinates 
        az_el_coordinates = [azel.az.deg, azel.alt.deg]
        return az_el_coordinates
