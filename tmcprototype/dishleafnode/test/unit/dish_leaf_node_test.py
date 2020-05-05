# Standard Python imports
import contextlib
import importlib
import types
import sys
import mock
from mock import Mock
import tango
import pytest

# Tango imports
from tango import DevState
from tango.test_context import DeviceTestContext

# Additional import
from dishleafnode import DishLeafNode, const
from ska.base.control_model import HealthState, AdminMode, TestMode, SimulationMode, ControlMode
from ska.base.control_model import LoggingLevel


def test_start_scan_should_command_dish_to_start_scan_when_it_is_ready():
    # arrange:
    device_under_test = DishLeafNode
    dish_master1_fqdn = 'mid_d0001/elt/master'
    dut_properties = {
        'DishMasterFQDN': dish_master1_fqdn
    }

    dish1_proxy_mock = Mock()
    dish1_proxy_mock.obsState = ObsState.READY

    proxies_to_mock = {
        dish_master1_fqdn: dish1_proxy_mock
    }

    with fake_tango_system(device_under_test, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        scan_input = "0"
        # act:
        tango_context.device.Scan(scan_input)

        # assert:
        if type(float(scan_input)) == float:
            dish1_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_DISH_SCAN, scan_input,
                                                                    any_method(with_name='commandCallback'))


#to do: actual AZ and EL values need to be generated.
'''
def test_configure_to_send_correct_configuration_data_when_dish_is_idle():
    # arrange:
    device_under_test = DishLeafNode
    dish_master1_fqdn = 'mid_d0001/elt/master'
    dut_properties = {
        'DishMasterFQDN': dish_master1_fqdn
    }

    dish1_proxy_mock = Mock()
    dish1_proxy_mock.obsState = ObsState.IDLE
    proxies_to_mock = {
        dish_master1_fqdn: dish1_proxy_mock
    }

    with fake_tango_system(device_under_test, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        dish_config = '{"pointing":{"target":{"system":"ICRS","name":"NGC6251","RA":"2:31:50.91",
                        "dec":"89:15:51.4"}},
        "dish":{"receiverBand":"1"}}'
        # act:
        tango_context.device.Configure(dish_config)

        # assert:
        jsonArgument = json.loads(dish_config)
        #ra_value = (jsonArgument["pointing"]["target"]["RA"])
        #dec_value = (jsonArgument["pointing"]["target"]["dec"])
        receiver_band = int(jsonArgument["dish"]["receiverBand"])

        arg_list = {"pointing": {
            "AZ": 0.3049571750805346,
            "EL": 19.113236909834765

        },
            "dish": {
                "receiverBand": receiver_band
            }

        }
        dish_str_ip = json.dumps(arg_list)

        dish1_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_DISH_CONFIGURE,
                                                                str(dish_str_ip),
                                                                any_method(with_name='commandCallback'))
'''


