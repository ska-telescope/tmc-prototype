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
    # PROTECTED REGION ID(CspMasterLeafNode.class_variable) ENABLED START #
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
        self._read_activity_message = CONST.STR_CSP_INIT_SUCCESS
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

        # Subscribing to DishMaster Attributes
        try:
            self._csp_proxy.subscribe_event(CONST.EVT_DISH_MODE, EventType.CHANGE_EVENT,
                                             self.dishModeCallback, stateless=True)
        except:
            pass
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
        return ''
        # PROTECTED REGION END #    //  CspMasterLeafNode.activityMessage_read

    def write_activityMessage(self, value):
        # PROTECTED REGION ID(CspMasterLeafNode.activityMessage_write) ENABLED START #
        pass
        # PROTECTED REGION END #    //  CspMasterLeafNode.activityMessage_write


    # --------
    # Commands
    # --------

    @command(
    dtype_in=('str',), 
    doc_in="If the array length is 0, the command applies to the whole\nCSP Element.\nIf the array length is > 1, each array element specifies the FQDN of the\nCSP SubElement to switch ON.", 
    )
    @DebugIt()
    def On(self, argin):
        # PROTECTED REGION ID(CspMasterLeafNode.On) ENABLED START #
        pass
        # PROTECTED REGION END #    //  CspMasterLeafNode.On

    @command(
    dtype_in=('str',), 
    doc_in="If the array length is 0, the command applies to the whole\nCSP Element.\nIf the array length is > 1, each array element specifies the FQDN of the\nCSP SubElement to switch OFF.", 
    )
    @DebugIt()
    def Off(self, argin):
        # PROTECTED REGION ID(CspMasterLeafNode.Off) ENABLED START #
        pass
        # PROTECTED REGION END #    //  CspMasterLeafNode.Off

    @command(
    dtype_in=('str',), 
    doc_in="If the array length is 0, the command applies to the whole\nCSP Element.\nIf the array length is > 1, each array element specifies the FQDN of the\nCSP SubElement to put in STANDBY mode.", 
    )
    @DebugIt()
    def Standby(self, argin):
        # PROTECTED REGION ID(CspMasterLeafNode.Standby) ENABLED START #
        pass
        # PROTECTED REGION END #    //  CspMasterLeafNode.Standby

    @command(
    dtype_in='DevEnum', 
    doc_in="adminMode", 
    )
    @DebugIt()
    def SetCbfAdminMode(self, argin):
        # PROTECTED REGION ID(CspMasterLeafNode.SetCbfAdminMode) ENABLED START #
        pass
        # PROTECTED REGION END #    //  CspMasterLeafNode.SetCbfAdminMode

    @command(
    dtype_in='DevEnum', 
    doc_in="adminMode", 
    )
    @DebugIt()
    def SetPssAdminMode(self, argin):
        # PROTECTED REGION ID(CspMasterLeafNode.SetPssAdminMode) ENABLED START #
        pass
        # PROTECTED REGION END #    //  CspMasterLeafNode.SetPssAdminMode

    @command(
    dtype_in='DevEnum', 
    doc_in="adminMode", 
    )
    @DebugIt()
    def SetPstAdminMode(self, argin):
        # PROTECTED REGION ID(CspMasterLeafNode.SetPstAdminMode) ENABLED START #
        pass
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
