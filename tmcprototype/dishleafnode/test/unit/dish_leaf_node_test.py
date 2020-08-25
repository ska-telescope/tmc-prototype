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
from tango import DevState
from tango.test_context import DeviceTestContext
from os.path import dirname, join

# Additional import
from dishleafnode import DishLeafNode, const, release
from ska.base.control_model import HealthState, AdminMode, TestMode, SimulationMode, ControlMode
from ska.base.control_model import LoggingLevel

from enum import IntEnum


# Enums
class DishMode(IntEnum):
    OFF = 0
    STARTUP = 1
    SHUTDOWN = 2
    STANDBY_LP = 3
    STANDBY_FP = 4
    STOW = 5
    CONFIG = 6
    OPERATE = 7
    MAINTENANCE = 8

config_input_file = 'command_Config.json'
path = join(dirname(__file__), 'data', config_input_file)
with open(path, 'r') as f:
    config_input_str = f.read()

invalid_arg_file = 'invalid_json_argument_Configure.json'
path = join(dirname(__file__), 'data', invalid_arg_file)
with open(path, 'r') as f:
    configure_invalid_arg = f.read()

invalid_arg_file2 = 'invalid_json_argument_Track.json'
path = join(dirname(__file__), 'data', invalid_arg_file2)
with open(path, 'r') as f:
    track_invalid_arg = f.read()

invalid_key_config_track_file = 'invalid_key_Configure_Track.json'
path = join(dirname(__file__), 'data', invalid_key_config_track_file)
with open(path, 'r') as f:
    config_track_invalid_str = f.read()


@pytest.fixture(scope="function")
def mock_dish_master():
    dish_master1_fqdn = 'mid_d0001/elt/master'
    dut_properties = {'DishMasterFQDN': dish_master1_fqdn}
    dish1_proxy_mock = Mock()
    event_subscription_map = {}
    proxies_to_mock = {dish_master1_fqdn: dish1_proxy_mock}
    dish1_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args,
               **kwargs: event_subscription_map.update({attr_name: callback}))
    with fake_tango_system(DishLeafNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        yield tango_context, dish1_proxy_mock, dish_master1_fqdn,event_subscription_map


@pytest.fixture(scope="function")
def event_subscription(mock_dish_master):
    event_subscription_map = {}
    mock_dish_master[1].command_inout_asynch.side_effect = (
        lambda command_name, callback, *args,
               **kwargs: event_subscription_map.update({command_name: callback}))
    yield event_subscription_map


@pytest.fixture(scope="function")
def event_subscription_with_arg(mock_dish_master):
    event_subscription_map = {}
    mock_dish_master[1].command_inout_asynch.side_effect = (
        lambda command_name, argument, callback, *args,
               **kwargs: event_subscription_map.update({command_name: callback}))
    yield event_subscription_map


def test_start_scan_should_command_dish_to_start_scan_when_it_is_ready(mock_dish_master):
    # arrange:
    tango_context, dish1_proxy_mock, dish_master1_fqdn, event_subscription_map = mock_dish_master
    scan_input = 0.0
    # act:
    tango_context.device.Scan(str(scan_input))
    # assert:
    dish1_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_DISH_SCAN,
                                                            str(scan_input),
                                                            any_method(with_name='scan_cmd_ended_cb'))


# TODO: actual AZ and EL values need to be generated.
@pytest.mark.xfail
def test_configure_to_send_correct_configuration_data_when_dish_is_idle(mock_dish_master):
    # arrange:
    tango_context, dish1_proxy_mock, dish_master1_fqdn, event_subscription_map = mock_dish_master
    dish_config = config_input_str
    # act:
    tango_context.device.Configure(json.dumps(dish_config))

    # assert:
    jsonArgument = (dish_config)
    # ra_value = (jsonArgument["pointing"]["target"]["RA"])
    # dec_value = (jsonArgument["pointing"]["target"]["dec"])
    receiver_band = int(jsonArgument["dish"]["receiverBand"])

    arg_list = {"pointing": {
        "AZ": 181.6281105048956,
        "EL": 27.336666294459825

    },
        "dish": {
            "receiverBand": receiver_band
        }

    }
    dish_str_ip = json.dumps(arg_list)

    dish1_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_DISH_CONFIGURE,
                                                             str(dish_str_ip),
                                                             any_method(with_name='configure_cmd_ended_cb'))


def test_end_scan_should_command_dish_to_end_scan_when_it_is_scanning(mock_dish_master):
    # arrange:
    tango_context, dish1_proxy_mock, dish_master1_fqdn, event_subscription_map = mock_dish_master
    scan_input = 0.0
    # act:
    tango_context.device.EndScan(str(scan_input))

    # assert:
    dish1_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_STOP_CAPTURE,
                                                            str(scan_input),
                                                            any_method(with_name='stopcapture_cmd_ended_cb'))


def test_standby_lp_mode_should_command_dish_to_standby(mock_dish_master):
    # arrange:
    tango_context, dish1_proxy_mock, dish_master1_fqdn, event_subscription_map = mock_dish_master
    # act:
    tango_context.device.SetStandByLPMode()

    # assert:
    dish1_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_SET_STANDBYLP_MODE,
                                                                 any_method(with_name='setstandbylpmode_cmd_ended_cb'))


def test_set_operate_mode_should_command_dish_to_start(mock_dish_master):
    # arrange:
    tango_context, dish1_proxy_mock, dish_master1_fqdn,event_subscription_map = mock_dish_master
    # act:
    tango_context.device.SetOperateMode()

    # assert:
    dish1_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_SET_OPERATE_MODE,
                                                                 any_method(with_name='setoperatemode_cmd_ended_cb'))


