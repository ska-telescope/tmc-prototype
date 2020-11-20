# Standard Python imports
import contextlib
import importlib
import types
import sys
import json
import mock
from mock import Mock, MagicMock
import tango
import pytest

# Tango imports
from tango.test_context import DeviceTestContext
from os.path import dirname, join

# Additional import
from dishleafnode import DishLeafNode, const, release
from dishleafnode.utils import DishMode
from ska.base.control_model import HealthState, AdminMode, TestMode, SimulationMode, ControlMode
from ska.base.control_model import LoggingLevel


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
def mock_dish_master():
    dish_master1_fqdn = "mid_d0001/elt/master"
    dut_properties = {"DishMasterFQDN": dish_master1_fqdn}
    dish1_proxy_mock = Mock()
    event_subscription_map = {}
    proxies_to_mock = {dish_master1_fqdn: dish1_proxy_mock}
    dish1_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args, **kwargs: event_subscription_map.update(
            {attr_name: callback}
        )
    )
    with fake_tango_system(
        DishLeafNode, initial_dut_properties=dut_properties, proxies_to_mock=proxies_to_mock
    ) as tango_context:
        yield tango_context, dish1_proxy_mock, dish_master1_fqdn, event_subscription_map


@pytest.fixture(scope="function")
def event_subscription(mock_dish_master):
    event_subscription_map = {}
    mock_dish_master[
        1
    ].command_inout_asynch.side_effect = lambda command_name, callback, *args, **kwargs: event_subscription_map.update(
        {command_name: callback}
    )
    yield event_subscription_map


@pytest.fixture(scope="function")
def event_subscription_with_arg(mock_dish_master):
    event_subscription_map = {}
    mock_dish_master[
        1
    ].command_inout_asynch.side_effect = lambda command_name, argument, callback, *args, **kwargs: event_subscription_map.update(
        {command_name: callback}
    )
    yield event_subscription_map


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
    mock_dish_master, command_with_arg
):
    tango_context, dish1_proxy_mock, _, _ = mock_dish_master
    cmd_name, input_arg, requested_cmd = command_with_arg

    tango_context.device.command_inout(cmd_name, input_arg)
    dish1_proxy_mock.command_inout_asynch.assert_called_with(
        requested_cmd, input_arg, any_method(with_name="cmd_ended_cb")
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
    mock_dish_master, dish_leaf_node_command_with_arg
):
    tango_context, dish1_proxy_mock, _, _ = mock_dish_master
    cmd_name, input_arg, requested_cmd = dish_leaf_node_command_with_arg

    tango_context.device.command_inout(cmd_name, input_arg)

    dish1_proxy_mock.command_inout_asynch.assert_called_with(
        requested_cmd, any_method(with_name="cmd_ended_cb")
    )


@pytest.fixture(
    scope="function",
    params=[
        ("SetStandbyLPMode", "SetStandbyLPMode"),
        ("SetOperateMode", "SetOperateMode"),
        ("StopTrack", "TrackStop"),
        ("SetStandbyFPMode", "SetStandbyFPMode"),
        ("SetStowMode", "SetStowMode"),
        ("Abort", "TrackStop"),
        ("Restart", "SetStandbyLPMode"),
    ],
)
def command_without_arg(request):
    cmd_name, requested_cmd = request.param
    return cmd_name, requested_cmd


def test_command_cb_is_invoked_when_command_without_arg_is_called_async(
    mock_dish_master, command_without_arg
):
    tango_context, dish1_proxy_mock, _, _ = mock_dish_master
    cmd_name, requested_cmd = command_without_arg

    tango_context.device.command_inout(cmd_name)

    dish1_proxy_mock.command_inout_asynch.assert_called_with(
        requested_cmd, any_method(with_name="cmd_ended_cb")
    )


# TODO: actual AZ and EL values need to be generated.
@pytest.mark.xfail
def test_configure_to_send_correct_configuration_data_when_dish_is_idle(mock_dish_master):
    tango_context, dish1_proxy_mock, _, _ = mock_dish_master
    dish_config = config_input_str
    tango_context.device.Configure(json.dumps(dish_config))

    jsonArgument = dish_config
    # ra_value = (jsonArgument["pointing"]["target"]["RA"])
    # dec_value = (jsonArgument["pointing"]["target"]["dec"])
    receiver_band = int(jsonArgument["dish"]["receiverBand"])

    arg_list = {
        "pointing": {"AZ": 181.6281105048956, "EL": 27.336666294459825},
        "dish": {"receiverBand": receiver_band},
    }
    dish_str_ip = json.dumps(arg_list)

    dish1_proxy_mock.command_inout_asynch.assert_called_with(
        const.CMD_DISH_CONFIGURE, str(dish_str_ip), any_method(with_name="cmd_ended_cb")
    )


