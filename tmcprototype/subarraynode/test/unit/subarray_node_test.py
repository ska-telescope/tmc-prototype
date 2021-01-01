# Standard Python imports
import contextlib
import importlib
import sys
import json
import types
from typing import Any, Callable, Dict, NamedTuple, Tuple
import pytest
import mock
from mock import Mock, MagicMock
from os.path import dirname, join
import threading
import re

# Tango imports
import tango
from tango import DevState, DeviceData
from tango.test_context import DeviceTestContext
# Additional import
from subarraynode import SubarrayNode, const, ElementDeviceData, release
from subarraynode.const import PointingState
from tmc.common.tango_client import TangoClient
from subarraynode.configure_command import ConfigureCommand
from subarraynode.scan_command import ScanCommand
from subarraynode.end_scan_command import EndScanCommand
from subarraynode.end_command import EndCommand
from subarraynode.abort_command import AbortCommand
from subarraynode.obsreset_command import ObsResetCommand
from subarraynode.restart_command import RestartCommand
from subarraynode.release_all_resources_command import ReleaseAllResourcesCommand
from subarraynode.track_command import TrackCommand
from subarraynode.device_data import DeviceData
from ska.base.control_model import AdminMode, HealthState, ObsState, ObsMode, TestMode, SimulationMode, \
    LoggingLevel
from ska.base.commands import ResultCode



# Command wait timeout:
assign_input_file = 'command_AssignResources.json'
path = join(dirname(__file__), 'data', assign_input_file)
with open(path, 'r') as f:
    assign_input_str = f.read()

scan_input_file = 'command_Scan.json'
path = join(dirname(__file__), 'data', scan_input_file)
with open(path, 'r') as f:
    scan_input_str = f.read()

configure_input_file = 'command_Configure.json'
path = join(dirname(__file__), 'data', configure_input_file)
with open(path, 'r') as f:
    configure_str = f.read()

configure_invalid_key_file = 'invalid_key_Configure.json'
path = join(dirname(__file__), 'data', configure_invalid_key_file)
with open(path, 'r') as f:
    configure_invalid_key = f.read()

configure_invalid_input_file = 'invalid_input_Configure.json'
path = join(dirname(__file__), 'data', configure_invalid_input_file)
with open(path, 'r') as f:
    invalid_conf_input = f.read()

assign_invalid_key_file = 'invalid_key_AssignResources.json'
path = join(dirname(__file__), 'data', assign_invalid_key_file)
with open(path, 'r') as f:
    assign_invalid_key = f.read()

sdp_configure_input_file = 'command_sdp_Configure.json'
path = join(dirname(__file__), 'data', sdp_configure_input_file)
with open(path, 'r') as f:
    sdp_conf_str = f.read()

csp_configure_input_file = 'command_csp_Configure.json'
path = join(dirname(__file__), 'data', csp_configure_input_file)
with open(path, 'r') as f:
    csp_conf_str = f.read()

scan_config_file = 'example_scan_config.json'
path = join(dirname(__file__), 'data', scan_config_file)
with open(path, 'r') as f:
    scan_config_str = f.read()

invalid_scan_config_file = 'example_invalid_scan_config.json'
path = join(dirname(__file__), 'data', invalid_scan_config_file)
with open(path, 'r') as f:
    invalid_scan_config_str = f.read()

receive_addresses_file = 'receive_addresses.json'
path = join(dirname(__file__), 'data', receive_addresses_file)
with open(path, 'r') as f:
    receive_addresses_map = f.read()


def set_timeout_event(timeout_event):
    timeout_event.set()


def wait_for(tango_context, obs_state_to_change, timeout=10):
    timer_event = threading.Event()
    timer_thread = threading.Timer(timeout, set_timeout_event, timer_event)
    timer_thread.start()

    # wait till timeout or obsState to change
    while (not timer_event.isSet() and tango_context.device.obsState != obs_state_to_change):
        print("tango_context.device.obsState: ", tango_context.device.obsState)
        continue

    if timer_event.isSet():
        return "timeout"
    else:
        timer_thread.cancel()
        return True


@pytest.fixture(scope="function")
def example_scan_configuration():
    scan_config = json.loads(scan_config_str)
    return scan_config


@pytest.fixture(scope="function")
def example_invalid_scan_configuration():
    scan_config = json.loads(invalid_scan_config_str)
    return scan_config


@pytest.fixture(scope="function")
def csp_func_args():
    attr_name_map = {
        "string1": "attr1",
        "string2": "attr2"
    }
    return attr_name_map


@pytest.fixture(scope="function")
def sdp_func_receive_addresses():
    return receive_addresses_map


class TestElementDeviceData:
    def test_build_up_sdp_cmd_data_with_valid_scan_configuration(self, example_scan_configuration):
        valid_scan_config = example_scan_configuration
        sdp_cmd_data = ElementDeviceData.build_up_sdp_cmd_data(valid_scan_config)

        expected_string_dict = {
            "scan_type": "science_A"
        }
        expected_string_dict = json.dumps(expected_string_dict)
        assert isinstance(sdp_cmd_data, str)
        assert expected_string_dict == sdp_cmd_data

    def test_build_up_sdp_cmd_data_with_scan_type_missing_configuration(self, example_invalid_scan_configuration):
        invalid_scan_config = example_invalid_scan_configuration
        with pytest.raises(KeyError) as exception:
            ElementDeviceData.build_up_sdp_cmd_data(invalid_scan_config)
        expected_msg = "SDP Subarray scan_type is empty. Command data not built up"
        assert exception.value.args[0] == expected_msg

    def test_build_up_sdp_cmd_data_with_invalid_scan_configuration(self, example_scan_configuration):
        invalid_scan_config = example_scan_configuration.pop("sdp")
        with pytest.raises(KeyError) as exception:
            ElementDeviceData.build_up_sdp_cmd_data(invalid_scan_config)
        expected_msg = "SDP configuration must be given. Aborting SDP configuration."
        assert exception.value.args[0] == expected_msg

    def test_build_up_csp_cmd_data_with_valid_scan_configuration(self, example_scan_configuration, csp_func_args,
                                                                 sdp_func_receive_addresses):
        valid_scan_config = example_scan_configuration
        attr_name_map = csp_func_args
        receive_addresses_map = sdp_func_receive_addresses
        csp_cmd_data = ElementDeviceData.build_up_csp_cmd_data(valid_scan_config, attr_name_map, receive_addresses_map)
        expected_json_string_file = 'expected_json_string.json'
        path = join(dirname(__file__), 'data', expected_json_string_file)
        with open(path, 'r') as f:
            expected_json = f.read()
        assert isinstance(csp_cmd_data, str)
        assert expected_json == csp_cmd_data

    def test_build_up_csp_cmd_data_with_empty_receive_addresses(self, example_scan_configuration, csp_func_args):
        valid_scan_config = example_scan_configuration
        attr_name_map = csp_func_args
        receive_addresses_map = ''
        with pytest.raises(KeyError) as exception:
            ElementDeviceData.build_up_csp_cmd_data(valid_scan_config, attr_name_map, receive_addresses_map)
        expected_msg = "Receive addresses must be given. Aborting CSP configuration."
        assert exception.value.args[0] == expected_msg

    def test_build_up_csp_cmd_data_with_empty_scan_configuration(self, csp_func_args,
                                                                 sdp_func_receive_addresses):
        empty_scan_config = {}
        attr_name_map = csp_func_args
        receive_addresses_map = sdp_func_receive_addresses
        with pytest.raises(KeyError) as exception:
            ElementDeviceData.build_up_csp_cmd_data(empty_scan_config, attr_name_map, receive_addresses_map)
        expected_msg = "CSP configuration must be given. Aborting CSP configuration."
        assert exception.value.args[0] == expected_msg

    def test_build_up_csp_cmd_data_with_invalid_scan_configuration(self, example_scan_configuration, csp_func_args,
                                                                   sdp_func_receive_addresses):
        invalid_scan_config = example_scan_configuration.pop("csp")
        attr_name_map = csp_func_args
        receive_addresses_map = sdp_func_receive_addresses
        with pytest.raises(KeyError) as exception:
            ElementDeviceData.build_up_csp_cmd_data(invalid_scan_config, attr_name_map, receive_addresses_map)
        expected_msg = "CSP configuration must be given. Aborting CSP configuration."
        assert exception.value.args[0] == expected_msg

    def test_build_up_dsh_cmd_data_with_valid_scan_configuration(self, example_scan_configuration):
        valid_scan_config = example_scan_configuration
        dsh_cmd_data = ElementDeviceData.build_up_dsh_cmd_data(valid_scan_config, True)
        valid_scan_config.pop("sdp")
        valid_scan_config.pop("csp")
        valid_scan_config.pop("tmc")
        expected_string_dict = json.dumps(valid_scan_config)

        assert isinstance(dsh_cmd_data, tango.DeviceData)
        assert expected_string_dict == dsh_cmd_data.extract()

    def test_build_up_dsh_cmd_data_with_invalid_scan_configuration(self, example_scan_configuration):
        invalid_scan_config = example_scan_configuration.pop("dish")
        with pytest.raises(KeyError) as exception:
            ElementDeviceData.build_up_dsh_cmd_data(invalid_scan_config, False)
        expected_msg = "Dish configuration must be given. Aborting Dish configuration."
        assert exception.value.args[0] == expected_msg
        
@pytest.fixture(scope="function")
def mock_lower_devices():
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

    event_subscription_map = {}
    dish_pointing_state_map = {}

    sdp_subarray1_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args, **kwargs: event_subscription_map.
            update({attr_name: callback}))

    csp_subarray1_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args, **kwargs: event_subscription_map.
            update({attr_name: callback}))

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
        with mock.patch.object(TangoClient, '_get_deviceproxy', return_value=Mock()) as mock_obj:
            tango_client_obj = TangoClient(dut_properties['CspSubarrayLNFQDN'])
            # yield tango_context.device, tango_client_obj

            yield tango_context, csp_subarray1_ln_proxy_mock, csp_subarray1_proxy_mock, sdp_subarray1_ln_proxy_mock, sdp_subarray1_proxy_mock, dish_ln_proxy_mock, csp_subarray1_ln_fqdn, csp_subarray1_fqdn, sdp_subarray1_ln_fqdn, sdp_subarray1_fqdn, dish_ln_prefix, event_subscription_map, dish_pointing_state_map, tango_client_obj

@pytest.fixture(scope="function")
def mock_device_proxy():
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
    
    with fake_tango_system(SubarrayNode, initial_dut_properties=dut_properties) as tango_context:
        with mock.patch.object(TangoClient, '_get_deviceproxy', return_value=Mock()) as mock_obj:
            tango_client_obj = TangoClient(dut_properties['CspSubarrayLNFQDN'])
            yield tango_context.device, tango_client_obj


@pytest.fixture(scope="function")
def mock_lower_devices_group():
    csp_subarray1_ln_fqdn = 'ska_mid/tm_leaf_node/csp_subarray01'
    csp_subarray1_fqdn = 'mid_csp/elt/subarray_01'
    sdp_subarray1_ln_fqdn = 'ska_mid/tm_leaf_node/sdp_subarray01'
    sdp_subarray1_fqdn = 'mid_sdp/elt/subarray_1'
    dish_ln_prefix = 'ska_mid/tm_leaf_node/d'
    dish_group = 'DishLeafNode_Group'

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
    dish_group_mock = Mock()

    proxies_to_mock = {
        csp_subarray1_ln_fqdn: csp_subarray1_ln_proxy_mock,
        csp_subarray1_fqdn: csp_subarray1_proxy_mock,
        sdp_subarray1_ln_fqdn: sdp_subarray1_ln_proxy_mock,
        sdp_subarray1_fqdn: sdp_subarray1_proxy_mock,
        dish_ln_prefix + "0001": dish_ln_proxy_mock

    }

    groups_to_mock = {
        dish_group: dish_group_mock
    }

    event_subscription_map = {}
    dish_pointing_state_map = {}

    sdp_subarray1_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args, **kwargs: event_subscription_map.
            update({attr_name: callback}))

    csp_subarray1_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args, **kwargs: event_subscription_map.
            update({attr_name: callback}))

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
                           proxies_to_mock=proxies_to_mock, group_to_mock=groups_to_mock) as tango_context:
        yield tango_context, csp_subarray1_ln_proxy_mock, csp_subarray1_proxy_mock, sdp_subarray1_ln_proxy_mock, sdp_subarray1_proxy_mock, dish_ln_proxy_mock, csp_subarray1_ln_fqdn, csp_subarray1_fqdn, sdp_subarray1_ln_fqdn, sdp_subarray1_fqdn, dish_ln_prefix, event_subscription_map, dish_pointing_state_map, dish_group_mock


# # Test cases for Attributes
# def test_status(mock_device_proxy):
#     """Test for Status"""
#     device_proxy, tango_client_obj = mock_device_proxy
#     assert device_proxy.Status() == "The device is in OFF state."

'''
def test_health_state():
    """Test for healthState"""
    with fake_tango_system(SubarrayNode) as tango_context:
        assert tango_context.device.healthState == HealthState.OK

def test_activation_time():
    """Test for activationTime"""
    with fake_tango_system(SubarrayNode) as tango_context:
        assert tango_context.device.activationTime == 0.0


def test_version_id():
    """Test for versionId"""
    with fake_tango_system(SubarrayNode) as tango_context:
        assert tango_context.device.versionId == release.version


def test_build_state():
    """Test for buildState"""
    with fake_tango_system(SubarrayNode) as tango_context:
        assert tango_context.device.buildState == ('{},{},{}'.format(release.name,release.version,release.description))


def test_configuration_delay_expected():
    """Test for configurationDelayExpected"""
    with fake_tango_system(SubarrayNode) as tango_context:
        assert tango_context.device.configurationDelayExpected == 0


def test_configuration_progress():
    """Test for configurationProgress"""
    with fake_tango_system(SubarrayNode) as tango_context:
        assert tango_context.device.configurationProgress == 0


def test_scan_id():
    """Test for scanID"""
    with fake_tango_system(SubarrayNode) as tango_context:
        assert tango_context.device.scanID == ""


def test_sb_id():
    """Test for sbID"""
    with fake_tango_system(SubarrayNode) as tango_context:
        assert tango_context.device.sbID == ""

'''
def test_read_activity_message():
    """Test for activityMessage"""
    with fake_tango_system(SubarrayNode) as tango_context:
        assert tango_context.device.activityMessage == const.STR_SA_INIT_SUCCESS

'''
def test_write_activity_message():
    """Test for activityMessage"""
    with fake_tango_system(SubarrayNode) as tango_context:
        tango_context.device.activityMessage = 'test'
        assert tango_context.device.activityMessage == 'test'


def test_configured_capabilities():
    """Test for configuredCapabilities"""
    with fake_tango_system(SubarrayNode) as tango_context:
        assert tango_context.device.configuredCapabilities is None


def test_receptor_id_list():
    """Test for receptorIDList"""
    with fake_tango_system(SubarrayNode) as tango_context:
        assert tango_context.device.receptorIDList is None

'''
# Test cases for Commands
def test_on_command_should_change_subarray_device_state_to_on(mock_device_proxy):
    device_proxy, tango_client_obj = mock_device_proxy
    assert device_proxy.On() == [[ResultCode.OK], ['On command completed OK']]
    assert device_proxy.state() == DevState.ON
    assert device_proxy.obsState == ObsState.EMPTY


def test_off_command_should_change_subarray_device_state_to_off(mock_device_proxy):
    device_proxy, tango_client_obj = mock_device_proxy
    device_proxy.On()
    assert device_proxy.Off() == [[ResultCode.OK], ['Off command completed OK']]
    assert device_proxy.state() == DevState.OFF
    assert device_proxy.obsState == ObsState.EMPTY

def test_assign_resource_should_command_dish_csp_sdp_subarray1_to_assign_valid_resources(mock_device_proxy):
    device_proxy, tango_client_obj = mock_device_proxy
    device_proxy.On()
    assign_input_dict = json.loads(assign_input_str)
    assert device_proxy.AssignResources(assign_input_str) == [[ResultCode.STARTED], ["['0001']"]]
    str_json_arg = json.dumps(assign_input_dict.get("sdp"))
    verify_called_correctly(tango_client_obj.deviceproxy,const.CMD_ASSIGN_RESOURCES,str_json_arg)
    # arg_list = []
    # json_argument = {}
    # dish = {}
    # receptor_list = assign_input_dict["dish"]["receptorIDList"]
    # dish[const.STR_KEY_RECEPTOR_ID_LIST] = receptor_list
    # json_argument[const.STR_KEY_DISH] = dish
    # arg_list.append(json.dumps(json_argument))
    #TODO: Not able to mock the second device, enable one device at a time
    # verify_called_correctly(tango_client_obj.deviceproxy,const.CMD_ASSIGN_RESOURCES,json.dumps(json_argument))
    assert device_proxy.obsState == ObsState.RESOURCING


