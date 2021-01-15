# Standard Python imports
import contextlib
import importlib
import sys
import json
from typing import Dict
import pytest
import mock
from mock import Mock, MagicMock
from os.path import dirname, join
import threading
import re
import logging
# Tango imports
import tango
from tango import DevState, DeviceData
from tango.test_context import DeviceTestContext
# Additional import
from subarraynode import SubarrayNode, const, ElementDeviceData, release
from tmc.common.tango_client import TangoClient
from subarraynode.configure_command import Configure
from subarraynode.scan_command import Scan
from subarraynode.end_scan_command import EndScan
from subarraynode.end_command import End
from subarraynode.abort_command import Abort
from subarraynode.obsreset_command import ObsReset
from subarraynode.restart_command import Restart
from subarraynode.release_all_resources_command import ReleaseAllResources
from subarraynode.track_command import Track
from subarraynode.device_data import DeviceData
from ska.base.control_model import HealthState, ObsState
from ska.base.commands import ResultCode
from ska.base import SKASubarrayStateModel

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
        dsh_cmd_data = ElementDeviceData.build_up_dsh_cmd_data(valid_scan_config)
        valid_scan_config.pop("sdp")
        valid_scan_config.pop("csp")
        valid_scan_config.pop("tmc")
        expected_string_dict = json.dumps(valid_scan_config)

        assert isinstance(dsh_cmd_data, tango.DeviceData)
        assert expected_string_dict == dsh_cmd_data.extract()

    def test_build_up_dsh_cmd_data_with_invalid_scan_configuration(self, example_scan_configuration):
        invalid_scan_config = example_scan_configuration.pop("dish")
        with pytest.raises(KeyError) as exception:
            ElementDeviceData.build_up_dsh_cmd_data(invalid_scan_config)
        expected_msg = "Dish configuration must be given. Aborting Dish configuration."
        assert exception.value.args[0] == expected_msg
        

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


def test_read_activity_message():
    """Test for activityMessage"""
    with fake_tango_system(SubarrayNode) as tango_context:
        assert tango_context.device.activityMessage == const.STR_SA_INIT_SUCCESS


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
    #TODO: Not able to mock the second device, enable one device at a time
    # arg_list = []
    # json_argument = {}
    # dish = {}
    # receptor_list = assign_input_dict["dish"]["receptorIDList"]
    # dish[const.STR_KEY_RECEPTOR_ID_LIST] = receptor_list
    # json_argument[const.STR_KEY_DISH] = dish
    # arg_list.append(json.dumps(json_argument))
    # verify_called_correctly(tango_client_obj.deviceproxy,const.CMD_ASSIGN_RESOURCES,json.dumps(json_argument))
    assert device_proxy.obsState == ObsState.RESOURCING


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
        assert "Error executing command AssignResources" in str(df.value)


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
    device_proxy, tango_client_obj = mock_device_proxy
    device_proxy.On()
    tango_client_obj.deviceproxy.command_inout.side_effect = raise_devfailed_exception

    with pytest.raises(tango.DevFailed) as df:
        device_proxy.AssignResources(assign_input_str)
    assert device_proxy.State() == DevState.ON
    assert device_proxy.obsState == ObsState.FAULT
    assert "This is error message for devfailed" in str(df.value)


def test_assign_resource_should_raise_exception_when_sdp_subarray_ln_throws_devfailed_exception(mock_device_proxy):
    device_proxy, tango_client_obj = mock_device_proxy

    device_proxy.On()
    tango_client_obj.deviceproxy.command_inout.side_effect = raise_devfailed_exception

    with pytest.raises(tango.DevFailed) as df:
        device_proxy.AssignResources(assign_input_str)
    assert device_proxy.State() == DevState.ON
    assert device_proxy.obsState == ObsState.FAULT
    assert "This is error message for devfailed" in str(df.value)


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


def test_log_transaction_with_assign(mock_device_proxy, caplog):
    device_proxy, tango_client_obj = mock_device_proxy
    device_proxy.On()
    device_proxy.AssignResources(assign_input_str)
    assert_that_log_contains('assign', caplog)


