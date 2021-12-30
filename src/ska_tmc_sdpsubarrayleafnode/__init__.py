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

# from . import const, exceptions, release
# from .device_data import DeviceData
# from .sdp_subarray_leaf_node import SdpSubarrayLeafNode

# __all__ = [
#     "const",
#     "release",
#     "SdpSubarrayLeafNode",
#     "DeviceData",
#     "exceptions",
# ]


from ska_tmc_sdpsubarrayleafnode import input_validator, release

__all__ = ["release", "input_validator"]

__version__ = release.version
__version_info__ = release.version_info
__author__ = release.author


__version__ = release.version
__version_info__ = release.version_info
__author__ = release.author
