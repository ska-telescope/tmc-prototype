import contextlib
import importlib
import sys
import json
import mock
import types

from mock import Mock
from sdpsubarrayleafnode import SdpSubarrayLeafNode, const
from tango.test_context import DeviceTestContext
from ska.base.control_model import ObsState


def test_start_scan_should_command_dish_master_to_start_scan_when_it_is_ready():
    # arrange:
    device_under_test = DishMaster
    dish_master_fqdn = 'mid_d0001/elt/master'
    dut_properties = {
        'DishMasterFQDN': dish_master_fqdn
    }

    dish_master_proxy_mock = Mock()
    dish_master_proxy_mock.obsState = ObsState.READY

    proxies_to_mock = {
        dish_master_fqdn: dish_master_proxy_mock
    }

    with fake_tango_system(device_under_test, initial_dut_properties=dut_properties, proxies_to_mock=proxies_to_mock) as tango_context:
        scan_config = '0'
        # act:
        tango_context.device.Scan(scan_config)

        # assert:
        dish_master_proxy_mock.command_inout_asynch.assert_called_with(const.STR_SCAN_INPROG, float(scan_config), any_method(with_name='commandCallback'))

def test_configure_to_send_correct_configuration_data_when_dish_master_is_idle():
    # arrange:
    device_under_test = DishMaster
    dish_master_fqdn = 'mid_d0001/elt/master'
    dut_properties = {
        'DishMasterFQDN': dish_master_fqdn
    }

    dish_master_proxy_mock = Mock()
    dish_master_proxy_mock.obsState = ObsState.IDLE

    proxies_to_mock = {
        dish_master_fqdn: dish_master_proxy_mock
    }

    with fake_tango_system(device_under_test, initial_dut_properties=dut_properties, proxies_to_mock=proxies_to_mock) \
            as tango_context:
        dm_config = '{"pointing":{"AZ": 1.0,"EL": 1.0},"dish":{"receiverBand":"1"}}'
        # act:
        tango_context.device.Configure(dm_config)

        # assert:
        json_argument = json.loads(dm_config)
        dm_arg = json_argument["pointing"]
        dm_configuration = dm_arg.copy()
        if "configureScan" in dm_configuration:
            del dm_configuration["configureScan"]
        dish_master_proxy_mock.command_inout_asynch.assert_called_with(const.STR_CONFIG_SUCCESS,
                                                                        json.dumps(dm_configuration),
                                                                        any_method(with_name='commandCallback'))

def test_standby_lp_mode_should_command_dish_master_to_standby():
    # arrange:
    device_under_test = DishMaster
    dish_master_fqdn = 'mid_d0001/elt/master'
    dut_properties = {
        'DishMasterFQDN': dish_master_fqdn
    }

    dish_master_proxy_mock = Mock()
    #dish_master_proxy_mock.obsState = ObsState.DISABLE
    proxies_to_mock = {
        dish_master_fqdn: dish_master_proxy_mock
    }

    with fake_tango_system(device_under_test, initial_dut_properties=dut_properties, proxies_to_mock=proxies_to_mock) \
            as tango_context:

        # act:
        tango_context.device.SetStandByLPMode()

        # assert:
        dish_master_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_SET_STANDBYLP_MODE,
                                                                        any_method(with_name='commandCallback'))


def test_set_operate_mode_should_command_dish_master_to_start():
    # arrange:
    device_under_test = DishMaster
    dish_master_fqdn = 'mid_d0001/elt/master'
    dut_properties = {
        'DishMasterFQDN': dish_master_fqdn
    }

    dish_master_proxy_mock = Mock()
    dish_master_proxy_mock.obsState = ObsState.ON  # referred from devstate of dishmaster setoperate
    proxies_to_mock = {
        dish_master_fqdn: dish_master_proxy_mock
    }

    with fake_tango_system(device_under_test, initial_dut_properties=dut_properties, proxies_to_mock=proxies_to_mock) \
            as tango_context:
        # act:
        tango_context.device.SetOperateMode()

        # assert:
        dish_master_proxy_mock.command_inout_asynch.assert_called_with(const.STR_DISH_OPERATE_MODE,
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
