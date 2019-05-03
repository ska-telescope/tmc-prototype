#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of the CspMasterLeafNode project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.
"""Contain the tests for the CspMasterLeafNode."""

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
from CspMasterLeafNode import CspMasterLeafNode

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
class CspMasterLeafNodeDeviceTestCase(DeviceTestCase):
    """Test case for packet generation."""
    # PROTECTED REGION ID(CspMasterLeafNode.test_additionnal_import) ENABLED START #
    # PROTECTED REGION END #    //  CspMasterLeafNode.test_additionnal_import
    device = CspMasterLeafNode
    properties = {'SkaLevel': '4', 'GroupDefinitions': '', 'CentralLoggingTarget': '', 'ElementLoggingTarget': '', 'StorageLoggingTarget': 'localhost', 'CspMasterFQDN': '', 
                  }
    empty = None  # Should be []

    @classmethod
    def mocking(cls):
        """Mock external libraries."""
        # Example : Mock numpy
        # cls.numpy = CspMasterLeafNode.numpy = MagicMock()
        # PROTECTED REGION ID(CspMasterLeafNode.test_mocking) ENABLED START #
        # PROTECTED REGION END #    //  CspMasterLeafNode.test_mocking

    def test_properties(self):
        # test the properties
        # PROTECTED REGION ID(CspMasterLeafNode.test_properties) ENABLED START #
        # PROTECTED REGION END #    //  CspMasterLeafNode.test_properties
        pass

    def test_State(self):
        """Test for State"""
        # PROTECTED REGION ID(CspMasterLeafNode.test_State) ENABLED START #
        self.device.State()
        # PROTECTED REGION END #    //  CspMasterLeafNode.test_State

    def test_Status(self):
        """Test for Status"""
        # PROTECTED REGION ID(CspMasterLeafNode.test_Status) ENABLED START #
        self.device.Status()
        # PROTECTED REGION END #    //  CspMasterLeafNode.test_Status

    def test_GetVersionInfo(self):
        """Test for GetVersionInfo"""
        # PROTECTED REGION ID(CspMasterLeafNode.test_GetVersionInfo) ENABLED START #
        self.device.GetVersionInfo()
        # PROTECTED REGION END #    //  CspMasterLeafNode.test_GetVersionInfo

    def test_Reset(self):
        """Test for Reset"""
        # PROTECTED REGION ID(CspMasterLeafNode.test_Reset) ENABLED START #
        self.device.Reset()
        # PROTECTED REGION END #    //  CspMasterLeafNode.test_Reset

    def test_On(self):
        """Test for On"""
        # PROTECTED REGION ID(CspMasterLeafNode.test_On) ENABLED START #
        self.device.On([""])
        # PROTECTED REGION END #    //  CspMasterLeafNode.test_On

    def test_Off(self):
        """Test for Off"""
        # PROTECTED REGION ID(CspMasterLeafNode.test_Off) ENABLED START #
        self.device.Off([""])
        # PROTECTED REGION END #    //  CspMasterLeafNode.test_Off

    def test_Standby(self):
        """Test for Standby"""
        # PROTECTED REGION ID(CspMasterLeafNode.test_Standby) ENABLED START #
        self.device.Standby([""])
        # PROTECTED REGION END #    //  CspMasterLeafNode.test_Standby

    def test_SetCbfAdminMode(self):
        """Test for SetCbfAdminMode"""
        # PROTECTED REGION ID(CspMasterLeafNode.test_SetCbfAdminMode) ENABLED START #
        self.device.SetCbfAdminMode(0)
        # PROTECTED REGION END #    //  CspMasterLeafNode.test_SetCbfAdminMode

    def test_SetPssAdminMode(self):
        """Test for SetPssAdminMode"""
        # PROTECTED REGION ID(CspMasterLeafNode.test_SetPssAdminMode) ENABLED START #
        self.device.SetPssAdminMode(0)
        # PROTECTED REGION END #    //  CspMasterLeafNode.test_SetPssAdminMode

    def test_SetPstAdminMode(self):
        """Test for SetPstAdminMode"""
        # PROTECTED REGION ID(CspMasterLeafNode.test_SetPstAdminMode) ENABLED START #
        self.device.SetPstAdminMode(0)
        # PROTECTED REGION END #    //  CspMasterLeafNode.test_SetPstAdminMode

    def test_buildState(self):
        """Test for buildState"""
        # PROTECTED REGION ID(CspMasterLeafNode.test_buildState) ENABLED START #
        self.device.buildState
        # PROTECTED REGION END #    //  CspMasterLeafNode.test_buildState

    def test_versionId(self):
        """Test for versionId"""
        # PROTECTED REGION ID(CspMasterLeafNode.test_versionId) ENABLED START #
        self.device.versionId
        # PROTECTED REGION END #    //  CspMasterLeafNode.test_versionId

    def test_centralLoggingLevel(self):
        """Test for centralLoggingLevel"""
        # PROTECTED REGION ID(CspMasterLeafNode.test_centralLoggingLevel) ENABLED START #
        self.device.centralLoggingLevel
        # PROTECTED REGION END #    //  CspMasterLeafNode.test_centralLoggingLevel

    def test_elementLoggingLevel(self):
        """Test for elementLoggingLevel"""
        # PROTECTED REGION ID(CspMasterLeafNode.test_elementLoggingLevel) ENABLED START #
        self.device.elementLoggingLevel
        # PROTECTED REGION END #    //  CspMasterLeafNode.test_elementLoggingLevel

    def test_storageLoggingLevel(self):
        """Test for storageLoggingLevel"""
        # PROTECTED REGION ID(CspMasterLeafNode.test_storageLoggingLevel) ENABLED START #
        self.device.storageLoggingLevel
        # PROTECTED REGION END #    //  CspMasterLeafNode.test_storageLoggingLevel

    def test_healthState(self):
        """Test for healthState"""
        # PROTECTED REGION ID(CspMasterLeafNode.test_healthState) ENABLED START #
        self.device.healthState
        # PROTECTED REGION END #    //  CspMasterLeafNode.test_healthState

    def test_adminMode(self):
        """Test for adminMode"""
        # PROTECTED REGION ID(CspMasterLeafNode.test_adminMode) ENABLED START #
        self.device.adminMode
        # PROTECTED REGION END #    //  CspMasterLeafNode.test_adminMode

    def test_controlMode(self):
        """Test for controlMode"""
        # PROTECTED REGION ID(CspMasterLeafNode.test_controlMode) ENABLED START #
        self.device.controlMode
        # PROTECTED REGION END #    //  CspMasterLeafNode.test_controlMode

    def test_simulationMode(self):
        """Test for simulationMode"""
        # PROTECTED REGION ID(CspMasterLeafNode.test_simulationMode) ENABLED START #
        self.device.simulationMode
        # PROTECTED REGION END #    //  CspMasterLeafNode.test_simulationMode

    def test_testMode(self):
        """Test for testMode"""
        # PROTECTED REGION ID(CspMasterLeafNode.test_testMode) ENABLED START #
        self.device.testMode
        # PROTECTED REGION END #    //  CspMasterLeafNode.test_testMode

    def test_activityMessage(self):
        """Test for activityMessage"""
        # PROTECTED REGION ID(CspMasterLeafNode.test_activityMessage) ENABLED START #
        self.device.activityMessage
        # PROTECTED REGION END #    //  CspMasterLeafNode.test_activityMessage


# Main execution
if __name__ == "__main__":
    main()
