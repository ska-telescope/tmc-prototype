# Standard Python imports
import contextlib
import importlib
import sys
import types
import mock
import pytest
from mock import Mock, MagicMock

# Tango imports
import tango
from tango.test_context import DeviceTestContext
from tango import DevState, DevFailed

# Additional import
from sdpmasterleafnode import SdpMasterLeafNode, const, release
from ska.base.control_model import HealthState, AdminMode, TestMode, SimulationMode, ControlMode
from ska.base.control_model import LoggingLevel


@pytest.fixture(scope="function")
def tango_context():
    with fake_tango_system(SdpMasterLeafNode) as tango_context:
        yield tango_context


@pytest.fixture(scope="function")
def event_subscription(mock_sdp_master):
    event_subscription_map = {}
    mock_sdp_master[1].command_inout_asynch.side_effect = (
        lambda command_name, callback, *args,
               **kwargs: event_subscription_map.update({command_name: callback}))
    yield event_subscription_map


@pytest.fixture(scope="function")
def mock_sdp_master():
    sdp_master_fqdn = 'mid_sdp/elt/master'
    dut_properties = {'SdpMasterFQDN': sdp_master_fqdn}
    sdp_master_proxy_mock = Mock()
    proxies_to_mock = {sdp_master_fqdn: sdp_master_proxy_mock}
    with fake_tango_system(SdpMasterLeafNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        yield tango_context.device, sdp_master_proxy_mock


@pytest.fixture(
    scope="function",
    params=[
        ("On", const.CMD_ON),
        ("Standby", const.CMD_STANDBY),
        ("Disable", const.CMD_Disable)
    ])
def command_without_args(request):
    cmd_name, requested_cmd = request.param
    return cmd_name, requested_cmd


def test_command_should_be_relayed_to_sdp_master(mock_sdp_master, command_without_args):
    device_proxy, sdp_master_proxy_mock = mock_sdp_master
    cmd_name, requested_cmd = command_without_args
    
    device_proxy.command_inout(cmd_name)

    callback_name = f"{requested_cmd.lower()}_cmd_ended_cb"
    sdp_master_proxy_mock.command_inout_asynch.assert_called_with(requested_cmd,
                                                           any_method(with_name= callback_name))

def test_off_should_command_sdp_master_leaf_node_to_stop(mock_sdp_master):
    device_proxy, sdp_master_proxy_mock = mock_sdp_master
    device_proxy.On()

    device_proxy.Off()

    assert const.STR_OFF_CMD_SUCCESS in device_proxy.activityMessage
    sdp_master_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_OFF,
                                                               any_method(with_name='off_cmd_ended_cb'))


def test_disable_should_command_sdp_master_leaf_node_to_disable_devfailed(mock_sdp_master):
    device_proxy, sdp_master_proxy_mock = mock_sdp_master
    device_proxy.On()
    device_proxy.DevState = DevState.FAULT
    with pytest.raises(tango.DevFailed) as df:
        device_proxy.Disable()
    assert "Failed to invoke Disable command on SdpMasterLeafNode." in str(df)


def test_on_command_should_raise_dev_failed(mock_sdp_master):
    device_proxy, sdp_master_proxy_mock = mock_sdp_master
    sdp_master_proxy_mock.command_inout_asynch.side_effect = raise_devfailed_without_arg
    with pytest.raises(tango.DevFailed) as df:
        device_proxy.On()    
    print("Value of DF in on command::::",str(df))
    assert const.ERR_DEVFAILED_MSG in str(df)

@pytest.fixture(
    scope="function",
    params=[
        ("Off", const.ERR_OFF_CMD_FAIL),
        ("Disable", const.ERR_DISABLE_CMD_FAIL),
        ("Standby", const.ERR_STANDBY_CMD_FAIL),
        ])

def command_name_to_raise_devfailed(request):
    cmd_name, error_msg = request.param
    return cmd_name, error_msg


