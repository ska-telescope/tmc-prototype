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
import sys
import os
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











    ActiveProcessingBlocks = attribute(
        dtype='str',
    )

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
        self._active_processing_block = "1"
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

    def read_ActiveProcessingBlocks(self):
        # PROTECTED REGION ID(SdpSubarrayLeafNode.ActiveProcessingBlocks_read) ENABLED START #
        return self._active_processing_block
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.ActiveProcessingBlocks_read

    def read_ReceiveAddresses(self):
        # PROTECTED REGION ID(SdpSubarrayLeafNode.ReceiveAddresses_read) ENABLED START #
        return self._receive_addresses
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.ReceiveAddresses_read


    # --------
    # Commands
    # --------

    @command(
    dtype_in='str', 
    dtype_out='str', 
    )
    @DebugIt()
    def ReleaseResource(self, argin):
        # PROTECTED REGION ID(SdpSubarrayLeafNode.ReleaseResource) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.ReleaseResource

    @command(
    dtype_in='str', 
    dtype_out='str', 
    )
    @DebugIt()
    def AssignResource(self, argin):
        # PROTECTED REGION ID(SdpSubarrayLeafNode.AssignResource) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.AssignResource

    @command(
    dtype_in='str', 
    )
    @DebugIt()
    def Configure(self, argin):
        # PROTECTED REGION ID(SdpSubarrayLeafNode.Configure) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.Configure

    @command(
    dtype_in='str', 
    )
    @DebugIt()
    def StartScan(self, argin):
        # PROTECTED REGION ID(SdpSubarrayLeafNode.StartScan) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.StartScan

    @command(
    )
    @DebugIt()
    def StopScan(self):
        # PROTECTED REGION ID(SdpSubarrayLeafNode.StopScan) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.StopScan

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(SdpSubarrayLeafNode.main) ENABLED START #
    return run((SdpSubarrayLeafNode,), args=args, **kwargs)
    # PROTECTED REGION END #    //  SdpSubarrayLeafNode.main

if __name__ == '__main__':
    main()
