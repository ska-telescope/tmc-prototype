import contextlib
import importlib
import sys
import json
import mock
import types

from mock import Mock
from dishleafnode import DishLeafNode, const
from tango.test_context import DeviceTestContext
from ska.base.control_model import ObsState


def test_start_scan_should_command_dish_to_start_scan_when_it_is_ready():
    # arrange:
    device_under_test = DishLeafNode
    dish_master_fqdn = 'mid_d0001/elt/master'
    dut_properties = {
        'DishMasterFQDN': dish_master_fqdn
    }

    dish_proxy_mock = Mock()
    dish_proxy_mock.obsState = ObsState.READY

    proxies_to_mock = {
        dish_master_fqdn: dish_proxy_mock
    }

    with fake_tango_system(device_under_test, initial_dut_properties=dut_properties, proxies_to_mock=proxies_to_mock) as tango_context:
        scan_config = "0"
        # act:
        tango_context.device.Scan(scan_config)

        # assert:
        if type(float(scan_config)) == float:
            dish_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_DISH_SCAN, scan_config, any_method(with_name='commandCallback'))


def test_configure_to_send_correct_configuration_data_when_dish_is_idle():
    # arrange:
    device_under_test = DishLeafNode
    dish_master_fqdn = 'mid_d0001/elt/master'
    dut_properties = {
        'DishMasterFQDN': dish_master_fqdn
    }

    dish_proxy_mock = Mock()
    dish_proxy_mock.obsState = ObsState.IDLE
    proxies_to_mock = {
        dish_master_fqdn: dish_proxy_mock
    }

    with fake_tango_system(device_under_test, initial_dut_properties=dut_properties, proxies_to_mock=proxies_to_mock) \
            as tango_context:
        dish_config = '{"pointing":{"target":{"system":"ICRS","name":"NGC6251","RA":"2:31:50.91","dec":"89:15:51.4"}},"dish":{"receiverBand":"1"}}'
        # act:
        tango_context.device.Configure(dish_config)

        # assert:
        jsonArgument = json.loads(dish_config)
        #ra_value = (jsonArgument["pointing"]["target"]["RA"])
        #dec_value = (jsonArgument["pointing"]["target"]["dec"])
        receiver_band = int(jsonArgument["dish"]["receiverBand"])

        arg_list = {"pointing": {
            "AZ": 0.0,
            "EL": 0.0

        },
            "dish": {
                "receiverBand": receiver_band
            }

        }
        dish_str_ip = json.dumps(arg_list)

        dish_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_DISH_CONFIGURE,
                                                                        str(dish_str_ip),
                                                                        any_method(with_name='commandCallback'))


def test_end_scan_should_command_dish_to_end_scan_when_it_is_scanning():
    # arrange:
    device_under_test = DishLeafNode
    dish_master_fqdn = 'mid_d0001/elt/master'
    dut_properties = {
        'DishMasterFQDN': dish_master_fqdn
    }

    dish_proxy_mock = Mock()
    dish_proxy_mock.obsState = ObsState.SCANNING
    proxies_to_mock = {
        dish_master_fqdn: dish_proxy_mock
    }

    with fake_tango_system(device_under_test, initial_dut_properties=dut_properties, proxies_to_mock=proxies_to_mock) \
            as tango_context:
        scan_config = 0.0
        # act:
        tango_context.device.EndScan(0.0)

        # assert:
        dish_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_STOP_CAPTURE,0.0,
                                                                        any_method(with_name='commandCallback'))


def test_standby_lp_mode_should_command_dish_to_standby():
    # arrange:
    device_under_test = DishLeafNode
    dish_master_fqdn = 'mid_d0001/elt/master'
    dut_properties = {
        'DishMasterFQDN': dish_master_fqdn
    }

    dish_proxy_mock = Mock()
    dish_proxy_mock.obsState = ObsState.DISABLE
    proxies_to_mock = {
        dish_master_fqdn: dish_proxy_mock
    }

    with fake_tango_system(device_under_test, initial_dut_properties=dut_properties, proxies_to_mock=proxies_to_mock) \
            as tango_context:

        # act:
        tango_context.device.SetStandByLPMode()

        # assert:
        dish_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_SET_STANDBYLP_MODE,
                                                                        any_method(with_name='commandCallback'))


def test_set_operate_mode_should_command_dish_to_start():
    # arrange:
    device_under_test = DishLeafNode
    dish_master_fqdn = 'mid_d0001/elt/master'
    dut_properties = {
        'DishMasterFQDN': dish_master_fqdn
    }

    dish_proxy_mock = Mock()
    dish_proxy_mock.obsState = ObsState.ON  # referred from devstate of dishmaster setoperate
    proxies_to_mock = {
        dish_master_fqdn: dish_proxy_mock
    }

    with fake_tango_system(device_under_test, initial_dut_properties=dut_properties, proxies_to_mock=proxies_to_mock) \
            as tango_context:
        # act:
        tango_context.device.SetOperateMode()

        # assert:
        dish_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_SET_OPERATE_MODE,
                                                                any_method(with_name='commandCallback'))




def any_method(with_name=None):
    class AnyMethod():
        def __eq__(self, other):
            if not isinstance(other, types.MethodType):
                return False

            return other.__func__.__name__ == with_name if with_name else True

    return AnyMethod()


@contextlib.contextmanager
def fake_tango_system(device_under_test, initial_dut_properties={}, proxies_to_mock={}, device_proxy_import_path='tango.DeviceProxy'):

    with mock.patch(device_proxy_import_path) as patched_constructor:
        patched_constructor.side_effect = lambda device_fqdn: proxies_to_mock.get(device_fqdn, Mock())
        patched_module = importlib.reload(sys.modules[device_under_test.__module__])

    device_under_test = getattr(patched_module, device_under_test.__name__)

    device_test_context = DeviceTestContext(device_under_test, properties=initial_dut_properties)
    device_test_context.start()
    yield device_test_context
    device_test_context.stop()