def test_end_scan_should_command_dish_to_end_scan_when_it_is_scanning():
    # arrange:
    device_under_test = DishLeafNode
    dish_master1_fqdn = 'mid_d0001/elt/master'
    dut_properties = {
        'DishMasterFQDN': dish_master1_fqdn
    }

    dish1_proxy_mock = Mock()
    dish1_proxy_mock.obsState = ObsState.SCANNING
    proxies_to_mock = {
        dish_master1_fqdn: dish1_proxy_mock
    }

    with fake_tango_system(device_under_test, initial_dut_properties=dut_properties,
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
    device_under_test = DishLeafNode
    dish_master1_fqdn = 'mid_d0001/elt/master'
    dut_properties = {
        'DishMasterFQDN': dish_master1_fqdn
    }

    dish1_proxy_mock = Mock()

    proxies_to_mock = {
        dish_master1_fqdn: dish1_proxy_mock
    }

    with fake_tango_system(device_under_test, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:

        # act:
        tango_context.device.SetStandByLPMode()

        # assert:
        dish1_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_SET_STANDBYLP_MODE,
                                                                any_method(with_name='commandCallback'))


def test_set_operate_mode_should_command_dish_to_start():
    # arrange:
    device_under_test = DishLeafNode
    dish_master1_fqdn = 'mid_d0001/elt/master'
    dut_properties = {
        'DishMasterFQDN': dish_master1_fqdn
    }

    dish1_proxy_mock = Mock()

    proxies_to_mock = {
        dish_master1_fqdn: dish1_proxy_mock
    }

    with fake_tango_system(device_under_test, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        # act:
        tango_context.device.SetOperateMode()

        # assert:
        dish1_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_SET_OPERATE_MODE,
                                                                any_method(with_name='commandCallback'))


'''
def test_track_should_command_dish_to_start_tracking():
    # arrange:
    device_under_test = DishLeafNode
    dish_master1_fqdn = 'mid_d0001/elt/master'
    dut_properties = {
        'DishMasterFQDN': dish_master1_fqdn
    }

    dish1_proxy_mock = Mock()
    
    proxies_to_mock = {
        dish_master1_fqdn: dish1_proxy_mock
    }

    with fake_tango_system(device_under_test, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        input_string = '{"pointing":{"target":{"system":"ICRS","name":"NGC6251","RA":"2:31:50.91",
                        "dec":"89:15:51.4"}},
        "dish":{"receiverBand":"1"}}'

        # act:
        tango_context.device.Track(input_string)

        # assert:
        jsonArgument = json.loads(input_string)
        ra_value = (jsonArgument["pointing"]["target"]["RA"])
        dec_value = (jsonArgument["pointing"]["target"]["dec"])
        radec_value = 'radec' + ',' + str(ra_value) + ',' + str(dec_value)
        dish1_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_TRACK, "0", 
                                                                any_method(with_name='commandCallback'))
'''


def test_stop_track_should_command_dish_to_stop_tracking():
    # arrange:
    device_under_test = DishLeafNode
    dish_master1_fqdn = 'mid_d0001/elt/master'
    dut_properties = {
        'DishMasterFQDN': dish_master1_fqdn
    }

    dish1_proxy_mock = Mock()

    proxies_to_mock = {
        dish_master1_fqdn: dish1_proxy_mock
    }

    with fake_tango_system(device_under_test, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        # act:
        tango_context.device.StopTrack()

        # assert:
        dish1_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_STOP_TRACK,
                                                                any_method(with_name='commandCallback'))


def test_slew_should_command_the_dish_to_slew_towards_the_set_pointing_coordinates():
    device_under_test = DishLeafNode
    dish_master1_fqdn = 'mid_d0001/elt/master'
    dut_properties = {
        'DishMasterFQDN': dish_master1_fqdn
    }

    dish1_proxy_mock = Mock()

    proxies_to_mock = {
        dish_master1_fqdn: dish1_proxy_mock
    }

    with fake_tango_system(device_under_test, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        slew_arg = "0"
        # act:
        tango_context.device.Slew(slew_arg)

        # assert:
        if type(float(slew_arg)) == float:
            dish1_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_DISH_SLEW, slew_arg,
                                                                    any_method(with_name='commandCallback'))


def test_start_capture_should_command_dish_to_start_capture_on_the_set_configured_band():
    device_under_test = DishLeafNode
    dish_master1_fqdn = 'mid_d0001/elt/master'
    dut_properties = {
        'DishMasterFQDN': dish_master1_fqdn
    }

    dish1_proxy_mock = Mock()

    proxies_to_mock = {
        dish_master1_fqdn: dish1_proxy_mock
    }

    with fake_tango_system(device_under_test, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        capture_arg = "0"
        # act:
        tango_context.device.StartCapture(capture_arg)

        # assert:
        if type(float(capture_arg)) == float:
            dish1_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_START_CAPTURE, capture_arg,
                                                                    any_method(with_name='commandCallback'))


def test_stop_capture_should_command_dish_to_stop_capture_on_the_set_configured_band():
    device_under_test = DishLeafNode
    dish_master1_fqdn = 'mid_d0001/elt/master'
    dut_properties = {
        'DishMasterFQDN': dish_master1_fqdn
    }

    dish1_proxy_mock = Mock()

    proxies_to_mock = {
        dish_master1_fqdn: dish1_proxy_mock
    }

    with fake_tango_system(device_under_test, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        capture_arg = "0"
        # act:
        tango_context.device.StopCapture(capture_arg)

        # assert:
        if type(float(capture_arg)) == float:
            dish1_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_STOP_CAPTURE, capture_arg,
                                                                    any_method(with_name='commandCallback'))


def create_dummy_event_for_dishmode(device_fqdn,dish_mode_value,attribute):
    fake_event = Mock()
    fake_event.err = False
    fake_event.attr_name = f"{device_fqdn}/{attribute}"
    fake_event.attr_value.value = dish_mode_value
    return fake_event


def test_dish_leaf_node_dish_mode_is_off_when_dish_is_off():
    # arrange:
    device_under_test = DishLeafNode
    dish_master1_fqdn = 'mid_d0001/elt/master'
    dish_master_dishmode_attribute = 'dishMode'
    initial_dut_properties = {
        'DishMasterFQDN': dish_master1_fqdn
    }

    event_subscription_map = {}

    dish_master_device_proxy_mock = Mock()
    dish_master_device_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args,
               **kwargs: event_subscription_map.update({attr_name: callback}))

    proxies_to_mock = {
        dish_master1_fqdn: dish_master_device_proxy_mock
    }

    with fake_tango_system(device_under_test, initial_dut_properties, proxies_to_mock) as tango_context:
        # act:
        dish_mode_value = 0
        dummy_event = create_dummy_event_for_dishmode(dish_master1_fqdn, dish_mode_value,
                                                         dish_master_dishmode_attribute)
        event_subscription_map[dish_master_dishmode_attribute](dummy_event)

        # assert:
        assert tango_context.device.activityMessage == const.STR_DISH_OFF_MODE


