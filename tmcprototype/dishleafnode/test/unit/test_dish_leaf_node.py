#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of the DishLeafNode project
#
#
#
# Distributed under the terms of the BSD-3-Clause license.
# See LICENSE.txt for more info.
"""Contain the tests for DishLeafNode."""
from __future__ import print_function


import tango
from tango import DevState, EventType
import pytest
from dishleafnode import DishLeafNode, const
from tango.server import Device, command
from ska.base.control_model import (
    HealthState,
    AdminMode,
    SimulationMode,
    TestMode,
    ControlMode,
    LoggingLevel,
)

@pytest.fixture(scope="function")
def devices_info(tango_context):
    yield tango_context.get_device("test_d0001/elt/master")


class Dish(Device):
    @command(dtype_in=None, dtype_out="DevVarLongStringArray")
    def SetStowMode(self):
        pass

    @command(dtype_in=None, dtype_out="DevVarLongStringArray")
    def SetStandbyLPMode(self):
        pass

    @command(dtype_in=None, dtype_out="DevVarLongStringArray")
    def SetOperateMode(self):
        pass

    @command(dtype_in="DevString", dtype_out=None)
    def Scan(self):
        pass

    @command(dtype_in=None, dtype_out=None)
    def StopCapture(self):
        pass

    @command(dtype_in=None, dtype_out=None)
    def StartCapture(self):
        pass

    @command(dtype_in=None, dtype_out="DevVarLongStringArray")
    def SetStandbyFPMode(self):
        pass

    @command(dtype_in="DevVarDoubleArray", dtype_out=None)
    def Slew(self):
        pass

    @command(dtype_in="DevString", dtype_out=None)
    def Track(self):
        pass

    @command(dtype_in=None, dtype_out=None)
    def TrackStop(self):
        pass


devices_info = [
    {
        "class": DishLeafNode,
        "devices": (
            {
                "name": "test/tm_leaf_node/d0001",
                "properties": {
                    "DishMasterFQDN": ["test_d0001/elt/master"],
                    "SkaLevel": ["3"],
                    "TrackDuration": ["1"],
                    "LoggingTargetsDefault": ["tango::logger"],
                    "LoggingLevelDefault": ["5"],
                    "polled_attr": ["activitymessage", "1000", "healthstate", "1000"],
                },
            },
        ),
    },
    {"class": Dish, "devices": ({"name": "test_d0001/elt/master"},)},
]


