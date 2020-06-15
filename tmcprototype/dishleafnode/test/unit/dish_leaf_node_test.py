# Standard Python imports
import contextlib
import importlib
import types
import sys
import json
import threading
import mock
from mock import Mock, MagicMock
import tango
import pytest

# Tango imports
from tango import DevState
from tango.test_context import DeviceTestContext

# Additional import
from dishleafnode import DishLeafNode, const
from ska.base.control_model import HealthState, AdminMode, TestMode, SimulationMode, ControlMode
from ska.base.control_model import ObsState, LoggingLevel


def test_start_scan_should_command_dish_to_start_scan_when_it_is_ready():
    # arrange:
    dish_master1_fqdn = 'mid_d0001/elt/master'
    dut_properties = {'DishMasterFQDN': dish_master1_fqdn}

    dish1_proxy_mock = Mock()
    dish1_proxy_mock.obsState = ObsState.READY

    proxies_to_mock = {dish_master1_fqdn: dish1_proxy_mock}

    with fake_tango_system(DishLeafNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        scan_input = "0"
        # act:
        tango_context.device.Scan(scan_input)

        # assert:
        if type(float(scan_input)) == float:
            dish1_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_DISH_SCAN, scan_input,
                                                                     any_method(with_name='commandCallback'))


# TODO: actual AZ and EL values need to be generated.
@pytest.mark.xfail
def test_configure_to_send_correct_configuration_data_when_dish_is_idle():
    # arrange:
    dish_master1_fqdn = 'mid_d0001/elt/master'
    dut_properties = {'DishMasterFQDN': dish_master1_fqdn}

    dish1_proxy_mock = Mock()
    dish1_proxy_mock.obsState = ObsState.IDLE
    proxies_to_mock = {dish_master1_fqdn: dish1_proxy_mock}

    with fake_tango_system(DishLeafNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        dish_config = {"pointing": {"target": {"system": "ICRS", "name": "Polaris Australis", "RA": "21:08:47.92",
                                               "dec": "-88:57:22.9"}}, "dish": {"receiverBand": "1"}}
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
                                                                 any_method(with_name='commandCallback'))


def test_end_scan_should_command_dish_to_end_scan_when_it_is_scanning():
    # arrange:
    dish_master1_fqdn = 'mid_d0001/elt/master'
    dut_properties = {'DishMasterFQDN': dish_master1_fqdn}

    dish1_proxy_mock = Mock()
    dish1_proxy_mock.obsState = ObsState.SCANNING
    proxies_to_mock = {dish_master1_fqdn: dish1_proxy_mock}

    with fake_tango_system(DishLeafNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        scan_input = "0"
        # act:
        tango_context.device.EndScan(scan_input)

        # assert:
        if type(float(scan_input)) == float:
            dish1_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_STOP_CAPTURE, scan_input,
                                                                     any_method(with_name='commandCallback'))


def test_standby_lp_mode_should_command_dish_to_standby():
    # arrange:
    dish_master1_fqdn = 'mid_d0001/elt/master'
    dut_properties = {'DishMasterFQDN': dish_master1_fqdn}

    dish1_proxy_mock = Mock()

    proxies_to_mock = {dish_master1_fqdn: dish1_proxy_mock}

    with fake_tango_system(DishLeafNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        # act:
        tango_context.device.SetStandByLPMode()

        # assert:
        dish1_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_SET_STANDBYLP_MODE,
                                                                 any_method(with_name='commandCallback'))


def test_set_operate_mode_should_command_dish_to_start():
    # arrange:
    dish_master1_fqdn = 'mid_d0001/elt/master'
    dut_properties = {'DishMasterFQDN': dish_master1_fqdn}

    dish1_proxy_mock = Mock()

    proxies_to_mock = {dish_master1_fqdn: dish1_proxy_mock}

    with fake_tango_system(DishLeafNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        # act:
        tango_context.device.SetOperateMode()

        # assert:
        dish1_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_SET_OPERATE_MODE,
                                                                 any_method(with_name='commandCallback'))


