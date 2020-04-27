import contextlib
import importlib
import sys
import json
import mock
import types
import tango
from tango import DevState, DeviceData, DevString, DevVarStringArray
import time
import pytest

from mock import Mock
from subarraynode import SubarrayNode, const
from subarraynode.const import PointingState
from tango.test_context import DeviceTestContext
from ska.base.control_model import AdminMode, HealthState, ObsState, ObsMode, TestMode, SimulationMode, LoggingLevel

def test_On_should_command_subarray_to_On():
    # arrange:
    device_under_test = SubarrayNode
    dut_properties = {
    }
    proxies_to_mock = {
    }

    with fake_tango_system(device_under_test, initial_dut_properties=dut_properties, proxies_to_mock=proxies_to_mock) \
            as tango_context:
        # act:
        tango_context.device.On()
        # assert:
        assert tango_context.device.state() == DevState.OFF

def test_Standby_command_subarray_to_OFF():
    # arrange:
    device_under_test = SubarrayNode
    dut_properties = {
    }
    proxies_to_mock = {
    }

    with fake_tango_system(device_under_test, initial_dut_properties=dut_properties, proxies_to_mock=proxies_to_mock) \
            as tango_context:
        # act:
        tango_context.device.Standby()
        # assert:
        assert tango_context.device.state() == DevState.DISABLE


def test_assignResource_should_command_subarray_AssignResource():
    # arrange:
    device_under_test = SubarrayNode
    csp_subarray_ln_fqdn = 'ska_mid/tm_leaf_node/csp_subarray01'
    csp_subarray_fqdn = 'mid_csp/elt/subarray_01'
    sdp_subarray_ln_fqdn = 'ska_mid/tm_leaf_node/sdp_subarray01'
    sdp_subarray_fqdn = 'mid_sdp/elt/subarray_1'
    dish_ln_prefix = 'ska_mid/tm_leaf_node/d'
    # dish_ln_fqdn = dish_ln_prefix+'0001'

    dut_properties = {
        'CspSubarrayLNFQDN': csp_subarray_ln_fqdn,
        'CspSubarrayFQDN': csp_subarray_fqdn,
        'SdpSubarrayLNFQDN': sdp_subarray_ln_fqdn,
        'SdpSubarrayFQDN': sdp_subarray_fqdn,
        'DishLeafNodePrefix' : dish_ln_prefix
    }

    csp_subarray_ln_proxy_mock = Mock()
    csp_subarray_proxy_mock = Mock()
    sdp_subarray_ln_proxy_mock = Mock()
    sdp_subarray_proxy_mock = Mock()
    dish_ln_proxy_mock = Mock()
    # csp_subarray_proxy_mock.obsState = ObsState.READY
    # sdp_subarray_proxy_mock.obsState = ObsState.READY
    # csp_subarray_proxy_mock.set_state(DevState.OFF)
    # sdp_subarray_proxy_mock.set_state(DevState.OFF)

    proxies_to_mock = {
        csp_subarray_ln_fqdn : csp_subarray_ln_proxy_mock,
        csp_subarray_fqdn : csp_subarray_proxy_mock,
        sdp_subarray_ln_fqdn : sdp_subarray_ln_proxy_mock,
        sdp_subarray_fqdn : sdp_subarray_proxy_mock,
        dish_ln_prefix+"0001": dish_ln_proxy_mock
    }


    with fake_tango_system(device_under_test, initial_dut_properties=dut_properties, proxies_to_mock=proxies_to_mock) \
            as tango_context:
        receptor_list = ['0001']
        # receptor_list1 = str(receptor_list)
        # print("type of receptor-list on subarray : ", type(receptor_list1))
        # act:
        # tango_context.device.set_state(DevState.ON)

        # cmdData = tango.DeviceData()
        # cmdData.insert(tango.DevVarStringArray, receptor_list)
        tango_context.device.On()
        tango_context.device.AssignResources(receptor_list)

        # assert:
        json_argument = {}
        dummy_sdp_resources = ["PB1", "PB2"]
        json_argument[const.STR_KEY_PB_ID_LIST] = dummy_sdp_resources
        str_json_arg = json.dumps(json_argument)
        sdp_subarray_ln_proxy_mock.command_inout.assert_called_with(const.CMD_ASSIGN_RESOURCES, str_json_arg)

        arg_list = []
        json_argument = {}
        dish = {}
        dish[const.STR_KEY_RECEPTOR_ID_LIST] = receptor_list
        json_argument[const.STR_KEY_DISH] = dish
        arg_list.append(json.dumps(json_argument))
        csp_subarray_ln_proxy_mock.command_inout.assert_called_with(const.CMD_ASSIGN_RESOURCES, arg_list)


