# -*- coding: utf-8 -*-
#
# This file is part of the ska-tmc-common project
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
import logging

class TangoServerHelper:
    """
    Helper class for TangoServer API
    """
    __instance = None

    def __init__(self):
        """Private constructor of the class""" 
        if TangoServerHelper.__instance is not None:
            raise Exception("This is singletone class")
        else:
            TangoServerHelper.__instance = self
        self.device = None
        # For property access
        # Maintain a map
        # key of map is the string containing property name
        # value of map is the tango.property class object (defined in Tango class)
        self.prop_map = dict("DishLeafNodePrefix", self.device.DishLeafNodePrefix)

    @staticmethod
    def get_instance():
        """
        Returns instance of TangoServerHelper class
        """
        if TangoServerHelper.__instance is None:
            TangoServerHelper()
        return TangoServerHelper.__instance

    def get_property(self, prop):
        """
        Returns the value of given device property
        """
        return self.prop_map[prop]
    
    def set_property(self, prop, attr_val):
        """
        Sets the value to a given device property
        """
        self.prop_map[prop].value = attr_val

    def get_status(self):
        """
        Get status of Tango device server
        """
        try:
            self.device.get_status()
        except DevFailed as dev_failed:
            # self.logger.exception("Failed to get status.")
            tango.Except.re_throw_exception(dev_failed,
                "Failed to get status .",
                str(dev_failed),
                "TangoGroupClient.get_status()",
                tango.ErrSeverity.ERR)      
        return self.device.get_status()

    def set_status(self, new_status):
        """
        Set device status.
        """
        try:
            self.device.set_status(new_status)
        except DevFailed as dev_failed:
            #self.logger.exception("Failed to set status.")
            tango.Except.re_throw_exception(dev_failed,
                "Failed to set status .",
                str(dev_failed),
                "TangoGroupClient.set_status()",
                tango.ErrSeverity.ERR)      

    def get_state(self):
        """
        Get a COPY of the device state.
        """
        try:
            self.device.get_state()
        except DevFailed as dev_failed:
            #self.logger.exception("Failed to get state.")
            tango.Except.re_throw_exception(dev_failed,
                "Failed to get state .",
                str(dev_failed),
                "TangoGroupClient.get_state()",
                tango.ErrSeverity.ERR)      
        return self.device.get_state()

    def set_state(self, new_state):
        """
        Set device state.
        """
        try:
            self.device.set_state(new_state)
        except DevFailed as dev_failed:
            # self.logger.exception("Failed to set state.")
            tango.Except.re_throw_exception(dev_failed,
                "Failed to set state .",
                str(dev_failed),
                "TangoGroupClient.set_state()",
                tango.ErrSeverity.ERR)      

def main(args=None, **kwargs):
    """
    Main function of the TangoServerHelper module.

    :param args: None
    :param kwargs:
    """
    return run((TangoServerHelper,), args=args, **kwargs)


if __name__ == '__main__':
    main()
        