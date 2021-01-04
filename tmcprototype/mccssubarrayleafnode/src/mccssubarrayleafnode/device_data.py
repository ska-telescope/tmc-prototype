# -*- coding: utf-8 -*-
#
# This file is part of the MCCSSubarrayLeafNode project
#
#
#
# Distributed under the terms of the BSD-3-Clause license.
# See LICENSE.txt for more info.
""" Device Data
This module defines the DeviceData class, which represents of the functional MCCSSubarrayLeafNode device.
"""


class DeviceData:
    """
    This class represents the MCCSSubarrayLeafNode
    as functional device. It mainly comprise the data common
    across various functions of a MCCSSubarrayLeafNode
    """
    __instance = None

    def __init__(self):
        """Private constructor of the class"""
        if DeviceData.__instance != None:
            raise Exception("This is singletone class")
        else:
            DeviceData.__instance = self

        self._read_activity_message = ""
        self._mccs_subarray_fqdn = ""
        self._sky_coordinates = []
        self._station_ids = []

    @staticmethod
    def get_instance():
        if DeviceData.__instance == None:
            DeviceData()
        return DeviceData.__instance