def test_dish_leaf_node_dish_mode_is_startup_when_dish_is_startup():
    # arrange:
    device_under_test = DishLeafNode
    dish_master1_fqdn = 'mid_d0001/elt/master'
    dish_master_dishmode_attribute = 'dishMode'
    initial_dut_properties = {
        'DishMasterFQDN': dish_master1_fqdn
    }
    event_subscription_map = {}
    dish_master_device_proxy_mock = Mock()
    dish_master_device_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args,
               **kwargs: event_subscription_map.update({attr_name: callback}))

    proxies_to_mock = {
        dish_master1_fqdn: dish_master_device_proxy_mock
    }

    with fake_tango_system(device_under_test, initial_dut_properties, proxies_to_mock) as tango_context:
        # act:
        dish_mode_value = 1
        dummy_event = create_dummy_event_for_dishmode(dish_master1_fqdn, dish_mode_value,
                                                         dish_master_dishmode_attribute)
        event_subscription_map[dish_master_dishmode_attribute](dummy_event)

        # assert:
        assert tango_context.device.activityMessage == const.STR_DISH_STARTUP_MODE


def test_dish_leaf_node_dish_mode_is_shutdown_when_dish_is_shutdown():
    # arrange:
    device_under_test = DishLeafNode
    dish_master1_fqdn = 'mid_d0001/elt/master'
    dish_master_dishmode_attribute = 'dishMode'
    initial_dut_properties = {
        'DishMasterFQDN': dish_master1_fqdn
    }

    event_subscription_map = {}
    dish_master_device_proxy_mock = Mock()
    dish_master_device_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args,
               **kwargs: event_subscription_map.update({attr_name: callback}))

    proxies_to_mock = {
        dish_master1_fqdn: dish_master_device_proxy_mock
    }

    with fake_tango_system(device_under_test, initial_dut_properties, proxies_to_mock) as tango_context:
        # act:
        dish_mode_value = 2
        dummy_event = create_dummy_event_for_dishmode(dish_master1_fqdn, dish_mode_value,
                                                         dish_master_dishmode_attribute)
        event_subscription_map[dish_master_dishmode_attribute](dummy_event)

        # assert:
        assert tango_context.device.activityMessage == const.STR_DISH_SHUTDOWN_MODE


