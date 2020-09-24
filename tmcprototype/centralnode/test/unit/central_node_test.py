# Standard Python imports
import contextlib
import importlib
import sys
import types
import json
import pytest
import mock
from mock import MagicMock
from mock import Mock
from os.path import dirname, join

# Tango imports
import tango
from tango import DevState
from tango.test_context import DeviceTestContext

# Additional import

from centralnode import CentralNode, const, release
from centralnode.const import CMD_SET_STOW_MODE, STR_ON_CMD_ISSUED, STR_STOW_CMD_ISSUED_CN, STR_STANDBY_CMD_ISSUED
from ska.base.control_model import HealthState, AdminMode, SimulationMode, ControlMode, TestMode
from ska.base.control_model import LoggingLevel
from ska.base.commands import ResultCode

assign_input_file = 'command_AssignResources.json'
path = join(dirname(__file__), 'data', assign_input_file)
with open(path, 'r') as f:
    assign_input_str = f.read()

release_input_file='command_ReleaseResources.json'
path= join(dirname(__file__), 'data' , release_input_file)
with open(path, 'r') as f:
    release_input_str= f.read()

invalid_json_Assign_Release_file='invalid_json_Assign_Release_Resources.json'
path= join(dirname(__file__), 'data', invalid_json_Assign_Release_file)
with open(path, 'r') as f:
    assign_release_invalid_str= f.read()

assign_invalid_key_file='invalid_key_AssignResources.json'
path= join(dirname(__file__), 'data', assign_invalid_key_file)
with open(path, 'r') as f:
    assign_invalid_key=f.read()

release_invalid_key_file='invalid_key_ReleaseResources.json'
path= join(dirname(__file__), 'data', release_invalid_key_file)
with open(path, 'r') as f:
    release_invalid_key=f.read()


@pytest.fixture(scope = 'function')
def mock_subarraynode_device():
    subarray1_fqdn = 'ska_mid/tm_subarray_node/1'
    initial_dut_properties = {
        'TMMidSubarrayNodes': subarray1_fqdn
    }

    event_subscription_map = {}
    subarray1_device_proxy_mock = Mock()
    subarray1_device_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args,
               **kwargs: event_subscription_map.update({attr_name: callback}))

    proxies_to_mock = {
        subarray1_fqdn: subarray1_device_proxy_mock
    }

    with fake_tango_system(CentralNode, initial_dut_properties, proxies_to_mock) as tango_context:
        yield tango_context.device, subarray1_device_proxy_mock, subarray1_fqdn, event_subscription_map


