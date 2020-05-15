# Standard Python imports
import contextlib
import importlib
import sys
import json
import types
import time
import pytest
import mock
from mock import Mock

# Tango imports
import tango
from tango import DevState, DeviceData, DevString, DevVarStringArray
from tango.test_context import DeviceTestContext

# Additional import
from subarraynode import SubarrayNode, const
from subarraynode.const import PointingState
from ska.base.control_model import AdminMode, HealthState, ObsState, ObsMode, TestMode, SimulationMode, \
    LoggingLevel

def test_on_command_should_change_subarray_device_state_from_disable_to_off():
    with fake_tango_system(SubarrayNode) as tango_context:
        # act:
        tango_context.device.On()
        # assert:
        assert tango_context.device.state() == DevState.OFF


def test_standby_command_should_change_subarray_device_state_to_disable():
    with fake_tango_system(SubarrayNode) as tango_context:
        # act:
        tango_context.device.Standby()
        # assert:
        assert tango_context.device.state() == DevState.DISABLE


def test_assign_resource_should_command_dish_csp_sdp_subarray1_to_assign_valid_resources():
    csp_subarray1_ln_fqdn = 'ska_mid/tm_leaf_node/csp_subarray01'
    csp_subarray1_fqdn = 'mid_csp/elt/subarray_01'
    sdp_subarray1_ln_fqdn = 'ska_mid/tm_leaf_node/sdp_subarray01'
    sdp_subarray1_fqdn = 'mid_sdp/elt/subarray_1'
    dish_ln_prefix = 'ska_mid/tm_leaf_node/d'

    dut_properties = {
        'CspSubarrayLNFQDN': csp_subarray1_ln_fqdn,
        'CspSubarrayFQDN': csp_subarray1_fqdn,
        'SdpSubarrayLNFQDN': sdp_subarray1_ln_fqdn,
        'SdpSubarrayFQDN': sdp_subarray1_fqdn,
        'DishLeafNodePrefix' : dish_ln_prefix
    }

    csp_subarray1_ln_proxy_mock = Mock()
    csp_subarray1_proxy_mock = Mock()
    sdp_subarray1_ln_proxy_mock = Mock()
    sdp_subarray1_proxy_mock = Mock()
    dish_ln_proxy_mock = Mock()

    proxies_to_mock = {
        csp_subarray1_ln_fqdn : csp_subarray1_ln_proxy_mock,
        csp_subarray1_fqdn : csp_subarray1_proxy_mock,
        sdp_subarray1_ln_fqdn : sdp_subarray1_ln_proxy_mock,
        sdp_subarray1_fqdn : sdp_subarray1_proxy_mock,
        dish_ln_prefix + "0001": dish_ln_proxy_mock
    }

    with fake_tango_system(SubarrayNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        assign_input = {"dish":{"receptorIDList":["0001","0002"]},"sdp":{"id":"sbi-mvp01-20200325-00001"
                        ,"max_length":100.0,"scan_types":[{"id":"science_A","coordinate_system":"ICRS",
                        "ra":"21:08:47.92","dec":"-88:5.7:22.9","subbands":[{"freq_min":0.35e9,"freq_max"
                        :1.05e9,"nchan":372,"input_link_map":[[1,0],[101,1]]}]},{"id":"calibration_B",
                        "coordinate_system":"ICRS","ra":"21:08:47.92","dec":"-88:5.7:22.9","subbands":
                        [{"freq_min":0.35e9,"freq_max":1.05e9,"nchan":372,"input_link_map":[[1,0],[101,1]]}]}],
                        "processing_blocks":[{"id":"pb-mvp01-20200325-00001","workflow":{"type":"realtime",
                        "id":"vis_receive","version":"0.1.0"},"parameters":{}},{"id":"pb-mvp01-20200325-00002"
                        ,"workflow":{"type":"realtime","id":"test_realtime","version":"0.1.0"},"parameters":{}},
                        {"id":"pb-mvp01-20200325-00003","workflow":{"type":"batch","id":"ical","version":"0.1.0"}
                        ,"parameters":{},"dependencies":[{"pb_id":"pb-mvp01-20200325-00001","type":["visibilities"
                        ]}]},{"id":"pb-mvp01-20200325-00004","workflow":{"type":"batch","id":"dpreb","version":
                        "0.1.0"},"parameters":{},"dependencies":[{"pb_id":"pb-mvp01-20200325-00003","type":
                        ["calibration"]}]}]}}
        tango_context.device.On()
        tango_context.device.AssignResources(json.dumps(assign_input))

        str_json_arg = json.dumps(assign_input.get("sdp"))
        sdp_subarray1_ln_proxy_mock.command_inout.assert_called_with(const.CMD_ASSIGN_RESOURCES, str_json_arg)

        arg_list = []
        json_argument = {}
        dish = {}
        receptor_list = assign_input["dish"]["receptorIDList"]
        dish[const.STR_KEY_RECEPTOR_ID_LIST] = receptor_list
        json_argument[const.STR_KEY_DISH] = dish
        arg_list.append(json.dumps(json_argument))
        csp_subarray1_ln_proxy_mock.command_inout.assert_called_with(const.CMD_ASSIGN_RESOURCES, arg_list)


def test_assign_resource_should_raise_exception_when_called_when_device_state_disable():
    # act
    with fake_tango_system(SubarrayNode) as tango_context:
        assign_input = {"dish":{"receptorIDList":["0001","0002"]},"sdp":{"id":"sbi-mvp01-20200325-00001"
                        ,"max_length":100.0,"scan_types":[{"id":"science_A","coordinate_system":"ICRS",
                        "ra":"21:08:47.92","dec":"-88:5.7:22.9","subbands":[{"freq_min":0.35e9,"freq_max"
                        :1.05e9,"nchan":372,"input_link_map":[[1,0],[101,1]]}]},{"id":"calibration_B",
                        "coordinate_system":"ICRS","ra":"21:08:47.92","dec":"-88:5.7:22.9","subbands":
                        [{"freq_min":0.35e9,"freq_max":1.05e9,"nchan":372,"input_link_map":[[1,0],[101,1]]}]}],
                        "processing_blocks":[{"id":"pb-mvp01-20200325-00001","workflow":{"type":"realtime",
                        "id":"vis_receive","version":"0.1.0"},"parameters":{}},{"id":"pb-mvp01-20200325-00002"
                        ,"workflow":{"type":"realtime","id":"test_realtime","version":"0.1.0"},"parameters":{}},
                        {"id":"pb-mvp01-20200325-00003","workflow":{"type":"batch","id":"ical","version":"0.1.0"}
                        ,"parameters":{},"dependencies":[{"pb_id":"pb-mvp01-20200325-00001","type":["visibilities"
                        ]}]},{"id":"pb-mvp01-20200325-00004","workflow":{"type":"batch","id":"dpreb","version":
                        "0.1.0"},"parameters":{},"dependencies":[{"pb_id":"pb-mvp01-20200325-00003","type":
                        ["calibration"]}]}]}}
        with pytest.raises(tango.DevFailed):
            tango_context.device.AssignResources(json.dumps(assign_input))

        # assert:
        assert tango_context.device.State() == DevState.DISABLE


def test_assign_resource_should_raise_exception_when_called_with_invalid_input():
    # act
    with fake_tango_system(SubarrayNode) as tango_context:
        tango_context.device.On()
        assign_input = '{"invalid_key": invalid_value}'
        with pytest.raises(tango.DevFailed):
            tango_context.device.AssignResources(assign_input)

        # assert:
        assert tango_context.device.State() == DevState.OFF


def test_release_resource_command_subarray():
    csp_subarray1_ln_fqdn = 'ska_mid/tm_leaf_node/csp_subarray01'
    csp_subarray1_fqdn = 'mid_csp/elt/subarray_01'
    sdp_subarray1_ln_fqdn = 'ska_mid/tm_leaf_node/sdp_subarray01'
    sdp_subarray1_fqdn = 'mid_sdp/elt/subarray_1'
    dish_ln_prefix = 'ska_mid/tm_leaf_node/d'

    dut_properties = {
        'CspSubarrayLNFQDN': csp_subarray1_ln_fqdn,
        'CspSubarrayFQDN': csp_subarray1_fqdn,
        'SdpSubarrayLNFQDN': sdp_subarray1_ln_fqdn,
        'SdpSubarrayFQDN': sdp_subarray1_fqdn,
        'DishLeafNodePrefix' : dish_ln_prefix
    }

    csp_subarray1_ln_proxy_mock = Mock()
    csp_subarray1_proxy_mock = Mock()
    sdp_subarray1_ln_proxy_mock = Mock()
    sdp_subarray1_proxy_mock = Mock()
    dish_ln_proxy_mock = Mock()

    proxies_to_mock = {
        csp_subarray1_ln_fqdn : csp_subarray1_ln_proxy_mock,
        csp_subarray1_fqdn : csp_subarray1_proxy_mock,
        sdp_subarray1_ln_fqdn : sdp_subarray1_ln_proxy_mock,
        sdp_subarray1_fqdn : sdp_subarray1_proxy_mock,
        dish_ln_prefix + "0001": dish_ln_proxy_mock
    }

    with fake_tango_system(SubarrayNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        tango_context.device.On()
        assign_input = '{"dish":{"receptorIDList":["0001","0002"]},"sdp":{"id":"sbi-mvp01-20200325-00001"' \
                        ',"max_length":100.0,"scan_types":[{"id":"science_A","coordinate_system":"ICRS",' \
                        '"ra":"21:08:47.92","dec":"-88:5.7:22.9","subbands":[{"freq_min":0.35e9,"freq_max"' \
                        ':1.05e9,"nchan":372,"input_link_map":[[1,0],[101,1]]}]},{"id":"calibration_B",' \
                        '"coordinate_system":"ICRS","ra":"21:08:47.92","dec":"-88:5.7:22.9","subbands":' \
                        '[{"freq_min":0.35e9,"freq_max":1.05e9,"nchan":372,"input_link_map":[[1,0],[101,1]]}]}],' \
                        '"processing_blocks":[{"id":"pb-mvp01-20200325-00001","workflow":{"type":"realtime",' \
                        '"id":"vis_receive","version":"0.1.0"},"parameters":{}},{"id":"pb-mvp01-20200325-00002"' \
                        ',"workflow":{"type":"realtime","id":"test_realtime","version":"0.1.0"},"parameters":{}},' \
                        '{"id":"pb-mvp01-20200325-00003","workflow":{"type":"batch","id":"ical","version":"0.1.0"}' \
                        ',"parameters":{},"dependencies":[{"pb_id":"pb-mvp01-20200325-00001","type":["visibilities"' \
                        ']}]},{"id":"pb-mvp01-20200325-00004","workflow":{"type":"batch","id":"dpreb","version":' \
                        '"0.1.0"},"parameters":{},"dependencies":[{"pb_id":"pb-mvp01-20200325-00003","type":' \
                        '["calibration"]}]}]}}'
        tango_context.device.AssignResources(assign_input)
        tango_context.device.ReleaseAllResources()
        # assert:
        sdp_subarray1_ln_proxy_mock.command_inout.assert_called_with(const.CMD_RELEASE_ALL_RESOURCES)
        csp_subarray1_ln_proxy_mock.command_inout.assert_called_with(const.CMD_RELEASE_ALL_RESOURCES)


def test_release_resource_should_raise_exception_when_called_before_assign_resource():
    # act
    with fake_tango_system(SubarrayNode) as tango_context:
        tango_context.device.On()
        with pytest.raises(tango.DevFailed):
            tango_context.device.ReleaseAllResources()

        # assert:
        assert tango_context.device.State() == DevState.OFF
        assert const.RESOURCE_ALREADY_RELEASED in tango_context.device.activityMessage


def test_configure_command_subarray():
    csp_subarray1_ln_fqdn = 'ska_mid/tm_leaf_node/csp_subarray01'
    csp_subarray1_fqdn = 'mid_csp/elt/subarray_01'
    sdp_subarray1_ln_fqdn = 'ska_mid/tm_leaf_node/sdp_subarray01'
    sdp_subarray1_fqdn = 'mid_sdp/elt/subarray_1'
    dish_ln_prefix = 'ska_mid/tm_leaf_node/d'

    dut_properties = {
        'CspSubarrayLNFQDN': csp_subarray1_ln_fqdn,
        'CspSubarrayFQDN': csp_subarray1_fqdn,
        'SdpSubarrayLNFQDN': sdp_subarray1_ln_fqdn,
        'SdpSubarrayFQDN': sdp_subarray1_fqdn,
        'DishLeafNodePrefix' : dish_ln_prefix
    }

    csp_subarray1_ln_proxy_mock = Mock()
    csp_subarray1_proxy_mock = Mock()
    sdp_subarray1_ln_proxy_mock = Mock()
    sdp_subarray1_proxy_mock = Mock()
    dish_ln_proxy_mock = Mock()

    proxies_to_mock = {
        csp_subarray1_ln_fqdn : csp_subarray1_ln_proxy_mock,
        csp_subarray1_fqdn : csp_subarray1_proxy_mock,
        sdp_subarray1_ln_fqdn : sdp_subarray1_ln_proxy_mock,
        sdp_subarray1_fqdn : sdp_subarray1_proxy_mock,
        dish_ln_prefix + "0001" : dish_ln_proxy_mock
    }

    csp_subarray1_proxy_mock.obsState = ObsState.IDLE
    sdp_subarray1_proxy_mock.obsState = ObsState.IDLE

    with fake_tango_system(SubarrayNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        tango_context.device.On()
        assign_input = '{"dish":{"receptorIDList":["0001","0002"]},"sdp":{"id":"sbi-mvp01-20200325-00001"' \
                        ',"max_length":100.0,"scan_types":[{"id":"science_A","coordinate_system":"ICRS",' \
                        '"ra":"21:08:47.92","dec":"-88:5.7:22.9","subbands":[{"freq_min":0.35e9,"freq_max"' \
                        ':1.05e9,"nchan":372,"input_link_map":[[1,0],[101,1]]}]},{"id":"calibration_B",' \
                        '"coordinate_system":"ICRS","ra":"21:08:47.92","dec":"-88:5.7:22.9","subbands":' \
                        '[{"freq_min":0.35e9,"freq_max":1.05e9,"nchan":372,"input_link_map":[[1,0],[101,1]]}]}],' \
                        '"processing_blocks":[{"id":"pb-mvp01-20200325-00001","workflow":{"type":"realtime",' \
                        '"id":"vis_receive","version":"0.1.0"},"parameters":{}},{"id":"pb-mvp01-20200325-00002"' \
                        ',"workflow":{"type":"realtime","id":"test_realtime","version":"0.1.0"},"parameters":{}},' \
                        '{"id":"pb-mvp01-20200325-00003","workflow":{"type":"batch","id":"ical","version":"0.1.0"}' \
                        ',"parameters":{},"dependencies":[{"pb_id":"pb-mvp01-20200325-00001","type":["visibilities"' \
                        ']}]},{"id":"pb-mvp01-20200325-00004","workflow":{"type":"batch","id":"dpreb","version":' \
                        '"0.1.0"},"parameters":{},"dependencies":[{"pb_id":"pb-mvp01-20200325-00003","type":' \
                        '["calibration"]}]}]}}'
        tango_context.device.AssignResources(assign_input)

        tango_context.device.Configure('{"pointing":{"target":{"system":"ICRS","name":""Polaris Australis",'
                                       '"RA":"21:08:47.92","dec":"-88:5.7:22.9"}},"dish":{"receiverBand":"1"},"csp":'
                                       '{"id":"sbi-mvp01-20200325-00001-science_A","frequencyBand":"1","fsp":[{"fspID":'
                                       '1,"functionMode":"CORR","frequencySliceID":1,"integrationTime":1400,'
                                       '"corrBandwidth":0}]},"sdp":{"scan_type":"science_A"},'
                                       '"tmc":{"scanDuration":10.0}}')

        # assert:
        sdp_config = '{"sdp": {"scan_type": "science_A"}}'
        sdp_subarray1_ln_proxy_mock.command_inout.assert_called_with(const.CMD_CONFIGURE, sdp_config)

        csp_config = '{"id": "sbi-mvp01-20200325-00001-science_A", "frequencyBand": "1", "fsp": [{"fspID": 1, ' \
                          '"functionMode": "CORR", "frequencySliceID": 1, "integrationTime": 1400, "corrBandwidth": 0}],' \
                          ' "delayModelSubscriptionPoint": "ska_mid/tm_leaf_node/csp_subarray01/delayModel", ' \
                          '"visDestinationAddressSubscriptionPoint": "mid_sdp/elt/subarray_1/receiveAddresses", ' \
                          '"pointing": {"target": {"system": "ICRS", "name": "Polaris Australis","RA":"21:08:47.92",'\ 
                          '"dec":"-88:5.7:22.9"}}, "scanID": "1"}'
        csp_subarray1_ln_proxy_mock.command_inout.assert_called_with(const.CMD_CONFIGURE, csp_config)


def create_dummy_event_state(device_fqdn, attribute, attr_value):
    fake_event = Mock()
    fake_event.err = False
    fake_event.attr_name = f"{device_fqdn}/{attribute}"
    fake_event.attr_value.value = attr_value
    return fake_event

def test_configure_command_subarray_with_invalid_key():
    csp_subarray1_ln_fqdn = 'ska_mid/tm_leaf_node/csp_subarray01'
    csp_subarray1_fqdn = 'mid_csp/elt/subarray_01'
    sdp_subarray1_ln_fqdn = 'ska_mid/tm_leaf_node/sdp_subarray01'
    sdp_subarray1_fqdn = 'mid_sdp/elt/subarray_1'
    dish_ln_prefix = 'ska_mid/tm_leaf_node/d'

    dut_properties = {
        'CspSubarrayLNFQDN': csp_subarray1_ln_fqdn,
        'CspSubarrayFQDN': csp_subarray1_fqdn,
        'SdpSubarrayLNFQDN': sdp_subarray1_ln_fqdn,
        'SdpSubarrayFQDN': sdp_subarray1_fqdn,
        'DishLeafNodePrefix': dish_ln_prefix
    }

    csp_subarray1_ln_proxy_mock = Mock()
    csp_subarray1_proxy_mock = Mock()
    sdp_subarray1_ln_proxy_mock = Mock()
    sdp_subarray1_proxy_mock = Mock()
    dish_ln_proxy_mock = Mock()

    proxies_to_mock = {
        csp_subarray1_ln_fqdn: csp_subarray1_ln_proxy_mock,
        csp_subarray1_fqdn: csp_subarray1_proxy_mock,
        sdp_subarray1_ln_fqdn: sdp_subarray1_ln_proxy_mock,
        sdp_subarray1_fqdn: sdp_subarray1_proxy_mock,
        dish_ln_prefix + "0001": dish_ln_proxy_mock
    }

    csp_subarray1_proxy_mock.obsState = ObsState.IDLE
    sdp_subarray1_proxy_mock.obsState = ObsState.IDLE

    with fake_tango_system(SubarrayNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        tango_context.device.On()
        assign_input = '{"dish":{"receptorIDList":["0001","0002"]},"sdp":{"id":"sbi-mvp01-20200325-00001"' \
                       ',"max_length":100.0,"scan_types":[{"id":"science_A","coordinate_system":"ICRS",' \
                       '"ra":"21:08:47.92","dec":"-88:5.7:22.9","subbands":[{"freq_min":0.35e9,"freq_max"' \
                       ':1.05e9,"nchan":372,"input_link_map":[[1,0],[101,1]]}]},{"id":"calibration_B",' \
                       '"coordinate_system":"ICRS","ra":"21:08:47.92","dec":"-88:5.7:22.9","subbands":' \
                       '[{"freq_min":0.35e9,"freq_max":1.05e9,"nchan":372,"input_link_map":[[1,0],[101,1]]}]}],' \
                       '"processing_blocks":[{"id":"pb-mvp01-20200325-00001","workflow":{"type":"realtime",' \
                       '"id":"vis_receive","version":"0.1.0"},"parameters":{}},{"id":"pb-mvp01-20200325-00002"' \
                       ',"workflow":{"type":"realtime","id":"test_realtime","version":"0.1.0"},"parameters":{}},' \
                       '{"id":"pb-mvp01-20200325-00003","workflow":{"type":"batch","id":"ical","version":"0.1.0"}' \
                       ',"parameters":{},"dependencies":[{"pb_id":"pb-mvp01-20200325-00001","type":["visibilities"' \
                       ']}]},{"id":"pb-mvp01-20200325-00004","workflow":{"type":"batch","id":"dpreb","version":' \
                       '"0.1.0"},"parameters":{},"dependencies":[{"pb_id":"pb-mvp01-20200325-00003","type":' \
                       '["calibration"]}]}]}}'
        tango_context.device.AssignResources(assign_input)
        with pytest.raises(tango.DevFailed):
            tango_context.device.Configure('{"pointing12345":{"target":{"system":"ICRS","name":"Polaris Australis","RA":"21:08:47.92","dec":"-88:5.7:22.9"}},"dish":{"receiverBand":"1"},"csp":'
                                       '{"id":"sbi-mvp01-20200325-00001-science_A","frequencyBand":"1","fsp":[{"fspID":'
                                       '1,"functionMode":"CORR","frequencySliceID":1,"integrationTime":1400,'
                                       '"corrBandwidth":0}]},"sdp":{"scan_type":"science_A"},'
                                       '"tmc":{"scanDuration":10.0}}')

        # assert:
        assert tango_context.device.obsState == ObsState.IDLE


def test_configure_command_subarray_with_invalid_configure_input():
    csp_subarray1_ln_fqdn = 'ska_mid/tm_leaf_node/csp_subarray01'
    csp_subarray1_fqdn = 'mid_csp/elt/subarray_01'
    sdp_subarray1_ln_fqdn = 'ska_mid/tm_leaf_node/sdp_subarray01'
    sdp_subarray1_fqdn = 'mid_sdp/elt/subarray_1'
    dish_ln_prefix = 'ska_mid/tm_leaf_node/d'

    dut_properties = {
        'CspSubarrayLNFQDN': csp_subarray1_ln_fqdn,
        'CspSubarrayFQDN': csp_subarray1_fqdn,
        'SdpSubarrayLNFQDN': sdp_subarray1_ln_fqdn,
        'SdpSubarrayFQDN': sdp_subarray1_fqdn,
        'DishLeafNodePrefix': dish_ln_prefix
    }

    csp_subarray1_ln_proxy_mock = Mock()
    csp_subarray1_proxy_mock = Mock()
    sdp_subarray1_ln_proxy_mock = Mock()
    sdp_subarray1_proxy_mock = Mock()
    dish_ln_proxy_mock = Mock()

    proxies_to_mock = {
        csp_subarray1_ln_fqdn: csp_subarray1_ln_proxy_mock,
        csp_subarray1_fqdn: csp_subarray1_proxy_mock,
        sdp_subarray1_ln_fqdn: sdp_subarray1_ln_proxy_mock,
        sdp_subarray1_fqdn: sdp_subarray1_proxy_mock,
        dish_ln_prefix + "0001": dish_ln_proxy_mock
    }

    csp_subarray1_proxy_mock.obsState = ObsState.IDLE
    sdp_subarray1_proxy_mock.obsState = ObsState.IDLE

    with fake_tango_system(SubarrayNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        tango_context.device.On()
        assign_input = '{"dish":{"receptorIDList":["0001","0002"]},"sdp":{"id":"sbi-mvp01-20200325-00001"' \
                       ',"max_length":100.0,"scan_types":[{"id":"science_A","coordinate_system":"ICRS",' \
                       '"ra":"21:08:47.92","dec":"-88:5.7:22.9","subbands":[{"freq_min":0.35e9,"freq_max"' \
                       ':1.05e9,"nchan":372,"input_link_map":[[1,0],[101,1]]}]},{"id":"calibration_B",' \
                       '"coordinate_system":"ICRS","ra":"21:08:47.92","dec":"-88:5.7:22.9","subbands":' \
                       '[{"freq_min":0.35e9,"freq_max":1.05e9,"nchan":372,"input_link_map":[[1,0],[101,1]]}]}],' \
                       '"processing_blocks":[{"id":"pb-mvp01-20200325-00001","workflow":{"type":"realtime",' \
                       '"id":"vis_receive","version":"0.1.0"},"parameters":{}},{"id":"pb-mvp01-20200325-00002"' \
                       ',"workflow":{"type":"realtime","id":"test_realtime","version":"0.1.0"},"parameters":{}},' \
                       '{"id":"pb-mvp01-20200325-00003","workflow":{"type":"batch","id":"ical","version":"0.1.0"}' \
                       ',"parameters":{},"dependencies":[{"pb_id":"pb-mvp01-20200325-00001","type":["visibilities"' \
                       ']}]},{"id":"pb-mvp01-20200325-00004","workflow":{"type":"batch","id":"dpreb","version":' \
                       '"0.1.0"},"parameters":{},"dependencies":[{"pb_id":"pb-mvp01-20200325-00003","type":' \
                       '["calibration"]}]}]}}'
        tango_context.device.AssignResources(assign_input)
        with pytest.raises(tango.DevFailed):
            tango_context.device.Configure('{"invalid_key"}')

        # assert:
        assert tango_context.device.obsState == ObsState.IDLE
        assert const.ERR_INVALID_JSON in tango_context.device.activityMessage


def test_start_scan_should_command_subarray_to_start_scan_when_it_is_ready():
    csp_subarray1_ln_fqdn = 'ska_mid/tm_leaf_node/csp_subarray01'
    csp_subarray1_fqdn = 'mid_csp/elt/subarray_01'
    sdp_subarray1_ln_fqdn = 'ska_mid/tm_leaf_node/sdp_subarray01'
    sdp_subarray1_fqdn = 'mid_sdp/elt/subarray_1'
    dish_ln_prefix = 'ska_mid/tm_leaf_node/d'

    dut_properties = {
        'CspSubarrayLNFQDN': csp_subarray1_ln_fqdn,
        'CspSubarrayFQDN': csp_subarray1_fqdn,
        'SdpSubarrayLNFQDN': sdp_subarray1_ln_fqdn,
        'SdpSubarrayFQDN': sdp_subarray1_fqdn,
        'DishLeafNodePrefix': dish_ln_prefix
    }
    event_subscription_map = {}
    csp_subarray1_ln_proxy_mock = Mock()
    csp_subarray1_proxy_mock = Mock()
    sdp_subarray1_ln_proxy_mock = Mock()
    sdp_subarray1_proxy_mock = Mock()
    dish_ln_proxy_mock = Mock()

    proxies_to_mock = {
        csp_subarray1_ln_fqdn : csp_subarray1_ln_proxy_mock,
        csp_subarray1_fqdn : csp_subarray1_proxy_mock,
        sdp_subarray1_ln_fqdn : sdp_subarray1_ln_proxy_mock,
        sdp_subarray1_fqdn : sdp_subarray1_proxy_mock,
        dish_ln_prefix + '0001' : dish_ln_proxy_mock
    }
    csp_subarray1_obsstate_attribute = "cspSubarrayObsState"
    sdp_subarray1_obsstate_attribute = "sdpSubarrayObsState"
    dish_pointing_state_attribute = "dishPointingState"

    event_subscription_map = {}
    dish_pointing_state_map = {}
    csp_subarray1_ln_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args, **kwargs: event_subscription_map.
            update({attr_name: callback}))

    sdp_subarray1_ln_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args, **kwargs: event_subscription_map.
            update({attr_name: callback}))

    dish_ln_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args, **kwargs: dish_pointing_state_map.
            update({attr_name: callback}))

    with fake_tango_system(SubarrayNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        tango_context.device.On()
        csp_subarray1_proxy_mock.obsState = ObsState.READY
        sdp_subarray1_proxy_mock.obsState = ObsState.READY
        attribute = 'ObsState'
        dummy_event_csp = create_dummy_event_state(csp_subarray1_ln_fqdn, attribute, ObsState.READY)
        event_subscription_map[csp_subarray1_obsstate_attribute](dummy_event_csp)

        dummy_event_sdp = create_dummy_event_state(sdp_subarray1_ln_fqdn, attribute, ObsState.READY)
        event_subscription_map[sdp_subarray1_obsstate_attribute](dummy_event_sdp)
        time.sleep(5)
        scan_input = '{"id": 1}'

        tango_context.device.Scan(scan_input)

        # assert:
        sdp_subarray1_ln_proxy_mock.command_inout.assert_called_with(const.CMD_SCAN, scan_input)

        csp_subarray1_ln_proxy_mock.command_inout.assert_called_with(const.CMD_START_SCAN, [scan_input])


def test_end_scan_should_command_subarray_to_end_scan_when_it_is_scanning():
    csp_subarray1_ln_fqdn = 'ska_mid/tm_leaf_node/csp_subarray01'
    csp_subarray1_fqdn = 'mid_csp/elt/subarray_01'
    sdp_subarray1_ln_fqdn = 'ska_mid/tm_leaf_node/sdp_subarray01'
    sdp_subarray1_fqdn = 'mid_sdp/elt/subarray_1'
    dish_ln_prefix = 'ska_mid/tm_leaf_node/d'

    dut_properties = {
        'CspSubarrayLNFQDN': csp_subarray1_ln_fqdn,
        'CspSubarrayFQDN': csp_subarray1_fqdn,
        'SdpSubarrayLNFQDN': sdp_subarray1_ln_fqdn,
        'SdpSubarrayFQDN': sdp_subarray1_fqdn,
        'DishLeafNodePrefix': dish_ln_prefix
    }
    event_subscription_map = {}
    csp_subarray1_ln_proxy_mock = Mock()
    csp_subarray1_proxy_mock = Mock()
    sdp_subarray1_ln_proxy_mock = Mock()
    sdp_subarray1_proxy_mock = Mock()
    dish_ln_proxy_mock = Mock()

    proxies_to_mock = {
        csp_subarray1_ln_fqdn: csp_subarray1_ln_proxy_mock,
        csp_subarray1_fqdn: csp_subarray1_proxy_mock,
        sdp_subarray1_ln_fqdn: sdp_subarray1_ln_proxy_mock,
        sdp_subarray1_fqdn: sdp_subarray1_proxy_mock,
        dish_ln_prefix + '0001': dish_ln_proxy_mock
    }
    csp_subarray1_obsstate_attribute = "cspSubarrayObsState"
    sdp_subarray1_obsstate_attribute = "sdpSubarrayObsState"
    dish_pointing_state_attribute = "dishPointingState"

    event_subscription_map = {}
    dish_pointing_state_map = {}
    csp_subarray1_ln_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args, **kwargs: event_subscription_map.
            update({attr_name: callback}))

    sdp_subarray1_ln_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args, **kwargs: event_subscription_map.
            update({attr_name: callback}))

    dish_ln_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args, **kwargs: dish_pointing_state_map.
            update({attr_name: callback}))

    with fake_tango_system(SubarrayNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        tango_context.device.On()
        csp_subarray1_proxy_mock.obsState = ObsState.SCANNING
        sdp_subarray1_proxy_mock.obsState = ObsState.SCANNING
        attribute = 'ObsState'
        dummy_event_csp = create_dummy_event_state(csp_subarray1_ln_fqdn, attribute,
                                                               ObsState.SCANNING)
        event_subscription_map[csp_subarray1_obsstate_attribute](dummy_event_csp)

        dummy_event_sdp = create_dummy_event_state(sdp_subarray1_ln_fqdn, attribute,
                                                               ObsState.SCANNING)
        event_subscription_map[sdp_subarray1_obsstate_attribute](dummy_event_sdp)

        time.sleep(5)
        tango_context.device.EndScan()

        # assert:
        sdp_subarray1_ln_proxy_mock.command_inout.assert_called_with(const.CMD_END_SCAN)
        csp_subarray1_ln_proxy_mock.command_inout.assert_called_with(const.CMD_END_SCAN)


def test_end_sb_should_command_subarray_to_end_sb_when_it_is_ready():
    csp_subarray1_ln_fqdn = 'ska_mid/tm_leaf_node/csp_subarray01'
    csp_subarray1_fqdn = 'mid_csp/elt/subarray_01'
    sdp_subarray1_ln_fqdn = 'ska_mid/tm_leaf_node/sdp_subarray01'
    sdp_subarray1_fqdn = 'mid_sdp/elt/subarray_1'
    dish_ln_prefix = 'ska_mid/tm_leaf_node/d'

    dut_properties = {
        'CspSubarrayLNFQDN': csp_subarray1_ln_fqdn,
        'CspSubarrayFQDN': csp_subarray1_fqdn,
        'SdpSubarrayLNFQDN': sdp_subarray1_ln_fqdn,
        'SdpSubarrayFQDN': sdp_subarray1_fqdn,
        'DishLeafNodePrefix': dish_ln_prefix
    }
    csp_subarray1_ln_proxy_mock = Mock()
    csp_subarray1_proxy_mock = Mock()
    sdp_subarray1_ln_proxy_mock = Mock()
    sdp_subarray1_proxy_mock = Mock()
    dish_ln_proxy_mock = Mock()

    proxies_to_mock = {
        csp_subarray1_ln_fqdn: csp_subarray1_ln_proxy_mock,
        csp_subarray1_fqdn: csp_subarray1_proxy_mock,
        sdp_subarray1_ln_fqdn: sdp_subarray1_ln_proxy_mock,
        sdp_subarray1_fqdn: sdp_subarray1_proxy_mock,
        dish_ln_prefix + '0001': dish_ln_proxy_mock
    }

    csp_subarray1_obsstate_attribute = "cspSubarrayObsState"
    sdp_subarray1_obsstate_attribute = "sdpSubarrayObsState"
    dish_pointing_state_attribute = "dishPointingState"

    event_subscription_map = {}
    dish_pointing_state_map = {}

    csp_subarray1_ln_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args, **kwargs: event_subscription_map.
            update({attr_name: callback}))

    sdp_subarray1_ln_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args, **kwargs: event_subscription_map.
            update({attr_name: callback}))

    with fake_tango_system(SubarrayNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        tango_context.device.On()

        csp_subarray1_proxy_mock.obsState = ObsState.READY
        sdp_subarray1_proxy_mock.obsState = ObsState.READY
        attribute = 'ObsState'
        dummy_event_csp = create_dummy_event_state(csp_subarray1_ln_fqdn, attribute, ObsState.READY)
        event_subscription_map[csp_subarray1_obsstate_attribute](dummy_event_csp)

        dummy_event_sdp = create_dummy_event_state(sdp_subarray1_ln_fqdn, attribute, ObsState.READY)
        event_subscription_map[sdp_subarray1_obsstate_attribute](dummy_event_sdp)
        time.sleep(5)

        tango_context.device.EndSB()
        # assert:
        sdp_subarray1_ln_proxy_mock.command_inout.assert_called_with(const.CMD_ENDSB)
        csp_subarray1_ln_proxy_mock.command_inout.assert_called_with(const.CMD_GOTOIDLE)
        dish_ln_proxy_mock.command_inout.asser_called_with(const.CMD_STOP_TRACK)


def test_obs_state_is_ready_when_other_leaf_node_is_ready_after_start():
    csp_subarray1_ln_fqdn = 'ska_mid/tm_leaf_node/csp_subarray01'
    csp_subarray1_fqdn = 'mid_csp/elt/subarray_01'
    sdp_subarray1_ln_fqdn = 'ska_mid/tm_leaf_node/sdp_subarray01'
    sdp_subarray1_fqdn = 'mid_sdp/elt/subarray_1'
    dish_ln_prefix = 'ska_mid/tm_leaf_node/d'

    dut_properties = {
        'CspSubarrayLNFQDN': csp_subarray1_ln_fqdn,
        'CspSubarrayFQDN': csp_subarray1_fqdn,
        'SdpSubarrayLNFQDN': sdp_subarray1_ln_fqdn,
        'SdpSubarrayFQDN': sdp_subarray1_fqdn,
        'DishLeafNodePrefix': dish_ln_prefix
    }

    csp_subarray1_ln_proxy_mock = Mock()
    csp_subarray1_proxy_mock = Mock()
    sdp_subarray1_ln_proxy_mock = Mock()
    sdp_subarray1_proxy_mock = Mock()
    dish_ln_proxy_mock = Mock()

    proxies_to_mock = {
        csp_subarray1_ln_fqdn: csp_subarray1_ln_proxy_mock,
        csp_subarray1_fqdn: csp_subarray1_proxy_mock,
        sdp_subarray1_ln_fqdn: sdp_subarray1_ln_proxy_mock,
        sdp_subarray1_fqdn: sdp_subarray1_proxy_mock,
        dish_ln_prefix + "0001": dish_ln_proxy_mock
    }
    csp_subarray1_obsstate_attribute = "cspSubarrayObsState"
    sdp_subarray1_obsstate_attribute = "sdpSubarrayObsState"
    dish_pointing_state_attribute = "dishPointingState"

    event_subscription_map = {}
    dish_pointing_state_map = {}

    csp_subarray1_ln_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args, **kwargs: event_subscription_map.
            update({attr_name: callback}))

    sdp_subarray1_ln_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args, **kwargs: event_subscription_map.
            update({attr_name: callback}))

    with fake_tango_system(SubarrayNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        # act:
        attribute = 'ObsState'
        dummy_event_csp = create_dummy_event_state(csp_subarray1_ln_fqdn, attribute, ObsState.READY)
        event_subscription_map[csp_subarray1_obsstate_attribute](dummy_event_csp)

        dummy_event_sdp = create_dummy_event_state(sdp_subarray1_ln_fqdn, attribute, ObsState.READY)
        event_subscription_map[sdp_subarray1_obsstate_attribute](dummy_event_sdp)

        # assert:
        time.sleep(5)
        assert tango_context.device.obsState == ObsState.READY


def test_obs_state_is_scanning_when_other_leaf_node_is_scanning_after_start():
    csp_subarray1_ln_fqdn = 'ska_mid/tm_leaf_node/csp_subarray01'
    csp_subarray1_fqdn = 'mid_csp/elt/subarray_01'
    sdp_subarray1_ln_fqdn = 'ska_mid/tm_leaf_node/sdp_subarray01'
    sdp_subarray1_fqdn = 'mid_sdp/elt/subarray_1'
    dish_ln_prefix = 'ska_mid/tm_leaf_node/d'

    dut_properties = {
        'CspSubarrayLNFQDN': csp_subarray1_ln_fqdn,
        'CspSubarrayFQDN': csp_subarray1_fqdn,
        'SdpSubarrayLNFQDN': sdp_subarray1_ln_fqdn,
        'SdpSubarrayFQDN': sdp_subarray1_fqdn,
        'DishLeafNodePrefix': dish_ln_prefix
    }

    csp_subarray1_ln_proxy_mock = Mock()
    csp_subarray1_proxy_mock = Mock()
    sdp_subarray1_ln_proxy_mock = Mock()
    sdp_subarray1_proxy_mock = Mock()
    dish_ln_proxy_mock = Mock()

    proxies_to_mock = {
        csp_subarray1_ln_fqdn: csp_subarray1_ln_proxy_mock,
        csp_subarray1_fqdn: csp_subarray1_proxy_mock,
        sdp_subarray1_ln_fqdn: sdp_subarray1_ln_proxy_mock,
        sdp_subarray1_fqdn: sdp_subarray1_proxy_mock,
        dish_ln_prefix + "0001": dish_ln_proxy_mock
    }
    csp_subarray1_obsstate_attribute = "cspSubarrayObsState"
    sdp_subarray1_obsstate_attribute = "sdpSubarrayObsState"

    event_subscription_map = {}

    csp_subarray1_ln_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args, **kwargs: event_subscription_map.
            update({attr_name: callback}))

    sdp_subarray1_ln_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args, **kwargs: event_subscription_map.
            update({attr_name: callback}))

    with fake_tango_system(SubarrayNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        # act:
        attribute = 'ObsState'
        dummy_event_csp = create_dummy_event_state(csp_subarray1_ln_fqdn, attribute, ObsState.SCANNING)
        event_subscription_map[csp_subarray1_obsstate_attribute](dummy_event_csp)

        dummy_event_sdp = create_dummy_event_state(sdp_subarray1_ln_fqdn, attribute, ObsState.SCANNING)
        event_subscription_map[sdp_subarray1_obsstate_attribute](dummy_event_sdp)
        # assert:
        time.sleep(5)
        assert tango_context.device.obsState == ObsState.SCANNING


def test_subarray_health_state_is_degraded_when_csp_subarray1_ln_is_degraded_after_start():
    csp_subarray1_ln_fqdn = 'ska_mid/tm_leaf_node/csp_subarray01'
    csp_subarray1_ln_health_attribute = 'cspsubarrayHealthState'
    initial_dut_properties = {
        'CspSubarrayLNFQDN': csp_subarray1_ln_fqdn
    }

    event_subscription_map = {}

    csp_subarray1_ln_proxy_mock = Mock()
    csp_subarray1_ln_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args, **kwargs: event_subscription_map.
            update({attr_name: callback}))

    proxies_to_mock = {
        csp_subarray1_ln_fqdn: csp_subarray1_ln_proxy_mock
    }

    with fake_tango_system(SubarrayNode, initial_dut_properties, proxies_to_mock) as tango_context:
        # act:
        health_state_value = HealthState.DEGRADED
        dummy_event = create_dummy_event_healthstate_with_proxy(
            csp_subarray1_ln_proxy_mock, csp_subarray1_ln_fqdn, health_state_value,
            csp_subarray1_ln_health_attribute)
        event_subscription_map[csp_subarray1_ln_health_attribute](dummy_event)

        # assert:
        assert tango_context.device.healthState == HealthState.DEGRADED


