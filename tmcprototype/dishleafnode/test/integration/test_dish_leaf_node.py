#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=redefined-outer-name

"""Contain the tests for DishLeafNode."""
from __future__ import print_function

import pkg_resources
import mock

import tango
import pytest

from tango import DevState, EventType
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
from tango_simlib.tango_sim_generator import configure_device_model, get_tango_device_server

DISH_DEVICE_NAME = "mid_d0001/nodb/master"
LEAF_NODE_DEVICE_NAME = "test/tm_leaf_node/d0001"
FGO_FILE_PATH = pkg_resources.resource_filename("dishmaster", "dish_master.fgo")
JSON_FILE_PATH = pkg_resources.resource_filename("dishmaster", "dish_master_SimDD.json")


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
    data_descr_files.append(FGO_FILE_PATH)
    data_descr_files.append(JSON_FILE_PATH)
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

    # @pytest.mark.xfail
    # def test_Configure(self, leaf_dish_context):
    #     input_string = '{"pointing":{"target":{"system":"ICRS","name":"Polaris Australis","RA":"21:08:47.92","dec":"-88:57:22.9"}},"dish":{"receiverBand":"1"}}'
    #     leaf_dish_context.dish_leaf_node.Configure(input_string)
    #     assert leaf_dish_context.dish_leaf_node.activityMessage == (
    #         const.STR_CONFIGURE_SUCCESS
    #     ) or (const.STR_DISH_POINT_STATE_READY)

    # def test_Configure_invalid_JSON(self, leaf_dish_context):
    #     input_string = '{"Invalid Key"}'
    #     with pytest.raises(tango.DevFailed):
    #         leaf_dish_context.dish_leaf_node.Configure(input_string)
    #     assert const.ERR_INVALID_JSON in leaf_dish_context.dish_leaf_node.activityMessage

    # def test_Configure_invalid_arguments(self, leaf_dish_context):
    #     """Test for Configure_invalid_arguments  (Negative test case)"""
    #     input_string = []
    #     input_string.append(
    #         '{"pointing":{"target":{"system":"ICRS","name":"Polaris Australis","":"21:08:47.92","":"-88:5.7:22.9"}},"dish":{"receiverBand":"1"}}'
    #     )
    #     with pytest.raises(tango.DevFailed):
    #         leaf_dish_context.dish_leaf_node.Configure(input_string[0])
    #     assert const.ERR_JSON_KEY_NOT_FOUND in leaf_dish_context.dish_leaf_node.activityMessage

    # @pytest.mark.xfail
    # def test_Configure_generic_exception(self, leaf_dish_context):
    #     Configure_input = "[123]"
    #     with pytest.raises(tango.DevFailed):
    #         leaf_dish_context.dish_leaf_node.Configure(Configure_input)
    #     assert const.ERR_EXE_CONFIGURE_CMD in leaf_dish_context.dish_leaf_node.activityMessage

    def test_Scan(self, leaf_dish_context):
        leaf_dish_context.dish_leaf_node.SetStandbyFPMode()
        leaf_dish_context.dish_leaf_node.SetOperateMode()
        leaf_dish_context.dish_leaf_node.Scan("0")
        assert "Scan invoked successfully" in leaf_dish_context.dish_leaf_node.activityMessage

    def test_EndScan(self, leaf_dish_context):
        leaf_dish_context.dish_leaf_node.SetStandbyFPMode()
        leaf_dish_context.dish_leaf_node.SetOperateMode()
        leaf_dish_context.dish_leaf_node.Scan("0")
        leaf_dish_context.dish_leaf_node.EndScan("0")
        assert (
            "StopCapture invoked successfully" in leaf_dish_context.dish_leaf_node.activityMessage
        )

    def test_StartCapture(self, leaf_dish_context):
        leaf_dish_context.dish_leaf_node.SetStandbyFPMode()
        leaf_dish_context.dish_leaf_node.SetOperateMode()
        leaf_dish_context.dish_leaf_node.StartCapture("0")
        assert (
            "StartCapture invoked successfully" in leaf_dish_context.dish_leaf_node.activityMessage
        )

    def test_StopCapture(self, leaf_dish_context):
        leaf_dish_context.dish_leaf_node.SetStandbyFPMode()
        leaf_dish_context.dish_leaf_node.SetOperateMode()
        leaf_dish_context.dish_leaf_node.StartCapture("0")
        leaf_dish_context.dish_leaf_node.StopCapture("0")
        assert (
            "StopCapture invoked successfully" in leaf_dish_context.dish_leaf_node.activityMessage
        )

    def test_SetStowMode(self, leaf_dish_context):
        leaf_dish_context.dish_leaf_node.SetStandByLPMode()
        leaf_dish_context.dish_leaf_node.SetStowMode()
        assert (
            "SetStowMode invoked successfully" in leaf_dish_context.dish_leaf_node.activityMessage
        )

    # @pytest.mark.xfail
    # def test_Slew(self, leaf_dish_context):
    #     leaf_dish_context.dish_leaf_node.SetStandByLPMode()
    #     leaf_dish_context.dish_leaf_node.Slew("0")
    #     assert leaf_dish_context.dish_leaf_node.activityMessage == const.STR_SLEW_SUCCESS

    # @pytest.mark.xfail
    # def test_Slew_invalid_arguments(self, leaf_dish_context):
    #     leaf_dish_context.dish_leaf_node.SetStandByLPMode()
    #     with pytest.raises(tango.DevFailed):
    #         leaf_dish_context.dish_leaf_node.Slew("a")
    #     assert const.ERR_EXE_SLEW_CMD in leaf_dish_context.dish_leaf_node.activityMessage

    # def test_Track_invalid_arg(self, leaf_dish_context):
    #     input_string = '{"pointing":{"target":{"system":"ICRS","name":"Polaris Australis","":"21:08:47.92","":"-88:57:22.9"}},"dish":{"receiverBand":"1"}}'
    #     with pytest.raises(tango.DevFailed):
    #         leaf_dish_context.dish_leaf_node.Track(input_string)
    #     assert const.ERR_JSON_KEY_NOT_FOUND in leaf_dish_context.dish_leaf_node.activityMessage
    #     leaf_dish_context.dish_leaf_node.SetStandByLPMode()

    # def test_Track_invalid_JSON(self, leaf_dish_context):
    #     input_string = '{"Invalid Key"}'
    #     with pytest.raises(tango.DevFailed):
    #         leaf_dish_context.dish_leaf_node.Track(input_string)
    #     assert const.ERR_INVALID_JSON in leaf_dish_context.dish_leaf_node.activityMessage

    # @pytest.mark.xfail
    # def test_Track(self, leaf_dish_context):
    #     input_string = '{"pointing":{"target":{"system":"ICRS","name":"Polaris Australis","RA":"21:08:47.92","dec":"-88:57:22.9"}},"dish":{"receiverBand":"1"}}'
    #     leaf_dish_context.dish_leaf_node.Track(input_string)
    #     assert (
    #         leaf_dish_context.dish_master.pointingState == 1
    #         or leaf_dish_context.dish_master.pointingState == 2
    #     )
    #     leaf_dish_context.dish_master.TrackStop()

    # @pytest.mark.xfail
    # def test_TrackStop(self, leaf_dish_context):
    #     leaf_dish_context.dish_leaf_node.TrackStop()
    #     assert leaf_dish_context.dish_master.pointingState == 0

    def test_healthState(self, leaf_dish_context):
        assert leaf_dish_context.dish_leaf_node.healthState == HealthState.OK

    def test_adminMode(self, leaf_dish_context):
        assert leaf_dish_context.dish_leaf_node.adminMode == AdminMode.MAINTENANCE

    def test_controlMode(self, leaf_dish_context):
        leaf_dish_context.dish_leaf_node.controlMode = ControlMode.REMOTE
        assert leaf_dish_context.dish_leaf_node.controlMode == ControlMode.REMOTE

    def test_simulationMode(self, leaf_dish_context):
        leaf_dish_context.dish_leaf_node.simulationMode = SimulationMode.FALSE
        assert leaf_dish_context.dish_leaf_node.simulationMode == SimulationMode.FALSE

    def test_testMode(self, leaf_dish_context):
        leaf_dish_context.dish_leaf_node.testMode = TestMode.NONE
        assert leaf_dish_context.dish_leaf_node.testMode == TestMode.NONE

    def test_dishMode_change_event(self, leaf_dish_context):
        leaf_dish_context.dish_leaf_node.SetStandbyFPMode()
        leaf_dish_context.dish_leaf_node.SetOperateMode()
        mock_cb = mock.MagicMock()
        eid = leaf_dish_context.dish_master.subscribe_event(
            const.EVT_DISH_MODE, EventType.CHANGE_EVENT, mock_cb
        )
        assert (
            "SetOperateMode invoked successfully"
            in leaf_dish_context.dish_leaf_node.activityMessage
        )
        assert leaf_dish_context.dish_master.dishMode == "OPERATE" or 8
        mock_cb.assert_called()
        leaf_dish_context.dish_master.unsubscribe_event(eid)

    # @pytest.mark.xfail
    # def test_capturing_change_event(self, leaf_dish_context):
    #     mock_cb = mock.MagicMock()
    #     eid = leaf_dish_context.dish_master.subscribe_event(
    #         const.EVT_DISH_CAPTURING, EventType.CHANGE_EVENT, mock_cb
    #     )
    #     leaf_dish_context.dish_leaf_node.SetStandbyFPMode()
    #     leaf_dish_context.dish_leaf_node.SetOperateMode()
    #     leaf_dish_context.dish_leaf_node.StartCapture("0")
    #     leaf_dish_context.dish_leaf_node.StopCapture("0")
    #     assert "StopCapture invoked successfully" in leaf_dish_context.dish_leaf_node.activityMessage
    #     assert leaf_dish_context.dish_master.capturing == False
    #     mock_cb.assert_called()
    #     leaf_dish_context.dish_master.unsubscribe_event(eid)

    def test_loggingLevel(self, leaf_dish_context):
        leaf_dish_context.dish_leaf_node.loggingLevel = LoggingLevel.INFO
        assert leaf_dish_context.dish_leaf_node.loggingLevel == LoggingLevel.INFO

    def test_loggingTargets(self, leaf_dish_context):
        leaf_dish_context.dish_leaf_node.loggingTargets = ["tango::logger"]
        assert "tango::logger" in leaf_dish_context.dish_leaf_node.loggingTargets
