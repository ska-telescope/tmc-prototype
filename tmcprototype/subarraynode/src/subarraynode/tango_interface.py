# -*- coding: utf-8 -*-
#
# This file is part of the SubarrayNode project
#
#
#
# Distributed under the terms of the BSD-3-Clause license.
# See LICENSE.txt for more info.

""" Tango Interface

"""
# Tango imports
import tango
from tango import AttrWriteType, DevFailed, DeviceProxy, EventType
from tango.server import run,attribute, command, device_property
from .const import GRP_DISH_LEAF_NODE

class TangoClient:
    """
    
    """

    def __init__(self, fqdn):
        self.fqdn = fqdn
        self.deviceproxy = None

    def create_tango_group(self, group_name):
        """
        Create Tango Group Command
        """
        return tango.Group(group_name)

    def get_deviceproxy(self):
        """
        Returns device proxy for given FQDN.
        """
        
        if self.deviceproxy == None:
            retry = 0
            while retry < 3:
                try:
                    self.deviceproxy = DeviceProxy(self.device_fqdn)
                    break
                except DevFailed as df:
                    self.logger.exception(df)
                    if retry >= 2:
                        tango.Except.re_throw_exception(df, "Retries exhausted while creating device proxy.",
                                                        "Failed to create DeviceProxy of " + str(self.device_fqdn),
                                                        "SubarrayNode.get_deviceproxy()", tango.ErrSeverity.ERR)
                    retry += 1
                    continue
        return self.deviceproxy

    def get_device_fqdn():
        return self.fqdn

    def send_command(self, command_name, input_data):
        """
        
        """
        self.device_proxy.command_inout(command_name, input_data)