@pytest.fixture(scope='function')
def mock_central_lower_devices():
    csp_master_ln_fqdn = 'ska_mid/tm_leaf_node/csp_master'
    sdp_master_ln_fqdn = 'ska_mid/tm_leaf_node/sdp_master'
    subarray1_fqdn = 'ska_mid/tm_subarray_node/1'
    dish_device_ids = [str(i).zfill(1) for i in range(1, 4)]
    dish_leaf_fqdn_prefix = "ska_mid/tm_leaf_node/d"

    dut_properties = {
        'DishLeafNodePrefix': dish_leaf_fqdn_prefix,
        'SdpMasterLeafNodeFQDN': sdp_master_ln_fqdn,
        'CspMasterLeafNodeFQDN': csp_master_ln_fqdn,
        'TMMidSubarrayNodes': subarray1_fqdn,
        'NumDishes': len(dish_device_ids)
    }
    # For subarray node and dish leaf node proxy creation MagicMock is used instead of Mock because when
    # proxy inout is called it returns list of resources allocated where length of list need to be evaluated
    # but Mock does not support len function for returned object. Hence MagicMock which is a superset of
    # Mock is used which supports this facility.
    dish_ln1_proxy_mock = MagicMock()
    csp_master_ln_proxy_mock = Mock()
    sdp_master_ln_proxy_mock = Mock()
    subarray1_proxy_mock = MagicMock()
    proxies_to_mock = {
        dish_leaf_fqdn_prefix + "0001": dish_ln1_proxy_mock,
        csp_master_ln_fqdn: csp_master_ln_proxy_mock,
        sdp_master_ln_fqdn: sdp_master_ln_proxy_mock,
        subarray1_fqdn: subarray1_proxy_mock
    }
    with fake_tango_system(CentralNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        yield tango_context.device, subarray1_proxy_mock, dish_ln1_proxy_mock, csp_master_ln_proxy_mock, sdp_master_ln_proxy_mock


@pytest.fixture( scope="function",
    params=[HealthState.DEGRADED, HealthState.OK, HealthState.UNKNOWN, HealthState.FAILED])
def central_node_test_info(request):
    # arrange:
    device_under_test = CentralNode
    csp_master_ln_fqdn = 'ska_mid/tm_leaf_node/csp_master'
    csp_master_ln_health_attribute = 'cspHealthState'

    initial_dut_properties = {
        'CspMasterLeafNodeFQDN': csp_master_ln_fqdn
    }

    event_subscription_map = {}
    csp_master_ln_proxy_mock = Mock()
    csp_master_ln_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args, **kwargs:
        event_subscription_map.update({attr_name: callback}))

    proxies_to_mock = {
        csp_master_ln_fqdn: csp_master_ln_proxy_mock
    }

    test_info = {
        'csp_master_ln_health_attribute': csp_master_ln_health_attribute,
        'initial_dut_properties': initial_dut_properties,
        'proxies_to_mock': proxies_to_mock,
        'csp_master_ln_health_state': request.param,
        'event_subscription_map': event_subscription_map,
        'csp_master_ln_fqdn': csp_master_ln_fqdn,
    }
    return test_info


# Test cases for Attributes
def test_telescope_health_state():
    # act & assert:
    with fake_tango_system(CentralNode) as tango_context:
        assert tango_context.device.telescopeHealthState == HealthState.OK


def test_subarray1_health_state():
    # act & assert:
    with fake_tango_system(CentralNode) as tango_context:
        assert tango_context.device.subarray1HealthState == HealthState.OK


def test_subarray2_health_state():
    # act & assert:
    with fake_tango_system(CentralNode) as tango_context:
        assert tango_context.device.subarray2HealthState == HealthState.OK


def test_subarray3_health_state():
    # act & assert:
    with fake_tango_system(CentralNode) as tango_context:
        assert tango_context.device.subarray3HealthState == HealthState.OK


def test_activity_message():
    # act & assert:
    with fake_tango_system(CentralNode) as tango_context:
        tango_context.device.activityMessage = ''
        assert tango_context.device.activityMessage == ''


def test_logging_level():
    # act & assert:
    with fake_tango_system(CentralNode) as tango_context:
        tango_context.device.loggingLevel = LoggingLevel.INFO
        assert tango_context.device.loggingLevel == LoggingLevel.INFO


def test_logging_targets():
    # act & assert:
    with fake_tango_system(CentralNode) as tango_context:
        tango_context.device.loggingTargets = ['console::cout']
        assert 'console::cout' in tango_context.device.loggingTargets


def test_test_mode():
    # act & assert:
    with fake_tango_system(CentralNode) as tango_context:
        test_mode = TestMode.NONE
        tango_context.device.testMode = test_mode
        assert tango_context.device.testMode == test_mode


def test_simulation_mode():
    # act & assert:
    with fake_tango_system(CentralNode) as tango_context:
        simulation_mode = SimulationMode.FALSE
        tango_context.device.simulationMode = simulation_mode
        assert tango_context.device.simulationMode == simulation_mode


def test_control_mode():
    # act & assert:
    with fake_tango_system(CentralNode) as tango_context:
        control_mode = ControlMode.REMOTE
        tango_context.device.controlMode = control_mode
        assert tango_context.device.controlMode == control_mode


def test_health_state():
    # act & assert:
    with fake_tango_system(CentralNode) as tango_context:
        assert tango_context.device.healthState == HealthState.OK