@pytest.mark.xfail
def test_track_should_command_dish_to_start_tracking(mock_dish_master):
    # arrange:
    tango_context, dish1_proxy_mock, dish_master1_fqdn, event_subscription_map = mock_dish_master
    # act:
    tango_context.device.Track(config_input_str)
    # assert:
    jsonArgument = config_input_str
    ra_value = (jsonArgument["pointing"]["target"]["RA"])
    dec_value = (jsonArgument["pointing"]["target"]["dec"])
    radec_value = 'radec' + ',' + str(ra_value) + ',' + str(dec_value)
    dish1_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_TRACK, "0",
                                                                 any_method(with_name='cmd_ended_cb'))


def test_stop_track_should_command_dish_to_stop_tracking(mock_dish_master):
    # arrange:
    tango_context, dish1_proxy_mock, dish_master1_fqdn, event_subscription_map = mock_dish_master
    tango_context.device.StopTrack()

    # assert:
    dish1_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_STOP_TRACK,
                                                             any_method(with_name='stoptrack_cmd_ended_cb'))


def test_slew_should_command_the_dish_to_slew_towards_the_set_pointing_coordinates(mock_dish_master):
    tango_context, dish1_proxy_mock, dish_master1_fqdn, event_subscription_map = mock_dish_master
    slew_arg = 0.0
    # act:
    tango_context.device.Slew(str(slew_arg))

    # assert:
    dish1_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_DISH_SLEW,
                                                            str(slew_arg),
                                                            any_method(with_name='slew_cmd_ended_cb'))


def test_start_capture_should_command_dish_to_start_capture_on_the_set_configured_band(mock_dish_master):
    tango_context, dish1_proxy_mock, dish_master1_fqdn, event_subscription_map = mock_dish_master
    capture_arg = 0.0
    # act:
    tango_context.device.StartCapture(str(capture_arg))

    # assert:
    dish1_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_START_CAPTURE,
                                                            str(capture_arg),
                                                                any_method(with_name='startcapture_cmd_ended_cb'))


def test_stop_capture_should_command_dish_to_stop_capture_on_the_set_configured_band(mock_dish_master):
    tango_context, dish1_proxy_mock, dish_master1_fqdn, event_subscription_map = mock_dish_master
    capture_arg = 0.0
    # act:
    tango_context.device.StopCapture(str(capture_arg))

    # assert:
    # if type(float(capture_arg)) == float:
    dish1_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_STOP_CAPTURE,
                                                            str(capture_arg),
                                                            any_method(with_name='stopcapture_cmd_ended_cb'))


def test_set_standby_fp_mode_should_command_dish_to_transition_to_standby_fp_mode(mock_dish_master):
    tango_context, dish1_proxy_mock, dish_master1_fqdn, event_subscription_map = mock_dish_master
    # act:
    tango_context.device.SetStandbyFPMode()

    # assert:
    dish1_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_SET_STANDBYFP_MODE,
                                                             any_method(with_name='setstandbyfpmode_cmd_ended_cb'))


def test_set_stow_mode_should_command_dish_to_transit_to_stow_mode(mock_dish_master):
    tango_context, dish1_proxy_mock, dish_master1_fqdn, event_subscription_map = mock_dish_master    # act:
    tango_context.device.SetStowMode()

    # assert:
    dish1_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_SET_STOW_MODE,
                                                             any_method(with_name='setstowmode_cmd_ended_cb'))


def test_abort_should_command_dish_to_abort(mock_dish_master):
    tango_context, dish1_proxy_mock, dish_master1_fqdn, event_subscription_map = mock_dish_master    # act:
    tango_context.device.Abort()

    # assert:
    dish1_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_ABORT,
                                                             any_method(with_name='abort_cmd_ended_cb'))


def test_abort_should_raise_dev_failed(mock_dish_master):
    # arrange:
    tango_context, dish1_proxy_mock, dish_master1_fqdn, event_subscription_map = mock_dish_master
    dish1_proxy_mock.command_inout_asynch.side_effect = raise_devfailed_exception
    # act
    with pytest.raises(tango.DevFailed):
        tango_context.device.Abort()

    # assert
    assert const.ERR_EXE_ABORT_CMD in tango_context.device.activityMessage


def test_restart_should_command_dish_to_restart(mock_dish_master):
    tango_context, dish1_proxy_mock, dish_master1_fqdn, event_subscription_map = mock_dish_master
    # act:
    tango_context.device.Restart()

    # assert:
    dish1_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_RESTART,
                                                             any_method(with_name='restart_cmd_ended_cb'))


def test_restart_should_raise_dev_failed(mock_dish_master):
    # arrange:
    tango_context, dish1_proxy_mock, dish_master1_fqdn, event_subscription_map = mock_dish_master
    dish1_proxy_mock.command_inout_asynch.side_effect = raise_devfailed_exception
    # act
    with pytest.raises(tango.DevFailed):
        tango_context.device.Restart()

    # assert
    assert const.ERR_EXE_RESTART_CMD in tango_context.device.activityMessage


def create_dummy_event_for_dishmode(device_fqdn, dish_mode_value, attribute):
    fake_event = Mock()
    fake_event.err = False
    fake_event.attr_name = f"{device_fqdn}/{attribute}"
    fake_event.attr_value.value = dish_mode_value
    return fake_event


def test_dish_leaf_node_dish_mode_is_off_when_dish_is_off(mock_dish_master):
    # arrange:
    dish_master_dishmode_attribute = 'dishMode'
    tango_context, dish1_proxy_mock, dish_master1_fqdn, event_subscription_map = mock_dish_master

    # act:
    dish_mode_value = DishMode.OFF
    dummy_event = create_dummy_event_for_dishmode(dish_master1_fqdn, dish_mode_value,
                                                  dish_master_dishmode_attribute)
    event_subscription_map[dish_master_dishmode_attribute](dummy_event)

    # assert:
    assert tango_context.device.activityMessage == const.STR_DISH_OFF_MODE


