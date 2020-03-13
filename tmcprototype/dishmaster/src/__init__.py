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
from .dish_master import DishMaster, main

__all__ = ["dish_master", "CONST", "release"]

__version__ = release.version
__version_info__ = release.version_info
__author__ = release.author