# Need to check the failure
def test_activity_message_attribute_captures_the_last_received_command():
    # act & assert:
    with fake_tango_system(CentralNode)as tango_context:
        dut = tango_context.device
        dut.StartUpTelescope()
        assert_activity_message(dut, STR_ON_CMD_ISSUED)

        dut.StandByTelescope()
        assert_activity_message(dut, STR_STANDBY_CMD_ISSUED)


# Test cases for commands
def test_stow_antennas_should_set_stow_mode_on_leaf_nodes():
    # arrange:
    dish_device_ids = [str(i).zfill(4) for i in range(1, 4)]
    fqdn_prefix = "ska_mid/tm_leaf_node/d"
    initial_dut_properties = {
        'DishLeafNodePrefix': fqdn_prefix,
        'NumDishes': len(dish_device_ids)
    }

    proxies_to_mock = { fqdn_prefix + device_id : Mock() for device_id in dish_device_ids }

    # act:
    with fake_tango_system(CentralNode, initial_dut_properties, proxies_to_mock) as tango_context:
        tango_context.device.StowAntennas(dish_device_ids)

    # assert:
        for proxy_mock in proxies_to_mock.values():
            proxy_mock.command_inout.assert_called_with(CMD_SET_STOW_MODE)


def test_stow_antennas_should_raise_devfailed_exception():
    # arrange:
    dish_device_ids = [str(i).zfill(4) for i in range(1, 4)]
    fqdn_prefix = "ska_mid/tm_leaf_node/d"
    initial_dut_properties = {
        'DishLeafNodePrefix': fqdn_prefix,
        'NumDishes': len(dish_device_ids)
    }

    proxies_to_mock = {fqdn_prefix + device_id: Mock() for device_id in dish_device_ids}
    # mock command_inout method to throw devfailed exception
    for proxy_mock in proxies_to_mock.values():
        proxy_mock.command_inout.side_effect = raise_devfailed_exception
    # act:
    with fake_tango_system(CentralNode, initial_dut_properties, proxies_to_mock) as tango_context:
        with pytest.raises(tango.DevFailed):
            tango_context.device.StowAntennas(dish_device_ids)
    # assert:
        assert const.ERR_EXE_STOW_CMD in tango_context.device.activityMessage


def test_stow_antennas_invalid_value():
    """Negative Test for StowAntennas"""
    # act
    with fake_tango_system(CentralNode) \
            as tango_context:
        argin = ["invalid_antenna", ]
        with pytest.raises(tango.DevFailed):
            tango_context.device.StowAntennas(argin)

        # assert:
        assert const.ERR_STOW_ARGIN in tango_context.device.activityMessage


# Mocking AssignResources command success response from SubarrayNode
def mock_subarray_call_assign_resources_success(arg1, arg2):
    arg = json.loads(assign_input_str)
    argout = [str(arg["dish"]["receptorIDList"])]
    return [ResultCode.STARTED, argout]


# Mocking ReleaseResources command success response from SubarrayNode
def mock_subarray_call_release_resources_success(arg1):
    argout = ["[]"]
    return [ResultCode.STARTED, argout]