def test_ReleaseResource_command_subarray():
    # arrange:
    device_under_test = SubarrayNode
    csp_subarray_ln_fqdn = 'ska_mid/tm_leaf_node/csp_subarray01'
    csp_subarray_fqdn = 'mid_csp/elt/subarray_01'
    sdp_subarray_ln_fqdn = 'ska_mid/tm_leaf_node/sdp_subarray01'
    sdp_subarray_fqdn = 'mid_sdp/elt/subarray_1'
    dish_ln_prefix = 'ska_mid/tm_leaf_node/d'
    # dish_ln_fqdn = dish_ln_prefix+'0001'

    dut_properties = {
        'CspSubarrayLNFQDN': csp_subarray_ln_fqdn,
        'CspSubarrayFQDN': csp_subarray_fqdn,
        'SdpSubarrayLNFQDN': sdp_subarray_ln_fqdn,
        'SdpSubarrayFQDN': sdp_subarray_fqdn,
        'DishLeafNodePrefix' : dish_ln_prefix
    }

    csp_subarray_ln_proxy_mock = Mock()
    csp_subarray_proxy_mock = Mock()
    sdp_subarray_ln_proxy_mock = Mock()
    sdp_subarray_proxy_mock = Mock()
    dish_ln_proxy_mock = Mock()
    # csp_subarray_proxy_mock.obsState = ObsState.READY
    # sdp_subarray_proxy_mock.obsState = ObsState.READY
    # csp_subarray_proxy_mock.set_state(DevState.OFF)
    # sdp_subarray_proxy_mock.set_state(DevState.OFF)

    proxies_to_mock = {
        csp_subarray_ln_fqdn : csp_subarray_ln_proxy_mock,
        csp_subarray_fqdn : csp_subarray_proxy_mock,
        sdp_subarray_ln_fqdn : sdp_subarray_ln_proxy_mock,
        sdp_subarray_fqdn : sdp_subarray_proxy_mock,
        dish_ln_prefix+"0001": dish_ln_proxy_mock
    }


    with fake_tango_system(device_under_test, initial_dut_properties=dut_properties, proxies_to_mock=proxies_to_mock) \
            as tango_context:
        tango_context.device.On()
        receptor_list = ['0001']
        tango_context.device.AssignResources(receptor_list)
        tango_context.device.ReleaseAllResources()
        # assert:
        sdp_subarray_ln_proxy_mock.command_inout.assert_called_with(const.CMD_RELEASE_ALL_RESOURCES)
        csp_subarray_ln_proxy_mock.command_inout.assert_called_with(const.CMD_RELEASE_ALL_RESOURCES)

