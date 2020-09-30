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
from centralnodelow.const import CMD_SET_STOW_MODE, STR_ON_CMD_ISSUED, STR_STOW_CMD_ISSUED_CN, STR_STANDBY_CMD_ISSUED
from ska.base.control_model import HealthState, AdminMode, SimulationMode, ControlMode, TestMode
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
    release_input_str= f.read()

invalid_json_Assign_Release_file='invalid_json_Assign_Release_Resources.json'
path= join(dirname(__file__), 'data', invalid_json_Assign_Release_file)
with open(path, 'r') as f:
    assign_release_invalid_str= f.read()

release_invalid_key_file='invalid_key_ReleaseResources.json'
path= join(dirname(__file__), 'data', release_invalid_key_file)
with open(path, 'r') as f:
    release_invalid_key=f.read()


@pytest.fixture(scope = 'function')
def mock_subarraynode_device():
    subarray1_fqdn = 'ska_low/tm_subarray_node/1'
    initial_dut_properties = {
        'TMLowSubarrayNodes': subarray1_fqdn
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
    proxies_to_mock = {
        mccs_master_ln_fqdn: mccs_master_ln_proxy_mock,
        subarray1_fqdn: subarray1_proxy_mock
    }
    with fake_tango_system(CentralNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        yield tango_context.device, subarray1_proxy_mock, mccs_master_ln_proxy_mock


@pytest.fixture( scope="function",
    params=[HealthState.DEGRADED, HealthState.OK, HealthState.UNKNOWN, HealthState.FAILED])
def central_node_test_info(request):
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
        assert tango_context.device.buildState == ('{},{},{}'.format(release.name,release.version,release.description))

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
# Mocking ReleaseResources command success response from SubarrayNode
def mock_subarray_call_release_resources_success(arg1):
    argout = ["[]"]
    return [ResultCode.STARTED, argout]


def test_assign_resources(mock_central_lower_devices):
    # arrange
    device_proxy, subarray1_proxy_mock, mccs_master_ln_proxy_mock = mock_central_lower_devices
    # mocking subarray device state as ON as per new state model
    subarray1_proxy_mock.DevState = DevState.ON
    # act
    device_proxy.AssignResources(assign_input_str)
    # assert
    subarray1_proxy_mock.command_inout.assert_called_with(const.CMD_ASSIGN_RESOURCES, assign_input_str_to_subarray)
    mccs_master_ln_proxy_mock.command_inout.assert_called_with(const.CMD_ASSIGN_RESOURCES, assign_input_str)


def test_assign_resources_should_raise_devfailed_exception_when_subarray_node_throws_devfailed_exception(mock_subarraynode_device):
    # arrange
    device_proxy, subarray1_proxy_mock, subarray1_fqdn, event_subscription_map = mock_subarraynode_device
    subarray1_proxy_mock.DevState = DevState.OFF
    subarray1_proxy_mock.command_inout.side_effect = raise_devfailed_exception_with_args
    # act
    with pytest.raises(tango.DevFailed) as df:
        device_proxy.AssignResources(assign_input_str)
    # assert
    assert "Error occurred while assigning resources to the Subarray" in str(df)


def test_assign_resources_invalid_json_value(mock_central_lower_devices):
    # arrange
    device_proxy, subarray1_proxy_mock, mccs_master_ln_proxy_mock = mock_central_lower_devices
    # act
    with pytest.raises(tango.DevFailed) as df:
        device_proxy.AssignResources(assign_release_invalid_str)

    # assert
    assert const.STR_RESOURCE_ALLOCATION_FAILED in str(df.value)

def test_release_resources(mock_central_lower_devices):
    # arrange
    device_proxy, subarray1_proxy_mock, mccs_master_ln_proxy_mock = mock_central_lower_devices
    # mocking subarray device state as ON as per new state model
    subarray1_proxy_mock.DevState = DevState.ON

    # act:
    device_proxy.ReleaseResources(release_input_str)
    #assert
    subarray1_proxy_mock.command_inout.assert_called_with(const.CMD_RELEASE_RESOURCES, release_input_str)
    mccs_master_ln_proxy_mock.command_inout.assert_called_with(const.CMD_RELEASE_RESOURCES, release_input_str)


def test_release_resources_should_raise_devfailed_exception_when_subarray_node_throws_devfailed_exception(mock_subarraynode_device):
    # arrange
    device_proxy, subarray1_proxy_mock, subarray1_fqdn, event_subscription_map = mock_subarraynode_device
    subarray1_proxy_mock.DevState = DevState.OFF
    subarray1_proxy_mock.command_inout.side_effect = raise_devfailed_exception_with_args
   
    # act:
    with pytest.raises(tango.DevFailed) as df:
        device_proxy.ReleaseResources(release_input_str)

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
def test_telescope_health_state_matches_mccs_master_leaf_node_health_state_after_start(
    central_node_test_info):
    initial_dut_properties = central_node_test_info['initial_dut_properties']
    proxies_to_mock = central_node_test_info['proxies_to_mock']
    mccs_master_ln_fqdn = central_node_test_info['mccs_master_ln_fqdn']
    event_subscription_map = central_node_test_info['event_subscription_map']
    mccs_master_ln_health_state = central_node_test_info['mccs_master_ln_health_state']
    mccs_master_ln_health_attribute = central_node_test_info['mccs_master_ln_health_attribute']

    with fake_tango_system(CentralNode, initial_dut_properties, proxies_to_mock) as tango_context:
        # act:
        dummy_event = create_dummy_event(mccs_master_ln_fqdn, mccs_master_ln_health_state)
        event_subscription_map[mccs_master_ln_health_attribute](dummy_event)

        # assert:
        assert tango_context.device.telescopeHealthState == mccs_master_ln_health_state



def test_telescope_health_state_is_ok_when_subarray_node_is_ok_after_start(mock_subarraynode_device):
    device_proxy , subarray1_device_proxy_mock, subarray1_fqdn, event_subscription_map = mock_subarraynode_device
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
    print (fake_event)
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
