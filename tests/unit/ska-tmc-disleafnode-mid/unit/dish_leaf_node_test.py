import contextlib
import importlib
import json
import sys
import types
from os.path import dirname, join
from unittest import mock
from unittest.mock import MagicMock, Mock

import numpy as np
import pytest
import tango
from ska.base.control_model import (
    ControlMode,
    HealthState,
    LoggingLevel,
    SimulationMode,
    TestMode,
)
from tango.test_context import DeviceTestContext
from tmc.common.tango_client import TangoClient
from tmc.common.tango_server_helper import TangoServerHelper

from src.ska_tmc_dishleafnode_mid.src.ska_tmc_dishleafnode_mid import (
    DishLeafNode,
    const,
    release,
)
from src.ska_tmc_dishleafnode_mid.src.ska_tmc_dishleafnode_mid.device_data import (
    DeviceData,
)
from src.ska_tmc_dishleafnode_mid.src.ska_tmc_dishleafnode_mid.utils import (
    DishMode,
)

config_input_file = "command_Config.json"
path = join(dirname(__file__), "data", config_input_file)
with open(path, "r") as f:
    config_input_str = f.read()

invalid_arg_file = "invalid_json_argument_Configure.json"
path = join(dirname(__file__), "data", invalid_arg_file)
with open(path, "r") as f:
    configure_invalid_arg = f.read()

invalid_arg_file2 = "invalid_json_argument_Track.json"
path = join(dirname(__file__), "data", invalid_arg_file2)
with open(path, "r") as f:
    track_invalid_arg = f.read()

invalid_key_config_track_file = "invalid_key_Configure_Track.json"
path = join(dirname(__file__), "data", invalid_key_config_track_file)
with open(path, "r") as f:
    config_track_invalid_str = f.read()


@pytest.fixture(scope="function")
def mock_tango_server_helper():
    dish_master_fqdn = "mid_d0001/elt/master"
    tango_server_obj = TangoServerHelper.get_instance()
    tango_server_obj.read_property = Mock(return_value=dish_master_fqdn)
    yield tango_server_obj


@pytest.fixture(scope="function")
def mock_dish_master_proxy():
    dut_properties = {"DishMasterFQDN": "mid_d0001/elt/master"}
    event_subscription_map = {}
    Mock().subscribe_event.side_effect = lambda attr_name, event_type, callback, *args, **kwargs: event_subscription_map.update(
        {attr_name: callback}
    )
    with fake_tango_system(
        DishLeafNode, initial_dut_properties=dut_properties
    ) as tango_context:
        with mock.patch.object(
            TangoClient, "_get_deviceproxy", return_value=Mock()
        ):
            tango_client_obj = TangoClient(dut_properties["DishMasterFQDN"])
            yield tango_context.device, tango_client_obj, dut_properties[
                "DishMasterFQDN"
            ], event_subscription_map


@pytest.fixture(scope="function")
def event_subscription_mock():
    dut_properties = {"DishMasterFQDN": "mid_d0001/elt/master"}
    event_subscription_map = {}
    with mock.patch.object(
        TangoClient, "_get_deviceproxy", return_value=Mock()
    ):
        tango_client_obj = TangoClient(dut_properties["DishMasterFQDN"])
        tango_client_obj.deviceproxy.command_inout_asynch.side_effect = lambda command_name, arg, callback, *args, **kwargs: event_subscription_map.update(
            {command_name: callback}
        )
        yield event_subscription_map


@pytest.fixture(scope="function")
def event_subscription_attr_mock():
    dut_properties = {"DishMasterFQDN": "mid_d0001/elt/master"}
    event_subscription_map = {}
    with mock.patch.object(
        TangoClient, "_get_deviceproxy", return_value=Mock()
    ):
        tango_client_obj = TangoClient(dut_properties["DishMasterFQDN"])
        tango_client_obj.deviceproxy.subscribe_event.side_effect = lambda attr_name, event_type, callback, *args, **kwargs: event_subscription_map.update(
            {attr_name: callback}
        )
        yield event_subscription_map


device_data = DeviceData.get_instance()