# def test_assign_resource_is_completed_when_csp_and_sdp_is_idle(mock_device_proxy):
#     device_proxy, tango_client_obj = mock_device_proxy
#     csp_subarray1_ln_fqdn = 'ska_mid/tm_leaf_node/csp_subarray01'
#     csp_subarray1_fqdn = 'mid_csp/elt/subarray_01'
#     sdp_subarray1_ln_fqdn = 'ska_mid/tm_leaf_node/sdp_subarray01'
#     sdp_subarray1_fqdn = 'mid_sdp/elt/subarray_1'
#     dish_ln_prefix = 'ska_mid/tm_leaf_node/d'
#
#     # event_subscription_map = {}
#     # dish_pointing_state_map = {}
#
#     # tango_client_obj.deviceproxy.subscribe_event.side_effect = (
#     #     lambda attr_name, event_type, callback, *args, **kwargs: event_subscription_map.
#     #         update({attr_name: callback}))
#     #
#     # tango_client_obj.deviceproxy.subscribe_event.side_effect = (
#     #     lambda attr_name, event_type, callback, *args, **kwargs: event_subscription_map.
#     #         update({attr_name: callback}))
#
#     csp_subarray1_obsstate_attribute = "cspSubarrayObsState"
#     sdp_subarray1_obsstate_attribute = "sdpSubarrayObsState"
#
#     # device_proxy.On()
#     # device_proxy.AssignResources(assign_input_str)
#         # Mock the behaviour of Csp and SDP subarray's ObsState
#     attribute = 'ObsState'
#     # with mock.patch.object(TangoClient, "get_deviceproxy", return_value = Mock()):
#     #     with mock.patch.object(TangoClient, "subscribe_attribute", side_effect=dummy_subscriber):
#     #         tango_client_obj = TangoClient('ska_mid/tm_leaf_node/csp_subarray01')
#     device_proxy.On()
#     device_proxy.AssignResources(assign_input_str)
#     create_dummy_event_state(csp_subarray1_fqdn, attribute, ObsState.IDLE)
#     create_dummy_event_state(sdp_subarray1_ln_fqdn, attribute, ObsState.IDLE)
#     # with mock.patch.object(TangoClient, "get_deviceproxy", return_value=Mock()):
#     #     with mock.patch.object(TangoClient, "subscribe_attribute", side_effect=dummy_subscriber_for_sdp):
#     #         tango_client_obj = TangoClient('ska_mid/tm_leaf_node/sdp_subarray01')
#     #         device_proxy.On()
#     #         device_proxy.AssignResources(assign_input_str)
#     # with mock.patch.object(TangoClient, "get_deviceproxy", return_value=Mock()):
#     #     with mock.patch.object(TangoClient, "subscribe_attribute", side_effect=dummy_subscriber_sdp):
#     #         tango_client_obj = TangoClient('ska_mid/tm_leaf_node/csp_master')
#         # dummy_event_csp = create_dummy_event_state(tango_client_obj.deviceproxy, csp_subarray1_ln_fqdn,
#         #                                            attribute, ObsState.IDLE)
#
#     # event_subscription_map[csp_subarray1_obsstate_attribute](dummy_event_csp)
#
#     # dummy_event_sdp = create_dummy_event_state(tango_client_obj.deviceproxy, sdp_subarray1_ln_fqdn,
#     #                                            attribute, ObsState.IDLE)
#     # event_subscription_map[sdp_subarray1_obsstate_attribute] = dummy_event_sdp
#     assert device_proxy.obsState == ObsState.IDLE

from ska.base import SKASubarrayStateModel
import logging
@pytest.fixture
def subarray_state_model():
    """
    Yields a new SKASubarrayStateModel for testing
    """
    yield SKASubarrayStateModel(logging.getLogger())

@pytest.fixture
def device_data():
    yield DeviceData()


def test_assign_resource_should_raise_exception_when_called_when_device_state_off():
    with fake_tango_system(SubarrayNode) as tango_context:
        with pytest.raises(tango.DevFailed) as df:
            tango_context.device.AssignResources(assign_input_str)
        assert tango_context.device.State() == DevState.OFF
        assert tango_context.device.obsState == ObsState.EMPTY
        assert "Error executing command AssignResourcesCommand" in str(df.value)


def test_assign_resource_should_raise_exception_when_called_with_invalid_input(mock_device_proxy):
    device_proxy, tango_client_obj = mock_device_proxy
    device_proxy.On()
    with pytest.raises(tango.DevFailed) as df:
        device_proxy.AssignResources(assign_invalid_key)
    assert device_proxy.State() == DevState.ON
    assert device_proxy.obsState == ObsState.FAULT
    assert "Invalid JSON format" in str(df.value)


def test_assign_resource_should_raise_exception_when_csp_subarray_ln_throws_devfailed_exception(mock_device_proxy):
    # # Generate dummy devFailed exception raised by Csp Subarray Leaf Node
    # tango_context, csp_subarray1_ln_proxy_mock, csp_subarray1_proxy_mock, sdp_subarray1_ln_proxy_mock, sdp_subarray1_proxy_mock, dish_ln_proxy_mock, csp_subarray1_ln_fqdn, csp_subarray1_fqdn, sdp_subarray1_ln_fqdn, sdp_subarray1_fqdn, dish_ln_prefix, event_subscription_map, dish_pointing_state_map = mock_lower_devices
    device_proxy, tango_client_obj = mock_device_proxy
    device_proxy.On()
    tango_client_obj.deviceproxy.command_inout.side_effect = raise_devfailed_exception

    with pytest.raises(tango.DevFailed) as df:
        device_proxy.AssignResources(assign_input_str)
    assert device_proxy.State() == DevState.ON
    assert device_proxy.obsState == ObsState.FAULT
    assert "This is error message for devfailed" in str(df.value)


def test_assign_resource_should_raise_exception_when_sdp_subarray_ln_throws_devfailed_exception(mock_device_proxy):
    # tango_context, csp_subarray1_ln_proxy_mock, csp_subarray1_proxy_mock, sdp_subarray1_ln_proxy_mock, sdp_subarray1_proxy_mock, dish_ln_proxy_mock, csp_subarray1_ln_fqdn, csp_subarray1_fqdn, sdp_subarray1_ln_fqdn, sdp_subarray1_fqdn, dish_ln_prefix, event_subscription_map, dish_pointing_state_map = mock_lower_devices
    device_proxy, tango_client_obj = mock_device_proxy

    device_proxy.On()
    tango_client_obj.deviceproxy.command_inout.side_effect = raise_devfailed_exception

    with pytest.raises(tango.DevFailed) as df:
        device_proxy.AssignResources(assign_input_str)
    assert device_proxy.State() == DevState.ON
    assert device_proxy.obsState == ObsState.FAULT
    assert "This is error message for devfailed" in str(df.value)


'''
def test_release_resource_command_subarray(mock_lower_devices):
    tango_context, csp_subarray1_ln_proxy_mock, csp_subarray1_proxy_mock, sdp_subarray1_ln_proxy_mock, sdp_subarray1_proxy_mock, dish_ln_proxy_mock, csp_subarray1_ln_fqdn, csp_subarray1_fqdn, sdp_subarray1_ln_fqdn, sdp_subarray1_fqdn, dish_ln_prefix, event_subscription_map, dish_pointing_state_map = mock_lower_devices
    csp_subarray1_obsstate_attribute = "cspSubarrayObsState"
    sdp_subarray1_obsstate_attribute = "sdpSubarrayObsState"
    tango_context.device.On()
    tango_context.device.AssignResources(assign_input_str)
    attribute = 'ObsState'
    dummy_event_csp = create_dummy_event_state(csp_subarray1_ln_proxy_mock, csp_subarray1_ln_fqdn,
                                               attribute, ObsState.IDLE)
    event_subscription_map[csp_subarray1_obsstate_attribute](dummy_event_csp)
    dummy_event_sdp = create_dummy_event_state(sdp_subarray1_ln_proxy_mock, sdp_subarray1_ln_fqdn,
                                               attribute, ObsState.IDLE)
    event_subscription_map[sdp_subarray1_obsstate_attribute](dummy_event_sdp)
    wait_for(tango_context, ObsState.IDLE)
    assert tango_context.device.obsState == ObsState.IDLE
    tango_context.device.ReleaseAllResources()
    attribute = 'ObsState'
    dummy_event_csp = create_dummy_event_state(csp_subarray1_ln_proxy_mock, csp_subarray1_ln_fqdn,
                                               attribute, ObsState.EMPTY)
    event_subscription_map[csp_subarray1_obsstate_attribute](dummy_event_csp)

    dummy_event_sdp = create_dummy_event_state(sdp_subarray1_ln_proxy_mock, sdp_subarray1_ln_fqdn,
                                               attribute, ObsState.EMPTY)
    event_subscription_map[sdp_subarray1_obsstate_attribute](dummy_event_sdp)
    wait_for(tango_context, ObsState.EMPTY)
    sdp_subarray1_ln_proxy_mock.command_inout.assert_called_with(const.CMD_RELEASE_ALL_RESOURCES)
    csp_subarray1_ln_proxy_mock.command_inout.assert_called_with(const.CMD_RELEASE_ALL_RESOURCES)
    assert tango_context.device.State() == DevState.ON
    assert tango_context.device.obsState == ObsState.EMPTY


def test_release_resource_should_raise_exception_when_called_before_assign_resource(mock_lower_devices):
    tango_context, csp_subarray1_ln_proxy_mock, csp_subarray1_proxy_mock = mock_lower_devices[:3]
    tango_context.device.On()
    with pytest.raises(tango.DevFailed) as df:
        tango_context.device.ReleaseAllResources()
    assert tango_context.device.State() == DevState.ON
    assert tango_context.device.obsState == ObsState.EMPTY
    assert "Error executing command ReleaseAllResourcesCommand" in str(df.value)


class ProxyContext():
    def __init__(self,
                 proxy_mock: Mock,
                 map: Dict[str, Callable],
                 fqdn: str = '',
                 *att_maps: Tuple[str, str]) -> None:
        self.proxy_mock = proxy_mock
        self.map = map
        self.fqdn = fqdn
        self._att_map = {}
        for att_map in att_maps:
            event_attr, device_attr = att_map
            self._att_map[event_attr] = device_attr

    def generate_event(self, attr: str, val: Any):
        event = create_dummy_event_state(self.proxy_mock, self.fqdn, attr, val)
        device_attr = self._att_map.get(attr, attr)
        self.map[device_attr](event)


class DishProxyContext(ProxyContext):

    def __init__(self,
                 proxy_mock: Mock,
                 map: Dict[str, Callable],
                 name: str,
                 fqdn: str = '',
                 *att_maps: Tuple[str, str]) -> None:
        self.name = name
        super(DishProxyContext, self).__init__(proxy_mock, map, fqdn, *att_maps)


class SubarrayProxyContext(ProxyContext):

    def __init__(self,
                 proxy_mock: Mock,
                 map: Dict[str, Callable],
                 fqdn: str = '',
                 *att_maps: Tuple[str, str]) -> None:
        super(SubarrayProxyContext, self).__init__(proxy_mock, map, fqdn, *att_maps)


class SubarrayContext(NamedTuple):
    # sdp_subarray1: SubarrayProxyContext
    # csp_subarray1: SubarrayProxyContext
    # event_subscription_map: Any
    # tango_context: Any
    # sdp_subarray1_ln: SubarrayProxyContext
    csp_subarray1_ln: SubarrayProxyContext
    # dish_ln: DishProxyContext


@pytest.fixture()
def empty_subarray_context(mock_device_proxy) -> SubarrayContext:
    # tango_context, csp_subarray1_ln_proxy_mock, csp_subarray1_proxy_mock, sdp_subarray1_ln_proxy_mock, sdp_subarray1_proxy_mock, dish_ln_proxy_mock, csp_subarray1_ln_fqdn, csp_subarray1_fqdn, sdp_subarray1_ln_fqdn, sdp_subarray1_fqdn, dish_ln_prefix, event_subscription_map, dish_pointing_state_map = mock_lower_devices
    device_proxy, tango_client_obj = mock_device_proxy
    csp_subarray1_ln_fqdn = 'ska_mid/tm_leaf_node/csp_subarray01'
    event_subscription_map = {}
    # sdp_obs_state_mapping = ("ObsState", "sdpSubarrayObsState")
    csp_obs_state_mapping = ("ObsState", "cspSubarrayObsState")
    # dish_pointing_state_mapping = ("PointingState", "dishPointingState")
    # csp_subarray1 = SubarrayProxyContext(
    #     csp_subarray1_proxy_mock,
    #     event_subscription_map,
    #     csp_subarray1_fqdn,
    #     csp_obs_state_mapping)
    # sdp_subarray1 = SubarrayProxyContext(
    #     sdp_subarray1_proxy_mock,
    #     event_subscription_map,
    #     sdp_subarray1_fqdn,
    #     sdp_obs_state_mapping)
    csp_subarray1_ln = SubarrayProxyContext(
        Mock(),
        event_subscription_map,
        csp_subarray1_ln_fqdn,
        csp_obs_state_mapping)
    # sdp_subarray1_ln = SubarrayProxyContext(
    #     sdp_subarray1_ln_proxy_mock,
    #     event_subscription_map,
    #     sdp_subarray1_ln_fqdn,
    #     sdp_obs_state_mapping)
    # dish_ln = DishProxyContext(
    #     dish_ln_proxy_mock,
    #     dish_pointing_state_map,
    #     (dish_ln_prefix + "0001"),
    #     '',
    #     dish_pointing_state_mapping)
    context = SubarrayContext(
        # sdp_subarray1,
        # csp_subarray1,
        # event_subscription_map,
        # tango_context,
        # sdp_subarray1_ln,
        csp_subarray1_ln
        # dish_ln)
    context.device_proxy.device.On()
    return context


@pytest.fixture()
def idle_subarray_context(empty_subarray_context: SubarrayContext) -> SubarrayContext:
    c = empty_subarray_context
    c.tango_context.device.AssignResources(assign_input_str)
    # Mock the behaviour of Csp asnd SDP subarray ObsState
    c.csp_subarray1_ln.generate_event('ObsState', ObsState.IDLE)
    c.sdp_subarray1_ln.generate_event('ObsState', ObsState.IDLE)
    wait_for(c.tango_context, ObsState.IDLE)
    return c

'''
def assert_that_log_contains(name: str, caplog):
    patterns = [f'^Transaction.*(?<=Enter\[{name}\])', f'^Transaction.*(?<=Exit\[{name}\])']
    for pattern in patterns:
        found = False
        for message in caplog.messages:
            if re.match(pattern, message):
                found = True
                break
        if not found:
            raise AssertionError(f'pattern ({pattern}) not found in expected log messages')


# def test_log_transaction_with_assign(empty_subarray_context: SubarrayContext, caplog):
#     c = empty_subarray_context
#     c.tango_context.device.AssignResources(assign_input_str)
#     assert_that_log_contains('assign', caplog)

def test_log_transaction_with_assign(mock_device_proxy, caplog):
    device_proxy, tango_client_obj = mock_device_proxy
    device_proxy.On()
    assign_input_dict = json.loads(assign_input_str)
    device_proxy.AssignResources(assign_input_str)
    assert_that_log_contains('assign', caplog)


# def test_log_transaction_with_config(idle_subarray_context: SubarrayContext, caplog):
#     c = idle_subarray_context
#     c.sdp_subarray1.generate_event("receiveAddresses", receive_addresses_map)
#     c.tango_context.device.Configure(configure_str)
#     assert_that_log_contains('configure', caplog)

