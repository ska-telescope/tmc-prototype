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
from ska.base.control_model import (
    HealthState,
    AdminMode,
    TestMode,
    SimulationMode,
    ControlMode,
)
from ska.base.control_model import LoggingLevel
from ska.base.commands import ResultCode
from tmc.common.tango_client import TangoClient
from tmc.common.tango_server_helper import TangoServerHelper

@pytest.fixture(scope="function")
def mock_tango_server_helper():
    sdp_master_ln_fqdn = "mid_sdp/elt/master"
    tango_server_obj = TangoServerHelper.get_instance()
    tango_server_obj.read_property = Mock(return_value = sdp_master_ln_fqdn)
    yield tango_server_obj

@pytest.fixture(scope="function")
def tango_context():
    with fake_tango_system(SdpMasterLeafNode) as tango_context:
        yield tango_context

@pytest.fixture(scope="function")
def event_subscription_mock():
    dut_properties = {"SdpMasterFQDN": "mid_sdp/elt/master"}
    event_subscription_map = {}
    with mock.patch.object(
        TangoClient, "_get_deviceproxy", return_value=Mock()
    ) as mock_obj:
        tango_client_obj = TangoClient(dut_properties["SdpMasterFQDN"])
        tango_client_obj.deviceproxy.command_inout_asynch.side_effect = lambda command_name, arg, callback, *args, **kwargs: event_subscription_map.update(
            {command_name: callback}
        )
        yield event_subscription_map


@pytest.fixture(scope="function")
def mock_sdp_master_proxy():
    dut_properties = {"SdpMasterFQDN": "mid_sdp/elt/master"}
    event_subscription_map = {}
    Mock().subscribe_event.side_effect = lambda attr_name, event_type, callback, *args, **kwargs: event_subscription_map.update(
        {attr_name: callback}
    )
    with fake_tango_system(
        SdpMasterLeafNode, initial_dut_properties=dut_properties
    ) as tango_context:
        with mock.patch.object(
            TangoClient, "_get_deviceproxy", return_value=Mock()
        ) as mock_obj:
            tango_client_obj = TangoClient(dut_properties["SdpMasterFQDN"])
            yield tango_context.device, tango_client_obj, dut_properties[
                "SdpMasterFQDN"
            ], event_subscription_map


def raise_devfailed_exception(*args):
    # "This function is called to raise DevFailed exception without arguments."
    tango.Except.throw_exception(
        const.STR_CMD_FAILED, const.ERR_DEVFAILED_MSG, "", tango.ErrSeverity.ERR
    )


@pytest.fixture(
    scope="function",
    params=[
        ("TelescopeOn", const.CMD_TELESCOPE_ON, const.ERR_DEVFAILED_MSG),
        ("TelescopeStandby", const.CMD_TELESCOPE_STANDBY, const.ERR_DEVFAILED_MSG),
        ("Disable", const.CMD_Disable, const.ERR_DEVFAILED_MSG),
    ],
)
def command_without_args(request):
    cmd_name, requested_cmd, Err_msg = request.param
    return cmd_name, requested_cmd, Err_msg


def test_command_should_be_relayed_to_sdp_master(
    mock_sdp_master_proxy, command_without_args, mock_tango_server_helper 
):
    device_proxy, tango_client_obj = mock_sdp_master_proxy[:2]
    cmd_name, requested_cmd, _ = command_without_args
    device_proxy.command_inout(cmd_name)
    callback_name = f"{requested_cmd.lower()}_cmd_ended_cb"
    tango_client_obj.deviceproxy.command_inout_asynch.assert_called_with(
        requested_cmd, None, any_method(with_name=callback_name)
    )


def test_command_should_raise_exception(mock_sdp_master_proxy, command_without_args, mock_tango_server_helper):
    device_proxy, tango_client_obj = mock_sdp_master_proxy[:2]
    cmd_name, _, error_msg = command_without_args
    tango_client_obj.deviceproxy.command_inout_asynch.side_effect = (
        raise_devfailed_exception
    )
    with pytest.raises(tango.DevFailed) as df:
        device_proxy.command_inout(cmd_name)
    assert error_msg in str(df)


