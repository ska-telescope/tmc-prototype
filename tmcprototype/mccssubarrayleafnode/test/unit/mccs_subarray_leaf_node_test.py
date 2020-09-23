#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of the MCCSSubarrayLeafNode project
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
from MCCSSubarrayLeafNode import MCCSSubarrayLeafNode

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
class MCCSSubarrayLeafNodeDeviceTestCase(DeviceTestCase):
    """Test case for packet generation."""
    # PROTECTED REGION ID(MCCSSubarrayLeafNode.test_additionnal_import) ENABLED START #
    # PROTECTED REGION END #    //  MCCSSubarrayLeafNode.test_additionnal_import
    device = MCCSSubarrayLeafNode
    properties = {'SkaLevel': '3', 'GroupDefinitions': '', 'LoggingLevelDefault': '5', 'LoggingTargetsDefault': 'tango::logger', 'MCCSSubarrayFQDN': 'low_mccs/elt/subarray_01', 
                  }
    empty = None  # Should be []

    @classmethod
    def mocking(cls):
        """Mock external libraries."""
        # Example : Mock numpy
        # cls.numpy = MCCSSubarrayLeafNode.numpy = MagicMock()
        # PROTECTED REGION ID(MCCSSubarrayLeafNode.test_mocking) ENABLED START #
        # PROTECTED REGION END #    //  MCCSSubarrayLeafNode.test_mocking

    def test_properties(self):
        # test the properties
        # PROTECTED REGION ID(MCCSSubarrayLeafNode.test_properties) ENABLED START #
        # PROTECTED REGION END #    //  MCCSSubarrayLeafNode.test_properties
        pass

    def test_State(self):
        """Test for State"""
        # PROTECTED REGION ID(MCCSSubarrayLeafNode.test_State) ENABLED START #
        self.device.State()
        # PROTECTED REGION END #    //  MCCSSubarrayLeafNode.test_State

    def test_Status(self):
        """Test for Status"""
        # PROTECTED REGION ID(MCCSSubarrayLeafNode.test_Status) ENABLED START #
        self.device.Status()
        # PROTECTED REGION END #    //  MCCSSubarrayLeafNode.test_Status

    def test_GetVersionInfo(self):
        """Test for GetVersionInfo"""
        # PROTECTED REGION ID(MCCSSubarrayLeafNode.test_GetVersionInfo) ENABLED START #
        self.device.GetVersionInfo()
        # PROTECTED REGION END #    //  MCCSSubarrayLeafNode.test_GetVersionInfo

    def test_Reset(self):
        """Test for Reset"""
        # PROTECTED REGION ID(MCCSSubarrayLeafNode.test_Reset) ENABLED START #
        self.device.Reset()
        # PROTECTED REGION END #    //  MCCSSubarrayLeafNode.test_Reset

    def test_AssignResources(self):
        """Test for AssignResources"""
        # PROTECTED REGION ID(MCCSSubarrayLeafNode.test_AssignResources) ENABLED START #
        self.device.AssignResources("")
        # PROTECTED REGION END #    //  MCCSSubarrayLeafNode.test_AssignResources

    def test_ReleaseResources(self):
        """Test for ReleaseResources"""
        # PROTECTED REGION ID(MCCSSubarrayLeafNode.test_ReleaseResources) ENABLED START #
        self.device.ReleaseResources("")
        # PROTECTED REGION END #    //  MCCSSubarrayLeafNode.test_ReleaseResources

    def test_Configure(self):
        """Test for Configure"""
        # PROTECTED REGION ID(MCCSSubarrayLeafNode.test_Configure) ENABLED START #
        self.device.Configure("")
        # PROTECTED REGION END #    //  MCCSSubarrayLeafNode.test_Configure

    def test_Scan(self):
        """Test for Scan"""
        # PROTECTED REGION ID(MCCSSubarrayLeafNode.test_Scan) ENABLED START #
        self.device.Scan([""])
        # PROTECTED REGION END #    //  MCCSSubarrayLeafNode.test_Scan

    def test_EndScan(self):
        """Test for EndScan"""
        # PROTECTED REGION ID(MCCSSubarrayLeafNode.test_EndScan) ENABLED START #
        self.device.EndScan()
        # PROTECTED REGION END #    //  MCCSSubarrayLeafNode.test_EndScan

    def test_End(self):
        """Test for End"""
        # PROTECTED REGION ID(MCCSSubarrayLeafNode.test_End) ENABLED START #
        self.device.End()
        # PROTECTED REGION END #    //  MCCSSubarrayLeafNode.test_End

    def test_Abort(self):
        """Test for Abort"""
        # PROTECTED REGION ID(MCCSSubarrayLeafNode.test_Abort) ENABLED START #
        self.device.Abort()
        # PROTECTED REGION END #    //  MCCSSubarrayLeafNode.test_Abort

    def test_Restart(self):
        """Test for Restart"""
        # PROTECTED REGION ID(MCCSSubarrayLeafNode.test_Restart) ENABLED START #
        self.device.Restart()
        # PROTECTED REGION END #    //  MCCSSubarrayLeafNode.test_Restart

    def test_obsReset(self):
        """Test for obsReset"""
        # PROTECTED REGION ID(MCCSSubarrayLeafNode.test_obsReset) ENABLED START #
        self.device.obsReset()
        # PROTECTED REGION END #    //  MCCSSubarrayLeafNode.test_obsReset

    def test_buildState(self):
        """Test for buildState"""
        # PROTECTED REGION ID(MCCSSubarrayLeafNode.test_buildState) ENABLED START #
        self.device.buildState
        # PROTECTED REGION END #    //  MCCSSubarrayLeafNode.test_buildState

    def test_versionId(self):
        """Test for versionId"""
        # PROTECTED REGION ID(MCCSSubarrayLeafNode.test_versionId) ENABLED START #
        self.device.versionId
        # PROTECTED REGION END #    //  MCCSSubarrayLeafNode.test_versionId

    def test_loggingLevel(self):
        """Test for loggingLevel"""
        # PROTECTED REGION ID(MCCSSubarrayLeafNode.test_loggingLevel) ENABLED START #
        self.device.loggingLevel
        # PROTECTED REGION END #    //  MCCSSubarrayLeafNode.test_loggingLevel

    def test_healthState(self):
        """Test for healthState"""
        # PROTECTED REGION ID(MCCSSubarrayLeafNode.test_healthState) ENABLED START #
        self.device.healthState
        # PROTECTED REGION END #    //  MCCSSubarrayLeafNode.test_healthState

    def test_adminMode(self):
        """Test for adminMode"""
        # PROTECTED REGION ID(MCCSSubarrayLeafNode.test_adminMode) ENABLED START #
        self.device.adminMode
        # PROTECTED REGION END #    //  MCCSSubarrayLeafNode.test_adminMode

    def test_controlMode(self):
        """Test for controlMode"""
        # PROTECTED REGION ID(MCCSSubarrayLeafNode.test_controlMode) ENABLED START #
        self.device.controlMode
        # PROTECTED REGION END #    //  MCCSSubarrayLeafNode.test_controlMode

    def test_simulationMode(self):
        """Test for simulationMode"""
        # PROTECTED REGION ID(MCCSSubarrayLeafNode.test_simulationMode) ENABLED START #
        self.device.simulationMode
        # PROTECTED REGION END #    //  MCCSSubarrayLeafNode.test_simulationMode

    def test_testMode(self):
        """Test for testMode"""
        # PROTECTED REGION ID(MCCSSubarrayLeafNode.test_testMode) ENABLED START #
        self.device.testMode
        # PROTECTED REGION END #    //  MCCSSubarrayLeafNode.test_testMode

    def test_activitymessage(self):
        """Test for activitymessage"""
        # PROTECTED REGION ID(MCCSSubarrayLeafNode.test_activitymessage) ENABLED START #
        self.device.activitymessage
        # PROTECTED REGION END #    //  MCCSSubarrayLeafNode.test_activitymessage

    def test_loggingTargets(self):
        """Test for loggingTargets"""
        # PROTECTED REGION ID(MCCSSubarrayLeafNode.test_loggingTargets) ENABLED START #
        self.device.loggingTargets
        # PROTECTED REGION END #    //  MCCSSubarrayLeafNode.test_loggingTargets


# Main execution
if __name__ == "__main__":
    main()