@pytest.mark.xfail
def test_track_should_command_dish_to_start_tracking():
    # arrange:
    dish_master1_fqdn = 'mid_d0001/elt/master'
    dut_properties = {'DishMasterFQDN': dish_master1_fqdn}

    dish1_proxy_mock = Mock()

    proxies_to_mock = {dish_master1_fqdn: dish1_proxy_mock}

    with fake_tango_system(DishLeafNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        input_string = {"pointing": {"target": {"system": "ICRS", "name": "Polaris Australis", "RA": "21:08:47.92",
                                                "dec": "-88:57:22.9"}}, "dish": {"receiverBand": "1"}}

        # act:
        tango_context.device.Track(json.dumps(input_string))

        # assert:
        jsonArgument = input_string
        ra_value = (jsonArgument["pointing"]["target"]["RA"])
        dec_value = (jsonArgument["pointing"]["target"]["dec"])
        radec_value = 'radec' + ',' + str(ra_value) + ',' + str(dec_value)
        dish1_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_TRACK, "0",
                                                                 any_method(with_name='commandCallback'))


def test_stop_track_should_command_dish_to_stop_tracking():
    # arrange:
    dish_master1_fqdn = 'mid_d0001/elt/master'
    dut_properties = {'DishMasterFQDN': dish_master1_fqdn}

    dish1_proxy_mock = Mock()

    proxies_to_mock = {dish_master1_fqdn: dish1_proxy_mock}

    with fake_tango_system(DishLeafNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        # act:
        tango_context.device.StopTrack()

        # assert:
        dish1_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_STOP_TRACK,
                                                                 any_method(with_name='commandCallback'))


def test_slew_should_command_the_dish_to_slew_towards_the_set_pointing_coordinates():
    dish_master1_fqdn = 'mid_d0001/elt/master'
    dut_properties = {'DishMasterFQDN': dish_master1_fqdn}

    dish1_proxy_mock = Mock()

    proxies_to_mock = {dish_master1_fqdn: dish1_proxy_mock}

    with fake_tango_system(DishLeafNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        slew_arg = "0"
        # act:
        tango_context.device.Slew(slew_arg)

        # assert:
        if type(float(slew_arg)) == float:
            dish1_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_DISH_SLEW, slew_arg,
                                                                     any_method(with_name='commandCallback'))


def test_start_capture_should_command_dish_to_start_capture_on_the_set_configured_band():
    dish_master1_fqdn = 'mid_d0001/elt/master'
    dut_properties = {'DishMasterFQDN': dish_master1_fqdn}

    dish1_proxy_mock = Mock()

    proxies_to_mock = {dish_master1_fqdn: dish1_proxy_mock}

    with fake_tango_system(DishLeafNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        capture_arg = "0"
        # act:
        tango_context.device.StartCapture(capture_arg)

        # assert:
        if type(float(capture_arg)) == float:
            dish1_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_START_CAPTURE, capture_arg,
                                                                     any_method(with_name='commandCallback'))


def test_stop_capture_should_command_dish_to_stop_capture_on_the_set_configured_band():
    dish_master1_fqdn = 'mid_d0001/elt/master'
    dut_properties = {'DishMasterFQDN': dish_master1_fqdn}

    dish1_proxy_mock = Mock()

    proxies_to_mock = {dish_master1_fqdn: dish1_proxy_mock}

    with fake_tango_system(DishLeafNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        capture_arg = "0"
        # act:
        tango_context.device.StopCapture(capture_arg)

        # assert:
        if type(float(capture_arg)) == float:
            dish1_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_STOP_CAPTURE, capture_arg,
                                                                     any_method(with_name='commandCallback'))


def test_set_standby_fp_mode_should_command_dish_to_transition_to_standby_fp_mode():
    dish_master1_fqdn = 'mid_d0001/elt/master'
    dut_properties = {'DishMasterFQDN': dish_master1_fqdn}

    dish1_proxy_mock = Mock()

    proxies_to_mock = {dish_master1_fqdn: dish1_proxy_mock}

    with fake_tango_system(DishLeafNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        # act:
        tango_context.device.SetStandbyFPMode()

        # assert:
        dish1_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_SET_STANDBYFP_MODE,
                                                                 any_method(with_name='commandCallback'))


def test_set_stow_mode_should_command_dish_to_transit_to_stow_mode():
    dish_master1_fqdn = 'mid_d0001/elt/master'
    dut_properties = {'DishMasterFQDN': dish_master1_fqdn}

    dish1_proxy_mock = Mock()

    proxies_to_mock = {dish_master1_fqdn: dish1_proxy_mock}

    with fake_tango_system(DishLeafNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        # act:
        tango_context.device.SetStowMode()

        # assert:
        dish1_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_SET_STOW_MODE,
                                                                 any_method(with_name='commandCallback'))


