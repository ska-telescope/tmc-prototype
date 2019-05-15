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

# Path
import sys
import os
file_path = os.path.dirname(os.path.abspath(__file__))
module_path = os.path.abspath(os.path.join(file_path, os.pardir)) + "/DishLeafNode"
sys.path.insert(0, module_path)

path = os.path.join(os.path.dirname(__file__), os.pardir)
sys.path.insert(0, os.path.abspath(path))

# Imports
import time
import tango
from tango import DevState, EventType
import pytest
from DishLeafNode.DishLeafNode import DishLeafNode
import CONST
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
@pytest.mark.usefixtures("tango_context", "initialize_device", "create_dish_proxy")

class TestDishLeafNode(object):
    """Test case for packet generation."""
    # PROTECTED REGION ID(DishLeafNode.test_additionnal_import) ENABLED START #
    # PROTECTED REGION END #    //  DishLeafNode.test_additionnal_import
    device = DishLeafNode
    properties = {'SkaLevel': '4', 'MetricList': 'healthState', 'GroupDefinitions': '',
                  'CentralLoggingTarget': '', 'ElementLoggingTarget': '', 'StorageLoggingTarget': 'localhost',
                  'DishMasterFQDN': 'tango://apurva-pc:10000/mid_d0001/elt/master','TrackDuration': 1,
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

    def test_State(self, tango_context): #, dishmaster_context):
        """Test for State"""
        # PROTECTED REGION ID(DishLeafNode.test_State) ENABLED START #
        assert tango_context.device.State() == DevState.ALARM
        # PROTECTED REGION END #    //  DishLeafNode.test_State

    def test_Status(self, tango_context): #, dishmaster_context):
        """Test for Status"""
        # PROTECTED REGION ID(DishLeafNode.test_Status) ENABLED START #
        assert tango_context.device.Status() != CONST.STR_DISH_INIT_SUCCESS
        # PROTECTED REGION END #    //  DishLeafNode.test_Status

    def test_GetMetrics(self, tango_context):
        """Test for GetMetrics"""
        # PROTECTED REGION ID(DishLeafNode.test_GetMetrics) ENABLED START #
        # PROTECTED REGION END #    //  DishLeafNode.test_GetMetrics

    def test_ToJson(self, tango_context):
        """Test for ToJson"""
        # PROTECTED REGION ID(DishLeafNode.test_ToJson) ENABLED START #
        # PROTECTED REGION END #    //  DishLeafNode.test_ToJson

    def test_GetVersionInfo(self, tango_context):
        """Test for GetVersionInfo"""
        # PROTECTED REGION ID(DishLeafNode.test_GetVersionInfo) ENABLED START #
        # PROTECTED REGION END #    //  DishLeafNode.test_GetVersionInfo

    def test_Reset(self, tango_context): #, dishmaster_context):
        """Test for Reset"""
        # PROTECTED REGION ID(DishLeafNode.test_Reset) ENABLED START #
        assert tango_context.device.Reset() is None
        # PROTECTED REGION END #    //  DishLeafNode.test_Reset

    def test_SetStandByLPMode(self, tango_context):
        """Test for SetStandByLPMode"""
        # PROTECTED REGION ID(DishLeafNode.test_SetStandByLPMode) ENABLED START #
        tango_context.device.SetStandByLPMode()
        time.sleep(4)
        assert tango_context.device.activityMessage == CONST.STR_SETSTANDBYLP_SUCCESS
        # PROTECTED REGION END #    //  DishLeafNode.test_SetStandByLPMode

    def test_SetOperateMode(self, tango_context, create_dish_proxy):
        """Test for SetOperateMode"""
        # PROTECTED REGION ID(DishLeafNode.test_SetOperateMode) ENABLED START #
        tango_context.device.SetOperateMode()
        time.sleep(2)
        assert tango_context.device.activityMessage == (CONST.STR_SETOPERATE_SUCCESS) or \
               (CONST.STR_DISH_OPERATE_MODE)
        # PROTECTED REGION END #    //  DishLeafNode.test_SetOperateMode

    def test_Configure(self, tango_context):
        """Test for Configure"""
        # PROTECTED REGION ID(DishLeafNode.test_Configure) ENABLED START #

        # tango_context.device.Configure(["Moon | moon, radec, 06: 52:09.64, 21: 13:41.6"])
        # time.sleep(2)
        # assert tango_context.device.activityMessage == CONST.STR_TARGET_NOT_OBSERVED

        tango_context.device.Configure(["radec, 2:31:50.88, 89:15:51.4", '2019-02-18 11:17:00'])
        # tango_context.device.Configure(['1','0'])
        time.sleep(25)
        assert tango_context.device.activityMessage == (CONST.STR_CONFIGURE_SUCCESS) or \
               (CONST.STR_DISH_POINT_STATE_READY)
        # PROTECTED REGION END #    //  DishLeafNode.test_Configure

    def test_Configure_invalid_arguments(self, tango_context):
        """Test for Configure_invalid_arguments"""
        tango_context.device.Configure(["Polaris | polaris, 2:31:50.88, 89:15:51.4", '2019-02-18 11:17:00'])
        print(tango_context.device.activityMessage)
        assert CONST.ERR_RADEC_TO_AZEL_VAL_ERR in tango_context.device.activityMessage

    def test_Scan(self, tango_context):
        """Test for Scan"""
        # PROTECTED REGION ID(DishLeafNode.test_Scan) ENABLED START #
        tango_context.device.Scan("0")
        time.sleep(2)
        assert tango_context.device.activityMessage == (CONST.STR_SCAN_SUCCESS) or \
               (CONST.STR_DISH_POINT_STATE_SCAN)
        # PROTECTED REGION END #    //  DishLeafNode.test_Scan

    def test_Scan_invalid_arguments(self, tango_context):
        """Test for Scan_invalid_arguments"""
        tango_context.device.Scan("a")
        assert CONST.ERR_EXE_SCAN_CMD in tango_context.device.activityMessage

    def test_EndScan(self, tango_context):
        """Test for EndScan"""
        # PROTECTED REGION ID(DishLeafNode.test_EndScan) ENABLED START #
        tango_context.device.EndScan("0")
        time.sleep(2)
        assert tango_context.device.activityMessage == (CONST.STR_ENDSCAN_SUCCESS) or \
               (CONST.STR_DISH_POINT_STATE_READY)
        # PROTECTED REGION END #    //  DishLeafNode.test_EndScan

    def test_EndScan_invalid_arguments(self, tango_context):
        """Test for EndScan_invalid_arguments"""
        tango_context.device.EndScan("a")
        assert CONST.ERR_EXE_END_SCAN_CMD in tango_context.device.activityMessage

    def test_StartCapture(self, tango_context):
        """Test for StartCapture"""
        # PROTECTED REGION ID(DishLeafNode.test_StartCapture) ENABLED START #
        tango_context.device.StartCapture("0")
        time.sleep(2)
        assert tango_context.device.activityMessage == (CONST.STR_STARTCAPTURE_SUCCESS) or \
               (CONST.STR_DISH_POINT_STATE_SCAN)
        # PROTECTED REGION END #    //  DishLeafNode.test_StartCapture

    def test_StartCapture_invalid_arguments(self, tango_context):
        """Test for StartCapture_invalid_arguments"""
        tango_context.device.StartCapture("a")
        assert CONST.ERR_EXE_START_CAPTURE_CMD in tango_context.device.activityMessage

    def test_StopCapture(self, tango_context):
        """Test for StopCapture"""
        # PROTECTED REGION ID(DishLeafNode.test_StopCapture) ENABLED START #
        tango_context.device.StopCapture("0")
        time.sleep(2)
        assert tango_context.device.activityMessage == (CONST.STR_STOPCAPTURE_SUCCESS) or \
               (CONST.STR_DISH_POINT_STATE_READY)
        # PROTECTED REGION END #    //  DishLeafNode.test_StopCapture

    def test_StopCapture_invalid_arguments(self, tango_context):
        """Test for StopCapture_invalid_arguments"""
        tango_context.device.StopCapture("a")
        assert CONST.ERR_EXE_STOP_CAPTURE_CMD in tango_context.device.activityMessage

    def test_SetStandbyFPMode(self, tango_context):
        """Test for SetStandbyFPMode"""
        # PROTECTED REGION ID(DishLeafNode.test_SetStandbyFPMode) ENABLED START #
        tango_context.device.SetStandbyFPMode()
        time.sleep(2)
        print(tango_context.device.activityMessage)
        assert tango_context.device.activityMessage == (CONST.STR_STANDBYFP_SUCCESS) or \
               (CONST.STR_DISH_STANDBYFP_MODE)
        # PROTECTED REGION END #    //  DishLeafNode.test_SetStandbyFPMode

    def test_SetStowMode(self, tango_context):
        """Test for SetStowMode"""
        # PROTECTED REGION ID(DishLeafNode.test_SetStowMode) ENABLED START #
        tango_context.device.SetStandByLPMode()
        tango_context.device.SetStowMode()
        time.sleep(50)
        assert tango_context.device.activityMessage == (CONST.STR_DISH_POINT_STATE_READY) or \
               (CONST.STR_DISH_STOW_MODE) or (CONST.STR_DESIREDPOINTING_0_0) or \
               (CONST.STR_ACHIEVEDPOINTING_0_0)
        # PROTECTED REGION END #    //  DishLeafNode.test_SetStowMode

    def test_Slew(self, tango_context):
        """Test for Slew"""
        # PROTECTED REGION ID(DishLeafNode.test_Slew) ENABLED START #
        tango_context.device.SetStandByLPMode()
        time.sleep(4)
        tango_context.device.Slew("0")
        time.sleep(8)
        assert tango_context.device.activityMessage == CONST.STR_SLEW_SUCCESS

    def test_Slew_invalid_arguments(self, tango_context):
        """Test for Slew_invalid_arguments"""
        tango_context.device.SetStandByLPMode()
        time.sleep(4)
        tango_context.device.Slew("a")
        assert CONST.ERR_EXE_SLEW_CMD in tango_context.device.activityMessage
        # PROTECTED REGION END #    //  DishLeafNode.test_Slew

    def test_buildState(self, tango_context):
        """Test for buildState"""
        # PROTECTED REGION ID(DishLeafNode.test_buildState) ENABLED START #
        assert tango_context.device.buildState == (
            "lmcbaseclasses, 0.1.3, A set of generic base devices for SKA Telescope.")
        # PROTECTED REGION END #    //  DishLeafNode.test_buildState

    def test_versionId(self, tango_context):
        """Test for versionId"""
        # PROTECTED REGION ID(DishLeafNode.test_versionId) ENABLED START #
        assert tango_context.device.versionId == "0.1.3"
        # PROTECTED REGION END #    //  DishLeafNode.test_versionId

    def test_centralLoggingLevel(self, tango_context):
        """Test for centralLoggingLevel"""
        # PROTECTED REGION ID(DishLeafNode.test_centralLoggingLevel) ENABLED START #
        tango_context.device.centralLoggingLevel = int(tango.LogLevel.LOG_DEBUG)
        assert tango_context.device.centralLoggingLevel == int(tango.LogLevel.LOG_DEBUG)
        # PROTECTED REGION END #    //  DishLeafNode.test_centralLoggingLevel

    def test_elementLoggingLevel(self, tango_context):
        """Test for elementLoggingLevel"""
        # PROTECTED REGION ID(DishLeafNode.test_elementLoggingLevel) ENABLED START #
        tango_context.device.elementLoggingLevel = int(tango.LogLevel.LOG_DEBUG)
        assert tango_context.device.elementLoggingLevel == int(tango.LogLevel.LOG_DEBUG)
        # PROTECTED REGION END #    //  DishLeafNode.test_elementLoggingLevel

    def test_storageLoggingLevel(self, tango_context):
        """Test for storageLoggingLevel"""
        # PROTECTED REGION ID(DishLeafNode.test_storageLoggingLevel) ENABLED START #
        #self.device.storageLoggingLevel
        tango_context.device.storageLoggingLevel = int(tango.LogLevel.LOG_DEBUG)
        assert tango_context.device.storageLoggingLevel == int(tango.LogLevel.LOG_DEBUG)
        # PROTECTED REGION END #    //  DishLeafNode.test_storageLoggingLevel

    def test_healthState(self, tango_context):
        """Test for healthState"""
        # PROTECTED REGION ID(DishLeafNode.test_healthState) ENABLED START #
        assert tango_context.device.healthState == 0
        # PROTECTED REGION END #    //  DishLeafNode.test_healthState

    def test_adminMode(self, tango_context):
        """Test for adminMode"""
        # PROTECTED REGION ID(DishLeafNode.test_adminMode) ENABLED START #
        assert tango_context.device.adminMode == 0
        # PROTECTED REGION END #    //  DishLeafNode.test_adminMode

    def test_controlMode(self, tango_context):
        """Test for controlMode"""
        # PROTECTED REGION ID(DishLeafNode.test_controlMode) ENABLED START #
        control_mode = 0
        tango_context.device.controlMode = control_mode
        assert tango_context.device.controlMode == control_mode
        # PROTECTED REGION END #    //  DishLeafNode.test_controlMode

    def test_simulationMode(self, tango_context):
        """Test for simulationMode"""
        # PROTECTED REGION ID(DishLeafNode.test_simulationMode) ENABLED START #
        simulation_mode = 0
        tango_context.device.simulationMode = simulation_mode
        assert tango_context.device.simulationMode == simulation_mode
        # PROTECTED REGION END #    //  DishLeafNode.test_simulationMode

    def test_testMode(self, tango_context):
        """Test for testMode"""
        # PROTECTED REGION ID(DishLeafNode.test_testMode) ENABLED START #
        test_mode = CONST.STR_FALSE
        tango_context.device.testMode = test_mode
        assert tango_context.device.testMode == test_mode
        # PROTECTED REGION END #    //  DishLeafNode.test_testMode

    def test_activityMessage(self, tango_context):
        """Test for activityMessage"""
        # PROTECTED REGION ID(DishLeafNode.test_activityMessage) ENABLED START #
        tango_context.device.activityMessage = CONST.STR_OK
        assert tango_context.device.activityMessage == CONST.STR_OK
        # PROTECTED REGION END #    //  DishLeafNode.test_activityMessage

    def test_dishMode_change_event(self, tango_context, create_dish_proxy):
        """Test for dishMode_change_event"""
        tango_context.device.SetOperateMode()
        eid = create_dish_proxy.subscribe_event(CONST.EVT_DISH_MODE,
                                                EventType.CHANGE_EVENT,
                                                DishLeafNode.dishModeCallback)
        time.sleep(2)
        assert tango_context.device.activityMessage == CONST.STR_DISH_OPERATE_MODE or \
               CONST.STR_SETOPERATE_SUCCESS
        assert create_dish_proxy.dishMode == "OPERATE" or 8
        create_dish_proxy.unsubscribe_event(eid)

    def test_pointingState_change_event(self, tango_context, create_dish_proxy):
        """Test for pointingState_change_event"""
        tango_context.device.Scan("0")
        eid = create_dish_proxy.subscribe_event(CONST.EVT_DISH_POINTING_STATE,
                                                EventType.CHANGE_EVENT,
                                                DishLeafNode.dishPointingStateCallback)
        time.sleep(6)
        #assert tango_context.device.activityMessage == CONST.STR_DISH_POINT_STATE_SCAN
        assert create_dish_proxy.pointingState == "SCANNING" or 3
        create_dish_proxy.unsubscribe_event(eid)

    def test_capturing_change_event(self, tango_context, create_dish_proxy):
        """Test for capturing_change_event"""
        tango_context.device.StopCapture("0")
        eid = create_dish_proxy.subscribe_event(CONST.EVT_DISH_CAPTURING, EventType.CHANGE_EVENT,
                                                DishLeafNode.dishCapturingCallback)
        time.sleep(6)
        assert tango_context.device.activityMessage == (CONST.STR_DISH_CAPTURING_FALSE) or \
               (CONST.STR_DISH_POINT_STATE_READY) or (CONST.STR_CAPTURE_EVENT)
        assert create_dish_proxy.capturing is False
        create_dish_proxy.unsubscribe_event(eid)

    def test_Track(self, tango_context, create_dish_proxy):
        """Test for Track"""
        # PROTECTED REGION ID(DishLeafNode.test_Track) ENABLED START #
        tango_context.device.Track(["radec|2:31:50.91|89:15:51.4"])
        time.sleep(60)
        assert create_dish_proxy.pointingState == 0
        # PROTECTED REGION END #    //  DishLeafNode.Track

    def test_Track_invalid_arg(self, tango_context):
        """Test for Track"""
        # PROTECTED REGION ID(DishLeafNode.test_Track) ENABLED START #
        tango_context.device.Track(["radec|2:31:50.91"])
        time.sleep(5)
        assert tango_context.device.activityMessage == CONST.ERR_RADEC_TO_AZEL_VAL_ERR
        # PROTECTED REGION END #    //  DishLeafNode.test_Track