def test_subarray_health_state_is_ok_when_csp_and_sdp_subarray1_ln_is_ok_after_start():
    csp_subarray1_ln_fqdn = 'ska_mid/tm_leaf_node/csp_subarray01'
    sdp_subarray1_ln_fqdn = 'ska_mid/tm_leaf_node/sdp_subarray01'
    csp_subarray1_ln_health_attribute = 'cspsubarrayHealthState'
    sdp_subarray1_ln_health_attribute = 'sdpSubarrayHealthState'
    initial_dut_properties = {
        'CspSubarrayLNFQDN': csp_subarray1_ln_fqdn,
        'SdpSubarrayLNFQDN': sdp_subarray1_ln_fqdn,
    }

    subarray_ln_health_state_map = {}

    csp_subarray1_ln_proxy_mock = Mock()
    sdp_subarray1_ln_proxy_mock = Mock()

    proxies_to_mock = {
        csp_subarray1_ln_fqdn: csp_subarray1_ln_proxy_mock,
        sdp_subarray1_ln_fqdn: sdp_subarray1_ln_proxy_mock
    }
    csp_subarray1_ln_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args, **kwargs: subarray_ln_health_state_map.
            update({attr_name: callback}))

    sdp_subarray1_ln_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args, **kwargs: subarray_ln_health_state_map.
            update({attr_name: callback}))

    with fake_tango_system(SubarrayNode, initial_dut_properties, proxies_to_mock) as tango_context:
        # act:
        health_state_value = HealthState.OK
        dummy_event_csp = create_dummy_event_healthstate_with_proxy(
            csp_subarray1_ln_proxy_mock, csp_subarray1_ln_fqdn, health_state_value,
            csp_subarray1_ln_health_attribute)
        subarray_ln_health_state_map[csp_subarray1_ln_health_attribute](dummy_event_csp)

        health_state_value = HealthState.OK
        dummy_event_sdp = create_dummy_event_healthstate_with_proxy(
            sdp_subarray1_ln_proxy_mock, sdp_subarray1_ln_fqdn, health_state_value,
            sdp_subarray1_ln_health_attribute)
        subarray_ln_health_state_map[sdp_subarray1_ln_health_attribute](dummy_event_sdp)

        # assert:
        assert tango_context.device.healthState == HealthState.OK


