# -*- coding: utf-8 -*-
#
# This file is part of the DishLeafNode project
#
#
#
# Distributed under the terms of the BSD-3-Clause license.
# See LICENSE.txt for more info.

"""

A Leaf control node for DishMaster.
"""

from . import release, CONST
from .dish_leaf_node import DishLeafNode, main

__all__ = ["dish_leaf_node", "CONST", "release"]

__version__ = release.version
__version_info__ = release.version_info
__author__ = release.author