def test_on_should_command_sdp_master_leaf_node_to_start(mock_sdp_master_proxy, mock_tango_server_helper):
    device_proxy, tango_client_obj = mock_sdp_master_proxy[:2]
    device_proxy.TelescopeOn()
    tango_client_obj.deviceproxy.command_inout_asynch.assert_called_with(
        const.CMD_TELESCOPE_ON, None, any_method(with_name="telescopeon_cmd_ended_cb")
    )

def test_on_command_should_raise_dev_failed(mock_sdp_master_proxy, mock_tango_server_helper):
    device_proxy, tango_client_obj = mock_sdp_master_proxy[:2]
    tango_client_obj.deviceproxy.command_inout_asynch.side_effect = (
        raise_devfailed_exception
    )
    with pytest.raises(tango.DevFailed) as df:
        device_proxy.TelescopeOn()
    assert const.ERR_DEVFAILED_MSG in str(df)


def test_on_should_command_with_callback_method(
    mock_sdp_master_proxy, event_subscription_mock, mock_tango_server_helper
):
    device_proxy, tango_client_obj = mock_sdp_master_proxy[:2]
    device_proxy.TelescopeOn()
    dummy_event = command_callback(const.CMD_TELESCOPE_ON)
    event_subscription_mock[const.CMD_TELESCOPE_ON](dummy_event)
    assert const.STR_COMMAND + const.CMD_TELESCOPE_ON in device_proxy.activityMessage


def test_on_should_command_with_callback_method_with_event_error(
    mock_sdp_master_proxy, event_subscription_mock, mock_tango_server_helper
):
    device_proxy, tango_client_obj = mock_sdp_master_proxy[:2]
    device_proxy.TelescopeOn()
    dummy_event = command_callback_with_event_error(const.CMD_TELESCOPE_ON)
    event_subscription_mock[const.CMD_TELESCOPE_ON](dummy_event)
    assert const.ERR_INVOKING_CMD + const.CMD_TELESCOPE_ON in device_proxy.activityMessage


def test_off_should_command_with_callback_method_with_event_error(
    mock_sdp_master_proxy, event_subscription_mock, mock_tango_server_helper
):
    device_proxy, tango_client_obj = mock_sdp_master_proxy[:2]
    device_proxy.TelescopeOff()
    dummy_event = command_callback_with_event_error(const.CMD_TELESCOPE_OFF)
    event_subscription_mock[const.CMD_TELESCOPE_OFF](dummy_event)
    assert const.ERR_INVOKING_CMD + const.CMD_TELESCOPE_OFF in device_proxy.activityMessage


def test_off_should_command_sdp_master_leaf_node_to_stop(mock_sdp_master_proxy, mock_tango_server_helper):
    device_proxy, tango_client_obj = mock_sdp_master_proxy[:2]
    device_proxy.TelescopeOff()
    assert const.STR_TELESCOPE_OFF_CMD_SUCCESS in device_proxy.activityMessage


def test_off_command_should_raise_dev_failed(mock_sdp_master_proxy, mock_tango_server_helper):
    device_proxy, tango_client_obj = mock_sdp_master_proxy[:2]
    tango_client_obj.deviceproxy.command_inout_asynch.side_effect = (
        raise_devfailed_exception
    )
    with pytest.raises(tango.DevFailed) as df:
        device_proxy.TelescopeOff()
    assert const.ERR_DEVFAILED_MSG in str(df)


def test_off_should_command_with_callback_method(
    mock_sdp_master_proxy, event_subscription_mock, mock_tango_server_helper
):
    device_proxy, tango_client_obj = mock_sdp_master_proxy[:2]
    device_proxy.TelescopeOff()
    dummy_event = command_callback(const.CMD_TELESCOPE_OFF)
    event_subscription_mock[const.CMD_TELESCOPE_OFF](dummy_event)
    assert const.STR_COMMAND + const.CMD_TELESCOPE_OFF in device_proxy.activityMessage


