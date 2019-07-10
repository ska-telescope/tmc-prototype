#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of the SdpSubarray project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.
"""Contain the tests for the SdpSubarray."""

# Path
import sys
import os
file_path = os.path.dirname(os.path.abspath(__file__))
module_path = os.path.abspath(os.path.join(file_path, os.pardir)) + "/SdpSubarray"
sys.path.insert(0, module_path)

path = os.path.join(os.path.dirname(__file__), os.pardir)
sys.path.insert(0, os.path.abspath(path))

# Imports
import tango
import pytest
from SdpSubarray.SdpSubarray import SdpSubarray

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

class TestSdpSubarray(object):
    """Test case for packet generation."""
    # PROTECTED REGION ID(SdpSubarray.test_additionnal_import) ENABLED START #
    # PROTECTED REGION END #    //  SdpSubarray.test_additionnal_import
    device = SdpSubarray
    properties = {'CapabilityTypes': '', 'CentralLoggingTarget': '', 'ElementLoggingTarget': '', 'GroupDefinitions': '', 'SkaLevel': '4', 'StorageLoggingTarget': 'localhost', 'SubID': '',
                  }
    empty = None  # Should be []

    @classmethod
    def mocking(cls):
        """Mock external libraries."""
        # Example : Mock numpy
        # cls.numpy = SdpSubarray.numpy = MagicMock()
        # PROTECTED REGION ID(SdpSubarray.test_mocking) ENABLED START #
        # PROTECTED REGION END #    //  SdpSubarray.test_mocking

    def test_properties(self):
        # test the properties
        # PROTECTED REGION ID(SdpSubarray.test_properties) ENABLED START #
        # PROTECTED REGION END #    //  SdpSubarray.test_properties
        pass

    # def test_Abort(self):
    #     """Test for Abort"""
    #     # PROTECTED REGION ID(SdpSubarray.test_Abort) ENABLED START #
    #     self.device.Abort()
    #     # PROTECTED REGION END #    //  SdpSubarray.test_Abort
    #
    # def test_ConfigureCapability(self):
    #     """Test for ConfigureCapability"""
    #     # PROTECTED REGION ID(SdpSubarray.test_ConfigureCapability) ENABLED START #
    #     self.device.ConfigureCapability([[0], [""]])
    #     # PROTECTED REGION END #    //  SdpSubarray.test_ConfigureCapability
    #
    # def test_DeconfigureAllCapabilities(self):
    #     """Test for DeconfigureAllCapabilities"""
    #     # PROTECTED REGION ID(SdpSubarray.test_DeconfigureAllCapabilities) ENABLED START #
    #     self.device.DeconfigureAllCapabilities("")
    #     # PROTECTED REGION END #    //  SdpSubarray.test_DeconfigureAllCapabilities
    #
    # def test_DeconfigureCapability(self):
    #     """Test for DeconfigureCapability"""
    #     # PROTECTED REGION ID(SdpSubarray.test_DeconfigureCapability) ENABLED START #
    #     self.device.DeconfigureCapability([[0], [""]])
    #     # PROTECTED REGION END #    //  SdpSubarray.test_DeconfigureCapability
    #
    # def test_GetVersionInfo(self):
    #     """Test for GetVersionInfo"""
    #     # PROTECTED REGION ID(SdpSubarray.test_GetVersionInfo) ENABLED START #
    #     self.device.GetVersionInfo()
    #     # PROTECTED REGION END #    //  SdpSubarray.test_GetVersionInfo
    #
    # def test_Status(self):
    #     """Test for Status"""
    #     # PROTECTED REGION ID(SdpSubarray.test_Status) ENABLED START #
    #     self.device.Status()
    #     # PROTECTED REGION END #    //  SdpSubarray.test_Status
    #
    # def test_State(self):
    #     """Test for State"""
    #     # PROTECTED REGION ID(SdpSubarray.test_State) ENABLED START #
    #     self.device.State()
    #     # PROTECTED REGION END #    //  SdpSubarray.test_State
    #
    # def test_AssignResources(self):
    #     """Test for AssignResources"""
    #     # PROTECTED REGION ID(SdpSubarray.test_AssignResources) ENABLED START #
    #     self.device.AssignResources([""])
    #     # PROTECTED REGION END #    //  SdpSubarray.test_AssignResources
    #
    # def test_EndSB(self):
    #     """Test for EndSB"""
    #     # PROTECTED REGION ID(SdpSubarray.test_EndSB) ENABLED START #
    #     self.device.EndSB()
    #     # PROTECTED REGION END #    //  SdpSubarray.test_EndSB
    #
    # def test_EndScan(self):
    #     """Test for EndScan"""
    #     # PROTECTED REGION ID(SdpSubarray.test_EndScan) ENABLED START #
    #     self.device.EndScan()
    #     # PROTECTED REGION END #    //  SdpSubarray.test_EndScan
    #
    # def test_ObsState(self):
    #     """Test for ObsState"""
    #     # PROTECTED REGION ID(SdpSubarray.test_ObsState) ENABLED START #
    #     self.device.ObsState()
    #     # PROTECTED REGION END #    //  SdpSubarray.test_ObsState
    #
    # def test_Pause(self):
    #     """Test for Pause"""
    #     # PROTECTED REGION ID(SdpSubarray.test_Pause) ENABLED START #
    #     self.device.Pause()
    #     # PROTECTED REGION END #    //  SdpSubarray.test_Pause
    #
    # def test_ReleaseAllResources(self):
    #     """Test for ReleaseAllResources"""
    #     # PROTECTED REGION ID(SdpSubarray.test_ReleaseAllResources) ENABLED START #
    #     self.device.ReleaseAllResources()
    #     # PROTECTED REGION END #    //  SdpSubarray.test_ReleaseAllResources
    #
    # def test_ReleaseResources(self):
    #     """Test for ReleaseResources"""
    #     # PROTECTED REGION ID(SdpSubarray.test_ReleaseResources) ENABLED START #
    #     self.device.ReleaseResources([""])
    #     # PROTECTED REGION END #    //  SdpSubarray.test_ReleaseResources
    #
    # def test_Reset(self):
    #     """Test for Reset"""
    #     # PROTECTED REGION ID(SdpSubarray.test_Reset) ENABLED START #
    #     self.device.Reset()
    #     # PROTECTED REGION END #    //  SdpSubarray.test_Reset
    #
    # def test_Resume(self):
    #     """Test for Resume"""
    #     # PROTECTED REGION ID(SdpSubarray.test_Resume) ENABLED START #
    #     self.device.Resume()
    #     # PROTECTED REGION END #    //  SdpSubarray.test_Resume
    #
    # def test_Scan(self):
    #     """Test for Scan"""
    #     # PROTECTED REGION ID(SdpSubarray.test_Scan) ENABLED START #
    #     self.device.Scan([""])
    #     # PROTECTED REGION END #    //  SdpSubarray.test_Scan
    #
    # def test_Configure(self):
    #     """Test for Configure"""
    #     # PROTECTED REGION ID(SdpSubarray.test_Configure) ENABLED START #
    #     self.device.Configure("")
    #     # PROTECTED REGION END #    //  SdpSubarray.test_Configure
    #
    # def test_activationTime(self):
    #     """Test for activationTime"""
    #     # PROTECTED REGION ID(SdpSubarray.test_activationTime) ENABLED START #
    #     self.device.activationTime
    #     # PROTECTED REGION END #    //  SdpSubarray.test_activationTime
    #
    # def test_adminMode(self):
    #     """Test for adminMode"""
    #     # PROTECTED REGION ID(SdpSubarray.test_adminMode) ENABLED START #
    #     self.device.adminMode
    #     # PROTECTED REGION END #    //  SdpSubarray.test_adminMode
    #
    # def test_buildState(self):
    #     """Test for buildState"""
    #     # PROTECTED REGION ID(SdpSubarray.test_buildState) ENABLED START #
    #     self.device.buildState
    #     # PROTECTED REGION END #    //  SdpSubarray.test_buildState
    #
    # def test_centralLoggingLevel(self):
    #     """Test for centralLoggingLevel"""
    #     # PROTECTED REGION ID(SdpSubarray.test_centralLoggingLevel) ENABLED START #
    #     self.device.centralLoggingLevel
    #     # PROTECTED REGION END #    //  SdpSubarray.test_centralLoggingLevel
    #
    # def test_configurationDelayExpected(self):
    #     """Test for configurationDelayExpected"""
    #     # PROTECTED REGION ID(SdpSubarray.test_configurationDelayExpected) ENABLED START #
    #     self.device.configurationDelayExpected
    #     # PROTECTED REGION END #    //  SdpSubarray.test_configurationDelayExpected
    #
    # def test_configurationProgress(self):
    #     """Test for configurationProgress"""
    #     # PROTECTED REGION ID(SdpSubarray.test_configurationProgress) ENABLED START #
    #     self.device.configurationProgress
    #     # PROTECTED REGION END #    //  SdpSubarray.test_configurationProgress
    #
    # def test_controlMode(self):
    #     """Test for controlMode"""
    #     # PROTECTED REGION ID(SdpSubarray.test_controlMode) ENABLED START #
    #     self.device.controlMode
    #     # PROTECTED REGION END #    //  SdpSubarray.test_controlMode
    #
    # def test_elementLoggingLevel(self):
    #     """Test for elementLoggingLevel"""
    #     # PROTECTED REGION ID(SdpSubarray.test_elementLoggingLevel) ENABLED START #
    #     self.device.elementLoggingLevel
    #     # PROTECTED REGION END #    //  SdpSubarray.test_elementLoggingLevel
    #
    # def test_healthState(self):
    #     """Test for healthState"""
    #     # PROTECTED REGION ID(SdpSubarray.test_healthState) ENABLED START #
    #     self.device.healthState
    #     # PROTECTED REGION END #    //  SdpSubarray.test_healthState
    #
    # def test_obsMode(self):
    #     """Test for obsMode"""
    #     # PROTECTED REGION ID(SdpSubarray.test_obsMode) ENABLED START #
    #     self.device.obsMode
    #     # PROTECTED REGION END #    //  SdpSubarray.test_obsMode
    #
    # def test_obsState(self):
    #     """Test for obsState"""
    #     # PROTECTED REGION ID(SdpSubarray.test_obsState) ENABLED START #
    #     self.device.obsState
    #     # PROTECTED REGION END #    //  SdpSubarray.test_obsState
    #
    # def test_simulationMode(self):
    #     """Test for simulationMode"""
    #     # PROTECTED REGION ID(SdpSubarray.test_simulationMode) ENABLED START #
    #     self.device.simulationMode
    #     # PROTECTED REGION END #    //  SdpSubarray.test_simulationMode
    #
    # def test_storageLoggingLevel(self):
    #     """Test for storageLoggingLevel"""
    #     # PROTECTED REGION ID(SdpSubarray.test_storageLoggingLevel) ENABLED START #
    #     self.device.storageLoggingLevel
    #     # PROTECTED REGION END #    //  SdpSubarray.test_storageLoggingLevel
    #
    # def test_testMode(self):
    #     """Test for testMode"""
    #     # PROTECTED REGION ID(SdpSubarray.test_testMode) ENABLED START #
    #     self.device.testMode
    #     # PROTECTED REGION END #    //  SdpSubarray.test_testMode
    #
    # def test_versionId(self):
    #     """Test for versionId"""
    #     # PROTECTED REGION ID(SdpSubarray.test_versionId) ENABLED START #
    #     self.device.versionId
    #     # PROTECTED REGION END #    //  SdpSubarray.test_versionId
    #
    # def test_ReceiveAddresses(self):
    #     """Test for ReceiveAddresses"""
    #     # PROTECTED REGION ID(SdpSubarray.test_ReceiveAddresses) ENABLED START #
    #     self.device.ReceiveAddresses
    #     # PROTECTED REGION END #    //  SdpSubarray.test_ReceiveAddresses
    #
    # def test_ActiveProcessingBlocks(self):
    #     """Test for ActiveProcessingBlocks"""
    #     # PROTECTED REGION ID(SdpSubarray.test_ActiveProcessingBlocks) ENABLED START #
    #     self.device.ActiveProcessingBlocks
    #     # PROTECTED REGION END #    //  SdpSubarray.test_ActiveProcessingBlocks
    #
    # def test_assignedResources(self):
    #     """Test for assignedResources"""
    #     # PROTECTED REGION ID(SdpSubarray.test_assignedResources) ENABLED START #
    #     self.device.assignedResources
    #     # PROTECTED REGION END #    //  SdpSubarray.test_assignedResources
    #
    # def test_configuredCapabilities(self):
    #     """Test for configuredCapabilities"""
    #     # PROTECTED REGION ID(SdpSubarray.test_configuredCapabilities) ENABLED START #
    #     self.device.configuredCapabilities
    #     # PROTECTED REGION END #    //  SdpSubarray.test_configuredCapabilities
