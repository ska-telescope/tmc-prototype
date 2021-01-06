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
        self.observer_location_lat = ""
        self.observer_location_long = ""
        self.observer_altitude = 0
        self.event_track_time = threading.Event()
        self.attr_event_map = {}

    @staticmethod
    def get_instance():
        if DeviceData.__instance == None:
            DeviceData()
        return DeviceData.__instance
        