def create_dummy_event_for_dishmode(device_fqdn, dish_mode_value, attribute):
    fake_event = Mock()
    fake_event.err = False
    fake_event.attr_name = f"{device_fqdn}/{attribute}"
    fake_event.attr_value.value = dish_mode_value
    return fake_event


def test_dish_leaf_node_dish_mode_is_off_when_dish_is_off():
    # arrange:
    dish_master1_fqdn = 'mid_d0001/elt/master'
    dish_master_dishmode_attribute = 'dishMode'
    initial_dut_properties = {'DishMasterFQDN': dish_master1_fqdn}

    event_subscription_map = {}

    dish_master_device_proxy_mock = Mock()
    dish_master_device_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args,
               **kwargs: event_subscription_map.update({attr_name: callback}))

    proxies_to_mock = {dish_master1_fqdn: dish_master_device_proxy_mock}

    with fake_tango_system(DishLeafNode, initial_dut_properties, proxies_to_mock) as tango_context:
        # act:
        dish_mode_value = 0
        dummy_event = create_dummy_event_for_dishmode(dish_master1_fqdn, dish_mode_value,
                                                      dish_master_dishmode_attribute)
        event_subscription_map[dish_master_dishmode_attribute](dummy_event)

        # assert:
        assert tango_context.device.activityMessage == const.STR_DISH_OFF_MODE


def test_dish_leaf_node_dish_mode_is_startup_when_dish_is_startup():
    # arrange:
    dish_master1_fqdn = 'mid_d0001/elt/master'
    dish_master_dishmode_attribute = 'dishMode'
    initial_dut_properties = {'DishMasterFQDN': dish_master1_fqdn}
    event_subscription_map = {}
    dish_master_device_proxy_mock = Mock()
    dish_master_device_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args,
               **kwargs: event_subscription_map.update({attr_name: callback}))

    proxies_to_mock = {dish_master1_fqdn: dish_master_device_proxy_mock}

    with fake_tango_system(DishLeafNode, initial_dut_properties, proxies_to_mock) as tango_context:
        # act:
        dish_mode_value = 1
        dummy_event = create_dummy_event_for_dishmode(dish_master1_fqdn, dish_mode_value,
                                                      dish_master_dishmode_attribute)
        event_subscription_map[dish_master_dishmode_attribute](dummy_event)

        # assert:
        assert tango_context.device.activityMessage == const.STR_DISH_STARTUP_MODE


def test_dish_leaf_node_dish_mode_is_shutdown_when_dish_is_shutdown():
    # arrange:
    dish_master1_fqdn = 'mid_d0001/elt/master'
    dish_master_dishmode_attribute = 'dishMode'
    initial_dut_properties = {'DishMasterFQDN': dish_master1_fqdn}

    event_subscription_map = {}
    dish_master_device_proxy_mock = Mock()
    dish_master_device_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args,
               **kwargs: event_subscription_map.update({attr_name: callback}))

    proxies_to_mock = {dish_master1_fqdn: dish_master_device_proxy_mock}

    with fake_tango_system(DishLeafNode, initial_dut_properties, proxies_to_mock) as tango_context:
        # act:
        dish_mode_value = 2
        dummy_event = create_dummy_event_for_dishmode(dish_master1_fqdn, dish_mode_value,
                                                      dish_master_dishmode_attribute)
        event_subscription_map[dish_master_dishmode_attribute](dummy_event)

        # assert:
        assert tango_context.device.activityMessage == const.STR_DISH_SHUTDOWN_MODE


def test_dish_leaf_node_dish_mode_is_standby_when_dish_is_standby():
    # arrange:
    dish_master1_fqdn = 'mid_d0001/elt/master'
    dish_master_dishmode_attribute = 'dishMode'
    initial_dut_properties = {'DishMasterFQDN': dish_master1_fqdn}

    event_subscription_map = {}

    dish_master_device_proxy_mock = Mock()
    dish_master_device_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args,
               **kwargs: event_subscription_map.update({attr_name: callback}))

    proxies_to_mock = {dish_master1_fqdn: dish_master_device_proxy_mock}

    with fake_tango_system(DishLeafNode, initial_dut_properties, proxies_to_mock) as tango_context:
        # act:
        dish_mode_value = 3
        dummy_event = create_dummy_event_for_dishmode(dish_master1_fqdn, dish_mode_value,
                                                      dish_master_dishmode_attribute)
        event_subscription_map[dish_master_dishmode_attribute](dummy_event)

        # assert:
        assert tango_context.device.activityMessage == const.STR_DISH_STANDBYLP_MODE