@pytest.mark.xfail
def test_track_should_command_dish_to_start_tracking(mock_dish_master):
    tango_context, dish1_proxy_mock, _, _ = mock_dish_master
    tango_context.device.Track(config_input_str)
    jsonArgument = config_input_str
    ra_value = jsonArgument["pointing"]["target"]["RA"]
    dec_value = jsonArgument["pointing"]["target"]["dec"]
    radec_value = "radec" + "," + str(ra_value) + "," + str(dec_value)
    dish1_proxy_mock.command_inout_asynch.assert_called_with(
        const.CMD_TRACK, "0", any_method(with_name="cmd_ended_cb")
    )

def create_dummy_event_for_dishmode(device_fqdn, dish_mode_value, attribute):
    fake_event = Mock()
    fake_event.err = False
    fake_event.attr_name = f"{device_fqdn}/{attribute}"
    fake_event.attr_value.value = dish_mode_value
    return fake_event


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
    mock_dish_master, dish_mode
):
    attribute_name = "dishMode"
    tango_context, _, dish_master1_fqdn, event_subscription_map = mock_dish_master
    dummy_event = create_dummy_event_for_dishmode(dish_master1_fqdn, dish_mode, attribute_name)
    event_subscription_map[attribute_name](dummy_event)
    assert tango_context.device.activityMessage == f"dishMode is {dish_mode}."


def test_dish_leaf_node_dish_mode_with_error_event(mock_dish_master):
    dish_master_dishmode_attribute = "dishMode"
    tango_context, _, dish_master1_fqdn, event_subscription_map = mock_dish_master
    dish_mode_value = 9
    dummy_event = create_dummy_event_with_error(
        dish_master1_fqdn, dish_mode_value, dish_master_dishmode_attribute
    )
    event_subscription_map[dish_master_dishmode_attribute](dummy_event)
    assert "Event system DevError(s) occured!!!" in tango_context.device.activityMessage


def create_dummy_event_with_error(device_fqdn, attr_value, attribute):
    fake_event = Mock()
    fake_event.err = True
    fake_event.errors = "Event Error"
    fake_event.attr_name = f"{device_fqdn}/{attribute}"
    fake_event.attr_value.value = attr_value
    return fake_event


def create_dummy_event_for_dish_capturing(device_fqdn, dish_capturing_value, attribute):
    fake_event = Mock()
    fake_event.err = False
    fake_event.attr_name = f"{device_fqdn}/{attribute}"
    fake_event.attr_value.value = dish_capturing_value
    return fake_event


@pytest.fixture(scope="function", params=["True", "False"])
def dish_capturing_callback_flag(request):
    flag = request.param
    return flag


def test_activity_message_reports_same_capturing_state_as_dish_master(
    mock_dish_master, dish_capturing_callback_flag
):
    flag = dish_capturing_callback_flag
    dish_master_capturing_attribute = "capturing"
    tango_context, _, dish_master1_fqdn, event_subscription_map = mock_dish_master
    dish_capturing_value = flag
    dummy_event = create_dummy_event_for_dish_capturing(
        dish_master1_fqdn, dish_capturing_value, dish_master_capturing_attribute
    )
    event_subscription_map[dish_master_capturing_attribute](dummy_event)
    assert tango_context.device.activityMessage == f"capturing is {dish_capturing_value}."


@pytest.fixture(
    scope="function",
    params=[
        ("capturing", "Invalid_value"),
        ("achievedPointing", 0.0),
        ("desiredPointing", 0.0),
    ],
)
def attribute_with_value(request):
    attribute, value = request.param
    return attribute, value


def test_activity_message_reports_correct_state_when_dish_leaf_node_receives_an_error_event(
    mock_dish_master, attribute_with_value
):
    attribute, value = attribute_with_value
    dish_master_attribute = attribute
    tango_context, _, dish_master1_fqdn, event_subscription_map = mock_dish_master
    dish_attribute_value = value
    dummy_event = create_dummy_event_with_error(
        dish_master1_fqdn, dish_attribute_value, dish_master_attribute
    )
    event_subscription_map[dish_master_attribute](dummy_event)
    assert "Event system DevError(s) occured!!!" in tango_context.device.activityMessage


def create_dummy_event(device_fqdn, attribute, attr_value):
    fake_event = Mock()
    fake_event.err = False
    fake_event.attr_name = f"{device_fqdn}/{attribute}"
    fake_event.attr_value.value = attr_value
    return fake_event


@pytest.fixture(
    scope="function",
    params=[
        ("achievedPointing"),
        ("desiredPointing"),
    ],
)
def pointing_attribute(request):
    attribute = request.param
    return attribute


def test_activity_message_reports_correct_pointing_attribute_values(
    mock_dish_master, pointing_attribute
):
    attribute = pointing_attribute
    dish_master_pointing_attribute = attribute
    tango_context, _, dish_master1_fqdn, event_subscription_map = mock_dish_master
    attribute_pointing = attribute
    value = 0.0
    dummy_event = create_dummy_event(dish_master1_fqdn, attribute_pointing, value)
    event_subscription_map[dish_master_pointing_attribute](dummy_event)
    assert tango_context.device.activityMessage == f"{attribute} is {value}."


def test_configure_should_raise_exception_when_called_with_invalid_json():
    with fake_tango_system(DishLeafNode) as tango_context:
        with pytest.raises(tango.DevFailed):
            tango_context.device.Configure(config_track_invalid_str)
        assert const.ERR_INVALID_JSON in tango_context.device.activityMessage


