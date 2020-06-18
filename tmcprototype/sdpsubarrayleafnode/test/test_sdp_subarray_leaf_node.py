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
# Imports
import tango
import pytest
import time
from tango import DevState, EventType, DeviceProxy
from sdpsubarrayleafnode import SdpSubarrayLeafNode, const
from ska.base.control_model import ObsState, HealthState, AdminMode, TestMode, ControlMode, SimulationMode, LoggingLevel

# Note:
# Since the device uses an inner thread, it is necessary to
# wait during the tests in order the let the device update itself.
# Hence, the sleep calls have to be secured enough not to produce
# any inconsistent behavior. However, the unittests need to run fast.
# Here, we use a factor 3 between the read period and the sleep calls.
#
# Look at devicetest examples for more advanced testing


# Device test case
@pytest.mark.usefixtures("tango_context", "create_sdpsubarray_proxy")
class TestSdpSubarrayLeafNode(object):
    """Test case for packet generation."""
    # PROTECTED REGION ID(SdpSubarrayLeafNode.test_additionnal_import) ENABLED START #
    # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_additionnal_import
    device = SdpSubarrayLeafNode
    properties = {'SkaLevel': '4', 'GroupDefinitions': '',
                  'LoggingLevelDefault': '4', 'LoggingTargetsDefault': 'console::cout',
                  'SdpSubarrayFQDN': 'mid_sdp/elt/subarray_1'}
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
        assert tango_context.device.Status() != const.STR_INIT_SUCCESS
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_Status

    def test_Reset(self, tango_context):
        """Test for Reset"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_Reset) ENABLED START #
        # self.device.Reset()
        assert tango_context.device.Reset() == None
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_Reset

    def test_AssignResources(self, tango_context, create_sdpsubarray_proxy):
        """Test for AssignResources"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_AssignResources) ENABLED START #
        test_input = '{"id":"sbi-mvp01-20200325-00001","max_length":100.0,"scan_types":[{"id":"science_A",' \
                     '"coordinate_system":"ICRS","ra":"02:42:40.771","dec":"-00:00:47.84","subbands":[' \
                     '{"freq_min":0.35e9,"freq_max":1.05e9,"nchan":372,"input_link_map":[[1,0],[101,1]]}],' \
                     '"channels":[{"count":744,"start":0,"stride":2,"freq_min":0.35e9,"freq_max":0.368e9,' \
                     '"link_map":[[0,0],[200,1],[744,2],[944,3]]},{"count":744,"start":2000,"stride":1,"freq_min"' \
                     ':0.36e9,"freq_max":0.368e9,"link_map":[[2000,4],[2200,5]]}]},{"id":"calibration_B",' \
                     '"coordinate_system":"ICRS","ra":"12:29:06.699","dec":"02:03:08.598","subbands":[{"freq_min"' \
                     ':0.35e9,"freq_max":1.05e9,"nchan":372,"input_link_map":[[1,0],[101,1]]}],"channels":[' \
                     '{"count":744,"start":0,"stride":2,"freq_min":0.35e9,"freq_max":0.368e9,"link_map":[[0,0],' \
                     '[200,1],[744,2],[944,3]]},{"count":744,"start":2000,"stride":1,"freq_min":0.36e9,"freq_max"' \
                     ':0.368e9,"link_map":[[2000,4],[2200,5]]}]}],"processing_blocks":[{"id":"pb-mvp01-20200325-00001"' \
                     ',"workflow":{"type":"realtime","id":"vis_receive","version":"0.1.0"},"parameters":{}},{"id":' \
                     '"pb-mvp01-20200325-00002","workflow":{"type":"realtime","id":"test_realtime","version":"0.1.0"}' \
                     ',"parameters":{}},{"id":"pb-mvp01-20200325-00003","workflow":{"type":"batch","id":"ical",' \
                     '"version":"0.1.0"},"parameters":{},"dependencies":[{"pb_id":"pb-mvp01-20200325-00001","type":' \
                     '["visibilities"]}]},{"id":"pb-mvp01-20200325-00004","workflow":{"type":"batch","id":"dpreb",' \
                     '"version":"0.1.0"},"parameters":{},"dependencies":[{"pb_id":"pb-mvp01-20200325-00003","type":' \
                     '["calibration"]}]}]}'
        tango_context.device.AssignResources(test_input)
        assert const.STR_ASSIGN_RESOURCES_SUCCESS in tango_context.device.activityMessage
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_AssignResources

    def test_ReleaseAllResources(self, tango_context):
        """Test for ReleaseAllResources"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_ReleaseAllResources) ENABLED START #
        tango_context.device.ReleaseAllResources()
        assert const.STR_REL_RESOURCES in tango_context.device.activityMessage
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_ReleaseAllResources

    def test_Scan_device_not_ready(self, tango_context, create_sdpsubarray_proxy):
        """Test for Scan"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_Scan_device_not_ready) ENABLED START #
        test_input = '{"id":1}'
        tango_context.device.Scan(test_input)
        time.sleep(1)
        assert const.ERR_DEVICE_NOT_READY in tango_context.device.activityMessage
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_Scan

    def test_Configure(self, tango_context, create_sdpsubarray_proxy):
        """Test for Configure"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_Configure) ENABLED START #
        create_sdpsubarray_proxy.toggleReadCbfOutLink = False
        time.sleep(2)
        test_input = '{"sdp":{ "scan_type": "science_A" }}'
        tango_context.device.Configure(test_input)
        time.sleep(1)
        assert create_sdpsubarray_proxy.obsState == ObsState.READY
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_Configure

    def test_Configure_invalid_key(self, tango_context):
        """Test for Configure command with invalid_key"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_Configure_invalid_key) ENABLED START #
        test_input = '{"invalid_key":"sbi-mvp01-20200325-00001"}'
        with pytest.raises(tango.DevFailed):
            tango_context.device.Configure(test_input)
        assert const.ERR_JSON_KEY_NOT_FOUND in tango_context.device.activityMessage
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_AssignResources

    def test_Configure_invalid_format(self, tango_context):
        """Test for Configure command with invalid_format"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_Configure_invalid_format) ENABLED START #
        test_input = '{"abc"}'
        with pytest.raises(tango.DevFailed):
            tango_context.device.Configure(test_input)
        assert const.ERR_INVALID_JSON_CONFIG in tango_context.device.activityMessage
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_AssignResources

    def test_Configure_generic_exception(self, tango_context):
        """Test for Configure command with invalid_format"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_Configure_generic_exception) ENABLED START #
        test_input = '[123]'
        with pytest.raises(tango.DevFailed):
            tango_context.device.Configure(test_input)
        assert const.ERR_CONFIGURE in tango_context.device.activityMessage
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_Configure_generic_exception

    def test_Scan(self, tango_context, create_sdpsubarray_proxy):
        """Test for Scan"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_Scan) ENABLED START #
        time.sleep(2)
        test_input = '{"id":1}'
        tango_context.device.Scan(test_input)
        time.sleep(1)
        assert create_sdpsubarray_proxy.obsState == ObsState.SCANNING
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_Scan

    def test_EndScan(self, tango_context, create_sdpsubarray_proxy):
        """Test for EndScan"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_EndScan) ENABLED START #
        create_sdpsubarray_proxy.obsState = ObsState.SCANNING
        time.sleep(2)
        tango_context.device.EndScan()
        tango_context.device.status()
        time.sleep(2)
        assert const.STR_ENDSCAN_SUCCESS in tango_context.device.activityMessage
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_EndScan

    def test_EndSB(self, tango_context, create_sdpsubarray_proxy):
        """Test for EndSB command."""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_EndSB) ENABLED START #
        tango_context.device.EndSB()
        time.sleep(2)
        assert create_sdpsubarray_proxy.ObsState == ObsState.IDLE
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_EndSB

    def test_EndSB_device_not_ready(self, tango_context):
        """Test for EndSB when SDP Subarray is not in Ready state command."""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_EndSB) ENABLED START #
        tango_context.device.EndSB()
        time.sleep(2)
        assert tango_context.device.activityMessage == const.ERR_DEVICE_NOT_READY
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_EndSB

    def test_EndScan_Invalid_State(self, tango_context):
        """Test for  Invalid EndScan"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_EndScan_Invalid_State) ENABLED START #
        tango_context.device.EndScan()
        time.sleep(2)
        assert const.ERR_DEVICE_NOT_IN_SCAN in tango_context.device.activityMessage
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_EndScan

    def test_versionId(self, tango_context):
        """Test for versionId"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_versionId) ENABLED START #
        # self.device.versionId
        assert tango_context.device.versionId == "0.5.4"
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_versionId

    def test_loggingLevel(self, tango_context):
        """Test for loggingLevel"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_loggingLevel) ENABLED START #
        tango_context.device.loggingLevel = LoggingLevel.INFO
        assert tango_context.device.loggingLevel == LoggingLevel.INFO
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_loggingLevel

    def test_healthState(self, tango_context):
        """Test for healthState"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_healthState) ENABLED START #
        assert tango_context.device.healthState == HealthState.OK
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_healthState

    def test_adminMode(self, tango_context):
        """Test for adminMode"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_adminMode) ENABLED START #
        assert tango_context.device.adminMode == AdminMode.ONLINE
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_adminMode

    def test_controlMode(self, tango_context):
        """Test for controlMode"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_controlMode) ENABLED START #
        control_mode = ControlMode.REMOTE
        tango_context.device.controlMode = control_mode
        assert tango_context.device.controlMode == control_mode
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_controlMode

    def test_simulationMode(self, tango_context):
        """Test for simulationMode"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_simulationMode) ENABLED START #
        simulation_mode = SimulationMode.FALSE
        tango_context.device.simulationMode = simulation_mode
        assert tango_context.device.simulationMode == simulation_mode
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_simulationMode

    def test_testMode(self, tango_context):
        """Test for testMode"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_testMode) ENABLED START #
        test_mode = TestMode.NONE
        tango_context.device.testMode = test_mode
        assert tango_context.device.testMode == test_mode
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_testMode

    def test_receiveAddresses(self, tango_context):
        """Test for receiveAddresses"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_receiveAddresses) ENABLED START #
        assert tango_context.device.receiveAddresses == ""
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_receiveAddresses

    def test_activeProcessingBlocks(self, tango_context):
        """Test for activeProcessingBlocks"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_activeProcessingBlocks) ENABLED START #
        assert tango_context.device.activeProcessingBlocks == ""
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_activeProcessingBlocks

    def test_activityMessage(self, tango_context):
        """Test for activityMessage"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_activityMessage) ENABLED START #
        tango_context.device.activityMessage = "test"
        assert tango_context.device.activityMessage == "test"
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_activityMessage

    def test_loggingTargets(self, tango_context):
        """Test for loggingTargets"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_loggingLevel) ENABLED START #
        tango_context.device.loggingTargets = ['tango::logger']
        assert 'tango::logger' in tango_context.device.loggingTargets
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_loggingTargets

    def test_buildState(self, tango_context):
        """Test for buildState"""
        # PROTECTED REGION ID(SdpSubarrayLeafNode.test_buildState) ENABLED START #
        assert tango_context.device.buildState == (
            "lmcbaseclasses, 0.5.4, A set of generic base devices for SKA Telescope.")
        # PROTECTED REGION END #    //  SdpSubarrayLeafNode.test_buildState
