#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of the MCCSMasterLeafNode project
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
from MCCSMasterLeafNode import MCCSMasterLeafNode

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
class MCCSMasterLeafNodeDeviceTestCase(DeviceTestCase):
    """Test case for packet generation."""
    # PROTECTED REGION ID(MCCSMasterLeafNode.test_additionnal_import) ENABLED START #
    # PROTECTED REGION END #    //  MCCSMasterLeafNode.test_additionnal_import
    device = MCCSMasterLeafNode
    properties = {'SkaLevel': '3', 'GroupDefinitions': '', 'LoggingLevelDefault': '5', 'LoggingTargetsDefault': 'tango::logger', 'MCCSMasterFQDN': 'low_mccs/elt/master', 
                  }
    empty = None  # Should be []

    @classmethod
    def mocking(cls):
        """Mock external libraries."""
        # Example : Mock numpy
        # cls.numpy = MCCSMasterLeafNode.numpy = MagicMock()
        # PROTECTED REGION ID(MCCSMasterLeafNode.test_mocking) ENABLED START #
        # PROTECTED REGION END #    //  MCCSMasterLeafNode.test_mocking

    def test_properties(self):
        # test the properties
        # PROTECTED REGION ID(MCCSMasterLeafNode.test_properties) ENABLED START #
        # PROTECTED REGION END #    //  MCCSMasterLeafNode.test_properties
        pass

    def test_State(self):
        """Test for State"""
        # PROTECTED REGION ID(MCCSMasterLeafNode.test_State) ENABLED START #
        self.device.State()
        # PROTECTED REGION END #    //  MCCSMasterLeafNode.test_State

    def test_Status(self):
        """Test for Status"""
        # PROTECTED REGION ID(MCCSMasterLeafNode.test_Status) ENABLED START #
        self.device.Status()
        # PROTECTED REGION END #    //  MCCSMasterLeafNode.test_Status

    def test_GetVersionInfo(self):
        """Test for GetVersionInfo"""
        # PROTECTED REGION ID(MCCSMasterLeafNode.test_GetVersionInfo) ENABLED START #
        self.device.GetVersionInfo()
        # PROTECTED REGION END #    //  MCCSMasterLeafNode.test_GetVersionInfo

    def test_Reset(self):
        """Test for Reset"""
        # PROTECTED REGION ID(MCCSMasterLeafNode.test_Reset) ENABLED START #
        self.device.Reset()
        # PROTECTED REGION END #    //  MCCSMasterLeafNode.test_Reset

    def test_AssignResource(self):
        """Test for AssignResource"""
        # PROTECTED REGION ID(MCCSMasterLeafNode.test_AssignResource) ENABLED START #
        self.device.AssignResource("")
        # PROTECTED REGION END #    //  MCCSMasterLeafNode.test_AssignResource

    def test_ReleaseResources(self):
        """Test for ReleaseResources"""
        # PROTECTED REGION ID(MCCSMasterLeafNode.test_ReleaseResources) ENABLED START #
        self.device.ReleaseResources("")
        # PROTECTED REGION END #    //  MCCSMasterLeafNode.test_ReleaseResources

    def test_On(self):
        """Test for On"""
        # PROTECTED REGION ID(MCCSMasterLeafNode.test_On) ENABLED START #
        self.device.On()
        # PROTECTED REGION END #    //  MCCSMasterLeafNode.test_On

    def test_Off(self):
        """Test for Off"""
        # PROTECTED REGION ID(MCCSMasterLeafNode.test_Off) ENABLED START #
        self.device.Off()
        # PROTECTED REGION END #    //  MCCSMasterLeafNode.test_Off

    def test_buildState(self):
        """Test for buildState"""
        # PROTECTED REGION ID(MCCSMasterLeafNode.test_buildState) ENABLED START #
        self.device.buildState
        # PROTECTED REGION END #    //  MCCSMasterLeafNode.test_buildState

    def test_versionId(self):
        """Test for versionId"""
        # PROTECTED REGION ID(MCCSMasterLeafNode.test_versionId) ENABLED START #
        self.device.versionId
        # PROTECTED REGION END #    //  MCCSMasterLeafNode.test_versionId

    def test_loggingLevel(self):
        """Test for loggingLevel"""
        # PROTECTED REGION ID(MCCSMasterLeafNode.test_loggingLevel) ENABLED START #
        self.device.loggingLevel
        # PROTECTED REGION END #    //  MCCSMasterLeafNode.test_loggingLevel

    def test_healthState(self):
        """Test for healthState"""
        # PROTECTED REGION ID(MCCSMasterLeafNode.test_healthState) ENABLED START #
        self.device.healthState
        # PROTECTED REGION END #    //  MCCSMasterLeafNode.test_healthState

    def test_adminMode(self):
        """Test for adminMode"""
        # PROTECTED REGION ID(MCCSMasterLeafNode.test_adminMode) ENABLED START #
        self.device.adminMode
        # PROTECTED REGION END #    //  MCCSMasterLeafNode.test_adminMode

    def test_controlMode(self):
        """Test for controlMode"""
        # PROTECTED REGION ID(MCCSMasterLeafNode.test_controlMode) ENABLED START #
        self.device.controlMode
        # PROTECTED REGION END #    //  MCCSMasterLeafNode.test_controlMode

    def test_simulationMode(self):
        """Test for simulationMode"""
        # PROTECTED REGION ID(MCCSMasterLeafNode.test_simulationMode) ENABLED START #
        self.device.simulationMode
        # PROTECTED REGION END #    //  MCCSMasterLeafNode.test_simulationMode

    def test_testMode(self):
        """Test for testMode"""
        # PROTECTED REGION ID(MCCSMasterLeafNode.test_testMode) ENABLED START #
        self.device.testMode
        # PROTECTED REGION END #    //  MCCSMasterLeafNode.test_testMode

    def test_activitymessage(self):
        """Test for activitymessage"""
        # PROTECTED REGION ID(MCCSMasterLeafNode.test_activitymessage) ENABLED START #
        self.device.activitymessage
        # PROTECTED REGION END #    //  MCCSMasterLeafNode.test_activitymessage

    def test_loggingTargets(self):
        """Test for loggingTargets"""
        # PROTECTED REGION ID(MCCSMasterLeafNode.test_loggingTargets) ENABLED START #
        self.device.loggingTargets
        # PROTECTED REGION END #    //  MCCSMasterLeafNode.test_loggingTargets


# Main execution
if __name__ == "__main__":
    main()
