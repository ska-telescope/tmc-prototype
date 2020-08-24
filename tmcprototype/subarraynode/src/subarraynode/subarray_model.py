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

    def __init__(self):
        self.is_scan_completed = False
        self.is_release_resources = False
        self.is_restart_command = False
        self.is_abort_command = False
        self.scan_duration = 0.0

        # TODO: For future use
        self.receptor_id_list = []
        self.csp_subarray = None
        self.csp_subarray = None