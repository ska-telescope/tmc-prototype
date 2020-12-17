# -*- coding: utf-8 -*-
#
# This file is part of the SubarrayNode project
#
#
#
# Distributed under the terms of the BSD-3-Clause license.
# See LICENSE.txt for more info.

""" Tango Server

"""
# Tango imports
import tango
from tango import AttrWriteType, DevFailed, DeviceProxy, EventType
from tango.server import run,attribute, command, device_property
from .const import GRP_DISH_LEAF_NODE
import logging

class TangoServer:
    """
    
    """
    __instance = None

    def __init__(self):
        """Private constructor of the class""" 
        if TangoServer.__instance != None:
            raise Exception("This is singletone class")
        else:
            TangoServer.__instance = self
        self.device = None

    @staticmethod
    def get_instance():
        if TangoServer.__instance == None:
            TangoServer()
        return TangoServer.__instance

    
    def get_attribute(self):
        """
        """
        pass

    def set_attribute(self):
        """
        """
        pass
        