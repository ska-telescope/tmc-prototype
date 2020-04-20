import contextlib
import importlib
import sys
import json
import mock
import types
import tango
from tango import DevState

from mock import Mock
from subarraynode import SubarrayNode, const
from tango.test_context import DeviceTestContext
from ska.base.control_model import ObsState

def test_On_should_command_subarray_to_On():
    # arrange:
    device_under_test = SubarrayNode
    dut_properties = {
    }
    proxies_to_mock = {
    }

    with fake_tango_system(device_under_test, initial_dut_properties=dut_properties, proxies_to_mock=proxies_to_mock) \
            as tango_context:
        # act:
        tango_context.device.On()
        # assert:
        assert tango_context.device.state() == DevState.OFF

def test_Standby_command_subarray_to_OFF():
    # arrange:
    device_under_test = SubarrayNode
    dut_properties = {
    }
    proxies_to_mock = {
    }

    with fake_tango_system(device_under_test, initial_dut_properties=dut_properties, proxies_to_mock=proxies_to_mock) \
            as tango_context:
        # act:
        tango_context.device.Standby()
        # assert:
        assert tango_context.device.state() == DevState.DISABLE


def test_assignResource_should_command_subarray_AssignResource():
    # arrange:
    device_under_test = SubarrayNode
    csp_subarray_ln_fqdn = 'ska_mid/tm_leaf_node/csp_subarray01'
    csp_subarray_fqdn = 'mid_csp/elt/subarray_01'
    sdp_subarray_ln_fqdn = 'ska_mid/tm_leaf_node/sdp_subarray01'
    sdp_subarray_fqdn = 'mid_sdp/elt/subarray_1'

    dut_properties = {
        'CspSubarrayLNFQDN': csp_subarray_ln_fqdn,
        'CspSubarrayFQDN': csp_subarray_fqdn,
        'SdpSubarrayLNFQDN': sdp_subarray_ln_fqdn,
        'SdpSubarrayFQDN': sdp_subarray_fqdn
    }

    csp_subarray_ln_proxy_mock = Mock()
    csp_subarray_proxy_mock = Mock()
    sdp_subarray_ln_proxy_mock = Mock()
    sdp_subarray_proxy_mock = Mock()

    # csp_subarray_proxy_mock.obsState = ObsState.READY
    # sdp_subarray_proxy_mock.obsState = ObsState.READY
    # csp_subarray_proxy_mock.set_state(DevState.OFF)
    # sdp_subarray_proxy_mock.set_state(DevState.OFF)

    proxies_to_mock = {
        csp_subarray_ln_fqdn : csp_subarray_ln_proxy_mock,
        csp_subarray_fqdn : csp_subarray_proxy_mock,
        sdp_subarray_ln_fqdn : sdp_subarray_ln_proxy_mock,
        sdp_subarray_fqdn : sdp_subarray_proxy_mock
    }


    with fake_tango_system(device_under_test, initial_dut_properties=dut_properties, proxies_to_mock=proxies_to_mock) \
            as tango_context:
        receptor_list = ['0001']
        # receptor_list1 = str(receptor_list)
        # print("type of receptor-list on subarray : ", type(receptor_list1))
        # act:
        # tango_context.device.set_state(DevState.ON)

        cmdData = tango.DeviceData()
        cmdData.insert(tango.DevVarStringArray, receptor_list)
        tango_context.device.On()
        tango_context.device.AssignResources(cmdData)
        arg_list = []
        json_argument = {}
        dish = {}
        dish[const.STR_KEY_RECEPTOR_ID_LIST] = receptor_list
        json_argument[const.STR_KEY_DISH] = dish
        arg_list.append(json.dumps(json_argument))

        # cmdData = tango.DeviceData()
        # cmdData.insert(tango.DevString, scan_config)

        # assert:
        # sdp_subarray_ln_proxy_mock.command_inout.assert_called_with(const.CMD_ASSIGN_RESOURCES, cmdData)
        csp_subarray_ln_proxy_mock.command_inout.assert_called_with(const.CMD_ASSIGN_RESOURCES, arg_list)

def test_start_scan_should_command_subarray_to_start_scan_when_it_is_ready():
    # arrange:
    device_under_test = SubarrayNode
    csp_subarray_ln_fqdn = 'ska_mid/tm_leaf_node/csp_subarray01'
    csp_subarray_fqdn = 'mid_csp/elt/subarray_01'
    sdp_subarray_ln_fqdn = 'ska_mid/tm_leaf_node/sdp_subarray01'
    sdp_subarray_fqdn = 'mid_sdp/elt/subarray_1'

    dut_properties = {
        'CspSubarrayLNFQDN': csp_subarray_ln_fqdn,
        'CspSubarrayFQDN': csp_subarray_fqdn,
        'SdpSubarrayLNFQDN': sdp_subarray_ln_fqdn,
        'SdpSubarrayFQDN': sdp_subarray_fqdn
    }

    csp_subarray_ln_proxy_mock = Mock()
    csp_subarray_proxy_mock = Mock()
    sdp_subarray_ln_proxy_mock = Mock()
    sdp_subarray_proxy_mock = Mock()

    # csp_subarray_proxy_mock.obsState = ObsState.READY
    # sdp_subarray_proxy_mock.obsState = ObsState.READY
    # csp_subarray_proxy_mock.set_state(DevState.ON)
    # sdp_subarray_proxy_mock.set_state(DevState.ON)

    proxies_to_mock = {
        csp_subarray_ln_fqdn : csp_subarray_ln_proxy_mock,
        csp_subarray_fqdn : csp_subarray_proxy_mock,
        sdp_subarray_ln_fqdn : sdp_subarray_ln_proxy_mock,
        sdp_subarray_fqdn : sdp_subarray_proxy_mock
    }

    with fake_tango_system(device_under_test, initial_dut_properties=dut_properties, proxies_to_mock=proxies_to_mock) \
            as tango_context:
        # tango_context.device.state = DevState.ON
        receptor_list = ['0001']
        # receptor_list1 = str(receptor_list)
        # print("type of receptor-list on subarray : ", type(receptor_list1))
        # act:
        # tango_context.device.set_state(DevState.ON)
        tango_context.device.On()
        tango_context.device.AssignResources(receptor_list)

        csp_subarray_proxy_mock.obsState = ObsState.READY
        sdp_subarray_proxy_mock.obsState = ObsState.READY

        scan_config = '{"scanDuration":10}'
        # print("device state of subarray state:", tango_context.device.state())
        # act:
        # tango_context.device.set_state(DevState.ON)
        tango_context.device.Scan(scan_config)
        # cmdData = tango.DeviceData()
        # cmdData.insert(tango.DevString, scan_config)

        # assert:
        # sdp_subarray_ln_proxy_mock.command_inout.assert_called_with(const.CMD_ASSIGN_RESOURCES, cmdData)
        # csp_subarray_ln_proxy_mock.command_inout.assert_called_with(const.CMD_ASSIGN_RESOURCES, cmdData)

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