def test_log_transaction_with_config(mock_device_proxy, subarray_state_model, caplog):
    device_proxy, tango_client_obj = mock_device_proxy
    device_data = DeviceData.get_instance()
    configure_cmd = ConfigureCommand(device_data, subarray_state_model)
    attribute = "receiveAddresses"
    with mock.patch.object(TangoClient, "_get_deviceproxy", return_value=Mock()):
        with mock.patch.object(TangoClient, "subscribe_attribute", side_effect=dummy_subscriber_receive_addresses):
            tango_client_obj = TangoClient('ska_mid/tm_leaf_node/sdp_subarray01')
            device_proxy.On()
    subarray_state_model._straight_to_state(DevState.ON, None, ObsState.IDLE)
    configure_cmd.do(configure_str)
    # c.sdp_subarray1.generate_event("receiveAddresses", receive_addresses_map)
    # c.tango_context.device.Configure(configure_str)
    assert_that_log_contains('configure', caplog)



@pytest.fixture()
def mock_transaction_id():
    with mock.patch('subarraynode.transaction_id.transaction') as transaction_mock:
        dummy_id = 'dummy id'
        context_manager_mock = transaction_mock.return_value
        context_manager_mock.__enter__.return_value = 'dummy id'
        yield json.dumps({'transaction_id': dummy_id})


def test_transaction_id_injected_in_config_command(mock_device_proxy, subarray_state_model, mock_transaction_id):
    device_proxy, tango_client_obj = mock_device_proxy
    device_data = DeviceData.get_instance()
    configure_cmd = ConfigureCommand(device_data, subarray_state_model)
    attribute = "receiveAddresses"
    with mock.patch.object(TangoClient, "_get_deviceproxy", return_value=Mock()):
        with mock.patch.object(TangoClient, "subscribe_attribute", side_effect=dummy_subscriber_receive_addresses):
            tango_client_obj = TangoClient('ska_mid/tm_leaf_node/sdp_subarray01')
            # valid_scan_config = example_scan_configuration #json.loads(scan_config_str)
            # attr_name_map = csp_func_args
            # receive_addresses_map = sdp_func_receive_addresses
            # csp_cmd_data = ElementDeviceData.build_up_csp_cmd_data(valid_scan_config, attr_name_map, receive_addresses_map)
            device_proxy.On()
            # device_proxy.Confiure()
            subarray_state_model._straight_to_state(DevState.ON, None, ObsState.IDLE)
            configure_cmd.do(configure_str)
    
    # c = idle_subarray_context
    # c.sdp_subarray1.generate_event("receiveAddresses", receive_addresses_map)
    # c.tango_context.device.Configure(configure_str)
            verify_called_correctly(tango_client_obj.deviceproxy, const.CMD_CONFIGURE, mock_transaction_id)
    # verify_called_correctly(c.csp_subarray1_ln.proxy_mock, const.CMD_CONFIGURE, mock_transaction_id)


def test_transaction_id_injected_in_assign_command(mock_device_proxy, mock_transaction_id):
    device_proxy, tango_client_obj = mock_device_proxy
    device_proxy.On()
    assign_input_dict = json.loads(assign_input_str)
    device_proxy.AssignResources(assign_input_str)
    # c = empty_subarray_context
    # c.tango_context.device.AssignResources(assign_input_str)
    # verify_called_correctly(c.sdp_subarray1_ln.proxy_mock,const.CMD_ASSIGN_RESOURCES,mock_transaction_id)
    verify_called_correctly(tango_client_obj.deviceproxy,const.CMD_ASSIGN_RESOURCES,mock_transaction_id)

def assert_data_is_subsisted_by(data:Dict,sub:Dict):
    for key,val in sub.items():
        assert(key in data.keys())
        assert(data[key] == val)


def verify_called_correctly(agent: Mock, command, data):
    agent.command_inout.assert_called_with(command, mock.ANY)
    args = json.loads(agent.command_inout.call_args.args[1])
    subsisted_data = json.loads(data)
    assert_data_is_subsisted_by(args, subsisted_data)


def test_configure_command(device_data, subarray_state_model, mock_device_proxy):
    device_proxy, tango_client_obj = mock_device_proxy
    configure_cmd = ConfigureCommand(device_data, subarray_state_model)
    attribute = "receiveAddresses"
    with mock.patch.object(TangoClient, "_get_deviceproxy", return_value=Mock()):
        with mock.patch.object(TangoClient, "subscribe_attribute", side_effect=dummy_subscriber_receive_addresses):
            tango_client_obj = TangoClient('ska_mid/tm_leaf_node/sdp_subarray01')
            device_proxy.On()
    subarray_state_model._straight_to_state(DevState.ON, None, ObsState.IDLE)
    assert configure_cmd.do(configure_str) == (ResultCode.STARTED, "Configure command invoked")


def dummy_subscriber_receive_addresses(attribute, callback_method):
    fake_event = Mock()
    fake_event.err = False
    fake_event.attr_name = f"ska_mid/tm_leaf_node/sdp_subarray01/{attribute}"
    fake_event.attr_value.value =  receive_addresses_map
    print("Inside dummy subscriber for receive add:::::::::::::::::::::::::::::::::::::::::::::::::::")
    print( fake_event.attr_value.value )
    callback_method(fake_event)
    return 10


def test_configure_command_subarray_with_invalid_configure_input(device_data, subarray_state_model, mock_device_proxy):
    device_proxy, tango_client_obj = mock_device_proxy
    configure_cmd = ConfigureCommand(device_data, subarray_state_model)
    attribute = "receiveAddresses"
    with mock.patch.object(TangoClient, "_get_deviceproxy", return_value=Mock()):
        with mock.patch.object(TangoClient, "subscribe_attribute", side_effect=dummy_subscriber_receive_addresses):
            tango_client_obj = TangoClient('ska_mid/tm_leaf_node/sdp_subarray01')
            device_proxy.On()
    subarray_state_model._straight_to_state(DevState.ON, None, ObsState.IDLE)
    with pytest.raises(tango.DevFailed) as df:
        configure_cmd.do(invalid_conf_input)
    device_data = DeviceData.get_instance()
    assert device_data._read_activity_message in str(df.value)
    # assert configure_cmd.do(configure_str) == (ResultCode.STARTED, "Configure command invoked")

def test_scan_command(device_data, subarray_state_model, mock_device_proxy):
    _ , _ = mock_device_proxy
    scan_cmd = ScanCommand(device_data, subarray_state_model)
    assert scan_cmd.do(configure_str) == (ResultCode.STARTED, 'Scan command is executed successfully.')


def test_scan_raise_devfailed(device_data, subarray_state_model, mock_device_proxy):
    device_proxy, tango_client_obj = mock_device_proxy
    tango_client_obj.deviceproxy.command_inout.side_effect = raise_devfailed_exception
    scan_cmd = ScanCommand(device_data, subarray_state_model)
    with pytest.raises(tango.DevFailed) as df:
        scan_cmd.do(configure_str)
    assert "This is error message for devfailed" in str(df.value)


def test_end_scan_command(device_data, subarray_state_model, mock_device_proxy):
    _ , _ = mock_device_proxy
    end_scan_cmd = EndScanCommand(device_data, subarray_state_model)
    assert end_scan_cmd.do() == (ResultCode.OK, const.STR_END_SCAN_SUCCESS)


def test_end_scan_raise_devfailed(device_data, subarray_state_model, mock_device_proxy):
    device_proxy, tango_client_obj = mock_device_proxy
    tango_client_obj.deviceproxy.command_inout.side_effect = raise_devfailed_exception
    end_scan_cmd = EndScanCommand(device_data, subarray_state_model)
    with pytest.raises(tango.DevFailed) as df:
        end_scan_cmd.do()
    assert "This is error message for devfailed" in str(df.value)


def test_end_command(device_data, subarray_state_model, mock_device_proxy):
    device_proxy , _ = mock_device_proxy
    end_cmd = EndCommand(device_data, subarray_state_model)
    assert end_cmd.do() == (ResultCode.OK, const.STR_ENDSB_SUCCESS)


def test_end_raise_devfailed(device_data, subarray_state_model, mock_device_proxy):
    device_proxy, tango_client_obj = mock_device_proxy
    tango_client_obj.deviceproxy.command_inout.side_effect = raise_devfailed_exception
    end_cmd = EndCommand(device_data, subarray_state_model)
    with pytest.raises(tango.DevFailed) as df:
        end_cmd.do()
    assert "This is error message for devfailed" in str(df.value)


def test_abort_command(device_data, subarray_state_model, mock_device_proxy):
    _ , _ = mock_device_proxy
    abort_cmd = AbortCommand(device_data, subarray_state_model)
    assert abort_cmd.do() == (ResultCode.STARTED, const.STR_ABORT_SUCCESS)


def test_abort_raise_devfailed(device_data, subarray_state_model, mock_device_proxy):
    device_proxy, tango_client_obj = mock_device_proxy
    tango_client_obj.deviceproxy.command_inout.side_effect = raise_devfailed_exception
    abort_cmd = AbortCommand(device_data, subarray_state_model)
    with pytest.raises(tango.DevFailed) as df:
        abort_cmd.do()
    assert "This is error message for devfailed" in str(df.value)


def test_obsreset_command(device_data, subarray_state_model, mock_device_proxy):
    # _ , _ = mock_device_proxy
    obsreset_cmd = ObsResetCommand(device_data, subarray_state_model)
    assert obsreset_cmd.do() == (ResultCode.STARTED, const.STR_OBSRESET_SUCCESS)


def test_obsreset_raise_devfailed(device_data, subarray_state_model, mock_device_proxy):
    device_proxy, tango_client_obj = mock_device_proxy
    tango_client_obj.deviceproxy.command_inout.side_effect = raise_devfailed_exception
    obsreset_cmd = ObsResetCommand(device_data, subarray_state_model)
    with pytest.raises(tango.DevFailed) as df:
        obsreset_cmd.do()
    assert "This is error message for devfailed" in str(df.value)


def test_restart_command(device_data, subarray_state_model, mock_device_proxy):
    restart_cmd = RestartCommand(device_data, subarray_state_model)
    assert restart_cmd.do() == (ResultCode.STARTED, const.STR_RESTART_SUCCESS)


def test_restart_raise_devfailed(device_data, subarray_state_model, mock_device_proxy):
    device_proxy, tango_client_obj = mock_device_proxy
    tango_client_obj.deviceproxy.command_inout.side_effect = raise_devfailed_exception
    restart_cmd = RestartCommand(device_data, subarray_state_model)
    with pytest.raises(tango.DevFailed) as df:
        restart_cmd.do()
    assert "This is error message for devfailed" in str(df.value)


def test_releaseallresources_command(device_data, subarray_state_model, mock_device_proxy):
    device_proxy, _ = mock_device_proxy
    device_proxy.On()
    device_proxy.AssignResources(assign_input_str)
    release_resources_cmd = ReleaseAllResourcesCommand(device_data, subarray_state_model)
    assert release_resources_cmd.do() == (ResultCode.STARTED, '[]')


def test_release_resource_should_raise_exception_when_called_before_assign_resource(device_data, subarray_state_model, mock_device_proxy):
    device_proxy, tango_client_obj = mock_device_proxy
    release_resources_cmd = ReleaseAllResourcesCommand(device_data, subarray_state_model)
    with pytest.raises(tango.DevFailed) as df:
        release_resources_cmd.do()
    assert const.ERR_RELEASE_RES_CMD in str(df.value)

def test_track_command_subarray(mock_device_proxy):
    device_proxy, tango_client_obj = mock_device_proxy
    device_proxy.On()
    device_proxy.AssignResources(assign_input_str)
    track_input = "radec|2:31:50.91|89:15:51.4"
    track_cmd = TrackCommand(device_data, subarray_state_model)
    assert track_cmd.do(track_input) == (ResultCode.OK, const.STR_TRACK_CMD_INVOKED_SA)

def create_dummy_event_healthstate_with_error(attribute, callback_method):
    fake_event = Mock()
    fake_event.err = True
    fake_event.attr_name = f"ska_mid/tm_leaf_node/csp_subarray01/{attribute}"
    fake_event.attr_value.value = HealthState.FAILED
    callback_method(fake_event)
    return 10

def dummy_subscriber(attribute, callback_method):
    fake_event = Mock()
    fake_event.err = False
    fake_event.attr_name = f"ska_mid/tm_leaf_node/csp_subarray01/{attribute}"
    fake_event.attr_value.value =  HealthState.FAILED
    print("Inside dummy subscriber ...........................")
    print( fake_event.attr_value.value )

    callback_method(fake_event)
    return 10


@pytest.fixture(
    scope = "function",
    params=[
        # HealthState.DEGRADED,
        # HealthState.UNKNOWN, //NOTE: Need to check for creating mock for more than one healthstate
        HealthState.FAILED,
    ])
def csp_health_state(request):
    csp_health_state = request.param
    return csp_health_state

# Test Health State Callback
def test_subarray_health_state_when_csubarray1_ln_is_in_health_state_after_start(mock_device_proxy, csp_health_state):
    device_proxy, tango_client_obj = mock_device_proxy
    device_data = DeviceData.get_instance()
    with mock.patch.object(TangoClient, '_get_deviceproxy', return_value=Mock()) as mock_obj:
        with mock.patch.object(TangoClient, "subscribe_attribute", side_effect=dummy_subscriber):
            device_proxy.On()
    assert device_data.health_state == csp_health_state

def test_subarray_health_state_is_ok_when_csp_and_sdp_subarray1_ln_is_ok_after_start(mock_device_proxy):
    device_proxy, tango_client_obj = mock_device_proxy
    with mock.patch.object(TangoClient, '_get_deviceproxy', return_value=Mock()) as mock_obj:
        with mock.patch.object(TangoClient, "subscribe_attribute", side_effect=dummy_subscriber):
            device_proxy.On()

    assert device_proxy.healthState == HealthState.OK

def test_subarray_health_state_with_error_event(mock_device_proxy):
    device_proxy, tango_client_obj = mock_device_proxy
    device_data = DeviceData.get_instance()
    with mock.patch.object(TangoClient, '_get_deviceproxy', return_value=Mock()) as mock_obj:
        with mock.patch.object(TangoClient, "subscribe_attribute", side_effect=create_dummy_event_healthstate_with_error):
            device_proxy.On()
    assert const.ERR_SUBSR_SA_HEALTH_STATE in device_proxy.activityMessage


def test_subarray_health_state_event_to_raise_devfailed_exception_for_csp_subarray_ln(mock_device_proxy):
    device_proxy, tango_client_obj = mock_device_proxy
    tango_client_obj.deviceproxy.command_inout.side_effect = raise_devfailed_exception
    with pytest.raises(tango.DevFailed) as df:
        device_proxy.On()
    assert device_proxy.State() == DevState.FAULT
    assert "This is error message for devfailed" in str(df.value)

