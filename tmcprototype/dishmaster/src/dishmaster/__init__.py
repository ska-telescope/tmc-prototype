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
from . import release, dish_master_behaviour, dish_master, utils

__all__ = ["release", "dish_master", "dish_master_behaviour", "utils"]

__version__ = release.version
__version_info__ = release.version_info
__author__ = release.author