def test_dish_leaf_node_dish_mode_is_stand_by_fp_when_dish_is_stand_by_fp():
    # arrange:
    dish_master1_fqdn = 'mid_d0001/elt/master'
    dish_master_dishmode_attribute = 'dishMode'
    initial_dut_properties = {'DishMasterFQDN': dish_master1_fqdn}

    event_subscription_map = {}

    dish_master_device_proxy_mock = Mock()
    dish_master_device_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args,
               **kwargs: event_subscription_map.update({attr_name: callback}))

    proxies_to_mock = {dish_master1_fqdn: dish_master_device_proxy_mock}

    with fake_tango_system(DishLeafNode, initial_dut_properties, proxies_to_mock) as tango_context:
        # act:
        dish_mode_value = 4
        dummy_event = create_dummy_event_for_dishmode(dish_master1_fqdn, dish_mode_value,
                                                      dish_master_dishmode_attribute)
        event_subscription_map[dish_master_dishmode_attribute](dummy_event)

        # assert:
        assert tango_context.device.activityMessage == const.STR_DISH_STANDBYFP_MODE


def test_dish_leaf_node_dish_mode_is_maint_when_dish_is_maint():
    # arrange:
    dish_master1_fqdn = 'mid_d0001/elt/master'
    dish_master_dishmode_attribute = 'dishMode'
    initial_dut_properties = {'DishMasterFQDN': dish_master1_fqdn}

    event_subscription_map = {}

    dish_master_device_proxy_mock = Mock()
    dish_master_device_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args,
               **kwargs: event_subscription_map.update({attr_name: callback}))

    proxies_to_mock = {dish_master1_fqdn: dish_master_device_proxy_mock}

    with fake_tango_system(DishLeafNode, initial_dut_properties, proxies_to_mock) as tango_context:
        # act:
        dish_mode_value = 5
        dummy_event = create_dummy_event_for_dishmode(dish_master1_fqdn, dish_mode_value,
                                                      dish_master_dishmode_attribute)
        event_subscription_map[dish_master_dishmode_attribute](dummy_event)

        # assert:
        assert tango_context.device.activityMessage == const.STR_DISH_MAINT_MODE


def test_dish_leaf_node_dish_mode_is_stow_when_dish_is_stow():
    # arrange:
    dish_master1_fqdn = 'mid_d0001/elt/master'
    dish_master_dishmode_attribute = 'dishMode'
    initial_dut_properties = {'DishMasterFQDN': dish_master1_fqdn}

    event_subscription_map = {}

    dish_master_device_proxy_mock = Mock()
    dish_master_device_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args,
               **kwargs: event_subscription_map.update({attr_name: callback}))

    proxies_to_mock = {dish_master1_fqdn: dish_master_device_proxy_mock}

    with fake_tango_system(DishLeafNode, initial_dut_properties, proxies_to_mock) as tango_context:
        # act:
        dish_mode_value = 6
        dummy_event = create_dummy_event_for_dishmode(dish_master1_fqdn, dish_mode_value,
                                                      dish_master_dishmode_attribute)
        event_subscription_map[dish_master_dishmode_attribute](dummy_event)

        # assert:
        assert tango_context.device.activityMessage == const.STR_DISH_STOW_MODE


def test_dish_leaf_node_dish_mode_is_config_when_dish_is_config():
    # arrange:
    dish_master1_fqdn = 'mid_d0001/elt/master'
    dish_master_dishmode_attribute = 'dishMode'
    initial_dut_properties = {'DishMasterFQDN': dish_master1_fqdn}

    event_subscription_map = {}

    dish_master_device_proxy_mock = Mock()
    dish_master_device_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args,
               **kwargs: event_subscription_map.update({attr_name: callback}))

    proxies_to_mock = {dish_master1_fqdn: dish_master_device_proxy_mock}

    with fake_tango_system(DishLeafNode, initial_dut_properties, proxies_to_mock) as tango_context:
        # act:
        dish_mode_value = 7
        dummy_event = create_dummy_event_for_dishmode(dish_master1_fqdn, dish_mode_value,
                                                      dish_master_dishmode_attribute)
        event_subscription_map[dish_master_dishmode_attribute](dummy_event)

        # assert:
        assert tango_context.device.activityMessage == const.STR_DISH_CONFIG_MODE


