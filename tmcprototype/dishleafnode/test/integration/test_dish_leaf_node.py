#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Contain the tests for DishLeafNode."""
from __future__ import print_function


import tango
from tango import DevState, EventType
import pytest
from os.path import dirname, join
from dishleafnode import DishLeafNode, const
from dishmaster.utils import get_tango_server_class
from tango.server import Device, command
from ska.base.control_model import (
    HealthState,
    AdminMode,
    SimulationMode,
    TestMode,
    ControlMode,
    LoggingLevel,
)
from tango_simlib.tango_sim_generator import configure_device_model, get_tango_device_server

DISH_DEVICE_NAME = "mid_d0001/nodb/master"
LEAF_NODE_DEVICE_NAME = "test/tm_leaf_node/d0001"


def get_dishmaster_server_class(DISH_DEVICE_NAME):
    """Build and return the Tango device class for DishMaster

    Parameters
    ----------
    DISH_DEVICE_NAME: string
        The Tango device name

    Returns
    -------
    DishMaster: tango.server.Device
        The Tango device class for dishmaster
    """
    data_descr_files = []
    data_descr_files.append(join(dirname(__file__), "data", "dish_master.fgo"))
    data_descr_files.append(join(dirname(__file__), "data", "dish_master_SimDD.json"))
    configure_args = {}
    configure_args["test_device_name"] = DISH_DEVICE_NAME
    model = configure_device_model(data_descr_files, **configure_args)
    DishMaster, _ = get_tango_device_server(model, data_descr_files)
    return DishMaster


DishMaster = get_dishmaster_server_class(DISH_DEVICE_NAME)

devices_info = [
    {
        "class": DishMaster,
        "devices": (
            {
                "name": DISH_DEVICE_NAME,
                "properties": {
                    "SkaLevel": ["1"],
                    "LoggingTargetsDefault": ["tango::logger"],
                    "LoggingLevelDefault": ["5"],
                    "min_update_period": ["0.2"],
                },
            },
        ),
    },
    {
        "class": DishLeafNode,
        "devices": (
            {
                "name": LEAF_NODE_DEVICE_NAME,
                "properties": {
                    "DishMasterFQDN": [DISH_DEVICE_NAME],
                    "SkaLevel": ["3"],
                    "TrackDuration": ["1"],
                    "LoggingTargetsDefault": ["tango::logger"],
                    "LoggingLevelDefault": ["5"],
                    "polled_attr": ["activitymessage", "1000", "healthstate", "1000"],
                },
            },
        ),
    },
]


@pytest.fixture(scope="function")
def leaf_dish_context(tango_context):
    tango_context.dish_leaf_node = tango_context.get_device(LEAF_NODE_DEVICE_NAME)
    tango_context.dish_master = tango_context.get_device(DISH_DEVICE_NAME)
    return tango_context


