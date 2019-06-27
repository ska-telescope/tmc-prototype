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
import time

file_path = os.path.dirname(os.path.abspath(__file__))
module_path = os.path.abspath(os.path.join(file_path, os.pardir)) + "/SdpSubarrayLeafNode"
sys.path.insert(0, module_path)

path = os.path.join(os.path.dirname(__file__), os.pardir)
sys.path.insert(0, os.path.abspath(path))

# Imports
import tango
from tango import DevState, EventType, DeviceProxy
from SdpSubarrayLeafNode.SdpSubarrayLeafNode import SdpSubarrayLeafNode
# import CONST
import pytest
import json

# Imports
from time import sleep
from mock import MagicMock
# from PyTango import DevFailed, DevState
# from devicetest import DeviceTestCase, main


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

class TestSdpSubarrayLeafNode(object):
    """Test case for packet generation."""
    # PROTECTED REGION ID(SdpSubarrayLeafNode.test_additionnal_import) ENABLED START #
    # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_additionnal_import
    device = SdpSubarrayLeafNode
    properties = {'SkaLevel': '4', 'GroupDefinitions': '', 'CentralLoggingTarget': '',
                  'ElementLoggingTarget': '', 'StorageLoggingTarget': 'localhost',
                  }
    empty = None  # Should be []

    @classmethod
    def mocking(cls):
        """Mock external libraries."""
        # Example : Mock numpy
        # cls.numpy = SdpSubarrayLeafNode.numpy = MagicMock()
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_mocking) ENABLED START #
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_mocking

    def test_properties(self, tango_context):
        # test the properties
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_properties) ENABLED START #
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_properties
        pass

    def test_State(self, tango_context):
        """Test for State"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_State) ENABLED START #
        self.device.State()
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_State

    def test_Status(self, tango_context):
        """Test for Status"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_Status) ENABLED START #
        self.device.Status()
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_Status

    def test_GetVersionInfo(self, tango_context):
        """Test for GetVersionInfo"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_GetVersionInfo) ENABLED START #
        self.device.GetVersionInfo()
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_GetVersionInfo

    def test_Reset(self, tango_context):
        """Test for Reset"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_Reset) ENABLED START #
        self.device.Reset()
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_Reset

    def test_ReleaseResource(self, tango_context):
        """Test for ReleaseResource"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_ReleaseResource) ENABLED START #
        self.device.ReleaseResource()
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_ReleaseResource

    def test_AssignResource(self, tango_context):
        """Test for AssignResource"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_AssignResource) ENABLED START #
        self.device.AssignResource("")
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_AssignResource

    def test_Configure(self, tango_context):
        """Test for Configure"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_Configure) ENABLED START #
        self.device.Configure("")
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_Configure

    def test_StartScan(self, tango_context):
        """Test for StartScan"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_StartScan) ENABLED START #
        self.device.StartScan("")
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_StartScan

    def test_StopScan(self, tango_context):
        """Test for StopScan"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_StopScan) ENABLED START #
        self.device.StopScan()
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_StopScan

    def test_buildState(self, tango_context):
        """Test for buildState"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_buildState) ENABLED START #
        self.device.buildState
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_buildState

    def test_versionId(self, tango_context):
        """Test for versionId"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_versionId) ENABLED START #
        # self.device.versionId
        assert tango_context.device.versionId == "0.1.3"
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_versionId

    def test_centralLoggingLevel(self, tango_context):
        """Test for centralLoggingLevel"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_centralLoggingLevel) ENABLED START #
        self.device.centralLoggingLevel
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_centralLoggingLevel

    def test_elementLoggingLevel(self, tango_context):
        """Test for elementLoggingLevel"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_elementLoggingLevel) ENABLED START #
        self.device.elementLoggingLevel
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_elementLoggingLevel

    def test_storageLoggingLevel(self, tango_context):
        """Test for storageLoggingLevel"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_storageLoggingLevel) ENABLED START #
        self.device.storageLoggingLevel
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_storageLoggingLevel

    def test_healthState(self, tango_context):
        """Test for healthState"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_healthState) ENABLED START #
        self.device.healthState
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_healthState

    def test_adminMode(self, tango_context):
        """Test for adminMode"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_adminMode) ENABLED START #
        self.device.adminMode
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_adminMode

    def test_controlMode(self, tango_context):
        """Test for controlMode"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_controlMode) ENABLED START #
        self.device.controlMode
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_controlMode

    def test_simulationMode(self, tango_context):
        """Test for simulationMode"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_simulationMode) ENABLED START #
        self.device.simulationMode
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_simulationMode

    def test_testMode(self, tango_context):
        """Test for testMode"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_testMode) ENABLED START #
        self.device.testMode
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_testMode

    def test_ActiveProcessingBlocks(self, tango_context):
        """Test for ActiveProcessingBlocks"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_ActiveProcessingBlocks) ENABLED START #
        assert tango_context.device.ActiveProcessingBlocks == "1"
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_ActiveProcessingBlocks

    def test_ReceiveAddresses(self, tango_context):
        """Test for ReceiveAddresses"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_ReceiveAddresses) ENABLED START #
        self.device.ReceiveAddresses
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_ReceiveAddresses

