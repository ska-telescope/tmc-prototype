# -*- coding: utf-8 -*-
#
# This file is part of the SubarrayNode project
#
#
#
# Distributed under the terms of the BSD-3-Clause license.
# See LICENSE.txt for more info.

""" Subarray Model
This module defines the SubarrayModel class, which represents of the functional Subarray device.
"""

class SubarrayModel:
    """
    This class represents the Subarray as functional device. It mainly comprise the data common
    across various functions of a subarray.
    """

    __instance = None

    def __init__(self):
        """Private constructor of the class""" 
        if SubarrayModel.__instance != None:
            raise Exception("This is singletone class")
        else:
            SubarrayModel.__instance = self

        self.is_scan_completed = False
        self.is_release_resources = False
        self.is_restart_command = False
        self.is_abort_command = False
        self.scan_duration = 0.0
        self.only_dishconfig_flag = False
        # TODO : Tango server class variables
        self._read_activity_message = ""
        self.sdp_subarray_ln_fqdn = ""
        self.csp_subarray_ln_fqdn = ""
        self._receive_addresses_map = ""

        # TODO: For future use
        self.receptor_id_list = []
        self.csp_subarray = None
        self.csp_subarray = None

    @staticmethod
    def get_instance():
        if SubarrayModel.__instance == None:
            SubarrayModel()
        return SubarrayModel.__instance
