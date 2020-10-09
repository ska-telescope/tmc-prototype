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
from centralnodelow import CentralNode, const, release
from centralnodelow.const import STR_ON_CMD_ISSUED, STR_STANDBY_CMD_ISSUED
from ska.base.control_model import HealthState
from ska.base.control_model import LoggingLevel
from ska.base.commands import ResultCode

assign_input_file = 'command_AssignResources.json'
path = join(dirname(__file__), 'data', assign_input_file)
with open(path, 'r') as f:
    assign_input_str = f.read()

assign_input_file_to_subarray = 'command_AssignResources_subarray.json'
path = join(dirname(__file__), 'data', assign_input_file_to_subarray)
with open(path, 'r') as f:
    assign_input_str_to_subarray = f.read()

release_input_file='command_ReleaseResources.json'
path= join(dirname(__file__), 'data' , release_input_file)
with open(path, 'r') as f:
    release_input_str = f.read()

invalid_json_Assign_Release_file = 'invalid_json_Assign_Release_Resources.json'
path = join(dirname(__file__), 'data', invalid_json_Assign_Release_file)
with open(path, 'r') as f:
    assign_release_invalid_str = f.read()

assign_invalid_key_file='invalid_key_AssignResources.json'
path= join(dirname(__file__), 'data', assign_invalid_key_file)
with open(path, 'r') as f:
    assign_invalid_key=f.read()

release_invalid_key_file='invalid_key_ReleaseResources.json'
path= join(dirname(__file__), 'data', release_invalid_key_file)
with open(path, 'r') as f:
    release_invalid_key = f.read()


@pytest.fixture(scope='function')
def mock_central_lower_devices():
    mccs_master_ln_fqdn = 'ska_low/tm_leaf_node/mccs_master'
    subarray1_fqdn = 'ska_low/tm_subarray_node/1'

    dut_properties = {
        'MCCSMasterLeafNodeFQDN': mccs_master_ln_fqdn,
        'TMLowSubarrayNodes': subarray1_fqdn
    }
    # For subarray node and dish leaf node proxy creation MagicMock is used instead of Mock because when
    # proxy inout is called it returns list of resources allocated where length of list need to be evaluated
    # but Mock does not support len function for returned object. Hence MagicMock which is a superset of
    # Mock is used which supports this facility.
    mccs_master_ln_proxy_mock = Mock()
    subarray1_proxy_mock = MagicMock()

    event_subscription_map = {}
    subarray1_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args,
               **kwargs: event_subscription_map.update({attr_name: callback}))

    proxies_to_mock = {
        mccs_master_ln_fqdn: mccs_master_ln_proxy_mock,
        subarray1_fqdn: subarray1_proxy_mock
    }
    with fake_tango_system(CentralNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        yield tango_context.device, subarray1_proxy_mock, mccs_master_ln_proxy_mock, subarray1_fqdn, event_subscription_map


@pytest.fixture(scope="function",
                params=[HealthState.DEGRADED, HealthState.OK, HealthState.UNKNOWN, HealthState.FAILED])
def central_node_test_health_state(request):
    # arrange:
    device_under_test = CentralNode
    mccs_master_ln_fqdn = 'ska_low/tm_leaf_node/mccs_master'
    mccs_master_ln_health_attribute = 'mccsHealthState'

    initial_dut_properties = {
        'MCCSMasterLeafNodeFQDN': mccs_master_ln_fqdn
    }

    event_subscription_map = {}
    mccs_master_ln_proxy_mock = Mock()
    mccs_master_ln_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args, **kwargs:
        event_subscription_map.update({attr_name: callback}))

    proxies_to_mock = {
        mccs_master_ln_fqdn: mccs_master_ln_proxy_mock
    }

    test_info = {
        'mccs_master_ln_health_attribute': mccs_master_ln_health_attribute,
        'initial_dut_properties': initial_dut_properties,
        'proxies_to_mock': proxies_to_mock,
        'mccs_master_ln_health_state': request.param,
        'event_subscription_map': event_subscription_map,
        'mccs_master_ln_fqdn': mccs_master_ln_fqdn,
    }
    return test_info


@pytest.fixture(
    scope="function",
    params= [
        ("AssignResources",const.STR_RESOURCE_ALLOCATION_FAILED, assign_invalid_key),
        ("ReleaseResources",const.ERR_INVALID_JSON, release_invalid_key)
])
def command_raise_error(request):
    cmd_name,error_msg,input_str= request.param
    return cmd_name,error_msg,input_str

@pytest.fixture(
    scope="function",
    params= [
        ("StandByTelescope"),
        ("StartUpTelescope")
])
def command_with_devfailed_error(request):
    cmd_name= request.param
    return cmd_name


# Test cases for Attributes
def test_telescope_health_state():
    # act & assert:
    with fake_tango_system(CentralNode) as tango_context:
        assert tango_context.device.telescopeHealthState == HealthState.OK


def test_subarray1_health_state():
    # act & assert:
    with fake_tango_system(CentralNode) as tango_context:
        assert tango_context.device.subarray1HealthState == HealthState.OK


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


