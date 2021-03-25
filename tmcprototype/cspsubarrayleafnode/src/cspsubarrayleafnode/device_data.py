# -*- coding: utf-8 -*-
#
# This file is part of the CspSubarrayLeafNode project
#
#
#
# Distributed under the terms of the BSD-3-Clause license.
# See LICENSE.txt for more info.
""" Device Data
This module defines the DeviceData class, which represents of the functional
CspSubarrayLeafNode device.
"""


class DeviceData:
    """
    This class represents the CspSubarrayLeafNode as functional device.
    It mainly comprise the data common across various functions/modules of cspsubarrayleafnode.
    """

    __instance = None

    def __init__(self):
        """Private constructor of the class"""
        if DeviceData.__instance is not None:
            raise Exception("This is singletone class")
        else:
            DeviceData.__instance = self

        self.receptorIDList_str = []
        self.target = None
        self.fsp_ids_object = []

    @staticmethod
    def get_instance():
        if DeviceData.__instance is None:
            DeviceData()
        return DeviceData.__instance
