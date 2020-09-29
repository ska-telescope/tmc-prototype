# -*- coding: utf-8 -*-
#
# This file is part of the MccsMasterLeafNode project
#
#
#
# Distributed under the terms of the BSD-3-Clause license.
# See LICENSE.txt for more info.

"""
MccsSubarrayLeafNode - Leaf Node to monitor and control MCCS Subarray
"""

from . import release
from . import const
from .mccs_master_leaf_node import MccsMasterLeafNode

__all__ = ["release", "const", "MccsMasterLeafNode"]

__version__ = release.version
__version_info__ = release.version_info
__author__ = release.author
