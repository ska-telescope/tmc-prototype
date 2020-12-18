# -*- coding: utf-8 -*-
#
# This file is part of the SubarrayNode project
#
#
#
# Distributed under the terms of the BSD-3-Clause license.
# See LICENSE.txt for more info.

""" Tango Group Client

"""
# Tango imports
import tango
from tango import AttrWriteType, DevFailed, DeviceProxy, EventType
from tango.server import run,attribute, command, device_property

import logging

LOGGER = logging.getLogger(__name__)

class TangoGroupClient:
    """
    
    """

    def __init__(self, group_name):
        self.tango_group = group_name
        self.tango_group = self.get_tango_group(group_name)
    
    def get_tango_group(self, group_name):
        """
        Create Tango Group Command
        """
        self.tango_group = tango.Group(group_name)

        return self.tango_group

    def add_device(self, devices_to_add):
        try:
            for device in devices_to_add:
                self.tango_group.add(device)
        except DevFailed as dev_failed:
            self.logger.exception("Failed to add device")
            tango.Except.re_throw_exception(dev_failed,
                "Failed to add device",
                str(dev_failed),
                "TangoGroupClient.add_device()",
                tango.ErrSeverity.ERR)  

    def remove_device(self, devices_to_remove):
        """
        Removes all elements in the Group.
        """
        try:
            for device in devices_to_remove:
                self.tango_group.remove(device)
        except DevFailed as dev_failed:
            self.logger.exception("Failed to remove device")
            tango.Except.re_throw_exception(dev_failed,
                "Failed to remove device",
                str(dev_failed),
                "TangoGroupClient.remove_device()",
                tango.ErrSeverity.ERR)

    def delete_group(self, group_to_delete):
        try:
            self.tango_group.delete(group_to_delete)
        except DevFailed as dev_failed:
            self.logger.exception("Failed to delete group")
            tango.Except.re_throw_exception(dev_failed,
                "Failed to remove device",
                str(dev_failed),
                "TangoGroupClient.delete_group()",
                tango.ErrSeverity.ERR)

    def get_group_device_list(self, forward=True):
        """
            :param argin: bool
            :return: The list of devices

            :rtype: str
        """
        try:
            self.tango_group.get_device_list()
            return True
        except DevFailed as dev_failed:
            self.logger.exception("Failed to get group device list")
            tango.Except.re_throw_exception(dev_failed,
                "Failed to get group device list",
                str(dev_failed),
                "TangoGroupClient.get_group_device_list()",
                tango.ErrSeverity.ERR)  
        
    def remove_all_device(self):
        return self.tango_group.remove_all()

    def send_command(self, command_name, input_arg = None):
        try:
            self.tango_group.command_inout(command_name, input_arg)
        except DevFailed as dev_failed:
            self.logger.exception("Failed to execute command .")
            tango.Except.re_throw_exception(dev_failed,
                "Failed to execute command .",
                str(dev_failed),
                "TangoGroupClient.send_command()",
                tango.ErrSeverity.ERR)  

    def send_command_async(self, command_name, input_arg = None):
        try:
            self.tango_group.command_inout_asynch(command_name, input_arg)
        except DevFailed as dev_failed:
            self.logger.exception("Failed to execute command .")
            tango.Except.re_throw_exception(dev_failed,
                "Failed to execute command .",
                str(dev_failed),
                "TangoGroupClient.send_command_async()",
                tango.ErrSeverity.ERR)      

def main(args=None, **kwargs):
    """
    Main function of the TangoGroupClient module.

    :param args: None
    :param kwargs:
    """
    return run((TangoGroupClient,), args=args, **kwargs)


if __name__ == '__main__':
    main()