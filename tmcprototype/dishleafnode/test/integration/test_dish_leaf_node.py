#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=redefined-outer-name

"""Contain the tests for DishLeafNode."""
from __future__ import print_function

import pkg_resources
import mock
import time

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
from tango_simlib.tango_sim_generator import (
    configure_device_model,
    get_tango_device_server,
)

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
    def delay_successful_message_check(self, command_name, activityMessage):
        """Wait for the activity_message to contain the command name

        Parameters
        ----------
        command_name: String
            The command name like `Scan`

        activityMessage : String
            The dishleafnode activitymessage

        """
        for _ in range(5):
            time.sleep(0.5)
            if command_name in activityMessage:
                return

    def wait_for_attribute_change(self, original_value, attribute_to_check):
        """Keep checking for an attribute to change for a maximum of a few minutes

        Parameters
        ----------
        original_value : Any
            The original value that should change to something else in time
        attribute_to_check: Any
            The attribute to check
        """
        for _ in range(10):
            time.sleep(0.5)
            if original_value != attribute_to_check:
                return

    def wait_for_dish_mode(self, mode, dish):
        """Wait for dishmaster dishMode to get to `mode` for a few minutes at most

        Parameters
        ----------
        mode : String
            Like OPERATE
        dish : DeviceProxy
            dishmaster DeviceProxy
        """
        for _ in range(20):
            time.sleep(0.5)
            if mode in str(dish.dishMode):
                return
        assert 0, f"dishmaster did not go to mode {mode}, currently {str(dish.dishMode)}"

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
        leaf_dish_context.dish_leaf_node.SetStandbyFPMode()
        self.wait_for_dish_mode("STANDBY-FP", leaf_dish_context.dish_master)
        leaf_dish_context.dish_leaf_node.SetOperateMode()
        self.wait_for_dish_mode("OPERATE", leaf_dish_context.dish_master)
        assert leaf_dish_context.dish_leaf_node.activityMessage == (
            const.STR_SETOPERATE_SUCCESS
        ) or (const.STR_DISH_OPERATE_MODE)

    def test_Configure(self, leaf_dish_context):
        desiredPointing_before = leaf_dish_context.dish_master.desiredPointing
        configuredBand_before = leaf_dish_context.dish_master.configuredBand
        leaf_dish_context.dish_leaf_node.SetStandbyFPMode()
        self.wait_for_dish_mode("STANDBY-FP", leaf_dish_context.dish_master)
        input_string = '{"pointing":{"target":{"system":"ICRS","name":"Polaris Australis","RA":"21:08:47.92","dec":"-88:57:22.9"}},"dish":{"receiverBand":"1"}}'
        leaf_dish_context.dish_leaf_node.Configure(input_string)
        self.wait_for_attribute_change(
            configuredBand_before, leaf_dish_context.dish_master.configuredBand
        )
        assert desiredPointing_before[0] != leaf_dish_context.dish_master.desiredPointing[0]
        assert configuredBand_before != leaf_dish_context.dish_master.configuredBand

    def test_Scan(self, leaf_dish_context):
        leaf_dish_context.dish_leaf_node.SetStandbyFPMode()
        self.wait_for_dish_mode("STANDBY-FP", leaf_dish_context.dish_master)
        leaf_dish_context.dish_leaf_node.SetOperateMode()
        self.wait_for_dish_mode("OPERATE", leaf_dish_context.dish_master)
        leaf_dish_context.dish_leaf_node.Scan("0")
        self.delay_successful_message_check(
            "Scan", leaf_dish_context.dish_leaf_node.activityMessage
        )
        assert "Scan invoked successfully" in leaf_dish_context.dish_leaf_node.activityMessage

    def test_EndScan(self, leaf_dish_context):
        leaf_dish_context.dish_leaf_node.SetStandbyFPMode()
        leaf_dish_context.dish_leaf_node.SetOperateMode()
        self.wait_for_dish_mode("OPERATE", leaf_dish_context.dish_master)
        leaf_dish_context.dish_leaf_node.Scan("0")
        leaf_dish_context.dish_leaf_node.EndScan("0")
        self.delay_successful_message_check(
            "StopCapture", leaf_dish_context.dish_leaf_node.activityMessage
        )
        assert (
            "StopCapture invoked successfully" in leaf_dish_context.dish_leaf_node.activityMessage
        )

    def test_StartCapture(self, leaf_dish_context):
        leaf_dish_context.dish_leaf_node.SetStandbyFPMode()
        self.wait_for_dish_mode("STANDBY-FP", leaf_dish_context.dish_master)
        leaf_dish_context.dish_leaf_node.SetOperateMode()
        self.wait_for_dish_mode("OPERATE", leaf_dish_context.dish_master)
        leaf_dish_context.dish_leaf_node.StartCapture("0")
        self.delay_successful_message_check(
            "StartCapture", leaf_dish_context.dish_leaf_node.activityMessage
        )
        assert (
            "StartCapture invoked successfully" in leaf_dish_context.dish_leaf_node.activityMessage
        )

    def test_StopCapture(self, leaf_dish_context):
        leaf_dish_context.dish_leaf_node.SetStandbyFPMode()
        self.wait_for_dish_mode("STANDBY-FP", leaf_dish_context.dish_master)
        leaf_dish_context.dish_leaf_node.SetOperateMode()
        self.wait_for_dish_mode("OPERATE", leaf_dish_context.dish_master)
        leaf_dish_context.dish_leaf_node.StartCapture("0")
        leaf_dish_context.dish_leaf_node.StopCapture("0")
        self.delay_successful_message_check(
            "StopCapture", leaf_dish_context.dish_leaf_node.activityMessage
        )
        assert (
            "StopCapture invoked successfully" in leaf_dish_context.dish_leaf_node.activityMessage
        )

    def test_SetStowMode(self, leaf_dish_context):
        leaf_dish_context.dish_leaf_node.SetStowMode()
        self.delay_successful_message_check(
            "SetStowMode", leaf_dish_context.dish_leaf_node.activityMessage
        )
        assert (
            "SetStowMode invoked successfully" in leaf_dish_context.dish_leaf_node.activityMessage
        )

    # def test_Slew(self, leaf_dish_context):
    #     leaf_dish_context.dish_leaf_node.SetStandbyFPMode()
    #     self.wait_for_dish_mode("STANDBY-FP", leaf_dish_context.dish_master)
    #     leaf_dish_context.dish_leaf_node.SetOperateMode()
    #     self.wait_for_dish_mode("OPERATE", leaf_dish_context.dish_master)
    #     leaf_dish_context.dish_leaf_node.Slew("[10.0, 20.0]")
    #     self.delay_successful_message_check(
    #         "Slew", leaf_dish_context.dish_leaf_node.activityMessage)
    #     assert (
    #         "Slew invoked successfully" in leaf_dish_context.dish_leaf_node.activityMessage
    #     )

    def test_Track(self, leaf_dish_context):
        leaf_dish_context.dish_leaf_node.SetStandbyFPMode()
        leaf_dish_context.dish_leaf_node.SetOperateMode()
        self.wait_for_dish_mode("OPERATE", leaf_dish_context.dish_master)

        input_string = '{"pointing":{"target":{"system":"ICRS","name":"Polaris Australis","RA":"21:08:47.92","dec":"-88:57:22.9"}},"dish":{"receiverBand":"1"}}'
        leaf_dish_context.dish_leaf_node.Track(input_string)
        self.delay_successful_message_check(
            "Track", leaf_dish_context.dish_leaf_node.activityMessage
        )
        assert "Track invoked successfully" in leaf_dish_context.dish_leaf_node.activityMessage
        leaf_dish_context.dish_leaf_node.StopTrack()
        self.delay_successful_message_check(
            "StopTrack", leaf_dish_context.dish_leaf_node.activityMessage
        )
        assert "TrackStop invoked successfully" in leaf_dish_context.dish_leaf_node.activityMessage

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
        self.wait_for_dish_mode("STANDBY-FP", leaf_dish_context.dish_master)
        leaf_dish_context.dish_leaf_node.SetOperateMode()
        self.wait_for_dish_mode("OPERATE", leaf_dish_context.dish_master)
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

    def test_loggingLevel(self, leaf_dish_context):
        leaf_dish_context.dish_leaf_node.loggingLevel = LoggingLevel.INFO
        assert leaf_dish_context.dish_leaf_node.loggingLevel == LoggingLevel.INFO

    def test_loggingTargets(self, leaf_dish_context):
        leaf_dish_context.dish_leaf_node.loggingTargets = ["tango::logger"]
        assert "tango::logger" in leaf_dish_context.dish_leaf_node.loggingTargets