'''
def test_configure_command_obsstate_changes_from_configuring_to_ready(mock_lower_devices):
    tango_context, csp_subarray1_ln_proxy_mock, csp_subarray1_proxy_mock, sdp_subarray1_ln_proxy_mock, sdp_subarray1_proxy_mock, dish_ln_proxy_mock, csp_subarray1_ln_fqdn, csp_subarray1_fqdn, sdp_subarray1_ln_fqdn, sdp_subarray1_fqdn, dish_ln_prefix, event_subscription_map, dish_pointing_state_map = mock_lower_devices
    csp_subarray1_obsstate_attribute = "cspSubarrayObsState"
    sdp_subarray1_obsstate_attribute = "sdpSubarrayObsState"
    dish_pointing_state_attribute = "dishPointingState"
    tango_context.device.On()
    tango_context.device.AssignResources(assign_input_str)
    # Mock the behaviour of Csp and SDP subarray ObsState
    attribute = 'ObsState'
    dummy_event_csp = create_dummy_event_state(csp_subarray1_ln_proxy_mock, csp_subarray1_ln_fqdn,
                                               attribute, ObsState.IDLE)
    event_subscription_map[csp_subarray1_obsstate_attribute](dummy_event_csp)

    dummy_event_sdp = create_dummy_event_state(sdp_subarray1_ln_proxy_mock, sdp_subarray1_ln_fqdn,
                                               attribute, ObsState.IDLE)
    event_subscription_map[sdp_subarray1_obsstate_attribute](dummy_event_sdp)
    wait_for(tango_context, ObsState.IDLE)
    assert tango_context.device.obsState == ObsState.IDLE

    attribute = "receiveAddresses"
    dummy_event = create_dummy_event_state(sdp_subarray1_proxy_mock, sdp_subarray1_fqdn, attribute,
                                           receive_addresses_map)
    event_subscription_map[attribute](dummy_event)
    assert tango_context.device.Configure(configure_str) == [[ResultCode.STARTED], ['Configure command invoked']]
    verify_called_correctly(sdp_subarray1_ln_proxy_mock, const.CMD_CONFIGURE, sdp_conf_str)
    verify_called_correctly(csp_subarray1_ln_proxy_mock, const.CMD_CONFIGURE, csp_conf_str)
    assert tango_context.device.obsState == ObsState.CONFIGURING

    # Mock the behaviour of Csp and SDP subarray ObsState
    attribute = 'ObsState'
    dummy_event_csp = create_dummy_event_state(csp_subarray1_ln_proxy_mock, csp_subarray1_ln_fqdn,
                                               attribute, ObsState.READY)
    event_subscription_map[csp_subarray1_obsstate_attribute](dummy_event_csp)

    dummy_event_sdp = create_dummy_event_state(sdp_subarray1_ln_proxy_mock, sdp_subarray1_ln_fqdn,
                                               attribute, ObsState.READY)
    event_subscription_map[sdp_subarray1_obsstate_attribute](dummy_event_sdp)

    attribute = 'PointingState'
    dummy_event_dish = create_dummy_event_state(dish_ln_proxy_mock, dish_ln_prefix + "0001", attribute,
                                                PointingState.TRACK)
    dish_pointing_state_map[dish_pointing_state_attribute](dummy_event_dish)
    wait_for(tango_context, ObsState.READY)
    assert tango_context.device.obsState == ObsState.READY


def test_configure_command_subarray_with_invalid_configure_input(mock_lower_devices):
    tango_context, csp_subarray1_ln_proxy_mock, csp_subarray1_proxy_mock, sdp_subarray1_ln_proxy_mock, sdp_subarray1_proxy_mock, dish_ln_proxy_mock, csp_subarray1_ln_fqdn, csp_subarray1_fqdn, sdp_subarray1_ln_fqdn, sdp_subarray1_fqdn, dish_ln_prefix, event_subscription_map, dish_pointing_state_map = mock_lower_devices
    csp_subarray1_obsstate_attribute = "cspSubarrayObsState"
    sdp_subarray1_obsstate_attribute = "sdpSubarrayObsState"
    tango_context.device.On()
    tango_context.device.AssignResources(assign_input_str)
    attribute = 'ObsState'
    dummy_event_csp = create_dummy_event_state(csp_subarray1_ln_proxy_mock, csp_subarray1_ln_fqdn,
                                               attribute, ObsState.IDLE)
    event_subscription_map[csp_subarray1_obsstate_attribute](dummy_event_csp)

    dummy_event_sdp = create_dummy_event_state(sdp_subarray1_ln_proxy_mock, sdp_subarray1_ln_fqdn,
                                               attribute, ObsState.IDLE)
    event_subscription_map[sdp_subarray1_obsstate_attribute](dummy_event_sdp)
    with pytest.raises(tango.DevFailed) as df:
        tango_context.device.Configure(invalid_conf_input)
    assert tango_context.device.obsState == ObsState.FAULT


def test_start_scan_should_command_subarray_to_start_scan_when_it_is_ready(mock_lower_devices):
    tango_context, csp_subarray1_ln_proxy_mock, csp_subarray1_proxy_mock, sdp_subarray1_ln_proxy_mock, sdp_subarray1_proxy_mock, dish_ln_proxy_mock, csp_subarray1_ln_fqdn, csp_subarray1_fqdn, sdp_subarray1_ln_fqdn, sdp_subarray1_fqdn, dish_ln_prefix, event_subscription_map, dish_pointing_state_map = mock_lower_devices
    csp_subarray1_obsstate_attribute = "cspSubarrayObsState"
    sdp_subarray1_obsstate_attribute = "sdpSubarrayObsState"
    dish_pointing_state_attribute = "dishPointingState"
    tango_context.device.On()
    # Assign Resources to the Subarray which change the obsState to RESOURCING
    tango_context.device.AssignResources(assign_input_str)
    # Mock the behaviour of ObsState of Csp and Sdp Subarray to change the ObsState to IDLE
    # Marking Assign Resources Command Completed
    attribute = 'ObsState'
    dummy_event_csp = create_dummy_event_state(csp_subarray1_ln_proxy_mock, csp_subarray1_ln_fqdn,
                                               attribute, ObsState.IDLE)
    event_subscription_map[csp_subarray1_obsstate_attribute](dummy_event_csp)

    dummy_event_sdp = create_dummy_event_state(sdp_subarray1_ln_proxy_mock, sdp_subarray1_ln_fqdn,
                                               attribute, ObsState.IDLE)
    event_subscription_map[sdp_subarray1_obsstate_attribute](dummy_event_sdp)
    # Check the ObsState changes to IDLE
    wait_for(tango_context, ObsState.IDLE)
    assert tango_context.device.obsState == ObsState.IDLE

    # Mock and update the receive address value received from ska-telescope model library.
    attribute = "receiveAddresses"
    dummy_event = create_dummy_event_state(sdp_subarray1_proxy_mock, sdp_subarray1_fqdn, attribute,
                                           receive_addresses_map)
    event_subscription_map[attribute](dummy_event)

    # Confiure subarray with correct configuration which will change the obsState to CONFIGURING
    tango_context.device.Configure(configure_str)
    # Mock the behaviour of ObsState of Csp and Sdp Subarray to change the ObsState to READY
    # Marking Configure Command Completed
    attribute = 'ObsState'
    dummy_event_csp = create_dummy_event_state(csp_subarray1_ln_proxy_mock, csp_subarray1_ln_fqdn,
                                               attribute, ObsState.READY)
    event_subscription_map[csp_subarray1_obsstate_attribute](dummy_event_csp)

    dummy_event_sdp = create_dummy_event_state(sdp_subarray1_ln_proxy_mock, sdp_subarray1_ln_fqdn,
                                               attribute, ObsState.READY)
    event_subscription_map[sdp_subarray1_obsstate_attribute](dummy_event_sdp)

    # Mock the behaviour of DishLeafNode PointingState change the PointingState to TRACK
    attribute = 'PointingState'
    dummy_event_dish = create_dummy_event_state(dish_ln_proxy_mock, dish_ln_prefix + "0001", attribute,
                                                PointingState.TRACK)
    dish_pointing_state_map[dish_pointing_state_attribute](dummy_event_dish)
    # Check the ObsState changes to READY
    wait_for(tango_context, ObsState.READY)
    assert tango_context.device.obsState == ObsState.READY

    # Now subarrayNode obsState is READY we can send Scan() command which will change the
    # obsState to Scanning
    assert tango_context.device.Scan(scan_input_str) == [[ResultCode.STARTED],
                                                         ['Scan command is executed successfully.']]
    # Check the ObsState changes to SCANNING
    wait_for(tango_context, ObsState.SCANNING)
    sdp_subarray1_ln_proxy_mock.command_inout.assert_called_with(const.CMD_SCAN, scan_input_str)
    csp_subarray1_ln_proxy_mock.command_inout.assert_called_with(const.CMD_START_SCAN, [scan_input_str])
    assert tango_context.device.obsState == ObsState.SCANNING


def test_start_scan_should_raise_devfailed_exception(mock_lower_devices):
    tango_context, csp_subarray1_ln_proxy_mock, csp_subarray1_proxy_mock, sdp_subarray1_ln_proxy_mock, sdp_subarray1_proxy_mock, dish_ln_proxy_mock, csp_subarray1_ln_fqdn, csp_subarray1_fqdn, sdp_subarray1_ln_fqdn, sdp_subarray1_fqdn, dish_ln_prefix, event_subscription_map, dish_pointing_state_map = mock_lower_devices
    csp_subarray1_obsstate_attribute = "cspSubarrayObsState"
    sdp_subarray1_obsstate_attribute = "sdpSubarrayObsState"
    dish_pointing_state_attribute = "dishPointingState"
    # Send On() command to SubarrayNode to change the DeviceState to On
    tango_context.device.On()
    # Assign Resources to the Subarray which change the obsState to RESOURCING
    tango_context.device.AssignResources(assign_input_str)
    # Mock the behaviour of ObsState of Csp and Sdp Subarray to change the ObsState to IDLE
    # Marking Assign Resources Command Completed
    attribute = 'ObsState'
    dummy_event_csp = create_dummy_event_state(csp_subarray1_ln_proxy_mock, csp_subarray1_ln_fqdn,
                                               attribute, ObsState.IDLE)
    event_subscription_map[csp_subarray1_obsstate_attribute](dummy_event_csp)

    dummy_event_sdp = create_dummy_event_state(sdp_subarray1_ln_proxy_mock, sdp_subarray1_ln_fqdn,
                                               attribute, ObsState.IDLE)
    event_subscription_map[sdp_subarray1_obsstate_attribute](dummy_event_sdp)
    # Check the ObsState changes to IDLE
    wait_for(tango_context, ObsState.IDLE)
    assert tango_context.device.obsState == ObsState.IDLE

    # Mock and update the receive address value received from ska-telescope model library.
    attribute = "receiveAddresses"
    dummy_event = create_dummy_event_state(sdp_subarray1_proxy_mock, sdp_subarray1_fqdn, attribute,
                                           receive_addresses_map)
    event_subscription_map[attribute](dummy_event)

    # Confiure subarray with correct configuration which will change the obsState to CONFIGURING
    tango_context.device.Configure(configure_str)
    # Mock the behaviour of ObsState of Csp and Sdp Subarray to change the ObsState to READY
    # Marking Configure Command Completed
    attribute = 'ObsState'
    dummy_event_csp = create_dummy_event_state(csp_subarray1_ln_proxy_mock, csp_subarray1_ln_fqdn,
                                               attribute, ObsState.READY)
    event_subscription_map[csp_subarray1_obsstate_attribute](dummy_event_csp)

    dummy_event_sdp = create_dummy_event_state(sdp_subarray1_ln_proxy_mock, sdp_subarray1_ln_fqdn,
                                               attribute, ObsState.READY)
    event_subscription_map[sdp_subarray1_obsstate_attribute](dummy_event_sdp)

    # Mock the behaviour of DishLeafNode PointingState change the PointingState to TRACK
    attribute = 'PointingState'
    dummy_event_dish = create_dummy_event_state(dish_ln_proxy_mock, dish_ln_prefix + "0001", attribute,
                                                PointingState.TRACK)
    dish_pointing_state_map[dish_pointing_state_attribute](dummy_event_dish)
    # Check the ObsState changes to READY
    wait_for(tango_context, ObsState.READY)
    assert tango_context.device.obsState == ObsState.READY

    # Now subarrayNode obsState is READY we can send Scan() command which will change the
    # obsState to Scanning
    csp_subarray1_ln_proxy_mock.command_inout.side_effect = raise_devfailed_exception

    with pytest.raises(tango.DevFailed) as df:
        tango_context.device.Scan(scan_input_str)
    assert tango_context.device.obsState == ObsState.FAULT
    assert "This is error message for devfailed" in str(df.value)


def test_end_scan_should_command_subarray_to_end_scan_when_it_is_scanning(mock_lower_devices):
    tango_context, csp_subarray1_ln_proxy_mock, csp_subarray1_proxy_mock, sdp_subarray1_ln_proxy_mock, sdp_subarray1_proxy_mock, dish_ln_proxy_mock, csp_subarray1_ln_fqdn, csp_subarray1_fqdn, sdp_subarray1_ln_fqdn, sdp_subarray1_fqdn, dish_ln_prefix, event_subscription_map, dish_pointing_state_map = mock_lower_devices
    csp_subarray1_obsstate_attribute = "cspSubarrayObsState"
    sdp_subarray1_obsstate_attribute = "sdpSubarrayObsState"
    dish_pointing_state_attribute = "dishPointingState"
    tango_context.device.On()
    tango_context.device.AssignResources(assign_input_str)
    attribute = 'ObsState'
    dummy_event_csp = create_dummy_event_state(csp_subarray1_ln_proxy_mock, csp_subarray1_ln_fqdn,
                                               attribute, ObsState.IDLE)
    event_subscription_map[csp_subarray1_obsstate_attribute](dummy_event_csp)

    dummy_event_sdp = create_dummy_event_state(sdp_subarray1_ln_proxy_mock, sdp_subarray1_ln_fqdn,
                                               attribute, ObsState.IDLE)
    event_subscription_map[sdp_subarray1_obsstate_attribute](dummy_event_sdp)

    wait_for(tango_context, ObsState.IDLE)
    assert tango_context.device.obsState == ObsState.IDLE

    attribute = "receiveAddresses"
    dummy_event = create_dummy_event_state(sdp_subarray1_proxy_mock, sdp_subarray1_fqdn, attribute,
                                           receive_addresses_map)
    event_subscription_map[attribute](dummy_event)

    tango_context.device.Configure(configure_str)
    attribute = 'ObsState'
    dummy_event_csp = create_dummy_event_state(csp_subarray1_ln_proxy_mock, csp_subarray1_ln_fqdn,
                                               attribute, ObsState.READY)
    event_subscription_map[csp_subarray1_obsstate_attribute](dummy_event_csp)

    dummy_event_sdp = create_dummy_event_state(sdp_subarray1_ln_proxy_mock, sdp_subarray1_ln_fqdn,
                                               attribute, ObsState.READY)
    event_subscription_map[sdp_subarray1_obsstate_attribute](dummy_event_sdp)
    attribute = 'PointingState'
    dummy_event_dish = create_dummy_event_state(dish_ln_proxy_mock, dish_ln_prefix + "0001", attribute,
                                                PointingState.TRACK)
    dish_pointing_state_map[dish_pointing_state_attribute](dummy_event_dish)

    wait_for(tango_context, ObsState.READY)
    assert tango_context.device.obsState == ObsState.READY

    tango_context.device.Scan(scan_input_str)
    attribute = 'ObsState'
    dummy_event_csp = create_dummy_event_state(csp_subarray1_ln_proxy_mock, csp_subarray1_ln_fqdn,
                                               attribute, ObsState.SCANNING)
    event_subscription_map[csp_subarray1_obsstate_attribute](dummy_event_csp)

    dummy_event_sdp = create_dummy_event_state(sdp_subarray1_ln_proxy_mock, sdp_subarray1_ln_fqdn,
                                               attribute, ObsState.SCANNING)
    event_subscription_map[sdp_subarray1_obsstate_attribute](dummy_event_sdp)
    attribute = 'PointingState'
    dummy_event_dish = create_dummy_event_state(dish_ln_proxy_mock, dish_ln_prefix + "0001", attribute,
                                                PointingState.TRACK)
    dish_pointing_state_map[dish_pointing_state_attribute](dummy_event_dish)
    wait_for(tango_context, ObsState.SCANNING)
    assert tango_context.device.obsState == ObsState.SCANNING
    assert tango_context.device.EndScan() == [[ResultCode.OK], ['EndScan command is executed successfully.']]

    sdp_subarray1_ln_proxy_mock.command_inout.assert_called_with(const.CMD_END_SCAN)
    csp_subarray1_ln_proxy_mock.command_inout.assert_called_with(const.CMD_END_SCAN)

    wait_for(tango_context, ObsState.READY)
    assert tango_context.device.obsState == ObsState.READY


def test_end_scan_should_raise_devfailed_exception_when_csp_subbarray_ln_throws_devfailed_exception(mock_lower_devices):
    tango_context, csp_subarray1_ln_proxy_mock, csp_subarray1_proxy_mock, sdp_subarray1_ln_proxy_mock, sdp_subarray1_proxy_mock, dish_ln_proxy_mock, csp_subarray1_ln_fqdn, csp_subarray1_fqdn, sdp_subarray1_ln_fqdn, sdp_subarray1_fqdn, dish_ln_prefix, event_subscription_map, dish_pointing_state_map = mock_lower_devices
    csp_subarray1_obsstate_attribute = "cspSubarrayObsState"
    sdp_subarray1_obsstate_attribute = "sdpSubarrayObsState"
    dish_pointing_state_attribute = "dishPointingState"
    tango_context.device.On()

    tango_context.device.AssignResources(assign_input_str)
    attribute = 'ObsState'
    dummy_event_csp = create_dummy_event_state(csp_subarray1_ln_proxy_mock, csp_subarray1_ln_fqdn,
                                               attribute, ObsState.IDLE)
    event_subscription_map[csp_subarray1_obsstate_attribute](dummy_event_csp)

    dummy_event_sdp = create_dummy_event_state(sdp_subarray1_ln_proxy_mock, sdp_subarray1_ln_fqdn,
                                               attribute, ObsState.IDLE)
    event_subscription_map[sdp_subarray1_obsstate_attribute](dummy_event_sdp)

    wait_for(tango_context, ObsState.IDLE)
    assert tango_context.device.obsState == ObsState.IDLE

    attribute = "receiveAddresses"
    dummy_event = create_dummy_event_state(sdp_subarray1_proxy_mock, sdp_subarray1_fqdn, attribute,
                                           receive_addresses_map)
    event_subscription_map[attribute](dummy_event)

    tango_context.device.Configure(configure_str)
    attribute = 'ObsState'
    dummy_event_csp = create_dummy_event_state(csp_subarray1_ln_proxy_mock, csp_subarray1_ln_fqdn,
                                               attribute, ObsState.READY)
    event_subscription_map[csp_subarray1_obsstate_attribute](dummy_event_csp)

    dummy_event_sdp = create_dummy_event_state(sdp_subarray1_ln_proxy_mock, sdp_subarray1_ln_fqdn,
                                               attribute, ObsState.READY)
    event_subscription_map[sdp_subarray1_obsstate_attribute](dummy_event_sdp)
    attribute = 'PointingState'
    dummy_event_dish = create_dummy_event_state(dish_ln_proxy_mock, dish_ln_prefix + "0001", attribute,
                                                PointingState.TRACK)
    dish_pointing_state_map[dish_pointing_state_attribute](dummy_event_dish)

    wait_for(tango_context, ObsState.READY)
    assert tango_context.device.obsState == ObsState.READY

    tango_context.device.Scan(scan_input_str)
    attribute = 'ObsState'
    dummy_event_csp = create_dummy_event_state(csp_subarray1_ln_proxy_mock, csp_subarray1_ln_fqdn,
                                               attribute, ObsState.SCANNING)
    event_subscription_map[csp_subarray1_obsstate_attribute](dummy_event_csp)

    dummy_event_sdp = create_dummy_event_state(sdp_subarray1_ln_proxy_mock, sdp_subarray1_ln_fqdn,
                                               attribute, ObsState.SCANNING)
    event_subscription_map[sdp_subarray1_obsstate_attribute](dummy_event_sdp)
    attribute = 'PointingState'
    dummy_event_dish = create_dummy_event_state(dish_ln_proxy_mock, dish_ln_prefix + "0001", attribute,
                                                PointingState.TRACK)
    dish_pointing_state_map[dish_pointing_state_attribute](dummy_event_dish)
    wait_for(tango_context, ObsState.SCANNING)
    assert tango_context.device.obsState == ObsState.SCANNING
    csp_subarray1_ln_proxy_mock.command_inout.side_effect = raise_devfailed_exception

    with pytest.raises(tango.DevFailed) as df:
        tango_context.device.EndScan()
    assert tango_context.device.obsState == ObsState.FAULT
    assert "This is error message for devfailed" in str(df.value)


def test_end_should_command_subarray_to_end_when_it_is_ready(mock_lower_devices_group):
    tango_context, csp_subarray1_ln_proxy_mock, csp_subarray1_proxy_mock, sdp_subarray1_ln_proxy_mock, sdp_subarray1_proxy_mock, dish_ln_proxy_mock, csp_subarray1_ln_fqdn, csp_subarray1_fqdn, sdp_subarray1_ln_fqdn, sdp_subarray1_fqdn, dish_ln_prefix, event_subscription_map, dish_pointing_state_map, dish_group_mock = mock_lower_devices_group
    csp_subarray1_obsstate_attribute = "cspSubarrayObsState"
    sdp_subarray1_obsstate_attribute = "sdpSubarrayObsState"
    dish_pointing_state_attribute = "dishPointingState"

    tango_context.device.On()
    tango_context.device.AssignResources(assign_input_str)
    attribute = 'ObsState'
    dummy_event_csp = create_dummy_event_state(csp_subarray1_ln_proxy_mock, csp_subarray1_ln_fqdn,
                                               attribute, ObsState.IDLE)
    event_subscription_map[csp_subarray1_obsstate_attribute](dummy_event_csp)

    dummy_event_sdp = create_dummy_event_state(sdp_subarray1_ln_proxy_mock, sdp_subarray1_ln_fqdn,
                                               attribute, ObsState.IDLE)
    event_subscription_map[sdp_subarray1_obsstate_attribute](dummy_event_sdp)

    wait_for(tango_context, ObsState.IDLE)
    assert tango_context.device.obsState == ObsState.IDLE

    attribute = "receiveAddresses"
    dummy_event = create_dummy_event_state(sdp_subarray1_proxy_mock, sdp_subarray1_fqdn, attribute,
                                           receive_addresses_map)
    event_subscription_map[attribute](dummy_event)

    tango_context.device.Configure(configure_str)
    attribute = 'ObsState'
    dummy_event_csp = create_dummy_event_state(csp_subarray1_ln_proxy_mock, csp_subarray1_ln_fqdn,
                                               attribute, ObsState.READY)
    event_subscription_map[csp_subarray1_obsstate_attribute](dummy_event_csp)

    dummy_event_sdp = create_dummy_event_state(sdp_subarray1_ln_proxy_mock, sdp_subarray1_ln_fqdn,
                                               attribute, ObsState.READY)
    event_subscription_map[sdp_subarray1_obsstate_attribute](dummy_event_sdp)
    attribute = 'PointingState'
    dummy_event_dish = create_dummy_event_state(dish_ln_proxy_mock, dish_ln_prefix + "0001", attribute,
                                                PointingState.TRACK)
    dish_pointing_state_map[dish_pointing_state_attribute](dummy_event_dish)
    wait_for(tango_context, ObsState.READY)
    assert tango_context.device.obsState == ObsState.READY

    tango_context.device.Scan(scan_input_str)
    wait_for(tango_context, ObsState.SCANNING)
    assert tango_context.device.obsState == ObsState.SCANNING

    # test without invoking EndScan
    tango_context.device.EndScan()
    wait_for(tango_context, ObsState.READY)
    assert tango_context.device.obsState == ObsState.READY
    assert tango_context.device.End() == [[ResultCode.OK], ['EndSB command invoked successfully on SDP Subarray Leaf '
                                                            'Node and CSP Subarray Leaf Node.']]

    wait_for(tango_context, ObsState.IDLE)

    assert tango_context.device.obsState == ObsState.IDLE

    sdp_subarray1_ln_proxy_mock.command_inout.assert_called_with(const.CMD_END)
    csp_subarray1_ln_proxy_mock.command_inout.assert_called_with(const.CMD_GOTOIDLE)
    dish_group_mock.command_inout.assert_called_with(const.CMD_STOP_TRACK)


def test_end_should_raise_devfailed_exception_when_csp_subarray_throws_devfailed_exception(mock_lower_devices):
    tango_context, csp_subarray1_ln_proxy_mock, csp_subarray1_proxy_mock, sdp_subarray1_ln_proxy_mock, sdp_subarray1_proxy_mock, dish_ln_proxy_mock, csp_subarray1_ln_fqdn, csp_subarray1_fqdn, sdp_subarray1_ln_fqdn, sdp_subarray1_fqdn, dish_ln_prefix, event_subscription_map, dish_pointing_state_map = mock_lower_devices
    csp_subarray1_obsstate_attribute = "cspSubarrayObsState"
    sdp_subarray1_obsstate_attribute = "sdpSubarrayObsState"
    dish_pointing_state_attribute = "dishPointingState"
    tango_context.device.On()
    tango_context.device.AssignResources(assign_input_str)
    attribute = 'ObsState'
    dummy_event_csp = create_dummy_event_state(csp_subarray1_ln_proxy_mock, csp_subarray1_ln_fqdn,
                                               attribute, ObsState.IDLE)
    event_subscription_map[csp_subarray1_obsstate_attribute](dummy_event_csp)

    dummy_event_sdp = create_dummy_event_state(sdp_subarray1_ln_proxy_mock, sdp_subarray1_ln_fqdn,
                                               attribute, ObsState.IDLE)
    event_subscription_map[sdp_subarray1_obsstate_attribute](dummy_event_sdp)

    wait_for(tango_context, ObsState.IDLE)
    assert tango_context.device.obsState == ObsState.IDLE
    attribute = "receiveAddresses"
    dummy_event = create_dummy_event_state(sdp_subarray1_proxy_mock, sdp_subarray1_fqdn, attribute,
                                           receive_addresses_map)
    event_subscription_map[attribute](dummy_event)

    tango_context.device.Configure(configure_str)
    attribute = 'ObsState'
    dummy_event_csp = create_dummy_event_state(csp_subarray1_ln_proxy_mock, csp_subarray1_ln_fqdn,
                                               attribute, ObsState.READY)
    event_subscription_map[csp_subarray1_obsstate_attribute](dummy_event_csp)

    dummy_event_sdp = create_dummy_event_state(sdp_subarray1_ln_proxy_mock, sdp_subarray1_ln_fqdn,
                                               attribute, ObsState.READY)
    event_subscription_map[sdp_subarray1_obsstate_attribute](dummy_event_sdp)
    attribute = 'PointingState'
    dummy_event_dish = create_dummy_event_state(dish_ln_proxy_mock, dish_ln_prefix + "0001", attribute,
                                                PointingState.TRACK)
    dish_pointing_state_map[dish_pointing_state_attribute](dummy_event_dish)

    wait_for(tango_context, ObsState.READY)
    assert tango_context.device.obsState == ObsState.READY
    csp_subarray1_ln_proxy_mock.command_inout.side_effect = raise_devfailed_exception

    with pytest.raises(tango.DevFailed) as df:
        tango_context.device.End()
    assert tango_context.device.obsState == ObsState.FAULT
    assert const.ERR_ENDSB_INVOKING_CMD in str(df.value)


def test_track_command_subarray(mock_lower_devices):
    tango_context = mock_lower_devices[0]
    tango_context.device.On()
    tango_context.device.AssignResources(assign_input_str)
    track_input = "radec|2:31:50.91|89:15:51.4"
    assert tango_context.device.Track(track_input) == [[ResultCode.OK], ['Track command invoked on Subarray']]
    assert const.STR_TRACK_IP_ARG in tango_context.device.activityMessage


# Test Observation State Callback
def test_obs_state_is_with_event_error(mock_lower_devices):
    tango_context, csp_subarray1_ln_proxy_mock, csp_subarray1_proxy_mock, sdp_subarray1_ln_proxy_mock, sdp_subarray1_proxy_mock, dish_ln_proxy_mock, csp_subarray1_ln_fqdn, csp_subarray1_fqdn, sdp_subarray1_ln_fqdn, sdp_subarray1_fqdn, dish_ln_prefix, event_subscription_map, dish_pointing_state_map = mock_lower_devices
    csp_subarray1_obsstate_attribute = "cspSubarrayObsState"
    attribute = 'ObsState'
    tango_context.device.On()
    dummy_event_csp = create_dummy_event_state_with_error(csp_subarray1_ln_proxy_mock, csp_subarray1_ln_fqdn,
                                                          attribute, ObsState.SCANNING)
    event_subscription_map[csp_subarray1_obsstate_attribute](dummy_event_csp)
    assert tango_context.device.activityMessage == const.ERR_SUBSR_CSPSDPSA_OBS_STATE + str(dummy_event_csp)


def test_obs_state_is_with_unknown_attribute(mock_lower_devices):
    tango_context, csp_subarray1_ln_proxy_mock, csp_subarray1_proxy_mock, sdp_subarray1_ln_proxy_mock, sdp_subarray1_proxy_mock, dish_ln_proxy_mock, csp_subarray1_ln_fqdn, csp_subarray1_fqdn, sdp_subarray1_ln_fqdn, sdp_subarray1_fqdn, dish_ln_prefix, event_subscription_map, dish_pointing_state_map = mock_lower_devices
    csp_subarray1_obsstate_attribute = "cspSubarrayObsState"
    attribute = 'ObsState'
    tango_context.device.On()
    dummy_event_csp = create_dummy_event_state(csp_subarray1_ln_proxy_mock, 'Wrong_fqdn',
                                               attribute, ObsState.EMPTY)
    event_subscription_map[csp_subarray1_obsstate_attribute](dummy_event_csp)
    assert tango_context.device.activityMessage in const.EVT_UNKNOWN


@pytest.fixture(
    scope="function",
    params=[
        PointingState.SLEW,
        PointingState.SCAN,
        PointingState.READY,
    ])
def pointing_state(request):
    pointing_state = request.param
    return pointing_state


# Test Pointing State Callback
def test_pointing_state_is_pointing_state(mock_lower_devices, pointing_state):
    tango_context, csp_subarray1_ln_proxy_mock, csp_subarray1_proxy_mock, sdp_subarray1_ln_proxy_mock, sdp_subarray1_proxy_mock, dish_ln_proxy_mock, csp_subarray1_ln_fqdn, csp_subarray1_fqdn, sdp_subarray1_ln_fqdn, sdp_subarray1_fqdn, dish_ln_prefix, event_subscription_map, dish_pointing_state_map = mock_lower_devices
    dish_pointing_state_attribute = "dishPointingState"
    tango_context.device.On()
    tango_context.device.AssignResources(assign_input_str)
    attribute = 'dishPointingState'
    dummy_event_dish = create_dummy_event_state(dish_ln_proxy_mock, dish_ln_prefix + "0001", attribute,
                                                pointing_state)
    dish_pointing_state_map[dish_pointing_state_attribute](dummy_event_dish)
    assert tango_context.device.obsState == ObsState.RESOURCING


def test_pointing_state_with_error_event(mock_lower_devices):
    tango_context, csp_subarray1_ln_proxy_mock, csp_subarray1_proxy_mock, sdp_subarray1_ln_proxy_mock, sdp_subarray1_proxy_mock, dish_ln_proxy_mock, csp_subarray1_ln_fqdn, csp_subarray1_fqdn, sdp_subarray1_ln_fqdn, sdp_subarray1_fqdn, dish_ln_prefix, event_subscription_map, dish_pointing_state_map = mock_lower_devices
    dish_pointing_state_attribute = "dishPointingState"
    tango_context.device.On()
    tango_context.device.AssignResources(assign_input_str)
    attribute = 'dishPointingState'
    dummy_event_dish = create_dummy_event_state_with_error(dish_ln_proxy_mock, dish_ln_prefix + "0001", attribute,
                                                           PointingState.SCAN)
    dish_pointing_state_map[dish_pointing_state_attribute](dummy_event_dish)
    assert tango_context.device.activityMessage == const.ERR_SUBSR_DSH_POINTING_STATE + str(dummy_event_dish.errors)


@pytest.fixture(
    scope="function",
    params=[
        HealthState.DEGRADED,
        HealthState.UNKNOWN,
        HealthState.FAILED,
    ])
def csp_health_state(request):
    csp_health_state = request.param
    return csp_health_state


# Test Health State Callback
def test_subarray_health_state_when_csubarray1_ln_is_in_health_state_after_start(mock_lower_devices, csp_health_state):
    csp_subarray1_ln_health_attribute = 'cspsubarrayHealthState'
    tango_context, csp_subarray1_ln_proxy_mock, csp_subarray1_proxy_mock, sdp_subarray1_ln_proxy_mock, sdp_subarray1_proxy_mock, dish_ln_proxy_mock, csp_subarray1_ln_fqdn, csp_subarray1_fqdn, sdp_subarray1_ln_fqdn, sdp_subarray1_fqdn, dish_ln_prefix, event_subscription_map, dish_pointing_state_map = mock_lower_devices
    tango_context.device.On()
    dummy_event = create_dummy_event_healthstate_with_proxy(
        csp_subarray1_ln_proxy_mock, csp_subarray1_ln_fqdn, csp_health_state,
        csp_subarray1_ln_health_attribute)
    event_subscription_map[csp_subarray1_ln_health_attribute](dummy_event)
    assert tango_context.device.healthState == csp_health_state


def test_subarray_health_state_is_ok_when_csp_and_sdp_subarray1_ln_is_ok_after_start(mock_lower_devices):
    tango_context, csp_subarray1_ln_proxy_mock, csp_subarray1_proxy_mock, sdp_subarray1_ln_proxy_mock, sdp_subarray1_proxy_mock, dish_ln_proxy_mock, csp_subarray1_ln_fqdn, csp_subarray1_fqdn, sdp_subarray1_ln_fqdn, sdp_subarray1_fqdn, dish_ln_prefix, event_subscription_map, dish_pointing_state_map = mock_lower_devices
    tango_context.device.On()
    csp_subarray1_ln_health_attribute = 'cspsubarrayHealthState'
    sdp_subarray1_ln_health_attribute = 'sdpSubarrayHealthState'
    health_state_value = HealthState.OK
    dummy_event_csp = create_dummy_event_healthstate_with_proxy(
        csp_subarray1_ln_proxy_mock, csp_subarray1_ln_fqdn, health_state_value,
        csp_subarray1_ln_health_attribute)
    event_subscription_map[csp_subarray1_ln_health_attribute](dummy_event_csp)

    health_state_value = HealthState.OK
    dummy_event_sdp = create_dummy_event_healthstate_with_proxy(
        sdp_subarray1_ln_proxy_mock, sdp_subarray1_ln_fqdn, health_state_value,
        sdp_subarray1_ln_health_attribute)
    event_subscription_map[sdp_subarray1_ln_health_attribute](dummy_event_sdp)

    assert tango_context.device.healthState == HealthState.OK


def test_subarray_health_state_with_error_event(mock_lower_devices):
    tango_context, csp_subarray1_ln_proxy_mock, csp_subarray1_proxy_mock, sdp_subarray1_ln_proxy_mock, sdp_subarray1_proxy_mock, dish_ln_proxy_mock, csp_subarray1_ln_fqdn, csp_subarray1_fqdn, sdp_subarray1_ln_fqdn, sdp_subarray1_fqdn, dish_ln_prefix, event_subscription_map, dish_pointing_state_map = mock_lower_devices
    tango_context.device.On()
    csp_subarray1_ln_health_attribute = 'cspsubarrayHealthState'
    health_state_value = HealthState.FAILED
    dummy_event = create_dummy_event_healthstate_with_error(
        csp_subarray1_ln_proxy_mock, csp_subarray1_ln_fqdn, health_state_value,
        csp_subarray1_ln_health_attribute)
    event_subscription_map[csp_subarray1_ln_health_attribute](dummy_event)
    assert const.ERR_SUBSR_SA_HEALTH_STATE in tango_context.device.activityMessage


@pytest.mark.parametrize(
    "subarray_ln_fqdn, subarray_ln_health_attribute, fqdn_property",
    [
        ("ska_mid/tm_leaf_node/csp_subarray01", 'cspsubarrayHealthState', 'CspSubarrayLNFQDN'),
        ("ska_mid/tm_leaf_node/sdp_subarray01", 'sdpSubarrayHealthState', 'SdpSubarrayLNFQDN'),
    ]
)
# Test case for event subscribtion
def test_subarray_health_state_event_to_raise_devfailed_exception_for_csp_subarray_ln(subarray_ln_fqdn,
                                                                                      subarray_ln_health_attribute,
                                                                                      fqdn_property):
    initial_dut_properties = {
        fqdn_property: subarray_ln_fqdn
    }

    subarray_ln_proxy_mock = Mock()

    proxies_to_mock = {
        subarray_ln_fqdn: subarray_ln_proxy_mock
    }

    with fake_tango_system(SubarrayNode, initial_dut_properties, proxies_to_mock) as tango_context:
        health_state_value = HealthState.FAILED
        subarray_ln_proxy_mock.subscribe_event.side_effect = raise_devfailed_for_event_subscription
        with pytest.raises(tango.DevFailed) as df:
            tango_context.device.On()
        assert tango_context.device.State() == DevState.FAULT
        assert "Exception occurred while subscribing " in str(df)


def test_end_command_subarray_when_in_invalid_state(mock_lower_devices):
    tango_context, csp_subarray1_ln_proxy_mock, csp_subarray1_proxy_mock, sdp_subarray1_ln_proxy_mock, sdp_subarray1_proxy_mock, dish_ln_proxy_mock, csp_subarray1_ln_fqdn, csp_subarray1_fqdn, sdp_subarray1_ln_fqdn, sdp_subarray1_fqdn, dish_ln_prefix, event_subscription_map, dish_pointing_state_map = mock_lower_devices
    csp_subarray1_obsstate_attribute = "cspSubarrayObsState"
    sdp_subarray1_obsstate_attribute = "sdpSubarrayObsState"
    tango_context.device.On()

    attribute = 'ObsState'
    dummy_event_csp = create_dummy_event_state(csp_subarray1_ln_proxy_mock, csp_subarray1_ln_fqdn,
                                               attribute, ObsState.EMPTY)
    event_subscription_map[csp_subarray1_obsstate_attribute](dummy_event_csp)

    dummy_event_sdp = create_dummy_event_state(sdp_subarray1_ln_proxy_mock, sdp_subarray1_ln_fqdn,
                                               attribute, ObsState.EMPTY)
    event_subscription_map[sdp_subarray1_obsstate_attribute](dummy_event_sdp)
    assert tango_context.device.obsState == ObsState.EMPTY

    with pytest.raises(tango.DevFailed) as df:
        tango_context.device.End()
    assert "Error executing command EndCommand" in str(df.value)


def test_abort_should_command_subarray_to_abort_when_it_is_configuring(mock_lower_devices_group):
    tango_context, csp_subarray1_ln_proxy_mock, csp_subarray1_proxy_mock, sdp_subarray1_ln_proxy_mock, sdp_subarray1_proxy_mock, dish_ln_proxy_mock, csp_subarray1_ln_fqdn, csp_subarray1_fqdn, sdp_subarray1_ln_fqdn, sdp_subarray1_fqdn, dish_ln_prefix, event_subscription_map, dish_pointing_state_map, dish_group_mock = mock_lower_devices_group
    csp_subarray1_obsstate_attribute = "cspSubarrayObsState"
    sdp_subarray1_obsstate_attribute = "sdpSubarrayObsState"
    dish_pointing_state_attribute = "dishPointingState"
    tango_context.device.On()
    tango_context.device.AssignResources(assign_input_str)
    attribute = 'ObsState'

    dummy_event_csp = create_dummy_event_state(csp_subarray1_ln_proxy_mock, csp_subarray1_ln_fqdn,
                                               attribute, ObsState.IDLE)
    event_subscription_map[csp_subarray1_obsstate_attribute](dummy_event_csp)

    dummy_event_sdp = create_dummy_event_state(sdp_subarray1_ln_proxy_mock, sdp_subarray1_ln_fqdn,
                                               attribute, ObsState.IDLE)
    event_subscription_map[sdp_subarray1_obsstate_attribute](dummy_event_sdp)

    wait_for(tango_context, ObsState.IDLE)

    assert tango_context.device.obsState == ObsState.IDLE

    attribute = "receiveAddresses"
    dummy_event = create_dummy_event_state(sdp_subarray1_proxy_mock, sdp_subarray1_fqdn, attribute,
                                           receive_addresses_map)
    event_subscription_map[attribute](dummy_event)

    tango_context.device.Configure(configure_str)
    assert tango_context.device.obsState == ObsState.CONFIGURING

    assert tango_context.device.Abort() == [[ResultCode.STARTED], ['Abort command invoked successfully on SDP Subarray '
                                                                   'Leaf Node and CSP Subarray Leaf Node and Dish Leaf Node.']]

    wait_for(tango_context, ObsState.ABORTING)
    assert tango_context.device.obsState == ObsState.ABORTING
    attribute = 'ObsState'
    dummy_event_csp = create_dummy_event_state(csp_subarray1_ln_proxy_mock, csp_subarray1_ln_fqdn,
                                               attribute, ObsState.ABORTED)
    event_subscription_map[csp_subarray1_obsstate_attribute](dummy_event_csp)

    dummy_event_sdp = create_dummy_event_state(sdp_subarray1_ln_proxy_mock, sdp_subarray1_ln_fqdn,
                                               attribute, ObsState.ABORTED)
    event_subscription_map[sdp_subarray1_obsstate_attribute](dummy_event_sdp)
    dummy_event_dish = create_dummy_event_state(dish_ln_proxy_mock, dish_ln_prefix + "0001", attribute,
                                                PointingState.READY)
    dish_pointing_state_map[dish_pointing_state_attribute](dummy_event_dish)
    sdp_subarray1_ln_proxy_mock.command_inout.assert_called_with(const.CMD_ABORT)
    csp_subarray1_ln_proxy_mock.command_inout.assert_called_with(const.CMD_ABORT)
    dish_group_mock.command_inout.assert_called_with(const.CMD_ABORT)
    assert tango_context.device.obsState == ObsState.ABORTED


def test_abort_should_command_subarray_to_abort_scan_when_it_is_idle(mock_lower_devices_group):
    tango_context, csp_subarray1_ln_proxy_mock, csp_subarray1_proxy_mock, sdp_subarray1_ln_proxy_mock, sdp_subarray1_proxy_mock, dish_ln_proxy_mock, csp_subarray1_ln_fqdn, csp_subarray1_fqdn, sdp_subarray1_ln_fqdn, sdp_subarray1_fqdn, dish_ln_prefix, event_subscription_map, dish_pointing_state_map, dish_group_mock = mock_lower_devices_group
    csp_subarray1_obsstate_attribute = "cspSubarrayObsState"
    sdp_subarray1_obsstate_attribute = "sdpSubarrayObsState"
    dish_pointing_state_attribute = "dishPointingState"
    tango_context.device.On()

    tango_context.device.AssignResources(assign_input_str)
    attribute = 'ObsState'
    dummy_event_csp = create_dummy_event_state(csp_subarray1_ln_proxy_mock, csp_subarray1_ln_fqdn,
                                               attribute, ObsState.IDLE)
    event_subscription_map[csp_subarray1_obsstate_attribute](dummy_event_csp)

    dummy_event_sdp = create_dummy_event_state(sdp_subarray1_ln_proxy_mock, sdp_subarray1_ln_fqdn,
                                               attribute, ObsState.IDLE)
    event_subscription_map[sdp_subarray1_obsstate_attribute](dummy_event_sdp)

    wait_for(tango_context, ObsState.IDLE)
    assert tango_context.device.obsState == ObsState.IDLE

    assert tango_context.device.Abort() == [[ResultCode.STARTED], ['Abort command invoked successfully on SDP Subarray '
                                                                   'Leaf Node and CSP Subarray Leaf Node and Dish Leaf Node.']]
    wait_for(tango_context, ObsState.ABORTING)
    assert tango_context.device.obsState == ObsState.ABORTING
    attribute = 'ObsState'
    dummy_event_csp = create_dummy_event_state(csp_subarray1_ln_proxy_mock, csp_subarray1_ln_fqdn,
                                               attribute, ObsState.ABORTED)
    event_subscription_map[csp_subarray1_obsstate_attribute](dummy_event_csp)

    dummy_event_sdp = create_dummy_event_state(sdp_subarray1_ln_proxy_mock, sdp_subarray1_ln_fqdn,
                                               attribute, ObsState.ABORTED)
    event_subscription_map[sdp_subarray1_obsstate_attribute](dummy_event_sdp)
    dummy_event_dish = create_dummy_event_state(dish_ln_proxy_mock, dish_ln_prefix + "0001", attribute,
                                                PointingState.READY)
    dish_pointing_state_map[dish_pointing_state_attribute](dummy_event_dish)
    sdp_subarray1_ln_proxy_mock.command_inout.assert_called_with(const.CMD_ABORT)
    csp_subarray1_ln_proxy_mock.command_inout.assert_called_with(const.CMD_ABORT)
    dish_group_mock.command_inout.assert_called_with(const.CMD_ABORT)
    wait_for(tango_context, ObsState.ABORTED)
    assert tango_context.device.obsState == ObsState.ABORTED


def test_abort_should_command_subarray_to_abort_when_it_is_READY(mock_lower_devices_group):
    tango_context, csp_subarray1_ln_proxy_mock, csp_subarray1_proxy_mock, sdp_subarray1_ln_proxy_mock, sdp_subarray1_proxy_mock, dish_ln_proxy_mock, csp_subarray1_ln_fqdn, csp_subarray1_fqdn, sdp_subarray1_ln_fqdn, sdp_subarray1_fqdn, dish_ln_prefix, event_subscription_map, dish_pointing_state_map, dish_group_mock = mock_lower_devices_group
    csp_subarray1_obsstate_attribute = "cspSubarrayObsState"
    sdp_subarray1_obsstate_attribute = "sdpSubarrayObsState"
    dish_pointing_state_attribute = "dishPointingState"
    tango_context.device.On()

    tango_context.device.AssignResources(assign_input_str)
    attribute = 'ObsState'
    dummy_event_csp = create_dummy_event_state(csp_subarray1_ln_proxy_mock, csp_subarray1_ln_fqdn,
                                               attribute, ObsState.IDLE)
    event_subscription_map[csp_subarray1_obsstate_attribute](dummy_event_csp)

    dummy_event_sdp = create_dummy_event_state(sdp_subarray1_ln_proxy_mock, sdp_subarray1_ln_fqdn,
                                               attribute, ObsState.IDLE)
    event_subscription_map[sdp_subarray1_obsstate_attribute](dummy_event_sdp)
    assert tango_context.device.obsState == ObsState.IDLE

    attribute = "receiveAddresses"
    dummy_event = create_dummy_event_state(sdp_subarray1_proxy_mock, sdp_subarray1_fqdn, attribute,
                                           receive_addresses_map)
    event_subscription_map[attribute](dummy_event)

    tango_context.device.Configure(configure_str)
    attribute = 'ObsState'
    dummy_event_csp = create_dummy_event_state(csp_subarray1_ln_proxy_mock, csp_subarray1_ln_fqdn,
                                               attribute, ObsState.READY)
    event_subscription_map[csp_subarray1_obsstate_attribute](dummy_event_csp)

    dummy_event_sdp = create_dummy_event_state(sdp_subarray1_ln_proxy_mock, sdp_subarray1_ln_fqdn,
                                               attribute, ObsState.READY)
    event_subscription_map[sdp_subarray1_obsstate_attribute](dummy_event_sdp)
    attribute = 'PointingState'
    dummy_event_dish = create_dummy_event_state(dish_ln_proxy_mock, dish_ln_prefix + "0001", attribute,
                                                PointingState.TRACK)
    dish_pointing_state_map[dish_pointing_state_attribute](dummy_event_dish)
    wait_for(tango_context, ObsState.READY)
    assert tango_context.device.obsState == ObsState.READY
    assert tango_context.device.Abort() == [[ResultCode.STARTED], ['Abort command invoked successfully on SDP Subarray '
                                                                   'Leaf Node and CSP Subarray Leaf Node and Dish Leaf Node.']]

    wait_for(tango_context, ObsState.ABORTING)
    assert tango_context.device.obsState == ObsState.ABORTING
    dummy_event_csp = create_dummy_event_state(csp_subarray1_ln_proxy_mock, csp_subarray1_ln_fqdn,
                                               attribute, ObsState.ABORTED)
    event_subscription_map[csp_subarray1_obsstate_attribute](dummy_event_csp)

    dummy_event_sdp = create_dummy_event_state(sdp_subarray1_ln_proxy_mock, sdp_subarray1_ln_fqdn,
                                               attribute, ObsState.ABORTED)
    event_subscription_map[sdp_subarray1_obsstate_attribute](dummy_event_sdp)

    dummy_event_dish = create_dummy_event_state(dish_ln_proxy_mock, dish_ln_prefix + "0001", attribute,
                                                PointingState.READY)
    dish_pointing_state_map[dish_pointing_state_attribute](dummy_event_dish)

    sdp_subarray1_ln_proxy_mock.command_inout.assert_called_with(const.CMD_ABORT)
    csp_subarray1_ln_proxy_mock.command_inout.assert_called_with(const.CMD_ABORT)
    dish_group_mock.command_inout.assert_called_with(const.CMD_ABORT)
    assert tango_context.device.obsState == ObsState.ABORTED


def test_abort_should_command_subarray_to_abort_when_it_is_scanning(mock_lower_devices_group):
    tango_context, csp_subarray1_ln_proxy_mock, csp_subarray1_proxy_mock, sdp_subarray1_ln_proxy_mock, sdp_subarray1_proxy_mock, dish_ln_proxy_mock, csp_subarray1_ln_fqdn, csp_subarray1_fqdn, sdp_subarray1_ln_fqdn, sdp_subarray1_fqdn, dish_ln_prefix, event_subscription_map, dish_pointing_state_map, dish_group_mock = mock_lower_devices_group
    csp_subarray1_obsstate_attribute = "cspSubarrayObsState"
    sdp_subarray1_obsstate_attribute = "sdpSubarrayObsState"
    dish_pointing_state_attribute = "dishPointingState"
    tango_context.device.On()

    tango_context.device.AssignResources(assign_input_str)
    attribute = 'ObsState'

    dummy_event_csp = create_dummy_event_state(csp_subarray1_ln_proxy_mock, csp_subarray1_ln_fqdn,
                                               attribute, ObsState.IDLE)
    event_subscription_map[csp_subarray1_obsstate_attribute](dummy_event_csp)

    dummy_event_sdp = create_dummy_event_state(sdp_subarray1_ln_proxy_mock, sdp_subarray1_ln_fqdn,
                                               attribute, ObsState.IDLE)
    event_subscription_map[sdp_subarray1_obsstate_attribute](dummy_event_sdp)

    wait_for(tango_context, ObsState.IDLE)
    assert tango_context.device.obsState == ObsState.IDLE

    attribute = "receiveAddresses"
    dummy_event = create_dummy_event_state(sdp_subarray1_proxy_mock, sdp_subarray1_fqdn, attribute,
                                           receive_addresses_map)
    event_subscription_map[attribute](dummy_event)

    tango_context.device.Configure(configure_str)
    attribute = 'ObsState'
    dummy_event_csp = create_dummy_event_state(csp_subarray1_ln_proxy_mock, csp_subarray1_ln_fqdn,
                                               attribute, ObsState.READY)
    event_subscription_map[csp_subarray1_obsstate_attribute](dummy_event_csp)

    dummy_event_sdp = create_dummy_event_state(sdp_subarray1_ln_proxy_mock, sdp_subarray1_ln_fqdn,
                                               attribute, ObsState.READY)
    event_subscription_map[sdp_subarray1_obsstate_attribute](dummy_event_sdp)
    attribute = 'PointingState'
    dummy_event_dish = create_dummy_event_state(dish_ln_proxy_mock, dish_ln_prefix + "0001", attribute,
                                                PointingState.TRACK)
    dish_pointing_state_map[dish_pointing_state_attribute](dummy_event_dish)

    wait_for(tango_context, ObsState.READY)
    assert tango_context.device.obsState == ObsState.READY

    tango_context.device.Scan(scan_input_str)
    attribute = 'ObsState'
    dummy_event_csp = create_dummy_event_state(csp_subarray1_ln_proxy_mock, csp_subarray1_ln_fqdn,
                                               attribute, ObsState.SCANNING)
    event_subscription_map[csp_subarray1_obsstate_attribute](dummy_event_csp)

    dummy_event_sdp = create_dummy_event_state(sdp_subarray1_ln_proxy_mock, sdp_subarray1_ln_fqdn,
                                               attribute, ObsState.SCANNING)
    event_subscription_map[sdp_subarray1_obsstate_attribute](dummy_event_sdp)
    attribute = 'PointingState'
    dummy_event_dish = create_dummy_event_state(dish_ln_proxy_mock, dish_ln_prefix + "0001", attribute,
                                                PointingState.TRACK)
    dish_pointing_state_map[dish_pointing_state_attribute](dummy_event_dish)
    wait_for(tango_context, ObsState.SCANNING)
    assert tango_context.device.obsState == ObsState.SCANNING

    assert tango_context.device.Abort() == [[ResultCode.STARTED], ['Abort command invoked successfully on SDP Subarray '
                                                                   'Leaf Node and CSP Subarray Leaf Node and Dish Leaf Node.']]
    wait_for(tango_context, ObsState.ABORTING)
    assert tango_context.device.obsState == ObsState.ABORTING
    attribute = 'ObsState'
    dummy_event_csp = create_dummy_event_state(csp_subarray1_ln_proxy_mock, csp_subarray1_ln_fqdn,
                                               attribute, ObsState.ABORTED)
    event_subscription_map[csp_subarray1_obsstate_attribute](dummy_event_csp)

    dummy_event_sdp = create_dummy_event_state(sdp_subarray1_ln_proxy_mock, sdp_subarray1_ln_fqdn,
                                               attribute, ObsState.ABORTED)
    event_subscription_map[sdp_subarray1_obsstate_attribute](dummy_event_sdp)
    attribute = 'PointingState'
    dummy_event_dish = create_dummy_event_state(dish_ln_proxy_mock, dish_ln_prefix + "0001", attribute,
                                                PointingState.READY)
    dish_pointing_state_map[dish_pointing_state_attribute](dummy_event_dish)
    sdp_subarray1_ln_proxy_mock.command_inout.assert_called_with(const.CMD_ABORT)
    csp_subarray1_ln_proxy_mock.command_inout.assert_called_with(const.CMD_ABORT)
    dish_group_mock.command_inout.assert_called_with(const.CMD_ABORT)
    assert tango_context.device.obsState == ObsState.ABORTED


def test_abort_should_raise_devfailed_exception(mock_lower_devices):
    tango_context, csp_subarray1_ln_proxy_mock, csp_subarray1_proxy_mock, sdp_subarray1_ln_proxy_mock, sdp_subarray1_proxy_mock, dish_ln_proxy_mock, csp_subarray1_ln_fqdn, csp_subarray1_fqdn, sdp_subarray1_ln_fqdn, sdp_subarray1_fqdn, dish_ln_prefix, event_subscription_map, dish_pointing_state_map = mock_lower_devices
    csp_subarray1_obsstate_attribute = "cspSubarrayObsState"
    sdp_subarray1_obsstate_attribute = "sdpSubarrayObsState"
    dish_pointing_state_attribute = "dishPointingState"
    tango_context.device.On()

    tango_context.device.AssignResources(assign_input_str)
    attribute = 'ObsState'
    dummy_event_csp = create_dummy_event_state(csp_subarray1_ln_proxy_mock, csp_subarray1_ln_fqdn,
                                               attribute, ObsState.IDLE)
    event_subscription_map[csp_subarray1_obsstate_attribute](dummy_event_csp)

    dummy_event_sdp = create_dummy_event_state(sdp_subarray1_ln_proxy_mock, sdp_subarray1_ln_fqdn,
                                               attribute, ObsState.IDLE)
    event_subscription_map[sdp_subarray1_obsstate_attribute](dummy_event_sdp)
    assert tango_context.device.obsState == ObsState.IDLE
    csp_subarray1_ln_proxy_mock.command_inout.side_effect = raise_devfailed_exception

    with pytest.raises(tango.DevFailed) as df:
        tango_context.device.Abort()
    assert tango_context.device.obsState == ObsState.FAULT
    assert "This is error message for devfailed" in str(df.value)


def test_abort_should_raise_devfailed_exception_when_obsstate_is_empty(mock_lower_devices):
    tango_context, csp_subarray1_ln_proxy_mock, csp_subarray1_proxy_mock, sdp_subarray1_ln_proxy_mock, sdp_subarray1_proxy_mock, dish_ln_proxy_mock, csp_subarray1_ln_fqdn, csp_subarray1_fqdn, sdp_subarray1_ln_fqdn, sdp_subarray1_fqdn, dish_ln_prefix, event_subscription_map, dish_pointing_state_map = mock_lower_devices
    csp_subarray1_obsstate_attribute = "cspSubarrayObsState"
    sdp_subarray1_obsstate_attribute = "sdpSubarrayObsState"
    tango_context.device.On()

    attribute = 'ObsState'
    dummy_event_csp = create_dummy_event_state(csp_subarray1_ln_proxy_mock, csp_subarray1_ln_fqdn,
                                               attribute, ObsState.EMPTY)
    event_subscription_map[csp_subarray1_obsstate_attribute](dummy_event_csp)

    dummy_event_sdp = create_dummy_event_state(sdp_subarray1_ln_proxy_mock, sdp_subarray1_ln_fqdn,
                                               attribute, ObsState.EMPTY)
    event_subscription_map[sdp_subarray1_obsstate_attribute](dummy_event_sdp)
    assert tango_context.device.obsState == ObsState.EMPTY
    csp_subarray1_ln_proxy_mock.command_inout.side_effect = raise_devfailed_exception

    with pytest.raises(tango.DevFailed) as df:
        tango_context.device.Abort()
    assert "Error executing command AbortCommand" in str(df.value)


def test_abort_should_raise_devfailed_exception_when_obsstate_is_resourcing(mock_lower_devices):
    tango_context, csp_subarray1_ln_proxy_mock, csp_subarray1_proxy_mock, sdp_subarray1_ln_proxy_mock, sdp_subarray1_proxy_mock, dish_ln_proxy_mock, csp_subarray1_ln_fqdn, csp_subarray1_fqdn, sdp_subarray1_ln_fqdn, sdp_subarray1_fqdn, dish_ln_prefix, event_subscription_map, dish_pointing_state_map = mock_lower_devices
    csp_subarray1_obsstate_attribute = "cspSubarrayObsState"
    sdp_subarray1_obsstate_attribute = "sdpSubarrayObsState"
    tango_context.device.On()

    tango_context.device.AssignResources(assign_input_str)
    attribute = 'ObsState'
    dummy_event_csp = create_dummy_event_state(csp_subarray1_ln_proxy_mock, csp_subarray1_ln_fqdn,
                                               attribute, ObsState.RESOURCING)
    event_subscription_map[csp_subarray1_obsstate_attribute](dummy_event_csp)

    dummy_event_sdp = create_dummy_event_state(sdp_subarray1_ln_proxy_mock, sdp_subarray1_ln_fqdn,
                                               attribute, ObsState.RESOURCING)
    event_subscription_map[sdp_subarray1_obsstate_attribute](dummy_event_sdp)
    assert tango_context.device.obsState == ObsState.RESOURCING
    csp_subarray1_ln_proxy_mock.command_inout.side_effect = raise_devfailed_exception

    with pytest.raises(tango.DevFailed) as df:
        tango_context.device.Abort()
    assert "Error executing command AbortCommand" in str(df.value)


def test_restart_should_command_subarray_to_restart_when_it_is_aborted(mock_lower_devices_group):
    tango_context, csp_subarray1_ln_proxy_mock, csp_subarray1_proxy_mock, sdp_subarray1_ln_proxy_mock, sdp_subarray1_proxy_mock, dish_ln_proxy_mock, csp_subarray1_ln_fqdn, csp_subarray1_fqdn, sdp_subarray1_ln_fqdn, sdp_subarray1_fqdn, dish_ln_prefix, event_subscription_map, dish_pointing_state_map, dish_group_mock = mock_lower_devices_group
    csp_subarray1_obsstate_attribute = "cspSubarrayObsState"
    sdp_subarray1_obsstate_attribute = "sdpSubarrayObsState"
    dish_pointing_state_attribute = "dishPointingState"

    tango_context.device.On()
    tango_context.device.AssignResources(assign_input_str)
    attribute = 'ObsState'
    dummy_event_csp = create_dummy_event_state(csp_subarray1_ln_proxy_mock, csp_subarray1_ln_fqdn,
                                               attribute, ObsState.IDLE)
    event_subscription_map[csp_subarray1_obsstate_attribute](dummy_event_csp)

    dummy_event_sdp = create_dummy_event_state(sdp_subarray1_ln_proxy_mock, sdp_subarray1_ln_fqdn,
                                               attribute, ObsState.IDLE)
    event_subscription_map[sdp_subarray1_obsstate_attribute](dummy_event_sdp)

    tango_context.device.Abort()
    wait_for(tango_context, ObsState.ABORTING)
    assert tango_context.device.obsState == ObsState.ABORTING
    attribute = 'ObsState'
    dummy_event_csp = create_dummy_event_state(csp_subarray1_ln_proxy_mock, csp_subarray1_ln_fqdn,
                                               attribute, ObsState.ABORTED)
    event_subscription_map[csp_subarray1_obsstate_attribute](dummy_event_csp)

    dummy_event_sdp = create_dummy_event_state(sdp_subarray1_ln_proxy_mock, sdp_subarray1_ln_fqdn,
                                               attribute, ObsState.ABORTED)
    event_subscription_map[sdp_subarray1_obsstate_attribute](dummy_event_sdp)

    attribute = 'PointingState'
    dummy_event_dish = create_dummy_event_state(dish_ln_proxy_mock, dish_ln_prefix + "0001", attribute,
                                                PointingState.READY)
    dish_pointing_state_map[dish_pointing_state_attribute](dummy_event_dish)

    wait_for(tango_context, ObsState.ABORTED)
    assert tango_context.device.obsState == ObsState.ABORTED

    assert tango_context.device.Restart() == [[ResultCode.STARTED], ['Restart command invoked successfully on SDP'
                                                                     ' Subarray Leaf Node, CSP Subarray Leaf Node and Dish Leaf Node.']]

    attribute = 'ObsState'
    dummy_event_csp = create_dummy_event_state(csp_subarray1_ln_proxy_mock, csp_subarray1_ln_fqdn,
                                               attribute, ObsState.RESTARTING)
    event_subscription_map[csp_subarray1_obsstate_attribute](dummy_event_csp)

    dummy_event_sdp = create_dummy_event_state(sdp_subarray1_ln_proxy_mock, sdp_subarray1_ln_fqdn,
                                               attribute, ObsState.RESTARTING)
    event_subscription_map[sdp_subarray1_obsstate_attribute](dummy_event_sdp)

    assert tango_context.device.obsState == ObsState.RESTARTING
    attribute = 'ObsState'
    dummy_event_csp = create_dummy_event_state(csp_subarray1_ln_proxy_mock, csp_subarray1_ln_fqdn,
                                               attribute, ObsState.EMPTY)
    event_subscription_map[csp_subarray1_obsstate_attribute](dummy_event_csp)

    dummy_event_sdp = create_dummy_event_state(sdp_subarray1_ln_proxy_mock, sdp_subarray1_ln_fqdn,
                                               attribute, ObsState.EMPTY)
    event_subscription_map[sdp_subarray1_obsstate_attribute](dummy_event_sdp)

    sdp_subarray1_ln_proxy_mock.command_inout.assert_called_with(const.CMD_RESTART)
    csp_subarray1_ln_proxy_mock.command_inout.assert_called_with(const.CMD_RESTART)
    dish_group_mock.command_inout.assert_called_with(const.CMD_RESTART)
    assert tango_context.device.obsState == ObsState.EMPTY


def test_restart_should_command_subarray_to_restart_when_it_is_Fault(mock_lower_devices_group):
    tango_context, csp_subarray1_ln_proxy_mock, csp_subarray1_proxy_mock, sdp_subarray1_ln_proxy_mock, sdp_subarray1_proxy_mock, dish_ln_proxy_mock, csp_subarray1_ln_fqdn, csp_subarray1_fqdn, sdp_subarray1_ln_fqdn, sdp_subarray1_fqdn, dish_ln_prefix, event_subscription_map, dish_pointing_state_map, dish_group_mock = mock_lower_devices_group
    csp_subarray1_obsstate_attribute = "cspSubarrayObsState"
    sdp_subarray1_obsstate_attribute = "sdpSubarrayObsState"
    dish_pointing_state_attribute = "dishPointingState"

    tango_context.device.On()
    with pytest.raises(tango.DevFailed):
        tango_context.device.AssignResources(assign_invalid_key)

    attribute = 'ObsState'
    dummy_event_csp = create_dummy_event_state(csp_subarray1_ln_proxy_mock, csp_subarray1_ln_fqdn,
                                               attribute, ObsState.FAULT)
    event_subscription_map[csp_subarray1_obsstate_attribute](dummy_event_csp)

    dummy_event_sdp = create_dummy_event_state(sdp_subarray1_ln_proxy_mock, sdp_subarray1_ln_fqdn,
                                               attribute, ObsState.FAULT)
    event_subscription_map[sdp_subarray1_obsstate_attribute](dummy_event_sdp)
    assert tango_context.device.obsState == ObsState.FAULT

    assert tango_context.device.Restart() == [[ResultCode.STARTED], ['Restart command invoked successfully on SDP'
                                                                     ' Subarray Leaf Node, CSP Subarray Leaf Node and Dish Leaf Node.']]
    attribute = 'ObsState'
    dummy_event_csp = create_dummy_event_state(csp_subarray1_ln_proxy_mock, csp_subarray1_ln_fqdn,
                                               attribute, ObsState.RESTARTING)
    event_subscription_map[csp_subarray1_obsstate_attribute](dummy_event_csp)

    dummy_event_sdp = create_dummy_event_state(sdp_subarray1_ln_proxy_mock, sdp_subarray1_ln_fqdn,
                                               attribute, ObsState.RESTARTING)
    event_subscription_map[sdp_subarray1_obsstate_attribute](dummy_event_sdp)

    assert tango_context.device.obsState == ObsState.RESTARTING
    attribute = 'ObsState'
    dummy_event_csp = create_dummy_event_state(csp_subarray1_ln_proxy_mock, csp_subarray1_ln_fqdn,
                                               attribute, ObsState.EMPTY)
    event_subscription_map[csp_subarray1_obsstate_attribute](dummy_event_csp)

    dummy_event_sdp = create_dummy_event_state(sdp_subarray1_ln_proxy_mock, sdp_subarray1_ln_fqdn,
                                               attribute, ObsState.EMPTY)
    event_subscription_map[sdp_subarray1_obsstate_attribute](dummy_event_sdp)
    sdp_subarray1_ln_proxy_mock.command_inout.assert_called_with(const.CMD_RESTART)
    csp_subarray1_ln_proxy_mock.command_inout.assert_called_with(const.CMD_RESTART)
    dish_group_mock.command_inout.assert_called_with(const.CMD_RESTART)
    assert tango_context.device.obsState == ObsState.EMPTY


def test_restart_should_not_restart_subarray_when_it_is_invalid_state(mock_lower_devices):
    tango_context, csp_subarray1_ln_proxy_mock, csp_subarray1_proxy_mock, sdp_subarray1_ln_proxy_mock, sdp_subarray1_proxy_mock, dish_ln_proxy_mock, csp_subarray1_ln_fqdn, csp_subarray1_fqdn, sdp_subarray1_ln_fqdn, sdp_subarray1_fqdn, dish_ln_prefix, event_subscription_map, dish_pointing_state_map = mock_lower_devices
    csp_subarray1_obsstate_attribute = "cspSubarrayObsState"
    sdp_subarray1_obsstate_attribute = "sdpSubarrayObsState"
    tango_context.device.On()

    attribute = 'ObsState'
    dummy_event_csp = create_dummy_event_state(csp_subarray1_ln_proxy_mock, csp_subarray1_ln_fqdn,
                                               attribute, ObsState.EMPTY)
    event_subscription_map[csp_subarray1_obsstate_attribute](dummy_event_csp)

    dummy_event_sdp = create_dummy_event_state(sdp_subarray1_ln_proxy_mock, sdp_subarray1_ln_fqdn,
                                               attribute, ObsState.EMPTY)
    event_subscription_map[sdp_subarray1_obsstate_attribute](dummy_event_sdp)
    assert tango_context.device.obsState == ObsState.EMPTY

    with pytest.raises(tango.DevFailed) as df:
        tango_context.device.Restart()
    assert "Error executing command RestartCommand" in str(df.value)


def test_obsreset_should_command_subarray_to_obsreset_when_it_is_aborted(mock_lower_devices_group):
    tango_context, csp_subarray1_ln_proxy_mock, csp_subarray1_proxy_mock, sdp_subarray1_ln_proxy_mock, sdp_subarray1_proxy_mock, dish_ln_proxy_mock, csp_subarray1_ln_fqdn, csp_subarray1_fqdn, sdp_subarray1_ln_fqdn, sdp_subarray1_fqdn, dish_ln_prefix, event_subscription_map, dish_pointing_state_map, dish_group_mock = mock_lower_devices_group
    csp_subarray1_obsstate_attribute = "cspSubarrayObsState"
    sdp_subarray1_obsstate_attribute = "sdpSubarrayObsState"
    dish_pointing_state_attribute = "dishPointingState"

    tango_context.device.On()
    tango_context.device.AssignResources(assign_input_str)
    attribute = 'ObsState'
    dummy_event_csp = create_dummy_event_state(csp_subarray1_ln_proxy_mock, csp_subarray1_ln_fqdn,
                                               attribute, ObsState.IDLE)
    event_subscription_map[csp_subarray1_obsstate_attribute](dummy_event_csp)

    dummy_event_sdp = create_dummy_event_state(sdp_subarray1_ln_proxy_mock, sdp_subarray1_ln_fqdn,
                                               attribute, ObsState.IDLE)
    event_subscription_map[sdp_subarray1_obsstate_attribute](dummy_event_sdp)
    tango_context.device.Abort()
    attribute = 'ObsState'
    dummy_event_csp = create_dummy_event_state(csp_subarray1_ln_proxy_mock, csp_subarray1_ln_fqdn,
                                               attribute, ObsState.ABORTED)
    event_subscription_map[csp_subarray1_obsstate_attribute](dummy_event_csp)

    dummy_event_sdp = create_dummy_event_state(sdp_subarray1_ln_proxy_mock, sdp_subarray1_ln_fqdn,
                                               attribute, ObsState.ABORTED)
    event_subscription_map[sdp_subarray1_obsstate_attribute](dummy_event_sdp)

    attribute = 'PointingState'
    dummy_event_dish = create_dummy_event_state(dish_ln_proxy_mock, dish_ln_prefix + "0001", attribute,
                                                PointingState.READY)
    dish_pointing_state_map[dish_pointing_state_attribute](dummy_event_dish)

    wait_for(tango_context, ObsState.ABORTED)
    assert tango_context.device.obsState == ObsState.ABORTED
    assert tango_context.device.ObsReset() == [[ResultCode.STARTED], ['ObsReset command invoked successfully on SDP'
                                                                      ' Subarray Leaf Node, CSP Subarray Leaf Node and Dish Leaf Node.']]

    attribute = 'ObsState'
    dummy_event_csp = create_dummy_event_state(csp_subarray1_ln_proxy_mock, csp_subarray1_ln_fqdn,
                                               attribute, ObsState.RESETTING)
    event_subscription_map[csp_subarray1_obsstate_attribute](dummy_event_csp)

    dummy_event_sdp = create_dummy_event_state(sdp_subarray1_ln_proxy_mock, sdp_subarray1_ln_fqdn,
                                               attribute, ObsState.RESETTING)
    event_subscription_map[sdp_subarray1_obsstate_attribute](dummy_event_sdp)

    assert tango_context.device.obsState == ObsState.RESETTING
    attribute = 'ObsState'
    dummy_event_csp = create_dummy_event_state(csp_subarray1_ln_proxy_mock, csp_subarray1_ln_fqdn,
                                               attribute, ObsState.IDLE)
    event_subscription_map[csp_subarray1_obsstate_attribute](dummy_event_csp)

    dummy_event_sdp = create_dummy_event_state(sdp_subarray1_ln_proxy_mock, sdp_subarray1_ln_fqdn,
                                               attribute, ObsState.IDLE)
    event_subscription_map[sdp_subarray1_obsstate_attribute](dummy_event_sdp)
    sdp_subarray1_ln_proxy_mock.command_inout.assert_called_with(const.CMD_OBSRESET)
    csp_subarray1_ln_proxy_mock.command_inout.assert_called_with(const.CMD_OBSRESET)
    dish_group_mock.command_inout.assert_called_with(const.CMD_OBSRESET)

    assert tango_context.device.obsState == ObsState.IDLE


def test_obsreset_should_command_subarray_to_obsreset_when_it_is_Fault(mock_lower_devices_group):
    tango_context, csp_subarray1_ln_proxy_mock, csp_subarray1_proxy_mock, sdp_subarray1_ln_proxy_mock, sdp_subarray1_proxy_mock, dish_ln_proxy_mock, csp_subarray1_ln_fqdn, csp_subarray1_fqdn, sdp_subarray1_ln_fqdn, sdp_subarray1_fqdn, dish_ln_prefix, event_subscription_map, dish_pointing_state_map, dish_group_mock = mock_lower_devices_group
    csp_subarray1_obsstate_attribute = "cspSubarrayObsState"
    sdp_subarray1_obsstate_attribute = "sdpSubarrayObsState"
    dish_pointing_state_attribute = "dishPointingState"

    tango_context.device.On()
    with pytest.raises(tango.DevFailed):
        tango_context.device.AssignResources(assign_invalid_key)

    attribute = 'ObsState'
    dummy_event_csp = create_dummy_event_state(csp_subarray1_ln_proxy_mock, csp_subarray1_ln_fqdn,
                                               attribute, ObsState.FAULT)
    event_subscription_map[csp_subarray1_obsstate_attribute](dummy_event_csp)

    dummy_event_sdp = create_dummy_event_state(sdp_subarray1_ln_proxy_mock, sdp_subarray1_ln_fqdn,
                                               attribute, ObsState.FAULT)
    event_subscription_map[sdp_subarray1_obsstate_attribute](dummy_event_sdp)
    assert tango_context.device.obsState == ObsState.FAULT

    assert tango_context.device.ObsReset() == [[ResultCode.STARTED], ['ObsReset command invoked successfully on SDP'
                                                                      ' Subarray Leaf Node, CSP Subarray Leaf Node and Dish Leaf Node.']]
    attribute = 'ObsState'
    dummy_event_csp = create_dummy_event_state(csp_subarray1_ln_proxy_mock, csp_subarray1_ln_fqdn,
                                               attribute, ObsState.RESETTING)
    event_subscription_map[csp_subarray1_obsstate_attribute](dummy_event_csp)

    dummy_event_sdp = create_dummy_event_state(sdp_subarray1_ln_proxy_mock, sdp_subarray1_ln_fqdn,
                                               attribute, ObsState.RESETTING)
    event_subscription_map[sdp_subarray1_obsstate_attribute](dummy_event_sdp)

    assert tango_context.device.obsState == ObsState.RESETTING
    attribute = 'ObsState'
    dummy_event_csp = create_dummy_event_state(csp_subarray1_ln_proxy_mock, csp_subarray1_ln_fqdn,
                                               attribute, ObsState.IDLE)
    event_subscription_map[csp_subarray1_obsstate_attribute](dummy_event_csp)

    dummy_event_sdp = create_dummy_event_state(sdp_subarray1_ln_proxy_mock, sdp_subarray1_ln_fqdn,
                                               attribute, ObsState.IDLE)
    event_subscription_map[sdp_subarray1_obsstate_attribute](dummy_event_sdp)
    sdp_subarray1_ln_proxy_mock.command_inout.assert_called_with(const.CMD_OBSRESET)
    csp_subarray1_ln_proxy_mock.command_inout.assert_called_with(const.CMD_OBSRESET)
    dish_group_mock.command_inout.assert_called_with(const.CMD_OBSRESET)

    assert tango_context.device.obsState == ObsState.IDLE


def test_obsreset_should_not_command_subarray_to_Obsreset_when_it_is_invalid_state(mock_lower_devices):
    tango_context, csp_subarray1_ln_proxy_mock, csp_subarray1_proxy_mock, sdp_subarray1_ln_proxy_mock, sdp_subarray1_proxy_mock, dish_ln_proxy_mock, csp_subarray1_ln_fqdn, csp_subarray1_fqdn, sdp_subarray1_ln_fqdn, sdp_subarray1_fqdn, dish_ln_prefix, event_subscription_map, dish_pointing_state_map = mock_lower_devices
    csp_subarray1_obsstate_attribute = "cspSubarrayObsState"
    sdp_subarray1_obsstate_attribute = "sdpSubarrayObsState"
    tango_context.device.On()

    attribute = 'ObsState'
    dummy_event_csp = create_dummy_event_state(csp_subarray1_ln_proxy_mock, csp_subarray1_ln_fqdn,
                                               attribute, ObsState.EMPTY)
    event_subscription_map[csp_subarray1_obsstate_attribute](dummy_event_csp)

    dummy_event_sdp = create_dummy_event_state(sdp_subarray1_ln_proxy_mock, sdp_subarray1_ln_fqdn,
                                               attribute, ObsState.EMPTY)
    event_subscription_map[sdp_subarray1_obsstate_attribute](dummy_event_sdp)
    assert tango_context.device.obsState == ObsState.EMPTY

    with pytest.raises(tango.DevFailed) as df:
        tango_context.device.ObsReset()
    assert "Error executing command ObsResetCommand" in str(df.value)


def any_method(with_name=None):
    class AnyMethod():
        def __eq__(self, other):
            if not isinstance(other, types.MethodType):
                return False

            return other.__func__.__name__ == with_name if with_name else True

    return AnyMethod()


def create_dummy_event_healthstate_with_proxy(proxy_mock, device_fqdn, health_state_value, attribute):
    fake_event = Mock()
    fake_event.err = False
    fake_event.attr_name = f"{device_fqdn}/{attribute}"
    fake_event.attr_value.value = health_state_value
    fake_event.device = proxy_mock
    return fake_event


def create_dummy_event_healthstate_with_error(proxy_mock, device_fqdn, health_state_value, attribute):
    fake_event = Mock()
    fake_event.err = True
    fake_event.attr_name = f"{device_fqdn}/{attribute}"
    fake_event.attr_value.value = health_state_value
    fake_event.device = proxy_mock
    return fake_event
'''
#
# def create_dummy_event_state(proxy_mock, device_fqdn, attribute, attr_value):
#     fake_event = Mock()
#     fake_event.err = False
#     fake_event.attr_name = f"{device_fqdn}/{attribute}"
#     fake_event.attr_value.value = attr_value
#     fake_event.device = proxy_mock
#     return fake_event


