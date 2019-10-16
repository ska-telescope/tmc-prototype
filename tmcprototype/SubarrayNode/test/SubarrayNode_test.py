#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of the SubarrayNode project
#
#
#
# Distributed under the terms of the BSD-3-Clause license.
# See LICENSE.txt for more info.
"""Contain the tests for the Subarray Node."""
from __future__ import print_function

# Path
import sys
import os
file_path = os.path.dirname(os.path.abspath(__file__))
module_path = os.path.abspath(os.path.join(file_path, os.pardir)) + "/SubarrayNode"
sys.path.insert(0, module_path)

path = os.path.join(os.path.dirname(__file__), os.pardir)
sys.path.insert(0, os.path.abspath(path))

# Imports
import tango
from tango import DevState
import pytest
from SubarrayNode.SubarrayNode import SubarrayNode
import CONST
import time

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
@pytest.mark.usefixtures("tango_context", "create_cbfsubarray1_proxy", "create_cspsubarray1_proxy")

class TestSubarrayNode(object):
    """Test case for packet generation."""
    # PROTECTED REGION ID(SubarrayNode.test_additionnal_import) ENABLED START #
    # PROTECTED REGION END #    //  SubarrayNode.test_additionnal_import
    device = SubarrayNode
    properties = {'CapabilityTypes': '', 'CentralLoggingTarget': '', 'ElementLoggingTarget': '',
                  'GroupDefinitions': '', 'MetricList': 'healthState', 'SkaLevel': '4',
                  'StorageLoggingTarget': 'localhost', 'SubID': '',
                  'DishLeafNodePrefix': 'ska_mid/tm_leaf_node/d',
                  }
    empty = None  # Should be []

    @classmethod
    def mocking(cls):
        """Mock external libraries."""
        # Example : Mock numpy
        # cls.numpy = SubarrayNode.numpy = MagicMock()
        # PROTECTED REGION ID(SubarrayNode.test_mocking) ENABLED START #
        # PROTECTED REGION END #    //  SubarrayNode.test_mocking

    def test_properties(self, tango_context):
        """Test for properties"""
        # PROTECTED REGION ID(SubarrayNode.test_properties) ENABLED START #
        # PROTECTED REGION END #    //  SubarrayNode.test_properties

    def test_Abort(self, tango_context):
        """Test for Abort"""
        # PROTECTED REGION ID(SubarrayNode.test_Abort) ENABLED START #
        # PROTECTED REGION END #    //  SubarrayNode.test_Abort

    def test_ConfigureCapability(self, tango_context):
        """Test for ConfigureCapability"""
        # PROTECTED REGION ID(SubarrayNode.test_ConfigureCapability) ENABLED START #
        # PROTECTED REGION END #    //  SubarrayNode.test_ConfigureCapability

    def test_DeconfigureAllCapabilities(self, tango_context):
        """Test for DeconfigureAllCapabilities"""
        # PROTECTED REGION ID(SubarrayNode.test_DeconfigureAllCapabilities) ENABLED START #
        # PROTECTED REGION END #    //  SubarrayNode.test_DeconfigureAllCapabilities

    def test_DeconfigureCapability(self, tango_context):
        """Test for DeconfigureCapability"""
        # PROTECTED REGION ID(SubarrayNode.test_DeconfigureCapability) ENABLED START #
        # PROTECTED REGION END #    //  SubarrayNode.test_DeconfigureCapability

    def test_Status(self, tango_context):
        """Test for Status"""
        # PROTECTED REGION ID(SubarrayNode.test_Status) ENABLED START #
        assert tango_context.device.Status() == CONST.STR_SA_INIT_SUCCESS
        # PROTECTED REGION END #    //  SubarrayNode.test_Status

    def test_State(self, tango_context):
        """Test for State"""
        # PROTECTED REGION ID(SubarrayNode.test_State) ENABLED START #
        assert tango_context.device.State() == DevState.OFF
        # PROTECTED REGION END #    //  SubarrayNode.test_State

    def test_healthState(self, tango_context):
        """Test for healthState"""
        # PROTECTED REGION ID(SubarrayNode.test_healthState) ENABLED START #
        assert tango_context.device.healthState == 1
        # PROTECTED REGION END #    //  SubarrayNode.test_healthState

    def test_AssignResources(self, tango_context, create_cbfsubarray1_proxy, create_cspsubarray1_proxy):
        """Test for AssignResources"""
        # PROTECTED REGION ID(SubarrayNode.test_AssignResources) ENABLED START #
        receptor_list = ['0001']
        tango_context.device.AssignResources(receptor_list)
        time.sleep(10)
        assert tango_context.device.State() == DevState.ON
        assert len(tango_context.device.receptorIDList) == 1
        assert tango_context.device.obsState == 0
        # PROTECTED REGION END #    //  SubarrayNode.test_AssignResources

    def test_Configure(self, tango_context, create_dish_proxy):
        """Test for Configure"""
        # PROTECTED REGION ID(SubarrayNode.test_Configure) ENABLED START #
        time.sleep(15)
        tango_context.device.Configure('{"scanID":12345,"pointing":{"target":{"system":"ICRS","name":'
                                       '"Polaris","RA":"02:31:49.0946","dec":"+89:15:50.7923"}},"dish":'
                                       '{"receiverBand":"1"},"csp":{"frequencyBand":"1","fsp":[{"fspID":1,'
                                       '"functionMode":"CORR","frequencySliceID":1,"integrationTime":1400,'
                                       '"corrBandwidth":0}]},"sdp":{"configure":'
                                       '[{"id":"realtime-20190627-0001","sbiId":"20190627-0001","workflow":'
                                       '{"id":"vis_ingest","type":"realtime","version":"0.1.0"},"parameters":'
                                       '{"numStations":4,"numChannels":372,"numPolarisations":4,'
                                       '"freqStartHz":0.35e9,"freqEndHz":1.05e9,"fields":{"0":'
                                       '{"system":"ICRS","name":"Polaris","ra":0.662432049839445,'
                                       '"dec":1.5579526053855042}}},"scanParameters":{"12345":'
                                       '{"fieldId":0,"intervalMs":1400}}}]}}')
        time.sleep(65)
        assert tango_context.device.obsState == 2
        time.sleep(45)
        create_dish_proxy.StopTrack()
        # PROTECTED REGION END #    //  SubarrayNode.test_Configure

    def test_Scan(self, tango_context):
        """Test for Scan"""
        # PROTECTED REGION ID(SubarrayNode.test_Scan) ENABLED START #
        tango_context.device.Scan('{"scanDuration": 10.0}')
        time.sleep(5)
        assert tango_context.device.obsState == 3
        # PROTECTED REGION END #    //  SubarrayNode.test_Scan

    def test_EndScan(self, tango_context):
        """Test for EndScan"""
        # PROTECTED REGION ID(SubarrayNode.test_EndScan) ENABLED START #
        #tango_context.obsState = CONST.OBS_STATE_ENUM_SCANNING
        tango_context.device.EndScan()
        time.sleep(10)
        assert tango_context.device.obsState == 2
        # PROTECTED REGION END #    //  SubarrayNode.test_EndScan

    def test_EndSB(self, tango_context):
        """Test for EndSB command."""
        # PROTECTED REGION ID(SubarrayNode.test_EndSB) ENABLED START #
        tango_context.device.EndSB()
        time.sleep(2)
        assert tango_context.device.ObsState == CONST.OBS_STATE_ENUM_IDLE
        # PROTECTED REGION END #    //  SubarrayNode.test_EndSB

    def test_EndSB_device_not_ready(self, tango_context):
        """Test for EndSB when SubarrayNode is not in Ready state command."""
        # PROTECTED REGION ID(SubarrayNode.test_EndSB) ENABLED START #
        tango_context.device.EndSB()
        time.sleep(2)
        assert tango_context.device.ObsState != CONST.OBS_STATE_ENUM_READY
        # assert tango_context.device.activityMessage == CONST.ERR_DEVICE_NOT_READY
        # PROTECTED REGION END #    //  SubarrayNode.test_EndSB

    def test_ReleaseAllResources(self, tango_context):
        """Test for ReleaseAllResources"""
        # PROTECTED REGION ID(SubarrayNode.test_ReleaseAllResources) ENABLED START #
        tango_context.device.ReleaseAllResources()
        assert tango_context.device.obsState == 0
        assert tango_context.device.State() == DevState.OFF
        with pytest.raises(tango.DevFailed):
            tango_context.device.ReleaseAllResources()
        assert CONST.RESRC_ALREADY_RELEASED in tango_context.device.activityMessage
        # PROTECTED REGION END #    //  SubarrayNode.test_ReleaseAllResources

    def test_ReleaseResources(self, tango_context):
        """Test for ReleaseResources"""
        # PROTECTED REGION ID(SubarrayNode.test_ReleaseResources) ENABLED START #
        # PROTECTED REGION END #    //  SubarrayNode.test_ReleaseResources

    def test_Reset(self, tango_context):
        """Test for Reset"""
        # PROTECTED REGION ID(SubarrayNode.test_Reset) ENABLED START #
        assert tango_context.device.Reset() is None
        # PROTECTED REGION END #    //  SubarrayNode.test_Reset

    def test_Resume(self, tango_context):
        """Test for Resume"""
        # PROTECTED REGION ID(SubarrayNode.test_Resume) ENABLED START #
        # PROTECTED REGION END #    //  SubarrayNode.test_Resume

    def test_activationTime(self, tango_context):
        """Test for activationTime"""
        # PROTECTED REGION ID(SubarrayNode.test_activationTime) ENABLED START #
        assert tango_context.device.activationTime == 0.0
        # PROTECTED REGION END #    //  SubarrayNode.test_activationTime

    def test_adminMode(self, tango_context):
        """Test for adminMode"""
        # PROTECTED REGION ID(SubarrayNode.test_adminMode) ENABLED START #
        assert tango_context.device.adminMode == 0
        # PROTECTED REGION END #    //  SubarrayNode.test_adminMode

    def test_buildState(self, tango_context):
        """Test for buildState"""
        # PROTECTED REGION ID(SubarrayNode.test_buildState) ENABLED START #
        assert tango_context.device.buildState == (
            "lmcbaseclasses, 0.1.3, A set of generic base devices for SKA Telescope.")
        # PROTECTED REGION END #    //  SubarrayNode.test_buildState

    def test_centralLoggingLevel(self, tango_context):
        """Test for centralLoggingLevel"""
        # PROTECTED REGION ID(SubarrayNode.test_centralLoggingLevel) ENABLED START #
        tango_context.device.centralLoggingLevel = int(tango.LogLevel.LOG_DEBUG)
        assert tango_context.device.centralLoggingLevel == int(tango.LogLevel.LOG_DEBUG)
        # PROTECTED REGION END #    //  SubarrayNode.test_centralLoggingLevel

    def test_configurationDelayExpected(self, tango_context):
        """Test for configurationDelayExpected"""
        # PROTECTED REGION ID(SubarrayNode.test_configurationDelayExpected) ENABLED START #
        assert tango_context.device.configurationDelayExpected == 0
        # PROTECTED REGION END #    //  SubarrayNode.test_configurationDelayExpected

    def test_configurationProgress(self, tango_context):
        """Test for configurationProgress"""
        # PROTECTED REGION ID(SubarrayNode.test_configurationProgress) ENABLED START #
        assert tango_context.device.configurationProgress == 0
        # PROTECTED REGION END #    //  SubarrayNode.test_configurationProgress

    def test_controlMode(self, tango_context):
        """Test for controlMode"""
        # PROTECTED REGION ID(SubarrayNode.test_controlMode) ENABLED START #
        control_mode = 0
        tango_context.device.controlMode = control_mode
        assert tango_context.device.controlMode == control_mode
        # PROTECTED REGION END #    //  SubarrayNode.test_controlMode

    def test_elementLoggingLevel(self, tango_context):
        """Test for elementLoggingLevel"""
        # PROTECTED REGION ID(SubarrayNode.test_elementLoggingLevel) ENABLED START #
        tango_context.device.elementLoggingLevel = int(tango.LogLevel.LOG_DEBUG)
        assert tango_context.device.elementLoggingLevel == int(tango.LogLevel.LOG_DEBUG)
        # PROTECTED REGION END #    //  SubarrayNode.test_elementLoggingLevel

    def test_obsMode(self, tango_context):
        """Test for obsMode"""
        # PROTECTED REGION ID(SubarrayNode.test_obsMode) ENABLED START #
        assert tango_context.device.obsMode == 0
        # PROTECTED REGION END #    //  SubarrayNode.test_obsMode

    def test_obsState(self, tango_context):
        """Test for obsState"""
        # PROTECTED REGION ID(SubarrayNode.test_obsState) ENABLED START #
        assert tango_context.device.obsState == 0
        # PROTECTED REGION END #    //  SubarrayNode.test_obsState

    def test_simulationMode(self, tango_context):
        """Test for simulationMode"""
        # PROTECTED REGION ID(SubarrayNode.test_simulationMode) ENABLED START #
        simulation_mode = 0
        tango_context.device.simulationMode = simulation_mode
        assert tango_context.device.simulationMode == simulation_mode
        # PROTECTED REGION END #    //  SubarrayNode.test_simulationMode

    def test_storageLoggingLevel(self, tango_context):
        """Test for storageLoggingLevel"""
        # PROTECTED REGION ID(SubarrayNode.test_storageLoggingLevel) ENABLED START #
        tango_context.device.storageLoggingLevel = int(tango.LogLevel.LOG_DEBUG)
        assert tango_context.device.storageLoggingLevel == int(tango.LogLevel.LOG_DEBUG)
        # PROTECTED REGION END #    //  SubarrayNode.test_storageLoggingLevel

    def test_testMode(self, tango_context):
        """Test for testMode"""
        # PROTECTED REGION ID(SubarrayNode.test_testMode) ENABLED START #
        test_mode = CONST.STR_FALSE
        tango_context.device.testMode = test_mode
        assert tango_context.device.testMode == test_mode
        # PROTECTED REGION END #    //  SubarrayNode.test_testMode

    def test_versionId(self, tango_context):
        """Test for versionId"""
        # PROTECTED REGION ID(SubarrayNode.test_versionId) ENABLED START #
        assert tango_context.device.versionId == "0.1.3"
        # PROTECTED REGION END #    //  SubarrayNode.test_versionId

    def test_scanID(self, tango_context):
        """Test for scanID"""
        # PROTECTED REGION ID(SubarrayNode.test_scanID) ENABLED START #
        assert tango_context.device.scanID == ""
        # PROTECTED REGION END #    //  SubarrayNode.test_scanID

    def test_sbID(self, tango_context):
        """Test for sbID"""
        # PROTECTED REGION ID(SubarrayNode.test_sbID) ENABLED START #
        assert tango_context.device.sbID == ""
        # PROTECTED REGION END #    //  SubarrayNode.test_sbID

    def test_activityMessage(self, tango_context):
        """Test for activityMessage"""
        # PROTECTED REGION ID(SubarrayNode.test_activityMessage) ENABLED START #
        message = CONST.STR_OK
        tango_context.device.activityMessage = message
        assert tango_context.device.activityMessage == message
        # PROTECTED REGION END #    //  SubarrayNode.test_activityMessage


    def test_configuredCapabilities(self, tango_context):
        """Test for configuredCapabilities"""
        # PROTECTED REGION ID(SubarrayNode.test_configuredCapabilities) ENABLED START #
        assert tango_context.device.configuredCapabilities is None
        # PROTECTED REGION END #    //  SubarrayNode.test_configuredCapabilities

    def test_receptorIDList(self, tango_context):
        """Test for receptorIDList"""
        # PROTECTED REGION ID(SubarrayNode.test_receptorIDList) ENABLED START #
        assert tango_context.device.receptorIDList is None
        # PROTECTED REGION END #    //  SubarrayNode.test_receptorIDList