def test_dish_leaf_node_dish_mode_is_standby_when_dish_is_standby():
    # arrange:
    device_under_test = DishLeafNode
    dish_master1_fqdn = 'mid_d0001/elt/master'
    dish_master_dishmode_attribute = 'dishMode'
    initial_dut_properties = {
        'DishMasterFQDN': dish_master1_fqdn
    }

    event_subscription_map = {}

    dish_master_device_proxy_mock = Mock()
    dish_master_device_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args,
               **kwargs: event_subscription_map.update({attr_name: callback}))

    proxies_to_mock = {
        dish_master1_fqdn: dish_master_device_proxy_mock
    }

    with fake_tango_system(device_under_test, initial_dut_properties, proxies_to_mock) as tango_context:
        # act:
        dish_mode_value = 3
        dummy_event = create_dummy_event_for_dishmode(dish_master1_fqdn, dish_mode_value,
                                                         dish_master_dishmode_attribute)
        event_subscription_map[dish_master_dishmode_attribute](dummy_event)

        # assert:
        assert tango_context.device.activityMessage == const.STR_DISH_STANDBYLP_MODE


def test_dish_leaf_node_dish_mode_is_standbyfp_when_dish_is_standbyfp():
    # arrange:
    device_under_test = DishLeafNode
    dish_master1_fqdn = 'mid_d0001/elt/master'
    dish_master_dishmode_attribute = 'dishMode'
    initial_dut_properties = {
        'DishMasterFQDN': dish_master1_fqdn
    }

    event_subscription_map = {}

    dish_master_device_proxy_mock = Mock()
    dish_master_device_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args,
               **kwargs: event_subscription_map.update({attr_name: callback}))

    proxies_to_mock = {
        dish_master1_fqdn: dish_master_device_proxy_mock
    }

    with fake_tango_system(device_under_test, initial_dut_properties, proxies_to_mock) as tango_context:
        # act:
        dish_mode_value = 4
        dummy_event = create_dummy_event_for_dishmode(dish_master1_fqdn, dish_mode_value,
                                                         dish_master_dishmode_attribute)
        event_subscription_map[dish_master_dishmode_attribute](dummy_event)

        # assert:
        assert tango_context.device.activityMessage == const.STR_DISH_STANDBYFP_MODE


def test_dish_leaf_node_dish_mode_is_maint_when_dish_is_maint():
    # arrange:
    device_under_test = DishLeafNode
    dish_master1_fqdn = 'mid_d0001/elt/master'
    dish_master_dishmode_attribute = 'dishMode'
    initial_dut_properties = {
        'DishMasterFQDN': dish_master1_fqdn
    }

    event_subscription_map = {}

    dish_master_device_proxy_mock = Mock()
    dish_master_device_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args,
               **kwargs: event_subscription_map.update({attr_name: callback}))

    proxies_to_mock = {
        dish_master1_fqdn: dish_master_device_proxy_mock
    }

    with fake_tango_system(device_under_test, initial_dut_properties, proxies_to_mock) as tango_context:
        # act:
        dish_mode_value = 5
        dummy_event = create_dummy_event_for_dishmode(dish_master1_fqdn, dish_mode_value,
                                                         dish_master_dishmode_attribute)
        event_subscription_map[dish_master_dishmode_attribute](dummy_event)

        # assert:
        assert tango_context.device.activityMessage == const.STR_DISH_MAINT_MODE


