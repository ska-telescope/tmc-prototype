# -*- coding: utf-8 -*-
#
# This file is part of the mccssubarrayleafnode project
#
#
#
# Distributed under the terms of the BSD-3-Clause license.
# See LICENSE.txt for more info.

"""CentralNode

Central Node is a coordinator of the complete M&C system.
"""

from . import release
from . import const
from .mccs_subarray_leaf_node import MccsSubarrayLeafNode

__all__ = ["release", "const", "MccsSubarrayLeafNode"]

__version__ = release.version
__version_info__ = release.version_info
__author__ = release.author
