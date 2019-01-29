#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of the DishMaster project
#
#
#
# Distributed under the terms of the BSD-3-Clause license.
# See LICENSE.txt for more info.
"""Contain the tests for the DishMaster Simulator."""

# Path
from builtins import range
from builtins import object
import sys
import os
file_path = os.path.dirname(os.path.abspath(__file__))
module_path = os.path.abspath(os.path.join(file_path, os.pardir)) + "/DishMaster"
sys.path.insert(0, module_path)

# path = os.path.join(os.path.dirname(__file__), os.pardir)
# sys.path.insert(0, os.path.abspath(path))
# sys.path.append("/home/user/Integration_P3/tmc-prototype/tmc-prototype/DishMaster/DishMaster/")

# Imports
from mock import MagicMock
import tango
from tango import DevFailed, DevState
import pytest
import DishMaster.DishMaster
import CONST
import time

# Note:
#
# Since the device uses an inner thread, it is necessary to
# wait during the tests in order the let the device update itself.
# Hence, the sleep calls have to be secured enough not to produce
# any inconsistent behavior. However, the unittests need to run fast.
# Here, we use a factor 3 between the read period and the sleep calls.
#
# Look at devicetest examples for more advanced testing

# Device test case
@pytest.mark.usefixtures("tango_context", "initialize_device")