def test_dish_leaf_node_dish_mode_is_stow_when_dish_is_stow():
    # arrange:
    device_under_test = DishLeafNode
    dish_master1_fqdn = 'mid_d0001/elt/master'
    dish_master_dishmode_attribute = 'dishMode'
    initial_dut_properties = {
        'DishMasterFQDN': dish_master1_fqdn
    }

    event_subscription_map = {}

    dish_master_device_proxy_mock = Mock()
    dish_master_device_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args,
               **kwargs: event_subscription_map.update({attr_name: callback}))

    proxies_to_mock = {
        dish_master1_fqdn: dish_master_device_proxy_mock
    }

    with fake_tango_system(device_under_test, initial_dut_properties, proxies_to_mock) as tango_context:
        # act:
        dish_mode_value = 6
        dummy_event = create_dummy_event_for_dishmode(dish_master1_fqdn, dish_mode_value,
                                                         dish_master_dishmode_attribute)
        event_subscription_map[dish_master_dishmode_attribute](dummy_event)

        # assert:
        assert tango_context.device.activityMessage == const.STR_DISH_STOW_MODE


def test_dish_leaf_node_dish_mode_is_config_when_dish_is_config():
    # arrange:
    device_under_test = DishLeafNode
    dish_master1_fqdn = 'mid_d0001/elt/master'
    dish_master_dishmode_attribute = 'dishMode'
    initial_dut_properties = {
        'DishMasterFQDN': dish_master1_fqdn
    }

    event_subscription_map = {}

    dish_master_device_proxy_mock = Mock()
    dish_master_device_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args,
               **kwargs: event_subscription_map.update({attr_name: callback}))

    proxies_to_mock = {
        dish_master1_fqdn: dish_master_device_proxy_mock
    }

    with fake_tango_system(device_under_test, initial_dut_properties, proxies_to_mock) as tango_context:
        # act:
        dish_mode_value = 7
        dummy_event = create_dummy_event_for_dishmode(dish_master1_fqdn, dish_mode_value,
                                                         dish_master_dishmode_attribute)
        event_subscription_map[dish_master_dishmode_attribute](dummy_event)

        # assert:
        assert tango_context.device.activityMessage == const.STR_DISH_CONFIG_MODE


def test_dish_leaf_node_dish_mode_is_operate_when_dish_is_operate():
    # arrange:
    device_under_test = DishLeafNode
    dish_master1_fqdn = 'mid_d0001/elt/master'
    dish_master_dishmode_attribute = 'dishMode'
    initial_dut_properties = {
        'DishMasterFQDN': dish_master1_fqdn
    }

    event_subscription_map = {}

    dish_master_device_proxy_mock = Mock()
    dish_master_device_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args,
               **kwargs: event_subscription_map.update({attr_name: callback}))

    proxies_to_mock = {
        dish_master1_fqdn: dish_master_device_proxy_mock
    }

    with fake_tango_system(device_under_test, initial_dut_properties, proxies_to_mock) as tango_context:
        # act:
        dish_mode_value = 8
        dummy_event = create_dummy_event_for_dishmode(dish_master1_fqdn, dish_mode_value,
                                                         dish_master_dishmode_attribute)
        event_subscription_map[dish_master_dishmode_attribute](dummy_event)

        # assert:
        assert tango_context.device.activityMessage == const.STR_DISH_OPERATE_MODE


def create_dummy_event_for_dish_capturing(device_fqdn,dish_capturing_value,attribute):
    fake_event = Mock()
    fake_event.err = False
    fake_event.attr_name = f"{device_fqdn}/{attribute}"
    fake_event.attr_value.value = dish_capturing_value
    return fake_event


