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

from src.ska_tmc_subarraynode_low.src.ska_tmc_subarraynode_low.scan_timer_handler import ScanTimerHandler

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
        if DeviceData.__instance is not None:
            raise Exception("This is singletone class")
        else:
            DeviceData.__instance = self

        self._resource_list = []
        self.is_end_command = False
        self.is_release_resources = False
        self.is_scan_completed = False
        self.isScanRunning = False
        self.is_abort_command_executed = False
        self.is_obsreset_command_executed = False
        self.is_restart_command_executed = False
        self.scan_duration = None
        self.health_state_aggregator = None
        self.obs_state_aggregator = None
        self.assigned_resources_maintainer = None
        self.assignd_resources_by_mccs = ""
        self._subarray_health_state = HealthState.UNKNOWN 
        self.subarray_health_state_map = {}
        self._health_event_id = {}
        self.resource_list = []
        self.scan_thread = None
        self.scan_timer_handler = ScanTimerHandler()

    @staticmethod
    def get_instance():
        if DeviceData.__instance is None:
            DeviceData()
        return DeviceData.__instance

    def __len__(self):
        """
        Returns the number of resources currently assigned. Note that
        this also functions as a boolean method for whether there are
        any assigned resources: ``if len()``.

        :return: number of resources assigned
        :rtype: int
        """

        return len(self.resource_list)
