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
import logging

from tango import DevFailed

# Additional import
from tmc.common.tango_group_client import TangoGroupClient
from . import const
from subarraynode.scan_timer_handler import ScanTimerHandler


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
        self.is_end_command_executed = False
        self.is_release_resources_command_executed = False
        self.is_restart_command_executed = False
        self.is_abort_command_executed = False
        self.is_obsreset_command_executed = False
        self.scan_duration = 0.0
        self.is_scan_running = False
        self.scan_timer_handler = ScanTimerHandler()
        self._read_activity_message = ""
        self.sdp_subarray_ln_fqdn = ""
        self.csp_subarray_ln_fqdn = ""
        self.sdp_sa_fqdn = ""
        self._receive_addresses_map = ""
        self.csp_sdp_ln_health_event_id = ""
        self.csp_sdp_ln_obs_state_event_id = ""
        self.dish_pointing_state_map = {}
        self.scan_configuration = ""
        self._scan_id = ""
        self._sb_id = ""
        self._scan_type = ""
        self._dish_leaf_node_group_client = TangoGroupClient(
            const.GRP_DISH_LEAF_NODE, None
        )
        self.health_state_aggr = None
        self.obs_state_aggr = None
        self.dish_leaf_node_prefix = 0
        self._dish_leaf_node_proxy = ""
        self.csp_sa_obs_state = None
        self.sdp_sa_obs_state = None
        self.dish_ln_health_even_id = {}
        self.dish_ln_pointing_state_event_id = {}
        self.health_state = None
        # TODO: For future use
        self._receptor_id_list = []
        self.receive_addresses = None

    def clean_up_dict(self, logger=None):
        """
        Cleans dictionaries of the resources across the subarraynode.

        Note: Currently there are only receptors allocated so the group contains only receptor ids.

        :param argin:
            DevVoid
        :return:
            DevVoid
        """
        if logger == None:
            self.logger = logging.getLogger(__name__)
        else:
            self.logger = logger
        if not self.dish_ln_health_even_id or not self.dish_ln_pointing_state_event_id:
            return
        try:
            self._dish_leaf_node_group_client.remove_all_device()
            log_message = const.STR_GRP_DEF
            self.logger.debug(log_message)
            self._read_activity_message = log_message
            self.logger.info(const.RECEPTORS_REMOVE_SUCCESS)
        except DevFailed as dev_failed:
            log_message = "Failed to remove receptors from the group. {}".format(
                dev_failed
            )
            self.logger.error(log_message)
            self._read_activity_message = log_message
            return

        self.health_state_aggr.unsubscribe_dish_health_state()
        self.obs_state_aggr.unsubscribe_dish_pointing_state()

        # clearing dictonaries and lists
        self.dish_ln_health_even_id.clear()  # Clear eventID dictionary
        self.dish_ln_pointing_state_event_id.clear()  # Clear eventID dictionary
        self._receptor_id_list.clear()
        self.dish_pointing_state_map.clear()
        self.health_state_aggr._remove_subarray_dish_lns_health_states()
        self.logger.info(const.STR_RECEPTORS_REMOVE_SUCCESS)

    @staticmethod
    def get_instance():
        if DeviceData.__instance == None:
            DeviceData()
        return DeviceData.__instance

    # This method is required to complete and AssignResources and ReleaseAllResources command.
    def __len__(self):
        """
        Returns the number of resources currently assigned. Note that
        this also functions as a boolean method for whether there are
        any assigned resources: ``if len()``.

        :return: number of resources assigned
        :rtype: int
        """

        return len(self._receptor_id_list)
