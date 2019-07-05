# -*- coding: utf-8 -*-
#
# This file is part of the SdpSubarray project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

""" SdpSubarray

"""

# Tango imports
import os
import sys
import tango
from tango import DebugIt, DevState, AttrWriteType, DevFailed, Group
from tango.server import run, DeviceMeta, attribute, command, device_property
from future.utils import with_metaclass
from skabase.SKASubarray.SKASubarray import SKASubarray
# PROTECTED REGION ID(SdpSubarray.additionnal_import) ENABLED START #
import CONST

file_path = os.path.dirname(os.path.abspath(__file__))
module_path = os.path.abspath(os.path.join(file_path, os.pardir)) + "/SdpSubarray"
sys.path.insert(0, module_path)
print("sys.path: ", sys.path)
# PROTECTED REGION END #    //  SdpSubarray.additionnal_import

__all__ = ["SdpSubarray", "main"]


class SdpSubarray(SKASubarray):
    """
    """
    __metaclass__ = DeviceMeta
    # PROTECTED REGION ID(SdpSubarray.class_variable) ENABLED START #

    @command(
        dtype_in=('str',),
        doc_in="Execute Scan on the Subarray",
    )
    @DebugIt()
    def Scan(self, argin):
        """
        Schedules a scan for execution on a subarray.
        """
        print("SdpSubarray.Scan command executed successfully.")

    def is_Scan_allowed(self):
        """ This method is an internal construct of TANGO """
        return self.get_state() not in [DevState.FAULT, DevState.UNKNOWN, DevState.DISABLE,
                                        DevState.STANDBY]

    @command(
        dtype_in=('str',),
        doc_in="List of Resources to add to subarray.",
        dtype_out=('str',),
        doc_out="A list of Resources added to the subarray.",
    )
    @DebugIt()
    def AssignResources(self, argin):
        """
        Assigns resources to the subarray.
        """
        print("SdpSubarray.AssignResources command executed successfully.")
        return ""

    def is_AssignResources_allowed(self):
        """Checks if AssignResources is allowed in the current state of SubarrayNode."""
        return self.get_state() not in [DevState.FAULT, DevState.UNKNOWN, DevState.DISABLE,
                                        DevState.STANDBY]

    @DebugIt()
    def ReleaseResources(self, argin):
        """
        Releases resources from the subarray.
        """
        print("SdpSubarray.ReleaseResources command executed successfully.")
        return ""

    def is_ReleaseResources_allowed(self):
        """Checks if AssignResources is allowed in the current state of SubarrayNode."""
        return self.get_state() not in [DevState.FAULT]

    # PROTECTED REGION END #    //  SdpSubarray.class_variable

    # -----------------
    # Device Properties
    # -----------------








    # ----------
    # Attributes
    # ----------
















    ReceiveAddresses = attribute(
        dtype='str',
    )

    ActiveProcessingBlocks = attribute(
        dtype='str',
    )



    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        SKASubarray.init_device(self)
        # PROTECTED REGION ID(SdpSubarray.init_device) ENABLED START #
        self.set_state(DevState.INIT)
        self.set_status(CONST.STR_SA_INIT)
        self.SkaLevel = 2  # set SKALevel to "2"
        self._admin_mode = 0  # set adminMode to "ON-LINE"
        self._health_state = 0  # set health state to "OK"
        self._obs_state = 0  # set obsState to "IDLE"
        self._obs_mode = 0  # set obsMode to "IDLE"
        self._simulation_mode = False
        self._active_processing_blocks = "0"
        self._receive_addresses = ""
        self.set_state(DevState.OFF)  # Set state = OFF
        self._read_activity_message = CONST.STR_SA_INIT_SUCCESS
        self.set_status(CONST.STR_SA_INIT_SUCCESS)
        # PROTECTED REGION END #    //  SdpSubarray.init_device

    def always_executed_hook(self):
        # PROTECTED REGION ID(SdpSubarray.always_executed_hook) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SdpSubarray.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(SdpSubarray.delete_device) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SdpSubarray.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    def read_ReceiveAddresses(self):
        # PROTECTED REGION ID(SdpSubarray.ReceiveAddresses_read) ENABLED START #
        return self._receive_addresses
        # PROTECTED REGION END #    //  SdpSubarray.ReceiveAddresses_read

    def read_ActiveProcessingBlocks(self):
        # PROTECTED REGION ID(SdpSubarray.ActiveProcessingBlocks_read) ENABLED START #
        return self._active_processing_blocks
        # PROTECTED REGION END #    //  SdpSubarray.ActiveProcessingBlocks_read


    # --------
    # Commands
    # --------

    @command(
    dtype_in='str', 
    )
    @DebugIt()
    def Configure(self, argin):
        # PROTECTED REGION ID(SdpSubarray.Configure) ENABLED START #
        print("SdpSubarray.Configure command executed successfully.")
        # PROTECTED REGION END #    //  SdpSubarray.Configure

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(SdpSubarray.main) ENABLED START #
    return run((SdpSubarray,), args=args, **kwargs)
    # PROTECTED REGION END #    //  SdpSubarray.main

if __name__ == '__main__':
    main()
