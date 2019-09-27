#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of the CspSubarrayLeafNode project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.
"""Contain the tests for the ."""

# Path
import sys
import os
# path = os.path.join(os.path.dirname(__file__), os.pardir)
# sys.path.insert(0, os.path.abspath(path))

file_path = os.path.dirname(os.path.abspath(__file__))
module_path = os.path.abspath(os.path.join(file_path, os.pardir)) + "/CspSubarrayLeafNode"
sys.path.insert(0, module_path)

path = os.path.join(os.path.dirname(__file__), os.pardir)
sys.path.insert(0, os.path.abspath(path))

# Imports
from time import sleep
from mock import MagicMock
#from tango import DevFailed, DevState
from tango import DevState, EventType, DeviceProxy
#from devicetest import DeviceTestCase, main
from CspSubarrayLeafNode.CspSubarrayLeafNode import CspSubarrayLeafNode
import CONST
import pytest
import json
import time
import tango

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
@pytest.mark.usefixtures("tango_context", "create_cspsubarray1_proxy")

class TestCspSubarrayLeafNode(object):
    """Test case for packet generation."""
    # PROTECTED REGION ID(CspSubarrayLeafNode.test_additionnal_import) ENABLED START #
    # PROTECTED REGION END #    //  CspSubarrayLeafNode.test_additionnal_import
    device = CspSubarrayLeafNode
    properties = {'SkaLevel': '3', 'GroupDefinitions': '', 'CentralLoggingTarget': '',
                  'ElementLoggingTarget': '', 'StorageLoggingTarget': 'localhost',
                  'CspSubarrayNodeFQDN': 'mid_csp/elt/subarray01',}
    empty = None  # Should be []

    @classmethod
    def mocking(cls):
        """Mock external libraries."""
        # Example : Mock numpy
        # cls.numpy = CspSubarrayLeafNode.numpy = MagicMock()
        # PROTECTED REGION ID(CspSubarrayLeafNode.test_mocking) ENABLED START #
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.test_mocking

    # TODO: Test case for activityMessage
    # def test_activityMessage(self, tango_context):
    #     """Test for activityMessage"""
    #     # PROTECTED REGION ID(CspSubarrayLeafNode.test_activityMessage) ENABLED START #
    #     assert tango_context.device.activityMessage != " "
    #     # PROTECTED REGION END #    //  CspSubarrayLeafNode.test_activityMessage

    def test_State(self, tango_context):
        """Test for State"""
        # PROTECTED REGION ID(CspSubarrayLeafNode.test_State) ENABLED START #
        assert tango_context.device.State() == DevState.ALARM
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.test_State

    def test_Status(self, tango_context):
        """Test for Status"""
        # PROTECTED REGION ID(CspSubarrayLeafNode.test_Status) ENABLED START #
        assert tango_context.device.Status() != CONST.STR_CSPSALN_INIT_SUCCESS
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.test_Status

    def test_delayModel(self, tango_context):
        """Test for delayModel"""
        # PROTECTED REGION ID(CspSubarrayLeafNode.test_delayModel) ENABLED START #
        assert tango_context.device.delayModel == " "
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.test_delayModel

    def test_GetVersionInfo(self, create_cspsubarray1_proxy):
        """Test for GetVersionInfo"""
        # PROTECTED REGION ID(CspSubarrayLeafNode.test_GetVersionInfo) ENABLED START #
        #create_cspsubarray1_proxy.device.GetVersionInfo()
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.test_GetVersionInfo

    def test_Reset(self, create_cspsubarray1_proxy):
        """Test for Reset"""
        # PROTECTED REGION ID(CspSubarrayLeafNode.test_Reset) ENABLED START #
        #create_cspsubarray1_proxy.device.Reset() is None
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.test_Reset

    #TODO: Test for ConfigureScan
    # def test_ConfigureScan(self, tango_context):
    #     """Test for ConfigureScan"""
    #     # PROTECTED REGION ID(CspSubarrayLeafNode.test_ConfigureScan) ENABLED START #
    #     configurescan_input = '{"csp":{"frequencyBand":"1","delayModelSubscriptionPoint":"",' \
    #                  '"visDestinationAddressSubscriptionPoint":"","fsp":[{"fspID":"1","functionMode":' \
    #                  '"CORR","frequencySliceID":1,"integrationTime":1400,"corrBandwidth":0,' \
    #                  '"channelAveragingMap":[]},{"fspID":"2","functionMode":"CORR","frequencySliceID":1,' \
    #                  '"integrationTime":1400,"corrBandwidth":0,"channelAveragingMap":[]}]}}'
    #     res = tango_context.device.ConfigureScan(configurescan_input)
    #     tango_context.device.status()
    #     time.sleep(1)
    #     assert CONST.STR_CONFIGURESCAN_SUCCESS in tango_context.device.activityMessage \
    #            and res is None
    #     # PROTECTED REGION END #    //  CspSubarrayLeafNode.test_ConfigureScan

    def test_ConfigureScan_invalid_json(self, tango_context):
        """
        Test case to check invalid JSON format (Negative test case)
        :param tango_context:
        :return:
        """
        configurescan_input = '{"invalid_key"}'
        with pytest.raises(tango.DevFailed):
            tango_context.device.ConfigureScan(configurescan_input)
        time.sleep(1)
        assert CONST.ERR_INVALID_JSON_CONFIG_SCAN in tango_context.device.activityMessage

    # TODO: Test for EndScan and EndSB
    # def test_EndScan(self, tango_context):
    #     """Test for EndScan"""
    #     # PROTECTED REGION ID(CspSubarrayLeafNode.test_EndScan) ENABLED START #
    #     configurescan_input = '{"csp":{"frequencyBand":"1","delayModelSubscriptionPoint":"",' \
    #                  '"visDestinationAddressSubscriptionPoint":"","fsp":[{"fspID":"1","functionMode":' \
    #                  '"CORR","frequencySliceID":1,"integrationTime":1400,"corrBandwidth":0,' \
    #                  '"channelAveragingMap":[]},{"fspID":"2","functionMode":"CORR","frequencySliceID":1,' \
    #                  '"integrationTime":1400,"corrBandwidth":0,"channelAveragingMap":[]}]}}'
    #     tango_context.device.ConfigureScan(configurescan_input)
    #     time.sleep(3)
    #     endscan_input = ['{"scanDuration": 10.0}']
    #     tango_context.device.StartScan(endscan_input)
    #     time.sleep(2)
    #     res = tango_context.device.EndScan()
    #     tango_context.device.status()
    #     time.sleep(1)
    #     assert CONST.STR_ENDSCAN_SUCCESS in tango_context.device.activityMessage \
    #            and res is None
    #     # PROTECTED REGION END #    //  CspSubarrayLeafNode.test_EndScan

    # def test_EndSB(self, tango_context, create_cspsubarray1_proxy):
    #     """Test for EndSB command."""
    #     # PROTECTED REGION ID(CspSubarrayLeafNode.test_EndSB) ENABLED START #
    #     tango_context.device.EndSB()
    #     time.sleep(2)
    #     assert create_cspsubarray1_proxy.ObsState == CONST.ENUM_IDLE
    #     # PROTECTED REGION END #    //  CspSubarrayLeafNode.test_EndSB

    def test_EndScan_Invalide_state(self, tango_context):
        """Test for  Invalid EndScan"""
        # PROTECTED REGION ID(CspSubarrayLeafNode.test_EndScan) ENABLED START #
        time.sleep(1)
        res = tango_context.device.EndScan()
        time.sleep(1)
        assert CONST.ERR_DEVICE_NOT_IN_SCAN in tango_context.device.activityMessage \
               and res is None
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.test_EndScan

    # TODO: Test for StartScan
    # def test_StartScan(self, tango_context):
    #     """Test for StartScan"""
    #     # PROTECTED REGION ID(CspSubarrayLeafNode.test_StartScan) ENABLED START #
    #     configurescan_input = '{"csp":{"frequencyBand":"1","delayModelSubscriptionPoint":"",' \
    #                   '"visDestinationAddressSubscriptionPoint":"","fsp":[{"fspID":"1","functionMode":' \
    #                   '"CORR","frequencySliceID":1,"integrationTime":1400,"corrBandwidth":0,' \
    #                   '"channelAveragingMap":[]},{"fspID":"2","functionMode":"CORR","frequencySliceID":1,' \
    #                   '"integrationTime":1400,"corrBandwidth":0,"channelAveragingMap":[]}]}}'
    #     tango_context.device.ConfigureScan(configurescan_input)
    #     time.sleep(2)
    #     startscan_input = ['{"scanDuration": 10.0}']
    #     tango_context.device.StartScan(startscan_input)
    #     time.sleep(1)
    #     assert CONST.STR_STARTSCAN_SUCCESS in tango_context.device.activityMessage
    #     # PROTECTED REGION END #    //  CspSubarrayLeafNode.test_StartScan

    def test_StartScan_Device_Not_Ready(self, tango_context):
        """Test for StartScan when device is not in READY state."""
        # PROTECTED REGION ID(CspSubarrayLeafNode.test_StartScan_Device_Not_Ready) ENABLED START #
        time.sleep(2)
        tango_context.device.StartScan(['{"scanDuration": 10.0}'])
        time.sleep(1)
        assert CONST.ERR_DEVICE_NOT_READY in tango_context.device.activityMessage
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.test_StartScan_Device_Not_Ready

    def test_ReleaseAllResources(self, tango_context):
        """Test for ReleaseResources"""
        res = tango_context.device.ReleaseAllResources()
        tango_context.device.status()
        time.sleep(1)
        assert CONST.STR_REMOVE_ALL_RECEPTORS_SUCCESS in tango_context.device.activityMessage \
               and res is None
    #     # PROTECTED REGION END #    //  CspSubarrayLeafNode.test_ReleaseResources

    def test_AssignResources(self, tango_context):
        """Test for AssignResources"""
        # PROTECTED REGION ID(CspSubarrayLeafNode.test_AssignResources) ENABLED START #
        assignresources_input = []
        assignresources_input.append('{"dish":{"receptorIDList":["0001","0002"]}}')
        res = tango_context.device.AssignResources(assignresources_input)
        tango_context.device.status()
        time.sleep(1)
        assert CONST.STR_ADD_RECEPTORS_SUCCESS in tango_context.device.activityMessage \
               and res is None
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.test_AssignResources

    def test_AssignResources_invalid_json(self, tango_context):
        """
        Test case to check invalid JSON format (Negative test case)
        :param tango_context:
        :return:
        """
        assignresources_input = '{"invalid_key"}'
        with pytest.raises(tango.DevFailed):
            tango_context.device.AssignResources(assignresources_input)
        time.sleep(1)
        assert CONST.ERR_INVALID_JSON_ASSIGN_RES in tango_context.device.activityMessage

    def test_AssignResources_key_not_found(self, tango_context):
        """
        Test case for missing key in JSON string (Negative test case)
        :param tango_context:
        :return:
        """
        assignresources_input = []
        assignresources_input.append('{"dis":{"receptorIDList":["0001","0002"]}}')
        with pytest.raises(tango.DevFailed):
            tango_context.device.AssignResources(assignresources_input)
        time.sleep(1)
        assert CONST.ERR_JSON_KEY_NOT_FOUND in tango_context.device.activityMessage

    def test_EndSB_device_not_ready(self, tango_context):
        """Test for EndSB when CSP Subarray is not in Ready state command."""
        # PROTECTED REGION ID(CspSubarrayLeafNode.test_EndSB) ENABLED START #
        tango_context.device.EndSB()
        time.sleep(2)
        assert tango_context.device.activityMessage == CONST.ERR_DEVICE_NOT_READY
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.test_EndSB

    def test_buildState(self, tango_context):
        """Test for buildState"""
        # PROTECTED REGION ID(CspSubarrayLeafNode.test_buildState) ENABLED START #
        assert tango_context.device.buildState == (
            "lmcbaseclasses, 0.1.3, A set of generic base devices for SKA Telescope.")
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.test_buildState

    def test_versionId(self, tango_context):
        """Test for versionId"""
        # PROTECTED REGION ID(CspSubarrayLeafNode.test_versionId) ENABLED START #
        assert tango_context.device.versionId == "0.1.3"
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.test_versionId

    def test_centralLoggingLevel(self, tango_context):
        """Test for centralLoggingLevel"""
        # PROTECTED REGION ID(CspSubarrayLeafNode.test_centralLoggingLevel) ENABLED START #
        tango_context.device.centralLoggingLevel = int(tango.LogLevel.LOG_DEBUG)
        assert tango_context.device.centralLoggingLevel == int(tango.LogLevel.LOG_DEBUG)
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.test_centralLoggingLevel

    def test_elementLoggingLevel(self, tango_context):
        """Test for elementLoggingLevel"""
        # PROTECTED REGION ID(CspSubarrayLeafNode.test_elementLoggingLevel) ENABLED START #
        tango_context.device.elementLoggingLevel = int(tango.LogLevel.LOG_DEBUG)
        assert tango_context.device.elementLoggingLevel == int(tango.LogLevel.LOG_DEBUG)
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.test_elementLoggingLevel

    def test_storageLoggingLevel(self, tango_context):
        """Test for storageLoggingLevel"""
        # PROTECTED REGION ID(CspSubarrayLeafNode.test_storageLoggingLevel) ENABLED START #
        tango_context.device.storageLoggingLevel = int(tango.LogLevel.LOG_DEBUG)
        assert tango_context.device.storageLoggingLevel == int(tango.LogLevel.LOG_DEBUG)
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.test_storageLoggingLevel

    def test_healthState(self, tango_context):
        """Test for healthState"""
        # PROTECTED REGION ID(CspSubarrayLeafNode.test_healthState) ENABLED START #
        assert tango_context.device.healthState == 0
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.test_healthState

    def test_adminMode(self, tango_context):
        """Test for adminMode"""
        # PROTECTED REGION ID(CspSubarrayLeafNode.test_adminMode) ENABLED START #
        assert tango_context.device.adminMode == 0
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.test_adminMode

    def test_controlMode(self, tango_context):
        """Test for controlMode"""
        # PROTECTED REGION ID(CspSubarrayLeafNode.test_controlMode) ENABLED START #
        control_mode = 0
        tango_context.device.controlMode = control_mode
        assert tango_context.device.controlMode == control_mode
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.test_controlMode

    def test_simulationMode(self, tango_context):
        """Test for simulationMode"""
        # PROTECTED REGION ID(CspSubarrayLeafNode.test_simulationMode) ENABLED START #
        simulation_mode = 0
        tango_context.device.simulationMode = simulation_mode
        assert tango_context.device.simulationMode == simulation_mode
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.test_simulationMode

    def test_testMode(self, tango_context):
        """Test for testMode"""
        # PROTECTED REGION ID(CspSubarrayLeafNode.test_testMode) ENABLED START #
        test_mode = CONST.STR_FALSE
        tango_context.device.testMode = test_mode
        assert tango_context.device.testMode == test_mode
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.test_testMode

    # TODO: Test for State
    # def test_state(self):
    #     """Test for state"""
    #     # PROTECTED REGION ID(CspSubarrayLeafNode.test_state) ENABLED START #
    #     self.device.state
    #     # PROTECTED REGION END #    //  CspSubarrayLeafNode.test_state

    def test_visDestinationAddress(self, tango_context):
        """Test for visDestinationAddress"""
        # PROTECTED REGION ID(CspSubarrayLeafNode.test_visDestinationAddress) ENABLED START #
        assert tango_context.device.visDestinationAddress == " "
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.test_visDestinationAddress

    def test_opState(self, tango_context):
        """Test for opState"""
        # PROTECTED REGION ID(CspSubarrayLeafNode.test_opState) ENABLED START #
        assert tango_context.device.opState == 0
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.test_opState