def test_subarray_health_state_is_unknown_when_csp_subarray1_ln_is_unknown_after_start():
    csp_subarray1_ln_fqdn = 'ska_mid/tm_leaf_node/csp_subarray01'
    csp_subarray1_ln_health_attribute = 'cspsubarrayHealthState'
    initial_dut_properties = {
        'CspSubarrayLNFQDN': csp_subarray1_ln_fqdn
    }

    event_subscription_map = {}

    csp_subarray1_ln_proxy_mock = Mock()
    csp_subarray1_ln_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args, **kwargs: event_subscription_map.
            update({attr_name: callback}))

    proxies_to_mock = {
        csp_subarray1_ln_fqdn: csp_subarray1_ln_proxy_mock
    }

    with fake_tango_system(SubarrayNode, initial_dut_properties, proxies_to_mock) as tango_context:
        # act:
        health_state_value = HealthState.UNKNOWN
        dummy_event = create_dummy_event_healthstate_with_proxy(
            csp_subarray1_ln_proxy_mock, csp_subarray1_ln_fqdn, health_state_value,
            csp_subarray1_ln_health_attribute)
        event_subscription_map[csp_subarray1_ln_health_attribute](dummy_event)

        # assert:
        assert tango_context.device.healthState == HealthState.UNKNOWN