@pytest.fixture(
    scope="function",
    params=[
        ("SetStandbyFPMode", "SetStandbyFPMode"),
        ("SetStowMode", "SetStowMode"),
        ("SetOperateMode", "SetOperateMode"),
        ("StopTrack", "TrackStop"),
        ("Abort", "TrackStop"),
        ("Restart", "StopCapture"),
    ],
)
def command_without_arg(request):
    cmd_name, requested_cmd = request.param
    return cmd_name, requested_cmd


def test_command_cb_is_invoked_when_command_without_arg_is_called_async(
    mock_dish_master_proxy, command_without_arg, mock_tango_server_helper
):
    device_proxy, dish1_proxy_mock, _, _ = mock_dish_master_proxy
    cmd_name, requested_cmd = command_without_arg

    device_proxy.command_inout(cmd_name)

    dish1_proxy_mock.deviceproxy.command_inout_asynch.assert_called_with(
        requested_cmd, None, any_method(with_name="cmd_ended_cb")
    )


def test_command_cb_is_invoked_when_standbylp_is_called_async(
    mock_dish_master_proxy, mock_tango_server_helper
):
    device_proxy, dish1_proxy_mock, _, _ = mock_dish_master_proxy

    cmd_name = "SetOperateMode"
    device_proxy.command_inout(cmd_name)
    cmd_name = "SetStandbyLPMode"
    device_proxy.command_inout(cmd_name)

    dish1_proxy_mock.deviceproxy.command_inout_asynch.assert_called_with(
        cmd_name, None, any_method(with_name="cmd_ended_cb")
    )


@pytest.fixture(
    scope="function",
    params=["SetStowMode", "SetOperateMode", "SetStandbyFPMode"],
)
def command_name(request):
    cmd_name = request.param
    return cmd_name


def test_activity_message_attribute_value_contains_command_name(
    mock_dish_master_proxy,
    event_subscription_mock,
    command_name,
    mock_tango_server_helper,
):
    device_proxy, _, _, _ = mock_dish_master_proxy
    device_proxy.command_inout(command_name)
    dummy_event = command_callback(command_name)
    event_subscription_mock[command_name](dummy_event)
    assert f"Command :-> {command_name}" in device_proxy.activityMessage


def test_activity_message_attribute_value_contains_command_name_with_event_error(
    mock_dish_master_proxy,
    event_subscription_mock,
    command_name,
    mock_tango_server_helper,
):
    device_proxy, _, _, _ = mock_dish_master_proxy
    device_proxy.command_inout(command_name)
    dummy_event = command_callback_with_event_error(command_name)
    event_subscription_mock[command_name](dummy_event)
    assert (
        f"Error in invoking command: {command_name}"
        in device_proxy.activityMessage
    )


def test_activity_message_attribute_value_contains_setstandbylpmode_command_name(
    mock_dish_master_proxy, event_subscription_mock, mock_tango_server_helper
):
    device_proxy, _, _, _ = mock_dish_master_proxy
    cmd_name = "SetOperateMode"
    device_proxy.command_inout(cmd_name)
    cmd_name = "SetStandbyLPMode"
    device_proxy.command_inout(cmd_name)
    dummy_event = command_callback(cmd_name)
    event_subscription_mock[cmd_name](dummy_event)
    assert f"Command :-> {cmd_name}" in device_proxy.activityMessage


def test_activity_message_attribute_value_contains_setstandbylpmode_command_name_with_event_error(
    mock_dish_master_proxy, event_subscription_mock, mock_tango_server_helper
):
    device_proxy, _, _, _ = mock_dish_master_proxy
    cmd_name = "SetOperateMode"
    device_proxy.command_inout(cmd_name)
    cmd_name = "SetStandbyLPMode"
    device_proxy.command_inout(cmd_name)
    dummy_event = command_callback_with_event_error(cmd_name)
    event_subscription_mock[cmd_name](dummy_event)
    assert (
        f"Error in invoking command: {cmd_name}"
        in device_proxy.activityMessage
    )


@pytest.fixture(
    scope="function",
    params=[
        ("Scan", "0.0", "Scan"),
        ("EndScan", "0.0", "StopCapture"),
        ("StartCapture", "0.0", "StartCapture"),
        ("StopCapture", "0.0", "StopCapture"),
    ],
)
def dish_leaf_node_command_with_arg(request):
    cmd_name, input_arg, requested_cmd = request.param
    return cmd_name, input_arg, requested_cmd


