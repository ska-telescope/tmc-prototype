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

# Additional import
# PROTECTED REGION ID(DishMaster.additionnal_import) ENABLED START #
import time
import threading
from threading import Timer

# tango imports
import tango
from tango import DebugIt, DevState, AttrWriteType
from tango.server import run, DeviceMeta, attribute, command, device_property
from SKAMaster import SKAMaster

import CONST

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
        """ This method sets achieved pointing attribute to the desired pointing attribute """
        if((self._achieved_pointing[1] != self._desired_pointing[1]) |
           (self._achieved_pointing[2] != self._desired_pointing[2])):
            try:
                self.azimuth_thread = threading.Thread(None, self.azimuth, 'DishMaster')
                self.elevation_thread = threading.Thread(None, self.elevation, 'DishMaster')
                self.azimuth_thread.start()
                self.elevation_thread.start()
                self._pointing_state = 1

            except Exception as except_occured:
                print CONST.ERR_EXE_POINT_FN, self.ReceptorNumber
                print CONST.STR_ERR_MSG, except_occured

    def azimuth(self):
        """ This method calculates the azimuth difference """
        self._pointing_state = 1
        self._azimuth_difference = self._desired_pointing[1] - self._achieved_pointing[1]
        if self._azimuth_difference > 0.0:
            self.increment_position([1, self._azimuth_difference])
        elif self._azimuth_difference < 0.0:
            self.decrement_position([1, abs(self._azimuth_difference)])

    def elevation(self):
        """ This method calculates the elevation difference """
        self._pointing_state = 1
        self._elevation_difference = self._desired_pointing[2] - self._achieved_pointing[2]
        if self._elevation_difference > 0.0:
            self.increment_position([2, self._elevation_difference])
        elif self._elevation_difference < 0.0:
            self.decrement_position([2, abs(self._elevation_difference)])

    def increment_position(self, argin):
        """
        This method gradually the increments the Dish to the desired coordinates
        :param argin:
        :return:
        """
        temp = int(argin[1])
        time.sleep(2)
        if abs(self._azimuth_difference) > abs(self._elevation_difference):
            temp1 = abs(self._azimuth_difference)
        elif abs(self._azimuth_difference) < abs(self._elevation_difference):
            temp1 = abs(self._elevation_difference)
        else:
            temp1 = temp

        if temp == temp1:
            temp = temp + 1

        for position in range(0, temp):
            self.set_status(CONST.STR_DISH_POINT_INPROG)
            self.devlogmsg(CONST.STR_DISH_POINT_INPROG, 4)
            self._pointing_state = 1
            time.sleep(2)
            if (self._achieved_pointing[1] == self._desired_pointing[1])\
                and (self._achieved_pointing[2] == self._desired_pointing[2]):
                self._pointing_state = 0
                self.set_status(CONST.STR_DISH_POINT_INPROG)
                self.devlogmsg(CONST.STR_DISH_POINT_INPROG, 4)
            else:
                self._achieved_pointing[argin[0]] = self._achieved_pointing[argin[0]] + 1

    def decrement_position(self, argin):
        """
        This method gradually the decrements the Dish to the desired coordinates
        :param argin:
        :return:
        """
        temp2 = int(argin[1])
        time.sleep(2)
        if abs(self._azimuth_difference) > abs(self._elevation_difference):
            temp3 = abs(self._azimuth_difference)
        elif abs(self._azimuth_difference) < abs(self._elevation_difference):
            temp3 = abs(self._elevation_difference)
        else:
            temp3 = temp2

        if temp2 == temp3:
            temp2 = temp2 + 1


        for position in range(0, (temp2)):
            self.set_status(CONST.STR_DISH_POINT_INPROG)
            self._pointing_state = 1
            time.sleep(2)
            if (self._achieved_pointing[1] == self._desired_pointing[1])\
                and (self._achieved_pointing[2] == self._desired_pointing[2]):
                self._pointing_state = 0
                self.set_status(CONST.STR_DISH_POINT_SUCCESS)
                self.devlogmsg(CONST.STR_DISH_POINT_SUCCESS, 4)

            else:
                self._achieved_pointing[argin[0]] = self._achieved_pointing[argin[0]] - 1


    def check_slew(self):
        """
        This method sets the Dish in slew position
        :return:
        """
        while True:
            print"in while loop"
            if self._pointing_state != 1:
                print "in if loop"
                self._admin_mode = 1                        # Set adminMode to OFFLINE
                self.set_state(tango.DevState.DISABLE)    # Set STATE to DISABLE
                self._dish_mode = 6                         # set dishMode to STOW
                self._health_state = 0                      # Set healthState to OK
                self.set_status(CONST.STR_DISH_STOW_SUCCESS)
                self.devlogmsg(CONST.STR_DISH_STOW_SUCCESS, 4)
                break


    # PROTECTED REGION END #    //DishMaster.class_variable

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
        enum_labels=["OFF", "STARTUP", "SHUTDOWN", "STANDBY-LP",
                     "STANDBY-FP", "MAINTENANCE", "STOW", "CONFIG", "OPERATE", ],
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
        """
        This method initializes the properties, attributes and command variables
        :return:
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
            self._desired_pointing = [0, 20, 40]
            self._achieved_pointing = [0, 0, 0]
            self._elevation_difference = 0
            self._azimuth_difference = 0
            self._configured_band = 1
            self._wind_speed = 5
            self.set_state(tango.DevState.STANDBY)    # Set STATE to STANDBY

            # Initialise Point command variables
            self._current_time = 0
            self._point_execution_time = 0
            self._point_delta_t = 0

            # Initialise Scan command variables
            self._scan_execution_time = 0
            self._scan_delta_t = 0

            self.set_status(CONST.STR_DISH_INIT_SUCCESS)
            self.devlogmsg(CONST.STR_DISH_INIT_SUCCESS, 4)

        except Exception as except_occured:
            print CONST.ERR_INIT_PROP_ATTR_DISH, self.ReceptorNumber
            self.devlogmsg("Unexpected error in initialising properties and attributes on Dish", 2)
            print CONST.STR_ERR_MSG, except_occured

        # PROTECTED REGION END #    //  DishMaster.always_executed_hook

    def always_executed_hook(self):
        # PROTECTED REGION ID(DishMaster.always_executed_hook) ENABLED START #
        """ This method is an internal construct of TANGO """
        # PROTECTED REGION END #    //  DishMaster.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(DishMaster.delete_device) ENABLED START #
        """ This method is an internal construct of TANGO """
        # PROTECTED REGION END #    //  DishMaster.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    def read_dishMode(self):
        # PROTECTED REGION ID(DishMaster.dishMode_read) ENABLED START #
        """ This is a getter method for the dishMode attribute """
        return self._dish_mode
        # PROTECTED REGION END #    //  DishMaster.dishMode_read

    def read_pointingState(self):
        # PROTECTED REGION ID(DishMaster.pointingState_read) ENABLED START #
        """ This is a getter method for the pointingState attribute """
        return self._pointing_state
        # PROTECTED REGION END #    //  DishMaster.pointingState_read

    def write_band1SamplerFrequency(self, value):
        # PROTECTED REGION ID(DishMaster.band1SamplerFrequency_write) ENABLED START #
        """
        This is a setter method for the band1SamplerFrequency attribute
        :param value: band1SamplerFrequency
        :return:
        """
        self._band1_sampler_frequency = value
        # PROTECTED REGION END #    //  DishMaster.band1SamplerFrequency_write

    def write_band2SamplerFrequency(self, value):
        # PROTECTED REGION ID(DishMaster.band2SamplerFrequency_write) ENABLED START #
        """
        This is a setter method for the band2SamplerFrequency attribute
        :param value: band2SamplerFrequency
        :return:
        """
        self._band2_sampler_frequency = value
        # PROTECTED REGION END #    //  DishMaster.band2SamplerFrequency_write

    def write_band3SamplerFrequency(self, value):
        # PROTECTED REGION ID(DishMaster.band3SamplerFrequency_write) ENABLED START #
        """
        This is a setter method for the band3SamplerFrequency attribute
        :param value: band3SamplerFrequency
        :return:
        """
        self._band3_sampler_frequency = value
        # PROTECTED REGION END #    //  DishMaster.band3SamplerFrequency_write

    def write_band4_samplerfrequency(self, value):
        # PROTECTED REGION ID(DishMaster.band4SamplerFrequency_write) ENABLED START #
        """
        This is a setter method for the band4SamplerFrequency attribute
        :param value: band4SamplerFrequency
        :return:
        """
        self._band4_sampler_frequency = value
        # PROTECTED REGION END #    //  DishMaster.band4SamplerFrequency_write

    def write_band5aSamplerFrequency(self, value):
        # PROTECTED REGION ID(DishMaster.band5aSamplerFrequency_write) ENABLED START #
        """
        This is a setter method for the band5aSamplerFrequency attribute
        :param value: band5aSamplerFrequency
        :return:
        """
        self._band5a_sampler_frequency = value
        # PROTECTED REGION END #    //  DishMaster.band5aSamplerFrequency_write

    def write_band5bSamplerFrequency(self, value):
        # PROTECTED REGION ID(DishMaster.band5bSamplerFrequency_write) ENABLED START #
        """
        This is a setter method for the band5bSamplerFrequency attribute
        :param value: band5bSamplerFrequency
        :return:
        """
        self._band5b_sampler_frequency = value
        # PROTECTED REGION END #    //  DishMaster.band5bSamplerFrequency_write

    def read_capturing(self):
        # PROTECTED REGION ID(DishMaster.capturing_read) ENABLED START #
        """ This is a getter method for the capturing attribute """
        return self._capturing
        # PROTECTED REGION END #    //  DishMaster.capturing_read

    def read_ConfiguredBand(self):
        # PROTECTED REGION ID(DishMaster.ConfiguredBand_read) ENABLED START #
        """ This is a getter method for the ConfiguredBand attribute """
        return self._configured_band
        # PROTECTED REGION END #    //  DishMaster.ConfiguredBand_read

    def read_WindSpeed(self):
        # PROTECTED REGION ID(DishMaster.WindSpeed_read) ENABLED START #
        """ This is a getter method for the WindSpeed attribute """
        return self._wind_speed
        # PROTECTED REGION END #    //  DishMaster.WindSpeed_read

    def write_WindSpeed(self, value):
        # PROTECTED REGION ID(DishMaster.WindSpeed_write) ENABLED START #
        """
        This is a setter method for the WindSpeed attribute
        :param value: WindSpeed
        :return:
        """
        self._wind_speed = value
        # PROTECTED REGION END #    //  DishMaster.WindSpeed_write

    def read_desiredPointing(self):
        # PROTECTED REGION ID(DishMaster.desiredPointing_read) ENABLED START #
        """ This is a getter method for the desiredPointing attribute """
        return self._desired_pointing
        # PROTECTED REGION END #    //  DishMaster.desiredPointing_read

    def write_desiredPointing(self, value):
        # PROTECTED REGION ID(DishMaster.desiredPointing_write) ENABLED START #
        """
        This is a setter method for the desiredPointing attribute
        :param value: desiredPointing
        :return:
        """
        self._desired_pointing = value
        # PROTECTED REGION END #    //  DishMaster.desiredPointing_write

    def read_achievedPointing(self):
        # PROTECTED REGION ID(DishMaster.achievedPointing_read) ENABLED START #
        """ This is a getter method for the achievedPointing attribute """
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
        This method triggers the Dish to transition to the STOW Dish Element Mode,
        and returns to the caller. To point the dish in a direction that minimises the wind
        loads on the structure,for survival in strong wind conditions.
        The Dish is able to observe in the stove position, for the purpose of transient detection
        """
        try:
            # Command to set Dish to STOW Mode
            self._desired_pointing = [0, 0, 0]
            self.Slew("0")
            time.sleep(1)
            self.stow_thread = threading.Thread(None, self.checkSlew, 'DishMaster')
            self.stow_thread.start()

        except Exception as except_occured:
            print CONST.ERR_EXE_SET_STOW_MODE_CMD, self.ReceptorNumber
            self.devlogmsg(CONST.ERR_EXE_SET_STOW_MODE_CMD, 2)
            print CONST.STR_ERR_MSG, except_occured

        # while True:
        #     print"in while loop"
        #     if (self._pointing_state != 1):
        #         print "in if loop"
        #         self._admin_mode = 1                        # Set adminMode to OFFLINE
        #         self.set_state(tango.DevState.DISABLE)    # Set STATE to DISABLE
        #         self._dish_mode = 6                         # set dishMode to STOW
        #         self._health_state = 0                      # Set healthState to OK
        #         self.set_status("Dish is stowed successfully.")
        #         break
        # PROTECTED REGION END #    //  DishMaster.SetStowMode

    def is_SetStowMode_allowed(self):
        # PROTECTED REGION ID(DishMaster.is_SetStowMode_allowed) ENABLED START #
        """ This method checks whether the STOW mode is allowed """
        return self.get_state() not in [DevState.ON, DevState.ALARM]
        # PROTECTED REGION END #    //  DishMaster.is_SetStowMode_allowed

    @command(
    )
    @DebugIt()
    def SetStandbyLPMode(self):
        # PROTECTED REGION ID(DishMaster.SetStandbyLPMode) ENABLED START #
        """
        This command triggers the Dish to transition to the STANDBY-LP Dish Element Mode,
        and returns to the caller. Standby_LP is the default mode when the Dish is to configured
        for low power consumption, and is the mode wherein Dish ends after a start up procedure.
        """
        try:
            # Command to set Dish to STANDBY-LP Mode
            self.set_state(tango.DevState.STANDBY)     # Set STATE to STANDBY
            self._dish_mode = 3                          # set dishMode to STANDBYLP
            self.set_status(CONST.STR_DISH_STANDBYLP_MODE)
            self.devlogmsg(CONST.STR_DISH_STANDBYLP_MODE, 4)

        except Exception as except_occured:
            print CONST.ERR_EXE_SET_STNBYLP_MODE_CMD, self.ReceptorNumber
            self.devlogmsg(CONST.ERR_EXE_SET_STNBYLP_MODE_CMD, 2)
            print CONST.STR_ERR_MSG, except_occured
        # PROTECTED REGION END #    //  DishMaster.SetStandbyLPMode

    @command(
    )
    @DebugIt()
    def SetMaintenanceMode(self):
        # PROTECTED REGION ID(DishMaster.SetMaintenanceMode) ENABLED START #
        """
        This command triggers the Dish to transition to the MAINTENANCE Dish Element Mode,
        and returns to the caller. This mode will also enable engineers and maintainers
        to upgrade SW and FW. Dish also enters this mode when an emergency stop button is pressed.
        """
        try:
            # Command to set Dish to MAINTENANCE Mode
            self._admin_mode = 2                        # Set adminMode to MAINTENANCE
            self.set_state(tango.DevState.DISABLE)    # Set STATE to DISABLE
            self._dish_mode = 5                         # set dishMode to MAINTENANCE
            self.set_status(CONST.STR_DISH_MAINT_MODE)
            self.devlogmsg(CONST.STR_DISH_MAINT_MODE, 4)

        except Exception as except_occured:
            print CONST.ERR_EXE_SET_MAINT_MODE_CMD, self.ReceptorNumber
            self.devlogmsg(CONST.ERR_EXE_SET_MAINT_MODE_CMD, 2)
            print CONST.STR_ERR_MSG, except_occured

        # PROTECTED REGION END #    //  DishMaster.SetMaintenanceMode

    def is_SetMaintenanceMode_allowed(self):
        # PROTECTED REGION ID(DishMaster.is_SetMaintenanceMode_allowed) ENABLED START #
        """ This method checks whether MAINTENANCE mode is allowed """
        return self.get_state() not in [DevState.ON, DevState.ALARM, DevState.DISABLE]
        # PROTECTED REGION END #    //  DishMaster.is_SetMaintenanceMode_allowed

    @command(
    )
    @DebugIt()
    def SetOperateMode(self):
        """
        This commands triggers the Dish to transition to the OPERATE Dish Element Mode,
        and returns to the caller. This mode fulfills the main purpose of the Dish, which is to point
        designated directions while capturing data and transmitting it to CSP.
        :return:
        """
        # PROTECTED REGION ID(DishMaster.SetOperateMode) ENABLED START #
        try:
            # Command to set Dish to OPERATE Mode
            self._admin_mode = 0                        # Set adminMode to ONLINE
            self.set_state(tango.DevState.ON)         # Set STATE to ON
            self._dish_mode = 8                         # set dishMode to OPERATE
            self.set_status(CONST.STR_DISH_OPERATE_MODE)
            self.devlogmsg(CONST.STR_DISH_OPERATE_MODE, 4)
        except Exception as except_occured:
            print CONST.ERR_EXE_SET_OPERATE_MODE_CMD, self.ReceptorNumber
            self.devlogmsg(CONST.ERR_EXE_SET_OPERATE_MODE_CMD, 2)
            print CONST.STR_ERR_MSG, except_occured

        # PROTECTED REGION END #    //  DishMaster.SetOperateMode

    def is_SetOperateMode_allowed(self):
        # PROTECTED REGION ID(DishMaster.is_SetOperateMode_allowed) ENABLED START #
        """ This method checks whether OPERATE mode is allowed """
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
        The Dish is tracking the commended pointing positions within the specified
        SCAN pointing accuracy.
        :param argin:
        :return:
        """
        try:
            # Command to start SCAN
            if self._pointing_state == 0:
                self._current_time = time.time()
                self._scan_execution_time = float(argin)
                self._scan_delta_t = self._scan_execution_time - self._current_time
                time1 = Timer(self._scan_delta_t, self.StartCapture, [argin])
                time1.start()
                self.devlogmsg(CONST.STR_SCAN_INPROG, 4)
            else:
                self.set_status(CONST.STR_DISH_NOT_READY)
                self.devlogmsg(CONST.STR_DISH_NOT_READY, 4)
        except Exception as except_occured:
            print CONST.ERR_EXE_SCAN_CMD, self.ReceptorNumber
            self.devlogmsg(CONST.ERR_EXE_SCAN_CMD, 2)
            print CONST.STR_ERR_MSG, except_occured

        # PROTECTED REGION END #    //  DishMaster.Scan

    def is_Scan_allowed(self):
        # PROTECTED REGION ID(DishMaster.is_Scan_allowed) ENABLED START #
        """ This methods checks whether Scan is allowed """
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
        Start capture on the configured band. Command only valid in SPFRx Data_Capture mode.
        :param argin:
        :return:
        """
        try:
            # Command to start Data Capturing
            self._capturing = True                      # set Capturing to True
            self._pointing_state = 3                    # set pointingState to SCAN
            self.set_status(CONST.STR_DATA_CAPTURE_STRT)
            self.devlogmsg(CONST.STR_DATA_CAPTURE_STRT, 4)
        except Exception as except_occured:
            print CONST.ERR_EXE_STRT_CAPTURE_CMD, self.ReceptorNumber
            self.devlogmsg(CONST.ERR_EXE_STRT_CAPTURE_CMD, 2)
            print CONST.STR_ERR_MSG, except_occured

        # PROTECTED REGION END #    //  DishMaster.StartCapture

    def is_StartCapture_allowed(self):
        """
        :return:
        """
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
        Stops capture on the configured band
        :param argin:
        :return:
        """
        try:
            # Command to stop Data Capturing
            self._capturing = False                     # set Capturing to FALSE
            self._pointing_state = 0                    # set pointingState to READY
            self.set_status(CONST.STR_DATA_CAPTURE_STOP)
            self.devlogmsg(CONST.STR_DATA_CAPTURE_STOP, 4)
        except Exception as except_occured:
            print CONST.ERR_EXE_STOP_CAPTURE_CMD, self.ReceptorNumber
            self.devlogmsg(CONST.ERR_EXE_STOP_CAPTURE_CMD, 2)
            print CONST.STR_ERR_MSG, except_occured

        # PROTECTED REGION END #    //  DishMaster.StopCapture

    def is_StopCapture_allowed(self):
        # PROTECTED REGION ID(DishMaster.is_StopCapture_allowed) ENABLED START #
        """ This methods checks whether stop capture is allowed """
        return self.get_state() not in [DevState.OFF, DevState.FAULT, DevState.INIT,
                                        DevState.UNKNOWN, DevState.STANDBY, DevState.DISABLE]
        # PROTECTED REGION END #    //  DishMaster.is_StopCapture_allowed

    @command(
    )
    @DebugIt()
    def SetStandbyFPMode(self):
        # PROTECTED REGION ID(DishMaster.SetStandbyFPMode) ENABLED START #
        """
        This command triggers the Dish to transition to the STANDBY-FP Dish Element Mode,
        and returns to the caller. To prepare all subsystems for active observation, once a command
        is received by TM to go to the FULL_POWER mode.
        :return:
        """
        try:
            # Command to set Dish to STANDBY-FP Mode
            self.set_state(tango.DevState.STANDBY)    # set STATE to STANDBY
            self._dish_mode = 4                         # set dishMode to STANDBY-FP
            self.set_status(CONST.STR_DISH_STANDBYFP_MODE)
            self.devlogmsg(CONST.STR_DISH_STANDBYFP_MODE, 4)
        except Exception as except_occured:
            print CONST.ERR_EXE_SET_STNBYFP_MODE_CMD, self.ReceptorNumber
            self.devlogmsg(CONST.ERR_EXE_SET_STNBYFP_MODE_CMD, 2)
            print CONST.STR_ERR_MSG, except_occured

        # PROTECTED REGION END #    //  DishMaster.SetStandbyFPMode

    def is_SetStandbyFPMode_allowed(self):
        # PROTECTED REGION ID(DishMaster.is_SetStandbyFPMode_allowed) ENABLED START #
        """ This methods checks whether the STANDBY-FP mode is allowed """
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
        The Dish moves to the commanded pointing angle at the maximum speed,
        as defined by specified slew rate. No pointing accuracy requirements are applicable
        in this state. SLEW state will also be reported while the Dish is setting onto a target
        and is still not within the specified pointing accuracy.
        As soon as the pointing accuracy is within specifications, the state changes to TRACK.
        :param argin: timestamp
        :return:
        """
        try:
            # Execute POINT command at given timestamp
            self._current_time = time.time()
            self._point_execution_time = self._desired_pointing[0]
            self._point_delta_t = self._point_execution_time - self._current_time
            time1 = Timer(self._point_delta_t, self.point)
            time1.start()
            self.devlogmsg(CONST.STR_DISH_SLEW, 4)
        except Exception as except_occured:
            print CONST.ERR_EXE_SLEW_CMD, self.ReceptorNumber
            self.devlogmsg(CONST.ERR_EXE_SLEW_CMD, 2)
            print CONST.STR_ERR_MSG, except_occured

        # PROTECTED REGION END #    //  DishMaster.Slew

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(DishMaster.main) ENABLED START #
    """ This methods runs the Dish Master module"""
    return run((DishMaster,), args=args, **kwargs)
    # PROTECTED REGION END #    //  DishMaster.main

if __name__ == '__main__':
    main()
