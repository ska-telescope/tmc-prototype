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
from . import release, const
from .dish_master import DishMaster
from .dish_master import DishMode
from .dish_master import ConfiguredBand
from .dish_master import PointingState

__all__ = ["const", "release", "DishMaster", "DishMode", "ConfiguredBand", "PointingState"]

__version__ = release.version
__version_info__ = release.version_info
__author__ = release.author