# @pytest.mark.xfail
def test_Configure_command_subarray():
    # arrange:
    device_under_test = SubarrayNode
    csp_subarray_ln_fqdn = 'ska_mid/tm_leaf_node/csp_subarray01'
    csp_subarray_fqdn = 'mid_csp/elt/subarray_01'
    sdp_subarray_ln_fqdn = 'ska_mid/tm_leaf_node/sdp_subarray01'
    sdp_subarray_fqdn = 'mid_sdp/elt/subarray_1'
    dish_ln_prefix = 'ska_mid/tm_leaf_node/d'

    dut_properties = {
        'CspSubarrayLNFQDN': csp_subarray_ln_fqdn,
        'CspSubarrayFQDN': csp_subarray_fqdn,
        'SdpSubarrayLNFQDN': sdp_subarray_ln_fqdn,
        'SdpSubarrayFQDN': sdp_subarray_fqdn,
        'DishLeafNodePrefix' : dish_ln_prefix
    }

    csp_subarray_ln_proxy_mock = Mock()
    csp_subarray_proxy_mock = Mock()
    sdp_subarray_ln_proxy_mock = Mock()
    sdp_subarray_proxy_mock = Mock()
    dish_ln_proxy_mock = Mock()

    proxies_to_mock = {
        csp_subarray_ln_fqdn : csp_subarray_ln_proxy_mock,
        csp_subarray_fqdn : csp_subarray_proxy_mock,
        sdp_subarray_ln_fqdn : sdp_subarray_ln_proxy_mock,
        sdp_subarray_fqdn : sdp_subarray_proxy_mock,
        dish_ln_prefix + "0001" : dish_ln_proxy_mock
    }

    csp_subarray_proxy_mock.obsState = ObsState.IDLE
    sdp_subarray_proxy_mock.obsState = ObsState.IDLE

    with fake_tango_system(device_under_test, initial_dut_properties=dut_properties, proxies_to_mock=proxies_to_mock) \
            as tango_context:
        tango_context.device.On()
        receptor_list = ['0001']
        tango_context.device.AssignResources(receptor_list)

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

        # assert:
        # scan_configuration = json.loads(argin)
        # self._scan_id = str(scan_configuration["scanID"])

        expected_string_dict = {
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
            "delayModelSubscriptionPoint": "ska_mid/tm_leaf_node/csp_subarray01/delayModel",
            "visDestinationAddressSubscriptionPoint": "mid_sdp/elt/subarray_1/receiveAddresses",
            "pointing": {
                "target": {
                    "system": "ICRS",
                    "name": "Polaris",
                    "RA": "02:31:49.0946",
                    "dec": "+89:15:50.7923"
                }
            },
            "scanID": 12345
        }
        # cmd_data = tango.DeviceData()
        # cmd_data.insert(tango.DevString, json.dumps(csp_scan_config))
        csp_scan_config = json.dumps(expected_string_dict)
        print ("csp_scan_config:", csp_scan_config)
        csp_subarray_ln_proxy_mock.command_inout.assert_called_with(const.CMD_CONFIGURE, csp_scan_config)

        scan_config = '{"sdp":{"configure":{"id":"realtime-20190627-0001","sbiId":"20190627-0001",' \
                     '"workflow":{"id":"vis_ingest","type":"realtime","version":"0.1.0"},"parameters":' \
                     '{"numStations":4,"numChanels":372,"numPolarisations":4,"freqStartHz":0.35e9,' \
                     '"freqEndHz":1.05e9,"fields":{"0":{"system":"ICRS","name":"NGC6251","ra":1.0,"dec"' \
                     ':1.0}}},"scanParameters":{"12345":{"fieldId":0,"intervalMs":1400}}},"configureScan"' \
                     ':{"scanParameters":{"12346":{"fieldId":0,"intervalMs":2800}}}}}'
        # cmd_data = tango.DeviceData()
        # cmd_data.insert(tango.DevString, json.dumps(scan_config))
        sdp_subarray_ln_proxy_mock.command_inout.assert_called_with(const.CMD_CONFIGURE, json.dumps(scan_config))

        dish_configure_input = '{"pointing":{"target":{"system":"ICRS","name":"NGC6251","RA":"2:31:50.91",' \
                               '"dec":"89:15:51.4"}},"dish":{"receiverBand":"1"}}'
        cmd_data = tango.DeviceData()
        cmd_data.insert(tango.DevString, json.dumps(dish_configure_input))
        dish_ln_proxy_mock.command_inout.asser_called_with(const.CMD_CONFIGURE, cmd_data)

def create_dummy_event_obsstate_scanning(device_fqdn):
    fake_event = Mock()
    fake_event.err = False
    fake_event.attr_name = f"{device_fqdn}/ObsState"
    fake_event.attr_value.value = ObsState.SCANNING
    return fake_event

