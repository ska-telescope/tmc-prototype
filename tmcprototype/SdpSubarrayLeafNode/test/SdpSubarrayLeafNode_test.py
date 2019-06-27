#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of the SdpSubarrayLeafNode project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.
"""Contain the tests for the SdpSubarrayLeafNode."""

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
from SdpSubarrayLeafNode import SdpSubarrayLeafNode

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
class SdpSubarrayLeafNodeDeviceTestCase(DeviceTestCase):
    """Test case for packet generation."""
    # PROTECTED REGION ID(SdpSubarrayLeafNode.test_additionnal_import) ENABLED START #
    # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_additionnal_import
    device = SdpSubarrayLeafNode
    properties = {'SkaLevel': '4', 'GroupDefinitions': '', 'CentralLoggingTarget': '', 'ElementLoggingTarget': '', 'StorageLoggingTarget': 'localhost', 'SdpSubarrayNodeFQDN': 'mid-sdp/elt/subarray_1', 
                  }
    empty = None  # Should be []

    @classmethod
    def mocking(cls):
        """Mock external libraries."""
        # Example : Mock numpy
        # cls.numpy = SdpSubarrayLeafNode.numpy = MagicMock()
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_mocking) ENABLED START #
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_mocking

    def test_properties(self):
        # test the properties
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_properties) ENABLED START #
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_properties
        pass

    def test_State(self):
        """Test for State"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_State) ENABLED START #
        self.device.State()
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_State

    def test_Status(self):
        """Test for Status"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_Status) ENABLED START #
        self.device.Status()
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_Status

    def test_GetVersionInfo(self):
        """Test for GetVersionInfo"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_GetVersionInfo) ENABLED START #
        self.device.GetVersionInfo()
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_GetVersionInfo

    def test_Reset(self):
        """Test for Reset"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_Reset) ENABLED START #
        self.device.Reset()
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_Reset

    def test_ReleaseResources(self):
        """Test for ReleaseResources"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_ReleaseResources) ENABLED START #
        self.device.ReleaseResources("")
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_ReleaseResources

    def test_AssignResources(self):
        """Test for AssignResources"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_AssignResources) ENABLED START #
        self.device.AssignResources("")
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_AssignResources

    def test_Configure(self):
        """Test for Configure"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_Configure) ENABLED START #
        self.device.Configure("")
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_Configure

    def test_Scan(self):
        """Test for Scan"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_Scan) ENABLED START #
        self.device.Scan()
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_Scan

    def test_EndScan(self):
        """Test for EndScan"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_EndScan) ENABLED START #
        self.device.EndScan()
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_EndScan

    def test_EndSB(self):
        """Test for EndSB"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_EndSB) ENABLED START #
        self.device.EndSB()
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_EndSB

    def test_Abort(self):
        """Test for Abort"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_Abort) ENABLED START #
        self.device.Abort()
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_Abort

    def test_buildState(self):
        """Test for buildState"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_buildState) ENABLED START #
        self.device.buildState
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_buildState

    def test_versionId(self):
        """Test for versionId"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_versionId) ENABLED START #
        # self.device.versionId
        assert tango_context.device.versionId == "0.1.3"
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_versionId

    def test_centralLoggingLevel(self):
        """Test for centralLoggingLevel"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_centralLoggingLevel) ENABLED START #
        self.device.centralLoggingLevel
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_centralLoggingLevel

    def test_elementLoggingLevel(self):
        """Test for elementLoggingLevel"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_elementLoggingLevel) ENABLED START #
        self.device.elementLoggingLevel
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_elementLoggingLevel

    def test_storageLoggingLevel(self):
        """Test for storageLoggingLevel"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_storageLoggingLevel) ENABLED START #
        self.device.storageLoggingLevel
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_storageLoggingLevel

    def test_healthState(self):
        """Test for healthState"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_healthState) ENABLED START #
        self.device.healthState
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_healthState

    def test_adminMode(self):
        """Test for adminMode"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_adminMode) ENABLED START #
        self.device.adminMode
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_adminMode

    def test_controlMode(self):
        """Test for controlMode"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_controlMode) ENABLED START #
        self.device.controlMode
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_controlMode

    def test_simulationMode(self):
        """Test for simulationMode"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_simulationMode) ENABLED START #
        self.device.simulationMode
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_simulationMode

    def test_testMode(self):
        """Test for testMode"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_testMode) ENABLED START #
        self.device.testMode
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_testMode

    def test_receiveAddresses(self):
        """Test for receiveAddresses"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_receiveAddresses) ENABLED START #
        self.device.receiveAddresses
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_receiveAddresses

    def test_sdpSubarrayHealthState(self):
        """Test for sdpSubarrayHealthState"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_sdpSubarrayHealthState) ENABLED START #
        self.device.sdpSubarrayHealthState
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_sdpSubarrayHealthState

    def test_activityMessage(self):
        """Test for activityMessage"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_activityMessage) ENABLED START #
        self.device.activityMessage
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_activityMessage

    def test_activeProcessingBlocks(self):
        """Test for activeProcessingBlocks"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_activeProcessingBlocks) ENABLED START #
        self.device.activeProcessingBlocks
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_activeProcessingBlocks


# Main execution
if __name__ == "__main__":
    main()
