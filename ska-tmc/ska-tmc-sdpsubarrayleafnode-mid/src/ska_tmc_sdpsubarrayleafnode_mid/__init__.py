# -*- coding: utf-8 -*-
#
# This file is part of the SdpSubarrayLeafNode project
#
#
#
# Distributed under the terms of the BSD-3-Clause license.
# See LICENSE.txt for more info.

"""
SdpSubarrayLeafNode
"""

from . import release, const, exceptions
from .sdp_subarray_leaf_node import SdpSubarrayLeafNode
from .device_data import DeviceData
# from .sdpsubarraysimulator.sdp_subarray import sdp_subarray_simulator

__all__ = ["const", "release", "SdpSubarrayLeafNode", "DeviceData", "exceptions"]

__version__ = release.version
__version_info__ = release.version_info
__author__ = release.author