# @pytest.mark.xfail
def test_start_scan_should_command_subarray_to_start_scan_when_it_is_ready():
    # arrange:
    device_under_test = SubarrayNode
    csp_subarray_ln_fqdn = 'ska_mid/tm_leaf_node/csp_subarray01'
    csp_subarray_fqdn = 'mid_csp/elt/subarray_01'
    sdp_subarray_ln_fqdn = 'ska_mid/tm_leaf_node/sdp_subarray01'
    sdp_subarray_fqdn = 'mid_sdp/elt/subarray_1'
    dish_ln_prefix = 'ska_mid/tm_leaf_node/d'

    dut_properties = {
        'CspSubarrayLNFQDN': csp_subarray_ln_fqdn,
        'CspSubarrayFQDN': csp_subarray_fqdn,
        'SdpSubarrayLNFQDN': sdp_subarray_ln_fqdn,
        'SdpSubarrayFQDN': sdp_subarray_fqdn,
        'DishLeafNodePrefix': dish_ln_prefix
    }
    event_subscription_map = {}
    csp_subarray_ln_proxy_mock = Mock()
    csp_subarray_proxy_mock = Mock()
    sdp_subarray_ln_proxy_mock = Mock()
    sdp_subarray_proxy_mock = Mock()
    dish_ln_proxy_mock = Mock()

    proxies_to_mock = {
        csp_subarray_ln_fqdn : csp_subarray_ln_proxy_mock,
        csp_subarray_fqdn : csp_subarray_proxy_mock,
        sdp_subarray_ln_fqdn : sdp_subarray_ln_proxy_mock,
        sdp_subarray_fqdn : sdp_subarray_proxy_mock,
        dish_ln_prefix+'0001' : dish_ln_proxy_mock
    }
    csp_subarray_obsstate_attribute = "cspSubarrayObsState"
    sdp_subarray_obsstate_attribute = "sdpSubarrayObsState"
    dish_pointing_state_attribute = "dishPointingState"

    event_subscription_map = {}
    dish_pointing_state_map = {}
    csp_subarray_ln_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args, **kwargs: event_subscription_map.update({attr_name: callback}))

    sdp_subarray_ln_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args, **kwargs: event_subscription_map.update({attr_name: callback}))

    dish_ln_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args, **kwargs: dish_pointing_state_map.update({attr_name: callback}))

    with fake_tango_system(device_under_test, initial_dut_properties=dut_properties, proxies_to_mock=proxies_to_mock) \
            as tango_context:
        receptor_list = ['0001']
        tango_context.device.On()
        csp_subarray_proxy_mock.obsState = ObsState.READY
        sdp_subarray_proxy_mock.obsState = ObsState.READY

        dummy_event_csp = create_dummy_event_obsstate(csp_subarray_ln_fqdn)
        event_subscription_map[csp_subarray_obsstate_attribute](dummy_event_csp)

        dummy_event_sdp = create_dummy_event_obsstate(sdp_subarray_ln_fqdn)
        event_subscription_map[sdp_subarray_obsstate_attribute](dummy_event_sdp)

        print("event_subscription_map:", event_subscription_map)
        time.sleep(5)
        scan_config = '{"scanDuration": 10.0}'
        print ("tango_context.device.obsState:", tango_context.device.obsState)

        tango_context.device.Scan(scan_config)

        # assert:
        json_scan_duration = json.loads(scan_config)
        scan_duration = int(json_scan_duration['scanDuration'])
        print ("scan_duration", scan_duration)

        # cmdData = DeviceData()
        # cmdData.insert(DevString, scan_config)
        sdp_subarray_ln_proxy_mock.command_inout.assert_called_with(const.CMD_SCAN, scan_config)

        csp_argin = []
        csp_argin.append(scan_config)
        # cmdData = DeviceData()
        # cmdData.insert(DevVarStringArray, csp_argin)
        csp_subarray_ln_proxy_mock.command_inout.assert_called_with(const.CMD_START_SCAN, csp_argin)

def create_dummy_event_obsstate(device_fqdn):
    fake_event = Mock()
    fake_event.err = False
    fake_event.attr_name = f"{device_fqdn}/ObsState"
    fake_event.attr_value.value = ObsState.READY
    return fake_event

def create_dummy_event_pointingState(device_fqdn):
    fake_event = Mock()
    fake_event.err = False
    fake_event.attr_name = f"{device_fqdn}/dishPointingState"
    fake_event.attr_value.value = PointingState.TRACK
    return fake_event


