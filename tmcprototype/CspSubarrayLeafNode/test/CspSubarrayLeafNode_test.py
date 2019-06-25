#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of the CspSubarrayLeafNode project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.
"""Contain the tests for the ."""

# Path
import sys
import os
import time
import pytest
import json

file_path = os.path.dirname(os.path.abspath(__file__))
module_path = os.path.abspath(os.path.join(file_path, os.pardir)) + "/CspSubarrayLeafNode"
sys.path.insert(0, module_path)

path = os.path.join(os.path.dirname(__file__), os.pardir)
sys.path.insert(0, os.path.abspath(path))

# Imports
from time import sleep
from mock import MagicMock
from PyTango import DevFailed, DevState
#from devicetest import DeviceTestCase, main
from CspSubarrayLeafNode.CspSubarrayLeafNode import CspSubarrayLeafNode

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

class TestCspSubarrayLeafNode(object):
    """Test case for packet generation."""
    # PROTECTED REGION ID(CspSubarrayLeafNode.test_additionnal_import) ENABLED START #
    # PROTECTED REGION END #    //  CspSubarrayLeafNode.test_additionnal_import
    device = CspSubarrayLeafNode
    properties = {'SkaLevel': '4', 'GroupDefinitions': '', 'CentralLoggingTarget': '', 'ElementLoggingTarget': '', 'StorageLoggingTarget': 'localhost', 'SkaLevel': '3', 'CspSubarrayNodeFQDN': 'mid-csp/elt/subarray01', 
                  }
    empty = None  # Should be []

    @classmethod
    def mocking(cls):
        """Mock external libraries."""
        # Example : Mock numpy
        # cls.numpy = CspSubarrayLeafNode.numpy = MagicMock()
        # PROTECTED REGION ID(CspSubarrayLeafNode.test_mocking) ENABLED START #
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.test_mocking

    def test_properties(self):
        # test the properties
        # PROTECTED REGION ID(CspSubarrayLeafNode.test_properties) ENABLED START #
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.test_properties
        pass

    def test_State(self):
        """Test for State"""
        # PROTECTED REGION ID(CspSubarrayLeafNode.test_State) ENABLED START #
        self.device.State()
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.test_State

    def test_Status(self):
        """Test for Status"""
        # PROTECTED REGION ID(CspSubarrayLeafNode.test_Status) ENABLED START #
        self.device.Status()
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.test_Status

    def test_GetVersionInfo(self):
        """Test for GetVersionInfo"""
        # PROTECTED REGION ID(CspSubarrayLeafNode.test_GetVersionInfo) ENABLED START #
        self.device.GetVersionInfo()
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.test_GetVersionInfo

    def test_Reset(self):
        """Test for Reset"""
        # PROTECTED REGION ID(CspSubarrayLeafNode.test_Reset) ENABLED START #
        self.device.Reset()
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.test_Reset

    def test_ConfigureScan(self):
        """Test for ConfigureScan"""
        # PROTECTED REGION ID(CspSubarrayLeafNode.test_ConfigureScan) ENABLED START #
        self.device.ConfigureScan("")
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.test_ConfigureScan

    def test_StartScan(self):
        """Test for StartScan"""
        # PROTECTED REGION ID(CspSubarrayLeafNode.test_StartScan) ENABLED START #
        self.device.StartScan("")
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.test_StartScan

    def test_EndScan(self):
        """Test for EndScan"""
        # PROTECTED REGION ID(CspSubarrayLeafNode.test_EndScan) ENABLED START #
        self.device.EndScan("")
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.test_EndScan

    def test_ReleaseResources(self):
        """Test for ReleaseResources"""
        # PROTECTED REGION ID(CspSubarrayLeafNode.test_ReleaseResources) ENABLED START #
        self.device.ReleaseResources()
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.test_ReleaseResources

    def test_AssignResources(self):
        """Test for AssignResources"""
        # PROTECTED REGION ID(CspSubarrayLeafNode.test_AssignResources) ENABLED START #
        self.device.AssignResources([""])
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.test_AssignResources

    def test_buildState(self):
        """Test for buildState"""
        # PROTECTED REGION ID(CspSubarrayLeafNode.test_buildState) ENABLED START #
        self.device.buildState
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.test_buildState

    def test_versionId(self):
        """Test for versionId"""
        # PROTECTED REGION ID(CspSubarrayLeafNode.test_versionId) ENABLED START #
        self.device.versionId
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.test_versionId

    def test_centralLoggingLevel(self):
        """Test for centralLoggingLevel"""
        # PROTECTED REGION ID(CspSubarrayLeafNode.test_centralLoggingLevel) ENABLED START #
        self.device.centralLoggingLevel
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.test_centralLoggingLevel

    def test_elementLoggingLevel(self):
        """Test for elementLoggingLevel"""
        # PROTECTED REGION ID(CspSubarrayLeafNode.test_elementLoggingLevel) ENABLED START #
        self.device.elementLoggingLevel
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.test_elementLoggingLevel

    def test_storageLoggingLevel(self):
        """Test for storageLoggingLevel"""
        # PROTECTED REGION ID(CspSubarrayLeafNode.test_storageLoggingLevel) ENABLED START #
        self.device.storageLoggingLevel
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.test_storageLoggingLevel

    def test_healthState(self):
        """Test for healthState"""
        # PROTECTED REGION ID(CspSubarrayLeafNode.test_healthState) ENABLED START #
        self.device.healthState
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.test_healthState

    def test_adminMode(self):
        """Test for adminMode"""
        # PROTECTED REGION ID(CspSubarrayLeafNode.test_adminMode) ENABLED START #
        self.device.adminMode
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.test_adminMode

    def test_controlMode(self):
        """Test for controlMode"""
        # PROTECTED REGION ID(CspSubarrayLeafNode.test_controlMode) ENABLED START #
        self.device.controlMode
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.test_controlMode

    def test_simulationMode(self):
        """Test for simulationMode"""
        # PROTECTED REGION ID(CspSubarrayLeafNode.test_simulationMode) ENABLED START #
        self.device.simulationMode
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.test_simulationMode

    def test_testMode(self):
        """Test for testMode"""
        # PROTECTED REGION ID(CspSubarrayLeafNode.test_testMode) ENABLED START #
        self.device.testMode
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.test_testMode

    def test_state(self):
        """Test for state"""
        # PROTECTED REGION ID(CspSubarrayLeafNode.test_state) ENABLED START #
        self.device.state
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.test_state

    def test_delayModel(self):
        """Test for delayModel"""
        # PROTECTED REGION ID(CspSubarrayLeafNode.test_delayModel) ENABLED START #
        self.device.delayModel
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.test_delayModel

    def test_visDestinationAddress(self):
        """Test for visDestinationAddress"""
        # PROTECTED REGION ID(CspSubarrayLeafNode.test_visDestinationAddress) ENABLED START #
        self.device.visDestinationAddress
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.test_visDestinationAddress

    def test_CspSubarrayHealthState(self):
        """Test for CspSubarrayHealthState"""
        # PROTECTED REGION ID(CspSubarrayLeafNode.test_CspSubarrayHealthState) ENABLED START #
        self.device.CspSubarrayHealthState
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.test_CspSubarrayHealthState

    def test_versionInfo(self):
        """Test for versionInfo"""
        # PROTECTED REGION ID(CspSubarrayLeafNode.test_versionInfo) ENABLED START #
        self.device.versionInfo
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.test_versionInfo

    def test_activityMessage(self):
        """Test for activityMessage"""
        # PROTECTED REGION ID(CspSubarrayLeafNode.test_activityMessage) ENABLED START #
        self.device.activityMessage
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.test_activityMessage

    def test_opState(self):
        """Test for opState"""
        # PROTECTED REGION ID(CspSubarrayLeafNode.test_opState) ENABLED START #
        self.device.opState
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.test_opState


# Main execution
if __name__ == "__main__":
    main()
