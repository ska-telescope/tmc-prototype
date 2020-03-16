# -*- coding: utf-8 -*-
#
# This file is part of the SdpMasterLeafNode project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

"""SdpMasterLeafNode

The primary responsibility of the SDP Subarray Leaf node is to monitor the SDP Subarray and issue control
actions during an observation. It also acts as a SDP contact point for Subarray Node for observation
execution. There is one to one mapping between SDP Subarray Leaf Node and SDP subarray.
"""

from . import release
from .sdp_master_leaf_node import SdpMasterLeafNode, main

__all__ = ["sdp_master_leaf_node", "CONST", "release"]

__version__ = release.version
__version_info__ = release.version_info
__author__ = release.author
