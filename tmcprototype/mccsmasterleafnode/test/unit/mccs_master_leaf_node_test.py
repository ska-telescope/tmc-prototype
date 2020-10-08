# PROTECTED REGION ID(MccsMasterLeafNode.import) ENABLED START #

# Standard Python imports
import contextlib
import importlib
import types
import sys
import json
import mock
from mock import Mock, MagicMock
from os.path import dirname, join

# Tango imports
import pytest
import tango
from tango import DevState
from tango.test_context import DeviceTestContext

# Additional import
from mccsmasterleafnode import MccsMasterLeafNode, const, release
from ska.base.control_model import HealthState, ObsState
from ska.base.control_model import LoggingLevel

# PROTECTED REGION END #    //  MccsMasterLeafNode imports
assign_input_file = 'command_AssignResources.json'
path = join(dirname(__file__), 'data', assign_input_file)
with open(path, 'r') as f:
    assign_input_str = f.read()

assign_invalid_key_file = 'invalid_key_AssignResources.json'
path = join(dirname(__file__), 'data', assign_invalid_key_file)
with open(path, 'r') as f:
    assign_invalid_key = f.read()

release_input_file = 'command_ReleaseResources.json'
path = join(dirname(__file__), 'data', release_input_file)
with open(path, 'r') as f:
    release_input_str = f.read() 

@pytest.fixture(scope="function")
def mock_mccs_master():
    mccs_master_fqdn = 'low-mccs/control/control'
    dut_properties = {'MccsMasterFQDN': mccs_master_fqdn}
    event_subscription_map = {}
    mccs_master_proxy_mock = Mock()
    mccs_master_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args,
            **kwargs: event_subscription_map.update({attr_name: callback}))
    proxies_to_mock = {mccs_master_fqdn: mccs_master_proxy_mock}
    with fake_tango_system(MccsMasterLeafNode, initial_dut_properties=dut_properties,
                        proxies_to_mock=proxies_to_mock) as tango_context:
        yield mccs_master_proxy_mock, tango_context.device, mccs_master_fqdn, event_subscription_map

@pytest.fixture(scope="function")
def event_subscription(mock_mccs_master):
    event_subscription_map = {}
    mock_mccs_master[0].command_inout_asynch.side_effect = (
        lambda command_name, arg, callback, *args,
            **kwargs: event_subscription_map.update({command_name: callback}))
    yield event_subscription_map

@pytest.fixture(scope="function")
def event_subscription_without_arg(mock_mccs_master):
    event_subscription_map = {}
    mock_mccs_master[0].command_inout_asynch.side_effect = (
        lambda command_name, callback, *args,
            **kwargs: event_subscription_map.update({command_name: callback}))
    yield event_subscription_map

@pytest.fixture(scope="function")
def tango_context():
    with fake_tango_system(MccsMasterLeafNode) as tango_context:
        yield tango_context

@pytest.fixture(
    scope="function",
    params= [
        ("AssignResources",const.CMD_ALLOCATE,assign_input_str,ObsState.EMPTY),
        ("ReleaseResources",const.CMD_Release,release_input_str,ObsState.IDLE)
    ])
def command_with_arg(request):
    cmd_name, requested_cmd, input_str, obs_state=request.param
    return cmd_name, requested_cmd, input_str, obs_state

@pytest.fixture(
    scope="function",
    params= [
        ("AssignResources",assign_input_str,ObsState.EMPTY,const.ERR_DEVFAILED_MSG),
        ("ReleaseResources",release_input_str,ObsState.IDLE,const.ERR_RELEASE_ALL_RESOURCES)
])
def command_raise_devfailed_exception(request):
    cmd_name,input_str,obs_state,error_msg= request.param
    return cmd_name,input_str,obs_state,error_msg