def test_subarray_health_state_is_failed_when_csp_subarray1_ln_is_failed_after_start():
    csp_subarray1_ln_fqdn = 'ska_mid/tm_leaf_node/csp_subarray01'
    csp_subarray1_ln_health_attribute = 'cspsubarrayHealthState'
    initial_dut_properties = {
        'CspSubarrayLNFQDN': csp_subarray1_ln_fqdn
    }

    event_subscription_map = {}

    csp_subarray1_ln_proxy_mock = Mock()
    csp_subarray1_ln_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args, **kwargs: event_subscription_map.
            update({attr_name: callback}))

    proxies_to_mock = {
        csp_subarray1_ln_fqdn: csp_subarray1_ln_proxy_mock
    }

    with fake_tango_system(SubarrayNode, initial_dut_properties, proxies_to_mock) as tango_context:
        # act:
        health_state_value = HealthState.FAILED
        dummy_event = create_dummy_event_healthstate_with_proxy(
            csp_subarray1_ln_proxy_mock, csp_subarray1_ln_fqdn, health_state_value,
            csp_subarray1_ln_health_attribute)
        event_subscription_map[csp_subarray1_ln_health_attribute](dummy_event)

        # assert:
        assert tango_context.device.healthState == HealthState.FAILED


def create_dummy_event_healthstate_with_proxy(proxy_mock, device_fqdn, health_state_value, attribute):
    fake_event = Mock()
    fake_event.err = False
    fake_event.attr_name = f"{device_fqdn}/{attribute}"
    fake_event.attr_value.value = health_state_value
    fake_event.device= proxy_mock
    return fake_event


