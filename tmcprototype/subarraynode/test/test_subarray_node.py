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
# Imports
import json
import pytest
import time
import tango
from tango import DevState
from subarraynode import SubarrayNode, SubarrayHealthState, ElementDeviceData, const
from ska.base.control_model import AdminMode, HealthState, ObsState, ObsMode, TestMode, SimulationMode, LoggingLevel

@pytest.fixture(scope="function",
                params=[HealthState.OK, HealthState.DEGRADED,
                        HealthState.FAILED, HealthState.UNKNOWN])
def valid_health_state(request):
    return request.param


@pytest.fixture(
    scope="function",
    params=[
        ([HealthState.OK], HealthState.OK),
        ([HealthState.FAILED], HealthState.FAILED),
        ([HealthState.DEGRADED], HealthState.DEGRADED),
        ([HealthState.UNKNOWN], HealthState.UNKNOWN),
        ([HealthState.OK, HealthState.FAILED], HealthState.FAILED),
        ([HealthState.OK, HealthState.DEGRADED], HealthState.DEGRADED),
        ([HealthState.OK, HealthState.UNKNOWN], HealthState.UNKNOWN),
        ([HealthState.FAILED, HealthState.DEGRADED], HealthState.FAILED),
        ([HealthState.FAILED, HealthState.UNKNOWN], HealthState.FAILED),
        ([HealthState.DEGRADED, HealthState.UNKNOWN], HealthState.DEGRADED),
        ([HealthState.OK, HealthState.FAILED, HealthState.DEGRADED], HealthState.FAILED),
        ([HealthState.OK, HealthState.FAILED, HealthState.UNKNOWN], HealthState.FAILED),
        ([HealthState.OK, HealthState.UNKNOWN, HealthState.DEGRADED],
         HealthState.DEGRADED),
        ([HealthState.FAILED, HealthState.UNKNOWN, HealthState.DEGRADED],
         HealthState.FAILED),
        ([HealthState.OK, HealthState.FAILED, HealthState.UNKNOWN, HealthState.DEGRADED],
         HealthState.FAILED),
                ])
def health_states_and_expected_aggregate(request):
    states_in, expected_state_out = request.param
    return states_in, expected_state_out

class TestSubarrayHealthState:

    def test_generate_health_state_log_msg_valid(self, valid_health_state):
        msg = SubarrayHealthState.generate_health_state_log_msg(
            valid_health_state, "my/dev/name", None
        )
        assert msg == "healthState of my/dev/name :-> {}".format(valid_health_state.name)

    def test_generate_health_state_log_msg_invalid(self):
        msg = SubarrayHealthState.generate_health_state_log_msg(
            "not a health state enum", "my/dev/name", None
        )
        assert msg == "healthState event returned unknown value \nNone"

    def test_calculate_health_state(self, health_states_and_expected_aggregate):
        health_states, expected_health_state = health_states_and_expected_aggregate
        result = SubarrayHealthState.calculate_health_state(health_states)
        assert result == expected_health_state


@pytest.fixture(scope="function")
def example_scan_configuration():
    scan_config = {
          "pointing": {
            "target": {
              "system": "ICRS",
              "name": "Polaris",
              "RA": "02:31:49.0946",
              "dec": "+89:15:50.7923"
            }
          },
          "dish": {
            "receiverBand": "1"
          },
          "csp": {
            "id": "sbi-mvp01-20200325-00001-science_A",
            "frequencyBand": "1",
            "fsp": [
              {
                "fspID": 1,
                "functionMode": "CORR",
                "frequencySliceID": 1,
                "integrationTime": 1400,
                "corrBandwidth": 0
              }
            ]
          },
          "sdp": {
            "scan_type": "science_A"
          },
          "tmc": {
            "scanDuration": 10.0
          }
        }

    return scan_config

@pytest.fixture(scope="function")
def csp_func_args():
    scan_id = 1
    attr_name_map = {
        "string1": "attr1",
        "string2": "attr2"
    }
    return scan_id, attr_name_map

