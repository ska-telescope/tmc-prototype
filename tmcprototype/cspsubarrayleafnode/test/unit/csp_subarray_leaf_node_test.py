import contextlib
import importlib
import sys
import json
import mock
import types

from mock import Mock
from cspsubarrayleafnode import CspSubarrayLeafNode, const
from tango.test_context import DeviceTestContext
from ska.base.control_model import ObsState

def test_start_scan_should_command_csp_subarray_master_to_start_its_scan_when_it_is_ready():
    # arrange:
    device_under_test = CspSubarrayLeafNode
    csp_subarray_fqdn = 'mid_csp/elt/subarray_01'
    dut_properties = {
        'CspSubarrayFQDN': csp_subarray_fqdn
    }

    csp_subarray_proxy_mock = Mock()
    csp_subarray_proxy_mock.obsState = ObsState.READY

    proxies_to_mock = {
        csp_subarray_fqdn: csp_subarray_proxy_mock
    }

    with fake_tango_system(device_under_test, initial_dut_properties=dut_properties, proxies_to_mock=proxies_to_mock) as tango_context:
        scan_config = { 'scanDuration': 10.0 }
        # act:
        tango_context.device.StartScan([json.dumps(scan_config)])

        # assert:
        csp_subarray_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_STARTSCAN, '0', any_method(with_name='commandCallback'))


def test_assign_resources_should_send_csp_subarray_with_correct_receptor_id_list():
    # arrange:
    device_under_test = CspSubarrayLeafNode
    csp_subarray_fqdn = 'mid_csp/elt/subarray_01'
    dut_properties = {
        'CspSubarrayFQDN': csp_subarray_fqdn
    }

    csp_subarray_proxy_mock = Mock()
    csp_subarray_proxy_mock.obsState = ObsState.IDLE

    proxies_to_mock = {
        csp_subarray_fqdn: csp_subarray_proxy_mock
    }

    with fake_tango_system(device_under_test, initial_dut_properties=dut_properties, proxies_to_mock=proxies_to_mock) as tango_context:
        assign_config='{"dish":{"receptorIDList":["0001","0002"]}}'
        device_proxy=tango_context.device
        #act
        device_proxy.AssignResources(assign_config)

        #assert
        csp_subarray_proxy_mock.command_inout_asynch.assert_called_with(const.CMD_ADD_RECEPTORS,assign_config,
                                                                        any_method(with_name='commandCallback'))
        assert_activity_message(device_proxy, const.STR_ADD_RECEPTORS_SUCCESS)


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



def assert_activity_message(device_proxy, expected_message):
    assert device_proxy.activityMessage == expected_message  # reads tango attribute
