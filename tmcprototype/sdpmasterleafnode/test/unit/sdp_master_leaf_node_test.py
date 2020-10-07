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
        ("On", "" , const.CMD_ON, ""),
        ("Off", "" , const.CMD_OFF, ""),
        ("Standby", "", const.CMD_STANDBY, ""),
        ("Disable", "", const.CMD_Disable, "")
    ])
def command_with_arg(request):
    cmd_name, cmd_arg, requested_cmd, requested_cmd_arg = request.param
    return cmd_name, cmd_arg, requested_cmd, requested_cmd_arg


def test_command_should_be_relayed_to_sdp_master(mock_sdp_master, command_with_arg):
    # arrange:
    device_proxy, sdp_master_proxy_mock = mock_sdp_master
    cmd_name, cmd_arg, requested_cmd, requested_cmd_arg = command_with_arg
    if cmd_name == "Off":
        device_proxy.On()
    
    # act:
    device_proxy.command_inout(cmd_name)

    # assert:
    sdp_master_proxy_mock.command_inout_asynch.assert_called_with(requested_cmd,
                                                           any_method(with_name= requested_cmd.lower() + '_cmd_ended_cb'))


def test_disable_should_command_sdp_master_leaf_node_to_disable_devfailed(mock_sdp_master):
    # arrange:
    device_proxy, sdp_master_proxy_mock = mock_sdp_master
    device_proxy.On()
    device_proxy.DevState = DevState.FAULT
    # act:
    with pytest.raises(tango.DevFailed) as df:
        device_proxy.Disable()
    # assert:
    assert "Failed to invoke Disable command on SdpMasterLeafNode." in str(df)


def test_command_should_command_with_callback_method(mock_sdp_master, event_subscription, command_with_arg):
    # arrange:
    device_proxy, sdp_master_proxy_mock = mock_sdp_master
    cmd_name, cmd_arg, requested_cmd, requested_cmd_arg = command_with_arg
    if cmd_name == "Off":
        device_proxy.On()
    
    # act:
    device_proxy.command_inout(cmd_name)
    dummy_event = command_callback(requested_cmd)
    event_subscription[requested_cmd](dummy_event)

    # assert:
    assert const.STR_COMMAND + requested_cmd in device_proxy.activityMessage


def test_command_with_callback_method_with_event_error(mock_sdp_master, event_subscription, command_with_arg):
    # arrange:
    device_proxy, sdp_master_proxy_mock = mock_sdp_master
    cmd_name, cmd_arg, requested_cmd, requested_cmd_arg = command_with_arg
    if cmd_name == "Off":
        device_proxy.On()

    # act:
    device_proxy.command_inout(cmd_name)
    dummy_event = command_callback_with_event_error(requested_cmd)
    event_subscription[requested_cmd](dummy_event)

    # assert:
    assert const.ERR_INVOKING_CMD + requested_cmd in device_proxy.activityMessage


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
    # act & assert:
    tango_context.device.activityMessage = "text"
    assert tango_context.device.activityMessage == "text"


def test_version_info(tango_context):
    # act & assert:
    assert tango_context.device.versionInfo == '1.0'


def test_processing_block_list(tango_context):
    # act & assert:
    assert tango_context.device.ProcessingBlockList


def test_status(tango_context):
    # act & assert:
    assert tango_context.device.Status() != const.STR_INIT_SUCCESS


def test_logging_level(tango_context):
    # act & assert:
    tango_context.device.loggingLevel = LoggingLevel.INFO
    assert tango_context.device.loggingLevel == LoggingLevel.INFO


def test_logging_targets(tango_context):
    # act & assert:
    tango_context.device.loggingTargets = ['console::cout']
    assert 'console::cout' in tango_context.device.loggingTargets


def test_test_mode(tango_context):
    # act & assert:
    test_mode = TestMode.NONE
    tango_context.device.testMode = test_mode
    assert tango_context.device.testMode == test_mode


def test_simulation_mode(tango_context):
    # act & assert:
    tango_context.device.simulationMode = SimulationMode.FALSE
    assert tango_context.device.simulationMode == SimulationMode.FALSE


def test_control_mode(tango_context):
    # act & assert:
    control_mode = ControlMode.REMOTE
    tango_context.device.controlMode = control_mode
    assert tango_context.device.controlMode == control_mode


def test_health_state(tango_context):
    # act & assert:
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