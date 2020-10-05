# -*- coding: utf-8 -*-
#
# This file is part of the CentralNode Low project
#
#
#
# Distributed under the terms of the BSD-3-Clause license.
# See LICENSE.txt for more info.

"""CentralNodeLow

Central Node Low is a coordinator of the complete M&C system.
"""

from . import release
from . import const
from .central_node_low import CentralNode

__all__ = ["release", "const", "CentralNode"]

__version__ = release.version
__version_info__ = release.version_info
__author__ = release.author
