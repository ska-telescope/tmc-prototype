# -*- coding: utf-8 -*-
#
# This file is part of the DishMaster project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

"""DishMaster Simulator

SKA Dish Master TANGO device server
"""

from . import release
from .DishMaster import DishMaster, main

__version__ = release.version
__version_info__ = release.version_info
__author__ = release.author
