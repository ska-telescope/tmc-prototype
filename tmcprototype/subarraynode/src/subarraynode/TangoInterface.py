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

class TangoInterface:
    """
    
    """

    def __init__(self, fqdn):
        self.device_fqdn = fqdn

    def create_tango_group(self):
        """
        Create Tango Group Command
        """
        return tango.Group(const.GRP_DISH_LEAF_NODE)

    def get_deviceproxy(self):
        """
        Returns device proxy for given FQDN.
        """
        retry = 0
        device_proxy = None
        while retry < 3:
            try:
                device_proxy = DeviceProxy(self.device_fqdn)
                break
            except DevFailed as df:
                self.logger.exception(df)
                if retry >= 2:
                    tango.Except.re_throw_exception(df, "Retries exhausted while creating device proxy.",
                                                    "Failed to create DeviceProxy of " + str(self.device_fqdn),
                                                    "SubarrayNode.get_deviceproxy()", tango.ErrSeverity.ERR)
                retry += 1
                continue
        return device_proxy

    def send_command(self, device_proxy, command_name, input_data):
        """
        
        """
        device_proxy.command_inout(command_name, input_data)