def test_log_transaction_with_config(mock_device_proxy, subarray_state_model, caplog):
    device_proxy, tango_client_obj = mock_device_proxy
    device_data = DeviceData.get_instance()
    configure_cmd = Configure(device_data, subarray_state_model)
    with mock.patch.object(TangoClient, "_get_deviceproxy", return_value=Mock()):
        with mock.patch.object(TangoClient, "subscribe_attribute", side_effect=dummy_subscriber_receive_addresses):
            tango_client_obj = TangoClient('ska_mid/tm_leaf_node/sdp_subarray01')
            device_proxy.On()
    subarray_state_model._straight_to_state(DevState.ON, None, ObsState.IDLE)
    configure_cmd.do(configure_str)
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
    configure_cmd = Configure(device_data, subarray_state_model)
    with mock.patch.object(TangoClient, "_get_deviceproxy", return_value=Mock()):
        with mock.patch.object(TangoClient, "subscribe_attribute", side_effect=dummy_subscriber_receive_addresses):
            tango_client_obj = TangoClient('ska_mid/tm_leaf_node/sdp_subarray01')
            device_proxy.On()
            subarray_state_model._straight_to_state(DevState.ON, None, ObsState.IDLE)
            configure_cmd.do(configure_str)
            verify_called_correctly(tango_client_obj.deviceproxy, const.CMD_CONFIGURE, mock_transaction_id)


def test_transaction_id_injected_in_assign_command(mock_device_proxy, mock_transaction_id):
    device_proxy, tango_client_obj = mock_device_proxy
    device_proxy.On()
    device_proxy.AssignResources(assign_input_str)
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
    configure_cmd = Configure(device_data, subarray_state_model)
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
    callback_method(fake_event)
    return 10


def test_configure_command_subarray_with_invalid_configure_input(device_data, subarray_state_model, mock_device_proxy):
    device_proxy, tango_client_obj = mock_device_proxy
    configure_cmd = Configure(device_data, subarray_state_model)
    with mock.patch.object(TangoClient, "_get_deviceproxy", return_value=Mock()):
        with mock.patch.object(TangoClient, "subscribe_attribute", side_effect=dummy_subscriber_receive_addresses):
            tango_client_obj = TangoClient('ska_mid/tm_leaf_node/sdp_subarray01')
            device_proxy.On()
    subarray_state_model._straight_to_state(DevState.ON, None, ObsState.IDLE)
    with pytest.raises(tango.DevFailed) as df:
        configure_cmd.do(invalid_conf_input)
    device_data = DeviceData.get_instance()
    assert device_data._read_activity_message in str(df.value)


def test_scan_command(device_data, subarray_state_model, mock_device_proxy):
    _ , _ = mock_device_proxy
    scan_cmd = Scan(device_data, subarray_state_model)
    assert scan_cmd.do(configure_str) == (ResultCode.STARTED, 'Scan command is executed successfully.')


def test_scan_raise_devfailed(device_data, subarray_state_model, mock_device_proxy):
    device_proxy, tango_client_obj = mock_device_proxy
    tango_client_obj.deviceproxy.command_inout.side_effect = raise_devfailed_exception
    scan_cmd = Scan(device_data, subarray_state_model)
    with pytest.raises(tango.DevFailed) as df:
        scan_cmd.do(configure_str)
    assert "This is error message for devfailed" in str(df.value)


def test_end_scan_command(subarray_state_model, mock_device_proxy):
    _ , _ = mock_device_proxy
    device_data = DeviceData.get_instance()
    end_scan_cmd = EndScan(device_data, subarray_state_model)
    device_data.scan_timer_handler.start_scan_timer(10)
    assert end_scan_cmd.do() == (ResultCode.OK, const.STR_END_SCAN_SUCCESS)


def test_end_scan_raise_devfailed(subarray_state_model, mock_device_proxy):
    device_proxy, tango_client_obj = mock_device_proxy
    tango_client_obj.deviceproxy.command_inout.side_effect = raise_devfailed_exception
    device_data = DeviceData.get_instance()
    end_scan_cmd = EndScan(device_data, subarray_state_model)
    device_data.scan_timer_handler.start_scan_timer(10)
    with pytest.raises(tango.DevFailed) as df:
        end_scan_cmd.do()
    assert "This is error message for devfailed" in str(df.value)


