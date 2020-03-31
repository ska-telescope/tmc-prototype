#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of the CspMasterLeafNode project
#
#
#
# Distributed under the terms of the BSD-3-Clause license.
# See LICENSE.txt for more info.
"""Contain the tests for the CspMasterLeafNode."""

# Imports
import tango
from tango import DevState
from cspmasterleafnode import CspMasterLeafNode, CONST
from skabase.SKABaseDevice import TangoLoggingLevel
from skabase.control_model import HealthState, AdminMode, TestMode, SimulationMode, ControlMode
import pytest
import time

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
@pytest.mark.usefixtures("tango_context","create_cspmaster_proxy")

class TestCspMasterLeafNode(object):
    """Test case for packet generation."""
    # PROTECTED REGION ID(CspMasterLeafNode.test_additionnal_import) ENABLED START #
    # PROTECTED REGION END #    //  CspMasterLeafNode.test_additionnal_import
    device = CspMasterLeafNode
    properties = {'SkaLevel': '3', 'GroupDefinitions': '',
                  'CspMasterFQDN': 'mid_csp/elt/master',
                  'LoggingLevelDefault': '4', 'LoggingTargetsDefault': 'console::cout'
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

    def test_On_invalid_argument(self, tango_context, create_cspmaster_proxy):
        """Test for On"""
        tango_context.device.On(["a/b/c"])
        time.sleep(1)
        assert create_cspmaster_proxy.State() == DevState.STANDBY

    def test_buildState(self, tango_context):
        """Test for buildState"""
        # PROTECTED REGION ID(CspMasterLeafNode.test_buildState) ENABLED START #
        assert tango_context.device.buildState == (
            "lmcbaseclasses, 0.4.1, A set of generic base devices for SKA Telescope.")
        # PROTECTED REGION END #    //  CspMasterLeafNode.test_buildState

    def test_versionId(self, tango_context):
        """Test for versionId"""
        # PROTECTED REGION ID(CspMasterLeafNode.test_versionId) ENABLED START #
        assert tango_context.device.versionId == "0.4.1"
        # PROTECTED REGION END #    //  CspMasterLeafNode.test_versionId

    def test_healthState(self, tango_context):
        """Test for healthState"""
        # PROTECTED REGION ID(CspMasterLeafNode.test_healthState) ENABLED START #
        assert tango_context.device.healthState == HealthState.OK
        # PROTECTED REGION END #    //  CspMasterLeafNode.test_healthState

    def test_adminMode(self, tango_context):
        """Test for adminMode"""
        # PROTECTED REGION ID(CspMasterLeafNode.test_adminMode) ENABLED START #
        assert tango_context.device.adminMode == AdminMode.ONLINE
        # PROTECTED REGION END #    //  CspMasterLeafNode.test_adminMode

    def test_controlMode(self, tango_context):
        """Test for controlMode"""
        # PROTECTED REGION ID(CspMasterLeafNode.test_controlMode) ENABLED START #
        control_mode = ControlMode.REMOTE
        tango_context.device.controlMode = control_mode
        assert tango_context.device.controlMode == control_mode
        # PROTECTED REGION END #    //  CspMasterLeafNode.test_controlMode

    def test_simulationMode(self, tango_context):
        """Test for simulationMode"""
        # PROTECTED REGION ID(CspMasterLeafNode.test_simulationMode) ENABLED START #
        simulation_mode = SimulationMode.FALSE
        tango_context.device.simulationMode = simulation_mode
        assert tango_context.device.simulationMode == simulation_mode
        # PROTECTED REGION END #    //  CspMasterLeafNode.test_simulationMode

    def test_testMode(self, tango_context):
        """Test for testMode"""
        # PROTECTED REGION ID(CspMasterLeafNode.test_testMode) ENABLED START #
        test_mode = TestMode.NONE
        tango_context.device.testMode = test_mode
        assert tango_context.device.testMode == test_mode
        # PROTECTED REGION END #    //  CspMasterLeafNode.test_testMode

    def test_activityMessage(self, tango_context):
        """Test for activityMessage"""
        # PROTECTED REGION ID(CspMasterLeafNode.test_activityMessage) ENABLED START #
        tango_context.device.activityMessage = "text"
        assert  tango_context.device.activityMessage == "text"
        # PROTECTED REGION END #    //  CspMasterLeafNode.test_activityMessage

    def test_On(self, tango_context, create_cspmaster_proxy):
        """Test for On"""
        # PROTECTED REGION ID(CspMasterLeafNode.test_On) ENABLED START #
        tango_context.device.On([])
        time.sleep(1)
        # assert CONST.STR_INVOKE_SUCCESS in tango_context.device.activityMessage
        assert create_cspmaster_proxy.State() == DevState.ON
        # PROTECTED REGION END #    //  CspMasterLeafNode.test_On

    def test_Standby(self, tango_context, create_cspmaster_proxy):
        """Test for Standby"""
        # PROTECTED REGION ID(CspMasterLeafNode.test_Standby) ENABLED START #
        time.sleep(1)
        tango_context.device.Standby([])
        time.sleep(1)
        # assert CONST.STR_INVOKE_SUCCESS in tango_context.device.activityMessage
        assert create_cspmaster_proxy.State() == DevState.STANDBY
        time.sleep(1)
        tango_context.device.On([])
        # PROTECTED REGION END #    //  CspMasterLeafNode.test_Standby

    def test_Off(self, tango_context):
        """Test for Off"""
        # PROTECTED REGION ID(CspMasterLeafNode.test_Off) ENABLED START #
        assert 1
        # PROTECTED REGION END #    //  CspMasterLeafNode.test_Off

    def test_loggingLevel(self, tango_context):
        """Test for loggingLevel"""
        # PROTECTED REGION ID(DishMaster.test_loggingLevel) ENABLED START #
        tango_context.device.loggingLevel = TangoLoggingLevel.INFO
        assert tango_context.device.loggingLevel == TangoLoggingLevel.INFO
        # PROTECTED REGION END #    //  DishMaster.test_loggingLevel

    def test_loggingTargets(self, tango_context):
        """Test for loggingTargets"""
        # PROTECTED REGION ID(DishMaster.test_loggingLevel) ENABLED START #
        tango_context.device.loggingTargets = ['console::cout']
        assert 'console::cout' in tango_context.device.loggingTargets
        # PROTECTED REGION END #    //  DishMaster.test_loggingTargets

