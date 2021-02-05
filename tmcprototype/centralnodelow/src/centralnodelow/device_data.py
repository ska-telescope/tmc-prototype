# -*- coding: utf-8 -*-
#
# This file is part of the CentralNode project
#
#
#
# Distributed under the terms of the BSD-3-Clause license.
# See LICENSE.txt for more info.
""" Device Data
This module defines the DeviceData class, which represents of the functional CentralNode device.
"""
# PROTECTED REGION ID(CentralNode.additionnal_import) ENABLED START #
from ska.base.control_model import HealthState

# PROTECTED REGION END #    //  CentralNode.additional_import


class DeviceData:
    """
    This class represents the CentralNode
    as functional device. It mainly comprise the data common
    across various functions of a central node.
    """

    __instance = None

    def __init__(self):
        """Private constructor of the class"""
        if DeviceData.__instance != None:
            raise Exception("This is singletone class")
        else:
            DeviceData.__instance = self

        self._subarray1_health_state = HealthState.UNKNOWN
        self._mccs_master_leaf_health = HealthState.UNKNOWN
        self._health_state = HealthState.UNKNOWN
        self._telescope_health_state = HealthState.UNKNOWN
        self.subarray_health_state_map = {}
        self.subarray_FQDN_dict = {}
        self.subarray_low = []
        self.mccs_master_ln_fqdn = ""
        self.mccs_controller_fqdn = ""
        self._read_activity_message = ""
        self.health_aggreegator = None
        self.cmd_res_evt_id = None
        self.cmd_res_evt_val = ""
        self.attr_event_map = {}


    @staticmethod
    def get_instance():
        if DeviceData.__instance == None:
            DeviceData()
        return DeviceData.__instance