def test_end_scan_should_command_subarray_to_end_scan_when_it_is_scanning():
    # arrange:
    device_under_test = SubarrayNode
    csp_subarray_ln_fqdn = 'ska_mid/tm_leaf_node/csp_subarray01'
    csp_subarray_fqdn = 'mid_csp/elt/subarray_01'
    sdp_subarray_ln_fqdn = 'ska_mid/tm_leaf_node/sdp_subarray01'
    sdp_subarray_fqdn = 'mid_sdp/elt/subarray_1'
    dish_ln_prefix = 'ska_mid/tm_leaf_node/d'

    dut_properties = {
        'CspSubarrayLNFQDN': csp_subarray_ln_fqdn,
        'CspSubarrayFQDN': csp_subarray_fqdn,
        'SdpSubarrayLNFQDN': sdp_subarray_ln_fqdn,
        'SdpSubarrayFQDN': sdp_subarray_fqdn,
        'DishLeafNodePrefix': dish_ln_prefix
    }
    event_subscription_map = {}
    csp_subarray_ln_proxy_mock = Mock()
    csp_subarray_proxy_mock = Mock()
    sdp_subarray_ln_proxy_mock = Mock()
    sdp_subarray_proxy_mock = Mock()
    dish_ln_proxy_mock = Mock()

    proxies_to_mock = {
        csp_subarray_ln_fqdn: csp_subarray_ln_proxy_mock,
        csp_subarray_fqdn: csp_subarray_proxy_mock,
        sdp_subarray_ln_fqdn: sdp_subarray_ln_proxy_mock,
        sdp_subarray_fqdn: sdp_subarray_proxy_mock,
        dish_ln_prefix + '0001': dish_ln_proxy_mock
    }
    csp_subarray_obsstate_attribute = "cspSubarrayObsState"
    sdp_subarray_obsstate_attribute = "sdpSubarrayObsState"
    dish_pointing_state_attribute = "dishPointingState"

    event_subscription_map = {}
    dish_pointing_state_map = {}
    csp_subarray_ln_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args, **kwargs: event_subscription_map.update({attr_name: callback}))

    sdp_subarray_ln_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args, **kwargs: event_subscription_map.update({attr_name: callback}))

    dish_ln_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args, **kwargs: dish_pointing_state_map.update({attr_name: callback}))

    with fake_tango_system(device_under_test, initial_dut_properties=dut_properties, proxies_to_mock=proxies_to_mock) \
            as tango_context:
        tango_context.device.On()
        csp_subarray_proxy_mock.obsState = ObsState.SCANNING
        sdp_subarray_proxy_mock.obsState = ObsState.SCANNING

        dummy_event_csp = create_dummy_event_obsstate_scanning(csp_subarray_ln_fqdn)
        event_subscription_map[csp_subarray_obsstate_attribute](dummy_event_csp)

        dummy_event_sdp = create_dummy_event_obsstate_scanning(sdp_subarray_ln_fqdn)
        event_subscription_map[sdp_subarray_obsstate_attribute](dummy_event_sdp)

        time.sleep(5)
        print ("tango_context.device.obsState:", tango_context.device.obsState)
        tango_context.device.EndScan()

        # assert:
        sdp_subarray_ln_proxy_mock.command_inout.assert_called_with(const.CMD_END_SCAN)
        csp_subarray_ln_proxy_mock.command_inout.assert_called_with(const.CMD_END_SCAN)

def test_end_sb_should_command_subarray_to_end_sb_when_it_is_ready():
    # arrange:
    device_under_test = SubarrayNode
    csp_subarray_ln_fqdn = 'ska_mid/tm_leaf_node/csp_subarray01'
    csp_subarray_fqdn = 'mid_csp/elt/subarray_01'
    sdp_subarray_ln_fqdn = 'ska_mid/tm_leaf_node/sdp_subarray01'
    sdp_subarray_fqdn = 'mid_sdp/elt/subarray_1'
    dish_ln_prefix = 'ska_mid/tm_leaf_node/d'

    dut_properties = {
        'CspSubarrayLNFQDN': csp_subarray_ln_fqdn,
        'CspSubarrayFQDN': csp_subarray_fqdn,
        'SdpSubarrayLNFQDN': sdp_subarray_ln_fqdn,
        'SdpSubarrayFQDN': sdp_subarray_fqdn,
        'DishLeafNodePrefix': dish_ln_prefix
    }
    csp_subarray_ln_proxy_mock = Mock()
    csp_subarray_proxy_mock = Mock()
    sdp_subarray_ln_proxy_mock = Mock()
    sdp_subarray_proxy_mock = Mock()
    dish_ln_proxy_mock = Mock()

    proxies_to_mock = {
        csp_subarray_ln_fqdn: csp_subarray_ln_proxy_mock,
        csp_subarray_fqdn: csp_subarray_proxy_mock,
        sdp_subarray_ln_fqdn: sdp_subarray_ln_proxy_mock,
        sdp_subarray_fqdn: sdp_subarray_proxy_mock,
        dish_ln_prefix + '0001': dish_ln_proxy_mock
    }

    csp_subarray_obsstate_attribute = "cspSubarrayObsState"
    sdp_subarray_obsstate_attribute = "sdpSubarrayObsState"
    dish_pointing_state_attribute = "dishPointingState"

    event_subscription_map = {}
    dish_pointing_state_map = {}

    csp_subarray_ln_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args, **kwargs: event_subscription_map.update({attr_name: callback}))

    sdp_subarray_ln_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args, **kwargs: event_subscription_map.update({attr_name: callback}))

    with fake_tango_system(device_under_test, initial_dut_properties=dut_properties, proxies_to_mock=proxies_to_mock) \
            as tango_context:
        tango_context.device.On()

        csp_subarray_proxy_mock.obsState = ObsState.READY
        sdp_subarray_proxy_mock.obsState = ObsState.READY

        dummy_event_csp = create_dummy_event_obsstate(csp_subarray_ln_fqdn)
        event_subscription_map[csp_subarray_obsstate_attribute](dummy_event_csp)

        dummy_event_sdp = create_dummy_event_obsstate(sdp_subarray_ln_fqdn)
        event_subscription_map[sdp_subarray_obsstate_attribute](dummy_event_sdp)

        print("event_subscription_map:", event_subscription_map)
        # assert tango_context.device.obsState == ObsState.READY
        time.sleep(5)

        tango_context.device.EndSB()
        # assert:
        sdp_subarray_ln_proxy_mock.command_inout.assert_called_with(const.CMD_ENDSB)
        csp_subarray_ln_proxy_mock.command_inout.assert_called_with(const.CMD_GOTOIDLE)
        dish_ln_proxy_mock.command_inout.asser_called_with(const.CMD_STOP_TRACK)

