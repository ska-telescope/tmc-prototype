# -*- coding: utf-8 -*-
#
# This file is part of the SubarrayNode project
#
#
#
# Distributed under the terms of the BSD-3-Clause license.
# See LICENSE.txt for more info.

"""Subarray Node

Provides the monitoring and control interface required by users as well as
other TM Components (such as OET, Central Node) for a Subarray.
"""

from . import release
from . import const
from .subarray_node import SubarrayNode
from .configure_command import ElementDeviceData
from .device_data import DeviceData
from .scan_command import Scan

__all__ = ["SubarrayNode", "ElementDeviceData", "const", "release", "DeviceData", "Scan"]

__version__ = release.version
__version_info__ = release.version_info
__author__ = release.author