def test_dish_leaf_node_dish_mode_is_startup_when_dish_is_startup(mock_dish_master):
    # arrange:
    dish_master_dishmode_attribute = 'dishMode'
    tango_context, dish1_proxy_mock, dish_master1_fqdn, event_subscription_map = mock_dish_master
    # act:
    dish_mode_value = DishMode.STARTUP
    dummy_event = create_dummy_event_for_dishmode(dish_master1_fqdn, dish_mode_value,
                                                  dish_master_dishmode_attribute)
    event_subscription_map[dish_master_dishmode_attribute](dummy_event)

    # assert:
    assert tango_context.device.activityMessage == const.STR_DISH_STARTUP_MODE


def test_dish_leaf_node_dish_mode_is_shutdown_when_dish_is_shutdown(mock_dish_master):
    # arrange:
    dish_master_dishmode_attribute = 'dishMode'
    tango_context, dish1_proxy_mock, dish_master1_fqdn, event_subscription_map = mock_dish_master
    # act:
    dish_mode_value = DishMode.SHUTDOWN
    dummy_event = create_dummy_event_for_dishmode(dish_master1_fqdn, dish_mode_value,
                                                  dish_master_dishmode_attribute)
    event_subscription_map[dish_master_dishmode_attribute](dummy_event)

    # assert:
    assert tango_context.device.activityMessage == const.STR_DISH_SHUTDOWN_MODE


def test_dish_leaf_node_dish_mode_is_standby_when_dish_is_standby(mock_dish_master):
    # arrange:
    dish_master_dishmode_attribute = 'dishMode'
    tango_context, dish1_proxy_mock, dish_master1_fqdn, event_subscription_map = mock_dish_master
    # act:
    dish_mode_value = DishMode.STANDBY_LP
    dummy_event = create_dummy_event_for_dishmode(dish_master1_fqdn, dish_mode_value,
                                                  dish_master_dishmode_attribute)
    event_subscription_map[dish_master_dishmode_attribute](dummy_event)

    # assert:
    assert tango_context.device.activityMessage == const.STR_DISH_STANDBYLP_MODE


def test_dish_leaf_node_dish_mode_is_stand_by_fp_when_dish_is_stand_by_fp(mock_dish_master):
    # arrange:
    dish_master_dishmode_attribute = 'dishMode'
    tango_context, dish1_proxy_mock, dish_master1_fqdn, event_subscription_map = mock_dish_master
    # act:
    dish_mode_value = DishMode.STANDBY_FP
    dummy_event = create_dummy_event_for_dishmode(dish_master1_fqdn, dish_mode_value,
                                                  dish_master_dishmode_attribute)
    event_subscription_map[dish_master_dishmode_attribute](dummy_event)

    # assert:
    assert tango_context.device.activityMessage == const.STR_DISH_STANDBYFP_MODE


def test_dish_leaf_node_dish_mode_is_maint_when_dish_is_maint(mock_dish_master):
    # arrange:
    dish_master_dishmode_attribute = 'dishMode'
    tango_context, dish1_proxy_mock, dish_master1_fqdn, event_subscription_map = mock_dish_master
    # act:
    dish_mode_value = DishMode.MAINTENANCE
    dummy_event = create_dummy_event_for_dishmode(dish_master1_fqdn, dish_mode_value,
                                                  dish_master_dishmode_attribute)
    event_subscription_map[dish_master_dishmode_attribute](dummy_event)

    # assert:
    assert tango_context.device.activityMessage == const.STR_DISH_MAINT_MODE


def test_dish_leaf_node_dish_mode_is_stow_when_dish_is_stow(mock_dish_master):
    # arrange:
    dish_master_dishmode_attribute = 'dishMode'
    tango_context, dish1_proxy_mock, dish_master1_fqdn, event_subscription_map = mock_dish_master
    # act:
    dish_mode_value = DishMode.STOW
    dummy_event = create_dummy_event_for_dishmode(dish_master1_fqdn, dish_mode_value,
                                                  dish_master_dishmode_attribute)
    event_subscription_map[dish_master_dishmode_attribute](dummy_event)

    # assert:
    assert tango_context.device.activityMessage == const.STR_DISH_STOW_MODE


def test_dish_leaf_node_dish_mode_is_config_when_dish_is_config(mock_dish_master):
    # arrange:
    dish_master_dishmode_attribute = 'dishMode'
    tango_context, dish1_proxy_mock, dish_master1_fqdn, event_subscription_map = mock_dish_master
    # act:
    dish_mode_value = DishMode.CONFIG
    dummy_event = create_dummy_event_for_dishmode(dish_master1_fqdn, dish_mode_value,
                                                  dish_master_dishmode_attribute)
    event_subscription_map[dish_master_dishmode_attribute](dummy_event)

    # assert:
    assert tango_context.device.activityMessage == const.STR_DISH_CONFIG_MODE


def test_dish_leaf_node_dish_mode_is_operate_when_dish_is_operate(mock_dish_master):
    # arrange:
    dish_master_dishmode_attribute = 'dishMode'
    tango_context, dish1_proxy_mock, dish_master1_fqdn, event_subscription_map = mock_dish_master
    # act:
    dish_mode_value = DishMode.OPERATE
    dummy_event = create_dummy_event_for_dishmode(dish_master1_fqdn, dish_mode_value,
                                                  dish_master_dishmode_attribute)
    event_subscription_map[dish_master_dishmode_attribute](dummy_event)

    # assert:
    assert tango_context.device.activityMessage == const.STR_DISH_OPERATE_MODE


