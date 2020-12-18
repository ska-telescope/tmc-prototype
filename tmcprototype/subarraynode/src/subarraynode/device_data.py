# -*- coding: utf-8 -*-
#
# This file is part of the SubarrayNode project
#
#
#
# Distributed under the terms of the BSD-3-Clause license.
# See LICENSE.txt for more info.

""" Device Data
This module defines the Device Data class, which represents the functional Subarray device.
"""
import tango
from . import const
from subarraynode.health_state_aggregator import HealthStateAggregator
from subarraynode.obs_state_aggregator import ObsStateAggregator

class DeviceData:
    """
    This class represents the Subarray as functional device. It mainly comprise the data common
    across various functions of a subarray.
    """

    __instance = None

    def __init__(self):
        """Private constructor of the class""" 
        if DeviceData.__instance != None:
            raise Exception("This is singletone class")
        else:
            DeviceData.__instance = self

        self.is_scan_completed = False
        self.is_release_resources = False
        self.is_restart_command = False
        self.is_abort_command = False
        self.is_obsreset_command = False
        self.scan_duration = 0.0
        self.isScanRunning = False
        self.only_dishconfig_flag = False
        # TODO : Tango server class variables
        self._read_activity_message = ""
        self.sdp_subarray_ln_fqdn = ""
        self.csp_subarray_ln_fqdn = ""
        self._receive_addresses_map = ""
        self.csp_sdp_ln_health_event_id = ""
        self.csp_sdp_ln_obs_state_event_id = ""
        self.scan_configuration = ""
        self._dish_leaf_node_group = tango.Group(const.GRP_DISH_LEAF_NODE)
        self.health_state_aggr = HealthStateAggregator()
        self.obs_state_aggr = ObsStateAggregator()

        # TODO: For future use
        self.receptor_id_list = []

    @staticmethod
    def get_instance():
        if DeviceData.__instance == None:
            DeviceData()
        return DeviceData.__instance
    
    def receive_addresses_cb(self, event):
        """
        Retrieves the receiveAddresses attribute of SDP Subarray.

        :param event: A TANGO_CHANGE event on SDP Subarray receiveAddresses attribute.

        :return: None
        """
        if not event.err:
            # self._receive_addresses_map = event.attr_value.value
            self._receive_addresses_map = event.attr_value.value
        else:
            log_msg = const.ERR_SUBSR_RECEIVE_ADDRESSES_SDP_SA + str(event)
            self.logger.debug(log_msg)
            self._read_activity_message = log_msg
