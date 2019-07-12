#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of the SdpMaster project
#
#
#
# Distributed under the terms of the BSD-3-Clause license.
# See LICENSE.txt for more info.
"""Contain the tests for the SdpMaster."""

# Path
import sys
import os

file_path = os.path.dirname(os.path.abspath(__file__))
module_path = os.path.abspath(os.path.join(file_path, os.pardir)) + "/SdpMaster"
sys.path.insert(0, module_path)

path = os.path.join(os.path.dirname(__file__), os.pardir)
sys.path.insert(0, os.path.abspath(path))

# Imports
from time import sleep
from mock import MagicMock
import tango
from tango import DevState, DevFailed, EventType, DeviceProxy
#from devicetest import DeviceTestCase, main
from SdpMaster.SdpMaster import SdpMaster
import pytest




# Note:
#
# Since the device uses an inner thread, it is necessary to
# wait during the tests in order the let the device update itself.
# Hence, the sleep calls have to be secured enough not to produce
# any inconsistent behavior. However, the unit tests need to run fast.
# Here, we use a factor 3 between the read period and the sleep calls.
#
# Look at devicetest examples for more advanced testing

# Device test case
@pytest.mark.usefixtures("tango_context", "initialize_device")

class TestSdpMaster(object):
    """Test case for packet generation."""
    # PROTECTED REGION ID(SdpMaster.test_additionnal_import) ENABLED START #
    # PROTECTED REGION END #    //  SdpMaster.test_additionnal_import
    device = SdpMaster
    properties = {'SkaLevel': '4', 'CentralLoggingTarget': '', 'ElementLoggingTarget': '',
                  'StorageLoggingTarget': 'localhost', 'GroupDefinitions': '', 'NrSubarrays': '16',
                  'CapabilityTypes': '', 'MaxCapabilities': '',
                  }
    empty = None  # Should be []

    @classmethod
    def mocking(cls):
        """Mock external libraries."""
        # Example : Mock numpy
        # cls.numpy = SdpMaster.numpy = MagicMock()
        # PROTECTED REGION ID(SdpMaster.test_mocking) ENABLED START #
        # PROTECTED REGION END #    //  SdpMaster.test_mocking

    def test_properties(self):
        # test the properties
        # PROTECTED REGION ID(SdpMaster.test_properties) ENABLED START #
        # PROTECTED REGION END #    //  SdpMaster.test_properties
        pass

    # def test_State(self):
    #     """Test for State"""
    #     # PROTECTED REGION ID(SdpMaster.test_State) ENABLED START #
    #     self.device.State()
    #     # PROTECTED REGION END #    //  SdpMaster.test_State
    #
    # def test_Status(self):
    #     """Test for Status"""
    #     # PROTECTED REGION ID(SdpMaster.test_Status) ENABLED START #
    #     self.device.Status()
    #     # PROTECTED REGION END #    //  SdpMaster.test_Status
    #
    # def test_GetVersionInfo(self):
    #     """Test for GetVersionInfo"""
    #     # PROTECTED REGION ID(SdpMaster.test_GetVersionInfo) ENABLED START #
    #     self.device.GetVersionInfo()
    #     # PROTECTED REGION END #    //  SdpMaster.test_GetVersionInfo
    #
    # def test_isCapabilityAchievable(self):
    #     """Test for isCapabilityAchievable"""
    #     # PROTECTED REGION ID(SdpMaster.test_isCapabilityAchievable) ENABLED START #
    #     self.device.isCapabilityAchievable([[0], [""]])
    #     # PROTECTED REGION END #    //  SdpMaster.test_isCapabilityAchievable
    #
    # def test_Reset(self):
    #     """Test for Reset"""
    #     # PROTECTED REGION ID(SdpMaster.test_Reset) ENABLED START #
    #     self.device.Reset()
    #     # PROTECTED REGION END #    //  SdpMaster.test_Reset
    #
    # def test_On(self):
    #     """Test for On"""
    #     # PROTECTED REGION ID(SdpMaster.test_On) ENABLED START #
    #     self.device.On()
    #     # PROTECTED REGION END #    //  SdpMaster.test_On
    #
    # def test_Off(self):
    #     """Test for Off"""
    #     # PROTECTED REGION ID(SdpMaster.test_Off) ENABLED START #
    #     self.device.Off()
    #     # PROTECTED REGION END #    //  SdpMaster.test_Off
    #
    # def test_StandBy(self):
    #     """Test for StandBy"""
    #     # PROTECTED REGION ID(SdpMaster.test_StandBy) ENABLED START #
    #     self.device.StandBy()
    #     # PROTECTED REGION END #    //  SdpMaster.test_StandBy
    #
    # def test_Disable(self):
    #     """Test for Disable"""
    #     # PROTECTED REGION ID(SdpMaster.test_Disable) ENABLED START #
    #     self.device.Disable()
    #     # PROTECTED REGION END #    //  SdpMaster.test_Disable
    #
    # def test_elementLoggerAddress(self):
    #     """Test for elementLoggerAddress"""
    #     # PROTECTED REGION ID(SdpMaster.test_elementLoggerAddress) ENABLED START #
    #     self.device.elementLoggerAddress
    #     # PROTECTED REGION END #    //  SdpMaster.test_elementLoggerAddress
    #
    # def test_elementAlarmAddress(self):
    #     """Test for elementAlarmAddress"""
    #     # PROTECTED REGION ID(SdpMaster.test_elementAlarmAddress) ENABLED START #
    #     self.device.elementAlarmAddress
    #     # PROTECTED REGION END #    //  SdpMaster.test_elementAlarmAddress
    #
    # def test_elementTelStateAddress(self):
    #     """Test for elementTelStateAddress"""
    #     # PROTECTED REGION ID(SdpMaster.test_elementTelStateAddress) ENABLED START #
    #     self.device.elementTelStateAddress
    #     # PROTECTED REGION END #    //  SdpMaster.test_elementTelStateAddress
    #
    # def test_elementDatabaseAddress(self):
    #     """Test for elementDatabaseAddress"""
    #     # PROTECTED REGION ID(SdpMaster.test_elementDatabaseAddress) ENABLED START #
    #     self.device.elementDatabaseAddress
    #     # PROTECTED REGION END #    //  SdpMaster.test_elementDatabaseAddress
    #
    # def test_buildState(self):
    #     """Test for buildState"""
    #     # PROTECTED REGION ID(SdpMaster.test_buildState) ENABLED START #
    #     self.device.buildState
    #     # PROTECTED REGION END #    //  SdpMaster.test_buildState
    #
    # def test_versionId(self):
    #     """Test for versionId"""
    #     # PROTECTED REGION ID(SdpMaster.test_versionId) ENABLED START #
    #     self.device.versionId
    #     # PROTECTED REGION END #    //  SdpMaster.test_versionId
    #
    # def test_centralLoggingLevel(self):
    #     """Test for centralLoggingLevel"""
    #     # PROTECTED REGION ID(SdpMaster.test_centralLoggingLevel) ENABLED START #
    #     self.device.centralLoggingLevel
    #     # PROTECTED REGION END #    //  SdpMaster.test_centralLoggingLevel
    #
    # def test_elementLoggingLevel(self):
    #     """Test for elementLoggingLevel"""
    #     # PROTECTED REGION ID(SdpMaster.test_elementLoggingLevel) ENABLED START #
    #     self.device.elementLoggingLevel
    #     # PROTECTED REGION END #    //  SdpMaster.test_elementLoggingLevel
    #
    # def test_storageLoggingLevel(self):
    #     """Test for storageLoggingLevel"""
    #     # PROTECTED REGION ID(SdpMaster.test_storageLoggingLevel) ENABLED START #
    #     self.device.storageLoggingLevel
    #     # PROTECTED REGION END #    //  SdpMaster.test_storageLoggingLevel
    #
    # def test_healthState(self):
    #     """Test for healthState"""
    #     # PROTECTED REGION ID(SdpMaster.test_healthState) ENABLED START #
    #     self.device.healthState
    #     # PROTECTED REGION END #    //  SdpMaster.test_healthState
    #
    # def test_adminMode(self):
    #     """Test for adminMode"""
    #     # PROTECTED REGION ID(SdpMaster.test_adminMode) ENABLED START #
    #     self.device.adminMode
    #     # PROTECTED REGION END #    //  SdpMaster.test_adminMode
    #
    # def test_controlMode(self):
    #     """Test for controlMode"""
    #     # PROTECTED REGION ID(SdpMaster.test_controlMode) ENABLED START #
    #     self.device.controlMode
    #     # PROTECTED REGION END #    //  SdpMaster.test_controlMode
    #
    # def test_simulationMode(self):
    #     """Test for simulationMode"""
    #     # PROTECTED REGION ID(SdpMaster.test_simulationMode) ENABLED START #
    #     self.device.simulationMode
    #     # PROTECTED REGION END #    //  SdpMaster.test_simulationMode
    #
    # def test_testMode(self):
    #     """Test for testMode"""
    #     # PROTECTED REGION ID(SdpMaster.test_testMode) ENABLED START #
    #     self.device.testMode
    #     # PROTECTED REGION END #    //  SdpMaster.test_testMode
    #
    # def test_ProcessingBlockList(self):
    #     """Test for ProcessingBlockList"""
    #     # PROTECTED REGION ID(SdpMaster.test_ProcessingBlockList) ENABLED START #
    #     self.device.ProcessingBlockList
    #     # PROTECTED REGION END #    //  SdpMaster.test_ProcessingBlockList
    #
    # def test_OperatingState(self):
    #     """Test for OperatingState"""
    #     # PROTECTED REGION ID(SdpMaster.test_OperatingState) ENABLED START #
    #     self.device.OperatingState
    #     # PROTECTED REGION END #    //  SdpMaster.test_OperatingState
    #
    # def test_maxCapabilities(self):
    #     """Test for maxCapabilities"""
    #     # PROTECTED REGION ID(SdpMaster.test_maxCapabilities) ENABLED START #
    #     self.device.maxCapabilities
    #     # PROTECTED REGION END #    //  SdpMaster.test_maxCapabilities
    #
    # def test_availableCapabilities(self):
    #     """Test for availableCapabilities"""
    #     # PROTECTED REGION ID(SdpMaster.test_availableCapabilities) ENABLED START #
    #     self.device.availableCapabilities
    #     # PROTECTED REGION END #    //  SdpMaster.test_availableCapabilities
    #