def test_dish_leaf_node_when_dish_capturing_callback_is_true():
    # arrange:
    device_under_test = DishLeafNode
    dish_master1_fqdn = 'mid_d0001/elt/master'
    dish_master_capturing_attribute = 'capturing'
    initial_dut_properties = {
        'DishMasterFQDN': dish_master1_fqdn
    }

    event_subscription_map = {}

    dish_master_device_proxy_mock = Mock()
    dish_master_device_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args,
               **kwargs: event_subscription_map.update({attr_name: callback}))

    proxies_to_mock = {
        dish_master1_fqdn: dish_master_device_proxy_mock
    }

    with fake_tango_system(device_under_test, initial_dut_properties, proxies_to_mock) as tango_context:
        # act:
        dish_capturing_value = True
        dummy_event = create_dummy_event_for_dish_capturing(dish_master1_fqdn, dish_capturing_value,
                                                            dish_master_capturing_attribute)
        event_subscription_map[dish_master_capturing_attribute](dummy_event)

        # assert:
        assert tango_context.device.activityMessage == const.STR_DISH_CAPTURING_TRUE


def test_dish_leaf_node_when_dish_capturing_callback_is_false():
    # arrange:
    device_under_test = DishLeafNode
    dish_master1_fqdn = 'mid_d0001/elt/master'
    dish_master_capturing_attribute = 'capturing'
    initial_dut_properties = {
        'DishMasterFQDN': dish_master1_fqdn
    }

    event_subscription_map = {}

    dish_master_device_proxy_mock = Mock()
    dish_master_device_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args,
               **kwargs: event_subscription_map.update({attr_name: callback}))

    proxies_to_mock = {
        dish_master1_fqdn: dish_master_device_proxy_mock
    }

    with fake_tango_system(device_under_test, initial_dut_properties, proxies_to_mock) as tango_context:
        # act:
        dish_capturing_value = False
        dummy_event = create_dummy_event_for_dish_capturing(dish_master1_fqdn, dish_capturing_value,
                                                            dish_master_capturing_attribute)
        event_subscription_map[dish_master_capturing_attribute](dummy_event)

        # assert:
        assert tango_context.device.activityMessage == const.STR_DISH_CAPTURING_FALSE


def create_dummy_event(device_fqdn, attribute, attr_value):
    fake_event = Mock()
    fake_event.err = False
    fake_event.attr_name = f"{device_fqdn}/{attribute}"
    fake_event.attr_value.value = attr_value
    return fake_event


def test_dish_leaf_node_when_acheived_pointing_callback_is_true():
    # arrange:
    device_under_test = DishLeafNode
    dish_master1_fqdn = 'mid_d0001/elt/master'
    dish_master_achievedPointing_attribute = 'achievedPointing'
    initial_dut_properties = {
        'DishMasterFQDN': dish_master1_fqdn
    }

    event_subscription_map = {}

    dish_master_device_proxy_mock = Mock()
    dish_master_device_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args,
               **kwargs: event_subscription_map.update({attr_name: callback}))

    proxies_to_mock = {
        dish_master1_fqdn: dish_master_device_proxy_mock
    }

    with fake_tango_system(device_under_test, initial_dut_properties, proxies_to_mock) as tango_context:
        # act:
        attribute = 'achievedPointing'
        value = 0.0
        dummy_event = create_dummy_event(dish_master1_fqdn, attribute, value)
        event_subscription_map[dish_master_achievedPointing_attribute](dummy_event)

        # assert:
        assert tango_context.device.activityMessage == const.STR_ACHIEVED_POINTING + \
               str(dummy_event.attr_value.value)


def test_dish_leaf_node_when_desired_pointing_callback_is_true():
    # arrange:
    device_under_test = DishLeafNode
    dish_master1_fqdn = 'mid_d0001/elt/master'
    dish_master_desiredPointing_attribute = 'desiredPointing'
    initial_dut_properties = {
        'DishMasterFQDN': dish_master1_fqdn
    }

    event_subscription_map = {}

    dish_master_device_proxy_mock = Mock()
    dish_master_device_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args,
               **kwargs: event_subscription_map.update({attr_name: callback}))

    proxies_to_mock = {
        dish_master1_fqdn: dish_master_device_proxy_mock
    }

    with fake_tango_system(device_under_test, initial_dut_properties, proxies_to_mock) as tango_context:
        # act:
        attribute = 'desiredPointing'
        value = 0.0
        dummy_event = create_dummy_event(dish_master1_fqdn, attribute, value)
        event_subscription_map[dish_master_desiredPointing_attribute](dummy_event)

        # assert:
        assert tango_context.device.activityMessage == const.STR_DESIRED_POINTING +\
               str(dummy_event.attr_value.value)


