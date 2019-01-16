# -*- coding: utf-8 -*-
#
# This file is part of the SubarrayNode project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

"""Subarray Node

Provides the monitoring and control interface required by users as well as 
other TM Components (such as OET, Central Node) for a Subarray.
"""

from . import release
from .SubarrayNode import SubarrayNode, main

__version__ = release.version
__version_info__ = release.version_info
__author__ = release.author
