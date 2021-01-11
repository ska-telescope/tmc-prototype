# -*- coding: utf-8 -*-
#
# This file is part of the DishLeafNode project
#
#
#
# Distributed under the terms of the BSD-3-Clause license.
# See LICENSE.txt for more info.
""" Device Data
This module defines the DeviceData class, which represents of the functional DishLeafNode device.
"""
import threading
import importlib.resources
from .utils import UnitConverter
import katpoint

class DeviceData:
    """
    This class represents the DishLeafNode
    as functional device. It mainly comprise the data common
    across various functions of a DishLeafNode
    """
    __instance = None
    
    def __init__(self):
        """Private constructor of the class"""
        if DeviceData.__instance != None:
            raise Exception("This is singletone class")
        else:
            DeviceData.__instance = self

        self._read_activity_message = ""
        self._dish_master_fqdn = ""
        self.el = 30.0
        self.az = 0.0
        self.ele_max_lim = 90
        self.ele_min_lim = 17.5
        self.el_limit = False
        self.radec_value = ""
        self.dish_name = ""
        self.dish_number = ""
        self.observer_location = {}
        self.event_track_time = threading.Event()
        self.attr_event_map = {}

    @staticmethod
    def get_instance():
        if DeviceData.__instance == None:
            DeviceData()
        return DeviceData.__instance

    def set_dish_name_number(self):
        # Find out dish number from DishMasterFQDN property e.g. mid_d0001/elt/master
        dish_name_string = self._dish_master_fqdn.split("/")[0]
        self.dish_name = dish_name_string.split("_")[1]
        self.dish_number = self.dish_name[1:]
    
    def set_observer_lat_long_alt(self, logger):
        # Load a set of antenna descriptions (latitude, longitude, altitude, enu coordinates)
        # from text file and construct Antenna objects from them. Currently the text file
        # contains Meerkat Antenna parameters.
        try:
            with importlib.resources.open_text("dishleafnode", "ska_antennas.txt") as f:
                descriptions = f.readlines()
            antennas = [katpoint.Antenna(line) for line in descriptions]
        except OSError as err:
            logger.exception(err)
            raise err
        except ValueError as verr:
            logger.exception(verr)
            raise verr

        antenna_exist = False

        for ant in antennas:
            if ant.name == self.dish_number:
                ref_ant_lat = ant.ref_observer.lat
                ref_ant_long = ant.ref_observer.long
                ref_ant_altitude = ant.ref_observer.elevation
                ant_delay_model = ant.delay_model.values()
                antenna_exist = True
                break

        if not antenna_exist:
            raise Exception(f"Antenna '{self.dish_number}' not in the ska_antennas.txt file.")

        # Convert reference antenna lat and long into radian
        obj_unitconverter = UnitConverter()
        ref_ant_lat_rad = obj_unitconverter.dms_to_rad(str(ref_ant_lat).split(":"))
        ref_ant_long_rad = obj_unitconverter.dms_to_rad(str(ref_ant_long).split(":"))

        # Find latitude, longitude and altitude of Dish antenna
        # Convert enu to ecef coordinates for dish
        dish_ecef_coordinates = katpoint.enu_to_ecef(
            ref_ant_lat_rad,
            ref_ant_long_rad,
            ref_ant_altitude,
            ant_delay_model[0],
            ant_delay_model[1],
            ant_delay_model[2],
        )
        # Convert ecef to lla coordinates for dish (in radians)
        dish_lat_long_alt_rad = katpoint.ecef_to_lla(
            dish_ecef_coordinates[0], dish_ecef_coordinates[1], dish_ecef_coordinates[2]
        )
        # Convert lla coordinates from rad to dms
        dish_lat_dms = obj_unitconverter.rad_to_dms(dish_lat_long_alt_rad[0])
        dish_long_dms = obj_unitconverter.rad_to_dms(dish_lat_long_alt_rad[1])

        self.observer_location["latitude"] = f"{dish_lat_dms[0]}:{dish_lat_dms[1]}:{dish_lat_dms[2]}"
        self.observer_location["longitude"] = f"{dish_long_dms[0]}:{dish_long_dms[1]}:{dish_long_dms[2]}"
        self.observer_location["altitude"] = dish_ecef_coordinates[2]