def test_configure_should_raise_exception_when_called_with_invalid_json():
    # arrange:
    device_under_test = DishLeafNode
    # act
    with fake_tango_system(device_under_test) as tango_context:
        input_string = '{"Invalid Key"}'
        with pytest.raises(tango.DevFailed):
            tango_context.device.Configure(input_string)

        # assert:
        assert const.ERR_INVALID_JSON in tango_context.device.activityMessage


def test_configure_should_raise_exception_when_called_with_invalid_arguments():
    # arrange:
    device_under_test = DishLeafNode
    # act
    with fake_tango_system(device_under_test) as tango_context:
        input_string = []
        input_string.append(
            '{"pointing":{"target":{"system":"ICRS","name":"NGC6251","":"2:31:50.91","":"89:15:51.4"}},\
            "dish":{"receiverBand":"1"}}')
        with pytest.raises(tango.DevFailed):
            tango_context.device.Configure(input_string[0])

        # assert:
        assert  const.ERR_JSON_KEY_NOT_FOUND in tango_context.device.activityMessage


def test_configure_should_raise_generic_exception():
    # arrange:
    device_under_test = DishLeafNode
    # act
    with fake_tango_system(device_under_test) as tango_context:
        Configure_input = '[123]'
        with pytest.raises(tango.DevFailed):
            tango_context.device.Configure(Configure_input)

        # assert:
        assert const.ERR_EXE_CONFIGURE_CMD in tango_context.device.activityMessage


def test_scan_should_raise_exception_when_called_with_invalid_arguments():
    # arrange:
    device_under_test = DishLeafNode
    # act
    with fake_tango_system(device_under_test) as tango_context:
        input_string = "a"
        with pytest.raises(tango.DevFailed):
            tango_context.device.Scan(input_string)

        # assert:
        assert const.ERR_EXE_SCAN_CMD in tango_context.device.activityMessage


def test_endscan_should_raise_exception_when_called_with_invalid_arguments():
    # arrange:
    device_under_test = DishLeafNode
    # act
    with fake_tango_system(device_under_test) as tango_context:
        input_string = "a"
        with pytest.raises(tango.DevFailed):
            tango_context.device.EndScan(input_string)

        # assert:
        assert const.ERR_EXE_END_SCAN_CMD in tango_context.device.activityMessage


def test_startcapture_should_raise_exception_when_called_with_invalid_arguments():
    # arrange:
    device_under_test = DishLeafNode
    # act
    with fake_tango_system(device_under_test) as tango_context:
        input_string = "a"
        with pytest.raises(tango.DevFailed):
            tango_context.device.StartCapture(input_string)

        # assert:
        assert const.ERR_EXE_START_CAPTURE_CMD in tango_context.device.activityMessage


def test_stopstartcapture_should_raise_exception_when_called_with_invalid_arguments():
    # arrange:
    device_under_test = DishLeafNode
    # act
    with fake_tango_system(device_under_test) as tango_context:
        input_string = "a"
        with pytest.raises(tango.DevFailed):
            tango_context.device.StopCapture(input_string)

        # assert:
        assert const.ERR_EXE_STOP_CAPTURE_CMD in tango_context.device.activityMessage