class TestElementDeviceData:

    def test_build_up_sdp_cmd_data_with_valid_scan_configuration(self, example_scan_configuration):
        valid_scan_config = example_scan_configuration
        sdp_cmd_data = ElementDeviceData.build_up_sdp_cmd_data(valid_scan_config)

        expected_string_dict = {
            "scan_type": "science_A"
          }
        expected_string_dict = json.dumps(expected_string_dict)

        assert isinstance(sdp_cmd_data, tango.DeviceData)
        assert expected_string_dict == sdp_cmd_data.extract()

    def test_build_up_sdp_cmd_data_with_invalid_scan_configuration(self, example_scan_configuration):
        invalid_scan_config = example_scan_configuration.pop("sdp")
        with pytest.raises(KeyError) as exception:
            ElementDeviceData.build_up_sdp_cmd_data(invalid_scan_config)
        expected_msg = "SDP configuration must be given. Aborting SDP configuration."
        assert exception.value.args[0] == expected_msg

    def test_build_up_sdp_cmd_data_with_modified_scan_configuration(self, example_scan_configuration):
        modified_scan_config = example_scan_configuration
        modified_scan_config["sdp"]["configure"] = {}
        with pytest.raises(KeyError) as exception:
            ElementDeviceData.build_up_sdp_cmd_data(modified_scan_config)
        expected_msg = "SDP Subarray configuration is empty. Command data not built up"
        assert exception.value.args[0] == expected_msg

    def test_build_up_csp_cmd_data_with_valid_scan_configuration(self, example_scan_configuration, csp_func_args):
        valid_scan_config = example_scan_configuration
        scan_id, attr_name_map = csp_func_args
        csp_cmd_data = ElementDeviceData.build_up_csp_cmd_data(valid_scan_config, attr_name_map)

        expected_string_dict = {
                "id": "sbi-mvp01-20200325-00001-science_A",
                "frequencyBand": "1",
                "fsp": [
                    {
                        "fspID": 1,
                        "functionMode": "CORR",
                        "frequencySliceID": 1,
                        "integrationTime": 1400,
                        "corrBandwidth": 0
                    }
                ],
                "scanID": "1"
            }
        expected_string_dict = json.dumps(expected_string_dict)

        assert isinstance(csp_cmd_data, tango.DeviceData)
        assert expected_string_dict == csp_cmd_data.extract()

    def test_build_up_csp_cmd_data_with_empty_scan_configuration(self, csp_func_args):
        empty_scan_config = {}
        scan_id, attr_name_map = csp_func_args
        with pytest.raises(KeyError) as exception:
            ElementDeviceData.build_up_csp_cmd_data(empty_scan_config, attr_name_map)
        expected_msg = "CSP configuration must be given. Aborting CSP configuration."
        assert exception.value.args[0] == expected_msg

    def test_build_up_csp_cmd_data_with_invalid_scan_configuration(self, example_scan_configuration, csp_func_args):
        invalid_scan_config = example_scan_configuration.pop("csp")
        scan_id, attr_name_map = csp_func_args
        with pytest.raises(KeyError) as exception:
            ElementDeviceData.build_up_csp_cmd_data(invalid_scan_config, attr_name_map)
        expected_msg = "CSP configuration must be given. Aborting CSP configuration."
        assert exception.value.args[0] == expected_msg

    def test_build_up_dsh_cmd_data_with_valid_scan_configuration(self, example_scan_configuration):
        valid_scan_config = example_scan_configuration
        dsh_cmd_data = ElementDeviceData.build_up_dsh_cmd_data(valid_scan_config, True)
        valid_scan_config.pop("sdp")
        valid_scan_config.pop("csp")
        expected_string_dict = json.dumps(valid_scan_config)

        assert isinstance(dsh_cmd_data, tango.DeviceData)
        assert expected_string_dict == dsh_cmd_data.extract()

    def test_build_up_dsh_cmd_data_with_invalid_scan_configuration(self, example_scan_configuration):
        invalid_scan_config = example_scan_configuration.pop("dish")
        with pytest.raises(KeyError) as exception:
            ElementDeviceData.build_up_dsh_cmd_data(invalid_scan_config, False)
        expected_msg = "Dish configuration must be given. Aborting Dish configuration."
        assert exception.value.args[0] == expected_msg


