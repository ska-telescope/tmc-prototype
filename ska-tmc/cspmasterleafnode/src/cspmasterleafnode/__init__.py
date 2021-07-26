# -*- coding: utf-8 -*-
#
# This file is part of the CspMasterLeafNode project
#
#
#
# Distributed under the terms of the BSD-3-Clause license.
# See LICENSE.txt for more info.

"""CspMasterLeafNode - Leaf Node to monitor and control CSP Master.

"""

from . import release
from . import const
from .csp_master_leaf_node import CspMasterLeafNode
from .device_data import DeviceData
from .attribute_callbacks import (
    CbfHealthStateAttributeUpdator,
    PssHealthStateAttributeUpdator,
    PstHealthStateAttributeUpdator,
)

__all__ = [
    "CspMasterLeafNode",
    "const",
    "release",
    "DeviceData",
    "CbfHealthStateAttributeUpdator",
    "PssHealthStateAttributeUpdator",
    "PstHealthStateAttributeUpdator",
]

__version__ = release.version
__version_info__ = release.version_info
__author__ = release.author