def test_dish_leaf_node_dish_mode_is_operate_when_dish_is_operate():
    # arrange:
    dish_master1_fqdn = 'mid_d0001/elt/master'
    dish_master_dishmode_attribute = 'dishMode'
    initial_dut_properties = {'DishMasterFQDN': dish_master1_fqdn}

    event_subscription_map = {}

    dish_master_device_proxy_mock = Mock()
    dish_master_device_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args,
               **kwargs: event_subscription_map.update({attr_name: callback}))

    proxies_to_mock = {dish_master1_fqdn: dish_master_device_proxy_mock}

    with fake_tango_system(DishLeafNode, initial_dut_properties, proxies_to_mock) as tango_context:
        # act:
        dish_mode_value = 8
        dummy_event = create_dummy_event_for_dishmode(dish_master1_fqdn, dish_mode_value,
                                                      dish_master_dishmode_attribute)
        event_subscription_map[dish_master_dishmode_attribute](dummy_event)

        # assert:
        assert tango_context.device.activityMessage == const.STR_DISH_OPERATE_MODE


def test_dish_leaf_node_dish_mode_is_unknown():
    # arrange:
    dish_master1_fqdn = 'mid_d0001/elt/master'
    dish_master_dishmode_attribute = 'dishMode'
    initial_dut_properties = {'DishMasterFQDN': dish_master1_fqdn}

    event_subscription_map = {}

    dish_master_device_proxy_mock = Mock()
    dish_master_device_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args,
               **kwargs: event_subscription_map.update({attr_name: callback}))

    proxies_to_mock = {dish_master1_fqdn: dish_master_device_proxy_mock}

    with fake_tango_system(DishLeafNode, initial_dut_properties, proxies_to_mock) as tango_context:
        # act:
        dish_mode_value = 9
        dummy_event = create_dummy_event_for_dishmode(dish_master1_fqdn, dish_mode_value,
                                                      dish_master_dishmode_attribute)
        event_subscription_map[dish_master_dishmode_attribute](dummy_event)

        # assert:
        assert const.STR_DISH_UNKNOWN_MODE in tango_context.device.activityMessage


def test_dish_leaf_node_dish_mode_with_error_event():
    # arrange:
    dish_master1_fqdn = 'mid_d0001/elt/master'
    dish_master_dishmode_attribute = 'dishMode'
    initial_dut_properties = {'DishMasterFQDN': dish_master1_fqdn}

    event_subscription_map = {}

    dish_master_device_proxy_mock = Mock()
    dish_master_device_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args,
               **kwargs: event_subscription_map.update({attr_name: callback}))

    proxies_to_mock = {dish_master1_fqdn: dish_master_device_proxy_mock}

    with fake_tango_system(DishLeafNode, initial_dut_properties, proxies_to_mock) as tango_context:
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


def test_dish_leaf_node_when_dish_capturing_callback_is_true():
    # arrange:
    dish_master1_fqdn = 'mid_d0001/elt/master'
    dish_master_capturing_attribute = 'capturing'
    initial_dut_properties = {'DishMasterFQDN': dish_master1_fqdn}

    event_subscription_map = {}

    dish_master_device_proxy_mock = Mock()
    dish_master_device_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args,
               **kwargs: event_subscription_map.update({attr_name: callback}))

    proxies_to_mock = {dish_master1_fqdn: dish_master_device_proxy_mock}

    with fake_tango_system(DishLeafNode, initial_dut_properties, proxies_to_mock) as tango_context:
        # act:
        dish_capturing_value = True
        dummy_event = create_dummy_event_for_dish_capturing(dish_master1_fqdn, dish_capturing_value,
                                                            dish_master_capturing_attribute)
        event_subscription_map[dish_master_capturing_attribute](dummy_event)

        # assert:
        assert tango_context.device.activityMessage == const.STR_DISH_CAPTURING_TRUE


