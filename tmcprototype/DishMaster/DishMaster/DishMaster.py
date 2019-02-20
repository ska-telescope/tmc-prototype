# -*- coding: utf-8 -*-
#
# This file is part of the DishMaster project
#
#
#
# Distributed under the terms of the BSD-3-Clause license.
# See LICENSE.txt for more info.

"""
SKA Dish Master TANGO device server
"""
from __future__ import print_function
from __future__ import absolute_import

import sys
import os
file_path = os.path.dirname(os.path.abspath(__file__))
module_path = os.path.abspath(os.path.join(file_path, os.pardir)) + "/DishMaster"
sys.path.insert(0, module_path)
print("sys.path: ", sys.path)

# PyTango imports
from builtins import str
from builtins import range
import tango
from tango import DebugIt, DevState, AttrWriteType
from tango.server import run, DeviceMeta, attribute, command, device_property
from skabase.SKAMaster.SKAMaster import SKAMaster
# Additional import
# PROTECTED REGION ID(DishMaster.additionnal_import) ENABLED START #
import time
from threading import Timer
import threading
import CONST
from future.utils import with_metaclass
import numpy
# PROTECTED REGION END #    //  DishMaster.additionnal_import

__all__ = ["DishMaster", "main"]


class DishMaster(with_metaclass(DeviceMeta, SKAMaster)):
# class DishMaster(SKAMaster):
    """
    SKA Dish Master TANGO device server
    """
    # PROTECTED REGION ID(DishMaster.class_variable) ENABLED START #

    # __metaclass__ =  SKAMaster

    # Function to set achieved pointing attribute to the desired pointing attribute
    def point(self):
        """ Points the dish towards the desired pointing coordinates. """
        if((self._achieved_pointing[1] != self._desired_pointing[1]) |
           (self._achieved_pointing[2] != self._desired_pointing[2])):
            try:
                self._azimuth_difference = self._desired_pointing[1] - self._achieved_pointing[1]
                print("azimuth difference is: ", self._azimuth_difference)
                self._elevation_difference = self._desired_pointing[2] - self._achieved_pointing[2]
                print("elevation difference is: ", (self._elevation_difference))
                self.change_azimuth_thread = threading.Thread(None, self.azimuth, 'DishMaster')
                self.change_elevation_thread = threading.Thread(None, self.elevation, 'DishMaster')
                self.change_azimuth_thread.start()
                self.change_elevation_thread.start()
                self._pointing_state = 1
            except Exception as except_occured:
                print(CONST.ERR_EXE_POINT_FN, self.ReceptorNumber)
                print(CONST.STR_ERR_MSG, except_occured)
        else:
            self.set_status(CONST.STR_DISH_POINT_ALREADY)
            self.dev_logging(CONST.STR_DISH_POINT_ALREADY, int(tango.LogLevel.LOG_INFO))

    def azimuth(self):
        """ Calculates the azimuth angle difference. """
        #time.sleep(1)
        self._pointing_state = 1
        azimuth_index = 1
        if self._azimuth_difference > 0.00:
            self.increment_position([azimuth_index, self._azimuth_difference])
        elif self._azimuth_difference < 0.00:
            self.decrement_position([azimuth_index, abs(self._azimuth_difference)])

    def elevation(self):
        """ Calculates the elevation angle difference. """
        self._pointing_state = 1
        elevation_index = 2
        if self._elevation_difference > 0.00:
            self.increment_position([elevation_index, self._elevation_difference])
        elif self._elevation_difference < 0.00:
            self.decrement_position([elevation_index, abs(self._elevation_difference)])

    def increment_position(self, argin):
        """
        Increments the current pointing coordinates gradually to match the desired pointing coordinates.
        :param argin: Difference between current and desired Azimuth/Elevation angle.
        :return: None
        """
        #input_increment = int(argin[1])
        input_increment = argin[1]
        #time.sleep(1)
        if abs(self._azimuth_difference) > abs(self._elevation_difference):
            max_increment = abs(self._azimuth_difference)
        elif abs(self._azimuth_difference) < abs(self._elevation_difference):
            max_increment = abs(self._elevation_difference)
        else:
            max_increment = input_increment

        if input_increment == max_increment:
            input_increment = input_increment + 0.01

        for position in numpy.arange(0, input_increment, 0.01):
            print(position)
            self.set_status(CONST.STR_DISH_POINT_INPROG)
            self.dev_logging(CONST.STR_DISH_POINT_INPROG, int(tango.LogLevel.LOG_INFO))
            self._pointing_state = 1
            time.sleep(0.01)
            if (self._achieved_pointing[1] == self._desired_pointing[1]) and (
                    self._achieved_pointing[2] == self._desired_pointing[2]):
                self._pointing_state = 0
                self.set_status(CONST.STR_DISH_POINT_SUCCESS)
                self.dev_logging(CONST.STR_DISH_POINT_SUCCESS, int(tango.LogLevel.LOG_INFO))
            else:
                self._achieved_pointing[argin[0]] = round((self._achieved_pointing[argin[0]] + 0.01), 2)


    def decrement_position(self, argin):
        """
        Decrements the current pointing coordinates gradually to match the desired pointing coordinates.
        :param argin: Difference between current and desired Azimuth/Elevation angle.
        :return: None
        """
        input_decrement = argin[1]
        #time.sleep(2)
        if abs(self._azimuth_difference) > abs(self._elevation_difference):
            max_decrement = abs(self._azimuth_difference)
        elif abs(self._azimuth_difference) < abs(self._elevation_difference):
            max_decrement = abs(self._elevation_difference)
        else:
            max_decrement = input_decrement
        if input_decrement == max_decrement:
            input_decrement = input_decrement + 0.01

        for position in numpy.arange(0, input_decrement, 0.01):
            self.set_status(CONST.STR_DISH_POINT_INPROG)
            self.dev_logging(CONST.STR_DISH_POINT_INPROG, int(tango.LogLevel.LOG_INFO))
            self._pointing_state = 1
            time.sleep(0.01)
            if (self._achieved_pointing[1] == self._desired_pointing[1]) and (
                    self._achieved_pointing[2] == self._desired_pointing[2]):
                self._pointing_state = 0
                self.set_status(CONST.STR_DISH_POINT_SUCCESS)
                self.dev_logging(CONST.STR_DISH_POINT_SUCCESS, int(tango.LogLevel.LOG_INFO))
            else:
                self._achieved_pointing[argin[0]] = round((self._achieved_pointing[argin[0]] - 0.01), 2)

    def check_slew(self):
        """
        Waits until the Dish is slewing and stows it later.
        :return: None
        """
        while True:
            if self._pointing_state != 1:
                self._admin_mode = 1                        # Set adminMode to OFFLINE
                self.set_state(DevState.DISABLE)            # Set STATE to DISABLE
                self._dish_mode = 6                         # Set dishMode to STOW
                self._health_state = 0                      # Set healthState to OK
                self.set_status(CONST.STR_DISH_STOW_SUCCESS)
                self.dev_logging(CONST.STR_DISH_STOW_SUCCESS, int(tango.LogLevel.LOG_INFO))
                break

    # PROTECTED REGION END #    //DishMaster.class_variable

    # -----------------
    # Device Properties
    # -----------------
    ReceptorNumber = device_property(
        dtype='uint',
        doc="Number of Receptor ",
    )

    # ----------
    # Attributes
    # ----------
    dishMode = attribute(
        dtype='DevEnum',
        enum_labels=["OFF", "STARTUP", "SHUTDOWN", "STANDBY-LP",
                     "STANDBY-FP", "MAINTENANCE", "STOW", "CONFIG", "OPERATE", ],
        doc="Mode of the dish",
    )

    pointingState = attribute(
        dtype='DevEnum',
        enum_labels=["READY", "SLEW", "TRACK", "SCAN", ],
        doc="Pointing state of the dish",

    )

    band1SamplerFrequency = attribute(
        dtype='double',
        access=AttrWriteType.WRITE,
        doc="Band1 Sampler Frequency of the dish",
    )

    band2SamplerFrequency = attribute(
        dtype='double',
        access=AttrWriteType.WRITE,
        doc="Band2 Sampler Frequency of the dish",
    )

    band3SamplerFrequency = attribute(
        dtype='double',
        access=AttrWriteType.WRITE,
        doc="Band3 Sampler Frequency of the dish",
    )

    band4SamplerFrequency = attribute(
        dtype='double',
        access=AttrWriteType.WRITE,
        doc="Band4 Sampler Frequency of the dish",
    )

    band5aSamplerFrequency = attribute(
        dtype='double',
        access=AttrWriteType.WRITE,
        doc="Band5a Sampler Frequency of the dish",
    )

    band5bSamplerFrequency = attribute(
        dtype='double',
        access=AttrWriteType.WRITE,
        doc="Band5b Sampler Frequency of the dish",
    )

    capturing = attribute(
        dtype='bool',
        doc="Data Capturing of the dish",
    )

    ConfiguredBand = attribute(
        dtype='DevEnum',
        enum_labels=["BAND1", "BAND2", "BAND3", "BAND4", "BAND5a", "BAND5b", "NONE", ],
        doc="Configured band of the dish",
    )

    WindSpeed = attribute(
        dtype='double',
        access=AttrWriteType.READ_WRITE,
        unit="km/h",
        doc="Wind speed of the dish",

    )

    desiredPointing = attribute(
        dtype=('double',),
        access=AttrWriteType.READ_WRITE,
        max_dim_x=7,
        doc="Desired pointing coordinates of the dish",
    )

    achievedPointing = attribute(
        dtype=('double',),
        max_dim_x=7,
        doc="Achieved pointing coordinates of the dish",
    )

    # ---------------
    # General methods
    # ---------------
    def init_device(self):
        """
        Initializes the properties and attributes of DishMaster.
        :return: None
        """
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
            self._desired_pointing = [0, 2, 4]
            self._achieved_pointing = [0, 0, 0]
            self._elevation_difference = 0
            self._azimuth_difference = 0
            self._configured_band = 1
            self._wind_speed = 5
            self.set_state(DevState.STANDBY)            # Set STATE to STANDBY
            # Initialise Point command variables
            self._current_time = 0
            self._point_execution_time = 0
            self._point_delta_t = 0
            # Initialise Scan command variables
            self._scan_execution_time = 0
            self._scan_delta_t = 0
            self.set_status(CONST.STR_DISH_INIT_SUCCESS)
            self.dev_logging(CONST.STR_DISH_INIT_SUCCESS, int(tango.LogLevel.LOG_INFO))
        except Exception as except_occured:
            print(CONST.ERR_INIT_PROP_ATTR_DISH, self.ReceptorNumber)
            self.dev_logging(CONST.ERR_INIT_PROP_ATTR_DISH, int(tango.LogLevel.LOG_ERROR))
            print(CONST.STR_ERR_MSG, except_occured)
        # PROTECTED REGION END #    //  DishMaster.always_executed_hook

    def always_executed_hook(self):
        # PROTECTED REGION ID(DishMaster.always_executed_hook) ENABLED START #
        """ Internal construct of TANGO. """
        # PROTECTED REGION END #    //  DishMaster.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(DishMaster.delete_device) ENABLED START #
        """ Internal construct of TANGO. """
        # PROTECTED REGION END #    //  DishMaster.delete_device

    # ------------------
    # Attributes methods
    # ------------------
    def read_dishMode(self):
        # PROTECTED REGION ID(DishMaster.dishMode_read) ENABLED START #
        """ Returns the dishMode. """
        return self._dish_mode
        # PROTECTED REGION END #    //  DishMaster.dishMode_read

    def read_pointingState(self):
        # PROTECTED REGION ID(DishMaster.pointingState_read) ENABLED START #
        """ Returns the pointingState. """
        return self._pointing_state
        # PROTECTED REGION END #    //  DishMaster.pointingState_read

    def write_band1SamplerFrequency(self, value):
        # PROTECTED REGION ID(DishMaster.band1SamplerFrequency_write) ENABLED START #
        """ Sets the band1 sampler frequency.
        :param value: band1SamplerFrequency
        :return: None
        """
        self._band1_sampler_frequency = value
        # PROTECTED REGION END #    //  DishMaster.band1SamplerFrequency_write

    def write_band2SamplerFrequency(self, value):
        # PROTECTED REGION ID(DishMaster.band2SamplerFrequency_write) ENABLED START #
        """
        Sets the band2 sampler frequency.
        :param value: band2SamplerFrequency
        :return: None
        """
        self._band2_sampler_frequency = value
        # PROTECTED REGION END #    //  DishMaster.band2SamplerFrequency_write

    def write_band3SamplerFrequency(self, value):
        # PROTECTED REGION ID(DishMaster.band3SamplerFrequency_write) ENABLED START #
        """
        Sets the band3 sampler frequency.
        :param value: band3SamplerFrequency
        :return: None
        """
        self._band3_sampler_frequency = value
        # PROTECTED REGION END #    //  DishMaster.band3SamplerFrequency_write

    def write_band4SamplerFrequency(self, value):
        # PROTECTED REGION ID(DishMaster.band4SamplerFrequency_write) ENABLED START #
        """
        Sets band4 sampler frequency.
        :param value: band4SamplerFrequency
        :return: None
        """
        self._band4_sampler_frequency = value
        # PROTECTED REGION END #    //  DishMaster.band4SamplerFrequency_write

    def write_band5aSamplerFrequency(self, value):
        # PROTECTED REGION ID(DishMaster.band5aSamplerFrequency_write) ENABLED START #
        """
        Sets the band5a sampler frequency.
        :param value: band5aSamplerFrequency
        :return: None
        """
        self._band5a_sampler_frequency = value
        # PROTECTED REGION END #    //  DishMaster.band5aSamplerFrequency_write

    def write_band5bSamplerFrequency(self, value):
        # PROTECTED REGION ID(DishMaster.band5bSamplerFrequency_write) ENABLED START #
        """
        Sets the band5b sampler frequency.
        :param value: band5bSamplerFrequency
        :return: None
        """
        self._band5b_sampler_frequency = value
        # PROTECTED REGION END #    //  DishMaster.band5bSamplerFrequency_write

    def read_capturing(self):
        # PROTECTED REGION ID(DishMaster.capturing_read) ENABLED START #
        """ Returns true if the dish is capturing the data, else false. """
        return self._capturing
        # PROTECTED REGION END #    //  DishMaster.capturing_read

    def read_ConfiguredBand(self):
        # PROTECTED REGION ID(DishMaster.ConfiguredBand_read) ENABLED START #
        """ Returns the band configured for the Dish. """
        return self._configured_band
        # PROTECTED REGION END #    //  DishMaster.ConfiguredBand_read

    def read_WindSpeed(self):
        # PROTECTED REGION ID(DishMaster.WindSpeed_read) ENABLED START #
        """ Returns the Wind speed. """
        return self._wind_speed
        # PROTECTED REGION END #    //  DishMaster.WindSpeed_read

    def write_WindSpeed(self, value):
        # PROTECTED REGION ID(DishMaster.WindSpeed_write) ENABLED START #
        """
        Sets the wind speed.
        :param value: WindSpeed
        :return: None
        """
        self._wind_speed = value
        # PROTECTED REGION END #    //  DishMaster.WindSpeed_write

    def read_desiredPointing(self):
        # PROTECTED REGION ID(DishMaster.desiredPointing_read) ENABLED START #
        """ Returns the desired pointing coordinates of Dish. """
        return self._desired_pointing
        # PROTECTED REGION END #    //  DishMaster.desiredPointing_read

    def write_desiredPointing(self, value):
        # PROTECTED REGION ID(DishMaster.desiredPointing_write) ENABLED START #
        """
        Sets the desired pointing coordinates of Dish.
        :param value: desiredPointing
        :return: None
        """
        self._desired_pointing = value
        # PROTECTED REGION END #    //  DishMaster.desiredPointing_write

    def read_achievedPointing(self):
        # PROTECTED REGION ID(DishMaster.achievedPointing_read) ENABLED START #
        """ Returns the achieved pointing coordinates of Dish. """
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
        """
        Triggers the Dish to transition into the STOW Dish Element Mode. Used to point the dish
        in a direction that minimises the wind loads on the structure,for survival in strong
        wind conditions. The Dish is able to observe in the stove position, for the purpose of
        transient detection.
        """
        try:
            # Command to set Dish to STOW Mode
            self._desired_pointing = [0, 0, 0]
            self.Slew("0")
            time.sleep(1)
            self.stow_thread = threading.Thread(None, self.check_slew, 'DishMaster')
            self.stow_thread.start()
        except Exception as except_occured:
            print(CONST.ERR_EXE_SET_STOW_MODE_CMD, self.ReceptorNumber)
            self.dev_logging(CONST.ERR_EXE_SET_STOW_MODE_CMD, int(tango.LogLevel.LOG_ERROR))
            print(CONST.STR_ERR_MSG, except_occured)
        # PROTECTED REGION END #    //  DishMaster.SetStowMode

    def is_SetStowMode_allowed(self):
        # PROTECTED REGION ID(DishMaster.is_SetStowMode_allowed) ENABLED START #
        """ Checks if the SetStowMode is allowed in the current state of DishMaster. """
        return self.get_state() not in [DevState.ON, DevState.ALARM]
        # PROTECTED REGION END #    //  DishMaster.is_SetStowMode_allowed

    @command(
    )
    @DebugIt()
    def SetStandbyLPMode(self):
        # PROTECTED REGION ID(DishMaster.SetStandbyLPMode) ENABLED START #
        """
        Triggers the Dish to transition into the STANDBY-LP (Standby-Low power) Dish Element Mode.
        Standby-LP is the default mode when the Dish is configured for low power consumption.
        It is the mode wherein Dish ends after a start up procedure.
        """
        try:
            # Command to set Dish to STANDBY-LP Mode
            self.set_state(DevState.STANDBY)             # Set STATE to STANDBY
            self._dish_mode = 3                          # set dishMode to STANDBYLP
            self.set_status(CONST.STR_DISH_STANDBYLP_MODE)
            self.dev_logging(CONST.STR_DISH_STANDBYLP_MODE, int(tango.LogLevel.LOG_INFO))
        except Exception as except_occured:
            print(CONST.ERR_EXE_SET_STNBYLP_MODE_CMD, self.ReceptorNumber)
            self.set_status(str(except_occured))
            self.dev_logging(CONST.ERR_EXE_SET_STNBYLP_MODE_CMD, int(tango.LogLevel.LOG_ERROR))
            print(CONST.STR_ERR_MSG, except_occured)
        # PROTECTED REGION END #    //  DishMaster.SetStandbyLPMode

    def is_SetStandbyLPMode_allowed(self):
        # PROTECTED REGION ID(DishMaster.is_SetMaintenanceMode_allowed) ENABLED START #
        return self._pointing_state not in [1, 2, 3]
        # PROTECTED REGION END #    //  DishMaster.is_SetMaintenanceMode_allowed

    @command(
    )
    @DebugIt()
    def SetMaintenanceMode(self):
        # PROTECTED REGION ID(DishMaster.SetMaintenanceMode) ENABLED START #
        """
        Triggers the Dish to transition into the MAINTENANCE Dish Element Mode. This mode will also
        enable engineers and maintainers to upgrade SW and FW. Dish also enters this mode when an
        emergency stop button is pressed.
        """
        try:
            # Command to set Dish to MAINTENANCE Mode
            self._admin_mode = 2                        # Set adminMode to MAINTENANCE
            self.set_state(DevState.DISABLE)            # Set STATE to DISABLE
            self._dish_mode = 5                         # set dishMode to MAINTENANCE
            self.set_status(CONST.STR_DISH_MAINT_MODE)
            self.dev_logging(CONST.STR_DISH_MAINT_MODE, int(tango.LogLevel.LOG_INFO))
        except Exception as except_occured:
            print(CONST.ERR_EXE_SET_MAINT_MODE_CMD, self.ReceptorNumber)
            self.dev_logging(CONST.ERR_EXE_SET_MAINT_MODE_CMD, int(tango.LogLevel.LOG_ERROR))
            print(CONST.STR_ERR_MSG, except_occured)
        # PROTECTED REGION END #    //  DishMaster.SetMaintenanceMode

    def is_SetMaintenanceMode_allowed(self):
        # PROTECTED REGION ID(DishMaster.is_SetMaintenanceMode_allowed) ENABLED START #
        """ Checks if SetMaintenanceMode is allowed in the current state of DishMaster."""
        return self.get_state() not in [DevState.ON, DevState.ALARM, DevState.DISABLE]
        # PROTECTED REGION END #    //  DishMaster.is_SetMaintenanceMode_allowed

    @command(
    )
    @DebugIt()
    def SetOperateMode(self):
        """
        Triggers the Dish to transition into the OPERATE Dish Element Mode.
        :return: None
        """
        # PROTECTED REGION ID(DishMaster.SetOperateMode) ENABLED START #
        try:
            # Command to set Dish to OPERATE Mode
            self._admin_mode = 0                        # Set adminMode to ONLINE
            self.set_state(DevState.ON)                 # Set STATE to ON
            self._dish_mode = 8                         # set dishMode to OPERATE
            self.set_status(CONST.STR_DISH_OPERATE_MODE)
            self.dev_logging(CONST.STR_DISH_OPERATE_MODE, int(tango.LogLevel.LOG_INFO))
        except Exception as except_occured:
            print(CONST.ERR_EXE_SET_OPERATE_MODE_CMD, self.ReceptorNumber)
            self.dev_logging(CONST.ERR_EXE_SET_OPERATE_MODE_CMD, int(tango.LogLevel.LOG_ERROR))
            print(CONST.STR_ERR_MSG, except_occured)
        # PROTECTED REGION END #    //  DishMaster.SetOperateMode

    def is_SetOperateMode_allowed(self):
        # PROTECTED REGION ID(DishMaster.is_SetOperateMode_allowed) ENABLED START #
        """ Checks if SetOperateMode is allowed in the current state of DishMaster."""
        return self.get_state() not in [DevState.ON, DevState.OFF, DevState.FAULT,
                                        DevState.ALARM, DevState.UNKNOWN, DevState.DISABLE]
        # PROTECTED REGION END #    //  DishMaster.is_SetOperateMode_allowed

    @command(
        dtype_in='str',
        doc_in="The timestamp indicates the time, in UTC, at which command execution"
               " should start.",
    )
    @DebugIt()
    def Scan(self, argin):
        # PROTECTED REGION ID(DishMaster.Scan) ENABLED START #
        """
        Triggers the dish to start scanning at the set pointing coordinates and capture the data at the
        input timestamp.
        :param argin: timestamp
        :return: None
        """
        try:
            # Command to start SCAN
            if self._pointing_state == 0:
                self._current_time = time.time()
                self._scan_execution_time = float(argin)
                self._scan_delta_t = self._scan_execution_time - self._current_time
                schedule_scan_thread = Timer(self._scan_delta_t, self.StartCapture, [argin])
                schedule_scan_thread.start()
                self.dev_logging(CONST.STR_SCAN_INPROG, int(tango.LogLevel.LOG_INFO))
            else:
                self.set_status(CONST.STR_DISH_NOT_READY)
                self.dev_logging(CONST.STR_DISH_NOT_READY, int(tango.LogLevel.LOG_INFO))
        except Exception as except_occured:
            print(CONST.ERR_EXE_SCAN_CMD, self.ReceptorNumber)
            self.dev_logging(CONST.ERR_EXE_SCAN_CMD, int(tango.LogLevel.LOG_ERROR))
            print(CONST.STR_ERR_MSG, except_occured)
        # PROTECTED REGION END #    //  DishMaster.Scan

    def is_Scan_allowed(self):
        # PROTECTED REGION ID(DishMaster.is_Scan_allowed) ENABLED START #
        """ Checks if the Scan is allowed in the current state of DishMaster. """
        return self.get_state() not in [DevState.OFF, DevState.FAULT, DevState.INIT,
                                        DevState.UNKNOWN, DevState.STANDBY, DevState.DISABLE]
        # PROTECTED REGION END #    //  DishMaster.is_Scan_allowed

    @command(
        dtype_in='str',
        doc_in="The timestamp indicates the time, in UTC, at which command execution"
               " should start.",
    )
    @DebugIt()
    def StartCapture(self, argin):
        # PROTECTED REGION ID(DishMaster.StartCapture) ENABLED START #
        """
        Triggers the dish to start capturing the data on the configured band.
        :param argin: timestamp
        :return: None
        """
        try:
            if type(float(argin)) == float:
                if (self._capturing == False):
                    # Command to start Data Capturing
                    self._capturing = True                      # set Capturing to True
                    self._pointing_state = 3                    # set pointingState to SCAN
                    self.set_status(CONST.STR_DATA_CAPTURE_STRT)
                    self.dev_logging(CONST.STR_DATA_CAPTURE_STRT, int(tango.LogLevel.LOG_INFO))
                else:
                    self.set_status(CONST.STR_DATA_CAPTURE_ALREADY_STARTED)
                    self.dev_logging(CONST.STR_DATA_CAPTURE_ALREADY_STARTED, int(tango.LogLevel.LOG_INFO))
        except Exception as except_occured:
            print(CONST.ERR_EXE_STRT_CAPTURE_CMD, self.ReceptorNumber)
            self.dev_logging(CONST.ERR_EXE_STRT_CAPTURE_CMD, int(tango.LogLevel.LOG_ERROR))
            print(CONST.STR_ERR_MSG, except_occured)
        # PROTECTED REGION END #    //  DishMaster.StartCapture

    def is_StartCapture_allowed(self):
        """ Checks if the StartCapture is allowed in the current state of DishMaster. """
        # PROTECTED REGION ID(DishMaster.is_StartCapture_allowed) ENABLED START #
        return self.get_state() not in [DevState.OFF, DevState.FAULT, DevState.INIT,
                                        DevState.UNKNOWN, DevState.STANDBY, DevState.DISABLE]
        # PROTECTED REGION END #    //  DishMaster.is_StartCapture_allowed

    @command(
        dtype_in='str',
        doc_in="The timestamp indicates the time, in UTC, at which command execution should start",
    )
    @DebugIt()
    def StopCapture(self, argin):
        # PROTECTED REGION ID(DishMaster.StopCapture) ENABLED START #
        """
        Triggers the dish to stop capturing the data on the configured band.
        :param argin: timestamp
        :return: None
        """
        try:
            if type(float(argin)) == float:
                if (self._capturing == True):
                    # Command to stop Data Capturing
                    self._capturing = False                     # set Capturing to FALSE
                    self._pointing_state = 0                    # set pointingState to READY
                    self.set_status(CONST.STR_DATA_CAPTURE_STOP)
                    self.dev_logging(CONST.STR_DATA_CAPTURE_STOP, int(tango.LogLevel.LOG_INFO))
                else:
                    self.set_status(CONST.STR_DATA_CAPTURE_ALREADY_STOPPED)
                    self.dev_logging(CONST.STR_DATA_CAPTURE_ALREADY_STOPPED, int(tango.LogLevel.LOG_INFO))
        except Exception as except_occured:
            print(CONST.ERR_EXE_STOP_CAPTURE_CMD, self.ReceptorNumber)
            self.dev_logging(CONST.ERR_EXE_STOP_CAPTURE_CMD, int(tango.LogLevel.LOG_ERROR))
            print(CONST.STR_ERR_MSG, except_occured)
        # PROTECTED REGION END #    //  DishMaster.StopCapture

    def is_StopCapture_allowed(self):
        # PROTECTED REGION ID(DishMaster.is_StopCapture_allowed) ENABLED START #
        """ Checks if the StopCapture is allowed in the current state of DishMaster. """
        return self.get_state() not in [DevState.OFF, DevState.FAULT, DevState.INIT,
                                        DevState.UNKNOWN, DevState.STANDBY, DevState.DISABLE]
        # PROTECTED REGION END #    //  DishMaster.is_StopCapture_allowed

    @command(
    )
    @DebugIt()
    def SetStandbyFPMode(self):
        # PROTECTED REGION ID(DishMaster.SetStandbyFPMode) ENABLED START #
        """
        Triggers the Dish to transition into the STANDBY-FP (Standby-Full power) Dish Element Mode.
        :return: None
        """
        try:
            # Command to set Dish to STANDBY-FP Mode
            self.set_state(DevState.STANDBY)            # set STATE to STANDBY
            self._dish_mode = 4                         # set dishMode to STANDBY-FP
            self.set_status(CONST.STR_DISH_STANDBYFP_MODE)
            self.dev_logging(CONST.STR_DISH_STANDBYFP_MODE, int(tango.LogLevel.LOG_INFO))
        except Exception as except_occured:
            print(CONST.ERR_EXE_SET_STNBYFP_MODE_CMD, self.ReceptorNumber)
            self.dev_logging(CONST.ERR_EXE_SET_STNBYFP_MODE_CMD, int(tango.LogLevel.LOG_ERROR))
            print(CONST.STR_ERR_MSG, except_occured)
        # PROTECTED REGION END #    //  DishMaster.SetStandbyFPMode

    def is_SetStandbyFPMode_allowed(self):
        # PROTECTED REGION ID(DishMaster.is_SetStandbyFPMode_allowed) ENABLED START #
        """ Checks if the SetStandbyFPMode is allowed in the current state of DishMaster. """
        return self.get_state() not in [DevState.UNKNOWN, DevState.DISABLE]
        # PROTECTED REGION END #    //  DishMaster.is_SetStandbyFPMode_allowed

    @command(
        dtype_in='str',
        doc_in="Timestamp at which command should be executed.",
    )
    @DebugIt()
    def Slew(self, argin=0):
        # PROTECTED REGION ID(DishMaster.Slew) ENABLED START #
        """
        Triggers the Dish to move (or slew) at the commanded pointing coordinates.
        :param argin: timestamp
        :return: None
        """
        try:
            print("Argin In DishMaster: ", self._desired_pointing)
            if type(float(argin)) == float:
                # Execute POINT command at given timestamp
                self._current_time = time.time()
                self._point_execution_time = self._desired_pointing[0]
                self._point_delta_t = self._point_execution_time - self._current_time
                schedule_slew_thread = Timer(self._point_delta_t, self.point)
                schedule_slew_thread.start()
                self.dev_logging(CONST.STR_DISH_SLEW, int(tango.LogLevel.LOG_INFO))
        except Exception as except_occured:
            print(CONST.ERR_EXE_SLEW_CMD, self.ReceptorNumber)
            self.dev_logging(CONST.ERR_EXE_SLEW_CMD, int(tango.LogLevel.LOG_ERROR))
            print(CONST.STR_ERR_MSG, except_occured)
        # PROTECTED REGION END #    //  DishMaster.Slew

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(DishMaster.main) ENABLED START #
    """
    Runs the DishMaster.
    :param args: Arguments internal to TANGO
    :param kwargs: Arguments internal to TANGO
    :return: DishMaster TANGO object.
    """
    return run((DishMaster,), args=args, **kwargs)
    # PROTECTED REGION END #    //  DishMaster.main


if __name__ == '__main__':
    main()