class TestDishLeafNode(object):
    """Test case for packet generation."""

    # PROTECTED REGION ID(DishLeafNode.test_additionnal_import) ENABLED START #
    # PROTECTED REGION END #    //  DishLeafNode.test_additionnal_import
    device = DishLeafNode
    properties = {
        "SkaLevel": "4",
        "MetricList": "healthState",
        "GroupDefinitions": "",
        "LoggingTargetsDefault": "console::cout",
        "LoggingLevelDefault": "4",
        "DishMasterFQDN": "mid_d0001/elt/master",
        "TrackDuration": 1,
    }
    empty = None  # Should be []

    @classmethod
    def mocking(cls):
        """Mock external libraries."""
        # Example : Mock numpy
        # cls.numpy = DishLeafNode.numpy = MagicMock()
        # PROTECTED REGION ID(DishLeafNode.test_mocking) ENABLED START #
        # PROTECTED REGION END #    //  DishLeafNode.test_mocking

    def test_properties(self, tango_context):
        """ test the properties """
        # PROTECTED REGION END #    //  DishLeafNode.test_properties

    def test_State(self, tango_context):
        """Test for State"""
        # PROTECTED REGION ID(DishLeafNode.test_State) ENABLED START #
        assert tango_context.device.State() == DevState.ALARM
        # PROTECTED REGION END #    //  DishLeafNode.test_State

    def test_Status(self, tango_context):
        """Test for Status"""
        # PROTECTED REGION ID(DishLeafNode.test_Status) ENABLED START #
        assert tango_context.device.Status() != const.STR_DISH_INIT_SUCCESS
        # PROTECTED REGION END #    //  DishLeafNode.test_Status

    @pytest.mark.xfail
    def test_Reset(self, tango_context):
        """Test for Reset"""
        # PROTECTED REGION ID(DishLeafNode.test_Reset) ENABLED START #
        assert tango_context.device.Reset() is None
        # PROTECTED REGION END #    //  DishLeafNode.test_Reset

    @pytest.mark.xfail
    def test_SetStandByLPMode(self, tango_context):
        """Test for SetStandByLPMode"""
        # PROTECTED REGION ID(DishLeafNode.test_SetStandByLPMode) ENABLED START #
        tango_context.device.SetStandByLPMode()
        assert tango_context.device.activityMessage == (const.STR_SETSTANDBYLP_SUCCESS) or (
            const.STR_DISH_STANDBYLP_MODE
        )
        # PROTECTED REGION END #    //  DishLeafNode.test_SetStandByLPMode

    def test_SetOperateMode(self, tango_context):
        """Test for SetOperateMode"""
        # PROTECTED REGION ID(DishLeafNode.test_SetOperateMode) ENABLED START #
        tango_context.device.SetOperateMode()
        assert tango_context.device.activityMessage == (const.STR_SETOPERATE_SUCCESS) or (
            const.STR_DISH_OPERATE_MODE
        )
        # PROTECTED REGION END #    //  DishLeafNode.test_SetOperateMode

    @pytest.mark.xfail
    def test_Track_invalid_radec(self, tango_context):
        """Test for Track"""
        # PROTECTED REGION ID(DishLeafNode.test_Track) ENABLED START #
        input_string = '{"pointing":{"target":{"system":"ICRS","name":"Polaris","RA":"02:31:49.09","dec":"+89:15:50.79"}},"dish":{"receiverBand":"1"}}'
        tango_context.device.Track(input_string)
        assert const.ERR_ELE_LIM in tango_context.device.activityMessage
        tango_context.dish.TrackStop()
        # PROTECTED REGION END #    //  DishLeafNode.Track

    @pytest.mark.xfail
    def test_Configure(self, tango_context):
        """Test for Configure"""
        # PROTECTED REGION ID(DishLeafNode.test_Configure) ENABLED START #
        input_string = '{"pointing":{"target":{"system":"ICRS","name":"Polaris Australis","RA":"21:08:47.92","dec":"-88:57:22.9"}},"dish":{"receiverBand":"1"}}'
        tango_context.device.Configure(input_string)
        assert tango_context.device.activityMessage == (const.STR_CONFIGURE_SUCCESS) or (
            const.STR_DISH_POINT_STATE_READY
        )
        # PROTECTED REGION END #    //  DishLeafNode.test_Configure

    @pytest.mark.xfail
    def test_Configure_invalid_JSON(self, tango_context):
        """Test for Configure_invalid_JSON  (Negative test case)"""
        # PROTECTED REGION ID(DishLeafNode.test_Track) ENABLED START #
        input_string = '{"Invalid Key"}'
        with pytest.raises(tango.DevFailed):
            tango_context.device.Configure(input_string)
        assert const.ERR_INVALID_JSON in tango_context.device.activityMessage

    def test_Configure_invalid_arguments(self, tango_context):
        """Test for Configure_invalid_arguments  (Negative test case)"""
        input_string = []
        input_string.append(
            '{"pointing":{"target":{"system":"ICRS","name":"Polaris Australis","":"21:08:47.92","":"-88:5.7:22.9"}},"dish":{"receiverBand":"1"}}'
        )
        with pytest.raises(tango.DevFailed):
            tango_context.device.Configure(input_string[0])
        assert const.ERR_JSON_KEY_NOT_FOUND in tango_context.device.activityMessage

    @pytest.mark.xfail
    def test_Configure_generic_exception(self, tango_context):
        """
        Test case to check generic exception (Negative test case)
        :param tango_context:
        :return:
        """
        Configure_input = "[123]"
        with pytest.raises(tango.DevFailed):
            tango_context.device.Configure(Configure_input)
        assert const.ERR_EXE_CONFIGURE_CMD in tango_context.device.activityMessage

    @pytest.mark.xfail
    def test_Scan(self, tango_context):
        """Test for Scan"""
        # PROTECTED REGION ID(DishLeafNode.test_Scan) ENABLED START #
        tango_context.device.Scan("0")
        assert tango_context.device.activityMessage == (const.STR_SCAN_SUCCESS) or (
            const.STR_DISH_POINT_STATE_SCAN
        )
        # PROTECTED REGION END #    //  DishLeafNode.test_Scan

    def test_Scan_invalid_arguments(self, tango_context):
        """Test for Scan_invalid_arguments (Negative test case)"""
        with pytest.raises(tango.DevFailed):
            tango_context.device.Scan("a")
        assert const.ERR_EXE_SCAN_CMD in tango_context.device.activityMessage

    @pytest.mark.xfail
    def test_EndScan(self, tango_context):
        """Test for EndScan"""
        # PROTECTED REGION ID(DishLeafNode.test_EndScan) ENABLED START #
        tango_context.device.EndScan("0")
        assert tango_context.device.activityMessage == (const.STR_ENDSCAN_SUCCESS) or (
            const.STR_DISH_POINT_STATE_READY
        )
        # PROTECTED REGION END #    //  DishLeafNode.test_EndScan

    def test_EndScan_invalid_arguments(self, tango_context):
        """Test for EndScan_invalid_arguments (Negative test case)"""
        with pytest.raises(tango.DevFailed):
            tango_context.device.EndScan("a")
        assert const.ERR_EXE_END_SCAN_CMD in tango_context.device.activityMessage

    @pytest.mark.xfail
    def test_StartCapture(self, tango_context):
        """Test for StartCapture"""
        # PROTECTED REGION ID(DishLeafNode.test_StartCapture) ENABLED START #
        tango_context.device.StartCapture("0")
        assert tango_context.device.activityMessage == (const.STR_STARTCAPTURE_SUCCESS) or (
            const.STR_DISH_POINT_STATE_SCAN
        )
        # PROTECTED REGION END #    //  DishLeafNode.test_StartCapture

    @pytest.mark.xfail
    def test_StartCapture_invalid_arguments(self, tango_context):
        """Test for StartCapture_invalid_arguments (Negative test case)"""
        with pytest.raises(tango.DevFailed):
            tango_context.device.StartCapture("a")
        assert const.ERR_EXE_START_CAPTURE_CMD in tango_context.device.activityMessage

    @pytest.mark.xfail
    def test_StopCapture(self, tango_context):
        """Test for StopCapture"""
        # PROTECTED REGION ID(DishLeafNode.test_StopCapture) ENABLED START #
        tango_context.device.StopCapture("0")
        assert tango_context.device.activityMessage == (const.STR_STOPCAPTURE_SUCCESS) or (
            const.STR_DISH_POINT_STATE_READY
        )
        # PROTECTED REGION END #    //  DishLeafNode.test_StopCapture

    @pytest.mark.xfail
    def test_StopCapture_invalid_arguments(self, tango_context):
        """Test for StopCapture_invalid_arguments (Negative test case)"""
        with pytest.raises(tango.DevFailed):
            tango_context.device.StopCapture("a")
        assert const.ERR_EXE_STOP_CAPTURE_CMD in tango_context.device.activityMessage

    @pytest.mark.xfail
    def test_SetStandbyFPMode(self, tango_context):
        """Test for SetStandbyFPMode"""
        # PROTECTED REGION ID(DishLeafNode.test_SetStandbyFPMode) ENABLED START #
        tango_context.device.SetStandbyFPMode()
        assert tango_context.device.activityMessage == (const.STR_STANDBYFP_SUCCESS) or (
            const.STR_DISH_STANDBYFP_MODE
        )
        # PROTECTED REGION END #    //  DishLeafNode.test_SetStandbyFPMode

    @pytest.mark.xfail
    def test_SetStowMode(self, tango_context):
        """Test for SetStowMode"""
        # PROTECTED REGION ID(DishLeafNode.test_SetStowMode) ENABLED START #
        tango_context.device.SetStandByLPMode()
        tango_context.device.SetStowMode()
        assert (
            tango_context.device.activityMessage == (const.STR_DISH_POINT_STATE_READY)
            or (const.STR_DISH_STOW_MODE)
            or (const.STR_DESIREDPOINTING_0_0)
            or (const.STR_ACHIEVEDPOINTING_0_0)
        )
        # PROTECTED REGION END #    //  DishLeafNode.test_SetStowMode

    @pytest.mark.xfail
    def test_Slew(self, tango_context):
        """Test for Slew"""
        # PROTECTED REGION ID(DishLeafNode.test_Slew) ENABLED START #
        tango_context.device.SetStandByLPMode()
        tango_context.device.Slew("0")
        assert tango_context.device.activityMessage == const.STR_SLEW_SUCCESS

    @pytest.mark.xfail
    def test_Slew_invalid_arguments(self, tango_context):
        """Test for Slew_invalid_arguments (Negative test case)"""
        tango_context.device.SetStandByLPMode()
        with pytest.raises(tango.DevFailed):
            tango_context.device.Slew("a")
        assert const.ERR_EXE_SLEW_CMD in tango_context.device.activityMessage
        # PROTECTED REGION END #    //  DishLeafNode.test_Slew

    @pytest.mark.xfail
    def test_Track_invalid_arg(self, tango_context):
        """Test for Track_invalid_arguments (Negative test case)"""
        # PROTECTED REGION ID(DishLeafNode.test_Track) ENABLED START #
        input_string = '{"pointing":{"target":{"system":"ICRS","name":"Polaris Australis","":"21:08:47.92","":"-88:57:22.9"}},"dish":{"receiverBand":"1"}}'
        with pytest.raises(tango.DevFailed):
            tango_context.device.Track(input_string)
        assert const.ERR_JSON_KEY_NOT_FOUND in tango_context.device.activityMessage
        tango_context.device.SetStandByLPMode()
        # PROTECTED REGION END #    //  DishLeafNode.test_Track

    @pytest.mark.xfail
    def test_Track_invalid_JSON(self, tango_context):
        """Test for Track_invalid_JSON (Negative test case)"""
        # PROTECTED REGION ID(DishLeafNode.test_Track) ENABLED START #
        input_string = '{"Invalid Key"}'
        with pytest.raises(tango.DevFailed):
            tango_context.device.Track(input_string)
        assert const.ERR_INVALID_JSON in tango_context.device.activityMessage

    @pytest.mark.xfail
    def test_Track(self, tango_context):
        """Test for Track"""
        # PROTECTED REGION ID(DishLeafNode.test_Track) ENABLED START #
        input_string = '{"pointing":{"target":{"system":"ICRS","name":"Polaris Australis","RA":"21:08:47.92","dec":"-88:57:22.9"}},"dish":{"receiverBand":"1"}}'
        tango_context.device.Track(input_string)
        assert tango_context.dish.pointingState == 1 or tango_context.dish.pointingState == 2
        tango_context.dish.TrackStop()
        # PROTECTED REGION END #    //  DishLeafNode.Track

    @pytest.mark.xfail
    def test_TrackStop(self, tango_context):
        """Test for Track"""
        # PROTECTED REGION ID(DishLeafNode.test_Track) ENABLED START #
        tango_context.device.TrackStop()
        assert tango_context.dish.pointingState == 0
        # PROTECTED REGION END #    //  DishLeafNode.Track

    @pytest.mark.xfail
    def test_buildState(self, tango_context):
        """Test for buildState"""
        # PROTECTED REGION ID(DishLeafNode.test_buildState) ENABLED START #
        assert tango_context.device.buildState == (
            "lmcbaseclasses, 0.6.3, A set of generic base devices for SKA Telescope."
        )
        # PROTECTED REGION END #    //  DishLeafNode.test_buildState

    @pytest.mark.xfail
    def test_versionId(self, tango_context):
        """Test for versionId"""
        # PROTECTED REGION ID(DishLeafNode.test_versionId) ENABLED START #
        assert tango_context.device.versionId == "0.6.3"
        # PROTECTED REGION END #    //  DishLeafNode.test_versionId

    def test_healthState(self, tango_context):
        """Test for healthState"""
        # PROTECTED REGION ID(DishLeafNode.test_healthState) ENABLED START #
        assert tango_context.device.healthState == HealthState.OK
        # PROTECTED REGION END #    //  DishLeafNode.test_healthState

    @pytest.mark.xfail
    def test_adminMode(self, tango_context):
        """Test for adminMode"""
        # PROTECTED REGION ID(DishLeafNode.test_adminMode) ENABLED START #
        assert tango_context.device.adminMode == AdminMode.ONLINE
        # PROTECTED REGION END #    //  DishLeafNode.test_adminMode

    def test_controlMode(self, tango_context):
        """Test for controlMode"""
        # PROTECTED REGION ID(DishLeafNode.test_controlMode) ENABLED START #
        control_mode = ControlMode.REMOTE
        tango_context.device.controlMode = control_mode
        assert tango_context.device.controlMode == control_mode
        # PROTECTED REGION END #    //  DishLeafNode.test_controlMode

    def test_simulationMode(self, tango_context):
        """Test for simulationMode"""
        # PROTECTED REGION ID(DishLeafNode.test_simulationMode) ENABLED START #
        simulation_mode = SimulationMode.FALSE
        tango_context.device.simulationMode = simulation_mode
        assert tango_context.device.simulationMode == simulation_mode
        # PROTECTED REGION END #    //  DishLeafNode.test_simulationMode

    def test_testMode(self, tango_context):
        """Test for testMode"""
        # PROTECTED REGION ID(DishLeafNode.test_testMode) ENABLED START #
        test_mode = TestMode.NONE
        tango_context.device.testMode = test_mode
        assert tango_context.device.testMode == test_mode
        # PROTECTED REGION END #    //  DishLeafNode.test_testMode

    @pytest.mark.xfail
    def test_activityMessage(self, tango_context):
        """Test for activityMessage"""
        # PROTECTED REGION ID(DishLeafNode.test_activityMessage) ENABLED START #
        tango_context.device.activityMessage = const.STR_OK
        assert tango_context.device.activityMessage == const.STR_OK
        # PROTECTED REGION END #    //  DishLeafNode.test_activityMessage

    @pytest.mark.xfail
    def test_dishMode_change_event(self, tango_context):
        """Test for dishMode_change_event"""
        tango_context.device.SetOperateMode()
        eid = tango_context.dish.subscribe_event(
            const.EVT_DISH_MODE, EventType.CHANGE_EVENT, DishLeafNode.dish_mode_cb
        )
        assert (
            tango_context.device.activityMessage == const.STR_DISH_OPERATE_MODE
            or const.STR_SETOPERATE_SUCCESS
        )
        assert tango_context.dish.dishMode == "OPERATE" or 8
        tango_context.dish.unsubscribe_event(eid)

    @pytest.mark.xfail
    def test_achieved_pointingState_change_event(self, tango_context):
        """Test for pointingState_change_event"""
        tango_context.device.Scan("0")
        eid = tango_context.dish.subscribe_event(
            const.EVT_DISH_POINTING_STATE,
            EventType.CHANGE_EVENT,
            DishLeafNode.dish_achieved_pointing_cb,
        )
        # assert tango_context.device.activityMessage == const.STR_DISH_POINT_STATE_SCAN
        assert tango_context.dish.pointingState == "SCANNING" or 3
        tango_context.dish.unsubscribe_event(eid)

    @pytest.mark.xfail
    def test_capturing_change_event(self, tango_context):
        """Test for capturing_change_event"""
        tango_context.device.StopCapture("0")
        eid = tango_context.dish.subscribe_event(
            const.EVT_DISH_CAPTURING, EventType.CHANGE_EVENT, DishLeafNode.dish_capturing_cb
        )
        assert (
            tango_context.device.activityMessage == (const.STR_DISH_CAPTURING_FALSE)
            or (const.STR_DISH_POINT_STATE_READY)
            or (const.STR_CAPTURE_EVENT)
        )
        assert tango_context.dish.capturing is False
        tango_context.dish.unsubscribe_event(eid)
        tango_context.device.SetStandByLPMode()

    def test_loggingLevel(self, tango_context):
        """Test for loggingLevel"""
        # PROTECTED REGION ID(DishLeafNode.test_loggingLevel) ENABLED START #
        tango_context.device.loggingLevel = LoggingLevel.INFO
        assert tango_context.device.loggingLevel == LoggingLevel.INFO
        # PROTECTED REGION END #    //  DishLeafNode.test_loggingLevel

    def test_loggingTargets(self, tango_context):
        """Test for loggingTargets"""
        # PROTECTED REGION ID(DishLeafNode.test_loggingLevel) ENABLED START #
        tango_context.device.loggingTargets = ["tango::logger"]
        assert "tango::logger" in tango_context.device.loggingTargets
        # PROTECTED REGION END #    //  DishLeafNode.test_loggingTargets