def test_dish_leaf_node_when_dish_capturing_callback_is_false():
    # arrange:
    dish_master1_fqdn = 'mid_d0001/elt/master'
    dish_master_capturing_attribute = 'capturing'
    initial_dut_properties = {'DishMasterFQDN': dish_master1_fqdn}

    event_subscription_map = {}

    dish_master_device_proxy_mock = Mock()
    dish_master_device_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args,
               **kwargs: event_subscription_map.update({attr_name: callback}))

    proxies_to_mock = {dish_master1_fqdn: dish_master_device_proxy_mock}

    with fake_tango_system(DishLeafNode, initial_dut_properties, proxies_to_mock) as tango_context:
        # act:
        dish_capturing_value = False
        dummy_event = create_dummy_event_for_dish_capturing(dish_master1_fqdn, dish_capturing_value,
                                                            dish_master_capturing_attribute)
        event_subscription_map[dish_master_capturing_attribute](dummy_event)

        # assert:
        assert tango_context.device.activityMessage == const.STR_DISH_CAPTURING_FALSE


def test_dish_leaf_node_when_invalid_attribute_value_for_dish_capturing():
    # arrange:
    dish_master1_fqdn = 'mid_d0001/elt/master'
    dish_master_capturing_attribute = 'capturing'
    initial_dut_properties = {'DishMasterFQDN': dish_master1_fqdn}

    event_subscription_map = {}

    dish_master_device_proxy_mock = Mock()
    dish_master_device_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args,
               **kwargs: event_subscription_map.update({attr_name: callback}))

    proxies_to_mock = {dish_master1_fqdn: dish_master_device_proxy_mock}

    with fake_tango_system(DishLeafNode, initial_dut_properties, proxies_to_mock) as tango_context:
        # act:
        dish_capturing_value = 'Invalid_value'
        dummy_event = create_dummy_event_for_dish_capturing(dish_master1_fqdn, dish_capturing_value,
                                                            dish_master_capturing_attribute)
        event_subscription_map[dish_master_capturing_attribute](dummy_event)

        # assert:
        assert const.STR_DISH_CAPTURING_UNKNOWN in tango_context.device.activityMessage


def test_dish_leaf_node_when_dish_capturing_callback_with_error_event():
    # arrange:
    dish_master1_fqdn = 'mid_d0001/elt/master'
    dish_master_capturing_attribute = 'capturing'
    initial_dut_properties = {'DishMasterFQDN': dish_master1_fqdn}

    event_subscription_map = {}

    dish_master_device_proxy_mock = Mock()
    dish_master_device_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args,
               **kwargs: event_subscription_map.update({attr_name: callback}))

    proxies_to_mock = {dish_master1_fqdn: dish_master_device_proxy_mock}

    with fake_tango_system(DishLeafNode, initial_dut_properties, proxies_to_mock) as tango_context:
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


def test_dish_leaf_node_when_achieved_pointing_callback_is_true():
    # arrange:
    dish_master1_fqdn = 'mid_d0001/elt/master'
    dish_master_achieved_pointing_attribute = 'achievedPointing'
    initial_dut_properties = {'DishMasterFQDN': dish_master1_fqdn}

    event_subscription_map = {}

    dish_master_device_proxy_mock = Mock()
    dish_master_device_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args,
               **kwargs: event_subscription_map.update({attr_name: callback}))

    proxies_to_mock = {dish_master1_fqdn: dish_master_device_proxy_mock}

    with fake_tango_system(DishLeafNode, initial_dut_properties, proxies_to_mock) as tango_context:
        # act:
        attribute = 'achievedPointing'
        value = 0.0
        dummy_event = create_dummy_event(dish_master1_fqdn, attribute, value)
        event_subscription_map[dish_master_achieved_pointing_attribute](dummy_event)

        # assert:
        assert tango_context.device.activityMessage == const.STR_ACHIEVED_POINTING + \
               str(dummy_event.attr_value.value)


def test_dish_leaf_node_when_achieved_pointing_callback_with_error_event():
    # arrange:
    dish_master1_fqdn = 'mid_d0001/elt/master'
    dish_master_achieved_pointing_attribute = 'achievedPointing'
    initial_dut_properties = {'DishMasterFQDN': dish_master1_fqdn}

    event_subscription_map = {}

    dish_master_device_proxy_mock = Mock()
    dish_master_device_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args,
               **kwargs: event_subscription_map.update({attr_name: callback}))

    proxies_to_mock = {dish_master1_fqdn: dish_master_device_proxy_mock}

    with fake_tango_system(DishLeafNode, initial_dut_properties, proxies_to_mock) as tango_context:
        # act:
        attribute = 'achievedPointing'
        value = 0.0
        dummy_event = create_dummy_event_with_error(dish_master1_fqdn, attribute, value)
        event_subscription_map[dish_master_achieved_pointing_attribute](dummy_event)

        # assert:
        assert const.ERR_ON_SUBS_DISH_ACHVD_ATTR in tango_context.device.activityMessage


