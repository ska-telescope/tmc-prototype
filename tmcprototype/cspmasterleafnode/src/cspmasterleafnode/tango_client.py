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
LOGGER = logging.getLogger(__name__)

class TangoClient:
    """
    
    """

    def __init__(self, fqdn):
        self.device_fqdn = fqdn
        self.deviceproxy = None
        self.deviceproxy = self.get_deviceproxy()
        # retry = 0
        # while retry < 3:
        #     try:
        #         self.deviceproxy = DeviceProxy(self.device_fqdn)
        #         break
        #     except DevFailed as df:
        #         # self.logger.exception(df)
        #         if retry >= 2:
        #             tango.Except.re_throw_exception(df, "Retries exhausted while creating device proxy.",
        #                                             "Failed to create DeviceProxy of " + str(self.device_fqdn),
        #                                             "CspMasterLeafNode.get_deviceproxy()", tango.ErrSeverity.ERR)
        #         retry += 1
        #         continue


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
                                                        "CspMasterLeafNode.get_deviceproxy()", tango.ErrSeverity.ERR)
                    retry += 1
                    continue
        return self.deviceproxy

    def get_device_fqdn(self):
        return self.device_fqdn

    def send_command_async(self, command_name, callback, argin=None):
        """
        Here, as per the device proxy this function is invoking commands on respective nodes. This command invocation
        is on other than the TMC elements as it is asynchronous command execution.
        """
        try:
            self.deviceproxy.command_inout_asynch(command_name, argin, callback)
        except DevFailed as dev_failed:
            log_msg = "Error in invoking command " + command_name + str(dev_failed)
            tango.Except.throw_exception("Error in invoking command " + command_name,
                                         log_msg,
                                         "TangoClient.send_command_async",
                                         tango.ErrSeverity.ERR)

    def get_attribute(self, attribute_name):
        """
        Here, as per the attribute name this function will read the attribute of perticular device.
        """
        try:
            self.deviceproxy.read_attribute(attribute_name)
            return True
        except AttributeError as attribute_error:
            log_msg = attribute_name + "Attribute not found" + str(attribute_error)
            tango.Except.throw_exception(attribute + "Attribute not found",
                                         log_msg,
                                         "TangoClient.get_attribute",
                                         tango.ErrSeverity.ERR)

    def set_attribute(self, attribute_name, value):
        """
        Here, as per the attribute name this function will read the attribute of perticular device.
        """
        try:
            self.deviceproxy.write_attribute(attribute_name, value)
        except AttributeError as attribute_error:
            log_msg = attribute_name + "Attribute not found" + str(attribute_error)
            tango.Except.throw_exception(attribute + "Attribute not found",
                                         log_msg,
                                         "TangoClient.set_attribute",
                                         tango.ErrSeverity.ERR)

    def subscribe_attribute(self, attr_name, callback_method):
        """
        Subscribes the attribute on Change event
        """
        try:
            event_id = self.deviceproxy.subscribe_event(attr_name, EventType.CHANGE_EVENT, callback_method, stateless=True)
            return event_id
        except DevFailed as dev_failed:
            tango.Except.throw_exception("Error is subscribing event",
                                         dev_failed,
                                         "TangoClient.subscribe_attribute",
                                         tango.ErrSeverity.ERR)

    def unsubscribe_attr(self, event_id):
        """
        Unsubscribes the attribute change event
        """
        try:
            self.deviceproxy.unsubscribe_event(event_id)
        except DevFailed as dev_failed:
            log_message = "Failed to unsubscribe event {}.".format(dev_failed)
            self.logger.error(log_message)
