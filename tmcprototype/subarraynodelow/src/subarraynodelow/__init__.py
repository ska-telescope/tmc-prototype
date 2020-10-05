# -*- coding: utf-8 -*-
#
# This file is part of the SubarrayNode Low project
#
#
#
# Distributed under the terms of the BSD-3-Clause license.
# See LICENSE.txt for more info.

"""SubarrayNodeLow

Provides the monitoring and control interface required by users as well as
other TM Components (such as OET, Central Node) for a SKA Low Subarray.
"""

from . import release
from . import const
from .subarray_node_low import SubarrayNode, SubarrayHealthState
from .configure_command import ElementDeviceData

__all__ = ["SubarrayNode", "ElementDeviceData", "SubarrayHealthState", "const", "release"]

__version__ = release.version
__version_info__ = release.version_info
__author__ = release.author