def test_dish_master_command_is_called_with_the_no_inputs_when_leaf_node_command_has_inputs(
    mock_dish_master_proxy,
    dish_leaf_node_command_with_arg,
    mock_tango_server_helper,
):
    device_proxy, dish1_proxy_mock, _, _ = mock_dish_master_proxy
    cmd_name, input_arg, requested_cmd = dish_leaf_node_command_with_arg
    device_proxy.command_inout(cmd_name, input_arg)


def test_configure_should_raise_exception_when_called_with_invalid_json(
    mock_tango_server_helper,
):
    with fake_tango_system(DishLeafNode) as tango_context:
        with pytest.raises(tango.DevFailed) as df:
            tango_context.device.Configure(config_track_invalid_str)
        assert const.ERR_INVALID_JSON in str(df.value)


def test_configure_should_raise_exception_when_called_with_invalid_arguments(
    mock_tango_server_helper,
):
    with fake_tango_system(DishLeafNode) as tango_context:
        input_string = []
        input_string.append(configure_invalid_arg)
        with pytest.raises(tango.DevFailed) as df:
            tango_context.device.Configure(input_string[0])
        assert const.ERR_JSON_KEY_NOT_FOUND in str(df.value)


# TODO: actual AZ and EL values need to be generated.
@pytest.mark.xfail
def test_configure_to_send_correct_configuration_data_when_dish_is_idle(
    mock_dish_master_proxy,
):
    device_proxy, tango_client, _, _ = mock_dish_master_proxy
    dish_config = config_input_str
    device_proxy.Configure(json.dumps(dish_config))

    json_argument = dish_config
    receiver_band = int(json_argument["dish"]["receiver_band"])

    arg_list = {
        "pointing": {"AZ": 181.6281105048956, "EL": 27.336666294459825},
        "dish": {"receiver_band": receiver_band},
    }
    dish_str_ip = json.dumps(arg_list)

    tango_client.deviceproxy.command_inout_asynch.assert_called_with(
        const.CMD_DISH_CONFIGURE,
        str(dish_str_ip),
        any_method(with_name="cmd_ended_cb"),
    )


# TODO: actual AZ and EL values need to be generated.
@pytest.mark.xfail
def test_configure_command_with_callback_method(
    mock_dish_master_proxy, event_subscription_mock
):
    device_proxy, _, _, _ = mock_dish_master_proxy
    dish_config = config_input_str
    device_proxy.Configure(json.dumps(dish_config))
    dummy_event = command_callback(const.CMD_DISH_CONFIGURE)
    event_subscription_mock[const.CMD_DISH_CONFIGURE](dummy_event)
    assert (
        const.STR_COMMAND + const.CMD_DISH_CONFIGURE
        in device_proxy.activityMessage
    )


def test_track_should_raise_exception_when_called_with_invalid_arguments(
    mock_tango_server_helper,
):
    with fake_tango_system(DishLeafNode) as tango_context:
        with pytest.raises(tango.DevFailed) as df:
            tango_context.device.Track(track_invalid_arg)
        assert const.ERR_JSON_KEY_NOT_FOUND in str(df.value)


def test_track_should_raise_exception_when_called_with_invalid_json(
    mock_tango_server_helper,
):
    with fake_tango_system(DishLeafNode) as tango_context:
        with pytest.raises(tango.DevFailed) as df:
            tango_context.device.Track(config_track_invalid_str)
        assert const.ERR_INVALID_JSON in str(df.value)


@pytest.mark.xfail
def test_track_should_command_dish_to_start_tracking(mock_dish_master_proxy):
    device_proxy, tango_client, _, _ = mock_dish_master_proxy
    device_proxy.Track(config_input_str)
    json_argument = config_input_str
    tango_client.deviceproxy.command_inout_asynch.assert_called_with(
        const.CMD_TRACK, "0", any_method(with_name="cmd_ended_cb")
    )


# TODO: actual AZ and EL values need to be generated.
@pytest.mark.xfail
def test_track_command_with_callback_method(
    mock_dish_master_proxy, event_subscription_mock
):
    device_proxy, device_proxy, _, _ = mock_dish_master_proxy
    device_proxy.Track("0")
    dummy_event = command_callback(const.CMD_TRACK)
    event_subscription_mock[const.CMD_TRACK](dummy_event)
    assert const.STR_COMMAND + const.CMD_TRACK in device_proxy.activityMessage