def test_subarray_device_state_is_on_when_csp_and_sdp_subarray1_is_on_after_start():
    csp_subarray1_fqdn = 'mid_csp/elt/subarray_01'
    sdp_subarray1_fqdn = 'mid_sdp/elt/subarray_1'

    initial_dut_properties = {
        'CspSubarrayFQDN': csp_subarray1_fqdn,
        'SdpSubarrayFQDN': sdp_subarray1_fqdn
    }

    csp_subarray1_proxy_mock = Mock()
    sdp_subarray1_proxy_mock = Mock()

    proxies_to_mock = {
        csp_subarray1_fqdn: csp_subarray1_proxy_mock,
        sdp_subarray1_fqdn: sdp_subarray1_proxy_mock
    }

    event_subscription_map = {}

    csp_subarray1_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args, **kwargs: event_subscription_map.
            update({attr_name: callback}))

    sdp_subarray1_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args, **kwargs: event_subscription_map.
            update({attr_name: callback}))

    with fake_tango_system(SubarrayNode, initial_dut_properties, proxies_to_mock) as tango_context:
        # act:
        attribute = "state"
        dummy_event = create_dummy_event_state(csp_subarray1_fqdn, attribute, DevState.ON)
        event_subscription_map[attribute](dummy_event)

        dummy_event = create_dummy_event_state(sdp_subarray1_fqdn, attribute, DevState.ON)
        event_subscription_map[attribute](dummy_event)

        # assert:
        assert tango_context.device.State() == DevState.ON


