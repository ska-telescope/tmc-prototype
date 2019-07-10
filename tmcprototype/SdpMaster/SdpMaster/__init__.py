# -*- coding: utf-8 -*-
#
# This file is part of the SdpMaster project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

"""SdpMaster

The SDP Master implements internal monitor and control functionality for its underlying components
and provides a high-level interface which allows TMC to monitor the status of equipment and processing
resources, and to configure and control the signal processing functions.
"""

from . import release
from .SdpMaster import SdpMaster, main

__all__ = ["SdpMaster", "release"]

__version__ = release.version
__version_info__ = release.version_info
__author__ = release.author