class TestDishMaster(object):
    """Test case for packet generation."""
    # PROTECTED REGION ID(DishMaster.test_additionnal_import) ENABLED START #
    # PROTECTED REGION END #    //  DishMaster.test_additionnal_import
    device = DishMaster
    properties = {'SkaLevel': '4', 'CentralLoggingTarget': '', 'ElementLoggingTarget': '',
                  'StorageLoggingTarget': 'localhost', 'MetricList': 'healthState', 'GroupDefinitions': '',
                  'NrSubarrays': '16', 'CapabilityTypes': '', 'MaxCapabilities': '', 'ReceptorNumber': '',
                  }
    empty = None  # Should be []

    @classmethod
    def mocking(cls):
        """Mock external libraries."""
        # Example : Mock numpy
        # cls.numpy = DishMaster.numpy = MagicMock()
        # PROTECTED REGION ID(DishMaster.test_mocking) ENABLED START #
        # PROTECTED REGION END #    //  DishMaster.test_mocking

    def test_properties(self, tango_context):
        """Test for Properties"""
        # PROTECTED REGION ID(DishMaster.test_properties) ENABLED START #
        # PROTECTED REGION END #    //  DishMaster.test_properties
        pass

    def test_State(self, tango_context):
        """Test for State"""
        # PROTECTED REGION ID(DishMaster.test_State) ENABLED START #
        assert tango_context.device.State() == DevState.STANDBY
        # PROTECTED REGION END #    //  DishMaster.test_State

    def test_Status(self, tango_context):
        """Test for Status"""
        # PROTECTED REGION ID(DishMaster.test_Status) ENABLED START #
        assert tango_context.device.Status() == CONST.STR_DISH_INIT_SUCCESS
        # PROTECTED REGION END #    //  DishMaster.test_Status

    def test_GetMetrics(self, tango_context):
        """Test for GetMetrics"""
        # PROTECTED REGION ID(DishMaster.test_GetMetrics) ENABLED START #
        # PROTECTED REGION END #    //  DishMaster.test_GetMetrics

    def test_ToJson(self, tango_context):
        """Test for ToJson"""
        # PROTECTED REGION ID(DishMaster.test_ToJson) ENABLED START #
        # PROTECTED REGION END #    //  DishMaster.test_ToJson

    def test_GetVersionInfo(self, tango_context):
        """Test for GetVersionInfo"""
        # PROTECTED REGION ID(DishMaster.test_GetVersionInfo) ENABLED START #
        # PROTECTED REGION END #    //  DishMaster.test_GetVersionInfo

    def test_isCapabilityAchievable(self, tango_context):
        """Test for isCapabilityAchievable"""
        # PROTECTED REGION ID(DishMaster.test_isCapabilityAchievable) ENABLED START #
        # PROTECTED REGION END #    //  DishMaster.test_isCapabilityAchievable

    def test_Reset(self, tango_context):
        """Test for Reset"""
        # PROTECTED REGION ID(DishMaster.test_Reset) ENABLED START #
        assert tango_context.device.Reset() == None
        # PROTECTED REGION END #    //  DishMaster.test_Reset

    def test_SetStowMode(self, tango_context):
        """Test for SetStowMode"""
        # PROTECTED REGION ID(DishMaster.test_SetStowMode) ENABLED START #
        tango_context.device.SetStowMode()
        assert tango_context.device.adminMode == 1
        assert tango_context.device.dishMode == 6
        assert tango_context.device.State() == DevState.DISABLE
        # PROTECTED REGION END #    //  DishMaster.test_SetStowMode

    def test_SetStandbyLPMode(self, tango_context):
        """Test for SetStandbyLPMode"""
        # PROTECTED REGION ID(DishMaster.test_SetStandbyLPMode) ENABLED START #
        tango_context.device.SetStandbyLPMode()
        assert tango_context.device.dishMode == 3
        assert tango_context.device.State() == DevState.STANDBY
        # PROTECTED REGION END #    //  DishMaster.test_SetStandbyLPMode

    def test_SetMaintenanceMode(self, tango_context):
        """Test for SetMaintenanceMode"""
        # PROTECTED REGION ID(DishMaster.test_SetMaintenanceMode) ENABLED START #
        tango_context.device.SetMaintenanceMode()
        assert tango_context.device.adminMode == 2
        assert tango_context.device.dishMode == 5
        assert tango_context.device.State() == DevState.DISABLE
        # PROTECTED REGION END #    //  DishMaster.test_SetMaintenanceMode

    def test_SetOperateMode(self, tango_context):
        """Test for SetOperateMode"""
        # PROTECTED REGION ID(DishMaster.test_SetOperateMode) ENABLED START #
        tango_context.device.SetStandbyLPMode()
        tango_context.device.SetOperateMode()
        assert tango_context.device.adminMode == 0
        assert tango_context.device.dishMode == 8
        assert tango_context.device.State() == DevState.ON
        # PROTECTED REGION END #    //  DishMaster.test_SetOperateMode

    def test_Scan(self, tango_context):
        """Test for Scan"""
        # PROTECTED REGION ID(DishMaster.test_Scan) ENABLED START #
        # Testing for invalid argument
        tango_context.device.Scan("a")
        assert tango_context.device.pointingState != 3
        assert tango_context.device.capturing != True
        # Testing for valid argument
        tango_context.device.Scan("0")
        assert tango_context.device.pointingState == 3
        assert tango_context.device.capturing == True
        # Testing if the Scan is already in progress
        tango_context.device.Scan("0")
        assert tango_context.device.Status() == CONST.STR_DISH_NOT_READY
        # PROTECTED REGION END #    //  DishMaster.test_Scan

    def test_StopCapture(self, tango_context):
        """Test for StopCapture"""
        # PROTECTED REGION ID(DishMaster.test_StopCapture) ENABLED START #
        # Testing for invalid argument
        tango_context.device.StopCapture("a")
        assert tango_context.device.capturing != False
        assert tango_context.device.pointingState != 0
        # Testing for valid argument
        tango_context.device.StopCapture("0")
        assert tango_context.device.capturing == False
        assert tango_context.device.pointingState == 0
        # Testing if data capturing is already stopped
        tango_context.device.StopCapture("0")
        assert tango_context.device.Status() == CONST.STR_DATA_CAPTURE_ALREADY_STOPPED
        # PROTECTED REGION END #    //  DishMaster.test_StopCapture

    def test_StartCapture(self, tango_context):
        """Test for StartCapture"""
        # PROTECTED REGION ID(DishMaster.test_StartCapture) ENABLED START #
        # Testing for invalid argument
        tango_context.device.StartCapture("a")
        assert tango_context.device.pointingState != 3
        assert tango_context.device.capturing != True
        # Testing for valid argument
        tango_context.device.StartCapture("0")
        assert tango_context.device.pointingState == 3
        assert tango_context.device.capturing == True
        # Testing if data capturing is already started
        tango_context.device.StartCapture("0")
        assert tango_context.device.Status() == CONST.STR_DATA_CAPTURE_ALREADY_STARTED
        # PROTECTED REGION END #    //  DishMaster.test_StartCapture

    def test_Slew(self, tango_context):
        """Test for Slew"""
        # PROTECTED REGION ID(DishMaster.test_Slew) ENABLED START #
        tango_context.device.StopCapture("0")
        tango_context.device.desiredPointing = [0, 1, 1]
        # Testing for invalid argument
        tango_context.device.Slew("a")
        time.sleep(8)
        result = []
        for i in range(1, len(tango_context.device.achievedPointing)):
            if (tango_context.device.achievedPointing[i] != 1):
                result.append(True)
            else:
                result.append(False)
        assert all(result)
        # Testing for valid argument
        tango_context.device.Slew("0")
        time.sleep(8)
        result = []
        for i in range(1,len(tango_context.device.achievedPointing)):
            if (tango_context.device.achievedPointing[i] == 1):
                result.append(True)
            else:
                result.append(False)
        assert all(result)
        # PROTECTED REGION END #    //  DishMaster.test_Slew

    def test_SetStandbyFPMode(self, tango_context):
        """Test for SetStandbyFPMode"""
        # PROTECTED REGION ID(DishMaster.test_SetStandbyFPMode) ENABLED START #
        tango_context.device.SetStandbyLPMode()
        tango_context.device.SetStandbyFPMode()
        assert tango_context.device.dishMode == 4
        assert tango_context.device.State() == DevState.STANDBY
        # PROTECTED REGION END #    //  DishMaster.test_SetStandbyFPMode

    def test_elementLoggerAddress(self, tango_context):
        """Test for elementLoggerAddress"""
        # PROTECTED REGION ID(DishMaster.test_elementLoggerAddress) ENABLED START #
        assert tango_context.device.elementLoggerAddress == ""
        # PROTECTED REGION END #    //  DishMaster.test_elementLoggerAddress

    def test_elementAlarmAddress(self, tango_context):
        """Test for elementAlarmAddress"""
        # PROTECTED REGION ID(DishMaster.test_elementAlarmAddress) ENABLED START #
        assert tango_context.device.elementAlarmAddress == ""
        # PROTECTED REGION END #    //  DishMaster.test_elementAlarmAddress

    def test_elementTelStateAddress(self, tango_context):
        """Test for elementTelStateAddress"""
        # PROTECTED REGION ID(DishMaster.test_elementTelStateAddress) ENABLED START #
        assert tango_context.device.elementTelStateAddress == ""
        # PROTECTED REGION END #    //  DishMaster.test_elementTelStateAddress

    def test_elementDatabaseAddress(self, tango_context):
        """Test for elementDatabaseAddress"""
        # PROTECTED REGION ID(DishMaster.test_elementDatabaseAddress) ENABLED START #
        assert tango_context.device.elementDatabaseAddress == ""
        # PROTECTED REGION END #    //  DishMaster.test_elementDatabaseAddress

    def test_buildState(self, tango_context):
        """Test for buildState"""
        # PROTECTED REGION ID(DishMaster.test_buildState) ENABLED START #
        assert tango_context.device.buildState == (
            "tangods-skabasedevice, 1.0.0, A generic base device for SKA.")
        # PROTECTED REGION END #    //  DishMaster.test_buildState

    def test_versionId(self, tango_context):
        """Test for versionId"""
        # PROTECTED REGION ID(DishMaster.test_versionId) ENABLED START #
        assert tango_context.device.versionId == "1.0.0"
        # PROTECTED REGION END #    //  DishMaster.test_versionId

    def test_centralLoggingLevel(self, tango_context):
        """Test for centralLoggingLevel"""
        # PROTECTED REGION ID(DishMaster.test_centralLoggingLevel) ENABLED START #
        tango_context.device.centralLoggingLevel = int(tango.LogLevel.LOG_DEBUG)
        assert tango_context.device.centralLoggingLevel == int(tango.LogLevel.LOG_DEBUG)
        # PROTECTED REGION END #    //  DishMaster.test_centralLoggingLevel

    def test_elementLoggingLevel(self, tango_context):
        """Test for elementLoggingLevel"""
        # PROTECTED REGION ID(DishMaster.test_elementLoggingLevel) ENABLED START #
        tango_context.device.elementLoggingLevel = int(tango.LogLevel.LOG_DEBUG)
        assert tango_context.device.elementLoggingLevel == int(tango.LogLevel.LOG_DEBUG)
        # PROTECTED REGION END #    //  DishMaster.test_elementLoggingLevel

    def test_storageLoggingLevel(self, tango_context):
        """Test for storageLoggingLevel"""
        # PROTECTED REGION ID(DishMaster.test_storageLoggingLevel) ENABLED START #
        tango_context.device.storageLoggingLevel = int(tango.LogLevel.LOG_DEBUG)
        assert tango_context.device.storageLoggingLevel == int(tango.LogLevel.LOG_DEBUG)
        # PROTECTED REGION END #    //  DishMaster.test_storageLoggingLevel

    def test_healthState(self, tango_context):
        """Test for healthState"""
        # PROTECTED REGION ID(DishMaster.test_healthState) ENABLED START #
        assert tango_context.device.healthState == 0
        # PROTECTED REGION END #    //  DishMaster.test_healthState

    def test_adminMode(self, tango_context):
        """Test for adminMode"""
        # PROTECTED REGION ID(DishMaster.test_adminMode) ENABLED START #
        assert tango_context.device.adminMode == 0
        # PROTECTED REGION END #    //  DishMaster.test_adminMode

    def test_controlMode(self, tango_context):
        """Test for controlMode"""
        # PROTECTED REGION ID(DishMaster.test_controlMode) ENABLED START #
        control_mode = 0
        tango_context.device.controlMode = control_mode
        assert tango_context.device.controlMode == control_mode
        # PROTECTED REGION END #    //  DishMaster.test_controlMode

    def test_simulationMode(self, tango_context):
        """Test for simulationMode"""
        # PROTECTED REGION ID(DishMaster.test_simulationMode) ENABLED START #
        simulation_mode = 0
        tango_context.device.simulationMode = simulation_mode
        assert tango_context.device.simulationMode == simulation_mode
        # PROTECTED REGION END #    //  DishMaster.test_simulationMode

    def test_testMode(self, tango_context):
        """Test for testMode"""
        # PROTECTED REGION ID(DishMaster.test_testMode) ENABLED START #
        test_mode = CONST.STR_FALSE
        tango_context.device.testMode = test_mode
        assert tango_context.device.testMode == test_mode
        # PROTECTED REGION END #    //  DishMaster.test_testMode

    def test_dishMode(self, tango_context):
        """Test for dishMode"""
        # PROTECTED REGION ID(DishMaster.test_dishMode) ENABLED START #
        assert tango_context.device.dishMode == 4
        # PROTECTED REGION END #    //  DishMaster.test_dishMode

    def test_pointingState(self, tango_context):
        """Test for pointingState"""
        # PROTECTED REGION ID(DishMaster.test_pointingState) ENABLED START #
        assert tango_context.device.pointingState == 0
        # PROTECTED REGION END #    //  DishMaster.test_pointingState

    def test_band1SamplerFrequency(self, tango_context):
        """Test for band1SamplerFrequency"""
        # PROTECTED REGION ID(DishMaster.test_band1SamplerFrequency) ENABLED START #
        assert tango_context.device.band1SamplerFrequency == 0
        # PROTECTED REGION END #    //  DishMaster.test_band1SamplerFrequency

    def test_band2SamplerFrequency(self, tango_context):
        """Test for band2SamplerFrequency"""
        # PROTECTED REGION ID(DishMaster.test_band2SamplerFrequency) ENABLED START #
        assert tango_context.device.band2SamplerFrequency == 0
        # PROTECTED REGION END #    //  DishMaster.test_band2SamplerFrequency

    def test_band3SamplerFrequency(self, tango_context):
        """Test for band3SamplerFrequency"""
        # PROTECTED REGION ID(DishMaster.test_band3SamplerFrequency) ENABLED START #
        assert tango_context.device.band3SamplerFrequency == 0
        # PROTECTED REGION END #    //  DishMaster.test_band3SamplerFrequency

    def test_band4SamplerFrequency(self, tango_context):
        """Test for band4SamplerFrequency"""
        # PROTECTED REGION ID(DishMaster.test_band4SamplerFrequency) ENABLED START #
        assert tango_context.device.band4SamplerFrequency == 0
        # PROTECTED REGION END #    //  DishMaster.test_band4SamplerFrequency

    def test_band5aSamplerFrequency(self, tango_context):
        """Test for band5aSamplerFrequency"""
        # PROTECTED REGION ID(DishMaster.test_band5aSamplerFrequency) ENABLED START #
        assert tango_context.device.band5aSamplerFrequency == 0
        # PROTECTED REGION END #    //  DishMaster.test_band5aSamplerFrequency

    def test_band5bSamplerFrequency(self, tango_context):
        """Test for band5bSamplerFrequency"""
        # PROTECTED REGION ID(DishMaster.test_band5bSamplerFrequency) ENABLED START #
        assert tango_context.device.band5bSamplerFrequency == 0
        # PROTECTED REGION END #    //  DishMaster.test_band5bSamplerFrequency

    def test_capturing(self, tango_context):
        """Test for capturing"""
        # PROTECTED REGION ID(DishMaster.test_capturing) ENABLED START #
        assert tango_context.device.capturing == False
        # PROTECTED REGION END #    //  DishMaster.test_capturing

    def test_ConfiguredBand(self, tango_context):
        """Test for ConfiguredBand"""
        # PROTECTED REGION ID(DishMaster.test_ConfiguredBand) ENABLED START #
        assert tango_context.device.configuredBand == 1
        # PROTECTED REGION END #    //  DishMaster.test_ConfiguredBand

    def test_WindSpeed(self, tango_context):
        """Test for WindSpeed"""
        # PROTECTED REGION ID(DishMaster.test_WindSpeed) ENABLED START #
        speed = 0
        tango_context.device.WindSpeed = speed
        assert tango_context.device.WindSpeed == speed
        # PROTECTED REGION END #    //  DishMaster.test_WindSpeed

    def test_maxCapabilities(self, tango_context):
        """Test for maxCapabilities"""
        # PROTECTED REGION ID(DishMaster.test_maxCapabilities) ENABLED START #
        assert tango_context.device.maxCapabilities == None
        # PROTECTED REGION END #    //  DishMaster.test_maxCapabilities

    def test_availableCapabilities(self, tango_context):
        """Test for availableCapabilities"""
        # PROTECTED REGION ID(DishMaster.test_availableCapabilities) ENABLED START #
        assert tango_context.device.availableCapabilities == None
        # PROTECTED REGION END #    //  DishMaster.test_availableCapabilities

    def test_desiredPointing(self, tango_context):
        """Test for desiredPointing"""
        # PROTECTED REGION ID(DishMaster.test_desiredPointing) ENABLED START #
        desired_pointing = [0,0,0]
        result = []
        tango_context.device.desiredPointing = [0,0,0]
        for i in range(0,len(desired_pointing)):
            if (tango_context.device.desiredPointing[i] == 0):
                result.append(True)
            else:
                result.append(False)
        assert all(result)
        # PROTECTED REGION END #    //  DishMaster.test_desiredPointing

    def test_achievedPointing(self, tango_context):
        """Test for achievedPointing"""
        # PROTECTED REGION ID(DishMaster.test_achievedPointing) ENABLED START #
        result = []
        for i in range(1,len(tango_context.device.achievedPointing)):
            if (tango_context.device.achievedPointing[i] == 1):
                result.append(True)
            else:
                result.append(False)
        assert all(result)
        # PROTECTED REGION END #    //  DishMaster.test_achievedPointing