def test_status():
    """Test for Status"""
    with fake_tango_system(SubarrayNode) as tango_context:
        assert tango_context.device.Status() == const.STR_SA_INIT_SUCCESS


def test_state():
    """Test for State"""
    with fake_tango_system(SubarrayNode) as tango_context:
        assert tango_context.device.State() == DevState.DISABLE


def test_health_state():
    """Test for healthState"""
    with fake_tango_system(SubarrayNode) as tango_context:
        assert tango_context.device.healthState == HealthState.OK


def test_activation_time():
    """Test for activationTime"""
    with fake_tango_system(SubarrayNode) as tango_context:
        assert tango_context.device.activationTime == 0.0


def test_admin_mode():
    """Test for adminMode"""
    with fake_tango_system(SubarrayNode) as tango_context:
        assert tango_context.device.adminMode == AdminMode.OFFLINE


def test_build_state():
    """Test for buildState"""
    with fake_tango_system(SubarrayNode) as tango_context:
        assert tango_context.device.buildState == (
        "lmcbaseclasses, 0.5.1, A set of generic base devices for SKA Telescope.")


def test_configuration_delay_expected():
    """Test for configurationDelayExpected"""
    with fake_tango_system(SubarrayNode) as tango_context:
        assert tango_context.device.configurationDelayExpected == 0


