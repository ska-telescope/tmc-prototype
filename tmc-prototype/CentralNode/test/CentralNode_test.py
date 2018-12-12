#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of the CentralNode project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.
"""Contain the tests for the CentralNode."""

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
from CentralNode import CentralNode

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
class CentralNodeDeviceTestCase(DeviceTestCase):
    """Test case for packet generation."""
    # PROTECTED REGION ID(CentralNode.test_additionnal_import) ENABLED START #
    # PROTECTED REGION END #    //  CentralNode.test_additionnal_import
    device = CentralNode
    properties = {'SkaLevel': '4', 'MetricList': 'healthState', 'GroupDefinitions': '', 'CentralLoggingTarget': '', 'ElementLoggingTarget': '', 'StorageLoggingTarget': 'localhost', 'CentralAlarmHandler': '', 'TMAlarmHandler': '', 'TMMidSubarrayNodes': 'ska_mid/tm_subarray_node/1', 'NumDishes': '4', 'DishLeafNodePrefix': 'ska_mid/tm_leaf_node/d', 
                  }
    empty = None  # Should be []

    @classmethod
    def mocking(cls):
        """Mock external libraries."""
        # Example : Mock numpy
        # cls.numpy = CentralNode.numpy = MagicMock()
        # PROTECTED REGION ID(CentralNode.test_mocking) ENABLED START #
        # PROTECTED REGION END #    //  CentralNode.test_mocking

    def test_properties(self):
        # test the properties
        # PROTECTED REGION ID(CentralNode.test_properties) ENABLED START #
        # PROTECTED REGION END #    //  CentralNode.test_properties
        pass

    def test_State(self):
        """Test for State"""
        # PROTECTED REGION ID(CentralNode.test_State) ENABLED START #
        self.device.State()
        # PROTECTED REGION END #    //  CentralNode.test_State

    def test_Status(self):
        """Test for Status"""
        # PROTECTED REGION ID(CentralNode.test_Status) ENABLED START #
        self.device.Status()
        # PROTECTED REGION END #    //  CentralNode.test_Status

    def test_GetMetrics(self):
        """Test for GetMetrics"""
        # PROTECTED REGION ID(CentralNode.test_GetMetrics) ENABLED START #
        self.device.GetMetrics()
        # PROTECTED REGION END #    //  CentralNode.test_GetMetrics

    def test_ToJson(self):
        """Test for ToJson"""
        # PROTECTED REGION ID(CentralNode.test_ToJson) ENABLED START #
        self.device.ToJson("")
        # PROTECTED REGION END #    //  CentralNode.test_ToJson

    def test_GetVersionInfo(self):
        """Test for GetVersionInfo"""
        # PROTECTED REGION ID(CentralNode.test_GetVersionInfo) ENABLED START #
        self.device.GetVersionInfo()
        # PROTECTED REGION END #    //  CentralNode.test_GetVersionInfo

    def test_Reset(self):
        """Test for Reset"""
        # PROTECTED REGION ID(CentralNode.test_Reset) ENABLED START #
        self.device.Reset()
        # PROTECTED REGION END #    //  CentralNode.test_Reset

    def test_StowAntennas(self):
        """Test for StowAntennas"""
        # PROTECTED REGION ID(CentralNode.test_StowAntennas) ENABLED START #
        self.device.StowAntennas([""])
        # PROTECTED REGION END #    //  CentralNode.test_StowAntennas

    def test_StandByTelescope(self):
        """Test for StandByTelescope"""
        # PROTECTED REGION ID(CentralNode.test_StandByTelescope) ENABLED START #
        self.device.StandByTelescope()
        # PROTECTED REGION END #    //  CentralNode.test_StandByTelescope

    def test_StartUpTelescope(self):
        """Test for StartUpTelescope"""
        # PROTECTED REGION ID(CentralNode.test_StartUpTelescope) ENABLED START #
        self.device.StartUpTelescope()
        # PROTECTED REGION END #    //  CentralNode.test_StartUpTelescope

    def test_buildState(self):
        """Test for buildState"""
        # PROTECTED REGION ID(CentralNode.test_buildState) ENABLED START #
        self.device.buildState
        # PROTECTED REGION END #    //  CentralNode.test_buildState

    def test_versionId(self):
        """Test for versionId"""
        # PROTECTED REGION ID(CentralNode.test_versionId) ENABLED START #
        self.device.versionId
        # PROTECTED REGION END #    //  CentralNode.test_versionId

    def test_centralLoggingLevel(self):
        """Test for centralLoggingLevel"""
        # PROTECTED REGION ID(CentralNode.test_centralLoggingLevel) ENABLED START #
        self.device.centralLoggingLevel
        # PROTECTED REGION END #    //  CentralNode.test_centralLoggingLevel

    def test_elementLoggingLevel(self):
        """Test for elementLoggingLevel"""
        # PROTECTED REGION ID(CentralNode.test_elementLoggingLevel) ENABLED START #
        self.device.elementLoggingLevel
        # PROTECTED REGION END #    //  CentralNode.test_elementLoggingLevel

    def test_storageLoggingLevel(self):
        """Test for storageLoggingLevel"""
        # PROTECTED REGION ID(CentralNode.test_storageLoggingLevel) ENABLED START #
        self.device.storageLoggingLevel
        # PROTECTED REGION END #    //  CentralNode.test_storageLoggingLevel

    def test_healthState(self):
        """Test for healthState"""
        # PROTECTED REGION ID(CentralNode.test_healthState) ENABLED START #
        self.device.healthState
        # PROTECTED REGION END #    //  CentralNode.test_healthState

    def test_adminMode(self):
        """Test for adminMode"""
        # PROTECTED REGION ID(CentralNode.test_adminMode) ENABLED START #
        self.device.adminMode
        # PROTECTED REGION END #    //  CentralNode.test_adminMode

    def test_controlMode(self):
        """Test for controlMode"""
        # PROTECTED REGION ID(CentralNode.test_controlMode) ENABLED START #
        self.device.controlMode
        # PROTECTED REGION END #    //  CentralNode.test_controlMode

    def test_simulationMode(self):
        """Test for simulationMode"""
        # PROTECTED REGION ID(CentralNode.test_simulationMode) ENABLED START #
        self.device.simulationMode
        # PROTECTED REGION END #    //  CentralNode.test_simulationMode

    def test_testMode(self):
        """Test for testMode"""
        # PROTECTED REGION ID(CentralNode.test_testMode) ENABLED START #
        self.device.testMode
        # PROTECTED REGION END #    //  CentralNode.test_testMode

    def test_telescopeHealthState(self):
        """Test for telescopeHealthState"""
        # PROTECTED REGION ID(CentralNode.test_telescopeHealthState) ENABLED START #
        self.device.telescopeHealthState
        # PROTECTED REGION END #    //  CentralNode.test_telescopeHealthState

    def test_subarray1HealthState(self):
        """Test for subarray1HealthState"""
        # PROTECTED REGION ID(CentralNode.test_subarray1HealthState) ENABLED START #
        self.device.subarray1HealthState
        # PROTECTED REGION END #    //  CentralNode.test_subarray1HealthState

    def test_subarray2HealthState(self):
        """Test for subarray2HealthState"""
        # PROTECTED REGION ID(CentralNode.test_subarray2HealthState) ENABLED START #
        self.device.subarray2HealthState
        # PROTECTED REGION END #    //  CentralNode.test_subarray2HealthState

    def test_activityMessage(self):
        """Test for activityMessage"""
        # PROTECTED REGION ID(CentralNode.test_activityMessage) ENABLED START #
        self.device.activityMessage
        # PROTECTED REGION END #    //  CentralNode.test_activityMessage


# Main execution
if __name__ == "__main__":
    main()