def test_obs_state_is_ready_when_other_leaf_node_is_ready_after_start():
    # arrange:
    device_under_test = SubarrayNode
    csp_subarray_ln_fqdn = 'ska_mid/tm_leaf_node/csp_subarray01'
    csp_subarray_fqdn = 'mid_csp/elt/subarray_01'
    sdp_subarray_ln_fqdn = 'ska_mid/tm_leaf_node/sdp_subarray01'
    sdp_subarray_fqdn = 'mid_sdp/elt/subarray_1'
    dish_ln_prefix = 'ska_mid/tm_leaf_node/d'

    dut_properties = {
        'CspSubarrayLNFQDN': csp_subarray_ln_fqdn,
        'CspSubarrayFQDN': csp_subarray_fqdn,
        'SdpSubarrayLNFQDN': sdp_subarray_ln_fqdn,
        'SdpSubarrayFQDN': sdp_subarray_fqdn,
        'DishLeafNodePrefix': dish_ln_prefix
    }

    csp_subarray_ln_proxy_mock = Mock()
    csp_subarray_proxy_mock = Mock()
    sdp_subarray_ln_proxy_mock = Mock()
    sdp_subarray_proxy_mock = Mock()
    dish_ln_proxy_mock = Mock()

    proxies_to_mock = {
        csp_subarray_ln_fqdn: csp_subarray_ln_proxy_mock,
        csp_subarray_fqdn: csp_subarray_proxy_mock,
        sdp_subarray_ln_fqdn: sdp_subarray_ln_proxy_mock,
        sdp_subarray_fqdn: sdp_subarray_proxy_mock,
        dish_ln_prefix + "0001": dish_ln_proxy_mock
    }
    csp_subarray_obsstate_attribute = "cspSubarrayObsState"
    sdp_subarray_obsstate_attribute = "sdpSubarrayObsState"
    dish_pointing_state_attribute = "dishPointingState"

    event_subscription_map = {}
    dish_pointing_state_map = {}

    csp_subarray_ln_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args, **kwargs: event_subscription_map.update({attr_name: callback}))

    sdp_subarray_ln_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args, **kwargs: event_subscription_map.update({attr_name: callback}))

    with fake_tango_system(device_under_test, initial_dut_properties=dut_properties, proxies_to_mock=proxies_to_mock) \
            as tango_context:
        # act:
        dummy_event_csp = create_dummy_event_obsstate(csp_subarray_ln_fqdn)
        event_subscription_map[csp_subarray_obsstate_attribute](dummy_event_csp)

        dummy_event_sdp = create_dummy_event_obsstate(sdp_subarray_ln_fqdn)
        event_subscription_map[sdp_subarray_obsstate_attribute](dummy_event_sdp)

        print ("event_subscription_map:", event_subscription_map)

        # assert:
        time.sleep(5)
        assert tango_context.device.obsState == ObsState.READY