# Note:

# Since the device uses an inner thread, it is necessary to
# wait during the tests in order the let the device update itself.
# Hence, the sleep calls have to be secured enough not to produce
# any inconsistent behavior. However, the unittests need to run fast.
# Here, we use a factor 3 between the read period and the sleep calls.

# Look at devicetest examples for more advanced testing

# Device test case
@pytest.mark.usefixtures("tango_context", "create_dish_proxy", "create_dishln_proxy")

class TestSubarrayNode(object):
    """Test case for packet generation."""
    # PROTECTED REGION ID(SubarrayNode.test_additionnal_import) ENABLED START #
    # PROTECTED REGION END #    //  SubarrayNode.test_additionnal_import
    device = SubarrayNode
    properties = {'CapabilityTypes': '',
                  'GroupDefinitions': '', 'MetricList': 'healthState', 'SkaLevel': '4',
                  'LoggingLevelDefault': '4', 'LoggingTargetsDefault': 'console::cout',
                  'SubID': '',
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
        assert tango_context.device.Status() == const.STR_SA_INIT_SUCCESS
        # PROTECTED REGION END #    //  SubarrayNode.test_Status

    def test_State(self, tango_context):
        """Test for State"""
        # PROTECTED REGION ID(SubarrayNode.test_State) ENABLED START #
        assert tango_context.device.State() == DevState.DISABLE
        # PROTECTED REGION END #    //  SubarrayNode.test_State

    def test_healthState(self, tango_context):
        """Test for healthState"""
        # PROTECTED REGION ID(SubarrayNode.test_healthState) ENABLED START #
        assert tango_context.device.healthState == HealthState.OK
        # PROTECTED REGION END #    //  SubarrayNode.test_healthState

    def test_AssignResourcesfailure_before_startup(self, tango_context):
        """Test for AssignResources"""
        #PROTECTED REGION ID(SubarrayNode.test_AssignResources) ENABLED START #
        receptor_list = {"dish":{"receptorIDList":["0001","0002"]},"sdp":
            {"id":"sbi-mvp01-20200325-00001","max_length":100.0,"scan_types":[{"id":"science_A",
            "coordinate_system":"ICRS","ra":"02:42:40.771","dec":"-00:00:47.84","subbands":[
            {"freq_min":0.35e9,"freq_max":1.05e9,"nchan":372,"input_link_map":[[1,0],[101,1]]}]},
            {"id":"calibration_B","coordinate_system":"ICRS","ra":"12:29:06.699","dec":"02:03:08.598",
            "subbands":[{"freq_min":0.35e9,"freq_max":1.05e9,"nchan":372,"input_link_map":[[1,0],[101,1]]}]}],
            "processing_blocks":[{"id":"pb-mvp01-20200325-00001","workflow":{"type":"realtime","id":"vis_receive",
            "version":"0.1.0"},"parameters":{}},{"id":"pb-mvp01-20200325-00002","workflow":{"type":"realtime","id":
            "test_realtime","version":"0.1.0"},"parameters":{}},{"id":"pb-mvp01-20200325-00003","workflow":{"type":
            "batch","id":"ical","version":"0.1.0"},"parameters":{},"dependencies":[{"pb_id":"pb-mvp01-20200325-00001",
            "type":["visibilities"]}]},{"id":"pb-mvp01-20200325-00004","workflow":{"type":"batch","id":"dpreb",
            "version":"0.1.0"},"parameters":{},"dependencies":[{"pb_id":"pb-mvp01-20200325-00003",
            "type":["calibration"]}]}]}}
        with pytest.raises(tango.DevFailed):
            tango_context.device.AssignResources(receptor_list)
        time.sleep(10)
        assert tango_context.device.State() == DevState.DISABLE
        assert tango_context.device.receptorIDList == None
        # PROTECTED REGION END #    //  SubarrayNode.test_AssignResources

    def test_On(self, tango_context):
        """Test for StartUpTelescope on subarray."""
        # PROTECTED REGION ID(SubarrayNode.test_On) ENABLED START #
        tango_context.device.On()
        assert tango_context.device.adminMode == AdminMode.ONLINE
        assert tango_context.device.State() == DevState.OFF
        # PROTECTED REGION END #    //  SubarrayNode.test_On

    def test_AssignResources(self, tango_context):
        """Test for AssignResources"""
        # PROTECTED REGION ID(SubarrayNode.test_AssignResources) ENABLED START #
        receptor_list = {"dish":{"receptorIDList":["0001","0002"]},"sdp":
            {"id":"sbi-mvp01-20200325-00001","max_length":100.0,"scan_types":[{"id":"science_A",
            "coordinate_system":"ICRS","ra":"02:42:40.771","dec":"-00:00:47.84","subbands":[
            {"freq_min":0.35e9,"freq_max":1.05e9,"nchan":372,"input_link_map":[[1,0],[101,1]]}]},
            {"id":"calibration_B","coordinate_system":"ICRS","ra":"12:29:06.699","dec":"02:03:08.598",
            "subbands":[{"freq_min":0.35e9,"freq_max":1.05e9,"nchan":372,"input_link_map":[[1,0],[101,1]]}]}],
            "processing_blocks":[{"id":"pb-mvp01-20200325-00001","workflow":{"type":"realtime","id":"vis_receive",
            "version":"0.1.0"},"parameters":{}},{"id":"pb-mvp01-20200325-00002","workflow":{"type":"realtime","id":
            "test_realtime","version":"0.1.0"},"parameters":{}},{"id":"pb-mvp01-20200325-00003","workflow":{"type":
            "batch","id":"ical","version":"0.1.0"},"parameters":{},"dependencies":[{"pb_id":"pb-mvp01-20200325-00001",
            "type":["visibilities"]}]},{"id":"pb-mvp01-20200325-00004","workflow":{"type":"batch","id":"dpreb",
            "version":"0.1.0"},"parameters":{},"dependencies":[{"pb_id":"pb-mvp01-20200325-00003",
            "type":["calibration"]}]}]}}
        tango_context.device.AssignResources(receptor_list)
        time.sleep(10)
        assert tango_context.device.State() == DevState.ON
        #assert len(tango_context.device.receptorIDList) == 1
        assert tango_context.device.obsState == ObsState.IDLE
        # PROTECTED REGION END #    //  SubarrayNode.test_AssignResources

    def test_AssignResources_ValueError(self, tango_context):
        """Negative Test for AssignResources_ValueError"""
        # PROTECTED REGION ID(SubarrayNode.test_AssignResources) ENABLED START #
        test_input = '{"invalid_key"}'
        with pytest.raises(tango.DevFailed):
            tango_context.device.AssignResources(test_input)
        time.sleep(10)
        assert tango_context.device.obsState == ObsState.IDLE
        # PROTECTED REGION END #    //  SubarrayNode.test_AssignResources_ValueError

    def test_Configure_Negative_ScanID(self, tango_context, create_dish_proxy):
        """Negative Test for Configure"""
        # PROTECTED REGION ID(SubarrayNode.test_Configure) ENABLED START #
        with pytest.raises(tango.DevFailed):
            tango_context.device.Configure('{"A":12345,"pointing":{"target":{"system":"ICRS","name":"NGC1068","RA":0.70984,'
                                           '"dec":0.000233},},"dish":{"receiverBand":"1"},'
                                           '"csp":{"id":"sbi-mvp01-20200325-00001-science_A","frequencyBand":"1",'
                                           '"fsp":[{"fspID":1,"functionMode":"CORR","frequencySliceID":1,'
                                           '"integrationTime":1400,"corrBandwidth":0,'
                                           '"channelAveragingMap":[[1,2],[745,0]],"outputLinkMap":[[1,0],[201,1]]},'
                                           '{"fspID":2,"functionMode":"CORR","frequencySliceID":2,'
                                           '"integrationTime":1400,"corrBandwidth":0},]},'
                                           '"sdp":{"scan_type":"science_A"},"tmc":{"scanDuration":10.0,}}')
            # tango_context.device.Configure('{"A":12345,"pointing":{"target":{"system":"ICRS","name":'
            #                                '"Polaris","RA":"02:31:49.0946","dec":"+89:15:50.7923"}},"dish":'
            #                                '{"receiverBand":"1"},"csp":{"frequencyBand":"1","fsp":[{"fspID":1,'
            #                                '"functionMode":"CORR","frequencySliceID":1,"integrationTime":1400,'
            #                                '"corrBandwidth":0}]},"sdp":{"configure":'
            #                                '[{"id":"realtime-20190627-0001","sbiId":"20190627-0001","workflow":'
            #                                '{"id":"vis_ingest","type":"realtime","version":"0.1.0"},"parameters":'
            #                                '{"numStations":4,"numChannels":372,"numPolarisations":4,'
            #                                '"freqStartHz":0.35e9,"freqEndHz":1.05e9,"fields":{"0":'
            #                                '{"system":"ICRS","name":"Polaris","ra":0.662432049839445,'
            #                                '"dec":1.5579526053855042}}},"scanParameters":{"12345":'
            #                                '{"fieldId":0,"intervalMs":1400}}}]}}')
        time.sleep(5)
        assert tango_context.device.obsState == ObsState.IDLE
        # PROTECTED REGION END #    //  SubarrayNode.test_Configure

    def test_Configure_Negative_InvalidJson(self, tango_context):
        test_input = '{"invalid_key"}'
        with pytest.raises(tango.DevFailed):
            tango_context.device.Configure(test_input)
        time.sleep(3)
        assert const.ERR_INVALID_JSON in tango_context.device.activityMessage

    def test_Configure(self, tango_context, create_dish_proxy):
        """Test for Configure"""
        # PROTECTED REGION ID(SubarrayNode.test_Configure) ENABLED START #
        tango_context.device.Configure('{"scanID":12345,"pointing":{"target":{"system":"ICRS","name":"NGC1068","RA":0.70984,'
                                       '"dec":0.000233},},"dish":{"receiverBand":"1"},'
                                       '"csp":{"id":"sbi-mvp01-20200325-00001-science_A","frequencyBand":"1",'
                                       '"fsp":[{"fspID":1,"functionMode":"CORR","frequencySliceID":1,'
                                       '"integrationTime":1400,"corrBandwidth":0,'
                                       '"channelAveragingMap":[[1,2],[745,0]],"outputLinkMap":[[1,0],[201,1]]},'
                                       '{"fspID":2,"functionMode":"CORR","frequencySliceID":2,'
                                       '"integrationTime":1400,"corrBandwidth":0},]},'
                                       '"sdp":{"scan_type":"science_A"},"tmc":{"scanDuration":10.0,}}')
        # tango_context.device.Configure('{"scanID":12345,"pointing":{"target":{"system":"ICRS","name":'
        #                                '"Polaris","RA":"02:31:49.0946","dec":"+89:15:50.7923"}},"dish":'
        #                                '{"receiverBand":"1"},"csp":{"frequencyBand":"1","fsp":[{"fspID":1,'
        #                                '"functionMode":"CORR","frequencySliceID":1,"integrationTime":1400,'
        #                                '"corrBandwidth":0}]},"sdp":{"configure":'
        #                                '[{"id":"realtime-20190627-0001","sbiId":"20190627-0001","workflow":'
        #                                '{"id":"vis_ingest","type":"realtime","version":"0.1.0"},"parameters":'
        #                                '{"numStations":4,"numChannels":372,"numPolarisations":4,'
        #                                '"freqStartHz":0.35e9,"freqEndHz":1.05e9,"fields":{"0":'
        #                                '{"system":"ICRS","name":"Polaris","ra":0.662432049839445,'
        #                                '"dec":1.5579526053855042}}},"scanParameters":{"12345":'
        #                                '{"fieldId":0,"intervalMs":1400}}}]}}')
        time.sleep(65)
        assert tango_context.device.obsState == ObsState.READY
        create_dish_proxy.StopTrack()
        # PROTECTED REGION END #    //  SubarrayNode.test_Configure

    def test_Configure_ObsState_NOT_Idle(self, tango_context, create_dish_proxy):
        """Negative Test for Configure"""
        # PROTECTED REGION ID(SubarrayNode.test_Configure) ENABLED START #
        tango_context.device.Scan('{"scanDuration": 5.0}')
        time.sleep(5)
        tango_context.device.Configure('{"scanID":12345,"pointing":{"target":{"system":"ICRS","name":"NGC1068","RA":0.70984,'
                                       '"dec":0.000233},},"dish":{"receiverBand":"1"},'
                                       '"csp":{"id":"sbi-mvp01-20200325-00001-science_A","frequencyBand":"1",'
                                       '"fsp":[{"fspID":1,"functionMode":"CORR","frequencySliceID":1,'
                                       '"integrationTime":1400,"corrBandwidth":0,'
                                       '"channelAveragingMap":[[1,2],[745,0]],"outputLinkMap":[[1,0],[201,1]]},'
                                       '{"fspID":2,"functionMode":"CORR","frequencySliceID":2,'
                                       '"integrationTime":1400,"corrBandwidth":0},]},'
                                       '"sdp":{"scan_type":"science_A"},"tmc":{"scanDuration":10.0,}}')
        # tango_context.device.Configure('{"scanID":12345,"pointing":{"target":{"system":"ICRS","name":'
        #                                    '"Polaris","RA":"02:31:49.0946","dec":"+89:15:50.7923"}},"dish":'
        #                                    '{"receiverBand":"1"},"csp":{"frequencyBand":"1","fsp":[{"fspID":1,'
        #                                    '"functionMode":"CORR","frequencySliceID":1,"integrationTime":1400,'
        #                                    '"corrBandwidth":0}]},"sdp":{"configure":'
        #                                    '[{"id":"realtime-20190627-0001","sbiId":"20190627-0001","workflow":'
        #                                    '{"id":"vis_ingest","type":"realtime","version":"0.1.0"},"parameters":'
        #                                    '{"numStations":4,"numChannels":372,"numPolarisations":4,'
        #                                    '"freqStartHz":0.35e9,"freqEndHz":1.05e9,"fields":{"0":'
        #                                    '{"system":"ICRS","name":"Polaris","ra":0.662432049839445,'
        #                                    '"dec":1.5579526053855042}}},"scanParameters":{"12345":'
        #                                    '{"fieldId":0,"intervalMs":1400}}}]}}')
        time.sleep(10)
        assert tango_context.device.obsState == ObsState.READY
        # create_dish_proxy.StopTrack()
        # PROTECTED REGION END #    //  SubarrayNode.test_Configure


    def test_Scan(self, tango_context):
        """Test for Scan"""
        # PROTECTED REGION ID(SubarrayNode.test_Scan) ENABLED START #
        tango_context.device.Scan('{"id": 1}')
        time.sleep(5)
        assert tango_context.device.obsState == ObsState.SCANNING
        # PROTECTED REGION END #    //  SubarrayNode.test_Scan

    def test_Scan_Duplicate(self, tango_context):
        """Negative Test for Scan"""
        # PROTECTED REGION ID(SubarrayNode.test_Scan) ENABLED START #
        with pytest.raises(tango.DevFailed):
            tango_context.device.Scan('{"id": 1}')
        time.sleep(2)
        assert tango_context.device.obsState == ObsState.SCANNING
        # PROTECTED REGION END #    //  SubarrayNode.test_Scan

    def test_EndScan(self, tango_context):
        """Negative Test for EndScan"""
        # PROTECTED REGION ID(SubarrayNode.test_EndScan) ENABLED START #
        tango_context.device.EndScan()
        time.sleep(10)
        assert tango_context.device.obsState == ObsState.READY
        # PROTECTED REGION END #    //  SubarrayNode.test_EndScan

    def test_EndScan_Duplicate(self, tango_context):
        """Negative Test for EndScan"""
        # PROTECTED REGION ID(SubarrayNode.test_EndScan) ENABLED START #
        with pytest.raises(tango.DevFailed):
            tango_context.device.EndScan()
        time.sleep(3)
        assert tango_context.device.obsState == ObsState.READY
        # PROTECTED REGION END #    //  SubarrayNode.test_EndScan

    def test_Scan_Negative_InvalidDataType(self, tango_context):
        """Test for InvalidScan"""
        # PROTECTED REGION ID(SubarrayNode.test_Scan) ENABLED START #
        test_input = '{"id": "abc"}'
        with pytest.raises(tango.DevFailed):
            tango_context.device.Scan(test_input)
        time.sleep(5)
        assert tango_context.device.obsState == ObsState.READY
        # PROTECTED REGION END #    //  SubarrayNode.test_Scan_Negative_InvalidDataType

    def test_Scan_Negative_Keynotfound_ScanPara(self, tango_context):
        """Test for InvalidScan"""
        # PROTECTED REGION ID(SubarrayNode.test_Scan) ENABLED START #
        test_input = '{"wrong_id": 1}'
        tango_context.device.Scan(test_input)
        time.sleep(5)
        assert const.ERR_SCAN_CMD in tango_context.device.activityMessage
        # PROTECTED REGION END #    //  SubarrayNode.test_Scan_Negative_InvalidDataType

    def test_EndSB(self, tango_context):
        """Test for EndSB command."""
        # PROTECTED REGION ID(SubarrayNode.test_EndSB) ENABLED START #
        tango_context.device.EndSB()
        time.sleep(5)
        assert tango_context.device.ObsState == ObsState.IDLE
        # PROTECTED REGION END #    //  SubarrayNode.test_EndSB

    def test_EndSB_device_not_ready(self, tango_context):
        """Test for EndSB when SubarrayNode is not in Ready state command."""
        # PROTECTED REGION ID(SubarrayNode.test_EndSB) ENABLED START #
        tango_context.device.EndSB()
        time.sleep(2)
        assert tango_context.device.ObsState != ObsState.READY
        # PROTECTED REGION END #    //  SubarrayNode.test_EndSB

    def test_ReleaseAllResources(self, tango_context):
        """Test for ReleaseAllResources"""
        # PROTECTED REGION ID(SubarrayNode.test_ReleaseAllResources) ENABLED START #
        tango_context.device.ReleaseAllResources()
        assert tango_context.device.assignedResources is None
        assert tango_context.device.obsState == ObsState.IDLE
        assert tango_context.device.State() == DevState.OFF
        with pytest.raises(tango.DevFailed):
            tango_context.device.ReleaseAllResources()
        assert const.RESRC_ALREADY_RELEASED in tango_context.device.activityMessage
        # PROTECTED REGION END #    //  SubarrayNode.test_ReleaseAllResources

    def test_ReleaseResources(self, tango_context):
        """Test for ReleaseResources"""
        # PROTECTED REGION ID(SubarrayNode.test_ReleaseResources) ENABLED START #
        # PROTECTED REGION END #    //  SubarrayNode.test_ReleaseResources

    def Standby(self, tango_context):
        """Test for StandbyTelescope on subarray."""
        # PROTECTED REGION ID(SubarrayNode.Standby) ENABLED START #
        tango_context.device.Standby()
        assert tango_context.device.adminMode == AdminMode.OFFLINE
        assert tango_context.device.State() == DevState.DISABLE
        # PROTECTED REGION END #    //  SubarrayNode.Standby

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
        assert tango_context.device.adminMode == AdminMode.ONLINE
        # PROTECTED REGION END #    //  SubarrayNode.test_adminMode

    def test_buildState(self, tango_context):
        """Test for buildState"""
        # PROTECTED REGION ID(SubarrayNode.test_buildState) ENABLED START #
        assert tango_context.device.buildState == (
            "lmcbaseclasses, 0.5.1, A set of generic base devices for SKA Telescope.")
        # PROTECTED REGION END #    //  SubarrayNode.test_buildState

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
        control_mode = tango_context.device.controlMode.REMOTE
        tango_context.device.controlMode = control_mode
        assert tango_context.device.controlMode == control_mode
        # PROTECTED REGION END #    //  SubarrayNode.test_controlMode

    def test_obsMode(self, tango_context):
        """Test for obsMode"""
        # PROTECTED REGION ID(SubarrayNode.test_obsMode) ENABLED START #
        assert tango_context.device.obsMode == ObsMode.IDLE
        # PROTECTED REGION END #    //  SubarrayNode.test_obsMode

    def test_obsState(self, tango_context):
        """Test for obsState"""
        # PROTECTED REGION ID(SubarrayNode.test_obsState) ENABLED START #
        assert tango_context.device.obsState == ObsState.IDLE
        # PROTECTED REGION END #    //  SubarrayNode.test_obsState

    def test_simulationMode(self, tango_context):
        """Test for simulationMode"""
        # PROTECTED REGION ID(SubarrayNode.test_simulationMode) ENABLED START #
        simulation_mode = SimulationMode.FALSE
        tango_context.device.simulationMode = simulation_mode
        assert tango_context.device.simulationMode == simulation_mode
        # PROTECTED REGION END #    //  SubarrayNode.test_simulationMode

    def test_testMode(self, tango_context):
        """Test for testMode"""
        # PROTECTED REGION ID(SubarrayNode.test_testMode) ENABLED START #
        test_mode = TestMode.NONE
        tango_context.device.testMode = test_mode
        assert tango_context.device.testMode == test_mode
        # PROTECTED REGION END #    //  SubarrayNode.test_testMode

    def test_versionId(self, tango_context):
        """Test for versionId"""
        # PROTECTED REGION ID(SubarrayNode.test_versionId) ENABLED START #
        assert tango_context.device.versionId == "0.5.1"
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
        message = const.STR_OK
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

    def test_Track(self, tango_context, create_dishln_proxy):
        """Test for Track"""
        # PROTECTED REGION ID(SubarrayNode.test_Track) ENABLED START #
        track_argin = "radec|2:31:50.91|89:15:51.4"
        tango_context.device.Track(track_argin)
        assert const.STR_TRACK_IP_ARG in tango_context.device.activityMessage
        create_dishln_proxy.StopTrack()
        # PROTECTED REGION END #    //  SubarrayNode.test_Track

    def test_loggingLevel(self, tango_context):
        """Test for loggingLevel"""
        # PROTECTED REGION ID(SubarrayNode.test_loggingLevel) ENABLED START #
        tango_context.device.loggingLevel = LoggingLevel.INFO
        assert tango_context.device.loggingLevel == LoggingLevel.INFO
        # PROTECTED REGION END #    //  SubarrayNode.test_loggingLevel

    def test_loggingTargets(self, tango_context):
        """Test for loggingTargets"""
        # PROTECTED REGION ID(DishMaster.test_loggingLevel) ENABLED START #
        tango_context.device.loggingTargets = ['console::cout']
        assert 'console::cout' in tango_context.device.loggingTargets
        # PROTECTED REGION END #    //  DishMaster.test_loggingTargets
