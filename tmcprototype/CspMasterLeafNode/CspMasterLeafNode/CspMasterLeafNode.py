# -*- coding: utf-8 -*-
#
# This file is part of the CspMasterLeafNode project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

""" CspMasterLeafNode

"""

from __future__ import print_function
from __future__ import absolute_import

import sys
import os
file_path = os.path.dirname(os.path.abspath(__file__))
module_path = os.path.abspath(os.path.join(file_path, os.pardir)) + "/CspMasterLeafNode"
sys.path.insert(0, module_path)
print("sys.path: ", sys.path)

# PyTango imports
import tango
from tango import DeviceProxy, EventType, ApiUtil, DebugIt, DevState, AttrWriteType
from tango.server import run, DeviceMeta, command, device_property, attribute, Device
from skabase.SKABaseDevice.SKABaseDevice import SKABaseDevice
# Additional import
# PROTECTED REGION ID(CspMasterLeafNode.additionnal_import) ENABLED START #
from future.utils import with_metaclass
import CONST
# PROTECTED REGION END #    //  CspMasterLeafNode.additionnal_import

__all__ = ["CspMasterLeafNode", "main"]


class CspMasterLeafNode(SKABaseDevice):
    """
    """
    __metaclass__ = DeviceMeta
    # PROTECTED REGION ID(CspMasterLeafNode.class_variable) ENABLED START #\
    def cspCbfHealthCallback(self, evt):
        """
        Retrieves the subscribed cspCbfHealthState attribute of CSPMaster.
        :param evt: A TANGO_CHANGE event on cspCbfHealthState attribute.
        :return: None
        """
        if evt.err is False:
            try:
                self._csp_cbf_health = evt.attr_value.value
                if self._csp_cbf_health == 0:
                    print(CONST.STR_CSP_CBF_HEALTH_OK)
                    self._read_activity_message = CONST.STR_CSP_CBF_HEALTH_OK
                elif self._csp_cbf_health == 1:
                    print(CONST.STR_CSP_CBF_HEALTH_DEGRADED)
                    self._read_activity_message = CONST.STR_CSP_CBF_HEALTH_DEGRADED
                elif self._csp_cbf_health == 2:
                    print(CONST.STR_CSP_CBF_HEALTH_FAILED)
                    self._read_activity_message = CONST.STR_CSP_CBF_HEALTH_FAILED
                else:
                    print(CONST.STR_CSP_CBF_HEALTH_UNKNOWN)
                    self._read_activity_message = CONST.STR_CSP_CBF_HEALTH_UNKNOWN
            except Exception as except_occurred:
                print(CONST.ERR_CSP_CBF_HEALTH_CB, except_occurred.message)
                self._read_activity_message = CONST.ERR_CSP_CBF_HEALTH_CB + str(except_occurred.message)
                self.dev_logging(CONST.ERR_CSP_CBF_HEALTH_CB, int(tango.LogLevel.LOG_ERROR))
        else:
            print(CONST.ERR_ON_SUBS_CSP_CBF_HEALTH, evt.errors)
            self._read_activity_message = CONST.ERR_ON_SUBS_CSP_CBF_HEALTH + str(evt.errors)
            self.dev_logging(CONST.ERR_ON_SUBS_CSP_CBF_HEALTH, int(tango.LogLevel.LOG_ERROR))

    def cspPssHealthCallback(self, evt):
        """
                Retrieves the subscribed cspPssHealthState attribute of CSPMaster.
                :param evt: A TANGO_CHANGE event on cspPssHealthState attribute.
                :return: None
                """
        if evt.err is False:
            try:
                self._csp_pss_health = evt.attr_value.value
                if self._csp_pss_health == 0:
                    print(CONST.STR_CSP_PSS_HEALTH_OK)
                    self._read_activity_message = CONST.STR_CSP_PSS_HEALTH_OK
                elif self._csp_pss_health == 1:
                    print(CONST.STR_CSP_PSS_HEALTH_DEGRADED)
                    self._read_activity_message = CONST.STR_CSP_PSS_HEALTH_DEGRADED
                elif self._csp_pss_health == 2:
                    print(CONST.STR_CSP_PSS_HEALTH_FAILED)
                    self._read_activity_message = CONST.STR_CSP_PSS_HEALTH_FAILED
                else:
                    print(CONST.STR_CSP_PSS_HEALTH_UNKNOWN)
                    self._read_activity_message = CONST.STR_CSP_PSS_HEALTH_UNKNOWN
            except Exception as except_occurred:
                print(CONST.ERR_CSP_PSS_HEALTH_CB, except_occurred.message)
                self._read_activity_message = CONST.ERR_CSP_PSS_HEALTH_CB + str(except_occurred.message)
                self.dev_logging(CONST.ERR_CSP_PSS_HEALTH_CB, int(tango.LogLevel.LOG_ERROR))
        else:
            print(CONST.ERR_ON_SUBS_CSP_PSS_HEALTH, evt.errors)
            self._read_activity_message = CONST.ERR_ON_SUBS_CSP_PSS_HEALTH + str(evt.errors)
            self.dev_logging(CONST.ERR_ON_SUBS_CSP_PSS_HEALTH, int(tango.LogLevel.LOG_ERROR))

    def cspPstHealthCallback(self, evt):
        """
                Retrieves the subscribed cspPstHealthState attribute of CSPMaster.
                :param evt: A TANGO_CHANGE event on cspPstHealthState attribute.
                :return: None
                """
        if evt.err is False:
            try:
                self._csp_pst_health = evt.attr_value.value
                if self._csp_pst_health == 0:
                    print(CONST.STR_CSP_PST_HEALTH_OK)
                    self._read_activity_message = CONST.STR_CSP_PST_HEALTH_OK
                elif self._csp_pst_health == 1:
                    print(CONST.STR_CSP_PST_HEALTH_DEGRADED)
                    self._read_activity_message = CONST.STR_CSP_PST_HEALTH_DEGRADED
                elif self._csp_pst_health == 2:
                    print(CONST.STR_CSP_PST_HEALTH_FAILED)
                    self._read_activity_message = CONST.STR_CSP_PST_HEALTH_FAILED
                else:
                    print(CONST.STR_CSP_PST_HEALTH_UNKNOWN)
                    self._read_activity_message = CONST.STR_CSP_PST_HEALTH_UNKNOWN
            except Exception as except_occurred:
                print(CONST.ERR_CSP_PST_HEALTH_CB, except_occurred.message)
                self._read_activity_message = CONST.ERR_CSP_PST_HEALTH_CB + str(except_occurred.message)
                self.dev_logging(CONST.ERR_CSP_PST_HEALTH_CB, int(tango.LogLevel.LOG_ERROR))
        else:
            print(CONST.ERR_ON_SUBS_CSP_PST_HEALTH, evt.errors)
            self._read_activity_message = CONST.ERR_ON_SUBS_CSP_PST_HEALTH + str(evt.errors)
            self.dev_logging(CONST.ERR_ON_SUBS_CSP_PST_HEALTH, int(tango.LogLevel.LOG_ERROR))

    def commandCallback(self, event):
        """
        Checks whether the command has been successfully invoked on CSPMaster.
        :param event: response from CspMaster for the invoked command
        :return: None
        """
        try:
            if event.err:
                log = CONST.ERR_INVOKING_CMD + event.cmd_name
                print(CONST.ERR_INVOKING_CMD + event.cmd_name + "\n" + str(event.errors))
                self._read_activity_message = CONST.ERR_INVOKING_CMD + str(event.cmd_name) + "\n" + str(
                    event.errors)
                self.dev_logging(log, int(tango.LogLevel.LOG_ERROR))
            else:
                log = CONST.STR_COMMAND + event.cmd_name + CONST.STR_INVOKE_SUCCESS
                self._read_activity_message = log
                self.dev_logging(log, int(tango.LogLevel.LOG_INFO))
        except Exception as except_occurred:
            print(CONST.ERR_EXCEPT_CMD_CB, except_occurred)
            self._read_activity_message = CONST.ERR_EXCEPT_CMD_CB + str(except_occurred)
            self.dev_logging(CONST.ERR_EXCEPT_CMD_CB, int(tango.LogLevel.LOG_ERROR))



    # PROTECTED REGION END #    //  CspMasterLeafNode.class_variable

    # -----------------
    # Device Properties
    # -----------------






    CspMasterFQDN = device_property(
        dtype='str',
    )

    # ----------
    # Attributes
    # ----------











    activityMessage = attribute(
        dtype='str',
        access=AttrWriteType.READ_WRITE,
    )

    cspHealthState = attribute(name="cspHealthState", label="cspHealthState", forwarded=True)
    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        SKABaseDevice.init_device(self)
        # PROTECTED REGION ID(CspMasterLeafNode.init_device) ENABLED START #
        self._read_activity_message = CONST.STR_CSP_INIT_LEAF_NODE
        self.SkaLevel = 3

        try:
            print(CONST.STR_CSPMASTER_FQDN, self.CspMasterFQDN)
            self._read_activity_message = CONST.STR_CSPMASTER_FQDN + str(self.CspMasterFQDN)
            self._csp_proxy = DeviceProxy(self.CspMasterFQDN)   #Creating proxy to the CSPMaster
        except Exception as except_occurred:
            print(CONST.ERR_IN_CREATE_PROXY_CSP_MASTER, except_occurred)
            self._read_activity_message = CONST.ERR_IN_CREATE_PROXY_CSP_MASTER + str(except_occurred)
            self.set_state(DevState.FAULT)

        self._admin_mode = 0  # Setting adminMode to "ONLINE"
        self._health_state = 0  # Setting healthState to "OK"
        self._simulation_mode = False  # Enabling the simulation mode

        ApiUtil.instance().set_asynch_cb_sub_model(tango.cb_sub_model.PUSH_CALLBACK)
        print(CONST.STR_SETTING_CB_MODEL, ApiUtil.instance().get_asynch_cb_sub_model())
        self._read_activity_message = CONST.STR_SETTING_CB_MODEL + str(
            ApiUtil.instance().get_asynch_cb_sub_model())

        # Subscribing to CSPMaster Attributes
        try:
            self._csp_proxy.subscribe_event(CONST.EVT_CBF_HEALTH, EventType.CHANGE_EVENT,
                                             self.cspCbfHealthCallback, stateless=True)
            self._csp_proxy.subscribe_event(CONST.EVT_PSS_HEALTH, EventType.CHANGE_EVENT,
                                            self.cspPssHealthCallback, stateless=True)
            self._csp_proxy.subscribe_event(CONST.EVT_PST_HEALTH, EventType.CHANGE_EVENT,
                                            self.cspPstHealthCallback, stateless=True)

            self.set_state(DevState.ON)
            self.set_status(CONST.STR_CSP_MASTER_INIT_SUCCESS)
            self.dev_logging(CONST.STR_CSP_MASTER_INIT_SUCCESS, int(tango.LogLevel.LOG_INFO))

        except Exception as except_occurred:
            print(CONST.ERR_SUBS_CSP_MASTER_ATTR, except_occurred)
            self._read_activity_message = CONST.ERR_SUBS_CSP_MASTER_ATTR + str(except_occurred)
            self.set_state(DevState.FAULT)
            self.set_status(CONST.ERR_CSP_MASTER_INIT)
            self.dev_logging(CONST.ERR_CSP_MASTER_INIT, int(tango.LogLevel.LOG_ERROR))
        # PROTECTED REGION END #    //  CspMasterLeafNode.init_device

    def always_executed_hook(self):
        # PROTECTED REGION ID(CspMasterLeafNode.always_executed_hook) ENABLED START #
        pass
        # PROTECTED REGION END #    //  CspMasterLeafNode.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(CspMasterLeafNode.delete_device) ENABLED START #
        pass
        # PROTECTED REGION END #    //  CspMasterLeafNode.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    def read_activityMessage(self):
        # PROTECTED REGION ID(CspMasterLeafNode.activityMessage_read) ENABLED START #
        """ Returns the activityMessage """
        return self._read_activity_message
        # PROTECTED REGION END #    //  CspMasterLeafNode.activityMessage_read

    def write_activityMessage(self, value):
        # PROTECTED REGION ID(CspMasterLeafNode.activityMessage_write) ENABLED START #
        """ Sets the activityMessage """
        self._read_activity_message = value
        # PROTECTED REGION END #    //  CspMasterLeafNode.activityMessage_write


    # --------
    # Commands
    # --------

    @command(
    dtype_in=('str',), 
    doc_in="If the array length is 0, the command applies to the whole\nCSP Element.\nIf the array "
           "length is > 1, each array element specifies the FQDN of the\nCSP SubElement to switch ON.",
    )
    @DebugIt()
    def On(self, argin):
        # PROTECTED REGION ID(CspMasterLeafNode.On) ENABLED START #
        """ Triggers On the CSPMaster"""
        self._csp_proxy.command_inout_asynch(CONST.CMD_ON, argin, self.commandCallback)

        # PROTECTED REGION END #    //  CspMasterLeafNode.On

    @command(
    dtype_in=('str',), 
    doc_in="If the array length is 0, the command applies to the whole\nCSP Element.\nIf the array "
           "length is > 1, each array element specifies the FQDN of the\nCSP SubElement to switch OFF.",
    )
    @DebugIt()
    def Off(self, argin):
        # PROTECTED REGION ID(CspMasterLeafNode.Off) ENABLED START #
        """ Triggers Off the CSPMaster"""
        self._csp_proxy.command_inout_asynch(CONST.CMD_OFF, self.commandCallback)

        # PROTECTED REGION END #    //  CspMasterLeafNode.Off

    @command(
    dtype_in=('str',), 
    doc_in="If the array length is 0, the command applies to the whole\nCSP Element.\nIf the array "
           "length is > 1, each array element specifies the FQDN of the\nCSP SubElement to put in "
           "STANDBY mode.",
    )
    @DebugIt()
    def Standby(self, argin):
        # PROTECTED REGION ID(CspMasterLeafNode.Standby) ENABLED START #
        """ Sets Standby Mode on the CSPMaster"""
        self._csp_proxy.command_inout_asynch(CONST.CMD_STANDBY, self.commandCallback)

        # PROTECTED REGION END #    //  CspMasterLeafNode.Standby

    @command(
    dtype_in='DevEnum', 
    doc_in="adminMode", 
    )
    @DebugIt()
    def SetCbfAdminMode(self, argin):
        # PROTECTED REGION ID(CspMasterLeafNode.SetCbfAdminMode) ENABLED START #
        """Sets Admin Mode of the CSP Cbf"""
        self._csp_proxy.command_inout_asynch(CONST.CMD_SET_CBF_ADMIN_MODE, self.commandCallback)
        # PROTECTED REGION END #    //  CspMasterLeafNode.SetCbfAdminMode

    @command(
    dtype_in='DevEnum', 
    doc_in="adminMode", 
    )
    @DebugIt()
    def SetPssAdminMode(self, argin):
        # PROTECTED REGION ID(CspMasterLeafNode.SetPssAdminMode) ENABLED START #
        """Sets Admin Mode of the CSP Pss"""
        self._csp_proxy.command_inout_asynch(CONST.CMD_SET_PSS_ADMIN_MODE, self.commandCallback)
        # PROTECTED REGION END #    //  CspMasterLeafNode.SetPssAdminMode

    @command(
    dtype_in='DevEnum', 
    doc_in="adminMode", 
    )
    @DebugIt()
    def SetPstAdminMode(self, argin):
        # PROTECTED REGION ID(CspMasterLeafNode.SetPstAdminMode) ENABLED START #
        """Sets Admin Mode of the CSP Pst"""
        self._csp_proxy.command_inout_asynch(CONST.CMD_SET_PST_ADMIN_MODE, self.commandCallback)
        # PROTECTED REGION END #    //  CspMasterLeafNode.SetPstAdminMode

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(CspMasterLeafNode.main) ENABLED START #
    return run((CspMasterLeafNode,), args=args, **kwargs)
    # PROTECTED REGION END #    //  CspMasterLeafNode.main

if __name__ == '__main__':
    main()
