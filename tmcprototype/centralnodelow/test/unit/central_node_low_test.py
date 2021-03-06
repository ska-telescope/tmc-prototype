# Standard Python imports
import contextlib
import importlib
import sys
import types
import json
import pytest
import mock
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
from tmc.common.tango_client import TangoClient
from ska.base.commands import ResultCode
from centralnodelow.device_data import DeviceData



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

@pytest.fixture(scope = 'function')
def mock_subarraynode_proxy():
    subarray1_fqdn = 'ska_low/tm_subarray_node/1'
    dut_properties = {
        'TMLowSubarrayNodes':'ska_low/tm_subarray_node/1'
    }

    event_subscription_map = {}
    subarray1_device_proxy_mock = Mock()
    Mock().subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args,
               **kwargs: event_subscription_map.update({attr_name: callback}))

    with fake_tango_system(CentralNode, initial_dut_properties=dut_properties) as tango_context:
        with mock.patch.object(TangoClient, '_get_deviceproxy', return_value=Mock()) as mock_obj:
            tango_client_obj = TangoClient(dut_properties['TMLowSubarrayNodes'])
            yield tango_context.device, tango_client_obj, dut_properties['TMLowSubarrayNodes'], event_subscription_map


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

def test_assign_resources(mock_subarraynode_proxy):
    device_proxy, tango_client_obj = mock_subarraynode_proxy[:2]
    device_proxy.AssignResources(assign_input_str)
    assert const.STR_ASSIGN_RESOURCES_SUCCESS in device_proxy.activityMessage


def test_assign_resources_should_raise_devfailed_exception_when_subarray_node_throws_devfailed_exception(
        mock_subarraynode_proxy):
    device_proxy, tango_client_obj = mock_subarraynode_proxy[:2]
    tango_client_obj.deviceproxy.command_inout.side_effect = raise_devfailed_exception
    with pytest.raises(tango.DevFailed) as df:
        device_proxy.AssignResources(assign_input_str)
    assert "Error occurred while assigning resources to the Subarray" in str(df)
    assert device_proxy.state() == DevState.FAULT

def test_release_resources(mock_subarraynode_proxy):
    device_proxy, tango_client_obj = mock_subarraynode_proxy[:2]
    device_proxy.ReleaseResources(release_input_str)
    input_release = json.loads(release_input_str)
    input_release = json.dumps(input_release["mccs"])
    tango_client_obj.deviceproxy.command_inout.assert_called_with(const.CMD_RELEASE_MCCS_RESOURCES, input_release)


def test_release_resources_should_raise_devfailed_exception_when_subarray_node_throws_devfailed_exception(
        mock_subarraynode_proxy):
    device_proxy, tango_client_obj = mock_subarraynode_proxy[:2]
    tango_client_obj.deviceproxy.command_inout.side_effect = raise_devfailed_exception
    with pytest.raises(tango.DevFailed) as df:
        device_proxy.ReleaseResources(release_input_str)
    assert "Error occurred while releasing resources from the Subarray" in str(df.value)
    assert device_proxy.state() == DevState.FAULT

def test_command_invalid_key(mock_subarraynode_proxy, command_raise_error):
    device_proxy, tango_client_obj = mock_subarraynode_proxy[:2]
    cmd_name,error_msg,input_str= command_raise_error
    with pytest.raises(tango.DevFailed) as df:
        device_proxy.command_inout(cmd_name,input_str)
    assert const.ERR_JSON_KEY_NOT_FOUND in str(df.value)

def test_command_invalid_json_value(mock_subarraynode_proxy,command_raise_error):
    device_proxy, tango_client_obj = mock_subarraynode_proxy[:2]
    cmd_name,error_msg= command_raise_error[:2]
    with pytest.raises(tango.DevFailed) as df:
        device_proxy.command_inout(cmd_name, assign_release_invalid_str)
    assert error_msg in str(df.value)


def test_startup(mock_subarraynode_proxy):
    device_proxy, tango_client_obj = mock_subarraynode_proxy[:2]
    assert device_proxy.StartUpTelescope() == [[ResultCode.OK],[const.STR_ON_CMD_ISSUED]]
    assert device_proxy.state() == DevState.ON

def test_standby(mock_subarraynode_proxy):
    device_proxy, tango_client_obj = mock_subarraynode_proxy[:2]
    device_proxy.StartUpTelescope()
    assert device_proxy.StandByTelescope() == [[ResultCode.OK],[const.STR_STANDBY_CMD_ISSUED]]
    assert device_proxy.state() == DevState.OFF

def test_command_should_raise_devfailed_exception(mock_subarraynode_proxy,command_with_devfailed_error):
    device_proxy, tango_client_obj = mock_subarraynode_proxy[:2]
    cmd_name= command_with_devfailed_error
    tango_client_obj.deviceproxy.command_inout.side_effect = raise_devfailed_exception
    with pytest.raises(tango.DevFailed):
        device_proxy.command_inout(cmd_name)
    assert device_proxy.state() == DevState.FAULT

# Test cases for Attributes
def test_telescope_health_state():
    with fake_tango_system(CentralNode) as tango_context:
        assert tango_context.device.telescopeHealthState == HealthState.UNKNOWN


def test_subarray1_health_state():
    with fake_tango_system(CentralNode) as tango_context:
        assert tango_context.device.subarray1HealthState == HealthState.UNKNOWN


def test_activity_message():
    with fake_tango_system(CentralNode) as tango_context:
        tango_context.device.activityMessage = ''
        assert tango_context.device.activityMessage == ''


def test_logging_level():
    with fake_tango_system(CentralNode) as tango_context:
        tango_context.device.loggingLevel = LoggingLevel.INFO
        assert tango_context.device.loggingLevel == LoggingLevel.INFO


def test_logging_targets():
    with fake_tango_system(CentralNode) as tango_context:
        tango_context.device.loggingTargets = ['console::cout']
        assert 'console::cout' in tango_context.device.loggingTargets


def test_health_state():
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

def test_telescope_health_state_is_ok_when_subarray_node_is_ok_after_start(mock_subarraynode_proxy, health_state):
    device_proxy , tango_client_obj, subarray1_fqdn, event_subscription_map = mock_subarraynode_proxy
    device_data = DeviceData.get_instance()
    with mock.patch.object(TangoClient, '_get_deviceproxy', return_value=Mock()) as mock_obj:
        with mock.patch.object(TangoClient, "subscribe_attribute", side_effect=dummy_subscriber):
            tango_client_obj = TangoClient('ska_low/tm_subarray_node/1')
            device_proxy.StartUpTelescope()
    assert device_data._telescope_health_state == health_state


def dummy_subscriber(attribute, callback_method):
    fake_event = Mock()
    fake_event.err = False
    fake_event.attr_name = f"ska_low/tm_subarray_node/1/{attribute}"
    fake_event.attr_value.value =  HealthState.UNKNOWN
    print( fake_event.attr_value.value )

    callback_method(fake_event)
    return 10

@pytest.fixture(
    scope="function",
    params=[
        HealthState.UNKNOWN
    ])
def health_state(request):
    return request.param


def create_dummy_event(device_fqdn, health_state):
    fake_event = Mock()
    fake_event.err = False
    fake_event.attr_name = f"{device_fqdn}/healthState"
    fake_event.attr_value.value = health_state
    return fake_event

def assert_activity_message(dut, expected_message):
    assert dut.activityMessage == expected_message  # reads tango attribute


# Throw Devfailed exception for command with argument
def raise_devfailed_exception(*args):
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