def create_dummy_event_state_with_error(proxy_mock, device_fqdn, attribute, attr_value):
    fake_event = MagicMock()
    fake_event.err = True
    fake_event.errors = 'Invalid Value'
    fake_event.attr_name = f"{device_fqdn}/{attribute}"
    fake_event.attr_value.value = attr_value
    fake_event.device = proxy_mock
    return fake_event


def create_dummy_event_custom_exception(proxy_mock, device_fqdn, attribute, attr_value):
    fake_event = MagicMock()
    fake_event.err = True
    fake_event.errors = 'Invalid Value'
    fake_event.attr_name = "{device_fqdn}/{attribute}"
    fake_event.attr_value = "Subarray is not in IDLE obsState, please check the subarray obsState"
    fake_event.device = proxy_mock
    return fake_event


def create_dummy_event_sdp_receiceAddresses(proxy_mock, device_fqdn, attribute, attr_value):
    fake_event = Mock()
    fake_event.err = False
    fake_event.attr_name = f"{device_fqdn}/{attribute}"
    fake_event.attr_value.value = attr_value
    fake_event.device = proxy_mock
    return fake_event


def raise_devfailed_exception(*args):
    tango.Except.throw_exception("SubarrayNode_Commandfailed",
                                 "This is error message for devfailed",
                                 "", tango.ErrSeverity.ERR)


