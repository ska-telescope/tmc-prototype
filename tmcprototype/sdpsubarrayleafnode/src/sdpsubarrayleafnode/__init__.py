# -*- coding: utf-8 -*-
#
# This file is part of the SdpSubarrayLeafNode project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

"""
SdpSubarrayLeafNode
"""

from . import release, const
from .sdp_subarray_leaf_node import SdpSubarrayLeafNode

__all__ = ["const", "release", "SdpSubarrayLeafNode"]

__version__ = release.version
__version_info__ = release.version_info
__author__ = release.author