def test_dish_leaf_node_dish_mode_is_unknown(mock_dish_master):
    # arrange:
    dish_master_dishmode_attribute = 'dishMode'
    tango_context, dish1_proxy_mock, dish_master1_fqdn, event_subscription_map = mock_dish_master
    # act:
    dish_mode_value = 9
    dummy_event = create_dummy_event_for_dishmode(dish_master1_fqdn, dish_mode_value,
                                                  dish_master_dishmode_attribute)
    event_subscription_map[dish_master_dishmode_attribute](dummy_event)

    # assert:
    assert const.STR_DISH_UNKNOWN_MODE in tango_context.device.activityMessage


def test_dish_leaf_node_dish_mode_with_error_event(mock_dish_master):
    # arrange:
    dish_master_dishmode_attribute = 'dishMode'
    tango_context, dish1_proxy_mock, dish_master1_fqdn, event_subscription_map = mock_dish_master
    # act:
    dish_mode_value = 9
    dummy_event = create_dummy_event_with_error(dish_master1_fqdn, dish_mode_value,
                                                dish_master_dishmode_attribute)
    event_subscription_map[dish_master_dishmode_attribute](dummy_event)

    # assert:
    assert const.ERR_ON_SUBS_DISH_MODE_ATTR in tango_context.device.activityMessage


def create_dummy_event_with_error(device_fqdn, attr_value, attribute):
    fake_event = Mock()
    fake_event.err = True
    fake_event.errors = 'Event Error'
    fake_event.attr_name = f"{device_fqdn}/{attribute}"
    fake_event.attr_value.value = attr_value
    return fake_event


def create_dummy_event_for_dish_capturing(device_fqdn, dish_capturing_value, attribute):
    fake_event = Mock()
    fake_event.err = False
    fake_event.attr_name = f"{device_fqdn}/{attribute}"
    fake_event.attr_value.value = dish_capturing_value
    return fake_event


def test_dish_leaf_node_when_dish_capturing_callback_is_true(mock_dish_master):
    # arrange:
    dish_master_capturing_attribute = 'capturing'
    tango_context, dish1_proxy_mock, dish_master1_fqdn, event_subscription_map = mock_dish_master
    # act:
    dish_capturing_value = True
    dummy_event = create_dummy_event_for_dish_capturing(dish_master1_fqdn, dish_capturing_value,
                                                        dish_master_capturing_attribute)
    event_subscription_map[dish_master_capturing_attribute](dummy_event)

    # assert:
    assert tango_context.device.activityMessage == const.STR_DISH_CAPTURING_TRUE


def test_dish_leaf_node_when_dish_capturing_callback_is_false(mock_dish_master):
    # arrange:
    dish_master_capturing_attribute = 'capturing'
    tango_context, dish1_proxy_mock, dish_master1_fqdn, event_subscription_map = mock_dish_master
    # act:
    dish_capturing_value = False
    dummy_event = create_dummy_event_for_dish_capturing(dish_master1_fqdn, dish_capturing_value,
                                                        dish_master_capturing_attribute)
    event_subscription_map[dish_master_capturing_attribute](dummy_event)

    # assert:
    assert tango_context.device.activityMessage == const.STR_DISH_CAPTURING_FALSE


def test_dish_leaf_node_when_invalid_attribute_value_for_dish_capturing(mock_dish_master):
    # arrange:
    dish_master_capturing_attribute = 'capturing'
    tango_context, dish1_proxy_mock, dish_master1_fqdn, event_subscription_map = mock_dish_master
    # act:
    dish_capturing_value = 'Invalid_value'
    dummy_event = create_dummy_event_for_dish_capturing(dish_master1_fqdn, dish_capturing_value,
                                                        dish_master_capturing_attribute)
    event_subscription_map[dish_master_capturing_attribute](dummy_event)

    # assert:
    assert const.STR_DISH_CAPTURING_UNKNOWN in tango_context.device.activityMessage


def test_dish_leaf_node_when_dish_capturing_callback_with_error_event(mock_dish_master):
    # arrange:
    dish_master_capturing_attribute = 'capturing'
    tango_context, dish1_proxy_mock, dish_master1_fqdn, event_subscription_map = mock_dish_master
    # act:
    dish_capturing_value = 'Invalid_value'
    dummy_event = create_dummy_event_with_error(dish_master1_fqdn, dish_capturing_value,
                                                dish_master_capturing_attribute)
    event_subscription_map[dish_master_capturing_attribute](dummy_event)

    # assert:
    assert const.ERR_SUBSR_CAPTURING_ATTR in tango_context.device.activityMessage


def create_dummy_event(device_fqdn, attribute, attr_value):
    fake_event = Mock()
    fake_event.err = False
    fake_event.attr_name = f"{device_fqdn}/{attribute}"
    fake_event.attr_value.value = attr_value
    return fake_event


def test_dish_leaf_node_when_achieved_pointing_callback_is_true(mock_dish_master):
    # arrange:
    dish_master_achieved_pointing_attribute = 'achievedPointing'
    tango_context, dish1_proxy_mock, dish_master1_fqdn, event_subscription_map = mock_dish_master
    # act:
    attribute = 'achievedPointing'
    value = 0.0
    dummy_event = create_dummy_event(dish_master1_fqdn, attribute, value)
    event_subscription_map[dish_master_achieved_pointing_attribute](dummy_event)

    # assert:
    assert tango_context.device.activityMessage == const.STR_ACHIEVED_POINTING + \
           str(dummy_event.attr_value.value)


