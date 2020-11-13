#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Contain the tests for DishLeafNode."""
from __future__ import print_function


import tango
from tango import DevState, EventType
import pytest
from dishleafnode import DishLeafNode, const
from dishmaster.utils import get_tango_server_class
from ska.base.control_model import (
    HealthState,
    AdminMode,
    SimulationMode,
    TestMode,
    ControlMode,
    LoggingLevel,
)

dish_master_device_name = "test/nodb/dishmaster"
DishMaster = get_tango_server_class(dish_master_device_name)
devices_info = [
    {
        "class": DishLeafNode,
        "devices": (
            {
                "name": "test/tm_leaf_node/d0001",
                "properties": {
                    "DishMasterFQDN": [dish_master_device_name],
                    "SkaLevel": ["3"],
                    "TrackDuration": ["1"],
                    "LoggingTargetsDefault": ["tango::logger"],
                    "LoggingLevelDefault": ["5"],
                    "polled_attr": ["activitymessage", "1000", "healthstate", "1000"],
                },
            },
        ),
    },
    {
        "class": DishMaster,
        "devices": (
            {
                "name": dish_master_device_name,
                "properties": {
                    "SkaLevel": ["1"],
                    "LoggingTargetsDefault": ["tango::logger"],
                    "LoggingLevelDefault": ["5"],
                    "min_update_period": ["0.2"],
                },
            },
        ),
    },
]