def test_assign_resources():
    # arrange
    subarray1_fqdn = 'ska_mid/tm_subarray_node/1'
    tm_subarrays = []
    tm_subarrays.append(subarray1_fqdn)
    dut_properties = {
        'TMMidSubarrayNodes': tm_subarrays,
        'NumDishes' : 4
    }
    # For subarray node proxy creation MagicMock is used instead of Mock because when subarray proxy inout
    # is called it returns list of resources allocated where length of list need to be evaluated but Mock
    # does not support len function for returned object. Hence MagicMock which is a superset of Mock is used
    # which supports this facility.
    subarray1_proxy_mock = MagicMock()
    # mocking subarray device state as ON as per new state model
    subarray1_proxy_mock.DevState = DevState.ON
    proxies_to_mock = {
        subarray1_fqdn: subarray1_proxy_mock
    }
    receptorIDList_success = []
    receptorIDList_success.append("0001")
    dish = {}
    dish["receptorIDList_success"] = receptorIDList_success
    success_response = {}
    success_response["dish"] = dish

    # arrange:
    with fake_tango_system(CentralNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        device_proxy = tango_context.device
        subarray1_proxy_mock.command_inout.side_effect = mock_subarray_call_assign_resources_success
        message = device_proxy.AssignResources(assign_input_str)

    assert json.loads(message) == success_response


def test_assign_resources_should_raise_devfailed_exception_when_subarray_node_throws_devfailed_exception(mock_subarraynode_device):
    device_proxy, subarray1_proxy_mock, subarray1_fqdn, event_subscription_map = mock_subarraynode_device
    subarray1_proxy_mock.DevState = DevState.OFF
    subarray1_proxy_mock.command_inout.side_effect = raise_devfailed_exception_with_args
    with pytest.raises(tango.DevFailed) as df:
        device_proxy.AssignResources(assign_input_str)
    # assert:
    assert "Error occurred while assigning resources to the Subarray" in str(df)


def test_assign_resources_invalid_json_value():
    # act & assert:
    with fake_tango_system(CentralNode) as tango_context:
        with pytest.raises(tango.DevFailed) as df:
            tango_context.device.AssignResources(assign_release_invalid_str)

        # assert:
        assert const.STR_RESOURCE_ALLOCATION_FAILED in str(df.value)


def test_assign_resources_invalid_key():
    # act
    with fake_tango_system(CentralNode) \
            as tango_context:
        result = 'test'
        with pytest.raises(tango.DevFailed):
            result = tango_context.device.AssignResources(assign_invalid_key)

        # assert:
        assert 'test' in result


def test_assign_resources_raise_devfailed_when_reseource_reallocation():
    subarray1_fqdn = 'ska_mid/tm_subarray_node/1'
    subarray2_fqdn = 'ska_mid/tm_subarray_node/2'
    tm_subarrays = []
    tm_subarrays.append(subarray1_fqdn)
    tm_subarrays.append(subarray2_fqdn)
    dut_properties = {
        'TMMidSubarrayNodes': tm_subarrays,
        'NumDishes' : 4
    }
    # For subarray node proxy creation MagicMock is used instead of Mock because when subarray proxy inout
    # is called it returns list of resources allocated where length of list need to be evaluated but Mock
    # does not support len function for returned object. Hence MagicMock which is a superset of Mock is used
    # which supports this facility.
    subarray1_proxy_mock = MagicMock()
    subarray2_proxy_mock = MagicMock()
    # mocking subarray device state as ON as per new state model
    subarray1_proxy_mock.DevState = DevState.ON
    subarray2_proxy_mock.DevState = DevState.ON
    proxies_to_mock = {
        subarray1_fqdn: subarray1_proxy_mock,
        subarray2_fqdn: subarray2_proxy_mock
    }

    receptorIDList_success = []
    receptorIDList_success.append("0001")
    dish = {}
    dish["receptorIDList_success"] = receptorIDList_success
    success_response = {}
    success_response["dish"] = dish

    # arrange:
    with fake_tango_system(CentralNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        device_proxy=tango_context.device
        subarray1_proxy_mock.command_inout.side_effect = mock_subarray_call_assign_resources_success
        message = device_proxy.AssignResources(assign_input_str)
        assert json.loads(message) == success_response

    # act:
        with pytest.raises(tango.DevFailed) as df:
            reallocation_request = json.loads(assign_input_str)
            reallocation_request["subarrayID"] = 2
            device_proxy.AssignResources(json.dumps(reallocation_request))

    # assert:
    assert const.ERR_RECEPTOR_ID_REALLOCATION in str(df.value)


def test_release_resources():
    # arrange
    subarray1_fqdn = 'ska_mid/tm_subarray_node/1'
    tm_subarrays = []
    tm_subarrays.append(subarray1_fqdn)
    dut_properties = {
        'TMMidSubarrayNodes': tm_subarrays,
        'NumDishes': 4
    }
    # For subarray node proxy creation MagicMock is used instead of Mock because when subarray proxy inout
    # is called it returns list of resources allocated where length of list need to be evaluated but Mock
    # does not support len function for returned object. Hence MagicMock which is a superset of Mock is used
    # which supports this facility.
    subarray1_proxy_mock = MagicMock()
    # mocking subarray device state as ON as per new state model
    subarray1_proxy_mock.DevState = DevState.ON
    proxies_to_mock = {
        subarray1_fqdn: subarray1_proxy_mock
    }

    release_all_success = {"ReleaseAll": True, "receptorIDList": []}

    # arrange:
    with fake_tango_system(CentralNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        device_proxy = tango_context.device
        subarray1_proxy_mock.command_inout.side_effect = mock_subarray_call_release_resources_success
        message = device_proxy.ReleaseResources(release_input_str)

        #assert
        assert json.dumps(release_all_success) in message


def test_release_resources_should_raise_devfailed_exception():
    # arrange
    subarray1_fqdn = 'ska_mid/tm_subarray_node/1'
    dut_properties = {
        'TMMidSubarrayNodes': subarray1_fqdn
    }

    # For subarray node proxy creation MagicMock is used instead of Mock because when subarray proxy inout
    # is called it returns list of resources allocated where length of list need to be evaluated but Mock
    # does not support len function for returned object. Hence MagicMock which is a superset of Mock is used
    # which supports this facility.
    subarray1_proxy_mock = MagicMock()
    subarray1_proxy_mock.DevState = DevState.ON
    subarray1_proxy_mock.receptorIDList = [1]
    proxies_to_mock = {
        subarray1_fqdn: subarray1_proxy_mock
    }
    subarray1_proxy_mock.command_inout.side_effect = raise_devfailed_exception
    with fake_tango_system(CentralNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        # act:
        with pytest.raises(tango.DevFailed) as df:
            tango_context.device.ReleaseResources(release_input_str)

        # assert:
        assert "Error occurred while releasing resources from the Subarray" in str(df.value)


def test_release_resources_invalid_json_value():
    # act
    with fake_tango_system(CentralNode) as tango_context:
        with pytest.raises(tango.DevFailed) as df:
            tango_context.device.ReleaseResources(assign_release_invalid_str)

        # assert:
        assert "Invalid JSON format" in str(df.value)


def test_release_resources_invalid_key():
    # act
    with fake_tango_system(CentralNode) as tango_context:
        with pytest.raises(tango.DevFailed) as df:
            tango_context.device.ReleaseResources(release_invalid_key)
        # assert:
        assert "JSON key not found" in str(df.value)


def test_standby(mock_central_lower_devices):
    # arrange:
    device_proxy, subarray1_proxy_mock, dish_ln1_proxy_mock, csp_master_ln_proxy_mock, sdp_master_ln_proxy_mock = mock_central_lower_devices
    # act:
    device_proxy.StartUpTelescope()
    assert device_proxy.state() == DevState.ON
    device_proxy.StandByTelescope()

    # assert:
    dish_ln1_proxy_mock.command_inout.assert_called_with(const.CMD_OFF)
    csp_master_ln_proxy_mock.command_inout.assert_called_with(const.CMD_STANDBY, [])
    sdp_master_ln_proxy_mock.command_inout.assert_called_with(const.CMD_STANDBY)
    subarray1_proxy_mock.command_inout.assert_called_with(const.CMD_OFF)
    assert device_proxy.state() == DevState.OFF


def test_standby_should_raise_devfailed_exception(mock_central_lower_devices):
    device_proxy, subarray1_proxy_mock, dish_ln1_proxy_mock, csp_master_ln_proxy_mock, sdp_master_ln_proxy_mock = mock_central_lower_devices
    dish_ln1_proxy_mock.command_inout.side_effect = raise_devfailed_exception
    csp_master_ln_proxy_mock.command_inout.side_effect = raise_devfailed_exception_with_args
    sdp_master_ln_proxy_mock.command_inout.side_effect = raise_devfailed_exception
    subarray1_proxy_mock.command_inout.side_effect = raise_devfailed_exception

    with pytest.raises(tango.DevFailed):
        device_proxy.StandByTelescope()

    # assert:
    assert device_proxy.state() == DevState.FAULT


def test_startup(mock_central_lower_devices):
    device_proxy, subarray1_proxy_mock, dish_ln1_proxy_mock, csp_master_ln_proxy_mock, sdp_master_ln_proxy_mock = mock_central_lower_devices
    # act:
    device_proxy.StartUpTelescope()
    # assert:
    dish_ln1_proxy_mock.command_inout.assert_called_with(const.CMD_SET_OPERATE_MODE)
    csp_master_ln_proxy_mock.command_inout.assert_called_with(const.CMD_ON)
    sdp_master_ln_proxy_mock.command_inout.assert_called_with(const.CMD_ON)
    subarray1_proxy_mock.command_inout.assert_called_with(const.CMD_ON)
    assert device_proxy.state() == DevState.ON


def test_startup_should_raise_devfailed_exception(mock_central_lower_devices):
    device_proxy, subarray1_proxy_mock, dish_ln1_proxy_mock, csp_master_ln_proxy_mock, sdp_master_ln_proxy_mock = mock_central_lower_devices
    dish_ln1_proxy_mock.command_inout.side_effect = raise_devfailed_exception
    csp_master_ln_proxy_mock.command_inout.side_effect = raise_devfailed_exception_with_args
    sdp_master_ln_proxy_mock.command_inout.side_effect = raise_devfailed_exception
    subarray1_proxy_mock.command_inout.side_effect = raise_devfailed_exception
    with pytest.raises(tango.DevFailed):
        device_proxy.StartUpTelescope()

    # assert:
    assert device_proxy.state() == DevState.FAULT


# Test cases for Telescope Health State
def test_telescope_health_state_matches_csp_master_leaf_node_health_state_after_start(
    central_node_test_info):
    initial_dut_properties = central_node_test_info['initial_dut_properties']
    proxies_to_mock = central_node_test_info['proxies_to_mock']
    csp_master_ln_fqdn = central_node_test_info['csp_master_ln_fqdn']
    event_subscription_map = central_node_test_info['event_subscription_map']
    csp_master_ln_health_state = central_node_test_info['csp_master_ln_health_state']
    csp_master_ln_health_attribute = central_node_test_info['csp_master_ln_health_attribute']

    with fake_tango_system(CentralNode, initial_dut_properties, proxies_to_mock) as tango_context:
        # act:
        dummy_event = create_dummy_event(csp_master_ln_fqdn, csp_master_ln_health_state)
        event_subscription_map[csp_master_ln_health_attribute](dummy_event)

        # assert:
        assert tango_context.device.telescopeHealthState == csp_master_ln_health_state


def test_telescope_health_state_is_ok_when_sdp_master_leaf_node_is_ok_after_start():
    # arrange:
    sdp_master_ln_fqdn = 'ska_mid/tm_leaf_node/sdp_master'
    csp_master_ln_fqdn = 'ska_mid/tm_leaf_node/csp_master'

    sdp_master_ln_health_attribute = 'sdpHealthState'
    initial_dut_properties = {
        'CspMasterLeafNodeFQDN': csp_master_ln_fqdn,
        'SdpMasterLeafNodeFQDN': sdp_master_ln_fqdn
    }

    event_subscription_map = {}
    sdp_master_ln_proxy_mock = Mock()
    sdp_master_ln_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args,
               **kwargs: event_subscription_map.update({attr_name: callback}))

    proxies_to_mock = {
        sdp_master_ln_fqdn: sdp_master_ln_proxy_mock
    }

    with fake_tango_system(CentralNode, initial_dut_properties, proxies_to_mock) as tango_context:
        # act:
        dummy_event = create_dummy_event(sdp_master_ln_fqdn, HealthState.OK)
        event_subscription_map[sdp_master_ln_health_attribute](dummy_event)
        # assert:
        assert tango_context.device.telescopeHealthState == HealthState.OK


def test_telescope_health_state_is_ok_when_subarray_leaf_node_is_ok_after_start(mock_subarraynode_device):
    device_proxy , subarray1_device_proxy_mock, subarray1_fqdn, event_subscription_map = mock_subarraynode_device
    subarray1_health_attribute = 'healthState'
    dummy_event = create_dummy_event(subarray1_fqdn, HealthState.OK)
    event_subscription_map[subarray1_health_attribute](dummy_event)
    # assert:
    assert device_proxy.telescopeHealthState == HealthState.OK


def test_telescope_health_state_is_ok_when_subarray2_leaf_node_is_ok_after_start():
    # arrange:
    subarray2_fqdn = 'ska_mid/tm_subarray_node/2'
    subarray2_health_attribute = 'healthState'
    initial_dut_properties = {
        'TMMidSubarrayNodes': subarray2_fqdn
    }

    event_subscription_map = {}
    subarray2_device_proxy_mock = Mock()
    subarray2_device_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args,
               **kwargs: event_subscription_map.update({attr_name: callback}))

    proxies_to_mock = {
        subarray2_fqdn: subarray2_device_proxy_mock
    }

    with fake_tango_system(CentralNode, initial_dut_properties, proxies_to_mock) as tango_context:
        # act:
        dummy_event = create_dummy_event(subarray2_fqdn, HealthState.OK)
        event_subscription_map[subarray2_health_attribute](dummy_event)

        # assert:
        assert tango_context.device.telescopeHealthState == HealthState.OK


def test_telescope_health_state_is_ok_when_subarray3_leaf_node_is_ok_after_start():
    # arrange:
    subarray3_fqdn = 'ska_mid/tm_subarray_node/3'
    subarray3_health_attribute = 'healthState'
    initial_dut_properties = {
        'TMMidSubarrayNodes': subarray3_fqdn
    }

    event_subscription_map = {}
    subarray3_device_proxy_mock = Mock()
    subarray3_device_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args,
               **kwargs: event_subscription_map.update({attr_name: callback}))

    proxies_to_mock = {
        subarray3_fqdn: subarray3_device_proxy_mock
    }

    with fake_tango_system(CentralNode, initial_dut_properties, proxies_to_mock) as tango_context:
        # act:
        dummy_event = create_dummy_event(subarray3_fqdn, HealthState.OK)
        event_subscription_map[subarray3_health_attribute](dummy_event)

        # assert:
        assert tango_context.device.telescopeHealthState == HealthState.OK


def create_dummy_event(device_fqdn, health_state):
    fake_event = Mock()
    fake_event.err = False
    fake_event.attr_name = f"{device_fqdn}/healthState"
    fake_event.attr_value.value = health_state
    return fake_event


def assert_activity_message(dut, expected_message):
    assert dut.activityMessage == expected_message # reads tango attribute


# Throw Devfailed exception for command without argument
def raise_devfailed_exception(cmd_name):
    tango.Except.throw_exception("CentralNode_Commandfailed", "This is error message for devfailed",
                                 " ", tango.ErrSeverity.ERR)


# Throw Devfailed exception for command with argument
def raise_devfailed_exception_with_args(cmd_name, input_args):
    tango.Except.throw_exception("CentralNode_Commandfailed", "This is error message for devfailed",
                                 " ", tango.ErrSeverity.ERR)

def test_version_id():
    """Test for versionId"""
    with fake_tango_system(CentralNode) as tango_context:
        assert tango_context.device.versionId == release.version


def test_build_state():
    """Test for buildState"""
    with fake_tango_system(CentralNode) as tango_context:
        assert tango_context.device.buildState == ('{},{},{}'.format(release.name,release.version,release.description))


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
