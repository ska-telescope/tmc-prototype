# -*- coding: utf-8 -*-
#
# This file is part of the CspSubarray project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

""" 

"""

# PyTango imports
import tango
from tango import DebugIt
from tango.server import run
from tango.server import Device, DeviceMeta
from tango.server import attribute, command
from tango.server import device_property
from tango import AttrQuality, DispLevel, DevState
from tango import AttrWriteType, PipeWriteType
# from SKASubarray import SKASubarray
# Additional import
# PROTECTED REGION ID(CspSubarray.additionnal_import) ENABLED START #
from skabase.SKASubarray.SKASubarray import SKASubarray
import os
import sys
import time

file_path = os.path.dirname(os.path.abspath(__file__))
module_path = os.path.abspath(os.path.join(file_path, os.pardir)) + "/CspSubarray"
sys.path.insert(0, module_path)
print("sys.path: ", sys.path)
# PROTECTED REGION END #    //  CspSubarray.additionnal_import

__all__ = ["CspSubarray", "main"]


class CspSubarray(SKASubarray):
    """
    """
    __metaclass__ = DeviceMeta
    # PROTECTED REGION ID(CspSubarray.class_variable) ENABLED START #
    # PROTECTED REGION END #    //  CspSubarray.class_variable

    # -----------------
    # Device Properties
    # -----------------

    # ----------
    # Attributes
    # ----------

    opState = attribute(
        dtype='DevEnum',
        enum_labels=["INIT", "OFF", "ON", "ALARM", "DISABLE", "FAULT", "UNKNOWN", ],
    )

    procMode = attribute(
        dtype='DevEnum',
        access=AttrWriteType.READ_WRITE,
        enum_labels=["CORRELATION", "PSS", "PST", "VLBI", "IDLE", ],
    )

    frequencyBand = attribute(
        dtype='DevEnum',
        access=AttrWriteType.READ_WRITE,
        enum_labels=["1", "2", "3", "4", "5a", "5b", ],
    )

    scanId = attribute(
        dtype='uint64',
        access=AttrWriteType.READ_WRITE,
    )

    correlation = attribute(
        dtype='str',
    )

    receptors = attribute(
        dtype=('str',),
        access=AttrWriteType.READ_WRITE,
        max_dim_x=4,
    )

    correlationDigitalBandpassCorrectionCoefficients = attribute(
        dtype=(('double',),),
        max_dim_x=10, max_dim_y=10,
    )

    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        SKASubarray.init_device(self)
        # PROTECTED REGION ID(CspSubarray.init_device) ENABLED START #
        self._opstate = 0       # Set operating state to INIT
        self._obs_state = 0  # Set observation state to IDLE
        self._scanid = 0
        self._frequencyband = 0
        self._procmode = 0
        self._receptor = []
        self._correlations = " "
        self._health_state = 0        # Set health state to OK
        self.set_state(DevState.OFF)  # Set state = OFF
        self._opstate = 1             # Set operating state to OFF
        # PROTECTED REGION END #    //  CspSubarray.init_device

    def always_executed_hook(self):
        # PROTECTED REGION ID(CspSubarray.always_executed_hook) ENABLED START #
        pass
        # PROTECTED REGION END #    //  CspSubarray.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(CspSubarray.delete_device) ENABLED START #
        pass
        # PROTECTED REGION END #    //  CspSubarray.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    def read_obsState(self):
        # PROTECTED REGION ID(CspSubarray.obsState_read) ENABLED START #
        return self._obs_state
        # PROTECTED REGION END #    //  CspSubarray.obsState_read

    def read_opState(self):
        # PROTECTED REGION ID(CspSubarray.opState_read) ENABLED START #
        return self._opstate
        # PROTECTED REGION END #    //  CspSubarray.opState_read

    def read_healthState(self):
        # PROTECTED REGION ID(CspSubarray.opState_read) ENABLED START #
        return self._health_state
        # PROTECTED REGION END #    //  CspSubarray.opState_read

    def read_procMode(self):
        # PROTECTED REGION ID(CspSubarray.procMode_read) ENABLED START #
        return self._procmode
        # PROTECTED REGION END #    //  CspSubarray.procMode_read

    def write_procMode(self, value):
        # PROTECTED REGION ID(CspSubarray.procMode_write) ENABLED START #
        self._procmode = value
        # PROTECTED REGION END #    //  CspSubarray.procMode_write

    def read_frequencyBand(self):
        # PROTECTED REGION ID(CspSubarray.frequencyBand_read) ENABLED START #
        return self._frequencyband
        # PROTECTED REGION END #    //  CspSubarray.frequencyBand_read

    def write_frequencyBand(self, value):
        # PROTECTED REGION ID(CspSubarray.frequencyBand_write) ENABLED START #
        self._frequencyband = value
        # PROTECTED REGION END #    //  CspSubarray.frequencyBand_write

    def read_scanId(self):
        # PROTECTED REGION ID(CspSubarray.scanId_read) ENABLED START #
        return self._scanid
        # PROTECTED REGION END #    //  CspSubarray.scanId_read

    def write_scanId(self, value):
        # PROTECTED REGION ID(CspSubarray.scanId_write) ENABLED START #
        self._scanid = value
        # PROTECTED REGION END #    //  CspSubarray.scanId_write

    def read_correlation(self):
        # PROTECTED REGION ID(CspSubarray.correlation_read) ENABLED START #
        return self._correlations
        # PROTECTED REGION END #    //  CspSubarray.correlation_read

    def read_receptors(self):
        # PROTECTED REGION ID(CspSubarray.receptors_read) ENABLED START #
        return self._receptor
        # PROTECTED REGION END #    //  CspSubarray.receptors_read

    def write_receptors(self, value):
        # PROTECTED REGION ID(CspSubarray.receptors_write) ENABLED START #
        self._receptor = value
        # PROTECTED REGION END #    //  CspSubarray.receptors_write

    def read_correlationDigitalBandpassCorrectionCoefficients(self):
        # PROTECTED REGION ID(CspSubarray.correlationDigitalBandpassCorrectionCoefficients_read) ENABLED START #
        return [[0.0]]
        # PROTECTED REGION END #    //  CspSubarray.correlationDigitalBandpassCorrectionCoefficients_read

    # --------
    # Commands
    # --------

    @command(
    dtype_in='str', 
    )
    @DebugIt()
    def ConfigureScan(self, argin):
        # PROTECTED REGION ID(CspSubarray.ConfigureScan) ENABLED START #
        self._obs_state = 1                 # Set ObsState to CONFIGURING
        print("ConfigureScan is invoked successfully on CspSubarray. Argin:", argin)
        self._obs_state = 2                 # Set ObsState to READY
        # PROTECTED REGION END #    //  CspSubarray.ConfigureScan

    @command(
    dtype_in=('uint16',), 
    )
    @DebugIt()
    def AddReceptors(self, argin):
        # PROTECTED REGION ID(CspSubarray.AddReceptors) ENABLED START #
        self.set_state(DevState.ON)  # Set state = ON
        self._opstate = 2                    # Set operating state to ON
        print("Add receptors command executed successfully on CspSubarray. Argin:", argin)
        # PROTECTED REGION END #    //  CspSubarray.AddReceptors

    @command(
    dtype_in=('uint16',), 
    )
    @DebugIt()
    def RemoveReceptors(self, argin):
        # PROTECTED REGION ID(CspSubarray.RemoveReceptors) ENABLED START #
        pass
        # PROTECTED REGION END #    //  CspSubarray.RemoveReceptors

    @command(
    )
    @DebugIt()
    def RemoveAllReceptors(self):
        # PROTECTED REGION ID(CspSubarray.RemoveAllReceptors) ENABLED START #
        self.set_state(DevState.OFF)  # Set state = OFF
        self._opstate = 1                   # Set operating state to OFF
        print("RemoveAllReceptors command executed successfully on CspSubarray.")
        # PROTECTED REGION END #    //  CspSubarray.RemoveAllReceptors

    @command(
        dtype_in=('str',),
    )
    @DebugIt()
    def Scan(self, argin):
        # PROTECTED REGION ID(CspSubarray.StartScan) ENABLED START #
        """
        This command starts the scan.

        :param argin:
        :return:
        """
        self._obs_state = 3               # Set observation state to SCANNING
        print("Scan command: Argin on CspSubarray:", argin)
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.StartScan

    @command(
    )
    @DebugIt()
    def EndScan(self):
        # PROTECTED REGION ID(CspSubarray.EndScan) ENABLED START #
        self._obs_state = 2               # Set observation state to READY
        print("EndScan command successfully invoked:")
        # PROTECTED REGION END #    //  CspSubarray.EndScan

    @command(
    )
    @DebugIt()
    def EndSB(self):
        # PROTECTED REGION ID(CspSubarray.EndSB) ENABLED START #
        self._obs_state = 0               # Set observation state to IDLE
        print("EndSB command is successfully invoked on CSP Subarray.")
        # PROTECTED REGION END #    //  CspSubarray.EndSB


# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(CspSubarray.main) ENABLED START #
    return run((CspSubarray,), args=args, **kwargs)
    # PROTECTED REGION END #    //  CspSubarray.main

if __name__ == '__main__':
    main()