def test_health_state():
    # act & assert:
    with fake_tango_system(CentralNode) as tango_context:
        assert tango_context.device.healthState == HealthState.OK


def test_version_id():
    """Test for versionId"""
    with fake_tango_system(CentralNode) as tango_context:
        assert tango_context.device.versionId == release.version


def test_build_state():
    """Test for buildState"""
    with fake_tango_system(CentralNode) as tango_context:
        assert tango_context.device.buildState == (
            '{},{},{}'.format(release.name, release.version, release.description))


# Test cases for command
def test_assign_resources(mock_central_lower_devices):
    # arrange
    device_proxy, subarray1_proxy_mock, mccs_master_ln_proxy_mock, subarray1_fqdn, event_subscription_map = mock_central_lower_devices
    # mocking subarray device state as ON as per new state model
    subarray1_proxy_mock.DevState = DevState.ON
    mccs_master_ln_proxy_mock.DevState = DevState.ON
    
    # act
    device_proxy.AssignResources(assign_input_str)
    # assert
    subarray1_proxy_mock.command_inout.assert_called_with(const.CMD_ASSIGN_RESOURCES, assign_input_str_to_subarray)
    mccs_master_ln_proxy_mock.command_inout.assert_called_with(const.CMD_ASSIGN_RESOURCES, assign_input_str)

def test_assign_resources_should_raise_devfailed_exception_when_mccs_master_ln_throws_devfailed_exception(
        mock_central_lower_devices):
    # arrange
    device_proxy, subarray1_proxy_mock, mccs_master_ln_proxy_mock, subarray1_fqdn, event_subscription_map = mock_central_lower_devices
    mccs_master_ln_proxy_mock.DevState = DevState.OFF
    subarray1_proxy_mock.DevState = DevState.ON
    mccs_master_ln_proxy_mock.command_inout.side_effect = raise_devfailed_exception_with_args
    # act
    with pytest.raises(tango.DevFailed) as df:
        device_proxy.AssignResources(assign_input_str)
    # assert
    assert "Error occurred while assigning resources to the Subarray" in str(df)
    assert device_proxy.state() == DevState.FAULT

def test_assign_resources_should_raise_devfailed_exception_when_subarray_node_throws_devfailed_exception(
        mock_central_lower_devices):
    # arrange
    device_proxy, subarray1_proxy_mock, mccs_master_ln_proxy_mock, subarray1_fqdn, event_subscription_map = mock_central_lower_devices
    subarray1_proxy_mock.DevState = DevState.OFF
    mccs_master_ln_proxy_mock.DevState = DevState.ON
    subarray1_proxy_mock.command_inout.side_effect = raise_devfailed_exception_with_args
    # act
    with pytest.raises(tango.DevFailed) as df:
        device_proxy.AssignResources(assign_input_str)
    # assert
    assert "Error occurred while assigning resources to the Subarray" in str(df)
    assert device_proxy.state() == DevState.FAULT

def test_command_invalid_key(mock_central_lower_devices, command_raise_error):
    # arrange
    device_proxy, subarray1_proxy_mock, mccs_master_ln_proxy_mock, subarray1_fqdn, event_subscription_map = mock_central_lower_devices
    cmd_name,error_msg,input_str= command_raise_error
    subarray1_proxy_mock.DevState = DevState.ON
    mccs_master_ln_proxy_mock.DevState = DevState.ON
    # act
    with pytest.raises(tango.DevFailed) as df:
        device_proxy.command_inout(cmd_name,input_str)
    # assert:
    assert "JSON key not found" in str(df.value)

def test_command_invalid_json_value(mock_central_lower_devices,command_raise_error):
    # arrange
    device_proxy, subarray1_proxy_mock, mccs_master_ln_proxy_mock, subarray1_fqdn, event_subscription_map = mock_central_lower_devices
    cmd_name,error_msg,input_str= command_raise_error
    subarray1_proxy_mock.DevState = DevState.ON
    mccs_master_ln_proxy_mock.DevState = DevState.ON

    # act
    with pytest.raises(tango.DevFailed) as df:
        device_proxy.command_inout(cmd_name,assign_release_invalid_str)

    # assert
    assert error_msg in str(df.value)

def test_release_resources_should_raise_devfailed_exception_when_subarray_node_throws_devfailed_exception(
        mock_central_lower_devices):
    # arrange
    device_proxy, subarray1_proxy_mock, mccs_master_ln_proxy_mock, subarray1_fqdn, event_subscription_map = mock_central_lower_devices
    subarray1_proxy_mock.DevState = DevState.OFF
    mccs_master_ln_proxy_mock.DevState = DevState.ON

    subarray1_proxy_mock.command_inout.side_effect = raise_devfailed_exception

    # act:
    with pytest.raises(tango.DevFailed) as df:
        device_proxy.ReleaseResources(release_input_str)
    # assert:
    assert "Error occurred while releasing resources from the Subarray" in str(df.value)
    assert device_proxy.state() == DevState.FAULT

