#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of the SdpMasterLeafNode project
#
#
#
# Distributed under the terms of the BSD-3-Clause license.
# See LICENSE.txt for more info.
"""Contain the tests for the SdpMasterLeafNode."""

# Imports
from time import sleep
from mock import MagicMock
# from devicetest import DeviceTestCase, main
import tango
import pytest
import time
from tango import DevState, EventType, DeviceProxy
from sdpmasterleafnode import SdpMasterLeafNode, const
from ska.base.control_model import HealthState, AdminMode, TestMode, ControlMode, SimulationMode, LoggingLevel

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
@pytest.mark.usefixtures("tango_context")

class TestSdpMasterLeafNode(object):
    """Test case for packet generation."""
    # PROTECTED REGION ID(SdpMasterLeafNode.test_additionnal_import) ENABLED START #
    # PROTECTED REGION END #    //  SdpMasterLeafNode.test_additionnal_import
    device = SdpMasterLeafNode
    properties = {'SkaLevel': '4', 'GroupDefinitions': '',
                  'SdpMasterFQDN': 'mid_sdp/elt/master',
                  'LoggingLevelDefault': '4', 'LoggingTargetsDefault': 'console::cout'
                  }
    empty = None  # Should be []

    @classmethod
    def mocking(cls):
        """Mock external libraries."""
        # Example : Mock numpy
        # cls.numpy = SdpMasterLeafNode.numpy = MagicMock()
        # PROTECTED REGION ID(SdpMasterLeafNode.test_mocking) ENABLED START #
        # PROTECTED REGION END #    //  SdpMasterLeafNode.test_mocking

    def test_State(self, tango_context):
        # PROTECTED REGION ID(SdpMasterLeafNode.test_State) ENABLED START #
        """Test for State"""
        assert tango_context.device.State() == DevState.ALARM
        # PROTECTED REGION END #    //  SdpMasterLeafNode.test_State

    def test_Status(self, tango_context):
        """Test for Status"""
        # PROTECTED REGION ID(SdpMasterLeafNode.test_Status) ENABLED START #
        assert tango_context.device.Status() != const.STR_INIT_SUCCESS
        # PROTECTED REGION END #    //  SdpMasterLeafNode.test_Status

    def test_GetVersionInfo(self, tango_context):
        """Test for GetVersionInfo"""
        # PROTECTED REGION ID(SdpMasterLeafNode.test_GetVersionInfo) ENABLED START #
        assert tango_context.device.GetVersionInfo()
        # PROTECTED REGION END #    //  SdpMasterLeafNode.test_GetVersionInfo

    def test_Reset(self, tango_context):
        """Test for Reset"""
        # PROTECTED REGION ID(SdpMasterLeafNode.test_Reset) ENABLED START #
        assert tango_context.device.Reset() == None
        # PROTECTED REGION END #    //  SdpMasterLeafNode.test_Reset

    def test_On(self, tango_context, create_sdp_master_proxy):
        """Test for On"""
        # PROTECTED REGION ID(SdpMasterLeafNode.test_On) ENABLED START #
        tango_context.device.On()
        time.sleep(4)
        assert create_sdp_master_proxy.OperatingState == 1
        assert const.STR_INVOKE_SUCCESS in tango_context.device.activityMessage
        # PROTECTED REGION END #    //  SdpMasterLeafNode.test_On

    def test_Standby(self, tango_context, create_sdp_master_proxy):
        """Test for Standby"""
        # PROTECTED REGION ID(SdpMasterLeafNode.test_Standby) ENABLED START #
        tango_context.device.Standby()
        time.sleep(4)
        assert create_sdp_master_proxy.OperatingState == 3
        assert const.STR_INVOKE_SUCCESS in tango_context.device.activityMessage
        # PROTECTED REGION END #    //  SdpMasterLeafNode.test_Standby

    def test_buildState(self, tango_context):
        """Test for buildState"""
        # PROTECTED REGION ID(SdpMasterLeafNode.test_buildState) ENABLED START #
        assert tango_context.device.buildState == (
            "lmcbaseclasses, 0.5.1, A set of generic base devices for SKA Telescope.")
        # PROTECTED REGION END #    //  SdpMasterLeafNode.test_buildState

    def test_versionId(self, tango_context):
        """Test for versionId"""
        # PROTECTED REGION ID(SdpMasterLeafNode.test_versionId) ENABLED START #
        assert tango_context.device.versionId == '0.5.1'
        # PROTECTED REGION END #    //  SdpMasterLeafNode.test_versionId

    def test_healthState(self, tango_context):
        """Test for healthState"""
        # PROTECTED REGION ID(SdpMasterLeafNode.test_healthState) ENABLED START #
        assert tango_context.device.healthState == HealthState.OK
        # PROTECTED REGION END #    //  SdpMasterLeafNode.test_healthState

    def test_adminMode(self, tango_context):
        """Test for adminMode"""
        # PROTECTED REGION ID(SdpMasterLeafNode.test_adminMode) ENABLED START #
        assert tango_context.device.adminMode == AdminMode.ONLINE
        # PROTECTED REGION END #    //  SdpMasterLeafNode.test_adminMode

    def test_controlMode(self, tango_context):
        """Test for controlMode"""
        # PROTECTED REGION ID(SdpMasterLeafNode.test_controlMode) ENABLED START #
        control_mode = ControlMode.REMOTE
        tango_context.device.controlMode = control_mode
        assert tango_context.device.controlMode == control_mode
        # PROTECTED REGION END #    //  SdpMasterLeafNode.test_controlMode

    def test_simulationMode(self, tango_context):
        """Test for simulationMode"""
        # PROTECTED REGION ID(SdpMasterLeafNode.test_simulationMode) ENABLED START #
        simulation_mode = SimulationMode.FALSE
        tango_context.device.simulationMode = simulation_mode
        assert tango_context.device.simulationMode == simulation_mode
        # PROTECTED REGION END #    //  SdpMasterLeafNode.test_simulationMode

    def test_testMode(self, tango_context):
        """Test for testMode"""
        # PROTECTED REGION ID(SdpMasterLeafNode.test_testMode) ENABLED START #
        test_mode = TestMode.NONE
        tango_context.device.testMode = test_mode
        assert tango_context.device.testMode == test_mode
        # PROTECTED REGION END #    //  SdpMasterLeafNode.test_testMode


    def test_versionInfo(self, tango_context):
        """Test for versionInfo"""
        # PROTECTED REGION ID(SdpMasterLeafNode.test_versionInfo) ENABLED START #
        assert tango_context.device.versionInfo == '1.0'
        # PROTECTED REGION END #    //  SdpMasterLeafNode.test_versionInfo

    def test_activityMessage(self, tango_context):
        """Test for activityMessage"""
        # PROTECTED REGION ID(SdpMasterLeafNode.test_activityMessage) ENABLED START #
        tango_context.device.activityMessage = "text"
        assert tango_context.device.activityMessage == "text"
        # PROTECTED REGION END #    //  SdpMasterLeafNode.test_activityMessage

    def test_ProcessingBlockList(self, tango_context):
        """Test for ProcessingBlockList"""
        # PROTECTED REGION ID(SdpMasterLeafNode.test_ProcessingBlockList) ENABLED START #
        assert tango_context.device.ProcessingBlockList
        # PROTECTED REGION END #    //  SdpMasterLeafNode.test_ProcessingBlockList

    def test_Off(self, tango_context, create_sdp_master_proxy):
        """Test for Off command"""
        # PROTECTED REGION ID(SdpMasterLeafNode.test_Off) ENABLED START #
        tango_context.device.Off()
        assert tango_context.device.activityMessage in const.STR_OFF_CMD_SUCCESS
        # PROTECTED REGION END #    //  SdpMasterLeafNode.test_Off

    def test_off_devfailed_exception(self, tango_context):
        """Negative test for Off command"""
        # PROTECTED REGION ID(SdpMasterLeafNode.test_off_devfailed_exception) ENABLED START #
        tango_context.device.testMode = TestMode.TEST
        tango_context.device.Off()
        assert const.ERR_MSG in tango_context.device.activityMessage
        # PROTECTED REGION END #    //  SdpMasterLeafNode.test_off_devfailed_exception

    def test_Disable(self, tango_context):
        """Test for Off command"""
        # PROTECTED REGION ID(SdpMasterLeafNode.test_Off) ENABLED START #
        tango_context.device.Disable()
        assert tango_context.device.activityMessage in const.STR_DISABLE_CMS_SUCCESS
        # PROTECTED REGION END #    //  SdpMasterLeafNode.test_Off

    def test_loggingLevel(self, tango_context):
        """Test for loggingLevel"""
        # PROTECTED REGION ID(DishMaster.test_loggingLevel) ENABLED START #
        tango_context.device.loggingLevel = LoggingLevel.INFO
        assert tango_context.device.loggingLevel == LoggingLevel.INFO
        # PROTECTED REGION END #    //  DishMaster.test_loggingLevel

    def test_loggingTargets(self, tango_context):
        """Test for loggingTargets"""
        # PROTECTED REGION ID(DishMaster.test_loggingLevel) ENABLED START #
        tango_context.device.loggingTargets = ['console::cout']
        assert 'console::cout' in tango_context.device.loggingTargets
        # PROTECTED REGION END #    //  DishMaster.test_loggingTargets