#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of the SdpSubarrayLeafNode project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.
"""Contain the tests for the SdpSubarrayLeafNode."""

# Path
import sys
import os
import time

file_path = os.path.dirname(os.path.abspath(__file__))
module_path = os.path.abspath(os.path.join(file_path, os.pardir)) + "/SdpSubarrayLeafNode"
sys.path.insert(0, module_path)

path = os.path.join(os.path.dirname(__file__), os.pardir)
sys.path.insert(0, os.path.abspath(path))

# Imports
import tango
from tango import DevState, EventType, DeviceProxy
from SdpSubarrayLeafNode.SdpSubarrayLeafNode import SdpSubarrayLeafNode
import CONST
import pytest
import json

# Imports
from time import sleep
from mock import MagicMock
# from PyTango import DevFailed, DevState
# from devicetest import DeviceTestCase, main

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
class TestSdpSubarrayLeafNode(object):
    """Test case for packet generation."""
    # PROTECTED REGION ID(SdpSubarrayLeafNode.test_additionnal_import) ENABLED START #
    # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_additionnal_import
    device = SdpSubarrayLeafNode
    properties = {'SkaLevel': '4', 'GroupDefinitions': '', 'CentralLoggingTarget': '', 'ElementLoggingTarget': '',
                  'StorageLoggingTarget': 'localhost', 'SdpSubarrayNodeFQDN': 'mid_sdp/elt/subarray_1',
                  }
    empty = None  # Should be []

    @classmethod
    def mocking(cls):
        """Mock external libraries."""
        # Example : Mock numpy
        # cls.numpy = SdpSubarrayLeafNode.numpy = MagicMock()
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_mocking) ENABLED START #
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_mocking

    def test_properties(self, tango_context):
        # test the properties
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_properties) ENABLED START #
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_properties
        pass

    def test_State(self, tango_context):
        """Test for State"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_State) ENABLED START #
        assert tango_context.device.State() == DevState.ALARM
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_State

    def test_Status(self, tango_context):
        """Test for Status"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_Status) ENABLED START #
        assert tango_context.device.Status() != CONST.STR_INIT_SUCCESS
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_Status

    def test_GetVersionInfo(self, tango_context):
        """Test for GetVersionInfo"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_GetVersionInfo) ENABLED START #
        # self.device.GetVersionInfo()
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_GetVersionInfo

    def test_Reset(self, tango_context):
        """Test for Reset"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_Reset) ENABLED START #
        # self.device.Reset()
        assert tango_context.device.Reset() == None
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_Reset

    # def test_ReleaseResources(self, tango_context):
    #     """Test for ReleaseResources"""
    #     # PROTECTED REGION ID(SdpSubarrayLeafNode.test_ReleaseResources) ENABLED START #
    #     self.device.ReleaseResources("")
    #     # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_ReleaseResources

    def test_AssignResources(self, tango_context, create_sdpsubarray_proxy):
        """Test for AssignResources"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_AssignResources) ENABLED START #
        test_input = '{"processingBlockIdList": ["0001", "0002"]}'
        retVal = tango_context.device.AssignResources(test_input)
        assert CONST.STR_ASSIGN_RESOURCES_SUCCESS in tango_context.device.activityMessage
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_AssignResources

    def test_AssignResources_invalid_key(self, tango_context):
        """Test for AssignResources_invalid_key"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_AssignResources) ENABLED START #
        test_input = '{"processingBlock": ["0001", "0002"]}'
        with pytest.raises(tango.DevFailed):
            tango_context.device.AssignResources(test_input)
        assert CONST.ERR_JSON_KEY_NOT_FOUND in tango_context.device.activityMessage
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_AssignResources

    def test_AssignResources_invalid_format(self, tango_context):
        """Test for AssignResources_invalid_format"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_AssignResources) ENABLED START #
        test_input = '{"abc"}'
        with pytest.raises(tango.DevFailed):
            tango_context.device.AssignResources(test_input)
        assert CONST.ERR_INVALID_JSON in tango_context.device.activityMessage
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_AssignResources

    def test_ReleaseAllResources(self, tango_context):
        """Test for ReleaseAllResources"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_ReleaseAllResources) ENABLED START #
        retVal = tango_context.device.ReleaseAllResources()
        assert CONST.STR_REL_RESOURCES in tango_context.device.activityMessage
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_ReleaseAllResources

    def test_Configure(self, tango_context):
        """Test for Configure"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_Configure) ENABLED START #
        test_input = '{"sdp":{"configure":{"id":"realtime-20190627-0001","sbiId":"20190627-0001",' \
                     '"workflow":{"id":"vis_ingest","type":"realtime","version":"0.1.0"},"parameters":' \
                     '{"numStations":4,"numChanels":372,"numPolarisations":4,"freqStartHz":0.35e9,' \
                     '"freqEndHz":1.05e9,"fields":{"0":{"system":"ICRS","name":"NGC6251","ra":1.0,"dec"' \
                     ':1.0}}},"scanParameters":{"12345":{"fieldId":0,"intervalMs":1400}}},"configureScan"' \
                     ':{"scanParameters":{"12346":{"fieldId":0,"intervalMs":2800}}}}}'
        tango_context.device.Configure(test_input)
        time.sleep(1)
        assert CONST.STR_CONFIGURE_SUCCESS in tango_context.device.activityMessage
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_Configure

    def test_Configure_invalid_key(self, tango_context):
        """Test for Configure command with invalid_key"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_Configure_invalid_key) ENABLED START #
        test_input = '{"sdp":{"":{"id":"realtime-20190627-0001","sbiId":"20190627-0001",' \
                     '"workflow":{"id":"vis_ingest","type":"realtime","version":"0.1.0"},"parameters":' \
                     '{"numStations":4,"numChanels":372,"numPolarisations":4,"freqStartHz":0.35e9,' \
                     '"freqEndHz":1.05e9,"fields":{"0":{"system":"ICRS","name":"NGC6251","ra":1.0,"dec"' \
                     ':1.0}}},"scanParameters":{"12345":{"fieldId":0,"intervalMs":1400}}},"configureScan"' \
                     ':{"scanParameters":{"12346":{"fieldId":0,"intervalMs":2800}}}}}'
        with pytest.raises(tango.DevFailed):
            tango_context.device.Configure(test_input)
        assert CONST.ERR_JSON_KEY_NOT_FOUND in tango_context.device.activityMessage
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_AssignResources

    def test_Configure_invalid_format(self, tango_context):
        """Test for Configure command with invalid_format"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_Configure_invalid_format) ENABLED START #
        test_input = '{"abc"}'
        with pytest.raises(tango.DevFailed):
            tango_context.device.Configure(test_input)
        assert CONST.ERR_INVALID_JSON_CONFIG in tango_context.device.activityMessage
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_AssignResources

    def test_EndScan(self, tango_context):
        """Test for EndScan"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_EndScan) ENABLED START #
        test_input = '{"sdp":{"configure":{"id":"realtime-20190627-0001","sbiId":"20190627-0001"' \
                     ',"workflow":{"id":"vis_ingest","type":"realtime","version":"0.1.0"},"parameters":' \
                     '{"numStations":4,"numChanels":372,"numPolarisations":4,"freqStartHz":0.35e9,' \
                     '"freqEndHz":1.05e9,"fields":{"0":{"system":"ICRS","name":"NGC6251","ra":1.0,"dec"' \
                     ':1.0}}},"scanParameters":{"12345":{"fieldId":0,"intervalMs":1400}}},"configureScan"' \
                     ':{"scanParameters":{"12346":{"fieldId":0,"intervalMs":2800}}}}}'
        tango_context.device.Configure(test_input)
        time.sleep(2)
        test_input = '{"scanDuration":0}'
        tango_context.device.Scan(test_input)
        time.sleep(2)
        tango_context.device.EndScan()
        tango_context.device.status()
        time.sleep(2)
        assert CONST.STR_ENDSCAN_SUCCESS in tango_context.device.activityMessage
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_EndScan

    def test_EndScan_Invalid_State(self, tango_context):
        """Test for  Invalid EndScan"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_EndScan_Invalid_State) ENABLED START #
        tango_context.device.EndScan()
        time.sleep(2)
        assert CONST.ERR_DEVICE_NOT_IN_SCAN in tango_context.device.activityMessage
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_EndScan


    def test_Scan(self, tango_context):
        """Test for Scan"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_Scan) ENABLED START #
        test_input = '{"sdp":{"configure":{"id":"realtime-20190627-0001","sbiId":"20190627-0001",' \
                     '"workflow":{"id":"vis_ingest","type":"realtime","version":"0.1.0"},"parameters":' \
                     '{"numStations":4,"numChanels":372,"numPolarisations":4,"freqStartHz":0.35e9,' \
                     '"freqEndHz":1.05e9,"fields":{"0":{"system":"ICRS","name":"NGC6251","ra":1.0,"dec"' \
                     ':1.0}}},"scanParameters":{"12345":{"fieldId":0,"intervalMs":1400}}},"configureScan"' \
                     ':{"scanParameters":{"12346":{"fieldId":0,"intervalMs":2800}}}}}'
        tango_context.device.Configure(test_input)
        time.sleep(2)
        test_input = '{"scanDuration":0}'
        tango_context.device.Scan(test_input)
        time.sleep(1)
        assert CONST.STR_SCAN_SUCCESS in tango_context.device.activityMessage
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_Scan

    #
    # def test_EndSB(self, tango_context):
    #     """Test for EndSB"""
    #     # PROTECTED REGION ID(SdpSubarrayLeafNode.test_EndSB) ENABLED START #
    #     self.device.EndSB()
    #     # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_EndSB
    #
    # def test_Abort(self, tango_context):
    #     """Test for Abort"""
    #     # PROTECTED REGION ID(SdpSubarrayLeafNode.test_Abort) ENABLED START #
    #     self.device.Abort()
    #     # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_Abort

    # def test_buildState(self, tango_context):
    #     """Test for buildState"""
    #     # PROTECTED REGION ID(SdpSubarrayLeafNode.test_buildState) ENABLED START #
    #     self.device.buildState
    #     # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_buildState

    def test_versionId(self, tango_context):
        """Test for versionId"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_versionId) ENABLED START #
        # self.device.versionId
        assert tango_context.device.versionId == "0.1.3"
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_versionId

    def test_centralLoggingLevel(self, tango_context):
        """Test for centralLoggingLevel"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_centralLoggingLevel) ENABLED START #
        tango_context.device.centralLoggingLevel = int(tango.LogLevel.LOG_DEBUG)
        assert tango_context.device.centralLoggingLevel == int(tango.LogLevel.LOG_DEBUG)
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_centralLoggingLevel

    def test_elementLoggingLevel(self, tango_context):
        """Test for elementLoggingLevel"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_elementLoggingLevel) ENABLED START #
        tango_context.device.elementLoggingLevel = int(tango.LogLevel.LOG_DEBUG)
        assert tango_context.device.elementLoggingLevel == int(tango.LogLevel.LOG_DEBUG)
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_elementLoggingLevel

    def test_storageLoggingLevel(self, tango_context):
        """Test for storageLoggingLevel"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_storageLoggingLevel) ENABLED START #
        tango_context.device.storageLoggingLevel = int(tango.LogLevel.LOG_DEBUG)
        assert tango_context.device.storageLoggingLevel == int(tango.LogLevel.LOG_DEBUG)
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_storageLoggingLevel

    def test_healthState(self, tango_context):
        """Test for healthState"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_healthState) ENABLED START #
        assert tango_context.device.healthState == 0
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_healthState

    def test_adminMode(self, tango_context):
        """Test for adminMode"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_adminMode) ENABLED START #
        assert tango_context.device.adminMode == 0
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_adminMode

    def test_controlMode(self, tango_context):
        """Test for controlMode"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_controlMode) ENABLED START #
        control_mode = 0
        tango_context.device.controlMode = control_mode
        assert tango_context.device.controlMode == control_mode
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_controlMode

    def test_simulationMode(self, tango_context):
        """Test for simulationMode"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_simulationMode) ENABLED START #
        simulation_mode = 0
        tango_context.device.simulationMode = simulation_mode
        assert tango_context.device.simulationMode == simulation_mode
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_simulationMode

    def test_testMode(self, tango_context):
        """Test for testMode"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_testMode) ENABLED START #
        test_mode = CONST.STR_FALSE
        tango_context.device.testMode = test_mode
        assert tango_context.device.testMode == test_mode
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_testMode

    def test_receiveAddresses(self, tango_context):
        """Test for receiveAddresses"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_receiveAddresses) ENABLED START #
        assert tango_context.device.receiveAddresses == ""
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_receiveAddresses

    # def test_sdpSubarrayHealthState(self, tango_context):
    #     """Test for sdpSubarrayHealthState"""
    #     # PROTECTED REGION ID(SdpSubarrayLeafNode.test_sdpSubarrayHealthState) ENABLED START #
    #     assert tango_context.device.sdpSubarrayHealthState == CONST.ENUM_OK
    #     # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_sdpSubarrayHealthState

    def test_activityMessage(self, tango_context):
        """Test for activityMessage"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_activityMessage) ENABLED START #
        assert tango_context.device.activityMessage == ""
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_activityMessage

    def test_activeProcessingBlocks(self, tango_context):
        """Test for activeProcessingBlocks"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_activeProcessingBlocks) ENABLED START #
        assert tango_context.device.activeProcessingBlocks == ""
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_activeProcessingBlocks