def raise_devfailed_for_event_subscription(evt_name, evt_type, callaback, stateless=True):
    tango.Except.throw_exception("SubarrayNode_CommandCallbackfailed",
                                 "This is error message for devfailed",
                                 "From function test devfailed", tango.ErrSeverity.ERR)


def command_callback_with_command_exception():
    fake_event = Mock()
    fake_event.err = False
    fake_event.attr_name = Exception("Exception in callback")
    return fake_event


def command_callback_with_devfailed_exception():
    fake_event = Mock()
    fake_event.err = False
    fake_event.attr_name = tango.Except.throw_exception("TestDevfailed", "This is error message for devfailed",
                                                        "From function test devfailed", tango.ErrSeverity.ERR)
    return fake_event


@contextlib.contextmanager
def fake_tango_system(device_under_test, initial_dut_properties={}, proxies_to_mock={}, group_to_mock={},
                    device_proxy_import_path='tango.DeviceProxy',device_group_import_path='tango.Group'):
    # with mock.patch.object(TangoClient, 'get_deviceproxy', return_value=Mock()) as patched_constructor:
    #     patched_constructor.side_effect = lambda device_fqdn: proxies_to_mock.get(device_fqdn, Mock())
    #     patched_module = importlib.reload(sys.modules[device_under_test.__module__])

    with mock.patch(device_proxy_import_path) as patched_constructor:
        with mock.patch(device_group_import_path) as group_constructor:
            patched_constructor.side_effect = lambda device_fqdn: proxies_to_mock.get(device_fqdn, Mock())
            group_constructor.side_effect = lambda dish_group_mock: group_to_mock.get(dish_group_mock,
                                                                                      Mock())  # group_to_mock: Mock()
            patched_module = importlib.reload(sys.modules[device_under_test.__module__])

    device_under_test = getattr(patched_module, device_under_test.__name__)
    device_test_context = DeviceTestContext(device_under_test, properties=initial_dut_properties)
    device_test_context.start()
    yield device_test_context
    device_test_context.stop()
