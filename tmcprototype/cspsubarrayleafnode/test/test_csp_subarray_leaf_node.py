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

# Imports
from tango import DevState, EventType, DeviceProxy
from cspsubarrayleafnode import CspSubarrayLeafNode, const
from ska.base.control_model import HealthState, ObsState, TestMode, SimulationMode, ControlMode, AdminMode, LoggingLevel
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
@pytest.mark.usefixtures("tango_context", "create_cspsubarray1_proxy", "create_sdpsubarrayln1_proxy")

class TestCspSubarrayLeafNode(object):
    """Test case for packet generation."""
    # PROTECTED REGION ID(CspSubarrayLeafNode.test_additionnal_import) ENABLED START #
    # PROTECTED REGION END #    //  CspSubarrayLeafNode.test_additionnal_import
    device = CspSubarrayLeafNode
    properties = {'SkaLevel': '3', 'GroupDefinitions': '',
                  'LoggingLevelDefault': '4', 'LoggingTargetsDefault': 'console::cout',
                  'CspSubarrayFQDN': 'mid_csp/elt/subarray_01',}
    empty = None  # Should be []

    @classmethod
    def mocking(cls):
        """Mock external libraries."""
        # Example : Mock numpy
        # cls.numpy = CspSubarrayLeafNode.numpy = MagicMock()
        # PROTECTED REGION ID(CspSubarrayLeafNode.test_mocking) ENABLED START #
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.test_mocking

    def test_State(self, tango_context):
        """Test for State"""
        # PROTECTED REGION ID(CspSubarrayLeafNode.test_State) ENABLED START #
        assert tango_context.device.State() == DevState.ALARM
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.test_State

    def test_Status(self, tango_context):
        """Test for Status"""
        # PROTECTED REGION ID(CspSubarrayLeafNode.test_Status) ENABLED START #
        assert tango_context.device.Status() != const.STR_CSPSALN_INIT_SUCCESS
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.test_Status

    def test_GetVersionInfo(self, tango_context):
        """Test for GetVersionInfo"""
        # PROTECTED REGION ID(CspSubarrayLeafNode.test_GetVersionInfo) ENABLED START #
        assert tango_context.device.versionInFo == " "
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.test_GetVersionInfo

    def test_Reset(self, create_cspsubarray1_proxy):
        """Test for Reset"""
        # PROTECTED REGION ID(CspSubarrayLeafNode.test_Reset) ENABLED START #
        #create_cspsubarray1_proxy.device.Reset() is None
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.test_Reset

    def test_AssignResources_invalid_json(self, tango_context, create_cspsubarray1_proxy):
        """
        Test case to check invalid JSON format (Negative test case)
        :param tango_context:
        :return:
        """
        assignresources_input = '{"invalid_key"}'
        with pytest.raises(tango.DevFailed):
            tango_context.device.AssignResources(assignresources_input)
        time.sleep(1)
        assert create_cspsubarray1_proxy.state() == DevState.OFF
        assert const.ERR_INVALID_JSON_ASSIGN_RES in tango_context.device.activityMessage

    def test_AssignResources_key_not_found(self, tango_context, create_cspsubarray1_proxy):
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
        assert create_cspsubarray1_proxy.state() == DevState.OFF
        assert const.ERR_JSON_KEY_NOT_FOUND in tango_context.device.activityMessage

    def test_AssignResources(self, tango_context,  create_cspsubarray1_proxy):
        """Test for AssignResources"""
        # PROTECTED REGION ID(CspSubarrayLeafNode.test_AssignResources) ENABLED START #
        assignresources_input = []
        assignresources_input.append('{"dish":{"receptorIDList":["0001","0002"]}}')
        res = tango_context.device.AssignResources(assignresources_input)
        tango_context.device.status()
        time.sleep(1)
        assert create_cspsubarray1_proxy.state() == DevState.ON
        assert const.STR_ADD_RECEPTORS_SUCCESS in tango_context.device.activityMessage \
               and res is None
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.test_AssignResources

    def test_StartScan_Device_Not_Ready(self, tango_context):
        """Test for StartScan when device is not in READY state."""
        # PROTECTED REGION ID(CspSubarrayLeafNode.test_StartScan_Device_Not_Ready) ENABLED START #
        time.sleep(2)
        tango_context.device.StartScan(['{"scanDuration": 10.0}'])
        time.sleep(1)
        assert const.ERR_DEVICE_NOT_READY in tango_context.device.activityMessage
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.test_StartScan_Device_Not_Ready

    def test_Configure_invalid_json(self, tango_context, create_cspsubarray1_proxy):
        """
        Test case to check invalid JSON format (Negative test case)
        :param tango_context:
        :return:
        """
        configure_input = '{"invalid_key"}'
        with pytest.raises(tango.DevFailed):
            tango_context.device.Configure(configure_input)
        time.sleep(1)
        assert const.ERR_INVALID_JSON_CONFIG in tango_context.device.activityMessage
        assert create_cspsubarray1_proxy.obsState is not ObsState.READY

    def test_StartScan_generic_exception(self, tango_context):
        """
        Test case to check generic exception (Negative test case)
        :param tango_context:
        :return:
        """
        StartScan_input = '[123]'
        with pytest.raises(tango.DevFailed):
            tango_context.device.StartScan(StartScan_input)
        time.sleep(1)
        assert const.ERR_STARTSCAN_RESOURCES in tango_context.device.activityMessage

    def test_Configure(self, tango_context, create_cspsubarray1_proxy, create_sdpsubarrayln1_proxy):
        """Test for Configure"""
        # PROTECTED REGION ID(CspSubarrayLeafNode.test_Configure) ENABLED START #
        create_sdpsubarrayln1_proxy.write_attribute('receiveAddresses','Null')
        time.sleep(2)
        configure_input = '{"frequencyBand": "1", "fsp": [{"fspID": 1, "functionMode": "CORR", ' \
                              '"frequencySliceID": 1, "integrationTime": 1400, "corrBandwidth": 0}], ' \
                              '"delayModelSubscriptionPoint": "ska_mid/tm_leaf_node/csp_subarray01/delayModel", ' \
                              '"visDestinationAddressSubscriptionPoint": "ska_mid/tm_leaf_node/sdp_subarray01/receiveAddresses", ' \
                              '"pointing": {"target": {"system": "ICRS", "name": "Polaris", "RA": "20:21:10.31", ' \
                              '"dec": "-30:52:17.3"}}, "scanID": "123"}'
        time.sleep(4)
        tango_context.device.Configure(configure_input)
        time.sleep(10)
        create_sdpsubarrayln1_proxy.write_attribute('receiveAddresses', '{"scanId":123,"totalChannels":0,'
                                                                        '"receiveAddresses":'
                                                                        '[{"fspId":1,"hosts":[]}]}')
        time.sleep(10)
        assert create_cspsubarray1_proxy.obsState == ObsState.READY
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.test_Configure

    def test_delayModel(self, tango_context):
        """Test for delayModel"""
        # PROTECTED REGION ID(CspSubarrayLeafNode.test_delayModel) ENABLED START #
        _assert_flag = True
        delay_model_json = json.loads(tango_context.device.delayModel)
        for delayModel in (delay_model_json['delayModel']):
            for delayDetails in delayModel['delayDetails']:
                for receptorDelayDetails in delayDetails['receptorDelayDetails']:
                    # Check if length of delay coefficients array is 6 and all the elements in array are float
                    delay_coeff_list = receptorDelayDetails['delayCoeff']
                    fsid = receptorDelayDetails['fsid']
                    if len(delay_coeff_list)== 6:
                        for i in range(0, 6):
                            if not isinstance(delay_coeff_list[i], float) :
                                _assert_flag = False
                                assert 0
                                break
                    else:
                        _assert_flag = False
                        assert 0
                        break

                    if not fsid in range(1, 27):
                        _assert_flag = False
                        assert 0
                        break

                # Check if receptor id is in the range 1 to 197
                if _assert_flag == False:
                    break
                elif not int(delayDetails['receptor']) in range(1, 198):
                    _assert_flag = False
                    assert 0
                    break

            # Check if epoch is empty and is float
            epoch = delayModel['epoch']
            if _assert_flag == False:
                break
            elif not (epoch) or not isinstance(float(epoch), float):
                _assert_flag = False
                assert 0
                break
            else:
                pass

        if _assert_flag == True:
            assert 1
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.test_delayModel

    def test_StartScan(self, tango_context, create_cspsubarray1_proxy):
        """Test for StartScan"""
        # PROTECTED REGION ID(CspSubarrayLeafNode.test_StartScan) ENABLED START #
        startscan_input = ['{"scanDuration": 10.0}']
        tango_context.device.StartScan(startscan_input)
        time.sleep(2)
        obs_state = create_cspsubarray1_proxy.obsState
        assert obs_state == ObsState.SCANNING
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.test_StartScan

    def test_EndScan(self, tango_context, create_cspsubarray1_proxy):
        """Test for EndScan"""
        # PROTECTED REGION ID(CspSubarrayLeafNode.test_EndScan) ENABLED START #
        tango_context.device.EndScan()
        time.sleep(2)
        obs_state = create_cspsubarray1_proxy.obsState
        assert obs_state == ObsState.READY
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.test_EndScan

    def test_GoToIdle(self, tango_context, create_cspsubarray1_proxy):
        """Test for GoToIdle command."""
        # PROTECTED REGION ID(CspSubarrayLeafNode.test_GoToIdle) ENABLED START #
        tango_context.device.GoToIdle()
        time.sleep(2)
        obs_state = create_cspsubarray1_proxy.obsState
        assert obs_state == ObsState.IDLE
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.test_GoToIdle

    def test_EndScan_Invalid_state(self, tango_context):
        """Test for  Invalid EndScan"""
        # PROTECTED REGION ID(CspSubarrayLeafNode.test_EndScan) ENABLED START #
        time.sleep(1)
        res = tango_context.device.EndScan()
        time.sleep(1)
        assert const.ERR_DEVICE_NOT_IN_SCAN in tango_context.device.activityMessage \
               and res is None
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.test_EndScan

    def test_GoToIdle_device_not_ready(self, tango_context):
        """Test for GoToIdle when CSP Subarray is not in Ready state command."""
        # PROTECTED REGION ID(CspSubarrayLeafNode.test_GoToIdle) ENABLED START #
        tango_context.device.GoToIdle()
        time.sleep(2)
        assert tango_context.device.activityMessage == const.ERR_DEVICE_NOT_READY
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.test_EndSB

    def test_ReleaseAllResources(self, tango_context, create_cspsubarray1_proxy):
        """Test for ReleaseResources"""
        res = tango_context.device.ReleaseAllResources()
        tango_context.device.status()
        time.sleep(1)
        assert create_cspsubarray1_proxy.state() == DevState.OFF
        assert const.STR_REMOVE_ALL_RECEPTORS_SUCCESS in tango_context.device.activityMessage \
               and res is None
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.test_ReleaseResources

    def test_buildState(self, tango_context):
        """Test for buildState"""
        # PROTECTED REGION ID(CspSubarrayLeafNode.test_buildState) ENABLED START #
        assert tango_context.device.buildState == (
            "lmcbaseclasses, 0.5.1, A set of generic base devices for SKA Telescope.")
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.test_buildState

    def test_versionId(self, tango_context):
        """Test for versionId"""
        # PROTECTED REGION ID(CspSubarrayLeafNode.test_versionId) ENABLED START #
        assert tango_context.device.versionId == "0.5.1"
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.test_versionId

    def test_healthState(self, tango_context):
        """Test for healthState"""
        # PROTECTED REGION ID(CspSubarrayLeafNode.test_healthState) ENABLED START #
        assert tango_context.device.healthState == HealthState.OK
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.test_healthState

    def test_adminMode(self, tango_context):
        """Test for adminMode"""
        # PROTECTED REGION ID(CspSubarrayLeafNode.test_adminMode) ENABLED START #
        assert tango_context.device.adminMode == AdminMode.ONLINE
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.test_adminMode

    def test_controlMode(self, tango_context):
        """Test for controlMode"""
        # PROTECTED REGION ID(CspSubarrayLeafNode.test_controlMode) ENABLED START #
        control_mode = ControlMode.REMOTE
        tango_context.device.controlMode = control_mode
        assert tango_context.device.controlMode == control_mode
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.test_controlMode

    def test_simulationMode(self, tango_context):
        """Test for simulationMode"""
        # PROTECTED REGION ID(CspSubarrayLeafNode.test_simulationMode) ENABLED START #
        simulation_mode = SimulationMode.FALSE
        tango_context.device.simulationMode = simulation_mode
        assert tango_context.device.simulationMode == simulation_mode
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.test_simulationMode

    def test_testMode(self, tango_context):
        """Test for testMode"""
        # PROTECTED REGION ID(CspSubarrayLeafNode.test_testMode) ENABLED START #
        test_mode = TestMode.NONE
        tango_context.device.testMode = test_mode
        assert tango_context.device.testMode == test_mode
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.test_testMode

    def test_visDestinationAddress(self, tango_context):
        """Test for visDestinationAddress"""
        # PROTECTED REGION ID(CspSubarrayLeafNode.test_visDestinationAddress) ENABLED START #
        tango_context.device.visDestinationAddress = "test"
        assert tango_context.device.visDestinationAddress == "test"
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.test_visDestinationAddress

    def test_activityMessage(self, tango_context):
        """Test for activityMessage"""
        # PROTECTED REGION ID(CspSubarrayLeafNode.test_activityMessage) ENABLED START #
        tango_context.device.activityMessage = 'text'
        assert tango_context.device.activityMessage == 'text'
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.test_activityMessage

    def test_loggingLevel(self, tango_context):
        """Test for loggingLevel"""
        # PROTECTED REGION ID(CspSubarrayLeafNode.test_loggingLevel) ENABLED START #
        tango_context.device.loggingLevel = LoggingLevel.INFO
        assert tango_context.device.loggingLevel == LoggingLevel.INFO
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.test_loggingLevel

    def test_loggingTargets(self, tango_context):
        """Test for loggingTargets"""
        # PROTECTED REGION ID(CspSubarrayLeafNode.test_loggingTargets) ENABLED START #
        tango_context.device.loggingTargets = ['console::cout']
        assert 'console::cout' in tango_context.device.loggingTargets
        # PROTECTED REGION END #    //  CspSubarrayLeafNode.test_loggingTargets