def test_dish_leaf_node_when_achieved_pointing_callback_with_error_event(mock_dish_master):
    # arrange:
    dish_master_achieved_pointing_attribute = 'achievedPointing'
    tango_context, dish1_proxy_mock, dish_master1_fqdn, event_subscription_map = mock_dish_master
    # act:
    attribute = 'achievedPointing'
    value = 0.0
    dummy_event = create_dummy_event_with_error(dish_master1_fqdn, attribute, value)
    event_subscription_map[dish_master_achieved_pointing_attribute](dummy_event)

    # assert:
    assert const.ERR_ON_SUBS_DISH_ACHVD_ATTR in tango_context.device.activityMessage


def test_dish_leaf_node_when_desired_pointing_callback_is_true(mock_dish_master):
    # arrange:
    dish_master_desired_pointing_attribute = 'desiredPointing'
    tango_context, dish1_proxy_mock, dish_master1_fqdn, event_subscription_map = mock_dish_master
    # act:
    attribute = 'desiredPointing'
    value = 0.0
    dummy_event = create_dummy_event(dish_master1_fqdn, attribute, value)
    event_subscription_map[dish_master_desired_pointing_attribute](dummy_event)

    # assert:
    assert tango_context.device.activityMessage == const.STR_DESIRED_POINTING + \
           str(dummy_event.attr_value.value)


def test_dish_leaf_node_when_desired_pointing_callback_with_error_event(mock_dish_master):
    # arrange:
    dish_master_desired_pointing_attribute = 'desiredPointing'
    tango_context, dish1_proxy_mock, dish_master1_fqdn, event_subscription_map = mock_dish_master
    # act:
    attribute = 'desiredPointing'
    value = 0.0
    dummy_event = create_dummy_event_with_error(dish_master1_fqdn, attribute, value)
    event_subscription_map[dish_master_desired_pointing_attribute](dummy_event)
    # assert:
    assert const.ERR_ON_SUBS_DISH_DESIRED_POINT_ATTR in tango_context.device.activityMessage


def test_configure_should_raise_exception_when_called_with_invalid_json():
    # act
    with fake_tango_system(DishLeafNode) as tango_context:
        with pytest.raises(tango.DevFailed):
            tango_context.device.Configure(config_track_invalid_str)

        # assert:
        assert const.ERR_INVALID_JSON in tango_context.device.activityMessage


def test_configure_should_raise_exception_when_called_with_invalid_arguments():
    # act
    with fake_tango_system(DishLeafNode) as tango_context:
        input_string = []
        input_string.append(configure_invalid_arg)
        with pytest.raises(tango.DevFailed):
            tango_context.device.Configure(input_string[0])

        # assert:
        assert const.ERR_JSON_KEY_NOT_FOUND in tango_context.device.activityMessage

def test_scan_should_raise_exception_when_called_with_invalid_arguments():
    # act
    with fake_tango_system(DishLeafNode) as tango_context:
        input_string = "a"
        with pytest.raises(tango.DevFailed):
            tango_context.device.Scan(input_string)

        # assert:
        assert const.ERR_EXE_SCAN_CMD in tango_context.device.activityMessage


def test_end_scan_should_raise_exception_when_called_with_invalid_arguments():
    # act
    with fake_tango_system(DishLeafNode) as tango_context:
        input_string = "a"
        with pytest.raises(tango.DevFailed):
            tango_context.device.EndScan(input_string)

        # assert:
        assert const.ERR_EXE_END_SCAN_CMD in tango_context.device.activityMessage


def test_start_capture_should_raise_exception_when_called_with_invalid_arguments():
    # act
    with fake_tango_system(DishLeafNode) as tango_context:
        input_string = "a"
        with pytest.raises(tango.DevFailed):
            tango_context.device.StartCapture(input_string)

        # assert:
        assert const.ERR_EXE_START_CAPTURE_CMD in tango_context.device.activityMessage


def test_stop_capture_should_raise_exception_when_called_with_invalid_arguments():
    # act
    with fake_tango_system(DishLeafNode) as tango_context:
        input_string = "a"
        with pytest.raises(tango.DevFailed):
            tango_context.device.StopCapture(input_string)

        # assert:
        assert const.ERR_EXE_STOP_CAPTURE_CMD in tango_context.device.activityMessage


def test_slew_should_raise_exception_when_called_with_invalid_arguments():
    # act
    with fake_tango_system(DishLeafNode) as tango_context:
        input_string = "a"
        with pytest.raises(tango.DevFailed):
            tango_context.device.Slew(input_string)

        # assert:
        assert const.ERR_EXE_SLEW_CMD in tango_context.device.activityMessage


def test_track_should_raise_exception_when_called_with_invalid_arguments():
    # act
    with fake_tango_system(DishLeafNode) as tango_context:
        with pytest.raises(tango.DevFailed):
            tango_context.device.Track(track_invalid_arg)

        # assert:
        assert const.ERR_JSON_KEY_NOT_FOUND in tango_context.device.activityMessage


def test_track_should_raise_exception_when_called_with_invalid_json():
    # act
    with fake_tango_system(DishLeafNode) as tango_context:
        with pytest.raises(tango.DevFailed):
            tango_context.device.Track(config_track_invalid_str)

        # assert:
        assert const.ERR_INVALID_JSON in tango_context.device.activityMessage


def test_activity_message():
    # act & assert:
    with fake_tango_system(DishLeafNode) as tango_context:
        tango_context.device.activityMessage = const.STR_OK
        assert tango_context.device.activityMessage == const.STR_OK

def test_status():
    # act & assert:
    with fake_tango_system(DishLeafNode) as tango_context:
        assert tango_context.device.Status() != const.STR_DISH_INIT_SUCCESS


def test_logging_level():
    # act & assert:
    with fake_tango_system(DishLeafNode) as tango_context:
        tango_context.device.loggingLevel = LoggingLevel.INFO
        assert tango_context.device.loggingLevel == LoggingLevel.INFO


