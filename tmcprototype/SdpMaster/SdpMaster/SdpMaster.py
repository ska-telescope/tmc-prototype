# -*- coding: utf-8 -*-
#
# This file is part of the SdpMaster project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

""" SdpMaster

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
from skabase.SKAMaster.SKAMaster import SKAMaster
# Additional import
# PROTECTED REGION ID(SdpMaster.additionnal_import) ENABLED START #
# PyTango imports
import tango
import os
import sys
from tango import DebugIt, DevState, AttrWriteType
from tango.server import run, DeviceMeta, attribute, command, device_property
from skabase.SKAMaster.SKAMaster import SKAMaster

# Additional import
from future.utils import with_metaclass

file_path = os.path.dirname(os.path.abspath(__file__))
module_path = os.path.abspath(os.path.join(file_path, os.pardir)) + "/SdpMaster"
sys.path.insert(0, module_path)
print("sys.path: ", sys.path)
# PROTECTED REGION END #    //  SdpMaster.additionnal_import

__all__ = ["SdpMaster", "main"]


class SdpMaster(SKAMaster):
    """
    """
    __metaclass__ = DeviceMeta
    # PROTECTED REGION ID(SdpMaster.class_variable) ENABLED START #
    # PROTECTED REGION END #    //  SdpMaster.class_variable

    # -----------------
    # Device Properties
    # -----------------









    # ----------
    # Attributes
    # ----------















    ProcessingBlockList = attribute(
        dtype='str',
    )

    OperatingState = attribute(
        dtype='DevEnum',
        enum_labels=["OFF", "ON", "STANDBY", "UNKNOWN", "FAULT", "DISABLE", "ALARM", "INIT"],
    )



    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        SKAMaster.init_device(self)
        # PROTECTED REGION ID(SdpMaster.init_device) ENABLED START #
        self._operating_state = 3
        self._processing_block_list = ''
        # PROTECTED REGION END #    //  SdpMaster.init_device

    def always_executed_hook(self):
        # PROTECTED REGION ID(SdpMaster.always_executed_hook) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SdpMaster.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(SdpMaster.delete_device) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SdpMaster.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    def read_ProcessingBlockList(self):
        # PROTECTED REGION ID(SdpMaster.ProcessingBlockList_read) ENABLED START #
        return self._processing_block_list
        # PROTECTED REGION END #    //  SdpMaster.ProcessingBlockList_read

    def read_OperatingState(self):
        # PROTECTED REGION ID(SdpMaster.OperatingState_read) ENABLED START #
        return self._operating_state
        # PROTECTED REGION END #    //  SdpMaster.OperatingState_read


    # --------
    # Commands
    # --------

    @command(
    )
    @DebugIt()
    def On(self):
        # PROTECTED REGION ID(SdpMaster.On) ENABLED START #
        self._operating_state = 1
        print("SdpMasterLeafNode.On command executed successfully.")
        # PROTECTED REGION END #    //  SdpMaster.On

    @command(
    )
    @DebugIt()
    def Off(self):
        # PROTECTED REGION ID(SdpMaster.Off) ENABLED START #
        self._operating_state = 0
        print("SdpMasterLeafNode.Off command executed successfully.")
        # PROTECTED REGION END #    //  SdpMaster.Off

    @command(
    )
    @DebugIt()
    def StandBy(self):
        # PROTECTED REGION ID(SdpMaster.StandBy) ENABLED START #
        self._operating_state = 2
        print("SdpMasterLeafNode.Standby command executed successfully.")
        # PROTECTED REGION END #    //  SdpMaster.StandBy

    @command(
    )
    @DebugIt()
    def Disable(self):
        # PROTECTED REGION ID(SdpMaster.Disable) ENABLED START #
        self._operating_state = 5
        print("SdpMasterLeafNode.Disable command executed successfully.")
        # PROTECTED REGION END #    //  SdpMaster.Disable

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(SdpMaster.main) ENABLED START #
    return run((SdpMaster,), args=args, **kwargs)
    # PROTECTED REGION END #    //  SdpMaster.main

if __name__ == '__main__':
    main()
