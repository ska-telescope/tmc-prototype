#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of the CentralNode project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.
"""Contain the tests for the CentralNode."""

# Path
import sys
import os
import time

from PyTango._PyTango import EventType

path = os.path.join(os.path.dirname(__file__), os.pardir)
sys.path.insert(0, os.path.abspath(path))

# Imports
from time import sleep
from mock import MagicMock
from PyTango import DevFailed, DevState
#from devicetest import DeviceTestCase, main
from CentralNode import CentralNode
from CentralNode.CentralNode import CentralNode
import pytest

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
@pytest.mark.usefixtures("tango_context", "initialize_device")

class TestCentralNode(object):
    """Test case for packet generation."""
    # PROTECTED REGION ID(CentralNode.test_additionnal_import) ENABLED START #
    # PROTECTED REGION END #    //  CentralNode.test_additionnal_import
    device = CentralNode
    properties = {'SkaLevel': '4', 'MetricList': 'healthState', 'GroupDefinitions': '', 'CentralLoggingTarget': '', 'ElementLoggingTarget': '', 'StorageLoggingTarget': 'localhost', 'CentralAlarmHandler': '', 'TMAlarmHandler': '', 'TMMidSubarrayNodes': 'ska_mid/tm_subarray_node/1', 'NumDishes': '4', 'DishLeafNodePrefix': 'ska_mid/tm_leaf_node/d', 
                  }
    empty = None  # Should be []

    @classmethod
    def mocking(cls):
        """Mock external libraries."""
        # Example : Mock numpy
        # cls.numpy = CentralNode.numpy = MagicMock()
        # PROTECTED REGION ID(CentralNode.test_mocking) ENABLED START #
        # PROTECTED REGION END #    //  CentralNode.test_mocking

    # def test_init_device(self,tango_context):
    #     CentralNode.init_device()
    #     assert tango_context.device.healthState == 0

    def test_properties(self, tango_context):
        # test the properties
        # PROTECTED REGION ID(CentralNode.test_properties) ENABLED START #
        # PROTECTED REGION END #    //  CentralNode.test_properties
        pass

    def test_State(self, tango_context):
        """Test for State"""
        # PROTECTED REGION ID(CentralNode.test_State) ENABLED START #
        #self.device.State()
        assert tango_context.device.State() == DevState.ON
        # PROTECTED REGION END #    //  CentralNode.test_State

    def test_Status(self, tango_context):
        """Test for Status"""
        # PROTECTED REGION ID(CentralNode.test_Status) ENABLED START #
        #self.device.Status()
        assert tango_context.device.Status() == "CentralNode is initialized successfully."
        # PROTECTED REGION END #    //  CentralNode.test_Status

    def test_GetMetrics(self, tango_context):
        """Test for GetMetrics"""
        # PROTECTED REGION ID(CentralNode.test_GetMetrics) ENABLED START #
        #self.device.GetMetrics()
        # PROTECTED REGION END #    //  CentralNode.test_GetMetrics

    def test_ToJson(self, tango_context):
        """Test for ToJson"""
        # PROTECTED REGION ID(CentralNode.test_ToJson) ENABLED START #
        #self.device.ToJson("")
        # PROTECTED REGION END #    //  CentralNode.test_ToJson

    def test_GetVersionInfo(self, tango_context):
        """Test for GetVersionInfo"""
        # PROTECTED REGION ID(CentralNode.test_GetVersionInfo) ENABLED START #
        #self.device.GetVersionInfo()
        # PROTECTED REGION END #    //  CentralNode.test_GetVersionInfo

    def test_Reset(self, tango_context):
        """Test for Reset"""
        # PROTECTED REGION ID(CentralNode.test_Reset) ENABLED START #
        #self.device.Reset()
        assert tango_context.device.Reset() == None
        # PROTECTED REGION END #    //  CentralNode.test_Reset

    def test_StowAntennas_Negative_Argument(self, tango_context):
        """Test for StowAntennas"""
        # PROTECTED REGION ID(CentralNode.test_StowAntennas) ENABLED START #
        argin = ["a", ]
        tango_context.device.StowAntennas(argin)
        assert "Exception in StowAntennas command:" in tango_context.device.activityMessage

        # PROTECTED REGION END #    //  CentralNode.test_StowAntennas

    def test_StowAntennas_Negative_Functionality(self, tango_context, create_leafNode1_proxy):
        """Test for StowAntennas"""
        # PROTECTED REGION ID(CentralNode.test_StowAntennas) ENABLED START #
        argin = ["0001",]
        tango_context.device.StartUpTelescope()
        # create_leafNode1_proxy.SetOperateMode()
        tango_context.device.StowAntennas(argin)
        assert "Error message is:" in tango_context.device.activityMessage

        # PROTECTED REGION END #    //  CentralNode.test_StowAntennas

    def test_StowAntennas(self, tango_context, create_leafNode1_proxy):
        """Test for StowAntennas"""
        # PROTECTED REGION ID(CentralNode.test_StowAntennas) ENABLED START #
        argin = ["0001",]
        create_leafNode1_proxy.SetStandByLPMode()
        tango_context.device.StowAntennas(argin)
        assert tango_context.device.activityMessage == "STOW command invoked from Central node on the requested dishes"
        # PROTECTED REGION END #    //  CentralNode.test_StowAntennas


    def test_StandByTelescope(self, tango_context):
        """Test for StandByTelescope"""
        # PROTECTED REGION ID(CentralNode.test_StandByTelescope) ENABLED START #
        #self.device.StandByTelescope()
        tango_context.device.StandByTelescope()
        # print "Test file output: ", tango_context.device.activityMessage
        assert tango_context.device.activityMessage == "StandByTelescope command invoked from Central node"
        # PROTECTED REGION END #    //  CentralNode.test_StandByTelescope

    def test_StandByTelescope_Negative(self, tango_context, create_leafNode1_proxy):
        """Test for StandByTelescope"""
        # PROTECTED REGION ID(CentralNode.test_StandByTelescope) ENABLED START #
        #self.device.StandByTelescope()
        create_leafNode1_proxy.SetOperateMode()
        #time.sleep(2)
        create_leafNode1_proxy.Scan("0")
        time.sleep(1)
        tango_context.device.StandByTelescope()
        # print "Test file output: ", tango_context.device.activityMessage
        #assert tango_context.device.activityMessage == "StandByTelescope command invoked from Central node"
        assert "Error message is:" in tango_context.device.activityMessage
        # PROTECTED REGION END #    //  CentralNode.test_StandByTelescope


    def test_StartUpTelescope(self, tango_context, create_leafNode1_proxy):
        """Test for StartUpTelescope"""
        # PROTECTED REGION ID(CentralNode.test_StartUpTelescope) ENABLED START #
        #self.device.StartUpTelescope()
        create_leafNode1_proxy.EndScan("0")
        time.sleep(1)
        create_leafNode1_proxy.SetStandByLPMode()

        tango_context.device.StartUpTelescope()
        assert tango_context.device.activityMessage == "StartUpTelescope command invoked from Central node"

        # argin = ["0001", ]
        # tango_context.device.StowAntennas(argin)
        # tango_context.device.StartUpTelescope()
        # assert "Error message is:" in tango_context.device.activityMessage
        # PROTECTED REGION END #    //  CentralNode.test_StartUpTelescope


    def test_StartUpTelescope_Negative(self, tango_context):
        """Test for StartUpTelescope"""
        # PROTECTED REGION ID(CentralNode.test_StartUpTelescope) ENABLED START #
        #self.device.StartUpTelescope()
        tango_context.device.StartUpTelescope()
        assert "Error message is:" in tango_context.device.activityMessage
        # PROTECTED REGION END #    //  CentralNode.test_StartUpTelescope

    def test_buildState(self, tango_context):
        """Test for buildState"""
        # PROTECTED REGION ID(CentralNode.test_buildState) ENABLED START #
        #self.device.buildState
        assert tango_context.device.buildState == "tangods-skabasedevice, 1.0.0, A generic base device for SKA."
        # PROTECTED REGION END #    //  CentralNode.test_buildState

    def test_versionId(self, tango_context):
        """Test for versionId"""
        # PROTECTED REGION ID(CentralNode.test_versionId) ENABLED START #
        #self.device.versionId
        assert tango_context.device.versionId == "1.0.0"
        # PROTECTED REGION END #    //  CentralNode.test_versionId

    def test_centralLoggingLevel(self, tango_context):
        """Test for centralLoggingLevel"""
        # PROTECTED REGION ID(CentralNode.test_centralLoggingLevel) ENABLED START #
        #self.device.centralLoggingLevel
        level = 5
        tango_context.device.centralLoggingLevel = level
        assert tango_context.device.centralLoggingLevel == level
        # PROTECTED REGION END #    //  CentralNode.test_centralLoggingLevel

    def test_elementLoggingLevel(self, tango_context):
        """Test for elementLoggingLevel"""
        # PROTECTED REGION ID(CentralNode.test_elementLoggingLevel) ENABLED START #
        #self.device.elementLoggingLevel
        level = 5
        tango_context.device.elementLoggingLevel = level
        assert tango_context.device.elementLoggingLevel == level
        # PROTECTED REGION END #    //  CentralNode.test_elementLoggingLevel

    def test_storageLoggingLevel(self, tango_context):
        """Test for storageLoggingLevel"""
        # PROTECTED REGION ID(CentralNode.test_storageLoggingLevel) ENABLED START #
        #self.device.storageLoggingLevel
        level = 5
        tango_context.device.storageLoggingLevel = level
        assert tango_context.device.storageLoggingLevel == level
        # PROTECTED REGION END #    //  CentralNode.test_storageLoggingLevel

    def test_healthState(self, tango_context):
        """Test for healthState"""
        # PROTECTED REGION ID(CentralNode.test_healthState) ENABLED START #
        #self.device.healthState
        assert tango_context.device.healthState == 0
        # PROTECTED REGION END #    //  CentralNode.test_healthState

    def test_adminMode(self, tango_context):
        """Test for adminMode"""
        # PROTECTED REGION ID(CentralNode.test_adminMode) ENABLED START #
        #self.device.adminMode
        assert tango_context.device.adminMode == 0
        # PROTECTED REGION END #    //  CentralNode.test_adminMode

    def test_controlMode(self, tango_context):
        """Test for controlMode"""
        # PROTECTED REGION ID(CentralNode.test_controlMode) ENABLED START #
        #self.device.controlMode
        control_mode = 0
        tango_context.device.controlMode = control_mode
        assert tango_context.device.controlMode == control_mode
        # PROTECTED REGION END #    //  CentralNode.test_controlMode

    def test_simulationMode(self, tango_context):
        """Test for simulationMode"""
        # PROTECTED REGION ID(CentralNode.test_simulationMode) ENABLED START #
        #self.device.simulationMode
        simulation_mode = 0
        tango_context.device.simulationMode = simulation_mode
        assert tango_context.device.simulationMode == simulation_mode
        # PROTECTED REGION END #    //  CentralNode.test_simulationMode

    def test_testMode(self, tango_context):
        """Test for testMode"""
        # PROTECTED REGION ID(CentralNode.test_testMode) ENABLED START #
        #self.device.testMode
        test_mode = "False"
        tango_context.device.testMode = test_mode
        assert tango_context.device.testMode == test_mode
        # PROTECTED REGION END #    //  CentralNode.test_testMode

    def test_telescopeHealthState(self, tango_context):
        """Test for telescopeHealthState"""
        # PROTECTED REGION ID(CentralNode.test_telescopeHealthState) ENABLED START #
        #self.device.telescopeHealthState
        assert tango_context.device.telescopeHealthState == 0
        # PROTECTED REGION END #    //  CentralNode.test_telescopeHealthState

    def test_subarray1HealthState(self, tango_context):
        """Test for subarray1HealthState"""
        # PROTECTED REGION ID(CentralNode.test_subarray1HealthState) ENABLED START #
        #self.device.subarray1HealthState
        assert tango_context.device.subarray1HealthState == 0
        # PROTECTED REGION END #    //  CentralNode.test_subarray1HealthState

    def test_subarray2HealthState(self, tango_context):
        """Test for subarray2HealthState"""
        # PROTECTED REGION ID(CentralNode.test_subarray2HealthState) ENABLED START #
        #self.device.subarray2HealthState
        assert tango_context.device.subarray2HealthState == 0
        # PROTECTED REGION END #    //  CentralNode.test_subarray2HealthState

    def test_activityMessage(self, tango_context):
        """Test for activityMessage"""
        # PROTECTED REGION ID(CentralNode.test_activityMessage) ENABLED START #
        #self.device.activityMessage
        # PROTECTED REGION END #    //  CentralNode.test_activityMessage

    def test_subarray1_health_change_event(self, tango_context, create_subarray1_proxy):
        eid = create_subarray1_proxy.subscribe_event("healthState", EventType.CHANGE_EVENT, CentralNode.subarrayHealthStateCallback)
        assert "Health state of " in tango_context.device.activityMessage

        # tango_context.device.SetStandByLPMode()
        # time.sleep(2)
        # assert tango_context.device.activityMessage == "Dish Mode :->  STANDBY-LP"
        create_subarray1_proxy.unsubscribe_event(eid)

    def test_subarray2_health_change_event(self, tango_context, create_subarray2_proxy):
        eid = create_subarray2_proxy.subscribe_event("healthState", EventType.CHANGE_EVENT, CentralNode.subarrayHealthStateCallback)
        assert "Health state of " in tango_context.device.activityMessage
        # tango_context.device.SetStandByLPMode()
        # time.sleep(2)
        # assert tango_context.device.activityMessage == "Dish Mode :->  STANDBY-LP"
        create_subarray2_proxy.unsubscribe_event(eid)

# Main execution
if __name__ == "__main__":
    main()
