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
import logging

class TangoClient:
    """
    
    """

    def __init__(self, fqdn):
        self.device_fqdn = fqdn
        self.deviceproxy = None
        retry = 0
        while retry < 3:
            try:
                self.deviceproxy = DeviceProxy(self.device_fqdn)
                break
            except DevFailed as df:
                # self.logger.exception(df)
                if retry >= 2:
                    tango.Except.re_throw_exception(df, "Retries exhausted while creating device proxy.",
                                                    "Failed to create DeviceProxy of " + str(self.device_fqdn),
                                                    "SubarrayNode.get_deviceproxy()", tango.ErrSeverity.ERR)
                retry += 1
                continue
        

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
                    # self.logger.exception(df)
                    if retry >= 2:
                        tango.Except.re_throw_exception(df, "Retries exhausted while creating device proxy.",
                                                        "Failed to create DeviceProxy of " + str(self.device_fqdn),
                                                        "SubarrayNode.get_deviceproxy()", tango.ErrSeverity.ERR)
                    retry += 1
                    continue
        return self.deviceproxy

    def get_device_fqdn(self):
        return self.device_fqdn

    def send_command_async(self, command_name, callback):
        """
        Here, as per the device proxy this function is invoking commands on respective nodes. This command invocation
        is on other than the TMC elements as it is asynchronous command execution.
        """
        try:
            self.deviceproxy.command_inout_asynch(command_name, [], callback)
            return True
        except DevFailed as dev_failed:
            log_msg = "Error in invoking command " + command_name + str(dev_failed)
            # self.logger.exception(dev_failed)
            tango.Except.throw_exception("Error in invoking command " + command_name,
                                         log_msg,
                                         "TangoClient.send_command_async",
                                         tango.ErrSeverity.ERR)