def test_obs_state_is_scanning_when_other_leaf_node_is_scanning_after_start():
    # arrange:
    device_under_test = SubarrayNode
    csp_subarray_ln_fqdn = 'ska_mid/tm_leaf_node/csp_subarray01'
    csp_subarray_fqdn = 'mid_csp/elt/subarray_01'
    sdp_subarray_ln_fqdn = 'ska_mid/tm_leaf_node/sdp_subarray01'
    sdp_subarray_fqdn = 'mid_sdp/elt/subarray_1'
    dish_ln_prefix = 'ska_mid/tm_leaf_node/d'

    dut_properties = {
        'CspSubarrayLNFQDN': csp_subarray_ln_fqdn,
        'CspSubarrayFQDN': csp_subarray_fqdn,
        'SdpSubarrayLNFQDN': sdp_subarray_ln_fqdn,
        'SdpSubarrayFQDN': sdp_subarray_fqdn,
        'DishLeafNodePrefix': dish_ln_prefix
    }

    csp_subarray_ln_proxy_mock = Mock()
    csp_subarray_proxy_mock = Mock()
    sdp_subarray_ln_proxy_mock = Mock()
    sdp_subarray_proxy_mock = Mock()
    dish_ln_proxy_mock = Mock()

    proxies_to_mock = {
        csp_subarray_ln_fqdn: csp_subarray_ln_proxy_mock,
        csp_subarray_fqdn: csp_subarray_proxy_mock,
        sdp_subarray_ln_fqdn: sdp_subarray_ln_proxy_mock,
        sdp_subarray_fqdn: sdp_subarray_proxy_mock,
        dish_ln_prefix + "0001": dish_ln_proxy_mock
    }
    csp_subarray_obsstate_attribute = "cspSubarrayObsState"
    sdp_subarray_obsstate_attribute = "sdpSubarrayObsState"

    event_subscription_map = {}

    csp_subarray_ln_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args, **kwargs: event_subscription_map.update({attr_name: callback}))

    sdp_subarray_ln_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args, **kwargs: event_subscription_map.update({attr_name: callback}))

    with fake_tango_system(device_under_test, initial_dut_properties=dut_properties, proxies_to_mock=proxies_to_mock) \
            as tango_context:
        # act:
        dummy_event_csp = create_dummy_event_obsstate_scanning(csp_subarray_ln_fqdn)
        event_subscription_map[csp_subarray_obsstate_attribute](dummy_event_csp)

        dummy_event_sdp = create_dummy_event_obsstate_scanning(sdp_subarray_ln_fqdn)
        event_subscription_map[sdp_subarray_obsstate_attribute](dummy_event_sdp)

        print ("event_subscription_map:", event_subscription_map)
        # assert:
        time.sleep(5)
        assert tango_context.device.obsState == ObsState.SCANNING

@pytest.mark.xfail
def test_subarray_health_state_is_degraded_when_csp_subarray_ln_is_degraded_after_start():
    # arrange:
    device_under_test = SubarrayNode
    csp_subarray_ln_fqdn = 'ska_mid/tm_leaf_node/csp_subarray01'
    csp_subarray_ln_health_attribute = 'cspsubarrayHealthState'
    initial_dut_properties = {
        'CspSubarrayLNFQDN': csp_subarray_ln_fqdn
    }

    event_subscription_map = {}

    csp_subarray_ln_proxy_mock = Mock()
    csp_subarray_ln_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args, **kwargs: event_subscription_map.update({attr_name: callback}))

    proxies_to_mock = {
        csp_subarray_ln_fqdn: csp_subarray_ln_proxy_mock
    }

    with fake_tango_system(device_under_test, initial_dut_properties, proxies_to_mock) as tango_context:
        # act:
        dummy_event = create_dummy_event_healthstate(csp_subarray_ln_fqdn)
        event_subscription_map[csp_subarray_ln_health_attribute](dummy_event)

        # assert:
        assert tango_context.device.healthState == HealthState.DEGRADED

def create_dummy_event_healthstate(device_fqdn):
    fake_event = Mock()
    fake_event.err = False
    fake_event.attr_name = f"{device_fqdn}/healthState"
    fake_event.attr_value.value = HealthState.DEGRADED
    return fake_event

def test_Status():
    """Test for Status"""
    device_under_test = SubarrayNode
    with fake_tango_system(device_under_test) as tango_context:
        assert tango_context.device.Status() == const.STR_SA_INIT_SUCCESS

def test_State():
    """Test for State"""
    device_under_test = SubarrayNode
    with fake_tango_system(device_under_test) as tango_context:
        assert tango_context.device.State() == DevState.DISABLE

def test_healthState():
    """Test for healthState"""
    device_under_test = SubarrayNode
    with fake_tango_system(device_under_test) as tango_context:
        assert tango_context.device.healthState == HealthState.OK

def test_activationTime():
    """Test for activationTime"""
    device_under_test = SubarrayNode
    with fake_tango_system(device_under_test) as tango_context:
        assert tango_context.device.activationTime == 0.0