def test_end_command(device_data, subarray_state_model, mock_device_proxy):
    device_proxy , _ = mock_device_proxy
    end_cmd = End(device_data, subarray_state_model)
    assert end_cmd.do() == (ResultCode.OK, const.STR_ENDSB_SUCCESS)


def test_end_raise_devfailed(device_data, subarray_state_model, mock_device_proxy):
    device_proxy, tango_client_obj = mock_device_proxy
    tango_client_obj.deviceproxy.command_inout.side_effect = raise_devfailed_exception
    end_cmd = End(device_data, subarray_state_model)
    with pytest.raises(tango.DevFailed) as df:
        end_cmd.do()
    assert "This is error message for devfailed" in str(df.value)


def test_abort_command(device_data, subarray_state_model, mock_device_proxy):
    _ , _ = mock_device_proxy
    abort_cmd = Abort(device_data, subarray_state_model)
    device_data.scan_timer_handler.start_scan_timer(10)
    assert abort_cmd.do() == (ResultCode.STARTED, const.STR_ABORT_SUCCESS)


def test_abort_raise_devfailed(device_data, subarray_state_model, mock_device_proxy):
    device_proxy, tango_client_obj = mock_device_proxy
    tango_client_obj.deviceproxy.command_inout.side_effect = raise_devfailed_exception
    abort_cmd = Abort(device_data, subarray_state_model)
    device_data.scan_timer_handler.start_scan_timer(10)
    with pytest.raises(tango.DevFailed) as df:
        abort_cmd.do()
    assert "This is error message for devfailed" in str(df.value)


def test_obsreset_command(device_data, subarray_state_model, mock_device_proxy):
    obsreset_cmd = ObsReset(device_data, subarray_state_model)
    assert obsreset_cmd.do() == (ResultCode.STARTED, const.STR_OBSRESET_SUCCESS)


def test_obsreset_raise_devfailed(device_data, subarray_state_model, mock_device_proxy):
    device_proxy, tango_client_obj = mock_device_proxy
    tango_client_obj.deviceproxy.command_inout.side_effect = raise_devfailed_exception
    obsreset_cmd = ObsReset(device_data, subarray_state_model)
    with pytest.raises(tango.DevFailed) as df:
        obsreset_cmd.do()
    assert "This is error message for devfailed" in str(df.value)


def test_restart_command(device_data, subarray_state_model, mock_device_proxy):
    restart_cmd = Restart(device_data, subarray_state_model)
    assert restart_cmd.do() == (ResultCode.STARTED, const.STR_RESTART_SUCCESS)


def test_restart_raise_devfailed(device_data, subarray_state_model, mock_device_proxy):
    device_proxy, tango_client_obj = mock_device_proxy
    tango_client_obj.deviceproxy.command_inout.side_effect = raise_devfailed_exception
    restart_cmd = Restart(device_data, subarray_state_model)
    with pytest.raises(tango.DevFailed) as df:
        restart_cmd.do()
    assert "This is error message for devfailed" in str(df.value)


def test_releaseallresources_command(device_data, subarray_state_model, mock_device_proxy):
    device_proxy, _ = mock_device_proxy
    device_proxy.On()
    device_proxy.AssignResources(assign_input_str)
    release_resources_cmd = ReleaseAllResources(device_data, subarray_state_model)
    assert release_resources_cmd.do() == (ResultCode.STARTED, '[]')


def test_release_resource_should_raise_exception_when_called_before_assign_resource(device_data, subarray_state_model, mock_device_proxy):
    device_proxy, tango_client_obj = mock_device_proxy
    release_resources_cmd = ReleaseAllResources(device_data, subarray_state_model)
    with pytest.raises(tango.DevFailed) as df:
        release_resources_cmd.do()
    assert const.ERR_RELEASE_RES_CMD in str(df.value)


def test_track_command_subarray(mock_device_proxy):
    device_proxy, tango_client_obj = mock_device_proxy
    device_proxy.On()
    device_proxy.AssignResources(assign_input_str)
    track_input = "radec|2:31:50.91|89:15:51.4"
    track_cmd = Track(device_data, subarray_state_model)
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
    callback_method(fake_event)
    return 10


@pytest.fixture(
    scope = "function",
    params=[
        #TODO:
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