class TestDishLeafNode(object):
    def test_State(self, leaf_dish_context):
        assert leaf_dish_context.dish_leaf_node.State() == DevState.ALARM

    def test_Status(self, leaf_dish_context):
        assert leaf_dish_context.dish_leaf_node.Status() != const.STR_DISH_INIT_SUCCESS

    @pytest.mark.xfail
    def test_Reset(self, leaf_dish_context):
        assert leaf_dish_context.dish_leaf_node.Reset() is None

    def test_SetStandByLPMode(self, leaf_dish_context):
        leaf_dish_context.dish_leaf_node.SetStandByLPMode()
        assert leaf_dish_context.dish_leaf_node.activityMessage == (
            const.STR_SETSTANDBYLP_SUCCESS
        ) or (const.STR_DISH_STANDBYLP_MODE)

    def test_SetOperateMode(self, leaf_dish_context):
        leaf_dish_context.dish_leaf_node.SetOperateMode()
        assert leaf_dish_context.dish_leaf_node.activityMessage == (
            const.STR_SETOPERATE_SUCCESS
        ) or (const.STR_DISH_OPERATE_MODE)

    @pytest.mark.xfail
    def test_Track_invalid_radec(self, leaf_dish_context):
        input_string = '{"pointing":{"target":{"system":"ICRS","name":"Polaris","RA":"02:31:49.09","dec":"+89:15:50.79"}},"dish":{"receiverBand":"1"}}'
        leaf_dish_context.dish_leaf_node.Track(input_string)
        assert const.ERR_ELE_LIM in leaf_dish_context.dish_leaf_node.activityMessage
        leaf_dish_context.dish_master.TrackStop()

    @pytest.mark.xfail
    def test_Configure(self, leaf_dish_context):
        input_string = '{"pointing":{"target":{"system":"ICRS","name":"Polaris Australis","RA":"21:08:47.92","dec":"-88:57:22.9"}},"dish":{"receiverBand":"1"}}'
        leaf_dish_context.dish_leaf_node.Configure(input_string)
        assert leaf_dish_context.dish_leaf_node.activityMessage == (
            const.STR_CONFIGURE_SUCCESS
        ) or (const.STR_DISH_POINT_STATE_READY)

    def test_Configure_invalid_JSON(self, leaf_dish_context):
        input_string = '{"Invalid Key"}'
        with pytest.raises(tango.DevFailed):
            leaf_dish_context.dish_leaf_node.Configure(input_string)
        assert const.ERR_INVALID_JSON in leaf_dish_context.dish_leaf_node.activityMessage

    def test_Configure_invalid_arguments(self, leaf_dish_context):
        """Test for Configure_invalid_arguments  (Negative test case)"""
        input_string = []
        input_string.append(
            '{"pointing":{"target":{"system":"ICRS","name":"Polaris Australis","":"21:08:47.92","":"-88:5.7:22.9"}},"dish":{"receiverBand":"1"}}'
        )
        with pytest.raises(tango.DevFailed):
            leaf_dish_context.dish_leaf_node.Configure(input_string[0])
        assert const.ERR_JSON_KEY_NOT_FOUND in leaf_dish_context.dish_leaf_node.activityMessage

    @pytest.mark.xfail
    def test_Configure_generic_exception(self, leaf_dish_context):
        Configure_input = "[123]"
        with pytest.raises(tango.DevFailed):
            leaf_dish_context.dish_leaf_node.Configure(Configure_input)
        assert const.ERR_EXE_CONFIGURE_CMD in leaf_dish_context.dish_leaf_node.activityMessage

    @pytest.mark.xfail
    def test_Scan(self, leaf_dish_context):
        leaf_dish_context.dish_leaf_node.Scan("0")
        assert leaf_dish_context.dish_leaf_node.activityMessage == (const.STR_SCAN_SUCCESS) or (
            const.STR_DISH_POINT_STATE_SCAN
        )

    def test_Scan_invalid_arguments(self, leaf_dish_context):
        with pytest.raises(tango.DevFailed):
            leaf_dish_context.dish_leaf_node.Scan("a")
        assert const.ERR_EXE_SCAN_CMD in leaf_dish_context.dish_leaf_node.activityMessage

    @pytest.mark.xfail
    def test_EndScan(self, leaf_dish_context):
        leaf_dish_context.dish_leaf_node.EndScan("0")
        assert leaf_dish_context.dish_leaf_node.activityMessage == (const.STR_ENDSCAN_SUCCESS) or (
            const.STR_DISH_POINT_STATE_READY
        )

    def test_EndScan_invalid_arguments(self, leaf_dish_context):
        """Test for EndScan_invalid_arguments (Negative test case)"""
        with pytest.raises(tango.DevFailed):
            leaf_dish_context.dish_leaf_node.EndScan("a")
        assert const.ERR_EXE_END_SCAN_CMD in leaf_dish_context.dish_leaf_node.activityMessage

    @pytest.mark.xfail
    def test_StartCapture(self, leaf_dish_context):
        leaf_dish_context.dish_leaf_node.StartCapture("0")
        assert leaf_dish_context.dish_leaf_node.activityMessage == (
            const.STR_STARTCAPTURE_SUCCESS
        ) or (const.STR_DISH_POINT_STATE_SCAN)

    def test_StartCapture_invalid_arguments(self, leaf_dish_context):
        with pytest.raises(tango.DevFailed):
            leaf_dish_context.dish_leaf_node.StartCapture("a")
        assert const.ERR_EXE_START_CAPTURE_CMD in leaf_dish_context.dish_leaf_node.activityMessage

    @pytest.mark.xfail
    def test_StopCapture(self, leaf_dish_context):
        leaf_dish_context.dish_leaf_node.StopCapture("0")
        assert leaf_dish_context.dish_leaf_node.activityMessage == (
            const.STR_STOPCAPTURE_SUCCESS
        ) or (const.STR_DISH_POINT_STATE_READY)

    def test_StopCapture_invalid_arguments(self, leaf_dish_context):
        with pytest.raises(tango.DevFailed):
            leaf_dish_context.dish_leaf_node.StopCapture("a")
        assert const.ERR_EXE_STOP_CAPTURE_CMD in leaf_dish_context.dish_leaf_node.activityMessage

    def test_SetStandbyFPMode(self, leaf_dish_context):
        leaf_dish_context.dish_leaf_node.SetStandbyFPMode()
        assert leaf_dish_context.dish_leaf_node.activityMessage == (
            const.STR_STANDBYFP_SUCCESS
        ) or (const.STR_DISH_STANDBYFP_MODE)

    @pytest.mark.xfail
    def test_SetStowMode(self, leaf_dish_context):
        leaf_dish_context.dish_leaf_node.SetStandByLPMode()
        leaf_dish_context.dish_leaf_node.SetStowMode()
        assert (
            leaf_dish_context.dish_leaf_node.activityMessage == (const.STR_DISH_POINT_STATE_READY)
            or (const.STR_DISH_STOW_MODE)
            or (const.STR_DESIREDPOINTING_0_0)
            or (const.STR_ACHIEVEDPOINTING_0_0)
        )

    @pytest.mark.xfail
    def test_Slew(self, leaf_dish_context):
        leaf_dish_context.dish_leaf_node.SetStandByLPMode()
        leaf_dish_context.dish_leaf_node.Slew("0")
        assert leaf_dish_context.dish_leaf_node.activityMessage == const.STR_SLEW_SUCCESS

    def test_Slew_invalid_arguments(self, leaf_dish_context):
        leaf_dish_context.dish_leaf_node.SetStandByLPMode()
        with pytest.raises(tango.DevFailed):
            leaf_dish_context.dish_leaf_node.Slew("a")
        assert const.ERR_EXE_SLEW_CMD in leaf_dish_context.dish_leaf_node.activityMessage

    def test_Track_invalid_arg(self, leaf_dish_context):
        input_string = '{"pointing":{"target":{"system":"ICRS","name":"Polaris Australis","":"21:08:47.92","":"-88:57:22.9"}},"dish":{"receiverBand":"1"}}'
        with pytest.raises(tango.DevFailed):
            leaf_dish_context.dish_leaf_node.Track(input_string)
        assert const.ERR_JSON_KEY_NOT_FOUND in leaf_dish_context.dish_leaf_node.activityMessage
        leaf_dish_context.dish_leaf_node.SetStandByLPMode()

    def test_Track_invalid_JSON(self, leaf_dish_context):
        input_string = '{"Invalid Key"}'
        with pytest.raises(tango.DevFailed):
            leaf_dish_context.dish_leaf_node.Track(input_string)
        assert const.ERR_INVALID_JSON in leaf_dish_context.dish_leaf_node.activityMessage

    @pytest.mark.xfail
    def test_Track(self, leaf_dish_context):
        input_string = '{"pointing":{"target":{"system":"ICRS","name":"Polaris Australis","RA":"21:08:47.92","dec":"-88:57:22.9"}},"dish":{"receiverBand":"1"}}'
        leaf_dish_context.dish_leaf_node.Track(input_string)
        assert (
            leaf_dish_context.dish_master.pointingState == 1
            or leaf_dish_context.dish_master.pointingState == 2
        )
        leaf_dish_context.dish_master.TrackStop()

    @pytest.mark.xfail
    def test_TrackStop(self, leaf_dish_context):
        leaf_dish_context.dish_leaf_node.TrackStop()
        assert leaf_dish_context.dish_master.pointingState == 0

    @pytest.mark.xfail
    def test_buildState(self, leaf_dish_context):
        assert leaf_dish_context.dish_leaf_node.buildState == (
            "lmcbaseclasses, 0.6.3, A set of generic base devices for SKA Telescope."
        )

    @pytest.mark.xfail
    def test_versionId(self, leaf_dish_context):
        assert leaf_dish_context.dish_leaf_node.versionId == "0.6.3"

    def test_healthState(self, leaf_dish_context):
        assert leaf_dish_context.dish_leaf_node.healthState == HealthState.OK

    @pytest.mark.xfail
    def test_adminMode(self, leaf_dish_context):
        assert leaf_dish_context.dish_leaf_node.adminMode == AdminMode.ONLINE

    def test_controlMode(self, leaf_dish_context):
        control_mode = ControlMode.REMOTE
        leaf_dish_context.dish_leaf_node.controlMode = control_mode
        assert leaf_dish_context.dish_leaf_node.controlMode == control_mode

    def test_simulationMode(self, leaf_dish_context):
        simulation_mode = SimulationMode.FALSE
        leaf_dish_context.dish_leaf_node.simulationMode = simulation_mode
        assert leaf_dish_context.dish_leaf_node.simulationMode == simulation_mode

    def test_testMode(self, leaf_dish_context):
        test_mode = TestMode.NONE
        leaf_dish_context.dish_leaf_node.testMode = test_mode
        assert leaf_dish_context.dish_leaf_node.testMode == test_mode

    def test_activityMessage(self, leaf_dish_context):
        leaf_dish_context.dish_leaf_node.activityMessage = const.STR_OK
        assert leaf_dish_context.dish_leaf_node.activityMessage == const.STR_OK

    @pytest.mark.xfail
    def test_dishMode_change_event(self, leaf_dish_context):
        """Test for dishMode_change_event"""
        leaf_dish_context.dish_leaf_node.SetOperateMode()
        eid = leaf_dish_context.dish_master.subscribe_event(
            const.EVT_DISH_MODE, EventType.CHANGE_EVENT, DishLeafNode.dish_mode_cb
        )
        assert (
            leaf_dish_context.dish_leaf_node.activityMessage == const.STR_DISH_OPERATE_MODE
            or const.STR_SETOPERATE_SUCCESS
        )
        assert leaf_dish_context.dish_master.dishMode == "OPERATE" or 8
        leaf_dish_context.dish_master.unsubscribe_event(eid)

    @pytest.mark.xfail
    def test_achieved_pointingState_change_event(self, leaf_dish_context):
        leaf_dish_context.dish_leaf_node.Scan("0")
        eid = leaf_dish_context.dish_master.subscribe_event(
            const.EVT_DISH_POINTING_STATE,
            EventType.CHANGE_EVENT,
            DishLeafNode.dish_achieved_pointing_cb,
        )
        # assert leaf_dish_context.dish_leaf_node.activityMessage == const.STR_DISH_POINT_STATE_SCAN
        assert leaf_dish_context.dish_master.pointingState == "SCANNING" or 3
        leaf_dish_context.dish_master.unsubscribe_event(eid)

    @pytest.mark.xfail
    def test_capturing_change_event(self, leaf_dish_context):
        leaf_dish_context.dish_leaf_node.StopCapture("0")
        eid = leaf_dish_context.dish_master.subscribe_event(
            const.EVT_DISH_CAPTURING, EventType.CHANGE_EVENT, DishLeafNode.dish_capturing_cb
        )
        assert (
            leaf_dish_context.dish_leaf_node.activityMessage == (const.STR_DISH_CAPTURING_FALSE)
            or (const.STR_DISH_POINT_STATE_READY)
            or (const.STR_CAPTURE_EVENT)
        )
        assert leaf_dish_context.dish_master.capturing is False
        leaf_dish_context.dish_master.unsubscribe_event(eid)
        leaf_dish_context.dish_leaf_node.SetStandByLPMode()

    def test_loggingLevel(self, leaf_dish_context):
        leaf_dish_context.dish_leaf_node.loggingLevel = LoggingLevel.INFO
        assert leaf_dish_context.dish_leaf_node.loggingLevel == LoggingLevel.INFO

    def test_loggingTargets(self, leaf_dish_context):
        leaf_dish_context.dish_leaf_node.loggingTargets = ["tango::logger"]
        assert "tango::logger" in leaf_dish_context.dish_leaf_node.loggingTargets
