# -*- coding: utf-8 -*-
#
# This file is part of the SDPSubarrayLeafNode project
#
#
#
# Distributed under the terms of the BSD-3-Clause license.
# See LICENSE.txt for more info.
""" Device Data
This module defines the DeviceData class, which represents of the functional SDPSubarrayLeafNode device.
"""


class DeviceData:
    """
    This class represents the SDPSubarrayLeafNode
    as functional device. It mainly comprise the data common
    across various functions of a SDPSubarrayLeafNode
    """

    __instance = None

    def __init__(self):
        """Private constructor of the class"""
        if DeviceData.__instance != None:
            raise Exception("This is singletone class")
        else:
            DeviceData.__instance = self

        self._receive_addresses = ""
        self._read_activity_message = ""
        self._active_processing_block = ""
        self._sdp_sa_fqdn = ""

    @staticmethod
    def get_instance():
        if DeviceData.__instance == None:
            DeviceData()
        return DeviceData.__instance