def test_command_should_raise_exception(mock_sdp_master, command_name_to_raise_devfailed):
    device_proxy, sdp_master_proxy_mock = mock_sdp_master
    cmd_name, error_msg = command_name_to_raise_devfailed
    device_proxy.On()
    sdp_master_proxy_mock.command_inout_asynch.side_effect = raise_devfailed_without_arg
    with pytest.raises(tango.DevFailed) as df:
        tango_context.device.command_inout(cmd_name)
    print("Value of DF in other commands::::",str(df))
    assert error_msg in str(df)


def raise_devfailed_without_arg(cmd_name, input_arg1):
    # "This function is called to raise DevFailed exception without arguments."
    tango.Except.throw_exception(const.STR_CMD_FAILED, const.ERR_DEVFAILED_MSG,
                                 cmd_name, tango.ErrSeverity.ERR)


def test_command_should_command_with_callback_method(mock_sdp_master, event_subscription, command_without_args):
    device_proxy, sdp_master_proxy_mock = mock_sdp_master
    cmd_name, requested_cmd = command_without_args
    
    device_proxy.command_inout(cmd_name)
    dummy_event = command_callback(requested_cmd)
    event_subscription[requested_cmd](dummy_event)

    assert const.STR_COMMAND + requested_cmd in device_proxy.activityMessage


def test_off_should_command_with_callback_method(mock_sdp_master, event_subscription):
    device_proxy, sdp_master_proxy_mock = mock_sdp_master
    device_proxy.On()
    
    device_proxy.Off()
    dummy_event = command_callback(const.CMD_OFF)
    event_subscription[const.CMD_OFF](dummy_event)
    
    assert const.STR_COMMAND + const.CMD_OFF in device_proxy.activityMessage



def test_command_with_callback_method_with_event_error(mock_sdp_master, event_subscription, command_without_args):
    device_proxy, sdp_master_proxy_mock = mock_sdp_master
    cmd_name, requested_cmd = command_without_args

    device_proxy.command_inout(cmd_name)
    dummy_event = command_callback_with_event_error(requested_cmd)
    event_subscription[requested_cmd](dummy_event)

    assert const.ERR_INVOKING_CMD + requested_cmd in device_proxy.activityMessage


def test_off_should_command_with_callback_method_with_event_error(mock_sdp_master, event_subscription):
    device_proxy, sdp_master_proxy_mock = mock_sdp_master
    device_proxy.On()
    
    device_proxy.Off()
    dummy_event = command_callback_with_event_error(const.CMD_OFF)
    event_subscription[const.CMD_OFF](dummy_event)
   
    assert const.ERR_INVOKING_CMD + const.CMD_OFF in device_proxy.activityMessage


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


def command_callback_with_command_exception():
    return Exception("Exception in Command callback")


def test_activity_message(tango_context):
    tango_context.device.activityMessage = "text"
    assert tango_context.device.activityMessage == "text"


def test_version_info(tango_context):
    assert tango_context.device.versionInfo == '1.0'


def test_processing_block_list(tango_context):
    assert tango_context.device.ProcessingBlockList


def test_status(tango_context):
    assert tango_context.device.Status() != const.STR_INIT_SUCCESS


def test_logging_level(tango_context):
    tango_context.device.loggingLevel = LoggingLevel.INFO
    assert tango_context.device.loggingLevel == LoggingLevel.INFO


def test_logging_targets(tango_context):
    tango_context.device.loggingTargets = ['console::cout']
    assert 'console::cout' in tango_context.device.loggingTargets


def test_test_mode(tango_context):
    test_mode = TestMode.NONE
    tango_context.device.testMode = test_mode
    assert tango_context.device.testMode == test_mode


def test_simulation_mode(tango_context):
    tango_context.device.simulationMode = SimulationMode.FALSE
    assert tango_context.device.simulationMode == SimulationMode.FALSE


def test_control_mode(tango_context):
    control_mode = ControlMode.REMOTE
    tango_context.device.controlMode = control_mode
    assert tango_context.device.controlMode == control_mode


def test_health_state(tango_context):
    assert tango_context.device.healthState == HealthState.OK


def test_version_id(tango_context):
    """Test for versionId"""
    assert tango_context.device.versionId == release.version


def test_build_state(tango_context):
    """Test for buildState"""
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