def test_configure_should_raise_exception_when_called_with_invalid_arguments():
    with fake_tango_system(DishLeafNode) as tango_context:
        input_string = []
        input_string.append(configure_invalid_arg)
        with pytest.raises(tango.DevFailed):
            tango_context.device.Configure(input_string[0])
        assert const.ERR_JSON_KEY_NOT_FOUND in tango_context.device.activityMessage

def test_track_should_raise_exception_when_called_with_invalid_arguments():
    with fake_tango_system(DishLeafNode) as tango_context:
        with pytest.raises(tango.DevFailed):
            tango_context.device.Track(track_invalid_arg)
        assert const.ERR_JSON_KEY_NOT_FOUND in tango_context.device.activityMessage


def test_track_should_raise_exception_when_called_with_invalid_json():
    with fake_tango_system(DishLeafNode) as tango_context:
        with pytest.raises(tango.DevFailed):
            tango_context.device.Track(config_track_invalid_str)

        assert const.ERR_INVALID_JSON in tango_context.device.activityMessage


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

@pytest.fixture(
    scope="function",
    params=[
        "SetStowMode",
        "SetStandbyLPMode",
        "SetOperateMode",
        "SetStandbyFPMode",
    ],
)
def command_name(request):
    cmd_name = request.param
    return cmd_name


def test_activity_message_attribute_value_contains_command_name(
    event_subscription, mock_dish_master, command_name
):
    tango_context, _, _, _ = mock_dish_master
    tango_context.device.command_inout(command_name)
    dummy_event = command_callback(command_name)
    event_subscription[command_name](dummy_event)
    assert f"Command :-> {command_name}" in tango_context.device.activityMessage


def test_activity_message_attribute_value_contains_command_name_with_event_error(
    event_subscription, mock_dish_master, command_name
):
    tango_context, _, _, _ = mock_dish_master
    tango_context.device.command_inout(command_name)
    dummy_event = command_callback_with_event_error(command_name)
    event_subscription[command_name](dummy_event)
    assert f"Error in invoking command: {command_name}" in tango_context.device.activityMessage


@pytest.fixture(
    scope="function",
    params=[("Slew", [10.0, 20.0])],
)
def command_name_with_args(request):
    cmd_name, input_args = request.param
    return cmd_name, input_args


def test_msg_in_activity_message_attribute(
    event_subscription_with_arg, mock_dish_master, command_name_with_args
):
    tango_context, _, _, _ = mock_dish_master
    command_name, input_args = command_name_with_args
    tango_context.device.command_inout(command_name, input_args)
    dummy_event = command_callback(command_name)
    event_subscription_with_arg[command_name](dummy_event)
    assert f"Command :-> {command_name}" in tango_context.device.activityMessage


def test_activity_message_attribute_when_command_callback_is_called_with_error_event(
    event_subscription_with_arg, mock_dish_master, command_name_with_args
):
    tango_context, _, _, _ = mock_dish_master
    command_name, input_args = command_name_with_args
    tango_context.device.command_inout(command_name, input_args)
    dummy_event = command_callback_with_event_error(command_name)
    event_subscription_with_arg[command_name](dummy_event)
    assert f"Error in invoking command: {command_name}" in tango_context.device.activityMessage


# TODO: actual AZ and EL values need to be generated.
@pytest.mark.xfail
def test_configure_command_with_callback_method(event_subscription, mock_dish_master):
    tango_context, _, _, _ = mock_dish_master
    dish_config = config_input_str
    tango_context.device.Configure(json.dumps(dish_config))
    dummy_event = command_callback(const.CMD_DISH_CONFIGURE)
    event_subscription[const.CMD_DISH_CONFIGURE](dummy_event)
    assert const.STR_COMMAND + const.CMD_DISH_CONFIGURE in tango_context.device.activityMessage


# TODO: actual AZ and EL values need to be generated.
@pytest.mark.xfail
def test_track_command_with_callback_method(event_subscription, mock_dish_master):
    tango_context, dish1_proxy_mock, dish_master1_fqdn, event_subscription_map = mock_dish_master
    tango_context.device.Track("0")
    dummy_event = command_callback(const.CMD_TRACK)
    event_subscription[const.CMD_TRACK](dummy_event)
    assert const.STR_COMMAND + const.CMD_TRACK in tango_context.device.activityMessage


def test_version_id():
    """Test for versionId"""
    with fake_tango_system(DishLeafNode) as tango_context:
        assert tango_context.device.versionId == release.version


def test_build_state():
    """Test for buildState"""
    with fake_tango_system(DishLeafNode) as tango_context:
        assert tango_context.device.buildState == (
            "{},{},{}".format(release.name, release.version, release.description)
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
    assert device_proxy.activityMessage == expected_message  # reads tango attribute


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

    device_test_context = DeviceTestContext(device_under_test, properties=initial_dut_properties)
    device_test_context.start()
    yield device_test_context
    device_test_context.stop()
