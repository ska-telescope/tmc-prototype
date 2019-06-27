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

# Additional import
# PROTECTED REGION ID(SdpSubarrayLeafNode.additionnal_import) ENABLED START #
from skabase.SKABaseDevice.SKABaseDevice import SKABaseDevice

from tango import DeviceProxy
import CONST
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






    SdpSubarrayNodeFQDN = device_property(
        dtype='str', default_value="mid-sdp/elt/subarray_1"
    )

    # ----------
    # Attributes
    # ----------











    receiveAddresses = attribute(
        dtype='str',
    )

    sdpSubarrayHealthState = attribute(
        dtype='DevEnum',
    )

    activityMessage = attribute(
        dtype='str',
        access=AttrWriteType.READ_WRITE,
    )

    activeProcessingBlocks = attribute(
        dtype='str',
    )

    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        SKABaseDevice.init_device(self)
        # PROTECTED REGION ID(SdpSubarrayLeafNode.init_device) ENABLED START #
        self._receive_addresses = "abc"
        self._sdp_subarray_health_state = ''
        self._activity_message = ''
        self._active_processing_block = ''
        try:
            self._sdp_subarray_proxy = DeviceProxy(self.SdpSubarrayNodeFQDN[0])
        except Exception as e:
            print ("Exception while creating device proxy for SDP Subarray:"), e



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

    def read_receiveAddresses(self):
        # PROTECTED REGION ID(SdpSubarrayLeafNode.receiveAddresses_read) ENABLED START #
        return self._receive_addresses
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.receiveAddresses_read

    def read_sdpSubarrayHealthState(self):
        # PROTECTED REGION ID(SdpSubarrayLeafNode.sdpSubarrayHealthState_read) ENABLED START #
        return self._sdp_subarray_health_state
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.sdpSubarrayHealthState_read

    def read_activityMessage(self):
        # PROTECTED REGION ID(SdpSubarrayLeafNode.activityMessage_read) ENABLED START #
        return self._activity_message
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.activityMessage_read

    def write_activityMessage(self, value):
        # PROTECTED REGION ID(SdpSubarrayLeafNode.activityMessage_write) ENABLED START #
        value = self._activity_message
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.activityMessage_write

    def read_activeProcessingBlocks(self):
        # PROTECTED REGION ID(SdpSubarrayLeafNode.activeProcessingBlocks_read) ENABLED START #
        return self._active_processing_block
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.activeProcessingBlocks_read


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
        # Create SDP Subarray proxy
        if self._sdp_subarray_proxy:
            self.response = self._sdp_subarray_proxy.command_inout_asynch(CONST.CMD_ASSIGN_RESOURCES)



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
    dtype_in='str', 
    )
    @DebugIt()
    def Scan(self, argin):
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
