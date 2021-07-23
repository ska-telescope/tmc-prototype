# -*- coding: utf-8 -*-
#
# This file is part of the DishMaster project
#
#
#
# Distributed under the terms of the BSD-3-Clause license.
# See LICENSE.txt for more info.

"""DishMaster Simulator

SKA Dish Master TANGO device server
"""
from .csp_master_behaviour import OverrideCspMaster, get_csp_master_sim

__all__ = ["get_csp_master_sim", "OverrideCspMaster"]