def test_release_resources_should_raise_devfailed_exception_when_mccs_master_ln_throws_devfailed_exception(
        mock_central_lower_devices):
    # arrange
    device_proxy, subarray1_proxy_mock, mccs_master_ln_proxy_mock, subarray1_fqdn, event_subscription_map = mock_central_lower_devices
    mccs_master_ln_proxy_mock.DevState = DevState.OFF
    subarray1_proxy_mock.DevState = DevState.ON
    
    mccs_master_ln_proxy_mock.command_inout.side_effect = raise_devfailed_exception_with_args
   
    # act:
    with pytest.raises(tango.DevFailed) as df:
        device_proxy.ReleaseResources(release_input_str)
    # assert:
    assert "Error occurred while releasing resources from the Subarray" in str(df.value)
    assert device_proxy.state() == DevState.FAULT


def test_standby(mock_central_lower_devices):
    # arrange:
    device_proxy, subarray1_proxy_mock, mccs_master_ln_proxy_mock, subarray1_fqdn, event_subscription_map = mock_central_lower_devices
    # act:
    device_proxy.StartUpTelescope()
    assert device_proxy.state() == DevState.ON
    device_proxy.StandByTelescope()

    # assert:
    mccs_master_ln_proxy_mock.command_inout.assert_called_with(const.CMD_OFF)
    subarray1_proxy_mock.command_inout.assert_called_with(const.CMD_OFF)
    assert device_proxy.state() == DevState.OFF


def test_startup(mock_central_lower_devices):
    device_proxy, subarray1_proxy_mock, mccs_master_ln_proxy_mock, subarray1_fqdn, event_subscription_map = mock_central_lower_devices
    # act:
    device_proxy.StartUpTelescope()
    # assert:
    mccs_master_ln_proxy_mock.command_inout.assert_called_with(const.CMD_ON)
    subarray1_proxy_mock.command_inout.assert_called_with(const.CMD_ON)
    assert device_proxy.state() == DevState.ON

def test_command_should_raise_devfailed_exception(mock_central_lower_devices,command_with_devfailed_error):
    device_proxy, subarray1_proxy_mock, mccs_master_ln_proxy_mock, subarray1_fqdn, event_subscription_map = mock_central_lower_devices
    cmd_name= command_with_devfailed_error
    mccs_master_ln_proxy_mock.command_inout.side_effect = raise_devfailed_exception
    subarray1_proxy_mock.command_inout.side_effect = raise_devfailed_exception
    with pytest.raises(tango.DevFailed):
        device_proxy.command_inout(cmd_name)
    # assert:
    assert device_proxy.state() == DevState.FAULT

# Test cases for Telescope Health State
def test_telescope_health_state_matches_mccs_master_leaf_node_health_state_after_start(
        central_node_test_health_state):
    initial_dut_properties = central_node_test_health_state['initial_dut_properties']
    proxies_to_mock = central_node_test_health_state['proxies_to_mock']
    mccs_master_ln_fqdn = central_node_test_health_state['mccs_master_ln_fqdn']
    event_subscription_map = central_node_test_health_state['event_subscription_map']
    mccs_master_ln_health_state = central_node_test_health_state['mccs_master_ln_health_state']
    mccs_master_ln_health_attribute = central_node_test_health_state['mccs_master_ln_health_attribute']

    with fake_tango_system(CentralNode, initial_dut_properties, proxies_to_mock) as tango_context:
        # act:
        dummy_event = create_dummy_event(mccs_master_ln_fqdn, mccs_master_ln_health_state)
        event_subscription_map[mccs_master_ln_health_attribute](dummy_event)

        # assert:
        assert tango_context.device.telescopeHealthState == mccs_master_ln_health_state

def test_telescope_health_state_is_ok_when_subarray_node_is_ok_after_start(mock_central_lower_devices):
    device_proxy, subarray1_proxy_mock, mccs_master_ln_proxy_mock, subarray1_fqdn, event_subscription_map = mock_central_lower_devices
    subarray1_health_attribute = 'healthState'
    dummy_event = create_dummy_event(subarray1_fqdn, HealthState.OK)
    event_subscription_map[subarray1_health_attribute](dummy_event)
    # assert:
    assert device_proxy.telescopeHealthState == HealthState.OK

def create_dummy_event(device_fqdn, health_state):
    fake_event = Mock()
    fake_event.err = False
    fake_event.attr_name = f"{device_fqdn}/healthState"
    fake_event.attr_value.value = health_state
    return fake_event

def assert_activity_message(dut, expected_message):
    assert dut.activityMessage == expected_message  # reads tango attribute


# Throw Devfailed exception for command without argument
def raise_devfailed_exception(cmd_name):
    tango.Except.throw_exception("CentralNode_Commandfailed", "This is error message for devfailed",
                                 " ", tango.ErrSeverity.ERR)

# Throw Devfailed exception for command with argument
def raise_devfailed_exception_with_args(cmd_name, input_args):
    tango.Except.throw_exception("CentralNode_Commandfailed", "This is error message for devfailed",
                                 " ", tango.ErrSeverity.ERR)

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