class TestDishLeafNode(object):
    def test_State(self, tango_context):
        assert tango_context.device.State() == DevState.ALARM

    def test_Status(self, tango_context):
        assert tango_context.device.Status() != const.STR_DISH_INIT_SUCCESS

    @pytest.mark.xfail
    def test_Reset(self, tango_context):
        assert tango_context.device.Reset() is None

    @pytest.mark.xfail
    def test_SetStandByLPMode(self, tango_context):
        tango_context.device.SetStandByLPMode()
        assert tango_context.device.activityMessage == (const.STR_SETSTANDBYLP_SUCCESS) or (
            const.STR_DISH_STANDBYLP_MODE
        )

    def test_SetOperateMode(self, tango_context):
        tango_context.device.SetOperateMode()
        assert tango_context.device.activityMessage == (const.STR_SETOPERATE_SUCCESS) or (
            const.STR_DISH_OPERATE_MODE
        )

    @pytest.mark.xfail
    def test_Track_invalid_radec(self, tango_context):
        input_string = '{"pointing":{"target":{"system":"ICRS","name":"Polaris","RA":"02:31:49.09","dec":"+89:15:50.79"}},"dish":{"receiverBand":"1"}}'
        tango_context.device.Track(input_string)
        assert const.ERR_ELE_LIM in tango_context.device.activityMessage
        tango_context.dish.TrackStop()

    @pytest.mark.xfail
    def test_Configure(self, tango_context):
        input_string = '{"pointing":{"target":{"system":"ICRS","name":"Polaris Australis","RA":"21:08:47.92","dec":"-88:57:22.9"}},"dish":{"receiverBand":"1"}}'
        tango_context.device.Configure(input_string)
        assert tango_context.device.activityMessage == (const.STR_CONFIGURE_SUCCESS) or (
            const.STR_DISH_POINT_STATE_READY
        )

    @pytest.mark.xfail
    def test_Configure_invalid_JSON(self, tango_context):
        input_string = '{"Invalid Key"}'
        with pytest.raises(tango.DevFailed):
            tango_context.device.Configure(input_string)
        assert const.ERR_INVALID_JSON in tango_context.device.activityMessage

    @pytest.mark.xfail
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
        Configure_input = "[123]"
        with pytest.raises(tango.DevFailed):
            tango_context.device.Configure(Configure_input)
        assert const.ERR_EXE_CONFIGURE_CMD in tango_context.device.activityMessage

    @pytest.mark.xfail
    def test_Scan(self, tango_context):
        tango_context.device.Scan("0")
        assert tango_context.device.activityMessage == (const.STR_SCAN_SUCCESS) or (
            const.STR_DISH_POINT_STATE_SCAN
        )

    @pytest.mark.xfail
    def test_Scan_invalid_arguments(self, tango_context):
        with pytest.raises(tango.DevFailed):
            tango_context.device.Scan("a")
        assert const.ERR_EXE_SCAN_CMD in tango_context.device.activityMessage

    @pytest.mark.xfail
    def test_EndScan(self, tango_context):
        tango_context.device.EndScan("0")
        assert tango_context.device.activityMessage == (const.STR_ENDSCAN_SUCCESS) or (
            const.STR_DISH_POINT_STATE_READY
        )

    def test_EndScan_invalid_arguments(self, tango_context):
        """Test for EndScan_invalid_arguments (Negative test case)"""
        with pytest.raises(tango.DevFailed):
            tango_context.device.EndScan("a")
        assert const.ERR_EXE_END_SCAN_CMD in tango_context.device.activityMessage

    @pytest.mark.xfail
    def test_StartCapture(self, tango_context):
        tango_context.device.StartCapture("0")
        assert tango_context.device.activityMessage == (const.STR_STARTCAPTURE_SUCCESS) or (
            const.STR_DISH_POINT_STATE_SCAN
        )

    @pytest.mark.xfail
    def test_StartCapture_invalid_arguments(self, tango_context):
        with pytest.raises(tango.DevFailed):
            tango_context.device.StartCapture("a")
        assert const.ERR_EXE_START_CAPTURE_CMD in tango_context.device.activityMessage

    @pytest.mark.xfail
    def test_StopCapture(self, tango_context):
        tango_context.device.StopCapture("0")
        assert tango_context.device.activityMessage == (const.STR_STOPCAPTURE_SUCCESS) or (
            const.STR_DISH_POINT_STATE_READY
        )

    @pytest.mark.xfail
    def test_StopCapture_invalid_arguments(self, tango_context):
        with pytest.raises(tango.DevFailed):
            tango_context.device.StopCapture("a")
        assert const.ERR_EXE_STOP_CAPTURE_CMD in tango_context.device.activityMessage

    @pytest.mark.xfail
    def test_SetStandbyFPMode(self, tango_context):
        tango_context.device.SetStandbyFPMode()
        assert tango_context.device.activityMessage == (const.STR_STANDBYFP_SUCCESS) or (
            const.STR_DISH_STANDBYFP_MODE
        )

    @pytest.mark.xfail
    def test_SetStowMode(self, tango_context):
        tango_context.device.SetStandByLPMode()
        tango_context.device.SetStowMode()
        assert (
            tango_context.device.activityMessage == (const.STR_DISH_POINT_STATE_READY)
            or (const.STR_DISH_STOW_MODE)
            or (const.STR_DESIREDPOINTING_0_0)
            or (const.STR_ACHIEVEDPOINTING_0_0)
        )

    @pytest.mark.xfail
    def test_Slew(self, tango_context):
        tango_context.device.SetStandByLPMode()
        tango_context.device.Slew("0")
        assert tango_context.device.activityMessage == const.STR_SLEW_SUCCESS

    @pytest.mark.xfail
    def test_Slew_invalid_arguments(self, tango_context):
        tango_context.device.SetStandByLPMode()
        with pytest.raises(tango.DevFailed):
            tango_context.device.Slew("a")
        assert const.ERR_EXE_SLEW_CMD in tango_context.device.activityMessage

    @pytest.mark.xfail
    def test_Track_invalid_arg(self, tango_context):
        input_string = '{"pointing":{"target":{"system":"ICRS","name":"Polaris Australis","":"21:08:47.92","":"-88:57:22.9"}},"dish":{"receiverBand":"1"}}'
        with pytest.raises(tango.DevFailed):
            tango_context.device.Track(input_string)
        assert const.ERR_JSON_KEY_NOT_FOUND in tango_context.device.activityMessage
        tango_context.device.SetStandByLPMode()

    @pytest.mark.xfail
    def test_Track_invalid_JSON(self, tango_context):
        input_string = '{"Invalid Key"}'
        with pytest.raises(tango.DevFailed):
            tango_context.device.Track(input_string)
        assert const.ERR_INVALID_JSON in tango_context.device.activityMessage

    @pytest.mark.xfail
    def test_Track(self, tango_context):
        input_string = '{"pointing":{"target":{"system":"ICRS","name":"Polaris Australis","RA":"21:08:47.92","dec":"-88:57:22.9"}},"dish":{"receiverBand":"1"}}'
        tango_context.device.Track(input_string)
        assert tango_context.dish.pointingState == 1 or tango_context.dish.pointingState == 2
        tango_context.dish.TrackStop()

    @pytest.mark.xfail
    def test_TrackStop(self, tango_context):
        tango_context.device.TrackStop()
        assert tango_context.dish.pointingState == 0

    @pytest.mark.xfail
    def test_buildState(self, tango_context):
        assert tango_context.device.buildState == (
            "lmcbaseclasses, 0.6.3, A set of generic base devices for SKA Telescope."
        )

    @pytest.mark.xfail
    def test_versionId(self, tango_context):
        assert tango_context.device.versionId == "0.6.3"

    def test_healthState(self, tango_context):
        assert tango_context.device.healthState == HealthState.OK

    @pytest.mark.xfail
    def test_adminMode(self, tango_context):
        assert tango_context.device.adminMode == AdminMode.ONLINE

    @pytest.mark.xfail
    def test_controlMode(self, tango_context):
        control_mode = ControlMode.REMOTE
        tango_context.device.controlMode = control_mode
        assert tango_context.device.controlMode == control_mode

    @pytest.mark.xfail
    def test_simulationMode(self, tango_context):
        simulation_mode = SimulationMode.FALSE
        tango_context.device.simulationMode = simulation_mode
        assert tango_context.device.simulationMode == simulation_mode

    @pytest.mark.xfail
    def test_testMode(self, tango_context):
        test_mode = TestMode.NONE
        tango_context.device.testMode = test_mode
        assert tango_context.device.testMode == test_mode

    @pytest.mark.xfail
    def test_activityMessage(self, tango_context):
        tango_context.device.activityMessage = const.STR_OK
        assert tango_context.device.activityMessage == const.STR_OK

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

    @pytest.mark.xfail
    def test_loggingLevel(self, tango_context):
        tango_context.device.loggingLevel = LoggingLevel.INFO
        assert tango_context.device.loggingLevel == LoggingLevel.INFO

    @pytest.mark.xfail
    def test_loggingTargets(self, tango_context):
        tango_context.device.loggingTargets = ["tango::logger"]
        assert "tango::logger" in tango_context.device.loggingTargets
