# -*- coding: utf-8 -*-
#
# This file is part of the MCCSSubarrayLeafNode project
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
from SKABaseDevice import SKABaseDevice
# Additional import
# PROTECTED REGION ID(MCCSSubarrayLeafNode.additionnal_import) ENABLED START #
# PROTECTED REGION END #    //  MCCSSubarrayLeafNode.additionnal_import

__all__ = ["MCCSSubarrayLeafNode", "main"]


class MCCSSubarrayLeafNode(SKABaseDevice):
    """
    """
    __metaclass__ = DeviceMeta
    # PROTECTED REGION ID(MCCSSubarrayLeafNode.class_variable) ENABLED START #
    # PROTECTED REGION END #    //  MCCSSubarrayLeafNode.class_variable

    # -----------------
    # Device Properties
    # -----------------





    MCCSSubarrayFQDN = device_property(
        dtype='str', default_value="low_mccs/elt/subarray_01"
    )

    # ----------
    # Attributes
    # ----------









    activitymessage = attribute(
        dtype='str',
        access=AttrWriteType.READ_WRITE,
    )


    mccssubarrayHealthState = attribute(label="mccssubarrayHealthState",
        forwarded=True
    )
    mccsSubarrayObsState = attribute(label="mccsSubarrayObsState",
        forwarded=True
    )
    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        SKABaseDevice.init_device(self)
        self.set_change_event("adminMode", True, True)
        self.set_archive_event("adminMode", True, True)
        # PROTECTED REGION ID(MCCSSubarrayLeafNode.init_device) ENABLED START #
        # PROTECTED REGION END #    //  MCCSSubarrayLeafNode.init_device

    def always_executed_hook(self):
        # PROTECTED REGION ID(MCCSSubarrayLeafNode.always_executed_hook) ENABLED START #
        pass
        # PROTECTED REGION END #    //  MCCSSubarrayLeafNode.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(MCCSSubarrayLeafNode.delete_device) ENABLED START #
        pass
        # PROTECTED REGION END #    //  MCCSSubarrayLeafNode.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    def read_activitymessage(self):
        # PROTECTED REGION ID(MCCSSubarrayLeafNode.activitymessage_read) ENABLED START #
        return ''
        # PROTECTED REGION END #    //  MCCSSubarrayLeafNode.activitymessage_read

    def write_activitymessage(self, value):
        # PROTECTED REGION ID(MCCSSubarrayLeafNode.activitymessage_write) ENABLED START #
        pass
        # PROTECTED REGION END #    //  MCCSSubarrayLeafNode.activitymessage_write


    # --------
    # Commands
    # --------

    @command(
    dtype_in='str', 
    dtype_out='str', 
    )
    @DebugIt()
    def AssignResources(self, argin):
        # PROTECTED REGION ID(MCCSSubarrayLeafNode.AssignResources) ENABLED START #
        return ""
        # PROTECTED REGION END #    //  MCCSSubarrayLeafNode.AssignResources

    @command(
    dtype_in='str', 
    dtype_out='str', 
    )
    @DebugIt()
    def ReleaseResources(self, argin):
        # PROTECTED REGION ID(MCCSSubarrayLeafNode.ReleaseResources) ENABLED START #
        return ""
        # PROTECTED REGION END #    //  MCCSSubarrayLeafNode.ReleaseResources

    @command(
    dtype_in='str', 
    )
    @DebugIt()
    def Configure(self, argin):
        # PROTECTED REGION ID(MCCSSubarrayLeafNode.Configure) ENABLED START #
        pass
        # PROTECTED REGION END #    //  MCCSSubarrayLeafNode.Configure

    @command(
    dtype_in=('str',), 
    )
    @DebugIt()
    def Scan(self, argin):
        # PROTECTED REGION ID(MCCSSubarrayLeafNode.Scan) ENABLED START #
        pass
        # PROTECTED REGION END #    //  MCCSSubarrayLeafNode.Scan

    @command(
    )
    @DebugIt()
    def EndScan(self):
        # PROTECTED REGION ID(MCCSSubarrayLeafNode.EndScan) ENABLED START #
        pass
        # PROTECTED REGION END #    //  MCCSSubarrayLeafNode.EndScan

    @command(
    )
    @DebugIt()
    def End(self):
        # PROTECTED REGION ID(MCCSSubarrayLeafNode.End) ENABLED START #
        pass
        # PROTECTED REGION END #    //  MCCSSubarrayLeafNode.End

    @command(
    )
    @DebugIt()
    def Abort(self):
        # PROTECTED REGION ID(MCCSSubarrayLeafNode.Abort) ENABLED START #
        pass
        # PROTECTED REGION END #    //  MCCSSubarrayLeafNode.Abort

    @command(
    )
    @DebugIt()
    def Restart(self):
        # PROTECTED REGION ID(MCCSSubarrayLeafNode.Restart) ENABLED START #
        pass
        # PROTECTED REGION END #    //  MCCSSubarrayLeafNode.Restart

    @command(
    )
    @DebugIt()
    def obsReset(self):
        # PROTECTED REGION ID(MCCSSubarrayLeafNode.obsReset) ENABLED START #
        pass
        # PROTECTED REGION END #    //  MCCSSubarrayLeafNode.obsReset

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(MCCSSubarrayLeafNode.main) ENABLED START #
    return run((MCCSSubarrayLeafNode,), args=args, **kwargs)
    # PROTECTED REGION END #    //  MCCSSubarrayLeafNode.main

if __name__ == '__main__':
    main()