def test_dish_leaf_node_when_desired_pointing_callback_is_true():
    # arrange:
    dish_master1_fqdn = 'mid_d0001/elt/master'
    dish_master_desired_pointing_attribute = 'desiredPointing'
    initial_dut_properties = {'DishMasterFQDN': dish_master1_fqdn}

    event_subscription_map = {}

    dish_master_device_proxy_mock = Mock()
    dish_master_device_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args,
               **kwargs: event_subscription_map.update({attr_name: callback}))

    proxies_to_mock = {dish_master1_fqdn: dish_master_device_proxy_mock}

    with fake_tango_system(DishLeafNode, initial_dut_properties, proxies_to_mock) as tango_context:
        # act:
        attribute = 'desiredPointing'
        value = 0.0
        dummy_event = create_dummy_event(dish_master1_fqdn, attribute, value)
        event_subscription_map[dish_master_desired_pointing_attribute](dummy_event)

        # assert:
        assert tango_context.device.activityMessage == const.STR_DESIRED_POINTING + \
               str(dummy_event.attr_value.value)


def test_dish_leaf_node_when_desired_pointing_callback_with_error_event():
    # arrange:
    dish_master1_fqdn = 'mid_d0001/elt/master'
    dish_master_desired_pointing_attribute = 'desiredPointing'
    initial_dut_properties = {'DishMasterFQDN': dish_master1_fqdn}

    event_subscription_map = {}

    dish_master_device_proxy_mock = Mock()
    dish_master_device_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args,
               **kwargs: event_subscription_map.update({attr_name: callback}))

    proxies_to_mock = {dish_master1_fqdn: dish_master_device_proxy_mock}

    with fake_tango_system(DishLeafNode, initial_dut_properties, proxies_to_mock) as tango_context:
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
        input_string = '{"Invalid Key"}'
        with pytest.raises(tango.DevFailed):
            tango_context.device.Configure(input_string)

        # assert:
        assert const.ERR_INVALID_JSON in tango_context.device.activityMessage


def test_configure_should_raise_exception_when_called_with_invalid_arguments():
    # act
    with fake_tango_system(DishLeafNode) as tango_context:
        input_string = []
        input_string.append(
            '{"pointing":{"target":{"system":"ICRS","name":"Polaris Australis","RA":"21:08:47.92","":"-88:5.7:22.9"}},\
            "dish":{"receiverBand":"1"}}')
        with pytest.raises(tango.DevFailed):
            tango_context.device.Configure(input_string[0])

        # assert:
        assert const.ERR_JSON_KEY_NOT_FOUND in tango_context.device.activityMessage


def test_configure_should_raise_generic_exception():
    # act
    with fake_tango_system(DishLeafNode) as tango_context:
        Configure_input = '[123]'
        with pytest.raises(tango.DevFailed):
            tango_context.device.Configure(Configure_input)

        # assert:
        assert const.ERR_EXE_CONFIGURE_CMD in tango_context.device.activityMessage


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
        input_string = \
            '{"pointing":{"target":{"system":"ICRS","name":"Polaris Australis","":"21:08:47.92","dec":"-88:57:22.9"}},' \
            '"dish":{"receiverBand":"1"}}'

        with pytest.raises(tango.DevFailed):
            tango_context.device.Track(input_string)

        # assert:
        assert const.ERR_JSON_KEY_NOT_FOUND in tango_context.device.activityMessage


def test_track_should_raise_exception_when_called_with_invalid_json():
    # act
    with fake_tango_system(DishLeafNode) as tango_context:
        input_string = '{"Invalid Key"}'

        with pytest.raises(tango.DevFailed):
            tango_context.device.Track(input_string)

        # assert:
        assert const.ERR_INVALID_JSON in tango_context.device.activityMessage


def test_activity_message():
    # act & assert:
    with fake_tango_system(DishLeafNode) as tango_context:
        tango_context.device.activityMessage = const.STR_OK
        assert tango_context.device.activityMessage == const.STR_OK


def test_state():
    # act & assert:
    with fake_tango_system(DishLeafNode) as tango_context:
        assert tango_context.device.State() == DevState.ALARM


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


