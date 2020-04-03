#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of the CentralNode project
#
#
#
# Distributed under the terms of the BSD-3-Clause license.
# See LICENSE.txt for more info.
"""Contain the tests for the CentralNode."""

# Imports
import tango
import pytest
import json
import time
from tango import DevState
from centralnode import CentralNode, CONST
from ska.base.control_model import HealthState, AdminMode, SimulationMode, ControlMode, TestMode, LoggingLevel

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
@pytest.mark.usefixtures("tango_context", "create_subarray1_proxy", "create_leafNode1_proxy", "create_dish_proxy")

class TestCentralNode(object):
    """Test case for packet generation."""
    # PROTECTED REGION ID(CentralNode.test_additionnal_import) ENABLED START #
    # PROTECTED REGION END #    //  CentralNode.test_additionnal_import
    device = CentralNode
    empty = None  # Should be []

    @classmethod
    def mocking(cls):
        """Mock external libraries."""
        # Example : Mock numpy
        # cls.numpy = CentralNode.numpy = MagicMock()
        # PROTECTED REGION ID(CentralNode.test_mocking) ENABLED START #
        # PROTECTED REGION END #    //  CentralNode.test_mocking

    def test_properties(self, tango_context):
        # test the properties
        # PROTECTED REGION ID(CentralNode.test_properties) ENABLED START #
        # PROTECTED REGION END #    //  CentralNode.test_properties
        pass

    def test_State(self, tango_context):
        """Test for State"""
        # PROTECTED REGION ID(CentralNode.test_State) ENABLED START #
        assert tango_context.device.State() == DevState.ON
        # PROTECTED REGION END #    //  CentralNode.test_State

    def test_Status(self, tango_context):
        """Test for Status"""
        # PROTECTED REGION ID(CentralNode.test_Status) ENABLED START #
        assert tango_context.device.Status() == CONST.STR_INIT_SUCCESS
        # PROTECTED REGION END #    //  CentralNode.test_Status

    def test_GetMetrics(self, tango_context):
        """Test for GetMetrics"""
        # PROTECTED REGION ID(CentralNode.test_GetMetrics) ENABLED START #
        # PROTECTED REGION END #    //  CentralNode.test_GetMetrics

    def test_ToJson(self, tango_context):
        """Test for ToJson"""
        # PROTECTED REGION ID(CentralNode.test_ToJson) ENABLED START #
        # PROTECTED REGION END #    //  CentralNode.test_ToJson

    def test_GetVersionInfo(self, tango_context):
        """Test for GetVersionInfo"""
        # PROTECTED REGION ID(CentralNode.test_GetVersionInfo) ENABLED START #
        # PROTECTED REGION END #    //  CentralNode.test_GetVersionInfo

    def test_Reset(self, tango_context):
        """Test for Reset"""
        # PROTECTED REGION ID(CentralNode.test_Reset) ENABLED START #
        assert tango_context.device.Reset() == None
        # PROTECTED REGION END #    //  CentralNode.test_Reset

    def test_StartUpTelescope(self, tango_context, create_leafNode1_proxy):
        """Test for StartUpTelescope"""
        # PROTECTED REGION ID(CentralNode.test_StartUpTelescope) ENABLED START #
        tango_context.device.StartUpTelescope()
        time.sleep(10)
        assert tango_context.device.activityMessage == CONST.STR_STARTUP_CMD_ISSUED
        # PROTECTED REGION END #    //  CentralNode.test_StartUpTelescope

    def test_StartUpTelescope_Negative(self, tango_context):
        """Test for StartUpTelescope"""
        # PROTECTED REGION ID(CentralNode.test_StartUpTelescope) ENABLED START #
        tango_context.device.StartUpTelescope()
        assert CONST.ERR_EXE_STARTUP_CMD in tango_context.device.activityMessage
        # PROTECTED REGION END #    //  CentralNode.test_StartUpTelescope

    def test_StowAntennas_invalid_argument(self, tango_context):
        """Test for StowAntennas"""
        # PROTECTED REGION ID(CentralNode.test_StowAntennas) ENABLED START #
        argin = ["a", ]
        with pytest.raises(tango.DevFailed) :
            tango_context.device.StowAntennas(argin)
        assert CONST.ERR_STOW_ARGIN in tango_context.device.activityMessage
        # PROTECTED REGION END #    //  CentralNode.test_StowAntennas

    def test_StowAntennas_invalid_functionality(self, tango_context):
        """Test for StowAntennas"""
        # PROTECTED REGION ID(CentralNode.test_StowAntennas) ENABLED START #
        argin = ["0001",]
        tango_context.device.StartUpTelescope()
        with pytest.raises(tango.DevFailed) :
            tango_context.device.StowAntennas(argin)
        assert CONST.ERR_EXE_STOW_CMD in tango_context.device.activityMessage
        # PROTECTED REGION END #    //  CentralNode.test_StowAntennas

    def test_StowAntennas(self, tango_context, create_leafNode1_proxy):
        """Test for StowAntennas"""
        # PROTECTED REGION ID(CentralNode.test_StowAntennas) ENABLED START #
        argin = ["0001",]
        create_leafNode1_proxy.SetStandByLPMode()
        tango_context.device.StowAntennas(argin)
        assert tango_context.device.activityMessage == CONST.STR_STOW_CMD_ISSUED_CN
        # PROTECTED REGION END #    //  CentralNode.test_StowAntennas

    def test_StowAntennas_ValueErr(self, tango_context, create_leafNode1_proxy):
        """Negative Test for StowAntennas"""
        # PROTECTED REGION ID(CentralNode.test_StowAntennas) ENABLED START #
        argin = ["xyz",]
        create_leafNode1_proxy.SetStandByLPMode()
        with pytest.raises(tango.DevFailed):
            tango_context.device.StowAntennas(argin)
        assert CONST.ERR_STOW_ARGIN in tango_context.device.activityMessage
        # PROTECTED REGION END #    //  CentralNode.test_StowAntennas_ValueErr

    def test_StandByTelescope(self, tango_context):
        """Test for StandByTelescope"""
        # PROTECTED REGION ID(CentralNode.test_StandByTelescope) ENABLED START #
        tango_context.device.StandByTelescope()
        time.sleep(2)
        assert tango_context.device.activityMessage == CONST.STR_STANDBY_CMD_ISSUED
        # PROTECTED REGION END #    //  CentralNode.test_StandByTelescope

    def test_StandByTelescope_invalid_functionality(self, tango_context, create_leafNode1_proxy):
        """Test for StandByTelescope"""
        # PROTECTED REGION ID(CentralNode.test_StandByTelescope) ENABLED START #
        create_leafNode1_proxy.SetOperateMode()
        create_leafNode1_proxy.Scan("0")
        time.sleep(1)
        tango_context.device.StandByTelescope()
        assert CONST.ERR_EXE_STANDBY_CMD in tango_context.device.activityMessage
        # PROTECTED REGION END #    //  CentralNode.test_StandByTelescope

    def test_buildState(self, tango_context):
        """Test for buildState"""
        # PROTECTED REGION ID(CentralNode.test_buildState) ENABLED START #
        assert tango_context.device.buildState == (
            "lmcbaseclasses, 0.5.1, A set of generic base devices for SKA Telescope.")
        # PROTECTED REGION END #    //  CentralNode.test_buildState

    def test_versionId(self, tango_context):
        """Test for versionId"""
        # PROTECTED REGION ID(CentralNode.test_versionId) ENABLED START #
        assert tango_context.device.versionId == "0.5.1"
        # PROTECTED REGION END #    //  CentralNode.test_versionId

    def test_loggingLevel(self, tango_context):
        """Test for loggingLevel"""
        # PROTECTED REGION ID(CentralNode.test_loggingLevel) ENABLED START #
        tango_context.device.loggingLevel = LoggingLevel.INFO
        assert tango_context.device.loggingLevel == LoggingLevel.INFO
        # PROTECTED REGION END #    //  CentralNode.test_loggingLevel

    def test_healthState(self, tango_context):
        """Test for healthState"""
        # PROTECTED REGION ID(CentralNode.test_healthState) ENABLED START #
        assert tango_context.device.healthState == HealthState.OK
        # PROTECTED REGION END #    //  CentralNode.test_healthState

    def test_adminMode(self, tango_context):
        """Test for adminMode"""
        # PROTECTED REGION ID(CentralNode.test_adminMode) ENABLED START #
        assert tango_context.device.adminMode == AdminMode.ONLINE
        # PROTECTED REGION END #    //  CentralNode.test_adminMode

    def test_controlMode(self, tango_context):
        """Test for controlMode"""
        # PROTECTED REGION ID(CentralNode.test_controlMode) ENABLED START #
        control_mode = ControlMode.REMOTE
        tango_context.device.controlMode = control_mode
        assert tango_context.device.controlMode == control_mode
        # PROTECTED REGION END #    //  CentralNode.test_controlMode

    def test_simulationMode(self, tango_context):
        """Test for simulationMode"""
        # PROTECTED REGION ID(CentralNode.test_simulationMode) ENABLED START #
        simulation_mode = SimulationMode.FALSE
        tango_context.device.simulationMode = simulation_mode
        assert tango_context.device.simulationMode == simulation_mode
        # PROTECTED REGION END #    //  CentralNode.test_simulationMode

    def test_testMode(self, tango_context):
        """Test for testMode"""
        # PROTECTED REGION ID(CentralNode.test_testMode) ENABLED START #
        test_mode = TestMode.NONE
        tango_context.device.testMode = test_mode
        assert tango_context.device.testMode == test_mode
        # PROTECTED REGION END #    //  CentralNode.test_testMode

    def test_AssignResources_Failure_Before_Startup(self, tango_context, create_subarray1_proxy):
        test_input = '{"subarrayID":1,"dish":{"receptorIDList":["0001"]}}'
        with pytest.raises(tango.DevFailed):
            tango_context.device.AssignResources(test_input)
        result = create_subarray1_proxy.receptorIDList
        time.sleep(3)
        assert result == None
        assert create_subarray1_proxy.State() == DevState.DISABLE

    def test_AssignResources(self, tango_context, create_subarray1_proxy):
        test_input = '{"subarrayID":1,"dish":{"receptorIDList":["0001"]}}'
        tango_context.device.StartUpTelescope()
        time.sleep(10)
        json.loads(tango_context.device.AssignResources(test_input))
        time.sleep(3)
        result = create_subarray1_proxy.receptorIDList
        create_subarray1_proxy.ReleaseAllResources()
        assert result == (1, )

    def test_duplicate_Allocation(self, tango_context, create_subarray1_proxy):
        test_input = '{"subarrayID":1,"dish":{"receptorIDList":["0001"]}}'
        tango_context.device.AssignResources(test_input)
        time.sleep(3)
        test_input1 = '{"subarrayID":1,"dish":{"receptorIDList":["0001"]}}'
        result = tango_context.device.AssignResources(test_input1)
        time.sleep(2)
        input_release_res = '{"subarrayID":1,"releaseALL":true,"receptorIDList":[]}'
        create_subarray1_proxy.ReleaseResources(input_release_res)
        assert result == '{"dish": {"receptorIDList_success": []}}'

    def test_AssignResources_invalid_json(self, tango_context):
        test_input = '{"invalid_key"}'
        result = 'a'
        with pytest.raises(tango.DevFailed):
            result = tango_context.device.AssignResources(test_input)
        time.sleep(1)
        assert 'a' in result

    def test_AssignResources_key_not_found(self, tango_context):
        test_input = '{"dish":{"receptorIDList":["0001"]}}'
        result = 'a'
        with pytest.raises(tango.DevFailed):
            result = tango_context.device.AssignResources(test_input)
        time.sleep(1)
        assert 'a' in result

    def test_ReleaseResources(self, tango_context, create_subarray1_proxy):
        test_input = '{"subarrayID":1,"releaseALL":true,"receptorIDList":[]}'
        time.sleep(2)
        with pytest.raises(tango.DevFailed):
            retVal = json.loads(tango_context.device.ReleaseResources(test_input))
            assert retVal["receptorIDList"] == []
        time.sleep(3)
        result = create_subarray1_proxy.receptorIDList
        assert result == None

    def test_ReleaseResources_FalseTag(self, tango_context):
        test_input = '{"subarrayID":1,"releaseALL":false,"receptorIDList":[]}'
        tango_context.device.ReleaseResources(test_input)
        time.sleep(1)
        assert tango_context.device.activityMessage == CONST.STR_FALSE_TAG

    def test_ReleaseResources_invalid_json(self, tango_context):
        test_input = '{"invalid_key"}'
        with pytest.raises(tango.DevFailed):
            tango_context.device.ReleaseResources(test_input)
        time.sleep(1)
        assert CONST.ERR_INVALID_JSON in tango_context.device.activityMessage

    def test_ReleaseResources_key_not_found(self, tango_context):
        test_input = '{"releaseALL":true,"receptorIDList":[]}'
        with pytest.raises(tango.DevFailed):
            tango_context.device.ReleaseResources(test_input)
        time.sleep(1)
        assert CONST.ERR_JSON_KEY_NOT_FOUND in tango_context.device.activityMessage


    def test_telescopeHealthState(self, tango_context):
        """Test for telescopeHealthState"""
        # PROTECTED REGION ID(CentralNode.test_telescopeHealthState) ENABLED START #
        assert tango_context.device.telescopeHealthState == HealthState.OK
        # PROTECTED REGION END #    //  CentralNode.test_telescopeHealthState

    def test_subarray1HealthState(self, tango_context):
        """Test for subarray1HealthState"""
        # PROTECTED REGION ID(CentralNode.test_subarray1HealthState) ENABLED START #
        assert tango_context.device.subarray1HealthState == HealthState.OK
        # PROTECTED REGION END #    //  CentralNode.test_subarray1HealthState

    def test_subarray2HealthState(self, tango_context):
        """Test for subarray2HealthState"""
        # PROTECTED REGION ID(CentralNode.test_subarray2HealthState) ENABLED START #
        assert tango_context.device.subarray2HealthState == HealthState.OK
        # PROTECTED REGION END #    //  CentralNode.test_subarray2HealthState

    def test_subarray3HealthState(self, tango_context):
        """Test for subarray3HealthState"""
        # PROTECTED REGION ID(CentralNode.test_subarray3HealthState) ENABLED START #
        assert tango_context.device.subarray3HealthState == HealthState.OK
        # PROTECTED REGION END #    //  CentralNode.test_subarray3HealthState

    def test_activityMessage(self, tango_context):
        """Test for activityMessage"""
        # PROTECTED REGION ID(CentralNode.test_activityMessage) ENABLED START #
        tango_context.device.activityMessage = 'test'
        assert tango_context.device.activityMessage == "test"
        # PROTECTED REGION END #    //  CentralNode.test_activityMessage

    def test_loggingTargets(self, tango_context):
        """Test for loggingTargets"""
        # PROTECTED REGION ID(DishMaster.test_loggingLevel) ENABLED START #
        tango_context.device.loggingTargets = ['console::cout']
        assert 'console::cout' in tango_context.device.loggingTargets
        # PROTECTED REGION END #    //  DishMaster.test_loggingTargets
