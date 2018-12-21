#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of the SubarrayNode project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.
"""Contain the tests for the Subarray Node."""

# Path
import sys
import os
path = os.path.join(os.path.dirname(__file__), os.pardir)
sys.path.insert(0, os.path.abspath(path))

# Imports
from time import sleep
from mock import MagicMock
from PyTango import DevFailed, DevState
#from devicetest import DeviceTestCase, main
import pytest
from SubarrayNode import SubarrayNode

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

class TestSubarrayNode(object):
    """Test case for packet generation."""
    # PROTECTED REGION ID(SubarrayNode.test_additionnal_import) ENABLED START #
    # PROTECTED REGION END #    //  SubarrayNode.test_additionnal_import
    device = SubarrayNode
    properties = {'CapabilityTypes': '', 'CentralLoggingTarget': '', 'ElementLoggingTarget': '', 'GroupDefinitions': '', 'MetricList': 'healthState', 'SkaLevel': '4', 'StorageLoggingTarget': 'localhost', 'SubID': '', 'DishLeafNodePrefix': 'ska_mid/tm_leaf_node/d', 
                  }
    empty = None  # Should be []

    @classmethod
    def mocking(cls):
        """Mock external libraries."""
        # Example : Mock numpy
        # cls.numpy = SubarrayNode.numpy = MagicMock()
        # PROTECTED REGION ID(SubarrayNode.test_mocking) ENABLED START #
        # PROTECTED REGION END #    //  SubarrayNode.test_mocking

    def test_properties(self, tango_context):
        # test the properties
        # PROTECTED REGION ID(SubarrayNode.test_properties) ENABLED START #
        # PROTECTED REGION END #    //  SubarrayNode.test_properties
        pass

    def test_Abort(self, tango_context):
        """Test for Abort"""
        # PROTECTED REGION ID(SubarrayNode.test_Abort) ENABLED START #
        #self.device.Abort()
        # PROTECTED REGION END #    //  SubarrayNode.test_Abort

    def test_ConfigureCapability(self, tango_context):
        """Test for ConfigureCapability"""
        # PROTECTED REGION ID(SubarrayNode.test_ConfigureCapability) ENABLED START #
        #self.device.ConfigureCapability([[0], [""]])
        # PROTECTED REGION END #    //  SubarrayNode.test_ConfigureCapability

    def test_DeconfigureAllCapabilities(self, tango_context):
        """Test for DeconfigureAllCapabilities"""
        # PROTECTED REGION ID(SubarrayNode.test_DeconfigureAllCapabilities) ENABLED START #
        #self.device.DeconfigureAllCapabilities("")
        # PROTECTED REGION END #    //  SubarrayNode.test_DeconfigureAllCapabilities

    def test_DeconfigureCapability(self, tango_context):
        """Test for DeconfigureCapability"""
        # PROTECTED REGION ID(SubarrayNode.test_DeconfigureCapability) ENABLED START #
        #self.device.DeconfigureCapability([[0], [""]])
        # PROTECTED REGION END #    //  SubarrayNode.test_DeconfigureCapability

    def test_GetMetrics(self, tango_context):
        """Test for GetMetrics"""
        # PROTECTED REGION ID(SubarrayNode.test_GetMetrics) ENABLED START #
        #self.device.GetMetrics()
        # PROTECTED REGION END #    //  SubarrayNode.test_GetMetrics

    def test_GetVersionInfo(self, tango_context):
        """Test for GetVersionInfo"""
        # PROTECTED REGION ID(SubarrayNode.test_GetVersionInfo) ENABLED START #
        #self.device.GetVersionInfo()
        # PROTECTED REGION END #    //  SubarrayNode.test_GetVersionInfo

    def test_Status(self, tango_context):
        """Test for Status"""
        # PROTECTED REGION ID(SubarrayNode.test_Status) ENABLED START #
        #self.device.Status()
        assert tango_context.device.Status() == "SubarrayNode is initialized successfully."
        # PROTECTED REGION END #    //  SubarrayNode.test_Status

    def test_State(self, tango_context):
        """Test for State"""
        # PROTECTED REGION ID(SubarrayNode.test_State) ENABLED START #
        #self.device.State()
        assert tango_context.device.State() == DevState.OFF
        # PROTECTED REGION END #    //  SubarrayNode.test_State

    def test_AssignResources(self, tango_context):
        """Test for AssignResources"""
        # PROTECTED REGION ID(SubarrayNode.test_AssignResources) ENABLED START #
        #self.device.AssignResources([""])
        list = ["0001"]
        tango_context.device.AssignResources(list)
        assert tango_context.device.State() == DevState.ON
        assert len(tango_context.device.receptorIDList) == 1
        print "receptor id list is:", tango_context.device.receptorIDList
        #assert tango_context.device.receptorIDList[1] == int(list)

        assert tango_context.device.obsState == 0
        # PROTECTED REGION END #    //  SubarrayNode.test_AssignResources

    def test_Scan(self, tango_context):
        """Test for Scan"""
        # PROTECTED REGION ID(SubarrayNode.test_Scan) ENABLED START #
        #self.device.Scan([""])
        tango_context.device.Scan("0")
        assert tango_context.device.obsState == 3
        # PROTECTED REGION END #    //  SubarrayNode.test_Scan

    def test_EndSB(self, tango_context):
        """Test for EndSB"""
        # PROTECTED REGION ID(SubarrayNode.test_EndSB) ENABLED START #
        #self.device.EndSB()
        # PROTECTED REGION END #    //  SubarrayNode.test_EndSB

    def test_EndScan(self, tango_context):
        """Test for EndScan"""
        # PROTECTED REGION ID(SubarrayNode.test_EndScan) ENABLED START #
        #self.device.EndScan()
        tango_context.device.EndScan()
        assert tango_context.device.obsState == 0
        # PROTECTED REGION END #    //  SubarrayNode.test_EndScan

    def test_ObsState(self, tango_context):
        """Test for ObsState"""
        # PROTECTED REGION ID(SubarrayNode.test_ObsState) ENABLED START #
        #self.device.ObsState()
        # PROTECTED REGION END #    //  SubarrayNode.test_ObsState

    def test_Pause(self, tango_context):
        """Test for Pause"""
        # PROTECTED REGION ID(SubarrayNode.test_Pause) ENABLED START #
        #self.device.Pause()
        # PROTECTED REGION END #    //  SubarrayNode.test_Pause

    def test_ReleaseAllResources(self, tango_context):
        """Test for ReleaseAllResources"""
        # PROTECTED REGION ID(SubarrayNode.test_ReleaseAllResources) ENABLED START #
        #self.device.ReleaseAllResources()
        tango_context.device.ReleaseAllResources()
        assert tango_context.device.obsState == 0
        assert tango_context.device.State() == DevState.OFF
        # PROTECTED REGION END #    //  SubarrayNode.test_ReleaseAllResources

    def test_ReleaseResources(self, tango_context):
        """Test for ReleaseResources"""
        # PROTECTED REGION ID(SubarrayNode.test_ReleaseResources) ENABLED START #
        #self.device.ReleaseResources([""])
        # PROTECTED REGION END #    //  SubarrayNode.test_ReleaseResources

    def test_Reset(self, tango_context):
        """Test for Reset"""
        # PROTECTED REGION ID(SubarrayNode.test_Reset) ENABLED START #
        #self.device.Reset()
        # PROTECTED REGION END #    //  SubarrayNode.test_Reset

    def test_Resume(self, tango_context):
        """Test for Resume"""
        # PROTECTED REGION ID(SubarrayNode.test_Resume) ENABLED START #
        #self.device.Resume()
        # PROTECTED REGION END #    //  SubarrayNode.test_Resume



    def test_ToJson(self, tango_context):
        """Test for ToJson"""
        # PROTECTED REGION ID(SubarrayNode.test_ToJson) ENABLED START #
        #self.device.ToJson("")
        # PROTECTED REGION END #    //  SubarrayNode.test_ToJson

    def test_Configure(self, tango_context):
        """Test for Configure"""
        # PROTECTED REGION ID(SubarrayNode.test_Configure) ENABLED START #
        #self.device.Configure()
        #tango_context.device.Configure("1,1")
        # PROTECTED REGION END #    //  SubarrayNode.test_Configure

    def test_activationTime(self, tango_context):
        """Test for activationTime"""
        # PROTECTED REGION ID(SubarrayNode.test_activationTime) ENABLED START #
        #self.device.activationTime
        assert tango_context.device.activationTime == 0.0
        # PROTECTED REGION END #    //  SubarrayNode.test_activationTime

    def test_adminMode(self, tango_context):
        """Test for adminMode"""
        # PROTECTED REGION ID(SubarrayNode.test_adminMode) ENABLED START #
        #self.device.adminMode
        assert tango_context.device.adminMode == 0
        # PROTECTED REGION END #    //  SubarrayNode.test_adminMode

    def test_buildState(self, tango_context):
        """Test for buildState"""
        # PROTECTED REGION ID(SubarrayNode.test_buildState) ENABLED START #
        #self.device.buildState
        assert tango_context.device.buildState == "tangods-skabasedevice, 1.0.0, A generic base device for SKA."
        # PROTECTED REGION END #    //  SubarrayNode.test_buildState

    def test_centralLoggingLevel(self, tango_context):
        """Test for centralLoggingLevel"""
        # PROTECTED REGION ID(SubarrayNode.test_centralLoggingLevel) ENABLED START #
        #self.device.centralLoggingLevel
        level = 5
        tango_context.device.centralLoggingLevel = level
        assert tango_context.device.centralLoggingLevel == level
        # PROTECTED REGION END #    //  SubarrayNode.test_centralLoggingLevel

    def test_configurationDelayExpected(self, tango_context):
        """Test for configurationDelayExpected"""
        # PROTECTED REGION ID(SubarrayNode.test_configurationDelayExpected) ENABLED START #
        #self.device.configurationDelayExpected
        assert tango_context.device.configurationDelayExpected == 0
        # PROTECTED REGION END #    //  SubarrayNode.test_configurationDelayExpected

    def test_configurationProgress(self, tango_context):
        """Test for configurationProgress"""
        # PROTECTED REGION ID(SubarrayNode.test_configurationProgress) ENABLED START #
        #self.device.configurationProgress
        assert tango_context.device.configurationProgress == 0
        # PROTECTED REGION END #    //  SubarrayNode.test_configurationProgress

    def test_controlMode(self, tango_context):
        """Test for controlMode"""
        # PROTECTED REGION ID(SubarrayNode.test_controlMode) ENABLED START #
        #self.device.controlMode
        control_mode = 0
        tango_context.device.controlMode = control_mode
        assert tango_context.device.controlMode == control_mode
        # PROTECTED REGION END #    //  SubarrayNode.test_controlMode

    def test_elementLoggingLevel(self, tango_context):
        """Test for elementLoggingLevel"""
        # PROTECTED REGION ID(SubarrayNode.test_elementLoggingLevel) ENABLED START #
        #self.device.elementLoggingLevel
        level = 5
        tango_context.device.elementLoggingLevel = level
        assert tango_context.device.elementLoggingLevel == level
        # PROTECTED REGION END #    //  SubarrayNode.test_elementLoggingLevel

    def test_healthState(self, tango_context):
        """Test for healthState"""
        # PROTECTED REGION ID(SubarrayNode.test_healthState) ENABLED START #
        #self.device.healthState
        assert tango_context.device.healthState == 0
        # PROTECTED REGION END #    //  SubarrayNode.test_healthState

    def test_obsMode(self, tango_context):
        """Test for obsMode"""
        # PROTECTED REGION ID(SubarrayNode.test_obsMode) ENABLED START #
        #self.device.obsMode
        assert tango_context.device.obsMode == 0
        # PROTECTED REGION END #    //  SubarrayNode.test_obsMode

    def test_obsState(self, tango_context):
        """Test for obsState"""
        # PROTECTED REGION ID(SubarrayNode.test_obsState) ENABLED START #
        #self.device.obsState
        assert tango_context.device.obsState == 0
        # PROTECTED REGION END #    //  SubarrayNode.test_obsState

    def test_simulationMode(self, tango_context):
        """Test for simulationMode"""
        # PROTECTED REGION ID(SubarrayNode.test_simulationMode) ENABLED START #
        #self.device.simulationMode
        simulation_mode = 0
        tango_context.device.simulationMode = simulation_mode
        assert tango_context.device.simulationMode == simulation_mode
        # PROTECTED REGION END #    //  SubarrayNode.test_simulationMode

    def test_storageLoggingLevel(self, tango_context):
        """Test for storageLoggingLevel"""
        # PROTECTED REGION ID(SubarrayNode.test_storageLoggingLevel) ENABLED START #
        #self.device.storageLoggingLevel
        level = 5
        tango_context.device.storageLoggingLevel = level
        assert tango_context.device.storageLoggingLevel == level
        # PROTECTED REGION END #    //  SubarrayNode.test_storageLoggingLevel

    def test_testMode(self, tango_context):
        """Test for testMode"""
        # PROTECTED REGION ID(SubarrayNode.test_testMode) ENABLED START #
        #self.device.testMode
        test_mode = "False"
        tango_context.device.testMode = test_mode
        assert tango_context.device.testMode == test_mode
        # PROTECTED REGION END #    //  SubarrayNode.test_testMode

    def test_versionId(self, tango_context):
        """Test for versionId"""
        # PROTECTED REGION ID(SubarrayNode.test_versionId) ENABLED START #
        #self.device.versionId
        assert tango_context.device.versionId == "1.0.0"
        # PROTECTED REGION END #    //  SubarrayNode.test_versionId

    def test_scanID(self, tango_context):
        """Test for scanID"""
        # PROTECTED REGION ID(SubarrayNode.test_scanID) ENABLED START #
        #self.device.scanID
        assert tango_context.device.scanID == ""
        # PROTECTED REGION END #    //  SubarrayNode.test_scanID

    def test_sbID(self, tango_context):
        """Test for sbID"""
        # PROTECTED REGION ID(SubarrayNode.test_sbID) ENABLED START #
        #self.device.sbID
        assert tango_context.device.sbID == ""
        # PROTECTED REGION END #    //  SubarrayNode.test_sbID

    def test_activityMessage(self, tango_context):
        """Test for activityMessage"""
        # PROTECTED REGION ID(SubarrayNode.test_activityMessage) ENABLED START #
        #self.device.activityMessage
        message = "OK"
        tango_context.device.activityMessage = message
        assert tango_context.device.activityMessage == message
        # PROTECTED REGION END #    //  SubarrayNode.test_activityMessage

    def test_assignedResources(self, tango_context):
        """Test for assignedResources"""
        # PROTECTED REGION ID(SubarrayNode.test_assignedResources) ENABLED START #
        #self.device.assignedResources
        assert tango_context.device.assignedResources == ("",)
        # PROTECTED REGION END #    //  SubarrayNode.test_assignedResources

    def test_configuredCapabilities(self, tango_context):
        """Test for configuredCapabilities"""
        # PROTECTED REGION ID(SubarrayNode.test_configuredCapabilities) ENABLED START #
        #self.device.configuredCapabilities
        assert tango_context.device.configuredCapabilities == None
        # PROTECTED REGION END #    //  SubarrayNode.test_configuredCapabilities

    def test_receptorIDList(self, tango_context):
        """Test for receptorIDList"""
        # PROTECTED REGION ID(SubarrayNode.test_receptorIDList) ENABLED START #
        #self.device.receptorIDList
        #receptors = []
        #tango_context.device.receptorIDList = receptors
        assert tango_context.device.receptorIDList == None
        # PROTECTED REGION END #    //  SubarrayNode.test_receptorIDList


# Main execution
if __name__ == "__main__":
    main()
