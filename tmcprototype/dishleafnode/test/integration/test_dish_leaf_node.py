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
from dishleafnode.utils import DishMode, PointingState
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
    def wait_until_dish_attribute_equals(self, attribute_value, attribute_name, dish_proxy):
        """Wait for dishmaster attribute to get to change to a different value for a few minutes at most

        :param attribute_value : any
            Like OPERATE
        :param attribute_name : String
        :param dish : DeviceProxy
            dishmaster DeviceProxy
        """
        current_value = None
        for _ in range(20):
            time.sleep(0.5)
            current_value = dish_proxy.read_attribute(attribute_name).value
            if attribute_value == current_value:
                return
        assert (
            0
        ), f"dishmaster attribute '{attribute_name}' did not change to {attribute_value}, currently {current_value}"

    def _set_dish_to_operate_mode(self, leaf_proxy, dish_proxy):
        leaf_proxy.SetStandbyFPMode()
        self.wait_until_dish_attribute_equals(DishMode.STANDBY_FP, "dishMode", dish_proxy)
        leaf_proxy.SetOperateMode()
        self.wait_until_dish_attribute_equals(DishMode.OPERATE, "dishMode", dish_proxy)

    def test_SetStandByLPMode(self, dish_master_dp):
        assert dish_master_dp.dishMode.name == "STANDBY-LP"

    def test_SetOperateMode(self, dish_leaf_node_dp, dish_master_dp):
        dish_leaf_node_dp.SetStandbyFPMode()
        self.wait_until_dish_attribute_equals(DishMode.STANDBY_FP, "dishMode", dish_master_dp)
        dish_leaf_node_dp.SetOperateMode()
        self.wait_until_dish_attribute_equals(DishMode.OPERATE, "dishMode", dish_master_dp)
        assert dish_master_dp.dishMode.name == "OPERATE"

    def test_Configure(self, dish_leaf_node_dp, dish_master_dp):
        previous_timestamp = dish_master_dp.desiredPointing[0]
        dish_leaf_node_dp.SetStandbyFPMode()
        self.wait_until_dish_attribute_equals(DishMode.STANDBY_FP, "dishMode", dish_master_dp)
        input_string = '{"pointing":{"target":{"system":"ICRS","name":"Polaris Australis","RA":"21:08:47.92","dec":"-88:57:22.9"}},"dish":{"receiverBand":"1"}}'
        dish_leaf_node_dp.Configure(input_string)
        # '1' here represents 'B1' in the configuredBand enum labels
        self.wait_until_dish_attribute_equals(1, "configuredBand", dish_master_dp)
        assert dish_master_dp.desiredPointing[0] != previous_timestamp
        assert dish_master_dp.configuredBand.name == "B1"
        assert dish_master_dp.dsIndexerPosition.name == "B1"

    def test_Scan(self, dish_leaf_node_dp, dish_master_dp):
        self._set_dish_to_operate_mode(dish_leaf_node_dp, dish_master_dp)
        dish_leaf_node_dp.Scan("0")
        assert dish_master_dp.pointingState == PointingState.SCAN

    def test_EndScan(self, dish_leaf_node_dp, dish_master_dp):
        self._set_dish_to_operate_mode(dish_leaf_node_dp, dish_master_dp)
        dish_leaf_node_dp.Scan("0")
        self.wait_until_dish_attribute_equals(PointingState.SCAN, "pointingState", dish_master_dp)
        assert dish_master_dp.pointingState == PointingState.SCAN
        dish_leaf_node_dp.EndScan("0")
        self.wait_until_dish_attribute_equals(PointingState.READY, "pointingState", dish_master_dp)
        assert not dish_master_dp.capturing
        assert dish_master_dp.pointingState == PointingState.READY

    def test_StartCapture(self, dish_leaf_node_dp, dish_master_dp):
        self._set_dish_to_operate_mode(dish_leaf_node_dp, dish_master_dp)
        dish_leaf_node_dp.StartCapture("0")
        assert dish_master_dp.capturing

    def test_StopCapture(self, dish_leaf_node_dp, dish_master_dp):
        self._set_dish_to_operate_mode(dish_leaf_node_dp, dish_master_dp)
        dish_leaf_node_dp.StartCapture("0")
        assert dish_master_dp.capturing
        dish_leaf_node_dp.StopCapture("0")
        assert not dish_master_dp.capturing

    def test_SetStowMode(self, dish_leaf_node_dp, dish_master_dp):
        dish_leaf_node_dp.SetStowMode()
        assert dish_master_dp.dishmode.name == "STOW"

    def test_Slew(self, dish_leaf_node_dp, dish_master_dp):
        self._set_dish_to_operate_mode(dish_leaf_node_dp, dish_master_dp)
        dish_leaf_node_dp.Slew([10.0, 20.0])
        assert dish_master_dp.pointingState.name == "SLEW"

    def test_Track(self, dish_leaf_node_dp, dish_master_dp):
        self._set_dish_to_operate_mode(dish_leaf_node_dp, dish_master_dp)
        input_string = '{"pointing":{"target":{"system":"ICRS","name":"Polaris Australis","RA":"21:08:47.92","dec":"-88:57:22.9"}},"dish":{"receiverBand":"1"}}'
        dish_leaf_node_dp.Track(input_string)
        assert dish_master_dp.pointingState == PointingState.TRACK
        dish_leaf_node_dp.StopTrack()
        assert dish_master_dp.pointingState == PointingState.READY

    def test_Restart(self, dish_leaf_node_dp, dish_master_dp):
        self._set_dish_to_operate_mode(dish_leaf_node_dp, dish_master_dp)
        dish_leaf_node_dp.Restart()
        assert dish_master_dp.pointingState.name == "READY"
        assert not dish_master_dp.capturing

    def test_dishMode_change_event(self, dish_leaf_node_dp, dish_master_dp):
        self._set_dish_to_operate_mode(dish_leaf_node_dp, dish_master_dp)
        mock_cb = mock.MagicMock()
        eid = dish_master_dp.subscribe_event("dishMode", EventType.CHANGE_EVENT, mock_cb)
        assert dish_master_dp.dishMode.name == "OPERATE"
        mock_cb.assert_called()
        dish_master_dp.unsubscribe_event(eid)