def test_slew_should_raise_exception_when_called_with_invalid_arguments():
    # arrange:
    device_under_test = DishLeafNode
    # act
    with fake_tango_system(device_under_test) as tango_context:
        input_string = "a"
        with pytest.raises(tango.DevFailed):
            tango_context.device.Slew(input_string)

        # assert:
        assert const.ERR_EXE_SLEW_CMD in tango_context.device.activityMessage


def test_track_should_raise_exception_when_called_with_invalid_arguments():
    # arrange:
    device_under_test = DishLeafNode
    # act
    with fake_tango_system(device_under_test) as tango_context:
        input_string =\
            '{"pointing":{"target":{"system":"ICRS","name":"NGC6251","":"2:31:50.91","":"89:15:51.4"}},' \
            '"dish":{"receiverBand":"1"}}'

        with pytest.raises(tango.DevFailed):
            tango_context.device.Track(input_string)

        # assert:
        assert const.ERR_JSON_KEY_NOT_FOUND in tango_context.device.activityMessage
        tango_context.device.SetStandByLPMode()


def test_track_should_raise_exception_when_called_with_invalid_json():
    # arrange:
    device_under_test = DishLeafNode
    # act
    with fake_tango_system(device_under_test) as tango_context:
        input_string = '{"Invalid Key"}'

        with pytest.raises(tango.DevFailed):
            tango_context.device.Track(input_string)

        # assert:
        assert const.ERR_INVALID_JSON in tango_context.device.activityMessage


def test_activity_message():
    # arrange
    device_under_test = DishLeafNode
    # act & assert:
    with fake_tango_system(device_under_test) as tango_context:
        tango_context.device.activityMessage = const.STR_OK
        assert tango_context.device.activityMessage == const.STR_OK


def test_state():
    # arrange
    device_under_test = DishLeafNode
    # act & assert:
    with fake_tango_system(device_under_test) as tango_context:
        assert tango_context.device.State() == DevState.ALARM


def test_status():
    # arrange
    device_under_test = DishLeafNode
    # act & assert:
    with fake_tango_system(device_under_test) as tango_context:
        assert tango_context.device.Status() != const.STR_DISH_INIT_SUCCESS


def test_logging_level():
    # arrange
    device_under_test = DishLeafNode
    # act & assert:
    with fake_tango_system(device_under_test) as tango_context:
        tango_context.device.loggingLevel = LoggingLevel.INFO
        assert tango_context.device.loggingLevel == LoggingLevel.INFO


def test_logging_targets():
    # arrange
    device_under_test = DishLeafNode
    # act & assert:
    with fake_tango_system(device_under_test) as tango_context:
        tango_context.device.loggingTargets = ['console::cout']
        assert 'console::cout' in tango_context.device.loggingTargets


def test_test_mode():
    # arrange
    device_under_test = DishLeafNode
    # act & assert:
    with fake_tango_system(device_under_test) as tango_context:
        test_mode = TestMode.NONE
        tango_context.device.testMode = test_mode
        assert tango_context.device.testMode == test_mode


def test_simulation_mode():
    # arrange
    device_under_test = DishLeafNode
    # act & assert:
    with fake_tango_system(device_under_test) as tango_context:
        simulation_mode = SimulationMode.FALSE
        tango_context.device.simulationMode = simulation_mode
        assert tango_context.device.simulationMode == simulation_mode


def test_control_mode():
    # arrange
    device_under_test = DishLeafNode
    # act & assert:
    with fake_tango_system(device_under_test) as tango_context:
        control_mode = ControlMode.REMOTE
        tango_context.device.controlMode = control_mode
        assert tango_context.device.controlMode == control_mode


def test_admin_mode():
    # arrange
    device_under_test = DishLeafNode
    # act & assert:
    with fake_tango_system(device_under_test) as tango_context:
        assert tango_context.device.adminMode == AdminMode.ONLINE


def test_health_state():
    # arrange
    device_under_test = DishLeafNode
    # act & assert:
    with fake_tango_system(device_under_test) as tango_context:
        assert tango_context.device.healthState == HealthState.OK


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
