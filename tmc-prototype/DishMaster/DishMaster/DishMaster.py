# -*- coding: utf-8 -*-
#
# This file is part of the DishMaster project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

""" DishMaster Simulator

SKA Dish Master TANGO device server
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
# PROTECTED REGION ID(DishMaster.additionnal_import) ENABLED START #
import time
from threading import Timer
import threading
import logging

# PROTECTED REGION END #    //  DishMaster.additionnal_import

__all__ = ["DishMaster", "main"]


class DishMaster(SKAMaster):
    """
    SKA Dish Master TANGO device server
    """
    __metaclass__ = DeviceMeta
    # PROTECTED REGION ID(DishMaster.class_variable) ENABLED START #

    # Function to set achieved pointing attribute to the desired pointing attribute

    def point(self):
        if ((self._achieved_pointing[1] != self._desired_pointing[1]) | (self._achieved_pointing[2] != self._desired_pointing[2])):
            try:
                self.azimuthThread = threading.Thread(None, self.azimuth, 'DishMaster')
                self.elevationThread = threading.Thread(None, self.elevation, 'DishMaster')
                self.azimuthThread.start()
                self.elevationThread.start()
                self._pointing_state = 1

            except Exception as e:
                print "Unexpected error in executing POINT function on Dish", self.ReceptorNumber
                print "Error message is: \n", e

    def azimuth(self):
        self._pointing_state = 1
        self._azimuth_difference = self._desired_pointing[1] - self._achieved_pointing[1]
        if self._azimuth_difference > 0.0:
            self.increment_position([1,self._azimuth_difference])
        elif self._azimuth_difference < 0.0:
            self.decrement_position([1,abs(self._azimuth_difference)])
        else:
            pass

    def elevation(self):
        self._pointing_state = 1
        self._elevation_difference = self._desired_pointing[2] - self._achieved_pointing[2]
        if self._elevation_difference > 0.0:
            self.increment_position([2,self._elevation_difference])
        elif self._elevation_difference < 0.0:
            self.decrement_position([2,abs(self._elevation_difference)])
        else:
            pass

    def increment_position(self,argin):
        temp = int(argin[1])
        time.sleep(2)
        if abs(self._azimuth_difference) > abs(self._elevation_difference):
            temp1 = abs(self._azimuth_difference)
        elif abs(self._azimuth_difference) < abs(self._elevation_difference):
            temp1 = abs(self._elevation_difference)
        else:
            temp1 = temp
            pass

        if temp == temp1:
            temp = temp + 1
        else:
            pass

        for position in range(0,temp):
            self.set_status("Dish is pointing towards the desired coordinates.")
            self.devlogmsg("Dish is pointing towards the desired coordinates.", 4)
            self._pointing_state = 1
            time.sleep(2)
            if (self._achieved_pointing[1] == self._desired_pointing[1]) and (self._achieved_pointing[2] == self._desired_pointing[2]):
                self._pointing_state = 0
                self.set_status("Dish has pointed towards the desired coordinates.")
                self.devlogmsg("Dish has pointed towards the desired coordinates.", 4)
                pass
            else:
                self._achieved_pointing[argin[0]] = self._achieved_pointing[argin[0]] + 1

    def decrement_position(self,argin):
        temp2 = int(argin[1])
        time.sleep(2)
        if abs(self._azimuth_difference) > abs(self._elevation_difference):
            temp3 = abs(self._azimuth_difference)
        elif abs(self._azimuth_difference) < abs(self._elevation_difference):
            temp3 = abs(self._elevation_difference)
        else:
            temp3 = temp2
            pass
        if temp2 == temp3:
            temp2 = temp2 + 1
        else:
            pass

        for position in range(0, (temp2)):
            self.set_status("Dish is pointing towards the desired coordinates.")
            self._pointing_state = 1
            time.sleep(2)
            if (self._achieved_pointing[1] == self._desired_pointing[1]) and (self._achieved_pointing[2] == self._desired_pointing[2]):
                self._pointing_state = 0
                self.set_status("Dish has pointed towards the desired coordinates.")
                self.devlogmsg("Dish has pointed towards the desired coordinates.", 4)

                pass
            else:
                self._achieved_pointing[argin[0]] = self._achieved_pointing[argin[0]] - 1


    def checkSlew(self):
        while True:
            print"in while loop"
            if (self._pointing_state != 1):
                print "in if loop"
                self._admin_mode = 1                        # Set adminMode to OFFLINE
                self.set_state(PyTango.DevState.DISABLE)    # Set STATE to DISABLE
                self._dish_mode = 6                         # set dishMode to STOW
                self._health_state = 0                      # Set healthState to OK
                self.set_status("Dish is stowed successfully.")
                self.devlogmsg("Dish is stowed successfully.", 4)
                break


    # PROTECTED REGION END #    //  DishMaster.class_variable

    # -----------------
    # Device Properties
    # -----------------










    ReceptorNumber = device_property(
        dtype='uint',
    )

    # ----------
    # Attributes
    # ----------















    dishMode = attribute(
        dtype='DevEnum',
        enum_labels=["OFF", "STARTUP", "SHUTDOWN", "STANDBY-LP", "STANDBY-FP", "MAINTENANCE", "STOW", "CONFIG", "OPERATE", ],
    )

    pointingState = attribute(
        dtype='DevEnum',
        enum_labels=["READY", "SLEW", "TRACK", "SCAN", ],
    )

    band1SamplerFrequency = attribute(
        dtype='double',
        access=AttrWriteType.WRITE,
    )

    band2SamplerFrequency = attribute(
        dtype='double',
        access=AttrWriteType.WRITE,
    )

    band3SamplerFrequency = attribute(
        dtype='double',
        access=AttrWriteType.WRITE,
    )

    band4SamplerFrequency = attribute(
        dtype='double',
        access=AttrWriteType.WRITE,
    )

    band5aSamplerFrequency = attribute(
        dtype='double',
        access=AttrWriteType.WRITE,
    )

    band5bSamplerFrequency = attribute(
        dtype='double',
        access=AttrWriteType.WRITE,
    )

    capturing = attribute(
        dtype='bool',
    )

    ConfiguredBand = attribute(
        dtype='DevEnum',
        enum_labels=["BAND1", "BAND2", "BAND3", "BAND4", "BAND5a", "BAND5b", "NONE", ],
    )

    WindSpeed = attribute(
        dtype='double',
        access=AttrWriteType.READ_WRITE,
        unit="km/h",
    )



    desiredPointing = attribute(
        dtype=('double',),
        access=AttrWriteType.READ_WRITE,
        max_dim_x=7,
    )

    achievedPointing = attribute(
        dtype=('double',),
        max_dim_x=7,
    )

    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        SKAMaster.init_device(self)
        # PROTECTED REGION ID(DishMaster.init_device) ENABLED START #
        try:
            # Initialise Properties
            self.SkaLevel = 1                           # Set SkaLevel to 1

            # Initialise Attributes
            self._health_state = 0                      # Set healthState to OK
            self._admin_mode = 0                        # Set adminMode to ONLINE
            self._dish_mode = 3                         # Set dishMode to STANDBY-LP Mode
            self._pointing_state = 0                    # Set pointingState to READY Mode
            self._band1_sampler_frequency = 0           # Set Band 1 Sampler Frequency to 0
            self._band2_sampler_frequency = 0           # Set Band 2 Sampler Frequency to 0
            self._band3_sampler_frequency = 0           # Set Band 3 Sampler Frequency to 0
            self._band4_sampler_frequency = 0           # Set Band 4 Sampler Frequency to 0
            self._band5a_sampler_frequency = 0          # Set Band 5a Sampler Frequency to 0
            self._band5b_sampler_frequency = 0          # Set Band 5b Sampler Frequency to 0
            self._capturing = False
            self._desired_pointing = [0,20,40]
            self._achieved_pointing = [0,0,0]
            self._elevation_difference = 0
            self._azimuth_difference = 0
            self._configured_band = 1
            self._wind_speed = 5
            self.set_state(PyTango.DevState.STANDBY)    # Set STATE to STANDBY

            # Initialise Point command variables
            self._current_time = 0
            self._point_execution_time = 0
            self._point_delta_t = 0

            # Initialise Scan command variables
            self._scan_execution_time = 0
            self._scan_delta_t = 0

            self.set_status("Dish Master is initialised successfully.")
            self.devlogmsg("Dish Master is initialised successfully.", 4)

        except Exception as e:
            print "Unexpected error in initialising properties and attributes on Dish", self.ReceptorNumber
            self.devlogmsg("Unexpected error in initialising properties and attributes on Dish", 2)
            print "Error message is: \n", e

        # PROTECTED REGION END #    //  DishMaster.always_executed_hook

    def always_executed_hook(self):
        # PROTECTED REGION ID(DishMaster.always_executed_hook) ENABLED START #
        pass
        # PROTECTED REGION END #    //  DishMaster.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(DishMaster.delete_device) ENABLED START #
        pass
        # PROTECTED REGION END #    //  DishMaster.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    def read_dishMode(self):
        # PROTECTED REGION ID(DishMaster.dishMode_read) ENABLED START #
        return self._dish_mode
        # PROTECTED REGION END #    //  DishMaster.dishMode_read

    def read_pointingState(self):
        # PROTECTED REGION ID(DishMaster.pointingState_read) ENABLED START #
        return self._pointing_state
        # PROTECTED REGION END #    //  DishMaster.pointingState_read

    def write_band1SamplerFrequency(self, value):
        # PROTECTED REGION ID(DishMaster.band1SamplerFrequency_write) ENABLED START #
        self._band1_sampler_frequency = value
        pass
        # PROTECTED REGION END #    //  DishMaster.band1SamplerFrequency_write

    def write_band2SamplerFrequency(self, value):
        # PROTECTED REGION ID(DishMaster.band2SamplerFrequency_write) ENABLED START #
        self._band2_sampler_frequency = value
        pass
        # PROTECTED REGION END #    //  DishMaster.band2SamplerFrequency_write

    def write_band3SamplerFrequency(self, value):
        # PROTECTED REGION ID(DishMaster.band3SamplerFrequency_write) ENABLED START #
        self._band3_sampler_frequency = value
        pass
        # PROTECTED REGION END #    //  DishMaster.band3SamplerFrequency_write

    def write_band4SamplerFrequency(self, value):
        # PROTECTED REGION ID(DishMaster.band4SamplerFrequency_write) ENABLED START #
        self._band4_sampler_frequency = value
        pass
        # PROTECTED REGION END #    //  DishMaster.band4SamplerFrequency_write

    def write_band5aSamplerFrequency(self, value):
        # PROTECTED REGION ID(DishMaster.band5aSamplerFrequency_write) ENABLED START #
        self._band5a_sampler_frequency = value
        pass
        # PROTECTED REGION END #    //  DishMaster.band5aSamplerFrequency_write

    def write_band5bSamplerFrequency(self, value):
        # PROTECTED REGION ID(DishMaster.band5bSamplerFrequency_write) ENABLED START #
        self._band5b_sampler_frequency = value
        pass
        # PROTECTED REGION END #    //  DishMaster.band5bSamplerFrequency_write

    def read_capturing(self):
        # PROTECTED REGION ID(DishMaster.capturing_read) ENABLED START #
        return self._capturing
        # PROTECTED REGION END #    //  DishMaster.capturing_read

    def read_ConfiguredBand(self):
        # PROTECTED REGION ID(DishMaster.ConfiguredBand_read) ENABLED START #
        return self._configured_band
        # PROTECTED REGION END #    //  DishMaster.ConfiguredBand_read

    def read_WindSpeed(self):
        # PROTECTED REGION ID(DishMaster.WindSpeed_read) ENABLED START #
        return self._wind_speed
        # PROTECTED REGION END #    //  DishMaster.WindSpeed_read

    def write_WindSpeed(self, value):
        # PROTECTED REGION ID(DishMaster.WindSpeed_write) ENABLED START #
        self._wind_speed = value
        pass
        # PROTECTED REGION END #    //  DishMaster.WindSpeed_write

    def read_desiredPointing(self):
        # PROTECTED REGION ID(DishMaster.desiredPointing_read) ENABLED START #
        return self._desired_pointing
        # PROTECTED REGION END #    //  DishMaster.desiredPointing_read

    def write_desiredPointing(self, value):
        # PROTECTED REGION ID(DishMaster.desiredPointing_write) ENABLED START #
        self._desired_pointing = value

        '''
        # Execute POINT command at given timestamp
        self._current_time = time.time()
        self._point_execution_time = self._desired_pointing[0]
        self._point_delta_t = self._point_execution_time - self._current_time
        t = Timer(self._point_delta_t, self.point)
        t.start()
        '''
        pass

        # PROTECTED REGION END #    //  DishMaster.desiredPointing_write

    def read_achievedPointing(self):
        # PROTECTED REGION ID(DishMaster.achievedPointing_read) ENABLED START #
        return self._achieved_pointing
        # PROTECTED REGION END #    //  DishMaster.achievedPointing_read


    # --------
    # Commands
    # --------

    @command(
    )
    @DebugIt()
    def SetStowMode(self):
        # PROTECTED REGION ID(DishMaster.SetStowMode) ENABLED START #
        try:
            # Command to set Dish to STOW Mode
            self._desired_pointing = [0, 0, 0]
            self.Slew("0")
            time.sleep(1)
            self.stowThread = threading.Thread(None, self.checkSlew, 'DishMaster')
            self.stowThread.start()

        except Exception as e:
            print "Unexpected error in executing SetStowMode Command on Dish", self.ReceptorNumber
            self.devlogmsg("Unexpected error in executing SetStowMode Command on Dish", 2)
            print "Error message is: \n", e

        # while True:
        #     print"in while loop"
        #     if (self._pointing_state != 1):
        #         print "in if loop"
        #         self._admin_mode = 1                        # Set adminMode to OFFLINE
        #         self.set_state(PyTango.DevState.DISABLE)    # Set STATE to DISABLE
        #         self._dish_mode = 6                         # set dishMode to STOW
        #         self._health_state = 0                      # Set healthState to OK
        #         self.set_status("Dish is stowed successfully.")
        #         break
        pass
        # PROTECTED REGION END #    //  DishMaster.SetStowMode

    def is_SetStowMode_allowed(self):
        # PROTECTED REGION ID(DishMaster.is_SetStowMode_allowed) ENABLED START #
        return self.get_state() not in [DevState.ON,DevState.ALARM]
        # PROTECTED REGION END #    //  DishMaster.is_SetStowMode_allowed

    @command(
    )
    @DebugIt()
    def SetStandbyLPMode(self):
        # PROTECTED REGION ID(DishMaster.SetStandbyLPMode) ENABLED START #
        try:
            # Command to set Dish to STANDBY-LP Mode
            self.set_state(PyTango.DevState.STANDBY)     # Set STATE to STANDBY
            self._dish_mode = 3                          # set dishMode to STANDBYLP
            self.set_status("Dish is in STANDBY-LP mode.")
            self.devlogmsg("Dish is in STANDBY-LP mode.", 4)

        except Exception as e:
            print "Unexpected error in executing SetStandbyLPMode Command on Dish", self.ReceptorNumber
            self.devlogmsg("Unexpected error in executing SetStandbyLPMode Command on Dish", 2)
            print "Error message is: \n", e

        pass
        # PROTECTED REGION END #    //  DishMaster.SetStandbyLPMode

    @command(
    )
    @DebugIt()
    def SetMaintenanceMode(self):
        # PROTECTED REGION ID(DishMaster.SetMaintenanceMode) ENABLED START #
        try:
            # Command to set Dish to MAINTENANCE Mode
            self._admin_mode = 2                        # Set adminMode to MAINTENANCE
            self.set_state(PyTango.DevState.DISABLE)    # Set STATE to DISABLE
            self._dish_mode = 5                         # set dishMode to MAINTENANCE
            self.set_status("Dish is in MAINTENANCE mode.")
            self.devlogmsg("Dish is in MAINTENANCE mode.", 4)

        except Exception as e:
            print "Unexpected error in executing SetMaintenanceMode Command on Dish", self.ReceptorNumber
            self.devlogmsg("Unexpected error in executing SetMaintenanceMode Command on Dish", 2)
            print "Error message is: \n", e

        pass
        # PROTECTED REGION END #    //  DishMaster.SetMaintenanceMode

    def is_SetMaintenanceMode_allowed(self):
        # PROTECTED REGION ID(DishMaster.is_SetMaintenanceMode_allowed) ENABLED START #
        return self.get_state() not in [DevState.ON,DevState.ALARM,DevState.DISABLE]
        # PROTECTED REGION END #    //  DishMaster.is_SetMaintenanceMode_allowed

    @command(
    )
    @DebugIt()
    def SetOperateMode(self):
        # PROTECTED REGION ID(DishMaster.SetOperateMode) ENABLED START #
        try:
            # Command to set Dish to OPERATE Mode
            self._admin_mode = 0                        # Set adminMode to ONLINE
            self.set_state(PyTango.DevState.ON)         # Set STATE to ON
            self._dish_mode = 8                         # set dishMode to OPERATE
            self.set_status("Dish is in OPERATE mode.")
            self.devlogmsg("Dish is in OPERATE mode", 4)
        except Exception as e:
            print "Unexpected error in executing SetOperateMode Command on Dish", self.ReceptorNumber
            self.devlogmsg("Unexpected error in executing SetOperateMode Command on Dish", 2)
            print "Error message is: \n", e
        pass
        # PROTECTED REGION END #    //  DishMaster.SetOperateMode

    def is_SetOperateMode_allowed(self):
        # PROTECTED REGION ID(DishMaster.is_SetOperateMode_allowed) ENABLED START #
        return self.get_state() not in [DevState.ON,DevState.OFF,DevState.FAULT,DevState.ALARM,DevState.UNKNOWN,DevState.DISABLE]
        # PROTECTED REGION END #    //  DishMaster.is_SetOperateMode_allowed

    @command(
    dtype_in='str', 
    doc_in="The timestamp indicates the time, in UTC, at which command execution should start.", 
    )
    @DebugIt()
    def Scan(self, argin):
        # PROTECTED REGION ID(DishMaster.Scan) ENABLED START #
        try:
            # Command to start SCAN
            if (self._pointing_state == 0):
                self._current_time = time.time()
                self._scan_execution_time = float(argin)
                self._scan_delta_t = self._scan_execution_time - self._current_time
                t1 = Timer(self._scan_delta_t, self.StartCapture, [argin])
                t1.start()
                self.devlogmsg("Scan in progress", 4)
            else:
                self.set_status("Dish Pointing State is not READY")
                self.devlogmsg("Dish Pointing State is not READY hence scan could not be started", 4)
        except Exception as e:
            print "Unexpected error in executing Scan Command on Dish", self.ReceptorNumber
            self.devlogmsg("Unexpected error in executing Scan Command on Dish", 2)
            print "Error message is: \n", e

        pass
        # PROTECTED REGION END #    //  DishMaster.Scan

    def is_Scan_allowed(self):
        # PROTECTED REGION ID(DishMaster.is_Scan_allowed) ENABLED START #
        return self.get_state() not in [DevState.OFF,DevState.FAULT,DevState.INIT,DevState.UNKNOWN,DevState.STANDBY,DevState.DISABLE]
        # PROTECTED REGION END #    //  DishMaster.is_Scan_allowed

    @command(
    dtype_in='str', 
    doc_in="The timestamp indicates the time, in UTC, at which command execution should start.", 
    )
    @DebugIt()
    def StartCapture(self, argin):
        # PROTECTED REGION ID(DishMaster.StartCapture) ENABLED START #
        try:
            # Command to start Data Capturing
            self._capturing = True                      # set Capturing to True
            self._pointing_state = 3                    # set pointingState to SCAN
            self.set_status("Data Capturing started.")
            self.devlogmsg("Data Capturing started", 4)
        except Exception as e:
            print "Unexpected error in executing StartCapture Command on Dish", self.ReceptorNumber
            self.devlogmsg("Unexpected error in executing StartCapture Command on Dish", 2)
            print "Error message is: \n", e
        pass
        # PROTECTED REGION END #    //  DishMaster.StartCapture

    def is_StartCapture_allowed(self):
        # PROTECTED REGION ID(DishMaster.is_StartCapture_allowed) ENABLED START #
        return self.get_state() not in [DevState.OFF,DevState.FAULT,DevState.INIT,DevState.UNKNOWN,DevState.STANDBY,DevState.DISABLE]
        # PROTECTED REGION END #    //  DishMaster.is_StartCapture_allowed

    @command(
    dtype_in='str', 
    doc_in="The timestamp indicates the time, in UTC, at which command execution should start.", 
    )
    @DebugIt()
    def StopCapture(self, argin):
        # PROTECTED REGION ID(DishMaster.StopCapture) ENABLED START #
        try:
            # Command to stop Data Capturing
            self._capturing = False                     # set Capturing to FALSE
            self._pointing_state = 0                    # set pointingState to READY
            self.set_status("Data Capturing stopped.")
            self.devlogmsg("Data Capturing stopped.", 4)
        except Exception as e:
            print "Unexpected error in executing StopCapture Command on Dish", self.ReceptorNumber
            self.devlogmsg("Unexpected error in executing StopCapture Command on Dish", 2)
            print "Error message is: \n", e
        pass
        # PROTECTED REGION END #    //  DishMaster.StopCapture

    def is_StopCapture_allowed(self):
        # PROTECTED REGION ID(DishMaster.is_StopCapture_allowed) ENABLED START #
        return self.get_state() not in [DevState.OFF,DevState.FAULT,DevState.INIT,DevState.UNKNOWN,DevState.STANDBY,DevState.DISABLE]
        # PROTECTED REGION END #    //  DishMaster.is_StopCapture_allowed

    @command(
    )
    @DebugIt()
    def SetStandbyFPMode(self):
        # PROTECTED REGION ID(DishMaster.SetStandbyFPMode) ENABLED START #
        try:
            # Command to set Dish to STANDBY-FP Mode
            self.set_state(PyTango.DevState.STANDBY)    # set STATE to STANDBY
            self._dish_mode = 4                         # set dishMode to STANDBY-FP
            self.set_status("Dish is in STANDBY-FP mode.")
            self.devlogmsg("Dish is in STANDBY-FP mode", 4)
        except Exception as e:
            print "Unexpected error in executing SetStandbyFPMode Command on Dish", self.ReceptorNumber
            self.devlogmsg("Unexpected error in executing SetStandbyFPMode Command on Dish", 2)
            print "Error message is: \n", e
        pass
        # PROTECTED REGION END #    //  DishMaster.SetStandbyFPMode

    def is_SetStandbyFPMode_allowed(self):
        # PROTECTED REGION ID(DishMaster.is_SetStandbyFPMode_allowed) ENABLED START #
        return self.get_state() not in [DevState.UNKNOWN,DevState.DISABLE]
        # PROTECTED REGION END #    //  DishMaster.is_SetStandbyFPMode_allowed

    @command(
    dtype_in='str', 
    doc_in="Timestamp at which command should be executed.", 
    )
    @DebugIt()
    def Slew(self, argin=0):
        # PROTECTED REGION ID(DishMaster.Slew) ENABLED START #
        try:
            # Execute POINT command at given timestamp
            self._current_time = time.time()
            self._point_execution_time = self._desired_pointing[0]
            self._point_delta_t = self._point_execution_time - self._current_time
            t = Timer(self._point_delta_t, self.point)
            t.start()
            self.devlogmsg("Dish is slewing ", 4)
        except Exception as e:
            print "Unexpected error in executing Slew Command on Dish", self.ReceptorNumber
            self.devlogmsg("Unexpected error in executing Slew Command on Dish", 2)
            print "Error message is: \n", e
        pass
        # PROTECTED REGION END #    //  DishMaster.Slew

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(DishMaster.main) ENABLED START #
    return run((DishMaster,), args=args, **kwargs)
    # PROTECTED REGION END #    //  DishMaster.main

if __name__ == '__main__':
    main()