def test_adminMode():
    """Test for adminMode"""
    device_under_test = SubarrayNode
    with fake_tango_system(device_under_test) as tango_context:
        assert tango_context.device.adminMode == AdminMode.OFFLINE

def test_buildState():
    """Test for buildState"""
    device_under_test = SubarrayNode
    with fake_tango_system(device_under_test) as tango_context:
        assert tango_context.device.buildState == (
        "lmcbaseclasses, 0.5.1, A set of generic base devices for SKA Telescope.")

def test_configurationDelayExpected():
    """Test for configurationDelayExpected"""
    device_under_test = SubarrayNode
    with fake_tango_system(device_under_test) as tango_context:
        assert tango_context.device.configurationDelayExpected == 0

def test_configurationProgress():
    """Test for configurationProgress"""
    device_under_test = SubarrayNode
    with fake_tango_system(device_under_test) as tango_context:
        assert tango_context.device.configurationProgress == 0

def test_controlMode():
    """Test for controlMode"""
    device_under_test = SubarrayNode
    with fake_tango_system(device_under_test) as tango_context:
        control_mode = tango_context.device.controlMode.REMOTE
        tango_context.device.controlMode = control_mode
        assert tango_context.device.controlMode == control_mode

def test_obsMode():
    """Test for obsMode"""
    device_under_test = SubarrayNode
    with fake_tango_system(device_under_test) as tango_context:
        assert tango_context.device.obsMode == ObsMode.IDLE

def test_obsState():
    """Test for obsState"""
    device_under_test = SubarrayNode
    with fake_tango_system(device_under_test) as tango_context:
        assert tango_context.device.obsState == ObsState.IDLE

def test_simulationMode():
    """Test for simulationMode"""
    device_under_test = SubarrayNode
    with fake_tango_system(device_under_test) as tango_context:
        simulation_mode = SimulationMode.FALSE
        tango_context.device.simulationMode = simulation_mode
        assert tango_context.device.simulationMode == simulation_mode

def test_testMode():
    """Test for testMode"""
    device_under_test = SubarrayNode
    with fake_tango_system(device_under_test) as tango_context:
        test_mode = TestMode.NONE
        tango_context.device.testMode = test_mode
        assert tango_context.device.testMode == test_mode

def test_versionId():
    """Test for versionId"""
    device_under_test = SubarrayNode
    with fake_tango_system(device_under_test) as tango_context:
        assert tango_context.device.versionId == "0.5.1"

def test_scanID():
    """Test for scanID"""
    device_under_test = SubarrayNode
    with fake_tango_system(device_under_test) as tango_context:
        assert tango_context.device.scanID == ""

def test_sbID():
    """Test for sbID"""
    device_under_test = SubarrayNode
    with fake_tango_system(device_under_test) as tango_context:
        assert tango_context.device.sbID == ""

def test_activityMessage():
    """Test for activityMessage"""
    device_under_test = SubarrayNode
    with fake_tango_system(device_under_test) as tango_context:
        message = const.STR_OK
        tango_context.device.activityMessage = message
        assert tango_context.device.activityMessage == message

def test_configuredCapabilities():
    """Test for configuredCapabilities"""
    device_under_test = SubarrayNode
    with fake_tango_system(device_under_test) as tango_context:
        assert tango_context.device.configuredCapabilities is None

def test_receptorIDList():
    """Test for receptorIDList"""
    device_under_test = SubarrayNode
    with fake_tango_system(device_under_test) as tango_context:
        assert tango_context.device.receptorIDList is None

def any_method(with_name=None):
    class AnyMethod():
        def __eq__(self, other):
            if not isinstance(other, types.MethodType):
                return False

            return other.__func__.__name__ == with_name if with_name else True

    return AnyMethod()


@contextlib.contextmanager
def fake_tango_system(device_under_test, initial_dut_properties={}, proxies_to_mock={},
                      device_proxy_import_path='tango.DeviceProxy'):

    with mock.patch(device_proxy_import_path) as patched_constructor:
        patched_constructor.side_effect = lambda device_fqdn: proxies_to_mock.get(device_fqdn, Mock())
        patched_module = importlib.reload(sys.modules[device_under_test.__module__])

    device_under_test = getattr(patched_module, device_under_test.__name__)

    device_test_context = DeviceTestContext(device_under_test, properties=initial_dut_properties)
    device_test_context.start()
    yield device_test_context
    device_test_context.stop()