def test_configuration_progress():
    """Test for configurationProgress"""
    with fake_tango_system(SubarrayNode) as tango_context:
        assert tango_context.device.configurationProgress == 0


def test_control_mode():
    """Test for controlMode"""
    with fake_tango_system(SubarrayNode) as tango_context:
        control_mode = tango_context.device.controlMode.REMOTE
        tango_context.device.controlMode = control_mode
        assert tango_context.device.controlMode == control_mode


def test_obs_mode():
    """Test for obsMode"""
    with fake_tango_system(SubarrayNode) as tango_context:
        assert tango_context.device.obsMode == ObsMode.IDLE


def test_obs_state():
    """Test for obsState"""
    with fake_tango_system(SubarrayNode) as tango_context:
        assert tango_context.device.obsState == ObsState.IDLE


def test_simulation_mode():
    """Test for simulationMode"""
    with fake_tango_system(SubarrayNode) as tango_context:
        simulation_mode = SimulationMode.FALSE
        tango_context.device.simulationMode = simulation_mode
        assert tango_context.device.simulationMode == simulation_mode


def test_test_mode():
    """Test for testMode"""
    with fake_tango_system(SubarrayNode) as tango_context:
        test_mode = TestMode.NONE
        tango_context.device.testMode = test_mode
        assert tango_context.device.testMode == test_mode


def test_version_id():
    """Test for versionId"""
    with fake_tango_system(SubarrayNode) as tango_context:
        assert tango_context.device.versionId == "0.5.1"


def test_scan_id():
    """Test for scanID"""
    with fake_tango_system(SubarrayNode) as tango_context:
        assert tango_context.device.scanID == ""


def test_sb_id():
    """Test for sbID"""
    with fake_tango_system(SubarrayNode) as tango_context:
        assert tango_context.device.sbID == ""


def test_activity_message():
    """Test for activityMessage"""
    with fake_tango_system(SubarrayNode) as tango_context:
        assert tango_context.device.activityMessage == const.STR_SA_INIT_SUCCESS


def test_configured_capabilities():
    """Test for configuredCapabilities"""
    with fake_tango_system(SubarrayNode) as tango_context:
        assert tango_context.device.configuredCapabilities is None


def test_receptor_id_list():
    """Test for receptorIDList"""
    with fake_tango_system(SubarrayNode) as tango_context:
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