def test_command_raise_devfailed_exception(mock_mccs_master,command_raise_devfailed_exception):
     mccs_master_proxy_mock, device_proxy, mccs_master_fqdn, event_subscription_map = mock_mccs_master
     cmd_name, input_str, obs_state, error_msg = command_raise_devfailed_exception
     mccs_master_proxy_mock.obsState = obs_state
     mccs_master_proxy_mock.command_inout_asynch.side_effect = raise_devfailed_with_arg
     with pytest.raises(tango.DevFailed) as df:
         device_proxy.command_inout(cmd_name, input_str)
     assert error_msg in str(df.value)

def test_command_invoke_with_command_callback_method(mock_mccs_master,event_subscription,command_with_arg):
    mccs_master_proxy_mock, device_proxy, mccs_master_fqdn, event_subscription_map = mock_mccs_master
    cmd_name, requested_cmd, input_str, obs_state = command_with_arg
    mccs_master_proxy_mock.obsState = obs_state
    device_proxy.command_inout(cmd_name,input_str)
    dummy_event = command_callback(requested_cmd)
    event_subscription[requested_cmd](dummy_event)
    assert const.STR_INVOKE_SUCCESS in device_proxy.activityMessage

def test_command_with_command_callback_event_error(mock_mccs_master,event_subscription,command_with_arg):
    mccs_master_proxy_mock, device_proxy, mccs_master_fqdn, event_subscription_map = mock_mccs_master
    cmd_name, requested_cmd, input_str, obs_state = command_with_arg
    mccs_master_proxy_mock.obsState = obs_state
    device_proxy.command_inout(cmd_name, input_str)
    dummy_event = command_callback_with_event_error(requested_cmd)
    event_subscription[requested_cmd](dummy_event)
    assert const.ERR_INVOKING_CMD + requested_cmd in device_proxy.activityMessage

def test_assign_command_with_callback_method_with_devfailed_error(mock_mccs_master, event_subscription):
    mccs_master_proxy_mock, device_proxy, mccs_master_fqdn, event_subscription_map = mock_mccs_master
    mccs_master_proxy_mock.obsState = ObsState.EMPTY
    with pytest.raises(tango.DevFailed) as df:
        device_proxy.AssignResources(assign_input_str)
        dummy_event = command_callback_with_devfailed_exception()
        event_subscription[const.CMD_ALLOCATE](dummy_event)
    assert const.ERR_CALLBACK_CMD_FAILED in str(df.value)

        
def test_release_resource_should_command_mccs_master_to_release_all_resources(mock_mccs_master):
    mccs_master_proxy_mock, device_proxy, mccs_master_fqdn, event_subscription_map = mock_mccs_master
    mccs_master_proxy_mock.obsState = ObsState.EMPTY
    device_proxy.On()
    device_proxy.AssignResources(assign_input_str)
    device_proxy.ReleaseResources(release_input_str)
    mccs_master_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_Release, release_input_str,
                                                                        any_method(
                                                                            with_name='releaseresources_cmd_ended_cb'))
    assert_activity_message(device_proxy, const.STR_REMOVE_ALL_RECEPTORS_SUCCESS)

def raise_devfailed_with_arg(cmd_name, input_arg1, inout_arg2):
    # "This function is called to raise DevFailed exception with arguments."
    tango.Except.throw_exception(const.STR_CMD_FAILED, const.ERR_DEVFAILED_MSG,
                                cmd_name, tango.ErrSeverity.ERR)

def raise_devfailed_exception(cmd_name, inp_str):
    # "This function is called to raise DevFailed exception."
    tango.Except.throw_exception("MccsMasterLeafNode_CommandFailed", const.ERR_DEVFAILED_MSG,
                                    " ", tango.ErrSeverity.ERR)

def test_on_should_command_mccs_master_leaf_node_to_start(mock_mccs_master):
    mccs_master_proxy_mock, device_proxy, mccs_master_fqdn, event_subscription_map = mock_mccs_master
    device_proxy.On()
    mccs_master_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_ON,
                                                                any_method(with_name='on_cmd_ended_cb'))


def test_on_should_command_to_on_with_callback_method(mock_mccs_master, event_subscription_without_arg):
    device_proxy=mock_mccs_master[1]
    device_proxy.On()
    dummy_event = command_callback(const.CMD_ON)
    event_subscription_without_arg[const.CMD_ON](dummy_event)
    assert const.STR_COMMAND + const.CMD_ON in device_proxy.activityMessage


