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

file_path = os.path.dirname(os.path.abspath(__file__))
module_path = os.path.abspath(os.path.join(file_path, os.pardir)) + "/CspMasterLeafNode"
sys.path.insert(0, module_path)

path = os.path.join(os.path.dirname(__file__), os.pardir)
sys.path.insert(0, os.path.abspath(path))

# Imports
import tango
from tango import DevState, EventType
from CspMasterLeafNode.CspMasterLeafNode import CspMasterLeafNode
import CONST
import pytest

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

class TestCspMasterLeafNode(object):
    """Test case for packet generation."""
    # PROTECTED REGION ID(CspMasterLeafNode.test_additionnal_import) ENABLED START #
    # PROTECTED REGION END #    //  CspMasterLeafNode.test_additionnal_import
    device = CspMasterLeafNode
    properties = {'SkaLevel': '4', 'GroupDefinitions': '', 'CentralLoggingTarget': '',
                  'ElementLoggingTarget': '', 'StorageLoggingTarget': 'localhost', 'CspMasterFQDN': 'tango://theta:10000/csp/master/1',
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

    def test_State(self, tango_context):
        """Test for State"""
        # PROTECTED REGION ID(CspMasterLeafNode.test_State) ENABLED START #
        assert tango_context.device.State() == DevState.ALARM
        # PROTECTED REGION END #    //  CspMasterLeafNode.test_State

    def test_Status(self, tango_context):
        """Test for Status"""
        # PROTECTED REGION ID(CspMasterLeafNode.test_Status) ENABLED START #
        print("tango_context.device.Status()", tango_context.device.Status())
        assert CONST.STR_DEV_ALARM in tango_context.device.Status()
        # PROTECTED REGION END #    //  CspMasterLeafNode.test_Status

    def test_GetVersionInfo(self):
        """Test for GetVersionInfo"""
        # PROTECTED REGION ID(CspMasterLeafNode.test_GetVersionInfo) ENABLED START #
        # PROTECTED REGION END #    //  CspMasterLeafNode.test_GetVersionInfo

    def test_Reset(self, tango_context):
        """Test for Reset"""
        # PROTECTED REGION ID(CspMasterLeafNode.test_Reset) ENABLED START #
        assert tango_context.device.Reset() == None
        # PROTECTED REGION END #    //  CspMasterLeafNode.test_Reset

    def test_On(self, tango_context):
        """Test for On"""
        # PROTECTED REGION ID(CspMasterLeafNode.test_On) ENABLED START #
        tango_context.device.On([])
        assert (CONST.ERR_INVOKING_CMD in tango_context.device.activityMessage) or (
                CONST.STR_CSP_PSS_HEALTH_UNKNOWN in tango_context.device.activityMessage)
        # PROTECTED REGION END #    //  CspMasterLeafNode.test_On

    def test_On_invalid_argument(self, tango_context):
        """Test for On"""
        tango_context.device.On(["a/b/c"])
        assert (CONST.ERR_INVOKING_CMD in tango_context.device.activityMessage) or (
                CONST.STR_CSP_PSS_HEALTH_UNKNOWN in tango_context.device.activityMessage)
    def test_Off(self, tango_context):
        """Test for Off"""
        # PROTECTED REGION ID(CspMasterLeafNode.test_Off) ENABLED START #
        tango_context.device.Off([])
        assert 1
        # PROTECTED REGION END #    //  CspMasterLeafNode.test_Off

    def test_Standby(self, tango_context):
        """Test for Standby"""
        # PROTECTED REGION ID(CspMasterLeafNode.test_Standby) ENABLED START #
        tango_context.device.Standby([])
        assert 1
        # PROTECTED REGION END #    //  CspMasterLeafNode.test_Standby

    def test_SetCbfAdminMode(self, tango_context):
        """Test for SetCbfAdminMode"""
        # PROTECTED REGION ID(CspMasterLeafNode.test_SetCbfAdminMode) ENABLED START #
        #tango_context.device.test_SetCbfAdminMode("ONLINE")
        assert 1
        # PROTECTED REGION END #    //  CspMasterLeafNode.test_SetCbfAdminMode

    def test_SetPssAdminMode(self, tango_context):
        """Test for SetPssAdminMode"""
        # PROTECTED REGION ID(CspMasterLeafNode.test_SetPssAdminMode) ENABLED START #
        #tango_context.device.test_SetPssAdminMode("ONLINE")
        assert 1
        # PROTECTED REGION END #    //  CspMasterLeafNode.test_SetPssAdminMode

    def test_SetPstAdminMode(self, tango_context):
        """Test for SetPstAdminMode"""
        # PROTECTED REGION ID(CspMasterLeafNode.test_SetPstAdminMode) ENABLED START #
        #tango_context.device.test_SetPstAdminMode(0)
        assert 1
        # PROTECTED REGION END #    //  CspMasterLeafNode.test_SetPstAdminMode

    def test_buildState(self, tango_context):
        """Test for buildState"""
        # PROTECTED REGION ID(CspMasterLeafNode.test_buildState) ENABLED START #
        assert tango_context.device.buildState == (
            "lmcbaseclasses, 0.1.3, A set of generic base devices for SKA Telescope.")
        # PROTECTED REGION END #    //  CspMasterLeafNode.test_buildState

    def test_versionId(self, tango_context):
        """Test for versionId"""
        # PROTECTED REGION ID(CspMasterLeafNode.test_versionId) ENABLED START #
        assert tango_context.device.versionId == "0.1.3"
        # PROTECTED REGION END #    //  CspMasterLeafNode.test_versionId

    def test_centralLoggingLevel(self, tango_context):
        """Test for centralLoggingLevel"""
        # PROTECTED REGION ID(CspMasterLeafNode.test_centralLoggingLevel) ENABLED START #
        tango_context.device.centralLoggingLevel = int(tango.LogLevel.LOG_DEBUG)
        assert tango_context.device.centralLoggingLevel == int(tango.LogLevel.LOG_DEBUG)
        # PROTECTED REGION END #    //  CspMasterLeafNode.test_centralLoggingLevel

    def test_elementLoggingLevel(self, tango_context):
        """Test for elementLoggingLevel"""
        # PROTECTED REGION ID(CspMasterLeafNode.test_elementLoggingLevel) ENABLED START #
        tango_context.device.elementLoggingLevel = int(tango.LogLevel.LOG_DEBUG)
        assert tango_context.device.elementLoggingLevel == int(tango.LogLevel.LOG_DEBUG)
        # PROTECTED REGION END #    //  CspMasterLeafNode.test_elementLoggingLevel

    def test_storageLoggingLevel(self, tango_context):
        """Test for storageLoggingLevel"""
        # PROTECTED REGION ID(CspMasterLeafNode.test_storageLoggingLevel) ENABLED START #
        tango_context.device.storageLoggingLevel = int(tango.LogLevel.LOG_DEBUG)
        assert tango_context.device.storageLoggingLevel == int(tango.LogLevel.LOG_DEBUG)
        # PROTECTED REGION END #    //  CspMasterLeafNode.test_storageLoggingLevel

    def test_healthState(self, tango_context):
        """Test for healthState"""
        # PROTECTED REGION ID(CspMasterLeafNode.test_healthState) ENABLED START #
        assert tango_context.device.healthState == 0
        # PROTECTED REGION END #    //  CspMasterLeafNode.test_healthState

    def test_adminMode(self, tango_context):
        """Test for adminMode"""
        # PROTECTED REGION ID(CspMasterLeafNode.test_adminMode) ENABLED START #
        assert tango_context.device.adminMode == 0
        # PROTECTED REGION END #    //  CspMasterLeafNode.test_adminMode

    def test_controlMode(self, tango_context):
        """Test for controlMode"""
        # PROTECTED REGION ID(CspMasterLeafNode.test_controlMode) ENABLED START #
        control_mode = 0
        tango_context.device.controlMode = control_mode
        assert tango_context.device.controlMode == control_mode
        # PROTECTED REGION END #    //  CspMasterLeafNode.test_controlMode

    def test_simulationMode(self, tango_context):
        """Test for simulationMode"""
        # PROTECTED REGION ID(CspMasterLeafNode.test_simulationMode) ENABLED START #
        simulation_mode = 0
        tango_context.device.simulationMode = simulation_mode
        assert tango_context.device.simulationMode == simulation_mode
        # PROTECTED REGION END #    //  CspMasterLeafNode.test_simulationMode

    def test_testMode(self, tango_context):
        """Test for testMode"""
        # PROTECTED REGION ID(CspMasterLeafNode.test_testMode) ENABLED START #
        test_mode = CONST.STR_FALSE
        tango_context.device.testMode = test_mode
        assert tango_context.device.testMode == test_mode
        # PROTECTED REGION END #    //  CspMasterLeafNode.test_testMode

    def test_activityMessage(self):
        """Test for activityMessage"""
        # PROTECTED REGION ID(CspMasterLeafNode.test_activityMessage) ENABLED START #
        # PROTECTED REGION END #    //  CspMasterLeafNode.test_activityMessage


# Main execution
if __name__ == "__main__":
    main()
