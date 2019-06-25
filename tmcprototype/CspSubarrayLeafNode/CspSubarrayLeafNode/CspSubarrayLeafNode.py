# -*- coding: utf-8 -*-
#
# This file is part of the CspSubarrayLeafNode project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

""" 

"""

# PyTango imports
import PyTango
from PyTango import DebugIt
from PyTango.server import run
from PyTango.server import Device, DeviceMeta
from PyTango.server import attribute, command
from PyTango.server import device_property
from PyTango import AttrQuality, DispLevel, DevState
from PyTango import AttrWriteType, PipeWriteType
from skabase.SKABaseDevice.SKABaseDevice import SKABaseDevice
# Additional import
# PROTECTED REGION ID(CspSubarrayLeafNode.additionnal_import) ENABLED START #
import sys
import os
file_path = os.path.dirname(os.path.abspath(__file__))
module_path = os.path.abspath(os.path.join(file_path, os.pardir)) + "/CspSubarrayLeafNode"
sys.path.insert(0, module_path)
# PROTECTED REGION END #    //  CspSubarrayLeafNode.additionnal_import

__all__ = ["CspSubarrayLeafNode", "main"]


class CspSubarrayLeafNode(SKABaseDevice):
    """
    """
    __metaclass__ = DeviceMeta
    # PROTECTED REGION ID(CspSubarrayLeafNode.class_variable) ENABLED START #
    # PROTECTED REGION END #    //  CspSubarrayLeafNode.class_variable

    # -----------------
    # Device Properties
    # -----------------






    SkaLevel = device_property(
        dtype='int16', default_value=3
    )

    CspSubarrayNodeFQDN = device_property(
        dtype='str', default_value="mid-csp/elt/subarray01"
    )

    # ----------
    # Attributes
    # ----------











    state = attribute(
        dtype='DevEnum',
        enum_labels=["INIT", "ON", "ALARM", "FAULT", "UNKNOWN", "DISABLE", ],
    )

    delayModel = attribute(
        dtype='str',
        access=AttrWriteType.READ_WRITE,
    )

    visDestinationAddress = attribute(
        dtype='str',
        access=AttrWriteType.READ_WRITE,
    )

    CspSubarrayHealthState = attribute(
        dtype='DevEnum',
        enum_labels=["OK", "DEGRADED", "FAILED", "UNKNOWN", ],
    )

    versionInfo = attribute(
        dtype='str',
    )

    activityMessage = attribute(
        dtype='str',
        access=AttrWriteType.READ_WRITE,
    )

    opState = attribute(
        dtype='DevEnum',
        enum_labels=["INIT", "OFF", "ON", "ALARM", "DISABLE", "FAULT", "UNKNOWN", ],
    )

    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        SKABaseDevice.init_device(self)
        # PROTECTED REGION ID(CspSubarrayLeafNode.init_device) ENABLED START #
        self._state = 0
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.init_device

    def always_executed_hook(self):
        # PROTECTED REGION ID(CspSubarrayLeafNode.always_executed_hook) ENABLED START #
        pass
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(CspSubarrayLeafNode.delete_device) ENABLED START #
        pass
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    def read_state(self):
        # PROTECTED REGION ID(CspSubarrayLeafNode.state_read) ENABLED START #
        return self._state
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.state_read

    def read_delayModel(self):
        # PROTECTED REGION ID(CspSubarrayLeafNode.delayModel_read) ENABLED START #
        return ''
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.delayModel_read

    def write_delayModel(self, value):
        # PROTECTED REGION ID(CspSubarrayLeafNode.delayModel_write) ENABLED START #
        pass
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.delayModel_write

    def read_visDestinationAddress(self):
        # PROTECTED REGION ID(CspSubarrayLeafNode.visDestinationAddress_read) ENABLED START #
        return ''
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.visDestinationAddress_read

    def write_visDestinationAddress(self, value):
        # PROTECTED REGION ID(CspSubarrayLeafNode.visDestinationAddress_write) ENABLED START #
        pass
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.visDestinationAddress_write

    def read_CspSubarrayHealthState(self):
        # PROTECTED REGION ID(CspSubarrayLeafNode.CspSubarrayHealthState_read) ENABLED START #
        return 0
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.CspSubarrayHealthState_read

    def read_versionInfo(self):
        # PROTECTED REGION ID(CspSubarrayLeafNode.versionInfo_read) ENABLED START #
        return ''
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.versionInfo_read

    def read_activityMessage(self):
        # PROTECTED REGION ID(CspSubarrayLeafNode.activityMessage_read) ENABLED START #
        return ''
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.activityMessage_read

    def write_activityMessage(self, value):
        # PROTECTED REGION ID(CspSubarrayLeafNode.activityMessage_write) ENABLED START #
        pass
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.activityMessage_write

    def read_opState(self):
        # PROTECTED REGION ID(CspSubarrayLeafNode.opState_read) ENABLED START #
        return 0
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.opState_read


    # --------
    # Commands
    # --------

    @command(
    dtype_in='str', 
    )
    @DebugIt()
    def ConfigureScan(self, argin):
        # PROTECTED REGION ID(CspSubarrayLeafNode.ConfigureScan) ENABLED START #
        pass
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.ConfigureScan

    @command(
    dtype_in='str', 
    )
    @DebugIt()
    def StartScan(self, argin):
        # PROTECTED REGION ID(CspSubarrayLeafNode.StartScan) ENABLED START #
        pass
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.StartScan

    @command(
    dtype_in='str', 
    )
    @DebugIt()
    def EndScan(self, argin):
        # PROTECTED REGION ID(CspSubarrayLeafNode.EndScan) ENABLED START #
        pass
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.EndScan

    @command(
    )
    @DebugIt()
    def ReleaseResources(self):
        # PROTECTED REGION ID(CspSubarrayLeafNode.ReleaseResources) ENABLED START #
        pass
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.ReleaseResources

    @command(
    dtype_in=('str',), 
    )
    @DebugIt()
    def AssignResources(self, argin):
        # PROTECTED REGION ID(CspSubarrayLeafNode.AssignResources) ENABLED START #
        pass
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.AssignResources

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(CspSubarrayLeafNode.main) ENABLED START #
    return run((CspSubarrayLeafNode,), args=args, **kwargs)
    # PROTECTED REGION END #    //  CspSubarrayLeafNode.main

if __name__ == '__main__':
    main()
