# -*- coding: utf-8 -*-
#
# This file is part of the MCCSMasterLeafNode project
#
#
#
# Distributed under the terms of the BSD-3-Clause license.
# See LICENSE.txt for more info.

"""MCCSMasterLeafNode - Leaf Node to monitor and control MCCS Master


"""

from . import release
from . import const
from .mccs_master_leaf_node import MccsMasterLeafNode

__all__ = ["release", "const", "MCCSMasterLeafNode"]

__version__ = release.version
__version_info__ = release.version_info
__author__ = release.author
