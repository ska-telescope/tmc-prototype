#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=redefined-outer-name

"""Contain the tests for DishLeafNode."""
from __future__ import print_function

import pkg_resources
from unittest import mock
import time
import pytest

from tango import EventType
from dishleafnode import DishLeafNode
from dishleafnode.utils import PointingState
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

    :param DISH_DEVICE_NAME: string
        The Tango device name
    :return DishMaster: tango.server.Device
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
                    "polled_attr": [
                        "activitymessage",
                        "1000",
                        "healthstate",
                        "1000",
                        "capturing",
                        "1000",
                        "achievedPointing",
                        "1000",
                        "desiredPointing",
                        "1000",
                        "dishMode",
                        "1000",
                    ],
                },
            },
        ),
    },
]


@pytest.fixture(scope="function")
def dish_leaf_node_dp(tango_context):
    dish_leaf_node = tango_context.get_device(LEAF_NODE_DEVICE_NAME)
    return dish_leaf_node


@pytest.fixture(scope="function")
def dish_master_dp(tango_context):
    dish_master = tango_context.get_device(DISH_DEVICE_NAME)
    return dish_master


class TestDishLeafNode:
    def wait_for_attribute_change(self, original_value, attribute_to_check):
        """Keep checking for an attribute to change for a maximum of a few minutes

        :param original_value: Any
            The original value that should change to something else in time
        :param attribute_to_check: Any
            The attribute to check
        """
        for _ in range(10):
            time.sleep(0.5)
            if original_value != attribute_to_check:
                return

    def wait_until_dish_mode_equals(self, mode, dish):
        """Wait for dishmaster dishMode to get to `mode` for a few minutes at most

        :param mode : String
            Like OPERATE
        :param dish : DeviceProxy
            dishmaster DeviceProxy
        """
        for _ in range(20):
            time.sleep(0.5)
            if mode in str(dish.dishMode):
                return
        assert 0, f"dishmaster did not go to mode {mode}, currently {str(dish.dishMode)}"

    def test_SetStandByLPMode(self, dish_master_dp):
        assert dish_master_dp.dishMode.name == "STANDBY-LP"

    def test_SetOperateMode(self, dish_leaf_node_dp, dish_master_dp):
        dish_leaf_node_dp.SetStandbyFPMode()
        self.wait_until_dish_mode_equals("STANDBY-FP", dish_master_dp)
        dish_leaf_node_dp.SetOperateMode()
        self.wait_until_dish_mode_equals("OPERATE", dish_master_dp)
        assert dish_master_dp.dishMode.name == "OPERATE"

    def test_Configure(self, dish_leaf_node_dp, dish_master_dp):
        previous_timestamp = dish_master_dp.desiredPointing[0]
        previous_configuredBand = dish_master_dp.configuredBand
        dish_leaf_node_dp.SetStandbyFPMode()
        self.wait_until_dish_mode_equals("STANDBY-FP", dish_master_dp)
        input_string = '{"pointing":{"target":{"system":"ICRS","name":"Polaris Australis","RA":"21:08:47.92","dec":"-88:57:22.9"}},"dish":{"receiverBand":"1"}}'
        dish_leaf_node_dp.Configure(input_string)
        self.wait_for_attribute_change(previous_configuredBand, dish_master_dp.configuredBand)
        assert dish_master_dp.desiredPointing[0] != previous_timestamp
        assert dish_master_dp.configuredBand != previous_configuredBand
        assert dish_master_dp.dsIndexerPosition != previous_configuredBand

    def test_Scan(self, dish_leaf_node_dp, dish_master_dp):
        dish_leaf_node_dp.SetStandbyFPMode()
        self.wait_until_dish_mode_equals("STANDBY-FP", dish_master_dp)
        dish_leaf_node_dp.SetOperateMode()
        self.wait_until_dish_mode_equals("OPERATE", dish_master_dp)
        dish_leaf_node_dp.Scan("0")
        assert dish_master_dp.pointingState == PointingState.SCAN

    def test_EndScan(self, dish_leaf_node_dp, dish_master_dp):
        dish_leaf_node_dp.SetStandbyFPMode()
        self.wait_until_dish_mode_equals("STANDBY-FP", dish_master_dp)
        dish_leaf_node_dp.SetOperateMode()
        self.wait_until_dish_mode_equals("OPERATE", dish_master_dp)
        dish_leaf_node_dp.Scan("0")
        assert dish_master_dp.pointingState == PointingState.SCAN
        dish_leaf_node_dp.EndScan("0")
        self.wait_for_attribute_change(PointingState.SCAN, dish_master_dp.pointingState)
        assert not dish_master_dp.capturing
        assert dish_master_dp.pointingState == PointingState.READY

    def test_StartCapture(self, dish_leaf_node_dp, dish_master_dp):
        dish_leaf_node_dp.SetStandbyFPMode()
        self.wait_until_dish_mode_equals("STANDBY-FP", dish_master_dp)
        dish_leaf_node_dp.SetOperateMode()
        self.wait_until_dish_mode_equals("OPERATE", dish_master_dp)
        dish_leaf_node_dp.StartCapture("0")
        assert dish_master_dp.capturing

    def test_StopCapture(self, dish_leaf_node_dp, dish_master_dp):
        dish_leaf_node_dp.SetStandbyFPMode()
        self.wait_until_dish_mode_equals("STANDBY-FP", dish_master_dp)
        dish_leaf_node_dp.SetOperateMode()
        self.wait_until_dish_mode_equals("OPERATE", dish_master_dp)
        dish_leaf_node_dp.StartCapture("0")
        previous_capturing = dish_master_dp.capturing
        dish_leaf_node_dp.StopCapture("0")
        self.wait_for_attribute_change(previous_capturing, dish_master_dp.capturing)
        assert not dish_master_dp.capturing

    def test_SetStowMode(self, dish_leaf_node_dp, dish_master_dp):
        dish_leaf_node_dp.SetStowMode()
        assert dish_master_dp.dishmode.name == "STOW"

    def test_Slew(self, dish_leaf_node_dp, dish_master_dp):
        dish_leaf_node_dp.SetStandbyFPMode()
        self.wait_until_dish_mode_equals("STANDBY-FP", dish_master_dp)
        dish_leaf_node_dp.SetOperateMode()
        self.wait_until_dish_mode_equals("OPERATE", dish_master_dp)
        dish_leaf_node_dp.Slew([10.0, 20.0])
        assert dish_master_dp.pointingState.name == "SLEW"

    def test_Track(self, dish_leaf_node_dp, dish_master_dp):
        dish_leaf_node_dp.SetStandbyFPMode()
        dish_leaf_node_dp.SetOperateMode()
        self.wait_until_dish_mode_equals("OPERATE", dish_master_dp)

        input_string = '{"pointing":{"target":{"system":"ICRS","name":"Polaris Australis","RA":"21:08:47.92","dec":"-88:57:22.9"}},"dish":{"receiverBand":"1"}}'
        dish_leaf_node_dp.Track(input_string)
        assert dish_master_dp.pointingState == PointingState.TRACK

        dish_leaf_node_dp.StopTrack()
        assert dish_master_dp.pointingState == PointingState.READY

    def test_dishMode_change_event(self, dish_leaf_node_dp, dish_master_dp):
        dish_leaf_node_dp.SetStandbyFPMode()
        self.wait_until_dish_mode_equals("STANDBY-FP", dish_master_dp)
        dish_leaf_node_dp.SetOperateMode()
        self.wait_until_dish_mode_equals("OPERATE", dish_master_dp)
        mock_cb = mock.MagicMock()
        eid = dish_master_dp.subscribe_event("dishMode", EventType.CHANGE_EVENT, mock_cb)
        assert dish_master_dp.dishMode.name == "OPERATE"
        mock_cb.assert_called()
        dish_master_dp.unsubscribe_event(eid)