def test_admin_mode():
    # act & assert:
    with fake_tango_system(DishLeafNode) as tango_context:
        assert tango_context.device.adminMode == AdminMode.ONLINE


def test_health_state():
    # act & assert:
    with fake_tango_system(DishLeafNode) as tango_context:
        assert tango_context.device.healthState == HealthState.OK


def raise_devfailed_exception(cmd_name, callback):
    tango.Except.throw_exception("DishLeafNode_Commandfailed", "This is error message for devfailed",
                                 " ", tango.ErrSeverity.ERR)


def test_stop_track_should_command_dish_to_stop_tracking_raise_dev_failed():
    # arrange:
    dish_master1_fqdn = 'mid_d0001/elt/master'
    dut_properties = {'DishMasterFQDN': dish_master1_fqdn}

    dish1_proxy_mock = Mock()

    proxies_to_mock = {dish_master1_fqdn: dish1_proxy_mock}

    dish1_proxy_mock.command_inout_asynch.side_effect = raise_devfailed_exception

    with fake_tango_system(DishLeafNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        # act
        tango_context.device.StopTrack()

        # assert
        assert const.ERR_EXE_STOP_TRACK_CMD in tango_context.device.activityMessage


def test_scan_command_with_callback_method():
    # arrange:
    dish_master1_fqdn = 'mid_d0001/elt/master'
    dut_properties = {'DishMasterFQDN': dish_master1_fqdn}

    dish1_proxy_mock = Mock()
    dish1_proxy_mock.obsState = ObsState.READY

    proxies_to_mock = {dish_master1_fqdn: dish1_proxy_mock}

    event_subscription_map = {}

    dish1_proxy_mock.command_inout_asynch.side_effect = (
        lambda command_name, argument, callback, *args,
               **kwargs: event_subscription_map.update({command_name: callback}))

    with fake_tango_system(DishLeafNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        scan_input = "0"
        device_proxy = tango_context.device

        # act
        device_proxy.Scan(scan_input)
        dummy_event = command_callback(const.CMD_DISH_SCAN)
        event_subscription_map[const.CMD_DISH_SCAN](dummy_event)

        # assert:
        assert const.STR_INVOKE_SUCCESS in tango_context.device.activityMessage


def test_scan_command_with_callback_method_with_event_error():
    # arrange:
    dish_master1_fqdn = 'mid_d0001/elt/master'
    dut_properties = {'DishMasterFQDN': dish_master1_fqdn}

    dish1_proxy_mock = Mock()
    dish1_proxy_mock.obsState = ObsState.READY

    proxies_to_mock = {dish_master1_fqdn: dish1_proxy_mock}

    event_subscription_map = {}

    dish1_proxy_mock.command_inout_asynch.side_effect = (
        lambda command_name, argument, callback, *args,
               **kwargs: event_subscription_map.update({command_name: callback}))

    with fake_tango_system(DishLeafNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        scan_input = "0"
        device_proxy = tango_context.device

        # act
        device_proxy.Scan(scan_input)
        dummy_event = command_callback_with_event_error(const.CMD_DISH_SCAN)
        event_subscription_map[const.CMD_DISH_SCAN](dummy_event)

        # assert:
        assert const.ERR_INVOKING_CMD in tango_context.device.activityMessage


def test_scan_command_with_callback_method_with_command_error():
    # arrange:
    dish_master1_fqdn = 'mid_d0001/elt/master'
    dut_properties = {'DishMasterFQDN': dish_master1_fqdn}

    dish1_proxy_mock = Mock()
    dish1_proxy_mock.obsState = ObsState.READY

    proxies_to_mock = {dish_master1_fqdn: dish1_proxy_mock}

    event_subscription_map = {}

    dish1_proxy_mock.command_inout_asynch.side_effect = (
        lambda command_name, argument, callback, *args,
               **kwargs: event_subscription_map.update({command_name: callback}))

    with fake_tango_system(DishLeafNode, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        scan_input = "0"
        device_proxy = tango_context.device

        # act
        with pytest.raises(Exception):
            device_proxy.Scan(scan_input)
            dummy_event = command_callback_with_command_exception(const.CMD_DISH_SCAN)
            event_subscription_map[const.CMD_DISH_SCAN](dummy_event)

        # assert:
        assert const.ERR_EXCEPT_CMD_CB in tango_context.device.activityMessage


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