def test_on_should_command_with_callback_method_with_event_error(mock_mccs_master, event_subscription_without_arg):
    device_proxy=mock_mccs_master[1]
    device_proxy.On()
    dummy_event = command_callback_with_event_error(const.CMD_ON)
    event_subscription_without_arg[const.CMD_ON](dummy_event)
    assert const.ERR_INVOKING_CMD + const.CMD_ON in device_proxy.activityMessage

def test_on_should_raise_devfailed_exception(mock_mccs_master):
    mccs_master_proxy_mock, device_proxy, mccs_master_fqdn, event_subscription_map = mock_mccs_master
    mccs_master_proxy_mock.obsState = ObsState.EMPTY
    mccs_master_proxy_mock.command_inout_asynch.side_effect = raise_devfailed_exception
    with pytest.raises(tango.DevFailed) as df:
        device_proxy.On()
    assert const.ERR_DEVFAILED_MSG in str(df.value)

def test_off_should_command_to_off_with_callback_method(mock_mccs_master):
    device_proxy=mock_mccs_master[1]
    device_proxy.On()
    device_proxy.Off()
    assert device_proxy.activityMessage in const.STR_OFF_CMD_ISSUED

def test_off_should_command_with_callback_method_with_event_error(mock_mccs_master ,event_subscription_without_arg):
    device_proxy=mock_mccs_master[1]
    device_proxy.On()
    device_proxy.Off()
    dummy_event = command_callback_with_event_error(const.CMD_OFF)
    event_subscription_without_arg[const.CMD_OFF](dummy_event)
    assert const.ERR_INVOKING_CMD + const.CMD_OFF in device_proxy.activityMessage

def test_off_should_raise_devfailed_exception(mock_mccs_master):
    mccs_master_proxy_mock, device_proxy, mccs_master_fqdn, event_subscription_map = mock_mccs_master
    mccs_master_proxy_mock.obsState = ObsState.EMPTY
    device_proxy.On()
    mccs_master_proxy_mock.command_inout_asynch.side_effect = raise_devfailed_exception
    with pytest.raises(tango.DevFailed) as df:
        device_proxy.Off()
    assert const.ERR_DEVFAILED_MSG in str(df.value)

def test_read_activity_message(tango_context):
    # test case for method read_activityMessage
    tango_context.device.activityMessage = 'test'
    assert_activity_message(tango_context.device, 'test')

def test_write_activity_message(tango_context):
    # test case for method write_activityMessage
    tango_context.device.activityMessage = 'test'
    assert_activity_message(tango_context.device, 'test')

def command_callback(command_name):
    fake_event = MagicMock()
    fake_event.err = False
    fake_event.cmd_name = f"{command_name}"
    return fake_event

def command_callback_with_event_error(command_name):
    fake_event = MagicMock()
    fake_event.err = True
    fake_event.errors = 'Event error in Command Callback'
    fake_event.cmd_name = f"{command_name}"
    return fake_event

def command_callback_with_devfailed_exception():
    # "This function is called when command is failed with DevFailed exception."
    tango.Except.throw_exception(const.ERR_DEVFAILED_MSG,
                                const.ERR_CALLBACK_CMD_FAILED, " ", tango.ErrSeverity.ERR)

def any_method(with_name=None):
    class AnyMethod():
        def __eq__(self, other):
            if not isinstance(other, types.MethodType):
                return False

            return other.__func__.__name__ == with_name if with_name else True

    return AnyMethod()

def assert_activity_message(device_proxy, expected_message):
    assert device_proxy.activityMessage == expected_message  # reads tango attribute

def raise_devfailed_exception(cmd_name, inp_str):
    # "This function is called to raise DevFailed exception."
    tango.Except.throw_exception("MccsMasterLeafNode_CommandFailed", const.ERR_DEVFAILED_MSG,
    " ", tango.ErrSeverity.ERR)

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