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
from . import release, CONST
from .dish_master import DishMaster

__all__ = ["CONST", "release", "DishMaster"]

__version__ = release.version
__version_info__ = release.version_info
__author__ = release.author