def test_logging_targets():
    # act & assert:
    with fake_tango_system(DishLeafNode) as tango_context:
        tango_context.device.loggingTargets = ['console::cout']
        assert 'console::cout' in tango_context.device.loggingTargets


def test_test_mode():
    # act & assert:
    with fake_tango_system(DishLeafNode) as tango_context:
        test_mode = TestMode.NONE
        tango_context.device.testMode = test_mode
        assert tango_context.device.testMode == test_mode


def test_simulation_mode():
    # act & assert:
    with fake_tango_system(DishLeafNode) as tango_context:
        simulation_mode = SimulationMode.FALSE
        tango_context.device.simulationMode = simulation_mode
        assert tango_context.device.simulationMode == simulation_mode


def test_control_mode():
    # act & assert:
    with fake_tango_system(DishLeafNode) as tango_context:
        control_mode = ControlMode.REMOTE
        tango_context.device.controlMode = control_mode
        assert tango_context.device.controlMode == control_mode


def test_health_state():
    # act & assert:
    with fake_tango_system(DishLeafNode) as tango_context:
        assert tango_context.device.healthState == HealthState.OK


def raise_devfailed_exception(cmd_name, callback):
    tango.Except.throw_exception("DishLeafNode_Commandfailed", "This is error message for devfailed",
                                 " ", tango.ErrSeverity.ERR)


def test_stop_track_should_raise_dev_failed(mock_dish_master):
    # arrange:
    tango_context, dish1_proxy_mock, dish_master1_fqdn, event_subscription_map = mock_dish_master
    dish1_proxy_mock.command_inout_asynch.side_effect = raise_devfailed_exception
    # act
    with pytest.raises(tango.DevFailed):
        tango_context.device.StopTrack()
    # assert
    assert const.ERR_EXE_STOP_TRACK_CMD in tango_context.device.activityMessage


def test_setstowmode_command_with_callback_method(event_subscription, mock_dish_master):
    # arrange:
    tango_context, dish1_proxy_mock, dish_master1_fqdn, event_subscription_map = mock_dish_master
    # act
    tango_context.device.SetStowMode()
    dummy_event = command_callback(const.CMD_SET_STOW_MODE)
    event_subscription[const.CMD_SET_STOW_MODE](dummy_event)

    # assert:
    assert const.STR_COMMAND + const.CMD_SET_STOW_MODE in tango_context.device.activityMessage

def test_setstandbylpmode_command_with_callback_method(event_subscription, mock_dish_master):
    # arrange:
    tango_context, dish1_proxy_mock, dish_master1_fqdn, event_subscription_map = mock_dish_master
    # act
    tango_context.device.SetStandByLPMode()
    dummy_event = command_callback(const.CMD_SET_STANDBYLP_MODE)
    event_subscription[const.CMD_SET_STANDBYLP_MODE](dummy_event)

    # assert:
    assert const.STR_COMMAND + const.CMD_SET_STANDBYLP_MODE in tango_context.device.activityMessage


def test_operatemode_command_with_callback_method(event_subscription, mock_dish_master):
    # arrange:
    tango_context, dish1_proxy_mock, dish_master1_fqdn, event_subscription_map = mock_dish_master
    # act
    tango_context.device.SetOperateMode()
    dummy_event = command_callback(const.CMD_SET_OPERATE_MODE)
    event_subscription[const.CMD_SET_OPERATE_MODE](dummy_event)
    # assert:
    assert const.STR_COMMAND + const.CMD_SET_OPERATE_MODE in tango_context.device.activityMessage


def test_scan_command_with_callback_method(event_subscription_with_arg, mock_dish_master):
    # arrange:
    tango_context, dish1_proxy_mock, dish_master1_fqdn, event_subscription_map = mock_dish_master
    scan_input = "0"
    # act
    tango_context.device.Scan(scan_input)
    dummy_event = command_callback(const.CMD_DISH_SCAN)
    event_subscription_with_arg[const.CMD_DISH_SCAN](dummy_event)

    # assert:
    assert const.STR_COMMAND + const.CMD_DISH_SCAN in tango_context.device.activityMessage


def test_endscan_command_with_callback_method(event_subscription_with_arg, mock_dish_master):
    # arrange:
    tango_context, dish1_proxy_mock, dish_master1_fqdn, event_subscription_map = mock_dish_master
    scan_input = "0"
    # act
    tango_context.device.EndScan(scan_input)
    dummy_event = command_callback(const.CMD_STOP_CAPTURE)
    event_subscription_with_arg[const.CMD_STOP_CAPTURE](dummy_event)

    # assert:
    assert const.STR_COMMAND + const.CMD_STOP_CAPTURE in tango_context.device.activityMessage

# TODO: actual AZ and EL values need to be generated.
@pytest.mark.xfail
def test_configure_command_with_callback_method(event_subscription, mock_dish_master):
    # arrange:
    tango_context, dish1_proxy_mock, dish_master1_fqdn, event_subscription_map = mock_dish_master
    dish_config = config_input_str
    # act:
    tango_context.device.Configure(json.dumps(dish_config))
    # act
    dummy_event = command_callback(const.CMD_DISH_CONFIGURE)
    event_subscription[const.CMD_DISH_CONFIGURE](dummy_event)

    # assert:
    assert const.STR_COMMAND + const.CMD_DISH_CONFIGURE in tango_context.device.activityMessage


def test_startcapture_command_with_callback_method(event_subscription_with_arg, mock_dish_master):
    # arrange:
    tango_context, dish1_proxy_mock, dish_master1_fqdn, event_subscription_map = mock_dish_master
    # act
    capture_arg = "0"
    tango_context.device.StartCapture(capture_arg)
    dummy_event = command_callback(const.CMD_START_CAPTURE)
    event_subscription_with_arg[const.CMD_START_CAPTURE](dummy_event)

    # assert:
    assert const.STR_COMMAND + const.CMD_START_CAPTURE in tango_context.device.activityMessage


