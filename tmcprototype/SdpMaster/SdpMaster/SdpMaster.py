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
from SKAMaster import SKAMaster
# Additional import
# PROTECTED REGION ID(SdpMaster.additionnal_import) ENABLED START #
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



    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        SKAMaster.init_device(self)
        # PROTECTED REGION ID(SdpMaster.init_device) ENABLED START #
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
        return ''
        # PROTECTED REGION END #    //  SdpMaster.ProcessingBlockList_read


    # --------
    # Commands
    # --------

    @command(
    )
    @DebugIt()
    def On(self):
        # PROTECTED REGION ID(SdpMaster.On) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SdpMaster.On

    @command(
    )
    @DebugIt()
    def Off(self):
        # PROTECTED REGION ID(SdpMaster.Off) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SdpMaster.Off

    @command(
    )
    @DebugIt()
    def ActivateSubarray(self):
        # PROTECTED REGION ID(SdpMaster.ActivateSubarray) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SdpMaster.ActivateSubarray

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(SdpMaster.main) ENABLED START #
    return run((SdpMaster,), args=args, **kwargs)
    # PROTECTED REGION END #    //  SdpMaster.main

if __name__ == '__main__':
    main()
