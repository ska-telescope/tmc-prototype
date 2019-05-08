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
from .CspMasterLeafNode import CspMasterLeafNode, main

__all__ = ["CspMasterLeafNode", "CONST", "release"]

__version__ = release.version
__version_info__ = release.version_info
__author__ = release.author
