#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of the DishLeafNode project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.
"""Contain the tests for the ."""

# Path
import sys
import os

from PyTango._PyTango import DeviceProxy, EventType
from tango.test_context import DeviceTestContext

path = os.path.join(os.path.dirname(__file__), os.pardir)
sys.path.insert(0, os.path.abspath(path))

# Imports
import time
from mock import MagicMock
from PyTango import DevFailed, DevState
#from devicetest import DeviceTestCase, main
import pytest
#from DishLeafNode import DishLeafNode
from DishLeafNode.DishLeafNode import DishLeafNode
from tango.server import command, attribute, device_property

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
    properties = {'SkaLevel': '4', 'MetricList': 'healthState', 'GroupDefinitions': '', 'CentralLoggingTarget': '', 'ElementLoggingTarget': '', 'StorageLoggingTarget': 'localhost', 'DishMasterFQDN': 'tango://apurva-pc:10000/mid_d0001/elt/master',
                  }
    empty = None  # Should be []

    @classmethod
    def mocking(cls):
        """Mock external libraries."""
        # Example : Mock numpy
        # cls.numpy = DishLeafNode.numpy = MagicMock()
        # PROTECTED REGION ID(DishLeafNode.test_mocking) ENABLED START #
        # PROTECTED REGION END #    //  DishLeafNode.test_mocking

    # def test_Init(self, tango_context):
    #     tango_context.device.Init()
    #     assert tango_context.device.adminMode == 0
    #     assert tango_context.device.healthState == 0
    #     assert tango_context.device.simulationMode == False

    def test_properties(self, tango_context):
        # test the properties
        # PROTECTED REGION ID(DishLeafNode.test_properties) ENABLED START #
        #assert tango_context.device.DishMasterFQDN == 'tango://apurva-pc:10000/mid_d0001/elt/master'
        # prop = tango_context.device.get_property("SkaLevel")
        # print "Properties are:", prop
        # assert prop != None
        # PROTECTED REGION END #    //  DishLeafNode.test_properties
        pass

    def test_State(self, tango_context):
        """Test for State"""
        # PROTECTED REGION ID(DishLeafNode.test_State) ENABLED START #
        #self.device.State()
        #print TestDishLeafNode.properties['DishMasterFQDN']
        assert tango_context.device.State() == DevState.ALARM
        # PROTECTED REGION END #    //  DishLeafNode.test_State

    def test_Status(self, tango_context):
        """Test for Status"""
        # PROTECTED REGION ID(DishLeafNode.test_Status) ENABLED START #
        #self.device.Status()
        print "Status is:", tango_context.device.Status()
        assert tango_context.device.Status() != "Dish Leaf Node initialized successfully."
        # PROTECTED REGION END #    //  DishLeafNode.test_Status

    def test_GetMetrics(self, tango_context):
        """Test for GetMetrics"""
        # PROTECTED REGION ID(DishLeafNode.test_GetMetrics) ENABLED START #
        #self.device.GetMetrics()
        # PROTECTED REGION END #    //  DishLeafNode.test_GetMetrics

    def test_ToJson(self, tango_context):
        """Test for ToJson"""
        # PROTECTED REGION ID(DishLeafNode.test_ToJson) ENABLED START #
        #self.device.ToJson("")
        # PROTECTED REGION END #    //  DishLeafNode.test_ToJson

    def test_GetVersionInfo(self, tango_context):
        """Test for GetVersionInfo"""
        # PROTECTED REGION ID(DishLeafNode.test_GetVersionInfo) ENABLED START #
        #self.device.GetVersionInfo()
        # PROTECTED REGION END #    //  DishLeafNode.test_GetVersionInfo

    def test_Reset(self, tango_context):
        """Test for Reset"""
        # PROTECTED REGION ID(DishLeafNode.test_Reset) ENABLED START #
        #self.device.Reset()
        assert tango_context.device.Reset() == None
        # PROTECTED REGION END #    //  DishLeafNode.test_Reset


    def test_SetStandByLPMode(self, tango_context, create_dish_proxy):
        """Test for SetStandByLPMode"""
        # PROTECTED REGION ID(DishLeafNode.test_SetStandByLPMode) ENABLED START #
        #self.device.SetStandByLPMode()

        #dish_proxy = DeviceProxy("tango://apurva-pc:10000/mid_d0001/elt/master")
        # time.sleep(3)
        tango_context.device.SetStandByLPMode()
        #assert tango_context.device.activityMessage == "SetStandByLPMode command is invoked on DishMaster"
        assert tango_context.device.activityMessage == "Command :-> SetStandByLPMode invoked successfully."
        #tango_context.device.StopCapture("0")
        # PROTECTED REGION END #    //  DishLeafNode.test_SetStandByLPMode

    # def test_SetStandByLPMode1(self, tango_context, create_dish_proxy):
    #     tango_context.device.SetOperateMode()
    #     tango_context.device.Scan("0")
    #     time.sleep(4)
    #     tango_context.device.SetStandByLPMode()
    #     time.sleep(4)
    #     print tango_context.device.activityMessage
    #     assert "Error in invoking command:" in tango_context.device.activityMessage

    def test_SetOperateMode(self, tango_context, create_dish_proxy):
        """Test for SetOperateMode"""
        # PROTECTED REGION ID(DishLeafNode.test_SetOperateMode) ENABLED START #
        #self.device.SetOperateMode()

        #dish_proxy = DeviceProxy("tango://apurva-pc:10000/mid_d0001/elt/master")
        # time.sleep(3)

        # tango_context.device.EndScan("0")
        # tango_context.device.SetStandByLPMode()
        tango_context.device.SetOperateMode()
        print tango_context.device.activityMessage
        assert tango_context.device.activityMessage == "Command :-> SetOperateMode invoked successfully."

        # assert create_dish_proxy.dishMode == 8
        #tango_context.device.SetStandByLPMode()

        # PROTECTED REGION END #    //  DishLeafNode.test_SetOperateMode


    def test_Configure(self, tango_context):
        """Test for Configure"""
        # PROTECTED REGION ID(DishLeafNode.test_Configure) ENABLED START #
        #self.device.Configure([""])
        tango_context.device.Configure(['1','0'])
        #assert tango_context.device.activityMessage == "Configure command is invoked on DishMaster"
        #time.sleep(4)
        print tango_context.device.activityMessage
        assert tango_context.device.activityMessage == "Command :-> Configure invoked successfully." or\
               "Dish Pointing State :-> READY" or "Achieved Pointing :-> [0. 1. 0.]"


        # PROTECTED REGION END #    //  DishLeafNode.test_Configure

    def test_Configure1(self, tango_context):
        tango_context.device.Configure(["a", "b"])
        #time.sleep(3)
        print tango_context.device.activityMessage
        #time.sleep(3)
        print tango_context.device.activityMessage

        assert "Exception in Configure command:" in tango_context.device.activityMessage

    def test_Scan(self, tango_context):
        """Test for Scan"""
        # PROTECTED REGION ID(DishLeafNode.test_Scan) ENABLED START #
        #self.device.Scan("")

        tango_context.device.Scan("0")
        #assert tango_context.device.activityMessage == "Scan command is invoked on DishMaster"
        time.sleep(2)
        assert tango_context.device.activityMessage == "Command :-> Scan invoked successfully." or "Dish Pointing State :-> SCANNING"
        # PROTECTED REGION END #    //  DishLeafNode.test_Scan

    def test_Scan1(self, tango_context):
        tango_context.device.Scan("a")
        assert "Exception in Scan command:" in tango_context.device.activityMessage

    def test_StartCapture(self, tango_context):
        """Test for StartCapture"""
        # PROTECTED REGION ID(DishLeafNode.test_StartCapture) ENABLED START #
        # self.device.StartCapture("")
        #tango_context.device.SetOperateMode()
        tango_context.device.StartCapture("0")
        #assert tango_context.device.activityMessage == "StartCapture command is invoked on DishMaster"
        time.sleep(5)
        assert tango_context.device.activityMessage == "Command :-> StartCapture invoked successfully."
        # PROTECTED REGION END #    //  DishLeafNode.test_StartCapture

    def test_StartCapture1(self, tango_context):
        tango_context.device.StartCapture("a")
        assert "Exception in StartCapture command:" in tango_context.device.activityMessage


    def test_StopCapture(self, tango_context):
        """Test for StopCapture"""
        # PROTECTED REGION ID(DishLeafNode.test_StopCapture) ENABLED START #
        # self.device.StopCapture("")
        tango_context.device.StopCapture("0")
        #assert tango_context.device.activityMessage == "StopCapture command is invoked on DishMaster"
        time.sleep(5)
        assert tango_context.device.activityMessage == "Command :-> StopCapture invoked successfully." or "Dish Pointing State :-> READY"


        # PROTECTED REGION END #    //  DishLeafNode.test_StopCapture

    def test_StopCapture1(self, tango_context):
        tango_context.device.StopCapture("a")
        assert "Exception in StopCapture command:" in tango_context.device.activityMessage


    def test_EndScan(self, tango_context):
        """Test for EndScan"""
        # PROTECTED REGION ID(DishLeafNode.test_EndScan) ENABLED START #
        #self.device.EndScan()
        tango_context.device.EndScan("0")
        #assert tango_context.device.activityMessage == "EndScan command is invoked on DishMaster"
        time.sleep(2)
        assert tango_context.device.activityMessage == "Command :->EndScaninvoked successfully." or "Dish Pointing State :-> READY"
        # PROTECTED REGION END #    //  DishLeafNode.test_EndScan

    def test_EndScan1(self, tango_context):
        tango_context.device.EndScan("a")
        assert "Exception in EndScan command:" in tango_context.device.activityMessage

    def test_SetStandbyFPMode(self, tango_context):
        """Test for SetStandbyFPMode"""
        # PROTECTED REGION ID(DishLeafNode.test_SetStandbyFPMode) ENABLED START #
        #self.device.SetStandbyFPMode()
        tango_context.device.SetStandbyFPMode()
        #assert tango_context.device.activityMessage == "SetStandbyFPMode command is invoked on DishMaster"
        time.sleep(4)
        assert tango_context.device.activityMessage == "Command :-> SetStandbyFPMode invoked successfully." or "Dish Mode :-> STANDBY-FP"
        # PROTECTED REGION END #    //  DishLeafNode.test_SetStandbyFPMode

    # def test_SetStowMode1(self, tango_context):
    #     """Test for SetStowMode"""
    #     # PROTECTED REGION ID(DishLeafNode.test_SetStowMode) ENABLED START #
    #     # self.device.SetStowMode()
    #
    #     # Testcase to cover exception in Command Callback
    #     tango_context.device.SetStandByLPMode()
    #     tango_context.device.SetOperateMode()
    #     tango_context.device.SetStowMode()
    #     assert ((tango_context.device.activityMessage != "Dish Mode :-> STOW") or
    #             (tango_context.device.activityMessage != "Desired Pointing :->  [0. 0. 0.]") or
    #             (tango_context.device.activityMessage != "Achieved Pointing :-> [0. 0. 0.]"))

    def test_SetStowMode(self, tango_context):
        tango_context.device.SetStandByLPMode()
        tango_context.device.SetStowMode()
        time.sleep(10)
        print "stow value:", tango_context.device.activityMessage
        assert tango_context.device.activityMessage == "Dish Pointing State :-> READY" or "Dish Mode :-> STOW" or "Desired Pointing :->  [0. 0. 0.]" or "Achieved Pointing :-> [0. 0. 0.]"

        # PROTECTED REGION END #    //  DishLeafNode.test_SetStowMode


    def test_Slew(self, tango_context):
        """Test for Slew"""
        # PROTECTED REGION ID(DishLeafNode.test_Slew) ENABLED START #
        #self.device.Slew("")
        tango_context.device.SetStandByLPMode()
        time.sleep(8)
        tango_context.device.Slew("0")
        #assert tango_context.device.activityMessage == "Slew command is invoked on DishMaster"
        time.sleep(4)
        assert tango_context.device.activityMessage == "Command :-> Slew invoked successfully."

    def test_Slew1(self, tango_context):
        tango_context.device.SetStandByLPMode()
        time.sleep(4)
        tango_context.device.Slew("a")
        assert "Exception in Slew command:" in tango_context.device.activityMessage

        # tango_context.device.SetStandByLPMode()
        # tango_context.device.Slew()
        # assert "Exception in Slew command:" in tango_context.device.activityMessage
        # PROTECTED REGION END #    //  DishLeafNode.test_Slew


    def test_buildState(self, tango_context):
        """Test for buildState"""
        # PROTECTED REGION ID(DishLeafNode.test_buildState) ENABLED START #
        #self.device.buildState
        assert tango_context.device.buildState == "tangods-skabasedevice, 1.0.0, A generic base device for SKA."
        # PROTECTED REGION END #    //  DishLeafNode.test_buildState


    def test_versionId(self, tango_context):
        """Test for versionId"""
        # PROTECTED REGION ID(DishLeafNode.test_versionId) ENABLED START #
        #self.device.versionId
        assert tango_context.device.versionId == "1.0.0"
        # PROTECTED REGION END #    //  DishLeafNode.test_versionId

    def test_centralLoggingLevel(self, tango_context):
        """Test for centralLoggingLevel"""
        # PROTECTED REGION ID(DishLeafNode.test_centralLoggingLevel) ENABLED START #
        #self.device.centralLoggingLevel
        level = 5
        tango_context.device.centralLoggingLevel = level
        assert tango_context.device.centralLoggingLevel == level
        # PROTECTED REGION END #    //  DishLeafNode.test_centralLoggingLevel

    def test_elementLoggingLevel(self, tango_context):
        """Test for elementLoggingLevel"""
        # PROTECTED REGION ID(DishLeafNode.test_elementLoggingLevel) ENABLED START #
        #self.device.elementLoggingLevel
        level = 5
        tango_context.device.elementLoggingLevel = level
        assert tango_context.device.elementLoggingLevel == level
        # PROTECTED REGION END #    //  DishLeafNode.test_elementLoggingLevel

    def test_storageLoggingLevel(self, tango_context):
        """Test for storageLoggingLevel"""
        # PROTECTED REGION ID(DishLeafNode.test_storageLoggingLevel) ENABLED START #
        #self.device.storageLoggingLevel
        level = 5
        tango_context.device.storageLoggingLevel = level
        assert tango_context.device.storageLoggingLevel == level
        # PROTECTED REGION END #    //  DishLeafNode.test_storageLoggingLevel

    def test_healthState(self, tango_context):
        """Test for healthState"""
        # PROTECTED REGION ID(DishLeafNode.test_healthState) ENABLED START #
        #self.device.healthState
        assert tango_context.device.healthState==0
        # PROTECTED REGION END #    //  DishLeafNode.test_healthState

    def test_adminMode(self, tango_context):
        """Test for adminMode"""
        # PROTECTED REGION ID(DishLeafNode.test_adminMode) ENABLED START #
        #self.device.adminMode
        assert tango_context.device.adminMode == 0
        # PROTECTED REGION END #    //  DishLeafNode.test_adminMode

    def test_controlMode(self, tango_context):
        """Test for controlMode"""
        # PROTECTED REGION ID(DishLeafNode.test_controlMode) ENABLED START #
        #self.device.controlMode
        control_mode = 0
        tango_context.device.controlMode = control_mode
        assert tango_context.device.controlMode == control_mode
        # PROTECTED REGION END #    //  DishLeafNode.test_controlMode

    def test_simulationMode(self, tango_context):
        """Test for simulationMode"""
        # PROTECTED REGION ID(DishLeafNode.test_simulationMode) ENABLED START #
        #self.device.simulationMode
        simulation_mode = 0
        tango_context.device.simulationMode = simulation_mode
        assert tango_context.device.simulationMode == simulation_mode
        # PROTECTED REGION END #    //  DishLeafNode.test_simulationMode

    def test_testMode(self, tango_context):
        """Test for testMode"""
        # PROTECTED REGION ID(DishLeafNode.test_testMode) ENABLED START #
        #self.device.testMode
        test_mode = "False"
        tango_context.device.testMode = test_mode
        assert tango_context.device.testMode == test_mode
        # PROTECTED REGION END #    //  DishLeafNode.test_testMode

    def test_activityMessage(self, tango_context):
        """Test for activityMessage"""
        # PROTECTED REGION ID(DishLeafNode.test_activityMessage) ENABLED START #
        #self.device.activityMessage
        tango_context.device.activityMessage = "OK"
        assert tango_context.device.activityMessage == "OK"
        # PROTECTED REGION END #    //  DishLeafNode.test_activityMessage

    def test_dishMode_change_event(self, tango_context, create_dish_proxy):
        tango_context.device.SetOperateMode()
        eid = create_dish_proxy.subscribe_event("dishMode", EventType.CHANGE_EVENT, DishLeafNode.dishModeCallback)
        time.sleep(2)
        assert tango_context.device.activityMessage == "Dish Mode :-> OPERATE"
        assert create_dish_proxy.dishMode == "OPERATE" or 8
        # tango_context.device.SetStandByLPMode()
        # time.sleep(2)
        # assert tango_context.device.activityMessage == "Dish Mode :->  STANDBY-LP"
        create_dish_proxy.unsubscribe_event(eid)

    def test_pointingState_change_event(self, tango_context, create_dish_proxy):
        #tango_context.device.SetOperateMode()
        tango_context.device.Scan("0")
        eid = create_dish_proxy.subscribe_event("pointingState", EventType.CHANGE_EVENT, DishLeafNode.dishPointingStateCallback)
        time.sleep(2)
        assert tango_context.device.activityMessage == "Dish Pointing State :-> SCANNING"
        #assert create_dish_proxy.pointingState == "SCANNING" or 3
        # tango_context.device.SetStandByLPMode()
        # time.sleep(2)
        # assert tango_context.device.activityMessage == "Dish Mode :->  STANDBY-LP"
        create_dish_proxy.unsubscribe_event(eid)

    def test_capturing_change_event(self, tango_context, create_dish_proxy):
        tango_context.device.StopCapture("0")
        eid = create_dish_proxy.subscribe_event("capturing", EventType.CHANGE_EVENT, DishLeafNode.dishCapturingCallback)
        time.sleep(2)
        #assert tango_context.device.activityMessage == "Dish data capturing :-> FALSE" or "Dish Pointing State :-> READY" \
               #or "StopCapture command is invoked on DishMaster"
        assert create_dish_proxy.capturing == False
        # tango_context.device.SetStandByLPMode()
        # time.sleep(2)
        # assert tango_context.device.activityMessage == "Dish Mode :->  STANDBY-LP"
        create_dish_proxy.unsubscribe_event(eid)


# Main execution
if __name__ == "__main__":
    main()
