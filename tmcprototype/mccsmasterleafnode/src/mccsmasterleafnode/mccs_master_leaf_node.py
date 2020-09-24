# -*- coding: utf-8 -*-
#
# This file is part of the MCCSMasterLeafNode project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

""" 

"""

# Tango imports
import tango
from tango import DeviceProxy, EventType, ApiUtil, DebugIt, DevState, AttrWriteType, DevFailed
from tango.server import run, command, device_property, attribute, Device, DeviceMeta
from ska.base import SKABaseDevice
from ska.base.commands import ResultCode, ResponseCommand
from ska.base.control_model import HealthState, SimulationMode, TestMode

# Additional import
# PROTECTED REGION ID(MCCSMasterLeafNode.additionnal_import) ENABLED START #
# PROTECTED REGION END #    //  MCCSMasterLeafNode.additionnal_import

__all__ = ["MCCSMasterLeafNode", "main"]


class MCCSMasterLeafNode(SKABaseDevice):
    """
    """
    __metaclass__ = DeviceMeta
    # PROTECTED REGION ID(MCCSMasterLeafNode.class_variable) ENABLED START #
    # PROTECTED REGION END #    //  MCCSMasterLeafNode.class_variable

    # -----------------
    # Device Properties
    # -----------------





    MCCSMasterFQDN = device_property(
        dtype='str', default_value="low_mccs/elt/master"
    )

    # ----------
    # Attributes
    # ----------









    activitymessage = attribute(
        dtype='str',
        access=AttrWriteType.READ_WRITE,
    )


    mccsHealthState = attribute(label="mccsHealthState",
        forwarded=True
    )
    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        SKABaseDevice.init_device(self)
        self.set_change_event("adminMode", True, True)
        self.set_archive_event("adminMode", True, True)
        # PROTECTED REGION ID(MCCSMasterLeafNode.init_device) ENABLED START #
        # PROTECTED REGION END #    //  MCCSMasterLeafNode.init_device

    def always_executed_hook(self):
        # PROTECTED REGION ID(MCCSMasterLeafNode.always_executed_hook) ENABLED START #
        pass
        # PROTECTED REGION END #    //  MCCSMasterLeafNode.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(MCCSMasterLeafNode.delete_device) ENABLED START #
        pass
        # PROTECTED REGION END #    //  MCCSMasterLeafNode.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    def read_activitymessage(self):
        # PROTECTED REGION ID(MCCSMasterLeafNode.activitymessage_read) ENABLED START #
        return ''
        # PROTECTED REGION END #    //  MCCSMasterLeafNode.activitymessage_read

    def write_activitymessage(self, value):
        # PROTECTED REGION ID(MCCSMasterLeafNode.activitymessage_write) ENABLED START #
        pass
        # PROTECTED REGION END #    //  MCCSMasterLeafNode.activitymessage_write


    # --------
    # Commands
    # --------

    @command(
    dtype_in='str', 
    dtype_out='str', 
    )
    @DebugIt()
    def AssignResource(self, argin):
        # PROTECTED REGION ID(MCCSMasterLeafNode.AssignResource) ENABLED START #
        return ""
        # PROTECTED REGION END #    //  MCCSMasterLeafNode.AssignResource

    @command(
    dtype_in='str', 
    dtype_out='str', 
    )
    @DebugIt()
    def ReleaseResources(self, argin):
        # PROTECTED REGION ID(MCCSMasterLeafNode.ReleaseResources) ENABLED START #
        return ""
        # PROTECTED REGION END #    //  MCCSMasterLeafNode.ReleaseResources

    @command(
    )
    @DebugIt()
    def On(self):
        # PROTECTED REGION ID(MCCSMasterLeafNode.On) ENABLED START #
        pass
        # PROTECTED REGION END #    //  MCCSMasterLeafNode.On

    @command(
    )
    @DebugIt()
    def Off(self):
        # PROTECTED REGION ID(MCCSMasterLeafNode.Off) ENABLED START #
        pass
        # PROTECTED REGION END #    //  MCCSMasterLeafNode.Off

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(MCCSMasterLeafNode.main) ENABLED START #
    return run((MCCSMasterLeafNode,), args=args, **kwargs)
    # PROTECTED REGION END #    //  MCCSMasterLeafNode.main

if __name__ == '__main__':
    main()