def test_disable_should_command_sdp_master_leaf_node_to_disable_devfailed(
    mock_sdp_master_proxy, mock_tango_server_helper
):
    device_proxy, tango_client_obj = mock_sdp_master_proxy[:2]
    device_proxy.TelescopeOn()
    device_proxy.DevState = DevState.FAULT
    tango_client_obj.deviceproxy.command_inout_asynch.side_effect = (
        raise_devfailed_exception
    )
    with pytest.raises(tango.DevFailed) as df:
        device_proxy.Disable()
    assert const.ERR_DEVFAILED_MSG in str(df)


def test_command_should_command_with_callback_method(
    mock_sdp_master_proxy, event_subscription_mock, command_without_args, mock_tango_server_helper
):
    device_proxy, tango_client_obj = mock_sdp_master_proxy[:2]
    cmd_name, requested_cmd, _ = command_without_args
    device_proxy.command_inout(cmd_name)
    dummy_event = command_callback(requested_cmd)
    event_subscription_mock[requested_cmd](dummy_event)
    assert const.STR_COMMAND + requested_cmd in device_proxy.activityMessage


def test_command_with_callback_method_with_event_error(
    mock_sdp_master_proxy, event_subscription_mock, command_without_args, mock_tango_server_helper
):
    device_proxy, tango_client_obj = mock_sdp_master_proxy[:2]
    cmd_name, requested_cmd, _ = command_without_args
    device_proxy.command_inout(cmd_name)
    dummy_event = command_callback_with_event_error(requested_cmd)
    event_subscription_mock[requested_cmd](dummy_event)
    assert const.ERR_INVOKING_CMD + requested_cmd in device_proxy.activityMessage


def command_callback(command_name):
    fake_event = MagicMock()
    fake_event.err = False
    fake_event.cmd_name = f"{command_name}"
    return fake_event


def command_callback_with_event_error(command_name):
    fake_event = MagicMock()
    fake_event.err = True
    fake_event.errors = "Event error in Command Callback"
    fake_event.cmd_name = f"{command_name}"
    return fake_event


def command_callback_with_command_exception():
    return Exception("Exception in Command callback")


def test_activity_message(tango_context):
    tango_context.device.activityMessage = "text"
    assert tango_context.device.activityMessage == "text"


def test_processing_block_list(tango_context):
    assert tango_context.device.ProcessingBlockList


def test_status(tango_context):
    assert tango_context.device.Status() != const.STR_INIT_SUCCESS


def test_logging_level(tango_context):
    tango_context.device.loggingLevel = LoggingLevel.INFO
    assert tango_context.device.loggingLevel == LoggingLevel.INFO


def test_logging_targets(tango_context):
    tango_context.device.loggingTargets = ["console::cout"]
    assert "console::cout" in tango_context.device.loggingTargets


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


#
def test_health_state(tango_context):
    assert tango_context.device.healthState == HealthState.OK


def test_version_id():
    """Test for versionId"""
    with fake_tango_system(SdpMasterLeafNode) as tango_context:
        assert tango_context.device.versionId == release.version


def test_build_state():
    """Test for buildState"""
    with fake_tango_system(SdpMasterLeafNode) as tango_context:
        assert tango_context.device.buildState == (
            "{},{},{}".format(release.name, release.version, release.description)
        )


def any_method(with_name=None):
    class AnyMethod:
        def __eq__(self, other):
            if not isinstance(other, types.MethodType):
                return False

            return other.__func__.__name__ == with_name if with_name else True

    return AnyMethod()


@contextlib.contextmanager
def fake_tango_system(
    device_under_test,
    initial_dut_properties={},
    proxies_to_mock={},
    device_proxy_import_path="tango.DeviceProxy",
):
    with mock.patch(device_proxy_import_path) as patched_constructor:
        patched_constructor.side_effect = lambda device_fqdn: proxies_to_mock.get(
            device_fqdn, Mock()
        )
        patched_module = importlib.reload(sys.modules[device_under_test.__module__])

    device_under_test = getattr(patched_module, device_under_test.__name__)

    device_test_context = DeviceTestContext(
        device_under_test, properties=initial_dut_properties
    )
    device_test_context.start()
    yield device_test_context
    device_test_context.stop()