def test_stopcapture_command_with_callback_method(event_subscription_with_arg, mock_dish_master):
    # arrange:
    tango_context, dish1_proxy_mock, dish_master1_fqdn, event_subscription_map = mock_dish_master
    # act
    capture_arg = "0"
    tango_context.device.StopCapture(capture_arg)
    dummy_event = command_callback(const.CMD_STOP_CAPTURE)
    event_subscription_with_arg[const.CMD_STOP_CAPTURE](dummy_event)

    # assert:
    assert const.STR_COMMAND + const.CMD_STOP_CAPTURE in tango_context.device.activityMessage


def test_setstandbyfpmode_command_with_callback_method(event_subscription, mock_dish_master):
    # arrange:
    tango_context, dish1_proxy_mock, dish_master1_fqdn, event_subscription_map = mock_dish_master
    # act
    tango_context.device.SetStandByFPMode()
    dummy_event = command_callback(const.CMD_SET_STANDBYFP_MODE)
    event_subscription[const.CMD_SET_STANDBYFP_MODE](dummy_event)

    # assert:
    assert const.STR_COMMAND + const.CMD_SET_STANDBYFP_MODE in tango_context.device.activityMessage


def test_slew_command_with_callback_method(event_subscription_with_arg, mock_dish_master):
    # arrange:
    tango_context, dish1_proxy_mock, dish_master1_fqdn, event_subscription_map = mock_dish_master
    # act
    slew_input = '0'
    tango_context.device.Slew(slew_input)
    dummy_event = command_callback(const.CMD_DISH_SLEW)
    event_subscription_with_arg[const.CMD_DISH_SLEW](dummy_event)

    # assert:
    assert const.STR_COMMAND + const.CMD_DISH_SLEW in tango_context.device.activityMessage

# TODO: actual AZ and EL values need to be generated.
@pytest.mark.xfail
def test_track_command_with_callback_method(event_subscription, mock_dish_master):
    # arrange:
    tango_context, dish1_proxy_mock, dish_master1_fqdn, event_subscription_map = mock_dish_master
    # act
    tango_context.device.Track()
    dummy_event = command_callback(const.CMD_TRACK)
    event_subscription[const.CMD_TRACK](dummy_event)

    # assert:
    assert const.STR_COMMAND + const.CMD_TRACK in tango_context.device.activityMessage


def test_stoptrack_command_with_callback_method(event_subscription, mock_dish_master):
    # arrange:
    tango_context, dish1_proxy_mock, dish_master1_fqdn, event_subscription_map = mock_dish_master
    # act
    #slew_input = '0'
    tango_context.device.StopTrack()
    dummy_event = command_callback(const.CMD_STOP_TRACK)
    event_subscription[const.CMD_STOP_TRACK](dummy_event)

    # assert:
    assert const.STR_COMMAND + const.CMD_STOP_TRACK in tango_context.device.activityMessage


def test_abort_command_with_callback_method(event_subscription, mock_dish_master):
    # arrange:
    tango_context, dish1_proxy_mock, dish_master1_fqdn, event_subscription_map = mock_dish_master
    # act
    tango_context.device.Abort()
    dummy_event = command_callback(const.CMD_ABORT)
    event_subscription[const.CMD_ABORT](dummy_event)

    # assert:
    assert const.STR_COMMAND + const.CMD_ABORT in tango_context.device.activityMessage

def test_restart_command_with_callback_method(event_subscription, mock_dish_master):
    # arrange:
    tango_context, dish1_proxy_mock, dish_master1_fqdn, event_subscription_map = mock_dish_master
    # act
    tango_context.device.Restart()
    dummy_event = command_callback(const.CMD_RESTART)
    event_subscription[const.CMD_RESTART](dummy_event)

    # assert:
    assert const.STR_COMMAND + const.CMD_RESTART in tango_context.device.activityMessage


def test_setstowmode_command_with_callback_method_with_event_error(event_subscription, mock_dish_master):
    # arrange:
    tango_context, dish1_proxy_mock, dish_master1_fqdn, event_subscription_map = mock_dish_master
    # act
    tango_context.device.SetStowMode()
    dummy_event = command_callback_with_event_error(const.CMD_SET_STOW_MODE)
    event_subscription[const.CMD_SET_STOW_MODE](dummy_event)

    # assert:
    assert const.ERR_INVOKING_CMD + const.CMD_SET_STOW_MODE in tango_context.device.activityMessage


def test_setstandbylpmode_command_with_callback_method_with_event_error(event_subscription, mock_dish_master):
    # arrange:
    tango_context, dish1_proxy_mock, dish_master1_fqdn, event_subscription_map = mock_dish_master
    # act
    tango_context.device.SetStandByLPMode()
    dummy_event = command_callback_with_event_error(const.CMD_SET_STANDBYLP_MODE)
    event_subscription[const.CMD_SET_STANDBYLP_MODE](dummy_event)

    # assert:
    assert const.ERR_INVOKING_CMD + const.CMD_SET_STANDBYLP_MODE in tango_context.device.activityMessage

def test_setoperatemode_command_with_callback_method_with_event_error(event_subscription, mock_dish_master):
    # arrange:
    tango_context, dish1_proxy_mock, dish_master1_fqdn, event_subscription_map = mock_dish_master
    # act
    tango_context.device.SetOperateMode()
    dummy_event = command_callback_with_event_error(const.CMD_SET_OPERATE_MODE)
    event_subscription[const.CMD_SET_OPERATE_MODE](dummy_event)

    # assert:
    assert const.ERR_INVOKING_CMD + const.CMD_SET_OPERATE_MODE in tango_context.device.activityMessage