@pytest.fixture(
    scope="function",
    params=[
        DishMode.OFF,
        DishMode.STARTUP,
        DishMode.SHUTDOWN,
        DishMode.STANDBY_LP,
        DishMode.STANDBY_FP,
        DishMode.STOW,
        DishMode.CONFIG,
        DishMode.OPERATE,
        DishMode.MAINTENANCE,
    ],
)
def dish_mode(request):
    return request.param


def test_dish_leaf_node_activity_message_reports_correct_dish_master_dish_mode(
    mock_dish_master_proxy,
    event_subscription_attr_mock,
    dish_mode,
    mock_tango_server_helper,
):
    (
        device_proxy,
        tango_client_obj,
        dish_master1_fqdn,
        _,
    ) = mock_dish_master_proxy
    attribute_name = "dishMode"
    device_proxy.SetOperateMode()
    dummy_event = create_dummy_event_for_dishmode(
        dish_master1_fqdn, dish_mode, attribute_name
    )
    event_subscription_attr_mock[attribute_name](dummy_event)
    assert device_proxy.activityMessage == f"dishMode is {dish_mode.value}."


def test_dish_leaf_node_dish_mode_with_error_event(
    mock_dish_master_proxy,
    event_subscription_attr_mock,
    mock_tango_server_helper,
):
    device_proxy, _, dish_master1_fqdn, _ = mock_dish_master_proxy
    dish_master_dishmode_attribute = "dishMode"
    dish_mode_value = 9
    device_proxy.SetOperateMode()
    dummy_event = create_dummy_event_with_error(
        dish_master1_fqdn, dish_mode_value, dish_master_dishmode_attribute
    )
    event_subscription_attr_mock[dish_master_dishmode_attribute](dummy_event)
    assert (
        "Event system DevError(s) occured!!!" in device_proxy.activityMessage
    )


@pytest.fixture(
    scope="function",
    params=[("Slew", [10.0, 20.0])],
)
def command_name_with_args(request):
    cmd_name, input_args = request.param
    return cmd_name, input_args


def test_msg_in_activity_message_attribute(
    mock_dish_master_proxy,
    event_subscription_mock,
    command_name_with_args,
    mock_tango_server_helper,
):
    device_proxy, _, _, _ = mock_dish_master_proxy
    command_name, input_args = command_name_with_args
    device_proxy.command_inout(command_name, input_args)
    dummy_event = command_callback(command_name)
    event_subscription_mock[command_name](dummy_event)
    assert f"Command :-> {command_name}" in device_proxy.activityMessage


def test_activity_message_attribute_when_command_callback_is_called_with_error_event(
    mock_dish_master_proxy,
    event_subscription_mock,
    command_name_with_args,
    mock_tango_server_helper,
):
    device_proxy, _, _, _ = mock_dish_master_proxy
    command_name, input_args = command_name_with_args
    device_proxy.command_inout(command_name, input_args)
    dummy_event = command_callback_with_event_error(command_name)
    event_subscription_mock[command_name](dummy_event)
    assert (
        f"Error in invoking command: {command_name}"
        in device_proxy.activityMessage
    )


@pytest.fixture(
    scope="function",
    params=[
        ("Slew", [10.0, 20.0], "Slew"),
    ],
)
def command_with_arg(request):
    cmd_name, input_arg, requested_cmd = request.param
    return cmd_name, input_arg, requested_cmd


def test_command_cb_is_invoked_when_command_with_arg_is_called_async(
    mock_dish_master_proxy, command_with_arg, mock_tango_server_helper
):
    device_proxy, dish1_proxy_mock, _, _ = mock_dish_master_proxy
    cmd_name, input_arg, requested_cmd = command_with_arg
    device_proxy.command_inout(cmd_name, input_arg)
    # Comparing np.arrys behaves differently, so it is suggested to use the
    # np.testing.assert_equal method.
    # See https://stackoverflow.com/questions/27781394/mock-assert-called-once-with-a-numpy-array-as-argument
    np.testing.assert_array_equal(
        dish1_proxy_mock.deviceproxy.command_inout_asynch.call_args[0][1],
        np.array(input_arg),
    )
    assert dish1_proxy_mock.deviceproxy.command_inout_asynch.call_args[0][
        2
    ] == any_method(with_name="cmd_ended_cb")


