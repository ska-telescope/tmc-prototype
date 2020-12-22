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
from centralnode.health_state_aggreegator import HealthStateAggreegator
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

        # self._subarray1_health_state = None
        # self._subarray2_health_state = None
        # self._subarray3_health_state = None
        self._sdp_master_leaf_health = None
        self._csp_master_leaf_health = None
        self._telescope_health_state = None
        self.receptorIDList = []
        # self.subarray_health_state_map = {}
        self._dish_leaf_node_devices = []
        self._leaf_device_proxy = []
        self.subarray_FQDN_dict = {}
        self._subarray_allocation = {}
        self.sdp_master_ln_fqdn = ""
        self.csp_master_ln_fqdn = ""
        self.dln_prefix = ""
        self.tm_mid_subarray = [] #"" # initialization is correct? it is array ('str',)
        self._read_activity_message = ""
        self.sln_prefix = ""
        # self.health_aggreegator = HealthStateAggreegator()
        self.obs_state_aggregator = None

    @staticmethod
    def get_instance():
        if DeviceData.__instance == None:
            DeviceData()
        return DeviceData.__instance