def test_scan_command_with_callback_method_with_event_error(event_subscription_with_arg, mock_dish_master):
    # arrange:
    tango_context, dish1_proxy_mock, dish_master1_fqdn, event_subscription_map = mock_dish_master

    scan_input = "0"
    # act
    tango_context.device.Scan(scan_input)
    dummy_event = command_callback_with_event_error(const.CMD_DISH_SCAN)
    event_subscription_with_arg[const.CMD_DISH_SCAN](dummy_event)

    # assert:
    assert const.ERR_INVOKING_CMD + const.CMD_DISH_SCAN in tango_context.device.activityMessage


def test_startcapture_command_with_callback_method_with_event_error(event_subscription_with_arg, mock_dish_master):
    # arrange:
    tango_context, dish1_proxy_mock, dish_master1_fqdn, event_subscription_map = mock_dish_master
    capture_arg = "0"

    # act
    tango_context.device.StartCapture(capture_arg)
    dummy_event = command_callback_with_event_error(const.CMD_START_CAPTURE)
    event_subscription_with_arg[const.CMD_START_CAPTURE](dummy_event)

    # assert:
    assert const.ERR_INVOKING_CMD + const.CMD_START_CAPTURE in tango_context.device.activityMessage


def test_stopcapture_command_with_callback_method_with_event_error(event_subscription_with_arg, mock_dish_master):
    # arrange:
    tango_context, dish1_proxy_mock, dish_master1_fqdn, event_subscription_map = mock_dish_master
    capture_arg = "0"
    # act
    tango_context.device.StopCapture(capture_arg)
    dummy_event = command_callback_with_event_error(const.CMD_STOP_CAPTURE)
    event_subscription_with_arg[const.CMD_STOP_CAPTURE](dummy_event)

    # assert:
    assert const.ERR_INVOKING_CMD + const.CMD_STOP_CAPTURE in tango_context.device.activityMessage


def test_setstandbyfpmode_command_with_callback_method_with_event_error(event_subscription, mock_dish_master):
    # arrange:
    tango_context, dish1_proxy_mock, dish_master1_fqdn, event_subscription_map = mock_dish_master
    # act
    tango_context.device.SetStandByFPMode()
    dummy_event = command_callback_with_event_error(const.CMD_SET_STANDBYFP_MODE)
    event_subscription[const.CMD_SET_STANDBYFP_MODE](dummy_event)

    # assert:
    assert const.ERR_INVOKING_CMD + const.CMD_SET_STANDBYFP_MODE in tango_context.device.activityMessage


def test_slew_command_with_callback_method_with_event_error(event_subscription_with_arg, mock_dish_master):
    # arrange:
    tango_context, dish1_proxy_mock, dish_master1_fqdn, event_subscription_map = mock_dish_master
    slew_arg = "0"
    # act
    tango_context.device.Slew(slew_arg)
    dummy_event = command_callback_with_event_error(const.CMD_DISH_SLEW)
    event_subscription_with_arg[const.CMD_DISH_SLEW](dummy_event)

    # assert:
    assert const.ERR_INVOKING_CMD + const.CMD_DISH_SLEW in tango_context.device.activityMessage


def test_stoptrack_command_with_callback_method_with_event_error(event_subscription, mock_dish_master):
    # arrange:
    tango_context, dish1_proxy_mock, dish_master1_fqdn, event_subscription_map = mock_dish_master
    # act
    tango_context.device.StopTrack()
    dummy_event = command_callback_with_event_error(const.CMD_STOP_TRACK)
    event_subscription[const.CMD_STOP_TRACK](dummy_event)

    # assert:
    assert const.ERR_INVOKING_CMD + const.CMD_STOP_TRACK in tango_context.device.activityMessage


def test_abort_command_with_callback_method_with_event_error(event_subscription, mock_dish_master):
    # arrange:
    tango_context, dish1_proxy_mock, dish_master1_fqdn, event_subscription_map = mock_dish_master
    # act
    tango_context.device.Abort()
    dummy_event = command_callback_with_event_error(const.CMD_ABORT)
    event_subscription[const.CMD_ABORT](dummy_event)

    # assert:
    assert const.ERR_INVOKING_CMD + const.CMD_ABORT in tango_context.device.activityMessage


def test_restart_command_with_callback_method_with_event_error(event_subscription, mock_dish_master):
    # arrange:
    tango_context, dish1_proxy_mock, dish_master1_fqdn, event_subscription_map = mock_dish_master
    # act
    tango_context.device.Restart()
    dummy_event = command_callback_with_event_error(const.CMD_RESTART)
    event_subscription[const.CMD_RESTART](dummy_event)

    # assert:
    assert const.ERR_INVOKING_CMD + const.CMD_RESTART in tango_context.device.activityMessage


def test_version_id():
    """Test for versionId"""
    with fake_tango_system(DishLeafNode) as tango_context:
        assert tango_context.device.versionId == release.version


def test_build_state():
    """Test for buildState"""
    with fake_tango_system(DishLeafNode) as tango_context:
        assert tango_context.device.buildState == ('{},{},{}'.format(release.name,release.version,release.description))



def command_callback(command_name):
    fake_event = MagicMock()
    fake_event.err = False
    fake_event.errors = 'Event error'
    fake_event.cmd_name = f"{command_name}"
    return fake_event


def command_callback_with_event_error(command_name):
    fake_event = MagicMock()
    fake_event.err = True
    fake_event.errors = 'Event error'
    fake_event.cmd_name = f"{command_name}"
    return fake_event


def command_callback_with_command_exception(command_name):
    return Exception("Exception in callback")


def assert_activity_message(device_proxy, expected_message):
    assert device_proxy.activityMessage == expected_message  # reads tango attribute


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