def create_dummy_event_for_dishmode(device_fqdn, dish_mode_value, attribute):
    fake_event = Mock()
    fake_event.err = False
    fake_event.attr_name = f"{device_fqdn}/{attribute}"
    fake_event.attr_value.value = dish_mode_value
    return fake_event


def create_dummy_event_with_error(device_fqdn, attr_value, attribute):
    fake_event = Mock()
    fake_event.err = True
    fake_event.errors = "Event Error"
    fake_event.attr_name = f"{device_fqdn}/{attribute}"
    fake_event.attr_value.value = attr_value
    return fake_event


def create_dummy_event_for_dish_capturing(
    device_fqdn, dish_capturing_value, attribute
):
    fake_event = Mock()
    fake_event.err = False
    fake_event.attr_name = f"{device_fqdn}/{attribute}"
    fake_event.attr_value.value = dish_capturing_value
    return fake_event


def test_activity_message():
    with fake_tango_system(DishLeafNode) as tango_context:
        tango_context.device.activityMessage = const.STR_OK
        assert tango_context.device.activityMessage == const.STR_OK


def test_status():
    with fake_tango_system(DishLeafNode) as tango_context:
        assert tango_context.device.Status() != const.STR_DISH_INIT_SUCCESS


def test_logging_level():
    with fake_tango_system(DishLeafNode) as tango_context:
        tango_context.device.loggingLevel = LoggingLevel.INFO
        assert tango_context.device.loggingLevel == LoggingLevel.INFO


def test_logging_targets():
    with fake_tango_system(DishLeafNode) as tango_context:
        tango_context.device.loggingTargets = ["console::cout"]
        assert "console::cout" in tango_context.device.loggingTargets


def test_test_mode():
    with fake_tango_system(DishLeafNode) as tango_context:
        test_mode = TestMode.NONE
        tango_context.device.testMode = test_mode
        assert tango_context.device.testMode == test_mode


def test_simulation_mode():
    with fake_tango_system(DishLeafNode) as tango_context:
        simulation_mode = SimulationMode.FALSE
        tango_context.device.simulationMode = simulation_mode
        assert tango_context.device.simulationMode == simulation_mode


def test_control_mode():
    with fake_tango_system(DishLeafNode) as tango_context:
        control_mode = ControlMode.REMOTE
        tango_context.device.controlMode = control_mode
        assert tango_context.device.controlMode == control_mode


def test_health_state():
    with fake_tango_system(DishLeafNode) as tango_context:
        assert tango_context.device.healthState == HealthState.OK


def raise_devfailed_exception(*args):
    tango.Except.throw_exception(
        "DishLeafNode_Commandfailed",
        "This is error message for devfailed",
        " ",
        tango.ErrSeverity.ERR,
    )


def test_version_id():
    """Test for versionId"""
    with fake_tango_system(DishLeafNode) as tango_context:
        assert tango_context.device.versionId == release.version


def test_build_state():
    """Test for buildState"""
    with fake_tango_system(DishLeafNode) as tango_context:
        assert tango_context.device.buildState == (
            "{},{},{}".format(
                release.name, release.version, release.description
            )
        )


def command_callback(command_name):
    fake_event = MagicMock()
    fake_event.err = False
    fake_event.errors = "Event error"
    fake_event.cmd_name = f"{command_name}"
    return fake_event


def command_callback_with_event_error(command_name):
    fake_event = MagicMock()
    fake_event.err = True
    fake_event.errors = "Event error"
    fake_event.cmd_name = f"{command_name}"
    return fake_event


def command_callback_with_command_exception(command_name):
    return Exception("Exception in callback")


def assert_activity_message(device_proxy, expected_message):
    assert (
        device_proxy.activityMessage == expected_message
    )  # reads tango attribute


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
        patched_constructor.side_effect = (
            lambda device_fqdn: proxies_to_mock.get(device_fqdn, Mock())
        )
        patched_module = importlib.reload(
            sys.modules[device_under_test.__module__]
        )

    device_under_test = getattr(patched_module, device_under_test.__name__)

    device_test_context = DeviceTestContext(
        device_under_test, properties=initial_dut_properties
    )
    device_test_context.start()
    yield device_test_context
    device_test_context.stop()
