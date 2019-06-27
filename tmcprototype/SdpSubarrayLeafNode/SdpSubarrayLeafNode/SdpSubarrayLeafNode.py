# -*- coding: utf-8 -*-
#
# This file is part of the SdpSubarrayLeafNode project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

""" SdpSubarrayLeafNode

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
# PROTECTED REGION ID(SdpSubarrayLeafNode.additionnal_import) ENABLED START #
import os
import sys
file_path = os.path.dirname(os.path.abspath(__file__))
module_path = os.path.abspath(os.path.join(file_path, os.pardir)) + "/SdpSubarrayLeafNode"
sys.path.insert(0, module_path)
print("sys.path: ", sys.path)
# PROTECTED REGION END #    //  SdpSubarrayLeafNode.additionnal_import

__all__ = ["SdpSubarrayLeafNode", "main"]


class SdpSubarrayLeafNode(SKABaseDevice):
    """
    """
    __metaclass__ = DeviceMeta
    # PROTECTED REGION ID(SdpSubarrayLeafNode.class_variable) ENABLED START #
    # PROTECTED REGION END #    //  SdpSubarrayLeafNode.class_variable

    # -----------------
    # Device Properties
    # -----------------






    # ----------
    # Attributes
    # ----------











    ReceiveAddresses = attribute(
        dtype='str',
    )

    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        SKABaseDevice.init_device(self)
        # PROTECTED REGION ID(SdpSubarrayLeafNode.init_device) ENABLED START #
        self._receive_addresses = "abc"
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.init_device

    def always_executed_hook(self):
        # PROTECTED REGION ID(SdpSubarrayLeafNode.always_executed_hook) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(SdpSubarrayLeafNode.delete_device) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    def read_ReceiveAddresses(self):
        # PROTECTED REGION ID(SdpSubarrayLeafNode.ReceiveAddresses_read) ENABLED START #
        return self._receive_addresses
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.ReceiveAddresses_read


    # --------
    # Commands
    # --------

    @command(
    dtype_in='str', 
    )
    @DebugIt()
    def ReleaseResources(self, argin):
        # PROTECTED REGION ID(SdpSubarrayLeafNode.ReleaseResources) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.ReleaseResources

    @command(
    dtype_in='str', 
    dtype_out='str', 
    )
    @DebugIt()
    def AssignResources(self, argin):
        # PROTECTED REGION ID(SdpSubarrayLeafNode.AssignResources) ENABLED START #
        return ""
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.AssignResources

    @command(
    dtype_in='str', 
    )
    @DebugIt()
    def Configure(self, argin):
        # PROTECTED REGION ID(SdpSubarrayLeafNode.Configure) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.Configure

    @command(
    )
    @DebugIt()
    def Scan(self):
        # PROTECTED REGION ID(SdpSubarrayLeafNode.Scan) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.Scan

    @command(
    )
    @DebugIt()
    def EndScan(self):
        # PROTECTED REGION ID(SdpSubarrayLeafNode.EndScan) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.EndScan

    @command(
    )
    @DebugIt()
    def EndSB(self):
        # PROTECTED REGION ID(SdpSubarrayLeafNode.EndSB) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.EndSB

    @command(
    )
    @DebugIt()
    def Abort(self):
        # PROTECTED REGION ID(SdpSubarrayLeafNode.Abort) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.Abort

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(SdpSubarrayLeafNode.main) ENABLED START #
    return run((SdpSubarrayLeafNode,), args=args, **kwargs)
    # PROTECTED REGION END #    //  SdpSubarrayLeafNode.main

if __name__ == '__main__':
    main()
