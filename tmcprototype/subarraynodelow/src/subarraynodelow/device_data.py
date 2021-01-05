# -*- coding: utf-8 -*-
#
# This file is part of the SubarrayNodeLow project
#
#
#
# Distributed under the terms of the BSD-3-Clause license.
# See LICENSE.txt for more info.
""" Device Data
This module defines the DeviceData class, which represents of the functional TMC-Low SubarrayNode device.
"""
# PROTECTED REGION ID(CentralNode.additionnal_import) ENABLED START #
from ska.base.control_model import HealthState
# PROTECTED REGION END #    //  CentralNode.additional_import

class DeviceData:
    """
    This class represents the SubarrayNode
    as functional device. It mainly comprise the data common
    across various functions of a subarray node.
    """
    __instance = None
    def __init__(self):
        """Private constructor of the class"""
        if DeviceData.__instance != None:
            raise Exception("This is singletone class")
        else:
            DeviceData.__instance = self

        self._resource_list = []
        self.is_end_command = False
        self.is_release_resources = False
        self.is_scan_completed = False
        self.isScanRunning = False
        self._scan_id = ""
        self.scan_duration = None
        self.health_state_aggregator = None
        self.obs_state_aggregator = None
        self._subarray_health_state = HealthState.UNKNOWN
        self.subarray_health_state_map = {}
        self._mccs_sa_obs_state = None
        self._health_event_id = {}
        self.mccs_subarray_fqdn = ""

    @staticmethod
    def get_instance():
        if DeviceData.__instance == None:
            DeviceData()
        return DeviceData.__instance
