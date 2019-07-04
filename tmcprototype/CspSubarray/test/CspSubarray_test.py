#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of the CspSubarray project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.
"""Contain the tests for the ."""

# Path
import sys
import os
path = os.path.join(os.path.dirname(__file__), os.pardir)
sys.path.insert(0, os.path.abspath(path))

# Imports
from time import sleep
from mock import MagicMock
from PyTango import DevFailed, DevState
from devicetest import DeviceTestCase, main
from CspSubarray import CspSubarray

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
class CspSubarrayDeviceTestCase(DeviceTestCase):
    """Test case for packet generation."""
    # PROTECTED REGION ID(CspSubarray.test_additionnal_import) ENABLED START #
    # PROTECTED REGION END #    //  CspSubarray.test_additionnal_import
    device = CspSubarray
    properties = {'CapabilityTypes': '', 'CentralLoggingTarget': '', 'ElementLoggingTarget': '', 'GroupDefinitions': '', 'SkaLevel': '4', 'StorageLoggingTarget': 'localhost', 'SubID': '', 'SkaLevel': '4', 
                  }
    empty = None  # Should be []

    @classmethod
    def mocking(cls):
        """Mock external libraries."""
        # Example : Mock numpy
        # cls.numpy = CspSubarray.numpy = MagicMock()
        # PROTECTED REGION ID(CspSubarray.test_mocking) ENABLED START #
        # PROTECTED REGION END #    //  CspSubarray.test_mocking

    def test_properties(self):
        # test the properties
        # PROTECTED REGION ID(CspSubarray.test_properties) ENABLED START #
        # PROTECTED REGION END #    //  CspSubarray.test_properties
        pass

    def test_Abort(self):
        """Test for Abort"""
        # PROTECTED REGION ID(CspSubarray.test_Abort) ENABLED START #
        self.device.Abort()
        # PROTECTED REGION END #    //  CspSubarray.test_Abort

    def test_ConfigureCapability(self):
        """Test for ConfigureCapability"""
        # PROTECTED REGION ID(CspSubarray.test_ConfigureCapability) ENABLED START #
        self.device.ConfigureCapability([[0], [""]])
        # PROTECTED REGION END #    //  CspSubarray.test_ConfigureCapability

    def test_DeconfigureAllCapabilities(self):
        """Test for DeconfigureAllCapabilities"""
        # PROTECTED REGION ID(CspSubarray.test_DeconfigureAllCapabilities) ENABLED START #
        self.device.DeconfigureAllCapabilities("")
        # PROTECTED REGION END #    //  CspSubarray.test_DeconfigureAllCapabilities

    def test_DeconfigureCapability(self):
        """Test for DeconfigureCapability"""
        # PROTECTED REGION ID(CspSubarray.test_DeconfigureCapability) ENABLED START #
        self.device.DeconfigureCapability([[0], [""]])
        # PROTECTED REGION END #    //  CspSubarray.test_DeconfigureCapability

    def test_GetVersionInfo(self):
        """Test for GetVersionInfo"""
        # PROTECTED REGION ID(CspSubarray.test_GetVersionInfo) ENABLED START #
        self.device.GetVersionInfo()
        # PROTECTED REGION END #    //  CspSubarray.test_GetVersionInfo

    def test_Status(self):
        """Test for Status"""
        # PROTECTED REGION ID(CspSubarray.test_Status) ENABLED START #
        self.device.Status()
        # PROTECTED REGION END #    //  CspSubarray.test_Status

    def test_State(self):
        """Test for State"""
        # PROTECTED REGION ID(CspSubarray.test_State) ENABLED START #
        self.device.State()
        # PROTECTED REGION END #    //  CspSubarray.test_State

    def test_AssignResources(self):
        """Test for AssignResources"""
        # PROTECTED REGION ID(CspSubarray.test_AssignResources) ENABLED START #
        self.device.AssignResources([""])
        # PROTECTED REGION END #    //  CspSubarray.test_AssignResources

    def test_EndSB(self):
        """Test for EndSB"""
        # PROTECTED REGION ID(CspSubarray.test_EndSB) ENABLED START #
        self.device.EndSB()
        # PROTECTED REGION END #    //  CspSubarray.test_EndSB

    def test_EndScan(self):
        """Test for EndScan"""
        # PROTECTED REGION ID(CspSubarray.test_EndScan) ENABLED START #
        self.device.EndScan()
        # PROTECTED REGION END #    //  CspSubarray.test_EndScan

    def test_ObsState(self):
        """Test for ObsState"""
        # PROTECTED REGION ID(CspSubarray.test_ObsState) ENABLED START #
        self.device.ObsState()
        # PROTECTED REGION END #    //  CspSubarray.test_ObsState

    def test_Pause(self):
        """Test for Pause"""
        # PROTECTED REGION ID(CspSubarray.test_Pause) ENABLED START #
        self.device.Pause()
        # PROTECTED REGION END #    //  CspSubarray.test_Pause

    def test_ReleaseAllResources(self):
        """Test for ReleaseAllResources"""
        # PROTECTED REGION ID(CspSubarray.test_ReleaseAllResources) ENABLED START #
        self.device.ReleaseAllResources()
        # PROTECTED REGION END #    //  CspSubarray.test_ReleaseAllResources

    def test_ReleaseResources(self):
        """Test for ReleaseResources"""
        # PROTECTED REGION ID(CspSubarray.test_ReleaseResources) ENABLED START #
        self.device.ReleaseResources([""])
        # PROTECTED REGION END #    //  CspSubarray.test_ReleaseResources

    def test_Reset(self):
        """Test for Reset"""
        # PROTECTED REGION ID(CspSubarray.test_Reset) ENABLED START #
        self.device.Reset()
        # PROTECTED REGION END #    //  CspSubarray.test_Reset

    def test_Resume(self):
        """Test for Resume"""
        # PROTECTED REGION ID(CspSubarray.test_Resume) ENABLED START #
        self.device.Resume()
        # PROTECTED REGION END #    //  CspSubarray.test_Resume

    def test_Scan(self):
        """Test for Scan"""
        # PROTECTED REGION ID(CspSubarray.test_Scan) ENABLED START #
        self.device.Scan([""])
        # PROTECTED REGION END #    //  CspSubarray.test_Scan

    def test_ConfigureScan(self):
        """Test for ConfigureScan"""
        # PROTECTED REGION ID(CspSubarray.test_ConfigureScan) ENABLED START #
        self.device.ConfigureScan("")
        # PROTECTED REGION END #    //  CspSubarray.test_ConfigureScan

    def test_AddReceptors(self):
        """Test for AddReceptors"""
        # PROTECTED REGION ID(CspSubarray.test_AddReceptors) ENABLED START #
        self.device.AddReceptors([0])
        # PROTECTED REGION END #    //  CspSubarray.test_AddReceptors

    def test_RemoveReceptors(self):
        """Test for RemoveReceptors"""
        # PROTECTED REGION ID(CspSubarray.test_RemoveReceptors) ENABLED START #
        self.device.RemoveReceptors([0])
        # PROTECTED REGION END #    //  CspSubarray.test_RemoveReceptors

    def test_activationTime(self):
        """Test for activationTime"""
        # PROTECTED REGION ID(CspSubarray.test_activationTime) ENABLED START #
        self.device.activationTime
        # PROTECTED REGION END #    //  CspSubarray.test_activationTime

    def test_adminMode(self):
        """Test for adminMode"""
        # PROTECTED REGION ID(CspSubarray.test_adminMode) ENABLED START #
        self.device.adminMode
        # PROTECTED REGION END #    //  CspSubarray.test_adminMode

    def test_buildState(self):
        """Test for buildState"""
        # PROTECTED REGION ID(CspSubarray.test_buildState) ENABLED START #
        self.device.buildState
        # PROTECTED REGION END #    //  CspSubarray.test_buildState

    def test_centralLoggingLevel(self):
        """Test for centralLoggingLevel"""
        # PROTECTED REGION ID(CspSubarray.test_centralLoggingLevel) ENABLED START #
        self.device.centralLoggingLevel
        # PROTECTED REGION END #    //  CspSubarray.test_centralLoggingLevel

    def test_configurationDelayExpected(self):
        """Test for configurationDelayExpected"""
        # PROTECTED REGION ID(CspSubarray.test_configurationDelayExpected) ENABLED START #
        self.device.configurationDelayExpected
        # PROTECTED REGION END #    //  CspSubarray.test_configurationDelayExpected

    def test_configurationProgress(self):
        """Test for configurationProgress"""
        # PROTECTED REGION ID(CspSubarray.test_configurationProgress) ENABLED START #
        self.device.configurationProgress
        # PROTECTED REGION END #    //  CspSubarray.test_configurationProgress

    def test_controlMode(self):
        """Test for controlMode"""
        # PROTECTED REGION ID(CspSubarray.test_controlMode) ENABLED START #
        self.device.controlMode
        # PROTECTED REGION END #    //  CspSubarray.test_controlMode

    def test_elementLoggingLevel(self):
        """Test for elementLoggingLevel"""
        # PROTECTED REGION ID(CspSubarray.test_elementLoggingLevel) ENABLED START #
        self.device.elementLoggingLevel
        # PROTECTED REGION END #    //  CspSubarray.test_elementLoggingLevel

    def test_healthState(self):
        """Test for healthState"""
        # PROTECTED REGION ID(CspSubarray.test_healthState) ENABLED START #
        self.device.healthState
        # PROTECTED REGION END #    //  CspSubarray.test_healthState

    def test_obsMode(self):
        """Test for obsMode"""
        # PROTECTED REGION ID(CspSubarray.test_obsMode) ENABLED START #
        self.device.obsMode
        # PROTECTED REGION END #    //  CspSubarray.test_obsMode

    def test_obsState(self):
        """Test for obsState"""
        # PROTECTED REGION ID(CspSubarray.test_obsState) ENABLED START #
        self.device.obsState
        # PROTECTED REGION END #    //  CspSubarray.test_obsState

    def test_simulationMode(self):
        """Test for simulationMode"""
        # PROTECTED REGION ID(CspSubarray.test_simulationMode) ENABLED START #
        self.device.simulationMode
        # PROTECTED REGION END #    //  CspSubarray.test_simulationMode

    def test_storageLoggingLevel(self):
        """Test for storageLoggingLevel"""
        # PROTECTED REGION ID(CspSubarray.test_storageLoggingLevel) ENABLED START #
        self.device.storageLoggingLevel
        # PROTECTED REGION END #    //  CspSubarray.test_storageLoggingLevel

    def test_testMode(self):
        """Test for testMode"""
        # PROTECTED REGION ID(CspSubarray.test_testMode) ENABLED START #
        self.device.testMode
        # PROTECTED REGION END #    //  CspSubarray.test_testMode

    def test_versionId(self):
        """Test for versionId"""
        # PROTECTED REGION ID(CspSubarray.test_versionId) ENABLED START #
        self.device.versionId
        # PROTECTED REGION END #    //  CspSubarray.test_versionId

    def test_opState(self):
        """Test for opState"""
        # PROTECTED REGION ID(CspSubarray.test_opState) ENABLED START #
        self.device.opState
        # PROTECTED REGION END #    //  CspSubarray.test_opState

    def test_procMode(self):
        """Test for procMode"""
        # PROTECTED REGION ID(CspSubarray.test_procMode) ENABLED START #
        self.device.procMode
        # PROTECTED REGION END #    //  CspSubarray.test_procMode

    def test_frequencyBand(self):
        """Test for frequencyBand"""
        # PROTECTED REGION ID(CspSubarray.test_frequencyBand) ENABLED START #
        self.device.frequencyBand
        # PROTECTED REGION END #    //  CspSubarray.test_frequencyBand

    def test_scanId(self):
        """Test for scanId"""
        # PROTECTED REGION ID(CspSubarray.test_scanId) ENABLED START #
        self.device.scanId
        # PROTECTED REGION END #    //  CspSubarray.test_scanId

    def test_correlation(self):
        """Test for correlation"""
        # PROTECTED REGION ID(CspSubarray.test_correlation) ENABLED START #
        self.device.correlation
        # PROTECTED REGION END #    //  CspSubarray.test_correlation

    def test_assignedResources(self):
        """Test for assignedResources"""
        # PROTECTED REGION ID(CspSubarray.test_assignedResources) ENABLED START #
        self.device.assignedResources
        # PROTECTED REGION END #    //  CspSubarray.test_assignedResources

    def test_configuredCapabilities(self):
        """Test for configuredCapabilities"""
        # PROTECTED REGION ID(CspSubarray.test_configuredCapabilities) ENABLED START #
        self.device.configuredCapabilities
        # PROTECTED REGION END #    //  CspSubarray.test_configuredCapabilities

    def test_receptors(self):
        """Test for receptors"""
        # PROTECTED REGION ID(CspSubarray.test_receptors) ENABLED START #
        self.device.receptors
        # PROTECTED REGION END #    //  CspSubarray.test_receptors

    def test_correlationDigitalBandpassCorrectionCoefficients(self):
        """Test for correlationDigitalBandpassCorrectionCoefficients"""
        # PROTECTED REGION ID(CspSubarray.test_correlationDigitalBandpassCorrectionCoefficients) ENABLED START #
        self.device.correlationDigitalBandpassCorrectionCoefficients
        # PROTECTED REGION END #    //  CspSubarray.test_correlationDigitalBandpassCorrectionCoefficients


# Main execution
if __name__ == "__main__":
    main()
